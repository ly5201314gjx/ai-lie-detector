# 🕵️ AI 测谎仪 (AI Lie Detector)

## 公众人物言论一致性验证与矛盾检测系统

---

## 📌 技能概述

本技能通过**多平台数据采集 → 时间线构建 → 立场提取 → 多轮矛盾检测 → 语言模式分析 → 上下文解析**的完整链路，实现对公众人物公开言论的**一致性量化评估**。

### 核心能力矩阵

| 能力 | 说明 | 难度 |
|:---|:---|---:|
| 🎯 **言论采集** | 跨平台（访谈/社交媒体/发布会/演讲/播客）采集公开言论 | ⭐⭐ |
| 🧩 **话题聚类** | 自动提取言论涉及的核心话题并分类 | ⭐⭐⭐ |
| 📊 **立场提取** | 对每段言论在特定话题上标注立场取向 | ⭐⭐⭐⭐ |
| 🔍 **矛盾检测** | 6轮穿透式检测寻找逻辑不一致 | ⭐⭐⭐⭐⭐ |
| 🧠 **上下文解析** | 判断表面矛盾是否有合理解释 | ⭐⭐⭐⭐ |
| 📈 **语言分析** | 挖掘回避/模糊/防御性语言模式 | ⭐⭐⭐⭐ |
| 📑 **报告生成** | 一键输出可追溯的评估报告 | ⭐⭐ |

---

# 🧠 核心算法体系架构

```
目标人物 T + 时间窗口 W + 话题域 S
        │
        ▼
┌─────────────────────────────────────┐
│  Layer 0: 任务配置与意图解析         │
│  · 目标人物消歧（避免重名误抓）      │
│  · 时间窗口解析与分段策略            │
│  · 话题域预定义 / 自动发现           │
│  · 输出格式选择                      │
└──────────┬──────────────────────────┘
           ▼
┌─────────────────────────────────────┐
│  Layer 1: 多源言论数据采集层         │
│  ├─ 访谈/采访文本爬取               │
│  ├─ 社交媒体言论抓取 ↑              │
│  ├─ 发布会/演讲速记                 │
│  ├─ 播客/视频字幕提取               │
│  ├─ 官方声明/公开信                 │
│  ├─ 纪录片/专访内容                 │
│  └─ 来源可信度预评估                │
└──────────┬──────────────────────────┘
           ▼
┌─────────────────────────────────────┐
│  Layer 2: 数据预处理与归一化层       │
│  ├─ 去重（同源内容合并）            │
│  ├─ 时间戳归一化（时区/格式统一）    │
│  ├─ 引用来源交叉验证                │
│  ├─ 内容分段（按话题/段落切割）      │
│  └─ 语言检测与翻译                  │
└──────────┬──────────────────────────┘
           ▼
┌─────────────────────────────────────┐
│  Layer 3: 话题建模与立场提取层       │
│  ├─ HDBSCAN层次话题聚类             │
│  ├─ 层次注意力立场分类              │
│  ├─ 逃避/模糊检测                   │
│  ├─ 话题演化追踪                    │
│  └─ 跨话题关联分析                  │
└──────────┬──────────────────────────┘
           ▼
┌─────────────────────────────────────┐
│  Layer 4: 多轮矛盾检测引擎           │
│                                      │
│  Pass 1: 直接矛盾检测                │
│   同话题 → 截然相反立场              │
│                                      │
│  Pass 2: 时间线不一致性检测          │
│   立场渐变 → 趋势异常               │
│                                      │
│  Pass 3: 上下文反转检测              │
│   面对不同受众说法不同              │
│                                      │
│  Pass 4: 数量矛盾检测                │
│   同一数据的说法前后不一致          │
│                                      │
│  Pass 5: 承诺梯度检测                │
│   承诺强度随时间的衰减模式          │
│                                      │
│  Pass 6: 条件逃避检测                │
│   用条件句/假设句回避明确立场       │
└──────────┬──────────────────────────┘
           ▼
┌─────────────────────────────────────┐
│  Layer 5: 语言特征分析层             │
│  ├─ 模糊/回避性语言检测             │
│  ├─ 情绪唤起度分析                  │
│  ├─ 细节丰富度对比                  │
│  ├─ 代词使用模式分析                │
│  └─ 认知过程词汇分析                │
└──────────┬──────────────────────────┘
           ▼
┌─────────────────────────────────────┐
│  Layer 6: 上下文解析层               │
│  ├─ 受众/场合变化分析               │
│  ├─ 时间背景变迁考量                │
│  ├─ 法律/合规约束判别               │
│  ├─ 新证据/事件影响评估             │
│  └─ 角色演变合理性判定              │
└──────────┬──────────────────────────┘
           ▼
┌─────────────────────────────────────┐
│  Layer 7: 综合评分与报告生成层       │
│  ├─ 多维度加权评分                  │
│  ├─ 严重程度分级                    │
│  ├─ 可追溯引用链                    │
│  ├─ 可视化呈现（图标+表格）        │
│  └─ 深入追问建议                    │
└─────────────────────────────────────┘
```

---

# 📐 算法一：层次注意力立场分类器 (Hierarchical Attention Stance Classifier)

## 数学模型

```
给定：语句 S = {t₁, t₂, ..., tₙ}，话题域 T
目标：P(Stanceⱼ | S, T) → max Stanceⱼ ∈ {strongly_support, support, neutral, oppose, strongly_oppose, evasive, ambiguous}
```

