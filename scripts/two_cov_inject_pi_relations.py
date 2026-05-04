#!/usr/bin/env python3
"""
為 _public/issues/PI-XX.html 注入「資料庫關聯」段落 (idempotent)
- 從 db 抓 related events / actors / co_paragraphs
- 透過 issue_tags / related_pi 比對

Usage:
    python3 scripts/two_cov_inject_pi_relations.py
"""
from __future__ import annotations
import re
import sqlite3
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "data" / "two_cov.db"
ISSUES_DIR = ROOT / "_public" / "issues"

MARKER_BEGIN = "<!-- pi-relations-begin -->"
MARKER_END = "<!-- pi-relations-end -->"

# PI → 議題標籤主題對照
PI_TO_TAGS = {
    "PI-01": ["兩公約施行"],
    "PI-02": [],  # 整體歷史
    "PI-03": [],  # 第四屆審查
    "PI-04": ["移工", "漁工"],  # 國際比較,涵蓋移工
    "PI-05": [],  # NAP
    "PI-06": [],  # NAP II
    "PI-07": [],  # NHRC
    "PI-08": ["宗教自由", "良心拒服兵役"],
    "PI-09": ["言論自由", "媒體換照", "媒體多元", "反滲透", "平台監管"],
    "PI-10": ["教育權", "選擇權", "性平教育", "家長教育選擇權"],
    "PI-11": ["兒少自殺", "健康權", "菸害", "校園菸毒"],
    "PI-12": [],  # 條文援引
    "PI-13": [],  # 立法院公報
    "PI-14": [],  # 民間代表團
    "PI-15": [],  # 人權白皮書
    "PI-16": [],  # 教科書
}


def get_relations(conn, pi_id: str) -> dict:
    """從 db 抽取與 pi_id 相關之資料"""
    rel = {"events": [], "actors": [], "co_paragraphs": [], "law_changes": []}

    # 1) related_pi 直接命中之 events
    for r in conn.execute("""
        SELECT event_id, event_date, event_type, title, summary, actor_id, issue_tags
        FROM event WHERE related_pi LIKE ?
        ORDER BY event_date DESC
    """, (f"%{pi_id}%",)):
        rel["events"].append(dict(zip([d[0] for d in conn.execute("PRAGMA table_info(event)").fetchall()[:7]],
                                       (r[0], r[1], r[2], r[3], r[4], r[5], r[6]))))

    # 重新乾淨抽:
    rel["events"] = []
    cur = conn.execute("SELECT event_id, event_date, event_type, title, actor_id, issue_tags FROM event WHERE related_pi LIKE ? ORDER BY event_date DESC LIMIT 20", (f"%{pi_id}%",))
    for r in cur:
        rel["events"].append({
            "event_id": r[0], "event_date": r[1], "event_type": r[2],
            "title": r[3], "actor_id": r[4], "issue_tags": r[5],
        })

    # 2) issue_tags 命中之 events(補充)
    tags = PI_TO_TAGS.get(pi_id, [])
    seen_ids = {e["event_id"] for e in rel["events"]}
    for tag in tags:
        cur = conn.execute("SELECT event_id, event_date, event_type, title, actor_id, issue_tags FROM event WHERE issue_tags LIKE ? ORDER BY event_date DESC LIMIT 30", (f"%{tag}%",))
        for r in cur:
            if r[0] in seen_ids:
                continue
            seen_ids.add(r[0])
            rel["events"].append({
                "event_id": r[0], "event_date": r[1], "event_type": r[2],
                "title": r[3], "actor_id": r[4], "issue_tags": r[5],
            })

    # 3) 涉入之 actors(去重)
    actor_ids = sorted({e["actor_id"] for e in rel["events"] if e["actor_id"]})
    for aid in actor_ids:
        a = conn.execute("SELECT actor_id, actor_type, name, position_spectrum FROM actor WHERE actor_id=?", (aid,)).fetchone()
        if a:
            rel["actors"].append({"actor_id": a[0], "actor_type": a[1], "name": a[2], "position": a[3]})

    # 4) co_paragraphs 命中(關鍵字搜)
    if tags:
        like_clauses = " OR ".join(["co_text LIKE ?" for _ in tags])
        params = [f"%{t}%" for t in tags]
        try:
            cur = conn.execute(
                f"SELECT co_id, cycle, paragraph_no, co_text FROM concluding_observation WHERE {like_clauses} LIMIT 5",
                params,
            )
            for r in cur:
                rel["co_paragraphs"].append({"co_id": r[0], "cycle": r[1], "para": r[2], "text": (r[3] or "")[:200]})
        except sqlite3.OperationalError:
            pass

    return rel


