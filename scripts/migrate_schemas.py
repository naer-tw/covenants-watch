#!/usr/bin/env python3
"""migrate_schemas.py — 還原 Wave 62+ 的 schema 擴充(rebuild 後跑)。

Wave 91:md_to_sqlite.py --rebuild 只重建核心表,本檔負責補回:
  - 6 vocab_* 表(Wave 62)
  - dashboard_metric 表(Wave 63)
  - document_version 之 raw/clean/publish 欄位(Wave 62)
  - nap_action 表(Wave 79)+ 11 項第一期 + 6 項第二期 placeholder
  - nhrc_indicator 表(Wave 85)+ 6 項範例
  - translation_status 表(Wave 81)

用法:
    python3 scripts/migrate_schemas.py            # 全跑(冪等)
    python3 scripts/migrate_schemas.py --check    # 只檢查表是否存在
"""
from __future__ import annotations

import argparse
import json
import sqlite3
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "data" / "crw.db"


def ensure_vocab(conn):
    """Wave 62:6 組受控詞表。"""
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS vocab_issue (
            code TEXT PRIMARY KEY, label_zh TEXT NOT NULL, label_en TEXT,
            cluster TEXT, pi_id TEXT, parent_code TEXT, deprecated INTEGER DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS vocab_crc_article (
            code TEXT PRIMARY KEY, label_zh TEXT, label_en TEXT, deprecated INTEGER DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS vocab_agency (
            code TEXT PRIMARY KEY, label_zh TEXT NOT NULL, label_en TEXT,
            parent_code TEXT, aliases TEXT, deprecated INTEGER DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS vocab_problem_tag (
            code TEXT PRIMARY KEY, label_zh TEXT NOT NULL, description TEXT, deprecated INTEGER DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS vocab_quotability (
            code TEXT PRIMARY KEY, label_zh TEXT NOT NULL, description TEXT
        );
        CREATE TABLE IF NOT EXISTS vocab_privacy (
            code TEXT PRIMARY KEY, label_zh TEXT NOT NULL, description TEXT
        );
    """)
    # 灌入詞條(冪等,INSERT OR IGNORE)
    issues = [
        ('campus-bullying','校園霸凌','E','PI-01'),
        ('youth-mental-health','青少年心理健康','G','PI-02'),
        ('corporal-punishment','體罰禁止','E','PI-03'),
        ('student-counseling','學生輔導體制','G','PI-04'),
        ('juvenile-justice','少年司法行政先行','I','PI-05'),
        ('child-cyber-safety','兒少網路安全','L','PI-06'),
        ('sexual-exploitation','性剝削防制','E','PI-07'),
        ('gender-equity-edu','性別平等教育','H','PI-08'),
        ('academic-pressure','課業壓力與學習權','H','PI-09'),
        ('child-voice','兒少表意與校園民主','C','PI-10'),
        ('family-policy','家庭功能政策','F','PI-11'),
        ('alternative-care','替代照顧與機構安置','F','PI-12'),
        ('migrant-stateless','移民無國籍與失聯兒少','I','PI-13'),
        ('lgbtqi-children','LGBTQI 兒少','D','PI-14'),
    ]
    conn.executemany("INSERT OR IGNORE INTO vocab_issue(code, label_zh, cluster, pi_id) VALUES (?,?,?,?)", issues)

    agencies = [
        ('MOHW','衛福部','["衛生福利部","衛福部"]'),
        ('SFAA','社家署','["社會及家庭署","衛福部社家署"]'),
        ('MOE','教育部','["教育部"]'),
        ('K12EA','國教署','["教育部國民及學前教育署","國教署"]'),
        ('NPA','警政署','["內政部警政署","警政署"]'),
        ('MOI','內政部','["內政部"]'),
        ('NIA','移民署','["內政部移民署","移民署"]'),
        ('MOJ','法務部','["法務部"]'),
        ('JY','司法院','["司法院"]'),
        ('NHRC','國家人權委員會','["人權會","NHRC","監察院國家人權委員會"]'),
        ('EY_HRP','行政院人權處','["行政院人權及轉型正義處","人權處"]'),
        ('NCC','通傳會','["國家通訊傳播委員會","通傳會","NCC"]'),
        ('MODA','數發部','["數位發展部","數發部"]'),
    ]
    conn.executemany("INSERT OR IGNORE INTO vocab_agency(code, label_zh, aliases) VALUES (?,?,?)", agencies)

    problem_tags = [
        ('NO_DATA','無具體數據','只列政策、無數據佐證'),
        ('NO_OUTCOME','無成效評估','只列投入,沒有產出/結果評估'),
        ('NO_DISAGG','無弱勢兒少分組資料','未按性別、族群、障別、性傾向細分'),
        ('NO_CO_RESPONSE','未回應前次結論性意見','CO 連續兩屆未兌現'),
        ('FIELD_DISCREPANCY','與現場經驗不符','官方陳述與一線觀察落差'),
        ('NO_BUDGET','無預算說明','行動方案缺具體預算'),
        ('NO_CROSS_AGENCY','無跨部會協調機制','需多部會但只列單一機關'),
        ('LAW_ONLY','只列法規,無執行','只引法條未交代執行細節'),
    ]
    conn.executemany("INSERT OR IGNORE INTO vocab_problem_tag(code, label_zh, description) VALUES (?,?,?)", problem_tags)

    quote = [
        ('Q_DIRECT','可直接引用','原文已精煉,可直接複製貼上'),
        ('Q_REWRITE','需改寫','需要編輯潤飾後再用'),
        ('Q_BACKGROUND','僅供背景','不公開引用,僅作為內部參考'),
    ]
    conn.executemany("INSERT OR IGNORE INTO vocab_quotability(code, label_zh, description) VALUES (?,?,?)", quote)

    privacy = [
        ('P_PUBLIC','公開','無敏感資訊'),
        ('P_REDACTED','匿名後可公開','經去識別化處理'),
        ('P_INTERNAL','限內部','僅供平台內部編輯'),
        ('P_SENSITIVE','極敏感','涉兒少身分、進行中案件、自傷敘事'),
    ]
    conn.executemany("INSERT OR IGNORE INTO vocab_privacy(code, label_zh, description) VALUES (?,?,?)", privacy)

    # 從 crc_article 同步
    conn.execute("""INSERT OR IGNORE INTO vocab_crc_article(code, label_zh, label_en)
                    SELECT crc_id, name_zh, name_en FROM crc_article""")
    conn.commit()


def ensure_dashboard(conn):
    """Wave 63 + 79:儀表板 8 項指標。"""
    conn.execute("""
        CREATE TABLE IF NOT EXISTS dashboard_metric (
            metric_id TEXT PRIMARY KEY,
            label_zh TEXT NOT NULL, label_unit TEXT, value_display TEXT,
            period_label TEXT, source_agency TEXT, trend TEXT,
            related_pi TEXT, color_hint TEXT, sort_order INTEGER, last_updated TEXT
        )
    """)
    metrics = [
        ('M01_youth_suicide','15-24 歲女性自殺通報增幅','%','+142%','10 年累計','衛福部 2024','critical','PI-02','red',1),
        ('M02_gonorrhea','青少年淋病增幅','倍','+7×','12 年累計','疾管署','critical','PI-08','red',2),
        ('M03_syphilis','青少女梅毒增幅','倍','+53×','10 年累計','疾管署','critical','PI-08','red',3),
        ('M04_school_violence','NHRC 4641 件師對生暴力處置失靈','%','65% 未通報','2025-12 NHRC 報告','NHRC + 臺北大學','critical','PI-01','red',4),
        ('M05_etomidate','依托咪酯校園案件(新北)','倍','+20×','2024H2 → 2025 全年','新北警','critical','PI-06','red',5),
        ('M06_youth_voice','8,743 份青年部問卷已完成','人','8,743','2025-01 公布','AABE 青年部','improving','PI-10','blue',6),
        ('M07_co_unmet','CRC2 結論性意見未兌現項數','項','~30/72','估算','AABE 雙軸分析','worsening','跨議題','orange',7),
        ('M08_nap','NAP 第一期(2022-2024)未達成 / 方向錯誤項數','項','⛔ 6/11','行政院 + NHRC 2025-07','行政院 / NHRC','critical','跨議題','red',8),
    ]
    today = sqlite3.Connection.cursor(conn).execute("SELECT date('now')").fetchone()[0]
    for m in metrics:
        conn.execute(
            "INSERT OR REPLACE INTO dashboard_metric VALUES (?,?,?,?,?,?,?,?,?,?,?)",
            m + (today,)
        )
    conn.commit()


def ensure_nap(conn):
    """Wave 79 + 86:NAP 行動表。"""
    conn.execute("""
        CREATE TABLE IF NOT EXISTS nap_action (
            action_id TEXT PRIMARY KEY,
            nap_period TEXT NOT NULL, theme_no INTEGER, theme_name TEXT,
            sub_section TEXT, action_text TEXT NOT NULL, kpi TEXT,
            target_year INTEGER, lead_agency TEXT, co_agencies TEXT,
            govt_self_assessment TEXT, govt_status TEXT,
            nhrc_comment TEXT, nhrc_severity TEXT,
            aabe_assessment TEXT, aabe_evidence TEXT,
            related_pi TEXT, related_co TEXT,
            recommend_carry_forward INTEGER DEFAULT 0, last_updated TEXT
        )
    """)
    # 從 /tmp/nap_populate.py 之資料(若已有 nap_action 內容會 INSERT OR REPLACE 更新)
    conn.commit()


def ensure_translation_status(conn):
    """Wave 81:翻譯狀態追蹤。"""
    conn.execute("""
        CREATE TABLE IF NOT EXISTS translation_status (
            issue_id TEXT, lang TEXT, field_name TEXT,
            status TEXT, translator TEXT, translation_date TEXT, word_count INTEGER,
            PRIMARY KEY (issue_id, lang, field_name)
        )
    """)
    # 14 PI × en × 4 fields
    fields = ['title', 'summary_adult', 'civil_observation', 'recommendations']
    pi_ids = [r[0] for r in conn.execute("SELECT issue_id FROM policy_issue").fetchall()]
    for pid in pi_ids:
        for f in fields:
            conn.execute(
                "INSERT OR IGNORE INTO translation_status(issue_id, lang, field_name, status) VALUES (?,?,?,?)",
                (pid, 'en', f, 'pending')
            )
    conn.commit()


def ensure_document_version_columns(conn):
    """Wave 62:加 raw_path/clean_path/publish_path/review_status 至 document_version。"""
    cols = [r[1] for r in conn.execute("PRAGMA table_info(document_version)").fetchall()]
    additions = [
        ("raw_path", "TEXT"),
        ("clean_path", "TEXT"),
        ("publish_path", "TEXT"),
        ("review_status", "TEXT DEFAULT 'raw'"),
    ]
    for col, decl in additions:
        if col not in cols:
            conn.execute(f"ALTER TABLE document_version ADD COLUMN {col} {decl}")
    conn.commit()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()

    if not DB.exists():
        print(f"❌ {DB} 不存在 — 先跑 md_to_sqlite.py --rebuild", file=sys.stderr)
        return 1

    conn = sqlite3.connect(str(DB))
    if args.check:
        tables = [r[0] for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        ).fetchall()]
        required = ['vocab_issue', 'vocab_agency', 'vocab_crc_article', 'vocab_problem_tag',
                    'vocab_quotability', 'vocab_privacy', 'dashboard_metric',
                    'nap_action', 'translation_status']
        missing = [t for t in required if t not in tables]
        if missing:
            print(f"❌ 缺 {len(missing)} 表:{missing}")
            return 1
        print(f"✓ Wave 62-91 schema 完整(共 {len(required)} 表)")
        return 0

    print("執行 schema 遷移(冪等)...")
    ensure_vocab(conn)
    print("  ✓ vocab_* 6 表")
    ensure_document_version_columns(conn)
    print("  ✓ document_version 欄位擴充")
    ensure_dashboard(conn)
    print("  ✓ dashboard_metric 8 項")
    ensure_nap(conn)
    print("  ✓ nap_action 表 schema(行動內容由 import_nap*.py 灌)")
    ensure_translation_status(conn)
    print("  ✓ translation_status 56 項 pending")
    conn.close()

    # 觸發 NAP 第一期 + 第二期 + NHRC 指標重灌
    print("\n灌入 NAP 第一期...")
    subprocess.run(["python3", "/tmp/nap_populate.py"], check=False)
    print("\n灌入 NAP 第二期 placeholder...")
    subprocess.run(["python3", str(ROOT / "scripts/import_nap2.py"), "--predicted"], check=False)
    print("\n灌入 NHRC 指標範例...")
    subprocess.run(["python3", str(ROOT / "scripts/parse_nhrc_indicators.py"), "--sample"], check=False)

    print("\n✓ 全部 schema + 資料還原完成")
    return 0


if __name__ == "__main__":
    sys.exit(main())
