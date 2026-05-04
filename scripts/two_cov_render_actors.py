#!/usr/bin/env python3
"""
產生 _public/actors/index.html — 動態列出全部 107 行動者
- 從資料庫 actor 表抓取
- 按 actor_type 分組(ngo / govt / court / ...)
- 每張卡顯示:名稱 + 立場光譜 + 隸屬

Usage:
    python3 scripts/two_cov_render_actors.py
"""
from __future__ import annotations
import sqlite3
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "data" / "two_cov.db"
OUT_DIR = ROOT / "_public" / "actors"
OUT = OUT_DIR / "index.html"

# actor_type 中文標籤 + 排序
TYPE_LABELS = [
    ("ngo", "民間團體", "ngo"),
    ("govt_agency", "政府機關", "govt"),
    ("court", "司法 / 法院", "court"),
    ("committee_member", "國際委員 / 審查專家", "intl"),
    ("legislator", "立法委員 / 政黨", "legis"),
    ("intl_actor", "國際組織", "intl"),
    ("academic", "學界 / 研究機構", "academic"),
    ("private_media", "媒體", "media"),
    ("media", "媒體", "media"),
    ("industry_assoc", "產業公會", "industry"),
    ("public", "公眾 / 個人", "public"),
]

TYPE_ORDER = {key: i for i, (key, _, _) in enumerate(TYPE_LABELS)}
TYPE_NAME = {key: name for key, name, _ in TYPE_LABELS}
TYPE_CSS = {key: cls for key, _, cls in TYPE_LABELS}


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row

    actors = list(conn.execute("""
        SELECT actor_id, actor_type, name, affiliation, position_spectrum, active_period, note
        FROM actor
        ORDER BY actor_type, name
    """))
    total = len(actors)

    # 統計各類型數量
    type_count: dict[str, int] = {}
    for a in actors:
        t = a["actor_type"]
        type_count[t] = type_count.get(t, 0) + 1

    # 取每位 actor 之事件參與數
    event_counts: dict[str, int] = {}
    for r in conn.execute("SELECT actor_id, COUNT(*) FROM event WHERE actor_id IS NOT NULL GROUP BY actor_id"):
        event_counts[r[0]] = r[1]

    # 取每位 actor 之完整事件清單(供 accordion 展開)
    actor_events: dict[str, list] = {}
    for r in conn.execute("""
        SELECT actor_id, event_id, event_date, event_type, title, summary, issue_tags, related_pi
        FROM event
        WHERE actor_id IS NOT NULL
        ORDER BY actor_id, event_date DESC
    """):
        actor_events.setdefault(r["actor_id"], []).append(dict(r))

    # ── HTML 起頭 ──
    types_present = sorted(type_count.keys(), key=lambda t: TYPE_ORDER.get(t, 999))

    html = f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>行動者目錄 · 全 {total} 個 — 兩公約監督平台</title>
