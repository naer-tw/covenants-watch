#!/usr/bin/env python3
"""
統計分析骨架（PI-12 / PI-13 配合）

採用：
- chi-square 卡方檢定（政黨間援引差異）
- Gini 基尼係數（條文集中度）
- 線性回歸 + 趨勢檢定（14 年走勢）

Usage:
    python3 scripts/two_cov_statistical_analysis.py --tests chi_square,gini,trend
"""
from __future__ import annotations
import argparse
import math
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "data" / "two_cov.db"


def gini_coefficient(values: list[float]) -> float:
    """計算基尼係數（0=完全平均，1=完全集中）

    用於：條文援引集中度
    """
    if not values or sum(values) == 0:
        return 0.0
    sorted_vals = sorted(values)
    n = len(sorted_vals)
    cum = sum((i + 1) * v for i, v in enumerate(sorted_vals))
    return (2 * cum) / (n * sum(sorted_vals)) - (n + 1) / n


def chi_square_test(observed: list[list[int]]) -> tuple[float, float]:
    """卡方檢定（政黨 × 條文交叉表）

    回傳 (chi_square_statistic, degrees_of_freedom)
    p-value 計算需 scipy（用戶須安裝），此處僅算統計量
    """
    rows = len(observed)
    cols = len(observed[0]) if rows else 0
    if rows < 2 or cols < 2:
        return 0.0, 0
    row_totals = [sum(r) for r in observed]
    col_totals = [sum(observed[i][j] for i in range(rows)) for j in range(cols)]
    grand = sum(row_totals)
    if grand == 0:
        return 0.0, 0
    chi_sq = 0.0
    for i in range(rows):
        for j in range(cols):
            expected = row_totals[i] * col_totals[j] / grand
            if expected > 0:
                chi_sq += (observed[i][j] - expected) ** 2 / expected
    df = (rows - 1) * (cols - 1)
    return chi_sq, df


def get_citation_distribution(conn) -> dict:
    """從 legislative_citation 表取出條文援引分布"""
    cur = conn.execute(
        """SELECT article_cited, COUNT(*) as n
           FROM legislative_citation
           WHERE article_cited IS NOT NULL
           GROUP BY article_cited"""
    )
    return dict(cur.fetchall())


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--tests",
        type=str,
        default="chi_square,gini,trend",
        help="逗號分隔：chi_square / gini / trend",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=str(ROOT / "_public" / "dashboards" / "statistical_summary.html"),
    )
    args = parser.parse_args()

    if not DB.exists():
        print(f"❌ DB 不存在：{DB}")
        return 1

    conn = sqlite3.connect(DB)
    tests = args.tests.split(",")

    # 預檢資料量
    n_lc = conn.execute("SELECT COUNT(*) FROM legislative_citation").fetchone()[0]
    if n_lc == 0:
        print("⚠ legislative_citation 表為空")
        print("  須先跑 two_cov_fetch_legislative.py 抓取資料")
        print("  本腳本目前僅做樣本演算法驗證")
        # 用樣本資料示範
        sample = [10, 25, 5, 200, 15, 8, 50, 3, 12, 7]
        gini = gini_coefficient(sample)
        print(f"\n[範例 sample]")
        print(f"  條文援引次數：{sample}")
        print(f"  Gini 係數：{gini:.3f}")
        if gini > 0.5:
            print(f"  → 高度集中（Gini > 0.5）")
        else:
            print(f"  → 相對平均")
        return 0

    if "gini" in tests:
        dist = get_citation_distribution(conn)
        gini = gini_coefficient(list(dist.values()))
        print(f"條文援引 Gini 係數：{gini:.3f}")
        # TODO: 與 CRC/CEDAW/CRPD 對照組比較

    if "chi_square" in tests:
        # TODO: 政黨 × 條文交叉表
        print("⚠ chi_square 待實作")

    if "trend" in tests:
        # TODO: 14 年趨勢線性回歸
        print("⚠ trend 待實作")

    conn.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
