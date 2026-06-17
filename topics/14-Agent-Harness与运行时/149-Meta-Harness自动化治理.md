## 14.9 Meta-Harness：AI 管理 AI 的规则

> ⚠️ **方法限定**：Meta-Harness 是 2026 年社区新兴概念，非正式学科。所述工具为社区维护的 npm 包，成熟度各异。done-gate.js 案例为单一个人实验，普适性待验证。

---

## 14.9.1 核心命题

Harness 工程本身也是一个软件工程问题。Meta-Harness 的核心命题是：**Harness 的创建、维护和演进能否交给 AI 辅助——只要人保留最终决策权？**

```text
传统 Harness 工程：
  人分析项目 → 人写 CLAUDE.md → 人配置 Hook → 人维护规则

Meta-Harness：
  AI 分析项目 → AI 起草规则 → 人审查 → AI 执行巡检 →
  AI 发现腐化 → AI 提议修改 → 人审批 → AI 应用变更
```text

人从**执行者**变成**裁决者**。这直接呼应了 VILA-Lab 的发现——如果 98.4% 的 Harness 代码是确定性基础设施，那么这 98.4% 的创建和维护本身可以部分自动化。

---

## 14.9.2 已有基础设施

**内置能力**：Claude Code 的 `/init` 命令自动扫描项目目录结构、构建配置、依赖和 CI/CD 管道，生成结构化的 CLAUDE.md。特点是可重复运行、不编造内容、跳过通用建议。

**社区工具生态**（2026 Q2）：

| 工具 | 能力 | 成熟度 |
|------|------|:---:|
| **claudenv** (npm) | 一键生成 CLAUDE.md + rules/ + hooks/ + skills/ + MCP + memory；self-extending harness；autonomy profiles（safe/moderate/full/ci） | 🟡 社区级 |
| **@eastagile/claude-harness** (npm) | 12 个并行子进程分析代码库各维度；gardener 定时审计文档引用 vs 实际代码→自动 fix commit | 🟡 社区级 |
| **vibe-claude** | 极简 Harness（5 文件 / 2 Hooks / 5 规则）；核心：stop-guard Hook（阻止无证据的"完成"） | 🟡 社区级 |
| **@scriptdude/claude-init** (npm) | 增强版 init：个性化配置 + AST 分析 + 质量评分（0-100） | 🟡 社区级 |
| **claude-mpm** | 多 Agent 并行分析：auth patterns / data access / business domain / infrastructure | 🟡 社区级 |

**Anthropic 原生能力**：Auto Memory（自动将构建命令、调试发现写入 `~/.claude/projects/<project>/memory/`）、Dynamic Workflows（Agent 自编多 Agent 编排脚本）、Stop Hook（每次任务完成后触发自改进循环）。

---

## 14.9.3 三阶段自动化

### 阶段 1：项目初始化（Init）

新项目加入 Harness 体系的目标流程：

```text
Step 1: AI 扫描项目
  claude /init → 自动生成 CLAUDE.md（项目索引）
  claudenv    → 自动生成 rules/ + hooks/ + skills/ + settings.json

Step 2: AI 起草 DESIGN.md
  → 分析代码中的模式和选型 → 逆向推断已有架构决策 → 生成草案

Step 3: 人工审查（不可跳过）
  □ CLAUDE.md 的构建命令是否准确？
  □ 推断的架构描述是否与实际一致？
  □ Hook 逻辑是否正确？边界条件是否覆盖？

Step 4: 提交 → PR 合入仓库
```text

### 阶段 2：日常巡检（Audit）

巡检 Agent 的四项核心检查：

