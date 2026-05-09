#!/usr/bin/env python3
"""
SQLite → JSON API 匯出(供前端互動 / 第三方使用)

輸出:_public/api/{pi,trace,laws,timeline,coverage}.json
全部 CC BY 4.0 授權

Usage:
    python3 scripts/two_cov_export_api.py
"""
from __future__ import annotations
import json
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "data" / "two_cov.db"
OUT_DIR = ROOT / "_public" / "api"

META = {
    "platform": "兩公約監督平台 / Two Covenants Watch Taiwan",
    "version": "v0.2-beta",
    "license": "CC BY-SA 4.0",
    "maintainer": "AABE 國教行動聯盟",
    "source": "https://github.com/naer-tw/covenants-watch",
}


def fetch_all(conn, sql: str) -> list[dict]:
    conn.row_factory = sqlite3.Row
    cur = conn.execute(sql)
    return [dict(r) for r in cur.fetchall()]


def export_pi(conn) -> dict:
    return {
        "_meta": {**META, "endpoint": "pi", "description": "16 PI 議題卡 metadata"},
        "items": fetch_all(conn,
            "SELECT pi_id, title, block, priority, status, covenant, co_referenced, keywords, file_path FROM policy_issue ORDER BY pi_id"
        ),
    }


def export_trace(conn) -> dict:
    return {
        "_meta": {**META, "endpoint": "trace", "description": "因果脈絡追溯系統 (actor / event / causal_link / outcome_indicator)"},
        "actors": fetch_all(conn, "SELECT * FROM actor ORDER BY actor_id"),
        "events": fetch_all(conn, "SELECT * FROM event ORDER BY event_date"),
        "causal_links": fetch_all(conn, "SELECT * FROM causal_link ORDER BY chain_depth, from_event"),
        "outcome_indicators": fetch_all(conn, "SELECT * FROM outcome_indicator ORDER BY indicator_id"),
    }


def export_laws(conn) -> dict:
    return {
        "_meta": {**META, "endpoint": "laws", "description": "6 部核心法律修法歷程 + 條文 delta"},
        "laws": fetch_all(conn, "SELECT * FROM law ORDER BY law_id"),
        "versions": fetch_all(conn, "SELECT * FROM law_version ORDER BY law_id, promulgated_date"),
        "article_changes": fetch_all(conn, "SELECT * FROM law_article_change ORDER BY change_id"),
        "amendments": fetch_all(conn, "SELECT * FROM law_amendment ORDER BY third_reading"),
        "executive_orders": fetch_all(conn, "SELECT * FROM executive_order ORDER BY promulgated_date"),
    }


def export_timeline(conn) -> dict:
    """混合 events + amendments 的全平台時間軸"""
    events = fetch_all(conn, """
        SELECT 'event' AS source, event_id AS id, event_date AS date, event_type, title, summary,
               issue_tags, related_pi, related_article, actor_id, is_positive_outcome
        FROM event
    """)
    amendments = fetch_all(conn, """
        SELECT 'amendment' AS source, amendment_id AS id, COALESCE(third_reading, promulgated) AS date,
               'legislation' AS event_type,
               (SELECT law_name_zh FROM law WHERE law_id = la.law_id) AS title,
               key_changes AS summary, NULL AS issue_tags, NULL AS related_pi,
               NULL AS related_article, NULL AS actor_id, NULL AS is_positive_outcome
        FROM law_amendment la
    """)
    timeline = sorted(events + amendments, key=lambda r: r["date"] or "")
    return {
        "_meta": {**META, "endpoint": "timeline", "description": "混合事件與修法之全平台時序軸"},
        "items": timeline,
    }


