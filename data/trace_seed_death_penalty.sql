-- 廢死議題完整脈絡（範例填充）
-- 含 13 年（2013-2026）跨行動者、跨層級之事件鏈
-- 紅線：每個 causal_link 必附 counter_evidence

-- =========================================================================
-- 一、行動者（actor）
-- =========================================================================
INSERT OR REPLACE INTO actor (actor_id, actor_type, name, affiliation, position_spectrum, active_period, is_anonymized) VALUES
('A001','ngo','廢死聯盟（TAEDP）','民間組織','寬鬆派（廢死）','2003-現在',0),
('A002','committee_member','Manfred Nowak','奧地利 / 前 UN 酷刑特別報告員','寬鬆派（廢死）','2013-2026 連 4 屆',0),
('A003','govt_agency','法務部','行政院','官方執行機關','持續',0),
('A004','court','憲法法庭','司法院','司法解釋','持續',0),
('A005','public','一般民眾（民調 88%）','—','嚴格派（保留死刑）','持續',0),
('A006','academic','法律學者群','學界','跨光譜','持續',0),
('A007','ngo','人權公約施行監督聯盟（CovenantsWatch）','民間組織','寬鬆派','2009-現在',0),
('A008','ngo','被害人家屬團體','民間組織','嚴格派','持續',0);

-- =========================================================================
-- 二、事件（event）— 廢死議題 13 年時序
-- =========================================================================
INSERT OR REPLACE INTO event (event_id, event_date, event_type, issue_tags, actor_id, title, summary, source_url, related_pi, related_co, related_article, is_positive_outcome, created_at) VALUES

-- 2009 起點
('EV-2009-001','2009-12-10','legislation','["廢死","兩公約施行"]','A003',
 '兩公約施行法施行','ICCPR Art.6 生命權成為國內法律效力',
 'https://law.moj.gov.tw/LawClass/LawAll.aspx?pcode=I0020028',
 '["PI-01"]','[]','["ICCPR-6"]',NULL,datetime('now')),

-- 2012 民間影子報告（送到 2013 審查）
('EV-2012-001','2012-12','shadow_report','["廢死"]','A007',
 '人約盟 ICCPR 影子報告 — 廢死章節','要求台灣立即停止執行死刑、批准 ICCPR OP2',
 'https://covenantswatch.org.tw/wp-content/uploads/2018/12/2013-ICCPR-State-Reports-Shadow-Report_EN.pdf',
 '["PI-02","PI-14"]','[]','["ICCPR-6"]',NULL,datetime('now')),

('EV-2012-002','2012-12','shadow_report','["廢死"]','A001',
 '廢死聯盟影子報告呼籲','要求批准 ICCPR 第二任擇議定書',
 'https://www.taedp.org.tw/story/1982',
 '["PI-02"]','[]','["ICCPR-6"]',NULL,datetime('now')),

-- 2013 第一次國際審查 CO
('EV-2013-001','2013-03-01','co_paragraph','["廢死"]','A002',
 'CO §6 要求批准 ICCPR OP2','國際委員建議台灣立即批准廢死議定書',
 'https://covenantswatch.org.tw/wp-content/uploads/2018/12/2013-ICCPR-ICESCR-CORs_EN.pdf',
 '["PI-02"]','["CO-1-§6"]','["ICCPR-6"]',NULL,datetime('now')),

('EV-2013-002','2013-03-01','co_paragraph','["廢死"]','A002',
 'CO §57 立即停止執行','國際委員建議立即停止執行死刑、邁向廢除',
 'https://covenantswatch.org.tw/wp-content/uploads/2018/12/2013-ICCPR-ICESCR-CORs_EN.pdf',
 '["PI-02"]','["CO-1-§57"]','["ICCPR-6"]',NULL,datetime('now')),

-- 2017 第二次審查（重複要求）
('EV-2017-001','2017-01-20','co_paragraph','["廢死"]','A002',
 '第二次審查 CO 重複要求廢死','13 年來 1/2/3/4 屆均要求',
 'https://covenantswatch.org.tw/wp-content/uploads/2018/12/2017-ICCPR-ICESCR-CORs_EN.pdf',
 '["PI-02"]','["CO-2-廢死"]','["ICCPR-6"]',NULL,datetime('now')),

-- 2022 第三次審查（仍未廢）
('EV-2022-001','2022-05-13','co_paragraph','["廢死"]','A002',
 '第三次審查 CO 再次要求','含心智障礙者不得判處死刑（CO §58）',
 'https://covenantswatch.org.tw/2021-third-review-on-iccpr-and-icescr/',
 '["PI-02","PI-03"]','["CO-3-廢死"]','["ICCPR-6"]',NULL,datetime('now')),

-- 2024 113 憲判 8 號（重大事件）
('EV-2024-001','2024-09-20','court_ruling','["廢死"]','A004',
 '113 憲判 8 號死刑釋憲','實質縮限死刑適用範圍但未廢除；要求 2 年內修法',
 'https://www.cna.com.tw/news/aipl/202409200280.aspx',
 '["PI-02"]','["CO-1-§57","CO-1-§58"]','["ICCPR-6"]',NULL,datetime('now')),

-- 2024 起政府未再執行
('EV-2024-002','2024-09-20','outcome','["廢死"]','A003',
 '法務部 2024-09 後未再執行死刑','36 名死囚仍在獄中；尚未進入 OP2 批准程序',
 'https://www.cna.com.tw/news/aipl/202409200280.aspx',
 '["PI-02"]','["CO-1-§57"]','["ICCPR-6"]',NULL,datetime('now')),

