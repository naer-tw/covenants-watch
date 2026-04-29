-- 兩公約總檢討平台 SQLite Schema
-- Created: 2026-04-29 (Wave 12)
-- Updated: -
-- DB Path: data/two_cov.db

-- =========================================================================
-- 一、議題卡片（Policy Issues / PI）
-- =========================================================================
CREATE TABLE IF NOT EXISTS policy_issue (
    pi_id           TEXT PRIMARY KEY,    -- PI-XX
    title           TEXT NOT NULL,
    block           TEXT,                -- A / B / C / D
    priority        TEXT,                -- P0 / P1 / P2 / P3
    status          TEXT,                -- draft / framework / data_pending / published
    covenant        TEXT,                -- ICCPR / ICESCR / both
    co_referenced   TEXT,                -- JSON array
    keywords        TEXT,
    file_path       TEXT,                -- data/policy_issues/...
    created         TEXT,
    last_updated    TEXT,
    summary         TEXT
);

-- =========================================================================
-- 二、結論性意見（Concluding Observations / CO）
-- =========================================================================
CREATE TABLE IF NOT EXISTS concluding_observation (
    co_id                       TEXT PRIMARY KEY,
    review                      INTEGER NOT NULL,
    review_year                 INTEGER,
    paragraph_number            INTEGER,
    topic                       TEXT,
    covenant                    TEXT,
    article_referenced          TEXT,    -- JSON array
    chinese_title               TEXT,
    recommendation_full         TEXT,
    follow_up_status            TEXT,    -- not_started / in_progress / partially_done / done / delayed / abandoned / ambiguous
    gov_response_url            TEXT,
    nhrc_assessment             TEXT,
    civil_society_view          TEXT,
    political_use_score         INTEGER DEFAULT 0,
    selective_citation_count    INTEGER DEFAULT 0,
    created_at                  TEXT,
    updated_at                  TEXT
);

CREATE INDEX IF NOT EXISTS idx_co_review     ON concluding_observation(review);
CREATE INDEX IF NOT EXISTS idx_co_topic      ON concluding_observation(topic);
CREATE INDEX IF NOT EXISTS idx_co_covenant   ON concluding_observation(covenant);

-- =========================================================================
-- 三、結論性意見之被引用（Citations）
-- =========================================================================
CREATE TABLE IF NOT EXISTS co_citation (
    citation_id         INTEGER PRIMARY KEY AUTOINCREMENT,
    co_id               TEXT REFERENCES concluding_observation(co_id),
    cited_by_org        TEXT,
    cited_by_person     TEXT,
    cited_in_context    TEXT,
    cited_date          TEXT,
    cited_url           TEXT,
    source_archive      TEXT,
    full_quote          TEXT,
    has_distortion      INTEGER DEFAULT 0,
    distortion_note     TEXT,
    created_at          TEXT
);

CREATE INDEX IF NOT EXISTS idx_citation_co_id ON co_citation(co_id);
CREATE INDEX IF NOT EXISTS idx_citation_org   ON co_citation(cited_by_org);
CREATE INDEX IF NOT EXISTS idx_citation_date  ON co_citation(cited_date);

-- =========================================================================
-- 四、國家人權行動計畫（NAP Action）
-- =========================================================================
CREATE TABLE IF NOT EXISTS nap_action (
    nap_id              TEXT PRIMARY KEY,    -- NAP1-018, NAP2-006
    phase               INTEGER,
    phase_period        TEXT,
    action_number       INTEGER,
    category            TEXT,
    short_title         TEXT,
    responsible_agency  TEXT,
    co_referenced       TEXT,                -- JSON array
    status              TEXT,
    self_evaluation     TEXT,
    nhrc_evaluation     TEXT,
    civil_society_view  TEXT,
    budget_allocated    REAL,
    budget_spent        REAL,
    keywords            TEXT,
    created_at          TEXT,
    updated_at          TEXT
);

CREATE INDEX IF NOT EXISTS idx_nap_phase    ON nap_action(phase);
CREATE INDEX IF NOT EXISTS idx_nap_category ON nap_action(category);

CREATE TABLE IF NOT EXISTS nap_milestone (
    milestone_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    nap_id          TEXT REFERENCES nap_action(nap_id),
    milestone_date  TEXT,
    description     TEXT,
    source_url      TEXT,
    is_official     INTEGER
);

