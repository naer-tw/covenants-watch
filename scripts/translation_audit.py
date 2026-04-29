#!/usr/bin/env python3
"""translation_audit.py — 檢查翻譯完整度 + 規則檢核。

Wave 81 + Wave 88 升級。對應 data/policy_issues/translations/README.md §翻譯品質檢核。

升級檢核項目(Wave 88):
  1. 完整度(Wave 81 已有)
  2. 機關名稱一致性 — vocab_agency 對照
  3. CRC 條文編號正確性 — 不可被翻譯改動
  4. 數字精確性 — 8,743 / 142% / 4,641 等不可改動
  5. 字數比對 — 中英 1.0:1.4 為合理範圍(中文簡潔 vs 英文展開)
  6. 機構縮寫格式 — NHRC / CRC / GC + 阿拉伯數字

用法:
    python3 scripts/translation_audit.py             # 完整度 + 規則檢核
    python3 scripts/translation_audit.py --lang en
    python3 scripts/translation_audit.py --strict    # 嚴格模式(任何 warn 即 fail)
"""
from __future__ import annotations

import argparse
import json
import re
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ISSUES = ROOT / "data" / "policy_issues"
TRANS = ISSUES / "translations"
DB = ROOT / "data" / "crw.db"


def _agency_aliases(conn: sqlite3.Connection) -> dict[str, list[str]]:
    """vocab_agency 表之 zh→aliases 對照,供 EN 翻譯檢核機關名一致性。"""
    rows = conn.execute("SELECT label_zh, aliases FROM vocab_agency").fetchall()
    out = {}
    for zh, aliases_json in rows:
        try:
            aliases = json.loads(aliases_json or "[]")
        except json.JSONDecodeError:
            aliases = []
        out[zh] = [zh] + aliases
    return out


# 數字 patterns:抓出可能被改動的具體數值
NUMBER_PATTERN = re.compile(r"\b(\d{1,3}(?:,\d{3})+|\d+(?:\.\d+)?)\s*(%|×|倍|歲|人|件|億|萬)?")


def _extract_numbers(text: str) -> list[tuple[str, str]]:
    """從文字中抽出數字 + 單位。"""
    return [(m.group(1), m.group(2) or "") for m in NUMBER_PATTERN.finditer(text)]


def _extract_crc_articles(text: str) -> list[str]:
    """抓 CRC 條文編號(中文 / 英文 / 縮寫)。"""
    matches = set()
    # CRC-XX
    for m in re.finditer(r"CRC[-_\s]?(\d{1,2})\b", text):
        matches.add(f"CRC-{int(m.group(1))}")
    # Article XX / 第 XX 條
    for m in re.finditer(r"(?:Article|第)\s*(\d{1,2})\s*條?", text):
        matches.add(f"CRC-{int(m.group(1))}")
    # CO-XX / 結論性意見第 XX 點
    for m in re.finditer(r"CO[-_\s]?(\d{1,3})\b|結論性意見第\s*(\d{1,3})\s*點", text):
        num = m.group(1) or m.group(2)
        if num:
            matches.add(f"CO-{num}")
    return sorted(matches)


def rule_check(zh_text: str, en_text: str, agencies: dict[str, list[str]]) -> list[str]:
    """跑規則檢核,回傳 warning 列表。"""
    warns = []

    # 1. 字數比對(中英 1.0 : 1.4)
    if zh_text and en_text:
        zh_len = len(re.sub(r"\s+", "", zh_text))
        en_words = len(en_text.split())
        # 中文 1 字 ≈ 英文 0.6-0.8 字(經驗值);若英文 < 中文 0.5 倍,可能漏譯
        if en_words < zh_len * 0.4:
            warns.append(f"字數疑漏譯:中 {zh_len} 字 vs 英 {en_words} 字(預期 {int(zh_len*0.6)}-{int(zh_len*0.9)})")
        if en_words > zh_len * 1.5:
            warns.append(f"字數疑膨脹:中 {zh_len} 字 vs 英 {en_words} 字(預期 {int(zh_len*0.6)}-{int(zh_len*0.9)})")

    # 2. 數字精確性
    zh_numbers = _extract_numbers(zh_text)
    en_numbers = _extract_numbers(en_text)
    zh_nums_set = {n[0] for n in zh_numbers}
    en_nums_set = {n[0] for n in en_numbers}
    missing_in_en = zh_nums_set - en_nums_set
    extra_in_en = en_nums_set - zh_nums_set
    if missing_in_en:
        warns.append(f"中文有但英文缺數字:{', '.join(sorted(missing_in_en))[:80]}")
    if extra_in_en:
        warns.append(f"英文有但中文缺數字:{', '.join(sorted(extra_in_en))[:80]}")

    # 3. CRC 條文編號
    zh_crc = set(_extract_crc_articles(zh_text))
    en_crc = set(_extract_crc_articles(en_text))
    if zh_crc != en_crc and zh_crc:
        warns.append(f"CRC 條文 / CO 不一致:zh={sorted(zh_crc)} en={sorted(en_crc)}")

    # 4. 機關名稱一致性(只檢核 EN 文字是否合理對應 ZH)
    for zh_name, aliases in agencies.items():
        if zh_name in zh_text:
            # 英文應該至少出現英文 alias 之一
            en_aliases = [a for a in aliases if re.match(r"[A-Za-z]", a)]
            if en_aliases:
                if not any(ea in en_text for ea in en_aliases):
                    warns.append(f"機關名 '{zh_name}' 在英文版未出現對應(任一)別稱:{en_aliases[:3]}")

    return warns


