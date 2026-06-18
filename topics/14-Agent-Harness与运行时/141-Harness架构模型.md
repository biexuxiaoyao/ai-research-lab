---
title: "Agent-Harness与运行时（子章节）"
date: "2026-06-18"
lang: zh-CN
---

## 14.1 Harness 架构模型

> Harness 是 AI 编程 Agent 的"操作系统"——位于大模型 API 和开发者之间，负责工具调用拦截、权限检查、上下文组装和状态持久化。2025-2026 年分化出三条清晰的演进路径。

---

## 14.1.1 三条演进路径

2025-2026 年，AI 编程 Agent 的运行时架构分化出三条路径：**CLI 原生型**、**IDE 嵌入型**和**云端自治型**。三条路径共享同一核心逻辑（Agent Loop），但在沙盒隔离、上下文管理和用户交互模式上存在根本性分歧。

```mermaid
flowchart TB
    subgraph CLI["🖥️ CLI 原生型"]
        C1[Claude Code] --- C2[Codex CLI]
        C3["while-loop 架构<br/>98.4% 确定性基础设施<br/>仅 1.6% AI 决策逻辑"]
    end
    subgraph IDE["💻 IDE 嵌入型"]
        I1[Cursor Agent] --- I2[Windsurf Cascade]
        I3["Shadow Workspace + Git Worktree<br/>最多 8 Agent 并行<br/>即时代码补全 + Agent 模式"]
    end
    subgraph Cloud["☁️ 云端自治型"]
        D1[Devin] --- D2[Cursor Cloud Agents]
        D3["Hypervisor 级 VM 隔离<br/>Temporal 工作流引擎<br/>工单→PR 全生命周期"]
    end
    CLI -->|"终端优先<br/>CI/CD 无头执行"| USE1[开发者在本地终端操作]
    IDE -->|"IDE 内无缝体验<br/>日常全栈开发"| USE2[开发者在 IDE 内操作]
    Cloud -->|"异步长时间运行<br/>无需本地资源"| USE3[开发者离线等待结果]
    style CLI fill:#e8f0fe
    style IDE fill:#e8f5e9
    style Cloud fill:#fff3e0
```mermaid

### CLI 原生型：while-loop + 确定性基础设施

**Claude Code** 的核心架构是经典的 Agent Loop：

```javascript
queryLoop() {
  while (running) {
    response = callModel(assembledContext)
    for (toolUse in response) {
      checkPermissions(toolUse)       // 权限门控
      executeHook("PreToolUse")        // Hook 拦截
      result = dispatchTool(toolUse)   // 工具路由
      executeHook("PostToolUse")       // Hook 后处理
      appendToContext(result)          // 上下文累积
    }
  }
}
```javascript

VILA-Lab 对约 51.2 万行 TypeScript 源码的逆向分析揭示了一个关键发现：**仅 1.6% 的代码是 AI 决策逻辑，其余 98.4% 是确定性基础设施**——权限门控、上下文管理、工具路由、崩溃恢复和 Compaction 逻辑。这意味着 Harness 的可靠性不取决于模型，而取决于这 98.4% 的工程质量。

**Codex CLI**（Apache 2.0，2025 年 4 月发布）同样采用 Agent Loop，但基于 OpenAI Responses API（非 Chat Completions），默认模型为 o4-mini。其关键差异化在于：(1) 多提供商支持（OpenAI/Azure/Gemini/Ollama/DeepSeek 等），(2) 开源可审计的沙盒实现，(3) macOS Seatbelt + Linux Docker 的双平台沙盒策略。

### IDE 嵌入型：工作区隔离 + 并行 Agent

**Cursor 2.0** 引入了 **Shadow Workspace** 机制——通过 FUSE（用户态文件系统）实现写时复制（Copy-on-Write）代理文件夹。每个后台 Agent 获得独立的文件系统视图，Agent 写入操作先进入 Shadow 层，人类审查通过后才合并回实际文件系统。配合 Git Worktree，最多支持 **8 个 Agent 并行执行**——每个在独立的分支和工作树中运行，互不干扰。

**Windsurf Wave 13**（2026 年 2 月）推出 **5 路并行 Cascade Agent**，采用同样的 Git Worktree 隔离策略，但增加了专用终端面板——每个 Agent 拥有独立的终端会话，开发者可以实时观察每个 Agent 的命令执行。

