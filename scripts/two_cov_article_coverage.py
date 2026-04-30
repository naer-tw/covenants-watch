#!/usr/bin/env python3
"""
22 條核心條文盤點 — 議程滲入掃描器

回應第四輪 cold read 之 Wave 90+ 優先工作：
> 「凡偏離均值 > 2σ 之條文需在卡片開頭加註『本平台特別關注此條文之理由』」

掃描所有 16 PI 之 ICCPR/ICESCR 條文提及頻率，產出：
1. 22 條核心條文 × 16 PI 出現次數矩陣
2. 偏離均值 > 2σ 之條文清單（議程滲入候選）
3. 每張 PI 之條文提及向量

Usage:
    python3 scripts/two_cov_article_coverage.py
    python3 scripts/two_cov_article_coverage.py --html
"""
from __future__ import annotations
import argparse
import re
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PI_DIR = ROOT / "data" / "policy_issues"

# ICCPR 1-27 + ICESCR 1-15（核心實質權利）
ICCPR_ARTICLES = list(range(1, 28))
ICESCR_ARTICLES = list(range(1, 16))

# Regex: ICCPR Art.X / ICCPR §X / 第 X 條 + 兩公約上下文
ICCPR_RE = re.compile(
    r"(?:ICCPR|公政公約|Art\.|Article|§)\s*(\d+)(?:[-\.]\d+)?\s*條?",
    re.IGNORECASE,
)
ICESCR_RE = re.compile(
    r"(?:ICESCR|經社文公約)\s*(?:Art\.|Article|§)?\s*(\d+)(?:[-\.]\d+)?\s*條?",
    re.IGNORECASE,
)


def count_articles_in_pi(pi_path: Path) -> dict:
    """掃描單張 PI 之條文提及"""
    text = pi_path.read_text(encoding="utf-8")
    iccpr_counts = {n: 0 for n in ICCPR_ARTICLES}
    icescr_counts = {n: 0 for n in ICESCR_ARTICLES}

    # ICCPR
    for m in ICCPR_RE.finditer(text):
        try:
            n = int(m.group(1))
            if n in iccpr_counts:
                iccpr_counts[n] += 1
        except ValueError:
            pass

    # ICESCR
    for m in ICESCR_RE.finditer(text):
        try:
            n = int(m.group(1))
            if n in icescr_counts:
                icescr_counts[n] += 1
        except ValueError:
            pass

    return {"ICCPR": iccpr_counts, "ICESCR": icescr_counts}


def build_matrix() -> dict:
    """16 PI × 22 條矩陣"""
    matrix = {}
    for pi_md in sorted(PI_DIR.glob("PI-*.md")):
        pi_id = pi_md.name.split("_")[0]
        matrix[pi_id] = count_articles_in_pi(pi_md)
    return matrix


def find_outliers(matrix: dict) -> dict:
    """找偏離均值 > 2σ 之條文"""
    iccpr_totals = {n: 0 for n in ICCPR_ARTICLES}
    icescr_totals = {n: 0 for n in ICESCR_ARTICLES}
    for pi_data in matrix.values():
        for n in ICCPR_ARTICLES:
            iccpr_totals[n] += pi_data["ICCPR"][n]
        for n in ICESCR_ARTICLES:
            icescr_totals[n] += pi_data["ICESCR"][n]

    iccpr_vals = list(iccpr_totals.values())
    icescr_vals = list(icescr_totals.values())

    def outliers(vals: list, names: list[int]) -> list:
        if len(vals) < 2:
            return []
        mean = statistics.mean(vals)
        stdev = statistics.stdev(vals)
        threshold = mean + 2 * stdev
        return [
            (n, vals[i], round((vals[i] - mean) / stdev, 2) if stdev else 0)
            for i, n in enumerate(names)
            if vals[i] > threshold
        ]

    return {
        "ICCPR_totals": iccpr_totals,
        "ICESCR_totals": icescr_totals,
        "ICCPR_outliers": outliers(iccpr_vals, ICCPR_ARTICLES),
        "ICESCR_outliers": outliers(icescr_vals, ICESCR_ARTICLES),
        "ICCPR_mean": round(statistics.mean(iccpr_vals), 2),
        "ICCPR_stdev": round(statistics.stdev(iccpr_vals), 2),
        "ICESCR_mean": round(statistics.mean(icescr_vals), 2),
        "ICESCR_stdev": round(statistics.stdev(icescr_vals), 2),
    }


