#!/usr/bin/env python3
"""
研究文档动态装配工具 — assemble.py

根据 RESEARCH-OUTLINE.md 的知识树结构，按需拼装文档。
零外部依赖，仅使用 Python 标准库。

用法:
  python assemble.py topic 01              # 按主题装配（需求工程）
  python assemble.py depth 2               # 按深度装配（L1-L2 概要）
  python assemble.py depth 3               # 按深度装配（L1-L3 标准分析）
  python assemble.py path 1.1.1            # 按路径装配（某个具体节点）
  python assemble.py full <output.md>      # 全量装配（单文件输出，锚点链接）
  python assemble.py pdf-ready <output.md> # PDF 就绪文件（清除 HTML 注释，YAML 元数据）
  python assemble.py split [output_dir]    # 按 L1 拆分为 18 个独立文件（~30KB/文件）
  python assemble.py site [output_dir]     # 生成 mdBook 文档站（侧边栏+搜索+主题）
  python assemble.py markmap [output.html] # 增强版 markmap（可点击节点+内容预览）
  python assemble.py pdf-help              # 打印 PDF 转换指南（中文 + 锚点）
  python assemble.py status                # 扫描文件，输出大小/行数/健康度
  python assemble.py suggest-splits        # 识别超阈值文件，建议拆分方案
  python assemble.py index                 # 生成文件路径索引
  python assemble.py backlinks             # 反向链接报告（哪些文件引用了本文件）
  python assemble.py backlinks --inject    # 自动注入 📎 被引用 区块

设计原则:
  - L1 节点 → 目录 (topics/XX-名称/)
  - L2 节点 → 独立文件 (topics/XX-名称/YY-子主题.md)
  - L3 节点 → 在 L2 文件内用 ## 章节表示
  - L4 节点 → 在 L3 章节内用 ### 表示
  - 文件 > 500 行 → 建议将内部 L3 章节拆出为独立文件
"""

import json
import os
import re
import sys
from pathlib import Path
from collections import OrderedDict

# ---- 配置 ----
ROOT = Path(__file__).parent
OUTLINE_FILE = ROOT / "RESEARCH-OUTLINE.md"
TOPICS_DIR = ROOT / "topics"
REPORTS_DIR = ROOT / "reports"
SPLIT_THRESHOLD = 500   # 文件行数阈值，超过建议拆分
WARN_THRESHOLD = 300     # 警告阈值


# ============================================================
# 第 1 部分：大纲解析
# ============================================================

def parse_outline():
    """
    解析 RESEARCH-OUTLINE.md，构建树结构。
    返回: [(depth, number, title, status, children), ...]

    其中:
      depth   = 1-4 (对应 # 个数，1 = #)
      number  = "1.1.2" 或 "" (节点编号)
      title   = "Spec-Driven Development"
      status  = "✅ L3" 或 "⬜ L1" 或 ""
    """
    if not OUTLINE_FILE.exists():
        print("[ERROR] RESEARCH-OUTLINE.md 未找到", file=sys.stderr)
        return []

    lines = OUTLINE_FILE.read_text(encoding="utf-8").split("\n")

    # 只取研究树部分（从第一个 # 开始，到统计表之前结束）
    tree_started = False
    tree_lines = []
    for line in lines:
        if line.startswith("# ") and "AI 驱动" in line and not tree_started:
            tree_started = True
        if tree_started:
            if line.startswith("# 📊") or line.startswith("# 🧭"):
                break  # 统计表和决策指南之前停止
            tree_lines.append(line)

    nodes = []
    for line in tree_lines:
        if not line.startswith("#"):
            continue

        # 解析深度
        depth = len(line) - len(line.lstrip("#"))
        if depth > 4:
            continue

        content = line.lstrip("#").strip()

        # 解析编号
        # 格式支持: "1. Title" (L1), "1.1 Title" (L2), "1.1.1 Title" (L3)
        number_match = re.match(r"(\d+(?:\.\d+)*)\.?\s+", content)
        number = number_match.group(1) if number_match else ""

        # 解析标题和状态
        if number:
            title_part = content[number_match.end():].strip()
        else:
            title_part = content
        title = title_part

        status = ""
        for st in ["✅", "🔄", "⬜", "🔒"]:
            if st in title:
                status_idx = title.index(st)
                status = title[status_idx:].strip()
                title = title[:status_idx].strip()
                break

        nodes.append({
            "depth": depth,
            "number": number,
            "title": title,
            "status": status,
        })

    return nodes


def build_tree(nodes):
    """将扁平的节点列表构建为树"""
    tree = []
    stack = []  # [(depth, node), ...]

    for node in nodes:
        # 为 node 添加 children
        node_with_children = {**node, "children": []}

        while stack and stack[-1][0] >= node["depth"]:
            stack.pop()

        if stack:
            stack[-1][1]["children"].append(node_with_children)
        else:
            tree.append(node_with_children)

        stack.append((node["depth"], node_with_children))

    return tree


# ============================================================
# 第 2 部分：文件路径映射
# ============================================================

# L1 节点编号 -> 目录名的映射
L1_DIR_MAP = {
    "1": "01-需求工程",
    "2": "02-原型设计",
    "3": "03-前端开发",
    "4": "04-后端与API",
    "5": "05-数据库与数据层",
    "6": "06-测试与QA",
    "7": "07-CICD与DevOps",
    "8": "08-生产运维",
    "9": "09-角色重塑与治理",
    "10": "10-安全工程",
    "11": "11-法律合规与知识产权",
    "12": "12-横切主题",
    "13": "13-Markdown工程化",
    "14": "14-Agent-Harness与运行时",
    "15": "15-模型选型与评估",
    "16": "16-多Agent系统与协作",
    "17": "17-可观测性与评估",
    "18": "18-提示工程与上下文工程",
}

