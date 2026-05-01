#!/usr/bin/env python3
"""
渲染法律修法對照 HTML(_public/laws/{slug}.html)

Usage:
    python3 scripts/two_cov_render_law.py --all
"""
from __future__ import annotations
import argparse
import html
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "data" / "two_cov.db"
OUT_DIR = ROOT / "_public" / "laws"

CHANGE_COLOR = {
    "new": "#65a30d",
    "amended": "#D97706",
    "deleted": "#8B2631",
    "renumbered": "#6d28d9",
}

HTML_TPL = """<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{name} 修法歷程 — 兩公約總檢討平台</title>
<meta name="description" content="{name} 之歷次三讀版本、條文 delta 對照、立法理由與行政命令">
<meta name="robots" content="noindex,nofollow">
<style>
  body{{font-family:"Noto Sans TC","Inter",sans-serif;background:#fafaf7;color:#0a0a0a;line-height:1.7;font-size:16px;margin:0}}
  .container{{max-width:980px;margin:0 auto;padding:48px 24px}}
  h1{{font-size:32px;font-weight:900;margin-bottom:14px;border-bottom:4px solid #0a0a0a;padding-bottom:14px}}
  h2{{font-size:22px;font-weight:800;margin:32px 0 14px;border-left:6px solid #1E40AF;padding-left:14px}}
  h3{{font-size:18px;font-weight:700;margin:18px 0 8px}}
  .nav{{font-size:14px;margin-bottom:24px}}
  .nav a{{color:#8B2631;text-decoration:none;border-bottom:1px solid #ccc;margin-right:14px}}
  .meta{{background:#f3f0e8;padding:14px 18px;margin:14px 0;border-radius:4px;font-size:14px}}
  .version-card{{background:white;border:1px solid #ccc;padding:16px 20px;margin:14px 0;border-radius:4px}}
  .version-tag{{display:inline-block;font-size:11px;padding:2px 8px;border-radius:10px;background:#1E40AF;color:white}}
  .current-tag{{background:#65a30d}}
  .change-block{{margin:12px 0;padding:12px;background:#fafaf7;border-left:3px solid #ccc}}
  .change-type{{display:inline-block;font-size:11px;padding:2px 6px;border-radius:3px;color:white;font-weight:600}}
  .text-diff{{font-size:13px;font-family:"SF Mono",monospace;margin:6px 0;padding:8px;background:white;border:1px solid #eee;white-space:pre-wrap}}
  .text-before{{border-left:3px solid #8B2631;background:#fff7f7}}
  .text-after{{border-left:3px solid #65a30d;background:#f7fff7}}
  table{{width:100%;border-collapse:collapse;font-size:13px;margin:14px 0}}
  th,td{{border:1px solid #ccc;padding:8px 10px;text-align:left;vertical-align:top}}
  th{{background:#f3f0e8}}
  .footer{{margin-top:60px;padding-top:24px;border-top:1px solid #ccc;font-size:13px;color:#666}}
</style>
</head>
<body>
<div class="container">
<div class="nav"><a href="../index.html">← 回首頁</a> · <a href="index.html">所有法律</a></div>

<h1>{name} 修法歷程</h1>

<div class="meta">
  <strong>全國法規 pcode：</strong>{pcode}
  <strong>制定公布：</strong>{enacted_date}
  <strong>主管機關：</strong>{primary_agency}<br>
  <strong>對應兩公約條文：</strong>{covers_articles}
  <strong>對應 PI：</strong>{related_pi}
</div>

<h2>歷次版本（{n_versions}）</h2>
{versions_html}

<h2>修法事件（{n_amendments}）</h2>
{amendments_html}

<h2>附屬行政命令／施行細則</h2>
<table>
<thead><tr><th>名稱</th><th>類型</th><th>公布日</th><th>機關</th><th>連結</th></tr></thead>
<tbody>{orders_html}</tbody>
</table>

<div class="footer">
最後更新：2026-04-30｜© 2026 國教行動聯盟｜CC BY-SA 4.0<br>
原始 SQLite：<code>data/two_cov.db</code> 之 law / law_version / law_article_change / law_amendment / executive_order 表
</div>
</div>
</body>
</html>
"""


def render_versions(conn, law_id: str) -> tuple[str, int]:
    cur = conn.execute(
        """SELECT version_id, version_label, promulgated_date, effective_date,
                  full_text_url, legislative_reason, is_current
           FROM law_version WHERE law_id=? ORDER BY promulgated_date""",
        (law_id,),
    )
    rows = cur.fetchall()
    out = []
    for v_id, label, prom, effect, url, reason, current in rows:
        tag_class = "current-tag" if current else "version-tag"
        tag_text = "現行" if current else label
        url_html = f'<br><small><a href="{html.escape(url)}" target="_blank">[ 全國法規資料庫 ]</a></small>' if url else ""
        out.append(f'<div class="version-card"><span class="{tag_class}">{html.escape(tag_text)}</span>')
        out.append(f' <strong>{html.escape(prom)}</strong>')
        if effect and effect != prom:
            out.append(f' <small>（施行 {html.escape(effect)}）</small>')
        out.append(f' <small style="color:#888">{html.escape(v_id)}</small>')
        if reason:
            out.append(f'<p style="font-size:14px;margin:8px 0">{html.escape(reason)}</p>')
        out.append(url_html)

        # 列條文變動
        changes = conn.execute(
            """SELECT article_number, change_type, text_before, text_after, reason, related_co
               FROM law_article_change WHERE version_id=?""",
            (v_id,),
        ).fetchall()
        for art, c_type, before, after, c_reason, related_co in changes:
            color = CHANGE_COLOR.get(c_type, "#666")
            out.append(f'<div class="change-block">')
            out.append(f'<span class="change-type" style="background:{color}">{html.escape(c_type)}</span> ')
            out.append(f'<strong>{html.escape(art)}</strong>')
            if before:
                out.append(f'<div class="text-diff text-before">[ 修正前 ]<br>{html.escape(before)}</div>')
            if after:
                out.append(f'<div class="text-diff text-after">[ 修正後 ]<br>{html.escape(after)}</div>')
            if c_reason:
                out.append(f'<div style="font-size:13px;color:#444;margin-top:6px">理由：{html.escape(c_reason)}</div>')
            if related_co:
                out.append(f'<div style="font-size:12px;color:#666">對應 CO：{html.escape(related_co)}</div>')
            out.append('</div>')
        out.append('</div>')
    return "\n".join(out), len(rows)


