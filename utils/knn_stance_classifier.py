"""
knn_stance_classifier.py — 优化1: 小样本语义嵌入立场分类器
用原型向量+KNN做立场分类，越用越准
"""

import re
from typing import List, Dict, Optional, Tuple
from collections import defaultdict


class KNNStanceClassifier:
    """
    基于原型积累的KNN立场分类器
    
    工作方式：
    1. 维护一个 stance_prototypes 池（从历史分析和人工校正积累）
    2. 新言论来的时候：
       a. 先用关键词粗筛（兜底）
       b. 然后在prototype池里找语义最近的3条
       c. 如果最近3条立场一致 → 直接采纳
       d. 如果不一致 → 标记为"不确定"让交互确认
    """
    
    def __init__(self):
        # 立场原型池：{(词袋指纹): {stance, text, count, source}}
        self.prototype_pool = []  # List of prototype dicts
        self.max_prototypes = 500
        
        # 关键词兜底
        self.keyword_map = {
            "strongly_support": [
                "坚决支持", "完全赞同", "绝对拥护", "坚定不移",
                "全力支持", "强烈支持", "由衷支持", "毫无保留"
            ],
            "support": [
                "支持", "赞同", "同意", "认可", "肯定", "看好",
                "鼓励", "拥护", "赞成"
            ],
            "neutral": [
                "不确定", "不好说", "不知道", "没意见", "保持中立",
                "不评论", "不发表看法", "不持立场"
            ],
            "oppose": [
                "反对", "不同意", "不赞同", "不认可", "不看好",
                "质疑", "存疑", "有保留", "持保留意见"
            ],
            "strongly_oppose": [
                "坚决反对", "强烈反对", "完全不同意", "严正反对",
                "绝不容忍", "严词谴责"
            ],
            "evasive": [
                "不予置评", "不方便回答", "不想多谈", "无可奉告",
                "跳过这个问题", "no comment", "不便回应"
            ],
            "ambiguous": [
                "这个问题问得好", "要分情况看", "看情况",
                "这个比较复杂", "不能简单说"
            ]
        }

    def classify(self, text: str, topic: str = None) -> Dict:
        """
        对单条言论进行立场分类，返回分类结果+置信度
        
        Returns:
            {"stance": str, "confidence": float, "method": str,
             "neighbors": [...], "signals": [...]}
        """
        if not text or len(text.strip()) < 5:
            return {"stance": "neutral", "confidence": 0.3, 
                    "method": "fallback_empty", "neighbors": []}
        
        signals = []
        
        # ---- Step 1: 检测逃避信号（最高优先级）----
        evasive_check = self._check_evasive(text)
        if evasive_check["detected"]:
            signals.append(f"逃避信号: {evasive_check['signal']}")
            return {
                "stance": "evasive",
                "confidence": 0.85,
                "method": "evasion_detected",
                "neighbors": [],
                "signals": signals
            }
        
        # ---- Step 2: KNN原型匹配（如果有足够原型）----
        if len(self.prototype_pool) >= 10:
            knn_result = self._knn_classify(text)
            if knn_result and knn_result["confidence"] > 0.6:
                signals.append(f"KNN匹配: {knn_result['neighbor_count']}个近邻一致")
                return {
                    "stance": knn_result["stance"],
                    "confidence": knn_result["confidence"],
                    "method": "knn_prototype",
                    "neighbors": knn_result["neighbors"][:3],
                    "signals": signals
                }
            elif knn_result:
                signals.append(f"KNN低置信: 最近邻居立场不一致")
        
        # ---- Step 3: 关键词匹配兜底 ----
        kw_result = self._keyword_classify(text)
        if kw_result["matched"]:
            signals.append(f"关键词匹配: {kw_result['matched_words']}")
            return {
                "stance": kw_result["stance"],
                "confidence": kw_result["confidence"],
                "method": "keyword_fallback",
                "neighbors": [],
                "signals": signals
            }
        
        # ---- Step 4: 情感极性终极兜底 ----
        polarity = self._sentiment_polarity(text)
        if abs(polarity) > 0.3:
            stance = "support" if polarity > 0 else "oppose"
            signals.append(f"情感极性: {'正向' if polarity > 0 else '负向'}({polarity:.2f})")
            return {
                "stance": stance,
                "confidence": 0.45 + abs(polarity) * 0.3,
                "method": "sentiment_fallback",
                "neighbors": [],
                "signals": signals
            }
        
        # ---- 全都不行 → 中性 ----
        signals.append("无明确信号，默认中性")
        return {
            "stance": "neutral",
            "confidence": 0.3,
            "method": "default_neutral",
            "neighbors": [],
            "signals": signals
        }

    def add_prototype(self, text: str, stance: str, source: str = ""):
        """添加一个经过验证的样本到原型池"""
        fingerprint = self._text_fingerprint(text)
        
        # 检查是否已有相似原型
        for existing in self.prototype_pool:
            if existing["fingerprint"] == fingerprint:
                existing["count"] += 1
                existing["sources"].append(source)
                return
        
        # 新增
        self.prototype_pool.append({
            "fingerprint": fingerprint,
            "stance": stance,
            "text_sample": text[:100],
            "source": source,
            "count": 1,
            "sources": [source] if source else []
        })
        
        # 限制池大小
        if len(self.prototype_pool) > self.max_prototypes:
            # 移除非活跃的（count最低的）
            self.prototype_pool.sort(key=lambda x: x["count"])
            self.prototype_pool = self.prototype_pool[-self.max_prototypes:]

    def _knn_classify(self, text: str) -> Optional[Dict]:
        """基于原型池做KNN分类"""
        fp = self._text_fingerprint(text)
        k = min(5, len(self.prototype_pool))
        
        # 计算与每个原型的文本相似度
        scored = []
        for proto in self.prototype_pool:
            sim = self._fingerprint_similarity(fp, proto["fingerprint"])
            scored.append((sim, proto["stance"], proto))
        
        # 取top-K
        scored.sort(key=lambda x: x[0], reverse=True)
        top_k = scored[:k]
        
        # 统计立场分布
        stance_counts = defaultdict(float)
        for sim, stance, _ in top_k:
            stance_counts[stance] += sim  # 加权投票
        
        total_weight = sum(stance_counts.values())
        if total_weight == 0:
            return None
        
        best_stance = max(stance_counts, key=stance_counts.get)
        best_weight = stance_counts[best_stance] / total_weight
        
        # 检查第二名
        sorted_stances = sorted(stance_counts.items(), key=lambda x: x[1], reverse=True)
        if len(sorted_stances) >= 2:
            second_ratio = sorted_stances[1][1] / total_weight
        else:
            second_ratio = 0
        
        # 如果第一名明显领先
        if best_weight - second_ratio > 0.3:
            return {
                "stance": best_stance,
                "confidence": best_weight,
                "neighbor_count": len(top_k),
                "neighbors": [(s, st, round(ss, 3)) for ss, st, _ in top_k[:3]]
            }
        
        return None

    def _keyword_classify(self, text: str) -> Dict:
        """关键词匹配分类"""
        best_stance = None
        best_count = 0
        matched_words = []
        
        for stance, keywords in self.keyword_map.items():
            count = 0
            matched = []
            for kw in keywords:
                if kw in text:
                    count += 1
                    matched.append(kw)
            if count > best_count:
                best_count = count
                best_stance = stance
                matched_words = matched
        
        if best_count > 0:
            # 置信度随匹配词数递增
            confidence = min(0.95, 0.4 + best_count * 0.15)
            return {
                "stance": best_stance,
                "confidence": confidence,
                "matched": True,
                "matched_words": matched_words[:3]
            }
        
        return {"matched": False, "stance": "neutral", "confidence": 0.3}

    def _check_evasive(self, text: str) -> Dict:
        """检测逃避信号"""
        evasion_signals = [
            "不予置评", "不方便回答", "不想多谈", "无可奉告",
            "no comment", "不便回应", "暂时不方便",
            "跳过这个问题", "下一个问题"
        ]
        
        for signal in evasion_signals:
            if signal in text:
                return {"detected": True, "signal": signal}
        
        # 条件句逃避
        conditional_ratio = self._calc_conditional_ratio(text)
        if conditional_ratio > 0.3:
            return {"detected": True, "signal": f"高条件句密度({conditional_ratio:.0%})"}
        
        return {"detected": False}

    def _calc_conditional_ratio(self, text: str) -> float:
        """计算条件句密度"""
        conditionals = ["如果", "假如", "要是", "除非", "只要", "if", "unless"]
        count = sum(1 for c in conditionals if c in text)
        sentences = re.split(r'[。！？.!?\n]', text)
        return count / max(1, len(sentences))

    def _sentiment_polarity(self, text: str) -> float:
        """简易情感极性分析"""
        positive = {"好": 0.3, "棒": 0.5, "优秀": 0.5, "厉害": 0.4,
                    "不错": 0.3, "满意": 0.4, "欣赏": 0.4, "期待": 0.3}
        negative = {"差": -0.3, "糟糕": -0.5, "失望": -0.4, "不满": -0.4,
                    "批评": -0.4, "拒绝": -0.3, "质疑": -0.3, "反对": -0.5}
        
        score = 0.0
        for word, val in positive.items():
            if word in text:
                score += val
        for word, val in negative.items():
            if word in text:
                score += val
        
        return max(-1.0, min(1.0, score))

    def _text_fingerprint(self, text: str) -> str:
        """生成文本指纹（去停用词的关键词集合排序后哈希）"""
        stopwords = {"的", "了", "是", "在", "和", "就", "都", "而",
                     "及", "与", "着", "或", "一个", "没有", "我们",
                     "你们", "他们", "这个", "那个", "什么", "怎么",
                     "因为", "所以", "可以", "the", "a", "an", "is",
                     "are", "was", "were", "in", "on", "at", "to",
                     "for", "of", "with", "and", "or", "but"}
        
        # 提取有意义的词
        words = re.findall(r'[\u4e00-\u9fff]{2,}|[a-zA-Z]{3,}', text.lower())
        filtered = sorted([w for w in words if w not in stopwords])
        return "|".join(filtered[:20])  # 限长

    def _fingerprint_similarity(self, fp1: str, fp2: str) -> float:
        """计算两个指纹的相似度（Jaccard）"""
        if not fp1 or not fp2:
            return 0.0
        set1 = set(fp1.split("|"))
        set2 = set(fp2.split("|"))
        inter = set1 & set2
        union = set1 | set2
        return len(inter) / len(union) if union else 0.0


# ============================================================
# 导出接口
# ============================================================

classifier = KNNStanceClassifier()

def classify_stance(text: str, topic: str = None) -> Dict:
    """一键立场分类"""
    return classifier.classify(text, topic)

def add_training_sample(text: str, stance: str, source: str = ""):
    """添加训练样本"""
    classifier.add_prototype(text, stance, source)

if __name__ == "__main__":
    print("🧠 KNN立场分类器加载完成")
    print(f"  - 原型池: 当前 {len(classifier.prototype_pool)} 条")
    print(f"  - 关键词兜底: {sum(len(v) for v in classifier.keyword_map.values())} 条")
    print(f"  - 分类策略: KNN原型 → 关键词 → 情感极性")