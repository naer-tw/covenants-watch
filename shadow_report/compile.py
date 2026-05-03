#!/usr/bin/env python3
"""
影子報告編譯（兩公約版，5 audience 自動匯流）

Usage:
    python3 shadow_report/compile.py --audience professional --out build/professional.md
    python3 shadow_report/compile.py --audience all  # 5 種版本一次產出
    python3 shadow_report/compile.py --check          # 驗證所需檔案齊全
"""
from __future__ import annotations
import argparse
import re
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PI_DIR = ROOT / "data" / "policy_issues"
BUILD_DIR = ROOT / "shadow_report" / "build"

AUDIENCES = ["professional", "media", "advocacy", "legislative", "social"]

AUDIENCE_HEADER = {
    "professional": "兩公約施行總檢討民間影子報告（專業版）",
    "media": "兩公約施行 16 年總檢討（媒體摘要版）",
    "advocacy": "兩公約議題倡議速查包（家長團體 / 教會 / NGO 用）",
    "legislative": "兩公約議題立法院質詢題草稿（給立委辦公室）",
    "social": "兩公約 16 年（社群版 140 字 + 圖卡腳本）",
}


def load_pi_card(pi_id: str) -> tuple[dict, str]:
    """讀取一張 PI 卡片"""
    matches = list(PI_DIR.glob(f"{pi_id}_*.md"))
    if not matches:
        return {}, ""
    text = matches[0].read_text(encoding="utf-8")
    fm_match = re.match(r"^---\n(.*?)\n---\n(.*)", text, re.DOTALL)
    if not fm_match:
        return {}, text
    fm_text = fm_match.group(1)
    body = fm_match.group(2)
    fm = {}
    for line in fm_text.splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            fm[k.strip()] = v.strip()
    return fm, body


def extract_section(body: str, section_marker: str) -> str:
    """擷取 markdown 之某 section（如『## 摘要』）"""
    pattern = rf"{re.escape(section_marker)}.*?(?=\n## |\Z)"
    m = re.search(pattern, body, re.DOTALL)
    return m.group(0).strip() if m else ""


def group_pi_by_block(pis: list[str]) -> dict[str, list[tuple[str, str]]]:
    """依 frontmatter 之 block 分群"""
    by_block: dict[str, list[tuple[str, str]]] = {}
    for pi_id in pis:
        fm, _ = load_pi_card(pi_id)
        if not fm:
            continue
        block = fm.get("block", "?")
        title = fm.get("title", "")
        by_block.setdefault(block, []).append((pi_id, title))
    return by_block


BLOCK_NAMES = {
    "A_overall_review": "A · 整體檢視",
    "B_nap_progress": "B · NAP 進程",
    "C_international_comparison": "C · 國際比較",
    "D_political_use_evidence": "D · 政治運用之證據",
}


def compile_professional(pis: list[str]) -> str:
    """專業版：完整 + 條文號 + GC + 統計"""
    out = [f"# {AUDIENCE_HEADER['professional']}", ""]
    out.append(f"> 版本：v0.2-skeleton｜更新：{datetime.now().date()}")
    out.append(f"> 涵蓋議題：{len(pis)} 張 PI 卡")
    out.append("")
    for pi_id in pis:
        fm, body = load_pi_card(pi_id)
        if not fm:
            continue
        out.append(f"\n## {pi_id} {fm.get('title', '')}")
        out.append(f"\n*狀態：{fm.get('status', '')}｜涵蓋公約：{fm.get('covenant', '')}*\n")
        # 抓「## 摘要」段落（前 1200 字）
        summary = extract_section(body, "## 摘要")
        out.append(summary[:1200] if summary else "（待補摘要）")
    out.append("\n\n---\n\n## 立場聲明\n本平台支持兩公約原始普世人權精神，反對工具化與政黨化。")
    return "\n".join(out)


