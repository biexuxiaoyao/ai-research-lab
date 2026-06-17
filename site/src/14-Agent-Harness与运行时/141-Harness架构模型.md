## 14.1 Harness 架构模型

> 2025-2026年，AI编程Agent的运行时架构分化出三条清晰的演进路径。

---

## 14.1.1 三条演进路径

2025-2026年，AI编程Agent的运行时架构分化出三条清晰的演进路径：**CLI原生型**（Claude Code、Codex CLI）、**IDE嵌入型**（Cursor、Windsurf Cascade）和**云端自治型**（Devin）。

**架构差异。** Claude Code采用经典的while-loop架构——`queryLoop`调用模型、分发工具、收集结果、循环执行。VILA-Lab对约51.2万行TypeScript源码的分析揭示了一个关键发现：**仅1.6%的代码是AI决策逻辑，其余98.4%是确定性基础设施**——权限门控、上下文管理、工具路由和恢复逻辑。Codex CLI（Apache 2.0，2025年4月发布）同样采用Agent Loop，但基于OpenAI Responses API（非Chat Completions），默认模型为o4-mini，支持多提供商（OpenAI/Azure/Gemini/Ollama/DeepSeek等）。Cursor 2.0推出Shadow Workspace机制，通过FUSE（用户态文件系统）实现写时复制代理文件夹，配合Git Worktree为每个后台Agent提供独立的文件系统视图，最多支持8个Agent并行。Windsurf Wave 13（2026年2月）推出5路并行Cascade Agent，采用Git Worktree隔离和专用终端面板。Devin则完全运行于云端VM沙盒中，采用计划-执行-验证三段式架构，配备专有的SWE-1.6执行模型（约950 tokens/sec）。

**部署拓扑对比。** CLI型（Claude Code、Codex CLI）适合终端优先的开发者、CI/CD无头执行和脚本化自动化场景。IDE嵌入型（Cursor、Windsurf）适合日常全栈开发，提供即时代码补全和免配置体验。Cloud Agent型（Devin、Cursor Cloud Agents）适合长时间异步任务——Cursor Cloud Agents基于Temporal工作流引擎，每日处理5000万+ Actions，35%的合并PR由Cloud Agents生成；Devin则实现完整的工单到PR全生命周期自动化。

---

## 14.1.2 五层架构模型

主流Harness实现共享一个五层架构：

- **工具层**：Claude Code内置6种工具类型（Read/Edit/Bash/Glob/Grep/WebSearch），Cursor通过Composer Agent模式提供多文件编辑能力，Devin拥有完整Shell+编辑器+浏览器工具链
- **权限层**：Claude Code实现7级渐进信任谱系（plan→default→acceptEdits→auto→dontAsk→bypassPermissions→bubble），其中auto模式使用独立ML分类器（`yoloClassifier.ts`）进行两阶段工具安全评估
- **沙盒层**：Codex CLI在macOS上使用Apple Seatbelt（`sandbox-exec`），Linux上使用Docker+iptables；Devin从容器级升级到Hypervisor级VM隔离，支持跨异步间隙的状态快照
- **编排层**：详见 [14.6 多Agent编排引擎](146-多Agent编排引擎.md)
- **观测层**：详见 [14.7 Harness可观测性](147-Harness可观测性.md)

---

> **来源**：VILA-Lab《Dive into Claude Code》(arxiv 2604.14228)；Simon Willison对Codex CLI的分析(2025/04/16)；Cursor 2.0 Changelog；Windsurf Wave 13公告；Cognition Devin架构文档

---

## 📎 被以下章节引用

- [141-Harness架构模型](README.md)
