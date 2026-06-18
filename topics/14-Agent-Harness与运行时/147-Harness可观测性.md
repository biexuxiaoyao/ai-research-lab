---
title: "14.7 Harness 的可观测性"
date: "2026-06-18"
lang: zh-CN
---

## 14.7 Harness 的可观测性

> Agent 行为可观测性在 2025-2026 年从"事后看 Token 消耗列表"快速演进为正式的 Trace/Log/Metrics 三支柱体系。

---

## 14.7.1 Trace/Log/Metrics 三支柱

**Future AGI 的 Agent Command Center** 代表了最完整的商业方案：端到端的 Agent 会话 Trace（每一步工具调用、推理决策、输入输出和错误），OpenTelemetry GenAI 语义约定作为 2026 年度的追踪标准（`gen_ai.client.token.usage`、`gen_ai.client.cost.usd`、`gen_ai.request.model`等），OpenInference（Apache 2.0）发布`llm.*`/`retrieval.*`/`tool.*`/`embedding.*`/`chain.*`规范属性命名空间。

**Dapr Agents** 提供最完整的开源方案：基于 W3C Trace Context 传播的完整 OpenTelemetry 追踪（跨 Agent、工具和 LLM 调用），Prometheus 指标暴露，`ContextAwareLogger`自动处理重放日志去重。

**各大 Harness 的观测成熟度**：

| Harness | 观测能力 |
|---------|---------|
| Claude Code | `/context`显示实时上下文使用量、`/cost`显示 Token 消耗和费用、`/doctor`诊断安装问题、`.jsonl`格式 Sidechain Transcript 记录子 Agent 完整执行历史 |
| Cursor | Agent Window 提供运行时 Agent 列表视图 |
| Devin | Web Dashboard 展示任务执行步骤和状态 |

**第三方观测工具生态**：Langfuse（自托管、MIT 许可）、LangSmith（LangChain 生态整合）、Helicone（基于代理，零代码改 URL）、AgentOps（400+集成、会话回放、时间旅行调试）。

---

## 14.7.2 Token 消耗追踪与成本归因

行业共识：成本是一个 Span 属性，不是独立的账单问题。标准实现模式为：网关处理器在响应返回前设置`llm.token_count.prompt`/`completion`/`total`和`llm.cost_usd`到 Span 上。多层预算体系（组织→团队→用户→密钥→标签）在网关层强制执行，80%警告阈值+硬/软模式，结构化 429 响应告知调用者哪个层级被阻止。

LangCost（开源 npm 包）代表了本地成本智能方向——6 条浪费检测规则（工具失败、Agent 循环、重试模式、高输出、低缓存、模型洞察），兼容 Claude Code/OpenClaw/Warp/Cline。

关键指标已从 **Cost-per-Token** 转向 **Cost-per-Outcome**（每次解决的对话成本、每个被接受的 PR 成本等）——这能捕获便宜模型循环 2 倍多导致结果反而更贵的退化情况。

---

## 14.7.3 幻觉工具调用的运行时检测

2025 年的前沿方案汇集到同一范式：**不信任 LLM 会诚实地报告工具返回了什么**。具体技术包括：

- **密码学工具收据**（NabaOS/Tool Receipts）：HMAC 签名的工具执行证明——LLM 从未持有签名密钥因此无法伪造，实现 94.2%的伪造工具引用检测、87.6%的计数误报检测、91.3%的虚假缺失声明检测，约**15ms**验证开销
- **Token 级实时检测**（HaluGate）：Rust/Candle 原生实现（<500ms 冷启动），Sentinel（ModernBERT，~12ms）判断 Prompt 是否需要事实核查→Detector（token 级二分类，~45ms）标记无支撑 Token→Explainer（NLI，~18ms），总延迟**76-162ms**
- **Go SDK 运行时验证**（hguard-go v0.5.0）：Schema 验证+上下文感知策略+自动纠正工具名称拼写错误
- **声明到证据的溯源图**（Statsig/Future AGI/Revefi）：每个断言必须可追溯到特定工具输出或源数据

---

> **来源**：Future AGI《What Is LLM Observability? A 2026 Architecture Guide》；Fiddler AI《Your MCP Agent Is Failing Silently》(2026/05)；arxiv 2603.10060(Tool Receipts)；HaluGate 技术博文；Dapr Agents v1.0 Observability 文档

---

## 交叉引用

- [17.1 Agent 可观测性三支柱](../17-可观测性与评估/171-Agent 可观测性三支柱.md) — 更深入的可观测性框架分析
- [17.3 成本可观测性](../17-可观测性与评估/173-成本可观测性.md) — Token 消耗与成本归因的详细实践
- [14.3 权限模型与沙盒](143-权限模型与沙盒.md) — 工具执行收据与权限控制的结合

---

## 📎 被以下章节引用

- [14.7 Harness 可观测性](141-Harness 架构模型.md)
- [14.3 权限模型与沙盒](143-权限模型与沙盒.md)
- [147-Harness 可观测性](README.md)
- [17.1 Agent 可观测性三支柱](../17-可观测性与评估/171-Agent 可观测性三支柱.md)
- [17.3 成本可观测性](../17-可观测性与评估/173-成本可观测性.md)
