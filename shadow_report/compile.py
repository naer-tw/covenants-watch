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
    "media": "兩公約施行 16 年總檢討（媒體摘要版 800-1200 字）",
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
        # 抓「## 摘要」段落（前 400 字）
        summary = extract_section(body, "## 摘要")
        out.append(summary[:1200] if summary else "（待補摘要）")
    out.append("\n\n---\n\n## 立場聲明\n本平台支持兩公約原始普世人權精神，反對工具化與政黨化。")
    return "\n".join(out)


def compile_media(pis: list[str]) -> str:
    """媒體版：800-1200 字、先講結論"""
    out = [f"# {AUDIENCE_HEADER['media']}", ""]
    out.append("**核心訊息**：兩公約施行 16 年，部分條文被高頻援引、部分條文被忽視，本平台用客觀資料檢驗此分布，不預設立場。")
    out.append("")
    out.append("**3 大客觀指標**：")
    out.append("- RSF 新聞自由指數：Taiwan 從 47 名（2013）→ 24 名（2025），亞洲第 1")
    out.append("- Freedom House：93-94 分穩定 9 年（2017-2025），2026 公民自由首次下降 1 分")
    out.append("- NAP 第一期（2022-2024）已結束，民間 CovenantsWatch 2022 即提出疑慮")
    out.append("")
    out.append("**16 張 PI 議題卡**涵蓋四大區塊：")
    out.append("1. 兩公約施行 16 年總體檢討")
    out.append("2. 國家人權行動計畫進度")
    out.append("3. 國際比較：原始公約精神 vs 台灣詮釋")
    out.append("4. 援引行為與政策落差客觀檢驗")
    out.append("")
    out.append("詳細議題：https://policy.aabe.org.tw/two-covenants/")
    return "\n".join(out)


def compile_advocacy(pis: list[str]) -> str:
    """倡議版：給家長團體、教會、其他 NGO 之速查包"""
    out = [f"# {AUDIENCE_HEADER['advocacy']}", ""]
    out.append("## 一、最常被誤用的法律邏輯")
    out.append("- 「兩公約要求 X」往往**未被援引方標明 GC 段落號**")
    out.append("- 第 26 條（不歧視）與第 18 條（宗教自由）為**同等位階**")
    out.append("- 一般性意見（GC）之地位**非具有條約法上之約束力**")
    out.append("")
    out.append("## 二、3 個立場明確之關鍵條文")
    out.append("- ICCPR Art.18 — 思想良心宗教自由（一般性意見 22 號）")
    out.append("- ICCPR Art.19 — 言論自由（一般性意見 34 號）")
    out.append("- ICESCR Art.13-3 — 父母教育選擇權（含道德教育，GC13 §28）")
    out.append("")
    out.append("## 三、可援引之國際判例")
    out.append("- Hosanna-Tabor v EEOC（565 U.S. 171, 2012）")
    out.append("- 303 Creative LLC v Elenis（600 U.S. 570, 2023）")
    out.append("- Mahmoud v Taylor（605 U.S., 2025-06-27）")
    out.append("")
    out.append("## 四、平台速查資源")
    out.append("- 16 PI 議題卡：https://policy.aabe.org.tw/two-covenants/")
    out.append("- 平台立場：/about.html")
    out.append("- 研究方法：/methodology.html")
    return "\n".join(out)


def compile_legislative(pis: list[str]) -> str:
    """立法院版：質詢題草稿"""
    out = [f"# {AUDIENCE_HEADER['legislative']}", ""]
    out.append("## 質詢題草稿")
    out.append("")
    out.append("### 對行政院 / 法務部")
    out.append("1. 第四次審查（2025）結論性意見發布日期及執行時程？")
    out.append("2. NAP 第一期（2022-2024）執行率自評，可否提供分項數據？")
    out.append("3. 政府如何確保兩公約 22 條核心條文之**均衡執行**？")
    out.append("")
    out.append("### 對監察院 / NHRC")
    out.append("1. NHRC 是否申請 GANHRI A 級認證？預計時程？")
    out.append("2. NHRC 監督報告之政府回覆率與採納率？")
    out.append("")
    out.append("### 對教育部")
    out.append("1. 108 課綱「人權公約」單元中，22 條核心條文之呈現比例？")
    out.append("2. 學校宗教活動（Art.18 + Art.13-3）之教師訓練內容？")
    out.append("")
    out.append("### 對 NCC")
    out.append("1. 過去 14 年處分案件中，符合 GC34 三要件（法律明確、比例原則、不打壓政治反對意見）之比例？")
    return "\n".join(out)


def compile_social(pis: list[str]) -> str:
    """社群版：140 字 + 圖卡腳本"""
    out = [f"# {AUDIENCE_HEADER['social']}", ""]
    out.append("## 三條核心 Tweet（各 140 字內）")
    out.append("")
    out.append("**Tweet 1**")
    out.append("> 兩公約在台施行 16 年，4 屆審查累計逾 250 條結論性意見。")
    out.append("> 本平台用客觀資料檢視：哪些做到、哪些被忘、哪些被選擇性援引？")
    out.append("> 立場明確、雙面 Steelman、客觀證據優先。 #兩公約 #人權")
    out.append("")
    out.append("**Tweet 2**")
    out.append("> 第 18 條（宗教自由）與第 26 條（不歧視）是兩公約**同等位階**條文。")
    out.append("> 不應該把後者拿來吞掉前者。")
    out.append("> 本平台用 9 條法源（含起草史 + 美國最高法院 3 案）論證。 #宗教自由")
    out.append("")
    out.append("**Tweet 3**")
    out.append("> Taiwan RSF 新聞自由指數：47 名（2013）→ 24 名（2025）亞洲第 1")
    out.append("> 但 Freedom House 公民自由 2026 首次下降 1 分。")
    out.append("> 兩個第三方指標的微妙差異，值得追蹤。")
    out.append("")
    out.append("## 圖卡腳本（IG / FB）")
    out.append("- 圖 1：四區塊圖（A/B/C/D）+ 16 PI 議題地圖")
    out.append("- 圖 2：RSF 13 年走勢線")
    out.append("- 圖 3：Steelman 雙面對等示意（A 派 vs B 派）")
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
