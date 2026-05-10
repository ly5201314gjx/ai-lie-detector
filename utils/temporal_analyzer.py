"""
temporal_analyzer.py — 时间线分析与时期划分 (算法四)
"""

import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from collections import defaultdict


class TemporalAnalyzer:
    """时间线标注与时期划分引擎"""
    
    def __init__(self):
        self.granularity_levels = {
            "exact_date": 0,   # 精确到日
            "month": 1,        # 精确到月
            "quarter": 2,      # 精确到季度
            "year": 3,         # 精确到年
            "era": 4           # 抽象时期
        }

    def normalize_date(self, raw_date: str) -> Tuple[Optional[str], int]:
        """
        归一化日期并返回粒度级别
        返回: (ISO日期字符串, 粒度级别)
        """
        if not raw_date or raw_date == "日期未知":
            return None, 4
        
        raw_date = raw_date.strip()
        
        # 精确日期 yyyy-mm-dd
        m = re.match(r'(\d{4})-(\d{1,2})-(\d{1,2})', raw_date)
        if m:
            return f"{m.group(1)}-{m.group(2).zfill(2)}-{m.group(3).zfill(2)}", 0
        
        # 精确日期 yyyy/mm/dd
        m = re.match(r'(\d{4})/(\d{1,2})/(\d{1,2})', raw_date)
        if m:
            return f"{m.group(1)}-{m.group(2).zfill(2)}-{m.group(3).zfill(2)}", 0
        
        # 年月 yyyy年mm月
        m = re.match(r'(\d{4})年(\d{1,2})月', raw_date)
        if m:
            return f"{m.group(1)}-{m.group(2).zfill(2)}", 1
        
        # 年份 yyyy年
        m = re.match(r'(\d{4})年', raw_date)
        if m:
            return f"{m.group(1)}", 3
        
        # ISO年月 yyyy-mm
        m = re.match(r'(\d{4})-(\d{1,2})', raw_date)
        if m:
            return f"{m.group(1)}-{m.group(2).zfill(2)}", 1
        
        # 季度 yyyy-Qn
        m = re.match(r'(\d{4}).*[Qq](\d)', raw_date)
        if m:
            return f"{m.group(1)}-Q{m.group(2)}", 2
        
        # 季度 yyyy年第n季度
        m = re.match(r'(\d{4})年第(\d)季度', raw_date)
        if m:
            return f"{m.group(1)}-Q{m.group(2)}", 2
        
        return None, 4

    def parse_date_to_days(self, date_str: str) -> Optional[int]:
        """将日期转换为距离某个基准的天数"""
        if not date_str:
            return None
        
        # 完整日期
        m = re.match(r'(\d{4})-(\d{1,2})-(\d{1,2})', date_str)
        if m:
            d = datetime(int(m.group(1)), int(m.group(2)), int(m.group(3)))
            return int(d.timestamp() / 86400)
        
        # 年月
        m = re.match(r'(\d{4})-(\d{1,2})$', date_str)
        if m:
            d = datetime(int(m.group(1)), int(m.group(2)), 1)
            return int(d.timestamp() / 86400)
        
        # 年份
        m = re.match(r'(\d{4})$', date_str)
        if m:
            d = datetime(int(m.group(1)), 1, 1)
            return int(d.timestamp() / 86400)
        
        return None

    def detect_era_boundaries(self, statements: List[Dict]) -> List[Dict]:
        """
        检测言论时期边界
        使用Kneedle-style密度检测
        """
        if not statements:
            return []
        
        # 收集有效日期
        dated = []
        for s in statements:
            date_tuple, level = self.normalize_date(s.get("date", ""))
            days = self.parse_date_to_days(date_tuple) if date_tuple else None
            if days:
                dated.append((days, s))
        
        if len(dated) < 5:
            return []
        
        dated.sort(key=lambda x: x[0])
        
        # 计算间隔
        gaps = []
        for i in range(1, len(dated)):
            gap = dated[i][0] - dated[i-1][0]
            gaps.append(gap)
        
        # 检测密度断裂点
        mean_gap = sum(gaps) / len(gaps) if gaps else 0
        std_gap = (sum((g - mean_gap)**2 for g in gaps) / len(gaps))**0.5 if gaps else 0
        
        boundaries = []
        for i, gap in enumerate(gaps):
            if gap > mean_gap + 2 * std_gap and gap > 180:  # 超过180天的断裂
                boundaries.append({
                    "type": "density_break",
                    "gap_days": gap,
                    "before_date": dated[i][1].get("date", ""),
                    "after_date": dated[i+1][1].get("date", ""),
                    "before_statement": dated[i][1].get("text", "")[:50],
                    "after_statement": dated[i+1][1].get("text", "")[:50],
                    "severity": min(1.0, gap / 365)
                })
        
        return boundaries

    def build_timeline(self, statements: List[Dict]) -> List[Dict]:
        """
        构建完整时间线
        
        Returns:
            [{
                "date": "2025-06-15",
                "granularity": 0,
                "statements": [...],
                "stance_summary": {...},
                "is_annotated": bool
            }, ...]
        """
        # 按日期分组
        timeline_map = defaultdict(list)
        for s in statements:
            date_tuple, level = self.normalize_date(s.get("date", ""))
            key = date_tuple or "unknown"
            timeline_map[key].append(s)
        
        # 构建时间线
        timeline = []
        for date_key, stmts in sorted(timeline_map.items()):
            _, level = self.normalize_date(date_key) if date_key != "unknown" else (None, 4)
            
            # 计算该时间点的立场汇总
            stances = {}
            for stmt in stmts:
                stance = stmt.get("stance", "unknown")
                stances[stance] = stances.get(stance, 0) + 1
            
            timeline.append({
                "date": date_key,
                "granularity": level,
                "statement_count": len(stmts),
                "stances": stances,
                "dominant_stance": max(stances, key=stances.get) if stances else "unknown",
                "statements_sample": [s.get("text", "")[:100] + "..." for s in stmts[:3]]
            })
        
        return timeline

    def check_temporal_gaps(self, timeline: List[Dict], 
                            max_gap_days: int = 180) -> List[Dict]:
        """检测时间线中的异常间隔"""
        warnings = []
        
        for i in range(1, len(timeline)):
            prev_date = self.parse_date_to_days(timeline[i-1]["date"])
            curr_date = self.parse_date_to_days(timeline[i]["date"])
            
            if prev_date and curr_date:
                gap = curr_date - prev_date
                if gap > max_gap_days:
                    warnings.append({
                        "type": "long_silence",
                        "gap_days": gap,
                        "from": timeline[i-1]["date"],
                        "to": timeline[i]["date"],
                        "missing_months": round(gap / 30, 1),
                        "severity": min(1.0, gap / (max_gap_days * 2))
                    })
        
        return warnings

    def detect_event_triggers(self, statements: List[Dict], 
                               events: List[Dict] = None) -> List[Dict]:
        """
        检测外部事件触发的言论变化
        
        Args:
            statements: 言论时间线
            events: 已知外部事件列表 [{"date": "...", "event": "...", ...}]
        """
        triggers = []
        
        if not events:
            return triggers
        
        for event in events:
            event_days = self.parse_date_to_days(event.get("date", ""))
            if not event_days:
                continue
            
            # 查找事件前后30天的言论变化
            before = []
            after = []
            
            for s in statements:
                s_days = self.parse_date_to_days(s.get("date", ""))
                if not s_days:
                    continue
                if event_days - 30 <= s_days < event_days:
                    before.append(s)
                elif event_days <= s_days <= event_days + 30:
                    after.append(s)
            
            if before and after:
                triggers.append({
                    "event": event.get("event", "未知事件"),
                    "event_date": event.get("date", ""),
                    "before_count": len(before),
                    "after_count": len(after),
                    "before_stances": self._summarize_stances(before),
                    "after_stances": self._summarize_stances(after),
                    "potential_turn": self._detect_turn(before, after)
                })
        
        return triggers

    def _summarize_stances(self, statements: List[Dict]) -> Dict:
        """汇总一组言论的立场分布"""
        stances = {}
        for s in statements:
            stance = s.get("stance", "unknown")
            stances[stance] = stances.get(stance, 0) + 1
        return stances

    def _detect_turn(self, before: List[Dict], after: List[Dict]) -> Optional[str]:
        """检测事件前后的立场转变"""
        b_stances = self._summarize_stances(before)
        a_stances = self._summarize_stances(after)
        
        if not b_stances or not a_stances:
            return None
        
        # 简单对比主要立场
        b_main = max(b_stances, key=b_stances.get)
        a_main = max(a_stances, key=a_stances.get)
        
        stance_map = {
            "strongly_support": 2, "support": 1, "neutral": 0,
            "oppose": -1, "strongly_oppose": -2
        }
        
        b_val = stance_map.get(b_main, 0)
        a_val = stance_map.get(a_main, 0)
        
        if abs(a_val - b_val) >= 2:
            return "significant_turn"
        elif a_val != b_val:
            return "minor_turn"
        else:
            return "stable"


# ============================================================
# 导出接口
# ============================================================

def build_timeline_report(statements: List[Dict]) -> Dict:
    """生成时间线报告"""
    analyzer = TemporalAnalyzer()
    
    boundaries = analyzer.detect_era_boundaries(statements)
    timeline = analyzer.build_timeline(statements)
    gaps = analyzer.check_temporal_gaps(timeline)
    
    return {
        "total_statements_analyzed": len(statements),
        "total_timeline_points": len(timeline),
        "detected_eras": len(boundaries),
        "era_boundaries": boundaries,
        "temporal_gap_warnings": gaps,
        "timeline_by_date": timeline
    }


if __name__ == "__main__":
    print("⏰ 时间线分析器模块加载完成")
    print(f"   - 粒度级别: 5级 (日/月/季度/年/时期)")
    print(f"   - 沉默警告阈值: 180天")
    print(f"   - 事件触发检测: 支持")