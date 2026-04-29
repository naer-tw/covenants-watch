---
name: 兩公約工具化與政黨化證據庫
purpose: 客觀記錄兩公約被選擇性援引的事實
methodology: 量化引用 + 質性對照
status: framework_only
---

# 工具化與政黨化證據資料庫

## 一、核心命題

> 本資料庫的存在不是為了主觀指控，而是為了讓**讀者用客觀數據自行判斷**：
> 兩公約是否被特定政黨、運動團體、政府機關「選擇性援引」？
> 援引哪些條文？避談哪些條文？這種選擇性是否構成「工具化」？

## 二、評估維度（5 個維度）

### 維度 1：條文援引頻率不對稱
- 統計 2009-2026 公開倡議文件、立法院質詢、媒體投書
- 計算每條兩公約條文被援引次數
- **異常指標**：某條文被援引 > 50 次，另一同等位階條文 < 5 次 → 標記不對稱

### 維度 2：原文與援引落差
- 比對援引方詮釋 vs 一般性意見原文
- **異常指標**：宣稱「公約要求」但原文實際未要求 → 標記扭曲

### 維度 3：政黨表決一致性
- 援引兩公約推動 X 法案的政黨，是否在 Y 法案（同條文涵蓋）也推動？
- **異常指標**：高調援引推 LGBT 法案、卻反對援引同條文推宗教自由保障 → 標記政黨化

### 維度 4：政府預算配置對稱性
- 性別平等處 / 心理健康司 / 原民會 / 移民署 / 宗教事務司預算演變
- **異常指標**：條文 A 比條文 B 出現結論性意見批評同等多次，但 A 預算成長 5 倍、B 預算下降 → 標記資源不對稱

### 維度 5：學術與公領域聲量
- Google Scholar 中各條文討論篇數
- 主流媒體（4 大報 + 公視 + 報導者）覆蓋
- **異常指標**：聲量分布與條文重要性嚴重失衡 → 標記注意力不對稱

## 三、證據卡 frontmatter schema

```yaml
---
evidence_id: EV-2024-001
collected_date: 2024-MM-DD
event_date: 2024-MM-DD
collected_by: ...
type: legislative | media | ngo | gov_official | academic | social_media

actor:
  name: 公開組織 / 立委 / 媒體名（不點名個人 不公開）
  affiliation: 政黨 / NGO / 媒體
  role: 提案人 / 倡議者 / 評論者

content:
  full_quote: |
    （原文引用）
  source_url: https://...
  source_archive: web.archive.org/...  # 必須有典藏
  context: 法案審查 / 公聽會 / 投書 / 社群

assessment:
  covenant_articles_cited: [ICCPR Art.26]
  covenant_articles_avoided: [ICCPR Art.18, Art.19]  # 該議題本應同時涉及但未提
  general_comment_distortion: yes/no
  distortion_note: 援引方稱「公約要求 X」，但 GC20 原文是 Y
  political_use_score: 1-5
  asymmetry_dimension: [1, 3]  # 觸發哪些異常維度

cross_reference:
  related_co: [CO-3-67]
  related_pi: [PI-12]
  related_evidence: [EV-2024-002]

privacy:
  contains_personal_info: no
  redaction_applied: no
  source_consent: public_record
---
```

## 四、量化分析腳本（規劃中）

`scripts/analyze_citations.py`（Wave 13+ 實作）：

```bash
# 從立法院公報下載全文 → 全文檢索兩公約條文 → 統計政黨/條文/年度交叉表
python3 scripts/analyze_citations.py --source legislative_yuan --years 2009-2026

# 從媒體 archive 下載 → 同上
python3 scripts/analyze_citations.py --source media --outlets 自由,聯合,中時,公視,報導者

# 產出戰情室
python3 scripts/render_dashboard.py --citation-asymmetry
```

## 五、發布原則

1. **每筆證據必有 archive.org 典藏**（避免事後刪文）
2. **不主觀標註當事人動機**（只記錄行為）
3. **量化指標公開可重現**（讀者可自行計算）
4. **異議申訴機制**：被收錄方可在 72h 內提出修正申請
5. **匿名化規則**：除已公開職務發言外，個人姓名打碼

## 六、防禦操作

由於本資料庫具高度政治敏感性，必須：

- 全部證據附 source_archive（web.archive.org/save/）
- 引用原則：寧可少不可錯
- 每次更新前跑 `scripts/self_qa.sh`
- 每月由 1 名外部編輯（非作者）抽 5% 比對原始檔
- 受指控方提異議時 72 小時內回應，必要時下架重審
