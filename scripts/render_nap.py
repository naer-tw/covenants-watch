#!/usr/bin/env python3
"""render_nap.py — 從 SQLite nap_action 表渲染 NAP 追蹤頁面 + 戰情室片段。

Wave 79:對應藍圖 §模組四 + 表 5 NAP 追蹤系統。

用法:
    python3 scripts/render_nap.py              # 印 HTML 至 stdout
    python3 scripts/render_nap.py --update     # 更新 _public/nap.html + 戰情室片段
"""
from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "data" / "crw.db"
NAP_PAGE = ROOT / "_public" / "nap.html"
INDEX_PAGE = ROOT / "_public" / "index.html"

ASSESS_COLOR = {
    "已落實有成效": "#2e7d32",
    "已落實但無成效": "#fbc02d",
    "部分達成": "#ef6c00",
    "未達成": "#d32f2f",
    "方向錯誤": "#b71c1c",
    "--": "#999",
}

ASSESS_ICON = {
    "已落實有成效": "🟢",
    "已落實但無成效": "🟡",
    "部分達成": "🟠",
    "未達成": "🔴",
    "方向錯誤": "⛔",
    "--": "⏳",
}

SEVERITY_COLOR = {
    "嚴重落差": "#b71c1c",
    "警告": "#d32f2f",
    "關切": "#ef6c00",
    "--": "#999",
}


def fetch_actions() -> list[dict]:
    if not DB.exists():
        return []
    conn = sqlite3.connect(str(DB))
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT * FROM nap_action ORDER BY nap_period, theme_no, action_id"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def stats(actions: list[dict]) -> dict:
    period1 = [a for a in actions if a["nap_period"] == "1"]
    return {
        "total_p1": len(period1),
        "未達成": sum(1 for a in period1 if a["aabe_assessment"] == "未達成"),
        "方向錯誤": sum(1 for a in period1 if a["aabe_assessment"] == "方向錯誤"),
        "部分達成": sum(1 for a in period1 if a["aabe_assessment"] == "部分達成"),
        "已落實有成效": sum(1 for a in period1 if a["aabe_assessment"] == "已落實有成效"),
        "嚴重落差": sum(1 for a in period1 if a["nhrc_severity"] == "嚴重落差"),
    }


def render_dashboard_widget(actions: list[dict]) -> str:
    """戰情室之 NAP 進度小方塊(嵌進 _public/index.html)。"""
    s = stats(actions)
    return f"""<div class="metric" style="border-left-color: #b71c1c;">
    <div class="label">NAP 第一期(2022-2024)未達成 / 方向錯誤項數</div>
    <div class="value" style="color: #b71c1c;">⛔ {s['未達成'] + s['方向錯誤']}/{s['total_p1']}</div>
    <div class="source">含 {s['嚴重落差']} 項 NHRC 列為嚴重落差 ‧ <a href="nap.html" style="color:#888;text-decoration:none;font-size:11px;">→ 詳見 NAP</a></div>
  </div>"""