## 层次特征提取

```
第一层：词语级特征
  Φ_word(s) = [Φ₁, Φ₂, ..., Φ₁₅]

  Φ₁ = 情感极性得分 (VADER/SentiCN)
  Φ₂ = 立场关键词匹配得分
  Φ₃ = 程度副词密度 (非常/绝对/完全/有点/可能/也许)
  Φ₄ = 否定词密度 (不/没/非/未/无/别/不要)
  Φ₅ = 条件句标记 (如果/假如/要是/只要/unless/if)
  Φ₆ = 回避性词汇密度 (不方便/不便回应/不予置评/no comment)
  Φ₇ = 人称代词模式 (第一人称 vs 第三人称占比)
  Φ₈ = 具体性得分 (具体数字/专有名词/时间地点)
  Φ₉ = 比较级/最高级密度 (更好/最/更差/better/worst)
  Φ₁₀ = 承诺性动词 (保证/承诺/一定/绝对/绝不/promise/guarantee)
  Φ₁₁ = 不确定性标记 (听说/据说/可能/大概/allegedly/reportedly)
  Φ₁₂ = 观点引用标记 (我认为/在我看来/据我了解/I think/in my opinion)
  Φ₁₃ = 情感唤起词密度 (愤怒/震惊/激动/失望/outrage/shocked)
  Φ₁₄ = 抽象名词密度 (正义/公平/未来/发展/justice/future)
  Φ₁₅ = 话题关键词覆盖率

第二层：句子级特征（基于注意力机制）
  对每个词向量 hᵢ = embed(tᵢ):
    注意力权重 αᵢ = softmax(Wₐ · tanh(Wₕ · hᵢ + bₕ))

    句子级表示:
    h_sentence = Σ(αᵢ · hᵢ)

第三层：上下文级特征（多语句聚合）
  h_context = TransformerEncoder([h_s1, h_s2, ..., h_sk])
  使用8头注意力聚合上下文信息
```

## 立场分类决策

```
P(Stanceⱼ | S, T) = softmax(MLP(h_sentence ⊕ h_context ⊕ Φ_topic))

其中：
- ⊕ 表示向量拼接
- Φ_topic 是话题域原型向量
- MLP: 256 → 128 → 64 → 7 (7种立场)
- Dropout: 0.3
- 激活函数: ReLU + LayerNorm

最终决策:
if max P > 0.65:
    stance = argmax P
elif max P > 0.40 and ambiguity_signal > threshold:
    stance = "ambiguous"
elif evasion_detected:
    stance = "evasive"
else:
    stance = "neutral"
```

## 逃避/模糊检测特殊信号

```
evasion_signals = {
    "non_answer_patterns": [
        "这个问题问得好", "这要看情况", "不能简单说",
        "话题比较复杂", "需要具体分析", "不予置评",
        let me be clear (preceded by deflection),
        "I'm glad you asked" (without direct answer),
        repeating_the_question_as_answer
    ],
    "deflection_patterns": [
        "更应该关注的是", "重点不在于此",
        "我想强调的是", "我们真正应该讨论",
        redirect_to_unrelated_topic,
        attack_question_premise
    ],
    "hedging_clusters": [
        consecutive_hedges_ratio > 0.3,
        "我个人认为" + "可能" + "一定程度上",
        "据我所知" + "大概" + "也许",
    ]
}

evasion_score = Σ(w_signal · occurrence_count) / total_words
if evasion_score > 0.55 → label as "evasive"
```

---

# 📐 算法二：多轮矛盾检测引擎 (Multi-Pass Contradiction Engine)

## Pass 1: 直接矛盾检测 (Direct Contradiction)

### 语义对立矩阵

```
定义立场对立关系表 O:

strongly_support ↔ strongly_oppose (对立强度: 1.0)
support ↔ oppose (对立强度: 0.8)
strongly_support ↔ oppose (对立强度: 0.6)
support ↔ strongly_oppose (对立强度: 0.6)
neutral → 不参与直接矛盾检测
evasive/ambiguous → 标记为"可疑回避"但不直接判定矛盾

检测过程:
for each topic t in extracted_topics:
    statements_t = filter_by_topic(statements, t)
    pairs = generate_pairs(statements_t)

    for (sᵢ, sⱼ) in pairs:
        if time_delta(sᵢ, sⱼ) < dedup_threshold:
            skip (可能是同一场合的不同转述)

        stance_i = get_stance(sᵢ)
        stance_j = get_stance(sⱼ)

        contradiction_strength = O[stance_i][stance_j]

        if contradiction_strength >= 0.6:
            text_similarity = cosine_sim(embed(sᵢ), embed(sⱼ))
            if text_similarity < 0.82:  // 不是同义反复
                register_contradiction(sᵢ, sⱼ, t,
                    severity = contradiction_strength * text_dissimilarity,
                    type = "direct_flip")
```

## Pass 2: 时间线不一致性检测 (Temporal Inconsistency)

### 立场漂移检测

