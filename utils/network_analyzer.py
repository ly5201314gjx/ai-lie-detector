"""
network_analyzer.py — 优化6: 跨目标"说谎者网络"分析
构建目标人物的利益相关者网络，交叉验证多人言论一致性
"""

import re
from typing import List, Dict, Optional, Tuple, Set
from collections import defaultdict


class NetworkAnalyzer:
    """
    跨目标网络分析引擎
    
    核心功能：
    1. 自动识别目标人物的利益相关者（合作者/竞争者/关联人）
    2. 收集关联人的相关言论
    3. 交叉验证：对同一事件/话题，不同人的说法是否一致
    4. 生成"说谎者网络图"
    """
    
    def __init__(self):
        # 关联关系类型
        self.relation_types = {
            "collaborator": ["合作", "搭档", "联合", "共同", "伙伴",
                            "collaborator", "partner", "co-founder"],
            "competitor": ["竞争", "对手", "竞品", "对标",
                          "competitor", "rival", "opponent"],
            "spokesperson": ["发言", "代表", "表示", "声称",
                            "spokesperson", "representative", "spokesman"],
            "superior": ["上级", "老板", "领导", "CEO", "董事长",
                        "boss", "superior", "manager", "director"],
            "subordinate": ["下属", "员工", "团队", "成员",
                           "employee", "subordinate", "team member"],
            "family": ["家人", "妻子", "丈夫", "父母", "子女",
                      "family", "wife", "husband", "parent"]
        }
        
        # 关联人缓存
        self.related_persons = []

    def discover_network(self, target: str, 
                          search_results: List[Dict]) -> Dict:
        """
        从已有搜索材料中发现目标人物的关系网络
        
        Args:
            target: 目标人物
            search_results: 已有搜索结果
            
        Returns:
            {"persons": [{name, relation, evidence, count}], "network_map": {...}}
        """
        person_relations = defaultdict(lambda: {
            "relations": defaultdict(int),  # 关联关系类型计数
            "mentions": [],                 # 提到该人的原文
            "co_occurrence_count": 0        # 共现次数
        })
        
        # 从搜索结果中提取人物共现
        for result in search_results:
            text = result.get("text", "") or result.get("snippet", "") or result.get("content", "")
            if not text:
                continue
            
            # 简单人物提取（中文名模式：2-4字中文）
            names = re.findall(r'[\u4e00-\u9fff]{2,4}(?:[\s，,]*[\u4e00-\u9fff]{2,4})?', text)
            
            for name in names:
                name = name.strip()
                if name == target or len(name) < 2:
                    continue
                
                # 判断关系类型
                for rel_type, keywords in self.relation_types.items():
                    for kw in keywords:
                        if kw in text:
                            person_relations[name]["relations"][rel_type] += 1
                            break
                
                person_relations[name]["co_occurrence_count"] += 1
                person_relations[name]["mentions"].append(text[:80])
        
        # 构建网络
        persons_list = []
        for name, data in person_relations.items():
            if data["co_occurrence_count"] >= 2:  # 至少出现2次才纳入
                main_relation = max(data["relations"], key=data["relations"].get) if data["relations"] else "unknown"
                persons_list.append({
                    "name": name,
                    "main_relation": main_relation,
                    "relation_detail": dict(data["relations"]),
                    "co_occurrence_count": data["co_occurrence_count"],
                    "evidence_sample": data["mentions"][:3]
                })
        
        # 排序：按共现次数
        persons_list.sort(key=lambda p: p["co_occurrence_count"], reverse=True)
        self.related_persons = persons_list
        
        # 生成摘要
        network_summary = {
            "target": target,
            "network_size": len(persons_list),
            "relation_breakdown": self._breakdown_relations(persons_list),
            "top_relations": persons_list[:5],
            "network_map": self._generate_network_map(target, persons_list[:10])
        }
        
        print(f"🕸️  说谎者网络: 发现 {len(persons_list)} 个关联人物")
        for p in persons_list[:5]:
            print(f"   - {p['name']} ({p['main_relation']}) 共现{p['co_occurrence_count']}次")
        
        return network_summary

    def cross_validate(self, target_statements: List[Dict], 
                        related_statements: Dict[str, List[Dict]]) -> List[Dict]:
        """
        交叉验证：目标人物 vs 关联人物 的言论一致性
        
        Args:
            target_statements: 目标人物言论
            related_statements: {关联人名: [言论列表]}
            
        Returns:
            交叉验证发现的矛盾列表
        """
        findings = []
        
        for person, stmts in related_statements.items():
            # 提取共同话题
            target_topics = self._extract_common_topics(
                [s.get("text", "") for s in target_statements]
            )
            person_topics = self._extract_common_topics(
                [s.get("text", "") for s in stmts]
            )
            
            common_topics = target_topics & person_topics
            if not common_topics:
                continue
            
            # 对每个共同话题对比说法
            for topic in list(common_topics)[:3]:  # 最多3个话题
                target_views = [s for s in target_statements if topic in s.get("text", "")]
                person_views = [s for s in stmts if topic in s.get("text", "")]
                
                if not target_views or not person_views:
                    continue
                
                # 粗略对比立场
                for tv in target_views[:2]:
                    for pv in person_views[:2]:
                        consistency = self._check_consistency(
                            tv.get("text", ""), pv.get("text", "")
                        )
                        
                        if consistency["mismatch"]:
                            findings.append({
                                "type": "cross_person_contradiction",
                                "topic": topic,
                                "person_a": target_statements[0].get("source", "目标"),
                                "person_b": person,
                                "statement_a": tv.get("text", "")[:150],
                                "statement_b": pv.get("text", "")[:150],
                                "severity": consistency["severity"],
                                "description": f"{person}与目标人物在「{topic}」上的说法不一致"
                            })
        
        findings.sort(key=lambda f: f["severity"], reverse=True)
        return findings

    def _breakdown_relations(self, persons: List[Dict]) -> Dict:
        """关系类型统计"""
        breakdown = defaultdict(int)
        for p in persons:
            for rel in p.get("relation_detail", {}):
                breakdown[rel] += 1
        return dict(breakdown)

    def _generate_network_map(self, target: str, 
                               top_persons: List[Dict]) -> str:
        """生成网络图（文本版）"""
        lines = [f"                    [{target}]"]
        lines.append("                    /  |  \\")
        
        for i, p in enumerate(top_persons):
            rel = p.get("main_relation", "关联")
            label = {
                "collaborator": "合作", "competitor": "竞争",
                "spokesperson": "代言的", "superior": "上级",
                "subordinate": "下属", "family": "家人"
            }.get(rel, rel)
            
            if i < 3:
                lines.append(f"                  ({label})")
                lines.append(f"                  [{p['name']}]")
            elif i == 3:
                lines.append(f"                  ... 共{len(top_persons)}个关联人")
        
        return "\n".join(lines)

    def _extract_common_topics(self, texts: List[str]) -> Set[str]:
        """从文本集合中提取共同话题"""
        common = defaultdict(int)
        
        # 预定义核心话题
        core_topics = [
            "合作", "竞争", "发展", "创新", "质量", "安全",
            "投资", "技术", "市场", "产品", "战略", "愿景",
            "上市", "融资", "并购", "重组", "转型",
            "争议", "道歉", "解释", "回应"
        ]
        
        for text in texts:
            for topic in core_topics:
                if topic in text:
                    common[topic] += 1
        
        return set(t for t, c in common.items() if c >= 1)

    def _check_consistency(self, text_a: str, text_b: str) -> Dict:
        """检查两段言论的一致性"""
        # 简易硬编码对立判断
        opposition_pairs = [
            ("是", "不是"), ("有", "没有"), ("支持", "反对"),
            ("同意", "不同意"), ("肯定", "否定"), ("会", "不会"),
            ("在", "不在"), ("行", "不行"), ("对", "错"),
            ("yes", "no"), ("will", "won't"), ("do", "don't"),
            ("支持", "不支持"), ("承认", "否认")
        ]
        
        mismatch_count = 0
        total_checks = 0
        
        for word_a, word_b in opposition_pairs:
            has_a = word_a in text_a
            has_b = word_b in text_b
            
            # 如果A用"是"，B用"不是" → 矛盾
            if has_a and word_b in text_a:
                pass  # A和B同一段，不算
            elif has_a and has_b:
                # 检查"是"和"不是"是否在争论同一件事
                context_a = self._get_context(text_a, word_a)
                context_b = self._get_context(text_b, word_b)
                if context_a and context_b and context_a == context_b:
                    mismatch_count += 1
                    total_checks += 1
            
            if has_a or has_b:
                total_checks += 1
        
        if total_checks == 0:
            return {"mismatch": False, "severity": 0.0}
        
        mismatch_ratio = mismatch_count / total_checks
        return {
            "mismatch": mismatch_ratio > 0.3,
            "severity": round(mismatch_ratio, 2),
            "mismatch_count": mismatch_count,
            "total_checks": total_checks
        }

    def _get_context(self, text: str, word: str) -> Optional[str]:
        """提取词附近的上下文"""
        idx = text.find(word)
        if idx == -1:
            return None
        start = max(0, idx - 10)
        end = min(len(text), idx + len(word) + 10)
        return text[start:end]


# ============================================================
# 导出接口
# ============================================================

def discover_network(target: str, search_results: List[Dict]) -> Dict:
    """发现关系网络"""
    analyzer = NetworkAnalyzer()
    return analyzer.discover_network(target, search_results)

def cross_validate_persons(target_stmts: List[Dict],
                            related_stmts: Dict[str, List[Dict]]) -> List[Dict]:
    """交叉验证多人言论"""
    analyzer = NetworkAnalyzer()
    return analyzer.cross_validate(target_stmts, related_stmts)

if __name__ == "__main__":
    print("🕸️  说谎者网络分析器加载完成")
    print(f"  - 关系类型: {len(NetworkAnalyzer().relation_types)} 种")
    print(f"  - 交叉验证: 多人同话题言论一致性")
    print(f"  - 网络图生成: 文本化关系图谱")