# Governance:文件治理三層 + 6 組受控詞表

> 版本:Wave 62 / 立基於藍圖「兒少人權監督與倡議作業系統:建構以實證為基礎的長期政策監督基礎建設」§文件治理 + MVP 藍圖 §6 標籤體系
>
> 適用範圍:`data/sources/` 之政府文件、CRC 母本、NHRC 報告、AABE 自有倡議資產、學者訪談、案例敘事

---

## 一、三層版本管理(raw / clean / publish)

### 1.1 raw — 原始檔保存

- 路徑:`data/sources/raw/`
- 規則:**禁止任何修改**(包含改檔名、重排頁碼、去浮水印、編輯文字)
- 用途:災害復原、爭議追溯、checksum 比對
- 加密:無(預設;若涉敏感案例敘事須移至 `data/sources/raw/_sensitive/` 並 git-encrypt)

### 1.2 clean — 清洗與切段

- 路徑:`data/sources/clean/`
- 流程:
  1. 從 `raw/` 複製副本(原檔保留)
  2. 去浮水印、修正 OCR 錯誤、頁碼校正
  3. 切段(章/節/條/項/款 為主,另加「議題摘要」一層)
  4. 補欄位 metadata(段號、CRC 條文標註、議題標籤)
- 不對外公開,僅供平台內部編輯查詢

### 1.3 publish — 可檢索可引用

- 路徑:`data/sources/publish/`
- 規則:**經 DPO + 兒少保護專員 + 領域編輯三方核可**始能進入
- 出口:
  - SQLite `passage` 表(全文 + 向量索引)
  - `_public/` HTML 頁面(含 Schema.org JSON-LD)
  - 影子報告自動匯流之來源池

### 1.4 變更管理

- 文件更新(例:CRC 第三次國家報告初稿 → 二稿)**禁止覆蓋舊版**,須建立新 `document_version` 條目
- `document_version.review_status` 欄位記錄當前層級(raw / clean / publish / archived)
- 每次升級層級須在 commit message 註記:`gov(doc): X 升級至 publish (DPO+專員+編輯三方核可 2026-XX-XX)`

---

## 二、檔名規則(對應證據基礎建設 §metadata 標準)

固定格式:

```
[文件類型]_[循環/主題]_[機關]_[日期YYYYMMDD]_[版本]_[語言].[副檔名]
```

範例:
- `CRC3_NR_SFAA_20260421_v02_zh.pdf`
- `CRC2_CO_SFAA_20221228_final_zh.pdf`
- `NAP_EY_20220505_v01_zh.pdf`
- `NHRC_NAPMonitor_20250701_final_zh.pdf`
- `AABE_juvenile-justice_20260323_v01_zh.html`

文件類型代號:
- `CRC1` / `CRC2` / `CRC3` — 第一/二/三次 CRC 國家報告
- `NR` 國家報告本體 / `CO` 結論性意見 / `LOI` 問題清單 / `LOIPR` 問題清單回應
- `NAP` 國家人權行動計畫(`NAPMonitor` = NHRC 監督報告)
- `AABE` 國教行動聯盟自有倡議
- `LAW` 國內法規
- `STAT` 政府統計
- `CASE` 案例(去識別化)
- `INTERVIEW` 訪談(僅 raw 層保留;clean/publish 必須是制度面摘要)

---

## 三、6 組受控詞表(SQLite vocab_* 表)

### 3.1 vocab_issue — 議題詞表

對應 14 PI(PI-01 ~ PI-14)+ 12 cluster(A-L)。新議題須由主編核可後新增,不允許自由命名標籤。

### 3.2 vocab_crc_article — CRC 條文詞表

30 條(從 `crc_article` 表自動同步)。

### 3.3 vocab_agency — 主管機關詞表

13 個(衛福部、教育部、社家署、警政署、移民署、司法院、法務部、NHRC、行政院人權處、通傳會、數發部、國教署、內政部)。
含 aliases JSON 欄位,處理同義詞(例:「衛福部」/「衛生福利部」)。

### 3.4 vocab_problem_tag — 問題判斷標籤

8 個(對應藍圖「問題判斷標籤」機制):
- `NO_DATA` 無具體數據
- `NO_OUTCOME` 無成效評估
- `NO_DISAGG` 無弱勢兒少分組資料
- `NO_CO_RESPONSE` 未回應前次結論性意見
- `FIELD_DISCREPANCY` 與現場經驗不符
- `NO_BUDGET` 無預算說明
- `NO_CROSS_AGENCY` 無跨部會協調機制
- `LAW_ONLY` 只列法規無執行

### 3.5 vocab_quotability — 可引用性詞表

3 個:
- `Q_DIRECT` 可直接引用
- `Q_REWRITE` 需改寫
- `Q_BACKGROUND` 僅供背景

### 3.6 vocab_privacy — 隱私等級詞表

4 個:
- `P_PUBLIC` 公開
- `P_REDACTED` 匿名後可公開
- `P_INTERNAL` 限內部
- `P_SENSITIVE` 極敏感(涉兒少身分、進行中案件、自傷自殺敘事)

---

## 四、tag 變更管理

- 新增 tag 須由**主編核可**(議題)、**領域編輯**(問題標籤)、**DPO**(隱私等級)
- 廢用 tag **不刪除**,僅標記 `deprecated = 1`,保留歷史對照
- 每週一次標籤審查會議(30 分鐘),整理新建 tag 與重命名提案
- 同一段落允許**多重標註**(藍圖 §法規條文標註規則)

---

## 五、與本平台既有治理文件的關聯

| 既有文件 | 本檔之關聯 |
|---|---|
| `child_safeguarding.md` §三點五 | 涉案例敘事之去識別化 → `vocab_privacy` 之 `P_SENSITIVE` 等級強制 |
| `transcript_citation_sop.md` §2.1 | 訪談原稿之公開禁區 → `data/sources/raw/_sensitive/` 路徑 |
| `proxy_kid_version_disclosure.md` | 成人代擬之兒少版透明標記 → `passage` 之 `child_friendly_origin` 欄位 |
| `privacy_policy.md` | 兒少資料外洩例外 → `vocab_privacy` 之 `P_SENSITIVE` 觸發 |
| `rbac.md` | 三層權限 vs 三層文件 → `publish` 層僅主編 + 議題編輯有寫入權 |
| `ai_use_policy.md` | AI 預設只看 redacted → AI 對 `data/sources/raw/_sensitive/` 之存取禁止 |

---

## 六、立即可執行清單

✅ **已完成**(本 wave):
- SQLite vocab_* 6 表已建,初始詞條完整
- `data/sources/{raw,clean,publish}/` 三層目錄結構建立
- `document_version` 表加入 `raw_path` / `clean_path` / `publish_path` / `review_status` 欄位

⚠ **待後續 wave 完成**:
- 既有 `data/sources/` 內檔案逐步遷入三層分類(現存 48 檔需人工或腳本判斷層級)
- 既有議題卡片之標籤對照至 vocab_* 表
- AI use policy 之 raw/clean/publish 存取規則之自動強制(目前靠 SOP)

⚠ **不在本 wave 範圍**(列為 Wave 65+):
- 重新命名 48 個既有 source 檔以符合 `[類型]_[循環]_[機關]_[日期]_[版本]_[語言]` 規則(會破壞既有引用)
- vocab_* 自動填充至所有 passage 紀錄(需大量人工標註)