def render_text(matrix: dict, outliers: dict) -> str:
    out = ["# 22 條核心條文完整盤點（議程滲入掃描）", ""]
    out.append("## ICCPR 1-27 條提及次數")
    out.append("")
    out.append(f"均值 {outliers['ICCPR_mean']} / 標準差 {outliers['ICCPR_stdev']}")
    out.append("")
    out.append("| 條 | 全平台提及次數 | 偏離 |")
    out.append("|---:|---:|---|")
    for n in ICCPR_ARTICLES:
        total = outliers["ICCPR_totals"][n]
        z = round((total - outliers["ICCPR_mean"]) / outliers["ICCPR_stdev"], 2) if outliers["ICCPR_stdev"] else 0
        flag = " 🔴 outlier" if z > 2 else ""
        out.append(f"| {n} | {total} | z={z}{flag} |")

    out.append("")
    out.append("## ICESCR 1-15 條提及次數")
    out.append("")
    out.append(f"均值 {outliers['ICESCR_mean']} / 標準差 {outliers['ICESCR_stdev']}")
    out.append("")
    out.append("| 條 | 全平台提及次數 | 偏離 |")
    out.append("|---:|---:|---|")
    for n in ICESCR_ARTICLES:
        total = outliers["ICESCR_totals"][n]
        z = round((total - outliers["ICESCR_mean"]) / outliers["ICESCR_stdev"], 2) if outliers["ICESCR_stdev"] else 0
        flag = " 🔴 outlier" if z > 2 else ""
        out.append(f"| {n} | {total} | z={z}{flag} |")

    out.append("")
    out.append("## 議程滲入掃描結果")
    out.append("")
    if outliers["ICCPR_outliers"]:
        out.append("### ICCPR 偏離 > 2σ 之條文（議程滲入候選）")
        for n, count, z in outliers["ICCPR_outliers"]:
            out.append(f"- ICCPR Art.{n}：{count} 次（z={z}）— **須在對應 PI 卡開頭加註平台特別關注理由**")
    else:
        out.append("### ICCPR：無條文偏離 > 2σ ✓")

    out.append("")
    if outliers["ICESCR_outliers"]:
        out.append("### ICESCR 偏離 > 2σ 之條文（議程滲入候選）")
        for n, count, z in outliers["ICESCR_outliers"]:
            out.append(f"- ICESCR Art.{n}：{count} 次（z={z}）— **須在對應 PI 卡開頭加註平台特別關注理由**")
    else:
        out.append("### ICESCR：無條文偏離 > 2σ ✓")

    return "\n".join(out)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--html", action="store_true")
    parser.add_argument(
        "--out",
        default=str(ROOT / "data" / "evidence" / "article_coverage_report.md"),
    )
    args = parser.parse_args()

    matrix = build_matrix()
    outliers = find_outliers(matrix)
    report = render_text(matrix, outliers)

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(report, encoding="utf-8")
    print(f"  ✓ {out_path}")
    print()
    # 簡略 stdout
    print(f"ICCPR 均值={outliers['ICCPR_mean']} σ={outliers['ICCPR_stdev']}")
    print(f"  outliers (>2σ): {len(outliers['ICCPR_outliers'])} 條")
    for n, count, z in outliers["ICCPR_outliers"]:
        print(f"    Art.{n}: {count} 次 (z={z})")
    print(f"\nICESCR 均值={outliers['ICESCR_mean']} σ={outliers['ICESCR_stdev']}")
    print(f"  outliers (>2σ): {len(outliers['ICESCR_outliers'])} 條")
    for n, count, z in outliers["ICESCR_outliers"]:
        print(f"    Art.{n}: {count} 次 (z={z})")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
