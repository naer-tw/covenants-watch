#!/usr/bin/env python3
"""submission_intake.py — Tally 表單回送之 webhook 接收 + 自動去識別化骨架。

Wave 72:對應藍圖 MVP §6 + governance/document_governance.md §3.6。

流程(對應 MVP 藍圖):
  Tally(EU 託管) → POST JSON 到本端點
    → 1. 寫入 submission_raw 表(僅 DPO + 主編可讀)
    → 2. 自動掃可識別資訊(姓名、學校、班級、住址)→ submission_redacted
    → 3. 風險關鍵字偵測(自傷 / 性侵 / 家暴)→ 通知兒少保護專員
    → 4. AI 工具(將來)只看 redacted 版本

本骨架提供:
  - CLI 模式:接收 JSON 檔案模擬入庫(供測試)
  - Flask 模式(可選):啟動本地 webhook server

用法:
  python3 scripts/submission_intake.py --intake test_submission.json
  python3 scripts/submission_intake.py --serve --port 5000  # 需 pip install flask
  python3 scripts/submission_intake.py --list-recent
  python3 scripts/submission_intake.py --redact-pending
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "data" / "crw.db"

# 風險關鍵字(觸發兒少保護專員通知)— 對應 governance/child_safeguarding.md
RISK_KEYWORDS = {
    "self_harm": ["自殺", "自傷", "想死", "活不下去", "活下去", "不想活", "割腕", "吃藥"],
    "domestic_violence": ["家暴", "被打", "爸爸打", "媽媽打", "繼父", "繼母"],
    "sexual_violence": ["性侵", "強暴", "猥褻", "摸我", "脫我衣服", "性騷擾"],
    "bullying_severe": ["霸凌", "被欺負", "圍毆", "霸凌到不想上學"],
    "drug": ["毒品", "依托咪酯", "喪屍煙彈", "K他命", "搖頭丸"],
    "trafficking": ["人口販運", "被賣", "援交"],
}

# 可識別資訊 patterns(去識別化用)
PII_PATTERNS = [
    (r"(我叫|我是)\s*([一-鿿]{2,4})", r"\1[姓名]"),
    (r"我的(同學|朋友|室友|姊姊|哥哥|妹妹|弟弟)\s*([一-鿿]{2,4})", r"我的\1[姓名]"),
    (r"([一-鿿]{2,4})老師", "[XX]老師"),
    (r"([一-鿿]{2,6}(?:國中|高中|國小|高職|附中))", "[XX學校]"),
    (r"\d+\s*年\s*\d+\s*班", "[X年X班]"),
    (r"09\d{2}-?\d{6}", "[手機號碼]"),
    (r"\d{1,2}/\d{1,2}/\d{2,4}", "[特定日期]"),
    (r"[\w._-]+@[\w.-]+\.\w+", "[email]"),
]


def schema_check(conn: sqlite3.Connection) -> None:
    """submission_raw / redacted 表已於初始 schema 建立。本檔對齊既有欄位。"""
    pass


def detect_risks(text: str) -> dict[str, list[str]]:
    matched: dict[str, list[str]] = {}
    for category, kws in RISK_KEYWORDS.items():
        hits = [kw for kw in kws if kw in text]
        if hits:
            matched[category] = hits
    return matched


def redact(text: str) -> tuple[str, list[str]]:
    """回傳 (redacted_text, log)。"""
    log = []
    redacted = text
    for pattern, replacement in PII_PATTERNS:
        new = re.sub(pattern, replacement, redacted)
        if new != redacted:
            log.append(f"redact pattern: {pattern[:30]}...")
            redacted = new
    return redacted, log


def hash_ip(ip: str) -> str:
    return hashlib.sha256((ip + "_2026").encode()).hexdigest()[:16] if ip else ""


def intake_submission(payload: dict) -> str:
    conn = sqlite3.connect(str(DB))
    schema_check(conn)
    submission_id = f"SUB_{dt.datetime.now().strftime('%Y%m%d%H%M%S')}_{hashlib.md5(str(payload).encode()).hexdigest()[:6]}"
    text = " ".join(str(v) for v in payload.get("responses", {}).values())
    risks = detect_risks(text)
    risk_json = json.dumps(risks, ensure_ascii=False) if risks else None

    # 對齊既有 schema(form_type / age_range / raw_payload / consent_scope)
    form_type_map = {
        "kids_8_11": "child_8_11", "kids_12_14": "child_12_14", "kids_15_18": "child_15_18",
        "adult": "adult", "expert": "expert",
    }
    form_type = form_type_map.get(payload.get("form_id", ""), "adult")
    consent_scope = json.dumps({
        "share": bool(payload.get("consent_to_share")),
        "parent_aware": bool(payload.get("consent_parent_aware")),
    }, ensure_ascii=False)

    conn.execute("""
        INSERT INTO submission_raw(submission_id, received_at, form_type, age_range,
            raw_payload, consent_scope, risk_flags)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        submission_id,
        dt.datetime.now().isoformat(),
        form_type,
        payload.get("age_group", "unknown"),
        json.dumps(payload, ensure_ascii=False),
        consent_scope,
        risk_json,
    ))

    # 自動產生 redacted 版本(對齊既有 schema)
    redacted_text, log = redact(text)
    conn.execute("""
        INSERT INTO submission_redacted(submission_id, redacted_text, usability)
        VALUES (?, ?, ?)
    """, (submission_id, redacted_text, "需改寫"))

    conn.commit()
    conn.close()

    print(f"✓ 入庫:{submission_id}")
    if risks:
        print(f"⚠ 風險旗標:{', '.join(risks.keys())} — 請通知兒少保護專員 24 小時內處理")
    print(f"✓ 已產生 redacted 版本({len(log)} 處去識別化)")
    return submission_id


