## 17.1 Agent可观测性三支柱

> 来源：17-可观测性与评估 | 拆分自 README.md | 2026-06-14

---

## 17.1.1 Trace：Agent决策链路的端到端追踪方案

Agent决策链路涉及LLM调用、工具调用（Tool Call）、检索增强（RAG）、守卫决策（Guardrails）等多层嵌套执行。端到端追踪需将每次模型调用、每个工具执行、每个检索步骤包装为分布式Trace中的Span，通过`trace_id`串联全链路。

### 四家平台能力对比

| 能力维度 | Langfuse | Braintrust | Arize Phoenix | Weights & Biases Weave |
|---|---|---|---|---|
| **License** | MIT核心（企业目录独立） | 闭源商业 | Elastic License 2.0（非OSI） | 闭源（有免费层） |
| **自托管** | 是（Docker: Postgres + ClickHouse + Redis） | 仅企业版 | 是（`phoenix.launch_app()`） | 否 |
| **Span类型数** | 5种（generation, tool, span, event, agent） | 实验范围内trace | 8种（OpenInference规范） | 10+种（含Chain/Agent/Tool/Rerank） |
| **Agent原生支持** | 有agent span，支持多步决策追踪 | 沙盒化Agent Eval（带工具调用执行） | OTel原生，OpenAI Agents SDK、LlamaIndex、LangChain自动插桩 | Weave Agent Protocol，支持LangGraph/CrewAI/AutoGen |
| **OTel兼容** | 支持OTel摄取 | 不强调OTel | **OpenInference规范定义者**，OTLP优先 | 兼容OTel导出 |
| **Prompt寄存器** | 有（版本化、部署标签、环境管理） | 有（实验驱动） | 无专用寄存器 | 有Prompts管理 |
| **MCP支持** | 2026年支持 | 2025年支持 | 有限 | 2026年支持 |
| **成本追踪** | 完整（延迟+成本+Eval） | 实验范围成本 | 部分（延迟+漂移+Eval） | 完整（延迟+成本+评估通过率趋势） |
| **入门价格** | Hobby免费（50K单位/月），Core $29/月 | Starter免费，Pro $249/月 | Phoenix免费自托管，AX Pro $50/月 | Free层，Teams $89/月起 |

**关键差异：**

- **Langfuse** 是开源阵营最受欢迎的LLM可观测性平台。其Trace功能包括：Prompt/Tool Call/Response的完整链式Span；Prompt版本化管理（支持部署标签、环境隔离、回滚）；实验CI/CD集成（2026年5月发布）。
- **Arize Phoenix** 是OpenTelemetry原生的参考实现。核心优势在于自动插桩覆盖LlamaIndex、LangChain、DSPy、Mastra、Vercel AI SDK、OpenAI Agents SDK、Bedrock、Anthropic等框架（Python、TypeScript、Java均支持）。同时具备Embedding漂移检测的独特能力。
- **Braintrust** 的Agent Eval支持沙盒化工具调用执行——可在隔离环境中真实执行Agent的工具链并评估结果，在Agent多步决策评估深度上领先。
- **W&B Weave** 拥有最丰富的Span类型（10+种），对LLM链式调用、Agent决策树、工具路由等复杂拓扑的建模能力最强，适合研究导向的深度Trace分析。

### Trace采集的行业标准：OpenInference/OTel语义约定

OpenTelemetry社区和OpenInference项目共同定义了GenAI Span的标准化属性：

```json
// 请求属性
{ "llm.request.model": "gpt-4-turbo", "llm.request.provider": "openai" }
// 用量指标
{ "llm.usage.input_tokens": 245, "llm.usage.output_tokens": 312,
  "llm.usage.total_tokens": 557, "llm.usage.cost": 0.012 }
// 响应属性
{ "llm.response.status": "completed", "llm.response.duration": 2300 }
```

