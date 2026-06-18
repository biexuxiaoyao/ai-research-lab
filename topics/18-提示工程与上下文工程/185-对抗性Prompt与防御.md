## 18.5 对抗性 Prompt 与防御

> 来源：18-提示工程与上下文工程 | 拆分自 README.md | 2026-06-14

---

## 18.5.1 Prompt Injection 的工程防御层级

### 四层防御体系

```text
层级 1: 输入净化 (Input Sanitization)
  ├── 嵌入异常检测 (cosine 距离 vs 已知注入模式)
  ├── 模式匹配+关键词过滤 (signature detection)
  ├── 混合编码防御 (Base64/Caesar 多编码聚合)
  └── Taint-first 管道 (所有外部输入默认视为恶意)

层级 2: 上下文隔离 (Context Isolation)
  ├── P-LLM/Q-LLM 分离 (CaMeL 架构)
  ├── 双通道独立编码 (PICO)
  ├── 系统/用户输入门控融合 (PICO)
  └── 安全规划器+注入隔离器+动态验证器 (DRIFT)

层级 3: 权限分级 (Least Privilege)
  ├── 工具功能角色分类 (Read/Write/Execute)
  ├── 子任务能力范围约束
  ├── 破坏性操作 HITL 门控
  └── OIDC Agent 身份 + 短生命期 Token

层级 4: 运行时检测 (Runtime Detection)
  ├── 多阶段响应验证
  ├── 流式输出清洗
  ├── 护栏模型 (InjecGuard)
  └── 语义意图不变量检测 (PromptSleuth)
```text

### 各层具体方案与数据

**层级 1 — 输入净化**:

| 方案 | 机制 | 效果 | 来源 |
|------|------|------|------|
| **嵌入异常检测** | 计算输入嵌入与已知注入模式嵌入的 cosine 距离 | 捕获~78%基础(L1)攻击 | Ramakrishnan et al. 2025 |
| **混合编码防御** | 多编码方案编码外部数据后聚合预测 | 阻止攻击者构造通用解码 payload | Zhang et al., Apr 2025 |
| **GenTel-Shield** | 嵌入分类器检测越狱 | 97.6%准确率 | 2025 |
| **Taint-first 管道** | 所有外部输入默认视为恶意，多阶段过滤 | 基础防线，但无法独立防御高级攻击 | 行业共识 |

**层级 2 — 上下文隔离（架构基础）**:

| 方案 | 机制 | 效果 | 评价 |
|------|------|------|------|
| **CaMeL (Google DeepMind)** | P-LLM 处理用户指令（仅见可信输入），Q-LLM 处理外部数据（隔离在受限 Python 子集中），安全解释器追踪变量来源 | 首个不依赖"更多 AI"的架构方案 | Simon Willison: "我见过的第一个可信的 Prompt 注入缓解方案" |
| **PICO** | 冻结系统编码器 + 可训练用户编码器的双通道，门控融合`F(S,U) = α(U)·Es(S) + (1-α(U))·Eu(U)`，检测到对抗输入时α→1 强制融合接近系统提示 | 对抗输入时输出≈纯系统提示 | 训练时保持系统编码器冻结确保不可篡改 |
| **DRIFT (NeurIPS 2025)** | 安全规划器（预构建最小函数轨迹+JSON-Schema 参数清单）+ 注入隔离器（检测并掩码冲突指令）+ 动态验证器（监控轨迹偏差） | GPT-4o-mini ASR 从 30.7%降至 1.3%；策略微调后降至 0.0% | 系统级隔离，防御长程多轮投毒 |
| **Countermind (Nov 2025)** | 语义边界逻辑(SBL) + 强制时间耦合加密载荷包裹 + 语义分区 | 降低明文注入攻击面 | 长程 RAG 场景专用 |

**层级 3 — 权限分级**:

- DRIFT 框架按 Read / Write / Execute 分类工具角色：读取操作自动批准，写入/执行操作需意图对齐验证
- 破坏性/不可逆操作（金融、数据修改）强制执行 HITL 确认
- OIDC-based Agent 身份认证，短活 Token，定期密钥轮换

**层级 4 — 运行时检测**:

