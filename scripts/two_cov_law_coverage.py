#!/usr/bin/env python3
"""
跨法律之公約條文覆蓋率分析

回答：
- ICCPR Art.18（宗教自由）有哪幾部國內法律涵蓋？
- ICCPR Art.6（生命權）相關之國內法律修法歷程？
- 哪些公約條文目前**沒有對應的國內施行法律**？

Usage:
    python3 scripts/two_cov_law_coverage.py
    python3 scripts/two_cov_law_coverage.py --article ICCPR-18
"""
from __future__ import annotations
import argparse
import json
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "data" / "two_cov.db"


def article_to_law_map(conn) -> dict:
    """ICCPR/ICESCR 條文 → 國內法律列表"""
    cur = conn.execute("SELECT law_id, law_name_zh, covers_articles FROM law")
    mapping = {}
    for law_id, name, covers in cur.fetchall():
        if not covers:
            continue
        try:
            arts = json.loads(covers)
        except Exception:
            continue
        for art in arts:
            mapping.setdefault(art, []).append((law_id, name))
    return mapping


def all_articles_summary(conn) -> None:
    mapping = article_to_law_map(conn)
    print("\n=== 公約條文 × 國內法律對照 ===\n")
    iccpr_arts = [f"ICCPR-{i}" for i in range(1, 28)]
    icescr_arts = [f"ICESCR-{i}" for i in range(1, 16)]

    print("ICCPR：")
    for art in iccpr_arts:
        laws = mapping.get(art, [])
        if laws:
            for law_id, name in laws:
                print(f"  Art.{art.split('-')[1]:>3}  → {name} ({law_id})")
        else:
            print(f"  Art.{art.split('-')[1]:>3}  ✗ 無對應國內法律")

    print("\nICESCR：")
    for art in icescr_arts:
        laws = mapping.get(art, [])
        if laws:
            for law_id, name in laws:
                print(f"  Art.{art.split('-')[1]:>3}  → {name} ({law_id})")
        else:
            print(f"  Art.{art.split('-')[1]:>3}  ✗ 無對應國內法律")


def article_detail(conn, article: str) -> None:
    """單一條文之詳細資料：對應法律 + 修法歷程 + 立法理由"""
    mapping = article_to_law_map(conn)
    laws = mapping.get(article, [])
    if not laws:
        print(f"\n  ✗ 條文 {article} 無對應之國內法律記錄")
        return

    print(f"\n=== {article} 對應之國內法律 ===\n")
    for law_id, name in laws:
        print(f"📜 {name}（{law_id}）")
        # 列版本
        vers = conn.execute(
            """SELECT version_label, promulgated_date, legislative_reason, is_current
               FROM law_version WHERE law_id=? ORDER BY promulgated_date""",
            (law_id,),
        ).fetchall()
        for label, prom, reason, current in vers:
            tag = "[現行]" if current else ""
            print(f"   {prom}  {label} {tag}")
            if reason:
                print(f"      → {reason[:120]}")

        # 列該條文相關之 article_change
        changes = conn.execute(
            """SELECT lac.article_number, lac.change_type, lac.text_after, lac.reason
               FROM law_article_change lac
               JOIN law_version lv ON lac.version_id=lv.version_id
               WHERE lv.law_id=? AND (lac.related_article LIKE ?)""",
            (law_id, f"%{article}%"),
        ).fetchall()
        if changes:
            print(f"   涉及 {article} 之條文變動：")
            for art_num, c_type, text, reason in changes:
                print(f"      [{c_type}] {art_num}: {(text or '')[:60]}")
                if reason:
                    print(f"         理由：{reason[:80]}")
        print()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--article", help="如 ICCPR-18 或 ICESCR-12")
    args = parser.parse_args()

    if not DB.exists():
        return 1
    conn = sqlite3.connect(DB)
    if args.article:
        article_detail(conn, args.article)
    else:
        all_articles_summary(conn)
    conn.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