EVENT_TYPE_LABEL = {
    "shadow_report": "影子報告",
    "legislation": "立法",
    "govt_response": "政府回應",
    "court_ruling": "判決",
    "public_opinion": "公民倡議",
    "outcome": "結果指標",
    "intl_actor": "國際行動者",
    "co_paragraph": "結論性意見",
    "committee_question": "委員質詢",
}

ACTOR_TYPE_LABEL = {
    "ngo": "NGO",
    "govt_agency": "政府",
    "court": "法院",
    "committee_member": "國際委員",
    "legislator": "立委",
    "intl_actor": "國際組織",
    "academic": "學界",
    "private_media": "媒體",
    "media": "媒體",
    "industry_assoc": "產業",
    "public": "公眾",
}


def render_relations(pi_id: str, rel: dict) -> str:
    """產生 HTML 段落"""
    events = rel["events"]
    actors = rel["actors"]
    cos = rel["co_paragraphs"]

    if not events and not actors and not cos:
        return ""

    parts = [
        '\n<section style="margin-top:48px;padding:24px;background:#F1EFEA;border-left:3px solid #0E2238;border-radius:4px">',
        '<h2 style="font-family:\'Noto Serif TC\',serif;font-size:20px;color:#0E2238;margin-bottom:8px">資料庫關聯(動態)</h2>',
        '<p style="font-size:13px;color:#5C5C5C;margin-bottom:16px">本段由 <code style="background:#fff;padding:1px 6px;border-radius:2px">scripts/two_cov_inject_pi_relations.py</code> 自動從資料庫產生,涵蓋 events / actors / 結論性意見三類關聯。</p>',
    ]

    # actors 區
    if actors:
        parts.append('<h3 style="font-family:\'Noto Serif TC\',serif;font-size:15px;color:#0E2238;margin:14px 0 8px">涉入行動者(' + str(len(actors)) + ')</h3>')
        parts.append('<div style="display:flex;flex-wrap:wrap;gap:6px;margin-bottom:14px">')
        for a in actors[:30]:
            t_label = ACTOR_TYPE_LABEL.get(a["actor_type"] or "", a["actor_type"] or "")
            color = {"ngo": "#B5371F", "govt_agency": "#0E2238", "court": "#5D3A1A",
                     "committee_member": "#8B6F50", "legislator": "#44638A",
                     "intl_actor": "#8B6F50", "academic": "#4f4f4f",
                     "private_media": "#6d28d9", "media": "#6d28d9",
                     "industry_assoc": "#5C1A1B", "public": "#8A8A8A"}.get(a["actor_type"] or "", "#8A8A8A")
            parts.append(
                f'<span style="display:inline-flex;align-items:center;gap:4px;padding:3px 8px;background:#fff;border:1px solid #DDD8CD;border-radius:3px;font-size:12px;color:#1F1F1F">'
                f'<span style="font-family:Inter,sans-serif;font-size:9px;font-weight:600;letter-spacing:.05em;text-transform:uppercase;padding:1px 5px;border-radius:2px;background:{color};color:#fff">{t_label}</span>'
                f'{escape(a["name"] or "")}'
                f'</span>'
            )
        parts.append('</div>')
        parts.append('<p style="font-size:11.5px;color:#8A8A8A;margin-bottom:14px"><a href="../actors/index.html" style="color:#B5371F">→ 查看全部 107 位行動者</a></p>')

    # events 區
    if events:
        parts.append('<h3 style="font-family:\'Noto Serif TC\',serif;font-size:15px;color:#0E2238;margin:14px 0 8px">相關事件(' + str(len(events)) + ',含 ' + str(sum(1 for e in events if e["event_type"] == "shadow_report")) + ' 影子報告)</h3>')
        parts.append('<div style="background:#fff;border:1px solid #DDD8CD;border-radius:3px;padding:10px;max-height:360px;overflow-y:auto;font-size:12.5px;line-height:1.55">')
        for ev in events[:20]:
            et = ev["event_type"] or ""
            et_label = EVENT_TYPE_LABEL.get(et, et)
            et_color = {
                "shadow_report": "#B5371F", "legislation": "#0E2238",
                "govt_response": "#5D3A1A", "court_ruling": "#4f4f4f",
                "public_opinion": "#44638A", "outcome": "#2D5F3E",
                "intl_actor": "#6d28d9", "co_paragraph": "#5C1A1B",
            }.get(et, "#8B6F50")
            parts.append(
                f'<div style="padding:6px 0;border-bottom:1px dashed #DDD8CD">'
                f'<span style="font-family:Inter,sans-serif;font-size:10px;color:#8A8A8A;margin-right:6px">{escape(ev["event_date"] or "")}</span>'
                f'<span style="font-family:Inter,sans-serif;font-size:9px;font-weight:600;letter-spacing:.04em;text-transform:uppercase;padding:1px 5px;border-radius:2px;background:{et_color};color:#fff">{et_label}</span>'
                f'<div style="font-weight:600;color:#0E2238;margin-top:2px">{escape(ev["title"] or "")}</div>'
                f'</div>'
            )
        if len(events) > 20:
            parts.append(f'<p style="text-align:center;padding:8px;font-size:11.5px;color:#8A8A8A">…另 {len(events) - 20} 筆事件,請見 <a href="../api/timeline.json" style="color:#B5371F">timeline API</a></p>')
        parts.append('</div>')

    # 結論性意見區(若有)
    if cos:
        parts.append('<h3 style="font-family:\'Noto Serif TC\',serif;font-size:15px;color:#0E2238;margin:14px 0 8px">相關結論性意見</h3>')
        parts.append('<div style="font-size:12.5px;color:#1F1F1F;line-height:1.55">')
        for co in cos:
            parts.append(
                f'<div style="padding:6px 0;border-bottom:1px dashed #DDD8CD">'
                f'<strong>第{escape(str(co["cycle"] or ""))}屆 §{escape(str(co["para"] or ""))}</strong>:'
                f'{escape(co["text"])}…'
                f'</div>'
            )
        parts.append('</div>')

    parts.append('</section>')
    return "\n".join(parts)


