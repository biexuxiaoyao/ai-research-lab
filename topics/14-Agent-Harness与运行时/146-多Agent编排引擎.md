# 14.6 多 Agent 编排引擎

> 多Agent编排在2025-2026年从单一Agent的简单并行演变为复杂的角色分工、层级委托和持久化工作流拓扑。

---

## 14.6.1 编排拓扑实现

**Claude Code Workflow** 采用计划-执行模式：主Agent在plan模式下生成任务分解，通过`TaskCreate`/`TaskUpdate`工具管理结构化任务表，子Agent（`AgentTool`）独立执行并汇报进度。每个子Agent拥有独立上下文窗口（约7x Token开销但上下文安全），支持最多10个并行子Agent，通过POSIX `flock()`实现零外部依赖的多实例协调。

**Cursor Cloud Agents** 基于Temporal工作流引擎实现大规模编排：每个Agent获得独立云端VM，子Agent（Child Workflows）复用父环境但拥有全新上下文，采用Signal-with-Start模式向运行中或新启动的工作流注入后续提示。实验性Planner/Worker/Judge模式针对超长任务（数周）：Planner作为架构师持续探索代码库并派生子规划者，Worker纯粹执行直至提交，Judge周期性评估进展。

**Windsurf Wave 13** 的5路并行Cascade Agent通过Git Worktree隔离和Arena Mode（双Agent盲比输出）实现开发期编排。

**Devin** 采用层级化多Agent系统：管理者Devin拆分大型任务→派生子Devin→内部MCP协调→Map-Reduce-Manage模式，关键原则是写入保持单线程（额外Agent贡献智能而非并行代码更改）。

---

## 14.6.2 Agent 间通信协议

三种模式各有优势：

| 模式 | 实现 | 适用场景 |
|------|------|---------|
| **消息传递** | Claude Code子Agent的summary回传、Cursor的Temporal Signal | 任务委托，清晰的所有权分离 |
| **共享状态** | Dapr Agents的Pub/Sub消息总线、Glink Engine的JSONL事件黑板 | 松散耦合的多Agent协作，至少一次投递保证 |
| **黑板模式** | Parsica Ventures的中央事件追加日志、OAO的不可变事件溯源日志 | 天然崩溃恢复——从事件日志重放即可重建完整运行时状态 |

---

## 14.6.3 工作流定义语言对比

当前存在三种范式：

**Markdown/YAML声明式**：Claude Code的`.claude/agents/*.md` + YAML frontmatter，定义name/description/tools/model/permissionMode/maxTurns/memory/skills等全部元数据；DevFlow的`workflow.yaml` + `agents.yaml` + `rules.yaml`，定义9种专业Agent和5种工作流模板。

**代码/SDK式**：Dapr Agents的Python `DurableAgent`类、defineworkflow的TypeScript虚拟机沙盒+日志序列号、Parsica Ventures的`VentureBuilder`链式API。

**纯Prompt式**：Cursor的Composer指令、Windsurf的Cascade对话指令、Spec Kit/OpenSpec/BMAD-Method的记忆文件和模板编排。

Declarative方案的YAML frontmatter已成为事实标准的Agent配置格式——Claude Code、OpenClaw、DevFlow、MCP Agent Swarm均采用此模式。Dapr Agents v1.0则代表了另一种方向：将Agent编排完全融入云原生基础设施。Cognition（Devin/Windsurf母公司）明确拒绝了"非结构化的协商Agent群"——称其"基本上是干扰"，坚持写入单线程化、智能并行化。

---

> **来源**：Claude Code Subagents/Custom Agents文档；Tembo《Claude Code Subagents: A 2026 Practical Guide》；Cursor社区论坛Long-Running Multi-Agent线程；Windsurf Wave 13公告；Cognition生产多Agent模式；Dapr Agents文档

---

## 交叉引用

- [14.4 上下文与状态管理](144-上下文与状态管理.md) — 子Agent的上下文隔离机制
- [16.3 角色分工与责任边界](../16-多Agent系统与协作/163-角色分工与责任边界.md) — 多Agent系统中的角色专业化
- [16.2 多Agent通信与协调](../16-多Agent系统与协作/162-多Agent通信与协调.md) — Agent间通信协议的深入分析

---

## 📎 被以下章节引用

- [14.6 多Agent编排引擎](141-Harness架构模型.md)
- [146-多Agent编排引擎](README.md)
