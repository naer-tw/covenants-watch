#!/usr/bin/env python3
"""classify_sources.py — 把 data/sources/ 下檔案依 raw/clean/publish 三層分類。

Wave 67:不實際移動檔案(會破壞 26 處引用),改寫:
1. CLASSIFICATION_INDEX.md(對外可讀分類表)
2. SQLite document_version 表填入 review_status 欄位

對應 governance/document_governance.md §1.1-1.3。

分類規則(基於 filename + 副檔名):
- raw     :原始未處理檔(*.pdf、*_Recording_*、*_逐字稿*.txt、_sensitive/)
- clean   :OCR 切段或清洗過(*.txt 非 recording、_part?.txt)
- publish :可檢索引用之最終版(*.md 摘要、*.csv 解析資料、naaes_policy/、CO 條文整理)

用法:
    python3 scripts/classify_sources.py            # 列出分類結果
    python3 scripts/classify_sources.py --update   # 更新 SQLite + 寫 INDEX
"""
from __future__ import annotations

import argparse
import re
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCES = ROOT / "data" / "sources"
DB = ROOT / "data" / "crw.db"


def classify(path: Path) -> tuple[str, str]:
    """回傳 (tier, reason)。"""
    name = path.name
    rel = str(path.relative_to(SOURCES))

    # 三層子目錄本身跳過
    if rel.startswith(("raw/", "clean/", "publish/")):
        return ("skip", "已在三層子目錄")

    # raw 規則
    if name.endswith(".pdf"):
        return ("raw", "原始 PDF(政府公文 / 政府報告 / 訪談原稿)")
    if "_Recording_" in name or "_groq" in name or "_逐字稿" in name:
        return ("raw", "音檔逐字稿原始(SOP §3.3 不對外)")
    if "_sensitive" in rel:
        return ("raw", "敏感層(限內部)")

    # clean 規則 — 從 PDF OCR 切出之 txt
    if name.endswith(".txt") and not name.endswith("_groq.txt"):
        # 檢查是否 PDF 配對:同名 .pdf 存在?
        pdf_sibling = path.with_suffix(".pdf")
        if pdf_sibling.exists():
            return ("clean", "PDF OCR 切段(原 PDF 在 raw)")
        return ("clean", "txt 中間檔(可能來自 OCR 或 transcripts)")

    # publish 規則 — 摘要、整理、政策資產
    if name.endswith(".md"):
        if "_摘要.md" in name or "_制度面摘要.md" in name:
            return ("publish", "摘要 / 制度面摘要(已去識別化)")
        if rel.startswith("naaes_policy/"):
            return ("publish", "AABE 政策站文章(已對外發布)")
        if "_佔位.md" in name:
            return ("publish", "schema 佔位(待數值匯入)")
        if name.startswith("CRC") and "條" in name:
            return ("publish", "CRC 條文 / CO 結構化整理")
        if "新聞稿" in name or "_十大議題" in name or "聯合記者會" in name:
            return ("publish", "AABE 新聞稿(已對外)")
        if rel.startswith(("0413_", "0415_")):
            return ("publish", "公聽會書面材料")
        return ("publish", "整理 / 分析 markdown(預設 publish)")

    if name.endswith(".csv"):
        return ("publish", "結構化資料(CSV,可引用)")

    if name.endswith(".html"):
        return ("publish", "已渲染 HTML(可發布)")

    return ("unknown", f"無法判斷({path.suffix})")


def collect_files() -> list[tuple[Path, str, str]]:
    files = []
    for p in sorted(SOURCES.rglob("*")):
        if not p.is_file():
            continue
        if any(part.startswith(".") for part in p.parts):
            continue
        tier, reason = classify(p)
        if tier == "skip":
            continue
        files.append((p, tier, reason))
    return files


def write_index(files: list[tuple[Path, str, str]]) -> None:
    out = SOURCES / "CLASSIFICATION_INDEX.md"
    by_tier: dict[str, list] = {"raw": [], "clean": [], "publish": [], "unknown": []}
    for p, t, r in files:
        by_tier[t].append((p, r))

    lines = [
        "# data/sources/ 三層分類索引(Wave 67)",
        "",
        "> 對應 governance/document_governance.md §1.1-1.3。",
        "> 本檔由 `scripts/classify_sources.py --update` 自動產生(每月執行一次)。",
        "> **檔案實際位置不變**(避免破壞 26 處引用),三層分類僅作為 metadata 與審查 SOP 之依據。",
        "",
        f"統計:raw {len(by_tier['raw'])} / clean {len(by_tier['clean'])} / publish {len(by_tier['publish'])} / unknown {len(by_tier['unknown'])}",
        "",
    ]
    for tier in ["raw", "clean", "publish", "unknown"]:
        items = by_tier[tier]
        if not items:
            continue
        lines.append(f"## {tier.upper()}({len(items)} 檔)")
        lines.append("")
        lines.append("| 檔名 | 分類理由 |")
        lines.append("|---|---|")
        for p, reason in sorted(items, key=lambda x: str(x[0])):
            rel = str(p.relative_to(ROOT))
            lines.append(f"| `{rel}` | {reason} |")
        lines.append("")
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"✓ 寫入 {out.relative_to(ROOT)}({sum(len(v) for v in by_tier.values())} 檔)")


def update_sqlite(files: list[tuple[Path, str, str]]) -> None:
    conn = sqlite3.connect(str(DB))
    # 用 file_path 對應 document_version
    cur = conn.cursor()
    updated = 0
    for p, tier, _reason in files:
        rel = str(p.relative_to(ROOT))
        # 看是否已有 document_version 記錄
        cur.execute("SELECT version_id FROM document_version WHERE file_path = ?", (rel,))
        row = cur.fetchone()
        if row:
            cur.execute(
                "UPDATE document_version SET review_status = ? WHERE version_id = ?",
                (tier, row[0]),
            )
            updated += 1
    conn.commit()
    conn.close()
    print(f"✓ SQLite document_version 更新 {updated} 筆 review_status")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--update", action="store_true", help="更新 INDEX 與 SQLite")
    args = ap.parse_args()

    files = collect_files()
    print(f"收集 {len(files)} 個來源檔案")
    counts = {"raw": 0, "clean": 0, "publish": 0, "unknown": 0}
    for _, t, _ in files:
        counts[t] += 1
    print(f"  raw {counts['raw']} / clean {counts['clean']} / publish {counts['publish']} / unknown {counts['unknown']}")

    if args.update:
        write_index(files)
        update_sqlite(files)
    else:
        for p, tier, reason in files:
            print(f"  [{tier:7}] {p.relative_to(SOURCES)} — {reason}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
