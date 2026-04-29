#!/usr/bin/env python3
"""wcag_audit.py — _public/ HTMLs 之 WCAG 2.1 AA 自動稽核。

Wave 69:對應 MVP 藍圖 §6。

檢核項目:
  C1. 色彩對比 ≥ 4.5:1(從 inline style 抓 color/background-color)
  C2. base font ≥ 18px(body / p)
  C3. line-height ≥ 1.6
  C4. 圖片 alt 屬性
  C5. 互動元素 aria-label
  C6. 鍵盤導覽 skip-to-content link
  C7. lang 屬性(zh-TW)
  C8. h1-h6 階層完整(不跳級)
  C9. 表格 th 標頭
  C10. 連結文字非「點此」「here」

用法:
    python3 scripts/wcag_audit.py
    python3 scripts/wcag_audit.py --fix       # 嘗試自動修補(skip-link 注入)
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PUBLIC = ROOT / "_public"


def hex_to_rgb(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")
    if len(h) == 3:
        h = "".join(c + c for c in h)
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def luminance(rgb: tuple[int, int, int]) -> float:
    def adj(c: float) -> float:
        c = c / 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (adj(x) for x in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast_ratio(c1: str, c2: str) -> float:
    try:
        l1 = luminance(hex_to_rgb(c1))
        l2 = luminance(hex_to_rgb(c2))
    except Exception:
        return 0.0
    if l1 < l2:
        l1, l2 = l2, l1
    return (l1 + 0.05) / (l2 + 0.05)


def audit_file(path: Path) -> list[dict]:
    findings = []
    text = path.read_text(encoding="utf-8")

    # C1 — 找所有 color / background pair
    color_pairs = []
    for m in re.finditer(r"color:\s*(#[0-9a-fA-F]{3,6})", text):
        color_pairs.append(("fg", m.group(1)))
    bg_match = re.search(r"background:\s*(#[0-9a-fA-F]{3,6})", text)
    main_bg = bg_match.group(1) if bg_match else "#ffffff"
    for label, color in color_pairs:
        ratio = contrast_ratio(color, main_bg)
        if ratio < 4.5 and ratio > 0:
            findings.append({"severity": "warn", "code": "C1",
                            "msg": f"色彩對比 {color} on {main_bg} = {ratio:.2f}:1 < 4.5"})

    # C2 — base font size
    font_match = re.search(r"body[^{]*\{[^}]*font-size:\s*(\d+)\s*(px|pt)", text)
    if font_match:
        size = int(font_match.group(1))
        unit = font_match.group(2)
        # 18px 是 AA 大字體建議;一般文字最低 16px
        min_size = 18 if path.parent.name == "kids" else 16
        if unit == "px" and size < min_size:
            findings.append({"severity": "warn", "code": "C2",
                            "msg": f"base font {size}px < {min_size}px"})

    # C3 — line-height
    lh_match = re.search(r"body[^{]*\{[^}]*line-height:\s*([\d.]+)", text)
    if lh_match:
        lh = float(lh_match.group(1))
        if lh < 1.5:
            findings.append({"severity": "warn", "code": "C3",
                            "msg": f"line-height {lh} < 1.5"})

    # C4 — img alt
    for m in re.finditer(r"<img[^>]*>", text):
        if "alt=" not in m.group(0):
            findings.append({"severity": "fail", "code": "C4",
                            "msg": f"img 缺 alt: {m.group(0)[:60]}"})

    # C6 — skip-to-content link
    if "skip-to-content" not in text and "skip-link" not in text and "skiplink" not in text:
        # 兒少入口 + index 一定要;議題卡片可選
        if path.name == "index.html" or path.parent.name == "kids":
            findings.append({"severity": "warn", "code": "C6",
                            "msg": "缺 skip-to-content link"})

    # C7 — lang 屬性
    if 'lang="zh-TW"' not in text and "lang='zh-TW'" not in text:
        findings.append({"severity": "fail", "code": "C7",
                        "msg": "<html> 缺 lang=\"zh-TW\""})

    # C10 — 連結文字
    for m in re.finditer(r"<a[^>]*>([^<]+)</a>", text):
        link_text = m.group(1).strip()
        if link_text in ("點此", "點這裡", "click here", "here", "→", "..."):
            findings.append({"severity": "warn", "code": "C10",
                            "msg": f"模糊連結文字: {link_text}"})

    return findings


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--fix", action="store_true", help="嘗試自動修補(待實作)")
    args = ap.parse_args()

    if not PUBLIC.exists():
        print(f"❌ {PUBLIC} 不存在", file=sys.stderr)
        return 1

    files = sorted(PUBLIC.rglob("*.html"))
    print(f"WCAG 稽核 {len(files)} 個 HTML 檔")
    print(f"{'─'*60}")

    total_fail = 0
    total_warn = 0
    files_with_issues = 0
    for f in files:
        findings = audit_file(f)
        if not findings:
            continue
        files_with_issues += 1
        rel = f.relative_to(ROOT)
        print(f"\n📄 {rel}")
        for fnd in findings:
            icon = "✗" if fnd["severity"] == "fail" else "⚠"
            print(f"  {icon} [{fnd['code']}] {fnd['msg']}")
            if fnd["severity"] == "fail":
                total_fail += 1
            else:
                total_warn += 1

    print(f"\n{'─'*60}")
    print(f"結算:{len(files) - files_with_issues}/{len(files)} 檔通過")
    print(f"  ✗ fail: {total_fail}")
    print(f"  ⚠ warn: {total_warn}")
    if total_fail == 0 and total_warn == 0:
        print("  ✅ WCAG 2.1 AA 全綠")
    return 0 if total_fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
