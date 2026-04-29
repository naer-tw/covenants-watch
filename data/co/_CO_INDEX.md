---
name: 兩公約結論性意見索引
covenants: ICCPR + ICESCR
total_reviews: 4
review_years: [2013, 2017, 2022, 2025]
status: framework_only
---

# 兩公約結論性意見（Concluding Observations）總索引

## 一、四次審查總表

| 審查 | 年份 | 民間代表團規模 | 委員人數 | CO 條目數（待確認） | 政府執行率（自評） |
|---|---|---|---|---|---|
| 第一次 | 2013-02 | 130+ NGO | 10 | 81 | （後續 NHRC 評估）|
| 第二次 | 2017-01 | 200+ NGO | 10 | 78 | （後續 NHRC 評估）|
| 第三次 | 2022-05 | 200+ NGO | 10 | 91 | （行政院評估中）|
| 第四次 | 2025-01 | 220+ NGO | 9 | 待整理 | 尚未自評 |

> **資料來源待補**：人權公約施行監督聯盟、法務部「人權大步走」官網
> **填表責任**：Wave 11 國際比較研究時系統性匯入

## 二、CO 編號規則

```
CO-{審查屆數}-{條目編號}-{議題分類}
例：
CO-1-23-死刑     第一次審查第 23 點 死刑廢除議題
CO-3-67-性少數    第三次審查第 67 點 性少數權益
CO-4-12-原民      第四次審查第 12 點 原住民權益
```

## 三、議題分類（vocab_co_topic 受控詞表）

```
01_civil_political          公民政治權概論
02_death_penalty            死刑
03_torture                  酷刑與不當對待
04_freedom_of_speech        言論自由
05_freedom_of_religion      宗教與良心自由
06_freedom_of_assembly      集會結社自由
07_privacy_data             隱私與資料保護
08_fair_trial               公平審判
09_indigenous               原住民權益
10_migrant_workers          移工
11_refugees                 難民
12_minorities               少數群體
13_gender_equality          性別平等
14_sexual_orientation       性傾向 / 性別認同
15_economic_rights          經濟權概論
16_labor                    勞動權
17_social_security          社會保障
18_health                   健康權
19_education                教育權
20_housing                  住房權
21_food                     食物權
22_culture                  文化權
23_environment              環境健康
24_children                 兒童權益
25_disability               身心障礙
26_elderly                  長者權益
27_implementation           施行機制
28_nhri                     國家人權機構
29_data_collection          數據蒐集
30_transitional_justice     轉型正義
```

## 四、CO 卡片 frontmatter schema

每筆 CO 應產生一份 .md，frontmatter 範例：

```yaml
---
co_id: CO-3-67-sexual_orientation
review: 3
review_year: 2022
paragraph_number: 67
topic: 14_sexual_orientation
covenant: ICCPR
article_referenced: [Article 26, Article 23]
chinese_title: 同性婚姻與家庭定義
recommendation_summary: 委員建議政府...
follow_up_status: partially_implemented | implemented | unimplemented | follow_up_pending
gov_response_url: https://...
nhrc_assessment: ...
civil_society_view: ...
keywords: [同婚, 釋字 748, 性別運動]
political_use_score: 0-5  # 被工具化程度評分
selective_citation_count: 整數  # 被援引次數
---
```

## 五、SQLite 表 schema（規劃中，Wave 5 實作）

```sql
CREATE TABLE concluding_observation (
    co_id TEXT PRIMARY KEY,
    review INTEGER NOT NULL,
    review_year INTEGER,
    paragraph_number INTEGER,
    topic TEXT,
    covenant TEXT,         -- ICCPR / ICESCR
    article_referenced TEXT,  -- JSON array
    chinese_title TEXT,
    recommendation_full TEXT,
    follow_up_status TEXT,
    gov_response_url TEXT,
    nhrc_assessment TEXT,
    civil_society_view TEXT,
    political_use_score INTEGER DEFAULT 0,
    selective_citation_count INTEGER DEFAULT 0,
    created_at TEXT,
    updated_at TEXT
);

CREATE TABLE co_citation (
    citation_id INTEGER PRIMARY KEY AUTOINCREMENT,
    co_id TEXT REFERENCES concluding_observation(co_id),
    cited_by_org TEXT,         -- 引用方 NGO/政黨/媒體
    cited_by_person TEXT,
    cited_in_context TEXT,     -- 立法院公報/媒體投書/社群貼文
    cited_date TEXT,
    cited_url TEXT,
    full_quote TEXT,
    has_distortion INTEGER DEFAULT 0,  -- 是否扭曲原文
    distortion_note TEXT
);
```

## 六、優先匯入順序

1. **第四次（2025）審查**結論性意見 → 最新最重要
2. **第一次（2013）13 年回顧**對比 → 看 13 年前要的至今做到沒
3. 第三次、第二次補齊
