## 第十八章：提示工程与上下文工程

> **📌 TL;DR — 本章核心发现** · ⏱ 45 分钟（全章深读）
>
> 1. **Prompt 从"提示词"升级为"工程制品"** — 需要版本控制、A/B 测试、回归检测、CI/CD 集成的完整工程化流程
> 2. **上下文窗口工程是 Agent 性能的核心杠杆** — 如何在有限窗口内装入最相关的信息（而非最多信息）决定了 Agent 的决策质量
> 3. **指令文件（CLAUDE.md/AGENTS.md/.cursorrules）成为关键的"Prompt 基础设施"** — 从运行时 Prompt 中抽离出持久化的项目级指令，实现跨会话一致性
> 4. **DESIGN.md 与"意图工程"（Intent Engineering）是新兴前沿** — 将"你想要什么"从 Prompt 中提升为独立的、结构化的工程制品，与"怎么做"（代码）分离

### 第 1 层：现状与工具

---

## 目录

- [18.1 Prompt架构模式](./181-Prompt架构模式.md)
- [18.2 上下文窗口工程](./182-上下文窗口工程.md)
- [18.3 指令文件工程](./183-指令文件工程.md)
- [18.4 多轮交互策略](./184-多轮交互策略.md)
- [18.5 对抗性Prompt与防御](./185-对抗性Prompt与防御.md)
- [18.6 DESIGN.md与意图工程](./186-DESIGN.md与意图工程.md) ⚠️ 社区新兴提案

> 综合来源：Galdren 4-Layer Prompt Architecture (2024); Luca Berton Context Engineering (2025); Adam Marsa Agent Context Stack (2025); CodeCoT (arXiv:2308.08784); CGO (2025); POEM (2024); Claude Code Context Window Docs; Succession/Identity Cycle (2025); arXiv:2601.06007 Prompt Caching; Microsoft Research Context Utilization (2025); Anthropic Context Editing Blog

---

## 概述

提示工程与上下文工程是 AI 驱动软件工程范式变革研究的重要组成部分。
本目录包含 5 个 L2 独立文件，每个文件对应研究大纲中的一个二级节点。

## 拆分说明

原始 README.md 已备份为 `README.md.bak`。
拆分后每个 L2 节点独立维护，便于增量更新和并行编辑。

---

## 交叉引用

- **01 需求工程** — [SDD 四阶段门控流程](../01-需求工程/README.md)（Constitution→Specify→Plan→Tasks）是一种"结构化 Prompt 工程"：每一阶段的输出是下一阶段的输入约束
- **13 Markdown工程化** — [指令文件生态](../13-Markdown工程化/README.md)（CLAUDE.md/AGENTS.md/Cursor Rules）是本章"指令文件工程"（18.3）的工程基础设施
- **14 Agent-Harness** — [指令文件加载机制](../14-Agent-Harness与运行时/148-指令文件加载机制.md)揭示了 Harness 层如何实际消费本章设计的指令文件
- **12 横切主题** — [Vibe Architecting](../12-横切主题/README.md)的隐性架构决策（12.5）正是 DESIGN.md（18.6）要解决的问题

---

## 📎 被以下章节引用

- [第 18 章：提示工程与上下文工程](../14-Agent-Harness与运行时/README.md)
- [18.1 Prompt架构模式](181-Prompt架构模式.md)
- [18.2 上下文窗口工程](182-上下文窗口工程.md)
- [18.3 指令文件工程](183-指令文件工程.md)
- [18.4 多轮交互策略](184-多轮交互策略.md)
- [18.5 对抗性Prompt与防御](185-对抗性Prompt与防御.md)
- [18.6 DESIGN.md与意图工程](186-DESIGN.md与意图工程.md)
