#!/usr/bin/env python3
"""
脈絡追溯查詢工具（不是責任追溯）

設計紅線（Wave 92 起）：
1. 稱「脈絡追溯」非「責任追溯」
2. 每個歸因節點必附反證
3. 因果鏈 > 3 層自動加警告
4. 正反結果並陳
5. 論述（statement）與責任歸屬嚴格分離

Usage:
    # 1) 議題向前追溯
    python3 scripts/two_cov_trace.py --issue 廢死

    # 2) 行動者全紀錄
    python3 scripts/two_cov_trace.py --actor "廢死聯盟"

    # 3) 結果反推（含警告）
    python3 scripts/two_cov_trace.py --backtrack EV-2024-002

    # 4) 全文檢索
    python3 scripts/two_cov_trace.py --search "OP2 批准"
"""
from __future__ import annotations
import argparse
import json
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "data" / "two_cov.db"


def issue_timeline(conn, issue: str) -> None:
    """1) 議題向前追溯：依時序列出該議題所有事件"""
    cur = conn.execute(
        """SELECT e.event_date, e.event_type, COALESCE(a.name,'—') AS actor,
                  e.title, e.summary, e.is_positive_outcome, e.event_id, e.source_url
           FROM event e LEFT JOIN actor a ON e.actor_id=a.actor_id
           WHERE e.issue_tags LIKE ?
           ORDER BY e.event_date""",
        (f"%{issue}%",),
    )
    rows = cur.fetchall()
    if not rows:
        print(f"  無 issue「{issue}」之事件記錄")
        return

    print(f"\n=== 「{issue}」議題時序鏈（{len(rows)} 個事件） ===\n")
    for r in rows:
        date, typ, actor, title, summary, positive, eid, url = r
        positive_label = (
            " [多數視為正面]" if positive == 1 else
            " [多數視為負面]" if positive == 0 else ""
        )
        print(f"  {date}  [{typ:18}]  {actor}{positive_label}")
        print(f"     ↳ {title}")
        if summary:
            print(f"        {summary[:100]}")
        print(f"        ({eid}) {url or ''}")
        print()


def actor_record(conn, actor_name: str) -> None:
    """2) 行動者全紀錄"""
    cur = conn.execute(
        """SELECT e.event_date, e.event_type, e.title, e.summary, e.source_url
           FROM event e JOIN actor a ON e.actor_id=a.actor_id
           WHERE a.name LIKE ?
           ORDER BY e.event_date""",
        (f"%{actor_name}%",),
    )
    rows = cur.fetchall()
    if not rows:
        print(f"  無行動者「{actor_name}」之記錄")
        return

    # 取行動者基本資訊
    info = conn.execute(
        "SELECT name, actor_type, position_spectrum, active_period FROM actor WHERE name LIKE ?",
        (f"%{actor_name}%",),
    ).fetchone()
    if info:
        print(f"\n=== 行動者：{info[0]} ===")
        print(f"  類型：{info[1]}｜立場：{info[2]}｜活躍期：{info[3]}\n")

    print(f"全部論述記錄（{len(rows)} 筆，按時序）：\n")
    for date, typ, title, summary, url in rows:
        print(f"  {date}  [{typ}]")
        print(f"     {title}")
        if summary:
            print(f"     {summary[:100]}")
        print(f"     {url or ''}")
        print()


def backtrack(conn, event_id: str, depth: int = 0, max_depth: int = 3, visited: set = None) -> None:
    """3) 結果反推：給一個 outcome event，反向找出可能影響它的事件鏈

    紅線：超過 3 層自動加警告
    """
    if visited is None:
        visited = set()
    if event_id in visited or depth > max_depth:
        if depth > max_depth:
            print("  " * depth + f"  ⚠ 鏈長 > {max_depth}，停止追溯（紅線 3：避免過度推論）")
        return
    visited.add(event_id)

    # 列當前事件
    cur = conn.execute(
        """SELECT e.event_date, e.event_type, COALESCE(a.name,'—'), e.title, e.summary
           FROM event e LEFT JOIN actor a ON e.actor_id=a.actor_id
           WHERE e.event_id=?""",
        (event_id,),
    )
    r = cur.fetchone()
    if not r:
        return

    indent = "  " * depth
    if depth == 0:
        print(f"\n=== 反向追溯：{event_id} ===\n")
        print(f"{indent}結果事件：[{r[1]}] {r[3]}")
        print(f"{indent}  日期：{r[0]}｜行動者：{r[2]}")
        print(f"{indent}  {r[4] or ''}")
        print(f"\n{indent}↑ 之上層論述鏈（含反證）：\n")
    else:
        print(f"{indent}└→ [{r[1]}] {r[3]}（{r[0]}）")

    # 找指向這個 event 的所有 causal_link
    cur = conn.execute(
        """SELECT cl.from_event, cl.link_type, cl.evidence_strength,
                  cl.counter_evidence, cl.multi_causal_note
           FROM causal_link cl
           WHERE cl.to_event=?""",
        (event_id,),
    )
    links = cur.fetchall()

    for from_e, link_type, strength, counter, multi in links:
        prev = conn.execute(
            "SELECT title, event_date FROM event WHERE event_id=?", (from_e,)
        ).fetchone()
        if prev:
            warn = " ⚠ inferred" if strength == "inferred" else (" ⚠ contested" if strength == "contested" else "")
            print(f"{indent}  ← {from_e}（{link_type}, {strength}{warn}）")
            print(f"{indent}     {prev[0]}（{prev[1]}）")
            if counter:
                print(f"{indent}     反證 / 反事實：{counter[:120]}")
            if multi:
                print(f"{indent}     並列原因：{multi[:120]}")
            print()
        # 遞迴
        backtrack(conn, from_e, depth + 1, max_depth, visited)


