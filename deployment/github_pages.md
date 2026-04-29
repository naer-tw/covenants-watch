---
deployment_target: GitHub Pages
domain_options:
  - policy.aabe.org.tw/two-covenants/  (subpath)
  - covenants.aabe.org.tw  (sub-domain)
status: pending_decision
last_updated: 2026-04-30
---

# GitHub Pages 部署指南

## 一、域名選項（待用戶決策）

### 選項 A：子目錄 `policy.aabe.org.tw/two-covenants/`
- **優點**：與既有國教盟政策站共用 SEO / GEO 累積
- **缺點**：兩公約議題政治敏感，可能影響母站
- **DNS**：無需新增
- **GitHub Pages 設定**：在既有 `naer-tw/policy` repo 之 `/two-covenants/` 子資料夾

### 選項 B：獨立子網域 `covenants.aabe.org.tw`
- **優點**：政治風險隔離；獨立 GA / GSC 追蹤
- **缺點**：須設 CNAME；SEO 需重新累積
- **DNS**：CNAME `covenants.aabe.org.tw` → `naer-tw.github.io`
- **GitHub Pages 設定**：新 repo `naer-tw/two-covenants`

### 選項 C：完全獨立 repo + 過渡期 noindex（推薦）
- 起初部署於新 repo，全頁 `<meta name="robots" content="noindex,nofollow">`
- 內容穩定 + 外部審查通過 + 法律複核完成 後始開放索引
- DNS / repo 結構同 B

## 二、部署 SOP（採選項 C 流程）

```bash
# 1. 在本機初始化（已完成）
cd /Users/coachyang/Documents/Claude/Projects/兩公約總檢討平台
git log --oneline | head -5

# 2. 建立 GitHub repo
gh repo create naer-tw/two-covenants --public --description "兩公約施行總檢討平台"

# 3. 加 remote 並 push（首次）
git remote add origin git@github.com:naer-tw/two-covenants.git
git push -u origin main

# 4. 啟用 GitHub Pages
# Settings → Pages → Source: Deploy from a branch / main / /_public

# 5. 等待 GitHub Actions 部署（約 30 秒）
gh run list --limit 1

# 6. 訪問 https://naer-tw.github.io/two-covenants/ 驗證
curl -I https://naer-tw.github.io/two-covenants/
```

## 三、CNAME 設定（選項 B/C，謹慎）

> **血淚教訓**（沿用 AABE GEO workflow）：DNS 未設前**不可**push CNAME，會打掛現網。

```bash
# Step 1: 先在 DNS provider 設定 CNAME
# covenants.aabe.org.tw  →  naer-tw.github.io
# 等待 DNS 全球傳播（5-30 分鐘）

# Step 2: 驗證
dig covenants.aabe.org.tw +short
# 應顯示 naer-tw.github.io 之 IP

# Step 3: 確認 ✓ 後才 push CNAME
echo "covenants.aabe.org.tw" > _public/CNAME
git add _public/CNAME
git commit -m "feat: enable custom domain covenants.aabe.org.tw"
git push

# Step 4: GitHub Pages Settings → Custom domain 填入 → 啟用 HTTPS
```

## 四、預檢清單（push 前必跑）

```bash
cd /Users/coachyang/Documents/Claude/Projects/兩公約總檢討平台

# 1. self_qa 通過
bash scripts/self_qa.sh 2>&1 | tail -5
# 預期：✓ 63 pass / ⚠ 0 / ✗ 0

# 2. 對外 HTML 無 emoji
python3 <<'EOF'
import re
from pathlib import Path
emoji_re = re.compile(r'[☀-➿\U0001F300-\U0001F9FF⚠]')
fail = sum(1 for f in Path('_public').rglob('*.html') if emoji_re.search(f.read_text()))
print(f"  ✓ 無 emoji 殘留" if fail==0 else f"  ✗ {fail} 個 HTML 含 emoji")
EOF

# 3. 預覽伺服器測試
cd _public && python3 -m http.server 8765 &
sleep 2
curl -s -o /dev/null -w "首頁: %{http_code}\n" http://localhost:8765/
for pi in PI-01 PI-08 PI-10 PI-13 PI-16; do
  curl -s -o /dev/null -w "${pi}: %{http_code}\n" http://localhost:8765/issues/${pi}.html
done
kill %1; cd ..

# 4. internal/ 不可在部署目錄
ls _public/internal 2>&1 | grep -q "No such" && echo "  ✓ internal/ 已隔離" || echo "  ✗ 須清理"

# 5. sync_to_jekyll 過濾 internal/（如使用）
# python3 scripts/sync_to_jekyll.py --filter internal
```

## 五、部署後驗證

```bash
DOMAIN="https://naer-tw.github.io/two-covenants"  # 或 https://covenants.aabe.org.tw

# HTTP 200 全頁
for path in / /about.html /methodology.html /feedback.html /sitemap.xml /llms.txt /robots.txt; do
  status=$(curl -s -o /dev/null -w "%{http_code}" "${DOMAIN}${path}")
  echo "  ${path}: ${status}"
done

# 16 PI 全 200
for pi in PI-01 PI-02 PI-03 PI-04 PI-05 PI-06 PI-07 PI-08 \
          PI-09 PI-10 PI-11 PI-12 PI-13 PI-14 PI-15 PI-16; do
  s=$(curl -s -o /dev/null -w "%{http_code}" "${DOMAIN}/issues/${pi}.html")
  echo "  ${pi}: ${s}"
done
```

## 六、上線後 GEO 整合（沿用 AABE 流程）

```bash
# 1. IndexNow ping
curl "https://api.indexnow.org/indexnow?url=https://covenants.aabe.org.tw/&key=41565caff1994461bfbbb0aaadd9c0cc"

# 2. Google Search Console
# 手動：https://search.google.com/search-console → URL inspection → Request indexing

# 3. Bing Webmaster
# 從 GSC 一鍵 import

# 4. AABE GEO checker
cd /Users/coachyang/Documents/Claude/Projects/瀚瀚/geo-checker
python3 geo_checker.py --check --site https://covenants.aabe.org.tw/
```

## 七、上線時機判準（不要急）

**不要上線**，若：
- self_qa 任何 fail
- 對外 HTML 含 emoji
- 第二輪 cold read QA 未通過
- 法律顧問未複核 PI-09 NCC / PI-13 立委發言相關內容
- 外部審查（含反對立場學者）未啟動

**可以上線**，當：
- 全部 self_qa pass
- 兩輪 cold read QA 修補完成（已達成於 Wave 36）
- 至少 1 篇實證 PI 完整（建議 PI-09，已部分達成）
- 法律顧問書面 OK
- 異議申訴流程確定（feedback.html ✓）

## 八、上線後監測

- 月度跑 `monitor_updates.py` 偵測政府站變動
- 月度跑 `geo_checker.py --check`
- 季度跑 `--ai-test` 評估 AI 引用率
- 每季外部問責委員會抽查 5%
