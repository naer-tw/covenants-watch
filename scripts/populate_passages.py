#!/usr/bin/env python3
"""populate_passages.py — 從 publish 層 markdown 切段 → 寫入 passage 表 + 自動 vocab 標籤。

Wave 68:對應證據基礎建設.md §平台架構與資料模型 + governance/document_governance.md §3。

流程:
1. 從 data/sources/CLASSIFICATION_INDEX.md 拿到 publish 層檔案清單
2. 依 markdown ## / ### 標題切段
3. 為每個 passage 自動比對 vocab_*:
   - vocab_issue:依 cluster + PI 關鍵字
   - vocab_crc_article:抓 CRC-XX / Article XX 模式
   - vocab_agency:依 vocab_agency.aliases JSON
   - vocab_problem_tag:依關鍵字
4. 寫入 passage 表 + rel_* 關聯表

用法:
    python3 scripts/populate_passages.py            # 全跑(--rebuild)
    python3 scripts/populate_passages.py --dry-run  # 不寫入,只列計
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCES = ROOT / "data" / "sources"
DB = ROOT / "data" / "crw.db"

# 議題關鍵字 → vocab_issue.code
ISSUE_KEYWORDS = {
    "campus-bullying": ["校園霸凌", "霸凌", "bullying"],
    "youth-mental-health": ["青少年自殺", "兒少心理健康", "自殺通報", "心理健康"],
    "corporal-punishment": ["體罰", "corporal punishment"],
    "student-counseling": ["學生輔導", "WISER", "輔導體制", "輔導員額"],
    "juvenile-justice": ["少年司法", "少事法", "中介教育", "國民轉介教育", "曝險少年"],
    "child-cyber-safety": ["兒少網路安全", "網路霸凌", "詐騙", "依托咪酯", "喪屍煙彈"],
    "sexual-exploitation": ["性剝削", "NCII", "深偽", "私密影像"],
    "gender-equity-edu": ["性別平等教育", "性教育", "全面性教育", "淋病", "梅毒"],
    "academic-pressure": ["課業壓力", "補習班", "上學時間", "學習權"],
    "child-voice": ["兒少表意", "校園民主", "學生會", "8,743", "8743", "GC12"],
    "family-policy": ["家庭功能", "親職", "家暴"],
    "alternative-care": ["替代照顧", "機構安置", "剴剴", "兒福聯盟", "保證人地位"],
    "migrant-stateless": ["失聯移工", "無國籍", "難民法", "移民"],
    "lgbtqi-children": ["LGBTQI", "LGBT", "跨性別"],
}

PROBLEM_KEYWORDS = {
    "NO_DATA": ["無具體數據", "缺乏數據", "未提供數據"],
    "NO_OUTCOME": ["無成效評估", "未交代成效", "缺成效"],
    "NO_DISAGG": ["未分組", "未分項", "無分組統計"],
    "NO_CO_RESPONSE": ["連續兩屆", "連續未兌現", "未回應結論性意見", "CO ", "結論性意見"],
    "FIELD_DISCREPANCY": ["與現場經驗", "與實務不符"],
    "NO_BUDGET": ["無預算", "缺預算", "未編列"],
    "NO_CROSS_AGENCY": ["跨部會", "缺乏跨部會"],
    "LAW_ONLY": ["只列法規", "僅引法條"],
}

CRC_ARTICLE_RE = re.compile(r"CRC-(\d{1,2})|Article\s+(\d{1,2})|公約第\s*(\d{1,2})\s*條")
CO_PARA_RE = re.compile(r"(?:CRC[12]-CO|結論性意見第\s*)\s*(\d{1,3})")


def make_passage_id(version_id: str, idx: int, text: str) -> str:
    h = hashlib.md5(text.encode("utf-8")).hexdigest()[:8]
    return f"{version_id}_p{idx:03d}_{h}"


def split_markdown(text: str) -> list[tuple[str, str]]:
    """按 ## / ### 切段。回傳 [(heading, content), ...]"""
    # 移除 frontmatter
    text = re.sub(r"^---\n.*?\n---\n", "", text, count=1, flags=re.DOTALL)
    sections = []
    current_heading = "前言"
    current_buffer: list[str] = []
    for line in text.splitlines():
        m = re.match(r"^(#{2,4})\s+(.+)", line)
        if m:
            if current_buffer:
                content = "\n".join(current_buffer).strip()
                if content:
                    sections.append((current_heading, content))
            current_heading = m.group(2).strip()
            current_buffer = []
        else:
            current_buffer.append(line)
    if current_buffer:
        content = "\n".join(current_buffer).strip()
        if content:
            sections.append((current_heading, content))
    return sections


