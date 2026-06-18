---
title: "18.6 DESIGN.md 与意图工程"
date: "2026-06-18"
lang: zh-CN
---

## 18.6 DESIGN.md 与意图工程

> ⚠️ **方法限定**：DESIGN.md 是 2026 年社区新兴提案，非正式标准。结构性门禁的 "~100% 合规率" 数据来自社区 312+ 任务实测，非经同行评审。

---

## 18.6.1 问题的本质：代码承载结果，不承载思考路径

人类代码和 AI 代码生成遵循两种根本不同的模型：

```text
人类写代码                              AI 生成代码
─────────                              ────────────
需求理解 → 方案权衡 → 设计决策          "输出能通过测试的代码"
    ↓                                      ↑
记录决策理由（为什么选 A 不选 B）         没有"为什么"
    ↓                                      ↑
编码实现（代码承载了思考路径）             代码只承载结果
    ↓
后人可追溯、可质疑、可演进
```text

AI 代码天然缺失一整层信息：**为什么这样写**。代码能跑，但团队积累的是"知识债务"——组织内没有人能捍卫或演进它。

---

## 18.6.2 隐性架构决策与 "Vibe Architecting"

arXiv 2604.04990（Konrad et al., 2026）首次提出了 **"Vibe Architecting"** 概念：架构由自然语言 prompt 驱动，而非经过深思熟虑的设计。研究者发现**仅改变 prompt 的措辞（不改需求），就能产生架构完全不同的系统**——代码量从 141 行到 827 行，组件结构完全不同。

### AI Agent 做隐性架构决策的五种机制

| 机制 | 说明 |
|------|------|
| **模型选择** | 不同的 LLM 产生结构不同的代码——切换模型本身就是架构决策 |
| **任务分解** | Agent 如何拆分工作决定了模块边界 |
| **默认配置** | 没有显式规则时，Agent 偏向训练数据中的常见模式 |
| **脚手架自动生成** | 一个 prompt 同时决定了框架、数据库、认证、部署方案 |
| **集成协议** | MCP 等工具决定了系统与外部世界的连接方式 |

### 三个危险属性

1. **规模（Scale）**：框架、数据库、认证、部署在一次交互中全部决定
2. **速度（Speed）**：团队讨论几天的决策，AI 在几秒内完成，远超审查流程
3. **不透明（Opacity）**：决策理由埋没在生成代码中——没有 ADR，没有设计文档

---

## 18.6.3 Agentic Entropy（智能体熵增）

arXiv 2604.16323（Casserini et al., 2026, CHI Workshop）提出 Agentic Entropy 概念：**Agent 优化局部正确性，侵蚀全局设计意图。**

### 三种典型失败模式

| 模式 | 表现 |
|------|------|
| **局部优化，全局漂移** | Agent 实现了模块级功能正确，但违反系统性设计模式 |
| **语义稳定性侵蚀** | Agent 重构遗留逻辑不理解其历史理由——移除看似冗余但实际处理边界条件的代码 |
| **审查者悖论** | Agent 输出量远超人类审查能力，导致被动橡皮图章式审查 |

---

## 18.6.4 四层思考路径重建

### 第一层：意图先于代码（Intent-Before-Code）

2025-2026 年各大工具的统一收敛模式：

```text
传统（反模式）：
  用户 Prompt → AI 生成代码 → 人审查 diff
  问题：意图误解在最后才暴露，修复成本最高

意图优先（新范式）：
  用户 Prompt → AI 写需求文档 → 人确认意图 ← 误解在此修正
            → AI 写设计文档 → 人确认方案
            → AI 写任务列表 → 人确认步骤
            → AI 逐任务实现 → 每步可验证
```text

**已落地工具**：Claude Code Plan Mode、Cursor Plan Mode、Amazon Kiro 三阶段、Devin 2.0、JetBrains Junie——均强制或强烈建议 "先计划、再执行"。

### 第二层：推理溯源（Reasoning Provenance）

arXiv 2603.21692（2026 年 3 月）提出了 AER（Agent Execution Record）标准：每一步记录三个一等公民字段——`intent`（意图）、`observation`（观察）、`inference`（推理）。核心结论：推理过程不能事后还原，必须是 Agent 执行时的一等公民结构化数据。

