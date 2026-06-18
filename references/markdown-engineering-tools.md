# Markdown 工程化工具全景 — 2026

> **背景**：AI 的爆发使得 Markdown 从"轻量标记语言"升级为"AI Agent 的核心交互格式"。`CLAUDE.md`、`AGENTS.md`、Spec 文档、知识库——全部是 Markdown。这要求我们以**工程思维**对待 Markdown：它需要 AST 解析、Lint 检查、链接验证、重构同步、CI 集成——就像代码一样。

---

## 目录

1. [AST 解析与结构化处理](#1-ast-解析与结构化处理)
2. [LSP 语言服务器（代码导航级体验）](#2-lsp-语言服务器)
3. [Lint 与风格检查](#3-lint-与风格检查)
4. [链接检查（死链检测）](#4-链接检查)
5. [交叉引用与知识图谱](#5-交叉引用与知识图谱)
6. [结构化搜索（AST 级查询）](#6-结构化搜索)
7. [结构化 Diff 与语义合并](#7-结构化-diff-与语义合并)
8. [文档构建与发布（SSG）](#8-文档构建与发布)
9. [CI 集成模式](#9-ci-集成模式)
10. [AI 原生工具（MCP/Agent）](#10-ai-原生工具)
11. [针对 ai-research-lab 的推荐工具栈](#11-推荐工具栈)

---

## 1. AST 解析与结构化处理

把 Markdown 当代码解析的基础设施。

### 1.1 tree-sitter 体系

| 工具 | 语言 | 用途 |
|------|------|------|
| **[tree-sitter-markdown-text](https://github.com/ophidiarium/tree-sitter-markdown-text)** | C (tree-sitter grammar) | 为文本分析设计的专用语法——区分 `word_token` / `numeric_token` / `identifier_like_token`，解析 Heading、Code Block、Table、Callout、Front Matter |
| **[tree-sitter-analyzer](https://github.com/aimasteracc/tree-sitter-analyzer)** | Python (MCP) | 支持 17 种语言的 AST 解析器，含 Markdown。提供 `get_code_outline`（层级大纲）、`query_key` 结构化查询。输出 TOON 格式，**比 JSON 省 54-56% token** |
| **[ast-grep](https://github.com/ast-grep/ast-grep)** | Rust | YAML 规则驱动的结构化搜索工具。含 `ast-grep-mcp` 提供 `dump_syntax_tree` / `find_code` / `find_code_by_rule` |

### 1.2 remark/unified 生态

| 工具 | 用途 | 关键数据 |
|------|------|----------|
| **[remark](https://github.com/remarkjs/remark)** | Markdown → mdast（AST）→ 插件变换 → Markdown | 150+ 插件，micromark 解析器，CommonMark+GFM 兼容 |
| **[remark-gfm](https://github.com/remarkjs/remark-gfm)** | GitHub Flavored Markdown 支持 | 表格、任务列表、删除线、自动链接 |
| **[remark-toc](https://github.com/remarkjs/remark-toc)** | 自动生成目录 | 基于 AST 级 Heading 提取 |
| **[remark-lint](https://github.com/remarkjs/remark-lint)** | AST 级结构检查 | ~80 条规则插件 |
| **[remark-directive](https://github.com/remarkjs/remark-directive)** | `:::name{...}` 指令语法 | 可扩展的自定义块级语法 |
| **[@adobe/remark-gridtables](https://github.com/adobe/remark-gridtables)** | ASCII 网格表格解析 | Adobe 维护，v3.0.20 (2026.4) |

### 1.3 关键区别

```text
tree-sitter → 通用 AST（多语言，IDE/LSP 用）
remark      → mdast 专有 AST（Markdown 的"编译 IR"）
             ↓
          remark 更适合做 Markdown→Markdown 变换（如重构、格式化）
          tree-sitter 更适合做跨语言的结构化搜索
```text

---

## 2. LSP 语言服务器

让 Markdown 文件获得 IDE 级导航体验——Go to Definition、Find References、Rename。

### 2.1 核心 LSP

| 工具 | 亮点 | 安装 |
|------|------|------|
| **[Marksman](https://github.com/artempyanykh/marksman)** ⭐ 推荐 | `[[wiki-link]]` 跳转、跨文件 Heading 引用查找、重命名重构、补全 | VS Code 扩展 "Marksman" |
| **VS Code 内置 Markdown LSP** | 已预装，零配置。`[text](#heading)` 的 Goto Def / Find All References / Rename | 无需安装 |
| **[Zeta Note](https://github.com/keynmol/zeta-note)** | `[:note@##heading]` 语法，补全、Hover、Diagnostics | VS Code 扩展 |

### 2.2 能力矩阵

| 能力 | VS Code 内置 | Marksman | Zeta Note |
|------|:---:|:---:|:---:|
| `[text](#heading)` 跳转 | ✅ | ✅ | ❌ |
| `[[wikilink]]` 跳转 | ❌ | ✅ | ❌ |
| `[:note@##heading]` 跳转 | ❌ | ❌ | ✅ |
| Heading 重命名（自动更新引用） | ✅ | ✅ | ✅ |
| Find All References | ✅ | ✅ | ✅ |
| 跨文件跳转 | ✅ | ✅ | ✅ |
| 补全 | ✅ (文件名) | ✅ (文件名+Heading) | ✅ |

---

## 3. Lint 与风格检查

类似 ESLint / Checkstyle 之于代码。

### 3.1 核心工具

| 工具 | 语言 | Stars | 规则数 | 定位 |
|------|------|-------|--------|------|
| **[markdownlint-cli2](https://github.com/DavidAnson/markdownlint-cli2)** | Node.js | 5.9K | 60 | **结构规则**—标题层级、空行、尾随空格、代码块语言标记 |
| **[Vale](https://github.com/errata-ai/vale)** | Go (单二进制) | 4.5K | 可定制 | **文风规则**—术语一致性、语气、拼写、词汇替换 |
| **[remark-lint](https://github.com/remarkjs/remark-lint)** | Node.js | 1K | 80+ | **AST 级规则**—可编程定制 |

### 3.2 推荐策略：markdownlint + Vale 双卡

```yaml
# GitHub Actions CI 示例
steps:
  # 结构检查（类似 Checkstyle）
  - uses: DavidAnson/markdownlint-cli2-action@v19
    with:
      globs: "**/*.md"

  # 文风检查（类似 EditorConfig + 术语表）
  - uses: errata-ai/vale-action@v3
    with:
      files: topics/ reports/
```text

---

## 4. 链接检查

类似"编译时依赖检查"——确保所有引用路径有效。

### 4.1 核心工具

| 工具 | 语言 | 检查范围 | 亮点 |
|------|------|----------|------|
| **[lychee](https://github.com/lycheeverse/lychee)** ⭐ | Rust | 外部 URL + 本地路径 + 锚点 | 速度最快，官方 GitHub Action，生态最成熟 |
| **[Linkspector](https://github.com/UmbrellaDocs/linkspector)** | TS | 外部 URL + JS 渲染页面 | Puppeteer 渲染 SPA 页面，**误报率极低** |
| **[Zenzic](https://github.com/PythonWoods/zenzic)** | Python | 链接 + 锚点 + 孤立文件 + 安全 | **安全扫描**—检测泄露的 API Key、路径遍历攻击 |
| **[md-kit](https://www.npmjs.com/package/@safetnsr/md-kit)** | TS | `[[wikilinks]]` + 相对路径 | **自动修复**—`md-kit fix` 修正断链，`md-kit mv` 移动文件并更新所有引用 |

### 4.2 快速对比

| | lychee | Linkspector | Zenzic | md-kit |
|------|:---:|:---:|:---:|:---:|
| 外部链接 | ✅ | ✅ (JS 页面友好) | ✅ | ❌ |
| 本地文件 | ✅ | ✅ | ✅ | ✅ |
| 锚点/Hash | ✅ | ❌ | ✅ | ❌ |
| Wiki-link | ❌ | ❌ | ❌ | ✅ (含自动修复) |
| 安全检测 | ❌ | ❌ | ✅ (API Key 泄露) | ❌ |
| CI 集成 | GitHub Action | GitHub Action + Reviewdog | `uvx` / `pip` | CLI exit code |

---

## 5. 交叉引用与知识图谱

类似"Find Usages"和"Call Graph"——理解文档间的引用关系。

### 5.1 知识图谱构建

| 工具 | 类型 | 核心能力 |
|------|------|----------|
| **[obsidian-parse](https://github.com/agent-hanju/obsidian-parse)** | Python 库 | 解析 vault 中所有 `[[wikilinks]]`、Embed、Tag、Front Matter → 输出 D3 兼容图 (`{nodes, links}`)。单依赖 (PyYAML) |
| **[mindgrove](https://www.npmjs.com/package/mindgrove)** | npm CLI | 爬取 Markdown 文件夹 → 注入 YAML frontmatter → 构建相似度矩阵 → **自动写入双向 `[[wikilinks]]`** |
| **[memex-md](https://pypi.org/project/memex-md/)** | Python CLI | 语义搜索 + wiki-link 图遍历 → SQLite。`search` (语义) / `explore` (出链+回链+相似) / `rename` (更新所有引用) |
| **[algrophy](https://www.npmjs.com/package/algrophy)** | npm CLI | 30 秒内将任意 Markdown 文件夹转为交互式知识图谱 Web 页面 |

### 5.2 Agent 集成

| 工具 | 类型 | 核心能力 |
|------|------|----------|
| **[markscribe](https://www.npmjs.com/package/markscribe)** | MCP Server | 24 个工具——`get_backlinks` / `find_broken_links` / `find_orphans` / `find_unlinked_mentions` |
| **[graph-context-for-claude-code](https://github.com/senna-lang/graph-context-for-claude-code)** | Obsidian 插件 | 在 Claude Code 中暴露 Obsidian 图谱上下文——内联嵌入 + wiki-link 摘要 + 回链 |

### 5.3 对本项目的意义

```text
RESEARCH-OUTLINE.md 中的节点编号（如 1.1.1）
    ↓ 被交叉引用
topics/01-需求工程/README.md  ← 定义节点
topics/04-后端与 API/README.md  ← "如 1.1.1 节所述"
reports/10-交叉洞察.md        ← "SDD 三层模型揭示了..."
    ↓ 使用 wiki-link 语法
[[01-需求工程#1.1.1 SDD 三层成熟度模型]]
    ↓ 配合 Marksman LSP
Ctrl+Click 跳转 / Find All References / Rename 自动更新
```text

---

## 6. 结构化搜索

类似 IntelliJ "Structural Search"——不是搜文本，是搜 AST 节点。

### 6.1 核心工具

| 工具 | 语言 | 核心能力 |
|------|------|----------|
| **[ast-grep](https://github.com/ast-grep/ast-grep)** | Rust | YAML 规则驱动的 AST 模式匹配。`find_code` / `test_match_code_rule` / `find_code_by_rule`。有 MCP Server |
| **[Probe](https://github.com/probelabs/probe)** | Rust | 零索引结构化搜索引擎——Elasticsearch 风格布尔查询 + tree-sitter AST。离线运行 |
| **[ast-bro](https://github.com/aeroxy/ast-bro)** | Rust | ast-grep 增强：`map` (结构大纲) / `deps` (依赖图) / `callers` (引用图) / `search` (BM25+向量混合搜索)。14 种语言含 Markdown |
| **[greplm](https://github.com/KhaledSMQ/greplm)** | Rust | 结构化搜索 + 调用图 + 去定义跳转 + 爆炸半径分析。为 LLM Agent 优化的 token 紧凑输出 |

### 6.2 典型查询示例

```yaml
# ast-grep 规则：搜索所有 ✅ 状态的 L3 节点
rule:
  pattern: '### $NAME ✅ [L3]'
  language: markdown

# ast-grep 规则：搜索所有引用 "1.1.1" 的段落
rule:
  pattern: '$BEFORE 1.1.1 $AFTER'
  language: markdown
```text

---

## 7. 结构化 Diff 与语义合并

传统 `git diff` 按行比较——改一个词的标题和改整个段落产生的 diff 一样大。
结构化 Diff 按 **语义单元**（标题、段落、列表项）比较。

### 7.1 核心工具

| 工具 | 核心能力 |
|------|----------|
| **[sem](https://github.com/tom-doerr/sem_cli)** | tree-sitter 实体级 diff。支持 Markdown。`sem diff`（语义 diff）/ `sem entities`（列出实体）/ `sem impact`（变更影响传播分析）/ `sem context`（为 LLM 优化的 token 预算上下文） |
| **[SemShift](https://pypi.org/project/semshift/)** | 语义漂移检测。按标题对齐文档 → 检测含义变化（如 "do not share" → "may share" → 标记 CRITICAL）。专为 Markdown 文档/策略/研究草稿设计 |
| **[aura-merge](https://crates.io/crates/aura-merge)** | 按文件类型选择合并策略——`.md` 用结构感知合并、`.json` 用 Key 级深度合并。为"多 AI Agent 并行编辑同一文件"场景设计 |

### 7.2 对本项目的意义

```text
场景：两个 Agent 同时编辑同一个 README.md
  Agent A：修改 ## 1.1 SDD → 新增 ### 1.1.4 节
  Agent B：修改 ## 1.2 指令文件 → 更新数据

传统 git merge → 行级冲突，人手动解决
aura-merge      → 感知 ## 结构，自动合并互不重叠的修改
```text

---

## 8. 文档构建与发布

### 8.1 核心 SSG

| 工具 | 语言 | 构建速度 | 适用场景 |
|------|------|----------|----------|
| **[mdBook](https://github.com/rust-lang/mdBook)** | Rust | 极快（单二进制） | 技术书籍、简洁文档、无 JS 输出 |
| **[Docusaurus](https://docusaurus.io/)** | React/Node | 中等 | 开发者文档、版本管理、MDX 交互 |
| **[MkDocs](https://www.mkdocs.org/) + Material** | Python | 快 | Python 项目、最小配置即美观 |
| **[Rspress](https://rspress.dev/)** | Rust/Rspack | 极快（1.8s/500 页） | 大型文档站 |
| **[VitePress](https://vitepress.dev/)** | Vue | 快 | Vue 生态项目 |

### 8.2 本项目的推荐

当前采用 Markdown + Markmap 可视化即可。若需要对外发布为文档站，推荐 **mdBook**（最小成本、单二进制）或 **MkDocs + Material**（最省心的美观方案）。

---

## 9. CI 集成模式

### 9.1 推荐的三层质量门禁

```yaml
# .github/workflows/docs-ci.yml
name: Docs Quality

on:
  pull_request:
    paths:
      - '**/*.md'

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      # 第一层：结构规则
      - uses: DavidAnson/markdownlint-cli2-action@v19
        with:
          globs: "**/*.md"

      # 第二层：链接有效
      - uses: lycheeverse/lychee-action@v2
        with:
          args: --no-progress './**/*.md'

      # 第三层：文风一致性
      - uses: errata-ai/vale-action@v3
        with:
          files: topics/ reports/
```text

### 9.2 可选的第四层

```yaml
      # 第四层：交叉引用完整性（如有 wiki-link）
      - run: npx @safetnsr/md-kit check
      # 或
      - run: npx markscribe find-broken-links
```text

---

## 10. AI 原生工具

### 10.1 MCP Server 一览

| 工具 | 提供的能力 |
|------|-----------|
| **[tree-sitter-analyzer (MCP)](https://github.com/aimasteracc/tree-sitter-analyzer)** | `get_code_outline` / `get_code_context` / `query_code` — 在 Claude Code 中直接查询 Markdown 结构 |
| **[ast-grep MCP](https://github.com/armelhbobdad/ast-grep-mcp)** | `dump_syntax_tree` / `find_code` / `find_code_by_rule` |
| **[syntax-tree-codebase-mcp](https://www.npmjs.com/package/syntax-tree-codebase-mcp)** | AST → 依赖图 + 语义向量搜索 |
| **[markscribe](https://www.npmjs.com/package/markscribe)** | 24 个 vault 管理工具（回链/断链/孤立文件/未链接提及） |
| **[markmap-mcp-server](https://github.com/jinzcdev/markmap-mcp-server)** | Markdown → 交互式思维导图 HTML/PNG/SVG |
| **[mcp-codebase-index](https://pypi.org/project/mcp-codebase-index/)** | 17 个 MCP 工具——`get_structure_summary` / `find_symbol` / `get_dependencies` |

### 10.2 趋势

2026 年 MCP 生态爆发——几乎所有结构化工具都提供了 MCP Server，使 AI Agent（Claude Code / Cursor / Codex）可以直接消费 Markdown 的结构化信息，而非阅读原始文本。

---

## 11. 推荐工具栈

### 针对 ai-research-lab 的分层选型

| 层级 | 推荐工具 | 理由 |
|------|----------|------|
| **AST 解析** | tree-sitter-markdown-text | 轻量，C 原生，可配合 ast-grep 做结构化搜索 |
| **LSP（IDE 导航）** | Marksman | `[[wiki-link]]` 跳转 + 跨文件引用查找 |
| **Lint** | markdownlint-cli2 | 结构一致性（标题层级、空行规范） |
| **链接检查** | lychee | 速度最快，GitHub Action 一步集成 |
| **知识图谱** | obsidian-parse | 轻量 Python 库，无重依赖，可将大纲→图 |
| **结构化搜索** | ast-grep | 搜索"所有 ⬜ 状态节点"/"所有引用 1.1.1 的位置" |
| **Diff** | sem | 查看"改了哪些标题/段落"而非"改了哪些行" |
| **装配/构建** | 自研 `assemble.py` | 按大纲节点拼装全量报告 |
| **可视化** | Markmap | Markdown → 交互式思维导图（一键命令） |

### 最小可运行工具链

```bash
# 1. 结构化搜索
cargo install ast-grep

# 2. 链接检查
cargo install lychee

# 3. LSP（VS Code 内）
code --install-extension artempyanykh.marksman

# 4. 可视化
npx markmap-cli RESEARCH-OUTLINE.md -o map.html

# 5. 健康检查
python assemble.py status
```text

---

## 附录：类比速查表

| Java/代码工具 | Markdown 对应工具 |
|--------------|------------------|
| javac → AST | tree-sitter / remark-parse → mdast |
| IntelliJ → 符号表/索引 | Marksman LSP → Heading 索引 + 引用图 |
| Find Usages | Marksman Find References / ast-grep |
| Rename Refactoring | Marksman Rename / md-kit mv |
| Checkstyle / ESLint | markdownlint / remark-lint |
| 编译依赖检查 | lychee / Linkspector (死链检查) |
| Structural Search | ast-grep / ast-bro |
| Call Graph | obsidian-parse / memex-md (知识图谱) |
| Semantic Diff | sem (tree-sitter entity diff) / SemShift |
| CI Quality Gate | markdownlint + lychee + vale |
| Javadoc 生成 | mdBook / MkDocs (文档站生成) |
| Maven/Gradle Assembly | `assemble.py full` (文档拼装) |
