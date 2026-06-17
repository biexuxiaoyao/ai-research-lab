## 18.1 Prompt架构模式

> 来源：18-提示工程与上下文工程 | 拆分自 README.md | 2026-06-14

---

## 18.1.1 四层分层架构设计模式

2024-2025年，业界从"提示词撰写"（Prompt Engineering）转向"上下文架构"（Context Engineering），多个独立来源收敛于同一个**四层分层架构**模式。

| 层级 | 名称 | 类型 | 职责 | token预算占比 |
|------|------|------|------|-------------|
| **Layer 1** | System / Foundation | 静态 | 角色定义、硬约束、输出格式、安全规则 | 10-20% |
| **Layer 2** | Context / Framework | 半静态 | 领域知识、API文档、编码规范、风格指南 | 20-25% |
| **Layer 3** | Task / Materials | 动态 | 本次请求的具体输入、文件、数据 | 25-30% |
| **Layer 4** | Process / Reasoning | 指令 | CoT触发、推理步骤、质量门控、验证规则 | 5-10% |

**来源与案例**:

1. **Galdren (2024)** 提出"四层提示架构"，强调**层级顺序**至关重要：LLM顺序处理输入，约束应前置，推理触发应后置，因为模型在先读到约束后会建立解释透镜，反之则已形成响应模式无法修正。

2. **Luca Berton (2025)** 在"Context Engineering Is King"中定义Context Stack为：System Context（静态）→ Domain Context（半静态，RAG在此发挥最大价值）→ Task Context（动态）→ Conversation Context（瞬时）。同时引入三个关键设计模式：
   - **Context Pruning**：通过相关性评分强制执行token预算
   - **Structured Context**：使用明确标题/章节格式化上下文，便于模型解析
   - **Negative Context**：明确告知模型"不要做什么"——与正向约束同等重要

3. **Adam Marsa / Dev.to (2025)** 从Agent视角定义四层：System Layer（合约式约束 + "如不能满足则[fallback]"）→ Memory Layer（含In-context、Episodic、Semantic、Procedural四种子类型）→ Task Layer（紧聚焦目标）→ Output Layer（精确Schema + 质量门控）。识别出五大生产故障模式：
   - **Context Bloat** → Token预算 + 激进摘要
   - **Tool Hallucination** → 工具描述中的逆向条件（anti-conditions）
   - **RAG Retrieval Miss** → 结构化chunk注入 + 来源元数据
   - **Instruction Drift** → 每N轮重新注入约束
   - **Silent Failure** → 后置生成LLM评估器调用

4. **mshogin/prompt-arch (GitHub)** 从软件架构角度将Prompt建模为：Prompt Template Engine → Context Builder → LLM Adapter Layer → Tool Execution Layer → Memory/Context Storage，将Prompt视为版本控制、参数化的对象。

## 18.1.2 CoT vs ToT vs ReAct在编码任务中的应用效果对比

### 基准数据对比（HumanEval / MBPP）

| 方法 | HumanEval pass@1 | MBPP pass@1 | 语法错误率 | Token消耗 |
|------|-----------------|-------------|-----------|----------|
| Baseline (Direct / Zero-shot) | 67.7% | 65.8% | ~5% | 最低 |
| **Chain-of-Thought (CoT)** | 69.5% | 67.7% | **30-36%** | 中 |
| **CodeCoT (CoT + Self-Exam, 1 step)** | 71.3% | 81.7% | 25-27% | 高 |
| **CodeCoT (5 steps)** | **79.3%** | **89.5%** | **1-2%** | 很高 |
| **Self-Planning** (LLaMA-3.1-70B) | 81.0% | -- | -- | 高 |
| **CGO (Chain of Grounded Objectives)** (2025) | 80.3% | -- | -- | **最低** |

**数据来源**: Huang et al., _CodeCoT: Tackling Code Syntax Errors in CoT Reasoning for Code Generation_ (2023, arXiv:2308.08784)；Yeo et al., CGO (2025).

### 关键发现

1. **CoT的编码悖论**：纯CoT虽然改善了逻辑推理路径，但极大增加了语法/运行时错误率（从~5%升至30-36%）。原因是CoT生成的自然语言推理与代码语法不在同一"通道"中，模型在推理和编码之间切换时产生结构不匹配。CodeCoT的核心贡献是通过**自检循环**将语法错误率降至1-2%。

2. **ReAct的编码场景表现**：ReAct（Reasoning + Acting）在需要工具调用和多步操作的任务中优于纯CoT。在SWE-bench等多文件编辑任务中，ReAct范式是当前编程Agent的基础模式。但ReAct在单函数生成（HumanEval类）上的开销大于收益——额外的"Act"步骤在不需要工具时只是消耗token。

3. **ToT的编码适用性**：Tree-of-Thoughts在需要探索多个解空间的复杂推理任务中（如竞赛编程、算法设计）有优势。RethinkMCTS (2024, arXiv:2409.09584) 将蒙特卡洛树搜索引入代码生成，在CodeContests上实现改进。但ToT的API调用开销是CoT的3-10倍，适合离线/批处理场景而非实时编码。

