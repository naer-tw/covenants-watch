#!/usr/bin/env python3
"""render_dashboard.py — 從 SQLite dashboard_metric 表渲染戰情室 HTML 片段。

Wave 63:取代 _public/index.html 中硬編碼的儀表板區塊,改為資料驅動。

對應 MVP 藍圖 §6 + 架構建議 §使用者介面:
  「首頁先展示『本月關鍵指標』儀表板(自殺率、霸凌通報、性剝削派案、兒保開案 5 項即時數)」

用法:
    python3 scripts/render_dashboard.py                  # 印 HTML 到 stdout
    python3 scripts/render_dashboard.py --update _public/index.html
        # 直接 in-place 更新 _public/index.html 之 <!-- DASHBOARD --> 區塊
"""
from __future__ import annotations

import argparse
import sqlite3
import sys
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "data" / "crw.db"

COLOR_HINT = {
    "red": "#d32f2f",
    "orange": "#ef6c00",
    "blue": "#1976d2",
    "green": "#2e7d32",
}

TREND_ICON = {
    "improving": "🟢",
    "stable": "🟡",
    "worsening": "🔴",
    "critical": "🚨",
}


def render_metrics() -> str:
    if not DB.exists():
        print(f"❌ SQLite not found: {DB}", file=sys.stderr)
        return ""
    conn = sqlite3.connect(str(DB))
    rows = conn.execute(
        "SELECT label_zh, value_display, period_label, source_agency, trend, color_hint, related_pi "
        "FROM dashboard_metric ORDER BY sort_order"
    ).fetchall()
    conn.close()

    parts = ['<div class="dashboard">']
    for label, value, period, source, trend, color, pi in rows:
        c = COLOR_HINT.get(color, "#E8734A")
        icon = TREND_ICON.get(trend, "")
        pi_link = f'<a href="issues/{pi}.html" style="color:#888;text-decoration:none;font-size:11px;">→ {pi}</a>' if pi.startswith("PI-") else f'<span style="color:#888;font-size:11px;">{pi}</span>'
        parts.append(f"""  <div class="metric" style="border-left-color: {c};">
    <div class="label">{label}</div>
    <div class="value" style="color: {c};">{icon} {value}</div>
    <div class="source">{period} ‧ {source} ‧ {pi_link}</div>
  </div>""")
    parts.append("</div>")
    return "\n".join(parts)


def update_index(index_path: Path, dashboard_html: str) -> bool:
    if not index_path.exists():
        print(f"❌ index.html not found: {index_path}", file=sys.stderr)
        return False
    text = index_path.read_text(encoding="utf-8")
    pattern = re.compile(
        r"(<!-- DASHBOARD START -->).*?(<!-- DASHBOARD END -->)",
        re.DOTALL,
    )
    new_block = f"<!-- DASHBOARD START -->\n{dashboard_html}\n<!-- DASHBOARD END -->"
    if pattern.search(text):
        text = pattern.sub(new_block, text)
    else:
        # 找現有 <div class="dashboard">...</div> 區塊取代
        existing = re.compile(r'<div class="dashboard">.*?</div>\s*</div>', re.DOTALL)
        if existing.search(text):
            text = existing.sub(new_block, text, count=1)
        else:
            print("⚠ 找不到既有儀表板區塊或標記;在 <h2>📊 戰情室</h2> 後注入")
            text = re.sub(r"(<h2>📊[^<]*</h2>)", r"\1\n" + new_block, text, count=1)
    index_path.write_text(text, encoding="utf-8")
    return True


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--update", help="In-place 更新指定 HTML 檔案的 dashboard 區塊")
    args = ap.parse_args()
    html = render_metrics()
    if not html:
        return 1
    if args.update:
        ok = update_index(Path(args.update), html)
        if ok:
            count = html.count('<div class="metric"')
            print(f"✓ 更新 {args.update}({count} 項指標)")
        return 0 if ok else 1
    print(html)
    return 0


if __name__ == "__main__":
    sys.exit(main())
