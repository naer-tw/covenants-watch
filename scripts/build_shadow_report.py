#!/usr/bin/env python3
"""
build_shadow_report.py — 把 master_template + 12 cluster 草稿拼接成可發布的影子報告。

輸出兩種格式:
1. 單一拼接 Markdown:shadow_report/build/Alternative_Report_v0.4.md
2. Standalone HTML(含 CSS,可瀏覽器 Cmd+P 列印 PDF):shadow_report/build/Alternative_Report_v0.4.html

依賴:
- pandoc(已裝):用於 md→HTML
- 真 PDF 輸出需另裝 wkhtmltopdf 或 weasyprint(README 中說明)

用法:
    python3 scripts/build_shadow_report.py                 # 拼接 + HTML
    python3 scripts/build_shadow_report.py --audience kid  # 兒少版
    python3 scripts/build_shadow_report.py --no-html       # 只拼 md,不轉 HTML
"""
from __future__ import annotations

import argparse
import datetime as dt
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SR = ROOT / "shadow_report"
BUILD = SR / "build"

CLUSTER_ORDER = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L"]
CLUSTER_NAMES = {
    "A": "一般執行措施", "B": "兒童之定義", "C": "一般原則",
    "D": "公民權利與自由", "E": "暴力侵害兒童",
    "F": "家庭環境與替代照顧", "G": "身心障礙、健康與福利",
    "H": "教育、休閒與文化", "I": "特別保護措施",
    "J": "任擇議定書", "K": "兒少權利與環境(GC26)", "L": "數位環境(GC25)",
}


def build_markdown(audience: str, lang: str = "zh") -> str:
    """拼接 master_template 摘要 + 12 cluster 內容。"""
    today = dt.date.today().isoformat()
    parts = [
        f"# 兒少人權監督與倡議作業系統 — 替代報告草稿(Alternative Report)\n",
        f"\n**版本**:v0.4 草稿 / **產製日**:{today} / **受眾**:{audience}\n",
        "\n**提交機構**:國教行動聯盟(AABE)+ 合作 NGO 平台\n",
        "\n**對應審查**:CRC 第三次國家報告審查(2026-11 提出預估)\n",
        "\n---\n\n",
        "## 提交說明\n\n",
        "本報告由國教行動聯盟兒少人權監督平台(`scripts/compile.py` + 14 個議題卡片)自動匯流產出,",
        "經編輯潤飾後提交。所有引用之 CO 段落號(CRC1/CRC2)、NHRC 監督報告(2025-07)、",
        "NHRC 師對生暴力專案報告(2024,委託臺北大學)、政府統計皆可回溯到 [`data/sources/`](../../data/sources/) 之原始 PDF。\n\n",
        "**體例**:Child Rights Connect 2024 新對話結構之 11+1 cluster,每章三段式(現況 → 對國家報告之評論 → 政策建議)。\n\n",
        "**字數限制**:CRC 委員會綜合性報告 ≤10,000 字、主題式 ≤3,000 字 — 中文版本草稿可超出,",
        "提交前由編輯濃縮至上限。\n\n",
        "---\n\n",
        "## 目錄\n\n",
    ]
    # 目錄
    for cl in CLUSTER_ORDER:
        parts.append(f"- Cluster {cl} — {CLUSTER_NAMES[cl]}\n")
    parts.append("\n---\n\n")

    # 各 cluster 內容
    for cl in CLUSTER_ORDER:
        suffix = f"_{lang}" if lang != "zh" else ""
        f = SR / "sections" / f"cluster_{cl}_{audience}{suffix}.md"
        if f.exists():
            parts.append(f.read_text(encoding="utf-8"))
            parts.append("\n\n---\n\n")
        else:
            parts.append(f"# Cluster {cl}:{CLUSTER_NAMES[cl]}\n\n_(本 cluster 暫無內容,先跑 `python3 shadow_report/compile.py --audience {audience}`)_\n\n---\n\n")

    return "".join(parts)


