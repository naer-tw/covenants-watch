#!/usr/bin/env python3
"""
search_archive.py — 對平台所有 markdown / txt 檔做全文搜尋(快速 grep + 上下文)。

涵蓋目錄:
  data/policy_issues/   (14 議題)
  data/advocacy_actions/(18+27 倡議)
  data/cases/           (4 案例)
  data/sources/         (CRC1+2 全文、NHRC 報告、訪談、NAAES 27 篇)
  shadow_report/sections/(影子報告草稿)

用法:
  python3 scripts/search_archive.py "關鍵字"
  python3 scripts/search_archive.py "保證人地位" --context 2  # 前後各 2 行
  python3 scripts/search_archive.py "自殺" --pi PI-02         # 限該議題
  python3 scripts/search_archive.py "梅毒" --naaes-only       # 只在 NAAES 文章
  python3 scripts/search_archive.py "CRC2-CO47" --regex       # regex 模式
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

SCOPE = {
    "policy_issues":    ROOT / "data" / "policy_issues",
    "advocacy_actions": ROOT / "data" / "advocacy_actions",
    "cases":            ROOT / "data" / "cases",
    "sources":          ROOT / "data" / "sources",
    "shadow_sections":  ROOT / "shadow_report" / "sections",
}


def search_file(path: Path, pattern: re.Pattern, context: int) -> list:
    """回傳 [(line_no, snippet), ...]"""
    try:
        lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    except Exception:
        return []
    hits = []
    for i, line in enumerate(lines):
        if pattern.search(line):
            start = max(0, i - context)
            end = min(len(lines), i + context + 1)
            snippet = "\n".join(f"  {n+1}: {lines[n]}" for n in range(start, end))
            hits.append((i + 1, snippet))
    return hits


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("query", help="搜尋關鍵字")
    ap.add_argument("--regex", action="store_true", help="把 query 當 regex(預設逐字)")
    ap.add_argument("--context", type=int, default=1, help="前後行數(預設 1)")
    ap.add_argument("--pi", help="限定 PI(如 PI-02)")
    ap.add_argument("--naaes-only", action="store_true", help="只搜 NAAES 政策站文章")
    ap.add_argument("--scope", choices=list(SCOPE), help="限定搜尋目錄")
    ap.add_argument("--max-files", type=int, default=20, help="最多顯示 N 個檔案命中")
    args = ap.parse_args()

    flags = re.IGNORECASE
    pattern = re.compile(args.query if args.regex else re.escape(args.query), flags)

    targets = []
    scopes = [args.scope] if args.scope else list(SCOPE)
    for s in scopes:
        d = SCOPE[s]
        if not d.exists():
            continue
        for f in d.rglob("*"):
            if f.suffix not in (".md", ".txt"):
                continue
            if args.pi and args.pi.lower() not in str(f).lower():
                continue
            if args.naaes_only and "naaes_policy" not in str(f):
                continue
            targets.append((s, f))

    print(f"▶ 搜尋「{args.query}」於 {len(targets)} 個檔案...")
    file_hits = 0
    line_hits = 0
    for scope_name, path in targets:
        hits = search_file(path, pattern, args.context)
        if not hits:
            continue
        if file_hits >= args.max_files:
            print(f"\n  ... 達到 --max-files {args.max_files},剩餘命中已省略")
            break
        rel = path.relative_to(ROOT)
        print(f"\n📄 [{scope_name}] {rel}({len(hits)} 個命中)")
        for ln, snippet in hits[:5]:  # 每檔最多顯示 5 個命中
            print(snippet)
            line_hits += 1
        if len(hits) > 5:
            print(f"  ... 另 {len(hits) - 5} 個命中省略")
        file_hits += 1

    print(f"\n=== 結果 ===")
    print(f"  📄 命中檔案:{file_hits}")
    print(f"  📍 命中行數:{line_hits}")
    return 0 if file_hits else 1


if __name__ == "__main__":
    sys.exit(main())
