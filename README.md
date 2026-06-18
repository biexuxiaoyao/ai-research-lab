---
title: "AI Research Lab — AI 驱动软件工程范式变革研究"
date: "2026-06-18"
lang: zh-CN
---

# AI Research Lab — AI 驱动软件工程范式变革研究

[![Research Status](https://img.shields.io/badge/research-18/18%20L1%20complete-brightgreen)](RESEARCH-OUTLINE.md)
[![Depth](https://img.shields.io/badge/depth-479/591%20≥%20L3-blue)](RESEARCH-OUTLINE.md)
[![Build](https://img.shields.io/badge/build-mdBook%20%2B%20EPUB%20%2B%20PDF-orange)](site/)

> **系统性地研究、跟踪与分析 AI 对软件工程全链路范式的深层变革。**

2024-2026 年，AI 编程 Agent 的快速进化动摇了传统 SDLC 的核心假设。当 Google 75% 新代码由 AI 生成、Cursor 35% 合并 PR 来自自主 Agent，整个软件工程正从"以编码为中心"重构为"以规格、验证和治理为中心"。本项目以**三层递归深度**（现状工具→深层机制→未来影响），系统覆盖需求到运维的全链路变革。

---

## 📖 阅读方式

| 格式 | 入口 | 说明 |
|------|------|------|
| **🌐 在线站点** | [`site/book/`](site/book/) | mdBook 构建，带搜索和侧边栏导航 |
| **📱 ePub** | [`reports/研究报告.epub`](reports/研究报告.epub) | Kindle/Apple Books / 通用阅读器 |
| **📄 PDF** | [`reports/研究报告-pdf-ready.md`](reports/研究报告-pdf-ready.md) → Pandoc 转换 | 含 `\newpage` 分页和 YAML 元数据 |
| **🗺️ 思维导图** | [`research-map-enhanced.html`](research-map-enhanced.html) | 交互式 Markmap，两栏布局 |
| **📝 分卷阅读** | [`reports/split/`](reports/split/) | 18 个独立章节 Markdown |

---

## 🧭 研究范围

18 个研究维度，每维度 3 层递归深挖：

| 编号 | 章节 | 核心主题 |
|:---:|------|---------|
| 01 | 需求工程 | SDD 成熟度模型、Spec-kit 门控流程、AGENTS.md 生态 |
| 02 | 原型设计 | 三圈层工具矩阵、Design Token 标准化、Figma AI 竞争重构 |
| 03 | 前端开发 | 五类用户工具、Matthew Effect 训练数据飞轮、AI 代码腐化 |
| 04 | 后端与 API | API Contract = 真相源、DDD + Agent 兼容性、架构漂移 |
| 05 | 数据库与数据层 | Text-to-SQL 生产鸿沟、Schema 不可逆性、语义层架构 |
| 06 | 测试与 QA | 测试即 Spec、环形验证、覆盖率信号贬值 |
| 07 | CI/CD 与 DevOps | PR 暴增危机、CI 成功率 70.8%、AI Code Review 四阵营 |
| 08 | 生产运维 | 闭环学习架构、自动化悖论、运维 L1-L5 自动驾驶等级 |
| 09 | 角色重塑与治理 | Vibe Coding→Agentic Engineering、Intent Engineer 新角色 |
| 10 | 安全工程 | AI 原生安全、Prompt Injection 进入 OWASP Top 10、Slopsquatting |
| 11 | 法律合规与知识产权 | Copilot 诉讼案、EU AI Act、GPL 许可证污染 |
| 12 | 横切主题 | 瓶颈全局位移、五大信号贬值与重建、异构性作为质量原则 |
| 13 | Markdown 工程化 | 文档基础设施、AST/LSP/CI/SemShift 工具链对等映射 |
| 14 | Agent Harness | 五层架构模型、MCP 协议生态、Meta-Harness 自动化治理 |
| 15 | 模型选型与评估 | 六维选型矩阵、Eval Harness 对比、Prompt Caching 策略 |
| 16 | 多 Agent 系统 | 四种拓扑对比、通信与协调、冲突检测与解决 |
| 17 | 可观测性与评估 | Trace/Log/Metrics 三支柱、成本可观测性、回归检测 |
| 18 | 提示工程与上下文工程 | 四层分层架构、上下文窗口工程、DESIGN.md 与意图工程 |

> 完整大纲见 [`RESEARCH-OUTLINE.md`](RESEARCH-OUTLINE.md)（591 个研究节点，Markmap 兼容格式）。

---

## 🔬 研究方法论

```text
每个研究方向执行三层递归深挖
  ├── 第 1 层：现状与工具生态 — 关键数据、主流产品、企业实践
  ├── 第 2 层：深层机制 — 底层原理、因果链、结构性矛盾
  └── 第 3 层：未来影响 — 趋势预测、反直觉洞察、应对策略

多源交叉验证：学术论文 × 行业报告 × 一线实践 × 产品数据
```text

---

## 🛠️ 工具链

```bash
# 装配与生成
python assemble.py status             # 健康报告（文件行数/状态）
python assemble.py topic 01           # 装配指定主题
python assemble.py full output.md     # 生成完整研究报告
python assemble.py split              # 分卷输出（18 章独立文件）
python assemble.py site               # 生成 mdBook 站点源文件
python assemble.py epub               # 生成 ePub 电子书
python assemble.py pdf-ready out.md   # 生成 Pandoc PDF 就绪文件
python assemble.py publish            # 一键生成所有格式

# 可视化
npx markmap-cli RESEARCH-OUTLINE.md -o research-map.html
```text

---

## 📁 文件架构

```text
ai-research-lab/
├── README.md                   # 项目入口
├── RESEARCH-OUTLINE.md         # 研究大纲（Agent 状态地图）
├── assemble.py                 # 动态装配工具
├── topics/                     # 各方向研究源文件（持续生长）
│   ├── 01-需求工程/README.md
│   ├── 02-原型设计/README.md
│   ├── ...
│   └── 18-提示工程与上下文工程/
│       ├── README.md           # 索引页
│       └── 181-186-*.md        # L2 子文件
├── reports/                    # 装配产物
│   ├── 00-引言.md
│   ├── split/                  # 18 章分卷
│   ├── 研究报告-pdf-ready.md
│   └── 研究报告.epub
├── references/                 # 参考文献
├── site/                       # mdBook 站点
│   ├── book.toml
│   └── src/
└── notes/                      # 研究笔记
```text

---

## 📊 研究状态

| 维度 | 数据 |
|------|------|
| L1 方向覆盖 | 18/18（100%） |
| L3 深度节点 | 479/591（81%） |
| 源文件数 | 52 |
| 总行数 | ~23,800 |
| 跨章节交叉引用 | 100+ 正文引用边 |
| 生成格式 | HTML / ePub / PDF / Markmap / 分卷 |

---

## ⚠️ 质量声明

本项目于 2026-06 完成系统性文档审计。部分数据点标注为 `⚠️ 待验证`——这些内容在独立审计中无法查证，建议读者以原始来源为准。[结论与参考文献](reports/11-结论与参考文献.md) 中提供了完整的审计说明。

AI 领域变化极快，部分数据和结论可能在报告完成后迅速过时。

---

## 📄 许可

研究内容遵循 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) 许可。工具脚本（`assemble.py`）遵循 MIT 许可。
