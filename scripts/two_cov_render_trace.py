#!/usr/bin/env python3
"""
渲染議題時序軸 HTML（_public/trace/{issue_slug}.html）

Usage:
    python3 scripts/two_cov_render_trace.py --issue 廢死 --slug death_penalty
    python3 scripts/two_cov_render_trace.py --all
"""
from __future__ import annotations
import argparse
import html
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "data" / "two_cov.db"
OUT_DIR = ROOT / "_public" / "trace"

EVENT_TYPE_COLOR = {
    "shadow_report": "#6d28d9",       # 紫
    "co_paragraph": "#0369A1",        # 藍
    "committee_question": "#0369A1",
    "govt_response": "#4338CA",
    "legislation": "#1E40AF",
    "court_ruling": "#8B2631",
    "outcome": "#D97706",             # 橘
    "public_opinion": "#65a30d",      # 綠
    "advocacy_campaign": "#6d28d9",
}

EVENT_TYPE_LABEL = {
    "shadow_report": "影子報告",
    "co_paragraph": "結論性意見",
    "committee_question": "委員提問",
    "govt_response": "政府回應",
    "legislation": "立法",
    "court_ruling": "司法",
    "outcome": "結果",
    "public_opinion": "民意",
    "advocacy_campaign": "倡議行動",
}

HTML_TPL = """<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{issue} 議題脈絡追溯 — 兩公約總檢討平台</title>
<meta name="description" content="{issue} 之完整時序鏈與因果脈絡（含反證 / 並列原因 / 警告）">
<meta name="robots" content="noindex,nofollow">
<style>
  body{{font-family:"Noto Sans TC","Inter",sans-serif;background:#fafaf7;color:#0a0a0a;line-height:1.7;font-size:16px;margin:0}}
  .container{{max-width:980px;margin:0 auto;padding:48px 24px}}
  h1{{font-size:32px;font-weight:900;margin-bottom:16px;border-bottom:4px solid #0a0a0a;padding-bottom:14px}}
  .stance{{background:#fef3c7;border:1px solid #d97706;padding:14px 18px;margin:18px 0;border-radius:4px;font-size:14px}}
  .nav{{font-size:14px;margin-bottom:24px}}
  .nav a{{color:#8B2631;text-decoration:none;border-bottom:1px solid #ccc;margin-right:14px}}
  .timeline{{position:relative;padding-left:32px;margin:32px 0}}
  .timeline::before{{content:"";position:absolute;left:8px;top:0;bottom:0;width:3px;background:#0a0a0a}}
  .event{{position:relative;margin:24px 0;background:white;border:1px solid #ccc;padding:14px 18px;border-radius:4px}}
  .event::before{{content:"";position:absolute;left:-30px;top:18px;width:14px;height:14px;border-radius:50%;background:#0a0a0a;border:3px solid #fafaf7}}
  .event-date{{font-size:13px;color:#666;font-variant-numeric:tabular-nums}}
  .event-type{{display:inline-block;font-size:11px;padding:2px 8px;border-radius:10px;color:white;margin-left:8px;letter-spacing:0.05em}}
  .event-actor{{font-size:13px;color:#444;margin:4px 0 6px}}
  .event-title{{font-size:17px;font-weight:700;margin:4px 0 6px}}
  .event-summary{{font-size:14px;color:#333}}
  .event-source{{font-size:12px;margin-top:6px}}
  .event-source a{{color:#6d28d9;text-decoration:none}}
  h2{{font-size:22px;font-weight:800;margin:36px 0 14px;border-left:6px solid #2FA598;padding-left:14px}}
  table{{width:100%;border-collapse:collapse;font-size:13px;margin:14px 0}}
  th,td{{border:1px solid #ccc;padding:8px 10px;text-align:left;vertical-align:top}}
  th{{background:#f3f0e8}}
  .warn-cell{{background:#fff7ed}}
  .footer{{margin-top:60px;padding-top:24px;border-top:1px solid #ccc;font-size:13px;color:#666}}
  .red-line{{background:#fef2f2;border-left:4px solid #8B2631;padding:12px 16px;margin:18px 0;font-size:14px}}
</style>
</head>
<body>
<div class="container">
<div class="nav">
  <a href="../index.html">← 回首頁</a>
  <a href="../about.html">關於</a>
  <a href="../methodology.html">方法</a>
</div>

<h1>「{issue}」議題脈絡追溯</h1>

<div class="red-line">
<strong>本平台脈絡追溯設計紅線（5 條）</strong>：<br>
1. 稱「脈絡追溯」非「責任追溯」｜ 2. 每個歸因附反證 ｜ 3. 因果鏈不超過 3 層 ｜ 4. 正反結果並陳 ｜ 5. 論述與責任歸屬嚴格分離
</div>

<h2>一、時序鏈（{n_events} 個事件）</h2>

<div class="timeline">
{events_html}
</div>

<h2>二、因果關係（{n_links} 條）</h2>

<table>
<thead><tr><th>從</th><th>關係</th><th>到</th><th>強度</th><th>反證 / 反事實</th><th>並列原因</th></tr></thead>
<tbody>
{links_html}
</tbody>
</table>

<h2>三、行動者立場光譜</h2>
<table>
<thead><tr><th>行動者</th><th>類型</th><th>立場</th><th>活躍期</th></tr></thead>
<tbody>
{actors_html}
</tbody>
</table>

<h2>四、結果指標（含混淆變項）</h2>
<table>
<thead><tr><th>指標</th><th>變化前</th><th>變化後</th><th>方向</th><th>混淆變項</th></tr></thead>
<tbody>
{outcomes_html}
</tbody>
</table>

<div class="stance">
<strong>本頁立場聲明</strong>：本頁為「<em>論述脈絡記錄</em>」，<strong>不是責任歸屬判決</strong>。
所有事件之因果連結附反證欄位 + 並列原因欄位，讀者應據此自行評估。
任何單向歸因（「某 NGO 造成某結果」）均非本平台立場。
</div>

<div class="footer">
最後更新：2026-04-30｜© 2026 國教行動聯盟｜CC BY-SA 4.0<br>
原始 SQLite：<code>data/two_cov.db</code> 之 actor / event / causal_link / outcome_indicator 表
</div>
</div>
</body>
</html>
"""