**工程含义**：
- 调试方式转变：不再读代码理解逻辑，而是读 trace 理解 Agent 的决策
- 测试方式转变：不再是 assert 输出值，而是 eval Agent 的推理质量
- 监控方式转变：从 uptime 监控转向推理质量监控

### 第三层：结构性门禁（Structural Gates）

**Prompt 是建议，Hook 是强制。** 这是 AI Agent 工程学最激进的实践。

三层门禁设计：

```text
L1 — 任务门禁（Task Gate）
  没有 task.md → 禁止 Edit/Write

L2 — 设计门禁（Design Gate）
  新建模块/引入依赖/改数据模型 → 必须先更新 DESIGN.md

L3 — 审查门禁（Review Gate）
  PR 提交前 → 自动检查是否缺少 DESIGN.md 更新
```text

**实测数据**（⚠️ 社区 312+ 任务实测，非系统性研究）：

| 执行方式 | 合规率 |
|----------|--------|
| Prompt 指令（"请先创建任务"） | 随会话增长逐渐下降 |
| 结构性门禁（Hook 阻止） | ≈ 100%（稳定） |

### 第四层：DESIGN.md — AI 的设计决策记录

社区正在推动 DESIGN.md 作为 CLAUDE.md / AGENTS.md 之外的第三标准文件：

```text
AGENTS.md   → 怎么做事（操作层面：build、test、lint、commit）
CLAUDE.md   → 行为边界（约束层面：不能做什么、架构红线）
DESIGN.md   → 为什么这样设计（意图层面：方案选择、拒绝的替代方案、权衡）
```text

**ADR 格式**：选择什么 + 考虑过但拒绝什么 + 权衡是什么 + 约束条件。修改已有代码前先读 DESIGN.md 中的相关决策；如果认为某决策不再适用，新增一条决策记录说明变更理由，不得直接修改原有决策。

---

## 18.6.5 2026 年范式收敛

三大工具在 Plan Mode 实现上的收敛：

| 工具 | 实现方式 | 特点 |
|------|---------|------|
| Claude Code | System Prompt 标签注入模式约束，依赖 Prompt 缓存 | Agent 被提示约束而非工具约束 |
| GitHub Copilot | 物理移除写入类工具（65→22），不安全操作结构性不可行 | 更安全的默认行为 |
| Codex CLI | 仅 5 个工具，"just use the shell" 哲学 | 极简设计 |

三者都实现了相同的 Reason → Act → Observe 循环，差异在工具粒度、模式限制和多模型路由。

---

## 18.6.6 核心命题

> 当代码生成成本趋近于零时，什么变得最稀缺？
> 不是更好的代码。是**意图、决策理由、权衡记录——也就是人类的思考路径**。

AI Agent 工程学的四个支柱：

1. **Plan First** → 意图在代码之前验证
2. **Trace Everything** → 推理过程必须是一等公民结构化数据
3. **Gate Structurally** → Prompt 建议不如 Hook 强制
4. **Record Decisions** → DESIGN.md + ADR，让"为什么"和"怎么做"同等可见

---

> **来源**：arxiv 2604.04990(Architecture Without Architects)；arxiv 2604.16323(Beyond the Diff)；arxiv 2603.21692(Reasoning Provenance)；dev.to《Governing AI Agents: The Task Gate》；LangChain《In Software, the Code Documents the App. In AI, the Traces Do.》；dev.to《Alignment Is Moving into the Agent Control Plane》

---

## 交叉引用

- [18.3 指令文件工程](./183-指令文件工程.md) — CLAUDE.md/AGENTS.md 的比较与治理实践
- [14.3 权限模型与沙盒](../14-Agent-Harness 与运行时/143-权限模型与沙盒.md) — Hooks 作为结构性门禁的执行层
- [12.5 速度 vs 质量悖论](../12-横切主题/README.md) — 速度暴增背景下的质量保障问题
- [09 角色重塑与治理](../09-角色重塑与治理/README.md) — 意图与判断力的稀缺性经济学

---

## 📎 被以下章节引用

- [18.6 DESIGN.md 与意图工程](../09-角色重塑与治理/README.md)
- [12.5 速度 vs 质量悖论](../12-横切主题/README.md)
- [14.3 权限模型与沙盒](../14-Agent-Harness 与运行时/143-权限模型与沙盒.md)
- [18.6 DESIGN.md 与意图工程](183-指令文件工程.md)
- [18.6 DESIGN.md 与意图工程](README.md)
