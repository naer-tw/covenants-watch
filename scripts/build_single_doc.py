#!/usr/bin/env python3
"""build_single_doc.py — 把任一 markdown 檔(發言稿、倡議檔、議題卡)轉為印刷友善 HTML。

複用 build_shadow_report.py 的 CSS 主題,但只處理單一檔案,不拼接。

用法:
    python3 scripts/build_single_doc.py data/advocacy_actions/A-2026-05_衛福部公聽會發言稿_TBD.md
    python3 scripts/build_single_doc.py data/policy_issues/PI-12_替代照顧與機構安置.md --out /tmp/PI-12.html
    python3 scripts/build_single_doc.py FILE --strip-frontmatter   # 印刷時不顯 YAML 頭
"""
from __future__ import annotations

import argparse
import datetime as dt
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

HTML_HEAD = """<!DOCTYPE html>
<html lang="zh-TW">
<head>
<meta charset="UTF-8">
{noindex}<title>{title}</title>
{schema_jsonld}
<style>
@page { size: A4; margin: 2cm 2.5cm; }
body { font-family: "PingFang TC", "Noto Sans TC", "Microsoft JhengHei", "Hiragino Sans", sans-serif;
       font-size: 11pt; line-height: 1.7; color: #1a1a2e; max-width: 210mm; margin: 0 auto; padding: 20px; }
h1 { font-size: 22pt; border-bottom: 3px solid #2C323C; padding-bottom: 8px; }
h2 { font-size: 16pt; color: #2C323C; margin-top: 28pt; padding-bottom: 4px; border-bottom: 1px solid #ccc; }
h3 { font-size: 13pt; color: #555770; margin-top: 18pt; }
h4 { font-size: 12pt; color: #555770; margin-top: 12pt; }
table { width: 100%; border-collapse: collapse; margin: 12pt 0; font-size: 10pt; page-break-inside: avoid; }
th, td { padding: 6pt 10pt; border: 1px solid #ddd; vertical-align: top; text-align: left; }
th { background: #f5f5f7; font-weight: 600; }
blockquote { border-left: 4px solid #E8734A; padding: 6pt 12pt; margin: 12pt 0; background: #fff8f5; color: #555770; }
strong { color: #2C323C; }
ul, ol { padding-left: 24pt; }
li { margin: 4pt 0; }
code { background: #f5f5f7; padding: 1pt 4pt; border-radius: 3px; font-size: 10pt; }
.footer-cite { margin-top: 36pt; padding-top: 12pt; border-top: 1px solid #ccc; font-size: 9pt; color: #888; }
@media print {
  table, blockquote { page-break-inside: avoid; }
  h2, h3 { page-break-after: avoid; }
}
</style>
</head>
<body>
"""

HTML_FOOT = """
<div class="footer-cite">
  <p>產製日:{date} ·
  來源:<code>{source}</code> ·
  國教行動聯盟兒少人權監督平台 · CC BY 4.0 ·
  自動匯流:<code>scripts/build_single_doc.py</code></p>
</div>
</body>
</html>
"""


def strip_frontmatter(text: str) -> str:
    """剝去 YAML frontmatter(印刷時通常不需要 metadata)。"""
    return re.sub(r"^---\n.*?\n---\n", "", text, count=1, flags=re.DOTALL)