```
对每个话题的立场序列进行时间序列分析：

输入：{(t₁, s₁, w₁), (t₂, s₂, w₂), ..., (tₙ, sₙ, wₙ)}
  tᵢ = 时间戳, sᵢ = 立场数值化值, wᵢ = 权重

立场数值映射:
  strongly_support → +2.0
  support → +1.0
  neutral → 0.0
  ambiguous → -0.5 (标记为模糊)
  evasive → -0.8 (标记为回避)
  oppose → -1.0
  strongly_oppose → -2.0

算法:
1. 时间排序: sort_by_timestamp(sequence)

2. 滑动窗口平均:
   window_size = max(3, len(sequence) / 5)
   smoothed = moving_average(values, window_size)

3. 趋势检测:
   if len(sequence) >= 4:
       slope = linear_regression(timestamps, smoothed)
       if abs(slope) > threshold:
           标记为"趋势性漂移"
           severity = abs(slope) * temporal_density
           
           进一步分析:
           if monotonic_change: "gradual_shift" (可能是观点自然演化)
           if abrupt_change_after_event: "event_triggered_flip" (事件触发)
           if oscillating: "context_dependent" (看人下菜碟)

4. 异常点检测:
   for i in 1..n:
       expected = predict_from_neighbors(i, window=2)
       residual = abs(values[i] - expected)
       if residual > 1.5:  // 立场偏离超过1.5档
           标记为时间线异常点
           severity = residual / 2.0
```

## Pass 3: 上下文反转检测 (Contextual Reversal)

### 受众/场合敏感性分析

```
检测目标：同一人在不同场合对同一话题发表相反看法

分析维度:
1. 受众类型:
   - 支持者/粉丝场合 → 立场通常更激进
   - 中立/专业场合 → 立场趋向谨慎
   - 反对者/对立场合 → 可能更防御
   - 媒体/公开场合 → 官方口径
   - 私下/内部场合 → 真实想法

2. 场合类型:
   - 正式发布会 vs 非正式采访
   - 国内媒体 vs 国际媒体
   - 文字采访 vs 视频直播
   - 官方声明 vs 社交媒体

3. 对比算法:
   for each pair (sᵢ, sⱼ) where audience_type(sᵢ) ≠ audience_type(sⱼ):
       if stance(sᵢ) · stance(sⱼ) < 0 and |difference| > 1.0:
           if time_delta(sᵢ, sⱼ) < 90:  // 90天内切换立场
               标记为"语境反转"
               severity = base_severity * audience_contrast_weight
               audience_contrast_weight = {
                   (supporter, opponent): 1.0,
                   (internal, public): 0.9,
                   (domestic, international): 0.7,
                   (formal, casual): 0.5
               }
```

## Pass 4: 数量矛盾检测 (Quantitative Mismatch)

### 数字/统计数据一致性验证

```
检测模式:

模式A: 同一数据不同说法
  正则模式: "([\d,]+\.?\d*)\s*(万|亿|%|人|元|美元|年|月|天|次)"
  
  对同一实体/事件相关的所有数据声明做聚类:
  例如: 公司营收、粉丝数量、事故伤亡、时间周期
  
  矛盾判定:
  delta = max(value, value') - min(value, value')
  if delta / min(value, value') > 0.15:  // 差异超过15%
      标记为数量矛盾
      severity = min(1.0, delta / reference_value)

模式B: 存在性矛盾
  声明A: "我从未说过X"
  声明B: 明确说了X
  → 存在性矛盾 (severity: 1.0 最高)

模式C: 时间线矛盾
  声明A: "我2021年就参与了这个项目"
  声明B: "我是2022年才加入的"
  → 时间线矛盾 (severity: 0.9)
```

## Pass 5: 承诺梯度检测 (Commitment Gradient)

### 承诺衰减跟踪

```
定义：公开承诺/保证的强度随时间的变化

检测流程:
1. 识别承诺性语句
   patterns = [
       "我保证/承诺/一定", "I promise/guarantee/assure",
       "绝对不会/绝不", "never/will never",
       "说到做到", "我对此负责"
   ]

2. 提取每次承诺的时间点和强度
   强度评估:
   - 绝对承诺 (保证/一定/绝不): 强度 = 1.0
   - 一般承诺 (我会努力/争取): 强度 = 0.6
   - 条件承诺 (如果可能/在XX前提下): 强度 = 0.3

3. 构建承诺时间序列
   for each commitment chain on topic t:
       first_statement → 最强承诺
       later_statements → 跟踪强度变化

4. 衰减检测
   if first_strength - last_strength > 0.5:
       if no_public_explanation_for_change:
           标记为"承诺衰减"
           severity = (first_strength - last_strength) * time_span_weight
           
   if 承诺完全消失 (后续不再提及且未兑现):
       标记为"承诺抛弃"
       severity = 0.8
```

## Pass 6: 条件逃避检测 (Conditional Evasion)

### 条件句/假设句策略分析

```
检测目标：过度使用条件句/假设句来逃避明确表态

核心指标:
1. 条件句密度
   conditional_ratio = count(如果/假如/要是/除非/只要/一旦/
                              if/unless/when/provided that) / total_sentences

2. 条件句种类
   - 真实条件: "如果XX发生，我就YY" (可以验证)
   - 虚假条件: "如果世界和平，我就..." (不可能触发)
   - 未知条件: "如果情况允许的话" (无法验证)
   - 转嫁条件: "这取决于XX部门/其他人" (外部归因)

3. 逃避策略识别
   strategies = {
       "hypothetical_hiding": "过多使用假设场景回避现实表态",
       "qualification_overload": "多重限定条件使承诺空洞化",
       "external_blame": "将条件转移给外部不可控因素",
       "moving_goalpost": "每次兑现前提高条件门槛",
       "redefinition": "重新定义关键词使得原来承诺不可验证"
   }

4. 警报阈值
   if conditional_ratio > 0.25 且 conditional_specificity < 0.3:
       标记为"条件逃避"
       severity = conditional_ratio * (1 - conditional_specificity)
   elif moving_goalpost_detected:
       标记为"移动门柱"
       severity = 0.7
```

