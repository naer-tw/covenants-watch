-- 因果脈絡追溯 Schema (Wave 92)
-- 設計紅線：
-- 1. 稱「脈絡追溯」非「責任追溯」
-- 2. 每個歸因必附反證欄位
-- 3. 因果鏈 > 3 層自動加警告
-- 4. 正反結果並陳（is_positive_outcome 欄位）
-- 5. 論述（statement）與責任歸屬（accountability）嚴格分離

-- =========================================================================
-- 一、行動者（actor）
-- =========================================================================
CREATE TABLE IF NOT EXISTS actor (
    actor_id            TEXT PRIMARY KEY,    -- A001 / A002 / 不點名個人時用代碼
    actor_type          TEXT NOT NULL,       -- ngo / committee_member / govt_agency / legislator / media / academic / public / court
    name                TEXT,                -- 組織 / 機關名（個人不點名，除已被法院判決公開）
    affiliation         TEXT,                -- 政黨 / 國別 / 機構
    position_spectrum   TEXT,                -- 立場光譜：寬鬆派 / 中間 / 嚴格派 / 中性記錄者
    active_period       TEXT,                -- 2009-2026 等
    is_anonymized       INTEGER DEFAULT 0,   -- 1=代碼化（個人）/ 0=公開職務組織
    note                TEXT
);

-- =========================================================================
-- 二、事件 / 論述（event）
-- =========================================================================
CREATE TABLE IF NOT EXISTS event (
    event_id        TEXT PRIMARY KEY,        -- EV-YYYY-NNN
    event_date      TEXT NOT NULL,           -- ISO 日期 / 月份
    event_type      TEXT NOT NULL,           -- shadow_report / co_paragraph / committee_question / govt_response /
                                             -- legislation / court_ruling / outcome / public_opinion / advocacy_campaign
    issue_tags      TEXT,                    -- JSON array：["同性婚姻","廢死","兒少自殺"]
    actor_id        TEXT REFERENCES actor(actor_id),

    title           TEXT NOT NULL,
    summary         TEXT,                    -- 一句話摘要
    full_quote      TEXT,                    -- 完整原文引用（如有）

    source_url      TEXT,
    source_archive  TEXT,                    -- web.archive.org URL

    related_pi      TEXT,                    -- JSON：["PI-02","PI-13"]
    related_co      TEXT,                    -- JSON：["CO-1-§6","CO-3-§57"]
    related_article TEXT,                    -- JSON：["ICCPR-6","ICCPR-26"]

    is_positive_outcome     INTEGER,         -- 對讀者的判斷有用：1=多數視為正面 / 0=多數視為負面 / NULL=爭議
    note            TEXT,
    created_at      TEXT
);

CREATE INDEX IF NOT EXISTS idx_event_date  ON event(event_date);
CREATE INDEX IF NOT EXISTS idx_event_type  ON event(event_type);
CREATE INDEX IF NOT EXISTS idx_event_actor ON event(actor_id);

-- =========================================================================
-- 三、因果鏈（causal_link）— **核心反思設計**
-- =========================================================================
CREATE TABLE IF NOT EXISTS causal_link (
    link_id             INTEGER PRIMARY KEY AUTOINCREMENT,
    from_event          TEXT NOT NULL REFERENCES event(event_id),
    to_event            TEXT NOT NULL REFERENCES event(event_id),

    link_type           TEXT NOT NULL,       -- triggered_by / responds_to / implements /
                                             -- contradicts / cites / opposes / parallels
    evidence_strength   TEXT NOT NULL,       -- direct / indirect / inferred / contested
                                             -- direct = 該行動者明示因果
                                             -- indirect = 時序 + 主題相關
                                             -- inferred = 平台推論（須附反證）
                                             -- contested = 各方有不同詮釋

    chain_depth         INTEGER DEFAULT 1,   -- 自動計算累積鏈長

    counter_evidence    TEXT,                -- **反證 / 反事實**（紅線 2 強制）
                                             -- 「若不發生 from_event，是否仍會發生 to_event？」之公開反證

    multi_causal_note   TEXT,                -- 標記其他並列原因（紅線 1）
                                             -- 「to_event 之同等並列原因尚有 X / Y / Z」

    note                TEXT,
    created_at          TEXT,
    reviewed_by         TEXT,                -- 雙人編碼仲裁
    review_kappa        REAL                 -- 編碼者間信度（≥ 0.7 才能對外發布）
);

CREATE INDEX IF NOT EXISTS idx_link_from ON causal_link(from_event);
CREATE INDEX IF NOT EXISTS idx_link_to   ON causal_link(to_event);

-- =========================================================================
-- 四、結果指標（outcome_indicator）
-- =========================================================================
CREATE TABLE IF NOT EXISTS outcome_indicator (
    indicator_id        TEXT PRIMARY KEY,
    event_id            TEXT REFERENCES event(event_id),
    indicator_type      TEXT,                -- statistic / case / law / public_opinion / qualitative
    metric_name         TEXT,                -- 「青少年自殺率」「同婚件數」
    before_value        TEXT,
    before_year         TEXT,
    after_value         TEXT,
    after_year          TEXT,
    direction           TEXT,                -- improved / worsened / unchanged / contested
    measurement_method  TEXT,                -- 衛福部死因統計 / 司法院統計 / 民調機構
    source_url          TEXT,
    confounders         TEXT,                -- 混淆變項清單（防止單向歸因）
    note                TEXT
);

-- =========================================================================
-- 五、追溯查詢檢索檢視（views）
-- =========================================================================

-- 議題時序鏈（按議題 tag 過濾，按時間排序）
CREATE VIEW IF NOT EXISTS v_issue_timeline AS
SELECT
    e.event_date,
    e.event_type,
    a.name AS actor_name,
    a.actor_type,
    e.title,
    e.summary,
    e.is_positive_outcome,
    e.issue_tags,
    e.related_pi,
    e.source_url,
    e.event_id
FROM event e
LEFT JOIN actor a ON e.actor_id = a.actor_id
ORDER BY e.event_date;

-- 行動者全紀錄
CREATE VIEW IF NOT EXISTS v_actor_record AS
SELECT
    a.name AS actor_name,
    a.actor_type,
    a.position_spectrum,
    e.event_date,
    e.event_type,
    e.title,
    e.summary,
    e.source_url
FROM actor a
JOIN event e ON a.actor_id = e.actor_id
ORDER BY a.name, e.event_date;

-- 全文檢索
CREATE VIRTUAL TABLE IF NOT EXISTS fts_event USING fts5(
    event_id, title, summary, full_quote, issue_tags,
    content='event', content_rowid='rowid'
);
