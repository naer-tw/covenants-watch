#!/usr/bin/env python3
"""
md_to_sqlite.py — 把 Markdown 母資料同步到 SQLite。

設計原則:
- Markdown = 單一真實來源(SSOT),SQLite = 衍生資料庫(可重建)
- INSERT OR REPLACE 確保 idempotent(可重複執行)
- 不修改 Markdown,只讀
- 只處理 frontmatter + 顯式段落,不做 NLP 推論

用法:
    python3 scripts/md_to_sqlite.py                # 全部同步
    python3 scripts/md_to_sqlite.py --table policy_issue   # 只同步議題表
    python3 scripts/md_to_sqlite.py --rebuild              # 先 drop 再建
    python3 scripts/md_to_sqlite.py --verify               # 不寫入,只檢查
"""
from __future__ import annotations

import argparse
import json
import re
import sqlite3
import sys
from pathlib import Path

# Wave 36:共用 frontmatter 模組
from _md_frontmatter import load_md, parse_yaml  # noqa: F401

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "data" / "crw.db"
DDL = ROOT / "schema" / "ddl.sql"


# Issue #4 修法:用模組層級 list 累積警告,在 main 結束時統一輸出
_section_warnings: list[str] = []


def extract_section(md: str, heading_patterns, source: str = "") -> str:
    """抓取 ## 標題下段落內容,直到下一個 ## 或檔尾。
    heading_patterns 可為單一 str 或 list[str](alternatives,依序嘗試)。
    Issue #4 修法:全部 alternatives 都未找到時記錄警告。"""
    if isinstance(heading_patterns, str):
        heading_patterns = [heading_patterns]
    for pat in heading_patterns:
        # 支援兩種格式:「## 一、概要」與「## 概要」(無 X、 前綴)
        m = re.search(
            rf"^##\s+(?:[一二三四五六七八九十]+、\s*)?{pat}.*?\n(.*?)(?=^##\s|\Z)",
            md, re.MULTILINE | re.DOTALL,
        )
        if m:
            return m.group(1).strip()
    _section_warnings.append(
        f"  ⚠ {source or '?'}: 任一 section 未找到 (試了 {heading_patterns}) → 寫入空字串"
    )
    return ""


# ---------------------------------------------------------------------
# 各表 ingest
# ---------------------------------------------------------------------
def safe_rel_insert(cur: sqlite3.Cursor, sql: str, params: tuple, warnings: list) -> None:
    """若 FK 失敗(目標不存在),記錄 warning 而不中斷。"""
    try:
        cur.execute(sql, params)
    except sqlite3.IntegrityError as e:
        warnings.append(f"  ⚠ skip rel: {params} — {e}")


def ingest_policy_issues(con: sqlite3.Connection) -> int:
    cur = con.cursor()
    warnings: list = []
    n = 0
    for path in sorted((ROOT / "data" / "policy_issues").glob("PI-*.md")):
        meta, body = load_md(path)
        if not meta:
            continue
        cur.execute("""
            INSERT OR REPLACE INTO policy_issue
            (issue_id, title_zh, title_en, slug, summary_adult, summary_kid,
             cluster, severity, status, schema_type, last_updated, published, editor_owner)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            meta.get("issue_id"),
            meta.get("title_zh"),
            meta.get("title_en"),
            meta.get("slug"),
            extract_section(body, r"議題摘要", path.name),
            extract_section(body, r"兒少版", path.name),
            meta.get("cluster"),
            meta.get("severity"),
            meta.get("status"),
            meta.get("schema_type", "Article"),
            meta.get("last_updated"),
            1 if meta.get("published") else 0,
            meta.get("editor_owner"),
        ))
        # 多對多關聯(目標可能尚未灌入,容錯處理)
        issue_id = meta.get("issue_id")
        for crc_id in meta.get("crc_articles", []) or []:
            safe_rel_insert(cur,
                "INSERT OR IGNORE INTO rel_issue_crc(issue_id, crc_id) VALUES (?, ?)",
                (issue_id, crc_id), warnings)
        for co_id in meta.get("co_paragraphs", []) or []:
            safe_rel_insert(cur,
                "INSERT OR IGNORE INTO rel_issue_co(issue_id, co_id) VALUES (?, ?)",
                (issue_id, co_id), warnings)
        for stat_id in meta.get("indicators", []) or []:
            safe_rel_insert(cur,
                "INSERT OR IGNORE INTO rel_issue_stat(issue_id, stat_id) VALUES (?, ?)",
                (issue_id, stat_id), warnings)
        n += 1
    if warnings:
        print(f"  ({len(warnings)} 筆關聯因目標尚未灌入而跳過,日後補)")
    return n


def ingest_domestic_laws(con: sqlite3.Connection) -> int:
    cur = con.cursor()
    n = 0
    for path in sorted((ROOT / "data" / "domestic_laws").glob("L*.md")):
        meta, _ = load_md(path)
        if not meta:
            continue
        cur.execute("""
            INSERT OR REPLACE INTO domestic_law
            (law_id, name_zh, short_name, competent_agency, source_url, last_amend_date)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            meta.get("law_id"),
            meta.get("name_zh"),
            meta.get("short_name"),
            meta.get("competent_agency"),
            meta.get("source_url"),
            meta.get("last_amend_date"),
        ))
        n += 1
    return n