def render_nap_page(actions: list[dict]) -> str:
    s = stats(actions)
    p1 = [a for a in actions if a["nap_period"] == "1"]
    p2 = [a for a in actions if a["nap_period"] == "2"]

    def _render_rows(actions_list):
        rows = []
        for a in actions_list:
            a_color = ASSESS_COLOR.get(a["aabe_assessment"] or "--", "#999")
            a_icon = ASSESS_ICON.get(a["aabe_assessment"] or "--", "⏳")
            sev_color = SEVERITY_COLOR.get(a["nhrc_severity"] or "--", "#999")
            related_pi = ", ".join(json.loads(a["related_pi"] or "[]")) or "跨議題"
            related_co = ", ".join(json.loads(a["related_co"] or "[]")) or "—"
            agency = a["lead_agency"] or "—"
            rows.append(f"""<tr>
                <td><strong>{a['action_id']}</strong><br><small style="color:#666;">議題 {a['theme_no']} · {a['theme_name']}</small></td>
                <td>{a['action_text']}<br><small style="color:#888;">KPI: {a.get('kpi') or '—'}</small></td>
                <td>{agency}</td>
                <td style="color:{sev_color};">{a['govt_status'] or '--'}</td>
                <td style="color:{sev_color};font-size:13px;">{a['nhrc_severity'] or '--'}<br><small>{(a.get('nhrc_comment') or '')[:60]}</small></td>
                <td style="color:{a_color};font-weight:600;">{a_icon} {a['aabe_assessment'] or '--'}</td>
                <td style="font-size:12px;color:#666;">{related_pi}<br><small>{related_co}</small></td>
            </tr>""")
        return "\n".join(rows)

    rows_p1 = []
    for a in p1:
        a_color = ASSESS_COLOR.get(a["aabe_assessment"] or "--", "#999")
        a_icon = ASSESS_ICON.get(a["aabe_assessment"] or "--", "⏳")
        sev_color = SEVERITY_COLOR.get(a["nhrc_severity"] or "--", "#999")
        related_pi = ", ".join(json.loads(a["related_pi"] or "[]")) or "跨議題"
        related_co = ", ".join(json.loads(a["related_co"] or "[]")) or "—"
        agency = a["lead_agency"] or "—"
        rows_p1.append(f"""<tr>
            <td><strong>{a['action_id']}</strong><br><small style="color:#666;">議題 {a['theme_no']} · {a['theme_name']}</small></td>
            <td>{a['action_text']}<br><small style="color:#888;">KPI: {a['kpi']}</small></td>
            <td>{agency}</td>
            <td style="color:{sev_color};">{a['govt_status']}</td>
            <td style="color:{sev_color};font-size:13px;">{a['nhrc_severity']}<br><small>{(a['nhrc_comment'] or '')[:60]}</small></td>
            <td style="color:{a_color};font-weight:600;">{a_icon} {a['aabe_assessment']}</td>
            <td style="font-size:12px;color:#666;">{related_pi}<br><small>{related_co}</small></td>
        </tr>""")

    # 排除第二期之 placeholder 假資料
    p2_real = [a for a in p2 if a["action_id"] != "NAP2-PLACEHOLDER"]
    if p2_real:
        p2_block = f"""<div class="note">
  <p><strong>狀態:依 NHRC 2025-07 §12 預期 placeholder({len(p2_real)} 項)</strong></p>
  <p>等行政院公布完整 NAP 第二期後,此處會更新為官方版本。目前列出之項目為預期內容(已從第一期延續或新增)。</p>
</div>

<table>
  <thead>
    <tr><th>行動 ID / 議題</th><th>行動內容 / KPI</th><th>主管</th><th>政府自評</th><th>NHRC 嚴重度</th><th>AABE 評估</th><th>對應 PI / CO</th></tr>
  </thead>
  <tbody>
    {_render_rows(p2_real)}
  </tbody>
</table>"""
    else:
        p2_block = """<div class="note">
  <p><strong>狀態:資料待匯入</strong></p>
  <p>第二期 NAP 已啟動但完整行動清單尚未公開。執行 <code>python3 scripts/import_nap2.py --predicted</code> 灌入預期 placeholder。</p>
</div>"""

    return f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>國家人權行動計畫追蹤 — 兒少人權監督平台</title>
