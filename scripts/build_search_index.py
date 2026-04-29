#!/usr/bin/env python3
"""build_search_index.py — 把 passage + PI 卡片 + 政策建議 預建為 JSON 索引。

Wave 71:對應藍圖 §使用者介面之全局關聯式搜尋。

輸出:_public/search-index.json
  {
    "version": "2026-04-27",
    "items": [
      {"id": "...", "type": "issue|passage|advocacy|case",
       "title": "...", "url": "...", "snippet": "...",
       "tags": ["PI-01", "CRC-19"], "cluster": "E"}
    ]
  }
"""
from __future__ import annotations

import json
import re
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "data" / "crw.db"
OUT = ROOT / "_public" / "search-index.json"


def read_pi_cards() -> list[dict]:
    items = []
    for f in sorted((ROOT / "data" / "policy_issues").glob("PI-*.md")):
        text = f.read_text(encoding="utf-8")
        m = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
        if not m:
            continue
        fm = m.group(1)
        body = text[m.end():]

        def grab(key, default=""):
            mt = re.search(rf"^{key}:\s*(.+?)$", fm, re.MULTILINE)
            return mt.group(1).strip() if mt else default

        title_zh = grab("title_zh")
        cluster = grab("cluster")
        crc_articles = grab("crc_articles", "[]")
        co_paragraphs = grab("co_paragraphs", "[]")
        pi_id = f.stem.split("_")[0]

        # 抓「議題摘要」第一段
        sm = re.search(r"##\s+[一二三四五六七八九]+、\s*議題摘要.*?\n(.*?)(?=^##\s|\Z)",
                       body, re.MULTILINE | re.DOTALL)
        snippet = sm.group(1).strip()[:240] if sm else ""

        items.append({
            "id": pi_id,
            "type": "issue",
            "title": f"{pi_id} {title_zh}",
            "url": f"issues/{pi_id}.html",
            "snippet": re.sub(r"\s+", " ", snippet),
            "tags": [pi_id] + [c.strip(" []") for c in crc_articles.strip("[]").split(",") if c.strip()][:5],
            "cluster": cluster,
            "search_text": (title_zh + " " + snippet + " " + crc_articles + " " + co_paragraphs).lower(),
        })
    return items


def read_passages_from_db() -> list[dict]:
    if not DB.exists():
        return []
    conn = sqlite3.connect(str(DB))
    cur = conn.execute(
        "SELECT passage_id, paragraph_no, summary_80w, raw_text, version_id FROM passage"
    )
    items = []
    for pid, heading, summary, raw, vid in cur.fetchall():
        # 從 version_id 推回原始 file_path
        cv = conn.execute(
            "SELECT file_path FROM document_version WHERE version_id = ?", (vid,)
        ).fetchone()
        file_path = cv[0] if cv else ""
        items.append({
            "id": pid,
            "type": "passage",
            "title": heading or "(無標題段落)",
            "url": file_path,
            "snippet": (summary or raw[:160] or "").replace("\n", " "),
            "tags": [],
            "cluster": "",
            "search_text": (heading + " " + raw).lower(),
        })
    conn.close()
    return items


def read_advocacy() -> list[dict]:
    items = []
    for f in sorted((ROOT / "data" / "advocacy_actions").glob("*.md")):
        text = f.read_text(encoding="utf-8")
        m = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
        if not m:
            continue
        fm = m.group(1)
        title_match = re.search(r"^title:\s*(.+?)$", fm, re.MULTILINE)
        if not title_match:
            continue
        title = title_match.group(1).strip()
        body = text[m.end():][:480]
        items.append({
            "id": f.stem,
            "type": "advocacy",
            "title": title,
            "url": f"advocacy/{f.stem}.html",
            "snippet": re.sub(r"\s+", " ", body),
            "tags": [],
            "cluster": "",
            "search_text": (title + " " + body).lower(),
        })
    return items


def read_nap_actions() -> list[dict]:
    """Wave 90:NAP 行動清單也納入搜尋索引。"""
    if not DB.exists():
        return []
    conn = sqlite3.connect(str(DB))
    rows = conn.execute(
        "SELECT action_id, theme_name, action_text, kpi, lead_agency, "
        "aabe_assessment, related_pi, nap_period FROM nap_action "
        "WHERE action_id != 'NAP2-PLACEHOLDER'"
    ).fetchall()
    conn.close()
    items = []
    for action_id, theme, action, kpi, agency, assess, related_pi, period in rows:
        items.append({
            "id": action_id,
            "type": "nap",
            "title": f"{action_id} — {action[:50]}",
            "url": "nap.html",
            "snippet": f"第{period}期 {theme} ‧ KPI: {kpi or '—'} ‧ 主管: {agency or '—'} ‧ AABE: {assess or '—'}",
            "tags": [action_id, f"NAP-{period}"],
            "cluster": "",
            "search_text": (action + " " + (kpi or "") + " " + theme + " " + (agency or "") + " " + (related_pi or "")).lower(),
        })
    return items


def read_nhrc_indicators() -> list[dict]:
    """Wave 90:NHRC 239 指標也納入搜尋索引。"""
    if not DB.exists():
        return []
    conn = sqlite3.connect(str(DB))
    try:
        rows = conn.execute(
            "SELECT indicator_id, name_zh, pillar, latest_value, related_pi "
            "FROM nhrc_indicator"
        ).fetchall()
    except sqlite3.OperationalError:
        # nhrc_indicator 表可能尚未建立
        conn.close()
        return []
    conn.close()
    items = []
    for ind_id, name, pillar, value, related_pi in rows:
        items.append({
            "id": ind_id,
            "type": "nhrc_indicator",
            "title": f"{ind_id} {name[:50]}",
            "url": "nap.html#nhrc-indicators",
            "snippet": f"NHRC 監測 ‧ 支柱: {pillar or '—'} ‧ 最新數值: {value or '--'}",
            "tags": [ind_id, "NHRC-239"],
            "cluster": "",
            "search_text": (name + " " + (pillar or "") + " " + (value or "") + " " + (related_pi or "")).lower(),
        })
    return items


def main() -> int:
    items = []
    items.extend(read_pi_cards())
    items.extend(read_passages_from_db())
    items.extend(read_advocacy())
    items.extend(read_nap_actions())
    items.extend(read_nhrc_indicators())

    # 為節省 client 流量,把 search_text 簡化(全部 lower-cased,空白標準化)
    for it in items:
        it["search_text"] = re.sub(r"\s+", " ", it["search_text"])[:600]

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({
        "version": "2026-04-27",
        "items": items,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    by_type: dict[str, int] = {}
    for it in items:
        by_type[it["type"]] = by_type.get(it["type"], 0) + 1
    print(f"✓ 產生 {OUT.relative_to(ROOT)}({len(items)} 筆 / {OUT.stat().st_size // 1024} KB)")
    for t, n in by_type.items():
        print(f"  {t}: {n}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
