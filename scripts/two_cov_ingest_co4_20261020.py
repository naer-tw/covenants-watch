#!/usr/bin/env python3
"""
一次性匯入:2026-05-15 通過之「第四次國際審查結論性意見與建議」(135 點) 入 concluding_observation。
(W2-3 更新員 2026-10-20 新增;取代審查前寫入的「(預備)」CO-4-1~10 預測稿,後者不刪、只加註。)

來源(法務部人權大步走):
  EN  https://www.humanrights.moj.gov.tw/media/20215621/2026-concluding-observations-and-recommendations_icescr-iccpr-independent-review-for-taiwan.pdf
  ZH  https://www.humanrights.moj.gov.tw/media/20215631/2026兩公約第四次國際審查結論性意見與建議-中譯定稿版-1150916奉核.pdf
  兩份 PDF 存 data/sources/raw/co/co_review_4_2026_{en,zh}.pdf

id 規則:沿用 two_cov_fetch_co.import_to_sqlite 的 `CO-{review}-{段號}-{標記}` 形式,標記=FINAL,
  故 CO-4-7-FINAL 與預測稿 CO-4-7 不衝突。

用法: python3 scripts/two_cov_ingest_co4_20261020.py [--dry-run]
前提: pdftotext(poppler)。先斷言中英兩份皆抽出 135 段才寫入。
"""
from __future__ import annotations
import json, re, sqlite3, subprocess, sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "data" / "two_cov.db"
RAW = ROOT / "data" / "sources" / "raw" / "co"
GOV_URL = "https://www.humanrights.moj.gov.tw/17725/17733/41766/41770/46434/46447/46452/post"
SUPERSEDE_NOTE = "【審查前預測稿・已由 2026-05-15 通過之正式結論性意見取代(見 CO-4-N-FINAL)・勿引用為 CO 原文】"


def pdf_text(p: Path) -> str:
    return subprocess.run(["pdftotext", "-layout", str(p), "-"], capture_output=True, text=True, check=True).stdout


def split_paragraphs(text: str, zh: bool):
    """回傳 {段號: (標題, 內文)};標題=該段前最近的小標。"""
    lines = [l.rstrip() for l in text.splitlines()]
    out, heading, cur, exp = {}, "", None, 1
    pend_heading = []
    para_re = re.compile(r"^\s*(\d{1,3})\.\s*(\S.*)$")
    for i, l in enumerate(lines):
        s = l.strip()
        if not s or re.fullmatch(r"\d{1,3}", s):
            continue  # 空行/頁碼
        m = para_re.match(l)
        if m and int(m.group(1)) == exp:
            cur = exp
            out[cur] = [heading, m.group(2).strip()]
            exp += 1
            continue
        if cur is None:
            continue
        # 小標:縮排淺、較短、且前一行為空行、不以小寫/a. 開頭
        prev_blank = i > 0 and not lines[i - 1].strip()
        indent = len(l) - len(l.lstrip())
        is_head = (prev_blank and indent <= 2 and len(s) <= (40 if zh else 90)
                   and not re.match(r"^[a-z]\.\s", s) and not s.endswith(("。", ".", ";", ";", ",", ",", "；", "，"))
                   and not s[0].islower())
        if is_head:
            heading = s
            continue
        out[cur][1] += ("" if zh else " ") + s
    return {k: (v[0], v[1]) for k, v in out.items()}


# 子標題本身不帶條號時,依其所屬大標補條號(人工對照 CO 目錄;未列者留空)
ARTS_OVERRIDE = {
    "Comprehensive Anti-Discrimination Legislation": ["ICCPR-2", "ICESCR-2"],
    "Persons with Disabilities": ["ICCPR-2", "ICESCR-2"],
    "Sex Workers": ["ICESCR-6"], "Asylum Seekers": ["ICESCR-6"],
    "Minimum Wage": ["ICESCR-7"], "Domestic Workers": ["ICESCR-7"], "Distant Water Fishers\u2019 Rights": ["ICESCR-7"],
    "Maternity, Paternity and Parental Leave": ["ICESCR-10"],
    "Forced Evictions and Displacement": ["ICESCR-11"], "The Role of the National Human Rights Commission": ["ICESCR-11"],
    "The Human Rights of the Homeless": ["ICESCR-11"],
    "Land Expropriation, Land Consolidation and Development Projects": ["ICESCR-11"],
    "Urban Indigenous Communities": ["ICESCR-11"], "Housing Rights of People with Disabilities": ["ICESCR-11"],
    "Sexual and Reproductive Health": ["ICESCR-12"], "Access to Assisted Reproduction": ["ICESCR-12"],
    "Institutionalisation, Health and Community Life": ["ICESCR-12"],
    "Education of Children and Young People with Disabilities": ["ICESCR-13"], "Sexuality Education": ["ICESCR-13"],
    "Facial Recognition Technology": ["ICCPR-17"], "Data Protection": ["ICCPR-17"],
    "Same-sex Marriage": ["ICCPR-23"], "Children of Same-sex Marriages": ["ICCPR-23"],
}
ZH_HEAD_OVERRIDE = {
    "Gender Equality and Gender-Based Violence (Common Article 3 ICESCR & ICCPR)": "性別平等與性別暴力(兩公約共同第 3 條)",
    "Principle of Non-Refoulement and the Refugee Act (Articles 6, 7 and 13)": "不強制遣返原則與難民法(第 6、7、13 條)",
    "Freedom of Expression (Articles 19 and 20)": "言論自由(第 19 條及第 20 條)",
    "Human Rights, Environment and Climate Change": "人權、環境與氣候變遷",
}


