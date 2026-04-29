---
name: 國家人權行動計畫追蹤索引
nap_phases: [first_2022_2024, second_2025_2028]
status: framework_only
---

# 國家人權行動計畫（NAP）追蹤總表

## 一、兩期 NAP 概況

| 期別 | 期程 | 核定機關 | 行動數 | 兒少 / 性別 / 宗教比重 | 預算總額 |
|---|---|---|---|---|---|
| 第一期 | 2022-05 ~ 2024-12 | 行政院 | 132 項（待確認）| 兒少 11 / 性別 18 / 宗教 1 | 待查 |
| 第二期 | 2025-01 ~ 2028-12 | 行政院 | 待確認 | 待確認 | 待查 |

## 二、行動項目分類

```
01_legislation         立法 / 修法
02_policy              政策制定
03_education_training  教育與培訓
04_data_collection     數據蒐集統計
05_indicator           指標建立
06_remedy              救濟與補償
07_research            研究調查
08_international       國際對接 / 報告
09_implementation      落實機制
10_review              評估與檢討
```

## 三、追蹤狀態定義

```
not_started      未啟動
in_progress      進行中（具體里程碑可查）
partially_done   部分完成（達成度 30-70%）
done             完成
delayed          延宕（與承諾期程比對）
abandoned        放棄（未明說，但實質停滯 > 18 個月）
ambiguous        進度敘述含糊（典型「持續推動」）
```

## 四、NAP 行動 frontmatter schema

```yaml
---
nap_id: NAP1-018
phase: 1
phase_period: "2022-2024"
action_number: 18
category: 02_policy
short_title: 強化 LGBT 反歧視措施
responsible_agency: 性別平等處
co_referenced: [CO-3-67-sexual_orientation, CO-3-68-gender_identity]
status: in_progress
self_evaluation: "已完成 70%"
nhrc_evaluation: "進度敘述模糊"
civil_society_evaluation: "實質指標下降"
budget_allocated: 8000  # 千元
budget_spent: ?
parallel_actions:
  - related_under_priority_topics: 兒少自殺
  - relative_funding: 1.2x
keywords: [LGBT, 反歧視, 性平]
---
```

## 五、NAP 戰情室視覺化規劃

```
┌────────────────────────────────────────────────────────┐
│ NAP 第一期執行率分布（依議題）                          │
├────────────────────────────────────────────────────────┤
│ 性別議題       ████████████░░░  85% （高度推進）       │
│ LGBT 議題      ██████████░░░░░  72%                    │
│ 兒少自殺       ████░░░░░░░░░░░  31% （低度推進）       │
│ 宗教自由       ██░░░░░░░░░░░░░  18%                    │
│ 移工權益       ███░░░░░░░░░░░░  22%                    │
│ 原住民         ████░░░░░░░░░░░  35%                    │
│ 死刑廢除       ░░░░░░░░░░░░░░░   3%                    │
│ 言論自由       ██░░░░░░░░░░░░░  18%                    │
└────────────────────────────────────────────────────────┘
```

> 此為**示意圖**，待 Wave 11 真實資料匯入後產出實際比例。
> 預期會凸顯**特定議題受重點投入、其他重大人權議題被冷落**的客觀對比。

## 六、SQLite 表 schema

```sql
CREATE TABLE nap_action (
    nap_id TEXT PRIMARY KEY,
    phase INTEGER,
    action_number INTEGER,
    category TEXT,
    short_title TEXT,
    responsible_agency TEXT,
    co_referenced TEXT,            -- JSON array
    status TEXT,
    self_evaluation TEXT,
    nhrc_evaluation TEXT,
    civil_society_evaluation TEXT,
    budget_allocated REAL,
    budget_spent REAL,
    keywords TEXT,
    created_at TEXT,
    updated_at TEXT
);

CREATE TABLE nap_milestone (
    milestone_id INTEGER PRIMARY KEY AUTOINCREMENT,
    nap_id TEXT REFERENCES nap_action(nap_id),
    milestone_date TEXT,
    description TEXT,
    source_url TEXT,
    is_official INTEGER  -- 1=政府公文、0=民間觀察
);
```