def render_amendments(conn, law_id: str) -> tuple[str, int]:
    cur = conn.execute(
        """SELECT amendment_id, third_reading, promulgated, proposer_summary,
                  contention_level, summary_before, summary_after, key_changes, triggered_by_co
           FROM law_amendment WHERE law_id=? ORDER BY third_reading""",
        (law_id,),
    )
    rows = cur.fetchall()
    if not rows:
        return "<p>（尚無修法事件記錄）</p>", 0
    out = ['<table><thead><tr><th>修法日</th><th>提案</th><th>爭議度</th><th>關鍵變動</th><th>觸發來源</th></tr></thead><tbody>']
    for a_id, tr, prom, prop, conten, sb, sa, key, trig in rows:
        out.append(f'<tr>')
        out.append(f'<td>{html.escape(tr or prom or "")}<br><small>{html.escape(a_id)}</small></td>')
        out.append(f'<td>{html.escape(prop or "")}</td>')
        out.append(f'<td>{html.escape(conten or "")}</td>')
        out.append(f'<td>{html.escape((key or "")[:200])}</td>')
        out.append(f'<td>{html.escape(trig or "")}</td>')
        out.append('</tr>')
    out.append('</tbody></table>')
    return "\n".join(out), len(rows)


def render_orders(conn, law_id: str) -> str:
    cur = conn.execute(
        "SELECT order_name, order_type, promulgated_date, issuing_agency, full_text_url FROM executive_order WHERE parent_law_id=?",
        (law_id,),
    )
    rows = cur.fetchall()
    if not rows:
        return '<tr><td colspan="5" style="text-align:center;color:#666">（尚無記錄）</td></tr>'
    out = []
    for name, typ, date, agency, url in rows:
        link = f'<a href="{html.escape(url)}" target="_blank">[ 連結 ]</a>' if url else ""
        out.append(f'<tr><td>{html.escape(name)}</td><td>{html.escape(typ or "")}</td><td>{html.escape(date or "")}</td><td>{html.escape(agency or "")}</td><td>{link}</td></tr>')
    return "\n".join(out)


def render_one(conn, law_id: str, slug: str):
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    info = conn.execute(
        "SELECT law_name_zh, law_pcode, enacted_date, primary_agency, covers_articles, related_pi FROM law WHERE law_id=?",
        (law_id,),
    ).fetchone()
    if not info:
        print(f"  - 跳過 {law_id}（無資料）")
        return
    versions_html, n_v = render_versions(conn, law_id)
    amends_html, n_a = render_amendments(conn, law_id)
    orders_html = render_orders(conn, law_id)
    final = HTML_TPL.format(
        name=html.escape(info[0]),
        pcode=html.escape(info[1] or ""),
        enacted_date=html.escape(info[2] or ""),
        primary_agency=html.escape(info[3] or ""),
        covers_articles=html.escape(info[4] or ""),
        related_pi=html.escape(info[5] or ""),
        n_versions=n_v,
        n_amendments=n_a,
        versions_html=versions_html,
        amendments_html=amends_html,
        orders_html=orders_html,
    )
    out_path = OUT_DIR / f"{slug}.html"
    out_path.write_text(final, encoding="utf-8")
    print(f"  ✓ {out_path}（{n_v} versions / {n_a} amendments）")


SLUG_MAP = {
    "兩公約施行法": "two_covenants_act",
    "學生輔導法": "student_counseling_act",
    "司法院釋字 748 號施行法": "748_act",
    "748 同婚施行法": "748_act",
    "性別平等教育法": "gender_equity_education_act",
    "自殺防治法": "suicide_prevention_act",
    "集會遊行法": "assembly_parade_act",
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--law-id", help="如 L001")
    parser.add_argument("--slug", help="URL slug")
    args = parser.parse_args()

    conn = sqlite3.connect(DB)
    if args.all:
        cur = conn.execute("SELECT law_id, law_name_zh FROM law")
        for law_id, name in cur.fetchall():
            slug = SLUG_MAP.get(name, name.lower().replace(" ", "_"))
            render_one(conn, law_id, slug)
    elif args.law_id and args.slug:
        render_one(conn, args.law_id, args.slug)
    else:
        parser.error("須提供 --all 或（--law-id + --slug）")
    conn.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