def compile_media(pis: list[str]) -> str:
    """媒體版：1500 字、先講結論、可直接引用"""
    out = [f"# {AUDIENCE_HEADER['media']}", ""]
    out.append(f"> 更新:{datetime.now().date()}｜涵蓋:{len(pis)} 張 PI 卡｜可直接引用,請註明出處 covenants.aabe.org.tw")
    out.append("")
    out.append("## 核心訊息(可作為標題)")
    out.append("> 兩公約施行 16 年,部分條文被高頻援引、部分條文被選擇性忽視。本平台用四維客觀資料(NAP 執行率、條文援引頻率、第三方人權指標、立法院公報量化),檢驗此援引分布,不預設立場。")
    out.append("")
    out.append("## 5 個可直接引用之數據錨點")
    out.append("1. **RSF 新聞自由指數**:Taiwan 從 47 名(2013)→ 24 名(2025),亞洲第 1。但 2022 RSF 改採新方法論,跨年度比較須註記。")
    out.append("2. **Freedom House 公民自由分項**:93-94 分穩定 9 年(2017-2025),2026 公民自由(Civil Liberties)子分項首次下降 1 分(60→59),為值得追蹤之早期訊號。")
    out.append("3. **NAP 第一期(2022-2024)** 已結束,民間 CovenantsWatch 2022 出版時即提出執行率不透明之疑慮;政府第二期 NAP(2025-2028)規劃時程,仍未對第一期做完整自評。")
    out.append("4. **兒少自殺率**:15-19 歲族群 2018-2024 上升至 7.0/十萬,高於 OECD 平均 6.5(z=3.12 outlier)— ICESCR §12 健康權之觀察點。")
    out.append("5. **條文援引不對稱**:立法院公報 2009-2026 兩公約援引,§19(言論)+§26(不歧視)合計超過總援引 60%;§18(宗教)、§22(集會)、ICESCR §13-3(父母教育選擇權)合計不足 5%。")
    out.append("")
    out.append("## 16 PI 議題卡 · 四大區塊")
    by_block = group_pi_by_block(pis)
    for blk_key, blk_label in BLOCK_NAMES.items():
        items = by_block.get(blk_key, [])
        if not items:
            continue
        out.append(f"\n### {blk_label}({len(items)} PI)")
        for pi_id, title in items:
            out.append(f"- **{pi_id}** {title}")
    out.append("")
    out.append("## 媒體聯絡 · 平台立場")
    out.append("- 本平台公開 API(JSON / CSV / SQLite):https://covenants.aabe.org.tw/api/")
    out.append("- 立場聲明 / 紅線:https://covenants.aabe.org.tw/about.html")
    out.append("- 研究方法論:https://covenants.aabe.org.tw/methodology.html")
    out.append("- 全平台搜尋(278 筆索引):https://covenants.aabe.org.tw/search.html")
    out.append("")
    out.append("## 引用建議格式")
    out.append("> 國教行動聯盟(AABE)兩公約監督平台,《兩公約施行 16 年總體檢討》,2026,https://covenants.aabe.org.tw/")
    return "\n".join(out)


