-- 法律資料層 Schema (Wave 104)
-- 為兩公約總檢討平台補齊修法前後條文 delta、立法理由、行政命令、判決

-- =========================================================================
-- 一、法規（law）— 一部法律的元資訊
-- =========================================================================
CREATE TABLE IF NOT EXISTS law (
    law_id              TEXT PRIMARY KEY,    -- L001 / L002 ...
    law_name_zh         TEXT NOT NULL,       -- 兩公約施行法
    law_name_en         TEXT,
    law_pcode           TEXT,                -- 全國法規資料庫 pcode（如 I0020028）
    enacted_date        TEXT,                -- 制定公布日
    primary_agency      TEXT,                -- 主管機關
    covers_articles     TEXT,                -- JSON：對應之兩公約條文 ["ICCPR-26"]
    related_pi          TEXT,                -- JSON：["PI-10","PI-13"]
    is_implementation_act INTEGER DEFAULT 0, -- 是否為施行法
    is_active           INTEGER DEFAULT 1,
    note                TEXT
);

-- =========================================================================
-- 二、版本（law_version）— 一部法律之歷次三讀版本
-- =========================================================================
CREATE TABLE IF NOT EXISTS law_version (
    version_id          TEXT PRIMARY KEY,    -- L001-V01 / L001-V02
    law_id              TEXT REFERENCES law(law_id),
    version_label       TEXT,                -- 制定 / 第一次修正 / 第二次修正
    promulgated_date    TEXT NOT NULL,       -- 公布日
    effective_date      TEXT,                -- 施行日
    full_text_url       TEXT,                -- 全國法規資料庫該版本連結
    full_text_archive   TEXT,                -- web.archive.org
    legislative_reason  TEXT,                -- 立法理由摘要
    is_current          INTEGER DEFAULT 0,
    note                TEXT
);

CREATE INDEX IF NOT EXISTS idx_law_version_law ON law_version(law_id);
CREATE INDEX IF NOT EXISTS idx_law_version_date ON law_version(promulgated_date);

-- =========================================================================
-- 三、條文 delta（law_article_change）— 修法前後具體條文之變動
-- =========================================================================
CREATE TABLE IF NOT EXISTS law_article_change (
    change_id           INTEGER PRIMARY KEY AUTOINCREMENT,
    version_id          TEXT REFERENCES law_version(version_id),
    article_number      TEXT NOT NULL,       -- 第 2 條 / 第 4 條第 1 項
    change_type         TEXT,                -- new / amended / deleted / renumbered
    text_before         TEXT,                -- 修正前條文（若有）
    text_after          TEXT,                -- 修正後條文
    reason              TEXT,                -- 該條修正理由
    related_co          TEXT,                -- JSON：對應 CO 條目
    related_article     TEXT,                -- JSON：對應兩公約條文
    note                TEXT
);

CREATE INDEX IF NOT EXISTS idx_article_change_version ON law_article_change(version_id);

-- =========================================================================
-- 四、修法事件（law_amendment）— 與既有 event 表連結
-- =========================================================================
CREATE TABLE IF NOT EXISTS law_amendment (
    amendment_id        TEXT PRIMARY KEY,    -- AMD-YYYY-NNN
    law_id              TEXT REFERENCES law(law_id),
    version_id          TEXT REFERENCES law_version(version_id),
    related_event_id    TEXT REFERENCES event(event_id),  -- 連到 trace event

    proposal_date       TEXT,                -- 提案日
    first_reading       TEXT,                -- 一讀日
    third_reading       TEXT,                -- 三讀日
    promulgated         TEXT,                -- 公布日

    proposer_summary    TEXT,                -- 提案人 / 黨團摘要（不點名個人）
    contention_level    TEXT,                -- low / medium / high / very_high

    -- 修法前後對比摘要
    summary_before      TEXT,
    summary_after       TEXT,
    key_changes         TEXT,                -- JSON：關鍵變動點

    -- 後續行政命令
    related_executive_orders TEXT,           -- JSON URLs

    -- 對應之 CO 來源（哪屆審查 CO 觸發了此修法）
    triggered_by_co     TEXT,                -- JSON: ["CO-3-§67"]

    note                TEXT
);

-- =========================================================================
-- 五、行政命令 / 施行細則（executive_order）
-- =========================================================================
CREATE TABLE IF NOT EXISTS executive_order (
    order_id            TEXT PRIMARY KEY,    -- EO-YYYY-NNN
    parent_law_id       TEXT REFERENCES law(law_id),
    order_name          TEXT NOT NULL,       -- 學生輔導法施行細則 / 性別平等教育法施行細則
    order_type          TEXT,                -- 施行細則 / 辦法 / 標準 / 準則
    promulgated_date    TEXT,
    issuing_agency      TEXT,
    full_text_url       TEXT,
    note                TEXT
);

-- =========================================================================
-- 六、views
-- =========================================================================
CREATE VIEW IF NOT EXISTS v_law_history AS
SELECT
    l.law_name_zh,
    lv.version_label,
    lv.promulgated_date,
    lv.effective_date,
    COUNT(lac.change_id) AS n_article_changes,
    lv.legislative_reason
FROM law l
LEFT JOIN law_version lv ON l.law_id = lv.law_id
LEFT JOIN law_article_change lac ON lv.version_id = lac.version_id
GROUP BY lv.version_id
ORDER BY l.law_name_zh, lv.promulgated_date;
