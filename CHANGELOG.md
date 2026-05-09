# Changelog

> 重大版本變更紀錄(由 commit log 整理)。完整 git 歷史:`git log --oneline`。

## [v0.2-beta] — 2026-05-08

### 後端 4 層完整上線(Wave 120-127)
- L1 客戶端搜尋:Fuse.js + 568 條目
- L2 公開 API:7 endpoint(CC BY-SA 4.0)
- L3 GitHub Actions CI/CD
- L4 Decap CMS 編輯後台

### 前端動態化(Wave 128-148)
- 文件資料庫:11 種 filter 串接 db(屆別 / 公約 / 文件類型 / 議題 / 提出單位 / 條文 / 採納狀態 / 排序 / 分頁)
- 16 PI 議題卡:注入動態 actors / events 段落
- trace 議題首頁:21 議題 + 4 分類 filter
- laws 法律首頁:6 部 + 時間軸 + filter
- actors 行動者目錄:107 位 + 11 類型 filter

### 資料層大幅擴充(Wave 132-152)
- events: 141 → **390**(+249, 含 80+ 影子報告 / 立法 / CO 援引 / 司法判決 等)
- 行動者 events 覆蓋:14 個 → **98 個 ≥ 3 筆**(達 92%)
- 0 筆 actor:22 → **0**(達 100% 實證覆蓋)
- 立法院援引(legislative_citation):0 → **23 筆**
- ≥ 5 筆 actor:0 → **13 個**

### Bug 修補(Wave 142-155)
- 文件資料庫之採納狀態 filter:`is_positive_outcome` 加入 timeline.json
- 公約條文 filter 正規化:支援 `ICCPR §18` / `§18` / `Art.18` / `18` / `ICCPR-18`
- broken links 修補:4 → 0(coming-soon stub)
- CI build pipeline:加 4 個 render/inject step,修「PI HTML rebuild 覆蓋注入」之順序問題
- 主頁過時數字統一:9 議題 → 21 議題,141 events → 390 events

### 文檔(Wave 156a-b)
- 新增 `README.md`(11 sections, 9 層架構表)
- 新增 `CONTRIBUTING.md`(三類貢獻管道 + 開發環境)
- 新增 `.github/ISSUE_TEMPLATE/`(訂正 / bug / feature)
- 新增 `_public/404.html`(自訂 404 頁)
- 新增 `CHANGELOG.md`

### 三表填充(Wave 156)
- `concluding_observation`: 0 → **80** 筆(4 屆累計關鍵段次,含廢死 / CAT / §22 集會 / 移工 / 原民 / 兒少自殺)
- `nap_action`: 0 → **90** 筆(NAP I 60 + NAP II 30,含主辦機關 + 預算 + 民間評語)
- `law_amendment`: 7 → **15** 筆(性平法 2011/2018/2024 三次 / 學輔法 2024 / 自殺防治法 2024 校園篇 等)
- coverage.json totals 加入 CO + NAP + legislative_citation 計數
- about.html 即時統計加 CO 段次 + NAP 行動兩欄
- self_qa: 82 pass / 0 fail

## [v0.1] — 2026-04-30

### 平台骨架建立
- 16 PI 議題卡(4 區塊分類)
- 因果鏈 trace 系統(actor / event / causal_link / outcome_indicator 四元結構)
- 5 audience 影子報告
- AABE design system v1.0(雙公約色帶)
- 軟閘門 AABE / 1234

### 治理文件
- 12 份 governance(AI 政策 / 兒少保護 / 內容 SOP / 隱私 / RBAC 等)
- 5 條 Steelman 紅線

### 基礎建設
- SQLite + Markdown + GitHub Pages($0/月)
- 自動化 build pipeline
- 公開 API + JSON / CC BY-SA 4.0

---

## 維護慣例

- 每個 Wave = 1 個目標 + 1 個 commit(原則上)
- 重大版本(v0.X)= 多個 Wave 之集大成
- 內容訂正即時更新,於 commit log 留痕
- 公開 release: 對外 NGO / 媒體 / 立委 知會時打 git tag
