# Session Handover — 兩公約施行總檢討平台

> **建立日**：2026-04-29
> **最後更新**：2026-04-30（Wave 1-51：16 PI + 兩輪 cold read + 首批實證注入 + 平台基礎設施完備）
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
| 37 | 本檔更新至 Wave 37 |
| 38 | 預覽驗證 — 17 HTML 全 200 / Steelman B 補強 9 條法源齊全 |
| 39 | 兩公約專用抓取腳本骨架（fetch_co / fetch_legislative / statistical_analysis）|
| 40 | **PI-09 首批實證**：RSF Taiwan 2013-2025 排名（47 → 24，亞洲第 1）|
| 41 | PI-09 加 Freedom House 2017-2026 評分 + 雙指標交叉佐證 + status 升 partial_evidence |
| 42 | _public/about.html + methodology.html + feedback.html（4 類回饋通道）|
| 43 | robots.txt + sitemap.xml（20 URL）+ llms.txt（AI 友善索引）|
| 44 | shadow_report/master_template.md（影子報告 v0.1 骨架，6 章 + 4 附錄）|
| 45 | deployment/github_pages.md（A/B/C 三種域名選項 + 預檢清單 + 上線判準）|
| 46 | 首頁 nav 加 about/methodology/feedback/llms 連結 |
| 47 | self_qa 升至 66 pass + commit |
| 48 | 預覽驗證 — 主要頁面 + 16 PI + sitemap/llms 全 200 |
| 49 | **PI-05 首批 metadata**：NAP I 期程、PDF URL、CovenantsWatch 既有評估 + status 升 partial_metadata |
| 50 | **PI-09 區域對照組**：日本 / 韓國 / 澳 / 紐 RSF 排名（佐證 Taiwan 上升非區域同步）|
| 51 | 本檔更新至 Wave 51 |
| 53 | 整合本地 skills（~/clawd/skills/）— legislative-monitor / international-radar / news-monitoring |
| 54 | PI-13 採用三表架構（A 議題 / B 事件 / C 對照）+ L1/L2/L3 + 兩公約特化偵測 |
| 55 | Felo AI 實證搜尋 — 抓到太極門案（PI-08 個案研究）|
| 56 | data/sources/_INTERNATIONAL_RADAR.md — 9 大國際資料源類別 |
| 57 | parallel-research spawn agent 蒐集 PI-11 自殺率資料（背景執行）|
| 58 | shadow_report/compile.py 5 audience 完整實作（professional/media/advocacy/legislative/social）|
| 59 | self_qa 升至 67 pass + commit |
| 60 | **PI-11 首批實證**：青少年自殺率 2018-2025（2023 年 7.0 高於 OECD 6.5）+ 政策投入時間軸 |
| 60 | status: partial_evidence（PI-05/08/09/11 皆已部分實證）|
| 62 | **並行 spawn 4 個 agent**（PI-04 / PI-07 / PI-15 / PI-01-02-03）|
| 63 | **重大資料更正**：第 4 次審查實際是 **2026-05~06 預定**（之前誤記 2025-01）|
| 63 | PI-03 全面更正 + 12 委員名單（含 Manfred Nowak 第 4 屆主席）|
| 63 | PI-04 6 國對照（英/日/韓/菲/印尼/台）+ 2 派學術論述（廖福特 vs 黃昭元）|
| 63 | PI-07 巴黎原則 6 要件 + GANHRI 未認證 + 4 國亞洲對照 |
| 64 | PI-15 性平處預算（2024 1,627 萬 → 2025 提案削至 3,000 元）|
| 64 | _public/dashboards/index.html 戰情室視覺化說明頁 |
| 65 | partial_evidence 達 7 張（PI-04/05/07/08/09/11/15）|
| 66-72 | spawn 第二波 4 agent + 第三輪 cold read QA + 5 個修補 |
| 73 | partial_evidence 達 10 張（+PI-02/06/14）|
| 75 | spawn 第三波 4 agent（PI-13/10/16/12）|
| 76 | PI-01/03 status 升 partial_evidence（PI-03 12 委員描述更正）|
| 77 | **🎯 全 16/16 PI 達 partial_evidence**（PI-10/12/13/16 完成）|
| 77 | data/evidence CSV 達 15 份 |

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

## 六、可進入下個階段的方向（Wave 52+）

已完成首批實證（Wave 40-50）：
- ✅ PI-09 RSF 13 年 + FH 10 年 + 日韓澳紐對照組
- ✅ PI-05 NAP I metadata（PDF URL + CovenantsWatch 既有評估）

下個 session 推薦做：
1. **下載 NAP I PDF + OCR 切段 → SQLite `nap_action` 表**
   `python3 scripts/two_cov_fetch_co.py --review 1 --pdf <path>`
2. **PI-01 / PI-02 4 屆 CO 全文匯入**（前三屆已公開）
3. **PI-09 加 NCC 處分量化**（須法律顧問複核 + 14 日異議期）
4. **PI-13 立法院公報 API 對接**（須申請 token）
5. **Datawrapper 視覺化**：RSF 13 年趨勢圖、FH 10 年趨勢圖、區域對照組
6. **Wave 60+ 影子報告 v0.2**（PI-05/09 實證注入後 compile）

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