def extract_nhrc_indicators(text: str) -> str:
    """Wave 60:從 frontmatter 抓 nhrc_indicators 欄位,渲染為 HTML 表格。

    對應 MVP 藍圖 §3:每個議題卡片下方顯示 NHRC 對應指標的官方數值與更新日期。
    若 frontmatter 無此欄位則返回空字串。
    """
    m = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    if not m:
        return ""
    fm = m.group(1)
    # 找 nhrc_indicators: 開始的列表(支援 YAML 巢狀)
    block_match = re.search(r"^nhrc_indicators:\s*\n((?:  -.*?\n(?:    .*?\n)*)+)", fm, re.MULTILINE)
    if not block_match:
        return ""
    items_block = block_match.group(1)
    # 拆每一個 - id: ... 的條目
    items = re.split(r"^  - ", items_block, flags=re.MULTILINE)
    rows = []
    for item in items:
        if not item.strip():
            continue
        fields = {}
        for line in item.splitlines():
            line_clean = line.strip()
            if ":" in line_clean and not line_clean.startswith("#"):
                k, _, v = line_clean.partition(":")
                fields[k.strip()] = v.strip().strip('"').strip("'")
        if fields.get("id") or fields.get("name"):
            rows.append(fields)
    if not rows:
        return ""
    # 渲染表格
    html = ['<section class="nhrc-indicators" style="margin: 32px 0; padding: 16px 20px; background: #f0f7ff; border-radius: 8px; border-left: 4px solid #1976d2;">']
    html.append('<h3 style="margin-top: 0; color: #1976d2;">📊 NHRC 對應監測指標(2026-02-04 指標集)</h3>')
    html.append('<table style="width: 100%; border-collapse: collapse; font-size: 13.5px;">')
    html.append('<thead><tr style="background: #e3f2fd;"><th style="padding: 6px 10px; text-align: left;">指標</th><th style="padding: 6px 10px;">最新數值</th><th style="padding: 6px 10px;">日期</th><th style="padding: 6px 10px;">趨勢</th></tr></thead><tbody>')
    trend_icon = {"improving": "🟢 改善", "stable": "🟡 持平", "worsening": "🔴 惡化"}
    for r in rows:
        name = r.get("name", r.get("id", "—"))
        val = r.get("latest_value", "—")
        date = r.get("latest_date", "—")
        trend = trend_icon.get(r.get("trend", ""), r.get("trend", "—"))
        concern = r.get("nhrc_concern", "")
        html.append(f'<tr style="border-top: 1px solid #ddd;"><td style="padding: 6px 10px;">{name}{"<br><small style=\"color:#888\">⚠ " + concern + "</small>" if concern else ""}</td><td style="padding: 6px 10px; font-weight: 600; color: #d32f2f;">{val}</td><td style="padding: 6px 10px; color: #666;">{date}</td><td style="padding: 6px 10px;">{trend}</td></tr>')
    html.append('</tbody></table>')
    html.append('<p style="margin: 8px 0 0; font-size: 11.5px; color: #888;">來源:國家人權委員會兒童權利監測指標集(2026-02-04 發布,239 項) ‧ 平台對接中</p>')
    html.append('</section>')
    return "\n".join(html)


def extract_title(text: str) -> str:
    """從 markdown 取第一個 # 標題作為 HTML <title>。"""
    m = re.search(r"^# (.+?)$", text, re.MULTILINE)
    if m:
        return m.group(1).strip()
    return "兒少人權監督平台"


def build_jsonld(schema_type: str, title: str, source_rel: str) -> str:
    """產生 Schema.org JSON-LD(對應 MVP 藍圖 §5 GEO/SEO 整合)。

    四種類型(對應藍圖):
    - organization:首頁,NGO 類型
    - article:每篇分析,含 citation
    - dataset:每個統計頁,含 license + distribution
    - faqpage:議題卡片底部,6-10 對 Q&A
    """
    import json
    today = dt.date.today().isoformat()
    if schema_type == "organization":
        data = {
            "@context": "https://schema.org",
            "@type": "NGO",
            "name": "國教行動聯盟兒少人權監督平台",
            "alternateName": ["AABE", "Child Rights Watch Taiwan"],
            "url": "https://naer-tw.github.io/policy/",
            "description": "將政府文件、CRC 條文、結論性意見、人權行動計畫、現場案例與民間倡議整合為可關聯查詢的知識圖譜。",
            "areaServed": "Taiwan",
            "knowsAbout": ["兒童權利公約", "兒少人權", "教育政策", "校園安全", "青少年心理健康"],
            "license": "https://creativecommons.org/licenses/by/4.0/",
        }
    elif schema_type == "article":
        data = {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": title,
            "datePublished": today,
            "dateModified": today,
            "author": {"@type": "Organization", "name": "國教行動聯盟兒少人權監督平台"},
            "publisher": {"@type": "Organization", "name": "國教行動聯盟", "url": "https://naer-tw.github.io/policy/"},
            "license": "https://creativecommons.org/licenses/by/4.0/",
            "isAccessibleForFree": True,
            "inLanguage": "zh-TW",
            "citation": f"國教行動聯盟兒少人權監督平台,「{title}」,{today},取自 {source_rel}",
        }
    elif schema_type == "dataset":
        data = {
            "@context": "https://schema.org",
            "@type": "Dataset",
            "name": title,
            "description": f"兒少人權監督平台之 {title} 資料集",
            "creator": {"@type": "Organization", "name": "國教行動聯盟兒少人權監督平台"},
            "license": "https://creativecommons.org/licenses/by/4.0/",
            "dateModified": today,
            "inLanguage": "zh-TW",
            "isAccessibleForFree": True,
            "distribution": [
                {"@type": "DataDownload", "encodingFormat": "text/markdown",
                 "contentUrl": source_rel}
            ],
        }
    elif schema_type == "faqpage":
        data = {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "name": title,
            "inLanguage": "zh-TW",
            "license": "https://creativecommons.org/licenses/by/4.0/",
            "mainEntity": [
                {"@type": "Question", "name": "本平台是什麼?",
                 "acceptedAnswer": {"@type": "Answer", "text": "兒少人權監督平台由國教行動聯盟維運,將政府文件、CRC 條文、結論性意見、現場案例與民間倡議整合為可關聯查詢的知識圖譜。"}},
                {"@type": "Question", "name": "資料如何引用?",
                 "acceptedAnswer": {"@type": "Answer", "text": "本平台採 CC BY 4.0 授權,引用請標示來源「國教行動聯盟兒少人權監督平台」與取得日期。"}},
                {"@type": "Question", "name": "兒少資料如何保護?",
                 "acceptedAnswer": {"@type": "Answer", "text": "依 governance/child_safeguarding §三點五,涉案例敘事一律去識別化,引用前須逐條檢核。"}},
            ],
        }
    else:
        return ""
    return f'<script type="application/ld+json">\n{json.dumps(data, ensure_ascii=False, indent=2)}\n</script>\n'


