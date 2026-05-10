"""
statement_collector.py — 多平台言论数据采集器
支持从搜索引擎、社交媒体、新闻平台采集公开言论
"""

import json
import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from urllib.parse import quote, urlparse


# ============================================================
# 搜索查询构造
# ============================================================

class SearchQueryBuilder:
    """构造针对不同目标类别的搜索查询"""
    
    @staticmethod
    def build_queries(target: str, topic: str = None, 
                      time_range: str = "3年") -> List[str]:
        """
        构建多维度搜索查询
        
        Args:
            target: 目标人物名
            topic: 可选话题限定
            time_range: 时间范围（如 "3年", "2024-2026"）
        """
        queries = []
        
        # 基础采访/访谈类
        base_patterns = [
            f"{target} 采访",
            f"{target} 访谈",
            f"{target} 专访",
            f"{target} 回应",
            f"{target} 声明",
            f"{target} 发言",
            f"{target} 演讲",
        ]
        
        # 媒体/发布会类
        media_patterns = [
            f"{target} 发布会",
            f"{target} 媒体采访",
            f"{target} 记者会",
            f"{target} 公开信",
            f"{target} 社交平台 发言",
        ]
        
        # 如果指定话题，增加话题限定查询
        if topic:
            topic_patterns = [
                f"{target} 谈 {topic}",
                f"{target} {topic} 观点",
                f"{target} {topic} 回应",
                f"{target} {topic} 采访",
            ]
            queries.extend(topic_patterns)
        
        queries.extend(base_patterns)
        queries.extend(media_patterns)
        
        # 英文搜索（适用于国际人物）
        en_patterns = [
            f"{target} interview",
            f"{target} statement",
            f"{target} says",
            f"{target} responds",
            f"{target} press conference",
        ]
        queries.extend(en_patterns)
        
        return queries

    @staticmethod
    def build_topic_specific(target: str, topic: str) -> List[str]:
        """针对特定话题构建深度查询"""
        return [
            f"{target} {topic} 观点 立场",
            f"{target} 谈{topic}",
            f"{target} {topic} 最新回应",
            f"{target} {topic} 采访 全文",
            f"{target} {topic} 博客 文章",
            f"'{target}' '{topic}' interview transcript",
        ]


# ============================================================
# 言论提取与规范化
# ============================================================