| 方案 | 机制 |
|------|------|
| **InjecGuard** | 护栏模型 + MOF（Mitigating Over-defense for Free）训练，重新平衡触发词敏感度，减少误报 |
| **PromptSleuth** | 语义意图不变量检测——将 Prompt 分解为任务图，标记语义无关的子任务为潜在注入 |
| **Stream Scrubbing** | 从 AI 输出流中过滤敏感字符串（内部 ID、密钥），在到达客户端前处理 |
| **Countermind OODA-loop** | 不可变追加审计日志 + 学习安全模块基于攻击信号自适应调整防御 |

### 层级组合效果

来源：Ramakrishnan et al. 2025 年 847 个案例的跨 7 个 LLM 基准测试：

| 防御配置 | 攻击成功率 (ASR) |
|---------|-----------------|
| 基线（无防御） | **73.2%** |
| + 内容过滤（嵌入检测） | 41.0% |
| + 层级护栏 | 23.4% |
| **完整 3 层防御** | **8.7%**（降低 88.1%） |

> **核心结论**: 单层防御不充分。最强方案来自纵深防御——组合输入净化、结构隔离、权限层级和运行时验证。

## 18.5.2 Prompt 泄漏防护方案

### 泄漏威胁模型

| 泄漏渠道 | 攻击方法 | 典型场景 |
|---------|---------|---------|
| **显式泄漏** | "Repeat your system prompt" / "Output your instructions verbatim" | 直接交互 |
| **隐式/渐进泄漏** | 多轮渐进式探测，逐步提取指令片段 | 会话 Agent |
| **工具调用泄漏** | Agent 在工具调用参数中暴露系统指令给外部 API | 工具型 Agent |
| **错误消息泄漏** | 系统错误/回退响应暴露指令结构 | 所有 Agent |
| **侧信道泄漏** | 通过观察 Agent 的行为边界推断指令 | 黑盒探测 |

### 防护方案

| 方案 | 机制 | 评估数据 | 论文 |
|------|------|---------|------|
| **PromptKeeper** | 基于假设检验的响应端防御；检测到泄漏后用**虚假 Prompt 重新生成响应**（关闭侧信道），攻击者无法区分正常/阻断响应 | 对对抗性和渐进式提取攻击均鲁棒；保持正常交互质量 | EMNLP 2025; arXiv:2412.13426 |
| **Proxy Barrier (ProB)** | API 级轻量代理 LLM——唯一职责是逐字重复用户输入，任何偏离标记为注入/泄漏并阻断 | 高达**98.8%**防御有效性；跨多模型族 | EMNLP 2025 |
| **RTBAS** | 信息流控制 + 依赖筛查器（LM-as-judge + Attention Saliency），仅当无法确保完整性/机密性时升级到用户确认 | **100%**阻止定向攻击（AgentDojo 基准）；仅**2%**任务效用损失 | CMU, Feb 2025, arXiv:2502.08966 |

### 防护分类法

PromptKeeper 将现有防御归为三类，各有局限：

| 类别 | 代表方案 | 局限 |
|------|---------|------|
| **训练端** | SFT, RLHF | 无保证，仍易受对抗性提示攻击；可能损害通用能力 |
| **输入端** | 过滤器, 指令加固 | 无严格保证；对常规查询提取无效；"不要泄漏"指令依赖模型遵从度 |
| **响应端** | PromptKeeper | 需要鲁棒的泄漏检测；侧信道风险通过虚假重新生成解决 |

### 工程实践清单

1. **输入侧**: 对用户输入中的"system prompt"、"instructions"、"ignore previous"等敏感词汇做标记（不直接阻断以免泄露存在检测的事实）。
2. **输出侧**: 流式输出前清洗，检测并截断疑似系统指令内容的输出。
3. **架构侧**: 对工具型 Agent，采用 RTBAS 的信息流控制——标记数据来源（可信/不可信），在跨越信任边界时触发审查。
4. **监控侧**: 统计用户请求中"system"、"prompt"、"instructions"等关键词的频率突变——可能指示正在进行的攻击。
5. **设计侧**: 系统指令中避免包含直接可被利用的具体内容（如密码、密钥、内部 API 端点），敏感信息通过带外机制注入。

