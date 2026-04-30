---
deployment_target: Datawrapper
status: ready_to_create
csv_inventory: 15 ready-to-import
---

# Datawrapper 視覺化建立指南

> 本平台 evidence/ 已備 15 份 CSV，全部設計為 Datawrapper-ready 結構。
> 本指南列出 8 個建議圖表 + 嵌入 HTML 程序。

## 一、Datawrapper 帳號開立

```
1. 註冊 https://www.datawrapper.de/
2. Free plan 即可（每月 10,000 views）
3. 上傳 CSV 從 data/evidence/*.csv
```

## 二、建議建立的 8 張圖表

### 圖表 1：RSF 新聞自由指數 13 年走勢
- **CSV**：`data/evidence/rsf_taiwan_2013_2025.csv`
- **圖型**：Line chart
- **注意**：必須加註「2022 RSF 方法論大幅改版，2022 前後不可直接比較」之 annotation
- **對應 PI**：PI-09

### 圖表 2：Freedom House 評分 2017-2026
- **CSV**：`data/evidence/freedom_house_taiwan_2017_2026.csv`
- **圖型**：Stacked bar（總分 / 政治權利 / 公民自由）
- **重點**：2026 公民自由首次下降 1 分
- **對應 PI**：PI-09

### 圖表 3：亞太區域 RSF 對照
- **CSV**：`data/evidence/rsf_asia_pacific_comparison.csv`
- **圖型**：Multi-line chart（5 國 × 年份）
- **重點**：Taiwan 上升非區域同步，但**不歸因任何單一原因**
- **對應 PI**：PI-09

### 圖表 4：青少年自殺率 2018-2025
- **CSV**：`data/evidence/youth_suicide_15to19.csv`（已拆口徑）
- **圖型**：Line chart 加註資料口徑
- **重點**：2023 高於 OECD 6.5（單點比較）
- **對應 PI**：PI-11

### 圖表 5：13 年來 15 條未兌現 CO 狀態分布
- **CSV**：`data/evidence/co_review1_unfulfilled.csv`
- **圖型**：Pie chart（done 2 / partial 6 / pending 3 / abandoned 4）
- **對應 PI**：PI-02

### 圖表 6：6 國施行法對照
- **CSV**：`data/evidence/treaty_implementation_comparison.csv`
- **圖型**：Comparison table
- **重點**：台灣施行法之獨特性
- **對應 PI**：PI-04

### 圖表 7：NHRC 巴黎原則對照組
- **CSV**：`data/evidence/nhrc_paris_principles.csv`
- **圖型**：Comparison table（4 國 NHRI A 級 vs 台灣未認證）
- **對應 PI**：PI-07

### 圖表 8：22 條核心條文盤點 + outliers
- **CSV**：自動產出於 `data/evidence/article_coverage_report.md`
- **圖型**：Bar chart 排序（含均值 + 2σ 線）
- **對應**：透明度聲明 `_AGENDA_TRANSPARENCY.md`

## 三、嵌入 HTML 程序

```bash
# Datawrapper 提供 iframe embed code
# 加入 _public/dashboards/index.html 對應位置
# 替換現有的 .embed-frame placeholder
```

範例 iframe：
```html
<iframe src="https://datawrapper.dwcdn.net/XXXX/1/" width="100%" height="420" frameborder="0"></iframe>
```

## 四、發布前檢核

- [ ] 每張圖表附完整資料來源 + 警語（如方法論變更）
- [ ] 不在圖表上做主觀詮釋（純資料）
- [ ] 標題使用「資料」而非「成效 / 退步」等價值字眼
- [ ] CSV 連同圖表公開供獨立重做

## 五、CC BY-SA 4.0 授權

所有圖表標明：
> 資料源：兩公約施行總檢討平台（CC BY-SA 4.0）
> 互動圖表：Datawrapper（自由使用）