# 特殊路径覆盖（不在 topics 下的文件）
SPECIAL_PATHS = {
    "0": REPORTS_DIR / "00-引言.md",
    "12": REPORTS_DIR / "10-交叉洞察.md",
}


def l1_number(node_number):
    """提取节点编号的 L1 部分，如 '1.2.3' -> '1'"""
    return node_number.split(".")[0] if node_number else ""


def l2_number(node_number):
    """提取节点编号的 L1.L2 部分，如 '1.2.3' -> '1.2'"""
    parts = node_number.split(".")
    return ".".join(parts[:2]) if len(parts) >= 2 else node_number


def node_to_path(node_number, title=""):
    """
    将大纲节点映射到文件路径（带 fallback）。

    规则:
      - L1 节点 (如 "1") → topics/01-需求工程/README.md
      - L2 节点 (如 "1.1") → 优先找独立文件，不存在则 fallback 到 README.md
      - L3+ 节点 → fallback 到父 L2 文件或 README.md
      - 当独立文件被创建后，自动检测并使用
    """
    if not node_number:
        return None

    parts = node_number.split(".")
    l1 = parts[0]

    # 特殊路径（不在 topics 下的文件）
    if node_number in SPECIAL_PATHS:
        return SPECIAL_PATHS[node_number]

    if l1 not in L1_DIR_MAP:
        return None

    l1_dir = TOPICS_DIR / L1_DIR_MAP[l1]
    readme = l1_dir / "README.md"

    if len(parts) == 1:
        # L1 节点 → README.md
        return readme if readme.exists() else None

    elif len(parts) == 2:
        # L2 节点 → 优先独立文件，不存在则 fallback 到 README.md
        l2_num = parts[1]
        safe_title = sanitize_filename(title)
        specific_file = l1_dir / f"{l2_num}-{safe_title}.md"
        if specific_file.exists():
            return specific_file
        return readme if readme.exists() else None

    else:
        # L3+ 节点 → 找父 L2 文件，不存在则 fallback 到 README.md
        parent_number = ".".join(parts[:2])
        parent_title = title  # 保留原始标题用于父级匹配
        parent_path = node_to_path(parent_number, parent_title)
        if parent_path and parent_path != readme:
            return parent_path
        return readme if readme.exists() else None


def sanitize_filename(title):
    """将标题转为安全的文件名片段"""
    if not title:
        return "untitled"
    # 保留中文、英文、数字、连字符，移除特殊字符
    safe = re.sub(r'[^\w一-鿿\-]', '', title.replace(' ', '-').replace('/', '-'))
    return safe[:40] if len(safe) > 40 else safe


def find_all_files():
    """扫描 topics/ 和 reports/ 下所有 .md 文件，返回 {路径: 行数}"""
    files = {}
    for d in [TOPICS_DIR, REPORTS_DIR]:
        if d.exists():
            for f in sorted(d.rglob("*.md")):
                try:
                    lines = len(f.read_text(encoding="utf-8").split("\n"))
                    files[f] = lines
                except:
                    files[f] = 0
    return files


# ============================================================
# 第 3 部分：装配模式
# ============================================================

def assemble_topic(topic_nums):
    """按主题编号装配"""
    nodes = parse_outline()
    files_to_assemble = []

    for node in nodes:
        l1 = l1_number(node["number"])
        if l1 in topic_nums:
            path = node_to_path(node["number"], node["title"])
            if path and path.exists():
                files_to_assemble.append(path)

    # 去重保持顺序
    seen = set()
    unique_files = []
    for f in files_to_assemble:
        if str(f) not in seen:
            seen.add(str(f))
            unique_files.append(f)

    return unique_files


def assemble_depth(max_depth):
    """按深度装配：收集深度 ≤ max_depth 的节点对应的文件"""
    nodes = parse_outline()
    files_to_assemble = []

    for node in nodes:
        if node["depth"] <= max_depth:
            path = node_to_path(node["number"], node["title"])
            if path and path.exists():
                files_to_assemble.append(path)

    # 去重保持顺序
    seen = set()
    unique_files = []
    for f in files_to_assemble:
        if str(f) not in seen:
            seen.add(str(f))
            unique_files.append(f)

    return unique_files


def assemble_path(node_path):
    """按路径装配：匹配 node_path 及其所有子节点"""
    nodes = parse_outline()
    files_to_assemble = []
    matching = False

    for node in nodes:
        number = node["number"]
        if number == node_path or number.startswith(node_path + "."):
            matching = True
            path = node_to_path(number, node["title"])
            if path and path.exists():
                files_to_assemble.append(path)

    if not matching:
        print(f"[WARN] 路径 '{node_path}' 未匹配任何节点", file=sys.stderr)

    seen = set()
    unique_files = []
    for f in files_to_assemble:
        if str(f) not in seen:
            seen.add(str(f))
            unique_files.append(f)

    return unique_files


def assemble_full():
    """全量装配：引言 + 18 大主题（含 L2 子文件） + 交叉洞察 + 结论"""
    files_to_assemble = []

    # 1. 引言
    intro = REPORTS_DIR / "00-引言.md"
    if intro.exists():
        files_to_assemble.append(intro)

    # 2. 大纲中的所有主题节点 — L1 目录中如有 L2 独立文件则包含
    nodes = parse_outline()
    for node in nodes:
        path = node_to_path(node["number"], node["title"])
        if not path or not path.exists():
            continue

        # 检查该 L1 目录是否有 L2 独立文件（拆分后的章节）
        l1_dir = path.parent if path.is_file() else path
        l2_files = sorted(
            [f for f in l1_dir.glob("*.md") if f.name != "README.md" and not f.name.endswith(".bak")],
            key=lambda f: f.name
        )
        if l2_files:
            # 有 L2 文件：先加索引 README，再加各 L2 文件
            if path.exists():
                files_to_assemble.append(path)
            for l2f in l2_files:
                if l2f.exists():
                    files_to_assemble.append(l2f)
        else:
            # 无 L2 文件：直接加 README
            files_to_assemble.append(path)

    # 3. 交叉洞察（如果大纲中未包含）
    cross = REPORTS_DIR / "10-交叉洞察.md"
    if cross.exists() and cross not in files_to_assemble:
        files_to_assemble.append(cross)

    # 4. 结论
    conclusion = REPORTS_DIR / "11-结论与参考文献.md"
    if conclusion.exists() and conclusion not in files_to_assemble:
        files_to_assemble.append(conclusion)

    # 去重保持顺序
    seen = set()
    unique_files = []
    for f in files_to_assemble:
        if str(f) not in seen:
            seen.add(str(f))
            unique_files.append(f)

    return unique_files