def render_events(conn, issue: str) -> tuple[str, int]:
    cur = conn.execute(
        """SELECT e.event_date, e.event_type, COALESCE(a.name,'—'), e.title,
                  e.summary, e.source_url, e.event_id, e.is_positive_outcome
           FROM event e LEFT JOIN actor a ON e.actor_id=a.actor_id
           WHERE e.issue_tags LIKE ?
           ORDER BY e.event_date""",
        (f"%{issue}%",),
    )
    rows = cur.fetchall()
    out = []
    for date, typ, actor, title, summary, url, eid, positive in rows:
        color = EVENT_TYPE_COLOR.get(typ, "#666")
        label = EVENT_TYPE_LABEL.get(typ, typ)
        positive_tag = ""
        if positive == 1:
            positive_tag = ' <span style="color:#65a30d;font-size:11px">[正面]</span>'
        elif positive == 0:
            positive_tag = ' <span style="color:#8B2631;font-size:11px">[負面]</span>'
        out.append(f'''
<div class="event">
  <span class="event-date">{html.escape(date)}</span>
  <span class="event-type" style="background:{color}">{label}</span>
  {positive_tag}
  <div class="event-actor">{html.escape(actor)}｜<small style="color:#888">{html.escape(eid)}</small></div>
  <div class="event-title">{html.escape(title)}</div>
  <div class="event-summary">{html.escape(summary or "")}</div>
  <div class="event-source">{f'<a href="{html.escape(url)}" target="_blank">[ 來源 ]</a>' if url else ""}</div>
</div>''')
    return "\n".join(out), len(rows)


def render_links(conn, issue: str) -> tuple[str, int]:
    cur = conn.execute(
        """SELECT cl.from_event, cl.link_type, cl.to_event, cl.evidence_strength,
                  cl.counter_evidence, cl.multi_causal_note,
                  e1.title AS from_title, e2.title AS to_title
           FROM causal_link cl
           JOIN event e1 ON cl.from_event=e1.event_id
           JOIN event e2 ON cl.to_event=e2.event_id
           WHERE e1.issue_tags LIKE ? OR e2.issue_tags LIKE ?
           ORDER BY cl.chain_depth, cl.from_event""",
        (f"%{issue}%", f"%{issue}%"),
    )
    rows = cur.fetchall()
    out = []
    for f_e, l_type, t_e, strength, counter, multi, f_t, t_t in rows:
        warn = ""
        if strength == "inferred":
            warn = ' <span style="color:#D97706;font-size:11px">[ 推論 ]</span>'
        elif strength == "contested":
            warn = ' <span style="color:#D97706;font-size:11px">[ 爭議 ]</span>'
        cell_class = "warn-cell" if strength in ("inferred", "contested") else ""
        out.append(f'''<tr class="{cell_class}">
  <td><small>{html.escape(f_e)}</small><br>{html.escape(f_t[:30])}</td>
  <td>{html.escape(l_type)}</td>
  <td><small>{html.escape(t_e)}</small><br>{html.escape(t_t[:30])}</td>
  <td>{html.escape(strength)}{warn}</td>
  <td>{html.escape(counter or "—")}</td>
  <td>{html.escape(multi or "—")}</td>
</tr>''')
    return "\n".join(out), len(rows)


