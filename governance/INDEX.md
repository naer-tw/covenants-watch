# 治理文件索引(Governance INDEX)

> **建立日**:2026-04-26(Wave 39 — QA #8 修法 G)
> **更新日**:2026-04-27(Wave 62 — 加入 document_governance.md)
> **角色**:讓編輯、DPO、兒少保護專員「**何時該翻哪份**」一目了然,並對齊各份文件中的時程數字。

## 一、12 份治理文件總覽

| 順位 | 文件 | 適用情境 | 主要負責人 |
|---:|---|---|---|
| 1 | [`content_sop.md`](content_sop.md) | 任何內容生產(議題卡、影子報告、媒體稿、社群、兒少版)| 主編 |
| 2 | [`child_safeguarding.md`](child_safeguarding.md) | 涉兒少敘事、案例、影像、聲音(含一審未確定案件)| 兒少保護專員 |
| 3 | [`transcript_citation_sop.md`](transcript_citation_sop.md) | 處理訪談 / 公聽會 / 記者會逐字稿 | 主編 + DPO |
| 4 | [`proxy_kid_version_disclosure.md`](proxy_kid_version_disclosure.md) | 議題卡片「兒少版」段落產出與審稿 | 主編 + 兒少審稿小組 |
| 5 | [`ai_use_policy.md`](ai_use_policy.md) | 使用 LLM / Whisper / 任何 AI 工具 | 全員 |
| 6 | [`privacy_policy.md`](privacy_policy.md) | 對外公開隱私政策(個資保護)| DPO |
| 7 | [`rbac.md`](rbac.md) | 角色權限分離(Notion / Super / Tally / SQLite)| DPO + 主編 |
| 8 | [`file_naming.md`](file_naming.md) | 檔名與版本規則 | 全員 |
| 9 | [`document_governance.md`](document_governance.md) | 三層 raw/clean/publish + 6 組受控詞表 | 主編 + DPO |
| 10 | [`wcag_audit_report.md`](wcag_audit_report.md) | WCAG 2.1 AA 稽核結果 | 主編 |
| 11 | [`youth_advisory_sop.md`](youth_advisory_sop.md) | 兒少顧問小組(8 人)組成、招募、議事 SOP | 主編 + 兒少保護專員 |
| 12 | [本檔 INDEX.md](INDEX.md) | 治理文件導讀 | 主編 |

## 二、決策樹:遇到狀況該翻哪份?

### 編輯內容時
```
正在寫議題卡 / 影子報告 / 媒體稿
    ├─ 涉及兒少敘事 / 案例?     → child_safeguarding.md
    ├─ 引用訪談 / 公聽會逐字稿? → transcript_citation_sop.md
    ├─ 寫「兒少版」段落?         → proxy_kid_version_disclosure.md
    ├─ 用 LLM / AI 草擬?          → ai_use_policy.md
    └─ 一般內容流程?              → content_sop.md
```

### 出狀況時(資安事件 / 個資外洩 / 內容下架)
```
發現外洩或誤發布
    ├─ 涉及兒少資料 / 訪談逐字稿 / 案例去識別化破口?
    │     → child_safeguarding.md §七(1h 通知 / 24h DPO 報告 + 對外公告)
    │     → 同時參考 rbac.md §五「敏感資料誤發布」(1h / 24h)
    └─ 一般成人個資外洩?
          → privacy_policy.md §九(24h 通知 / 72h 主管機關 / 7 日公布)
```

### 處理人員權限時
```
新成員加入 / 離職 / 帳號被盜
    → rbac.md §四 撤銷權限(離職 24h 內 / 主編離職 7 日內)
    → rbac.md §五 安全事件處置
```

## 三、時程一覽(統一對齊版,Wave 39 修法 G)

> 三份文件曾各寫不同時程,以下為**統一後**的權威版本:

| 情境 | 通知當事人 | DPO 報告 | 對外公告 | 出處 |
|---|---|---|---|---|
| **兒少資料外洩**(訪談逐字稿、案例破口、兒少個資) | **1 小時** | **24 小時** | **24 小時** | child_safeguarding §七 + rbac §五 |
| **敏感資料誤發布**(編輯失誤誤推) | **1 小時** | **24 小時** | — | rbac §五 |
| **一般成人個資外洩** | **24 小時** | **72 小時** | **7 日** | privacy_policy §九 |
| **帳號被盜** | — | **24 小時** | — | rbac §五 |
| **主編離職 / 成員離職** | — | — | — | rbac §四:24h(成員)/ 7d(主編)撤權 |

> **判斷原則**:若疑似涉及兒少,**從嚴**適用兒少時程;事後若確認非兒少,可放寬。

## 四、跨文件引用關係

```
content_sop ─┬─ 引用 child_safeguarding(兒少內容)
             ├─ 引用 transcript_citation_sop(訪談)
             ├─ 引用 proxy_kid_version_disclosure(兒少版)
             └─ 引用 ai_use_policy(AI 使用)

privacy_policy §九 ─→ child_safeguarding §七(兒少資料外洩例外)
                  ─→ rbac §五(敏感資料誤發布)

transcript_citation_sop §3.1 ─→ scripts/sync_to_jekyll.py(技術強制)
                            §3.2 ─→ scripts/transcribe_audio.sh(倫理提示)
                            §3.3 ─→ scripts/self_qa.sh(直連檢核)
```

## 五、各文件的觸發歷史

| 文件 | 觸發 | 修訂歷史 |
|---|---|---|
| child_safeguarding.md | 平台啟動初版 | 2026-04-25 補「一審未確定案件被告全名」紅線(QA 第一輪 #2)|
| transcript_citation_sop.md | QA 第二輪(Wave 25 後)| 2026-04-26 Wave 39 #1 補技術強制(sync_to_jekyll + transcribe_audio + self_qa)|
| proxy_kid_version_disclosure.md | QA 第二輪 | 「by children, not for children」對齊 |
| privacy_policy.md | 平台啟動 | 2026-04-26 Wave 39 #8 加兒少資料外洩例外 |
| rbac.md | 平台啟動 | — |
| ai_use_policy.md | 平台啟動 | — |
| content_sop.md | 平台啟動 | — |
| file_naming.md | 平台啟動 | — |
| **INDEX.md(本檔)** | 2026-04-26 Wave 39 #8 | — |

## 六、自動化保護總覽

下列由 `scripts/self_qa.sh` 與 `scripts/sync_to_jekyll.py` 強制檢核(若違規,self_qa fail / sync 跳過):

| 檢核 | 來源 SOP | 實作位置 |
|---|---|---|
| 議題卡 / advocacy 不直連原始逐字稿 | transcript_citation_sop §2.1 | self_qa.sh §7 + sync_to_jekyll(`_逐字稿_` glob)|
| `ethics_status: 內部歸檔` 之檔案不出 Jekyll | transcript_citation_sop §3.1 | sync_to_jekyll(ethics_status 過濾)|
| `published: false` 之議題不出 Jekyll | content_sop | sync_to_jekyll(published 過濾)|
| 案例頁不含真實姓名(C-1101 例外:法院判決加害人)| child_safeguarding §3.5 | self_qa.sh §7 |
| 兒少版字數合理(警告 ≤300 字)| proxy_kid_version_disclosure | self_qa.sh §7 |

## 七、下個 session 接手說明

新治理需求應先檢查本 INDEX 是否已有對應文件,避免新增重複規範。若需修訂時程數字,**必須**:
1. 同步更新本 INDEX 第三節「時程一覽」
2. 更新對應文件的修訂歷史
3. 跑 `bash scripts/self_qa.sh` 確認沒打壞
