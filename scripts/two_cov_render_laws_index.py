#!/usr/bin/env python3
"""
產生 _public/laws/index.html — 動態列出 6 部核心法律 + 修法歷程
- 從 db law / law_amendment 表抓
- 加 filter(主政機關 / 公約對應 / 修法年代)
- 視覺化:時間軸圖示

Usage:
    python3 scripts/two_cov_render_laws_index.py
"""
from __future__ import annotations
import json
import sqlite3
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "data" / "two_cov.db"
OUT = ROOT / "_public" / "laws" / "index.html"

LAW_SLUG = {
    "L001": "two_covenants_act",
    "L002": "student_counseling_act",
    "L003": "748_act",
    "L004": "gender_equity_education_act",
    "L005": "suicide_prevention_act",
    "L006": "assembly_parade_act",
}


def main() -> int:
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row

    laws = list(conn.execute("""
        SELECT law_id, law_name_zh, law_name_en, primary_agency, enacted_date,
               covers_articles, related_pi, is_implementation_act, note
        FROM law ORDER BY enacted_date
    """))

    # 統計每法之 amendment 數
    amend_counts: dict[str, int] = {}
    amend_by_law: dict[str, list] = {}
    for r in conn.execute("""
        SELECT law_id, amendment_id, third_reading, promulgated, key_changes,
               contention_level, triggered_by_co
        FROM law_amendment ORDER BY COALESCE(third_reading, promulgated)
    """):
        d = dict(r)
        amend_counts[d["law_id"]] = amend_counts.get(d["law_id"], 0) + 1
        amend_by_law.setdefault(d["law_id"], []).append(d)

    total_amendments = sum(amend_counts.values())

    # 抽出獨立之主政機關列表
    agencies = sorted({(l["primary_agency"] or "").strip() for l in laws if l["primary_agency"]})

    # 條文覆蓋(JSON array 字串解析)
    def parse_articles(s):
        if not s: return []
        try:
            j = json.loads(s) if s.startswith('[') else [s]
            return j if isinstance(j, list) else [s]
        except Exception:
            return [s]

    def covenant_of(arts):
        cov = set()
        for a in arts:
            au = (a or "").upper()
            if "ICCPR" in au: cov.add("ICCPR")
            if "ICESCR" in au: cov.add("ICESCR")
        return sorted(cov)

    # 時間軸 — 集中所有 amendment 之第三讀日期 + 法律之 enacted
    timeline_points = []
    for l in laws:
        if l["enacted_date"]:
            timeline_points.append({
                "year": (l["enacted_date"] or "")[:4],
                "law_id": l["law_id"],
                "type": "enacted",
                "label": f'{l["law_name_zh"]} 制定',
            })
    for la in conn.execute("""
        SELECT a.law_id, a.amendment_id,
               COALESCE(a.third_reading, a.promulgated) AS d,
               a.key_changes, l.law_name_zh
        FROM law_amendment a JOIN law l ON a.law_id = l.law_id
        WHERE COALESCE(a.third_reading, a.promulgated) IS NOT NULL
        ORDER BY d
    """):
        timeline_points.append({
            "year": (la["d"] or "")[:4],
            "law_id": la["law_id"],
            "type": "amend",
            "label": f'{la["law_name_zh"]}: ' + ((la["key_changes"] or "")[:35]),
        })
    timeline_points.sort(key=lambda x: x["year"])

    # ── HTML ──
    html = f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>法律修法歷程 · {len(laws)} 部 + {total_amendments} 修法 — 兩公約監督平台</title>
