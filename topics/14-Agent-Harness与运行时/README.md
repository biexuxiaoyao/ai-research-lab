## 第十四章：Agent Harness 与运行时基础设施

> **📌 TL;DR — 本章核心发现**
>
> 1. **Harness 是 Agent 的"操作系统"** — 工具注册、权限控制、沙盒隔离、生命周期管理、多 Agent 编排，五层架构模型承托所有上层 Agent 行为
> 2. **MCP 协议生态爆发** — 9700 万 SDK 下载、21K+ 服务器、IANA 注册表标准化，MCP 正在成为 Agent 工具注册的事实标准
> 3. **Harness 可靠性需要防御纵深** — 幻觉工具调用、权限泄露路径、上下文污染、Agent 崩溃恢复，Harness 层必须提供独立于模型稳健性的安全保障
> 4. **Meta-Harness（AI 管理 AI 的规则）是 2026 Q2 的新趋势** — 三阶段自动化（Init → Audit → Retrospective），但自治理陷阱和成熟度评估仍是开放问题

---

## 目录

| 文件 | 内容 |
|------|------|
| [141-Harness架构模型](141-Harness架构模型.md) | CLI/IDE/Cloud 三条演进路径、五层架构模型、部署拓扑对比 |
| [142-工具注册与MCP协议](142-工具注册与MCP协议.md) | MCP生态爆发（9700万SDK下载/21K+服务器）、标准化进展、工具定义规范 |
| [143-权限模型与沙盒](143-权限模型与沙盒.md) | 7级权限谱系、四种沙盒方案对比、权限泄露路径与最小权限强制方案 |
| [144-上下文与状态管理](144-上下文与状态管理.md) | 上下文窗口预算分配、三层记忆架构、上下文污染检测与隔离 |
| [145-Agent生命周期管理](145-Agent生命周期管理.md) | 正式状态机、长时间运行监控、崩溃恢复与断点续传（Dapr Agents/Devin） |
| [146-多Agent编排引擎](146-多Agent编排引擎.md) | 编排拓扑对比、Agent间通信协议、工作流定义语言三种范式 |
| [147-Harness可观测性](147-Harness可观测性.md) | Trace/Log/Metrics三支柱、Token消耗与成本归因、幻觉工具调用运行时检测 |
| [148-指令文件加载机制](148-指令文件加载机制.md) | ⚠️ 社区逆向分析：Harness拦截层、Read事件驱动触发、新建文件陷阱、paths格式要求、Compaction持久性 |
| [149-Meta-Harness自动化治理](149-Meta-Harness自动化治理.md) | ⚠️ 社区新兴概念：三阶段自动化（Init→Audit→Retrospective）、自治理陷阱、成熟度评估 |

---

## 核心发现

Agent Harness 基础设施在 2025-2026 年的核心进程是从"模型包装器"向"确定性工程系统"的转型——Claude Code 的 98.4% 确定性代码、Dapr Agents 的持久化工作流、Devin 的 Hypervisor 沙盒、MCP 的 IANA 注册表标准化共同指向一个方向：**Agent 的可靠性不再依赖于模型的稳健性，而是依赖于 Harness 层的防御纵深、状态持久性和可观测性。**

2026 年 Q2 的新趋势是 **Meta-Harness（AI 管理 AI 的规则）** 概念的出现，将 Harness 工程本身纳入 AI 辅助的范围——但仍以人为最终裁决者。

---

## 交叉引用

- [第 18 章：提示工程与上下文工程](../18-提示工程与上下文工程/README.md) — 指令文件的设计哲学与工程实践
- [第 15 章：模型选型与评估](../15-模型选型与评估/README.md) — 模型能力如何影响 Harness 设计选择
- [第 12 章：横切主题](../12-横切主题/README.md) — Agent 指令文件成为基础设施的演化路径
- [第 17 章：可观测性与评估](../17-可观测性与评估/README.md) — Harness 层观测数据的收集与分析
- [参考：Harness 改造实战指南](../../references/harness-transformation-guides.md) — Spring Boot / React 项目的 10-Phase 实践方法

---

> **来源汇总**：VILA-Lab arxiv 2604.14228；MCP Spec 2025-11-25；OWASP Agentic Skills Top 10(2026/03)；CNCF Dapr Agents v1.0；Claude Code 官方文档；社区逆向工程分析（Agiflow、dev.to）；arxiv 2604.11088（Agent 规则研究）