4. **CGO的启示 (2025)**：Chain of Grounded Objectives通过简洁的注释式目标（而非长篇自然语言推理），在HumanEval上用**114 tokens**达到了与CodeCoT（367 tokens）相当的准确率（80.3% vs 79.6%），证明**token效率**是下一代提示工程的核心优化维度。

### 适用场景矩阵

| 场景 | 推荐方法 | 原因 |
|------|---------|------|
| 单函数生成（HumanEval类） | CodeCoT + Self-Exam (3步) | 语法错误消除效果最佳 |
| 多文件编辑（SWE-bench类） | ReAct + 结构化输出 | 需要文件搜索、读取、修改的工具链 |
| 竞赛编程/算法设计 | ToT / MCTS变体 | 需要探索多个候选解 |
| 生产环境（成本敏感） | CGO或直接Self-Planning | token效率优先 |
| RAG增强编码 | CoT + 检索上下文 | 简单CoT + 外部知识即可 |

## 18.1.3 Few-Shot策略的工程最优解

### 示例数量的最优区间

2024年多项研究收敛于**3-8个示例**为实用最优区间：

- **Xu et al. (Dec 2024, arXiv:2412.02906)** 在代码合成任务上发现：精心选择的2-shot可超越随机选择的8-shot——**选择质量 > 数量**。
- **Lilian Weng (2024) 提示工程指南** 指出：超过4个示例后的边际收益递减显著，增加到16个示例时收益增量往往不覆盖额外的token成本。
- **实际上限约束**：对于长输入/输出的任务（如代码合成、长文档QA），2-4个示例可能是上下文窗口能承载的最大数量。

### 示例选择方法

2024年形成了**五阶段管道**式的成熟方法论：

```
检索(Retrieve) → 选择(Select) → 排序(Order) → 格式化(Format) → 校准(Calibrate)
```

| 阶段 | 方法 | 代表工作 | 关键数据 |
|------|------|---------|---------|
| **检索** | Embedding相似度KNN | 行业标准做法 | top 10-20候选 |
| **选择** | 多样性约束 + 标签平衡 + 主动学习 | APE (DaSH 2024), CODEEXEMPLAR (Xu 2024) | CODEEXEMPLAR通过模型学习方法挑选示例 |
| **排序** | 基于相似度 / 学习排序 / Bandit | POEM (Do et al. 2024), EASE (Wu et al. 2024), TRIPLE (NeurIPS 2024) | POEM比TEMPERA改进5.3%；EASE联合优化选择+排序 |
| **格式化** | 一致模板 + 清晰分隔 | 行业最佳实践 | 双换行/明确分隔符 |
| **校准** | Contextual Calibration (Zhao et al.) | 学术共识 | 用N/A基线输入测量并消去模型固有标签偏好 |

### 排序的关键发现

- **排序对性能的影响可能超过选择**：同一组示例的不同排列可使性能从接近随机摆动到接近SOTA。
- 三种偏见需要对抗：**近因偏见**（末尾示例权重过高）、**首因偏见**（首个示例定锚）、**多数标签偏见**。
- POEM (2024) 的一个关键工程洞察：**在rank-space而非text-space中编码排列**，搜索空间从M!/(M-m)!缩减至m!，大幅降低优化成本。
- **随机序 + 多数投票**（Self-Consistency）仍是一个强基线：采样多种排列取多数票，实现简单且效果稳定。

**L4 Prompt Caching 实证数据 (2025-2026)**

| 指标 | Anthropic | OpenAI | Google |
|------|-----------|--------|--------|
| 缓存读取折扣 | **90%**（0.10× 基础价） | 50% | 80% |
| TTFT 降低 | **85%** | 30-80% | 30-60% |
| 写入成本 | 1.25×（5分TTL）/2×（1小时） | 免费 | 存储费 |
| 配置方式 | 显式 `cache_control` | 全自动 | 隐式+显式 |

实际命中率：批量处理 92% / 代码补全 85% / 多轮对话 72% / Agent 工作流 63%（动态工具结果破坏前缀匹配）/ RAG 45%。arXiv:2601.06007 在 DeepResearch Agent 基准测试中实现 **61% 成本降低**，策略性 `exclude-dynamic-tools` 缓存放置。多层缓存（语义+前缀）复合节省 **>80%**，语义缓存命中率 61.6-68.8%，正命中准确率 >97%。vLLM 自托管方案相比朴素实现吞吐量提升 **14-24×**。

**L4 上下文窗口实际利用率研究**

微软研究院 2025：有效利用率在 >100K token 时降至 ~60%，>500K token 时降至 ~45%。Claude Code 实际会话分布：System Prompt 3-8%（5-15K）、已读文件 25-60%（50-120K）、对话历史 15-40%（30-80K）、生成响应 10-25%（20-50K）。Anthropic Context Editing（`clear_tool_uses`）在 100 轮网页搜索评估中将 Token 消耗降低 **84%**，结合 Memory Tool 后 Agent 性能提升 **39%**。

---

---

## 📎 被以下章节引用

- [18.1 Prompt架构模式](README.md)