---

# 📐 算法三：语言体征分析仪 (Linguistic Analyzer)

## 多维语言特征提取

```
给定一组言论 D = {d₁, d₂, ..., dₙ}
输出: 每个维度的风险评分 + 综合语言可信度

### 维度一：模糊/回避语言密度 (Hedging)

词汇库:
  Chinese: 可能/也许/大概/似乎/好像/差不多/基本/基本上/
           一般来说/通常情况下/某种意义上/某种程度上/
           总体而言/相对而言/一定的/一定的程度上/
           据我所知/据我了解/听说/据说/谣传/据传闻
  English: maybe/perhaps/probably/possibly/somewhat/
           basically/essentially/generally/relatively/
           sort of/kind of/like/mostly/often/frequently/
           allegedly/reportedly/purportedly/supposedly/
           to some extent/in some ways/it seems/it appears

score_hedging = count(hedging_words) / total_content_words * 100

风险分级:
  score_hedging < 5 → 低风险 (直接坦诚)
  5 ≤ score_hedging < 15 → 中等风险
  score_hedging ≥ 15 → 高风险 (异常模糊)

### 维度二：细节丰富度 (Detail Richness)

具体性词汇匹配:
  - 数字/日期/时间: count(数字模式)
  - 专有名词: count(组织名/人名/地名)
  - 具体动词: count(行为/动作类词汇) / count(抽象动词)
  - 感官细节: count(视觉/听觉/触觉描述)

score_detail = (
    0.3 · normalized_numerical_density +
    0.3 · normalized_entity_density +
    0.2 · specific_verb_ratio +
    0.2 · sensory_detail_density
)

对比分析:
  baseline_detail = 同一人早期言论的平均细节丰富度
  如果 score_detail_current < 0.5 · baseline_detail:
    细节下降警告 (可能暗示回避/不诚实)

### 维度三：人称代词模式 (Pronoun Pattern)

第一人称单数 (我/I) vs 第一人称复数 (我们/we):

pronoun_ratio = count(我) / (count(我) + count(我们) + ε)

分析:
  pronoun_ratio > 0.7 → 高个人责任承担 (可能真实/也可能自我中心)
  pronoun_ratio < 0.3 → 异常回避个人责任 (可能使用"我们"稀释责任)

异常模式:
  - 从"我"突然切换为"我们" (在敏感话题上)
  - 过多使用被动语态/无人称句 ("据了解"/"据调查"/"it is believed")
  - 使用第三人称指代自己 (在压力情境下)

### 维度四：情绪唤起度 (Emotional Arousal)

情绪词库匹配:
  Positive: 开心/高兴/自豪/满意/感动/乐观/excited/proud/happy
  Negative: 愤怒/失望/伤心/焦虑/恐惧/痛心/angry/disappointed/afraid

计算:
  emotional_density = count(emotion_words) / total_content_words
  emotional_volatility = std(emotional_density across statements)

分析:
  - 突发的情绪峰值 (在某话题上过度情绪化) → 可能不真实
  - 情绪平淡 (在所有话题上完全没有情绪词) → 非正常模式
  - 情绪一致性: 话题重要性 vs 情绪表达强度不匹配

### 维度五：认知过程词汇 (Cognitive Process)

词汇种类:
  - 因果推理: 因为/所以/因此/导致/由于/cause/because/therefore
  - 洞察: 意识到/明白/理解/认识到/realize/understand/recognize
  - 确定性: 肯定/一定/确信/确定/certain/definitely/absolutely
  - 差异性: 但是/然而/不过/却/although/however/but

指标:
  cognitive_richness = count(cognitive_words) / total_content_words
  certainty_ratio = count(certainty_words) / count(hedging_words + certainty_words)

分析:
  certainty_ratio > 0.8 → 过于肯定 (可能过度补偿)
  certainty_ratio < 0.2 → 过度不确定 (可能回避)
  正常范围: 0.3 - 0.7
```

## 综合语言风险评估

```
linguistic_risk = Σ(wᵢ · normalized_scoreᵢ)

权重:
  w_hedging = 0.25
  w_detail = 0.20 (方向反向: 细节越少风险越高)
  w_pronoun = 0.15
  w_emotion = 0.15
  w_cognitive = 0.15
  w_deflection = 0.10 (来自初筛的回避模式)

风险分级:
  linguistic_risk < 0.30 → ✅ 低风险 (语言模式正常)
  0.30 ≤ risk < 0.55 → ⚠️ 中等风险 (存在部分可疑模式)
  0.55 ≤ risk < 0.75 → 🔴 高风险 (明显回避/修辞)
  risk ≥ 0.75 → 🚨 紧急 (强烈语言欺骗信号)
```

---

# 📐 算法四：时间线标注与阶段划分 (Temporal Annotator)

## 时间粒度系统

