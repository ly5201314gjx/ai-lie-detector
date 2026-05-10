"""
scoring_ensemble.py — 综合评分集成 (优化7: 贝叶斯置信区间评分)
从确定性评分升级为概率分布评分
"""

import math
import random
from typing import List, Dict, Optional, Tuple


class BayesianScoringEnsemble:
    """
    贝叶斯评分集成器 v2.0
    
    升级内容：
    - 从确定性"72分" → "72分 (90%置信: 65-79)"
    - 基于贝叶斯后验估计
    - 数据量少时置信区间宽，数据多时收窄
    """
    
    def __init__(self):
        # 扣分权重
        self.penalty_weights = {
            "direct_contradictions": 35,
            "temporal_inconsistencies": 20,
            "linguistic_evasion": 15,
            "quantitative_mismatch": 10,
            "commitment_decay": 15
        }
        
        # 加分权重
        self.bonus_weights = {
            "context_resolution": 15,
            "longitudinal_stability": 20,
            "source_diversity": 5
        }
        
        # 贝叶斯先验参数
        self.prior_mean = 65.0        # 普通人先验一致性均值
        self.prior_std = 15.0          # 先验标准差
        self.prior_precision = 1.0 / (self.prior_std ** 2)  # 先验精度
        
        # 观测噪声
        self.observation_noise_std = 12.0  # 观测噪声标准差
        self.observation_precision = 1.0 / (self.observation_noise_std ** 2)
        
        # 评级
        self.ratings = [
            (85, 100, "卓越", "🟢⭐⭐⭐", "高度一致 — 言论可信度高"),
            (70, 85, "良好", "🟢⭐", "基本一致 — 存在少量波动"),
            (50, 70, "中等", "🟡⚠️", "部分一致 — 发现一定矛盾"),
            (30, 50, "差等", "🟠🔴", "明显不一致 — 存在严重矛盾"),
            (0, 30, "危急", "🔴🚨", "严重不一致 — 系统性问题")
        ]

    def score(self, contradictions: List[Dict] = None,
              linguistic_risk: float = 0.0,
              statement_count: int = 0,
              source_count: int = 0,
              stability_years: float = 0.0,
              bayesian: bool = True) -> Dict:
        """
        综合评分（支持贝叶斯模式）
        
        Args:
            contradictions: 矛盾列表（含adjusted_severity）
            linguistic_risk: 语言风险 [0,1]
            statement_count: 言论总数
            source_count: 去重来源数
            stability_years: 稳定年数
            bayesian: 是否启用贝叶斯区间
            
        Returns:
            评分结果（含置信区间）
        """
        base_score = 100.0
        
        # ---- 扣分（同v1.0计算逻辑）----
        direct_penalty = self._calc_direct_penalty(contradictions)
        temporal_penalty = self._calc_temporal_penalty(contradictions)
        linguistic_penalty = linguistic_risk * self.penalty_weights["linguistic_evasion"]
        quant_penalty = self._calc_quant_penalty(contradictions)
        commitment_penalty = self._calc_commitment_penalty(contradictions)
        
        # ---- 加分 ----
        context_bonus = self._calc_context_bonus(contradictions)
        stability_bonus = self._calc_stability_bonus(stability_years)
        diversity_bonus = self._calc_diversity_bonus(statement_count, source_count)
        
        # ---- 确定性评分 ----
        point_estimate = (base_score 
                        - direct_penalty - temporal_penalty 
                        - linguistic_penalty - quant_penalty - commitment_penalty
                        + context_bonus + stability_bonus + diversity_bonus)
        point_estimate = max(0, min(100, point_estimate))
        
        # ---- 贝叶斯后验（置信区间）----
        if bayesian:
            posterior = self._bayesian_update(
                point_estimate=point_estimate,
                n_statements=statement_count,
                n_sources=source_count,
                n_contradictions=len(contradictions) if contradictions else 0
            )
            
            final_score = round(posterior["mean"], 1)
            ci_lower = round(max(0, posterior["ci_lower"]), 1)
            ci_upper = round(min(100, posterior["ci_upper"]), 1)
            uncertainty = posterior["uncertainty_label"]
        else:
            final_score = round(point_estimate, 1)
            ci_lower = None
            ci_upper = None
            uncertainty = "确定性评分（未启用贝叶斯）"
        
        # 评级
        rating = self._get_rating(final_score)
        
        # 分项分解
        breakdown = {
            "base_score": 100,
            "penalties": {
                "direct_contradictions": round(-direct_penalty, 1),
                "temporal_inconsistencies": round(-temporal_penalty, 1),
                "linguistic_evasion": round(-linguistic_penalty, 1),
                "quantitative_mismatch": round(-quant_penalty, 1),
                "commitment_decay": round(-commitment_penalty, 1),
                "total_penalty": round(-(direct_penalty + temporal_penalty + 
                                        linguistic_penalty + quant_penalty + commitment_penalty), 1)
            },
            "bonuses": {
                "context_resolution": round(context_bonus, 1),
                "longitudinal_stability": round(stability_bonus, 1),
                "source_diversity": round(diversity_bonus, 1),
                "total_bonus": round(context_bonus + stability_bonus + diversity_bonus, 1)
            }
        }
        
        result = {
            "final_score": final_score,
            "rating": rating,
            "breakdown": breakdown,
            "bayesian": {
                "enabled": bayesian,
                "prior": f"N({self.prior_mean}, {self.prior_std}²)",
                "point_estimate": round(point_estimate, 1),
                "posterior_mean": round(posterior["mean"], 1) if bayesian else None,
                "confidence_interval": f"{ci_lower} - {ci_upper}" if ci_lower else None,
                "ci_lower": ci_lower,
                "ci_upper": ci_upper,
                "interval_width": round(ci_upper - ci_lower, 1) if ci_lower else None,
                "uncertainty": uncertainty,
                "data_quality": self._data_quality(statement_count, source_count)
            },
            "raw_inputs": {
                "contradiction_count": len(contradictions) if contradictions else 0,
                "linguistic_risk": round(linguistic_risk, 3),
                "statement_count": statement_count,
                "source_count": source_count,
                "stability_years": stability_years
            }
        }
        
        return result

    def _bayesian_update(self, point_estimate: float, 
                         n_statements: int,
                         n_sources: int,
                         n_contradictions: int) -> Dict:
        """
        贝叶斯后验更新
        
        模型：
           先验: θ ~ N(μ₀, σ₀²)  其中 μ₀=65, σ₀=15
           似然: x|θ ~ N(θ, σ²/n) 其中 σ=观测噪声
           后验: θ|x ~ N(μₙ, σₙ²)
           
           其中:
             μₙ = (μ₀/σ₀² + x̄·n/σ²) / (1/σ₀² + n/σ²)
             σₙ² = 1 / (1/σ₀² + n/σ²)
        """
        # 有效样本量（考虑来源多样性和矛盾数量对信心的影响）
        effective_n = self._effective_sample_size(n_statements, n_sources, n_contradictions)
        
        if effective_n < 1:
            effective_n = 1.0
        
        # 观测噪声（随有效样本量减小）
        observation_var = self.observation_noise_std ** 2
        noise_var_effective = observation_var / effective_n
        
        # 后验均值
        prior_var = self.prior_std ** 2
        post_precision = 1.0 / prior_var + 1.0 / noise_var_effective
        post_var = 1.0 / post_precision
        
        post_mean = ((self.prior_mean / prior_var) + 
                    (point_estimate / noise_var_effective)) / post_precision
        
        # 90%置信区间（正态近似）
        z_score = 1.645  # 90% CI
        ci_half_width = z_score * math.sqrt(post_var)
        
        # 不确定性标签
        uncertainty_label = self._uncertainty_label(post_var, effective_n)
        
        return {
            "mean": post_mean,
            "variance": post_var,
            "std": math.sqrt(post_var),
            "ci_lower": post_mean - ci_half_width,
            "ci_upper": post_mean + ci_half_width,
            "effective_sample_size": round(effective_n, 1),
            "uncertainty_label": uncertainty_label
        }

    def _effective_sample_size(self, n_statements: int, 
                                n_sources: int,
                                n_contradictions: int) -> float:
        """
        计算有效样本量
        
        原则：
        - 言论越多越好，但边际效用递减
        - 来源多样更好
        - 矛盾太多说明数据质量有问题
        """
        # 基础：言论数的对数
        base_n = math.log2(n_statements + 1) * 3
        
        # 来源多样性加权
        source_factor = math.log2(n_sources + 1) * 2
        
        # 矛盾惩罚：太多矛盾说明评分本身就不准
        contradiction_penalty = max(0, 1.0 - n_contradictions * 0.02)
        
        effective = (base_n + source_factor) * contradiction_penalty
        
        # 封顶
        return min(50, max(1, effective))

    def _uncertainty_label(self, post_var: float, effective_n: float) -> str:
        """不确定性标签"""
        post_std = math.sqrt(post_var)
        
        if effective_n < 5:
            return f"🔴 极高不确定性 (有效样本仅{effective_n:.0f})"
        elif effective_n < 10:
            return f"🟡 高不确定性 (有效样本{effective_n:.0f})"
        elif effective_n < 20:
            return f"🟢 中等不确定性 (有效样本{effective_n:.0f})"
        else:
            return f"✅ 低不确定性 (有效样本{effective_n:.0f})"

    def _data_quality(self, n_statements: int, n_sources: int) -> str:
        """数据质量评估"""
        if n_statements >= 50 and n_sources >= 5:
            return "⭐⭐⭐ 高质量 - 数据充分，结论可靠"
        elif n_statements >= 20 and n_sources >= 3:
            return "⭐⭐ 中等质量 - 数据基本充足"
        elif n_statements >= 5:
            return "⭐ 低质量 - 数据有限，结果仅供参考"
        else:
            return "❌ 极低质量 - 数据严重不足，请谨慎引用"

    def _calc_direct_penalty(self, contradictions: List[Dict]) -> float:
        if not contradictions:
            return 0.0
        direct = [c for c in contradictions if c.get("type") == "direct_flip"]
        if not direct:
            return 0.0
        penalty = sum(c.get("adjusted_severity", c.get("severity", 0)) for c in direct)
        return min(penalty * 35 / 3, self.penalty_weights["direct_contradictions"])

    def _calc_temporal_penalty(self, contradictions: List[Dict]) -> float:
        if not contradictions:
            return 0.0
        temporal = [c for c in contradictions if c.get("type") in ["abrupt_change", "gradual_drift"]]
        if not temporal:
            return 0.0
        penalty = sum(c.get("adjusted_severity", c.get("severity", 0)) for c in temporal)
        return min(penalty * 20 / 3, self.penalty_weights["temporal_inconsistencies"])

    def _calc_quant_penalty(self, contradictions: List[Dict]) -> float:
        if not contradictions:
            return 0.0
        quant = [c for c in contradictions if c.get("type") == "quantitative_mismatch"]
        if not quant:
            return 0.0
        return min(len(quant) * 3, self.penalty_weights["quantitative_mismatch"])

    def _calc_commitment_penalty(self, contradictions: List[Dict]) -> float:
        if not contradictions:
            return 0.0
        commitment = [c for c in contradictions if c.get("type") == "commitment_decay"]
        if not commitment:
            return 0.0
        penalty = sum(c.get("adjusted_severity", c.get("severity", 0)) for c in commitment)
        return min(penalty * 15 / 2, self.penalty_weights["commitment_decay"])

    def _calc_context_bonus(self, contradictions: List[Dict]) -> float:
        if not contradictions:
            return 0.0
        justified = [c for c in contradictions 
                    if c.get("context_analysis", {}).get("justification_score", 0) > 0.5]
        if not justified:
            return 0.0
        avg = sum(c["context_analysis"]["justification_score"] for c in justified) / len(justified)
        return avg * self.bonus_weights["context_resolution"]

    def _calc_stability_bonus(self, stability_years: float) -> float:
        if stability_years >= 2:
            return self.bonus_weights["longitudinal_stability"]
        elif stability_years >= 1:
            return self.bonus_weights["longitudinal_stability"] / 2
        return 0.0

    def _calc_diversity_bonus(self, stmt_count: int, src_count: int) -> float:
        expected = max(3, stmt_count / 5)
        ratio = min(1.0, src_count / expected) if expected > 0 else 0
        return ratio * self.bonus_weights["source_diversity"]

    def _get_rating(self, score: float) -> Dict:
        for lo, hi, label, icon, desc in self.ratings:
            if lo <= score <= hi:
                return {"label": label, "icon": icon, "description": desc, "score_range": f"{lo}-{hi}"}
        return {"label": "未知", "icon": "❓", "description": ""}


# ============================================================
# 导出接口
# ============================================================

def compute_score(contradictions: List[Dict] = None,
                  linguistic_risk: float = 0.0,
                  statement_count: int = 0,
                  source_count: int = 0,
                  stability_years: float = 0.0,
                  bayesian: bool = True) -> Dict:
    """一键评分（v2.0贝叶斯版）"""
    engine = BayesianScoringEnsemble()
    return engine.score(contradictions, linguistic_risk,
                        statement_count, source_count, stability_years, bayesian)


if __name__ == "__main__":
    print("📊 贝叶斯评分集成器 v2.0加载完成")
    engine = BayesianScoringEnsemble()
    print(f"  - 先验分布: N({engine.prior_mean}, {engine.prior_std}²)")
    print(f"  - 置信水平: 90%")
    print(f"  - 有效样本量算法: 对数加权+来源多样性+矛盾惩罚")
    print(f"  - 不确定性分级: 4级")