"""共用 HTTP 工具(Wave 36 抽出)

提供 4 個函式:
- make_opener(verify_ssl)             — cookie jar + optional SSL fallback
- encode_url(url)                     — 編碼含中文的 path
- fetch(url, ...) -> (bytes, bool)    — 嚴格 SSL,白名單 host 允許降級
- fetch_with_opener(url, opener, ...) — 用呼叫端建立的 opener(共用 cookie session)
- fetch_text(url, ...) -> str         — 便利包裝,decode 為 utf-8 字串

設計原則:
- 純 stdlib(無外部依賴,不需 venv)
- 預設嚴格 SSL,只對 SSL_DOWNGRADE_ALLOWED 白名單 host 允許降級(Issue #7 修法)
- 非白名單 host SSL 失敗直接拋錯(避免 MITM 偽造頁面寫入快取)
"""
from __future__ import annotations

import http.cookiejar
import ssl
import urllib.error
import urllib.request
from urllib.parse import quote, urlparse, urlsplit, urlunsplit

USER_AGENT_DEFAULT = "Mozilla/5.0 (CRW-TW/fetcher; +https://naer-tw.github.io/policy/)"

DEFAULT_HEADERS = {
    "User-Agent": USER_AGENT_DEFAULT,
    "Accept-Language": "zh-TW,zh;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/pdf",
}

# 政府站白名單(Issue #7 修法 + QA #6 修法分兩層)
#
# 兩層白名單設計:
# - SSL_DOWNGRADE_ALLOWED:允許 CERT_NONE(跳過憑證驗證,因政府站憑證鏈不全)
# - SSL_LEGACY_RENEG_ALLOWED:在上述基礎上額外允許 OP_LEGACY_SERVER_CONNECT
#   (僅給真正需要 unsafe legacy renegotiation 的站,如立法院 IVOD)
#
# 預設 NAAES 等非政府站走嚴格 SSL,完全不在白名單。
SSL_DOWNGRADE_ALLOWED: set = {
    "nhrc.cy.gov.tw",          # NHRC 政府站,憑證設定不嚴謹
    "nhrc-ws.cy.gov.tw",
    "crc.sfaa.gov.tw",
    "dep.mohw.gov.tw",
    "www.cy.gov.tw",
    "www.sfaa.gov.tw",
    "www.ey.gov.tw",
    "law.moj.gov.tw",
    # Wave 37 加 4 個監測目標,host 補進白名單
    "ivod.ly.gov.tw",          # 立法院 IVOD(同時需 LEGACY_RENEG)
    "www.judicial.gov.tw",     # 司法院統計
    "www.immigration.gov.tw",  # 內政部移民署
    "www.guide.edu.tw",        # 教育部學生輔導資訊網
}

# QA #6 修法:legacy renegotiation 屬第二層白名單,只給真的需要的站
# 目前已知:立法院 IVOD 用舊 OpenSSL 不支援 RFC 5746
SSL_LEGACY_RENEG_ALLOWED: set = {
    "ivod.ly.gov.tw",
}

# QA #6 修法:精確的 SSL 錯誤識別字串(取代寬鬆的 "SSL" / "CERTIFICATE" 子字串比對)
_SSL_ERR_CERT = "CERTIFICATE_VERIFY_FAILED"
_SSL_ERR_LEGACY = "UNSAFE_LEGACY_RENEGOTIATION_DISABLED"


def make_opener(
    verify_ssl: bool = True,
    legacy_reneg: bool = False,
) -> urllib.request.OpenerDirector:
    """每次 fetch 用獨立 opener + cookie jar(處理 ASP.NET session redirect)。

    QA #6 修法:把 SSL 降級拆成兩個獨立旗標,避免「進入降級就拿到所有放寬」。
    - verify_ssl=False:跳過憑證驗證(政府站憑證鏈不全)
    - legacy_reneg=True:額外開啟 OP_LEGACY_SERVER_CONNECT,接受 unsafe legacy
      renegotiation(限立法院 IVOD 等舊 OpenSSL 站,風險最高)
    """
    cj = http.cookiejar.CookieJar()
    handlers = [urllib.request.HTTPCookieProcessor(cj)]
    if not verify_ssl or legacy_reneg:
        ctx = ssl.create_default_context()
        if not verify_ssl:
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
        if legacy_reneg:
            # OP_LEGACY_SERVER_CONNECT = 0x4(Python 3.12+ 才有常數;舊版用魔數)
            ctx.options |= getattr(ssl, "OP_LEGACY_SERVER_CONNECT", 0x4)
        handlers.append(urllib.request.HTTPSHandler(context=ctx))
    return urllib.request.build_opener(*handlers)