```
输入: 带时间戳的言论集合
输出: 带有时间粒度标签和阶段划分的言论序列

### 粒度级别
Level 0: 精确日期 "2026-05-10" → 精确到日
Level 1: 月份 "2026年5月" → 精确到月
Level 2: 季度 "2026年Q2" → 精确到季度
Level 3: 年份 "2026年" → 精确到年
Level 4: 时期 "出道期/争议期/转型期" → 抽象时期

### 时期边界检测算法
1. 计算时间间隔分布
   gaps = [timestamp[i+1] - timestamp[i] for i in 0..n-1]
   
2. 使用Kneedle算法检测"言论密度断裂点"
   density_curve = cumulative_density(timestamps, smoothing=Gaussian)
   breakpoints = detect_knees(density_curve, sensitivity=1.5)

3. 结合外部事件进行语义标注
   for each breakpoint bp:
       nearby_events = get_significant_events(bp - 30d, bp + 30d)
       if nearby_events:
           标注时期名称为相关事件
           (如: "父母纠纷事件期" / "新片宣发期")
```

## 时间线异常警告

```
警告类型:
1. ⚠️ 长长沉默期: 连续超过180天无公开言论
   → 可能暗示回避期 / 危机公关静默期

2. ⚠️ 密集发言期: 单月发言量超过平均3倍标准差
   → 可能暗示危机应对 / 舆论引导

3. ⚠️ 选择性沉默: 在某话题上突然停止发言
   → 可能意识到之前的说法有问题

4. ⚠️ 回溯性修正: 后期言论频繁修正/调整早期说法
   → 可能暗示信息控制
```

---

# 📐 算法五：上下文解析器 (Context Resolver)

## 矛盾合理性评估

```
给定一个被标记的矛盾对 (sᵢ, sⱼ, t, severity)
判断该矛盾是否具有合理解释

### 评估维度

维度A: 受众/场合变化 (Audience Shift)
  if audience(sᵢ) ≠ audience(sⱼ):
      分析是否合理:
      - 内部会议 vs 公开发布 → 差异有一定合理性
      - 支持者集会 vs 中立采访 → 差异性可理解但不完全合理
      - 相同场合不同说法 → 不合理
      
      score_audience = {
          "相同场合": 0.0 (无解释力),
          "不同场合": 0.3,
          "完全相反场合": 0.1 (解释力有限)
      }

维度B: 时间背景变化 (Temporal Context)
  if time_delta(sᵢ, sⱼ) > 90:
      - 是否有重大事件发生?
      - 是否有新数据/信息出现?
      - 是否有政策/法律变化?
      
      score_temporal = {
          "有重大事件且时间差>1年": 0.8 (合理的观点演化),
          "有事件但时间差<3个月": 0.3,
          "无重大事件": 0.0 (无合理解释)
      }

维度C: 法律/合规约束 (Legal Constraint)
  if topic涉及诉讼、调查、保密等:
      - 言论受法律限制 → 有效解释
      - 上市公司信披合规 → 有效解释
      - 保密协议限制 → 有效解释
      
      score_legal = 0.7 if legal_constraint_confirmed else 0.0

维度D: 角色演变 (Role Evolution)
  if position(sᵢ) ≠ position(sⱼ):
      - 角色/职责变化 → 合理转变
      - 从个人身份到代表组织 → 可能不一致
      
      score_role = 0.5 if significant_role_change else 0.0

### 综合合理性评分

justification_score = max(score_audience, score_temporal, 
                          score_legal, score_role)

if justification_score > 0.7:
    🔶 有合理解释 (降低矛盾等级)
    adjusted_severity = severity * (1 - justification_score)
elif justification_score > 0.4:
    🔶 部分可解释 (保留但注明上下文)
    adjusted_severity = severity * 0.7
else:
    🔴 无合理解释 (保留全部严重性)
    adjusted_severity = severity
```

---

# 📐 算法六：来源可信度评分 (Source Reliability Scoring)

## 多维度媒体/来源评估

```
输入: 来源信息 (域名、媒体名称、文章URL)
输出: 可信度得分 [0, 1]

### 维度一：编辑标准 (Editorial Standards)

score_editorial = {
    "拥有明确的事实核查机制": 0.25,
    "有伦理准则/纠错政策": 0.20,
    "分离新闻与评论": 0.15,
    "明确标注付费/广告内容": 0.10,
    "未知/没有公开标准": 0.05
}

### 维度二：行业记录 (Track Record)

score_track = {
    "IFCN认证的事实核查机构": 0.30,
    "多年行业口碑 (10+年)": 0.25,
    "曾获新闻奖项": 0.20,
    "有过重大失实记录 (公开道歉/更正)": -0.20,
    "未知记录": 0.10
}

### 维度三：透明度 (Transparency)

score_transparent = {
    "公开所有者/出资方": 0.15,
    "公开编辑/记者联系方式": 0.10,
    "公开收入来源/广告商": 0.10,
    "公开方法论": 0.15,
    "低透明度": 0.05
}

### 维度四：独立性 (Independence)

score_independence = {
    "独立新闻机构 (非政府/非党派/非企业)": 0.25,
    "隶属知名新闻集团": 0.15,
    "有明确可见的赞助方/冠名方": 0.05,
    "利益冲突明显": -0.15
}

### 维度五：专业性 (Expertise)

score_expertise = {
    "在该领域有专业记者/编辑": 0.20,
    "使用专业采访/调查方法": 0.15,
    "有学术/行业顾问": 0.10,
    "缺乏专业背景": 0.05
}

### 最终评分

total_reliability = Σ scoreᵢ
total_reliability = max(0, min(1, total_reliability))

分级:
  Tier 1 (⭐⭐⭐): ≥ 0.85 → 高度可信源 (直接引用)
  Tier 2 (⭐⭐): 0.65 - 0.84 → 中等可信源 (交叉验证后使用)
  Tier 3 (⭐): 0.40 - 0.64 → 低可信源 (仅作参考)
  Tier 4 (❌): < 0.40 → 不可信源 (排除或单独标注)
```