def heading_anchor(title):
    """将标题转为 GitHub/Pandoc 兼容的锚点 ID。

    Pandoc 和大多数 Markdown 渲染器的规则：
    - 转小写
    - 移除标点（保留中文/英文/数字/空格/连字符）
    - 空格替换为连字符
    - 连续连字符合并为一个
    """
    # 保留 Unicode 字母、数字、空格、连字符
    result = []
    for ch in title.lower():
        if ch.isalnum() or ch in (' ', '-', '_'):
            result.append(ch)
        elif '一' <= ch <= '鿿' or '぀' <= ch <= 'ヿ':
            # CJK 字符直接保留
            result.append(ch)
        # 其他字符（标点等）跳过
    anchor = ''.join(result).strip()
    # 空格 → 连字符，合并重复连字符
    anchor = re.sub(r'\s+', '-', anchor)
    anchor = re.sub(r'-{2,}', '-', anchor)
    return anchor


def collect_headings(file_list):
    """扫描所有文件，提取标题树用于生成内链目录。

    返回: [(level, title, anchor), ...]
      level  = 1-4（对应 # 个数，在拼装后的文档中统一加 2 级偏移）
      title  = 标题文本
      anchor = 生成的锚点 ID
    """
    headings = []
    for f in file_list:
        content = f.read_text(encoding="utf-8")
        for line in content.split("\n"):
            line = line.strip()
            if line.startswith("# ") or line.startswith("## ") or line.startswith("### "):
                depth = len(line) - len(line.lstrip("#"))
                title = line.lstrip("#").strip()
                # 去除状态标记（✅ L3 等）
                title = re.sub(r'\s*[✅🔄⬜🔒]\s*.*$', '', title).strip()
                anchor = heading_anchor(title)
                headings.append((depth, title, anchor))
    return headings


def assemble_files(file_list, output_file=None):
    """拼接文件内容并输出"""
    total_lines = 0

    if output_file:
        out = open(output_file, "w", encoding="utf-8")
        is_single_file = True
    else:
        out = sys.stdout
        is_single_file = False

    # 文档头部元信息
    out.write("# 完整研究报告\n\n")
    if is_single_file:
        out.write("> ⚠️ 本文件由 `assemble.py full` 自动拼装生成。")
        out.write("部分数据已经过内容审计，标注为待验证的数据点请勿直接引用。\n\n")

    # 生成目录（单文件模式使用锚点链接，多文件模式使用文件路径）
    toc = generate_toc(file_list, use_anchors=is_single_file)
    out.write(toc)
    out.write("\n---\n\n")

    for idx, f in enumerate(file_list):
        rel = f.relative_to(ROOT)
        content = f.read_text(encoding="utf-8")
        lines = len(content.split("\n"))
        total_lines += lines

        if is_single_file:
            # 单文件模式：加入文件分隔标记，但不使用 HTML 注释
            # Pandoc 会保留 HTML 注释但在某些模式下可能导致问题
            fname = rel.stem if rel.stem != "README" else rel.parent.name
            out.write(f"\n\n<!-- ════════════════════════════════════════ -->\n")
            out.write(f"<!-- 来源: {rel} -->\n")
            out.write(f"<!-- ════════════════════════════════════════ -->\n\n")

            # 修复文件内部的相对链接为锚点链接
            fixed_content = fix_internal_links(content, file_list)
            out.write(fixed_content)
        else:
            out.write(f"<!-- source: {rel} -->\n")
            out.write(content)

        out.write("\n\n")

    if output_file:
        out.close()
        # 输出统计
        size_kb = Path(output_file).stat().st_size / 1024
        print(f"✅ 完整报告已生成: {output_file}")
        print(f"   文件数: {len(file_list)}  |  总行数: {total_lines}  |  大小: {size_kb:.0f} KB")

    return total_lines


def fix_internal_links(content, file_list):
    """修复内容中的内部链接。

    将指向同仓库其他 .md 文件的链接转为锚点链接（在单文件拼装模式下）。
    例如: [text](../topics/01-需求工程/README.md) → [text](#章节标题)

    当前策略：保留原链接但添加标记，因为完整解析所有交叉引用
    需要 AST 级别的处理。简单替换可能导致错误。
    """
    # 对于单文件拼装，相对链接本身在 Markdown 阅读器中仍然可点击
    # 但 PDF 渲染会断开。最安全的做法是保持原样并在文档头添加说明。
    return content


