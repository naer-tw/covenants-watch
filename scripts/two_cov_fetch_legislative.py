#!/usr/bin/env python3
"""
立法院公報全文抓取（PI-13 配合）

Usage:
    python3 scripts/two_cov_fetch_legislative.py --years 2009-2026 --dry-run
    python3 scripts/two_cov_fetch_legislative.py --terms "兩公約,ICCPR,ICESCR"

立法院 API：https://data.ly.gov.tw/
公報全文：https://lis.ly.gov.tw/
IVOD：https://ivod.ly.gov.tw/
"""
from __future__ import annotations
import argparse
import sqlite3
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "data" / "two_cov.db"
RAW_DIR = ROOT / "data" / "sources" / "raw" / "legislative"

DEFAULT_TERMS = [
    "兩公約", "公政公約", "ICCPR", "ICESCR",
    "經社文公約", "公約施行法", "人權兩公約",
]

LY_API_BASE = "https://data.ly.gov.tw/odw/ID9.json"
LY_BULLETIN_BASE = "https://lis.ly.gov.tw/lygazettec/"


def fetch_bulletin_index(year: int, dry: bool) -> list[dict]:
    """抓取單一年度公報索引（須加 rate limit + robots 合規）"""
    if dry:
        print(f"  [dry] 將抓 {year} 年立法院公報索引（{LY_API_BASE}）")
        return []
    raise NotImplementedError(
        "立法院 API 對接須:\n"
        "1. 申請 API key (data.ly.gov.tw)\n"
        "2. 確認 robots + rate limit\n"
        "3. 用 _http.py 共用模組（已存在於 scripts/）\n"
        "4. 暫存原始 JSON 至 data/sources/raw/legislative/{year}/"
    )


def search_full_text(text: str, terms: list[str]) -> list[dict]:
    """於公報全文中搜尋兩公約相關發言段落"""
    hits = []
    for term in terms:
        idx = 0
        while True:
            i = text.find(term, idx)
            if i < 0:
                break
            ctx_start = max(0, i - 200)
            ctx_end = min(len(text), i + 400)
            hits.append({
                "term": term,
                "context": text[ctx_start:ctx_end],
                "position": i,
            })
            idx = i + len(term)
    return hits


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--years", type=str, default="2009-2026")
    parser.add_argument("--terms", type=str, default=",".join(DEFAULT_TERMS))
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    start, end = map(int, args.years.split("-"))
    terms = args.terms.split(",")

    print(f"年份範圍：{start}-{end}")
    print(f"搜尋詞：{terms}")
    print(f"原始檔暫存：{RAW_DIR}")

    if args.dry_run:
        print("\n[dry-run] 不實際抓取")
        for year in range(start, end + 1):
            fetch_bulletin_index(year, dry=True)
        return 0

    print("\n⚠ 實際抓取尚未實作")
    print("須先完成：")
    print("  1. data.ly.gov.tw API key 申請")
    print("  2. robots.txt + 抓取頻率合規")
    print("  3. 用 scripts/_http.py + retry/backoff")
    print("  4. 原始 JSON / HTML 暫存至 data/sources/raw/legislative/")
    print("  5. 用 _md_frontmatter.py 解析 → SQLite legislative_citation 表")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
