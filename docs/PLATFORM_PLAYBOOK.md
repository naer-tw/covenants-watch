# Platform Playbook — 給新專案 session 的方法論交接

> **撰寫日**:2026-04-28(Wave 92 收尾後)
> **適用情境**:當您要開新專案(政策監督 / 議題倡議 / 知識庫平台),想直接套用此平台之經驗
> **不適用情境**:純技術專案、APP 開發、商業系統(本 playbook 是 NGO 政策監督專屬)

## 一、本平台跑通的核心方法論(可直接複製)

### 1.1 雙軸審查框架(對任何國際公約 / 政府承諾追蹤皆可用)

```
類別一:過去要求沒兌現
  ├─ CRC / CEDAW / CRPD / 兩公約 / 任一審查機制
  ├─ 國際委員結論性意見(CO)逐條追蹤
  └─ NHRC 監督報告 / NAP 行動計畫 進度檢核

類別二:關注議題沒提
  ├─ NGO 自家倡議資產(過去 3-5 年累積)
  ├─ 重大社會事件(剴剴案、新北割頸案等)
  └─ 民間問卷調查(本專案 8,743 份青年部問卷)
```

**用法**:每場政府公聽會 / 民間審查發言稿,都用「類別一 + 類別二」結構 → 政府很難迴避。

### 1.2 5 種輸出版本(從同一份議題卡片生)

| 版本 | 受眾 | 字數 | 特徵 |
|---|---|---|---|
| 專業版 | 審查委員、政府、NGO | 完整 | 法理 + 統計 + CO 段落號 |
| 媒體版 | 記者、公眾 | 800-1200 字 | 先講結論、核心數字、3 項建議 |
| 兒少版 | 8-18 歲學生 | 200 字以內 | 白話、生活語言、求助專線 |
| 立法院版 | 立委辦公室 | 條列式 | 機關缺失 + 修法建議 + 質詢題草稿 |
| 社群版 | IG / FB / Threads | 140 字 + 圖卡腳本 + 30 秒短影音腳本 | 鉤子 + CTA |

**實作**:`shadow_report/compile.py` 之 `--audience` 旗標。

### 1.3 三層文件治理(對任何資料密集型專案皆可用)

```
data/sources/
├── raw/      原始檔(不修改)
├── clean/    OCR 切段 / 去浮水印 / 切頁
└── publish/  可檢索引用之最終版(寫入 SQLite + HTML)
```

**規則**:任何文件都先進 raw,經 DPO + 編輯雙簽才升 publish。

### 1.4 6 組受控詞表(避免標籤野生長)

- `vocab_issue` 議題
- `vocab_crc_article` 國際公約條文
- `vocab_agency` 主管機關(含 aliases JSON)
- `vocab_problem_tag` 問題判斷標籤(NO_DATA、NO_OUTCOME 等 8 種)
- `vocab_quotability` 可引用性(可直接 / 需改寫 / 僅背景)
- `vocab_privacy` 隱私等級(公開 / 匿名後可公開 / 限內部 / 極敏感)

**規則**:新標籤須由主編核可,廢用 tag 不刪除只 deprecate。

### 1.5 Wave-based 開發節奏

```
1 wave = 1 個明確目標(可在 30-90 分鐘完成)
       + 1 commit(訊息含 Wave 編號 + 對照藍圖檢核)
       + self_qa.sh 通過

每 5-10 wave 跑一次:
       + 第 N 輪獨立 QA cold read(spawn agent)
       + SESSION_HANDOVER.md 更新
```

## 二、技術堆疊選型(已驗證)

| 層 | 工具 | 月成本 | 為何選 |
|---|---|---|---|
| 後台編輯 | **Markdown + git** | $0 | 版本控制 + 文字搜尋 + 不鎖定 |
| 主資料庫 | **SQLite(本機檔)** | $0 | FTS5 全文索引 + 關聯查詢 + 100K 行不卡 |
| 部署 | **GitHub Pages** | $0 | 純靜態 + CDN + 免費自訂域 |
| 表單 | Tally(免費版)| $0 | EU 託管 + 條件邏輯 + 無 cookie |
| 圖表 | Datawrapper(免費)| $0 | 新聞媒體標準 + iframe 嵌入 |
| **總月成本** | | **$0** | 比藍圖原推 USD 37-41 / 月省 100% |

**偏離藍圖**:藍圖預設 Notion+Super.so($40/月)。我們選 Markdown 是因為:
- NGO 預算現實
- git 工作流可長期維運
- 零鎖定風險

## 三、可直接複製的核心檔案(複製後改名即可)

### 3.1 必複製(架構基礎)

