"""
context_resolver.py — 上下文解析器 (算法五)
判断矛盾是否有合理的语境解释，调整严重性
"""

import re
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta


class ContextResolver:
    """上下文解析器"""
    
    def __init__(self):
        self.event_keywords = {
            "legal": ["诉讼", "起诉", "判决", "法院", "仲裁", "和解", "赔偿",
                      "lawsuit", "litigation", "court", "verdict", "settlement"],
            "policy": ["政策", "法规", "新政", "条例", "regulation", "policy"],
            "scandal": ["丑闻", "争议", "爆料", "曝光", "质疑",
                       "scandal", "controversy", "allegation"],
            "milestone": ["获奖", "上市", "上线", "发布", "成立",
                         "award", "launch", "IPO", "anniversary"]
        }

    def resolve(self, contradictions: List[Dict], 
                 statements: List[Dict]) -> List[Dict]:
        """
        对检测到的矛盾进行上下文解析
        
        Args:
            contradictions: 矛盾列表
            statements: 全部言论
            
        Returns:
            解析后的矛盾（含合理性评分）
        """
        resolved = []
        
        for c in contradictions:
            context = self._analyze_context(c, statements)
            justification = context["justification_score"]
            
            # 调整严重性
            if justification > 0.7:
                c["adjusted_severity"] = round(c.get("severity", 0) * (1 - justification), 3)
                c["context_note"] = context["note"]
            elif justification > 0.4:
                c["adjusted_severity"] = round(c.get("severity", 0) * 0.7, 3)
                c["context_note"] = context["note"]
            else:
                c["adjusted_severity"] = c.get("severity", 0)
                c["context_note"] = "无合理解释"
            
            c["context_analysis"] = context
            resolved.append(c)
        
        return resolved

    def _analyze_context(self, contradiction: Dict,
                          statements: List[Dict]) -> Dict:
        """分析单个矛盾的上下文"""
        
        # 获取矛盾双方信息
        stmt_a = contradiction.get("statement_a", {})
        stmt_b = contradiction.get("statement_b", {})
        
        date_a = stmt_a.get("date", "")
        date_b = stmt_b.get("date", "")
        
        text_a = stmt_a.get("text", "")
        text_b = stmt_b.get("text", "")
        
        scores = []
        reasons = []
        
        # 维度A: 时间背景变化
        time_delta = self._calc_date_diff(date_a, date_b)
        if time_delta:
            if time_delta > 365:
                # 超过1年，检查是否有重大事件
                events_found = self._find_events_between(statements, date_a, date_b)
                if events_found:
                    scores.append(0.7)
                    reasons.append(f"时间跨度{time_delta}天，期间发生: {events_found[:2]}")
                else:
                    scores.append(0.3)
                    reasons.append(f"时间跨度{time_delta}天，但无明确重大事件")
            elif time_delta > 90:
                scores.append(0.5)
                reasons.append(f"时间跨度{time_delta}天（3个月以上），观点可能自然演化")
            else:
                scores.append(0.1)
                reasons.append(f"时间跨度{time_delta}天，短期内转变")
        
        # 维度B: 法律/合规约束
        if self._has_legal_context(text_a, text_b):
            scores.append(0.7)
            reasons.append("涉及法律/合规内容，言论可能受约束")
        
        # 维度C: 受众变化
        audience_a = stmt_a.get("audience_type", "unknown")
        audience_b = stmt_b.get("audience_type", "unknown")
        if audience_a != audience_b and audience_a != "unknown" and audience_b != "unknown":
            scores.append(0.4)
            reasons.append(f"受众不同: {audience_a} vs {audience_b}")
        
        # 维度D: 话题性质
        topic = contradiction.get("topic", "")
        if topic in ["争议回应", "个人生活"]:
            scores.append(0.3)  # 这类话题更容易被误导
            reasons.append("话题涉及个人争议/隐私，言论可能不完整")
        elif topic in ["政策立场", "行业观点"]:
            scores.append(0.5)  # 这类话题观点可以自然演变
            reasons.append("话题涉及观点/立场，随时间合理演变")
        
        # 计算综合合理性
        justification_score = max(scores) if scores else 0.0
        
        return {
            "justification_score": round(justification_score, 2),
            "reasons": reasons,
            "time_delta_days": time_delta,
            "note": "; ".join(reasons) if reasons else "未发现合理解释"
        }

    def _calc_date_diff(self, d1: str, d2: str) -> Optional[int]:
        """计算日期差"""
        if not d1 or not d2:
            return None
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

    def _find_events_between(self, statements: List[Dict], 
                               date_from: str, date_to: str) -> List[str]:
        """查找两个日期之间的事件"""
        events = []
        event_keywords_all = []
        for kw_list in self.event_keywords.values():
            event_keywords_all.extend(kw_list)
        
        for s in statements:
            s_date = s.get("date", "")
            if not s_date:
                continue
            diff_from = self._calc_date_diff(date_from, s_date)
            diff_to = self._calc_date_diff(date_to, s_date)
            if diff_from is not None and diff_to is not None:
                if diff_from >= 0 and diff_to <= 0:
                    text = s.get("text", "")
                    for kw in event_keywords_all:
                        if kw in text:
                            events.append(text[:80])
                            break
        
        return events[:5]

    def _has_legal_context(self, text_a: str, text_b: str) -> bool:
        """检查是否涉及法律/合规内容"""
        legal_kw = self.event_keywords.get("legal", [])
        for kw in legal_kw:
            if kw in text_a or kw in text_b:
                return True
        return False


def resolve_contradictions(contradictions: List[Dict], 
                            statements: List[Dict]) -> List[Dict]:
    """一键解析"""
    resolver = ContextResolver()
    return resolver.resolve(contradictions, statements)


if __name__ == "__main__":
    print("🧠 上下文解析器模块加载完成")
    print(f"  - 解析维度: 时间/法律/受众/话题性质")