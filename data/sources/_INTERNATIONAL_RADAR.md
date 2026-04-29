---
name: 國際資料來源雷達清單
purpose: PI-04/08/09/10/11 國際比較研究之資料源索引
adapted_from: ~/clawd/skills/international-radar
last_updated: 2026-04-30
---

# 國際資料來源雷達（兩公約 C 區國際比較專用）

> 改編自 `~/clawd/skills/international-radar`，本平台特化加入兩公約議題篩選。

## 一、國際組織原始來源

| 組織 | 網址 | 監測重點 | 對應 PI |
|---|---|---|---|
| **UN OHCHR** | ohchr.org | ICCPR/ICESCR 全文 + GC 全集 | PI-08/09/10/11 |
| UN HRC Treaty Body Database | tbinternet.ohchr.org | 各國 CO + Concluding Observations | PI-04 |
| UN OHCHR Special Rapporteur on Freedom of Religion | ohchr.org/srfreedomreligion | Art.18 原始材料 | PI-08 |
| UN Special Rapporteur on Freedom of Expression | ohchr.org/srexpression | Art.19 原始材料 | PI-09 |
| WHO | who.int | 健康權 GC14 | PI-11 |
| UNESCO | unesco.org | 教育權 + 宗教教育 | PI-08/10 |

## 二、區域人權法庭

| 法庭 | 網址 | 對應 PI |
|---|---|---|
| **歐洲人權法院（ECtHR）** | hudoc.echr.coe.int | Art.18/19/26 判例（Lautsi/SAS/Eweida）| PI-08/09/10 |
| 美洲人權法院 | corteidh.or.cr | 拉美對照 | PI-04 |
| 非洲人權與人民權利法院 | african-court.org | 全球比較 | PI-04 |

## 三、國家最高法院判例

| 國家 | 系統 | 對應 PI |
|---|---|---|
| 美國 | supremecourt.gov | Hosanna-Tabor / 303 Creative / Mahmoud | PI-08/10 |
| 英國 | supremecourt.uk | 1998 HRA 援引案例 | PI-04 |
| 德國 | bundesverfassungsgericht.de | 基本法第 4 條（宗教）+ 6 條（家庭）| PI-08/10 |
| 加拿大 | scc-csc.ca | Charter Section 2 / 15 對應 | PI-08/10 |

## 四、新聞自由 / 言論自由指數

| 來源 | 網址 | 用途 | 對應 PI |
|---|---|---|---|
| RSF World Press Freedom Index | rsf.org | 14 年指標（**已部分匯入**）| PI-09 |
| Freedom House Freedom in the World | freedomhouse.org | 政治權利 + 公民自由（**已部分匯入**）| PI-09 |
| Freedom House Freedom on the Net | freedomhouse.org | 網路言論專項 | PI-09 |
| V-Dem Institute | v-dem.net | 民主指標 | PI-09 |

## 五、人權施行法 / NHRI 對照

| 國家 | 機構 | 對應 PI |
|---|---|---|
| 韓國 NHRCK | humanrights.go.kr | NHRI A 級對照 | PI-07 |
| 菲律賓 CHR | chr.gov.ph | NHRI A 級對照 | PI-07 |
| 印度 NHRC | nhrc.nic.in | NHRI A 級對照 | PI-07 |
| 日本 | （無獨立 NHRI）| 對照組 | PI-07 |

## 六、學術資料庫

| 來源 | 用途 | 對應 PI |
|---|---|---|
| HeinOnline | 國際法判例 | PI-08/10 |
| Westlaw / Lexis | 美國判例 | PI-08/10 |
| Google Scholar | 跨領域 | 全部 |
| SSRN | 法學 working paper | 全部 |

## 七、台灣對應（用於對比）

| 來源 | 用途 |
|---|---|
| 司法院法學資料檢索系統 | judicial.gov.tw | 台灣法院引用兩公約之判決 |
| 法務部「人權大步走」 | humanrights.moj.gov.tw | 4 屆 CO + 2 期 NAP |
| 監察院國家人權委員會 | nhrc.cy.gov.tw | 監督報告 |
| CovenantsWatch | covenantswatch.org.tw | 民間影子報告 |
| 立法院法律系統 | lis.ly.gov.tw | 公報全文 |

## 八、學術期刊（兩公約相關）

| 期刊 | 適用主題 |
|---|---|
| Human Rights Quarterly | 人權法理論 |
| Journal of Human Rights Practice | NHRI 與 NAP |
| International Journal of Constitutional Law | 條文詮釋光譜 |
| Religion and Human Rights | Art.18 |
| Journal of Media Law | Art.19 |

## 九、Felo AI 搜尋整合

可用 `~/clawd/tools/felo-search.sh "..."` 即時搜尋。
- API key: `~/.clawdbot/secrets/felo-api-key`
- 用法：每次需查具體條文 / 案例 / 統計時即時搜尋 + archive.org 典藏

## 十、執行 SOP

每月跑一次：
1. 各組織新發布 CO / GC 之自動偵測
2. 重要判例摘要 → SQLite `evidence` 表
3. 將摘要翻譯為中文 + 台灣對應分析
4. 寫入 PI 卡之 §steelman 或 §case 段落
