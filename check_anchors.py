#!/usr/bin/env python3
"""Anchor link checker — scans all .md files for broken #anchor links."""

import re
from pathlib import Path

ROOT = Path(__file__).parent


def heading_anchor(title):
    """Generate anchor ID from heading (same algorithm as assemble.py)."""
    result = []
    for ch in title.lower():
        if ch.isalnum() or ch in (' ', '-', '_'):
            result.append(ch)
        elif '一' <= ch <= '鿿' or '぀' <= ch <= 'ヿ':
            result.append(ch)
    anchor = ''.join(result).strip()
    anchor = re.sub(r'\s+', '-', anchor)
    anchor = re.sub(r'-{2,}', '-', anchor)
    return anchor


def extract_heading_title(line):
    """Extract clean title from a heading line."""
    title = line.lstrip('#').strip()
    # Strip status markers
    for st in ['✅', '\U0001f504', '⬜', '\U0001f512']:
        if st in title:
            title = title[:title.index(st)].strip()
    # Strip leading number like '1.1.1 '
    title = re.sub(r'^\d+(?:\.\d+)*\s*', '', title)
    return title


def build_heading_index():
    """Scan all .md files, return {rel_path: {anchor: heading_text}}."""
    target_headings = {}
    all_files = list(ROOT.rglob('*.md'))

    for f in all_files:
        fstr = str(f)
        if 'site/src' in fstr or 'site/book' in fstr or 'node_modules' in fstr:
            continue
        try:
            content = f.read_text(encoding='utf-8')
        except Exception:
            continue
        headings = {}
        for line in content.split('\n'):
            line_stripped = line.strip()
            if re.match(r'^#{1,4}\s', line_stripped):
                title = extract_heading_title(line_stripped)
                anchor = heading_anchor(title)
                headings[anchor] = title
        if headings:
            rel = str(f.relative_to(ROOT)).replace('\\', '/')
            target_headings[rel] = headings

    return target_headings


def find_anchor_links():
    """Find all [text](path.md#anchor) links and check validity."""
    target_headings = build_heading_index()
    link_pattern = re.compile(r'\[([^\]]*)\]\(([^)]+\.md)#([^)]+)\)')

    broken = []
    all_files = list(ROOT.rglob('*.md'))

    for f in all_files:
        fstr = str(f)
        # Skip generated files
        if 'site/src' in fstr or 'site/book' in fstr or 'node_modules' in fstr:
            continue
        if '研究报告-pdf-ready.md' in fstr:
            continue  # assembled report: internal links can't resolve in flat output
        source_rel = str(f.relative_to(ROOT)).replace('\\', '/')
        try:
            content = f.read_text(encoding='utf-8')
        except Exception:
            continue

        for m in link_pattern.finditer(content):
            # Skip if link is inside backtick-wrapped inline code (documentation examples)
            line_start = content.rfind('\n', 0, m.start()) + 1
            line = content[line_start:content.find('\n', m.end())]
            if '`' in line[:m.start() - line_start] and '`' in line[m.end() - line_start:]:
                continue  # inline code example, not a real link

            text = m.group(1)
            target = m.group(2)
            anchor = m.group(3)

            # Resolve relative path
            target_abs = (f.parent / target).resolve()
            try:
                target_rel = str(target_abs.relative_to(ROOT)).replace('\\', '/')
            except ValueError:
                broken.append({
                    'source': source_rel,
                    'target': target,
                    'anchor': anchor,
                    'text': text,
                    'error': 'TARGET_OUTSIDE_ROOT',
                    'available': [],
                })
                continue

            if target_rel not in target_headings:
                broken.append({
                    'source': source_rel,
                    'target': target_rel,
                    'anchor': anchor,
                    'text': text,
                    'error': 'FILE_NOT_FOUND',
                    'available': [],
                })
                continue

            if anchor not in target_headings[target_rel]:
                broken.append({
                    'source': source_rel,
                    'target': target_rel,
                    'anchor': anchor,
                    'text': text,
                    'error': 'ANCHOR_NOT_FOUND',
                    'available': list(target_headings[target_rel].keys())[:8],
                })

    return broken, target_headings


def main():
    broken, headings = find_anchor_links()

    print(f"Files with headings: {len(headings)}")
    print(f"Broken anchor links:  {len(broken)}")
    print()

    if not broken:
        print("All anchor links are valid!")
        return

    # Group by error type
    file_not_found = [b for b in broken if b['error'] == 'FILE_NOT_FOUND']
    anchor_broken = [b for b in broken if b['error'] == 'ANCHOR_NOT_FOUND']
    outside = [b for b in broken if b['error'] == 'TARGET_OUTSIDE_ROOT']

    if file_not_found:
        print(f"{'='*60}")
        print(f"  FILE NOT FOUND ({len(file_not_found)} issues)")
        print(f"{'='*60}")
        for b in file_not_found:
            print(f"\n  Source: {b['source']}")
            print(f"  Link:   [{b['text']}]({b['target']}#{b['anchor']})")
            print(f"  Error:  Target file does not exist")

    if anchor_broken:
        print(f"\n{'='*60}")
        print(f"  ANCHOR MISMATCH ({len(anchor_broken)} issues)")
        print(f"{'='*60}")
        for b in anchor_broken:
            print(f"\n  Source: {b['source']}")
            print(f"  Link:   [{b['text']}]({b['target']}#{b['anchor']})")
            print(f"  Error:  Anchor '#{b['anchor']}' not found")
            print(f"  Available anchors (first 8):")
            for a in b['available']:
                print(f"    - #{a}")

    if outside:
        print(f"\n{'='*60}")
        print(f"  OUTSIDE ROOT ({len(outside)} issues)")
        print(f"{'='*60}")


if __name__ == '__main__':
    main()
