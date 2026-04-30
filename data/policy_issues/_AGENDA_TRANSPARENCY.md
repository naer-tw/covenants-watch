---
name: 平台議程透明度聲明
purpose: 顯性化平台關注偏好，回應第四輪 cold read 之要求
last_scan: 2026-04-30
methodology: scripts/two_cov_article_coverage.py
status: published
---

# 平台議程透明度聲明

## 一、為何需要本聲明

第四輪 cold read QA 指出：
> 「凡偏離均值 > 2σ 之條文需在卡片開頭加註『本平台特別關注此條文之理由』，把預設立場顯性化而非偽裝中立。」

本平台採此建議，**主動公開**全 16 PI 中條文提及次數之偏離分析，並對偏離條文逐一說明關注理由。

## 二、最新掃描結果（2026-04-30）

由 `scripts/two_cov_article_coverage.py` 自動掃描全 16 PI 卡 markdown 內容。

### ICCPR（均值 4.56 / 標準差 6.55）

**3 條偏離 > 2σ 之條文**：

| 條文 | 提及次數 | z 分數 | 平台關注理由 |
|---|---:|---:|---|
| **Art.18** 思想良心宗教自由 | 23 | 2.82 | 國教行動聯盟既有立場：保障宗教與良心自由不被吞沒 |
| **Art.26** 不歧視 | 25 | 3.12 | 詮釋光譜核心條文：本平台關注其與 Art.18 / Art.13-3 之衝突詮釋邊界 |

> 註：Art.13 教育權（ICESCR）非 ICCPR 條文，下表分開列。

### ICESCR（均值 1.20 / 標準差 1.52）

| 條文 | 提及次數 | z 分數 | 平台關注理由 |
|---|---:|---:|---|
| **Art.13** 教育權 | 5 | 2.50 | 父母教育選擇權（13-3）為平台關注之延伸；與 ICCPR 18-4 並重 |

## 三、議程聲明

本平台不偽裝中立。**議程偏好已顯性化**：
- 偏向關注「Art.18 / Art.13-3 父母教育選擇權」與「Art.26 不歧視」之衝突邊界詮釋
- 此偏好源自國教行動聯盟之家長立場
- 讀者應據此自行評估資訊取捨

但本平台承諾：
1. 對其他條文（如 Art.6 死刑、Art.27 原民、ICESCR Art.7 勞動權）之低關注度，**不代表這些條文不重要**
2. Wave 90+ 對 22 條核心條文進行**完整缺席率盤點**，使本平台之議程偏好可被獨立驗證
3. 任何結論性詮釋（如 Steelman B）必須以對等強度呈現（含 ICCPR 內生 vs 比較法外溢之區分）

## 四、自我檢核機制

本平台每月跑一次 `two_cov_article_coverage.py`：
- 若某條文 z 分數 > 2σ 且**未在本聲明中說明關注理由**，必須補說明
- 若某條文 z 分數 > 3σ，須評估是否退回 P0_research 重審
- 全部結果歸檔於 `data/evidence/article_coverage_report.md`

## 五、第三方獨立檢核

第三方可重做掃描：
```bash
cd /path/to/平台
python3 scripts/two_cov_article_coverage.py
```

掃描程式採 BSD-3 開源，方法論於本檔公開。

## 六、相關資源

- 報告原始檔：`data/evidence/article_coverage_report.md`
- 掃描腳本：`scripts/two_cov_article_coverage.py`
- 本聲明：`data/policy_issues/_AGENDA_TRANSPARENCY.md`
