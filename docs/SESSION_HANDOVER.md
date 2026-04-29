# Session Handover — 兩公約施行總檢討平台

> **建立日**：2026-04-29（Wave 1-16 一氣呵成）
> **方法論來源**：兒少權監督平台 PLATFORM_PLAYBOOK.md
> **此檔目的**：讓下個 session 不依賴對話脈絡即可冷接手

---

## 一、平台目前狀態（截至 Wave 16）

```
git log --oneline 顯示（最新）：
  init: 兩公約總檢討平台 — 從兒少權監督平台 fork（含 16 PI 規劃 + 4 P0 卡 + SQLite）
```

**self_qa.sh 狀態**：待 Wave 16 首次執行（已知問題：scripts/ 仍有兒少權專用腳本，已標記 .disabled）
**SQLite**：4 PI 入庫 / 30 vocab_co_topic / 7 政黨 / 8 problem_tag / 3 quotability / 4 privacy
**部署**：尚未 git push（無 remote），_public/index.html 已生

## 二、Wave 1-16 增量

| Wave | 重點 |
|---|---|
| 1 | 建立目錄結構 + 複製 governance（12 份）+ scripts（28 個）|
| 2 | CLAUDE.md（含立場紅線 9 條）|
| 3 | _PI_PLANNING.md（16 PI 四大區塊）|
| 4 | _CO_INDEX.md（CO schema + 30 topic vocab）|
| 5 | _NAP_INDEX.md（NAP 兩期追蹤架構）|
| 6 | _EVIDENCE_INDEX.md（5 維工具化評估）|
| 7 | PI-01 兩公約 16 年總覽（draft）|
| 8 | PI-03 第四次審查 2025（draft_pending_data）|
| 9 | PI-12 條文援引不對稱（framework_pending_data）|
| 10 | PI-13 立法院公報量化（framework_pending_data）|
| 11 | _ARTICLE_INDEX.md（ICCPR 53+ICESCR 31 條反查表）|
| 12 | data/schema.sql + two_cov.db 初始化（含 FTS5）|
| 13 | scripts/two_cov_md_to_db.py + 兒少權專用腳本 .disabled |
| 14 | _public/index.html 首頁 |
| 15 | 本檔 + ROADMAP + DECISIONS |
| 16 | git init + first commit + self_qa 首跑 |

## 三、四大區塊與 16 張議題卡狀態

### A 區：兩公約施行 16 年總體檢討（4 卡）
- [x] PI-01 兩公約 16 年施行歷程（draft）
- [ ] PI-02 第一次審查 13 年回顧
- [x] PI-03 第四次審查 2025 全覽（draft_pending_data）
- [ ] PI-04「施行法」獨特性國際比較

### B 區：NAP 國家人權行動計畫（3 卡）
- [ ] PI-05 第一期 NAP 執行率
- [ ] PI-06 第二期 NAP 關鍵承諾
- [ ] PI-07 NHRC 獨立監督盲點

### C 區：國際比較（4 卡）
- [ ] PI-08 第 18 條宗教自由國際標準
- [ ] PI-09 第 19 條言論自由在台萎縮
- [ ] PI-10 第 26 條 vs 第 13 條條文選擇性
- [ ] PI-11 第 12 條健康權與兒少自殺

### D 區：工具化與政黨化證據（5 卡）
- [x] PI-12 條文援引頻率不對稱（framework_pending_data）
- [x] PI-13 立法院公報量化（framework_pending_data）
- [ ] PI-14 民間代表團組成代表性
- [ ] PI-15 人權白皮書 vs 施政落差
- [ ] PI-16 教科書中的兩公約敘事

> 4/16 完成，狀態多為「框架完成、待實證資料」。

## 四、用戶端待辦（本平台無法代為）

| 動作 | 觸發條件 | 截止 |
|---|---|---|
| **下載人權公約施行監督聯盟資料** | covenantswatch.org.tw 全文檔 | 隨時 |
| **下載 4 次審查結論性意見全文** | 法務部「人權大步走」 PDF | 隨時 |
| **下載 NAP 第一/二期 PDF** | 行政院公告 | 隨時 |
| **立法院公報 API 申請** | 取得 token / 確認 robots 合規 | Wave 12 量化前 |
| **媒體 archive 取得授權** | 各報 archive 或 web.archive.org | Wave 12 量化前 |
| **Tally 表單開立**（feedback）| 連通 _public/feedback.html | 上線前 |
| **GitHub repo 建立 + push** | naer-tw/two-covenants 或 sub-path | 任何時候 |
| **域名 / sub-path 決定** | policy.aabe.org.tw/two-covenants/ vs 獨立 | 部署前 |

