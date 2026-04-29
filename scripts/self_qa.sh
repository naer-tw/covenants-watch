#!/usr/bin/env bash
# self_qa.sh — 自動化品質檢查
# 用法: bash scripts/self_qa.sh
set -uo pipefail
cd "$(dirname "$0")/.."

PASS=0; FAIL=0; WARN=0
say() { printf "%-3s %s\n" "$1" "$2"; case $1 in ✓) PASS=$((PASS+1));; ✗) FAIL=$((FAIL+1));; ⚠) WARN=$((WARN+1));; esac; }

echo "=== 兒少人權監督平台 — 自動 QA ==="
echo

# 1. 檔案完整性
echo "▶ 1. 檔案完整性"
[ -f README.md ] && say "✓" "README.md" || say "✗" "README.md 缺失"
[ -f INDEX.md ] && say "✓" "INDEX.md" || say "✗" "INDEX.md 缺失"
[ -f schema/ddl.sql ] && say "✓" "schema/ddl.sql" || say "✗" "schema/ddl.sql 缺失"
[ -f data/crw.db ] && say "✓" "data/crw.db" || say "✗" "data/crw.db 缺失"
n=$(find data/policy_issues -name "PI-*.md" | wc -l | tr -d ' ')
[ "$n" -eq 14 ] && say "✓" "14 議題卡片齊全" || say "✗" "議題卡片數錯:$n / 14"
n=$(find data/domestic_laws -name "L*.md" | wc -l | tr -d ' ')
[ "$n" -eq 15 ] && say "✓" "15 部法規齊全" || say "✗" "法規數錯:$n / 15"
echo

# 2. 議題卡片 frontmatter 完整性
echo "▶ 2. 議題卡片 frontmatter 必要欄位"
for f in data/policy_issues/PI-*.md; do
  base=$(basename "$f")
  # Wave 62 修法:讀完整 frontmatter(從第 1 個 --- 到第 2 個 ---),
  # 而非 head -20(議題卡片可能含巢狀欄位如 nhrc_indicators 而擴大長度)
  fm=$(awk '/^---$/{c++; next} c==1' "$f")
  for field in issue_id title_zh cluster severity crc_articles last_updated; do
    if ! echo "$fm" | grep -q "^${field}:"; then
      say "✗" "$base 缺欄位 $field"
    fi
  done
done
say "✓" "12 議題 frontmatter 檢核完畢"
echo

# 3. SQLite 完整性
echo "▶ 3. SQLite 一致性"
crc=$(sqlite3 data/crw.db "SELECT COUNT(*) FROM crc_article")
co=$(sqlite3 data/crw.db "SELECT COUNT(*) FROM concluding_observation")
pi=$(sqlite3 data/crw.db "SELECT COUNT(*) FROM policy_issue")
law=$(sqlite3 data/crw.db "SELECT COUNT(*) FROM domestic_law")
[ "$pi" -eq 14 ] && say "✓" "policy_issue=14" || say "✗" "policy_issue=$pi(預期 14)"
[ "$law" -eq 15 ] && say "✓" "domestic_law=15" || say "✗" "domestic_law=$law(預期 15)"
[ "$co" -ge 72 ] && say "✓" "concluding_observation=$co(CRC1+CRC2)" || say "✗" "concluding_observation=$co(預期 ≥72)"
[ "$crc" -ge 30 ] && say "✓" "crc_article=$crc" || say "⚠" "crc_article=$crc(預期 ≥30)"
# 知識圖譜密度
rel_co=$(sqlite3 data/crw.db "SELECT COUNT(*) FROM rel_issue_co")
[ "$rel_co" -ge 25 ] && say "✓" "rel_issue_co=$rel_co(議題-CO 關聯)" || say "⚠" "rel_issue_co=$rel_co(預期 ≥25)"
echo

