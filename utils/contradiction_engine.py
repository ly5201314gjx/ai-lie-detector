"""
contradiction_engine.py — 多轮矛盾检测引擎 (算法二)
"""

import re
from typing import List, Dict, Optional, Tuple
from collections import defaultdict
import itertools


class ContradictionEngine:
    """6轮矛盾检测引擎"""
    
    def __init__(self, topic_modeler=None):
        self.topic_modeler = topic_modeler
        self.contradictions = []
        
        # 对立关系映射
        self.opposition_map = {
            ("strongly_support", "strongly_oppose"): 1.0,
            ("strongly_support", "oppose"): 0.8,
            ("support", "strongly_oppose"): 0.8,
            ("support", "oppose"): 0.7,
            ("strongly_support", "support"): 0.0,
            ("neutral", "neutral"): 0.0,
        }
        
        # 数值模式
        self.quantity_pattern = re.compile(r'([\d,]+\.?\d*)\s*(万|亿|%|人|元|美元|年|月|天|次|部|家|个|倍)')

    def run_all_passes(self, statements: List[Dict], topics: List[str] = None) -> List[Dict]:
        """
        执行全部6轮矛盾检测
        
        Args:
            statements: 带时间戳和立场标注的言论列表
            topics: 限定检测的话题列表
            
        Returns:
            检测到的矛盾列表
        """
        self.contradictions = []
        
        if not topics:
            # 从言论中自动提取话题
            topics = self._extract_topics(statements)
        
        print(f"\n🔍 启动6轮矛盾检测...")
        
        # Pass 1: 直接矛盾
        print(f"  Pass 1/6: 直接矛盾检测...")
        c1 = self.pass1_direct_contradiction(statements, topics)
        print(f"    → 发现 {len(c1)} 处")
        
        # Pass 2: 时间线不一致性
        print(f"  Pass 2/6: 时间线不一致性检测...")
        c2 = self.pass2_temporal_inconsistency(statements, topics)
        print(f"    → 发现 {len(c2)} 处")
        
        # Pass 3: 上下文反转
        print(f"  Pass 3/6: 上下文反转检测...")
        c3 = self.pass3_contextual_reversal(statements, topics)
        print(f"    → 发现 {len(c3)} 处")
        
        # Pass 4: 数量矛盾
        print(f"  Pass 4/6: 数量矛盾检测...")
        c4 = self.pass4_quantitative_mismatch(statements)
        print(f"    → 发现 {len(c4)} 处")
        
        # Pass 5: 承诺梯度
        print(f"  Pass 5/6: 承诺梯度检测...")
        c5 = self.pass5_commitment_gradient(statements)
        print(f"    → 发现 {len(c5)} 处")
        
        # Pass 6: 条件逃避
        print(f"  Pass 6/6: 条件逃避检测...")
        c6 = self.pass6_conditional_evasion(statements)
        print(f"    → 发现 {len(c6)} 处")
        
        # 合并全部结果
        all_contradictions = c1 + c2 + c3 + c4 + c5 + c6
        
        # 检测时间相近的矛盾（可能本质上是同一件事）
        all_contradictions = self._merge_related(all_contradictions)
        
        self.contradictions = all_contradictions
        print(f"\n📊 总计发现 {len(all_contradictions)} 处矛盾")
        
        return all_contradictions

    def _extract_topics(self, statements: List[Dict]) -> List[str]:
        """从言论中提取话题"""
        topics = set()
        for s in statements:
            for t in s.get("topics", []):
                topics.add(t)
        return list(topics)

    def _stance_to_value(self, stance: str) -> float:
        """立场转数值"""
        mapping = {
            "strongly_support": 2.0,
            "support": 1.0,
            "neutral": 0.0,
            "ambiguous": -0.5,
            "evasive": -0.8,
            "oppose": -1.0,
            "strongly_oppose": -2.0
        }
        return mapping.get(stance, 0.0)

    def pass1_direct_contradiction(self, statements: List[Dict], 
                                     topics: List[str]) -> List[Dict]:
        """Pass 1: 直接矛盾检测"""
        contradictions = []
        
        for topic in topics:
            # 筛选该话题的言论
            topic_stmts = [
                s for s in statements 
                if topic in s.get("topics", [])
            ]
            
            if len(topic_stmts) < 2:
                continue
            
            # 两两对比
            for i, j in itertools.combinations(range(len(topic_stmts)), 2):
                si, sj = topic_stmts[i], topic_stmts[j]
                
                stance_i = si.get("stance", "neutral")
                stance_j = sj.get("stance", "neutral")
                
                # 查对立强度
                pair = (stance_i, stance_j)
                opp_strength = self.opposition_map.get(pair, 0.0)
                
                if opp_strength >= 0.6:
                    # 计算文本相似度（快速版：词重叠率）
                    text_i = si.get("text", "")
                    text_j = sj.get("text", "")
                    words_i = set(self._tokenize(text_i))
                    words_j = set(self._tokenize(text_j))
                    
                    overlap = len(words_i & words_j)
                    union = len(words_i | words_j)
                    similarity = overlap / union if union > 0 else 0
                    
                    if similarity < 0.82:  # 不是同义反复
                        contradictions.append({
                            "pass": 1,
                            "type": "direct_flip",
                            "topic": topic,
                            "severity": round(opp_strength * (1 - similarity), 2),
                            "statement_a": {
                                "text": text_i[:150],
                                "date": si.get("date", ""),
                                "stance": stance_i,
                                "source": si.get("source_url", "")
                            },
                            "statement_b": {
                                "text": text_j[:150],
                                "date": sj.get("date", ""),
                                "stance": stance_j,
                                "source": sj.get("source_url", "")
                            },
                            "time_delta_days": self._date_diff(si.get("date", ""), sj.get("date", "")),
                            "description": f"对「{topic}」的立场从「{stance_i}」转为「{stance_j}」"
                        })
        
        return contradictions

    def pass2_temporal_inconsistency(self, statements: List[Dict],
                                       topics: List[str]) -> List[Dict]:
        """Pass 2: 时间线不一致性检测（立场漂移）"""
        contradictions = []
        
        for topic in topics:
            topic_stmts = [
                s for s in statements 
                if topic in s.get("topics", [])
            ]
            
            if len(topic_stmts) < 4:
                continue
            
            # 按时间排序
            topic_stmts.sort(key=lambda s: s.get("date", ""))
            
            # 提取立场数值序列
            values = []
            for s in topic_stmts:
                val = self._stance_to_value(s.get("stance", "neutral"))
                values.append((s.get("date", ""), val))
            
            # 滑动窗口检测趋势
            window_size = max(3, len(values) // 5)
            smoothed = []
            for i in range(len(values)):
                start = max(0, i - window_size // 2)
                end = min(len(values), i + window_size // 2 + 1)
                window_vals = [v[1] for v in values[start:end]]
                smoothed.append(sum(window_vals) / len(window_vals))
            
            # 检测趋势变化
            for i in range(1, len(smoothed)):
                delta = smoothed[i] - smoothed[i-1]
                if abs(delta) >= 2.0:  # 超过2档的改变
                    contradictions.append({
                        "pass": 2,
                        "type": "abrupt_change",
                        "topic": topic,
                        "severity": round(min(1.0, abs(delta) / 4.0), 2),
                        "from_date": values[i-1][0],
                        "to_date": values[i][0],
                        "from_value": values[i-1][1],
                        "to_value": values[i][1],
                        "description": f"对「{topic}」在第{i}条言论后发生剧烈立场转变"
                    })
            
            # 总体趋势检测
            if len(smoothed) >= 4:
                first_avg = sum(smoothed[:3]) / 3
                last_avg = sum(smoothed[-3:]) / 3
                total_drift = last_avg - first_avg
                
                if abs(total_drift) >= 2.0 and len(values) >= 6:
                    contradictions.append({
                        "pass": 2,
                        "type": "gradual_drift",
                        "topic": topic,
                        "severity": round(min(1.0, abs(total_drift) / 4.0), 2),
                        "from_date": values[0][0],
                        "to_date": values[-1][0],
                        "drift_amount": round(total_drift, 2),
                        "description": f"对「{topic}」的立场在分析期间发生系统性漂移 ({total_drift:.1f}档)"
                    })
        
        return contradictions

    def pass3_contextual_reversal(self, statements: List[Dict],
                                    topics: List[str]) -> List[Dict]:
        """Pass 3: 上下文/受众反转检测"""
        contradictions = []
        
        for topic in topics:
            topic_stmts = [
                s for s in statements 
                if topic in s.get("topics", [])
            ]
            
            if len(topic_stmts) < 2:
                continue
            
            # 按场合分类
            by_audience = defaultdict(list)
            for s in topic_stmts:
                audience = s.get("audience_type", "unknown")
                by_audience[audience].append(s)
            
            # 对比不同场合的言论
            audience_types = list(by_audience.keys())
            for i, j in itertools.combinations(range(len(audience_types)), 2):
                a1, a2 = audience_types[i], audience_types[j]
                stmts1 = by_audience[a1]
                stmts2 = by_audience[a2]
                
                # 取各场合的主要立场
                stances1 = [s.get("stance", "neutral") for s in stmts1]
                stances2 = [s.get("stance", "neutral") for s in stmts2]
                
                main1 = max(set(stances1), key=stances1.count)
                main2 = max(set(stances2), key=stances2.count)
                
                val1 = self._stance_to_value(main1)
                val2 = self._stance_to_value(main2)
                
                if val1 * val2 < 0:  # 立场相反
                    # 检查时间窗
                    dates1 = [s.get("date", "") for s in stmts1 if s.get("date")]
                    dates2 = [s.get("date", "") for s in stmts2 if s.get("date")]
                    
                    if dates1 and dates2:
                        d1 = min(dates1)
                        d2 = min(dates2)
                        days_diff = abs(self._date_diff(d1, d2))
                        
                        if days_diff is None or days_diff < 90:
                            contradictions.append({
                                "pass": 3,
                                "type": "audience_reversal",
                                "topic": topic,
                                "severity": round(min(1.0, abs(val1 - val2) / 4.0), 2),
                                "audience_a": a1,
                                "audience_b": a2,
                                "stance_a": main1,
                                "stance_b": main2,
                                "description": f"对不同受众（{a1} vs {a2}）就「{topic}」发表相反观点"
                            })
        
        return contradictions

    def pass4_quantitative_mismatch(self, statements: List[Dict]) -> List[Dict]:
        """Pass 4: 数量/数据矛盾检测"""
        contradictions = []
        
        # 提取所有含数字的言论
        numbered_statements = []
        for s in statements:
            text = s.get("text", "")
            matches = self.quantity_pattern.findall(text)
            for num_str, unit in matches:
                try:
                    num = float(num_str.replace(",", ""))
                    numbered_statements.append({
                        "statement": s,
                        "number": num,
                        "unit": unit,
                        "text_fragment": text[:100]
                    })
                except:
                    pass
        
        # 分组对比（同单位、相近数值）
        for s1, s2 in itertools.combinations(numbered_statements, 2):
            n1, n2 = s1["number"], s2["number"]
            u1, u2 = s1["unit"], s2["unit"]
            
            if u1 != u2:
                continue
            
            # 跳过显然是不同实体的
            if abs(n1 - n2) / max(n1, n2) < 0.05:
                continue
            
            # 检查是否有相同的主题词
            text1 = s1["statement"].get("text", "")
            text2 = s2["statement"].get("text", "")
            common_words = set(self._tokenize(text1)) & set(self._tokenize(text2))
            
            if len(common_words) >= 3:  # 可能说的是同一件事
                ratio = abs(n1 - n2) / max(n1, n2)
                if ratio > 0.15:
                    contradictions.append({
                        "pass": 4,
                        "type": "quantitative_mismatch",
                        "topic": "数据不一致",
                        "severity": round(min(1.0, ratio), 2),
                        "number_a": n1,
                        "number_b": n2,
                        "unit": u1,
                        "date_a": s1["statement"].get("date", ""),
                        "date_b": s2["statement"].get("date", ""),
                        "description": f"数据不一致: {n1}{u1} vs {n2}{u2} (差异{ratio:.0%})"
                    })
        
        return contradictions

    def pass5_commitment_gradient(self, statements: List[Dict]) -> List[Dict]:
        """Pass 5: 承诺梯度检测"""
        contradictions = []
        
        # 承诺动词强度映射
        commitment_verbs = {
            "保证": 1.0, "承诺": 1.0, "发誓": 1.0, "担保": 1.0,
            "确保": 0.9, "一定": 0.9, "绝对": 0.9, "绝不": 1.0,
            "必定": 0.9, "争取": 0.6, "努力": 0.6, "尽力": 0.6,
            "力求": 0.7, "致力于": 0.7, "希望": 0.4, "计划": 0.4,
            "考虑": 0.3, "研究": 0.3, "探讨": 0.3,
            "promise": 1.0, "guarantee": 1.0, "swear": 1.0,
            "assure": 0.9, "pledge": 0.9, "commit": 0.8,
            "vow": 0.9, "undertake": 0.8
        }
        
        # 按话题分组检测承诺
        for topic_key in ["政策", "质量", "安全", "公益", "时间", "价格"]:
            topic_stmts = [
                s for s in statements
                if any(kw in s.get("text", "") for kw in [topic_key])
            ]
            
            if len(topic_stmts) < 3:
                continue
            
            # 按时间排序
            topic_stmts.sort(key=lambda s: s.get("date", ""))
            
            # 提取承诺强度
            commitment_chain = []
            for s in topic_stmts:
                text = s.get("text", "")
                max_strength = 0
                matched_word = ""
                for word, strength in commitment_verbs.items():
                    if word in text:
                        if strength > max_strength:
                            max_strength = strength
                            matched_word = word
                
                if max_strength > 0:
                    commitment_chain.append({
                        "date": s.get("date", ""),
                        "strength": max_strength,
                        "word": matched_word,
                        "text": text[:100]
                    })
            
            # 检测衰减
            if len(commitment_chain) >= 2:
                first = commitment_chain[0]["strength"]
                last = commitment_chain[-1]["strength"]
                
                if first - last > 0.5:
                    contradictions.append({
                        "pass": 5,
                        "type": "commitment_decay",
                        "topic": topic_key,
                        "severity": round((first - last) * 0.8, 2),
                        "first_statement": commitment_chain[0],
                        "last_statement": commitment_chain[-1],
                        "chain_length": len(commitment_chain),
                        "description": f"关于「{topic_key}」的承诺强度从{first:.0f}衰减到{last:.0f}"
                    })
        
        return contradictions

    def pass6_conditional_evasion(self, statements: List[Dict]) -> List[Dict]:
        """Pass 6: 条件逃避检测"""
        contradictions = []
        
        # 条件词
        conditionals_zh = ["如果", "假如", "要是", "除非", "只要", "一旦", "假设"]
        conditionals_en = ["if", "unless", "when", "provided that", "assuming"]
        
        for s in statements:
            text = s.get("text", "")
            topic = s.get("topics", ["未知话题"])[0]
            
            # 统计条件句密度
            cond_count = sum(1 for c in conditionals_zh + conditionals_en if c in text)
            sentences = re.split(r'[。！？.!?\n]', text)
            
            if len(sentences) == 0:
                continue
            
            cond_ratio = cond_count / len(sentences)
            
            # 检测条件句中的逃避策略
            evasion_strategies = []
            
            # 虚假条件（不可能触发的假设）
            if re.search(r'如果\s*(.*(?:和平|完美|绝对|所有人都|任何)).*就', text):
                evasion_strategies.append("hypothetical_hiding")
            
            # 转嫁条件
            if re.search(r'取决于|看(有关部门|政府|上级|领导|他们)', text):
                evasion_strategies.append("external_blame")
            
            # 多限定条件
            if cond_ratio > 0.3:
                evasion_strategies.append("qualification_overload")
            
            if evasion_strategies:
                contradictions.append({
                    "pass": 6,
                    "type": "conditional_evasion",
                    "topic": topic,
                    "severity": round(min(1.0, cond_ratio * 0.7 + 0.3 * (len(evasion_strategies) / 5)), 2),
                    "conditional_ratio": round(cond_ratio, 2),
                    "strategies": evasion_strategies,
                    "text_sample": text[:150],
                    "description": f"使用条件句/假设句逃避明确表态 (密度:{cond_ratio:.0%})"
                })
        
        return contradictions

    def _merge_related(self, contradictions: List[Dict]) -> List[Dict]:
        """合并相关的矛盾（基于话题和时间）"""
        # 由于结构复杂，暂时做去重
        seen = set()
        unique = []
        for c in contradictions:
            key = f"{c.get('type', '')}_{c.get('topic', '')}_{c.get('statement_a', {}).get('text', '')[:50]}"
            if key not in seen:
                seen.add(key)
                unique.append(c)
        return unique

    def _tokenize(self, text: str) -> List[str]:
        """简易分词"""
        import re
        # 中英文混排
        tokens = re.findall(r'[\u4e00-\u9fff]+|[a-zA-Z]+|\d+', text)
        return tokens

    def _date_diff(self, d1: str, d2: str) -> Optional[int]:
        """计算日期差（天数）"""
        from datetime import datetime
        try:
            for fmt in ['%Y-%m-%d', '%Y-%m', '%Y']:
                try:
                    dt1 = datetime.strptime(d1[:len(fmt)], fmt)
                    dt2 = datetime.strptime(d2[:len(fmt)], fmt)
                    return abs((dt2 - dt1).days)
                except:
                    continue
        except:
            pass
        return None


# ============================================================
# 导出接口
# ============================================================

def detect_contradictions(statements: List[Dict], 
                          topics: List[str] = None) -> List[Dict]:
    """一键矛盾检测"""
    engine = ContradictionEngine()
    return engine.run_all_passes(statements, topics)


if __name__ == "__main__":
    print("🔍 矛盾检测引擎加载完成")
    print(f"  - 6轮检测: 直接/时间线/上下文/数量/承诺/条件")
    print(f"  - 对立强度映射: {len(ContradictionEngine().opposition_map)} 种组合")
    print(f"  - 承诺词典: 支持中英文")