def compile_advocacy(pis: list[str]) -> str:
    """倡議版:給家長團體、教會、其他 NGO 之速查 + 反論模板 + 16 PI 速查表"""
    out = [f"# {AUDIENCE_HEADER['advocacy']}", ""]
    out.append(f"> 更新:{datetime.now().date()}｜涵蓋:{len(pis)} 張 PI 卡")
    out.append("")
    out.append("## 一、最常被誤用的 4 個法律邏輯(辨識指引)")
    out.append("1. **援引兩公約但未標 GC 段落號** — 主張「兩公約要求 X」之文宣,若未標明 General Comment 段號,通常為「援引者個人詮釋」,非條約原文。")
    out.append("2. **將條文 A 用來吞掉條文 B** — 例如以 ICCPR §26(不歧視)凌駕於 ICCPR §18(宗教自由),但二者為同等位階,聯合國人權事務委員會 GC22 §11 明示宗教自由之核心不可被「平衡」。")
    out.append("3. **混淆「公約原文」與「一般性意見」** — GC 由委員會制定,屬詮釋指引而非條約文,各國司法機關可拒絕跟隨;台灣司法院亦未具拘束力之裁定。")
    out.append("4. **以「進步詮釋」覆蓋父母教育選擇權** — ICESCR §13-3 明文保障父母依其信念選擇宗教與道德教育,GC13 §28 進一步強調此為核心權利。")
    out.append("")
    out.append("## 二、5 個立場明確之關鍵條文(附 GC + 段號)")
    out.append("- **ICCPR §18** 思想良心宗教自由 — GC22(1993),特別 §3、§8、§11 之核心保障")
    out.append("- **ICCPR §19** 言論自由 — GC34(2011),三要件:法律明確、合法目的、必要與比例")
    out.append("- **ICCPR §22** 結社自由 — GC10 + 工會權之最低標準")
    out.append("- **ICCPR §26** 不歧視 — GC18(1989),平等保護但不延伸到強制信念之同質化")
    out.append("- **ICESCR §13-3** 父母教育選擇權 — GC13(1999)§28、§30,含「依其信念之宗教與道德教育」")
    out.append("")
    out.append("## 三、可援引之國際判例(對照組)")
    out.append("- **Hosanna-Tabor v EEOC**(565 U.S. 171, 2012)— 美國最高法院確立宗教團體之雇用自治(ministerial exception)")
    out.append("- **303 Creative LLC v Elenis**(600 U.S. 570, 2023)— 言論自由凌駕反歧視法之具體應用")
    out.append("- **Mahmoud v Taylor**(605 U.S., 2025-06-27)— 父母依宗教信念請求子女不參與特定課程之保護")
    out.append("- **Eweida v UK**(ECHR 48420/10, 2013)— 工作場所宗教表達之歐洲標準")
    out.append("- **Lautsi v Italy**(ECHR 30814/06, 2011 GC)— 公立學校懸掛宗教象徵之合法性")
    out.append("")
    out.append("## 四、雙面 Steelman 反論模板")
    out.append("當對方主張「條文 X 要求 Y」時,可依下列順序回應:")
    out.append("1. **要求 GC 段號** — 「請問是哪一條 General Comment 之第幾段?」(若對方答不出,主張站不住腳)")
    out.append("2. **回援同位階條文** — 例如對方援 §26,你可援 §18 並指出 GC22 §11 之核心保障")
    out.append("3. **指出國際判例反例** — 例如援 Hosanna-Tabor 反例平衡性過度延伸")
    out.append("4. **要求平衡執行** — 「兩公約 22 條核心條文應均衡執行,而非選擇性援引」")
    out.append("")
    out.append("## 五、16 PI 速查表(可直接引用)")
    for pi_id in pis:
        fm, _ = load_pi_card(pi_id)
        if not fm:
            continue
        title = fm.get("title", "")
        keywords = fm.get("keywords", "")
        out.append(f"- **{pi_id}** {title}")
        if keywords:
            out.append(f"  關鍵字:{keywords}")
    out.append("")
    out.append("## 六、行動工具(可下載)")
    out.append("- 公文模板(寄行政院 / 教育部之 NAP 進度查詢):待 v0.3 發布")
    out.append("- 公聽會發言稿模板(立法院教文 / 司法委員會):待 v0.3 發布")
    out.append("- 雙面對等議題卡(可作為媒體投書之資料卡):16 PI 全部已上線")
    out.append("")
    out.append("## 七、平台速查資源")
    out.append("- 16 PI 議題卡:https://covenants.aabe.org.tw/issues/")
    out.append("- 因果鏈追溯(actor / event / causal_link):https://covenants.aabe.org.tw/trace/")
    out.append("- 法律修法歷程(6 部核心法):https://covenants.aabe.org.tw/laws/")
    out.append("- 全平台搜尋(278 筆索引):https://covenants.aabe.org.tw/search.html")
    out.append("- 平台立場 / 紅線:https://covenants.aabe.org.tw/about.html")
    out.append("- 研究方法論:https://covenants.aabe.org.tw/methodology.html")
    out.append("")
    out.append("## 八、AABE 立場聲明")
    out.append("本平台支持兩公約原始普世人權精神,反對任何條文之選擇性援引或政黨工具化。")
    out.append("我們承諾雙面 Steelman 之客觀檢驗 — 若資料顯示我方論點站不住腳,平台將公開更正。")
    return "\n".join(out)


