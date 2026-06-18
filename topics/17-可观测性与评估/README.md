---
title: "第十七章：可观测性与评估基础设施"
date: "2026-06-18"
lang: zh-CN
---

## 第十七章：可观测性与评估基础设施

> **📌 TL;DR — 本章核心发现** · ⏱ 30 分钟（全章深读）
>
> 1. **Agent 可观测性需要新三支柱** — 传统 Trace/Log/Metrics 不足以覆盖 Agent 行为，需要增加：推理链追踪（Chain-of-Thought Trace）、工具调用审计（Tool Call Audit）、幻觉检测（Hallucination Detection）
> 2. **LLM-as-Judge 是评估的支柱但有盲区** — 用 LLM 评估 LLM 输出存在自我偏好偏差，需要多模型交叉验证 + 人工抽样校准
> 3. **成本归因是 Agent 可观测性的独特维度** — 每个 Agent 调用的 Token 消耗、工具调用次数、端到端延迟需要精确追踪和归因到具体任务/用户
> 4. **OpenTelemetry GenAI Semantic Conventions 正在标准化** — 2026 年发布的语义约定为 Agent 追踪提供了统一的数据模型，Langfuse/Arize/W&B Weave 等工具正在接入

### 第 1 层：现状与工具

---

## 目录

- [17.1 Agent 可观测性三支柱](./171-Agent 可观测性三支柱.md)
- [17.2 质量评估体系](./172-质量评估体系.md)
- [17.3 成本可观测性](./173-成本可观测性.md)
- [17.4 回归检测与告警](./174-回归检测与告警.md)
- [17.5 产品与工具矩阵](./175-产品与工具矩阵.md)

> 综合来源：Langfuse (MIT); Braintrust; Arize Phoenix (OpenInference); W&B Weave; OpenTelemetry GenAI Semantic Conventions (2026); Future AGI LLM Observability Guide; Fiddler AI MCP Agent Analysis; Tool Receipts arXiv:2603.10060; HaluGate; Dapr Agents v1.0 Observability; LangCost; AI Observability Market 1.3B (2025)

---

## 概述

可观测性与评估基础设施是 AI 驱动软件工程范式变革研究的重要组成部分。
本目录包含 5 个 L2 独立文件，每个文件对应研究大纲中的一个二级节点。

## 拆分说明

原始 README.md 已备份为 `README.md.bak`。
拆分后每个 L2 节点独立维护，便于增量更新和并行编辑。

---

## 交叉引用

- **06 测试与 QA** — [覆盖率信号贬值](../06-测试与 QA/README.md)与本章"行为覆盖率"（17.2.3）形成信号体系的完整迁移路径：从代码覆盖率 → 突变测试 → Agent 行为覆盖率
- **08 生产运维** — [闭环学习架构](../08-生产运维/README.md)（Observe→Detect→Diagnose→Remediate→Verify→Learn）是 Agent 可观测性的应用场景；FinOps（08.5.6）是成本可观测性（17.3）的运维实例
- **14 Agent-Harness** — [Harness 可观测性](../14-Agent-Harness 与运行时/147-Harness 可观测性.md)是本章三支柱的 Harness 层实现
- **12 横切主题** — [信号体系崩溃与重建](../12-横切主题/README.md)是本章度量迁移的宏观背景

---

## 📎 被以下章节引用

- [第 17 章：可观测性与评估](../14-Agent-Harness 与运行时/README.md)
- [17.1 Agent 可观测性三支柱](171-Agent 可观测性三支柱.md)
- [17.2 质量评估体系](172-质量评估体系.md)
- [17.3 成本可观测性](173-成本可观测性.md)
- [17.4 回归检测与告警](174-回归检测与告警.md)
- [17.5 产品与工具矩阵](175-产品与工具矩阵.md)
