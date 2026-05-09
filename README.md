# 兩公約監督平台 · Two Covenants Watch Taiwan

> **Live**: <https://covenants.aabe.org.tw/> · **GitHub**: <https://github.com/naer-tw/covenants-watch>
> **Maintainer**: 國教行動聯盟(AABE)Alliance for the Advancement of Basic Education
> **License**: 程式碼 BSD-3 · 資料 [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/)
> **Status**: v0.2-beta(2026-05 民間影子報告版)· 預計 2026-Q3 對外開放

---

## 平台宗旨

聚焦 ICCPR / ICESCR 兩公約於 2009 年通過《兩公約施行法》後 16 年(2009-2026)之施行歷程。
以 16 張結構化議題卡 + 21 議題因果鏈 + 6 部核心法律修法歷程,作為四屆國際審查之客觀證據庫。

**立場聲明**:支持兩公約原始普世人權精神,反對任何條文之選擇性援引或政黨工具化。
承諾雙面 Steelman 之客觀檢驗 — 若資料顯示我方論點站不住腳,平台將公開更正。

## 即時統計(動態自 [api/coverage.json](https://covenants.aabe.org.tw/api/coverage.json))

| 維度 | 數量 |
|---|---|
| Policy Issues (PI) 議題卡 | 16 |
| 因果鏈議題 (trace) | 21 |
| 行動者 (actors) | 107(NGO 39 / 政府 27 / 法院 9 / 國際委員 9 / 立委 6 / 其他 17)|
| 事件 (events) | 390(影子報告 80+ / CO 援引 / 立法 / 政府回應 / 司法判決 / 倡議行動 / 結果指標)|
| 因果連結 (causal_link) | 74(含反證 + 並列原因 + 鏈長警告) |
| 結果指標 (outcome_indicator) | 33 |
| 核心法律 + 修法 | 6 + 7+ amendments |
| 全平台搜尋索引 | 568 條目(Fuse.js) |
| 影子報告 (5 audience) | professional / advocacy / legislative / media / social |

## 平台 9 層架構

| 層 | 路徑 | 內容 |
|---|---|---|
| **L0 主頁** | `/` | 文件資料庫(8 種文件類型 × 4 屆 × 2 公約 × 21 議題 × 107 提出單位 filter)|
| **L1 議題卡** | `/issues/PI-{01-16}.html` | 16 PI 之 markdown render + db 動態關聯段 |
| **L2 因果鏈** | `/trace/{slug}.html` + `/actors/` | 21 議題 × 107 行動者 |
| **L3 法律** | `/laws/{slug}.html` + 時間軸 | 6 部 + amendment delta |
| **L4 影子報告** | `/shadow_reports/{audience}.html` | 5 audience(專業 / 倡議 / 立委 / 媒體 / 社群)|
| **L5 視覺化** | `/dashboards/` | 4 張 Chart.js(RSF / Freedom House / 兒少自殺率 / 條文援引)|
| **L6 透明度** | `/agenda_transparency.html` + `/about.html` | z-score outlier 動態 + 即時統計 |
| **L7 搜尋** | `/search.html` | Fuse.js 客戶端模糊搜尋 568 條目 |
| **L8 公開 API** | `/api/{index,pi,trace,laws,timeline,coverage,search-index}.json` | CC BY-SA 4.0 / 7 endpoint |
| **L9 自家人預覽** | `/login.html` + `insider-gate.js` | AABE 軟閘門(2026-Q3 公開上線後移除)|

## 自動化 Pipeline(GitHub Actions)

每次 push 至 `main`,完整 build & deploy:

```
md → SQLite (md_to_db)
   → render PI HTML  (×16)
   → render trace HTML (×21) + trace index
   → render law HTML (×6) + laws index + actors index
   → inject PI relations (動態 events/actors 段)
   → recompile shadow report (×5 audience)
   → build search-index (568 條目)
   → export 7 API JSON
   → article coverage scan (z-score outlier)
   → emoji enforcement (對外頁面 SVG only)
   → self_qa (82 pass / 0 fail)
   → upload-pages-artifact → deploy-pages
   → IndexNow ping
```