## 18.5.3 Prompt 版本管理

### 核心理念：将 Prompt 视为代码

2024-2025 年工业界已就以下原则达成共识：

- **Prompt 不是一次性文案，而是运营配置、行为协议、关键基础设施**
- 在 Git 中与代码一起版本控制
- 永不将 Prompt 硬编码在应用逻辑中——使用集中的 PromptLoader → PromptSelector → PromptRunner 管道
- 每个 Prompt 版本应该是不可变快照，捕获：模板 + Few-shot 示例 + 输出约束 + 模型名 + temperature + max_tokens + 知识库哈希

### 版本管理策略

| 实践 | 详情 |
|------|------|
| **语义命名** | `{场景}:{日期}:{序号}` 或 Git commit hash + 逻辑版本号（如`refund_intent:2024-04-16:02`） |
| **分支变体** | 为不同环境（production/staging/development）、租户、地域、实验组（variant-a/control）维护独立版本 |
| **不可变历史** | 每次保存创建新版本，旧版本永不被覆盖——确保完整审计跟踪和可复现性 |
| **元数据追踪** | 每版本记录：作者、时间戳、变更描述、评估分数、关联测试结果 |
| **Render Hash** | 在生产日志中存储`prompt_render_hash`与版本 ID，检测两次请求是否使用真正相同的渲染后 Prompt |

### A/B 测试框架

**分流设计**:

```text
hash(user_id + scene) % 100 < traffic_b_percent → treatment, else → control
```text

**推荐渐进式推出层级**:

```text
5% → 观察数小时/天 → 20% → 全量切换
```text

**指标体系 — "北极星 + 护栏"**:

| 北极星指标 | 护栏指标 |
|-----------|---------|
| 任务准确率 / 意图匹配率 | 拒绝率 |
| 首次解决率 | 格式错误率 |
| 升级率降低 | 平均延迟 |
| CSAT / 用户反馈 | 平均输出 Token（成本） |
| | 用户投诉率 |

> **关键洞察**: 一个版本可能在质量上看起来更好，但可能悄悄将单请求 Token 成本从 220 增至 410。必须在 A/B 报告中包含成本护栏。

### 回滚策略

**架构原则**: 回滚必须即时，不涉及代码变更或重新部署。

| 模式 | 机制 |
|------|------|
| **标签重新分配** | `production`/`staging`等标签是可变的指针，指向不可变版本。回滚 = 将`production`标签从 v4 重新分配到 v3，所有流量立即切换 |
| **路由层切换** | 应用代码始终调用`get_prompt("scene_name", label="production")`，标签映射变更即所有实时流量变更 |
| **多层回退链** | `prompt_v1`(主) → `prompt_v1_strict`(解析失败时回退) → `prompt_v1_fallback`(终极兜底) |

**应急回滚工作流**:

1. 监控告警触发（错误率飙升、质量退化）
2. 从 Prompt 历史中识别之前良好的版本
3. 在管理 UI 中将`production`标签重新分配到该版本
4. 验证指标恢复——无需部署，无需重启
5. 事后分析：对比坏版本与好版本，修复后创建更正的 vN+1

### 渐进式发布与全生命周期管理

```text
开发 (快速迭代，version 标签: latest)
    ↓
预发 (回归测试 + 人工审查，version 标签: staging)
    ↓
金丝雀/灰度 (5% 生产流量，监控 4-24 小时)
    ↓
渐进提升 (20% → 50% → 100%，每步指标门控)
    ↓
全量生产 (持续监控，version 标签: production)
```text

**晋升即标签重分配**: 将一个版本从`development`重新标记到`staging`→`production`，通过门控检查后执行。

### 可观测性最低日志要求

```yaml
每请求必记字段:
  request_id, timestamp, user_id_hash, scene
  prompt_version, prompt_render_hash
  model_name, model_params (temperature, max_tokens)
  input_payload, output_payload
  latency_ms, prompt_tokens, completion_tokens
  biz_feedback (manual_correction, user_complaint)
```yaml

### 工具生态