-- =========================================================================
-- 五、工具化證據（Evidence）
-- =========================================================================
CREATE TABLE IF NOT EXISTS evidence (
    evidence_id                     TEXT PRIMARY KEY,
    collected_date                  TEXT,
    event_date                      TEXT,
    type                            TEXT,    -- legislative / media / ngo / gov_official / academic / social_media
    actor_name                      TEXT,
    actor_affiliation               TEXT,
    actor_role                      TEXT,
    full_quote                      TEXT,
    source_url                      TEXT,
    source_archive                  TEXT,    -- web.archive.org URL
    context                         TEXT,
    covenant_articles_cited         TEXT,    -- JSON
    covenant_articles_avoided       TEXT,    -- JSON
    general_comment_distortion      INTEGER DEFAULT 0,
    distortion_note                 TEXT,
    political_use_score             INTEGER DEFAULT 0,
    asymmetry_dimension             TEXT,    -- JSON [1,3]
    related_co                      TEXT,    -- JSON
    related_pi                      TEXT,    -- JSON
    contains_personal_info          INTEGER DEFAULT 0,
    redaction_applied               INTEGER DEFAULT 0,
    created_at                      TEXT
);

CREATE INDEX IF NOT EXISTS idx_evidence_date    ON evidence(event_date);
CREATE INDEX IF NOT EXISTS idx_evidence_type    ON evidence(type);
CREATE INDEX IF NOT EXISTS idx_evidence_actor   ON evidence(actor_name);

-- =========================================================================
-- 六、立法院公報援引追蹤
-- =========================================================================
CREATE TABLE IF NOT EXISTS legislative_citation (
    leg_cit_id          INTEGER PRIMARY KEY AUTOINCREMENT,
    session_date        TEXT,
    session_number      TEXT,
    speaker_name        TEXT,
    speaker_party       TEXT,
    speaker_district    TEXT,
    article_cited       TEXT,    -- ICCPR-26 等
    full_quote          TEXT,
    bill_related        TEXT,
    vote_outcome        TEXT,
    bulletin_url        TEXT,
    bulletin_archive    TEXT,
    created_at          TEXT
);

CREATE INDEX IF NOT EXISTS idx_legcit_party     ON legislative_citation(speaker_party);
CREATE INDEX IF NOT EXISTS idx_legcit_article   ON legislative_citation(article_cited);
CREATE INDEX IF NOT EXISTS idx_legcit_date      ON legislative_citation(session_date);

-- =========================================================================
-- 七、受控詞表（Vocabulary Tables）
-- =========================================================================
CREATE TABLE IF NOT EXISTS vocab_co_topic (
    code        TEXT PRIMARY KEY,    -- 14_sexual_orientation 等
    name_zh     TEXT,
    name_en     TEXT,
    description TEXT
);

CREATE TABLE IF NOT EXISTS vocab_political_party (
    party_code  TEXT PRIMARY KEY,    -- DPP / KMT / TPP / NPP / PFP / IND
    name_zh     TEXT,
    name_en     TEXT,
    aliases     TEXT,                -- JSON
    is_active   INTEGER DEFAULT 1
);

CREATE TABLE IF NOT EXISTS vocab_agency (
    agency_code TEXT PRIMARY KEY,
    name_zh     TEXT,
    name_en     TEXT,
    aliases     TEXT,                -- JSON
    parent_code TEXT
);

CREATE TABLE IF NOT EXISTS vocab_problem_tag (
    tag_code    TEXT PRIMARY KEY,
    name_zh     TEXT,
    description TEXT
);

CREATE TABLE IF NOT EXISTS vocab_quotability (
    code        TEXT PRIMARY KEY,    -- direct / rewrite / background
    name_zh     TEXT
);

CREATE TABLE IF NOT EXISTS vocab_privacy (
    code        TEXT PRIMARY KEY,
    name_zh     TEXT,
    description TEXT
);

-- =========================================================================
-- 八、全文搜尋索引（FTS5）
-- =========================================================================
CREATE VIRTUAL TABLE IF NOT EXISTS fts_co USING fts5(
    co_id, recommendation_full, chinese_title,
    content='concluding_observation', content_rowid='rowid'
);

CREATE VIRTUAL TABLE IF NOT EXISTS fts_evidence USING fts5(
    evidence_id, full_quote, distortion_note,
    content='evidence', content_rowid='rowid'
);

CREATE VIRTUAL TABLE IF NOT EXISTS fts_legislative USING fts5(
    leg_cit_id, full_quote, speaker_name, bill_related,
    content='legislative_citation', content_rowid='rowid'
);
