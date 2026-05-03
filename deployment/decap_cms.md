---
deployment_target: Decap CMS
status: ready_after_repo_push
admin_url: /admin/
---

# Decap CMS 部署指南

> Decap CMS（前 Netlify CMS）是 git-based 靜態站 CMS,所有編輯透過 GitHub PR 提交,
> 完全免費 + 不需 server + 自動歸檔到 git 歷史。

## 一、快速啟動(部署後)

### Step 1：push 到 GitHub
```bash
gh repo create naer-tw/covenants-watch --public
git push -u origin main
```

### Step 2：啟用 GitHub OAuth
- GitHub repo Settings → Developer settings → OAuth Apps → 新建
- Authorization callback URL: `https://api.netlify.com/auth/done`
- 取 Client ID + Secret

### Step 3：用 Netlify Identity 之 OAuth proxy(免費)
免架 server 最簡方式:
1. 註冊 [Netlify](https://netlify.com) 免費帳號(只用 OAuth proxy,不部署)
2. 站點設定 → Access control → OAuth → Install provider GitHub
3. config.yml 之 backend 改:
   ```yaml
   backend:
     name: github
     repo: naer-tw/covenants-watch
     branch: main
     base_url: https://api.netlify.com  # OAuth proxy
   ```

### Step 4：訪問
```
https://covenants.aabe.org.tw/admin/
```
登入 GitHub 帳號(必須是 repo collaborator)→ 進入編輯後台。

## 二、可編輯的內容(已配置)

| Collection | 用途 | 權限 |
|---|---|---|
| **PI 議題卡** | 16 張,固定架構 | 編輯但不允許新建/刪除 |
| **Trace 議題種子 SQL** | 9 議題 + 未來新增 | 編輯 + 新建 |
| **治理文件** | 12 份 governance/ | 編輯但不允許新建/刪除 |
| **Evidence CSV** | 15 份原始資料 | 唯讀(避免亂改數據) |

## 三、編輯工作流(editorial_workflow 已啟用)

每筆編輯產生一個 PR:
```
編輯 → 草稿(draft)→ 審核中(in_review)→ 已準備發布(ready)→ 發布(published)
```

只有具 repo 寫入權限者可發布。

## 四、常用操作

### 編輯 PI-09 言論自由(範例)
1. 訪問 `/admin/`
2. Collections → PI 議題卡 → 找 PI-09
3. 修改 status / 內文 / keywords
4. Save 草稿 → Submit for review → Publish
5. GitHub Actions 自動觸發 build,5 分鐘內 GH Pages 重新部署

### 新增 trace 議題
1. Collections → Trace 議題種子 SQL → New
2. 輸入 title / status / SQL 內容
3. Save → 自動 commit 到 `data/trace_seed_*.sql`
4. 本地 `pull` 後跑 `sqlite3 data/two_cov.db < data/trace_seed_*.sql`
5. 跑 render → push → GH Pages 部署

## 五、無 server 限制

Decap CMS 完全 client-side:
- 不需自架後端
- 不需資料庫
- 所有變更走 git PR

風險:
- GitHub OAuth client secret 須妥善保管(用 Netlify proxy 規避)
- 同時多人編輯同一檔可能 conflict(git 自會提示)
- 媒體檔案(media_folder)直接進 git,大檔不適合(用 Cloudinary 之類另議)

## 六、與 GitHub Actions 整合

Decap CMS 之 commit 訊息格式為 `cms: create XXX`,build.yml 不會觸發無限迴圈
(我們之 ci commit 訊息含 `[skip ci]`)。

## 七、本地開發測試

如需本地預覽 CMS UI:
```bash
# 1. config.yml 加一行: local_backend: true
# 2. 啟動代理
npx decap-server
# 3. 啟動 http server
cd _public && python3 -m http.server 8765
# 4. 開 http://localhost:8765/admin/
```

## 八、AABE 自家人登入(如不用 OAuth)

備案:純前端密碼閘門(現有 INSIDER_PASS)+ 限本機編輯 git 提交。
適合 1-2 人團隊,無 OAuth 流程。

## 九、相容性

- Decap CMS v3.0+ (本檔載入 `decap-cms@^3.0.0`)
- 需 modern browser(IE11 不支援)
- 中文介面已啟用(locale: zh_Hant)
