#!/usr/bin/env python3
"""list_publish_status.py — 列出所有 PI / case / advocacy 之 published 狀態

用途:部署前快速檢視「哪些議題卡是可對外發布的」「哪些仍是 draft」。
sync_to_jekyll.py 對 policy_issues collection 預設只發布 published: true。

用法:
    python3 scripts/list_publish_status.py            # 列所有
    python3 scripts/list_publish_status.py --drafts   # 只列 draft
    python3 scripts/list_publish_status.py --ready    # 只列 published: true
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Wave 36 共用模組
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _md_frontmatter import load_md  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
DIRS = [
    ("policy_issues", "data/policy_issues", "PI"),
    ("advocacy_actions", "data/advocacy_actions", "A"),
    ("cases", "data/cases", "C"),
]


def status_of(meta: dict, coll: str) -> str:
    """sync_to_jekyll 的 published 過濾邏輯之鏡像。

    policy_issues 預設不發布(避免半成品意外公開);
    其他 collection(advocacy_actions / cases / etc.)預設發布。"""
    pub = meta.get("published")
    if pub is True:
        return "published"
    if pub is False:
        return "draft (false)"
    if coll == "policy_issues":
        return "draft (欄位缺,policy_issues 預設不發布)"
    return "published (欄位缺,此 collection 預設發布)"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--drafts", action="store_true")
    ap.add_argument("--ready", action="store_true")
    args = ap.parse_args()

    for coll, rel_path, prefix in DIRS:
        d = ROOT / rel_path
        if not d.exists():
            continue
        files = sorted(d.glob(f"{prefix}*.md"))
        if not files:
            continue
        n_pub = n_draft = 0
        rows = []
        for f in files:
            meta, _ = load_md(f)
            st = status_of(meta, coll)
            if st.startswith("published"):
                n_pub += 1
            else:
                n_draft += 1
            if args.drafts and not st.startswith("draft"):
                continue
            if args.ready and not st.startswith("published"):
                continue
            kid_status = meta.get("kid_version_status", "—")
            ethics = meta.get("ethics_status", "—")
            rows.append((f.name, st, kid_status, ethics))

        print(f"\n=== {coll}({n_pub} ready / {n_draft} draft)===")
        if not rows:
            print("  (無)")
            continue
        for name, st, kid, eth in rows:
            print(f"  {st:<32} {name}")
            if kid != "—":
                print(f"  {' ':<32}    kid: {kid[:50]}")
            if eth != "—":
                print(f"  {' ':<32}    ethics: {eth[:50]}")

    if not args.drafts and not args.ready:
        print("\n💡 部署前必做:把已定稿的議題 frontmatter 設為 `published: true`")
        print("   只有 published: true 的議題會被 sync_to_jekyll 推到對外網站")

    return 0


if __name__ == "__main__":
    sys.exit(main())