def law_history(conn, law_query: str) -> None:
    """5) 法律修法歷程：列出該法律全部版本 + 條文 delta + 修法事件"""
    cur = conn.execute(
        """SELECT law_id, law_name_zh, law_pcode, enacted_date, primary_agency
           FROM law WHERE law_name_zh LIKE ?""",
        (f"%{law_query}%",),
    )
    laws = cur.fetchall()
    if not laws:
        print(f"  無法律「{law_query}」之記錄")
        return

    for law_id, name, pcode, enacted, agency in laws:
        print(f"\n=== 法律：{name}（{law_id}） ===")
        print(f"  全國法規資料庫 pcode：{pcode}")
        print(f"  制定日：{enacted}｜主管：{agency}\n")

        # 列版本
        vers = conn.execute(
            """SELECT version_id, version_label, promulgated_date, effective_date,
                      legislative_reason, is_current
               FROM law_version WHERE law_id=? ORDER BY promulgated_date""",
            (law_id,),
        ).fetchall()

        print(f"歷次版本（{len(vers)} 個）：\n")
        for v_id, label, prom, effect, reason, current in vers:
            tag = " [現行]" if current else ""
            print(f"  {prom}  {label}{tag}  ({v_id})")
            if reason:
                print(f"     立法理由：{reason[:80]}")

            # 列該版本的條文變動
            changes = conn.execute(
                """SELECT article_number, change_type, text_before, text_after, reason
                   FROM law_article_change WHERE version_id=?""",
                (v_id,),
            ).fetchall()
            for art, c_type, before, after, c_reason in changes:
                print(f"\n     [{c_type}] {art}")
                if before:
                    print(f"        修正前：{before[:80]}")
                if after:
                    print(f"        修正後：{after[:80]}")
                if c_reason:
                    print(f"        理由：{c_reason[:80]}")
            print()

        # 修法事件
        amends = conn.execute(
            """SELECT amendment_id, third_reading, key_changes, triggered_by_co
               FROM law_amendment WHERE law_id=? ORDER BY third_reading""",
            (law_id,),
        ).fetchall()
        if amends:
            print(f"修法事件（{len(amends)} 筆）：")
            for a_id, tr, key, triggered in amends:
                print(f"  {tr}  {a_id}")
                if key:
                    print(f"     關鍵變動：{key[:100]}")
                if triggered:
                    print(f"     觸發來源：{triggered}")
            print()

        # 行政命令
        orders = conn.execute(
            "SELECT order_name, order_type, promulgated_date FROM executive_order WHERE parent_law_id=?",
            (law_id,),
        ).fetchall()
        if orders:
            print(f"附屬行政命令 / 施行細則（{len(orders)} 筆）：")
            for o_name, o_type, o_date in orders:
                print(f"  {o_date}  [{o_type}] {o_name}")


def search_full_text(conn, query: str) -> None:
    """4) 全文檢索"""
    cur = conn.execute(
        "SELECT event_id, title, summary FROM event WHERE title LIKE ? OR summary LIKE ? OR full_quote LIKE ? LIMIT 20",
        (f"%{query}%", f"%{query}%", f"%{query}%"),
    )
    rows = cur.fetchall()
    print(f"\n=== 「{query}」搜尋結果（{len(rows)} 筆）===\n")
    for eid, title, summary in rows:
        print(f"  {eid}: {title}")
        if summary:
            print(f"      {summary[:100]}")
        print()


def main() -> int:
    parser = argparse.ArgumentParser()
    g = parser.add_mutually_exclusive_group(required=True)
    g.add_argument("--issue", help="議題向前追溯（如：廢死、同性婚姻、兒少自殺）")
    g.add_argument("--actor", help="行動者全紀錄（如：廢死聯盟）")
    g.add_argument("--backtrack", help="結果反推（給 event_id）")
    g.add_argument("--search", help="全文檢索")
    g.add_argument("--law", help="法律修法歷程（如：學生輔導法）")
    parser.add_argument("--max-depth", type=int, default=3,
                        help="反推鏈最大深度（紅線：超過 3 層加警告）")
    args = parser.parse_args()

    if not DB.exists():
        print(f"❌ DB 不存在：{DB}")
        return 1

    conn = sqlite3.connect(DB)
    try:
        if args.issue:
            issue_timeline(conn, args.issue)
        elif args.actor:
            actor_record(conn, args.actor)
        elif args.backtrack:
            backtrack(conn, args.backtrack, max_depth=args.max_depth)
        elif args.search:
            search_full_text(conn, args.search)
        elif args.law:
            law_history(conn, args.law)
    finally:
        conn.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