<meta name="description" content="政府 NAP 自評 vs NHRC 監督意見 vs AABE 民間評估 — 涉兒少之 11 項行動逐項追蹤">
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "Dataset",
  "name": "國家人權行動計畫(NAP)兒少相關行動追蹤",
  "description": "從行政院 2022-2024 NAP 與 NHRC 2025-07 監督報告抽取涉兒少 11 項行動,逐項列政府自評、NHRC 評估、AABE 民間評估。",
  "creator": {{"@type": "Organization", "name": "國教行動聯盟兒少人權監督平台"}},
  "license": "https://creativecommons.org/licenses/by/4.0/",
  "inLanguage": "zh-TW"
}}
</script>
<style>
* {{ box-sizing: border-box; }}
body {{ font-family: "PingFang TC", "Noto Sans TC", "Microsoft JhengHei", sans-serif;
       font-size: 15px; line-height: 1.6; color: #1a1a2e; margin: 0; background: #fff8f5; }}
header {{ background: #2C323C; color: #fff; padding: 24px; text-align: center; }}
header h1 {{ margin: 0 0 6px; font-size: 22px; }}
header p {{ margin: 0; font-size: 13px; color: #ccc; }}
main {{ max-width: 1200px; margin: 0 auto; padding: 24px 16px; }}
.summary {{ background: #fff; padding: 16px 20px; border-radius: 8px; margin: 12px 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.06); display: grid;
            grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 10px; }}
.summary .stat {{ padding: 10px; border-left: 4px solid #E8734A; }}
.summary .stat .num {{ font-size: 22px; font-weight: 700; color: #d32f2f; }}
.summary .stat .lab {{ font-size: 12px; color: #555; }}
table {{ width: 100%; border-collapse: collapse; margin: 16px 0; background: #fff;
         border-radius: 8px; overflow: hidden; box-shadow: 0 2px 4px rgba(0,0,0,0.06); }}
th, td {{ padding: 10px; text-align: left; vertical-align: top; border-bottom: 1px solid #eee;
         font-size: 13px; }}
th {{ background: #2C323C; color: #fff; font-weight: 600; font-size: 12px; }}
tr:hover {{ background: #fff8f5; }}
.legend {{ display: flex; gap: 14px; flex-wrap: wrap; font-size: 12px; color: #555;
           margin: 12px 0; }}
.legend span {{ display: inline-flex; align-items: center; gap: 4px; }}
.note {{ background: #fff3cd; padding: 12px 16px; border-radius: 6px; font-size: 13.5px;
         margin: 16px 0; border-left: 4px solid #f0ad4e; }}
footer {{ text-align: center; padding: 24px; font-size: 13px; color: #555; }}
@media (max-width: 800px) {{
  table {{ font-size: 12px; }}
  th, td {{ padding: 6px; }}
}}
</style>
</head>
<body>
<a href="#main" style="position:absolute;left:-999px;" onfocus="this.style.left='12px';this.style.top='12px';">跳到主要內容</a>

<header>
  <h1>🏛 國家人權行動計畫追蹤</h1>
  <p>第一期 2022-2024 已結束 ‧ 第二期 2025-2027 進行中 ‧ 涉兒少 11 項逐項追蹤</p>
</header>

<main id="main">

<div class="summary">
  <div class="stat"><div class="num">{s['total_p1']}</div><div class="lab">第一期涉兒少行動數</div></div>
  <div class="stat"><div class="num" style="color:#d32f2f;">{s['未達成']}</div><div class="lab">AABE 評估「未達成」</div></div>
  <div class="stat"><div class="num" style="color:#b71c1c;">{s['方向錯誤']}</div><div class="lab">AABE 評估「方向錯誤」</div></div>
  <div class="stat"><div class="num" style="color:#ef6c00;">{s['部分達成']}</div><div class="lab">AABE 評估「部分達成」</div></div>
  <div class="stat"><div class="num" style="color:#b71c1c;">{s['嚴重落差']}</div><div class="lab">NHRC「嚴重落差」</div></div>
</div>

<div class="note">
  <p><strong>📌 民間評估指南</strong>(對應藍圖 §模組四):</p>
  <p style="margin: 4px 0;">• <strong>政府自評</strong>:行政院 2022-2024 NAP 成果總結報告所載狀態</p>
  <p style="margin: 4px 0;">• <strong>NHRC 監督</strong>:國家人權委員會 2025-07 監督報告之意見</p>
  <p style="margin: 4px 0;">• <strong>AABE 評估</strong>:國教行動聯盟兒少人權監督平台依第一線觀察逐項評估;打破「KPI 完成即代表政策成功」之迷思</p>
</div>

<div class="legend">
  <strong>AABE 五級評估:</strong>
  <span>{ASSESS_ICON['已落實有成效']} 已落實有成效</span>
  <span>{ASSESS_ICON['已落實但無成效']} 已落實但無成效</span>
  <span>{ASSESS_ICON['部分達成']} 部分達成</span>
  <span>{ASSESS_ICON['未達成']} 未達成</span>
  <span>{ASSESS_ICON['方向錯誤']} 方向錯誤</span>
</div>

<h2>第一期 NAP 2022-2024 兒少相關行動</h2>

<table>
  <thead>
    <tr>
      <th>行動 ID / 議題</th>
      <th>行動內容 / KPI</th>
      <th>主管</th>
      <th>政府自評</th>
      <th>NHRC 嚴重度</th>
      <th>AABE 評估</th>
      <th>對應 PI / CO</th>
    </tr>
  </thead>
  <tbody>
    {''.join(rows_p1)}
  </tbody>
</table>

<h2>第二期 NAP 2025-2027(進行中)</h2>

{p2_block}

<h2>方法論說明</h2>

<p>本追蹤系統對應藍圖 §模組四「國家人權行動計畫追蹤系統」。對每項涉兒少之 NAP 行動,平台記錄:</p>

<ul>
  <li><strong>行動 ID</strong> — NAP{{期數}}-{{議題}}-{{議題小節}}</li>
  <li><strong>政府自評 vs NHRC vs AABE 三方對照</strong> — 打破政府 83.9% 自評率之迷思</li>
  <li><strong>對應 PI / CRC CO</strong> — 連到本平台議題卡與結論性意見</li>
  <li><strong>是否建議延續</strong> — 標記 NAP 第二期應否繼續追蹤</li>
</ul>

<p>資料來源:</p>
<ul>
  <li><a href="../data/sources/NHRC_NAPMonitor_2025-07_摘要.md">NHRC 監督 2022-2024 NAP 執行情形成果報告(2025-07)</a></li>
  <li>行政院 2022-2024 NAP 成果總結報告(2025)</li>
  <li>NHRC 兒童權利監測指標集 239 項(2026-02-04 發布,平台對接中)</li>
</ul>

<p style="text-align: center; margin-top: 32px;"><a href="./" style="color:#555;text-decoration:none;">← 回平台首頁</a> ‧ <a href="map.html" style="color:#555;text-decoration:none;">議題地圖</a> ‧ <a href="search.html" style="color:#555;text-decoration:none;">搜尋</a></p>

</main>

<footer>
  資料更新:{p1[0]['last_updated'] if p1 else '—'} ‧ CC BY 4.0 ‧ 國教行動聯盟兒少人權監督平台
</footer>

</body>
</html>"""


def update_index_with_nap_metric(actions: list[dict]) -> bool:
    """在 _public/index.html 戰情室加入 NAP 第 8 項指標。"""
    if not INDEX_PAGE.exists():
        return False
    text = INDEX_PAGE.read_text(encoding="utf-8")
    widget = render_dashboard_widget(actions)

    # 在 DASHBOARD END 前插入(若該指標已存在則替換)
    import re
    if "NAP 第一期" in text:
        # 替換現有
        pattern = re.compile(
            r'<div class="metric" style="border-left-color: #b71c1c;">.*?NAP 第一期.*?</div>\s*</div>',
            re.DOTALL
        )
        text = pattern.sub(widget, text, count=1)
    else:
        # 插入到 DASHBOARD END 前
        text = text.replace("<!-- DASHBOARD END -->", widget + "\n<!-- DASHBOARD END -->")

    INDEX_PAGE.write_text(text, encoding="utf-8")
    return True


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--update", action="store_true")
    args = ap.parse_args()

    actions = fetch_actions()
    if not actions:
        print("❌ nap_action 表為空。先跑 /tmp/nap_populate.py", file=sys.stderr)
        return 1

    html = render_nap_page(actions)
    if args.update:
        NAP_PAGE.parent.mkdir(parents=True, exist_ok=True)
        NAP_PAGE.write_text(html, encoding="utf-8")
        print(f"✓ {NAP_PAGE.relative_to(ROOT)}({len(actions)} 項)")
        if update_index_with_nap_metric(actions):
            print(f"✓ 戰情室加入 NAP 指標(8 項即時數)")
    else:
        print(html)
    return 0


if __name__ == "__main__":
    sys.exit(main())