IDE 嵌入型的核心优势是 **免配置体验**：开发者无需离开 IDE 即可从"代码补全"平滑过渡到"Agent 自主执行"，上下文自动从当前文件、项目结构和 Git 历史中组装。

### 云端自治型：完全隔离 + 异步执行

**Devin** 运行于云端 VM 沙盒中，采用**计划→执行→验证**三段式架构。配备专有的 SWE-1.6 执行模型（约 950 tokens/sec），从工单（Issue/Ticket）解析需求、规划实施方案、执行代码变更、运行测试验证、提交 PR——全流程无需人类实时参与。关键安全设计是 **Hypervisor 级 VM 隔离**，支持跨异步间隙的状态快照和恢复。

**Cursor Cloud Agents** 基于 Temporal 工作流引擎，每日处理 **5000 万+ Actions**。35% 的合并 PR 由 Cloud Agents 生成——开发者提交任务后关闭 IDE，Agent 在云端继续工作数小时，完成后通过 PR 通知开发者审查。

| 维度 | CLI 原生型 | IDE 嵌入型 | 云端自治型 |
|------|-----------|-----------|-----------|
| **代表** | Claude Code, Codex CLI | Cursor, Windsurf | Devin, Cursor Cloud |
| **沙盒** | 进程级 / OS 级 (Seatbelt) | Git Worktree + FUSE | Hypervisor VM |
| **并行度** | 1 Agent（本地） | 最多 8 Agent | 无限制（云端弹性） |
| **交互模式** | 终端 REPL | IDE 内无缝 | 异步（PR 回调） |
| **最佳场景** | CI/CD 无头执行、脚本化 | 日常全栈开发 | 大规模重构、跨仓库变更 |
| **上下文** | 显式文件 Read 触发 | 自动从 IDE 收集 | 从 Issue/PR 描述组装 |
| **安全模型** | 7 级信任谱系 + ML 分类器 | Shadow Workspace + 审查合并 | VM 全隔离 + 网络策略 |

---

## 14.1.2 五层架构模型

三条演进路径在实现上存在差异，但主流 Harness 实现共享一个**五层参考架构**：

```mermaid
flowchart LR
    subgraph L1["① 工具层 Tool Layer"]
        T1["Read / Edit / Bash"]
        T2["Glob / Grep / WebSearch"]
        T3["MCP 外部工具"]
    end
    subgraph L2["② 权限层 Permission Layer"]
        P1["7 级信任谱系"]
        P2["ML 分类器 (yoloClassifier)"]
        P3["PreToolUse / PostToolUse Hook"]
    end
    subgraph L3["③ 沙盒层 Sandbox Layer"]
        S1["进程级 (Seatbelt)"]
        S2["容器级 (Docker)"]
        S3["VM 级 (Hypervisor)"]
    end
    subgraph L4["④ 编排层 Orchestration Layer"]
        O1["Agent Loop 主循环"]
        O2["多 Agent 并行调度"]
        O3["工作流引擎 (Temporal)"]
    end
    subgraph L5["⑤ 观测层 Observability Layer"]
        V1["Trace / Log / Metrics"]
        V2["Token 成本归因"]
        V3["幻觉工具调用检测"]
    end
    L1 --> L2 --> L3 --> L4 --> L5
    style L1 fill:#e3f2fd
    style L2 fill:#fff8e1
    style L3 fill:#fce4ec
    style L4 fill:#e8f5e9
    style L5 fill:#f3e5f5
```mermaid

### ① 工具层 — Agent 的"手"

Claude Code 内置 6 种工具类型（Read/Edit/Bash/Glob/Grep/WebSearch），每种工具有独立的输入 Schema 和输出格式。Cursor 通过 Composer Agent 模式提供多文件编辑能力——一个 Agent 调用可同时修改多个文件。Devin 拥有完整 Shell + 编辑器 + 浏览器工具链，使其能执行"打开浏览器查看前端渲染效果 → 修改代码 → 刷新验证"的完整闭环。

**MCP（Model Context Protocol）** 将工具层从"内置"扩展为"开放生态"——9700 万 SDK 下载、21K+ 服务器（详见 [14.2 工具注册与 MCP 协议](142-工具注册与 MCP 协议.md)）。