def article_list(en_heading: str, covenant: str) -> list[str]:
    """由英文小標「(Article 6)」「(Articles 6 and 7)」「(Common Article 3 ...)」抽條號;子標題走 ARTS_OVERRIDE。"""
    if en_heading in ARTS_OVERRIDE:
        return ARTS_OVERRIDE[en_heading]
    nums = []
    for m in re.finditer(r"\((?:Common )?Articles? ([0-9, and]+)\)?", en_heading):
        nums += re.findall(r"\d+", m.group(1))
    if not nums:
        return []
    if "Common" in en_heading:
        return [f"{c}-{n}" for n in nums for c in ("ICCPR", "ICESCR")]
    return [f"{covenant}-{n}" for n in nums]


def main():
    dry = "--dry-run" in sys.argv
    en = split_paragraphs(pdf_text(RAW / "co_review_4_2026_en.pdf"), zh=False)
    zh = split_paragraphs(pdf_text(RAW / "co_review_4_2026_zh.pdf"), zh=True)
    assert len(en) == 135, f"EN 段數 {len(en)} != 135"
    assert len(zh) == 135, f"ZH 段數 {len(zh)} != 135"
    # 中文小標以「英文小標 -> 中文小標最多數」對映,避開換行/跨頁造成的誤判
    from collections import Counter, defaultdict
    votes = defaultdict(Counter)
    for n in range(1, 136):
        votes[en[n][0]][zh[n][0]] += 1
    zh_head = {k: c.most_common(1)[0][0] for k, c in votes.items()}
    now = datetime.now().isoformat(timespec="seconds")
    rows = []
    for n in range(1, 136):
        if n <= 10:
            eh, zh_h, cov = "Introduction", "緒論", "BOTH"
        else:
            eh = en[n][0]
            zh_h = ZH_HEAD_OVERRIDE.get(eh, zh_head[eh])
            cov = "BOTH" if n <= 51 else ("ICESCR" if n <= 95 else "ICCPR")  # B 一般議題 11-51 / C ICESCR 52-95 / D ICCPR 96-135
        arts = article_list(eh, cov if cov != "BOTH" else "")
        body = zh[n][1] + "\n\n[EN] " + en[n][1]
        rows.append((f"CO-4-{n}-FINAL", 4, 2026, n, zh_h, cov, json.dumps(arts, ensure_ascii=False),
                     zh_h, body, "not_started", GOV_URL, now, now))
    if dry:
        for r in rows:
            print(r[0], r[5], r[4], r[6])
        return 0
    conn = sqlite3.connect(DB)
    before = conn.execute("select count(*) from concluding_observation").fetchone()[0]
    conn.executemany(
        """INSERT OR IGNORE INTO concluding_observation
           (co_id, review, review_year, paragraph_number, topic, covenant, article_referenced,
            chinese_title, recommendation_full, follow_up_status, gov_response_url, created_at, updated_at)
           VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""", rows)
    # 預測稿(CO-4-1..10,無 -FINAL 後綴)加註,不刪列
    for n in range(1, 11):
        conn.execute("UPDATE concluding_observation SET chinese_title = ? || chinese_title, updated_at=? "
                     "WHERE co_id=? AND chinese_title NOT LIKE '【審查前預測稿%'", (SUPERSEDE_NOTE, now, f"CO-4-{n}"))
    conn.execute("INSERT INTO fts_co(fts_co) VALUES('rebuild')")
    conn.commit()
    after = conn.execute("select count(*) from concluding_observation").fetchone()[0]
    print(f"concluding_observation: {before} -> {after} (+{after-before})")
    conn.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