<meta name="description" content="兩公約監督平台行動者目錄,涵蓋 {type_count.get('ngo',0)} 民間團體 / {type_count.get('govt_agency',0)} 政府機關 / {type_count.get('court',0)} 法院 / {type_count.get('committee_member',0)} 國際委員 等共 {total} 位行動者。">
<meta name="robots" content="noindex,nofollow">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Noto+Sans+TC:wght@400;500;700&family=Noto+Serif+TC:wght@600;700;900&display=swap" rel="stylesheet">
<style>
:root {{
  --bg: #FAFAF7; --bg-alt: #F1EFEA; --bg-deep: #0E2238;
  --text: #1F1F1F; --text-muted: #5C5C5C; --text-meta: #8A8A8A;
  --brand: #B5371F; --aabe-gold: #8B6F50;
  --cycle-iccpr: #5D3A1A; --cycle-icescr: #5C1A1B;
  --institutional-light: #44638A;
  --border: #DDD8CD; --hairline: #E8E3D6;
  --serif: "Noto Serif TC", Georgia, serif;
  --sans: "Noto Sans TC", "PingFang TC", -apple-system, sans-serif;
  --sans-en: "Inter", "Noto Sans TC", sans-serif;
}}
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{ font-family: var(--sans); font-size: 16px; line-height: 1.6; color: var(--text); background: var(--bg); -webkit-font-smoothing: antialiased; }}
.color-strip {{ display:flex; height:5px; width:100%; }}
.color-strip > div:nth-child(1) {{ flex:1; background: var(--cycle-iccpr); }}
.color-strip > div:nth-child(2) {{ flex:1; background: var(--cycle-icescr); }}
.container {{ max-width: 1100px; margin: 0 auto; padding: 32px 24px 80px; }}
.nav {{ font-size: 14px; margin-bottom: 16px; }}
.nav a {{ color: var(--brand); text-decoration: none; border-bottom: 1px solid #ccc; margin-right: 14px; }}
header.page {{ margin-bottom: 24px; padding-bottom: 20px; border-bottom: 2px solid var(--bg-deep); }}
h1 {{ font-family: var(--serif); font-size: 30px; font-weight: 700; line-height: 1.2; margin-bottom: 8px; }}
.lead {{ color: var(--text-muted); font-size: 14.5px; max-width: 720px; }}

.totals {{ display: flex; gap: 20px; margin: 16px 0;
  padding: 12px 16px; background: var(--bg-alt);
  border-left: 3px solid var(--bg-deep); flex-wrap: wrap; }}
.totals .stat {{ display: flex; flex-direction: column; }}
.totals .num {{ font-family: var(--sans-en); font-size: 22px; font-weight: 700; color: var(--bg-deep); line-height: 1; }}
.totals .lbl {{ font-size: 11.5px; color: var(--text-muted); margin-top: 2px; }}

.controls {{ margin: 24px 0 16px; }}
.search-bar {{ width: 100%; padding: 10px 14px; border: 1.5px solid var(--border); border-radius: 4px; font-family: var(--sans); font-size: 14px; background: #fff; }}
.search-bar:focus {{ outline: none; border-color: var(--bg-deep); }}
.filter-bar {{ display: flex; gap: 6px; margin-top: 12px; flex-wrap: wrap; align-items: center; }}
.filter-label {{ font-size: 13px; color: var(--text-muted); margin-right: 4px; }}
.filter-btn {{
  background: #fff; border: 1px solid var(--border); border-radius: 4px;
  padding: 5px 10px; font-size: 12.5px; cursor: pointer; font-family: var(--sans);
}}
.filter-btn.active {{ background: var(--bg-deep); color: #fff; border-color: var(--bg-deep); }}
.filter-btn .cnt {{ color: var(--text-meta); font-size: 11px; margin-left: 4px; font-family: var(--sans-en); }}
.filter-btn.active .cnt {{ color: rgba(255,255,255,0.7); }}

.actor-section {{ margin-top: 28px; }}
.actor-section h2 {{ font-family: var(--serif); font-size: 19px; font-weight: 700; color: var(--bg-deep); margin-bottom: 12px; padding-bottom: 6px; border-bottom: 1px solid var(--hairline); display: flex; align-items: baseline; gap: 8px; }}
.actor-section h2 .count {{ font-family: var(--sans-en); font-size: 13px; color: var(--text-meta); font-weight: 500; }}

.grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 10px; }}

.card {{
  background: #fff; border: 1px solid var(--border); border-radius: 4px;
  padding: 12px 14px; transition: border-color .15s, box-shadow .15s;
  display: flex; flex-direction: column;
}}
.card:hover {{ border-color: var(--brand); }}
.card-head {{ display: flex; gap: 6px; align-items: center; margin-bottom: 4px; flex-wrap: wrap; }}
.type-tag {{
  font-family: var(--sans-en); font-size: 9.5px; font-weight: 600; letter-spacing: 0.05em; text-transform: uppercase;
  padding: 2px 6px; border-radius: 3px; color: #fff;
}}
.type-tag.ngo {{ background: var(--brand); }}
.type-tag.govt {{ background: var(--bg-deep); }}
.type-tag.court {{ background: var(--cycle-iccpr); }}
.type-tag.intl {{ background: var(--aabe-gold); }}
.type-tag.legis {{ background: var(--institutional-light); }}
.type-tag.academic {{ background: #4f4f4f; }}
.type-tag.media {{ background: #6d28d9; }}
.type-tag.industry {{ background: #5C1A1B; }}
.type-tag.public {{ background: #8A8A8A; }}
.actor-id {{ font-family: var(--sans-en); font-size: 10px; color: var(--text-meta); }}

.card .name {{ font-family: var(--serif); font-size: 15px; font-weight: 700; color: var(--bg-deep); line-height: 1.35; margin-bottom: 4px; }}
.card .meta {{ font-size: 12px; color: var(--text-muted); line-height: 1.5; }}
.card .position {{ display: inline-block; margin-top: 4px; padding: 1px 6px; background: var(--bg-alt); border-radius: 2px; font-size: 11px; color: var(--text-muted); }}
.card .events-count {{ margin-top: 6px; font-family: var(--sans-en); font-size: 11px; color: var(--text-meta); }}
.card .events-count b {{ color: var(--bg-deep); font-weight: 700; }}
.card .toggle-events {{
  margin-top: 8px; padding: 5px 10px; font-size: 11.5px;
  background: var(--bg-alt); border: 1px solid var(--border); border-radius: 3px;
  color: var(--text-muted); cursor: pointer; font-family: var(--sans);
  transition: background .15s;
}}
.card .toggle-events:hover {{ background: var(--bg-deep); color: #fff; border-color: var(--bg-deep); }}
.card .events-list {{
  display: none; margin-top: 10px; padding: 10px; background: var(--bg-alt); border-radius: 3px;
  font-size: 11.5px; line-height: 1.55; max-height: 300px; overflow-y: auto;
}}
.card .events-list.open {{ display: block; }}
.event-item {{
  padding: 6px 0; border-bottom: 1px dashed var(--border);
}}
.event-item:last-child {{ border-bottom: none; }}
.event-date {{ font-family: var(--sans-en); font-size: 10.5px; color: var(--text-meta); margin-right: 6px; }}
.event-type-mini {{
  font-family: var(--sans-en); font-size: 9px; font-weight: 600; letter-spacing: 0.04em; text-transform: uppercase;
  padding: 1px 5px; border-radius: 2px; background: var(--aabe-gold); color: #fff;
}}
.event-type-mini.shadow_report {{ background: var(--brand); }}
.event-type-mini.legislation {{ background: var(--bg-deep); }}
.event-type-mini.govt_response {{ background: var(--cycle-iccpr); }}
.event-type-mini.court_ruling {{ background: #4f4f4f; }}
.event-type-mini.public_opinion {{ background: var(--institutional-light); }}
.event-type-mini.outcome {{ background: #2D5F3E; }}
.event-type-mini.intl_actor {{ background: #6d28d9; }}
.event-type-mini.co_paragraph {{ background: var(--cycle-icescr); }}
.event-title {{ font-weight: 600; color: var(--bg-deep); margin-top: 2px; }}
.event-summary {{ color: var(--text-muted); margin-top: 2px; }}

.legend {{ margin-top: 32px; padding: 16px; background: var(--bg-alt); border-left: 3px solid var(--aabe-gold); font-size: 13px; color: var(--text-muted); }}
.legend strong {{ color: var(--bg-deep); }}
.footer {{ margin-top: 60px; padding-top: 16px; border-top: 1px solid var(--hairline); font-size: 12px; color: var(--text-muted); text-align: center; }}
.footer a {{ color: var(--brand); }}

.empty {{ text-align: center; padding: 24px; color: var(--text-muted); font-size: 14px; }}
.hidden {{ display: none !important; }}
</style>
</head>
<body>
<div class="color-strip"><div></div><div></div></div>
<div class="container">
  <div class="nav">
    <a href="../index.html">← 回首頁</a>
    <a href="../issues/index.html">16 PI 議題卡</a>
    <a href="../trace/index.html">議題脈絡追溯</a>
    <a href="../laws/index.html">法律修法</a>
    <a href="../search.html">全平台搜尋</a>
  </div>

  <header class="page">
    <h1>行動者目錄 · 全 {total} 個</h1>
    <p class="lead">
      本平台收錄之行動者,涵蓋民間團體、政府機關、司法、國際委員、立委、學界、媒體等 11 類。
      所有立場光譜(position_spectrum)為依其公開出版物 / 公開立場彙整,雙人編碼,可請求修正。
    </p>
  </header>

  <div class="totals">
    <div class="stat"><span class="num">{total}</span><span class="lbl">行動者總數</span></div>
"""

    for type_key in types_present:
        cnt = type_count.get(type_key, 0)
        label = TYPE_NAME.get(type_key, type_key)
        html += f'    <div class="stat"><span class="num">{cnt}</span><span class="lbl">{label}</span></div>\n'

    html += """  </div>

  <div class="controls">
    <input type="search" id="q" class="search-bar" placeholder="搜尋行動者名稱、立場、隸屬...(例:廢死、宗教、人權)">
    <div class="filter-bar">
      <span class="filter-label">類型:</span>
      <button class="filter-btn active" data-type="all">全部 <span class="cnt">""" + str(total) + """</span></button>
"""

    for type_key in types_present:
        cnt = type_count.get(type_key, 0)
        label = TYPE_NAME.get(type_key, type_key)
        html += f'      <button class="filter-btn" data-type="{type_key}">{label} <span class="cnt">{cnt}</span></button>\n'

    html += """    </div>
  </div>

  <div id="results">
"""

    # ── 依 type 分區渲染 ──
    by_type: dict[str, list] = {}
    for a in actors:
        by_type.setdefault(a["actor_type"], []).append(a)

    for type_key in types_present:
        actors_in_type = by_type.get(type_key, [])
        if not actors_in_type:
            continue
        label = TYPE_NAME.get(type_key, type_key)
        css_cls = TYPE_CSS.get(type_key, "ngo")
        html += f"""
  <section class="actor-section" data-type-section="{type_key}">
    <h2>{label} <span class="count">({len(actors_in_type)})</span></h2>
    <div class="grid">
"""
        for a in actors_in_type:
            n_evt = event_counts.get(a["actor_id"], 0)
            position = a["position_spectrum"] or ""
            affil = a["affiliation"] or ""
            name = escape(a["name"] or "")
            actor_id = escape(a["actor_id"] or "")
            search_text = f"{a['name']} {position} {affil} {a['note'] or ''}".lower()
            html += f"""      <div class="card" data-type="{type_key}" data-search="{escape(search_text)}">
        <div class="card-head">
          <span class="type-tag {css_cls}">{label}</span>
          <span class="actor-id">{actor_id}</span>
        </div>
        <div class="name">{name}</div>
"""
            if affil:
                html += f'        <div class="meta">{escape(affil)}</div>\n'
            if position:
                html += f'        <div><span class="position">{escape(position)}</span></div>\n'
            if n_evt > 0:
                html += f'        <div class="events-count">參與事件:<b>{n_evt}</b> 個</div>\n'
                html += f'        <button class="toggle-events" data-target="evts-{a["actor_id"]}">▸ 展開事件清單</button>\n'
                html += f'        <div id="evts-{a["actor_id"]}" class="events-list">\n'
                for ev in actor_events.get(a["actor_id"], []):
                    et = ev["event_type"] or ""
                    et_label = {
                        "shadow_report": "影子報告",
                        "legislation": "立法",
                        "govt_response": "政府回應",
                        "court_ruling": "判決",
                        "public_opinion": "公民倡議",
                        "outcome": "結果指標",
                        "intl_actor": "國際行動者",
                        "co_paragraph": "結論性意見",
                        "committee_question": "委員質詢",
                    }.get(et, et)
                    date_str = escape(ev["event_date"] or "")
                    title = escape(ev["title"] or "")
                    summary = escape((ev["summary"] or "")[:160])
                    html += f"""          <div class="event-item">
            <span class="event-date">{date_str}</span>
            <span class="event-type-mini {et}">{et_label}</span>
            <div class="event-title">{title}</div>
            <div class="event-summary">{summary}{'…' if len(ev['summary'] or '') > 160 else ''}</div>
          </div>
"""
                html += '        </div>\n'
            html += "      </div>\n"

        html += """    </div>
  </section>
"""

    html += """
    <div id="empty" class="empty hidden">無符合條件之行動者</div>
  </div>

  <div class="legend">
    <strong>說明</strong>:
    本目錄為動態產生(由資料庫 actor 表),每次部署時重新編譯。立場光譜採雙人獨立編碼,如有錯誤請來信
    <a href="mailto:contact@aabe.org.tw" style="color:var(--brand)">contact@aabe.org.tw</a> 申請修正,72 小時內回覆。
    <br><br>
    <strong>API</strong>:本目錄之原始資料可由 <a href="../api/trace.json" style="color:var(--brand)">api/trace.json</a> 取得(actors 欄位)。
  </div>

  <div class="footer">
    兩公約監督平台 · 國教行動聯盟(AABE)<br>
    <a href="../index.html">回首頁</a> · <a href="../about.html">關於</a> · <a href="../methodology.html">方法論</a>
  </div>
</div>

<script>
(function () {
  var q = document.getElementById('q');
  var buttons = document.querySelectorAll('.filter-btn');
  var cards = document.querySelectorAll('.card');
  var sections = document.querySelectorAll('.actor-section');
  var empty = document.getElementById('empty');

  var activeType = 'all';

  function applyFilter() {
    var query = q.value.trim().toLowerCase();
    var visibleCount = 0;
    cards.forEach(function (c) {
      var typeMatch = activeType === 'all' || c.dataset.type === activeType;
      var searchMatch = !query || c.dataset.search.indexOf(query) >= 0;
      if (typeMatch && searchMatch) {
        c.classList.remove('hidden');
        visibleCount++;
      } else {
        c.classList.add('hidden');
      }
    });
    // 隱藏空白 section
    sections.forEach(function (s) {
      var visibleCards = s.querySelectorAll('.card:not(.hidden)').length;
      s.style.display = visibleCards === 0 ? 'none' : '';
    });
    empty.classList.toggle('hidden', visibleCount > 0);
  }

  buttons.forEach(function (btn) {
    btn.addEventListener('click', function () {
      buttons.forEach(function (b) { b.classList.remove('active'); });
      btn.classList.add('active');
      activeType = btn.dataset.type;
      applyFilter();
    });
  });

  var debounce;
  q.addEventListener('input', function () {
    clearTimeout(debounce);
    debounce = setTimeout(applyFilter, 120);
  });

  // accordion 展開事件清單
  document.querySelectorAll('.toggle-events').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var target = document.getElementById(btn.dataset.target);
      if (!target) return;
      var open = target.classList.toggle('open');
      btn.textContent = open ? '▾ 收合事件清單' : '▸ 展開事件清單';
    });
  });
})();
</script>
</body>
</html>
"""

    OUT.write_text(html, encoding="utf-8")
    print(f"  ✓ actors/index.html  {total} actors  {OUT.stat().st_size:,} bytes")
    conn.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
