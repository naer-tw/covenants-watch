-- 同性婚姻議題完整脈絡

-- 同婚相關行動者
INSERT OR REPLACE INTO actor (actor_id, actor_type, name, affiliation, position_spectrum, active_period, is_anonymized) VALUES
('A101','court','大法官／憲法法庭','司法院','司法解釋','持續',0),
('A102','public','婚姻平權支持方（民間）','—','寬鬆派','2013-現在',0),
('A103','public','婚姻平權反對方（民間）','—','嚴格派','2013-現在',0),
('A104','academic','法律 / 神學學者群','學界','跨光譜','持續',0),
('A105','court','美國最高法院（比較法）','—','—','持續',0),
('A106','court','UN 人權事務委員會','—','—','持續',0);

-- 同婚事件鏈
INSERT OR REPLACE INTO event (event_id, event_date, event_type, issue_tags, actor_id, title, summary, source_url, related_pi, related_co, related_article, is_positive_outcome, created_at) VALUES

('EV-1994-001','1994-03-31','court_ruling','["同性婚姻"]','A106',
 'Toonen v Australia 個人申訴決定','UN HRC 首次認定 ICCPR sex 涵蓋 sexual orientation',
 'https://juris.ohchr.org/casedetails/702/en-US',
 '["PI-10"]','[]','["ICCPR-26","ICCPR-17"]',NULL,datetime('now')),

('EV-2015-001','2015-06-26','court_ruling','["同性婚姻"]','A105',
 'Obergefell v Hodges 同婚為基本權','美國最高法院 5-4 認定結婚為基本權',
 'https://supreme.justia.com/cases/federal/us/576/644/',
 '["PI-10"]','[]','["ICCPR-26"]',NULL,datetime('now')),

('EV-2017-001','2017-05-24','court_ruling','["同性婚姻"]','A101',
 '司法院釋字 748','要求 2 年內完成同性結合立法',
 'https://cons.judicial.gov.tw/',
 '["PI-13"]','[]','["ICCPR-26","ICCPR-23"]',NULL,datetime('now')),

('EV-2018-001','2018-11-24','public_opinion','["同性婚姻"]','A103',
 '愛家公投三案通過','公投反對同性婚姻納入民法',
 '',
 '["PI-13"]','[]','["ICCPR-26","ICCPR-18"]',NULL,datetime('now')),

('EV-2019-001','2019-05-17','legislation','["同性婚姻"]','A003',
 '立法院三讀《748 施行法》','另立專法保障同性結合',
 'https://www.cna.com.tw/news/firstnews/201905175004.aspx',
 '["PI-13"]','[]','["ICCPR-26"]',NULL,datetime('now')),

('EV-2022-001','2022-05-13','co_paragraph','["同性婚姻"]','A002',
 '第三次審查 CO 同婚範圍擴張要求','要求同性收養、跨國同婚立法',
 'https://covenantswatch.org.tw/2021-third-review-on-iccpr-and-icescr/',
 '["PI-03"]','["CO-3-67"]','["ICCPR-26","ICCPR-23"]',NULL,datetime('now')),

('EV-2023-001','2023-05-16','legislation','["同性婚姻"]','A003',
 '同性同婚收養可','行政院修法允許同性收養共同子女',
 '',
 '["PI-13"]','[]','["ICCPR-26"]',NULL,datetime('now')),

('EV-2025-001','2025-06-27','court_ruling','["同性婚姻","宗教自由"]','A105',
 'Mahmoud v Taylor 父母 opt-out','美最高 6-3 父母宗教教育權須通過 strict scrutiny',
 'https://www.supremecourt.gov/opinions/24pdf/24-297_4f14.pdf',
 '["PI-10"]','[]','["ICCPR-18"]',NULL,datetime('now'));

-- 同婚因果鏈
INSERT INTO causal_link (from_event, to_event, link_type, evidence_strength, chain_depth, counter_evidence, multi_causal_note, note, created_at) VALUES

('EV-1994-001','EV-2017-001','cites','indirect',1,
 '釋字 748 主要法源為憲法第 7 條（平等）+ 第 22 條（婚姻自由），ICCPR 為間接背景',
 '並列原因：(a) 國際同婚立法趨勢；(b) 大法官個別立場；(c) 民間倡議累積',
 '司法院 748 號中 Toonen 為比較法引用',datetime('now')),

('EV-2017-001','EV-2018-001','triggered_by','direct',1,
 '若無釋字 748 之「2 年內立法」要求，反對方可能不會發動公投',
 '愛家公投反映社會分歧，非單純對 748 之回應',
 '釋字 748 之 2 年期限直接觸發 2018 公投時程',datetime('now')),

('EV-2017-001','EV-2019-001','triggered_by','direct',1,
 '若無釋字 748 之憲法強制，立法院可能不會在 2 年內三讀',
 '並列原因：(a) 國際比較壓力；(b) 民間倡議累積；(c) 政黨決策',
 '釋字 748 為立法之憲法上強制力',datetime('now')),

('EV-2018-001','EV-2019-001','contradicts','direct',1,
 '若無公投反對結果，立法可能採民法路徑而非專法',
 '專法路徑為公投限制 + 釋字強制之妥協結果',
 '愛家公投限縮立法形式（專法 vs 民法）',datetime('now')),

('EV-2019-001','EV-2022-001','triggered_by','indirect',2,
 '即使無 2019 立法，國際委員仍可能要求擴張範圍',
 '並列原因：(a) 國際同婚標準上升；(b) 同志團體跨國同婚倡議；(c) CRC 兒童權利之收養討論',
 '2019 立法之「不完整」（無收養 + 無跨國）成為 CO 要求擴張之直接基礎',datetime('now')),

('EV-2022-001','EV-2023-001','triggered_by','direct',1,
 '即使無 CO 要求，行政院仍可能基於司法判決推進收養',
 '並列原因：(a) 司法判決累積；(b) 行政院政策考量；(c) 民間倡議',
 'CO 要求為行政院修法之直接外部壓力',datetime('now')),

('EV-2025-001','EV-2022-001','contradicts','contested',1,
 'Mahmoud 為美國憲法判決，與 ICCPR Art.18 之關係屬比較法外溢',
 'Mahmoud 後續對 Art.18 父母教育選擇權之國際法詮釋影響仍待觀察',
 '美國判例對 ICCPR 詮釋光譜之挑戰',datetime('now'));

-- 同婚結果指標
INSERT OR REPLACE INTO outcome_indicator (indicator_id, event_id, indicator_type, metric_name, before_value, before_year, after_value, after_year, direction, measurement_method, source_url, confounders) VALUES

('IND-101','EV-2019-001','case','同性結婚累計件數','0','2018','逾 10,000','2024','improved','戶政司',
 '',
 '混淆變項：(a) 釋字 748 強制；(b) 國際趨勢；(c) 民眾接受度上升'),

('IND-102','EV-2018-001','public_opinion','支持同性婚姻民意','37%','2013','約 60%','2024','improved','多家民調',
 '',
 '混淆變項：(a) 世代效應（年輕世代支持率較高）；(b) 立法後常態化效應；(c) 反對方議題退潮');
