---
deployment_target: Tally
status: ready_to_create
forms_count: 4
---

# Tally 表單建立指南（4 類回饋通道）

> 對應 `_public/feedback.html` 之 4 類回饋通道

## 一、Tally 帳號開立

```
1. https://tally.so/ 註冊（免費版即可）
2. EU 託管 + 無 cookie 預設
3. 不啟用 GA / FB pixel
```

## 二、4 個表單規格

### Form 1：A. 引用錯誤訂正（form_id: feedback_citation）

**欄位**：
- 錯誤所在頁面 URL（必填，URL validator）
- 段落號 / 章節（必填）
- 原文錯誤內容（textarea，必填）
- 您主張之正確內容（textarea，必填）
- 支持您主張之原始出處 URL（可多筆）
- 您的姓名（選填）
- 您的 email（必填，verify token）
- 是否同意公開引用您的訂正？（radio）

**回應 SLA**：72 小時

**自動處理**：webhook → SQLite `feedback` 表（待建）

### Form 2：B. 立場分類異議（form_id: feedback_stance）

**欄位**：
- 您的組織名稱（必填）
- 您的組織官網（URL）
- 本平台對您組織之分類描述（textarea）
- 您主張之正確立場（textarea）
- 是否同意公開您的澄清？（radio）
- 異議期內是否暫緩相關量化結果發布？（radio）

**回應 SLA**：14 日

### Form 3：C. 方法論挑戰（form_id: feedback_methodology）

**欄位**：
- 您的學術背景（選填）
- 挑戰之具體章節 / 議題卡編號
- 您主張之方法論問題
- 建議修正方向
- 支持您論述之學術文獻 DOI / URL

**回應 SLA**：30 日

### Form 4：D. 外部審查邀請（form_id: feedback_review）

**欄位**：
- 您的姓名 + 學術機構
- 願意擔任之審查類型（A 方法論 / B 法律 / **C 反對立場**）
- 是否同意公開您的審查意見摘要？
- 期待之審查報酬（依國科會學者顧問費標準）

**回應 SLA**：5 個工作天

## 三、嵌入 _public/feedback.html

```html
<!-- 取代現有 placeholder -->
<iframe data-tally-src="https://tally.so/embed/{form_id}?alignLeft=1"
        loading="lazy" width="100%" height="600" frameborder="0">
</iframe>
<script src="https://tally.so/widgets/embed.js"></script>
```

## 四、Webhook 設定（可選）

```
Tally Settings → Integrations → Webhook URL
→ 連到自建 endpoint（須有 server）
→ 或先用 Email Notification（免 server）
```

## 五、隱私聲明

加 `_public/feedback.html` 顯眼處：
- Tally 為 EU 託管之表單服務
- 本平台不收集 IP 位址
- email 僅用於回應，不轉作其他用途
- 14 日後若無回覆視為撤回