### ② 权限层 — Agent 的"门禁"

Claude Code 的 7 级渐进信任谱系代表了当前最细粒度的权限控制：

| 级别 | 模式 | 行为 |
|:---:|------|------|
| 1 | `plan` | 仅读取和分析，不执行任何变更 |
| 2 | `default` | 每次工具调用前询问用户 |
| 3 | `acceptEdits` | 自动批准文件编辑，Bash 仍需确认 |
| 4 | `auto` | ML 分类器两阶段评估，安全的自动执行 |
| 5 | `dontAsk` | 跳过确认，仅记录日志 |
| 6 | `bypassPermissions` | 绕过所有权限检查（极度危险） |
| 7 | `bubble` | 将权限决策向上传递给父 Agent |

`auto` 模式使用独立 ML 分类器（`yoloClassifier.ts`）进行两阶段工具安全评估——第一阶段判断操作是否"显然安全"（如读取已知文件），第二阶段对边界案例进行概率评估。这确保了权限决策**独立于大模型**——即使模型产生幻觉或被注入恶意指令，权限层仍有独立的判定能力。

### ③ 沙盒层 — Agent 的"隔离舱"

三种沙盒方案在安全性和性能之间取不同平衡点：

| 方案 | 代表 | 隔离强度 | 性能开销 | 适用场景 |
|------|------|:---:|:---:|------|
| **进程级** | Apple Seatbelt (`sandbox-exec`) | ⭐⭐ | 极低 | macOS 本地开发 |
| **容器级** | Docker + iptables | ⭐⭐⭐ | 低 | Linux CI/CD、Codex CLI |
| **VM 级** | Hypervisor (Devin) | ⭐⭐⭐⭐⭐ | 中 | 云端自治 Agent、不可信代码 |

Codex CLI 在 macOS 上使用 Apple Seatbelt（`sandbox-exec`）实现进程级沙盒——限制文件系统访问范围、网络出站连接和系统调用。Linux 上降级为 Docker + iptables。Devin 从容器级升级到 Hypervisor 级 VM 隔离，支持跨异步间隙的状态快照——Agent 可以暂停、保存完整 VM 状态、数小时后恢复执行。

### ④ 编排层

多 Agent 的并行调度、工作流定义和 Agent 间通信。详见 [14.6 多 Agent 编排引擎](146-多 Agent 编排引擎.md)。

### ⑤ 观测层

Agent 行为的 Trace/Log/Metrics 三支柱、Token 成本归因和幻觉工具调用检测。详见 [14.7 Harness 可观测性](147-Harness 可观测性.md)。

---

## 14.1.3 Harness 设计原则：从模型依赖到工程确定性

五层架构的共同设计哲学可概括为三条原则：

1. **独立性原则**：每一层的决策逻辑独立于大模型。权限判定不依赖模型"自觉"，沙盒隔离不依赖模型"自律"，观测审计不依赖模型"自报"。

2. **纵深防御原则**：安全边界不在 Prompt 层（本质是建议性的），而在工具层→权限层→沙盒层的逐层强制执行。即使模型被注入恶意指令，仍需要穿透三层防御才能造成实际损害。

3. **确定性优先原则**：98.4% 的代码是确定性基础设施（非 AI 逻辑），意味着 Harness 的行为可审计、可复现、可验证。当 Agent 行为异常时，问题可以定位到具体的 Harness 层而非"AI 的幻觉"。

> **核心推论**：Harness 的可靠性不再依赖于模型的稳健性，而是依赖于权限门控的细粒度、沙盒隔离的强度和观测审计的完整性。这是从"信任模型"到"信任工程"的范式转移。

---

> **来源**：VILA-Lab《Dive into Claude Code》(arxiv 2604.14228，51.2 万行 TS 源码逆向)；Simon Willison 对 Codex CLI 的分析 (2025/04/16)；Cursor 2.0 Changelog (Shadow Workspace + FUSE)；Windsurf Wave 13 公告 (2026/02)；Cognition Devin 架构文档；Claude Code 官方文档（权限谱系 + Hook 系统）

---

## 📎 被以下章节引用

- [14.6 多 Agent 编排引擎](146-多 Agent 编排引擎.md)
- [14.7 Harness 可观测性](147-Harness 可观测性.md)
- [141-Harness 架构模型](README.md)
