#!/usr/bin/env python3
"""
將 insider-gate.js 注入 _public/ 全部 HTML 之 <head>(idempotent)
例外:login.html / api/index.html / admin/

Usage:
    python3 scripts/two_cov_inject_gate.py
"""
from __future__ import annotations
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PUBLIC = ROOT / "_public"

# 例外:這些頁面不注入 gate
EXCLUDE_NAMES = {"login.html"}
EXCLUDE_PREFIXES = {"api/", "admin/"}

# 注入標記(idempotent)
MARKER = "<!-- aabe-insider-gate -->"


def gate_tag(rel_path: str) -> str:
    """根據相對路徑深度算出對 insider-gate.js 之相對路徑"""
    depth = rel_path.count("/")
    base = "../" * depth
    return f'{MARKER}<script src="{base}insider-gate.js"></script>'


def main() -> int:
    count_inject = 0
    count_skip = 0
    count_already = 0
    for p in sorted(PUBLIC.rglob("*.html")):
        rel = str(p.relative_to(PUBLIC))
        if rel in EXCLUDE_NAMES:
            count_skip += 1
            continue
        if any(rel.startswith(prefix) for prefix in EXCLUDE_PREFIXES):
            count_skip += 1
            continue
        text = p.read_text(encoding="utf-8")
        if MARKER in text:
            count_already += 1
            continue
        # 在 <head> 之開始注入(讓 gate 在任何 render 之前執行)
        new_text, n = re.subn(
            r"(<head[^>]*>)",
            r"\1\n" + gate_tag(rel),
            text,
            count=1,
        )
        if n == 0:
            print(f"  ⚠ 跳過(無 <head>):{rel}")
            count_skip += 1
            continue
        p.write_text(new_text, encoding="utf-8")
        count_inject += 1

    print(f"  ✓ inject:{count_inject}")
    print(f"  · already:{count_already}")
    print(f"  · skip:   {count_skip}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