def generate_toc(file_list, use_anchors=False):
    """生成目录

    Args:
        file_list: 文件列表
        use_anchors: True = 使用标题锚点链接（单文件模式）
                     False = 使用文件路径链接（多文件/标准模式）
    """
    toc = "# 目录\n\n"

    if use_anchors:
        # 单文件模式：提取所有文件的标题，生成锚点链接目录
        current_l1 = None
        for f in file_list:
            content = f.read_text(encoding="utf-8")
            for line in content.split("\n"):
                line_stripped = line.strip()
                if line_stripped.startswith("## ") and not line_stripped.startswith("### "):
                    title = line_stripped.lstrip("#").strip()
                    # 去除状态标记
                    clean_title = re.sub(r'\s*[✅🔄⬜🔒]\s*.*$', '', title).strip()
                    anchor = heading_anchor(clean_title)
                    toc += f"- [{clean_title}](#{anchor})\n"
                elif line_stripped.startswith("### "):
                    title = line_stripped.lstrip("#").strip()
                    clean_title = re.sub(r'\s*[✅🔄⬜🔒]\s*.*$', '', title).strip()
                    anchor = heading_anchor(clean_title)
                    toc += f"  - [{clean_title}](#{anchor})\n"
    else:
        # 多文件模式：链接到文件路径
        for f in file_list:
            rel = f.relative_to(ROOT)
            try:
                content = f.read_text(encoding="utf-8")
                title = None
                for line in content.split("\n"):
                    if line.startswith("# "):
                        title = line.lstrip("#").strip()
                        break
                    elif line.startswith("## ") and not title:
                        title = line.lstrip("#").strip()
                if not title:
                    title = rel.stem
            except:
                title = rel.stem
            toc += f"- [{title}]({rel})\n"

    return toc


# ============================================================
# 第 4 部分：状态报告
# ============================================================

