# Harness 改造实战指南 — 摘要

> ⚠️ **方法限定**：以下内容提取自社区最佳实践和个人工程经验，非系统性研究。10-Phase 改造方法为规范性建议，非经实证验证的方法论。

---

## 概述

本参考文件总结了针对 **Java Spring Boot** 和 **React 前端** 项目的完整 Harness 工程化改造方法论。两份改造指南（各约 1000-1600 行）提供了详细的步骤、配置模板和代码示例。以下为提取的核心方法论摘要。

---

## 10-Phase 改造方法论

| Phase | 内容 | 关键产出 |
|:---:|------|---------|
| 1 | 项目评估与现状梳理 | 盘点项目结构、构建命令、现有规范 |
| 2 | 创建目录结构 | `.claude/{rules,hooks,skills,agents,commands,memory}/` |
| 3 | 编写 CLAUDE.md | ~80行项目索引：技术栈、构建命令、架构约束 |
| 4 | 配置 settings.json + Hooks | 权限配置 + PreToolUse/PostToolUse/SessionStart/Stop 四类 Hook |
| 5 | 创建路径作用域规则 | `.claude/rules/` 下按模块（controller/service/repository/components/hooks/api/styles/testing/state）拆分规则，通过 `paths:` frontmatter 精确匹配 |
| 6 | 创建 DESIGN.md | 架构决策记录（ADR 格式）：选择、拒绝的方案、权衡、约束 |
| 7 | 创建 Skills 和 Commands | 可复用工作流（new-api/new-component/code-review 等） |
| 8 | 创建子代理（Agents） | 专业化 Agent 定义（architect + reviewer），模型分层路由（opus/sonnet） |
| 9 | 工具链集成 | Maven Spotless+PMD+JaCoCo / ESLint 9 flat config+Prettier+Vitest |
| 10 | 分阶段推进计划 | 4 周渐进式采纳：个人示范→团队共享→制度化→知识沉淀 |

---

## Java vs React Harness 关键差异

| 关注点 | Java Spring Boot | React Frontend |
|--------|:---:|:---:|
| **架构约束重点** | 分层不允许越级调用 | 组件不允许混入业务逻辑 |
| **禁止模式** | @Autowired / SELECT * / 空 catch | default export / any / inline style / useEffect fetch |
| **Hook 检查项** | Spotless + PMD + 编译 | Prettier + ESLint + tsc + a11y + 组件行数 |
| **性能关注** | N+1 查询、循环内 DB 操作 | 不必要重渲染、大列表未虚拟化、未 code-split |
| **安全关注** | SQL 注入、密钥硬编码 | XSS、dangerouslySetInnerHTML、localStorage 敏感信息 |

---

## Monorepo 策略

对于包含前后端和共享库的 Monorepo：

- **根级 CLAUDE.md**（~80 行）：仓库级全局约定、跨包依赖方向、共享类型管理
- **Package 级 CLAUDE.md**：各子项目的技术栈、模块结构、专用命令
- **关键约束**：跨包约束必须放在根级 CLAUDE.md（始终加载），不能只放在单个 package 的 rules 里（兄弟目录的 CLAUDE.md 不会被加载）

---

## 团队采纳策略

三阶段推进：

1. **阶段 1（个人级，1-2 周）**：一个人先配好，自然展示 Demo，让同事好奇而非被要求
2. **阶段 2（团队级，3-4 周）**：验证过的 CLAUDE.md + rules/ 提交仓库，PR Review 中使用统一术语（"这个设计需要在 DESIGN.md 中记录"）
3. **阶段 3（组织级，2-3 月）**：Hooks 成为 CI 补充门禁，新成员 Onboarding 包含"阅读 CLAUDE.md"

---

## ROI 度量

建议追踪的指标（非 AI 代码行数或裸 Token 消耗量）：

- PR 审查时间（Git 平台统计）
- 返工率（Request Changes 比例）
- 规范违规数（Lint/Checkstyle 失败次数）
- 新人上手时间（入职到首次 PR 合并）
- Hook 拦截率（PreToolUse exit 2 次数，期望趋势：初期高→逐渐降低）

**参考数据**（⚠️ Salesforce 自报告，未经独立审计）：Salesforce 2026 年 4 月 vs 2025 年 4 月——Effective Output Score +151.3%、人均合并 PR +79%、人均完成工作项 +50.8%、事故总数 -5%。PR 量暴增伴随审查瓶颈转移——Faros AI 数据显示 AI 重度用户中位 PR 审查时间增加 441.5%。

---

## Compaction 持久性

当对话上下文超过窗口限制时，Harness 触发 Context Compaction。关键启示：

- ❌ 对话中口述的约定 → Compaction → 丢失
- ✅ 写在 CLAUDE.md 中 → Compaction → 从磁盘重读 → 保持
- ✅ 写在 settings.json Hooks 中 → 不受 Compaction 影响 → 保持

**设计原则**：永久的架构约定和编码规则必须写文件，永远不要只依赖对话中的口头指令。

---

> **来源**：[Claude Code 官方文档](https://code.claude.com/docs/zh-CN/hooks)；社区最佳实践（dev.to、CSDN、GitHub: bzatrok/claude-code-best-practices）；Salesforce 工程博客（2026/05）；Faros AI《AI Code Quality: The Hidden Cost Senior Engineers Pay》

---

## 交叉引用

- [14.8 指令文件加载机制](../topics/14-Agent-Harness与运行时/148-指令文件加载机制.md) — Harness 拦截层与路径规则触发机制
- [14.9 Meta-Harness自动化治理](../topics/14-Agent-Harness与运行时/149-Meta-Harness自动化治理.md) — Harness 本身的自动化维护
- [18.3 指令文件工程](../topics/18-提示工程与上下文工程/183-指令文件工程.md) — CLAUDE.md 的设计哲学与治理最佳实践
