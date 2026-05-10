"""
topic_modeler.py — 话题建模与立场提取 (算法一)
"""

import re
import json
from typing import List, Dict, Optional, Tuple
from collections import defaultdict, Counter


class TopicModeler:
    """话题建模与立场提取器"""
    
    def __init__(self, topic_keywords: Dict = None, stance_lexicon: Dict = None):
        self.topic_keywords = topic_keywords or {}
        self.stance_lexicon = stance_lexicon or {}
        self._load_defaults()

    def _load_defaults(self):
        """加载默认关键词（如果没有外部数据）"""
        if not self.topic_keywords:
            self.topic_keywords = {
                "职业生涯": ["转型", "突破", "发展", "规划", "瓶颈", "成长", "进步"],
                "演技评价": ["演技", "表演", "角色", "演员", "塑造", "情感", "表达"],
                "作品票房": ["票房", "收视", "口碑", "收视率", "票房", "评分"],
                "争议回应": ["争议", "道歉", "回应", "澄清", "误会", "指责", "批评"],
                "合作团队": ["合作", "导演", "团队", "搭档", "制片", "剧组"],
                "个人生活": ["家庭", "父母", "童年", "学校", "成长", "生活"],
                "行业观点": ["行业", "市场", "趋势", "发展", "未来", "机会"],
            }

        if not self.stance_lexicon:
            self.stance_lexicon = {
                "strongly_support": ["坚决支持", "完全赞同", "绝对拥护", "坚定不移"],
                "support": ["支持", "赞同", "同意", "认可", "肯定", "看好"],
                "neutral": ["不确定", "不好说", "不知道", "没意见", "保持中立"],
                "oppose": ["反对", "不同意", "不赞同", "不认可", "质疑"],
                "strongly_oppose": ["坚决反对", "强烈反对", "严词谴责"],
                "evasive": ["不予置评", "不方便回答", "不想多谈", "无可奉告"]
            }

    def extract_topics(self, statements: List[Dict]) -> Dict:
        """
        从言论中提取话题并分类
        
        Returns:
            {topic_name: {"count": n, "statements": [...], "key_phrases": [...]}}
        """
        topic_map = defaultdict(list)
        
        for stmt in statements:
            text = stmt.get("text", "")
            if not text:
                continue
            
            matched_topics = []
            for topic, keywords in self.topic_keywords.items():
                for kw in keywords:
                    if kw in text:
                        matched_topics.append(topic)
                        break
            
            if matched_topics:
                stmt["topics"] = matched_topics
                for topic in matched_topics:
                    topic_map[topic].append(stmt)
            else:
                # 标记为"其他"
                stmt["topics"] = ["综合"]
                topic_map["综合"].append(stmt)
        
        # 聚合统计
        result = {}
        for topic, stmts in topic_map.items():
            # 提取关键词频
            all_text = " ".join([s.get("text", "") for s in stmts])
            words = self._tokenize(all_text)
            word_freq = Counter(words)
            
            # 高频内容词
            stopwords = {"的", "了", "是", "在", "和", "就", "都", "而", "及", 
                        "与", "着", "或", "一个", "没有", "我们", "你们", "他们",
                        "这个", "那个", "什么", "怎么", "因为", "所以", "可以"}
            content_words = [w for w in word_freq if w not in stopwords and len(w) > 1]
            top_kws = word_freq.most_common(10)
            
            result[topic] = {
                "count": len(stmts),
                "ratio": round(len(stmts) / max(1, len(statements)), 3),
                "key_phrases": content_words[:5],
                "statements": stmts
            }
        
        return result

    def classify_stance(self, text: str, topic: str = None) -> str:
        """
        对文本进行立场分类
        
        Returns:
            strongly_support / support / neutral / oppose / strongly_oppose / evasive
        """
        if not text:
            return "neutral"
        
        # 1. 检查逃避信号（优先检查）
        evasive_signals = ["不予置评", "不方便回答", "不想多谈", "无可奉告", 
                          "跳过这个问题", "no comment"]
        for signal in evasive_signals:
            if signal in text:
                return "evasive"
        
        # 2. 立场关键词匹配
        stance_scores = {}
        for stance, keywords in self.stance_lexicon.items():
            score = 0
            for kw in keywords:
                if kw in text:
                    score += 1
            if score > 0:
                stance_scores[stance] = score
        
        if stance_scores:
            # 取最高分立场
            return max(stance_scores, key=stance_scores.get)
        
        # 3. 情感极性兜底
        positive = ["好", "棒", "优秀", "厉害", "不错", "满意", "欣赏",
                    "喜欢", "爱", "感动", "值得", "期待"]
        negative = ["差", "糟糕", "失望", "不满", "批评", "拒绝",
                    "讨厌", "反感", "质疑", "反对"]
        
        pos_count = sum(1 for w in positive if w in text)
        neg_count = sum(1 for w in negative if w in text)
        
        if pos_count > neg_count:
            return "support"
        elif neg_count > pos_count:
            return "oppose"
        else:
            return "neutral"

    def annotate_statements(self, statements: List[Dict]) -> List[Dict]:
        """
        批量标注言论：话题 + 立场
        
        Returns:
            标注后的言论列表
        """
        annotated = []
        
        # 先提取话题
        topics = self.extract_topics(statements)
        
        for stmt in statements:
            text = stmt.get("text", "")
            
            # 立场分类
            stance = self.classify_stance(text)
            stmt["stance"] = stance
            
            # 话题标记
            if "topics" not in stmt:
                stmt["topics"] = ["综合"]
            
            annotated.append(stmt)
        
        return annotated

    def _tokenize(self, text: str) -> List[str]:
        """简易分词"""
        tokens = re.findall(r'[\u4e00-\u9fff]+|[a-zA-Z]+|\d+', text)
        return tokens


def annotate_all(statements: List[Dict]) -> List[Dict]:
    """一键标注"""
    modeler = TopicModeler()
    return modeler.annotate_statements(statements)


def get_topic_distribution(statements: List[Dict]) -> Dict:
    """获取话题分布"""
    modeler = TopicModeler()
    return modeler.extract_topics(statements)


if __name__ == "__main__":
    print("🏷️  话题建模器模块加载完成")
    print(f"  - 话题类别: {len(TopicModeler().topic_keywords)} 类")
    print(f"  - 立场分类: {len(TopicModeler().stance_lexicon)} 种")