def show_status():
    """扫描所有文件，输出健康状态"""
    files = find_all_files()
    total_lines = sum(files.values())
    total_files = len(files)

    healthy, warn, critical = 0, 0, 0

    print("=" * 60)
    print("  研究文档健康报告")
    print("=" * 60)
    print(f"  总文件数: {total_files}")
    print(f"  总行数:   {total_lines}")
    print(f"  拆分阈值: {SPLIT_THRESHOLD} 行")
    print(f"  警告阈值: {WARN_THRESHOLD} 行")
    print("-" * 60)

    for f, lines in sorted(files.items(), key=lambda x: -x[1]):
        rel = f.relative_to(ROOT)

        if lines > SPLIT_THRESHOLD:
            status_icon = "⚠️  拆分"
            critical += 1
        elif lines > WARN_THRESHOLD:
            status_icon = "⚡ 关注"
            warn += 1
        else:
            status_icon = "✅ 健康"
            healthy += 1

        bar = "█" * min(lines // 20, 25)
        print(f"  {status_icon}  {str(rel):<50} {lines:>4} 行  {bar}")

    print("-" * 60)
    print(f"  健康: {healthy}  |  关注: {warn}  |  需拆分: {critical}")

    if critical > 0:
        print(f"\n  💡 运行 'python assemble.py suggest-splits' 查看拆分建议")

    print("=" * 60)


def suggest_splits():
    """识别超阈值文件并建议拆分方案"""
    files = find_all_files()
    oversized = [(f, n) for f, n in files.items() if n > SPLIT_THRESHOLD]

    if not oversized:
        print("✅ 所有文件都在健康范围内，无需拆分。")
        return

    print("建议拆分以下文件:\n")
    for f, lines in sorted(oversized, key=lambda x: -x[1]):
        rel = f.relative_to(ROOT)
        print(f"  {rel} ({lines} 行, 超出阈值 {lines - SPLIT_THRESHOLD} 行)")

        # 分析文件中的 ## 章节（L3 节点）
        try:
            content = f.read_text(encoding="utf-8")
            sections = re.findall(r'^##\s+(.+)$', content, re.MULTILINE)
            if sections:
                print(f"    → 可拆分为 {len(sections)} 个独立文件:")
                for s in sections:
                    safe = sanitize_filename(s)
                    print(f"      {f.parent.name}/{safe}.md")
            else:
                print(f"    → 无明显的 ## 章节，建议人工审查")
        except:
            pass
        print()


# ============================================================
# 第 5 部分：索引生成
# ============================================================

def generate_index():
    """生成文件路径索引"""
    nodes = parse_outline()
    tree = build_tree(nodes)

    print("# 文件路径索引\n")
    print("| 大纲编号 | 标题 | 文件路径 | 状态 |")
    print("|----------|------|----------|------|")

    def print_node(node, level=0):
        number = node["number"]
        title = node["title"]
        status = node.get("status", "")
        path = node_to_path(number, title)
        rel_path = path.relative_to(ROOT) if path and path.exists() else "(待创建)"

        indent = "  " * level
        print(f"| {indent}{number} | {indent}{title} | {rel_path} | {status} |")

        for child in node.get("children", []):
            print_node(child, level + 1)

    for root_node in tree:
        print_node(root_node)


def assemble_pdf_ready(output_file):
    """
    生成 Pandoc PDF 转换优化的单文件 Markdown。

    与 full 模式的区别：
    - YAML 元数据头（Pandoc 原生支持）
    - 清除 HTML 注释（避免 LaTeX 渲染异常）
    - 分页标记
    - 编码声明
    """
    files = assemble_full()
    total_lines = 0

    with open(output_file, "w", encoding="utf-8") as out:
        # YAML 元数据块（Pandoc 自动识别）
        out.write("---\n")
        out.write("title: 'AI 驱动软件工程范式变革 — 完整研究报告'\n")
        out.write("date: '2026-06-17'\n")
        out.write("lang: zh-CN\n")
        out.write("toc: true\n")
        out.write("toc-depth: 3\n")
        out.write("numbersections: false\n")
        out.write("---\n\n")

        for f in files:
            content = f.read_text(encoding="utf-8")
            lines = len(content.split("\n"))
            total_lines += lines

            # 去除 HTML 注释（在 LaTeX/PDF 渲染中无意义且可能引入乱码）
            content = re.sub(r'<!--.*?-->', '', content, flags=re.DOTALL)

            out.write(content.strip())
            out.write("\n\n\\newpage\n\n")

    size_kb = Path(output_file).stat().st_size / 1024
    print(f"PDF-ready: {output_file} ({len(files)} files, {total_lines} lines, {size_kb:.0f} KB)")
    print()
    print("PDF 转换命令 (需要安装 Pandoc + TeX 发行版):")
    print(f"  pandoc {output_file} --pdf-engine=xelatex -o output.pdf")
    print()
    print("  Windows 字体建议 (需先安装 Noto CJK 或使用系统字体):")
    print("    -V CJKmainfont='SimSun'")
    print("  macOS:")
    print("    -V CJKmainfont='PingFang SC'")

    return total_lines


def assemble_split(output_dir=None):
    """
    按 L1 主题拆分为多个独立的单文件，每个文件约 25-40KB。
    适合 Markdown 阅读器/渲染器无法处理超大单文件（>500KB）的场景。
    """
    if output_dir is None:
        output_dir = ROOT / "reports" / "split"
    else:
        output_dir = Path(output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)

    nodes = parse_outline()
    l1_set = set()
    for node in nodes:
        l1 = l1_number(node["number"])
        if l1 and l1 not in l1_set:
            l1_set.add(l1)

    total_lines = 0
    files_generated = []

    for l1 in sorted(l1_set, key=int):
        topic_files = assemble_topic([l1])
        if not topic_files:
            continue

        l1_dir_name = L1_DIR_MAP.get(l1, f"topic-{l1}")
        output_file = output_dir / f"{l1}-{l1_dir_name}.md"

        with open(output_file, "w", encoding="utf-8") as out:
            for f in topic_files:
                content = f.read_text(encoding="utf-8")
                lines = len(content.split("\n"))
                total_lines += lines

                # 去除 HTML 注释
                content = re.sub(r'<!--.*?-->', '', content, flags=re.DOTALL)

                out.write(content.strip())
                out.write("\n\n")

        size_kb = output_file.stat().st_size / 1024
        files_generated.append((output_file, size_kb))

    print(f"分卷生成完成: {len(files_generated)} 个文件 → {output_dir}")
    for f, size in files_generated:
        print(f"  {f.name:<45} {size:>5.0f} KB")

    return total_lines


def assemble_site(output_dir=None):
    """
    生成 mdBook 静态文档站点。

    产出:
    - book.toml (CJK 优化配置)
    - src/SUMMARY.md (从 RESEARCH-OUTLINE.md 自动生成的导航)
    - src/ (所有研究文件的副本，链接自动修复)

    构建:
      cd site && mdbook build
      输出在 site/book/ 目录，可直接部署到 GitHub Pages。
    """
    if output_dir is None:
        output_dir = ROOT / "site"
    else:
        output_dir = Path(output_dir)

    src_dir = output_dir / "src"
    src_dir.mkdir(parents=True, exist_ok=True)

    # 1. 生成 book.toml
    book_toml = output_dir / "book.toml"
    book_toml.write_text("""[book]
title = "AI 驱动软件工程范式变革"
authors = ["AI Research Lab"]
language = "zh-CN"
multilingual = false
src = "src"

[build]
build-dir = "book"
create-missing = false

[output.html]
site-url = "/ai-research-lab/"
git-repository-url = "https://github.com/user/ai-research-lab"
edit-url-template = "https://github.com/user/ai-research-lab/edit/main/{path}"
default-theme = "light"
preferred-dark-theme = "navy"
copy-fonts = true
mathjax-support = false
additional-css = []
additional-js = []
no-section-label = true

[output.html.search]
limit-results = 30
use-boolean-and = true

[preprocessor]
""", encoding="utf-8")

    # 2. 生成 SUMMARY.md（从大纲树生成嵌套导航）
    summary = generate_summary_md()
    (src_dir / "SUMMARY.md").write_text(summary, encoding="utf-8")

    # 3. 复制所有内容文件
    files_copied = 0
    total_lines = 0

    # 引言和结论放在 src/ 根
    for report_name in ["00-引言.md", "10-交叉洞察.md", "11-结论与参考文献.md"]:
        src = REPORTS_DIR / report_name
        if src.exists():
            content = src.read_text(encoding="utf-8")
            total_lines += len(content.split("\n"))
            dst = src_dir / report_name
            dst.write_text(content, encoding="utf-8")
            files_copied += 1

    # 各 topic 目录
    for topic_dir in sorted(TOPICS_DIR.iterdir()):
        if not topic_dir.is_dir():
            continue
        dst_dir = src_dir / topic_dir.name
        dst_dir.mkdir(exist_ok=True)
        for md_file in topic_dir.glob("*.md"):
            content = md_file.read_text(encoding="utf-8")
            total_lines += len(content.split("\n"))
            # 修复指向 reports/ 的相对链接
            content = content.replace("../reports/", "./")
            (dst_dir / md_file.name).write_text(content, encoding="utf-8")
            files_copied += 1

    # 4. 生成首页 README.md
    readme = src_dir / "README.md"
    if not readme.exists():
        readme.write_text("""# AI 驱动软件工程范式变革

> 完整研究报告 | 2026 年 6 月

本网站是 "AI Research Lab" 项目的完整文档站点，
涵盖从需求工程到生产运维的全链路 AI 化研究。

## 快速导航

- **左侧边栏**：按主题浏览全部 18 个研究方向
- **顶部搜索栏**：全文搜索（快捷键 `s`）
- **主题切换**：支持浅色/深色模式
- **每章 TL;DR**：30 秒了解核心发现

## 研究范围

| 维度 | 覆盖 |
|------|------|
| L1 主题 | 18 个研究方向 |
| L2 子主题 | 118 个 |
| L3 细节节点 | 479+ 个 |
| 总文件数 | 51 个 |

## 按读者画像选择阅读路径

| 你是... | 推荐起点 | 预计时间 |
|---------|---------|:---:|
| 🧑‍💻 工程经理 / Tech Lead | [01 需求工程](01-需求工程/README.md) | ~45 min |
| 🔬 研究者 / 架构师 | [12 横切主题](12-横切主题/README.md) | ~90 min |
| 🛡️ 安全 / 合规 | [10 安全工程](10-安全工程/README.md) | ~60 min |
| ⚡ 快速概览 | [引言](00-引言.md) → 各章 TL;DR → 结论 | ~20 min |

## 使用方式

- **在线阅读**：使用左侧边栏导航
- **搜索**：按 `s` 键打开搜索
- **打印**：每个页面均可直接打印（浏览器 `Ctrl+P`）
- **PDF**：运行 `python assemble.py pdf-ready` 生成 PDF 版本
""", encoding="utf-8")

    print(f"✅ mdBook 站点已生成: {output_dir}")
    print(f"   文件: {files_copied}  |  总行数: {total_lines}")
    print()
    print("🔨 构建静态站点：")
    print(f"   cd {output_dir}")
    print("   mdbook build")
    print()
    print("📖 本地预览：")
    print("   mdbook serve --open")
    print()
    print("🚀 部署到 GitHub Pages：")
    print("   # 将 site/book/ 目录推送到 gh-pages 分支即可")


def generate_summary_md():
    """从 RESEARCH-OUTLINE.md 生成 mdBook SUMMARY.md。

    格式:
      # Summary
      [引言](README.md)
      - [需求工程 AI 化](01-需求工程/README.md)
        - [SDD 成熟度模型](01-需求工程/README.md#spec-driven-development)
    """
    nodes = parse_outline()
    tree = build_tree(nodes)

    lines = ["# Summary\n"]
    lines.append("[引言](00-引言.md)\n")

    def write_node(node, indent=0):
        prefix = "  " * indent + "- "
        number = node["number"]
        title = node["title"]
        children = node.get("children", [])

        path = None
        if number:
            parts = number.split(".")
            l1 = parts[0]
            if l1 in L1_DIR_MAP:
                l1_dir = L1_DIR_MAP[l1]
                if len(parts) == 1:
                    # L1: 链接到 README.md
                    path = f"{l1_dir}/README.md"
                elif len(parts) >= 2:
                    # L2+: 链接到 L2 文件或 fallback README
                    node_path = node_to_path(number, title)
                    if node_path and node_path.exists():
                        rel = node_path.relative_to(ROOT)
                        path = str(rel).replace("\\", "/")
                        # 在站点 src/ 目录中，文件没有 topics/ 前缀
                        # topics/XX-名称/README.md → XX-名称/README.md
                        if path.startswith("topics/"):
                            path = path[len("topics/"):]
                    else:
                        path = f"{l1_dir}/README.md"

        if path:
            # mdBook 需要正斜杠路径
            path = path.replace("\\", "/")
            # SUMMARY.md 只做文件级导航，不加锚点
            # （大纲标题与文件内实际标题经常不一致，锚点链接会 404）
            lines.append(f"{prefix}[{title}]({path})\n")
        else:
            lines.append(f"{prefix}{title}\n")

        for child in children:
            write_node(child, indent + 1)

    for root_node in tree:
        # 跳过根节点（整体标题），直接写其子节点（18 个 L1 主题）
        # mdBook 要求：有子项的父节点必须是链接，根标题无链接会导致构建失败
        if root_node["number"]:
            write_node(root_node)
        else:
            for child in root_node.get("children", []):
                write_node(child)

    # 交叉洞察和结论
    lines.append("\n[交叉洞察](10-交叉洞察.md)\n")
    lines.append("[结论与参考文献](11-结论与参考文献.md)\n")

    return "".join(lines)


def generate_enhanced_markmap(output_file=None):
    """
    生成带可点击节点的增强版 markmap HTML。

    与标准 npx markmap-cli 的区别:
    - 每个节点链接到对应的内容文件
    - 两栏布局：左侧思维导图 + 右侧内容预览区
    - 支持键盘导航
    """
    if output_file is None:
        output_file = ROOT / "research-map-enhanced.html"

    # 读取原始大纲
    outline_text = OUTLINE_FILE.read_text(encoding="utf-8")

    # 构建节点→路径的映射
    nodes = parse_outline()
    node_map = {}
    for node in nodes:
        number = node["number"]
        title = node["title"]
        if number:
            path = node_to_path(number, title)
            if path and path.exists():
                rel = str(path.relative_to(ROOT)).replace("\\", "/")
                node_map[title] = rel

    # 生成增强版 HTML
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>AI 研究知识地图 — 交互式思维导图</title>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Microsoft YaHei', sans-serif; }}
#container {{ display: flex; height: 100vh; }}
#mindmap {{ flex: 1; min-width: 0; overflow: auto; }}
#panel {{ width: 420px; border-left: 1px solid #e0e0e0; padding: 24px; overflow-y: auto; background: #fafafa; display: flex; flex-direction: column; }}
#panel h3 {{ font-size: 16px; color: #333; margin-bottom: 8px; }}
#panel .path {{ font-size: 12px; color: #999; margin-bottom: 16px; font-family: monospace; }}
#panel .preview {{ flex: 1; overflow-y: auto; font-size: 13px; line-height: 1.7; color: #444; border-top: 1px solid #eee; padding-top: 16px; }}
#panel .actions {{ margin-top: 16px; }}
#panel a {{ display: inline-block; padding: 6px 14px; background: #e8e8ff; color: #445; border-radius: 4px; text-decoration: none; font-size: 13px; }}
#panel a:hover {{ background: #d0d0ff; }}
#panel .empty {{ color: #bbb; font-size: 14px; text-align: center; margin-top: 80px; }}
.tip {{ position: fixed; bottom: 12px; left: 12px; font-size: 11px; color: #aaa; background: white; padding: 4px 10px; border-radius: 10px; border: 1px solid #eee; }}
</style>
</head>
<body>
<div id="container">
  <svg id="mindmap"></svg>
  <div id="panel">
    <h3 id="node-title">点击左侧节点查看详情</h3>
    <div class="path" id="node-path"></div>
    <div class="preview" id="node-preview">
      <p class="empty">← 点击思维导图中的任意节点<br>右侧将显示对应章节概览</p>
    </div>
    <div class="actions">
      <a id="node-link" href="#" style="display:none">📖 查看完整章节</a>
    </div>
  </div>
</div>
<div class="tip">🖱 滚轮缩放 | 拖拽平移 | 点击节点查看详情 | <span id="node-count"></span></div>

<script src="https://cdn.jsdelivr.net/npm/markmap-autoloader@0.17"></script>
<script src="https://cdn.jsdelivr.net/npm/markmap-view@0.17"></script>
<script src="https://cdn.jsdelivr.net/npm/markmap-lib@0.17/dist/browser/index.min.js"></script>
<script>
(async () => {{
  const {{ Transformer }} = window.markmap;
  const {{ Markmap }} = window.markmap;

  const markdown = {json.dumps(outline_text)};

  const transformer = new Transformer();
  const {{ root }} = transformer.transform(markdown);

  // 节点→路径映射
  const nodeMap = {json.dumps(node_map)};

  // 将文件路径注入到节点 data 中
  function injectPaths(node) {{
    const t = (node.content || '').trim();
    // 匹配标题并添加路径
    for (const [title, path] of Object.entries(nodeMap)) {{
      if (t.includes(title) || title.includes(t)) {{
        node.payload = {{ path }};
        break;
      }}
    }}
    if (node.children) node.children.forEach(injectPaths);
  }}
  injectPaths(root);

  const mm = Markmap.create('#mindmap', {{
    autoFit: true,
    colorFreezeLevel: 3,
    duration: 300,
    maxInitialScale: 1.2,
  }}, root);

  document.getElementById('node-count').textContent =
    `${{Object.keys(nodeMap).length}} 个研究节点`;

  // 点击节点事件
  document.querySelector('#mindmap').addEventListener('click', (e) => {{
    const g = e.target.closest('g.markmap-node');
    if (!g) return;
    const text = (g.getAttribute('data-content') || '').trim();
    const panelTitle = document.getElementById('node-title');
    const panelPath = document.getElementById('node-path');
    const panelPreview = document.getElementById('node-preview');
    const panelLink = document.getElementById('node-link');

    panelTitle.textContent = text || '未命名节点';

    // 查找对应文件路径
    let foundPath = null;
    for (const [title, path] of Object.entries(nodeMap)) {{
      if (text.includes(title) || title.includes(text)) {{
        foundPath = path;
        break;
      }}
    }}

    if (foundPath) {{
      panelPath.textContent = '📁 ' + foundPath;
      panelLink.href = foundPath;
      panelLink.style.display = 'inline-block';

      // 尝试加载文件内容预览（前 500 字）
      fetch(foundPath)
        .then(r => r.text())
        .then(content => {{
          const lines = content.split('\\n');
          // 跳过来源行，取前 30 行有意义的内容
          const filtered = lines
            .filter(l => !l.startsWith('>') && !l.startsWith('<!--') && l.trim())
            .slice(0, 30)
            .join('\\n');
          panelPreview.innerHTML = '<pre style="white-space:pre-wrap;font-size:12px;line-height:1.6">'
            + filtered.slice(0, 1500)
            + (filtered.length > 1500 ? '...' : '')
            + '</pre>';
        }})
        .catch(() => {{
          panelPreview.innerHTML = '<p class="empty">预览不可用<br>点击下方按钮查看完整章节</p>';
        }});
    }} else {{
      panelPath.textContent = '';
      panelLink.style.display = 'none';
      panelPreview.innerHTML = '<p class="empty">（此节点为分组节点，展开可查看子主题）</p>';
    }}
  }});
}})();
</script>
</body>
</html>"""

    output_file = Path(output_file)
    output_file.write_text(html, encoding="utf-8")
    size_kb = output_file.stat().st_size / 1024
    print(f"✅ 增强版 markmap 已生成: {output_file} ({size_kb:.0f} KB)")
    print(f"   节点数: {len(node_map)}  |  布局: 左侧思维导图 + 右侧内容预览")


def show_pdf_help():
    """打印 PDF 转换详细帮助"""
    print("=" * 60)
    print("  Markdown → PDF 转换指南（中文支持）")
    print("=" * 60)
    print()
    print("1. 安装依赖:")
    print("   - Pandoc:  https://pandoc.org/installing.html")
    print("   - TeX:     https://miktex.org/ (Windows) 或 MacTeX (macOS)")
    print()
    print("2. 生成 PDF 就绪文件:")
    print("   python assemble.py pdf-ready 研究报告.md")
    print()
    print("3. 转换为 PDF:")

    cmd = (
        "pandoc 研究报告.md \\\n"
        "  --pdf-engine=xelatex \\\n"
        "  -o 研究报告.pdf \\\n"
        "  --toc --toc-depth=3 \\\n"
        "  -V CJKmainfont='SimSun' \\\n"
        "  -V mainfont='Microsoft YaHei' \\\n"
        "  -V monofont='Consolas' \\\n"
        "  -V geometry:margin=2.5cm \\\n"
        "  --metadata title='AI 驱动软件工程范式变革'"
    )
    print(f"   {cmd}")
    print()
    print("4. 排查乱码:")
    print("   - 确认系统安装了中文字体（SimSun / Microsoft YaHei）")
    print("   - 必须使用 --pdf-engine=xelatex（不要用 pdflatex）")
    print("   - 检查 fc-list | grep -i cjk 确认 CJK 字体可用")
    print()
    print("5. 排查锚点失效:")
    print("   - Pandoc 自动将 ## 标题转为 PDF 书签")
    print("   - 锚点 ID 规则: 中文标题保留汉字，标点移除，空格转连字符")
    print("   - 已执行 `python assemble.py pdf-help` 查看锚点生成逻辑")
    print()


# ============================================================
# 第 6 部分：反向链接生成
# ============================================================

def generate_backlinks(inject=False):
    """
    扫描所有 Markdown 文件中的内部链接，生成反向链接索引。

    对于每个被引用的文件，列出所有引用它的文件。
    当 --inject 时，自动将反向链接注入到文件末尾的"被引用"区域。

    用法:
      python assemble.py backlinks           # 打印反向链接报告
      python assemble.py backlinks --inject  # 注入反向链接到文件
    """
    all_files = find_all_files()

    # 构建文件路径 → 相对路径的映射
    path_to_rel = {}
    for f in all_files:
        rel = str(f.relative_to(ROOT)).replace("\\", "/")
        path_to_rel[str(f)] = rel

    # 扫描所有文件中的内部链接
    # 返回: {target_rel_path: [(source_rel_path, link_text), ...]}
    backlinks = {}

    # 匹配 Markdown 链接: [text](path.md) 或 [text](path.md#anchor)
    link_pattern = re.compile(r'\[([^\]]*)\]\(([^)]+\.md)(?:#[^)]*)?\)')

    for f in all_files:
        source_rel = path_to_rel[str(f)]
        try:
            content = f.read_text(encoding="utf-8")
        except:
            continue

        for match in link_pattern.finditer(content):
            link_text = match.group(1)
            link_target = match.group(2)

            # 解析相对路径为目标文件的绝对路径
            target_abs = (f.parent / link_target).resolve()
            target_str = str(target_abs)

            if target_str in path_to_rel:
                target_rel = path_to_rel[target_str]
                if target_rel not in backlinks:
                    backlinks[target_rel] = []
                backlinks[target_rel].append((source_rel, link_text))

    if not inject:
        # 打印反向链接报告
        print("=" * 60)
        print("  反向链接报告（哪些文件引用了本文件）")
        print("=" * 60)

        # 按引用数量排序
        sorted_targets = sorted(backlinks.items(), key=lambda x: -len(x[1]))

        for target, sources in sorted_targets:
            print(f"\n📄 {target}")
            print(f"   被 {len(sources)} 个文件引用:")
            for src, text in sources:
                print(f"   ← {src}  ({text})")

        print(f"\n{'=' * 60}")
        print(f"  总计: {len(backlinks)} 个文件有入链")
        print(f"  文件总数: {len(all_files)}")
        print(f"  孤立文件（无入链）: {len(all_files) - len(backlinks)}")
        print("=" * 60)

        if len(all_files) > len(backlinks):
            print("\n📌 无入链的文件（可能缺少交叉引用）:")
            for f in sorted(all_files):
                rel = path_to_rel[str(f)]
                if rel not in backlinks:
                    print(f"   - {rel}")

    else:
        # 注入模式：向每个文件添加或更新"被引用"区块
        updated = 0
        for f in all_files:
            rel = path_to_rel[str(f)]
            if rel not in backlinks:
                continue

            try:
                content = f.read_text(encoding="utf-8")
            except:
                continue

            sources = backlinks[rel]
            # 去重（同一源文件的多个链接合并）
            seen_sources = set()
            unique_sources = []
            for src, text in sources:
                if src not in seen_sources:
                    seen_sources.add(src)
                    unique_sources.append((src, text))

            # 构建反向链接区块
            backlink_section = "\n\n---\n\n## 📎 被以下章节引用\n\n"
            for src, text in unique_sources:
                # 计算从当前文件到源文件的相对路径
                try:
                    src_path = ROOT / src
                    link = os.path.relpath(src_path, f.parent).replace("\\", "/")
                except:
                    link = src
                backlink_section += f"- [{text}]({link})\n"

            # 检查是否已有反向链接区块
            existing_pattern = r'\n\n---\n\n## 📎 被以下章节引用\n\n.*'
            if re.search(existing_pattern, content, re.DOTALL):
                # 替换已有区块
                content = re.sub(existing_pattern, backlink_section, content, flags=re.DOTALL)
            else:
                # 追加
                content = content.rstrip() + backlink_section

            f.write_text(content, encoding="utf-8")
            updated += 1

        print(f"✅ 反向链接已注入 {updated} 个文件")
        print(f"   (每个文件末尾增加了 '📎 被以下章节引用' 区块)")

    return backlinks


# ============================================================
# CLI 入口
# ============================================================

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return

    mode = sys.argv[1]

    if mode == "topic":
        topics = sys.argv[2:]
        files = assemble_topic(topics)
        if files:
            assemble_files(files)

    elif mode == "depth":
        max_depth = int(sys.argv[2]) if len(sys.argv) > 2 else 3
        files = assemble_depth(max_depth)
        if files:
            assemble_files(files)

    elif mode == "path":
        node_path = sys.argv[2]
        files = assemble_path(node_path)
        if files:
            assemble_files(files)

    elif mode == "full":
        output = sys.argv[2] if len(sys.argv) > 2 else None
        files = assemble_full()
        lines = assemble_files(files, output)
        if output:
            print(f"✅ 完整报告已生成: {output} ({lines} 行)")
        else:
            print(f"\n[总计 {len(files)} 个文件, {lines} 行]", file=sys.stderr)

    elif mode == "status":
        show_status()

    elif mode == "suggest-splits":
        suggest_splits()

    elif mode == "index":
        generate_index()

    elif mode == "pdf-ready":
        output = sys.argv[2] if len(sys.argv) > 2 else "reports/研究报告-pdf-ready.md"
        assemble_pdf_ready(output)

    elif mode == "split":
        output_dir = sys.argv[2] if len(sys.argv) > 2 else None
        assemble_split(output_dir)

    elif mode == "site":
        output_dir = sys.argv[2] if len(sys.argv) > 2 else None
        assemble_site(output_dir)

    elif mode == "markmap":
        output_file = sys.argv[2] if len(sys.argv) > 2 else None
        generate_enhanced_markmap(output_file)

    elif mode == "pdf-help":
        show_pdf_help()

    elif mode == "backlinks":
        inject = "--inject" in sys.argv
        generate_backlinks(inject=inject)

    else:
        print(f"未知模式: {mode}", file=sys.stderr)
        print(__doc__)


if __name__ == "__main__":
    main()