-- 民意（嚴格派論述）
('EV-2025-001','2025-08','public_opinion','["廢死"]','A005',
 '民調 88% 反對廢死','喆律法律統整多方民調',
 'https://zhelu.tw/post/abolition-of-the-death-penalty',
 '["PI-02"]','[]','["ICCPR-6"]',0,datetime('now')),

-- 2026 第四次審查預期
('EV-2026-001','2026-05','co_paragraph','["廢死"]','A002',
 '第四次審查預期再次提出','Manfred Nowak 第 4 屆主席連續 4 屆關注',
 'https://www.humanrights.moj.gov.tw/media/20214843/',
 '["PI-03"]','[]','["ICCPR-6"]',NULL,datetime('now'));

-- =========================================================================
-- 三、因果鏈（causal_link）— 含反證、多元因果
-- =========================================================================
INSERT INTO causal_link (from_event, to_event, link_type, evidence_strength, chain_depth, counter_evidence, multi_causal_note, note, created_at) VALUES

-- 影子報告 → 2013 CO
('EV-2012-001','EV-2013-001','triggered_by','direct',1,
 '即使無民間影子報告，國際委員可能仍會獨立提出廢死要求（基於 ICCPR Art.6 國際標準）',
 '本 CO 之並列原因尚包含：(a) 國際間 OP2 趨勢；(b) Manfred Nowak 個人專業立場；(c) 其他國家 CO 之比較基線',
 '人約盟主編影子報告為制度化之輸入管道',datetime('now')),

('EV-2012-002','EV-2013-001','triggered_by','indirect',1,
 '同上 — 即使無 TAEDP 個別倡議，CO 廢死要求仍可能成立',
 '人約盟整合多 NGO 之集體倡議為主要管道',
 'TAEDP 為個別倡議方之一',datetime('now')),

-- 2013 CO → 13 年 abandoned
('EV-2013-001','EV-2024-002','responds_to','contested',2,
 '即使無 CO §6 壓力，台灣 2014 後執行死刑案件數量本就因社會討論加劇而下降',
 '並列原因：(a) 民意 88% 反對；(b) 法務部行政考量；(c) 多次冤案疑慮',
 '13 年來 OP2 仍未批准，CO 未實質兌現',datetime('now')),

-- 2013 CO + 多次再要求 → 2024 憲判
('EV-2013-002','EV-2024-001','triggered_by','indirect',2,
 '113 憲判 8 號之主要法源為憲法第 15 條 + 第 23 條，非直接援引 ICCPR；CO 為間接背景之一',
 '主要因素：(a) 憲法解釋方法論；(b) 國際人權趨勢；(c) 立法院 2018-2024 多次冤案討論',
 '法院判決中 CO 援引被歸類為「裝飾性援引」（蘇慧婕 2018）',datetime('now')),

-- 民意 → 立法院延宕
('EV-2025-001','EV-2024-002','contradicts','direct',1,
 '若無 88% 民意反對，OP2 批准可能更早通過',
 '民意反映非單一因素，含個案影響、媒體報導、家屬團體倡議',
 '民意是廢死進度延遲之直接政治壓力來源',datetime('now')),

-- 2024 憲判 + 民意 → 2024 暫停執行
('EV-2024-001','EV-2024-002','triggered_by','direct',1,
 '若無憲判 8 號之 2 年修法期，法務部仍可能於 2024-2026 間執行 1-2 案',
 '法務部之政治考量為直接因素，憲判 8 號為法律拘束',
 '暫停執行為憲判 + 行政綜合結果',datetime('now')),

-- 1-3 屆 CO → 4 屆預期
('EV-2013-002','EV-2026-001','parallels','direct',1,
 '即使前 3 屆未產出廢死 CO，第 4 屆 Nowak 仍會基於 OP2 趨勢提出',
 'Nowak 之專業立場為直接因素；累積 CO 為強化背景',
 '13 年來廢死議題之 CO 連續性',datetime('now'));

-- =========================================================================
-- 四、結果指標（outcome_indicator）
-- =========================================================================
INSERT OR REPLACE INTO outcome_indicator (indicator_id, event_id, indicator_type, metric_name, before_value, before_year, after_value, after_year, direction, measurement_method, source_url, confounders) VALUES

('IND-001','EV-2024-002','statistic','實際執行死刑人次','1（2020）','2020','0（2024-2026）','2026','improved','法務部統計',
 'https://www.cna.com.tw/news/aipl/202409200280.aspx',
 '混淆變項：(a) 113 憲判 8 號 2 年修法期；(b) 政務首長個人立場；(c) 重大個案發生頻率'),

('IND-002','EV-2024-002','case','OP2 批准進度','未批准','2009','未批准','2026','unchanged','法務部',
 'https://www.humanrights.moj.gov.tw/',
 '混淆變項：(a) 88% 民意反對；(b) 朝野共識不足；(c) 兩公約施行法之內國效力已涵蓋部分要求'),

('IND-003','EV-2025-001','public_opinion','支持廢死民意','11.6%（部分民調）','2009','12%（2025）','2025','unchanged','喆律法律 + 多家民調',
 'https://zhelu.tw/post/abolition-of-the-death-penalty',
 '混淆變項：(a) 民調題目設計（無條件 vs 配套）；(b) 重大個案前後民調波動；(c) 樣本族群差異');
