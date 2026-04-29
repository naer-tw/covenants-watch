#!/usr/bin/env python3
"""
sync_to_jekyll.py — 把本地 Markdown 議題卡片轉為 Jekyll 可發布格式。

設計原則:
- 不直接寫到 GH Pages repo,而是輸出到本地 _jekyll_output/ 讓使用者人工 cp(避免誤推)
- 加上 Jekyll 必需的 frontmatter(layout、permalink、date)
- 重寫跨檔案相對連結(../advocacy_actions/A-XX.md → /actions/a-xx/)
- 過濾本地路徑連結(~/Desktop/)為「內部資料」標示
- 跳過 published=false 的議題

用法:
    python3 scripts/sync_to_jekyll.py                      # 全部同步
    python3 scripts/sync_to_jekyll.py --include-drafts     # 含 published=false
    python3 scripts/sync_to_jekyll.py --strip-todos        # 去除 [待補] 內容
    python3 scripts/sync_to_jekyll.py --target /path/to/gh # 直接寫入 GH Pages repo(需 --confirm)
"""
from __future__ import annotations

import argparse
import re
import shutil
import sys
from pathlib import Path

# Wave 36:共用 frontmatter 模組
from _md_frontmatter import YAML_RE, parse_yaml as parse_yaml_simple  # noqa: F401

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUT = ROOT / "_jekyll_output"


# ---------------------------------------------------------------------
# 路徑與連結映射
# ---------------------------------------------------------------------
COLLECTIONS = {
    "policy_issues": {"layout": "issue", "permalink_prefix": "/issues/"},
    "domestic_laws": {"layout": "law", "permalink_prefix": "/laws/"},
    "advocacy_actions": {"layout": "action", "permalink_prefix": "/actions/"},
    "cases": {"layout": "case", "permalink_prefix": "/cases/"},
    "sources": {"layout": "source", "permalink_prefix": "/sources/"},
}

# layout → permalink prefix(供 frontmatter 構建用)
LAYOUT_TO_PREFIX = {v["layout"]: v["permalink_prefix"] for v in COLLECTIONS.values()}


def slugify(stem: str) -> str:
    """把議題/法規/案例 ID 轉為 URL slug。
    PI-12_替代照顧 → pi-12;L01_兒少 → l01;A-2026-04-17_X → a-2026-04-17"""
    base = stem.split("_", 1)[0].lower()
    return re.sub(r"[^a-z0-9-]", "-", base)


def rewrite_links(text: str, current_collection: str, strip_todos: bool) -> str:
    """重寫 Markdown 中的相對連結與本地路徑。"""
    # 跨檔案相對連結:../advocacy_actions/A-XX.md → /actions/a-xx/
    def cross_ref(m: re.Match) -> str:
        label = m.group(1)
        target_dir = m.group(2)
        target_file = m.group(3)
        coll = COLLECTIONS.get(target_dir, {})
        prefix = coll.get("permalink_prefix", f"/{target_dir}/")
        slug = slugify(target_file.replace(".md", ""))
        return f"[{label}]({prefix}{slug}/)"

    text = re.sub(
        r"\[([^\]]+)\]\(\.\./([^/]+)/([^)]+\.md)\)",
        cross_ref,
        text,
    )

    # 同目錄相對連結
    text = re.sub(
        r"\[([^\]]+)\]\(([^/)]+\.md)\)",
        lambda m: f"[{m.group(1)}]({COLLECTIONS.get(current_collection, {}).get('permalink_prefix', '/')}{slugify(m.group(2).replace('.md', ''))}/)",
        text,
    )

    # 本地路徑(~/Desktop, file://):轉為「內部資料」標示
    text = re.sub(
        r"\[([^\]]+)\]\((~/Desktop[^)]*|file://[^)]*)\)",
        r"_\1_(內部資料,未公開)",
        text,
    )

    # [待補] 處理
    if strip_todos:
        text = re.sub(r"\[待補[^\]]*\]", "_(資料整理中)_", text)
        text = re.sub(r"^- \[待補.*$", "", text, flags=re.MULTILINE)

    return text


def build_jekyll_frontmatter(meta: dict, layout: str, slug: str, date: str) -> str:
    """產生 Jekyll 規格 frontmatter。"""
    prefix = LAYOUT_TO_PREFIX.get(layout, f"/{layout}s/")
    yaml_lines = [
        f"layout: {layout}",
        f"permalink: {prefix}{slug}/",
        f"date: {date}",
        "sitemap: true",
    ]
    # 帶上原 frontmatter 的關鍵欄位
    passthrough = ["title_zh", "title_en", "issue_id", "law_id", "action_id", "case_id",
                   "cluster", "severity", "crc_articles", "co_paragraphs",
                   "domestic_laws", "indicators", "published", "last_updated",
                   "name_zh", "competent_agency", "action_date", "action_type",
                   "ethics_status"]  # SOP §3.1:讓 Jekyll 端可選擇性顯示
    for key in passthrough:
        if key in meta:
            v = meta[key]
            if isinstance(v, list):
                v = "[" + ", ".join(str(x) for x in v) + "]"
            yaml_lines.append(f"{key}: {v}")

    # 加上 SEO 用 title
    title = meta.get("title_zh") or meta.get("name_zh") or meta.get("title", "")
    if title:
        yaml_lines.insert(0, f"title: {title}")

    return "---\n" + "\n".join(yaml_lines) + "\n---\n\n"


