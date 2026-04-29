#!/usr/bin/env bash
# monthly_maintenance.sh — 平台每月維護主腳本(串起 12 個工具,Wave 91 升級)
#
# 用法:
#   bash scripts/monthly_maintenance.sh                    # 全跑
#   bash scripts/monthly_maintenance.sh --skip-fetch       # 不抓政府站,只重建本地
#   bash scripts/monthly_maintenance.sh --skip-monitor     # 跳過監測
#
# 排程:
#   crontab -e
#   0 9 1 * * cd /path/to/平台 && bash scripts/monthly_maintenance.sh > .last_maintenance.log 2>&1
#
#   或 Claude Code:
#   /schedule monthly /scripts/monthly_maintenance.sh

set -uo pipefail
cd "$(dirname "$0")/.."

# QA #4 修法 + QA 第五輪 #3 修正:統一 venv Python 環境
# (原 `[ -f python3 ]` 檢查 cwd 永遠為 false — 是 replace_all 過度替換 .venv/bin/python3 → python3 的副作用)
# 改用絕對路徑檢查 .venv/bin/python3 是否存在且可執行
if [ -x "$PWD/.venv/bin/python3" ]; then
  export PATH="$PWD/.venv/bin:$PATH"
fi

SKIP_FETCH=0
SKIP_MONITOR=0
for arg in "$@"; do
  case $arg in
    --skip-fetch) SKIP_FETCH=1;;
    --skip-monitor) SKIP_MONITOR=1;;
  esac
done

START_TS=$(date +%s)
LOG_DIR=".maintenance_logs"
mkdir -p "$LOG_DIR"
LOG="$LOG_DIR/$(date +%Y%m%d_%H%M%S).log"

step() {
  echo ""
  echo "▶ [$(date +%H:%M:%S)] $1"
  echo "─────────────────────────────"
}

run() {
  local label="$1"; shift
  if "$@" >> "$LOG" 2>&1; then
    echo "  ✓ $label"
  else
    echo "  ✗ $label(見 $LOG)"
  fi
}

echo "=========================================="
echo " 兒少人權監督平台 — 每月維護"
echo " 開始時間:$(date +'%Y-%m-%d %H:%M:%S')"
echo " 紀錄檔:  $LOG"
echo "=========================================="

# 1. 監測政府站(SSL+cookie+stable hash)
if [ "$SKIP_MONITOR" -eq 0 ]; then
  step "1/7 監測政府站(NHRC、CRC、衛福部、國教盟政策站)"
  run "monitor_updates" python3 scripts/monitor_updates.py
fi

# 2. 抓 NAAES 政策站新文章
if [ "$SKIP_FETCH" -eq 0 ]; then
  step "2/7 抓 NAAES 政策知識庫新文章"
  run "fetch_aabe_policy" python3 scripts/fetch_aabe_policy.py --skip-existing
fi

# 3. md → sqlite 全平台同步(必須先重建,aabe_to_advocacy 才不會被清)
step "3/7 全平台 Markdown → SQLite(rebuild)"
run "md_to_sqlite --rebuild" python3 scripts/md_to_sqlite.py --rebuild

# 4. NAAES → SQLite advocacy_action(在 rebuild 之後追加)
step "4/12 NAAES 27+ 篇 → SQLite advocacy_action(追加)"
run "aabe_to_advocacy" python3 scripts/aabe_to_advocacy.py

# 4.5 Wave 62-91 schema 遷移(rebuild 會沖掉 vocab/dashboard/nap/nhrc/translation,本步補回)
step "4.5/12 schema 遷移(vocab + dashboard + nap + nhrc + translation)"
run "migrate_schemas" python3 scripts/migrate_schemas.py

# 5. 影子報告 5 audience(Wave 91 從 3 擴大到 5)
step "5/12 影子報告 compile.py(5 audience)"
for aud in professional media kid legislative social; do
  run "compile.py --audience $aud" python3 shadow_report/compile.py --audience "$aud"
done

# 6. build 5 版本 HTML
step "6/12 build_shadow_report 5 版本 HTML"
for aud in professional media kid legislative social; do
  run "build $aud" python3 scripts/build_shadow_report.py --audience "$aud"
done

# 7. 86 source 檔三層分類索引(Wave 67)
step "7/12 source 檔三層分類索引"
run "classify_sources" python3 scripts/classify_sources.py --update

# 8. passage 全文索引重建(Wave 68)
step "8/12 passage 全文入庫(SQLite FTS5)"
run "populate_passages" python3 scripts/populate_passages.py

# 9. 戰情室儀表板重建(Wave 63 + 79)
step "9/12 戰情室儀表板重建"
run "render_dashboard" python3 scripts/render_dashboard.py --update _public/index.html

# 10. NAP 追蹤頁重建(Wave 79 + 86)
step "10/12 NAP 追蹤頁重建"
run "render_nap" python3 scripts/render_nap.py --update

# 11. 全平台搜尋索引(Wave 71 + 90)
step "11/12 全平台搜尋索引"
run "build_search_index" python3 scripts/build_search_index.py

# 12. WCAG + self_qa + 翻譯稽核(Wave 69 + 88)
step "12/12 WCAG + self_qa + 翻譯稽核"
run "wcag_audit" python3 scripts/wcag_audit.py
run "self_qa" bash scripts/self_qa.sh
run "translation_audit" python3 scripts/translation_audit.py --lang en

# === 結算 ===
END_TS=$(date +%s)
DURATION=$((END_TS - START_TS))

echo ""
echo "=========================================="
echo " 維護完成 — 用時 ${DURATION}s"
echo "=========================================="
echo ""
echo "📊 SQLite 統計:"
sqlite3 data/crw.db "SELECT 'crc_article: ' || COUNT(*) FROM crc_article
UNION ALL SELECT 'concluding_observation: ' || COUNT(*) FROM concluding_observation
UNION ALL SELECT 'policy_issue: ' || COUNT(*) FROM policy_issue
UNION ALL SELECT 'domestic_law: ' || COUNT(*) FROM domestic_law
UNION ALL SELECT 'advocacy_action: ' || COUNT(*) FROM advocacy_action
UNION ALL SELECT 'case_story: ' || COUNT(*) FROM case_story
UNION ALL SELECT 'rel_issue_action: ' || COUNT(*) FROM rel_issue_action;" 2>/dev/null | sed 's/^/  /'
echo ""
echo "📝 影子報告草稿(v0.4):"
for f in shadow_report/build/Alternative_Report_v0.4_*.{md,html}; do
  if [ -f "$f" ]; then
    sz=$(wc -c < "$f")
    echo "  $(basename "$f"): $((sz/1024))K"
  fi
done

echo ""
echo "🏛 NAP 追蹤統計:"
sqlite3 data/crw.db "SELECT '第' || nap_period || '期: ' || COUNT(*) || ' 項' FROM nap_action GROUP BY nap_period;" 2>/dev/null | sed 's/^/  /'

echo ""
echo "📊 NHRC 監測指標:"
sqlite3 data/crw.db "SELECT '已入庫: ' || COUNT(*) FROM nhrc_indicator;" 2>/dev/null | sed 's/^/  /'

echo ""
echo "🔍 全平台搜尋索引:"
[ -f _public/search-index.json ] && echo "  $(wc -c < _public/search-index.json | xargs) bytes / $(grep -c '"id":' _public/search-index.json) 筆"
echo ""
echo "📋 完整日誌:$LOG"
echo "📋 監測快取:.monitor_cache/log.jsonl 最後 5 筆:"
tail -5 .monitor_cache/log.jsonl 2>/dev/null | sed 's/^/  /'