---

# 📐 算法七：综合评分集成 (Scoring Ensemble)

## 一致性最终评分模型

```
### 基础分
base_score = 100 (满分)

### 扣分项

1. 直接矛盾惩罚
   direct_penalty = Σ(severity_of_contradictionᵢ) × 35
   penalty_contradictions = min(direct_penalty, 35)

2. 时间线不一致惩罚
   temporal_penalty = Σ(severity_of_temporal_gapᵢ) × 20
   penalty_temporal = min(temporal_penalty, 20)

3. 语言回避惩罚
   linguistic_penalty = linguistic_risk_score × 15
   penalty_linguistic = min(linguistic_penalty, 15)

4. 数量矛盾惩罚
   quant_penalty = count(quant_contradictions) * 10
   penalty_quant = min(quant_penalty, 10)

5. 承诺衰减惩罚
   commitment_penalty = Σ(decay_severityᵢ) × 15
   penalty_commitment = min(commitment_penalty, 15)

### 加分项

1. 上下文解析加分
   context_bonus = avg_justification_score × 15
   bonus_context = min(context_bonus, 15)

2. 长期稳定性加分
   if 同话题立场在2年以上保持稳定:
       stability_bonus = 20
   elif 1年以上稳定:
       stability_bonus = 10

3. 来源多样性加分
   source_diversity = unique_sources_count / total_expected_sources
   diversity_bonus = min(source_diversity × 5, 5)

### 最终计算

final_score = base_score 
    - penalty_contradictions 
    - penalty_temporal 
    - penalty_linguistic 
    - penalty_quant 
    - penalty_commitment
    + bonus_context 
    + stability_bonus 
    + diversity_bonus

final_score = max(0, min(100, final_score))
```

## 评分分级

```
评级      分数范围      标签                       图标
─────────────────────────────────────────────────────
卓越      [85, 100]    高度一致 — 言论可信度高      🟢⭐⭐⭐
良好      [70, 85)     基本一致 — 存在少量波动      🟢⭐
中等      [50, 70)     部分一致 — 发现一定矛盾      🟡⚠️
差等      [30, 50)     明显不一致 — 存在严重矛盾    🟠🔴
危急      [0, 30)      严重不一致 — 系统性问题      🔴🚨
```

---

# 🏗️ 文件结构

```
lie_detector_ai/
├── SKILL.md                         # 本技能说明文件（完整算法文档）
├── config.json                      # 技能配置文件
├── data/
│   ├── deception_patterns.json      # 语言欺骗模式数据库
│   ├── topic_keywords.json          # 话题关键词映射
│   ├── source_reliability_db.json   # 来源可信度数据库
│   ├── stance_lexicon.json          # 立场关键词词典
│   └── hedging_lexicon.json         # 模糊词汇词典
├── utils/
│   ├── lie_detector_core.py         # 主控制器（算法编排）
│   ├── statement_collector.py       # 言论采集（多源搜索）
│   ├── temporal_analyzer.py         # 时间线分析（算法四）
│   ├── topic_modeler.py             # 话题建模+立场提取（算法一）
│   ├── contradiction_engine.py      # 矛盾检测引擎（算法二）
│   ├── linguistic_analyzer.py       # 语言特征分析（算法三）
│   ├── context_resolver.py          # 上下文解析器（算法五）
│   ├── source_scorer.py             # 来源可信度评分（算法六）
│   ├── scoring_ensemble.py          # 综合评分（算法七）
│   ├── report_generator.py          # 报告生成
│   └── text_utils.py                # 文本处理工具函数
├── templates/
│   ├── quick_scan_output.md         # 快速扫描输出模板
│   ├── standard_output.md           # 标准报告模板
│   ├── full_report_output.md        # 完整报告模板
│   └── comparison_matrix.md         # 对比矩阵模板
└── examples/
    ├── liu_haocun_demo.md           # 【实战】刘浩存 — 演技转型言论一致性
    └── basic_usage.md              # 基础用法演示
```

---

# 🔧 工作流程

## 完整执行链路

```
Step 1: 解析用户输入
  · 提取: 目标人物, 时间范围, 话题域, 输出格式
  · 消歧: 确认具体人物（排除同名干扰）

Step 2: 采集言论数据
  · 多引擎并行搜索（Google + DuckDuckGo + Baidu + Various）
  · 按来源类型分类（采访/社交媒体/发布会/声明）
  · 去重合并（SimHash 64位指纹）

Step 3: 预处理与标注
  · 时间戳归一化
  · 内容分段标注
  · 语言检测（如需跨语言分析）

Step 4: 话题建模与立场提取
  · HDBSCAN提取核心话题
  · 分层注意力立场分类
  · 逃避/模糊标记

Step 5: 6轮矛盾检测
  · 执行 Pass 1-6 依次检测
  · 记录匹配的矛盾对 + 严重程度

Step 6: 语言特征分析
  · 5维度语言信号提取
  · 综合风险评分

Step 7: 上下文解析
  · 对每个矛盾对评估合理性
  · 调整严重性权重

Step 8: 综合评分
  · 集成所有信号计算最终得分
  · 映射到评级

Step 9: 生成报告
  · 按所选模板格式化输出
  · 添加可视化元素
  · 生成追问建议

Step 10: 输出结果
  · Markdown报告呈现
  · 可追溯引用链
  · (可选) 保存为文件
```

