# 檔名與版本規則

## 一、固定檔名格式

`[文件類型]_[循環/主題]_[機關/單位]_[日期YYYYMMDD]_[版本]_[語言].[副檔名]`

## 二、範例

| 類型 | 範例 |
|---|---|
| CRC 國家報告 | `CRC3_NR_SFAA_20260421_v02_zh.pdf` |
| 結論性意見 | `CRC2_CO_SFAA_20221228_final_zh.pdf` |
| 國家人權行動計畫 | `NAP_EY_20220505_v01_zh.pdf` |
| NHRC 監督報告 | `NHRC_NAPMonitor_20250701_final_zh.pdf` |
| 國教盟倡議 | `CAMPAIGN_NAER_juvenile-justice_20260323_v01_zh.html` |
| 媒體報導 | `MEDIA_LTN_etomidate-newtaipei_20251210_zh.html` |
| 法規 | `LAW_MOJ_CRPS_20240101_amended_zh.pdf` |

## 三、版本管理三層

| 層級 | 用途 | 規則 |
|---|---|---|
| `raw/` | 原始檔保存 | 不修改、不重命名、checksum 驗核 |
| `clean/` | 去浮水印、切頁、頁碼校正、段落切分 | 衍生自 raw,可重新生成 |
| `publish/` | 對外可引用版本 | 經主編簽核,進入 SQLite `document_version` |

## 四、文件更新規則

- **禁止覆蓋舊版**:第三次國家報告初稿 → 二稿 → 定稿,各為獨立 `document_version`
- 在 `document_version.is_current` 標記目前現行版,舊版改為 `0`
- 引用時必須明確版本(例:CRC3 二稿第 X 段,而非「國家報告第 X 段」)

## 五、SQLite checksum 驗核

```
sha256sum data/raw/CRC3_NR_SFAA_20260421_v02_zh.pdf > .checksum
```

每次匯入新版本時對照 checksum,確認檔案未被竄改。
