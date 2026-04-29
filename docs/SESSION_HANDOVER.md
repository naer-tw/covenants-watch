# Session Handover — 兩公約施行總檢討平台

> **建立日**：2026-04-29
> **最後更新**：2026-04-30（Wave 1-37：16 PI 全完成 + 兩輪 cold read QA + 全部修補）
> **方法論來源**：兒少權監督平台 PLATFORM_PLAYBOOK.md
> **此檔目的**：讓下個 session 不依賴對話脈絡即可冷接手

---

## 一、平台目前狀態（截至 Wave 19）

```
git log --oneline 最新 4 條：
61e14c7 fix(Wave 18): cold read QA 全面修補 — 移除預設貼標 + 數字一致 + steelman 規範
04b5b99 fix: remove stray crw.db from old self_qa heredoc
24f9c10 fix(Wave 16): self_qa.sh 改寫為兩公約版
ff6d8ea init: 兩公約施行總檢討平台 — fork 自兒少權監督平台(Wave 1-16)
```

**self_qa.sh 狀態**：✓ 63 pass / ⚠ 0 / ✗ 0
**SQLite**：4 PI 入庫 / 30 vocab_co_topic / 7 政黨 / 8 problem_tag / 3 quotability / 4 privacy
**對外 HTML**：5 份（首頁 + 4 PI），全通過 emoji 檢核
**部署**：尚未 git push（無 remote）

## 一·二、cold read QA 修補（Wave 18）

外部 QA agent 發現 5 個關鍵問題，全部已修補：
1. 「308 點 CO」數字不一致 → 改「逾 250 點」
2. PI-12/13/_ARTICLE_INDEX 違反自家紅線（預設貼標、政黨偏好預設、團體點名）→ 整份重寫，所有預設假設移入 `internal/PI-12_hypotheses.md`
3. 「× 10 不對稱」閾值缺統計學依據 → 改 chi-square / 基尼係數 + CRC/CEDAW/CRPD 對照組
4. 點名 NGO 名稱有名譽風險 → 改代碼匿名化（P1/P2/N01-N99）
5. 首頁含 ⚠ emoji → 替換為 inline SVG

新增 `_STEELMAN_AND_CONTROL_GROUPS.md` 強制 SOP-1/2/3/4。

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
| 16 | git init + first commit + self_qa 首跑（63 pass）|
| 17 | 4 張 PI 生成 _public/issues/PI-XX.html + spawn cold read QA |
| 18 | **cold read 全面修補**：移除預設貼標、政黨點名、假數字、emoji + 新增 _STEELMAN SOP + internal/ 內部研究夾 |
| 19 | auto memory + 預覽驗證 + 本檔首次更新 |
| 20-31 | 完成剩餘 12 張 PI（PI-02/04/05/06/07/08/09/10/11/14/15/16）全含 §steelman + §control_group |
| 32 | 16 PI HTML 重生 + emoji 統一替換為 inline SVG |
| 33-34 | 首頁加 16 PI 連結 + 統計欄；PI-01/03 cold read 漏網部分補修 |
| 35 | **第二輪 cold read QA**（5 個 actionable 問題） |
| 36 | 第二輪 5 問題全修：PI-01 政黨欄位中性化、PI-09 NCC 案件匿名化條款、**PI-10 Steelman B 補強至對等強度**（補 9 條判例 + 起草史 + GC13 §28）、PI-07 NHRC 措辭柔化、PI-02 交叉引用補齊 |
| 37 | 本檔最終更新至 Wave 37 |

## 三、四大區塊與 16 張議題卡狀態

### A 區：兩公約施行 16 年總體檢討（4 卡）
- [x] PI-01 兩公約 16 年施行歷程
- [x] PI-02 第一次審查 13 年回顧
- [x] PI-03 第四次審查 2025 全覽
- [x] PI-04「施行法」獨特性國際比較

### B 區：NAP 國家人權行動計畫（3 卡）
- [x] PI-05 第一期 NAP 執行率
- [x] PI-06 第二期 NAP 關鍵承諾
- [x] PI-07 NHRC 獨立監督盲點

### C 區：國際比較（4 卡）
- [x] PI-08 第 18 條宗教自由國際標準
- [x] PI-09 第 19 條言論自由在台萎縮
- [x] PI-10 第 26 條 vs 第 13 條詮釋光譜（**雙面 Steelman 對等**）
- [x] PI-11 第 12 條健康權與兒少自殺

### D 區：援引行為與政策落差客觀檢驗（5 卡）
- [x] PI-12 條文援引頻率分布客觀檢驗
- [x] PI-13 立法院公報量化
- [x] PI-14 民間代表團組成代表性
- [x] PI-15 人權白皮書 4 維對照
- [x] PI-16 教科書中的兩公約敘事

> **16/16 框架完成**，狀態為「研究設計骨架完成，待實證資料 Wave 21+ 匯入」。
> 全部含 §steelman + §control_group + 品質控管 + 立場聲明。

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

## 六、可進入下個階段的方向（Wave 38+）

實證化優先順序（依第二輪 cold read 建議）：
1. **PI-09 言論自由客觀指標** — 資料最易（RSF / Freedom House 公開）、政治風險最低、可立即視覺化 14 年時間序列
2. **PI-05 第一期 NAP 執行率** — NAP I 已於 2024 結束，期末報告 + CovenantsWatch 評估皆已存在
3. **PI-01 / PI-02 16 年 250 點 CO 匯入** — 全平台地基；前三屆 CO 全文公開；建議與 PI-12 共用 schema
4. **Wave 50+ 影子報告 v0.1** — compile 5 audience（壓縮已實證之 PI）

最難取得（後排）：PI-15 各部會分年預算數位化、PI-16 五版教科書授權、PI-07 NHRC 內部任命過程

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
