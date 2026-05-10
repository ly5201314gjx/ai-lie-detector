"""
text_utils.py — 文本处理工具函数
"""

import re
from typing import List, Dict, Optional, Set


def deduplicate_statements(statements: List[Dict], 
                           threshold: float = 0.85) -> List[Dict]:
    """
    去重：基于文本相似度合并重复言论
    
    Args:
        statements: 言论列表
        threshold: 相似度阈值，超过即视为重复
        
    Returns:
        去重后的言论列表
    """
    if not statements:
        return []
    
    unique = []
    
    for stmt in statements:
        is_dup = False
        text = stmt.get("text", "")
        
        for existing in unique:
            existing_text = existing.get("text", "")
            sim = _text_similarity(text, existing_text)
            if sim > threshold:
                is_dup = True
                # 合并来源信息
                if "sources" not in existing:
                    existing["sources"] = [existing.get("source_url", "")]
                new_url = stmt.get("source_url", "")
                if new_url and new_url not in existing["sources"]:
                    existing["sources"].append(new_url)
                break
        
        if not is_dup:
            unique.append(stmt)
    
    print(f"📦 去重: {len(statements)} → {len(unique)} (去除 {len(statements)-len(unique)} 条重复)")
    return unique


def _text_similarity(t1: str, t2: str) -> float:
    """
    计算两段文本的相似度
    使用 Jaccard 相似度（基于字符级n-gram）
    """
    if not t1 or not t2:
        return 0.0
    
    # 使用3-gram
    def get_ngrams(text, n=3):
        text = text.lower()
        return set(text[i:i+n] for i in range(len(text) - n + 1))
    
    grams1 = get_ngrams(t1)
    grams2 = get_ngrams(t2)
    
    if not grams1 or not grams2:
        return 0.0
    
    intersection = grams1 & grams2
    union = grams1 | grams2
    
    return len(intersection) / len(union) if union else 0.0


def extract_named_entities(text: str) -> Dict[str, List[str]]:
    """
    简易命名实体提取
    
    Returns:
        {"person": [...], "org": [...], "location": [...], "date": [...], "number": [...]}
    """
    result = {
        "person": [],
        "org": [],
        "location": [],
        "date": [],
        "number": []
    }
    
    # 日期
    date_patterns = [
        r'\d{4}年\d{1,2}月\d{1,2}日',
        r'\d{4}年\d{1,2}月',
        r'\d{4}年',
        r'\d{4}-\d{1,2}-\d{1,2}'
    ]
    for pat in date_patterns:
        result["date"].extend(re.findall(pat, text))
    
    # 数字
    nums = re.findall(r'\d+\.?\d*', text)
    result["number"] = [n for n in nums if len(n) >= 1]
    
    # 英文人名（大写开头词序列）
    en_names = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
    if en_names:
        result["person"].extend(en_names)
    
    return result


def extract_key_sentences(text: str, max_sentences: int = 3) -> List[str]:
    """
    提取关键句子（基于位置 + 长度）
    """
    if not text:
        return []
    
    sentences = re.split(r'[。！？.!?\n]', text)
    sentences = [s.strip() for s in sentences if s.strip() and len(s.strip()) > 10]
    
    if len(sentences) <= max_sentences:
        return sentences
    
    # 取前1~2句（通常最有信息量）+ 随机抽取
    selected = []
    
    # 第一句
    if sentences:
        selected.append(sentences[0])
    
    # 如果有第二句且长度合理
    if len(sentences) >= 2 and len(sentences[1]) > 15:
        selected.append(sentences[1])
    
    # 从中间选一句
    if len(sentences) >= 4:
        mid = len(sentences) // 2
        if sentences[mid] not in selected:
            selected.append(sentences[mid])
    
    # 最后一句
    if len(sentences) >= 3:
        last = sentences[-1]
        if last not in selected:
            selected.append(last)
    
    return selected[:max_sentences]


def truncate_text(text: str, max_length: int = 150) -> str:
    """截断文本到指定长度"""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."


def detect_language(text: str) -> str:
    """检测文本语言"""
    if not text:
        return "unknown"
    
    chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
    english_chars = len(re.findall(r'[a-zA-Z]', text))
    
    if chinese_chars > english_chars:
        return "zh"
    elif english_chars > chinese_chars:
        return "en"
    else:
        return "mixed"


if __name__ == "__main__":
    print("🛠️  文本工具模块加载完成")
    print(f"  - 3-gram去重算法: Jaccard相似度")
    print(f"  - 命名实体提取: 5类")