def compile_legislative(pis: list[str]) -> str:
    """立法院版:質詢題草稿 + 預期回覆框架 + 法源清單 + 16 PI 質詢角度"""
    out = [f"# {AUDIENCE_HEADER['legislative']}", ""]
    out.append(f"> 更新:{datetime.now().date()}｜涵蓋:{len(pis)} 張 PI 卡｜本草稿可直接拷貝至質詢稿")
    out.append("")
    out.append("## 一、總質詢時建議引言(15 秒版)")
    out.append("> 「兩公約施行至今 16 年,累計四屆國際審查與兩期 NAP。但條文援引顯著不對稱,部分核心條文被選擇性忽視。本席以下質詢,聚焦於均衡執行之實質指標。」")
    out.append("")
    out.append("## 二、分機關質詢題草稿(共 18 題)")
    out.append("")
    out.append("### A. 對行政院 / 法務部(主政機關)")
    out.append("1. 第四次兩公約國際審查(2025)結論性意見發布日期、後續執行時程,以及由哪一機關擔任跨部會協調?")
    out.append("2. NAP 第一期(2022-2024)執行率自評,可否提供分項數據(經濟、社會、文化、公民、政治五大類)?")
    out.append("3. 政府如何確保兩公約 22 條核心條文之**均衡執行**?可否提供條文援引頻率之內部統計?")
    out.append("4. 第二期 NAP(2025-2028)新增之承諾,與第一期未達標之承諾如何銜接?")
    out.append("")
    out.append("### B. 對監察院 / NHRC(獨立監督)")
    out.append("1. NHRC 是否已申請 GANHRI A 級認證?預計時程?目前獨立性是否符合巴黎原則?")
    out.append("2. NHRC 監督報告之政府回覆率與實質採納率,過去 4 年資料?")
    out.append("3. NHRC 預算與人員編制是否足以履行《巴黎原則》要求之四大職能(調查、教育、政策建議、申訴)?")
    out.append("4. NHRC 與監察院本部之分工界線,是否存在功能重疊或互相推諉?")
    out.append("")
    out.append("### C. 對教育部(108 課綱)")
    out.append("1. 108 課綱「人權公約」單元中,兩公約 22 條核心條文之呈現比例?是否所有條文均納入教材?")
    out.append("2. 學校宗教活動(Art.18 + Art.13-3 父母選擇權)之教師訓練內容,可否提供當年訓練手冊?")
    out.append("3. 高中公民與社會領綱中之兩公約敘事,是否經過國際標準之外部審查?")
    out.append("")
    out.append("### D. 對 NCC(言論自由監管)")
    out.append("1. 過去 14 年處分案件中,符合 GC34 三要件(法律明確性、合法目的、必要與比例)之比例?")
    out.append("2. NCC 處分對「政治反對意見」與「政治支持意見」之比例,是否存在不對稱?")
    out.append("3. RSF 新聞自由指數 2025 排名 24(亞洲第 1),但 2026 Freedom House 公民自由首次下降 1 分,主管機關之解讀?")
    out.append("")
    out.append("### E. 對衛福部 / 健康權")
    out.append("1. 兒少自殺率 15-19 歲 2024 達 7.0/十萬,高於 OECD 平均 6.5(z=3.12),ICESCR §12 健康權之具體因應?")
    out.append("2. 兒少自殺防治預算,過去 5 年逐年編列數字?執行率?")
    out.append("3. 學生輔導法施行 12 年(2014-2026),學校輔導員數量是否達法定人數比例?")
    out.append("")
    out.append("## 三、預期回覆框架(備好反問題)")
    out.append("- 政府常見回覆 1:「本部已盡力執行 / 已逐年改善」→ 反問:「請提供分項數據,而非整體敘述」")
    out.append("- 政府常見回覆 2:「資料蒐集中 / 待第四次審查後評估」→ 反問:「過去 16 年累計資料為何?」")
    out.append("- 政府常見回覆 3:「兩公約已內國法化,本部依法行政」→ 反問:「請說明 22 條條文之執行優先順序與其依據」")
    out.append("")
    out.append("## 四、可援引之法源清單")
    out.append("- 《兩公約施行法》(2009-04-22 公布,2009-12-10 施行)")
    out.append("- 《人權公約之國家義務》:聯合國人權事務委員會 GC1-37(ICCPR)+ ICESCR Committee GC1-26")
    out.append("- 《巴黎原則》(UN GA Res 48/134, 1993):NHRC 獨立性標準")
    out.append("- 《結論性意見》:第一屆(2013)、第二屆(2017)、第三屆(2022)累計 250+ 點")
    out.append("- RSF World Press Freedom Index 2013-2025 / Freedom House 2017-2026")
    out.append("")
    out.append("## 五、16 PI 議題卡 · 質詢角度速查")
    by_block = group_pi_by_block(pis)
    for blk_key, blk_label in BLOCK_NAMES.items():
        items = by_block.get(blk_key, [])
        if not items:
            continue
        out.append(f"\n### {blk_label}")
        for pi_id, title in items:
            out.append(f"- **{pi_id}** {title}")
    out.append("")
    out.append("## 六、資料下載 / 引用")
    out.append("- 16 PI 議題卡 HTML:https://covenants.aabe.org.tw/issues/")
    out.append("- 公開 API(JSON/CSV/SQLite):https://covenants.aabe.org.tw/api/")
    out.append("- 立法院公報量化資料(PI-13 原始檔):https://covenants.aabe.org.tw/api/laws.json")
    return "\n".join(out)


