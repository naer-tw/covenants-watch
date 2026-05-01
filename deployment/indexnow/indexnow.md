---
deployment_target: IndexNow
status: ready_to_deploy_after_dns
api_key: 41565caff1994461bfbbb0aaadd9c0cc
---

# IndexNow 部署（兩公約平台版）

> 沿用 AABE 既有 IndexNow key（與其他 NAER 子站共用）。
> DNS 設定後即可啟用。

## 一、IndexNow 簡介

- 微軟主導之搜尋引擎即時索引協議
- Bing / Yandex / Seznam 接受
- 免費、無 API 限額
- 一個 ping 即通知多個搜尋引擎

## 二、部署步驟

### Step 1：在站根放 key 驗證檔
```bash
echo "41565caff1994461bfbbb0aaadd9c0cc" > _public/41565caff1994461bfbbb0aaadd9c0cc.txt
```

### Step 2：發新文章後 ping
```bash
curl "https://api.indexnow.org/indexnow?url=https://covenants.aabe.org.tw/issues/PI-09.html&key=41565caff1994461bfbbb0aaadd9c0cc"
```

### Step 3：批次 ping（多 URL）
```bash
curl -X POST 'https://api.indexnow.org/indexnow' \
  -H 'Content-Type: application/json' \
  -d '{
    "host": "covenants.aabe.org.tw",
    "key": "41565caff1994461bfbbb0aaadd9c0cc",
    "urlList": [
      "https://covenants.aabe.org.tw/",
      "https://covenants.aabe.org.tw/issues/PI-01.html",
      ...
    ]
  }'
```

## 三、整合進部署 SOP

新文章發布或重大更新後：
```bash
bash scripts/two_cov_indexnow_ping.sh
```

（須建立此腳本，沿用 AABE deploy 工作流之模式）

## 四、與其他搜尋引擎之關係

- Google Search Console：須**手動**提交（不接受 IndexNow）
- Bing Webmaster Tools：可從 GSC 一鍵 import
- Baidu / Naver：依國別需求另外處理

## 五、DNS 啟用前的限制

**IndexNow 須在 DNS 完成設定後才能 ping**：
- key 檔案必須能透過 https://covenants.aabe.org.tw/{key}.txt 讀取
- 否則 IndexNow 拒絕請求

**血淚教訓**（沿用 AABE GEO workflow）：
DNS 未設前不要 push CNAME，會打掛現網。