2025年的最佳实践共识是：**Langfuse做Trace存储+Prompt管理，Promptfoo做CI回归测试，两者配对是目前最成熟的开源方案。**

来源：FutureAGI "W&B Weave Alternatives in 2026" (2026)；Braintrust "Langfuse vs. Braintrust" (2025)；Arize Blog "LLM Observability for AI Agents" (2025)；Coralogix "OpenTelemetry for AI" (2025)

---

## 17.1.2 Log：结构化日志的最佳实践

### Schema设计原则

根据Skywork.ai的2025年生产级指南，结构化日志Schema需覆盖五大类别：

**核心Schema字段：**

| 类别 | 字段 | 说明 |
|---|---|---|
| **身份与关联** | `request_id`, `session_id`, `user_id_hash`, `trace_id`, `span_id` | 支持全链路关联查询 |
| **Prompt层** | `prompt_template_id`, `prompt_template_version`, `sanitized_prompt`, `system_instructions`, `examples_hash` | Prompt版本和内容追踪（需脱敏） |
| **模型配置** | `model.name`, `model.provider`, `model.temperature`, `model.max_tokens`, `model.top_p`, `model.seed` | 完整的模型调用参数 |
| **工具调用** | `tool_name`, `inputs`（脱敏）, `outputs`（脱敏）, `latency_ms`, `status` | 每次Tool Call的输入输出和状态 |
| **RAG上下文** | `corpus`, `retrieved_doc_ids`, `relevance_scores`, `source_attribution` | 检索质量和溯源 |
| **守卫决策** | `intervention_type`, `policy_category`, `confidence_score`, `action_taken` | PII/越狱/毒性检测的干预记录 |
| **输出信号** | `raw_text`（脱敏）, `parsed_output`, `safety_labels`, `cache_hit` | 结构化输出和缓存命中 |
| **用量/成本** | `input_tokens`, `output_tokens`, `total_tokens`, `estimated_cost_usd`, `retries` | Token消耗和预估成本 |
| **反馈信号** | `rating`, `thumbs_up/down`, `free_text_comment` | 用户反馈 |
| **部署信息** | `app_version`, `prompt_pack_version`, `evaluator_version` | 版本溯源 |

### Prompt / Tool Call / Response / Error 的日志Schema设计

**1. Prompt日志**：记录`prompt_template_id`+`prompt_template_version`而非全量Prompt文本。对Prompt内容进行`sanitized_prompt`脱敏（移除PII）。通过`prompt_template_version`实现Prompt变更的精确溯源。

**2. Tool Call日志**：每个工具调用记录为独立的`skill`对象数组——包含`tool_name`（工具名称）、`inputs`/`outputs`（脱敏后的参数）、`latency_ms`（执行耗时）、`status`（ok/error/timeout）。错误时附加`error.message`和`error.type`。

**3. Response日志**：记录`raw_text`（脱敏后）、`parsed`（结构化输出）、`safety_labels`（安全分类）、`cache_hit`（是否命中缓存）。缓存命中可节省40-70%的Token成本。

**4. Error日志**：必须包含完整的错误上下文——`error.message`、`error.stack`、`error.type`（timeout/rate_limit/api_error/validation_error/guardrail_block）、发生错误的Span位置、关联的`trace_id`和失败时的Agent状态快照。

### 七大日志反模式（2025年行业共识）

1. **全量Prompt/Response记录** → PII风险和存储爆炸
2. **缺失父Span** → 孤立的操作无法关联到上游调用
3. **日志中的密钥泄露** → API Key写入Span属性
4. **阻塞式遥测** → 热路径上的同步日志发送导致延迟激增
5. **高基数Span名称** → 动态值嵌入Span名称破坏查询效率
6. **无Token/成本追踪** → 生产环境的成本盲区
7. **缺失错误上下文** → 无法重构失败时的完整状态

来源：Skywork.ai "Observability for Skills: Best Practices in Logs, Evals, and Regression" (2025)；Traceloop "How to Trace LLM Agents and Find Failures" (2025)；Nexus Labs agent-observability (2025)