def encode_url(url: str) -> str:
    """編碼含中文的 URL path(只編 path,不動 scheme/host/query)。"""
    parts = urlsplit(url)
    safe_path = quote(parts.path, safe="/")
    return urlunsplit((parts.scheme, parts.netloc, safe_path, parts.query, parts.fragment))


def fetch(
    url: str,
    timeout: int = 30,
    headers: dict | None = None,
    encode_path: bool = True,
    allow_insecure: set | None = None,
) -> tuple[bytes, bool]:
    """嚴格 SSL,只對白名單 host 允許降級。

    回 (content_bytes, ssl_downgraded_bool)。

    QA #6 修法:
    - 錯誤識別精確化:只允許 `CERTIFICATE_VERIFY_FAILED` 與
      `UNSAFE_LEGACY_RENEGOTIATION_DISABLED` 兩種錯誤觸發降級;
      其他 SSL 錯誤(如握手失敗、密碼套件協商失敗)直接 raise
    - 兩層白名單:`SSL_DOWNGRADE_ALLOWED` 控 CERT_NONE,
      `SSL_LEGACY_RENEG_ALLOWED` 額外控 legacy renegotiation
    """
    h = dict(DEFAULT_HEADERS)
    if headers:
        h.update(headers)
    safe_url = encode_url(url) if encode_path else url
    req = urllib.request.Request(safe_url, headers=h)
    try:
        with make_opener(verify_ssl=True, legacy_reneg=False).open(req, timeout=timeout) as resp:
            return resp.read(), False
    except urllib.error.URLError as e:
        err_str = str(e)
        # QA #6 修法:精確識別兩種已知 / 可降級的 SSL 錯誤
        is_cert_err = _SSL_ERR_CERT in err_str
        is_legacy_err = _SSL_ERR_LEGACY in err_str
        if not (is_cert_err or is_legacy_err):
            # 非已知降級情境,直接拋(可能是握手失敗、密碼套件協商失敗等)
            raise
        host = urlparse(url).hostname or ""
        whitelist = allow_insecure if allow_insecure is not None else SSL_DOWNGRADE_ALLOWED
        if host not in whitelist:
            raise urllib.error.URLError(
                f"SSL 驗證失敗({'CERT' if is_cert_err else 'LEGACY_RENEG'})"
                f"且 {host} 不在 SSL_DOWNGRADE_ALLOWED;拒絕降級避免 MITM。原錯:{e}"
            )
        # 第二層判斷:是否需要 legacy renegotiation
        need_legacy = is_legacy_err and host in SSL_LEGACY_RENEG_ALLOWED
        if is_legacy_err and not need_legacy:
            raise urllib.error.URLError(
                f"{host} 觸發 legacy renegotiation 但不在 SSL_LEGACY_RENEG_ALLOWED;"
                f"拒絕進一步放寬。原錯:{e}"
            )
        with make_opener(verify_ssl=False, legacy_reneg=need_legacy).open(
            req, timeout=timeout
        ) as resp:
            return resp.read(), True


def fetch_with_opener(
    url: str,
    opener: urllib.request.OpenerDirector,
    timeout: int = 30,
    headers: dict | None = None,
    encode_path: bool = False,
) -> bytes:
    """用呼叫端建立的 opener(供共用 cookie session 場景,如多次抓 ASP.NET 站)。"""
    h = dict(DEFAULT_HEADERS)
    if headers:
        h.update(headers)
    safe_url = encode_url(url) if encode_path else url
    req = urllib.request.Request(safe_url, headers=h)
    with opener.open(req, timeout=timeout) as resp:
        return resp.read()


def fetch_text(url: str, timeout: int = 30, encoding: str = "utf-8") -> str:
    """便利包裝:呼叫 fetch() 並 decode 為字串(忽略 ssl_downgraded 旗標)。"""
    content, _ = fetch(url, timeout=timeout)
    return content.decode(encoding, errors="ignore")