def main() -> int:
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    count_inject = 0
    count_skip = 0

    for pi_num in range(1, 17):
        pi_id = f"PI-{pi_num:02d}"
        pi_html = ISSUES_DIR / f"{pi_id}.html"
        if not pi_html.exists():
            continue
        rel = get_relations(conn, pi_id)
        block = render_relations(pi_id, rel)
        if not block:
            count_skip += 1
            continue
        text = pi_html.read_text(encoding="utf-8")
        new_block = MARKER_BEGIN + block + "\n" + MARKER_END
        if MARKER_BEGIN in text:
            # idempotent 替換
            new_text = re.sub(
                re.escape(MARKER_BEGIN) + r".*?" + re.escape(MARKER_END),
                new_block,
                text, count=1, flags=re.DOTALL,
            )
        else:
            # 注入到 </main> 之前;若無 </main> 則注入到 </body> 之前
            if "</main>" in text:
                new_text = text.replace("</main>", new_block + "\n</main>", 1)
            else:
                new_text = text.replace("</body>", new_block + "\n</body>", 1)
        pi_html.write_text(new_text, encoding="utf-8")
        count_inject += 1
        print(f"  ✓ {pi_id}  events={len(rel['events'])}  actors={len(rel['actors'])}  cos={len(rel['co_paragraphs'])}")

    print(f"\n  inject: {count_inject} / skip(無關聯): {count_skip}")
    conn.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