def export_coverage(conn) -> dict:
    """16 PI status + 法律覆蓋 + 條文盤點"""
    pi = fetch_all(conn, "SELECT pi_id, title, status FROM policy_issue ORDER BY pi_id")
    laws_count = fetch_all(conn, """
        SELECT l.law_id, l.law_name_zh,
               (SELECT COUNT(*) FROM law_version WHERE law_id=l.law_id) AS n_versions,
               (SELECT COUNT(*) FROM law_article_change lac
                JOIN law_version lv ON lac.version_id=lv.version_id
                WHERE lv.law_id=l.law_id) AS n_changes
        FROM law l
    """)
    return {
        "_meta": {**META, "endpoint": "coverage", "description": "PI 狀態 / 法律覆蓋 / 條文盤點 統計"},
        "pi_status": pi,
        "laws_count": laws_count,
        "totals": {
            "pi": len(pi),
            "partial_evidence": sum(1 for p in pi if str(p["status"]).startswith("partial")),
            "actor": _count(conn, "actor"),
            "event": _count(conn, "event"),
            "causal_link": _count(conn, "causal_link"),
            "outcome_indicator": _count(conn, "outcome_indicator"),
            "law": _count(conn, "law"),
            "law_version": _count(conn, "law_version"),
            "law_article_change": _count(conn, "law_article_change"),
            "law_amendment": _count(conn, "law_amendment"),
            "concluding_observation": _count(conn, "concluding_observation"),
            "nap_action": _count(conn, "nap_action"),
            "legislative_citation": _count(conn, "legislative_citation"),
        },
    }


def _count(conn, table: str) -> int:
    return conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]


def export_index(conn) -> dict:
    """API 入口頁,列所有可用 endpoint"""
    return {
        **META,
        "description": "兩公約監督平台公開 API · 全部資料採 CC BY-SA 4.0 授權",
        "endpoints": [
            {"name": "pi", "url": "pi.json", "description": "16 PI 議題卡 metadata"},
            {"name": "trace", "url": "trace.json", "description": "因果脈絡追溯系統(actor/event/causal_link/outcome)"},
            {"name": "laws", "url": "laws.json", "description": "6 部核心法律修法歷程 + 條文 delta"},
            {"name": "timeline", "url": "timeline.json", "description": "混合事件與修法之全平台時序軸"},
            {"name": "coverage", "url": "coverage.json", "description": "PI 狀態 + 法律覆蓋 + 統計"},
            {"name": "search-index", "url": "search-index.json", "description": "fuse.js 全文搜尋索引"},
        ],
        "schema": {
            "actor": "actor_id, actor_type, name, affiliation, position_spectrum, active_period, is_anonymized",
            "event": "event_id, event_date, event_type, issue_tags, actor_id, title, summary, related_pi, related_co, related_article, is_positive_outcome",
            "causal_link": "from_event, to_event, link_type, evidence_strength, chain_depth, counter_evidence, multi_causal_note",
            "outcome_indicator": "indicator_id, event_id, metric_name, before_value, after_value, direction, confounders",
            "law": "law_id, law_name_zh, law_pcode, enacted_date, primary_agency, covers_articles",
            "law_article_change": "change_id, version_id, article_number, change_type, text_before, text_after, reason, related_co, related_article",
        },
        "usage_examples": {
            "fetch all PI": "fetch('api/pi.json').then(r=>r.json()).then(d=>console.log(d.items))",
            "filter events by issue tag": "data.events.filter(e => e.issue_tags && e.issue_tags.includes('廢死'))",
            "join causal_link with events": "links.map(l => ({...l, from: events.find(e=>e.event_id===l.from_event), to: events.find(e=>e.event_id===l.to_event)}))",
        },
        "license_text": "Released under Creative Commons Attribution-ShareAlike 4.0. You are free to share and adapt; please credit AABE 國教行動聯盟 and link back to this platform.",
    }


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB)

    exports = {
        "index.json": export_index(conn),
        "pi.json": export_pi(conn),
        "trace.json": export_trace(conn),
        "laws.json": export_laws(conn),
        "timeline.json": export_timeline(conn),
        "coverage.json": export_coverage(conn),
    }
    for name, data in exports.items():
        path = OUT_DIR / name
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        size = path.stat().st_size
        print(f"  ✓ api/{name}  {size:,} bytes")

    conn.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
