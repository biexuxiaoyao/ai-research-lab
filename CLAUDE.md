---
title: "项目定位"
date: "2026-06-18"
lang: zh-CN
---

# AI Research Lab — AI 驱动软件工程范式变革研究

> 本项目专注于 **AI 对软件工程全链路范式变革** 的深度研究、跟踪与分析。

## 项目定位

对 AI 驱动开发范式变革进行**系统性、分层递进**的研究。每项研究遵循三层递归方法论：

- **第 1 层**：现状与工具生态 — 关键数据、主流产品、企业实践
- **第 2 层**：深层机制 — 底层原理、因果链、结构性矛盾
- **第 3 层**：未来影响 — 趋势预测、反直觉洞察、应对策略

## 文件架构（分层存储 + 动态装配）

```text
ai-research-lab/
├── CLAUDE.md                    # 本文件
├── RESEARCH-OUTLINE.md          # 研究大纲（Agent 状态地图，Markmap 兼容）
├── assemble.py                  # 动态装配工具（零依赖 Python 脚本）
├── reports/                     # 总纲零部件（跨主题内容）
│   ├── 00-引言.md
│   ├── 10-交叉洞察.md
│   └── 11-结论与参考文献.md
├── topics/                      # 各方向研究文档（持续生长）
│   ├── 01-需求工程/
│   │   └── README.md            # 当前内容在此，超 1000 行自动建议拆 L2 子文件
│   ├── 02-原型设计/
│   │   └── README.md
│   ├── 03-前端开发/
│   │   └── README.md
│   ├── 04-后端与 API/
│   │   └── README.md
│   ├── 05-数据库与数据层/
│   │   └── README.md
│   ├── 06-测试与 QA/
│   │   └── README.md
│   ├── 07-CICD 与 DevOps/
│   │   └── README.md
│   ├── 08-生产运维/
│   │   └── README.md
│   ├── 09-角色重塑与治理/
│   │   └── README.md
│   ├── 10-安全工程/
│   ├── 11-法律合规与知识产权/
│   └── 13-Markdown 工程化/
│       └── README.md
├── reports/                     # 总纲零部件（跨主题内容 + 附录）
│   ├── 00-引言.md
│   ├── 10-交叉洞察.md
│   ├── 11-结论与参考文献.md       # 增强版（80+ 条分类文献，标注验证状态）
│   ├── 12-术语表.md              # 🆕 核心概念定义与索引
│   ├── 13-研究方法.md            # 🆕 研究设计、三层递归法、方法学局限
│   ├── 14-实践检查清单.md         # 🆕 SDD/测试/CI/CD/安全/可观测性检查清单
│   ├── 15-章节要点速览.md         # 🆕 18 章执行摘要与核心发现
│   └── 研究报告-pdf-ready.md     # 装配后的完整报告（8,056 行）
├── references/                  # 参考文献、论文、数据来源
│   └── markdown-engineering-tools.md  # Markdown 工程化工具全景
└── notes/                       # 研究笔记、临时观察、待验证假设 + 外部评估
```text

**分层规则**：L1=目录，L2=超 1000 行时拆出独立文件，L3=文件内 `##` 章节，L4=文件内 `###` 子章节。

## assemble.py 用法

```bash
python assemble.py status              # 健康报告（所有文件行数/状态）
python assemble.py suggest-splits      # 识别超阈值文件，建议拆分方案
python assemble.py topic 01            # 装配指定主题
python assemble.py depth 3             # 按深度装配（L3 标准分析）
python assemble.py path 1.1.1          # 装配具体节点
python assemble.py full <output.md>    # 生成完整研究报告
```text

## 研究方法论

1. **多源交叉验证**：学术论文 + 行业报告 + 一线实践 + 产品数据
2. **三层递归深挖**：每一层均需覆盖现状、机制、影响
3. **反直觉洞察优先**：寻找常识之外的发现
4. **可操作输出**：每个研究方向最终产出应包含可操作的策略建议

## 研究知识地图

- **研究大纲**：[`RESEARCH-OUTLINE.md`](./RESEARCH-OUTLINE.md) — 广度 × 深度的树形知识地图，含 571 个研究节点和状态追踪
- **状态图例**：✅ 已完成 [L3] / 🔄 浅覆盖 [L2] / ⬜ 待研究 / 🔒 暂不可研究
- **Agent 决策**：主 Agent 每次启动时读取大纲文件，基于覆盖状态自主决策下探方向和深度
- **可视化**：大纲为 Markmap 兼容格式，运行 `npx markmap-cli RESEARCH-OUTLINE.md -o research-map.html` 生成交互式思维导图
- **装配**：需要输出完整报告时，运行 `python assemble.py full reports/完整研究报告.md`
- **工具链参考**：[`references/markdown-engineering-tools.md`](./references/markdown-engineering-tools.md) — Markdown 工程化工具全景（AST/LSP/Lint/链接检查/知识图谱/结构化搜索/语义 Diff/SSG/MCP）

## 自动扩展机制

- 每次深度研究完成后，Agent 更新 topic 文件
- 运行 `python assemble.py status` 检查文件健康度
- 当 README.md 超 1000 行 → 自动建议拆分为 L2 独立文件
- 大纲 L2 节点 → 独立文件存在时自动检测，不存在时 fallback 到 README.md

## 工作约定

