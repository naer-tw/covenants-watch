# 貢獻指南 · Contributing Guide

> 兩公約監督平台歡迎挑戰、訂正與補強。本指南說明如何貢獻。

## 三類貢獻管道

### A. 內容回饋(訂正 / 異議申訴)

如您發現:
- 引用錯誤
- 條文誤讀
- 量化方法錯誤
- 您的組織 / 立場被錯誤呈現

請循以下管道之一:

1. **GitHub Issue**: <https://github.com/naer-tw/covenants-watch/issues/new>
   - 標題格式:`[訂正] PI-XX 第 N 段 — 簡述`
   - 內容:原文 + 應為 + 出處
2. **Email**: contact@aabe.org.tw(主旨「兩公約平台訂正」)
3. **平台回饋頁**: <https://covenants.aabe.org.tw/feedback.html>

我們承諾:**72 小時內回覆**,並於下次部署時公開更正記錄(見 commit log)。

### B. 資料補強(影子報告 / 國際判例 / 統計數據)

歡迎民間團體 / 學者貢獻:
- 民間影子報告章節(對應 16 PI 或 21 議題)
- 國際比較案例
- 第三方統計數據(附來源)

提交方式:
- Pull Request: 修改 `data/policy_issues/PI-XX_*.md` 或 `data/sources/*.csv`
- 直接寄稿至 contact@aabe.org.tw

**雙人編碼制**:任何資料變更必須由 ≥ 2 名研究員獨立檢核,於 PR description 標明。

### C. 程式碼貢獻(腳本 / UI 改進)

#### 開發環境

```bash
git clone https://github.com/naer-tw/covenants-watch.git
cd covenants-watch

# 跑 QA(必須 0 fail)
bash scripts/self_qa.sh

# 跑全 build pipeline(模擬 CI)
python3 scripts/two_cov_md_to_db.py
python3 scripts/two_cov_render_trace.py --all
python3 scripts/two_cov_render_trace_index.py
python3 scripts/two_cov_render_law.py --all
python3 scripts/two_cov_render_laws_index.py
python3 scripts/two_cov_render_actors.py
python3 scripts/two_cov_inject_pi_relations.py
python3 shadow_report/compile.py --audience all
python3 scripts/two_cov_build_search_index.py
python3 scripts/two_cov_export_api.py
python3 scripts/two_cov_inject_gate.py
python3 scripts/two_cov_build_sitemap.py

# 本地預覽
cd _public && python3 -m http.server 8765
# 開 http://localhost:8765/(輸入 AABE / 1234)
```

#### 編碼規範

- **Python**: stdlib 優先,新依賴須於 PR 說明理由
- **HTML / CSS**: 遵循 [`about.html`](https://covenants.aabe.org.tw/about.html) 之 design system
- **配色**: 使用 CSS 變數(`--brand` / `--aabe-gold` / `--cycle-iccpr` / `--cycle-icescr`)
- **emoji**: 對外 HTML 不用 emoji,改 inline SVG(內部 markdown / 對話 OK)
- **JS**: 客戶端 vanilla JS 優先,避免 bundler

#### PR 規則

1. Branch name: `wave-XXX-{topic}` 或 `fix/{issue}`
2. Commit message:
   - `feat(Wave XXX): ` 新功能
   - `fix(Wave XXX): ` 修 bug
   - `docs(Wave XXX): ` 文檔
   - `refactor(Wave XXX): ` 重構
3. 每個 PR 必須 self_qa 全 PASSED(82+ pass / 0 fail)
4. 任何資料變更附 source URL

## 雙面 Steelman 文化

本平台之內容創作須遵循**雙面對等強度**:

- 觸碰爭議議題時,A 派 / B 派論點之長度、引用數、語氣強度應對等
- 不單方歸因
- 任何因果連結附 `counter_evidence`
- 立場聲明 ≠ 責任歸屬

詳見 [`governance/content_sop.md`](governance/content_sop.md)。

## 資料治理

- 所有原始資料於 `data/sources/raw/`(未清洗)
- 清洗後於 `data/sources/clean/`
- 公開發布於 `data/sources/publish/`(也鏡射至 `_public/api/evidence/`)
- 三層分流確保可追溯

## 安全與隱私

- **個資保護**:不蒐集訪客資料(無 cookie / 無分析)
- **匿名化**:所有 actor 之 `is_anonymized` 欄位記錄是否經匿名化
- **兒少保護**:遵循 [`governance/child_safeguarding.md`](governance/child_safeguarding.md)
- **AI 使用**:遵循 [`governance/ai_use_policy.md`](governance/ai_use_policy.md)

## 授權

- 程式碼:**BSD-3-Clause**
- 資料:**CC BY-SA 4.0**(歡迎複製、修改、商用,須註明出處 + 採用相同授權)

## 聯絡

維護:國教行動聯盟(AABE)
- contact@aabe.org.tw
- <https://aabe.org.tw>
- <https://github.com/naer-tw/covenants-watch>
