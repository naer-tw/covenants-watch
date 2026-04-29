#!/usr/bin/env python3
"""
monitor_updates.py — 輪詢政府/監督機構網頁,偵測新公告。

設計原則:
- 純 Python stdlib + urllib(無外部依賴,不需 venv)
- 比對前次快取,有變動才印出
- 適合 cron / launchd / Claude Code /schedule 觸發
- 不修改任何資料,只通知

監測對象:
  1. NHRC 監督報告頁面 — 是否有新一輪 NAP 監督報告
  2. CRC 國家報告資料夾 — 是否有第三次審查新文件
  3. 衛福部心理健康司自殺統計 — 是否有月度更新
  4. 國教盟政策知識庫 — 是否有新分析文章
  5. 立法院 IVOD — 教文/社福衛環委員會公聽會新影片(Wave 37)
  6. 司法院統計訊息公告 — 少年法庭統計年報(Wave 37)
  7. 內政部移民署統計專區 — 失聯移工子女、無國籍兒少(Wave 37)
  8. 教育部學生輔導資訊網 — 學生輔導工作年報、霸凌處置統計(Wave 37)

用法:
  python3 scripts/monitor_updates.py                # 跑所有監測
  python3 scripts/monitor_updates.py --target nhrc  # 只跑單一目標
  python3 scripts/monitor_updates.py --reset-cache  # 清除快取(下次抓的全當作新)

排程方式:
  Claude Code /schedule weekly /scripts/monitor_updates.py
  或 macOS launchd:     ~/Library/LaunchAgents/crw.monitor.plist
  或 cron:              0 9 * * MON cd /path && python3 scripts/monitor_updates.py
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import sys
import urllib.error
from pathlib import Path

# Wave 36:共用 HTTP 模組
from _http import SSL_DOWNGRADE_ALLOWED, fetch as _fetch_http  # noqa: F401

ROOT = Path(__file__).resolve().parent.parent
CACHE_DIR = ROOT / ".monitor_cache"
LOG_FILE = ROOT / ".monitor_cache" / "log.jsonl"

# QA #7 修法:debug 模式
MONITOR_DEBUG = os.environ.get("MONITOR_DEBUG", "").lower() in ("1", "true", "yes")

TARGETS = {
    "nhrc": {
        "name": "NHRC 監督 NAP 執行情形成果報告",
        "url": "https://nhrc.cy.gov.tw/News_Content.aspx?n=7459&s=7483",
        "next_milestone": "下一輪 NAP 2025-2027 監督報告(預估 2027 中)",
        "related_pi": ["跨議題"],
    },
    "crc_3rd": {
        "name": "CRC 第三次國家報告國內審查總入口",
        "url": "https://crc.sfaa.gov.tw/Document?folderid=503",
        "next_milestone": "第二輪民間審查會議紀錄、第三次定稿",
        "related_pi": ["跨議題"],
    },
    "crc_2nd_round2": {
        "name": "CRC 第三次第 2 輪民間審查會議資訊",
        "url": "https://crc.sfaa.gov.tw/Document/Detail?documentId=4C7C8EF2-4ECB-4678-84D7-1529C1CDE9E4",
        "next_milestone": "會議紀錄公告",
        "related_pi": ["跨議題"],
    },
    "moh_suicide": {
        "name": "衛福部心理健康司 — 自殺死亡及通報統計",
        "url": "https://dep.mohw.gov.tw/domhaoh/cp-4904-8883-107.html",
        "next_milestone": "月度自殺通報、年度自殺死亡統計、衛福部臺大研究公開",
        "related_pi": ["PI-02"],
    },
    "naer_policy": {
        "name": "國教盟政策知識庫",
        "url": "https://naer-tw.github.io/policy/",
        "next_milestone": "下一篇政策分析",
        "related_pi": ["跨議題"],
    },
    # Wave 37 — 4 個新監測目標(獨立 QA #8)
    "ly_ivod_edu": {
        "name": "立法院 IVOD(委員會公聽會與審議影片)",
        "url": "https://ivod.ly.gov.tw/Demand",
        "next_milestone": "教育及文化、社福衛環委員會新公聽會 IVOD 上架(用於 transcribe_audio 後續歸位)",
        "related_pi": ["跨議題", "PI-05", "PI-08", "PI-12"],
    },
    "judicial_stats": {
        "name": "司法院統計訊息公告(含少年法庭統計年報)",
        "url": "https://www.judicial.gov.tw/tw/lp-1488-1.html",
        "next_milestone": "下一年度少年事件審理終結統計、少年觸法案件數釋出",
        "related_pi": ["PI-05"],
    },
    "moi_immigration_stats": {
        "name": "內政部移民署統計資料專區",
        "url": "https://www.immigration.gov.tw/5385/7344/7350/8883/",
        "next_milestone": "失聯移工子女通報、無國籍兒少現況更新",
        "related_pi": ["PI-13"],
    },
    "moe_guide": {
        "name": "教育部學生輔導資訊網(含國教署輔導工作年報)",
        "url": "https://www.guide.edu.tw/",
        "next_milestone": "下一年度學生輔導工作年報(WISER-3.0 成效)、霸凌處置統計",
        "related_pi": ["PI-01", "PI-04"],
    },
    # Wave 60 — NHRC 兒童權利監測指標集(2026-02-04 發布,239 項)
    "nhrc_239_indicators": {
        "name": "NHRC 兒童權利監測指標集(239 項,對接平台關鍵基礎建設)",
        "url": "https://nhrc.cy.gov.tw/",
        "next_milestone": "239 項指標數值更新、四大支柱(SDGs / 受教育權 / 公共參與 / 兒童司法)季度刷新",
        "related_pi": ["跨議題"],
    },
}


def fetch(url: str, timeout: int = 30, allow_insecure: set | None = None) -> tuple[bytes, bool]:
    """Wave 36:委派至 _http.fetch(保留本檔簽名供既有呼叫端使用)。"""
    return _fetch_http(url, timeout=timeout, encode_path=False, allow_insecure=allow_insecure)


def _strip_dynamic_elements(text: str) -> str:
    """剝去動態元素(ASP.NET ViewState、CSRF token、計數器、時間戳),
    只保留「會被人類察覺到變動」的內容部分,降低噪音。"""
    # 剝去動態 input(__VIEWSTATE、__EVENTVALIDATION、__VIEWSTATEGENERATOR、CSRF token)
    text = re.sub(r'<input[^>]*name="__VIEWSTATE[^"]*"[^>]*>', "", text)
    text = re.sub(r'<input[^>]*name="__EVENTVALIDATION"[^>]*>', "", text)
    text = re.sub(r'<input[^>]*name="__VIEWSTATEGENERATOR"[^>]*>', "", text)
    text = re.sub(r'<input[^>]*name="[Cc]srf[^"]*"[^>]*>', "", text)
    # Wave 37 補:ASP.NET MVC __RequestVerificationToken(移民署等)
    text = re.sub(r'<input[^>]*name="__RequestVerificationToken"[^>]*>', "", text)
    text = re.sub(r'<meta[^>]*name="csrf-token"[^>]*>', "", text)
    # Wave 37 補:司法院 <meta name="buildtime" content="..."> 每次抓回不同
    text = re.sub(r'<meta[^>]*name="buildtime"[^>]*>', "", text)
    # QA #7 修法:剝 <script>/<style> 但例外保留 JSON-LD(可能含 dateModified 等真實內容)
    text = re.sub(
        r'<script(?![^>]*type="application/ld\+json")[^>]*>.*?</script>',
        "",
        text,
        flags=re.DOTALL,
    )
    text = re.sub(r'<style[^>]*>.*?</style>', "", text, flags=re.DOTALL)
    # Wave 37 補:剝去網站瀏覽計數器(立法院 IVOD <span class="counter">數字</span>)
    text = re.sub(r'<span[^>]*class="[^"]*counter[^"]*"[^>]*>[\d,]+</span>', "", text)
    # Wave 37 補:剝去「資料點閱次數:N」「網站瀏覽人次:N」等政府站常見統計
    # (注意:政府網站常用全形冒號 ：。可能含 <em> 包裝。)
    text = re.sub(
        r'(資料點閱次數|頁面點閱次數|網站瀏覽人次|瀏覽人次|累計瀏覽次數)[:：]\s*(?:<em[^>]*>\s*)?[\d,]+(?:\s*</em>)?',
        r'\1',
        text,
    )
    # 剝去常見時間戳(?_=1234567890、v=20260425、?_=v3.20260425 等)
    text = re.sub(r'\?_=[\w.]+', "", text)  # QA #7 修法:支援 v3.20260425 混合格式
    text = re.sub(r'(?:v|t|cache)=\d{8,}', "", text)
    # 折疊空白
    text = re.sub(r'\s+', " ", text).strip()
    return text


def stable_fingerprint(content: bytes, target_id: str | None = None) -> str:
    """Issue #7 修法:剝去動態元素後 hash。
    QA #7 修法:MONITOR_DEBUG=1 時把 stripped text 落地供人工檢視。"""
    try:
        text = content.decode("utf-8", errors="ignore")
    except Exception:
        return hashlib.sha256(content).hexdigest()[:16]

    stripped = _strip_dynamic_elements(text)

    if MONITOR_DEBUG and target_id:
        debug_path = CACHE_DIR / f"{target_id}_stripped.html"
        debug_path.parent.mkdir(parents=True, exist_ok=True)
        debug_path.write_text(stripped, encoding="utf-8")

    return hashlib.sha256(stripped.encode("utf-8")).hexdigest()[:16]


