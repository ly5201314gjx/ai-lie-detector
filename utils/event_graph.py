"""
event_graph.py — 优化4: 外部事件知识图谱注入
自动发现目标人物相关的外部关键事件，注入时间线作为上下文锚点
"""

import re
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict


class EventKnowledgeGraph:
    """
    事件知识图谱引擎
    
    核心功能：
    1. 自动发现目标人物相关的外部关键事件（搜索+模板匹配）
    2. 将事件注入时间线作为"锚点"
    3. 评估矛盾对是否可以用外部事件合理解释
    """
    
    def __init__(self):
        # 事件类型模板
        self.event_templates = {
            "legal": {
                "zh_queries": ["诉讼", "起诉", "判决", "法院", "仲裁", "和解", "赔偿", "调查"],
                "en_queries": ["lawsuit", "litigation", "court", "verdict", "settlement", "prosecution"],
                "weight": 0.9,
                "description": "法律/监管事件"
            },
            "financial": {
                "zh_queries": ["财报", "营收", "亏损", "融资", "上市", "市值", "业绩", "利润"],
                "en_queries": ["earnings", "revenue", "loss", "funding", "IPO", "market cap"],
                "weight": 0.8,
                "description": "财务/市场事件"
            },
            "product": {
                "zh_queries": ["发布", "上线", "推出", "新品", "召回", "停产", "升级"],
                "en_queries": ["launch", "release", "recall", "discontinue", "update", "new product"],
                "weight": 0.7,
                "description": "产品/业务事件"
            },
            "scandal": {
                "zh_queries": ["争议", "丑闻", "质疑", "曝光", "道歉", "批评", "投诉"],
                "en_queries": ["scandal", "controversy", "allegation", "apology", "criticism"],
                "weight": 0.95,
                "description": "争议/丑闻事件"
            },
            "milestone": {
                "zh_queries": ["获奖", "签约", "合作", "成立", "里程碑", "突破", "纪录"],
                "en_queries": ["award", "milestone", "partnership", "record", "achievement"],
                "weight": 0.5,
                "description": "里程碑/成就事件"
            },
            "personnel": {
                "zh_queries": ["离职", "上任", "任命", "辞职", "免职", "加入", "离开"],
                "en_queries": ["resign", "appoint", "hire", "fire", "join", "leave", "CEO"],
                "weight": 0.7,
                "description": "人事变动事件"
            }
        }

    def discover_events(self, target: str, time_range_months: int = 36) -> List[Dict]:
        """
        自动发现目标人物的相关外部事件
        
        Args:
            target: 目标人物
            time_range_months: 回溯时间（月）
            
        Returns:
            事件列表
        """
        events = []
        
        # 对每种事件类型构建搜索查询
        for event_type, template in self.event_templates.items():
            queries = []
            for q in template.get("zh_queries", []):
                queries.append(f"{target} {q}")
            for q in template.get("en_queries", []):
                queries.append(f"{target} {q}")
            
            events.append({
                "type": event_type,
                "type_description": template["description"],
                "weight": template["weight"],
                "search_queries": queries[:3],  # 只保留前3个查询
                "auto_discovered": False,  # 标记为待搜索
                "discovered_events": []
            })
        
        print(f"🌐 事件知识图谱: 已构建{len(events)}种事件类型的搜索模板")
        print(f"   - 法律事件: 权重 {self.event_templates['legal']['weight']}")
        print(f"   - 争议事件: 权重 {self.event_templates['scandal']['weight']}")
        print(f"   - 财务事件: 权重 {self.event_templates['financial']['weight']}")
        print(f"   - 人事变动: 权重 {self.event_templates['personnel']['weight']}")
        
        return events

    def inject_events_to_timeline(self, timeline: List[Dict], 
                                   events: List[Dict]) -> List[Dict]:
        """
        将事件注入时间线
        
        每条时间线条目检查其前后30天是否有相关事件
        """
        enriched_timeline = []
        
        for tl_point in timeline:
            date = tl_point.get("date", "")
            if not date or date == "日期未知":
                enriched_timeline.append(tl_point)
                continue
            
            # 找这个时间点附近的匹配事件
            nearby_events = self._find_nearby_events(date, events)
            
            tl_point_copy = dict(tl_point)
            tl_point_copy["nearby_events"] = nearby_events
            tl_point_copy["has_nearby_event"] = len(nearby_events) > 0
            
            enriched_timeline.append(tl_point_copy)
        
        return enriched_timeline

    def evaluate_context(self, contradiction: Dict, 
                          events: List[Dict]) -> Dict:
        """
        用事件知识图谱评估矛盾的合理性
        
        Args:
            contradiction: 单条矛盾
            events: 已知外部事件列表
            
        Returns:
            增强的上下文解析结果
        """
        date_a = contradiction.get("statement_a", {}).get("date", "")
        date_b = contradiction.get("statement_b", {}).get("date", "")
        
        if not date_a or not date_b:
            return {"event_based_justification": 0.0, "events_found": []}
        
        # 查找矛盾发生期间的外部事件
        events_between = self._find_events_between(date_a, date_b, events)
        
        if not events_between:
            return {"event_based_justification": 0.0, "events_found": []}
        
        # 评估事件是否能解释立场变化
        total_weight = sum(e.get("weight", 0.5) for e in events_between)
        justification = min(0.8, total_weight * 0.3)  # 最多给0.8的解释力
        
        return {
            "event_based_justification": round(justification, 3),
            "events_found": events_between,
            "event_count": len(events_between),
            "note": f"矛盾期间发现{len(events_between)}个相关外部事件，"
                    f"可解释性评分{justification:.2f}"
        }

    def _find_nearby_events(self, date_str: str, 
                             events: List[Dict]) -> List[Dict]:
        """查找日期附近30天的事件"""
        nearby = []
        
        date_days = self._date_to_days(date_str)
        if date_days is None:
            return nearby
        
        for event_group in events:
            for discovered in event_group.get("discovered_events", []):
                event_date = discovered.get("date", "")
                event_days = self._date_to_days(event_date)
                if event_days is None:
                    continue
                
                delta = abs(event_days - date_days)
                if delta <= 30:  # 30天内
                    nearby.append({
                        "type": event_group["type_description"],
                        "date": event_date,
                        "title": discovered.get("title", ""),
                        "delta_days": delta,
                        "weight": event_group.get("weight", 0.5)
                    })
        
        # 按时间近远排序
        nearby.sort(key=lambda e: e["delta_days"])
        return nearby[:5]  # 最多5个

    def _find_events_between(self, date_from: str, date_to: str,
                               events: List[Dict]) -> List[Dict]:
        """查找两个日期之间的事件"""
        between = []
        
        days_from = self._date_to_days(date_from)
        days_to = self._date_to_days(date_to)
        if days_from is None or days_to is None:
            return between
        
        start, end = min(days_from, days_to), max(days_from, days_to)
        
        for event_group in events:
            for discovered in event_group.get("discovered_events", []):
                event_date = discovered.get("date", "")
                event_days = self._date_to_days(event_date)
                if event_days is None:
                    continue
                
                if start <= event_days <= end:
                    between.append({
                        "type": event_group["type_description"],
                        "date": event_date,
                        "title": discovered.get("title", ""),
                        "weight": event_group.get("weight", 0.5)
                    })
        
        between.sort(key=lambda e: e["date"])
        return between

    def _date_to_days(self, date_str: str) -> Optional[int]:
        """日期转天数"""
        if not date_str:
            return None
        try:
            for fmt in ['%Y-%m-%d', '%Y-%m', '%Y']:
                try:
                    dt = datetime.strptime(date_str[:len(fmt)], fmt)
                    return int(dt.timestamp() / 86400)
                except:
                    continue
        except:
            pass
        return None


# ============================================================
# 导出接口
# ============================================================

event_graph = EventKnowledgeGraph()

def discover_events(target: str, months: int = 36) -> List[Dict]:
    """发现目标相关事件"""
    return event_graph.discover_events(target, months)

def evaluate_with_events(contradiction: Dict, events: List[Dict]) -> Dict:
    """用事件评估矛盾"""
    return event_graph.evaluate_context(contradiction, events)

if __name__ == "__main__":
    print("🌐 事件知识图谱模块加载完成")
    print(f"  - 事件类型: {len(EventKnowledgeGraph().event_templates)} 种")
    print(f"  - 时间窗口: 前后30天匹配")