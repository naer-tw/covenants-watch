#!/usr/bin/env python3
"""
建立全平台搜尋索引(JSON)

含 PI 議題卡 / trace events / law amendments / 議程透明度 / 結果指標。
輸出:_public/api/search-index.json
前端用 fuse.js 客戶端模糊搜尋。

Usage:
    python3 scripts/two_cov_build_search_index.py
"""
from __future__ import annotations
import json
import re
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "data" / "two_cov.db"
PI_DIR = ROOT / "data" / "policy_issues"
OUT = ROOT / "_public" / "api" / "search-index.json"


def index_policy_issues() -> list[dict]:
    out = []
    for md in sorted(PI_DIR.glob("PI-*.md")):
        text = md.read_text(encoding="utf-8")
        m_pi = re.search(r"^pi_id:\s*(.+)$", text, re.MULTILINE)
        m_title = re.search(r"^title:\s*(.+)$", text, re.MULTILINE)
        m_status = re.search(r"^status:\s*(.+)$", text, re.MULTILINE)
        m_block = re.search(r"^block:\s*(.+)$", text, re.MULTILINE)
        m_kw = re.search(r"^keywords:\s*\[(.+?)\]", text)
        body = re.sub(r"^---\n.*?\n---\n", "", text, flags=re.DOTALL)
        # 拿摘要(前 200 字)
        summary_match = re.search(r"##\s*摘要\s*\n+(.+?)(?=\n##\s|\Z)", body, re.DOTALL)
        summary = (summary_match.group(1).strip()[:300] if summary_match else "")

        pi_id = m_pi.group(1).strip() if m_pi else ""
        out.append({
            "type": "pi",
            "id": pi_id,
            "title": (m_title.group(1).strip() if m_title else ""),
            "summary": summary,
            "block": (m_block.group(1).strip() if m_block else ""),
            "status": (m_status.group(1).strip() if m_status else ""),
            "keywords": [k.strip() for k in m_kw.group(1).split(",")] if m_kw else [],
            "url": f"issues/{pi_id}.html",
        })
    return out


def index_events(conn) -> list[dict]:
    cur = conn.execute(
        """SELECT e.event_id, e.event_date, e.event_type, e.title, e.summary,
                  e.issue_tags, e.related_pi, e.related_co, e.related_article,
                  COALESCE(a.name, '—') AS actor_name
           FROM event e LEFT JOIN actor a ON e.actor_id = a.actor_id
           ORDER BY e.event_date DESC"""
    )
    out = []
    for row in cur.fetchall():
        eid, date, etype, title, summary, tags, pis, cos, arts, actor = row
        out.append({
            "type": "event",
            "id": eid,
            "title": title,
            "summary": (summary or "")[:300],
            "date": date,
            "event_type": etype,
            "actor": actor,
            "issue_tags": tags,
            "related_pi": pis,
            "related_article": arts,
            "url": f"trace/index.html#{eid}",
        })
    return out


def index_actors(conn) -> list[dict]:
    cur = conn.execute(
        """SELECT actor_id, actor_type, name, affiliation, position_spectrum, active_period
           FROM actor"""
    )
    return [{
        "type": "actor",
        "id": aid,
        "title": name,
        "summary": f"{actor_type} · {affiliation or ''} · {position or ''}",
        "actor_type": actor_type,
        "active_period": active or "",
        "url": f"trace/index.html#{aid}",
    } for aid, actor_type, name, affiliation, position, active in cur.fetchall()]


def index_laws(conn) -> list[dict]:
    out = []
    cur = conn.execute(
        "SELECT law_id, law_name_zh, law_pcode, enacted_date, primary_agency, covers_articles, note FROM law"
    )
    for lid, name, pcode, enacted, agency, covers, note in cur.fetchall():
        out.append({
            "type": "law",
            "id": lid,
            "title": name,
            "summary": (note or "")[:300],
            "pcode": pcode,
            "enacted": enacted,
            "agency": agency,
            "covers_articles": covers,
            "url": f"laws/{_law_slug(lid)}.html",
        })
    return out


def index_law_changes(conn) -> list[dict]:
    cur = conn.execute(
        """SELECT lac.change_id, lac.article_number, lac.change_type, lac.text_after,
                  lac.reason, lac.related_co, lac.related_article,
                  lv.law_id, lv.version_label, lv.promulgated_date,
                  l.law_name_zh
           FROM law_article_change lac
           JOIN law_version lv ON lac.version_id = lv.version_id
           JOIN law l ON lv.law_id = l.law_id"""
    )
    out = []
    for cid, art, ctype, text, reason, rco, rart, lid, vlabel, pdate, lname in cur.fetchall():
        out.append({
            "type": "law_change",
            "id": f"LAC-{cid}",
            "title": f"{lname} {art}({ctype}) · {pdate}",
            "summary": (text or "")[:200] + (" — " + (reason or "") if reason else ""),
            "law_id": lid,
            "version_label": vlabel,
            "article_number": art,
            "change_type": ctype,
            "url": f"laws/{_law_slug(lid)}.html",
        })
    return out


def index_outcomes(conn) -> list[dict]:
    cur = conn.execute(
        """SELECT indicator_id, metric_name, before_value, before_year, after_value, after_year,
                  direction, source_url
           FROM outcome_indicator"""
    )
    return [{
        "type": "outcome",
        "id": iid,
        "title": metric,
        "summary": f"{before or '—'}({byr or ''}) → {after or '—'}({ayr or ''}) · {direction or ''}",
        "direction": direction,
        "url": (src or "trace/index.html"),
    } for iid, metric, before, byr, after, ayr, direction, src in cur.fetchall()]


_LAW_SLUG_MAP = {
    "L001": "two_covenants_act",
    "L002": "student_counseling_act",
    "L003": "748_act",
    "L004": "gender_equity_education_act",
    "L005": "suicide_prevention_act",
    "L006": "assembly_parade_act",
}


def _law_slug(lid: str) -> str:
    return _LAW_SLUG_MAP.get(lid, lid.lower())


def main() -> int:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB)
    items = []
    items.extend(index_policy_issues())
    items.extend(index_events(conn))
    items.extend(index_actors(conn))
    items.extend(index_laws(conn))
    items.extend(index_law_changes(conn))
    items.extend(index_outcomes(conn))

    OUT.write_text(
        json.dumps({
            "version": "v0.2-beta",
            "generated_at": "2026-05-04",
            "total": len(items),
            "by_type": _count_by_type(items),
            "items": items,
        }, ensure_ascii=False, indent=0),
        encoding="utf-8",
    )
    print(f"  ✓ {OUT}")
    print(f"  Total: {len(items)} items")
    print(f"  By type: {_count_by_type(items)}")
    return 0


def _count_by_type(items: list[dict]) -> dict:
    from collections import Counter
    return dict(Counter(i["type"] for i in items))


if __name__ == "__main__":
    raise SystemExit(main())
