#!/usr/bin/env bash
# self_qa.sh — 兩公約總檢討平台自動 QA
# 用法: bash scripts/self_qa.sh
set -uo pipefail
cd "$(dirname "$0")/.."

PASS=0; FAIL=0; WARN=0
say() { printf "%-3s %s\n" "$1" "$2"; case $1 in ✓) PASS=$((PASS+1));; ✗) FAIL=$((FAIL+1));; ⚠) WARN=$((WARN+1));; esac; }

echo "=== 兩公約施行總檢討平台 — 自動 QA ==="
echo

# 1. 基礎檔案完整性
echo "▶ 1. 基礎檔案完整性"
[ -f CLAUDE.md ] && say "✓" "CLAUDE.md" || say "✗" "CLAUDE.md 缺失"
[ -f docs/SESSION_HANDOVER.md ] && say "✓" "SESSION_HANDOVER.md" || say "✗" "SESSION_HANDOVER.md 缺失"
[ -f docs/ROADMAP.md ] && say "✓" "ROADMAP.md" || say "✗" "ROADMAP.md 缺失"
[ -f docs/DECISIONS.md ] && say "✓" "DECISIONS.md" || say "✗" "DECISIONS.md 缺失"
[ -f docs/PLATFORM_PLAYBOOK.md ] && say "✓" "PLATFORM_PLAYBOOK.md" || say "✗" "方法論 PLAYBOOK 缺失"
[ -f data/schema.sql ] && say "✓" "schema.sql" || say "✗" "schema.sql 缺失"
[ -f data/two_cov.db ] && say "✓" "two_cov.db" || say "✗" "two_cov.db 缺失"
[ -f governance/INDEX.md ] && say "✓" "governance/INDEX.md" || say "✗" "governance/INDEX.md 缺失"
[ -f _public/index.html ] && say "✓" "_public/index.html" || say "✗" "_public/index.html 缺失"
echo

# 2. 議題卡片框架
echo "▶ 2. 議題卡片"
[ -f data/policy_issues/_PI_PLANNING.md ] && say "✓" "_PI_PLANNING.md" || say "✗" "_PI_PLANNING.md 缺失"
n_pi=$(find data/policy_issues -name "PI-*.md" -type f 2>/dev/null | wc -l | tr -d ' ')
[ "$n_pi" -ge 4 ] && say "✓" "已建立 PI 卡:$n_pi(目標 16,當前 ≥4)" || say "⚠" "PI 卡片數:$n_pi(目標 16)"

for f in data/policy_issues/PI-*.md; do
  [ -f "$f" ] || continue
  base=$(basename "$f")
  fm=$(awk '/^---$/{c++; next} c==1' "$f")
  for field in pi_id title block priority status covenant; do
    echo "$fm" | grep -q "^${field}:" || say "⚠" "$base 缺欄位 $field"
  done
done
say "✓" "PI frontmatter 必要欄位檢核完畢"
echo

# 3. SQLite 一致性
echo "▶ 3. SQLite 一致性"
if [ -f data/two_cov.db ]; then
  pi_db=$(sqlite3 data/two_cov.db "SELECT COUNT(*) FROM policy_issue" 2>/dev/null || echo 0)
  topic=$(sqlite3 data/two_cov.db "SELECT COUNT(*) FROM vocab_co_topic" 2>/dev/null || echo 0)
  party=$(sqlite3 data/two_cov.db "SELECT COUNT(*) FROM vocab_political_party" 2>/dev/null || echo 0)
  [ "$pi_db" -ge 4 ] && say "✓" "policy_issue=$pi_db(目標 16)" || say "⚠" "policy_issue=$pi_db"
  [ "$topic" -eq 30 ] && say "✓" "vocab_co_topic=30" || say "✗" "vocab_co_topic=$topic"
  [ "$party" -ge 7 ] && say "✓" "vocab_political_party=$party" || say "✗" "政黨詞表=$party"

  for tbl in policy_issue concluding_observation co_citation nap_action evidence legislative_citation; do
    has=$(sqlite3 data/two_cov.db "SELECT name FROM sqlite_master WHERE type='table' AND name='$tbl'" 2>/dev/null)
    [ -n "$has" ] && say "✓" "table:$tbl" || say "✗" "table:$tbl 缺失"
  done

  for fts in fts_co fts_evidence fts_legislative; do
    has=$(sqlite3 data/two_cov.db "SELECT name FROM sqlite_master WHERE type='table' AND name='$fts'" 2>/dev/null)
    [ -n "$has" ] && say "✓" "fts:$fts" || say "⚠" "fts:$fts 缺失"
  done
