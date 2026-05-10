"""
report_generator.py — 报告生成器
将分析结果格式化为可视化报告
"""

from typing import List, Dict, Optional
from datetime import datetime


class ReportGenerator:
    """报告生成器"""
    
    def __init__(self):
        self.template_base = "/sdcard/Download/Operit/skills/lie_detector_ai/templates"

    def generate(self, results: Dict, output_format: str = "standard") -> str:
        """
        生成报告
        
        Args:
            results: 分析结果字典
            output_format: quick_scan / standard / full_report / comparison_matrix
            
        Returns:
            Markdown格式报告
        """
        if output_format == "quick_scan":
            return self._quick_scan(results)
        elif output_format == "full_report":
            return self._full_report(results)
        elif output_format == "comparison_matrix":
            return self._comparison_matrix(results)
        else:
            return self._standard(results)

    def _quick_scan(self, results: Dict) -> str:
        """快速扫描报告"""
        target = results.get("target", "未知")
        contradictions = results.get("contradictions", [])
        final_score = results.get("final_score", {}).get("final_score", 0)
        rating = results.get("final_score", {}).get("rating", {}).get("icon", "❓")
        linguistic = results.get("linguistic_analysis", {}).get("risk_level", "未分析")
        
        lines = [
            f"# 🔍 AI测谎仪 · 快速扫描",
            f"",
            f"**目标**: {target}",
            f"**评分**: {rating} {final_score}/100",
            f"**语言风险**: {linguistic}",
            f"**矛盾数**: {len(contradictions)} 处",
            f"",
            f"---",
            f"",
        ]
        
        if contradictions:
            lines.append("### ⚠️ 核心矛盾")
            top_contradictions = sorted(contradictions, 
                                       key=lambda c: c.get("severity", 0), reverse=True)[:5]
            for i, c in enumerate(top_contradictions, 1):
                severity = c.get("severity", 0)
                sev_bar = "🔴" * min(5, int(severity * 5)) + "⚪" * (5 - min(5, int(severity * 5)))
                lines.append(f"**{i}.** {c.get('description', '未知矛盾')}")
                lines.append(f"   - 严重程度: {sev_bar} ({severity:.2f})")
                lines.append(f"   - 话题: {c.get('topic', '综合')}")
                lines.append(f"")
        
        if linguistic != "未分析":
            lr = results.get("linguistic_analysis", {}).get("risk_score", 0)
            lines.append(f"### 🗣️ 语言特征")
            lines.append(f"- 语言风险评分: {lr:.2f}")
            details = results.get("linguistic_analysis", {}).get("details", {})
            if details:
                lines.append(f"- 模糊词密度: {details.get('hedging_count', 0)} 处")
                lines.append(f"- 情绪唤起度: {details.get('emotional_arousal', 0):.2f}")
                lines.append(f"- 细节丰富度: {details.get('detail_richness', 0):.2f}")
        
        lines.append("")
        lines.append("---")
        lines.append(f"*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}*")
        lines.append(f"*提示: 使用「full_report」格式获取更详细的分析*")
        
        return "\n".join(lines)

    def _standard(self, results: Dict) -> str:
        """标准报告"""
        target = results.get("target", "未知")
        time_range = results.get("time_range", "")
        contradictions = results.get("contradictions", [])
        final_score_data = results.get("final_score", {})
        final_score = final_score_data.get("final_score", 0)
        rating = final_score_data.get("rating", {})
        language_analysis = results.get("linguistic_analysis", {})
        
        lines = [
            f"# 🕵️ AI测谎仪 · 言论一致性分析报告",
            f"",
            f"## 📋 基础信息",
            f"",
            f"| 项目 | 内容 |",
            f"|------|------|",
            f"| 分析目标 | {target} |",
            f"| 时间范围 | {time_range} |",
            f"| 言论总数 | {results.get('statement_count', 0)} 条 |",
            f"| 检测矛盾 | {len(contradictions)} 处 |",
            f"| 分析时间 | {datetime.now().strftime('%Y-%m-%d %H:%M')} |",
            f"",
            f"---",
            f"",
            f"## 📊 综合评分",
            f"",
            f"### 最终得分: **{final_score}/100** {rating.get('icon', '')}",
            f"",
            f"**评级**: {rating.get('label', '未知')}",
            f"",
            f"**说明**: {rating.get('description', '')}",
            f"",
        ]
        
        # 评分分解
        breakdown = final_score_data.get("breakdown", {})
        if breakdown:
            lines.append(f"### 评分分解")
            lines.append(f"")
            lines.append(f"| 维度 | 分值 |")
            lines.append(f"|------|-----:|")
            lines.append(f"| 基础分 | +100.0 |")
            
            penalties = breakdown.get("penalties", {})
            for key, val in penalties.items():
                if key != "total_penalty":
                    lines.append(f"| {self._name_pretty(key)} | {val} |")
            lines.append(f"| **扣分合计** | {penalties.get('total_penalty', 0)} |")
            
            bonuses = breakdown.get("bonuses", {})
            for key, val in bonuses.items():
                if key != "total_bonus":
                    lines.append(f"| {self._name_pretty(key)} | +{val} |")
            lines.append(f"| **加分合计** | +{bonuses.get('total_bonus', 0)} |")
            lines.append(f"")
        
        # 矛盾详情
        if contradictions:
            lines.append(f"---")
            lines.append(f"")
            lines.append(f"## ⚠️ 检测到的矛盾 ({len(contradictions)} 处)")
            lines.append(f"")
            
            # 按严重程度排序
            sorted_c = sorted(contradictions, 
                            key=lambda c: c.get("adjusted_severity", c.get("severity", 0)),
                            reverse=True)
            
            for i, c in enumerate(sorted_c, 1):
                severity = c.get("adjusted_severity", c.get("severity", 0))
                sev_bar = "🔴" * min(5, int(severity * 5)) + "⚪" * (5 - min(5, int(severity * 5)))
                
                lines.append(f"### {i}. {c.get('description', '未命名矛盾')}")
                lines.append(f"")
                lines.append(f"- **类型**: {c.get('type', '未知')}")
                lines.append(f"- **话题**: {c.get('topic', '综合')}")
                lines.append(f"- **严重程度**: {sev_bar} ({severity:.2f})")
                lines.append(f"- **来源检测**: Pass {c.get('pass', '?')}/6")
                
                # 上下文解析
                context = c.get("context_analysis", {})
                if context:
                    lines.append(f"- **上下文解析**: {context.get('justification_score', 0):.2f}")
                    if context.get("note"):
                        lines.append(f"- **解析说明**: {context['note']}")
                
                # 具体内容
                stmt_a = c.get("statement_a", {})
                stmt_b = c.get("statement_b", {})
                if stmt_a:
                    lines.append(f"")
                    lines.append(f"  > **言论 A** ({stmt_a.get('date', '未知日期')}):")
                    lines.append(f"  > {stmt_a.get('text', '')}")
                if stmt_b:
                    lines.append(f"  > **言论 B** ({stmt_b.get('date', '未知日期')}):")
                    lines.append(f"  > {stmt_b.get('text', '')}")
                lines.append(f"")
        
        # 语言分析
        if language_analysis:
            lines.append(f"---")
            lines.append(f"")
            lines.append(f"## 🗣️ 语言特征分析")
            lines.append(f"")
            lines.append(f"**综合风险**: {language_analysis.get('risk_level', '未分析')}")
            lines.append(f"")
            
            details = language_analysis.get("details", {})
            if details:
                lines.append(f"| 指标 | 值 | 评估 |")
                lines.append(f"|------|:---:|:----:|")
                
                hedging = details.get("hedging_count", 0)
                hedging_note = "⚠️ 偏高" if hedging > 10 else "✅ 正常"
                lines.append(f"| 模糊词次数 | {hedging} | {hedging_note} |")
                
                emotion = details.get("emotional_arousal", 0)
                emotion_note = "⚠️ 情绪化" if emotion > 0.3 else "✅ 合理"
                lines.append(f"| 情绪唤起度 | {emotion:.2f} | {emotion_note} |")
                
                detail = details.get("detail_richness", 0.5)
                detail_note = "⚠️ 细节不足" if detail < 0.3 else "✅ 具体"
                lines.append(f"| 细节丰富度 | {detail:.2f} | {detail_note} |")
                
                lines.append(f"")
            
            trend = language_analysis.get("trend", {})
            if trend:
                lines.append(f"**语言变化趋势**: {trend.get('description', '无')}")
                lines.append(f"")
        
        # 来源信息
        sources = results.get("sources", [])
        if sources:
            lines.append(f"---")
            lines.append(f"")
            lines.append(f"## 📡 数据来源")
            lines.append(f"")
            for i, src in enumerate(sources, 1):
                lines.append(f"{i}. {src.get('media', '未知')} — {src.get('url', '')}")
                if src.get("tier"):
                    lines.append(f"   (可信度: {src['tier']})")
            lines.append(f"")
        
        lines.append(f"---")
        lines.append(f"")
        lines.append(f"*报告由 🕵️ AI测谎仪 自动生成 | {datetime.now().strftime('%Y-%m-%d %H:%M')}*")
        lines.append(f"*免责声明: 本报告基于公开数据分析，不构成事实判定。建议结合原始来源进行验证。*")
        
        return "\n".join(lines)

    def _full_report(self, results: Dict) -> str:
        """完整报告（在标准报告基础上增加更多细节）"""
        standard = self._standard(results)
        
        # 增加话题分布
        topics = results.get("topics", {})
        if topics:
            topic_section = [
                f"",
                f"---",
                f"",
                f"## 📂 话题分布",
                f"",
                f"| 话题 | 言论数 | 占比 | 高频词 |",
                f"|------|:-----:|:----:|--------|",
            ]
            for topic, data in topics.items():
                topic_section.append(
                    f"| {topic} | {data.get('count', 0)} | {data.get('ratio', 0)*100:.0f}% | "
                    f"{', '.join(data.get('key_phrases', [])[:4])} |"
                )
            
            topic_section.append(f"")
            standard += "\n".join(topic_section)
        
        # 增加时间线
        timeline = results.get("timeline", [])
        if timeline:
            timeline_section = [
                f"",
                f"---",
                f"",
                f"## ⏰ 时间线概览",
                f"",
                f"| 时间 | 言论数 | 主要立场 | 样本 |",
                f"|------|:-----:|:--------:|------|",
            ]
            for tp in timeline[:10]:  # 最多10个时间点
                date = tp.get("date", "未知")
                count = tp.get("statement_count", 0)
                stance = tp.get("dominant_stance", "unknown")
                sample = tp.get("statements_sample", [""])[0][:50] if tp.get("statements_sample") else ""
                timeline_section.append(f"| {date} | {count} | {stance} | {sample}... |")
            
            timeline_section.append(f"")
            standard += "\n".join(timeline_section)
        
        return standard

    def _comparison_matrix(self, results: Dict) -> str:
        """对比矩阵报告"""
        target = results.get("target", "未知")
        
        lines = [
            f"# 🆚 言论对比矩阵",
            f"",
            f"**目标**: {target}",
            f"",
            f"## 多话题立场对比",
            f"",
            f"| 话题 | 最早立场 | 最新立场 | 变化 | 矛盾数 |",
            f"|------|:--------:|:--------:|:----:|:-----:|",
        ]
        
        # 从结果中提取话题立场变化
        topics = results.get("topics", {})
        contradictions = results.get("contradictions", [])
        
        if topics:
            for topic, data in topics.items():
                stmts = data.get("statements", [])
                if stmts:
                    stmts_sorted = sorted(stmts, key=lambda s: s.get("date", ""))
                    earliest = stmts_sorted[0].get("stance", "?") if stmts_sorted else "?"
                    latest = stmts_sorted[-1].get("stance", "?") if stmts_sorted else "?"
                    
                    # 简化立场显示
                    stance_map = {"strongly_support": "👍", "support": "✓", 
                                 "neutral": "○", "oppose": "✗", 
                                 "strongly_oppose": "👎", "evasive": "⬜"}
                    
                    e_icon = stance_map.get(earliest, "?")
                    l_icon = stance_map.get(latest, "?")
                    
                    change = "→" if e_icon != l_icon else "="
                    c_count = sum(1 for c in contradictions if c.get("topic") == topic)
                    
                    lines.append(f"| {topic} | {e_icon} | {l_icon} | {change} | {c_count} |")
        
        lines.append(f"")
        lines.append(f"---")
        lines.append(f"*对比矩阵由 🕵️ AI测谎仪 自动生成*")
        
        return "\n".join(lines)

    def _name_pretty(self, key: str) -> str:
        """键名美化"""
        names = {
            "direct_contradictions": "直接矛盾扣分",
            "temporal_inconsistencies": "时间线不一致扣分",
            "linguistic_evasion": "语言回避扣分",
            "quantitative_mismatch": "数据矛盾扣分",
            "commitment_decay": "承诺衰减扣分",
            "context_resolution": "上下文解析加分",
            "longitudinal_stability": "长期稳定性加分",
            "source_diversity": "来源多样性加分"
        }
        return names.get(key, key)


def generate_report(results: Dict, fmt: str = "standard") -> str:
    """一键生成报告"""
    gen = ReportGenerator()
    return gen.generate(results, fmt)


if __name__ == "__main__":
    print("📝 报告生成器模块加载完成")
    print(f"  - 输出格式: quick_scan / standard / full_report / comparison_matrix")