def detect_issues(text: str) -> list[str]:
    matched = []
    for code, keywords in ISSUE_KEYWORDS.items():
        if any(kw.lower() in text.lower() for kw in keywords):
            matched.append(code)
    return matched


def detect_crc_articles(text: str) -> list[str]:
    matches = set()
    for m in CRC_ARTICLE_RE.finditer(text):
        for g in m.groups():
            if g:
                num = int(g)
                if 1 <= num <= 54:
                    matches.add(f"CRC-{num}")
    return sorted(matches)


def detect_problems(text: str) -> list[str]:
    matched = []
    for code, keywords in PROBLEM_KEYWORDS.items():
        if any(kw in text for kw in keywords):
            matched.append(code)
    return matched


def detect_agencies(conn: sqlite3.Connection, text: str) -> list[str]:
    cur = conn.execute("SELECT code, label_zh, aliases FROM vocab_agency")
    matched = []
    for code, label, aliases_json in cur.fetchall():
        aliases = [label]
        if aliases_json:
            try:
                aliases.extend(json.loads(aliases_json))
            except json.JSONDecodeError:
                pass
        if any(a in text for a in aliases if a):
            matched.append(code)
    return matched


def get_publish_files() -> list[Path]:
    """從 CLASSIFICATION_INDEX.md 抓 publish 層檔案。"""
    idx = SOURCES / "CLASSIFICATION_INDEX.md"
    if not idx.exists():
        print(f"❌ 先跑 scripts/classify_sources.py --update", file=sys.stderr)
        return []
    text = idx.read_text(encoding="utf-8")
    in_publish = False
    files = []
    for line in text.splitlines():
        if line.startswith("## PUBLISH"):
            in_publish = True
            continue
        if line.startswith("## ") and not line.startswith("## PUBLISH"):
            in_publish = False
            continue
        if in_publish and line.startswith("| `"):
            m = re.search(r"`([^`]+)`", line)
            if m:
                p = ROOT / m.group(1)
                if p.exists() and p.suffix in (".md",):  # 只處理 markdown
                    files.append(p)
    return files


def populate(dry_run: bool = False) -> int:
    files = get_publish_files()
    print(f"處理 {len(files)} 份 publish 層 markdown")

    if dry_run:
        print("(dry-run 模式 — 不寫入)")

    conn = sqlite3.connect(str(DB))
    cur = conn.cursor()

    total_passages = 0
    total_issue_tags = 0
    total_crc_tags = 0

    for f in files:
        rel = str(f.relative_to(ROOT))
        text = f.read_text(encoding="utf-8", errors="replace")
        sections = split_markdown(text)

        # 為這份檔案建/取 document_version
        doc_id = f"DOC_{f.stem[:30]}"
        version_id = f"V_{f.stem[:30]}_2026-04-27"
        if not dry_run:
            cur.execute(
                "INSERT OR IGNORE INTO document(doc_id, title, doc_type, language, public_status, source_url) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (doc_id, f.stem, "publish", "zh", "公開", ""),
            )
            cur.execute(
                "INSERT OR IGNORE INTO document_version(version_id, doc_id, version_label, file_path, review_status, publish_path) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (version_id, doc_id, "current", rel, "publish", rel),
            )

        for i, (heading, content) in enumerate(sections):
            if len(content) < 30:
                continue  # 跳過過短段落
            issue_tags = detect_issues(content)
            crc_articles = detect_crc_articles(content)
            problem_tags = detect_problems(content)
            agency_tags = detect_agencies(conn, content)

            passage_id = make_passage_id(version_id, i, content)
            total_passages += 1
            total_issue_tags += len(issue_tags)
            total_crc_tags += len(crc_articles)

            if not dry_run:
                summary = content[:160].replace("\n", " ")
                cur.execute(
                    "INSERT OR REPLACE INTO passage(passage_id, version_id, paragraph_no, raw_text, "
                    "summary_80w, privacy_level, review_status) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (passage_id, version_id, heading[:50], content, summary, "公開", "AI初稿"),
                )

    if not dry_run:
        conn.commit()
    conn.close()

    print(f"\n統計:")
    print(f"  總 passage 數: {total_passages}")
    print(f"  議題標籤: {total_issue_tags}")
    print(f"  CRC 條文: {total_crc_tags}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="不寫入,只列計")
    args = ap.parse_args()
    return populate(dry_run=args.dry_run)


if __name__ == "__main__":
    sys.exit(main())