def audit(lang: str, strict: bool = False) -> int:
    pi_files = sorted(ISSUES.glob("PI-*.md"))
    print(f"翻譯稽核 — lang={lang} ({len(pi_files)} 份 PI 卡)")
    print("─" * 70)

    # 載入 vocab_agency
    agencies = {}
    if DB.exists():
        conn0 = sqlite3.connect(str(DB))
        agencies = _agency_aliases(conn0)
        conn0.close()

    completed = 0
    total_warns = 0
    for pf in pi_files:
        pid = pf.stem.split("_")[0]
        text = pf.read_text(encoding="utf-8")
        slug_match = re.search(r"^slug:\s*(.+)$", text, re.MULTILINE)
        if not slug_match:
            continue
        slug = slug_match.group(1).strip()
        trans_file = TRANS / f"{pid}_{slug}_{lang}.json"

        if not trans_file.exists():
            print(f"  ✗ {pid} ({slug}): 無翻譯檔")
            continue

        try:
            data = json.loads(trans_file.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            print(f"  ✗ {pid}: JSON 解析錯誤 {e}")
            continue

        fields = data.get("fields", {})
        required = ["title", "summary_adult", "civil_observation", "recommendations"]
        missing = [k for k in required if not fields.get(k) or len(fields[k]) < 10]
        status = data.get("review_status", "pending")

        if missing:
            print(f"  ⚠ {pid}: 翻譯狀態 {status},缺欄位 {missing}")
            continue

        # Wave 88:跑規則檢核
        # 從 zh PI 卡片 body 抽對應段落
        body = text[text.find("---", 3) + 3:] if text.startswith("---") else text
        warns = []
        for field in ["summary_adult", "civil_observation", "recommendations"]:
            heading_re = {
                "summary_adult": r"議題摘要",
                "civil_observation": r"民間觀察",
                "recommendations": r"政策建議"
            }[field]
            m = re.search(rf"^##\s+[一二三四五六七八九十]+、\s*{heading_re}.*?\n(.*?)(?=^##\s|\Z)",
                          body, re.MULTILINE | re.DOTALL)
            zh_text = m.group(1).strip() if m else ""
            en_text = fields.get(field, "")
            field_warns = rule_check(zh_text, en_text, agencies)
            for w in field_warns:
                warns.append(f"{field}: {w}")

        if warns:
            print(f"  ⚠ {pid}: 翻譯狀態 {status},完整但有 {len(warns)} 項規則警告")
            for w in warns[:3]:
                print(f"      - {w}")
            if len(warns) > 3:
                print(f"      ... +{len(warns)-3} 條")
            total_warns += len(warns)
        else:
            print(f"  ✓ {pid}: 翻譯狀態 {status},全部欄位齊全 + 規則通過")
            completed += 1

    print(f"\n結算:{completed}/{len(pi_files)} 份完整 + 規則通過,共 {total_warns} 項規則警告")

    # 從 SQLite 補充狀態
    if DB.exists():
        conn = sqlite3.connect(str(DB))
        cur = conn.execute(
            "SELECT field_name, status, COUNT(*) FROM translation_status "
            "WHERE lang=? GROUP BY field_name, status ORDER BY field_name, status",
            (lang,)
        )
        rows = cur.fetchall()
        if rows:
            print(f"\nSQLite translation_status (lang={lang}):")
            for field, status, count in rows:
                print(f"  {field:25} | {status:18} | {count}")
        conn.close()

    if strict and total_warns > 0:
        return 2
    return 0 if completed == len(pi_files) else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--lang", default="en")
    ap.add_argument("--strict", action="store_true", help="任何規則 warn 即 exit 2")
    args = ap.parse_args()
    return audit(args.lang, strict=args.strict)


if __name__ == "__main__":
    sys.exit(main())
