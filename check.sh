#!/usr/bin/env bash
# ============================================================
# Markdown 质量管线 — 三层质量门禁
#
# 用法:
#   ./check.sh           # 运行全部检查
#   ./check.sh lint      # 仅结构检查
#   ./check.sh links     # 仅链接检查
#   ./check.sh assemble  # 仅装配验证
#   ./check.sh fix       # 自动修复可修复的问题
# ============================================================
set -euo pipefail
cd "$(dirname "$0")"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

PASS=0
FAIL=0

pass() { echo -e "${GREEN}✅ PASS${NC} $1"; PASS=$((PASS + 1)); }
fail() { echo -e "${RED}❌ FAIL${NC} $1"; FAIL=$((FAIL + 1)); }

summary() {
    echo ""
    echo "========================================"
    TOTAL=$((PASS + FAIL))
    if [ $FAIL -eq 0 ]; then
        echo -e "${GREEN}  All $TOTAL checks passed${NC}"
        echo "========================================"
        exit 0
    else
        echo -e "${RED}  $FAIL/$TOTAL checks failed${NC}"
        echo "========================================"
        exit 1
    fi
}

# ============================================================
# 第一层：结构 Lint
# ============================================================
run_lint() {
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  第 1 层：结构 Lint (markdownlint)"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    if npx markdownlint-cli2 "topics/**/*.md" "reports/**/*.md" "*.md" 2>&1; then
        pass "markdownlint — 结构规范"
    else
        fail "markdownlint — 结构问题（运行 './check.sh fix' 自动修复）"
    fi
}

# ============================================================
# 第二层：链接检查
# ============================================================
run_links() {
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  第 2 层：链接检查 (check_links.py)"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    if python3 check_links.py --strict 2>&1; then
        pass "check_links  — 内部链接有效"
    else
        fail "check_links  — 存在断链"
    fi
}

# ============================================================
# 第三层：装配验证
# ============================================================
run_assemble() {
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  第 3 层：装配验证 (assemble.py)"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    # 全量装配到临时文件
    TMPFILE=$(mktemp /tmp/assemble-check-XXXXXX.md)
    if python3 assemble.py full "$TMPFILE" 2>&1; then
        LINES=$(wc -l < "$TMPFILE")
        rm "$TMPFILE"
        pass "assemble   — 全量装配成功 ($LINES 行)"
    else
        rm -f "$TMPFILE"
        fail "assemble   — 装配失败"
    fi
}

# ============================================================
# 自动修复
# ============================================================
run_fix() {
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  自动修复 (markdownlint --fix)"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    npx markdownlint-cli2 --fix "topics/**/*.md" "reports/**/*.md" "*.md" 2>&1 || true
    echo "Done. Run './check.sh' to verify."
}

# ============================================================
# 主入口
# ============================================================
case "${1:-all}" in
    lint)
        run_lint
        ;;
    links)
        run_links
        ;;
    assemble)
        run_assemble
        ;;
    fix)
        run_fix
        ;;
    all|*)
        run_lint
        run_links
        run_assemble
        summary
        ;;
esac