def md_to_html_body(md_path: Path) -> str | None:
    """用 pandoc 轉 md → body HTML 片段。"""
    try:
        result = subprocess.run(
            ["pandoc", str(md_path), "-f", "markdown", "-t", "html5", "--no-highlight"],
            capture_output=True, text=True, check=True,
        )
        return result.stdout
    except FileNotFoundError:
        print("⚠ pandoc 未安裝。安裝:brew install pandoc", file=sys.stderr)
        return None
    except subprocess.CalledProcessError as e:
        print(f"⚠ pandoc 失敗:{e.stderr}", file=sys.stderr)
        return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("source", help="markdown 檔路徑(相對於專案根或絕對路徑)")
    ap.add_argument("--out", help="輸出 HTML 路徑(預設與 source 同目錄,副檔名換為 .html)")
    ap.add_argument("--strip-frontmatter", action="store_true", help="印刷時不顯 YAML 頭")
    ap.add_argument("--noindex", action="store_true", help="注入 noindex meta 標籤(部署到 _share/ 等私有頁面時用)")
    ap.add_argument("--schema-type", choices=["organization", "article", "dataset", "faqpage"], help="注入 Schema.org JSON-LD(對應 MVP 藍圖 §5 GEO/SEO 整合)")
    args = ap.parse_args()

    src = Path(args.source)
    if not src.is_absolute():
        src = ROOT / src
    if not src.exists():
        print(f"❌ 找不到檔案:{src}", file=sys.stderr)
        return 1

    text = src.read_text(encoding="utf-8")
    if args.strip_frontmatter:
        clean = strip_frontmatter(text)
        # pandoc 對 stripped 內容轉換,要先寫 tmp
        tmp = src.parent / f".tmp_{src.stem}.md"
        tmp.write_text(clean, encoding="utf-8")
        try:
            html_body = md_to_html_body(tmp)
        finally:
            tmp.unlink(missing_ok=True)
    else:
        html_body = md_to_html_body(src)

    if html_body is None:
        return 1

    title = extract_title(text)
    out = Path(args.out) if args.out else src.with_suffix(".html")
    out.parent.mkdir(parents=True, exist_ok=True)
    source_rel = str(src.relative_to(ROOT)) if src.is_relative_to(ROOT) else str(src)
    noindex_tags = (
        '<meta name="robots" content="noindex,nofollow,noarchive,nosnippet">\n'
        '<meta name="googlebot" content="noindex,nofollow">\n'
        if args.noindex else ""
    )
    schema_jsonld = build_jsonld(args.schema_type, title, source_rel) if args.schema_type else ""
    nhrc_block = extract_nhrc_indicators(text)
    # 用 replace 而非 format,避免 CSS 的 {} 衝突
    html = (
        HTML_HEAD.replace("{noindex}", noindex_tags)
                 .replace("{title}", title)
                 .replace("{schema_jsonld}", schema_jsonld)
        + html_body
        + nhrc_block
        + HTML_FOOT.replace("{date}", dt.date.today().isoformat()).replace("{source}", source_rel)
    )
    out.write_text(html, encoding="utf-8")
    print(f"✓ 輸出:{out}")
    print(f"  標題:{title}")
    print(f"  下一步:open {out}  → 瀏覽器 Cmd+P → 存成 PDF")
    return 0


if __name__ == "__main__":
    sys.exit(main())