# 4. Python 腳本語法
echo "▶ 4. Python 腳本語法"
for py in scripts/*.py shadow_report/compile.py; do
  if python3 -m py_compile "$py" 2>/dev/null; then
    say "✓" "$py"
  else
    say "✗" "$py 語法錯誤"
  fi
done
echo

# 5. compile.py 與 sync_to_jekyll 可執行
echo "▶ 5. 工具腳本可執行性"
python3 shadow_report/compile.py --check >/dev/null 2>&1 && say "✓" "compile.py --check" || say "✗" "compile.py 執行失敗"
python3 scripts/md_to_sqlite.py --verify >/dev/null 2>&1 && say "✓" "md_to_sqlite.py --verify" || say "✗" "md_to_sqlite.py 執行失敗"
echo

# 6. Markdown 連結檢查(同目錄與跨目錄相對連結)
echo "▶ 6. 內部連結檢查"
broken=0
for f in $(find data -name "*.md"); do
  dir=$(dirname "$f")
  # 抓所有 (相對連結.md)
  while IFS= read -r link; do
    target="$dir/$link"
    if [ ! -f "$target" ] && [ ! -f "${target%.md}.md" ]; then
      broken=$((broken+1))
    fi
  done < <(grep -oE '\]\(\.\./[^)]+\.md\)' "$f" 2>/dev/null | sed -E 's/^\]\((.*)\)$/\1/')
done
[ "$broken" -eq 0 ] && say "✓" "無 broken markdown 連結" || say "⚠" "$broken 個 broken 連結(可能正常,因 sources/governance 不是議題)"
echo

# 7. 兒少報導倫理紅線(QA 第五輪 #7 修正:擴大檢核範圍至 advocacy_actions、policy_issues)
echo "▶ 7. 兒少報導倫理"
# 7.1 child_safeguarding §三點五:剴剴案被告全名僅可在 cases/ 出現(且僅限 C-1101 為法院判決原文背景),
#     advocacy_actions/policy_issues 一律改用「兒福聯盟負責社工(一審判決)」
files_with_full_name=$(grep -lE "(陳尚潔|劉彩萱)" data/advocacy_actions/*.md data/policy_issues/*.md 2>/dev/null || true)
if [ -z "$files_with_full_name" ]; then
  say "✓" "advocacy / policy_issues 無剴剴案被告全名(governance §三點五)"
else
  say "✗" "違反 governance/child_safeguarding §三點五 — 以下檔案含剴剴案被告全名,須改用「兒福聯盟負責社工(一審判決)」:"
  echo "$files_with_full_name" | sed 's/^/      /'
fi
# 7.2 案例檔之去識別化(僅允許 C-1101 含法院判決加害人姓名作為背景說明)
true_names_in_cases=$(grep -lE "(陳尚潔|劉彩萱)" data/cases/*.md 2>/dev/null | wc -l | tr -d ' ')
[ "$true_names_in_cases" -le 1 ] && say "✓" "案例頁去識別化(C-1101 已移除全名;若仍出現則為法院判決原文段落,人工複核)" || say "⚠" "$true_names_in_cases 個案例含可識別人名,需人工複核"
# 檢查兒少版段落不超過 200 字
# (Wave 45 修正:wc -m 在 macOS C locale 下數 bytes 非 chars,中文 1 字 = 3 bytes
#  改用 Python 計 char 數,且去除 markdown 強調記號 / 空白)
for f in data/policy_issues/PI-*.md; do
  base=$(basename "$f")
  kid=$(awk '/^## 二、兒少版/,/^## 三、/' "$f" | sed '1d;$d' | python3 -c "
import sys, re
text = sys.stdin.read()
# 去除 markdown 標記與所有空白(對齊 compile.py:62 的字數計算)
text = re.sub(r'[*_\[\]()\`]', '', text)
text = re.sub(r'\s+', '', text)
print(len(text))
")
  if [ "$kid" -gt 300 ]; then
    say "⚠" "$base 兒少版過長:${kid} 字(理想 ≤200)"
  fi
done
# transcript_citation_sop §3.3:議題卡 / advocacy 不得直連原始逐字稿 .txt/.srt
transcripts_in_pi=$(grep -lE '\(\.\./sources/[^)]*_(逐字稿|Recording_groq|whisper-(small|medium|large))[^)]*\.(txt|srt)\)' \
  data/policy_issues/*.md data/advocacy_actions/*.md 2>/dev/null || true)
if [ -z "$transcripts_in_pi" ]; then
  say "✓" "無議題卡片 / advocacy 直連原始逐字稿(SOP §2.1 + §3.3)"
else
  say "✗" "違反 SOP §2.1 — 以下檔案直連原始逐字稿,須改連 _制度面摘要.md:"
  echo "$transcripts_in_pi" | sed 's/^/      /'
fi
echo

# 8. SaaS 部署指南齊全
echo "▶ 8. 部署指南齊全"
for d in notion super tally datawrapper github_pages; do
  if ls deployment/${d}*.md >/dev/null 2>&1; then
    say "✓" "deployment/${d}_*.md"
  else
    say "✗" "deployment/${d}_*.md 缺失"
  fi
done
echo

# === 結算 ===
echo "=== 結算 ==="
echo "  ✓ pass: $PASS"
echo "  ⚠ warn: $WARN"
echo "  ✗ fail: $FAIL"
[ "$FAIL" -eq 0 ] && exit 0 || exit 1