# ---------------------------------------------------------------------
# 主流程
# ---------------------------------------------------------------------
def process_collection(coll_dir: str, out_root: Path, args) -> int:
    src_dir = ROOT / "data" / coll_dir
    if not src_dir.exists():
        return 0
    coll_meta = COLLECTIONS[coll_dir]
    out_dir = out_root / f"_{coll_meta['layout']}s"
    out_dir.mkdir(parents=True, exist_ok=True)

    n = 0
    # transcript_citation_sop §3.1:檔名 glob 排除原始逐字稿(防呆,避免有人意外存成 .md)
    # QA 第五輪 #4 修正:對齊 self_qa.sh §7 之 regex,涵蓋三種命名格式
    transcript_filename_re = re.compile(r"_(逐字稿|Recording_groq|whisper-(small|medium|large))")

    for md_path in sorted(src_dir.glob("*.md")):
        if transcript_filename_re.search(md_path.name):
            print(f"  ⏭  skip transcript filename (SOP §3.1): {md_path.name}")
            continue

        text = md_path.read_text(encoding="utf-8")
        m = YAML_RE.match(text)
        if not m:
            continue
        meta = parse_yaml_simple(m.group(1))
        body = text[m.end():]

        # transcript_citation_sop §3.1:排除「內部歸檔」之檔案(主要實際生效之過濾)
        ethics_status = str(meta.get("ethics_status", ""))
        if ethics_status.startswith("內部歸檔"):
            print(f"  ⏭  skip ethics_status=內部歸檔 (SOP §3.1): {md_path.name}")
            continue

        # published 過濾
        if not args.include_drafts:
            published = meta.get("published")
            # policy_issue 預設未發布需跳過;其他類別預設發布
            if coll_dir == "policy_issues" and not published:
                print(f"  ⏭  skip draft: {md_path.name}")
                continue

        slug = slugify(md_path.stem)
        date = str(meta.get("last_updated") or meta.get("action_date") or "2026-04-25")
        fm = build_jekyll_frontmatter(meta, coll_meta["layout"], slug, date)
        body = rewrite_links(body, coll_dir, args.strip_todos)

        out_path = out_dir / f"{slug}.md"
        out_path.write_text(fm + body, encoding="utf-8")
        n += 1

    return n


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--include-drafts", action="store_true",
                    help="含 published=false 之議題")
    ap.add_argument("--strip-todos", action="store_true",
                    help="把 [待補] 改寫為「資料整理中」")
    ap.add_argument("--target", type=Path,
                    help="直接寫入指定路徑(例如 GH Pages repo);需配合 --confirm")
    ap.add_argument("--confirm", action="store_true",
                    help="允許寫入 --target 指定的非 _jekyll_output/ 路徑")
    args = ap.parse_args()

    out_root = args.target if args.target else DEFAULT_OUT

    if args.target and not args.confirm:
        print(f"❌ 寫入 {args.target} 需要 --confirm 旗標(避免誤推)")
        return 1

    if out_root == DEFAULT_OUT:
        # 修法:只刪除自動產出的 collection 目錄,保留 templates/、README.md 等人工檔
        # (原本 shutil.rmtree(out_root) 會把人工建的 Jekyll templates 也炸掉)
        out_root.mkdir(parents=True, exist_ok=True)
        for coll_meta in COLLECTIONS.values():
            auto_dir = out_root / f"_{coll_meta['layout']}s"
            if auto_dir.exists():
                shutil.rmtree(auto_dir)

    total = 0
    print(f"輸出目錄:{out_root.relative_to(ROOT) if out_root.is_relative_to(ROOT) else out_root}")
    for coll in COLLECTIONS:
        n = process_collection(coll, out_root, args)
        print(f"  {coll:<20} {n:>4} 筆")
        total += n

    print(f"\n✓ 共輸出 {total} 個 Jekyll 檔案")
    print(f"\n下一步(若使用本地預設輸出):")
    print(f"  1. 檢視 {out_root.relative_to(ROOT) if out_root.is_relative_to(ROOT) else out_root}/ 的內容")
    print(f"  2. cp -r {out_root.relative_to(ROOT) if out_root.is_relative_to(ROOT) else out_root}/_*  /path/to/gh-pages-repo/")
    print(f"  3. 在 GH Pages repo 新增對應的 _layouts/issue.html 等模板")
    print(f"  4. git push 觸發 GH Pages build")
    return 0


if __name__ == "__main__":
    sys.exit(main())
