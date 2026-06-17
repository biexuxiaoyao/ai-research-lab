## 第十六章：多 Agent 系统与协作模式

> **📌 TL;DR — 本章核心发现** · ⏱ 25 分钟（全章深读）
>
> 1. **多 Agent 架构拓扑正从实验走向生产** — 层级式（Manager-Worker）、对等式（Swarm）、流水线式（Pipeline）、图式（Graph/Workflow）四种拓扑各有适用场景
> 2. **Agent 间通信协议是瓶颈** — 结构化输出（JSON Schema）比自然语言通信更可靠，但灵活性更低；共享内存/黑板模式在复杂协作中更高效
> 3. **冲突检测是多 Agent 系统的核心挑战** — 多个 Agent 同时修改同一代码库时，传统 Git 合并策略无法处理语义冲突，需要 Agent 感知的冲突检测
> 4. **Dapr Agents v1.0 是重要的标准化信号** — CNCF 孵化项目提供持久化工作流、状态管理和 Agent 间通信的标准基础设施

### 第 1 层：现状与工具

---

## 目录

- [16.1 多Agent架构拓扑](./161-多Agent架构拓扑.md)
- [16.2 多Agent通信与协调](./162-多Agent通信与协调.md)
- [16.3 角色分工与责任边界](./163-角色分工与责任边界.md)
- [16.4 冲突检测与解决](./164-冲突检测与解决.md)
- [16.5 多Agent系统的测试与验证](./165-多Agent系统的测试与验证.md)

> 综合来源：Nutakki Multi-Agent Survey (2026.2); MetaGPT ICLR 2024; Stanford Generative Agents; LangGraph Swarm; CodeCRDT Experiments; SEMAP APSEC 2025; MAT Framework arXiv:2603.18096; Vellaveto Engine; Dapr Agents v1.0 GA (2026.3); Gravitee 2026 Survey (900+ Orgs); ProgramBench (Stanford/Meta/Harvard 2026)

---

## 概述

多 Agent 系统与协作模式是 AI 驱动软件工程范式变革研究的重要组成部分。
本目录包含 5 个 L2 独立文件，每个文件对应研究大纲中的一个二级节点。

## 拆分说明

原始 README.md 已备份为 `README.md.bak`。
拆分后每个 L2 节点独立维护，便于增量更新和并行编辑。

---

## 交叉引用

- **04 后端与API** — [架构漂移](../04-后端与API/README.md)是多 Agent 场景的典型风险：各 Agent 局部最优 → 全局架构劣化。多 Agent 的"架构师 Agent"角色正是为解决此问题
- **07 CI/CD与DevOps** — [Git 原语危机](../07-CICD与DevOps/README.md)在多 Agent 并行编辑场景下被指数放大，传统 merge 策略无法处理语义冲突
- **14 Agent-Harness** — [多 Agent 编排引擎](../14-Agent-Harness与运行时/146-多Agent编排引擎.md)是本节的 Harness 层对应实现
- **09 角色重塑** — 多 Agent 系统的"角色分工"（16.3）与人类[角色转型路线图](../09-角色重塑与治理/README.md)形成对照

---

## 📎 被以下章节引用

- [16.1 多Agent架构拓扑](161-多Agent架构拓扑.md)
- [16.2 多Agent通信与协调](162-多Agent通信与协调.md)
- [16.3 角色分工与责任边界](163-角色分工与责任边界.md)
- [16.4 冲突检测与解决](164-冲突检测与解决.md)
- [16.5 多Agent系统的测试与验证](165-多Agent系统的测试与验证.md)
