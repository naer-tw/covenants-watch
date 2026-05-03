#!/usr/bin/env python3
"""
動態掃 _public/ 之全部 HTML,輸出 sitemap.xml + llms.txt URL 段
基準域名:covenants.aabe.org.tw

Usage:
    python3 scripts/two_cov_build_sitemap.py
"""
from __future__ import annotations
import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PUBLIC = ROOT / "_public"
BASE = "https://covenants.aabe.org.tw"

# 不入索引 / 不發到 sitemap 的 patterns(管理頁、原始 db 等)
EXCLUDE = {
    "admin/index.html",
    "index_legacy.html",  # 舊首頁備份
}

# 各路徑優先級
PRIORITY = {
    "index.html": 1.0,
    "issues/": 0.9,
    "trace/": 0.85,
    "laws/": 0.85,
    "shadow_reports/": 0.85,
    "dashboards/": 0.7,
    "api/": 0.6,
    "search.html": 0.7,
    "about.html": 0.6,
    "methodology.html": 0.6,
    "feedback.html": 0.5,
    "agenda_transparency.html": 0.7,
}


def get_priority(rel_path: str) -> float:
    if rel_path == "index.html":
        return 1.0
    for prefix, pri in PRIORITY.items():
        if rel_path.startswith(prefix):
            return pri
    return 0.5


def main() -> int:
    today = datetime.date.today().isoformat()

    htmls: list[str] = []
    for p in sorted(PUBLIC.rglob("*.html")):
        rel = str(p.relative_to(PUBLIC))
        if rel in EXCLUDE:
            continue
        # 跳過 admin/
        if rel.startswith("admin/"):
            continue
        htmls.append(rel)

    # 寫 sitemap.xml
    out = ['<?xml version="1.0" encoding="UTF-8"?>']
    out.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
    for rel in htmls:
        # index.html 路徑簡化為目錄
        url_path = rel
        if rel.endswith("/index.html"):
            url_path = rel[:-len("index.html")]
        elif rel == "index.html":
            url_path = ""
        loc = f"{BASE}/{url_path}" if url_path else f"{BASE}/"
        pri = get_priority(rel)
        out.append(f"  <url><loc>{loc}</loc><lastmod>{today}</lastmod><priority>{pri}</priority></url>")
    out.append("</urlset>")

    sitemap_path = PUBLIC / "sitemap.xml"
    sitemap_path.write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"  ✓ sitemap.xml  {len(htmls)} URLs  {sitemap_path.stat().st_size:,} bytes")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
