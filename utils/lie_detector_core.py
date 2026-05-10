"""
lie_detector_core.py — AI测谎仪主控制器 v2.0
集成:KNN立场分类+矛盾交叉矩阵+事件知识图谱+红队检测+说谎者网络+贝叶斯评分
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Optional, Tuple


class LieDetectorCore:
    """主控制器 v2.0"""
    
    def __init__(self, skill_base_path: str = None):
        self.skill_base_path = skill_base_path or "/sdcard/Download/Operit/skills/lie_detector_ai"
        self.data_path = os.path.join(self.skill_base_path, "data")
        self._load_data()
        self.config = self._load_config()
        
        # v2.0 新模块
        self.knn_classifier = None
        self.contradiction_matrix = None
        self.event_graph = None
        self.adversarial_engine = None
        self.network_analyzer = None
        self.temporal_analyzer = None
        self.linguistic_analyzer = None
        self.scoring_engine = None
        self.report_generator = None
        
        self.results = {
            "target": "",
            "time_range": "",
            "version": "2.0.0",
            "topics": {},
            "statements": [],
            "contradictions": [],
            "linguistic_analysis": {},
            "scores": {},
            "final_rating": "",
            "sources": [],
            "matrix_analysis": {},      # 优化2: 交叉矩阵结果
            "red_team_findings": {},    # 优化5: 红队结果
            "network_analysis": {},     # 优化6: 网络分析
            "timeline": [],             # 优化4: 事件注入后的时间线
            "bayesian_interval": None   # 优化7: 贝叶斯区间
        }
    
    def _load_data(self):
        self.deception_patterns = self._load_json("deception_patterns.json")
        self.stance_lexicon = self._load_json("stance_lexicon.json")
        self.source_db = self._load_json("source_reliability_db.json")
        self.topic_keywords = self._load_json("topic_keywords.json")
    
    def _load_json(self, filename: str) -> dict:
        path = os.path.join(self.data_path, filename)
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    
    def _load_config(self) -> dict:
        path = os.path.join(self.skill_base_path, "config.json")
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    
    def _lazy_import_modules(self):
        """延迟加载各模块"""
        if self.knn_classifier is None:
            from knn_stance_classifier import KNNStanceClassifier
            self.knn_classifier = KNNStanceClassifier()
        
        if self.contradiction_matrix is None:
            from contradiction_matrix import ContradictionMatrix
            self.contradiction_matrix = ContradictionMatrix()
        
        if self.event_graph is None:
            from event_graph import EventKnowledgeGraph
            self.event_graph = EventKnowledgeGraph()
        
        if self.adversarial_engine is None:
            from adversarial_search import AdversarialSearchEngine
            self.adversarial_engine = AdversarialSearchEngine()
        
        if self.network_analyzer is None:
            from network_analyzer import NetworkAnalyzer
            self.network_analyzer = NetworkAnalyzer()
        
        if self.temporal_analyzer is None:
            from temporal_analyzer import TemporalAnalyzer
            self.temporal_analyzer = TemporalAnalyzer()
        
        if self.linguistic_analyzer is None:
            from linguistic_analyzer import LinguisticAnalyzer
            self.linguistic_analyzer = LinguisticAnalyzer(self.deception_patterns)
        
        if self.scoring_engine is None:
            from scoring_ensemble import BayesianScoringEnsemble
            self.scoring_engine = BayesianScoringEnsemble()
        
        if self.report_generator is None:
            from report_generator import ReportGenerator
            self.report_generator = ReportGenerator()
    
    def analyze(self, target: str, time_range_months: int = 36,
                topic_filter: str = None, output_format: str = "standard",
                enable_red_team: bool = True,
                enable_bayesian: bool = True,
                enable_network: bool = False):
        """
        全流程分析主入口 v2.0
        
        Args:
            target: 目标人物
            time_range_months: 回溯月数
            topic_filter: 话题过滤
            output_format: quick_scan/standard/full_report/red_team
            enable_red_team: 是否开启红队模式
            enable_bayesian: 是否用贝叶斯评分
            enable_network: 是否开启网络分析
        """
        self._lazy_import_modules()
        
        self.results["target"] = target
        self.results["time_range"] = f"过去{time_range_months}个月"
        self.results["output_format"] = output_format
        
        print(f"=" * 60)
        print(f"🕵️ AI测谎仪 v2.0 — 启动分析")
        print(f"=" * 60)
        print(f"🎯 目标: {target}")
        print(f"⏱️  时间窗口: {time_range_months}个月")
        print(f"📋 输出格式: {output_format}")
        print(f"🔴 红队模式: {'开启' if enable_red_team else '关闭'}")
        print(f"📊 贝叶斯评分: {'开启' if enable_bayesian else '关闭'}")
        print(f"🕸️  网络分析: {'开启' if enable_network else '关闭'}")
        print()
        
        # ---- Phase 1: 数据采集 ----
        print(f"📡 [Phase 1/8] 数据采集...")
        # 由外部搜索引擎完成
        
        # ---- Phase 2: KNN立场分类 ----
        print(f"\n🧠 [Phase 2/8] KNN立场分类...")
        
        # ---- Phase 3: 时间线+事件注入 ----
        print(f"\n⏰ [Phase 3/8] 时间线分析+事件注入...")
        if self.event_graph:
            events = self.event_graph.discover_events(target, time_range_months)
            self.results["events_template"] = events
            print(f"   ✅ 事件知识图谱已准备")
        
        # ---- Phase 4: 6轮矛盾检测 ----
        print(f"\n🔍 [Phase 4/8] 6轮矛盾检测...")
        
        # ---- Phase 5: 矛盾交叉验证矩阵 ----
        print(f"\n🔗 [Phase 5/8] 矛盾交叉验证矩阵...")
        if self.contradiction_matrix:
            print(f"   ✅ 6×6矩阵已就绪，可进行综合症候分析")
        
        # ---- Phase 6: 语言特征分析 ----
        print(f"\n🗣️  [Phase 6/8] 语言特征分析...")
        if self.linguistic_analyzer:
            print(f"   ✅ 7维语言分析已就绪")
        
        # ---- Phase 7: 红队对抗检测 ----
        if enable_red_team and self.adversarial_engine:
            print(f"\n🔴 [Phase 7/8] 红队对抗检测...")
            queries = self.adversarial_engine.generate_adversarial_queries(target)
            # 由外部搜索引擎执行查询
            self.results["red_team_queries"] = queries
            print(f"   ✅ 红队引擎已准备，{len(queries)}条攻击查询")
        
        # ---- Phase 8: 贝叶斯评分 ----
        print(f"\n📊 [Phase 8/8] 综合评分...")
        if self.scoring_engine:
            print(f"   ✅ 贝叶斯评分引擎已就绪")
            print(f"   📌 先验分布: N({self.scoring_engine.prior_mean}, {self.scoring_engine.prior_std}²)")
        
        print(f"\n" + "=" * 60)
        print(f"✅ 分析管道就绪，等待数据流入")
        print(f"=" * 60)
        
        return self.results
    
    def feed_statements(self, statements: List[Dict]):
        """注入言论数据并执行全流程分析"""
        self._lazy_import_modules()
        self.results["statements"] = statements
        self.results["statement_count"] = len(statements)
        
        print(f"\n📦 接收 {len(statements)} 条言论")
        
        # ---- 执行KNN立场分类 ----
        annotated = []
        for s in statements:
            text = s.get("text", "")
            if self.knn_classifier:
                result = self.knn_classifier.classify(text)
                s["stance"] = result["stance"]
                s["stance_confidence"] = result["confidence"]
                s["stance_method"] = result["method"]
                s["stance_signals"] = result.get("signals", [])
            annotated.append(s)
        
        self.results["statements"] = annotated
        
        # ---- 执行时间线分析 ----
        if self.temporal_analyzer and statements:
            timeline = self.temporal_analyzer.build_timeline(annotated)
            self.results["timeline"] = timeline
            
            # 注入事件
            if self.event_graph and self.results.get("events_template"):
                enriched = self.event_graph.inject_events_to_timeline(
                    timeline, self.results["events_template"]
                )
                self.results["timeline"] = enriched
        
        # ---- 执行矛盾检测 ----
        from contradiction_engine import detect_contradictions
        contradictions = detect_contradictions(annotated)
        
        # ---- 执行交叉验证矩阵 ----
        if self.contradiction_matrix:
            matrix_result = self.contradiction_matrix.analyze(contradictions)
            self.results["matrix_analysis"] = matrix_result
            refined = matrix_result["refined"]
            self.results["matrix_cross_insights"] = matrix_result.get("cross_pass_discoveries", [])
        else:
            refined = contradictions
        
        self.results["contradictions"] = refined
        
        # ---- 语言分析 ----
        if self.linguistic_analyzer:
            analysis = self.linguistic_analyzer.analyze(annotated)
            self.results["linguistic_analysis"] = analysis
        
        # ---- 来源统计 ----
        urls = set(s.get("source_url", "") for s in annotated if s.get("source_url"))
        self.results["source_count"] = len(urls)
        
        # ---- 贝叶斯评分 ----
        if self.scoring_engine:
            ling_risk = self.results.get("linguistic_analysis", {}).get("risk_score", 0.0)
            score_result = self.scoring_engine.score(
                contradictions=refined,
                linguistic_risk=ling_risk,
                statement_count=len(annotated),
                source_count=len(urls),
                stability_years=0.5,
                bayesian=True
            )
            self.results["final_score"] = score_result["final_score"]
            self.results["rating"] = score_result["rating"]
            self.results["bayesian_details"] = score_result["bayesian"]
            self.results["score_breakdown"] = score_result["breakdown"]
            self.results["final_rating"] = score_result["rating"]["label"]
            self.results["full_scoring"] = score_result
            self.results["bayesian_interval"] = score_result["bayesian"]["confidence_interval"]
        
        return self.results
    
    def generate_report(self) -> str:
        """生成最终报告"""
        if self.report_generator:
            fmt = self.results.get("output_format", "standard")
            return self.report_generator.generate(self.results, fmt)
        return "报告生成器未加载"


# ============================================================
# 快速接口函数
# ============================================================

def quick_scan(target: str, months: int = 12, topic: str = None,
               red_team: bool = True) -> str:
    """快速扫描模式"""
    engine = LieDetectorCore()
    engine.analyze(target, months, topic, "quick_scan", enable_red_team=red_team)
    return engine.generate_report()


def full_analysis(target: str, months: int = 36, topic: str = None,
                  red_team: bool = True, bayesian: bool = True,
                  network: bool = False) -> Dict:
    """完整分析模式"""
    engine = LieDetectorCore()
    engine.analyze(target, months, topic, "full_report",
                   enable_red_team=red_team, enable_bayesian=bayesian,
                   enable_network=network)
    return engine.results


def compare_persons(persons: List[str], topic: str, months: int = 36) -> Dict:
    """多人对比分析"""
    results = {}
    for person in persons:
        engine = LieDetectorCore()
        engine.analyze(person, months, topic, "comparison_matrix")
        results[person] = engine.results
    return results


if __name__ == "__main__":
    print("=" * 60)
    print("🤖 AI测谎仪 v2.0 - 核心引擎就绪")
    print("=" * 60)
    print(f"\n📦 数据路径: {LieDetectorCore().data_path}")
    print(f"🆕 新功能:")
    print(f"  ✅ 优化1: KNN小样本立场分类器")
    print(f"  ✅ 优化2: 6×6矛盾交叉验证矩阵")
    print(f"  ✅ 优化4: 事件知识图谱注入")
    print(f"  ✅ 优化5: 红队对抗检测引擎")
    print(f"  ✅ 优化6: 说谎者网络分析器")
    print(f"  ✅ 优化7: 贝叶斯置信区间评分")
    print(f"\n✅ v2.0 核心引擎加载完成！")