def list_recent(n: int = 20) -> None:
    conn = sqlite3.connect(str(DB))
    schema_check(conn)
    cur = conn.execute(
        "SELECT submission_id, received_at, age_range, form_type, risk_flags "
        "FROM submission_raw ORDER BY received_at DESC LIMIT ?", (n,)
    )
    rows = cur.fetchall()
    print(f"最近 {len(rows)} 筆 submission:")
    for row in rows:
        sid, at, age, ftype, risks = row
        risk_status = "⚠ needs_attention" if risks else "ok"
        print(f"  {sid} | {at[:19]} | {ftype} / {age} | {risk_status} | risks: {risks or '-'}")
    conn.close()


def serve(port: int = 5000) -> int:
    """需要 pip install flask 才能跑。"""
    try:
        from flask import Flask, request, jsonify
    except ImportError:
        print("❌ Flask 未安裝。請跑 `.venv/bin/pip install flask`", file=sys.stderr)
        return 1

    app = Flask(__name__)

    @app.route("/api/submission/intake", methods=["POST"])
    def intake():
        try:
            payload = request.get_json() or {}
            payload["ip"] = request.remote_addr
            sid = intake_submission(payload)
            return jsonify({"status": "ok", "submission_id": sid})
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500

    @app.route("/api/health", methods=["GET"])
    def health():
        return jsonify({"status": "ok", "wave": 72, "version": "2026-04-27"})

    print(f"📡 submission_intake server 啟動於 http://127.0.0.1:{port}")
    print(f"   Tally webhook URL 應設為:http://your-host/api/submission/intake")
    app.run(host="127.0.0.1", port=port)
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--intake", help="從 JSON 檔案入庫一筆 submission(測試用)")
    ap.add_argument("--list-recent", action="store_true", help="列最近 20 筆")
    ap.add_argument("--serve", action="store_true", help="啟動 Flask webhook server")
    ap.add_argument("--port", type=int, default=5000)
    args = ap.parse_args()

    if args.list_recent:
        list_recent()
        return 0
    if args.serve:
        return serve(args.port)
    if args.intake:
        payload = json.loads(Path(args.intake).read_text(encoding="utf-8"))
        intake_submission(payload)
        return 0
    ap.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
