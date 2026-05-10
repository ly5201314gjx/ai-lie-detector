"""
linguistic_analyzer.py — 多维度语言特征分析 (算法三)
"""

import re
import json
from typing import List, Dict, Optional, Tuple
from collections import Counter


class LinguisticAnalyzer:
    """语言体征分析仪"""
    
    def __init__(self, deception_patterns: Dict = None):
        self.patterns = deception_patterns or {}
        self.weights = {
            "hedging": 0.25,
            "vagueness": 0.20,
            "deflection": 0.15,
            "emotional_arousal": 0.10,
            "detail_richness": 0.15,
            "personal_pronoun_ratio": 0.10,
            "cognitive_process": 0.05
        }

    def analyze(self, statements: List[Dict]) -> Dict:
        """
        对一组言论进行全维度语言分析
        
        Returns:
            analysis result with dimensions and overall risk score
        """
        if not statements:
            return {"error": "无言论可分析", "overall_risk": 0.0}
        
        # 聚合所有文本
        all_texts = [s.get("text", "") for s in statements]
        combined = " ".join(all_texts)
        
        # 逐条分析 + 整体分析
        per_statement = [self._analyze_single(s.get("text", "")) for s in statements]
        overall = self._analyze_single(combined)
        
        # 综合风险
        risk_score = self._compute_overall_risk(per_statement, overall)
        
        # 趋势分析（对比早期和近期言论）
        if len(statements) >= 4:
            mid = len(statements) // 2
            early = " ".join([s.get("text", "") for s in statements[:mid]])
            recent = " ".join([s.get("text", "") for s in statements[mid:]])
            early_score = self._analyze_single(early)
            recent_score = self._analyze_single(recent)
            trend = self._detect_trend(early_score, recent_score)
        else:
            trend = {"direction": "stable", "description": "样本不足"}
        
        result = {
            "statements_analyzed": len(statements),
            "total_chars": len(combined),
            "overall": overall,
            "per_statement_summary": self._summarize(per_statement),
            "trend": trend,
            "risk_score": risk_score,
            "risk_level": self._risk_level(risk_score),
            "risk_color": self._risk_color(risk_score),
            "details": {
                "hedging_count": overall.get("hedging_count", 0),
                "deflection_count": overall.get("deflection_count", 0),
                "emotional_arousal": overall.get("emotional_score", 0),
                "detail_richness": overall.get("detail_richness", 0.5),
                "pronoun_ratio": overall.get("pronoun_ratio", 0.5),
                "cognitive_balance": overall.get("cognitive_balance", 0.5)
            }
        }
        
        return result

    def _analyze_single(self, text: str) -> Dict:
        """分析单段文本"""
        if not text:
            return {
                "hedging_ratio": 0, "hedging_count": 0,
                "deflection_count": 0, "emotional_score": 0,
                "detail_richness": 0.5, "pronoun_ratio": 0.5,
                "cognitive_balance": 0.5, "word_count": 0,
                "sentence_count": 0, "avg_sentence_length": 0
            }
        
        # 分词（简易）
        words = self._tokenize(text)
        sentences = re.split(r'[。！？.!?\n]', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        word_count = len(words)
        sentence_count = len(sentences) if sentences else 1
        
        # 1. 模糊/回避语言密度
        hedging_words = self._load_hedging()
        hedging_count = sum(1 for w in words if w in hedging_words)
        hedging_ratio = hedging_count / word_count if word_count > 0 else 0
        
        # 2. 回避策略计数
        deflection_count = self._count_deflections(text)
        
        # 3. 情绪唤起度
        emotional_score = self._emotional_analysis(text)
        
        # 4. 细节丰富度
        detail_richness = self._detail_richness(text)
        
        # 5. 人称代词比例
        pronoun_ratio = self._pronoun_analysis(text)
        
        # 6. 认知过程词
        cognitive_balance = self._cognitive_analysis(text)
        
        return {
            "hedging_ratio": round(hedging_ratio, 4),
            "hedging_count": hedging_count,
            "deflection_count": deflection_count,
            "emotional_score": round(emotional_score, 3),
            "detail_richness": round(detail_richness, 3),
            "pronoun_ratio": round(pronoun_ratio, 3),
            "cognitive_balance": round(cognitive_balance, 3),
            "word_count": word_count,
            "sentence_count": sentence_count,
            "avg_sentence_length": round(word_count / sentence_count, 1)
        }

    def _load_hedging(self) -> set:
        """加载模糊词汇"""
        hedging = set()
        if self.patterns and "hedging_phrases" in self.patterns:
            for lang in ["zh", "en"]:
                for word in self.patterns["hedging_phrases"].get(lang, []):
                    hedging.add(word)
        return hedging

    def _count_deflections(self, text: str) -> int:
        """统计回避策略使用次数"""
        count = 0
        if not self.patterns or "deflection_strategies" not in self.patterns:
            return 0
        for strategy, data in self.patterns["deflection_strategies"].items():
            for lang in ["zh", "en"]:
                for phrase in data.get(lang, []):
                    if phrase in text:
                        count += 1
        return count

    def _emotional_analysis(self, text: str) -> float:
        """分析情绪唤起度"""
        # 正面情绪词
        positive = ["开心", "高兴", "自豪", "满意", "感动", "乐观", 
                    "兴奋", "激动", "欣慰", "喜悦",
                    "happy", "proud", "excited", "delighted", "thrilled"]
        # 负面情绪词
        negative = ["愤怒", "失望", "伤心", "焦虑", "恐惧", "痛心",
                    "生气", "震惊", "沮丧", "悲哀",
                    "angry", "disappointed", "fear", "shocked", "upset"]
        
        pos_count = sum(1 for w in positive if w in text)
        neg_count = sum(1 for w in negative if w in text)
        total = pos_count + neg_count
        
        if total == 0:
            return 0.0
        
        # 情绪总体强度，同时考虑正负比例是否异常
        intensity = min(1.0, total * 0.15)
        balance = (pos_count - neg_count) / total if total > 0 else 0
        
        # 极端情绪（所有情绪词集中在一侧）
        if abs(balance) > 0.8 and total > 3:
            intensity = min(1.0, intensity * 1.3)
        
        return round(intensity, 3)

    def _detail_richness(self, text: str) -> float:
        """细节丰富度评估"""
        # 数字密度
        numbers = re.findall(r'\d+', text)
        num_density = len(numbers) / max(1, len(text) / 10)  # 每10字含数字数
        
        # 专有名词密度（大写字母开头词）
        entities = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
        entity_density = len(entities) / max(1, len(text) / 20)
        
        # 具体动词（行为类）
        specific_verbs = [
            "做", "写", "读", "画", "唱", "跳", "跑", "买", "卖",
            "制作", "完成", "到达", "获得",
            "write", "create", "build", "design", "develop", "produce"
        ]
        verb_count = sum(1 for v in specific_verbs if v in text)
        verb_density = verb_count / max(1, len(text) / 50)
        
        # 综合
        richness = min(1.0, 0.4 * num_density + 0.3 * entity_density + 0.3 * verb_density)
        return round(richness, 3)

    def _pronoun_analysis(self, text: str) -> float:
        """人称代词分析：我/(我+我们) 比例"""
        i_count = len(re.findall(r'[我I](?=[^a-zA-Z])', text))
        we_count = len(re.findall(r'[我们we](?=[^a-zA-Z])', text))
        # 修正：we 可能匹配到字母组合
        we_count = len(re.findall(r'\bwe\b', text.lower()))
        
        total = i_count + we_count
        if total == 0:
            return 0.5  # 中性
        
        ratio = i_count / total
        return round(ratio, 3)

    def _cognitive_analysis(self, text: str) -> float:
        """认知过程词分析"""
        # 因果词
        causal = ["因为", "所以", "因此", "导致", "由于", "原因",
                  "cause", "because", "therefore", "result"]
        # 确定性词
        certain = ["肯定", "一定", "确信", "确定", "绝对",
                   "certain", "definitely", "absolutely", "sure"]
        # 差异词
        contrast = ["但是", "然而", "不过", "却", "虽然",
                    "however", "but", "although", "yet"]
        
        causal_count = sum(1 for w in causal if w in text)
        certain_count = sum(1 for w in certain if w in text)
        contrast_count = sum(1 for w in contrast if w in text)
        
        # 认知平衡评分
        hedging = self._load_hedging()
        hedging_count = sum(1 for w in self._tokenize(text) if w in hedging)
        
        if certain_count + hedging_count > 0:
            balance = certain_count / (certain_count + hedging_count)
        else:
            balance = 0.5
        
        # 0=过于回避, 0.5=平衡, 1=过于肯定
        return round(balance, 3)

    def _compute_overall_risk(self, per_stmt: List[Dict], overall: Dict) -> float:
        """计算综合语言风险"""
        if not per_stmt:
            return 0.0
        
        # 平均各维度分
        avg_hedging = sum(s.get("hedging_ratio", 0) for s in per_stmt) / len(per_stmt)
        avg_emotion = sum(s.get("emotional_score", 0) for s in per_stmt) / len(per_stmt)
        avg_detail = sum(s.get("detail_richness", 0.5) for s in per_stmt) / len(per_stmt)
        avg_pronoun = sum(abs(s.get("pronoun_ratio", 0.5) - 0.5) for s in per_stmt) / len(per_stmt)
        
        # 风险计算
        risk_hedging = min(1.0, avg_hedging * 10)  # 模糊词越多风险越高
        risk_emotion = min(1.0, avg_emotion * 2)   # 情绪过度也高风险
        risk_detail_loss = 1.0 - avg_detail         # 细节越少风险越高
        risk_pronoun_abnormal = avg_pronoun * 2     # 代词偏差越大风险越高
        
        weighted_risk = (
            self.weights["hedging"] * risk_hedging +
            self.weights["emotional_arousal"] * risk_emotion +
            self.weights["detail_richness"] * risk_detail_loss +
            self.weights["personal_pronoun_ratio"] * min(1.0, risk_pronoun_abnormal) +
            self.weights["deflection"] * min(1.0, overall.get("deflection_count", 0) * 0.1)
        )
        
        return round(min(1.0, weighted_risk), 3)

    def _summarize(self, analyses: List[Dict]) -> Dict:
        """汇总统计"""
        if not analyses:
            return {}
        
        avg_hedging = sum(a.get("hedging_ratio", 0) for a in analyses) / len(analyses)
        max_hedging = max(a.get("hedging_ratio", 0) for a in analyses)
        avg_detail = sum(a.get("detail_richness", 0.5) for a in analyses) / len(analyses)
        
        return {
            "avg_hedging_ratio": round(avg_hedging, 4),
            "max_hedging_ratio": round(max_hedging, 4),
            "avg_detail_richness": round(avg_detail, 4),
            "high_hedging_count": sum(1 for a in analyses if a.get("hedging_ratio", 0) > 0.05),
            "deflection_total": sum(a.get("deflection_count", 0) for a in analyses)
        }

    def _detect_trend(self, early: Dict, recent: Dict) -> Dict:
        """检测语言特征变化趋势"""
        trends = []
        
        if recent.get("hedging_ratio", 0) > early.get("hedging_ratio", 0) * 1.5:
            trends.append("模糊语言增多")
        if recent.get("detail_richness", 0) < early.get("detail_richness", 0) * 0.7:
            trends.append("细节丰富度下降")
        if recent.get("emotional_score", 0) > early.get("emotional_score", 0) * 2:
            trends.append("情绪表达增多")
        
        if not trends:
            direction = "stable"
            desc = "语言特征基本稳定"
        elif len(trends) >= 2:
            direction = "worsening"
            desc = "语言模式恶化: " + ", ".join(trends)
        else:
            direction = "slight_change"
            desc = "轻微变化: " + trends[0]
        
        return {"direction": direction, "description": desc}

    def _risk_level(self, score: float) -> str:
        if score >= 0.75: return "🚨 紧急"
        if score >= 0.55: return "🔴 高风险"
        if score >= 0.30: return "⚠️ 中等风险"
        return "✅ 低风险"

    def _risk_color(self, score: float) -> str:
        if score >= 0.75: return "red"
        if score >= 0.55: return "orange"
        if score >= 0.30: return "yellow"
        return "green"

    def _tokenize(self, text: str) -> List[str]:
        """简易分词"""
        tokens = re.findall(r'[\u4e00-\u9fff]+|[a-zA-Z]+', text)
        return [t for t in tokens if len(t) >= 1]


def analyze_language(statements: List[Dict]) -> Dict:
    """一键语言分析"""
    analyzer = LinguisticAnalyzer()
    return analyzer.analyze(statements)


if __name__ == "__main__":
    print("🗣️  语言分析器模块加载完成")
    print(f"  - 维度: {len(LinguisticAnalyzer().weights)} 个")
    print(f"  - 模糊词库: 中英文双语")