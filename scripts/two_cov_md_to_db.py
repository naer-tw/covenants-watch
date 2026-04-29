#!/usr/bin/env python3
"""
Sync Markdown frontmatter → SQLite (two_cov.db)
僅同步 policy_issues / co / nap / evidence 四類

Usage:
    python3 scripts/two_cov_md_to_db.py [--dry-run]
"""
from __future__ import annotations
import argparse
import json
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _md_frontmatter import load_md as load_frontmatter  # noqa

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "data" / "two_cov.db"


def sync_policy_issues(conn, dry: bool) -> int:
    """同步 PI 卡片"""
    pi_dir = ROOT / "data" / "policy_issues"
    n = 0
    for md in sorted(pi_dir.glob("PI-*.md")):
        fm, _ = load_frontmatter(md)
        if not fm or "pi_id" not in fm:
            continue
        if dry:
            print(f"  [dry] {fm['pi_id']}: {fm.get('title','')}")
            n += 1
            continue
        conn.execute(
            """INSERT OR REPLACE INTO policy_issue
               (pi_id, title, block, priority, status, covenant, co_referenced,
                keywords, file_path, created, last_updated)
               VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
            (
                fm["pi_id"],
                fm.get("title", ""),
                fm.get("block", ""),
                fm.get("priority", ""),
                fm.get("status", ""),
                fm.get("covenant", ""),
                json.dumps(fm.get("co_referenced", []), ensure_ascii=False),
                ",".join(str(k) for k in (fm.get("keywords", []) or [])),
                str(md.relative_to(ROOT)),
                str(fm.get("created", "")),
                str(fm.get("last_updated", "")),
            ),
        )
        n += 1
    return n


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if not DB.exists():
        print(f"❌ DB 不存在：{DB}\n   先執行：sqlite3 {DB} < data/schema.sql")
        return 1

    conn = sqlite3.connect(DB)
    try:
        n_pi = sync_policy_issues(conn, args.dry_run)
        if not args.dry_run:
            conn.commit()
        print(f"✓ policy_issue: {n_pi} 筆")
        # TODO: sync_co / sync_nap / sync_evidence 待議題卡有後再加
    finally:
        conn.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
