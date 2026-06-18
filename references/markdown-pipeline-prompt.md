# Markdown 工程化管线 — 分析提示词

> 将以下内容完整复制给目标大模型，即可获得对本项目的独立分析。

---

## 背景

2024-2026 年，AI 编程 Agent 的爆发使 Markdown 从"轻量标记语言"升级为"AI Agent 的核心交互格式"——`CLAUDE.md`、`AGENTS.md`、Spec 文档、研究知识库，全部是 Markdown。这要求以**工程思维**对待 Markdown：它需要 AST 解析、LSP 导航、Lint 检查、链接验证、CI 集成——就像代码一样。

本项目 `ai-research-lab` 是一个 AI 驱动软件工程范式变革的研究知识库，包含 11 个研究方向、341 个研究节点、14 个 Markdown 文件。我们为其搭建了完整的 Markdown 质量管线。

## 项目结构

```text
ai-research-lab/
├── CLAUDE.md                        # 项目配置（Agent 自举指令）
├── RESEARCH-OUTLINE.md              # 研究大纲（Markmap 兼容的思维导图源文件）
├── assemble.py                      # 动态文档装配器（按深度/主题/路径拼装）
├── check.sh                         # 一键质量门禁（串联三层检查）
├── check_links.py                   # 内部链接验证器（零依赖 Python）
├── .markdownlint.json               # Lint 规则配置
├── reports/                         # 总纲零部件
│   ├── 00-引言.md
│   ├── 10-交叉洞察.md
│   └── 11-结论与参考文献.md
├── topics/                          # 各研究方向（L1=目录，L2=超 500 行自动拆分）
│   ├── 01-需求工程/README.md
│   ├── 02-原型设计/README.md
│   ├── 03-前端开发/README.md
│   ├── 04-后端与 API/README.md
│   ├── 05-数据库与数据层/README.md
│   ├── 06-测试与 QA/README.md
│   ├── 07-CICD 与 DevOps/README.md
│   ├── 08-生产运维/README.md
│   ├── 09-角色重塑与治理/README.md
│   └── 10-Markdown 工程化/README.md
├── references/
│   ├── markdown-engineering-tools.md  # 工具生态全景（10 维度调研）
│   └── markdown-pipeline-prompt.md    # 本文件
└── notes/
```text

## 管线架构

### 三层质量门禁

```text
./check.sh
    ├── 第 1 层：markdownlint-cli2       结构规范检查
    │   （标题层级、空行、列表格式、代码块语言标签）
    │
    ├── 第 2 层：check_links.py          内部链接验证
    │   （[text](path) / [[wiki-link]] / #anchor）
    │
    └── 第 3 层：assemble.py full        装配完整性验证
        （全量文档能否成功拼装为完整报告）
```text

当前状态：**15 个文件，0 errors，31 个内部链接全有效，装配产出 1186 行。**

### 动态装配器（assemble.py）

零依赖 Python 脚本，提供 6 种装配模式：

```bash
python assemble.py status              # 健康报告（每文件行数/拆分建议）
python assemble.py topic 01            # 按主题装配
python assemble.py depth 3             # 按深度装配（L3 = 标准分析）
python assemble.py path 1.1.1          # 按大纲路径装配
python assemble.py full output.md      # 全量装配为完整报告
python assemble.py suggest-splits      # 识别超 500 行文件，建议拆分
```text

核心逻辑：
- 读取 `RESEARCH-OUTLINE.md` 解析 341 个节点的知识树
- 节点编号（如 `1.1.1`）→ 文件路径映射（如 `topics/01-需求工程/README.md`）
- L2 节点优先找独立文件，不存在则 fallback 到父级 README.md
- 自动检测文件行数：< 300 健康 / 300-500 关注 / > 500 建议拆分

### 链接验证器（check_links.py）

零依赖 Python 脚本，校验三类内部引用：

- `[text](./path/to/file.md)` 和 `[text](./path.md#anchor)` — 文件路径 + 锚点
- `[[wiki-link]]` — Obsidian 风格的跨文件引用
- `[text](#heading)` — 同文件内锚点

特性：跳过代码块和内联代码中的链接（避免语法示例被误报），支持 `--strict`（遇错退出非零）、`--json`（结构化输出）。

### Lint 配置（.markdownlint.json）

基于 `markdownlint-cli2`，针对研究型文档定制：
- 关闭 MD025（多 H1）— 大纲文件有多个顶层标题
- 关闭 MD029（有序列表前缀）— 参考文献跨节编号
- 关闭 MD040（代码块语言标签）— 允许 ASCII 图
- 关闭 MD013（行长度）— 研究文档有长段落和表格

## 设计原则

1. **Markdown 是结构，不是文本**：用它自带的 `#` 层级、`[link]`、`[[wiki]]` 语法构建可导航、可检查、可重构的知识图谱
2. **管道而非平台**：每个工具做一件事（Lint / Link / Assemble），通过 `check.sh` 编排
3. **零依赖优先**：`assemble.py` 和 `check_links.py` 仅用 Python 标准库；lint 依赖 `markdownlint-cli2`（npx 免安装）
4. **渐进式复杂度**：单文件 < 300 行时保持简单，超过 500 行自动建议拆分，不预先过度设计
5. **Agent 自举**：CLAUDE.md 让 AI Agent 启动时自动读取管线配置和研究状态

## 工具栈对照

| Java 工程工具 | Markdown 工程对应 |
|-------------|-----------------|
| javac → AST | tree-sitter / remark-parse |
| IntelliJ 符号表 | Marksman LSP |
| Checkstyle / ESLint | markdownlint-cli2 |
| 编译依赖检查 | check_links.py（死链检查） |
| Find Usages | Marksman Find References |
| Rename Refactoring | Marksman Rename |
| Maven Assembly | assemble.py full |
| CI Quality Gate | check.sh |

## 个人工作流

```text
Claude Code (CLI+AI)  →  生产/消费引擎
VS Code + Marksman    →  编辑 + LSP 导航（Ctrl+Shift+O / F12 / Shift+F12）
Typora                →  WYSIWYG 预览校验
Pandoc                →  多格式编译（PDF/HTML/DOCX）
check.sh              →  提交前质量门禁
```text

## 供分析的问题

请从以下角度分析这套体系：

1. **架构评价**：三层管线（Lint → Link → Assemble）的设计是否合理？有无遗漏的质量维度？
2. **可扩展性**：当文件数从 15 增长到 150 时，这套管线会遇到什么瓶颈？如何应对？
3. **与其他工程体系的类比**：这套 Markdown 管线与代码 CI/CD 管线的对等映射是否完整？缺少什么？
4. **AI 原生性**：哪些环节应该进一步 AI 化（例如 AI 自动修复断链、AI 检测语义漂移）？
5. **团队协作**：如果多人同时编辑这个知识库，管线需要增加什么（Merge 策略、冲突检测、变更审批）？
6. **工具替代**：当前选型（markdownlint + 自研 link checker + 自研 assemble）是否有更好的开源替代？
7. **反模式**：这套管线是否可能过度工程化？对于 15 个文件的规模，三层检查是否合理？