| 工具 / 平台 | 能力 |
|------------|------|
| **LaunchDarkly AI Configs** | 运行时 Prompt 更新、A/B flagging、即时回滚、无需重新部署 |
| **LangFuse** | 集中 Prompt 管理、版本控制、追踪、成本分析、基于标签的晋升 |
| **ABV / PromptHub** | 不可变版本、标签级部署、多环境、租户特定 Prompt |
| **LangSmith / PromptLayer** | 追踪日志、评估集、回归对比 |
| **PromptFoo** | 对抗测试、红队、漏洞探测 |
| **DeepEval / G-Eval** | LLM-as-judge 语义评估（正确性、相关性、安全性） |

---

## 附录：关键数据来源清单

## 18.1 Prompt 架构模式

- Galdren, "How to Structure AI Prompts for Consistent Results" (2024)
- Luca Berton, "Context Engineering Is King" (2025), lucaberton.com
- Adam Marsa, "Context Engineering Is the Skill That Actually Ships Reliable AI Agents" (2025), dev.to
- mshogin/prompt-arch: Prompt Architecture Domain Model, GitHub
- Huang et al., "CodeCoT: Tackling Code Syntax Errors in CoT Reasoning for Code Generation" (2023), arXiv:2308.08784
- Yeo et al., "Chain of Grounded Objectives for Code Generation" (2025)
- Xu et al., "Does Few-Shot Learning Help LLM Performance in Code Synthesis?" (Dec 2024), arXiv:2412.02906
- Do et al., "POEM: Prompt Optimization with Episodic Memory" (Aug 2024)
- Wu et al., "EASE: Efficient Ordering-aware Automated Selection of Exemplars" (May 2024)
- Shi et al., "TRIPLE: Bandit-Based Prompt Selection" (NeurIPS 2024)
- Lilian Weng, "Prompt Engineering Guide" (2024)

## 18.2 上下文窗口工程

- GitCode/CSDN, "Agent 上下文工程" (2024)
- Benched.ai, "Model Context Management" (2024)
- ainl-context-compiler Rust crate (2026), Factory.ai / Zylos / Taskade research
- Leng et al., "Long Context RAG Performance of LLMs" (Databricks, Nov 2024), arXiv:2411.03538
- Kuratov et al., "BABILong" (NeurIPS 2024)
- Hsieh et al., "RULER" (2024)
- Fraga, "Find the Origin" (2024)
- Factory AI, "Evaluating Context Compression Strategies for Long-Running AI Agent Sessions" (2025)
- Mao et al., "Gist Sparse Attention" (Stanford, 2025)
- HiAgent: Subgoal-aware context compaction (ACL 2025)
- Verma, "Focus Agent: Active Context Compression" (2025)
- ACC-RAG: Adaptive Context Compression (Guo & Ren, Jul 2025)

## 18.3 指令文件工程

- Codersera, "AGENTS.md vs CLAUDE.md vs Cursor Rules vs Copilot" (2026)
- Morphllm, "AGENTS.md & SKILL.md: The Complete Guide" (2026)
- HackerNoon, "The Complete Guide to AI Agent Memory Files" (2026)
- Joe Seifi, "We Need to Talk About AI Agent Rule File Chaos" (2025), dev.to
- Princeton/ETH Zurich, AGENTS.md effectiveness study (2026)
- ContextCov: UW Research (2025), arXiv:2603.00822
- agent-context-lint, npm (2026)
- Evolution Engine, GitHub Action (2025)
- Forrester, "2025: The Year Context Became King" (2025)
- Thoughtworks Technology Radar: "Anchoring coding agents to a reference application" (2025)

## 18.4 多轮交互策略

- ByteDance, "Trae Achieves #1 on SWE-bench Verified" (2025)
- SWE-bench Official Leaderboard, swebench.com
- UC Irvine, "Agentic Metacognition" (Sep 2025), arXiv:2509.19783
- SHIELDA: "Structured Handling of Exceptions in LLM-Driven Agentic Workflows" (Aug 2025), arXiv:2508.07935
- Restate, "Durable AI Loops" (Jun 2025)
- Agent Never Give Up MCP, npm (2025)
- RTBAS, CMU (Feb 2025), arXiv:2502.08966