class StatementExtractor:
    """从搜索结果中提取言论内容"""
    
    def __init__(self):
        # 中文引号模式
        self.quote_patterns_cn = [
            r'「([^」]+)」',
            r'『([^』]+)』',
            r'"([^"]+)"',
            r'"([^"]+)"',
            r'"』',
            r'"',
            r'',
        ]
        
    def extract_quotes(self, text: str) -> List[str]:
        """从文本中提取引号内的言论"""
        quotes = []
        
        # 中文引号
        cn_matches = re.findall(r'[""]([^""]+)[""]', text)
        quotes.extend(cn_matches)
        
        # 英文引号
        en_matches = re.findall(r'"([^"]+)"', text)
        quotes.extend(en_matches)
        
        # 单引号
        single_matches = re.findall(r""'([^']+)'""", text)
        quotes.extend(single_matches)
        
        return [q.strip() for q in quotes if len(q.strip()) > 10]

    def extract_date(self, text: str, url: str = "") -> Optional[str]:
        """从文本或URL中提取日期"""
        # URL中的日期模式 (如 /2024/03/15/)
        url_date = re.search(r'/(20\d{2})/(\d{1,2})/(\d{1,2})/', url)
        if url_date:
            return f"{url_date.group(1)}-{url_date.group(2).zfill(2)}-{url_date.group(3).zfill(2)}"
        
        # 文本中的日期
        patterns = [
            r'(\d{4})年(\d{1,2})月(\d{1,2})日',
            r'(\d{4})-(\d{1,2})-(\d{1,2})',
            r'(\d{4})/(\d{1,2})/(\d{1,2})',
            r'(\d{1,2})月(\d{1,2})日',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                groups = match.groups()
                if len(groups) == 3:
                    return f"{groups[0]}-{groups[1].zfill(2)}-{groups[2].zfill(2)}"
        return None

    def extract_source_media(self, url: str, title: str = "") -> str:
        """从URL提取来源媒体名称"""
        domain = urlparse(url).netloc
        # 移除 www. 前缀
        domain = re.sub(r'^www\.', '', domain)
        # 提取主域名
        main_domain = domain.split('.')[0] if domain else "未知来源"
        
        # 常见媒体域名映射
        media_map = {
            "163": "网易",
            "sohu": "搜狐",
            "sina": "新浪",
            "qq": "腾讯",
            "people": "人民网",
            "xinhuanet": "新华网",
            "chinanews": "中新网",
            "thepaper": "澎湃新闻",
            "bjnews": "新京报",
            "caixin": "财新网",
            "36kr": "36氪",
            "huxiu": "虎嗅",
            "weibo": "微博",
            "zhihu": "知乎",
            "bilibili": "B站",
            "douban": "豆瓣",
        }
        
        for key, name in media_map.items():
            if key in domain:
                return name
        
        return domain

    def normalize_statement(self, text: str, url: str = "",
                            title: str = "", date: str = None) -> Dict:
        """规范化单条言论"""
        return {
            "text": text.strip(),
            "source_url": url,
            "source_media": self.extract_source_media(url, title),
            "source_title": title,
            "date": date or self.extract_date(text, url) or "日期未知",
            "length": len(text.strip()),
            "language": "zh" if re.search(r'[\u4e00-\u9fff]', text) else "en"
        }


# ============================================================
# 言论采集主函数
# ============================================================

async def collect_statements(target: str, topic: str = None,
                              max_queries: int = 5) -> List[Dict]:
    """
    异步多源采集言论
    通过调用搜索引擎获取目标人物的公开言论
    
    Args:
        target: 目标人物
        topic: 话题限定
        max_queries: 最多并发搜索数
        
    Returns:
        规范化后的言论列表
    """
    from .text_utils import deduplicate_statements
    
    queries = SearchQueryBuilder.build_queries(target, topic)
    queries = queries[:max_queries]  # 限制并发数
    
    # 这里通过AI调用搜索引擎工具实现
    # 实际搜索由上层调用 search_web 工具完成
    # 本模块负责构造查询和处理结果
    
    extractor = StatementExtractor()
    
    print(f"🔍 言论采集器就绪")
    print(f"🎯 目标: {target}")
    print(f"📝 构建查询: {len(queries)} 条")
    print(f"   - 采访/访谈类: {len([q for q in queries if '采访' in q or '访谈' in q])} 条")
    print(f"   - 话题限定类: {len([q for q in queries if topic and topic in q])} 条")
    print(f"   - 英文搜索: {len([q for q in queries if q.startswith(tuple('abcdefghijklmnopqrstuvwxyz'))])} 条")
    
    return []


# ============================================================
# 来源可信度评估
# ============================================================

def evaluate_source(url: str, source_db: Dict = None) -> Dict:
    """评估来源可信度"""
    domain = urlparse(url).netloc if url else ""
    
    # 默认评估
    result = {
        "domain": domain,
        "tier": 3,
        "score": 0.5,
        "label": "未评估"
    }
    
    if source_db:
        # 检查域名覆盖
        for key, score in source_db.get("domain_overrides", {}).items():
            if key in domain:
                tier = 1 if score >= 0.85 else (2 if score >= 0.65 else (3 if score >= 0.4 else 4))
                result = {
                    "domain": domain,
                    "tier": tier,
                    "score": score,
                    "label": f"Tier {tier}",
                    "override": True
                }
                return result
    
    return result


if __name__ == "__main__":
    print("📡 言论采集器模块加载完成")
    print(f"  查询构造器: SearchQueryBuilder")
    print(f"  言论提取器: StatementExtractor")
