# 14.5 Agent 生命周期管理

> Agent生命周期管理在2025-2026年从"尽力而为"到"正式状态机+崩溃恢复"完成了关键跃迁。

---

## 14.5.1 完整生命周期

多个框架定义了正式的Agent状态机：

- **AXME**：`CREATED→SUBMITTED→DELIVERED→ACKNOWLEDGED→IN_PROGRESS→WAITING→COMPLETED/FAILED/CANCELLED/TIMED_OUT`
- **OpenAgentOrchestrator**：`INIT→PLAN→EXECUTE→REVIEW→TERMINATE`
- **Parsica Ventures**：支持`start→pause→resume→abort`带Token阈值和时间间隔双策略的Checkpoint过渡
- **Devin**：任务分配（Slack/API/Windsurf IDE）→沙盒供给（云VM启动+仓库克隆）→仓库摄取（企业版支持千万Token级上下文窗口）→交互式规划（v3.0，可人工审查修改）→自主执行（编写代码、运行测试、自愈诊断）→内部代码审查→PR创建→状态持久化（CI失败或评审反馈时快照并挂起，反馈到达时恢复）

---

## 14.5.2 长时间运行Agent的监控与超时

- **Claude Code 后台Agent**：通过Ctrl+B将任务发送到后台，后台权限在启动前就预先批准，未经批准的工具自动被拒绝。`CLAUDE_CODE_DISABLE_BACKGROUND_TASKS=1`可禁用所有后台任务
- **Parsica Ventures**：Supervisor驱动的健康轮询（默认每30秒检查执行器存活），3次连续健康失败后将Venture转为`FAILED`态且标记`recoverable=True`
- **Glink Engine**（v0.3.4，2026）：JSONL追加式事件黑板，每一步成功Checkpoint，重启后精确从断点续传，内置可配置重试循环和健康检查守护进程

---

## 14.5.3 崩溃恢复与断点续传

**Dapr Agents v1.0**（2026年3月23日GA，CNCF毕业项目）提供了当前最成熟的崩溃恢复方案。每个Agent调用作为独立的持久化工作流执行——不仅仅是对话记忆，而是用户输入、中间决策、工具调用、模型响应全部持久化。Pod被驱逐或节点宕机时，Agent从故障的精确点恢复，无需开发者干预。核心机制包括：

- 事件溯源/重放模型（`ContextAwareLogger`在重放周期中静默抑制重复日志）
- 精确一次执行保证（即使多个恢复实例同时运行，Actor架构确保只有一个实例实际执行）
- 基于Dapr Workflow的持久化重试（非暂态retry+timeout，而是由工作流状态支持的长期失败重试）
- 30+状态存储后端（Redis/Postgres/DynamoDB/CosmosDB/Cassandra等）

**Devin的自愈协议**定义了四级策略：
1. RETRY（瞬时错误，最多3次）
2. FIX（代码错误，诊断+补丁→重新测试）
3. ROLLBACK（无法挽救的破坏性更改，回滚并重新规划）
4. ESCALATE（连续2次失败后的未知/关键错误，求助人工）

**OpenAgentOrchestrator** 使用SHA-256工具调用哈希防止重试时的重复外部动作，基于Redis `RPOPLPUSH`实现零丢失任务认领。

---

> **来源**：CNCF Dapr Agents v1.0 GA公告(2026/03/23)；Diagrid Dapr Agents 1.0技术解读；Parsica Ventures v0.5.0；Glink Engine v0.3.4；AXME文档；Devin架构分析

---

## 📎 被以下章节引用

- [145-Agent生命周期管理](README.md)