- 细小修改直接编辑 topic 文件
- 新增 L2 深度内容时，若文件已超 1000 行则拆分
- 重大发现更新回总纲（通过 `assemble.py full` 重新生成）
- 引用来源统一记录在 `references/` 目录
- 研究报告使用中文撰写，Markdown 格式

## 当前研究状态

| 方向 | 文件数 | 状态 |
|------|--------|------|
| 01-需求工程 | 1 | L3 覆盖，+经济效益+工具选型 L2 |
| 02-原型设计 | 1 | L3 覆盖，+经济效益+工具选型+Design-to-Code 准确率+竞争动态 |
| 03-前端开发 | 1 | L3 覆盖，+经济效益 L2 |
| 04-后端与 API | 1 | L3 覆盖，+经济效益+安全风险 L2 |
| 05-数据库 | 1 | L3 覆盖，+安全风险 L2 |
| 06-测试与 QA | 1 | L3 覆盖，+经济效益 L2 |
| 07-CICD | 1 | L3 覆盖，+安全风险 L2 |
| 08-生产运维 | 1 | L3 覆盖，+安全风险 L2 |
| 09-治理安全 | 1 | L3 覆盖，+Intent Engineer 角色+Harness 治理反模式 |
| 10-安全工程 | 1 | ✅ L3 覆盖（76 行，5 L2 × 15 L3） |
| 11-法律合规 | 1 | ✅ L3 覆盖（287 行，4 L2 × 12 L3） |
| 12-横切主题 | 1 | ✅ L3 覆盖（375 行，7 L2 × 17 L3，+Meta-Governance 阶段 5+AGENTS.md 生态全景） |
| 13-Markdown 工程化 | 1 | ✅ L3 覆盖（9 L2，含 wiki-link 取舍 + SemShift + DOA + 工具栈参考架构） |
| 14-Agent-Harness | 10 | ✅ L3 覆盖（已拆分 9 L2 子文件 + 索引，含指令文件加载机制 + Meta-Harness 自动化治理） |
| 15-模型选型 | 6 | ✅ L3 覆盖（已拆分 5 L2 子文件 + 索引，+DeepSeek 适配层分析+模型路由案例） |
| 16-多 Agent 系统 | 6 | ✅ L3 覆盖（已拆分 5 L2 子文件 + 索引，16 L3 全完成） |
| 17-可观测性 | 6 | ✅ L3 覆盖（已拆分 5 L2 子文件 + 索引，15 L3 全完成） |
| 18-提示工程 | 7 | ✅ L3 覆盖（已拆分 6 L2 子文件 + 索引，含 DESIGN.md 与意图工程） |

### 报告附录（2026-06-18 体系化完成）

| 编号 | 附录 | 文件 | 内容 |
|------|------|------|------|
| A | 缩略语表 | `reports/附录 A-缩略语表.md` | 🆕 74 条英文缩写全称与中文译名 |
| B | 图表索引 | `reports/附录 B-图表索引.md` | 🆕 37 张 Mermaid 图表索引 + 类型分布 |
| C | 待验证数据清单 | `reports/附录 C-待验证数据清单.md` | 🆕 28 个待验证数据点 + 验证优先级 |
| D | 参考文献交叉索引 | `reports/附录 D-参考文献章节交叉索引.md` | 🆕 99 条文献 × 18 章双向追溯矩阵 |
| E | 术语表 | `reports/12-术语表.md` | 55 条核心概念定义（A-Z 全覆盖，30→55） |
| F | 研究方法 | `reports/13-研究方法.md` | 研究设计、三层递归法、数据收集、方法学局限 |
| G | 实践检查清单 | `reports/14-实践检查清单.md` | SDD/测试/CI/CD/安全/可观测性 + 综合转型路线图 |
| H | 章节要点速览 | `reports/15-章节要点速览.md` | 18 章执行摘要、关键数据与主要结论 |
| I | 多元视角补充 | `reports/16-多元视角补充.md` | 法律伦理/教育人才/行业差异/国际比较 |
| — | 附录总目录 | `reports/附录-总目录.md` | 🆕 全部附录导航入口 |
| — | 完整参考文献 | `reports/11-结论与参考文献.md` | 99 条分类文献（行业报告/学术论文/产品/法规），标注验证状态 |

### 外部评估材料（2026-06-18 存入 notes/）

| 文件 | 内容 |
|------|------|
| `notes/外部评估-AI 驱动软件工程范式变革研究报告.md` | 七维度综合评审 |
| `notes/外部评估-具体改进建议.md` | 28 条可操作改进建议 |
| `notes/外部评估-推荐引用工具指南.md` | 文献管理→校验→检测→写作工具链 |
| `notes/外部评估-自动化引用校验工具使用指南.md` | 四种校验工具操作手册 |
| `notes/外部评估-出版纸质书标准准备指南.md` | 选题→三审三校→印刷→发行全流程 |

详见 [`RESEARCH-OUTLINE.md`](./RESEARCH-OUTLINE.md)。

## 环境

- **操作系统**: Windows 11 Home China
- **Shell**: Bash (Git Bash)
- **研究工具**: Claude Code Workflow（多 Agent 并行研究）
- **可视化工具**: Markmap（Markdown → 思维导图）
- **工作目录**: `C:\Users\25220\Projects\ai-research-lab`
