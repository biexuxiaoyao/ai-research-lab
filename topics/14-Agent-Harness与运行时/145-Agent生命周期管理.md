---
title: "Agent-Harness与运行时（子章节）"
date: "2026-06-18"
lang: zh-CN
---

## 14.5 Agent 生命周期管理

> Agent 生命周期管理在 2025-2026 年从"尽力而为"到"正式状态机 + 崩溃恢复"完成了关键跃迁。Dapr Agents v1.0 的持久化工作流代表了当前最成熟的工程方案——Agent 不再是一次性的"函数调用"，而是可暂停、可恢复、可审计的长期运行实体。

---

## 14.5.1 完整生命周期状态机

多个框架独立定义了正式的 Agent 状态机，虽然命名不同但状态转换逻辑高度收敛：

```mermaid
flowchart LR
    subgraph Lifecycle["Agent 生命周期状态机"]
        CREATED["🆕 CREATED<br/>已创建"] -->|"提交任务"| SUBMITTED["📤 SUBMITTED<br/>已提交"]
        SUBMITTED -->|"开始执行"| IN_PROGRESS["⚡ IN_PROGRESS<br/>执行中"]
        IN_PROGRESS -->|"等待外部输入"| WAITING["⏸️ WAITING<br/>等待中"]
        WAITING -->|"输入到达"| IN_PROGRESS
        IN_PROGRESS -->|"主动暂停"| PAUSED["⏯️ PAUSED<br/>已暂停"]
        PAUSED -->|"恢复执行"| IN_PROGRESS
        IN_PROGRESS -->|"完成"| COMPLETED["✅ COMPLETED<br/>已完成"]
        IN_PROGRESS -->|"超时"| TIMED_OUT["⏰ TIMED_OUT<br/>已超时"]
        IN_PROGRESS -->|"失败(可恢复)"| FAILED["❌ FAILED<br/>已失败"]
        FAILED -->|"重试恢复"| IN_PROGRESS
        TIMED_OUT -->|"重试"| IN_PROGRESS
        IN_PROGRESS -->|"取消"| CANCELLED["🚫 CANCELLED<br/>已取消"]
    end
    style CREATED fill:#e3f2fd
    style IN_PROGRESS fill:#fff8e1
    style COMPLETED fill:#e8f5e9
    style FAILED fill:#fce4ec
    style TIMED_OUT fill:#fff3e0
```mermaid

### 各框架的状态机对比

| 框架 | 状态定义 | 特色机制 |
|------|---------|---------|
| **AXME** | CREATED→SUBMITTED→DELIVERED→ACKNOWLEDGED→IN_PROGRESS→WAITING→COMPLETED/FAILED/CANCELLED/TIMED_OUT | 最完整的状态枚举，ACKNOWLEDGED 态支持人机交接 |
| **OpenAgentOrchestrator** | INIT→PLAN→EXECUTE→REVIEW→TERMINATE | REVIEW 阶段作为质量门禁，不合格则退回 EXECUTE |
| **Parsica Ventures** | start→pause→resume→abort | 双策略 Checkpoint：Token 阈值 + 时间间隔触发存档 |
| **Devin** | 任务分配→沙盒供给→仓库摄取→交互规划→自主执行→内部 CR→PR 创建→状态持久化 | v3.0 支持人工审查修改规划，反馈驱动恢复 |

**Devin 的完整流水线**值得展开：任务分配（通过 Slack/API/Windsurf IDE 三种入口）→ 沙盒供给（云 VM 启动 + 仓库克隆，启动延迟约 2-5 秒）→ 仓库摄取（企业版支持千万 Token 级上下文窗口）→ 交互式规划（v3.0，可人工审查修改计划步骤）→ 自主执行（编写代码、运行测试、自愈诊断）→ 内部代码审查（Devin 自身先审查再提交）→ PR 创建 → 状态持久化（CI 失败或评审反馈时快照并挂起，反馈到达时从精确断点恢复）。

---

## 14.5.2 长时间运行 Agent 的监控与超时

长时间运行的 Agent（数小时到数天）带来了独特的工程挑战：如何在不过度消耗资源的前提下确保 Agent 仍在"正确运行"而非陷入死循环？

| 策略 | 实现 | 适用场景 |
|------|------|---------|
| **心跳轮询** | Parsica Ventures：Supervisor 每 30 秒检查执行器存活，3 次连续失败 → FAILED + `recoverable=True` | 分布式 Agent 集群 |
| **预授权后台** | Claude Code：`Ctrl+B` 发送后台，权限在启动前预批准，未授权工具自动拒绝 | 本地开发 Agent |
| **事件黑板** | Glink Engine (v0.3.4)：JSONL 追加式事件日志，每步成功 Checkpoint，重启精确续传 | 需要审计追踪的场景 |
| **Token 预算硬限制** | 企业普遍实践：单 Agent 最大步数 + 总 Token 上限，防止"Token 暴走"（详见 08-生产运维 FinOps） | 所有生产环境 |