def fingerprint(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()[:16]


def cache_path(target_id: str) -> Path:
    return CACHE_DIR / f"{target_id}.json"


def log_event(event: dict) -> None:
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")


def check_target(target_id: str, conf: dict) -> tuple[str, str, int]:
    """回 (status, message, stripped_size)。status ∈ {NEW, CHANGED, UNCHANGED, ERROR}"""
    cp = cache_path(target_id)
    try:
        content, ssl_downgraded = fetch(conf["url"])
    except (urllib.error.URLError, TimeoutError) as e:
        return "ERROR", f"❌ {conf['name']}: 抓取失敗 ({e})", 0

    # Issue #7 修法:用 stable_fingerprint 剝去動態元素,而非整頁 SHA256
    fp = stable_fingerprint(content, target_id=target_id)
    size = len(content)
    # QA #7 修法:計算 stripped 後大小,供 debug
    try:
        stripped_size = len(_strip_dynamic_elements(content.decode("utf-8", errors="ignore")))
    except Exception:
        stripped_size = 0
    ssl_note = " ⚠ SSL 降級驗證" if ssl_downgraded else ""

    if not cp.exists():
        cp.parent.mkdir(parents=True, exist_ok=True)
        cp.write_text(json.dumps({
            "url": conf["url"],
            "fingerprint": fp,
            "size": size,
            "stripped_size": stripped_size,
            "first_seen": dt.datetime.now().isoformat(),
        }, ensure_ascii=False, indent=2), encoding="utf-8")
        return "NEW", f"📋 首次抓取 {conf['name']}(指紋 {fp},{size:,} bytes){ssl_note}", stripped_size

    cached = json.loads(cp.read_text(encoding="utf-8"))
    if cached["fingerprint"] == fp:
        return "UNCHANGED", f"✓ {conf['name']}(無變動,指紋 {fp}){ssl_note}", stripped_size

    # 有變動
    cached_fp = cached["fingerprint"]
    cached_size = cached.get("size", 0)
    delta = size - cached_size

    cached_stripped = cached.get("stripped_size", 0)
    cp.write_text(json.dumps({
        "url": conf["url"],
        "fingerprint": fp,
        "size": size,
        "stripped_size": stripped_size,
        "previous_fingerprint": cached_fp,
        "previous_size": cached_size,
        "previous_stripped_size": cached_stripped,
        "first_seen": cached.get("first_seen"),
        "last_changed": dt.datetime.now().isoformat(),
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    return "CHANGED", (
        f"🔔 **{conf['name']} 有變動**\n"
        f"   URL:     {conf['url']}\n"
        f"   指紋:    {cached_fp} → {fp}\n"
        f"   大小變化:{cached_size:,} → {size:,} bytes ({delta:+,})\n"
        f"   stripped:{cached_stripped:,} → {stripped_size:,} bytes\n"
        f"   下一里程碑:{conf['next_milestone']}\n"
        f"   相關議題:{', '.join(conf['related_pi'])}\n"
        f"   👉 建議:人工檢視該頁面內容,若有新公告,執行 `python3 scripts/md_to_sqlite.py --rebuild` 並更新對應議題卡片"
    ), stripped_size


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", choices=list(TARGETS), help="只跑單一目標")
    ap.add_argument("--reset-cache", action="store_true", help="清除快取")
    args = ap.parse_args()

    if args.reset_cache:
        if CACHE_DIR.exists():
            for f in CACHE_DIR.glob("*.json"):
                f.unlink()
            print(f"✓ 清除 {CACHE_DIR.relative_to(ROOT)}/ 下所有快取")
        return 0

    targets = [args.target] if args.target else list(TARGETS)
    print(f"=== {dt.datetime.now().strftime('%Y-%m-%d %H:%M')} 監測開始({len(targets)} 個目標)===\n")

    counts = {"NEW": 0, "CHANGED": 0, "UNCHANGED": 0, "ERROR": 0}
    for tid in targets:
        status, msg, stripped_size = check_target(tid, TARGETS[tid])
        counts[status] += 1
        print(msg)
        print()
        log_event({
            "ts": dt.datetime.now().isoformat(),
            "target": tid,
            "status": status,
            "stripped_size": stripped_size,  # QA #7 修法:供 debug
        })

    print(f"=== 監測結果 ===")
    print(f"  🔔 變動:{counts['CHANGED']}")
    print(f"  📋 首次:{counts['NEW']}")
    print(f"  ✓  無變:{counts['UNCHANGED']}")
    print(f"  ❌ 錯誤:{counts['ERROR']}")

    # 退出碼:有變動 → 0;只有 UNCHANGED → 0;只有 ERROR → 1
    # (用於 cron 通知:有 CHANGED 時 stdout 會夠多以觸發 mail)
    if counts["ERROR"] and not (counts["CHANGED"] or counts["NEW"]):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