## 資料來源

### 第一手資料
- 法務部 / 行政院公報 / 各部會公開資料
- 立法院公報 (2009-2026)
- 司法院釋字 / 113 憲判系列
- 監察院國家人權委員會 (NHRC) 監督報告
- 4 屆國際審查結論性意見 (2013 / 2017 / 2022 / 2025)

### 第三方人權指標
- RSF World Press Freedom Index 2013-2025
- Freedom House 2017-2026
- OECD 兒少自殺率
- WHO FCTC

### 國際法源
- ICCPR / ICESCR 條約原文
- UN Human Rights Committee General Comments (GC18 / GC22 / GC24 / GC34)
- UN ICESCR Committee General Comments (GC13 / GC14)
- 巴黎原則 (UN GA Res 48/134, 1993)

### 國際判例
- Hosanna-Tabor v EEOC (565 U.S. 171, 2012)
- Eweida v UK (ECHR 48420/10, 2013)
- 303 Creative LLC v Elenis (600 U.S. 570, 2023)
- Mahmoud v Taylor (605 U.S., 2025-06-27)
- Yoon and Choi v Korea (UN HRC 2007)

## 本地開發

```bash
git clone https://github.com/naer-tw/covenants-watch.git
cd covenants-watch
python3 scripts/self_qa.sh                    # 全平台 QA(82 pass / 0 fail)
python3 scripts/two_cov_md_to_db.py           # MD → SQLite
python3 scripts/two_cov_render_trace.py --all # 重生全部 trace HTML
python3 scripts/two_cov_inject_pi_relations.py # 注入 PI 關聯段

# 本地預覽
cd _public && python3 -m http.server 8765
# 開 http://localhost:8765/(會跳 login.html,輸入 AABE / 1234)
```

## Decap CMS(自家人編輯後台)

- URL: `/admin/`(目前需 GitHub OAuth 設定後啟用)
- 4 collections: PI(16 張) / trace seeds / governance / evidence(唯讀)
- 編輯流程: editorial_workflow(草稿 → 審核 → 發布)
- 部署文件: [`deployment/decap_cms.md`](deployment/decap_cms.md)

## 治理(Governance)

12 份治理文件於 [`governance/`](governance/):

- `INDEX.md` 索引
- `ai_use_policy.md` AI 使用政策
- `child_safeguarding.md` 兒少保護
- `content_sop.md` 內容 SOP
- `document_governance.md` 文件治理
- `file_naming.md` 檔案命名
- `privacy_policy.md` 隱私政策
- `rbac.md` 權限角色
- `transcript_citation_sop.md` 引用 SOP

## 雙面 Steelman 立場

平台之 5 條紅線(於 [`about.html`](https://covenants.aabe.org.tw/about.html)):

1. **脈絡 not 責任** — 因果鏈用於描述,不用於歸罪
2. **counter_evidence 必填** — 任何因果連結必須附反證考量
3. **chain_depth ≤ 3** — 避免過長推理鏈造成因果誇張
4. **正向 / 負向 parity** — 不選擇性記錄
5. **statement 與 accountability 分離** — 立場聲明歸立場,責任歸司法

## 引用建議

> 國教行動聯盟(AABE)兩公約監督平台,《兩公約施行 16 年總體檢討》,2026,
> https://covenants.aabe.org.tw/

## 連絡

- Email: contact@aabe.org.tw
- GitHub Issues: <https://github.com/naer-tw/covenants-watch/issues>
- 內容回饋 / 訂正: <https://covenants.aabe.org.tw/feedback.html>

---

© 2026 國教行動聯盟(AABE)· 程式碼 BSD-3 · 資料 CC BY-SA 4.0