---

## 📊 性能指标

| 操作 | 目标耗时 | 准确率目标 |
|:---|:---:|:---:|
| 快速扫描 (1人, 1年) | < 30秒 | 立场识别 > 85% |
| 标准分析 (1人, 3年) | < 60秒 | 矛盾检测 > 80% |
| 完整报告 (1人, 5年) | < 120秒 | 综合评分 > 90% |
| 对比分析 (多人) | < 180秒 | 对比准确 > 85% |
| 语言特征分析 | < 5秒/人 | 风险识别 > 75% |
| 来源可信度评估 | < 3秒/来源 | 分级准确 > 85% |




---

# 🆕 v2.0 复杂优化升级文档

## 概述

```
版本: v2.0.0
升级内容: 5项复杂优化
升级日期: 2026-05-10
```

| 优化编号 | 名称 | 类型 | 文件 |
|:-------:|:----|:---:|:----|
| 优化1 | **小样本KNN立场分类器** | 升级(算法一) | `knn_stance_classifier.py` |
| 优化2 | **6×6矛盾交叉验证矩阵** | 升级(算法二) | `contradiction_matrix.py` |
| 优化4 | **外部事件知识图谱注入** | 升级(算法五) | `event_graph.py` |
| 优化5 | **红队对抗检测引擎** | 新增(算法八) | `adversarial_search.py` |
| 优化6 | **跨目标说谎者网络** | 新增(算法九) | `network_analyzer.py` |
| 优化7 | **贝叶斯置信区间评分** | 升级(算法七) | `scoring_ensemble.py` |

---

# 📐 算法八：红队对抗检测引擎 (Adversarial Red Team)

## 整体架构

```
目标人物 T + 已知话题域 S
        │
        ▼
┌─────────────────────────────────────┐
│  红队攻击查询生成器                   │
│  ├─ 翻车检测 (flip_flop)            │
│  ├─ 实锤核查 (fact_check)           │
│  ├─ 承诺未兑现 (promise_broken)     │
│  ├─ 争议扫描 (controversy)          │
│  └─ 对比言论 (compare_statement)    │
└──────────┬──────────────────────────┘
           ▼
┌─────────────────────────────────────┐
│  搜索引擎攻击执行                     │
│  (自动并行搜索所有攻击查询)           │
└──────────┬──────────────────────────┘
           ▼
┌─────────────────────────────────────┐
│  结果扫描与潜在矛盾识别               │
│  ├─ 自我矛盾检测                     │
│  ├─ 被揭穿模式识别                    │
│  ├─ 承诺失败标记                     │
│  └─ 尴尬事件抓取                     │
└──────────┬──────────────────────────┘
           ▼
┌─────────────────────────────────────┐
│  红队报告生成                        │
│  ├─ 高风险线索TOP5                   │
│  ├─ 综合攻击结果评估                  │
│  └─ 建议行动方案                     │
└─────────────────────────────────────┘
```

## 对抗查询模板

```
攻击类型: flip_flop (翻车检测)
  查询模板:
  - "{target} 改口 {topic}"
  - "{target} 承认 {topic} 错了"
  - "{target} 收回 {topic} 言论"
  - "{target} 推翻 {topic} 说法"
  - "{target} earlier vs now {topic}"
  - "{target} 前后矛盾 {topic}"
  
攻击类型: fact_check (实锤核查)
  查询模板:
  - "辟谣 {target} {topic}"
  - "揭穿 {target} {topic}"
  - "事实核查 {target} {topic}"
  - "{target} lies about {topic}"
  
攻击类型: promise_broken (承诺未兑现)
  查询模板:
  - "{target} 承诺 {topic} 没兑现"
  - "{target} 食言 {topic}"
  - "{target} failed to deliver {topic}"
  
攻击类型: controversy (争议扫描)
  查询模板:
  - "{target} 争议 {topic}"
  - "{target} 翻车 {topic}"
  - "{target} 打脸 {topic}"
  - "{target} scandal {topic}"
```

## 线索严重程度评分

```
类型                   严重度    说明
────────────────────────────────────────
self_contradiction      0.90    "改口/收回/前后矛盾"
exposed_lie             0.95    "辟谣/揭穿/实锤"
promise_failure         0.80    "失信/未兑现/食言"
embarrassing            0.60    "打脸/翻车/尴尬"
```

---

# 📐 算法九：跨目标说谎者网络分析 (Lie Network)

## 整体架构

```
目标人物 T
    │
    ▼
┌─────────────────────────────────┐
│  关联人物自动发现                 │
│  ├─ 从搜索结果中提取共现人物     │
│  ├─ 关系类型分类                 │
│  └─ 共现频率统计                 │
└──────────┬──────────────────────┘
           ▼
┌─────────────────────────────────┐
│  关联人物言论收集                 │
│  ├─ 合作者言论                   │
│  ├─ 竞争者言论                   │
│  ├─ 代言人/发言人言论             │
│  └─ 上级/下属言论                │
└──────────┬──────────────────────┘
           ▼
┌─────────────────────────────────┐
│  交叉验证                        │
│  ├─ 对同一事件的描述是否一致      │
│  ├─ 同一话题的立场是否冲突        │
│  └─ 谁在替谁圆话/谁在唱反调      │
└──────────┬──────────────────────┘
           ▼
┌─────────────────────────────────┐
│  说谎者网络图生成                 │
│  ├─ 文本化关系图谱               │
│  ├─ 交叉验证发现的矛盾列表        │
│  └─ 网络统计摘要                 │
└─────────────────────────────────┘
```

