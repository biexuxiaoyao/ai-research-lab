#!/usr/bin/env python3
"""
内部链接验证器 — 检查 Markdown 文件中的本地链接和锚点有效性。
零依赖，仅需 Python 3 标准库。

用法:
  python check_links.py              # 检查所有文件
  python check_links.py --strict     # 遇错即退出非零
  python check_links.py --json       # JSON 格式输出
"""

import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent
MD_FILES = list(ROOT.glob("**/*.md"))
EXIT_CODE = 0


def extract_links(filepath):
    """从 Markdown 文件中提取所有本地链接（跳过代码块和内联代码）"""
    text = filepath.read_text(encoding="utf-8")
    links = []

    # 移除代码块区域（```...```)
    cleaned = re.sub(r'```[^`]*```', '', text, flags=re.DOTALL)
    # 移除内联代码 (`...`)
    cleaned = re.sub(r'`[^`]+`', '', cleaned)

    # [text](path.md) 或 [text](path.md#anchor)
    for m in re.finditer(r'\[([^\]]*)\]\(([^)]+)\)', cleaned):
        target = m.group(2)
        # 跳过外部 URL
        if target.startswith(("http://", "https://", "mailto:", "#")):
            if target.startswith("#"):
                links.append(("anchor", target[1:], m.group(1), m.start()))
            continue
        # 跳过纯锚点
        if not target or target.startswith("?"):
            continue
        links.append(("file", target, m.group(1), m.start()))

    # [[wiki-link]] 或 [[path|alias]]（跳过代码块中的）
    for m in re.finditer(r'\[\[([^\]|]+)(?:\|[^\]]+)?\]\]', cleaned):
        target = m.group(1).strip()
        if target.startswith(("http://", "https://")):
            continue
        links.append(("wiki", target, m.group(0), m.start()))

    return links


def get_headings(filepath):
    """提取文件中所有标题的 anchor"""
    text = filepath.read_text(encoding="utf-8")
    headings = set()
    for m in re.finditer(r'^#{1,6}\s+(.+)$', text, re.MULTILINE):
        title = m.group(1).strip()
        # 生成 GitHub 风格的 anchor
        anchor = title.lower()
        anchor = re.sub(r'[^\w\s一-鿿-]', '', anchor)
        anchor = re.sub(r'\s+', '-', anchor)
        headings.add(anchor)
    return headings


def resolve_link(filepath, link_type, target):
    """解析链接目标是否存在"""
    basedir = filepath.parent

    if link_type == "wiki":
        # [[01-需求工程]] → topics/01-需求工程/README.md
        candidates = [
            ROOT / f"{target}.md",
            ROOT / f"topics/{target}/README.md",
            ROOT / f"topics/{target}.md",
        ]
        # Also try fuzzy match in topics/
        for d in (ROOT / "topics").iterdir() if (ROOT / "topics").exists() else []:
            if d.is_dir() and target in d.name:
                candidates.append(d / "README.md")
        for c in candidates:
            if c.exists():
                return True, str(c.relative_to(ROOT))
        return False, None

    elif link_type == "file":
        # [text](./path/to/file.md) or [text](../file.md)
        parts = target.split("#", 1)
        file_part = parts[0]
        anchor_part = parts[1] if len(parts) > 1 else None

        target_path = (basedir / file_part).resolve()
        try:
            target_path.relative_to(ROOT.resolve())
        except ValueError:
            return None, None  # 不在项目内的链接跳过

        if not target_path.exists():
            return False, None

        if anchor_part:
            headings = get_headings(target_path)
            if anchor_part not in headings:
                return False, f"anchor '#{anchor_part}' not found"
        return True, str(target_path.relative_to(ROOT))

    elif link_type == "anchor":
        headings = get_headings(filepath)
        if target not in headings:
            return False, f"anchor '#{target}' not found in same file"
        return True, None

    return None, None


def main():
    global EXIT_CODE
    strict = "--strict" in sys.argv
    json_out = "--json" in sys.argv

    total_links = 0
    broken = []

    for md_file in sorted(MD_FILES):
        rel = md_file.relative_to(ROOT)
        links = extract_links(md_file)

        for link_type, target, label, pos in links:
            total_links += 1
            status, detail = resolve_link(md_file, link_type, target)

            if status is False:
                # 获取行号
                text = md_file.read_text(encoding="utf-8")
                line_num = text[:pos].count("\n") + 1
                entry = {
                    "file": str(rel),
                    "line": line_num,
                    "type": link_type,
                    "target": target,
                    "label": label,
                    "detail": detail,
                }
                broken.append(entry)

    if json_out:
        print(json.dumps({"total": total_links, "broken": len(broken), "links": broken},
                         ensure_ascii=False, indent=2))
    else:
        if broken:
            print(f"\n❌ {len(broken)} broken links found:\n")
            for b in broken:
                loc = f"{b['file']}:{b['line']}"
                detail = f" — {b['detail']}" if b.get('detail') else ""
                print(f"  {loc}")
                print(f"    [{b['type']}] {b['target']}{detail}")
                print(f"    text: \"{b['label'][:60]}\"")
                print()
            EXIT_CODE = 1
        else:
            print(f"✅ All {total_links} internal links valid")

    if strict:
        sys.exit(EXIT_CODE)


if __name__ == "__main__":
    main()