def render_actors(conn, issue: str) -> str:
    cur = conn.execute(
        """SELECT DISTINCT a.name, a.actor_type, a.position_spectrum, a.active_period
           FROM actor a JOIN event e ON e.actor_id=a.actor_id
           WHERE e.issue_tags LIKE ?
           ORDER BY a.actor_type, a.name""",
        (f"%{issue}%",),
    )
    rows = cur.fetchall()
    out = []
    for name, typ, pos, period in rows:
        out.append(f'<tr><td>{html.escape(name)}</td><td>{html.escape(typ)}</td><td>{html.escape(pos or "")}</td><td>{html.escape(period or "")}</td></tr>')
    return "\n".join(out)


def render_outcomes(conn, issue: str) -> str:
    cur = conn.execute(
        """SELECT oi.metric_name, oi.before_value, oi.before_year, oi.after_value, oi.after_year,
                  oi.direction, oi.confounders
           FROM outcome_indicator oi
           JOIN event e ON oi.event_id=e.event_id
           WHERE e.issue_tags LIKE ?""",
        (f"%{issue}%",),
    )
    rows = cur.fetchall()
    out = []
    for name, b_val, b_yr, a_val, a_yr, direction, confounders in rows:
        direction_color = {"improved": "#65a30d", "worsened": "#8B2631", "unchanged": "#666"}.get(direction, "#666")
        out.append(f'''<tr>
<td>{html.escape(name)}</td>
<td>{html.escape(b_val or "")} ({html.escape(b_yr or "")})</td>
<td>{html.escape(a_val or "")} ({html.escape(a_yr or "")})</td>
<td><span style="color:{direction_color}">{html.escape(direction or "")}</span></td>
<td>{html.escape(confounders or "")}</td>
</tr>''')
    return "\n".join(out)


def render_one(conn, issue: str, slug: str) -> Path:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    events_html, n_events = render_events(conn, issue)
    links_html, n_links = render_links(conn, issue)
    actors_html = render_actors(conn, issue)
    outcomes_html = render_outcomes(conn, issue)
    final = HTML_TPL.format(
        issue=html.escape(issue),
        n_events=n_events,
        n_links=n_links,
        events_html=events_html,
        links_html=links_html,
        actors_html=actors_html,
        outcomes_html=outcomes_html,
    )
    out_path = OUT_DIR / f"{slug}.html"
    out_path.write_text(final, encoding="utf-8")
    print(f"  ✓ {out_path}（{n_events} events / {n_links} links）")
    return out_path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--issue", help="議題（如：廢死）")
    parser.add_argument("--slug", help="URL slug（如：death_penalty）")
    parser.add_argument("--all", action="store_true", help="渲染所有已知議題")
    args = parser.parse_args()

    conn = sqlite3.connect(DB)

    if args.all:
        # 找全部 issue tag
        cur = conn.execute("SELECT DISTINCT issue_tags FROM event")
        all_issues = set()
        for (tags,) in cur.fetchall():
            if tags:
                import json
                try:
                    for t in json.loads(tags):
                        all_issues.add(t)
                except Exception:
                    pass
        slug_map = {
            "廢死": "death_penalty", "同性婚姻": "same_sex_marriage",
            "兒少自殺": "youth_suicide", "兩公約施行": "covenants_implementation",
            "宗教自由": "religious_freedom",
        }
        for issue in sorted(all_issues):
            # 計算事件數，跳過 < 3
            n = conn.execute(
                "SELECT COUNT(*) FROM event WHERE issue_tags LIKE ?",
                (f"%{issue}%",),
            ).fetchone()[0]
            if n < 3:
                print(f"  - 跳過「{issue}」({n} events < 3)")
                continue
            slug = slug_map.get(issue, issue.lower().replace(" ", "_"))
            render_one(conn, issue, slug)
    else:
        if not args.issue or not args.slug:
            parser.error("須提供 --issue 與 --slug，或用 --all")
        render_one(conn, args.issue, args.slug)

    conn.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