HTML_HEAD = """<!DOCTYPE html>
<html lang="zh-TW">
<head>
<meta charset="UTF-8">
<title>兒少人權監督平台 — 替代報告草稿</title>
<style>
@page { size: A4; margin: 2cm 2.5cm; }
body { font-family: "PingFang TC", "Noto Sans TC", "Microsoft JhengHei", "Hiragino Sans", sans-serif;
       font-size: 11pt; line-height: 1.7; color: #1a1a2e; max-width: 210mm; margin: 0 auto; padding: 20px; }
h1 { font-size: 22pt; border-bottom: 3px solid #2C323C; padding-bottom: 8px; page-break-before: always; }
h1:first-of-type { page-break-before: auto; }
h2 { font-size: 16pt; color: #2C323C; margin-top: 28pt; padding-bottom: 4px; border-bottom: 1px solid #ccc; }
h3 { font-size: 13pt; color: #555770; margin-top: 18pt; }
table { width: 100%; border-collapse: collapse; margin: 12pt 0; font-size: 10pt; page-break-inside: avoid; }
th, td { padding: 6pt 10pt; border: 1px solid #ddd; vertical-align: top; text-align: left; }
th { background: #f5f5f7; font-weight: 600; }
blockquote { border-left: 4px solid #E8734A; padding: 6pt 12pt; margin: 12pt 0; background: #fff8f5; color: #555770; }
ul, ol { padding-left: 24pt; }
li { margin: 4pt 0; }
.footer-cite { margin-top: 36pt; padding-top: 12pt; border-top: 1px solid #ccc; font-size: 9pt; color: #888; }
@media print {
  h1 { page-break-before: always; }
  table, blockquote { page-break-inside: avoid; }
}
</style>
</head>
<body>
"""

HTML_FOOT = """
<div class="footer-cite">
  <p>產製來源:[兒少人權監督與倡議作業系統 (CRW-TW)](https://naer-tw.github.io/policy/)
  · 國教行動聯盟 AABE · 內容採 CC BY 4.0 授權 ·
  原始資料:<code>data/sources/</code> · 自動匯流:<code>scripts/build_shadow_report.py</code></p>
</div>
</body>
</html>
"""


def md_to_html(md_path: Path, html_path: Path) -> bool:
    """用 pandoc 轉 md → 純 body HTML,再用 HTML_HEAD/FOOT 包覆。"""
    try:
        result = subprocess.run(
            ["pandoc", str(md_path), "-f", "markdown", "-t", "html5", "--no-highlight"],
            capture_output=True, text=True, check=True,
        )
        html_body = result.stdout
    except FileNotFoundError:
        print("⚠ pandoc 未安裝 — 跳過 HTML 輸出。安裝:brew install pandoc")
        return False
    except subprocess.CalledProcessError as e:
        print(f"⚠ pandoc 失敗:{e.stderr}")
        return False
    html_path.write_text(HTML_HEAD + html_body + HTML_FOOT, encoding="utf-8")
    return True


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--audience", choices=["professional", "kid", "media", "legislative", "social"], default="professional")
    ap.add_argument("--lang", choices=["zh", "en"], default="zh", help="Wave 81")
    ap.add_argument("--no-html", action="store_true", help="只拼 md,不轉 HTML")
    args = ap.parse_args()

    BUILD.mkdir(parents=True, exist_ok=True)

    md_text = build_markdown(args.audience, args.lang)
    suffix = f"_{args.lang}" if args.lang != "zh" else ""
    md_path = BUILD / f"Alternative_Report_v0.4_{args.audience}{suffix}.md"
    md_path.write_text(md_text, encoding="utf-8")
    wc = len(re.sub(r"\s+", "", md_text))
    print(f"✓ 拼接 Markdown:{md_path.relative_to(ROOT)}({wc:,} 字)")

    if args.no_html:
        return 0

    html_path = BUILD / f"Alternative_Report_v0.4_{args.audience}{suffix}.html"
    if md_to_html(md_path, html_path):
        print(f"✓ 轉 HTML:{html_path.relative_to(ROOT)}")
        print(f"\n下一步(輸出 PDF):")
        print(f"  瀏覽器開啟 {html_path.relative_to(ROOT)} → Cmd+P → 存為 PDF")
        print(f"  或安裝 wkhtmltopdf:brew install wkhtmltopdf,然後跑:")
        print(f"  wkhtmltopdf -O Portrait -s A4 --enable-local-file-access \\")
        print(f"    {html_path.relative_to(ROOT)} {BUILD.relative_to(ROOT)}/Alternative_Report_v0.4_{args.audience}.pdf")

    return 0


if __name__ == "__main__":
    sys.exit(main())