fi
echo

# 4. Python 腳本語法
echo "▶ 4. Python 腳本語法(略過 .disabled)"
for py in scripts/*.py; do
  [ -f "$py" ] || continue
  case "$py" in *.disabled) continue;; esac
  if python3 -m py_compile "$py" 2>/dev/null; then
    say "✓" "$py"
  else
    say "✗" "$py 語法錯誤"
  fi
done
echo

# 5. 兩公約核心腳本可執行
echo "▶ 5. 兩公約核心腳本"
python3 scripts/two_cov_md_to_db.py --dry-run >/dev/null 2>&1 && say "✓" "two_cov_md_to_db.py --dry-run" || say "✗" "two_cov_md_to_db.py 失敗"
echo

# 6. 立場與紅線
echo "▶ 6. 立場與紅線"
emoji_files=$(find _public -name "*.html" -exec grep -lP "[\x{1F300}-\x{1F9FF}]|[\x{2600}-\x{27BF}]" {} \; 2>/dev/null || true)
[ -z "$emoji_files" ] && say "✓" "_public/ HTML 無 emoji" || say "⚠" "_public/ 含 emoji:$emoji_files"
(grep -q "支持兩公約原始精神\|Support 兩公約 original spirit\|本平台支持兩公約原始精神" CLAUDE.md 2>/dev/null) && say "✓" "CLAUDE.md 立場聲明" || say "✗" "CLAUDE.md 立場聲明缺失"
(grep -q "絕對紅線\|Absolute red lines\|Red lines" CLAUDE.md 2>/dev/null) && say "✓" "CLAUDE.md 絕對紅線" || say "✗" "CLAUDE.md 絕對紅線缺失"
echo

# 7. 治理文件
echo "▶ 7. 治理文件"
for gov in INDEX.md ai_use_policy.md child_safeguarding.md content_sop.md \
           document_governance.md file_naming.md privacy_policy.md \
           rbac.md transcript_citation_sop.md; do
  [ -f "governance/$gov" ] && say "✓" "governance/$gov" || say "✗" "governance/$gov 缺失"
done
echo

# 8. 三層資料治理
echo "▶ 8. 三層資料治理"
for layer in raw clean publish; do
  [ -d "data/sources/$layer" ] && say "✓" "data/sources/$layer/" || say "✗" "data/sources/$layer 缺失"
done
echo

# 9. 內部 markdown 連結
echo "▶ 9. 內部連結"
broken=0
for f in $(find data docs CLAUDE.md -name "*.md" 2>/dev/null); do
  dir=$(dirname "$f")
  while IFS= read -r link; do
    [ -z "$link" ] && continue
    case "$link" in http*|//*|\#*) continue;; esac
    target="$dir/$link"
    [ -e "$target" ] || broken=$((broken+1))
  done < <(grep -oE '\]\(([^)]+\.md)\)' "$f" 2>/dev/null | sed -E 's/\]\(([^)]+)\)/\1/')
done
[ "$broken" -eq 0 ] && say "✓" "無 broken markdown 連結" || say "⚠" "$broken 個 broken 連結"
echo

# 10. Evidence 框架
echo "▶ 10. 證據框架"
[ -f data/evidence/_EVIDENCE_INDEX.md ] && say "✓" "evidence 索引存在" || say "✗" "evidence 索引缺失"
n_evidence=$(find data/evidence -name "EV-*.md" -type f 2>/dev/null | wc -l | tr -d ' ')
say "✓" "evidence 卡:$n_evidence(框架期,Wave 21+ 才匯入)"
echo

echo "=== 結算 ==="
echo "  ✓ pass: $PASS"
echo "  ⚠ warn: $WARN"
echo "  ✗ fail: $FAIL"
[ "$FAIL" -eq 0 ] && exit 0 || exit 1