**关键反直觉洞察**：最危险的 Agent 不是失败的那个，而是**看似正常运行但效率极低**的那个——它每小时消耗数千 Token 却未产出有效结果。健康检查需要同时监控"是否活着"和"是否在有效工作"（如 PR 进展/测试通过率变化）。

### 超时策略分级

| 级别 | 超时 | 行为 |
|:---:|------|------|
| 单个工具调用 | 30-120s | 超时 → 重试（最多 3 次）→ 跳过该工具 |
| 单步推理 | 60-300s | 超时 → 要求模型重新推理 |
| 整个 Agent 会话 | 可配置（分钟到小时） | 超时 → 挂起 + 通知用户 |
| 后台 Agent 总时长 | 可配置上限 | 超时 → 强制终止 + 保留上下文快照 |

---

## 14.5.3 崩溃恢复与断点续传

### Dapr Agents v1.0：持久化工作流的黄金标准

**Dapr Agents v1.0**（2026 年 3 月 23 日 GA，CNCF 毕业项目）代表了当前最成熟的崩溃恢复方案。核心思路是将每个 Agent 调用建模为**持久化工作流**——不仅仅是对话记忆（如 LangChain Memory），而是用户输入、中间决策、工具调用、模型响应的**全量持久化**。

```mermaid
flowchart TB
    subgraph Normal["正常运行"]
        A1["用户输入 Prompt"] --> A2["Agent 规划步骤"]
        A2 --> A3["调用工具 1"]
        A3 -->|"Checkpoint"| DB[("持久化存储<br/>Redis/Postgres/<br/>DynamoDB/CosmosDB")]
        A3 --> A4["调用工具 2"]
        A4 -->|"Checkpoint"| DB
        A4 --> A5["生成最终响应"]
        A5 -->|"Checkpoint"| DB
    end
    subgraph Crash["Pod 崩溃 / 节点宕机"]
        B1["💥 故障发生"] --> B2["Dapr Workflow 检测到中断"]
        B2 --> B3["从最后 Checkpoint 重建状态"]
        B3 --> B4["精确恢复执行<br/>(Event Sourcing Replay)"]
    end
    DB --> B3
    Normal -.->|"故障"| Crash
    style Normal fill:#e8f5e9
    style Crash fill:#fce4ec
    style DB fill:#e3f2fd
```mermaid

**四项核心机制**：

1. **事件溯源/重放模型**：`ContextAwareLogger` 在重放周期中静默抑制重复日志——开发者看到的日志与正常执行完全一致，无需区分"新执行"还是"重放执行"。

2. **精确一次执行保证**：基于 Dapr Actor 架构——即使多个恢复实例同时启动（如 K8s 重启 Pod），Actor 的单线程执行模型确保只有一个实例实际执行，消除重复副作用。

3. **持久化重试**：非暂态 `retry + timeout`，而是由工作流状态支持的**长期失败重试**——Agent 可以等待数小时（等待外部 API 恢复、等待人工审批）后继续。

4. **30+ 状态存储后端**：Redis、Postgres、DynamoDB、CosmosDB、Cassandra 等——团队可以在现有基础设施上启用，无需引入新依赖。

### Devin 的四级自愈协议

Devin 定义了递增的四级恢复策略，从自动化到人工介入：

| 级别 | 策略 | 触发条件 | 行为 |
|:---:|------|---------|------|
| 1 | **RETRY** | 瞬时错误（网络超时/API 限流） | 自动重试最多 3 次，指数退避 |
| 2 | **FIX** | 代码错误（测试失败/lint 报错） | 诊断 → 生成补丁 → 重新测试 |
| 3 | **ROLLBACK** | 不可挽救的破坏性更改 | 回滚到上一个 Checkpoint → 重新规划方案 |
| 4 | **ESCALATE** | 连续 2 次失败后的未知/关键错误 | 挂起 + 保存完整上下文 + 通知人工介入 |

### OpenAgentOrchestrator 的幂等性保障

使用 **SHA-256 工具调用哈希**防止重试时的重复外部动作——每个工具调用（如 `POST /api/orders`）被哈希后存入 Redis。重试前检查哈希是否已存在，若存在则跳过执行直接返回缓存结果。基于 Redis `RPOPLPUSH` 实现**零丢失任务认领**——Worker 崩溃时，正在处理的任务自动回到队列头部。

---

> **来源**：CNCF Dapr Agents v1.0 GA 公告 (2026/03/23)；Diagrid Dapr Agents 1.0 技术解读；Parsica Ventures v0.5.0；Glink Engine v0.3.4 (2026)；AXME 文档；Devin 架构分析；OpenAgentOrchestrator 设计文档

---

## 📎 被以下章节引用

- [145-Agent 生命周期管理](README.md)