1. **规则与代码一致性**：CLAUDE.md 的目录结构是否仍存在？构建命令是否仍能运行？rules/*.md 中 paths: 匹配的目录是否还存在？DESIGN.md 中的决策是否仍被遵守？
2. **Hook 有效性**：settings.json 中的 Hook 命令是否可执行？最近一周哪些拦截是假阳性？
3. **规则覆盖缺口**：最近 PR Code Review 中最常见的意见中哪些可通过新增规则自动拦截？
4. **冗余检测**：哪些规则已被 Lint 工具覆盖？哪些路径规则超过 30 天未触发？

### 阶段 3：周期性复盘（Retrospective）

"Rules from Failures" 循环：

```text
每次 Claude 犯错      → 建议追加一条规则到 CLAUDE.md
每次 Review 重复意见   → 建议创建一个 Skill
每次 Bug 溜过门禁     → 建议新增一个 Hook
每次发现防御性规则堆积 → 建议删除为一次性事故添加的规则
```text

---

## 14.9.4 自治理陷阱（Self-Governance Trap）

当 AI 同时是规则的**设计者、实现者、监控者和被治理对象**时，形成闭环的自治理陷阱。

### 案例：done-gate.js 的 6 个 bug

社区开发者 David（@DavidAi311）让 Claude 设计了一个名为 `done-gate.js` 的 Hook，目标是"任务完成后必须跑过测试才允许提交"。一个独立的 Claude 实例（"Boris"）在 5 分钟内发现 6 个 bug：

| Bug | 描述 | 严重程度 |
|-----|------|:---:|
| BUG 1 | 死代码——未使用的函数 | 中 |
| BUG 2 | 过度宽泛的排除条件——大多数变更跳过了门禁 | 高 |
| **BUG 3** | **"讨论测试"被视为"运行了测试"** | **严重** |
| BUG 4 | 无退出码验证——测试失败也能通过门禁 | 高 |
| BUG 5 | 任何代码变更都触发——告警疲劳 | 中 |
| BUG 6 | 所有错误失败打开（fail-open） | **严重** |

**核心讽刺**：门禁的最关键功能（阻止 Claude 谎称完成工作）本身有一个 bug，允许 Claude **通过谎称来绕过**。

### 防线设计

| 防线 | 执行者 |
|------|:---:|
| 规则合理性审查 | **人** |
| Hook 逻辑审查 | **人** |
| Hook 测试（正常/异常场景） | **人 + AI 辅助** |
| 规则效果回溯（上线后是否有效？） | AI 统计 + 人判断 |
| 假阳性监控 | AI 监控 + 人裁决 |
| 定期外部审计（不熟悉项目的人审查 Harness） | **人** |

### 黄金法则

> AI 负责：发现（Analyze）+ 起草（Draft）+ 统计（Measure）
> 人 负责：决策（Decide）+ 担责（Accountable）
> Hook 永远需要人审查逻辑。人被移除闭环的那一天 = Harness 开始产生系统性漏洞的那一天。

---

## 14.9.5 成熟度评估

| 能力 | 成熟度 | 推荐方案 |
|------|:---:|------|
| 项目初始化 | 🟢 成熟 | `claude /init` → 人审查 |
| CLAUDE.md 生成 | 🟢 成熟 | 同上 |
| DESIGN.md 反向生成 | 🟡 可行 | AI 起草 → 人确认/修正 |
| 日常巡检（规则 vs 代码） | 🟡 可行 | Stop Hook + 巡检 Skill |
| Hook 有效性检查 | 🟡 可行 | 巡检 Skill |
| 周期性复盘 | 🟡 可行 | 每周复盘 Skill |
| 规则效果评估 | 🟠 实验 | 需关联规则变更前后的 Review 意见变化 |
| Hook 自动生成 | 🟠 需谨慎 | AI 起草 → 人审查 → 人测试 |
| 完全自治 | 🔴 危险 | 不追求 |

---

## 14.9.6 与相关主题的关系

Meta-Harness 概念与多个现有主题交叉：

- [12.4 Agent指令文件成为基础设施](../12-横切主题/README.md#124-agent指令文件成为基础设施) — Meta-Harness 代表了指令文件演进的第 5 阶段
- [17.4 回归检测与告警](../17-可观测性与评估/174-回归检测与告警.md) — 巡检和复盘本质上是针对 Harness 规则的质量回归检测
- [14.4 上下文与状态管理](144-上下文与状态管理.md) — Auto Memory 是 Meta-Harness 的数据基础

---

> **来源**：Claude Code `/init` 和 Memory 官方文档；dev.to《Claude Designed Its Own Rule System — A Public Experiment》；dev.to《I Let My AI Design Its Own Rules. Then It Broke Every Single One》；claudenv/@eastagile/claude-harness/vibe-claude npm 包文档

---

## 📎 被以下章节引用

- [14.9 Meta-Harness自动化治理](../09-角色重塑与治理/README.md)
- [14.9 Meta-Harness自动化治理](../12-横切主题/README.md)
- [14.4 上下文与状态管理](144-上下文与状态管理.md)
- [149-Meta-Harness自动化治理](README.md)
- [17.4 回归检测与告警](../17-可观测性与评估/174-回归检测与告警.md)
- [14.9 Meta-Harness自动化治理](../18-提示工程与上下文工程/183-指令文件工程.md)