```
governance/
├── INDEX.md                          # 治理文件導讀
├── child_safeguarding.md             # 兒少 / 弱勢群體保護
├── transcript_citation_sop.md        # 訪談 / 公聽會引用 SOP
├── proxy_kid_version_disclosure.md   # 成人代擬透明標記
├── ai_use_policy.md                  # AI 使用政策
├── privacy_policy.md                 # 隱私政策
├── rbac.md                           # 角色權限矩陣
├── file_naming.md                    # 檔名規則
├── content_sop.md                    # 內容生產 SOP
├── document_governance.md            # 三層 + 6 詞表
├── wcag_audit_report.md              # 無障礙稽核
└── youth_advisory_sop.md             # 青少年顧問小組(若涉兒少)

scripts/
├── _http.py                          # 共用 HTTP 模組
├── _md_frontmatter.py                # YAML frontmatter 解析
├── monitor_updates.py                # 政府站指紋監測
├── md_to_sqlite.py                   # Markdown → SQLite 同步
├── build_single_doc.py               # md → 印刷 HTML(--noindex / --schema-type)
├── build_search_index.py             # 預建 JSON 搜尋索引
├── render_dashboard.py               # 戰情室資料驅動
├── self_qa.sh                        # 37+ 項自動檢核
├── wcag_audit.py                     # WCAG 2.1 AA 稽核
├── classify_sources.py               # 三層文件分類
├── populate_passages.py              # 段落入庫 + 自動標籤
├── migrate_schemas.py                # rebuild 後 schema 還原
├── translation_audit.py              # 翻譯品質檢核
├── monthly_maintenance.sh            # 12 步驟月度維護
└── emoji_to_svg.py                   # emoji → SVG 替換

CLAUDE.md                             # 專案根指令(改 NGO 名 + 議題)
.gitignore                            # 標準 Python + venv + 監測快取
```

### 3.2 可仿照(議題客製)

```
data/policy_issues/PI-XX_*.md         # 議題卡片 frontmatter schema
data/advocacy_actions/A-YYYY-MM-DD_*.md  # 倡議行動 frontmatter
shadow_report/master_template.md      # 影子報告體例
shadow_report/compile.py              # 5 audience 自動匯流
deployment/{tally,datawrapper,decap_cms,super,notion,github_pages}_*.md
```

### 3.3 不要複製(專案專屬)

```
data/sources/                         # 原始檔(新專案不同)
data/policy_issues/PI-XX_xx.md        # 議題內容(專案專屬)
_share/                                # CRC 審查代表準備包(專案專屬)
_public/                               # 公開頁面(專案專屬)
```

## 四、新 session 啟動 prompt 範本

### 4.1 短版(直接給 Claude)

```
我要開新專案 [專案名稱],主題是 [X 政策監督 / Y 議題倡議]。

請先讀以下檔案理解方法論:
1. /Users/coachyang/Documents/Claude/Projects/兒少權監督平台/docs/PLATFORM_PLAYBOOK.md
2. /Users/coachyang/Documents/Claude/Projects/兒少權監督平台/docs/SESSION_HANDOVER.md
3. /Users/coachyang/Documents/Claude/Projects/兒少權監督平台/governance/INDEX.md

讀完後告訴我:
1. 你理解的核心方法論摘要(雙軸框架 / 5 audience / 三層治理 / wave 節奏 / Markdown SSOT)
2. 哪些檔案要直接複製到新專案
3. 第一個 wave 應該做什麼(建議:scaffolding + CLAUDE.md + 第 1 個議題卡)

我會回答後再開始實作。
```

### 4.2 長版(含議題清單)

加上:
```
新專案的議題範圍:
- 議題 1: ...
- 議題 2: ...
- 對應國際公約 / 政府機制: ...
- 預估議題卡片數: 10-15 張
- 預期審查時程: ...
```

## 五、轉移的 3 條路徑(由淺到深)

### 5.1 最輕量:複製 PLAYBOOK + 啟動 prompt(15 分鐘)

```bash
# 在新專案目錄
cd ~/Documents/Claude/Projects/新專案/
cp ~/Documents/Claude/Projects/兒少權監督平台/docs/PLATFORM_PLAYBOOK.md ./
```

然後新 session 用 §4.1 prompt。

### 5.2 中等:複製核心架構(60 分鐘)

```bash
# 複製治理 + scripts + 配置(共 ~30 檔)
mkdir -p 新專案/{data/{policy_issues,advocacy_actions,sources,cases},governance,scripts,docs,shadow_report,_public,deployment}

# governance(整套複製,改 NGO 名)
cp -r ~/.../兒少權監督平台/governance/ 新專案/governance/

# scripts(整套複製)
cp -r ~/.../兒少權監督平台/scripts/ 新專案/scripts/

# CLAUDE.md + .gitignore
cp ~/.../兒少權監督平台/CLAUDE.md 新專案/

# 議題卡片 schema 範本(複製 PI-01 改名後改內容)
cp ~/.../兒少權監督平台/data/policy_issues/PI-01_*.md 新專案/data/policy_issues/_TEMPLATE.md

# 部署指南
cp -r ~/.../兒少權監督平台/deployment/ 新專案/deployment/

cd 新專案
git init
python3 -m venv .venv
.venv/bin/pip install pypdf openpyxl  # 依需求
```

