## 14.6 多 Agent 编排引擎

> 多 Agent 编排在 2025-2026 年从单一 Agent 的简单并行演变为复杂的角色分工、层级委托和持久化工作流拓扑。

---

## 14.6.1 编排拓扑实现

**Claude Code Workflow** 采用计划-执行模式：主 Agent 在 plan 模式下生成任务分解，通过`TaskCreate`/`TaskUpdate`工具管理结构化任务表，子 Agent（`AgentTool`）独立执行并汇报进度。每个子 Agent 拥有独立上下文窗口（约 7x Token 开销但上下文安全），支持最多 10 个并行子 Agent，通过 POSIX `flock()`实现零外部依赖的多实例协调。

**Cursor Cloud Agents** 基于 Temporal 工作流引擎实现大规模编排：每个 Agent 获得独立云端 VM，子 Agent（Child Workflows）复用父环境但拥有全新上下文，采用 Signal-with-Start 模式向运行中或新启动的工作流注入后续提示。实验性 Planner/Worker/Judge 模式针对超长任务（数周）：Planner 作为架构师持续探索代码库并派生子规划者，Worker 纯粹执行直至提交，Judge 周期性评估进展。

**Windsurf Wave 13** 的 5 路并行 Cascade Agent 通过 Git Worktree 隔离和 Arena Mode（双 Agent 盲比输出）实现开发期编排。

**Devin** 采用层级化多 Agent 系统：管理者 Devin 拆分大型任务→派生子 Devin→内部 MCP 协调→Map-Reduce-Manage 模式，关键原则是写入保持单线程（额外 Agent 贡献智能而非并行代码更改）。

---

## 14.6.2 Agent 间通信协议

三种模式各有优势：

| 模式 | 实现 | 适用场景 |
|------|------|---------|
| **消息传递** | Claude Code 子 Agent 的 summary 回传、Cursor 的 Temporal Signal | 任务委托，清晰的所有权分离 |
| **共享状态** | Dapr Agents 的 Pub/Sub 消息总线、Glink Engine 的 JSONL 事件黑板 | 松散耦合的多 Agent 协作，至少一次投递保证 |
| **黑板模式** | Parsica Ventures 的中央事件追加日志、OAO 的不可变事件溯源日志 | 天然崩溃恢复——从事件日志重放即可重建完整运行时状态 |

---

## 14.6.3 工作流定义语言对比

当前存在三种范式：

**Markdown/YAML 声明式**：Claude Code 的`.claude/agents/*.md` + YAML frontmatter，定义 name/description/tools/model/permissionMode/maxTurns/memory/skills 等全部元数据；DevFlow 的`workflow.yaml` + `agents.yaml` + `rules.yaml`，定义 9 种专业 Agent 和 5 种工作流模板。

**代码/SDK 式**：Dapr Agents 的 Python `DurableAgent`类、defineworkflow 的 TypeScript 虚拟机沙盒+日志序列号、Parsica Ventures 的`VentureBuilder`链式 API。

**纯 Prompt 式**：Cursor 的 Composer 指令、Windsurf 的 Cascade 对话指令、Spec Kit/OpenSpec/BMAD-Method 的记忆文件和模板编排。

Declarative 方案的 YAML frontmatter 已成为事实标准的 Agent 配置格式——Claude Code、OpenClaw、DevFlow、MCP Agent Swarm 均采用此模式。Dapr Agents v1.0 则代表了另一种方向：将 Agent 编排完全融入云原生基础设施。Cognition（Devin/Windsurf 母公司）明确拒绝了"非结构化的协商 Agent 群"——称其"基本上是干扰"，坚持写入单线程化、智能并行化。

---

> **来源**：Claude Code Subagents/Custom Agents 文档；Tembo《Claude Code Subagents: A 2026 Practical Guide》；Cursor 社区论坛 Long-Running Multi-Agent 线程；Windsurf Wave 13 公告；Cognition 生产多 Agent 模式；Dapr Agents 文档

---

## 交叉引用

- [14.4 上下文与状态管理](144-上下文与状态管理.md) — 子 Agent 的上下文隔离机制
- [16.3 角色分工与责任边界](../16-多 Agent 系统与协作/163-角色分工与责任边界.md) — 多 Agent 系统中的角色专业化
- [16.2 多 Agent 通信与协调](../16-多 Agent 系统与协作/162-多 Agent 通信与协调.md) — Agent 间通信协议的深入分析

---

## 📎 被以下章节引用

- [14.6 多 Agent 编排引擎](141-Harness 架构模型.md)
- [14.4 上下文与状态管理](144-上下文与状态管理.md)
- [146-多 Agent 编排引擎](README.md)
- [16.2 多 Agent 通信与协调](../16-多 Agent 系统与协作/162-多 Agent 通信与协调.md)
- [16.3 角色分工与责任边界](../16-多 Agent 系统与协作/163-角色分工与责任边界.md)
