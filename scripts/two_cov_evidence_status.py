#!/usr/bin/env python3
"""
資料完整度報告 — 統計 16 PI 之實證進度

Usage:
    python3 scripts/two_cov_evidence_status.py
    python3 scripts/two_cov_evidence_status.py --markdown    # 產 markdown 表
    python3 scripts/two_cov_evidence_status.py --html        # 產 HTML 報告
"""
from __future__ import annotations
import argparse
import re
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PI_DIR = ROOT / "data" / "policy_issues"
EVIDENCE_DIR = ROOT / "data" / "evidence"
DB = ROOT / "data" / "two_cov.db"

STATUS_LEVELS = [
    "framework",
    "research_design_only",
    "draft",
    "draft_pending_data",
    "framework_pending_data",
    "partial_metadata",
    "partial_evidence",
    "research_complete",
    "external_review_complete",
    "published",
]

STATUS_RANK = {s: i for i, s in enumerate(STATUS_LEVELS)}


def gather() -> list[dict]:
    """蒐集每張 PI 卡之 status + evidence 引用"""
    rows = []
    for md in sorted(PI_DIR.glob("PI-*.md")):
        text = md.read_text(encoding="utf-8")
        m_pi = re.search(r"^pi_id:\s*(.+)$", text, re.MULTILINE)
        m_status = re.search(r"^status:\s*(.+)$", text, re.MULTILINE)
        m_title = re.search(r"^title:\s*(.+)$", text, re.MULTILINE)
        # 引用之 CSV
        cited_csv = re.findall(r"data/evidence/[\w_]+\.csv", text)
        rows.append({
            "pi_id": m_pi.group(1).strip() if m_pi else "?",
            "title": m_title.group(1).strip() if m_title else "",
            "status": m_status.group(1).strip() if m_status else "framework",
            "cited_csv": list(set(cited_csv)),
            "n_csv": len(set(cited_csv)),
        })
    return rows


def csv_inventory() -> list[dict]:
    """data/evidence/*.csv 清單"""
    rows = []
    for csv_path in sorted(EVIDENCE_DIR.glob("*.csv")):
        rows.append({
            "name": csv_path.name,
            "size_kb": round(csv_path.stat().st_size / 1024, 1),
            "lines": sum(1 for _ in csv_path.read_text().splitlines()) - 1,  # exclude header
        })
    return rows


def render_markdown(rows: list[dict], csvs: list[dict]) -> str:
    out = ["# 兩公約平台資料完整度報告\n"]
    # 摘要
    by_status = {}
    for r in rows:
        by_status[r["status"]] = by_status.get(r["status"], 0) + 1
    out.append("## 一、PI 狀態分布\n")
    out.append("| 狀態 | 張數 |")
    out.append("|---|---:|")
    for s in sorted(by_status, key=lambda x: STATUS_RANK.get(x, 99), reverse=True):
        out.append(f"| {s} | {by_status[s]} |")
    out.append(f"| **合計** | **{len(rows)}** |")
    out.append("")

    # PI 列表
    out.append("## 二、16 PI 實證對照\n")
    out.append("| PI | Status | CSV 引用數 | Title |")
    out.append("|---|---|---:|---|")
    for r in rows:
        out.append(f"| {r['pi_id']} | {r['status']} | {r['n_csv']} | {r['title'][:40]} |")
    out.append("")

    # CSV 清單
    out.append(f"## 三、Evidence CSV 清單（共 {len(csvs)} 份）\n")
    out.append("| 檔名 | 大小（KB）| 行數 |")
    out.append("|---|---:|---:|")
    for c in csvs:
        out.append(f"| {c['name']} | {c['size_kb']} | {c['lines']} |")
    out.append("")

    return "\n".join(out)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--markdown", action="store_true")
    parser.add_argument("--html", action="store_true")
    args = parser.parse_args()

    rows = gather()
    csvs = csv_inventory()

    if args.markdown or args.html:
        md = render_markdown(rows, csvs)
        if args.html:
            # 簡易 markdown -> html
            html_path = ROOT / "_public" / "dashboards" / "evidence_status.html"
            html_path.parent.mkdir(parents=True, exist_ok=True)
            body = md.replace("\n", "<br>")
            html_path.write_text(
                f"<!DOCTYPE html><html lang='zh-Hant'><head><meta charset='UTF-8'>"
                f"<title>資料完整度</title><meta name='robots' content='noindex'>"
                f"<style>body{{font-family:sans-serif;max-width:980px;margin:auto;padding:24px;line-height:1.7}}</style></head>"
                f"<body><pre style='white-space:pre-wrap'>{md}</pre></body></html>",
                encoding="utf-8",
            )
            print(f"  ✓ {html_path}")
        else:
            print(md)
    else:
        # 簡略
        n_partial = sum(1 for r in rows if r["status"].startswith("partial"))
        n_framework = sum(1 for r in rows if r["status"] == "framework")
        n_research = sum(1 for r in rows if r["status"].startswith("research"))
        print(f"PI 狀態分布:")
        print(f"  partial_evidence/metadata: {n_partial}/16")
        print(f"  research_design_only:       {n_research}/16")
        print(f"  framework only:             {n_framework}/16")
        print(f"\nEvidence CSV: {len(csvs)} 份")
        for c in csvs:
            print(f"  • {c['name']:50} {c['size_kb']:>6.1f} KB / {c['lines']:>4} rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
