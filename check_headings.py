#!/usr/bin/env python3
"""Heading structure auditor — checks heading hierarchy across all .md files."""

import re
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).parent


def extract_headings(filepath):
    """Extract all headings from a file.
    Returns [(line_number, level, title, raw_line), ...]
    Skips lines inside fenced code blocks (```).
    """
    headings = []
    try:
        content = filepath.read_text(encoding='utf-8')
    except Exception:
        return headings

    in_code_block = False
    for i, line in enumerate(content.split('\n'), 1):
        stripped = line.strip()
        # Track fenced code blocks
        if stripped.startswith('```'):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            continue

        if stripped.startswith('#'):
            # Count # at start
            level = len(stripped) - len(stripped.lstrip('#'))
            if level > 6:
                continue
            title = stripped.lstrip('#').strip()
            # Skip empty headings like just "##"
            if not title:
                continue
            headings.append((i, level, title, stripped))
    return headings


def audit_file(filepath, headings):
    """Check heading issues in a single file.
    Returns list of (severity, message) tuples.
    """
    issues = []
    fname = filepath.name

    if not headings:
        issues.append(('WARN', f'{fname}: 无任何标题'))
        return issues

    levels = [h[1] for h in headings]

    # Rule 1: First heading should be H1 or H2 (not H3+)
    if levels[0] >= 3:
        issues.append(('ERROR', f'{fname}: 首标题是 H{levels[0]}，应为 H1 或 H2'))

    # Rule 2: No more than one H1
    h1_count = sum(1 for l in levels if l == 1)
    if h1_count > 1:
        h1_lines = [h[0] for h in headings if h[1] == 1]
        issues.append(('ERROR', f'{fname}: {h1_count} 个 H1（行 {h1_lines}），应只有 0 或 1 个'))

    # Rule 3: No level skipping (e.g., H2 → H4)
    for i in range(1, len(headings)):
        prev_level = headings[i-1][1]
        curr_level = headings[i][1]
        if curr_level > prev_level + 1:
            issues.append(('ERROR',
                f'{fname}:{headings[i][0]} 标题层级跳跃 H{prev_level}→H{curr_level} '
                f'("{headings[i-1][2][:40]}" → "{headings[i][2][:40]}")'))

    # Rule 4: H2 should not appear before H1 (if H1 exists)
    if h1_count == 1:
        h1_line = next(h[0] for h in headings if h[1] == 1)
        for h in headings:
            if h[1] == 2 and h[0] < h1_line:
                issues.append(('ERROR',
                    f'{fname}:{h[0]} H2 出现在 H1（行 {h1_line}）之前'))

    return issues


def check_heading_consistency(all_files_headings):
    """Check cross-file heading pattern consistency."""
    issues = []

    # Check if topic README files use consistent heading style
    topic_h1_styles = []
    for fpath, headings in all_files_headings.items():
        if 'topics/' in str(fpath) and fpath.name == 'README.md':
            if headings:
                h1 = headings[0]
                if h1[1] == 1:
                    topic_h1_styles.append((str(fpath), h1[2]))

    # Check: topic READMEs should all use H1 or all use H2
    h1_files = [f for f, t in topic_h1_styles]
    # Actually, just report what we find

    return issues


def main():
    all_files = sorted(ROOT.rglob('*.md'))
    # Filter out generated files
    skip_dirs = ['site/src', 'site/book', 'node_modules', '.git']
    files_to_check = []
    for f in all_files:
        fstr = str(f)
        if any(d in fstr for d in skip_dirs):
            continue
        files_to_check.append(f)

    print(f"{'='*70}")
    print(f"  文档标题层级审计")
    print(f"  检查文件: {len(files_to_check)}")
    print(f"{'='*70}\n")

    all_headings_data = {}
    total_issues = 0
    errors = 0
    warns = 0

    # Group files by directory for organized output
    by_dir = defaultdict(list)
    for f in files_to_check:
        rel = str(f.relative_to(ROOT)).replace('\\', '/')
        parts = rel.split('/')
        if len(parts) == 1:
            d = '.'
        else:
            d = parts[0]
        by_dir[d].append(f)

    for directory in sorted(by_dir.keys()):
        files = sorted(by_dir[directory])
        dir_issues = 0
        print(f"--- {directory}/ ({len(files)} files) ---")

        for f in files:
            headings = extract_headings(f)
            all_headings_data[f] = headings
            issues = audit_file(f, headings)

            if not issues:
                # Print heading structure summary
                if headings:
                    levels_str = '→'.join(str(h[1]) for h in headings[:8])
                    if len(headings) > 8:
                        levels_str += f'...({len(headings)} total)'
                    # Show first heading
                    first = headings[0]
                    print(f"  ✅ {f.name:<40} {levels_str:<25} {first[2][:50]}")
                else:
                    print(f"  ⚠️  {f.name:<40} [无标题]")
            else:
                for severity, msg in issues:
                    if severity == 'ERROR':
                        prefix = '❌'
                        errors += 1
                    else:
                        prefix = '⚠️ '
                        warns += 1
                    print(f"  {prefix} {msg}")
                    dir_issues += 1
                    total_issues += 1

        if dir_issues == 0 and len(files) > 1:
            pass  # all clean
        print()

    # Heading level distribution
    all_levels = defaultdict(int)
    for headings in all_headings_data.values():
        for h in headings:
            all_levels[h[1]] += 1

    print(f"{'='*70}")
    print(f"  统计")
    print(f"{'='*70}")
    print(f"  文件总数: {len(files_to_check)}")
    print(f"  标题总数: {sum(all_levels.values())}")
    print(f"  H1: {all_levels[1]:>5}  |  H2: {all_levels[2]:>5}  |  H3: {all_levels[3]:>5}  |  H4+: {all_levels[4]+all_levels[5]:>5}")
    print(f"  ❌ 错误: {errors}  |  ⚠️ 警告: {warns}")

    if total_issues == 0:
        print(f"\n  🎉 所有文件标题层级规范！")
    else:
        print(f"\n  共 {total_issues} 个问题需要修复")

    # Cross-file consistency check
    print(f"\n{'='*70}")
    print(f"  跨文件一致性")
    print(f"{'='*70}")

    # Report topic READMEs heading style
    topic_h1 = []
    topic_h2 = []
    for fpath, headings in all_headings_data.items():
        rel = str(fpath.relative_to(ROOT)).replace('\\', '/')
        if 'topics/' in rel and fpath.name == 'README.md':
            if headings:
                if headings[0][1] == 1:
                    topic_h1.append((rel, headings[0][2]))
                elif headings[0][1] == 2:
                    topic_h2.append((rel, headings[0][2]))

    if topic_h1:
        print(f"\n  使用 H1 开头的 topic README ({len(topic_h1)}):")
        for path, title in topic_h1:
            print(f"    {path}  →  # {title}")
    if topic_h2:
        print(f"\n  使用 H2 开头的 topic README ({len(topic_h2)}):")
        for path, title in topic_h2:
            print(f"    {path}  →  ## {title}")

    if topic_h1 and topic_h2:
        print(f"\n  ⚠️  不一致：部分 README 使用 H1，部分使用 H2")
        print(f"     建议统一为一种风格")


if __name__ == '__main__':
    main()
