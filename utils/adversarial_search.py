"""
adversarial_search.py — 优化5: 对抗性红队检测引擎
主动搜索"最坏情况"证据，变被动为主动
"""

import re
from typing import List, Dict, Optional, Tuple
from collections import defaultdict


class AdversarialSearchEngine:
    """
    对抗性检测引擎（红队模式）
    
    核心思想：
    - 不满足于"搜到什么算什么"
    - 主动推导目标人物"最可能被打脸"的点
    - 专门搜这些方向，找自我矛盾证据
    """
    
    def __init__(self):
        # 对抗搜索模板
        self.adversarial_templates = {
            "flip_flop": [
                "{target} 改口 {topic}",
                "{target} 承认 {topic} 错了",
                "{target} 收回 {topic} 言论",
                "{target} 推翻 {topic} 说法",
                "{target} earlier vs now {topic}",
                "{target} backtracks on {topic}",
                "{target} 前后矛盾 {topic}",
            ],
            "promise_broken": [
                "{target} 承诺 {topic} 没兑现",
                "{target} 食言 {topic}",
                "{target} 违约 {topic}",
                "{target} failed to deliver {topic}",
                "{target} 失信 {topic}",
            ],
            "controversy": [
                "{target} 争议 {topic}",
                "{target} 翻车 {topic}",
                "{target} 打脸 {topic}",
                "{target} 红黑 {topic}",
                "{target} scandal {topic}",
                "{target} controversy {topic}",
            ],
            "fact_check": [
                "辟谣 {target} {topic}",
                "揭穿 {target} {topic}",
                "事实核查 {target} {topic}",
                "fact check {target} {topic}",
                "{target} lies about {topic}",
                "{target} mislead {topic}",
            ],
            "compare_statement": [
                "昨天说{keyword}今天说{keyword2} {target}",
                "{target} 之前说{keyword} 现在说{keyword2}",
                "{target} used to say {keyword} now says {keyword2}",
            ]
        }
        
        # 观点对立词对（用于构造对比搜索）
        self.opposite_pairs = [
            ("支持", "反对"), ("支持", "质疑"),
            ("肯定", "否定"), ("赞成", "反对"),
            ("乐观", "悲观"), ("看好", "不看好"),
            ("支持", "不支持"), ("相信", "不信"),
            ("support", "oppose"), ("for", "against"),
            ("approve", "disapprove"), ("optimistic", "pessimistic")
        ]

    def generate_adversarial_queries(self, target: str, 
                                       topics: List[str] = None) -> List[Dict]:
        """
        生成对抗性搜索查询
        
        Args:
            target: 目标人物
            topics: 已知话题列表（没有则用通用模板）
            
        Returns:
            查询列表，每个包含查询字符串和攻击目标
        """
        queries = []
        
        # 为每个话题生成对抗查询
        working_topics = topics or ["", "言论", "表态", "立场", "观点"]
        
        for topic in working_topics:
            for attack_type, templates in self.adversarial_templates.items():
                for template in templates:
                    q = template.replace("{target}", target)
                    q = q.replace("{topic}", topic if topic else "")
                    queries.append({
                        "query": q.strip(),
                        "attack_type": attack_type,
                        "topic": topic or "综合",
                        "priority": self._get_priority(attack_type)
                    })
        
        # 去重
        unique = []
        seen = set()
        for q in queries:
            if q["query"] not in seen and len(q["query"]) > 3:
                seen.add(q["query"])
                unique.append(q)
        
        # 排序：高优先级在前
        unique.sort(key=lambda q: q["priority"], reverse=True)
        
        print(f"🔴 红队对抗搜索: 生成 {len(unique)} 条攻击查询")
        print(f"   - 翻车检测: {sum(1 for q in unique if q['attack_type'] == 'flip_flop')} 条")
        print(f"   - 实锤核查: {sum(1 for q in unique if q['attack_type'] == 'fact_check')} 条")
        print(f"   - 争议扫描: {sum(1 for q in unique if q['attack_type'] == 'controversy')} 条")
        
        return unique

    def _get_priority(self, attack_type: str) -> int:
        """攻击优先级"""
        priorities = {
            "flip_flop": 5,       # 翻车最高优先
            "fact_check": 5,      # 实锤核查
            "promise_broken": 4,  # 承诺未兑现
            "controversy": 3,     # 争议
            "compare_statement": 4  # 对比言论
        }
        return priorities.get(attack_type, 1)

    def scan_for_contradictions(self, search_results: List[Dict]) -> List[Dict]:
        """
        从对抗搜索结果中扫描潜在矛盾
        
        Args:
            search_results: 对抗搜索返回的结果
            
        Returns:
            潜在矛盾线索
        """
        leads = []
        
        for result in search_results:
            text = result.get("text", "") or result.get("snippet", "")
            title = result.get("title", "")
            url = result.get("url", "")
            query = result.get("query_used", "")
            
            # 检测模式
            patterns = {
                "self_contradiction": [
                    r"改口|收回|推翻|前后矛盾|自相矛盾",
                    r"backtrack|contradict|flip.?flop",
                ],
                "exposed_lie": [
                    r"辟谣|揭穿|实锤|造假|虚构",
                    r"fact.check|debunk|expose|lie|false",
                ],
                "promise_failure": [
                    r"失信|未兑现|食言|违约",
                    r"fail|broken promise|not delivered",
                ],
                "embarrassing": [
                    r"打脸|翻车|翻船|尴尬",
                    r"embarrass|awkward|backfire",
                ]
            }
            
            for signal_type, pattern_list in patterns.items():
                for pat in pattern_list:
                    if re.search(pat, text, re.IGNORECASE) or re.search(pat, title, re.IGNORECASE):
                        leads.append({
                            "type": signal_type,
                            "source_url": url,
                            "title": title,
                            "snippet": text[:200],
                            "matched_pattern": pat,
                            "trigger_query": query,
                            "severity": self._lead_severity(signal_type)
                        })
                        break
        
        leads.sort(key=lambda l: l["severity"], reverse=True)
        return leads

    def _lead_severity(self, lead_type: str) -> float:
        """线索严重程度"""
        mapping = {
            "self_contradiction": 0.9,
            "exposed_lie": 0.95,
            "promise_failure": 0.8,
            "embarrassing": 0.6
        }
        return mapping.get(lead_type, 0.5)

    def generate_opposite_search(self, target: str, 
                                  known_statement: str) -> List[str]:
        """
        基于已知言论生成相反立场搜索
        
        例如：已知说过"支持A" → 搜索"反对A"
        """
        queries = []
        
        for kw1, kw2 in self.opposite_pairs:
            if kw1 in known_statement:
                # 替换为相反立场
                opposite_stmt = known_statement.replace(kw1, kw2)
                queries.append(f"{target} {opposite_stmt[:30]}")
            elif kw2 in known_statement:
                opposite_stmt = known_statement.replace(kw2, kw1)
                queries.append(f"{target} {opposite_stmt[:30]}")
        
        return queries

    def red_team_report(self, leads: List[Dict]) -> Dict:
        """生成红队测试报告"""
        if not leads:
            return {
                "red_team_result": "PASS - 未发现对抗性矛盾",
                "lead_count": 0,
                "high_risk_leads": []
            }
        
        high_risk = [l for l in leads if l["severity"] >= 0.8]
        
        return {
            "red_team_result": "ALERT - 发现潜在对抗性证据",
            "lead_count": len(leads),
            "high_risk_count": len(high_risk),
            "high_risk_leads": high_risk[:5],  # top5
            "summary": f"红队攻击发现{len(leads)}条可疑线索，"
                      f"其中{len(high_risk)}条高风险",
            "recommendation": self._recommendation(len(high_risk))
        }

    def _recommendation(self, high_risk_count: int) -> str:
        if high_risk_count >= 3:
            return "🚨 强烈建议深入核查，存在系统性言论风险"
        elif high_risk_count >= 1:
            return "⚠️ 建议对高风险线索进行追溯验证"
        else:
            return "✅ 言论整体抗攻击性良好"


# ============================================================
# 导出接口
# ============================================================

def adversarial_scan(target: str, topics: List[str] = None) -> Dict:
    """一键对抗扫描"""
    engine = AdversarialSearchEngine()
    queries = engine.generate_adversarial_queries(target, topics)
    return {
        "target": target,
        "queries_generated": len(queries),
        "queries": queries,
        "note": "使用生成的查询调用搜索引擎获取结果，然后调用scan_for_contradictions"
    }

def scan_results(search_results: List[Dict]) -> List[Dict]:
    """扫描搜索结果中的潜在矛盾"""
    engine = AdversarialSearchEngine()
    return engine.scan_for_contradictions(search_results)

if __name__ == "__main__":
    print("🔴 对抗性检测引擎(红队模式)加载完成")
    engine = AdversarialSearchEngine()
    print(f"  - 攻击模板: {sum(len(v) for v in engine.adversarial_templates.values())} 种")
    print(f"  - 对立词对: {len(engine.opposite_pairs)} 组")
    print(f"  - 攻击类型: 翻车/实锤/承诺/争议/对比")