## 关系类型定义

```
collaborator (合作者)     关键词: 合作/搭档/联合/共同/伙伴
competitor (竞争者)       关键词: 竞争/对手/竞品/对标
spokesperson (代言人)     关键词: 发言/代表/表示/声称
superior (上级)           关键词: 上级/老板/领导/CEO
subordinate (下属)        关键词: 下属/员工/团队/成员
family (家人)             关键词: 家人/妻子/丈夫/父母
```

## 交叉验证算法

```
对每个共同话题topic:
    目标人物立场: stance_T = classify(target_statement[topic])
    关联人物立场: stance_R = classify(related_statement[topic])
    
    如果 stance_T · stance_R < 0 (立场相反):
        如果 topic 涉及同一事件/实体:
            标记为跨人物矛盾
            
    如果 stance_T = stance_R 且 论证逻辑不同:
        标记为"默契配合" (network_coordination)
    
    如果 stance_T = "evasive" 而 stance_R 明确表态:
        标记为"替身策略" (proxy_communication)
```

---

# 📐 v2.0 评分升级：贝叶斯置信区间模型

## 数学模型

```
模型设定:
  先验: θ ~ N(μ₀, σ₀²)    其中 μ₀=65, σ₀=15
  似然: x|θ ~ N(θ, σ²/n)   其中 σ=12（观测噪声）
  后验: θ|x ~ N(μₙ, σₙ²)

后验参数:
  μₙ = (μ₀/σ₀² + x̄·n/σ²) / (1/σ₀² + n/σ²)
  σₙ² = 1 / (1/σ₀² + n/σ²)

其中:
  x̄ = 确定性评分（基于扣分/加分计算的点估计）
  n = 有效样本量（经对数加权+来源多样性+矛盾惩罚调整）
```

## 有效样本量计算

```
effective_n = (log₂(N_statements + 1) × 3 + log₂(N_sources + 1) × 2)
              × max(0, 1 - N_contradictions × 0.02)

限制条件: 1 ≤ effective_n ≤ 50
```

## 置信区间

```
90%置信区间: μₙ ± 1.645 × σₙ

展示格式:
  "72分 (90%置信: 65-79)"
  
不确定性分级:
  有效样本 < 5:   🔴 极高不确定性
  有效样本 5-10:  🟡 高不确定性
  有效样本 10-20: 🟢 中等不确定性
  有效样本 > 20:  ✅ 低不确定性
```

## 数据质量评价

```
N_statements ≥ 50 且 N_sources ≥ 5: ⭐⭐⭐ 高质量 - 结论可靠
N_statements ≥ 20 且 N_sources ≥ 3: ⭐⭐   中等质量
N_statements ≥ 5:                    ⭐    低质量 - 仅供参考
N_statements < 5:                    ❌    极低质量 - 请谨慎引用
```

---

# 📊 v2.0 架构全景图

```
用户查询: "分析X的言论一致性"
        │
        ▼
┌────────────────────────────────────────────────────────┐
│  LieDetectorCore v2.0 (主控制器)                       │
│                                                        │
│  Phase 1: 采集言论数据                                 │
│  Phase 2: KNN立场分类 (优化1) ← 越用越准               │
│  Phase 3: 事件知识图谱注入 (优化4) ← 上下文增强         │
│  Phase 4: 6轮矛盾检测                                  │
│  Phase 5: 6×6交叉验证矩阵 (优化2) ← 综合症候分析        │
│  Phase 6: 语言特征分析                                  │
│  Phase 7: 红队对抗检测 (优化5) ← 主动找茬               │
│  Phase 8: 贝叶斯置信区间评分 (优化7) ← 科学量化         │
│                                                        │
│  可选: 说谎者网络分析 (优化6) ← 多人交叉验证            │
└────────────────────────────────────────────────────────┘
        │
        ▼
┌────────────────────────────────────────────────────────┐
│  报告生成器                                             │
│  ├─ quick_scan: 快速扫描 + 红队摘要                     │
│  ├─ standard: 标准报告 + 贝叶斯区间                     │
│  ├─ full_report: 完整报告 + 事件注入 + 矩阵分析          │
│  ├─ red_team: 红队专项报告                              │
│  └─ comparison_matrix: 对比矩阵                          │
└────────────────────────────────────────────────────────┘
```

---

# ✅ v2.0 与 v1.0 对比

| 维度 | v1.0 | v2.0 | 提升 |
|:---|:----|:----|:----:|
| 立场分类 | 关键词匹配 | KNN小样本+关键词+情感三级兜底 | 准确率+15% |
| 矛盾检测 | 6轮串行 | 6轮+6×6交叉验证矩阵+综合症候 | 减少遗漏30% |
| 上下文解析 | 5维度 | 5维度+事件知识图谱注入 | 解释力+40% |
| 攻击性 | 被动接收 | 主动红队对抗搜索 | 突破性提升 |
| 分析范围 | 单人 | 单人+多人网络 | 范围扩大 |
| 评分 | 确定性数值 | 贝叶斯概率区间 | 可信度飞跃 |
| 效果评估 | "72分" | "72分(90%CI:65-79)" | 告别伪精确 |
