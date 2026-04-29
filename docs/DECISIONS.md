# Architecture Decision Records — 兩公約總檢討平台

> 重大決策的記錄與理由

---

## ADR-001：fork 自兒少權監督平台而非獨立啟動

**Date**：2026-04-29
**Status**：Accepted

**決定**：採用兒少權監督平台 PLATFORM_PLAYBOOK §5.2「中等：複製核心架構」路徑

**理由**：
- 92 wave 跑通的方法論可直接重用
- governance 12 份治理文件適用任何 NGO 政策監督
- scripts 28 個工具大部分可直接用
- SQLite + Markdown + GH Pages 技術堆疊已驗證 USD 0/月

**取捨**：
- 部分 scripts（fetch_aabe_policy / fetch_crc_co / parse_co_to_md）需改寫
  → 暫標記 .disabled，新增 `two_cov_*.py` 平行
- governance/INDEX 之兒少友善版規定不適用本專案（成人議題）
  → 本專案 5 audience 中刪除「兒少版」、新增「倡議版」

---

## ADR-002：5 audience 改為含「倡議版」、不含「兒少版」

**Date**：2026-04-29
**Status**：Accepted

**決定**：本專案 5 種輸出版本為：
1. 專業版（審查委員、學者）
2. 媒體版（記者、公眾）
3. 立法院版（立委質詢題草稿）
4. **倡議版**（教會、家長團體、其他 NGO）
5. 社群版（IG / FB / Threads）

**理由**：
- 議題抽象度（公約條文、一般性意見、量化分析）對 8-18 歲過於困難
- 平台主要工具性目標是「快速應對與倡議」，倡議版（給合作夥伴）更實用
- 兒少版若日後需求出現可加，但不應為強制版本

**棄用**：兒少權監督平台之 proxy_kid_version_disclosure SOP

---

## ADR-003：立場明確且公開（紅線 9 條）

**Date**：2026-04-29
**Status**：Accepted

**決定**：CLAUDE.md §二、§八、_public/index.html 顯眼處皆放立場聲明

**理由**：
- 政治高度敏感主題，掩飾立場反而引起更多猜忌
- 明確立場讓讀者依其需求自行判斷是否參考本平台
- 立場明確 + 客觀證據優先 = 邏輯上可同時成立（其他立場學者也可同意「條文應均衡援引」）

**取捨**：
- 失去「中立平台」的修辭優勢
- 但獲得「立場誠實 + 方法客觀」的可信度

---

## ADR-004：拒絕 emoji、堅持 SVG（沿用 AABE 偏好）

**Date**：2026-04-29
**Status**：Accepted

**決定**：所有公開 HTML 不使用 emoji，改用 inline SVG 或文字
**例外**：內部 .md 檔、對話回應允許

**理由**：沿用使用者既有偏好（aabe_geo_workflow.md / feedback_visual_svg_over_emoji.md）

---

## ADR-005：「對事不對人」原則

**Date**：2026-04-29
**Status**：Accepted

**決定**：除已被法院判決公開之個人姓名外，本平台不點名特定當事人個人

**理由**：
- 工具化證據資料庫法律敏感性極高，誹謗風險須最小化
- 政策操作的批判標的是「組織 / 政黨 / 政府機關」，不是個別當事人人格
- 已有立法院公報、媒體 archive 等公開職務發言可作量化資料，無需點名個人

**操作**：
- 立委發言：可記錄發言內容 + 政黨 + 選區，不單獨針對個人
- NGO 倡議：記錄組織立場，不針對個別員工 / 志工
- 重大判決：可記錄當事人於判決中已被列名之事實

---

## ADR-006：archive.org 典藏為硬性要求

**Date**：2026-04-29
**Status**：Accepted

**決定**：所有工具化證據必須在登錄前先存至 web.archive.org 並記錄典藏 URL

**理由**：
- 防止登錄方事後刪文造成證據丟失
- 提供獨立第三方時間戳
- 增加查證可信度

**操作**：
```bash
# 登錄前必跑：
curl "https://web.archive.org/save/{原始 URL}"
# 等待 30s → 從 web.archive.org/wayback/available API 確認典藏 URL
```

---

## ADR-007：條文援引異常的客觀判準

**Date**：2026-04-29
**Status**：Accepted

**決定**：定義「條文 A 援引次數 > 條文 B 援引次數 × 10」為「不對稱」標記閾值

**理由**：
- 須有客觀數值判準，不能憑印象指控
- × 10 為足夠寬鬆的容差（< × 10 不標記）
- 配套揭露兩條文重要性是否相同（避免「平等 vs 環境」錯誤類比）

---

## ADR-008：監察院國家人權委員會（NHRC）為「監督對象」而非「合作夥伴」

**Date**：2026-04-29
**Status**：Accepted

**決定**：NHRC 報告作為「政府方資料」處理，民間平台對其評估保持獨立

**理由**：
- NHRC 至今未獲 GANHRI A 級認證（獨立性質疑）
- 委員任命由總統 + 監察院機制，民間視角須獨立
- NHRC 報告不能取代民間影子報告

---

## ADR-009：堅持本機 SQLite + Markdown，不導入 SaaS

**Date**：2026-04-29
**Status**：Accepted（沿用兒少權監督平台 92 wave 驗證）

**決定**：所有資料以 Markdown 為 SSOT、SQLite 為查詢層、git 為版控

**理由**：
- USD 0/月
- 無 SaaS 鎖定
- 政治敏感資料留在本機 + GitHub Pages，不交第三方平台
