"""
contradiction_matrix.py — 优化2: 多轮矛盾交叉验证矩阵
解决6轮检测窜行问题，实现跨轮关联分析和矛盾综合症候识别
"""

from typing import List, Dict, Optional, Tuple
from collections import defaultdict
import itertools


class ContradictionMatrix:
    """
    矛盾交叉验证矩阵
    
    核心思想：
    - 6轮检测跑完后，不是各自为政地输出
    - 而是进入 6×6 交叉验证矩阵，做关联分析
    - 同一个根因的矛盾合并为"矛盾综合症候"
    """
    
    def __init__(self):
        # Pass名称映射
        self.pass_names = {
            1: "直接矛盾",
            2: "时间线漂移",
            3: "上下文反转",
            4: "数量矛盾",
            5: "承诺衰减",
            6: "条件逃避"
        }
        self.matrix = None

    def analyze(self, all_contradictions: List[Dict]) -> Dict:
        """
        对6轮检测结果做交叉验证
        
        Args:
            all_contradictions: 6轮全部矛盾
            
        Returns:
            {
                "matrix": 6×6关联矩阵,
                "syndromes": 合并后的综合症候,
                "refined": 精炼后的矛盾列表 (合并+排序),
                "cross_pass_discoveries": 跨轮新发现
            }
        """
        if not all_contradictions:
            return {"matrix": {}, "syndromes": [], 
                    "refined": [], "cross_pass_discoveries": []}
        
        # 构建6×6关联矩阵
        self.matrix = self._build_matrix(all_contradictions)
        
        # 合并相关矛盾为综合症候
        syndromes = self._cluster_syndromes(all_contradictions)
        
        # 跨轮新发现（矩阵中高关联度的对角线外元素）
        cross_discoveries = self._find_cross_pass_insights(all_contradictions)
        
        # 精炼（合并+重排序）
        refined = self._refine_contradictions(all_contradictions, syndromes)
        
        return {
            "matrix": self.matrix,
            "syndrome_count": len(syndromes),
            "syndromes": syndromes,
            "refined": refined,
            "cross_pass_count": len(cross_discoveries),
            "cross_pass_discoveries": cross_discoveries,
            "merge_savings": f"合并前{len(all_contradictions)}条 → 合并后{len(refined)}条"
        }

    def _build_matrix(self, contradictions: List[Dict]) -> Dict:
        """
        构建6×6关联矩阵
        
        矩阵元素 M[i][j] = 从Pass i到Pass j的关联强度
        """
        # 按pass分组
        by_pass = defaultdict(list)
        for c in contradictions:
            p = c.get("pass", 0)
            by_pass[p].append(c)
        
        # 初始化6×6矩阵
        passes = list(range(1, 7))
        matrix = {}
        for i in passes:
            for j in passes:
                if i <= j:
                    key = f"{i}-{j}"
                    matrix[key] = {
                        "strength": 0.0,
                        "overlapping_topics": [],
                        "overlapping_entities": [],
                        "shared_count": 0
                    }
        
        # 计算跨pass关联
        for i, j in itertools.combinations_with_replacement(passes, 2):
            ci_list = by_pass.get(i, [])
            cj_list = by_pass.get(j, [])
            
            if not ci_list or not cj_list:
                continue
            
            # 统计话题重叠
            topics_i = set(c.get("topic", "") for c in ci_list)
            topics_j = set(c.get("topic", "") for c in cj_list)
            overlapping = topics_i & topics_j
            
            if overlapping:
                key = f"{i}-{j}"
                matrix[key]["overlapping_topics"] = list(overlapping)
                matrix[key]["shared_count"] = len(overlapping)
                
                # 关联强度 = 重叠话题数 / (总话题数 + 1)
                total = len(topics_i | topics_j)
                matrix[key]["strength"] = round(len(overlapping) / max(1, total), 3)
        
        return matrix

    def _cluster_syndromes(self, contradictions: List[Dict]) -> List[Dict]:
        """
        将相关矛盾聚类为"综合症候"
        
        同一话题 + 时间接近 + 不同pass → 可能是同一个根因
        """
        # 按话题+时间聚类
        clusters = defaultdict(list)
        
        for c in contradictions:
            # 用"话题 + 前后30天"作为聚类键
            topic = c.get("topic", "综合")
            date_a = c.get("statement_a", {}).get("date", "")[:7]  # yyyy-mm
            date_b = c.get("statement_b", {}).get("date", "")[:7]
            cluster_key = f"{topic}|{date_a}|{date_b}"
            clusters[cluster_key].append(c)
        
        syndromes = []
        for key, cluster in clusters.items():
            if len(cluster) < 2:
                continue  # 单条不构成症候
            
            # 检查是否来自不同pass
            passes_used = set(c.get("pass", 0) for c in cluster)
            if len(passes_used) < 2:
                continue  # 同pass的多个矛盾不算综合症候
            
            # 提取症候信息
            topic = cluster[0].get("topic", "综合")
            avg_severity = sum(c.get("adjusted_severity", c.get("severity", 0)) 
                              for c in cluster) / len(cluster)
            
            # 生成症候描述
            pass_names_str = " + ".join(self.pass_names.get(p, f"Pass{p}") 
                                        for p in sorted(passes_used))
            
            syndromes.append({
                "topic": topic,
                "pass_involved": sorted(passes_used),
                "pass_description": pass_names_str,
                "contradiction_count": len(cluster),
                "avg_severity": round(avg_severity, 3),
                "severity": round(avg_severity * (1 + 0.1 * len(cluster)), 3),  # 聚集加重
                "description": f"关于「{topic}」的{pass_names_str}交叉印证显示综合矛盾症候",
                "members": cluster
            })
        
        # 按严重程度排序
        syndromes.sort(key=lambda s: s["severity"], reverse=True)
        return syndromes

    def _find_cross_pass_insights(self, contradictions: List[Dict]) -> List[Dict]:
        """从矩阵中找出跨轮新发现"""
        if not self.matrix:
            return []
        
        insights = []
        
        # 寻找高关联度的跨pass配对
        for key, data in self.matrix.items():
            parts = key.split("-")
            i, j = int(parts[0]), int(parts[1])
            
            if i == j:
                continue  # 忽略对角线（同pass内）
            
            if data["strength"] > 0.4:  # 中高关联
                # 这是跨轮新发现
                insights.append({
                    "pass_pair": f"Pass{i} ↔ Pass{j}",
                    "cross_type": f"{self.pass_names.get(i, f'Pass{i}')} ↔ {self.pass_names.get(j, f'Pass{j}')}",
                    "strength": data["strength"],
                    "overlapping_topics": data["overlapping_topics"],
                    "insight": self._generate_insight(i, j, data)
                })
        
        return insights

    def _generate_insight(self, pass_i: int, pass_j: int, 
                           data: Dict) -> str:
        """生成跨轮洞察描述"""
        topics = data.get("overlapping_topics", [])
        topic_str = "、".join(topics[:3])
        
        templates = {
            (1, 2): f"直接矛盾(P1)与时间线漂移(P2)在「{topic_str}」上吻合 → 非偶然性矛盾",
            (1, 3): f"直接矛盾(P1)与上下文反转(P3)在「{topic_str}」上重叠 → 可能存在场合性双标",
            (1, 4): f"直接矛盾(P1)与数量矛盾(P4)在「{topic_str}」上关联 → 数据层面也存疑",
            (1, 5): f"直接矛盾(P1)与承诺衰减(P5)在「{topic_str}」上关联 → 承诺不可靠",
            (2, 3): f"时间线漂移(P2)与上下文反转(P3)在「{topic_str}」上关联 → 立场随受众漂移",
            (2, 5): f"时间线漂移(P2)与承诺衰减(P5)在「{topic_str}」上吻合 → 承诺随时间的系统性弱化",
            (3, 6): f"上下文反转(P3)与条件逃避(P6)在「{topic_str}」上关联 → 两面人+回避表态",
            (5, 6): f"承诺衰减(P5)与条件逃避(P6)在「{topic_str}」上重叠 → 空洞承诺模式",
        }
        
        # 找最匹配的模板
        pair = (min(pass_i, pass_j), max(pass_i, pass_j))
        if pair in templates:
            return templates[pair]
        
        # 通用模板
        return f"Pass{pass_i}与Pass{pass_j}在「{topic_str}」上存在{data['strength']:.0%}关联"

    def _refine_contradictions(self, contradictions: List[Dict], 
                                syndromes: List[Dict]) -> List[Dict]:
        """精炼矛盾列表（合并+标记症候成员）"""
        # 标记哪些矛盾属于症候
        syndromed_ids = set()
        for syndrome in syndromes:
            for member in syndrome["members"]:
                # 用文本指纹标记
                text_a = member.get("statement_a", {}).get("text", "")[:50]
                text_b = member.get("statement_b", {}).get("text", "")[:50]
                syndromed_ids.add(hash(text_a + text_b))
        
        refined = []
        for c in contradictions:
            text_a = c.get("statement_a", {}).get("text", "")[:50]
            text_b = c.get("statement_b", {}).get("text", "")[:50]
            cid = hash(text_a + text_b)
            
            if cid in syndromed_ids:
                c["is_syndrome"] = True
                # 找对应的症候
                for s in syndromes:
                    if any(hash(m.get("statement_a", {}).get("text", "")[:50] + 
                               m.get("statement_b", {}).get("text", "")[:50]) == cid
                           for m in s["members"]):
                        c["syndrome_ref"] = s["description"]
                        break
                c["adjusted_severity"] = c.get("adjusted_severity", c.get("severity", 0)) * 1.15
            else:
                c["is_syndrome"] = False
            
            refined.append(c)
        
        # 按严重程度排序
        refined.sort(key=lambda c: c.get("adjusted_severity", c.get("severity", 0)), reverse=True)
        return refined


# ============================================================
# 导出接口
# ============================================================

def cross_validate(contradictions: List[Dict]) -> Dict:
    """一键交叉验证"""
    matrix = ContradictionMatrix()
    return matrix.analyze(contradictions)


if __name__ == "__main__":
    print("🔗 矛盾交叉验证矩阵加载完成")
    print(f"  - 6×6关联矩阵: 21个单元格")
    print(f"  - 综合症候聚类: 多Pass交叉印证")
    print(f"  - 跨轮洞察: 自动发现跨检测维度关联")