def compile_social(pis: list[str]) -> str:
    """社群版:8 條 tweet + 圖卡腳本詳述 + hashtag 策略"""
    out = [f"# {AUDIENCE_HEADER['social']}", ""]
    out.append(f"> 更新:{datetime.now().date()}｜每篇 ≤140 字、可直接發布(Twitter/X / Threads / LinkedIn)")
    out.append("")
    out.append("## A. 整體檢視(2 篇)")
    out.append("")
    out.append("**Tweet 01 — 開場(140字)**")
    out.append("> 兩公約在台施行 16 年,4 屆審查累計逾 250 條結論性意見。本平台以四維客觀資料(NAP 執行率、條文援引頻率、第三方人權指標、立法院公報量化)檢視:哪些做到、哪些被忘、哪些被選擇性援引?#兩公約 #人權 #國教盟")
    out.append("")
    out.append("**Tweet 02 — 16 PI 速覽(135字)**")
    out.append("> 16 張議題卡分四區塊:A 總體檢討、B NAP 進程、C 國際比較、D 政治運用之證據。每張卡標示優先級 P0-P3 + 證據完備度狀態,雙面 Steelman 並陳。立場明確、客觀證據優先。https://covenants.aabe.org.tw/issues/ #雙面論證")
    out.append("")
    out.append("## B. 國際比較(2 篇)")
    out.append("")
    out.append("**Tweet 03 — 條文同等位階(138字)**")
    out.append("> 第 18 條(宗教自由)與第 26 條(不歧視)是兩公約**同等位階**條文。不該把後者拿來吞掉前者。聯合國人權事務委員會 GC22 §11 明示宗教自由之核心保障不可被「平衡」。本平台以 9 條法源 + 美國最高法院 3 案論證。#宗教自由 #ICCPR")
    out.append("")
    out.append("**Tweet 04 — 第三方指標(140字)**")
    out.append("> Taiwan RSF 新聞自由指數:47 名(2013)→ 24 名(2025)亞洲第 1。但 2026 Freedom House 公民自由(Civil Liberties)首次下降 1 分(60→59)。兩個第三方指標的微妙差異,值得追蹤。早期訊號不可忽視。#新聞自由 #FreedomHouse")
    out.append("")
    out.append("## C. NAP 進程(2 篇)")
    out.append("")
    out.append("**Tweet 05 — NAP 第一期(135字)**")
    out.append("> 第一期國家人權行動計畫(2022-2024)已結束,但分項執行率自評至今未公布。民間 CovenantsWatch 2022 出版時已提出疑慮。第二期 NAP(2025-2028)規劃前,應對第一期做完整可驗證之自評。#NAP #人權行動計畫")
    out.append("")
    out.append("**Tweet 06 — NHRC 獨立性(138字)**")
    out.append("> 監察院國家人權委員會(NHRC)成立 4 年,GANHRI A 級認證仍未到位。《巴黎原則》四大職能(調查、教育、政策建議、申訴)是否完整?預算與人員編制是否足夠?獨立性是否符合國際標準?https://covenants.aabe.org.tw/issues/PI-07.html #NHRC")
    out.append("")
    out.append("## D. 政治運用證據(2 篇)")
    out.append("")
    out.append("**Tweet 07 — 援引不對稱(140字)**")
    out.append("> 立法院公報 2009-2026 兩公約援引:§19(言論)+§26(不歧視)合計超過 60%;§18(宗教)、§22(集會)、ICESCR §13-3(父母教育選擇權)合計不足 5%。22 條核心條文未均衡執行。是否為政治運用?#兩公約 #立法院公報")
    out.append("")
    out.append("**Tweet 08 — 兒少自殺率(138字)**")
    out.append("> 兒少自殺率 15-19 歲族群 2024 達 7.0/十萬,高於 OECD 平均 6.5(z=3.12 outlier)。ICESCR §12 健康權之觀察點。學生輔導法施行 12 年,輔導員數量是否達法定比例?政府之具體因應?#兒少自殺 #健康權")
    out.append("")
    out.append("## 圖卡腳本(IG / FB / Threads · 9:16 + 1:1 雙版)")
    out.append("")
    out.append("**圖 1:四區塊地圖(主圖,1:1 1080×1080)**")
    out.append("- 標題:「兩公約 16 PI 議題地圖」")
    out.append("- 配色:雙公約色帶(深棕 #5D3A1A + 深酒紅 #5C1A1B)")
    out.append("- 內容:A/B/C/D 四象限,每區塊放 PI 編號 + 一行摘要")
    out.append("- 末行:「→ covenants.aabe.org.tw/issues/」")
    out.append("")
    out.append("**圖 2:RSF 13 年走勢線(數據圖)**")
    out.append("- 標題:「Taiwan 新聞自由 13 年(2013-2025)」")
    out.append("- 配色:單色線(深酒紅)+ 2022 方法論變更虛線標註")
    out.append("- 註腳:「2022 RSF 改變方法論,跨年度比較須註記」")
    out.append("")
    out.append("**圖 3:Steelman 雙面對等示意(立場圖)**")
    out.append("- 標題:「雙面 Steelman:對等強度論證」")
    out.append("- 左:A 派論點(深棕底 + 白字)")
    out.append("- 右:B 派論點(深酒紅底 + 白字)")
    out.append("- 中央:本平台立場(黃金 #8B6F50)+ 紅線提示")
    out.append("")
    out.append("**圖 4:條文援引不對稱柱狀圖**")
    out.append("- 標題:「立法院 16 年條文援引頻率」")
    out.append("- X 軸:22 條核心條文 / Y 軸:援引次數")
    out.append("- 高頻條文(>100 次):亮朱紅 / 低頻(<10 次):灰")
    out.append("")
    out.append("## Hashtag 策略")
    out.append("- **核心**:#兩公約 #人權 #國教盟 #ICCPR #ICESCR")
    out.append("- **議題標籤**:#宗教自由 #言論自由 #兒少自殺 #健康權 #NAP")
    out.append("- **方法論**:#雙面論證 #Steelman #客觀證據")
    out.append("- **時事連動**:依當週政治事件動態加入,但避免黨派標籤")
    out.append("")
    out.append("## 發布節奏建議")
    out.append("- 週一:整體檢視類(Tweet 01-02)")
    out.append("- 週三:議題深度(Tweet 03-08 輪播)")
    out.append("- 週五:圖卡 + 連結到完整 PI 卡")
    out.append("- 月底:Threads 長串(可串 4-8 篇)總結當月")
    return "\n".join(out)