### 5.3 完整:fork 整個架構(2-3 小時)

```bash
# 1. clone 本專案到新位置
cp -r ~/Documents/Claude/Projects/兒少權監督平台 ~/Documents/Claude/Projects/新專案

cd ~/Documents/Claude/Projects/新專案

# 2. 清空專案專屬內容(保留 schema + scripts)
rm -rf data/sources/* data/policy_issues/PI-* data/advocacy_actions/A-*
rm -rf _share _public/issues/* _public/reports/*
rm data/crw.db
sqlite3 data/crw.db < schema.sql  # 重建空 schema(本平台未產出 schema.sql 但可從 .schema 匯出)

# 3. 改名所有 NGO 識別
grep -rl "AABE\|國教行動聯盟" --include="*.{md,html,py,sh}" | \
  xargs sed -i '' 's/AABE/新NGO英文簡稱/g; s/國教行動聯盟/新NGO中文名/g'

# 4. 改 CLAUDE.md 之專案描述

# 5. 跑 self_qa.sh 看狀態
bash scripts/self_qa.sh

# 6. git init + 第一個 commit
git init && git add -A && git commit -m "init: from 兒少權監督平台 fork"
```

## 六、Memory 系統設定(讓所有 session 自動知道這個 playbook)

寫一條全域 memory 讓未來任何 session 都能引用:

```bash
cat > ~/.claude/projects/-Users-coachyang-Documents-Claude-Projects---/memory/aabe_platform_playbook.md <<'EOF'
---
name: AABE 兒少權監督平台之方法論可複用
description: 政策監督 / 議題倡議 / 知識庫平台之 NGO 專屬 playbook
type: methodology
---

當用戶開新政策監督 / 議題倡議 / 知識庫平台 / NGO 平台專案時,先參考:
`/Users/coachyang/Documents/Claude/Projects/兒少權監督平台/docs/PLATFORM_PLAYBOOK.md`

該檔含:
- 雙軸審查框架
- 5 audience 輸出
- 三層 raw/clean/publish 文件治理
- 6 受控詞表 schema
- Wave-based 開發節奏
- Markdown + SQLite + GH Pages 技術堆疊(USD 0/月)
- 12 份治理文件可直接複製

**Why:** 該專案歷時 92 wave 跑通完整 NGO 平台架構,經 8 輪獨立 QA 驗證,可直接重用。

**How to apply:** 收到「新專案 + 政策監督 / 議題」需求時,先建議用戶讀 PLATFORM_PLAYBOOK.md
+ governance/INDEX.md + SESSION_HANDOVER.md 三檔,再決定走 §5.1/5.2/5.3 哪條路徑。
EOF
```

## 七、提問模板(轉移後若新 session 有疑問)

讓新 session 與本平台對話之提問範例:

```
看了 PLATFORM_PLAYBOOK.md,但我新專案是 [X 議題],
不是兒少權,有些細節不一樣:

1. 我沒有 NHRC 對等機制 → 該如何替代?
2. 沒有 CRC 等級的國際公約 → 「過去要求沒兌現」軸該抓什麼?
3. 兒少友善版用不上 → 是否簡化為 4 種輸出?

請給我修改建議。
```

通常本 PLAYBOOK 的 §1.1-1.4 結構性方法論可保留,§3 之檔案選擇性複製即可。

## 八、不要做的事(從 92 wave 學到的教訓)

1. **不要先選 Notion / Super.so** — SaaS 鎖定 + 月費 + 編輯 5,000 條後退化。Markdown + git 完勝。
2. **不要急著移動既有 source 檔** — 會破壞引用網絡(本平台 Wave 67 卡在這,改用「分類索引而非實際移檔」)
3. **不要忘記 rebuild 會沖掉自訂 schema** — 必跑 `migrate_schemas.py`(Wave 91 學到)
4. **不要在沒 spawn 獨立 QA 前繼續加內容** — 自審盲點累積快(每 5-10 wave 跑一次 cold read)
5. **不要 force push** — wave-based 開發每 commit 是檢查點,要保留歷史
6. **不要把 emoji 放在所有公開 HTML** — 跨平台渲染不一致,專業場合不嚴謹(本平台 Wave 80+82 學到)
7. **不要在沒讀 governance/transcript_citation_sop.md 前處理任何訪談**

## 九、本 playbook 之版本

- v1.0 / 2026-04-28 — 初稿,從 兒少權監督平台 Wave 1-92 經驗萃取
- 適用對象:NGO 政策監督平台、議題倡議知識庫、CRC/CEDAW 等公約民間影子報告

如果用得上,記得回報任何「不適用」之處,本檔可持續修訂。