def ingest_advocacy_actions(con: sqlite3.Connection) -> int:
    cur = con.cursor()
    warnings: list = []
    n = 0
    actions_dir = ROOT / "data" / "advocacy_actions"
    if not actions_dir.exists():
        return 0
    for path in sorted(actions_dir.glob("A-*.md")):
        meta, body = load_md(path)
        if not meta:
            continue
        main_arg = extract_section(body, [r"主要主張", r"立場聲明", r"概要", r"出席背景", r"組織說明"], path.name)
        cur.execute("""
            INSERT OR REPLACE INTO advocacy_action
            (action_id, title, action_date, action_type, main_argument,
             public_url, quotable_excerpt)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            meta.get("action_id"),
            meta.get("title"),
            meta.get("action_date"),
            meta.get("action_type"),
            main_arg,
            meta.get("public_url"),
            main_arg,
        ))
        action_id = meta.get("action_id")
        for issue_id in meta.get("related_issues", []) or []:
            safe_rel_insert(cur,
                "INSERT OR IGNORE INTO rel_issue_action(issue_id, action_id) VALUES (?, ?)",
                (issue_id, action_id), warnings)
        n += 1
    if warnings:
        print(f"  ({len(warnings)} 筆關聯跳過)")
    return n


def extract_status_and_note(s) -> tuple:
    """Issue #4-extra 修法:把「查證屬實(法院判決)」拆成 (status, note)。
    舊版 strip_paren_note 直接丟掉註記,違反「不可逆遺失資料」原則。
    回傳:(主值, 註記 or None)"""
    if s is None:
        return (None, None)
    s = str(s)
    m = re.search(r"^([^\((]*?)[\((]([^\)\)]*)[\))]\s*$", s)
    if m:
        return (m.group(1).strip(), m.group(2).strip())
    return (s.strip(), None)


# Backwards compat 別名(若外部仍呼叫舊名)
def strip_paren_note(s) -> str:
    status, _ = extract_status_and_note(s)
    return status


def ingest_cases(con: sqlite3.Connection) -> int:
    cur = con.cursor()
    warnings: list = []
    n = 0
    cases_dir = ROOT / "data" / "cases"
    if not cases_dir.exists():
        return 0
    for path in sorted(cases_dir.glob("C-*.md")):
        meta, body = load_md(path)
        if not meta:
            continue
        rights = meta.get("rights_violated", []) or []
        v_status, v_note = extract_status_and_note(meta.get("verification_status"))
        p_status, p_note = extract_status_and_note(meta.get("publication_status"))
        # 註記保留為 description 末尾的小段,不丟失
        desc = extract_section(body, [r"案例概要", r"概要"], path.name)
        if v_note or p_note:
            desc += f"\n\n_(查證來源:{v_note or '—'};公開狀態註記:{p_note or '—'})_"
        cur.execute("""
            INSERT OR REPLACE INTO case_story
            (case_id, title_anonymized, occurred_period, region_blurred,
             description, rights_violated, verification_status, publication_status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            meta.get("case_id"),
            meta.get("title_anonymized"),
            meta.get("occurred_period"),
            meta.get("region_blurred"),
            desc,
            json.dumps(rights, ensure_ascii=False) if rights else None,
            v_status,
            p_status,
        ))
        case_id = meta.get("case_id")
        for issue_id in meta.get("related_issues", []) or []:
            safe_rel_insert(cur,
                "INSERT OR IGNORE INTO rel_issue_case(issue_id, case_id) VALUES (?, ?)",
                (issue_id, case_id), warnings)
        n += 1
    if warnings:
        print(f"  ({len(warnings)} 筆關聯跳過)")
    return n


# ---------------------------------------------------------------------
# CRC 條文 / CO / 統計指標 — 從單一 Markdown 檔解析(較複雜)
# ---------------------------------------------------------------------
CRC_ENTRY_RE = re.compile(
    r"^###\s+(CRC-\d+)\s+(.+?)\s*$\n(.*?)(?=^###|\Z)",
    re.MULTILINE | re.DOTALL,
)