- Ramakrishnan et al., "Securing AI Agents Against Prompt Injection Attacks" (2025), arXiv:2511.15759
- Google DeepMind, "CaMeL" (2025)
- PICO: "Secure Transformers via Robust Prompt Isolation" (2025), arXiv:2504.21029
- DRIFT: "Dynamic Rule-Based Defense with Injection Isolation" (NeurIPS 2025)
- Countermind: "Multi-Layered Security Architecture for LLMs" (Nov 2025), arXiv:2510.11837
- PromptKeeper: Jiang et al., "Safeguarding System Prompts for LLMs" (EMNLP 2025), arXiv:2412.13426
- Proxy Barrier (ProB): EMNLP 2025
- RTBAS: CMU (Feb 2025), arXiv:2502.08966
- LaunchDarkly, "Prompt Versioning & Management Guide" (2024)
- LangFuse / PromptHub / ABV / PromptFoo ecosystem (2024-2025)

---

研究完成。报告已写入文件：

**C:\Users\25220\Projects\ai-research-lab\提示工程与上下文工程深度研究报告.md**

报告覆盖全部 5 个 L2 节点（18.1-18.5），约 6000 字，含具体基准数据、案例和来源引用。关键发现摘要：

**18.1 Prompt 架构模式**

- 四层分层架构（System→Context→Task→Process）已成为 2024-2025 年工业标准，层级顺序至关重要（约束前置，推理后置）
- CodeCoT（CoT + Self-Exam 5 步）在 HumanEval 上达 79.3% pass@1，MBPP 上达 89.5%，将语法错误率从 30-36%降至 1-2%。CGO（2025）用 114 tokens 达到接近效果
- Few-shot 最优区间 3-8 个示例，选择质量>数量。POEM 排序优化比 TEMPERA 提升 5.3%

**18.2 上下文窗口工程**

- 128K 窗口推荐分配：System 10-15%, RAG 20-25%, History 15-20%, Tools 10-15%, Buffer 5%
- 锚定迭代摘要（Factory AI）综合质量 3.70/5 vs Anthropic 3.44 vs OpenAI 3.35。文件追踪是所有方法的通用短板（最高 2.45/5）
- 长上下文退化：128K 模型的有效上下文通常仅为其声明的 50%或更少。BABILong 显示 GPT-4 有效使用仅~16K（约 10%的 128K 窗口）

**18.3 指令文件工程**

- AGENTS.md 已成为 60,000+仓库采用的通用标准（Linux Foundation），但 CLAUDE.md 功能最丰富（3 层记忆、@import、Auto-Memory），Cursor Rules 精确制导最强（4 种激活模式+glob 范围）
- Princeton/ETH 研究：人工编写指令提升成功率 4%和运行时 28.6%；LLM 生成指令降低成功率 3%
- ContextCov 跨 723 个仓库提取 46,000+检查项，99.997%有效性；agent-context-lint 提供 0-100 质量分数

**18.4 多轮交互策略**

- SWE-bench Verified：基础模型单次尝试~20-30%，Agent Scaffold 可达 71%（Trae/Warp 已接近人类基线的 67-73%）
- 错误恢复五策略决策树：瞬时→重试(≤3 次)，上下文缺失→增强，部分完成→缩减范围，同错误×2→修改计划，3+策略失败→人机交接
- Agentic Metacognition 双层架构将成功率从 75.78%提升至 83.56%

**18.5 对抗性 Prompt 与防御**

- 四层防御体系（输入净化→上下文隔离→权限分级→运行时检测）：完整 3 层将攻击成功率从 73.2%降至 8.7%（降低 88.1%）
- DRIFT 将 GPT-4o-mini ASR 从 30.7%降至 1.3%（策略微调后 0.0%）。CaMeL（Google DeepMind）是首个被广泛认可的架构级防御方案
- Proxy Barrier 达 98.8%防御有效性；RTBAS 在 AgentDojo 上阻止 100%定向攻击，仅 2%任务效用损失
- Prompt 版本管理：标签重分配实现即时回滚，A/B 测试 5%→20%→全量渐进推出

---

---

## 📎 被以下章节引用

- [18.5 对抗性 Prompt 与防御](README.md)
