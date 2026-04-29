#!/usr/bin/env python3
"""
兩公約結論性意見（CO）抓取與解析骨架

Usage:
    python3 scripts/two_cov_fetch_co.py --review 4 --dry-run
    python3 scripts/two_cov_fetch_co.py --review 1 --pdf path/to/co1.pdf

來源：法務部「人權大步走」、人權公約施行監督聯盟（CovenantsWatch）
"""
from __future__ import annotations
import argparse
import json
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "data" / "two_cov.db"
CO_DIR = ROOT / "data" / "co"
RAW_DIR = ROOT / "data" / "sources" / "raw" / "co"

OFFICIAL_URLS = {
    1: "https://www.humanrights.moj.gov.tw/",
    2: "https://www.humanrights.moj.gov.tw/",
    3: "https://www.humanrights.moj.gov.tw/",
    4: "https://www.humanrights.moj.gov.tw/",
    "civil_society": "https://covenantswatch.org.tw/",
}


def parse_pdf_to_paragraphs(pdf_path: Path) -> list[dict]:
    """解析結論性意見 PDF，回傳逐段結構化資料

    輸出每筆：
        {
            "paragraph_number": int,
            "topic": str,
            "covenant": "ICCPR" | "ICESCR",
            "article_referenced": [str],
            "chinese_title": str,
            "recommendation_full": str,
        }
    """
    raise NotImplementedError(
        "PDF 解析：須先安裝 pypdf + 人工標註段落分類\n"
        "建議使用 pypdf 抽文字 + regex 抓段落號 + 人工分類 topic"
    )


def import_to_sqlite(records: list[dict], review: int, conn) -> int:
    """匯入 CO 至 SQLite"""
    n = 0
    for r in records:
        co_id = f"CO-{review}-{r['paragraph_number']}-{r.get('topic', 'tbd')}"
        conn.execute(
            """INSERT OR REPLACE INTO concluding_observation
               (co_id, review, review_year, paragraph_number, topic, covenant,
                article_referenced, chinese_title, recommendation_full,
                follow_up_status, created_at, updated_at)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
            (
                co_id,
                review,
                _review_year(review),
                r["paragraph_number"],
                r.get("topic", ""),
                r.get("covenant", ""),
                json.dumps(r.get("article_referenced", []), ensure_ascii=False),
                r.get("chinese_title", ""),
                r.get("recommendation_full", ""),
                "not_started",
                datetime.now().isoformat(),
                datetime.now().isoformat(),
            ),
        )
        n += 1
    return n


def _review_year(review: int) -> int:
    return {1: 2013, 2: 2017, 3: 2022, 4: 2025}.get(review, 0)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--review", type=int, required=True, choices=[1, 2, 3, 4])
    parser.add_argument("--pdf", type=str, help="原始 PDF 檔（已下載）")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    print(f"審查屆：{args.review}（{_review_year(args.review)}）")
    print(f"來源 URL：{OFFICIAL_URLS[args.review]}")

    if not args.pdf:
        print(f"\n下一步：")
        print(f"  1. 從 {OFFICIAL_URLS[args.review]} 下載第 {args.review} 屆 CO PDF")
        print(f"  2. 存至 {RAW_DIR / f'co_review_{args.review}.pdf'}")
        print(f"  3. 重跑：python3 {Path(__file__).name} --review {args.review} --pdf <path>")
        return 0

    pdf_path = Path(args.pdf)
    if not pdf_path.exists():
        print(f"❌ PDF 不存在：{pdf_path}")
        return 1

    try:
        records = parse_pdf_to_paragraphs(pdf_path)
    except NotImplementedError as e:
        print(f"⚠ {e}")
        return 1

    if args.dry_run:
        for r in records[:5]:
            print(f"  §{r['paragraph_number']}: {r.get('chinese_title', '')[:50]}")
        return 0

    conn = sqlite3.connect(DB)
    n = import_to_sqlite(records, args.review, conn)
    conn.commit()
    conn.close()
    print(f"✓ 匯入 {n} 筆 CO（review {args.review}）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