def ingest_crc_articles(con: sqlite3.Connection) -> int:
    cur = con.cursor()
    text = (ROOT / "data" / "crc_articles.md").read_text(encoding="utf-8")
    n = 0
    for m in CRC_ENTRY_RE.finditer(text):
        crc_id, name_zh, body = m.group(1), m.group(2).strip(), m.group(3)
        article_no = int(crc_id.split("-")[1])

        def grab(label: str) -> str:
            mm = re.search(rf"-\s*\*\*{label}.*?\*\*\s*:\s*(.+?)(?=\n-\s*\*\*|\Z)",
                           body, re.DOTALL)
            return mm.group(1).strip() if mm else ""

        cur.execute("""
            INSERT OR REPLACE INTO crc_article
            (crc_id, article_no, name_zh, text_zh, plain_zh)
            VALUES (?, ?, ?, ?, ?)
        """, (
            crc_id, article_no, name_zh,
            grab(r"條文\(中\)"),
            grab(r"白話"),
        ))
        n += 1
    return n


# ---------------------------------------------------------------------
# 主流程
# ---------------------------------------------------------------------
def ingest_concluding_observations(con: sqlite3.Connection) -> int:
    """從 CRC1_CO_98條.csv 與 CRC2_CO_72條.csv 灌入歷次結論性意見。"""
    import csv
    cur = con.cursor()
    n = 0
    for cycle, fname in [(1, "CRC1_CO_98條.csv"), (2, "CRC2_CO_72條.csv")]:
        csv_path = ROOT / "data" / "sources" / fname
        if not csv_path.exists():
            print(f"  ⚠ {fname} 不存在,跳過。先跑 scripts/parse_co_to_md.py --cycle {cycle}")
            continue
        with csv_path.open(encoding="utf-8") as f:
            for row in csv.DictReader(f):
                cur.execute("""
                    INSERT OR REPLACE INTO concluding_observation
                    (co_id, cycle, co_paragraph, text_zh, cluster)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    row["co_id"],
                    int(row["cycle"]),
                    row["co_paragraph"],
                    row["text_zh"],
                    row["cluster"],
                ))
                for crc_id in row["crc_articles"].split(","):
                    crc_id = crc_id.strip()
                    if not crc_id or "OPSC" in crc_id or "OPAC" in crc_id or "OPIC" in crc_id:
                        continue
                    try:
                        cur.execute("INSERT OR IGNORE INTO rel_co_crc(co_id, crc_id) VALUES (?, ?)",
                                    (row["co_id"], crc_id))
                    except sqlite3.IntegrityError:
                        pass
                n += 1
    return n


# 順序很重要:被關聯的表(crc_article、domestic_law、concluding_observation)必須先建,
# 主體表(policy_issue)中間,引用主體的表(case_story、advocacy_action)在後。
TABLES = {
    "crc_article": ingest_crc_articles,
    "domestic_law": ingest_domestic_laws,
    "concluding_observation": ingest_concluding_observations,
    "policy_issue": ingest_policy_issues,
    "case_story": ingest_cases,
    "advocacy_action": ingest_advocacy_actions,
}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--table", choices=list(TABLES), help="只同步單一表")
    ap.add_argument("--rebuild", action="store_true", help="先刪 DB 再從 DDL 重建")
    ap.add_argument("--verify", action="store_true", help="只統計,不寫入")
    args = ap.parse_args()

    if args.rebuild:
        if DB.exists():
            DB.unlink()
            for sfx in ("-shm", "-wal"):
                p = DB.with_suffix(DB.suffix + sfx)
                if p.exists():
                    p.unlink()
        # 從 DDL 建空庫
        con = sqlite3.connect(DB)
        con.executescript(DDL.read_text(encoding="utf-8"))
        con.commit()
        con.close()
        print(f"✓ 重建 {DB.relative_to(ROOT)}")

    con = sqlite3.connect(DB)
    con.execute("PRAGMA foreign_keys = ON")

    targets = [args.table] if args.table else list(TABLES)
    total = 0
    for tbl in targets:
        n = TABLES[tbl](con)
        print(f"  {tbl:<20} {n:>4} 筆")
        total += n

    if args.verify:
        con.rollback()
        print(f"\n[verify mode] 共 {total} 筆,未寫入")
    else:
        con.commit()
        print(f"\n✓ 寫入 {total} 筆")

    # Issue #4 修法:統一輸出 section 警告
    if _section_warnings:
        print(f"\n⚠ {len(_section_warnings)} 個 section 抽取警告(議題卡片格式不一致):")
        for w in _section_warnings[:10]:
            print(w)
        if len(_section_warnings) > 10:
            print(f"  ... 另 {len(_section_warnings) - 10} 個")

    # 統計現況
    cur = con.cursor()
    print("\n=== 寫入後統計 ===")
    for t in ("crc_article", "concluding_observation", "policy_issue", "domestic_law",
              "advocacy_action", "case_story",
              "rel_issue_crc", "rel_issue_action", "rel_issue_case", "rel_issue_co",
              "rel_co_crc"):
        try:
            cnt = cur.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
            print(f"  {t:<24} {cnt}")
        except sqlite3.OperationalError:
            pass

    con.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