COMPILERS = {
    "professional": compile_professional,
    "media": compile_media,
    "advocacy": compile_advocacy,
    "legislative": compile_legislative,
    "social": compile_social,
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--audience", choices=AUDIENCES + ["all"], default="all")
    parser.add_argument("--out", type=str, help="輸出路徑（單一 audience 用）")
    parser.add_argument("--check", action="store_true", help="僅檢查 PI 檔案是否齊全")
    args = parser.parse_args()

    pis = sorted(p.name.split("_")[0] for p in PI_DIR.glob("PI-*.md"))
    print(f"找到 {len(pis)} 張 PI 卡：{pis}")

    if args.check:
        if len(pis) >= 16:
            print("✓ 16 PI 框架齊全")
            return 0
        print(f"⚠ 僅 {len(pis)} 張 < 16")
        return 1

    BUILD_DIR.mkdir(parents=True, exist_ok=True)

    audiences = AUDIENCES if args.audience == "all" else [args.audience]
    for aud in audiences:
        out_path = Path(args.out) if args.out and args.audience != "all" else BUILD_DIR / f"shadow_report_{aud}.md"
        content = COMPILERS[aud](pis)
        out_path.write_text(content, encoding="utf-8")
        print(f"  ✓ {aud:12} → {out_path} ({len(content)} chars)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