## 五、下個 session 開頭該跑的指令

```bash
cd /Users/coachyang/Documents/Claude/Projects/兩公約總檢討平台

# 1. 看當前狀態
git log --oneline | head -10
bash scripts/self_qa.sh 2>&1 | tail -10

# 2. 確認 SQLite 狀態
sqlite3 data/two_cov.db "SELECT pi_id, status FROM policy_issue;"
sqlite3 data/two_cov.db ".tables"

# 3. 看待辦
cat docs/SESSION_HANDOVER.md | head -50
cat docs/ROADMAP.md
cat data/policy_issues/_PI_PLANNING.md | head -40

# 4. 跑 md 同步
python3 scripts/two_cov_md_to_db.py
```

## 六、可進入下個階段的方向

1. **Wave 17 候選**：個別 PI 生成印刷 HTML（從 .md 用 build_single_doc.py，需先確認該腳本是否能跑兩公約 PI schema）
2. **Wave 18 候選**：第一輪 cold read QA（spawn Explore agent 讀 4 PI + INDEX + 給回饋）
3. **Wave 19 候選**：完成剩餘 12 PI 框架（每張 30-60 min）
4. **Wave 20 候選**：CO 結論性意見資料匯入（需用戶下載 PDF）
5. **Wave 21 候選**：立法院公報 API 對接 + 援引頻率實測（PI-13）
6. **Wave 22 候選**：第一份影子報告 v0.1（壓縮 PI-01/03/12/13）

## 七、不要做的事

- ❌ 不要在沒讀 `governance/transcript_citation_sop.md` 前處理任何訪談
- ❌ 不要在公開頁面放 emoji（CLAUDE.md §八）
- ❌ 不要點名特定當事個人（除已被法院判決公開）
- ❌ 不要使用情緒性 / 攻擊性語言（紅線 9 條）
- ❌ 不要 force push、不要 amend 已 push 的 commit
- ❌ 不要安裝 brew/pip 系統套件（用 .venv/bin/pip）
- ❌ 不要 Notion / Super.so（堅持 Markdown SSOT）
- ❌ 不要在沒有 archive.org 典藏前發布工具化證據

## 八、本平台立場（每個新 session 必讀）

支持兩公約原始普世人權精神 / 反對工具化 / 反對政黨化 / 客觀證據優先 / 尊重宗教良心自由 / 對事不對人。

詳見 `CLAUDE.md` §二「核心立場（紅線）」。

## 九、目錄速覽

```
data/
├── policy_issues/
│   ├── _PI_PLANNING.md         (16 PI 規劃)
│   ├── PI-01_兩公約16年施行歷程.md
│   ├── PI-03_第四次國際審查2025.md
│   ├── PI-12_條文援引頻率不對稱.md
│   └── PI-13_立法院公報量化分析.md
├── co/
│   ├── _CO_INDEX.md
│   └── _ARTICLE_INDEX.md       (ICCPR 53+ICESCR 31)
├── nap/
│   └── _NAP_INDEX.md
├── evidence/
│   └── _EVIDENCE_INDEX.md
├── sources/{raw,clean,publish}/
├── cases/
├── two_cov.db                  (SQLite + FTS5)
└── schema.sql

scripts/
├── two_cov_md_to_db.py         (新)
├── _http.py / _md_frontmatter.py
├── self_qa.sh
├── build_single_doc.py
├── md_to_sqlite.py
├── monitor_updates.py
├── *.disabled                  (兒少權專用,改寫前停用)
└── ...

governance/        (12 份完整複製)
docs/
├── PLATFORM_PLAYBOOK.md         (方法論來源)
├── SESSION_HANDOVER.md          (本檔)
├── ROADMAP.md
└── DECISIONS.md
_public/
└── index.html                   (首頁,noindex)
shadow_report/                   (空,Wave 22+ 啟動)
deployment/                      (空,部署前填)
forms/                           (空)
CLAUDE.md
.gitignore
```