---

## 17.1.3 Metrics：关键指标定义

### 1. Task Success Rate（任务成功率）

**定义**：Agent执行完成指定目标且无错误的执行次数占比。

**细分维度：**

- **完全完成**（Full completion）：Agent独立完成整个任务
- **部分完成**（Partial completion）：任务部分达成，需人工辅助
- **一次性成功率**（One-shot success rate）：无需任何人工干预或纠正即完成任务

**关键数据**：KTH皇家理工学院对60,000条执行轨迹的研究发现，同一任务在不同运行中的成功率波动可达**24.9个百分点**。Agent在一小时内的任务成功率为70-80%，但超过四小时的任务成功率骤降至20%以下。

来源：KTH Royal Institute study on 60,000 trajectories; n8n "AI Agent Performance Metrics" (2025); IBM "AI Agent Evaluation" (2025)

### 2. Token Efficiency / Token Efficiency Ratio (TER)

**定义**：Agent完成任务所消耗的Token数量，通常表述为Token用量与完成质量的关系比。

**计算公式**：TER = 完成任务所需Token数 / 基线模型Token数（或最小必要Token数）

**关键意义**：如果模型A用100K Token（$1.50）解决问题，模型B需要2.5M Token（$37.50），基准测试分数几乎相同——那么仅凭基准测试分数会产生严重误导。Goldman Sachs预测到2030年全球Token消耗量将增长**24倍**，主要由企业AI Agent驱动。

**监控维度**：

- `input_tokens`和`output_tokens`分别追踪——常见激增原因包括对话历史膨胀、冗余上下文加载
- Reasoning Token单独计量——推理模型的内部思考Token可达可见输出的60倍
- 缓存Token与未缓存Token分离统计——缓存读取成本约为未缓存的10%

来源：Goldman Sachs Token Consumption Forecast (2025); FutureAGI "LLM Cost Tracking Best Practices" (2026); LayerLens "Evaluate AI Agents" (2025)

### 3. Time-to-Completion（完成时间）

**定义**：从触发/请求到任务完成的端到端耗时。

**子指标：**
| 子指标 | 定义 | 用途 |
|---|---|---|
| Time to First Token (TTFT) | Agent产生第一个Response Token前的延迟 | 感知性能和用户体验 |
| Tokens Per Second (TPS) / Throughput | 生成速率 | 模型效率 |
| End-to-End Latency | 完整用户请求→完成的全过程 | 终端用户SLA |
| Component Latency | 各步骤的耗时分解（Plan、Reasoning、Tool Call、Retrieval） | 瓶颈定位 |

**最佳实践**：P95/P99延迟比均值更有意义——长尾异常请求（Agent陷入循环或外部API超时）是影响用户体验的主要来源。

来源：InformIT "First Steps with AI Agents" (2025); Tricentis "AI Agent Evaluation" (2025)

### 4. Defect Rate（缺陷率）

**定义**：Agent组件或工作流中错误/失败的发生频率。涵盖范畴：

- **计划生成失败率**（Plan generation failure）
- **工具调用错误率**（Tool call error rate）——工具选择错误、执行超时、结果解析失败
- **幻觉率**（Hallucination rate）——Agent生成未基于上下文的信息的频率
- **Schema合规失败率**（Schema compliance failure）——结构化输出不符合预期格式
- **守卫触发率**（Guardrail intervention rate）——PII/越狱/毒性检测的干预频率
- **数据访问失败率**（Database access fault rate）

来源：Blaxel "AI Observability for Coding Agents" (2025); Tricentis "AI Agent Evaluation" (2025)

---

---

## 📎 被以下章节引用

- [17.1 Agent可观测性三支柱](../14-Agent-Harness与运行时/147-Harness可观测性.md)
- [17.1 Agent可观测性三支柱](README.md)