<meta name="description" content="兩公約監督平台 · 6 部核心法律之完整修法歷程與條文 delta。可按主政機關 / 公約 / 修法年代篩選。">
<meta name="robots" content="noindex,nofollow">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Noto+Sans+TC:wght@400;500;700&family=Noto+Serif+TC:wght@600;700;900&display=swap" rel="stylesheet">
<style>
:root {{
  --bg:#FAFAF7; --bg-alt:#F1EFEA; --bg-deep:#0E2238;
  --text:#1F1F1F; --text-muted:#5C5C5C; --text-meta:#8A8A8A;
  --brand:#B5371F; --aabe-gold:#8B6F50;
  --cycle-iccpr:#5D3A1A; --cycle-icescr:#5C1A1B;
  --institutional-light:#44638A;
  --border:#DDD8CD; --hairline:#E8E3D6;
  --serif:"Noto Serif TC",Georgia,serif;
  --sans:"Noto Sans TC","PingFang TC",-apple-system,sans-serif;
  --sans-en:"Inter","Noto Sans TC",sans-serif;
}}
* {{ box-sizing:border-box; margin:0; padding:0; }}
body {{ font-family:var(--sans); font-size:16px; line-height:1.6; color:var(--text); background:var(--bg); -webkit-font-smoothing:antialiased; }}
.color-strip {{ display:flex; height:5px; width:100%; }}
.color-strip > div:nth-child(1) {{ flex:1; background:var(--cycle-iccpr); }}
.color-strip > div:nth-child(2) {{ flex:1; background:var(--cycle-icescr); }}
.container {{ max-width:1100px; margin:0 auto; padding:32px 24px 80px; }}
.nav {{ font-size:14px; margin-bottom:16px; }}
.nav a {{ color:var(--brand); text-decoration:none; border-bottom:1px solid #ccc; margin-right:14px; }}
header.page {{ margin-bottom:24px; padding-bottom:20px; border-bottom:2px solid var(--bg-deep); }}
h1 {{ font-family:var(--serif); font-size:30px; font-weight:700; line-height:1.2; margin-bottom:8px; }}
.lead {{ color:var(--text-muted); font-size:14.5px; max-width:720px; }}

.totals {{ display:flex; gap:20px; margin:16px 0; padding:12px 16px; background:var(--bg-alt); border-left:3px solid var(--bg-deep); flex-wrap:wrap; }}
.totals .stat {{ display:flex; flex-direction:column; }}
.totals .num {{ font-family:var(--sans-en); font-size:22px; font-weight:700; color:var(--bg-deep); line-height:1; }}
.totals .lbl {{ font-size:11.5px; color:var(--text-muted); margin-top:2px; }}

.timeline {{ position:relative; margin:32px 0 40px; padding:24px 16px; background:#fff; border:1px solid var(--border); border-radius:4px; overflow-x:auto; }}
.timeline-track {{ position:relative; height:60px; border-bottom:2px solid var(--bg-deep); margin:32px 12px 0; }}
.timeline-point {{ position:absolute; bottom:0; transform:translateX(-50%); }}
.timeline-dot {{ width:10px; height:10px; border-radius:50%; background:var(--brand); margin:0 auto -6px; }}
.timeline-dot.enacted {{ background:var(--bg-deep); width:14px; height:14px; }}
.timeline-dot.amend {{ background:var(--aabe-gold); }}
.timeline-year {{ font-family:var(--sans-en); font-size:11px; color:var(--text-muted); margin-top:8px; text-align:center; white-space:nowrap; }}

.filter-bar {{ display:flex; gap:8px; margin:24px 0 16px; flex-wrap:wrap; align-items:center; }}
.filter-label {{ font-size:13px; color:var(--text-muted); margin-right:4px; }}
.filter-btn {{
  background:#fff; border:1px solid var(--border); border-radius:4px;
  padding:6px 12px; font-size:13px; cursor:pointer; font-family:var(--sans);
}}
.filter-btn.active {{ background:var(--bg-deep); color:#fff; border-color:var(--bg-deep); }}
.filter-btn .cnt {{ color:var(--text-meta); font-size:11px; margin-left:4px; font-family:var(--sans-en); }}
.filter-btn.active .cnt {{ color:rgba(255,255,255,0.7); }}

.law-card {{
  background:#fff; border:1px solid var(--border); border-radius:4px;
  padding:18px 20px; margin:14px 0; transition:border-color .15s;
}}
.law-card:hover {{ border-color:var(--brand); }}
.law-head {{ display:flex; gap:8px; align-items:baseline; flex-wrap:wrap; margin-bottom:6px; }}
.law-id {{ font-family:var(--sans-en); font-size:11px; font-weight:700; background:var(--bg-alt); padding:2px 7px; border-radius:3px; color:var(--bg-deep); }}
.law-card h3 {{ font-family:var(--serif); font-size:18px; font-weight:700; color:var(--bg-deep); }}
.law-card h3 a {{ color:inherit; text-decoration:none; }}
.law-card h3 a:hover {{ color:var(--brand); }}
.cov-tag {{ font-family:var(--sans-en); font-size:10px; font-weight:600; padding:2px 7px; border-radius:3px; color:#fff; }}
.cov-tag.iccpr {{ background:var(--cycle-iccpr); }}
.cov-tag.icescr {{ background:var(--cycle-icescr); }}
.law-card .meta {{ font-size:13px; color:var(--text-muted); margin-bottom:8px; }}
.law-card .meta b {{ color:var(--bg-deep); font-weight:600; }}
.law-card .stats {{ font-family:var(--sans-en); font-size:12px; color:var(--text-meta); margin-top:8px; padding-top:8px; border-top:1px dashed var(--hairline); }}
.law-card .stats b {{ color:var(--bg-deep); }}

.amendments {{ margin-top:10px; }}
.amend-row {{ display:flex; gap:10px; align-items:flex-start; padding:6px 0; border-bottom:1px dotted var(--hairline); font-size:12.5px; }}
.amend-row:last-child {{ border:none; }}
.amend-date {{ font-family:var(--sans-en); color:var(--text-muted); white-space:nowrap; min-width:90px; }}
.amend-text {{ color:var(--text); }}
.contention-tag {{ display:inline-block; font-size:10px; padding:1px 5px; border-radius:2px; margin-left:4px; font-family:var(--sans-en); font-weight:600; color:#fff; }}
.contention-tag.high {{ background:var(--brand); }}
.contention-tag.medium {{ background:var(--aabe-gold); }}
.contention-tag.low {{ background:#2D5F3E; }}
.contention-tag.unknown {{ background:#8A8A8A; }}

.legend {{ margin-top:32px; padding:16px; background:var(--bg-alt); border-left:3px solid var(--aabe-gold); font-size:13px; color:var(--text-muted); }}
.legend strong {{ color:var(--bg-deep); }}
.footer {{ margin-top:60px; padding-top:16px; border-top:1px solid var(--hairline); font-size:12px; color:var(--text-muted); text-align:center; }}
.footer a {{ color:var(--brand); }}
.empty {{ text-align:center; padding:40px; color:var(--text-muted); font-size:14px; }}
</style>
</head>
<body>
<div class="color-strip"><div></div><div></div></div>
<div class="container">
  <div class="nav">
    <a href="../index.html">← 回首頁</a>
    <a href="../issues/index.html">16 PI 議題卡</a>
    <a href="../trace/index.html">議題鏈追溯</a>
    <a href="../actors/index.html">行動者目錄</a>
    <a href="../search.html">全平台搜尋</a>
  </div>

  <header class="page">
    <h1>法律修法歷程 · 全 {len(laws)} 部 + {total_amendments} 修法</h1>
    <p class="lead">
      與兩公約議題密切相關之核心法律,記錄條文 delta、立法理由、行政命令。
      與 trace(議題鏈追溯)雙向連結:每個 amendment 對應一個 trace event。
      可按主政機關 / 公約對應 / 修法年代篩選。
    </p>
  </header>

  <div class="totals">
    <div class="stat"><span class="num">{len(laws)}</span><span class="lbl">部核心法律</span></div>
    <div class="stat"><span class="num">{total_amendments}</span><span class="lbl">修法紀錄</span></div>
    <div class="stat"><span class="num">{len(agencies)}</span><span class="lbl">主政機關</span></div>
    <div class="stat"><span class="num">{(timeline_points[-1]['year'] if timeline_points else '—') + ' / ' + (timeline_points[0]['year'] if timeline_points else '—')}</span><span class="lbl">時間範圍(降冪)</span></div>
  </div>
"""

    # 時間軸
    if timeline_points:
        years = [int(p["year"]) for p in timeline_points if p["year"].isdigit()]
        if years:
            ymin, ymax = min(years), max(years)
            yspan = max(1, ymax - ymin)
            html += '<div class="timeline">\n'
            html += '  <div style="font-family:var(--serif);font-size:15px;font-weight:700;color:var(--bg-deep);margin-bottom:8px">時間軸</div>\n'
            html += '  <div style="font-size:11.5px;color:var(--text-muted);margin-bottom:12px">'
            html += '<span style="display:inline-block;width:14px;height:14px;border-radius:50%;background:var(--bg-deep);vertical-align:middle;margin-right:4px"></span>制定&nbsp;&nbsp;'
            html += '<span style="display:inline-block;width:10px;height:10px;border-radius:50%;background:var(--aabe-gold);vertical-align:middle;margin-right:4px"></span>修法'
            html += '</div>\n'
            html += '  <div class="timeline-track">\n'
            for p in timeline_points:
                if not p["year"].isdigit():
                    continue
                y = int(p["year"])
                pct = (y - ymin) / yspan * 100
                cls = p["type"]
                html += (
                    f'    <div class="timeline-point" style="left:{pct:.1f}%" title="{escape(p["label"])}">'
                    f'<div class="timeline-dot {cls}"></div>'
                    f'<div class="timeline-year">{y}</div>'
                    f'</div>\n'
                )
            html += '  </div>\n'
            html += '</div>\n'

    # filter
    html += '<div class="filter-bar">\n'
    html += '  <span class="filter-label">主政機關:</span>\n'
    html += f'  <button class="filter-btn active" data-agency="all">全部 <span class="cnt">{len(laws)}</span></button>\n'
    for ag in agencies:
        n = sum(1 for l in laws if (l["primary_agency"] or "").strip() == ag)
        html += f'  <button class="filter-btn" data-agency="{escape(ag)}">{escape(ag)} <span class="cnt">{n}</span></button>\n'
    html += '</div>\n'

    html += '<div class="filter-bar">\n'
    html += '  <span class="filter-label">公約:</span>\n'
    html += f'  <button class="filter-btn active" data-cov="all">全部 <span class="cnt">{len(laws)}</span></button>\n'
    n_iccpr = sum(1 for l in laws if "ICCPR" in covenant_of(parse_articles(l["covers_articles"])))
    n_icescr = sum(1 for l in laws if "ICESCR" in covenant_of(parse_articles(l["covers_articles"])))
    html += f'  <button class="filter-btn" data-cov="ICCPR">ICCPR 公政 <span class="cnt">{n_iccpr}</span></button>\n'
    html += f'  <button class="filter-btn" data-cov="ICESCR">ICESCR 經社文 <span class="cnt">{n_icescr}</span></button>\n'
    html += '</div>\n'

    html += '<div id="laws-list">\n'

    # law cards
    for l in laws:
        slug = LAW_SLUG.get(l["law_id"], "")
        arts = parse_articles(l["covers_articles"])
        cov = covenant_of(arts)
        ag = (l["primary_agency"] or "—").strip()
        amends = amend_by_law.get(l["law_id"], [])

        cov_tags = "".join(
            f'<span class="cov-tag {c.lower()}">{c}</span>'
            for c in cov
        )

        # amendment 列
        amend_html = ""
        if amends:
            amend_html += '<div class="amendments"><div style="font-size:12px;color:var(--text-muted);margin-bottom:4px;font-weight:600">修法紀錄:</div>'
            for a in amends:
                d = a["third_reading"] or a["promulgated"] or "—"
                ct = (a["contention_level"] or "unknown").lower()
                ct_label = {"high":"高度爭議","medium":"中度","low":"低度","unknown":"—"}.get(ct, "—")
                co_note = ""
                if a["triggered_by_co"]:
                    co_note = f' <span style="font-size:11px;color:var(--cycle-icescr)">(觸發:{escape(str(a["triggered_by_co"])[:40])})</span>'
                amend_html += (
                    f'<div class="amend-row">'
                    f'<span class="amend-date">{escape(str(d))}</span>'
                    f'<span class="amend-text">{escape((a["key_changes"] or "")[:80])}'
                    f'<span class="contention-tag {ct}">{ct_label}</span>'
                    f'{co_note}</span></div>'
                )
            amend_html += '</div>'

        href = f"{slug}.html" if slug else "#"
        html += f"""  <div class="law-card" data-agency="{escape(ag)}" data-cov="{','.join(cov)}">
    <div class="law-head">
      <span class="law-id">{escape(l["law_id"])}</span>
      <h3><a href="{escape(href)}">{escape(l["law_name_zh"])}</a></h3>
      {cov_tags}
    </div>
    <div class="meta">
      <b>制定:</b>{escape(l["enacted_date"] or "—")} ·
      <b>主政機關:</b>{escape(ag)}
      {(' · <b>條文對應:</b>' + ', '.join(arts[:6]) + ('…' if len(arts)>6 else '')) if arts else ''}
    </div>
    {f'<div style="font-size:13px;color:var(--text-muted);margin-bottom:6px">{escape(l["note"])}</div>' if l["note"] else ''}
    <div class="stats">
      共 <b>{len(amends)}</b> 筆修法紀錄
    </div>
    {amend_html}
  </div>
"""

    html += "</div>\n"
    html += '<div id="empty" class="empty" style="display:none">無符合條件之法律</div>\n'

    html += """
  <div class="legend">
    <strong>說明</strong>:本頁從資料庫即時抽取,每次部署時重新編譯。
    每筆修法紀錄含「爭議程度」(contention_level)+ 「觸發來源」(triggered_by_co — 結論性意見之具體段次)。
    完整條文 delta(text_before / text_after)請點各法律之獨立頁面。
  </div>

  <div class="footer">
    兩公約監督平台 · 國教行動聯盟(AABE)<br>
    <a href="../index.html">回首頁</a> · <a href="../about.html">關於</a> · <a href="../api/laws.json">laws API (JSON)</a>
  </div>
</div>

<script>
(function () {
  var agencyBtns = document.querySelectorAll('.filter-btn[data-agency]');
  var covBtns = document.querySelectorAll('.filter-btn[data-cov]');
  var cards = document.querySelectorAll('.law-card');
  var empty = document.getElementById('empty');
  var state = { agency: 'all', cov: 'all' };

  function apply() {
    var visible = 0;
    cards.forEach(function (c) {
      var agencyMatch = state.agency === 'all' || c.dataset.agency === state.agency;
      var covMatch = state.cov === 'all' || (c.dataset.cov || '').indexOf(state.cov) >= 0;
      if (agencyMatch && covMatch) {
        c.style.display = '';
        visible++;
      } else {
        c.style.display = 'none';
      }
    });
    empty.style.display = visible === 0 ? 'block' : 'none';
  }

  agencyBtns.forEach(function (b) {
    b.addEventListener('click', function () {
      agencyBtns.forEach(function (x) { x.classList.remove('active'); });
      b.classList.add('active');
      state.agency = b.dataset.agency;
      apply();
    });
  });
  covBtns.forEach(function (b) {
    b.addEventListener('click', function () {
      covBtns.forEach(function (x) { x.classList.remove('active'); });
      b.classList.add('active');
      state.cov = b.dataset.cov;
      apply();
    });
  });
})();
</script>
</body>
</html>
"""

    OUT.write_text(html, encoding="utf-8")
    print(f"  ✓ laws/index.html  {len(laws)} 部 / {total_amendments} 修法 / {len(agencies)} 機關")
    print(f"  bytes: {OUT.stat().st_size:,}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
