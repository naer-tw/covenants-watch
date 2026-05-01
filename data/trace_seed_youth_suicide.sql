-- 兒少自殺議題 trace seed（你最關心的議題）
-- 由 parallel-research agent 蒐集（2026-04-30）
-- 設計紅線：不點名個人；每 link 必填 counter_evidence；每 indicator 必填 confounders；鏈深 ≤ 3

-- =========================================================================
-- 一、行動者
-- =========================================================================
INSERT OR REPLACE INTO actor (actor_id, actor_type, name, affiliation, position_spectrum, active_period, is_anonymized) VALUES
('A201','ngo','兒童福利聯盟基金會','民間','兒少權益倡議','1991-現在',0),
('A202','ngo','董氏基金會心理衛生中心','民間','心理健康倡議','1984-現在',0),
('A203','ngo','人本教育基金會','民間','校園文化批判／結構派','1989-現在',0),
('A204','ngo','台灣少年權益與福利促進聯盟','民間','青少年權益寬鬆派','2003-現在',0),
('A205','ngo','人權公約施行監督聯盟','民間','人權監督中性記錄者','2009-現在',0),
('A206','govt_agency','衛福部心理健康司','行政院','政策執行','2013-現在',0),
('A207','govt_agency','教育部學生事務及特殊教育司','行政院','政策執行','持續',0),
('A208','govt_agency','衛福部社會及家庭署（CRC 主政）','行政院','政策執行','持續',0),
('A209','committee_member','兩公約／CRC 國際審查委員會','聯合國體系專家','國際標準','2013-現在',0),
('A210','academic','自殺防治學會／公衛學者群','學界','實證派','持續',0),
('A211','legislator','立法院教育及文化委員會','立法院','跨黨派','持續',0);

-- =========================================================================
-- 二、事件鏈
-- =========================================================================
INSERT OR REPLACE INTO event (event_id, event_date, event_type, issue_tags, actor_id, title, summary, source_url, related_pi, related_co, related_article, is_positive_outcome, created_at) VALUES
('EV-2014-101','2014-11-12','legislation','["兒少自殺"]','A207','學生輔導法施行','建立國中小／高中／大專三級輔導體制與輔諮中心','https://edu.law.moe.gov.tw/LawContent.aspx?id=GL001380','["PI-11"]','[]','["ICESCR-12","ICESCR-13"]',1,datetime('now')),
('EV-2017-101','2017-01-20','shadow_report','["兒少自殺"]','A205','兩公約第二次審查 NGO 平行報告','80 個 NGO 聯合提交，涵蓋兒少權益／心理健康人力不足','https://covenantswatch.org.tw/','["PI-11"]','[]','["ICESCR-12"]',NULL,datetime('now')),
('EV-2017-102','2017-11-24','co_paragraph','["兒少自殺"]','A209','CRC 第一次國家報告審查 CO','關注兒少自殺率與心理健康支持資源不足','https://crc.sfaa.gov.tw/','["PI-11"]','["CRC-CO1"]','["CRC-6","CRC-24"]',NULL,datetime('now')),
('EV-2019-101','2019-06-19','legislation','["兒少自殺"]','A206','《自殺防治法》三讀施行','建立通報、關懷、媒體報導規範','https://law.moj.gov.tw/','["PI-11"]','[]','["ICESCR-12"]',1,datetime('now')),
('EV-2019-102','2019-06','outcome','["兒少自殺"]','A210','15-24 歲自殺人數年增 22.4%','2019 較 2018 增 47 人達 257 人，連 6 年上升','https://dep.mohw.gov.tw/domhaoh/fp-4904-8883-107.html','["PI-11"]','[]','["ICESCR-12"]',0,datetime('now')),
('EV-2021-101','2021','public_opinion','["兒少自殺"]','A203','重大校園自殺事件群（公開報導）','數起高中／國中校園事件引發對校規、自述書、學業壓力之檢討（不點名個人）','','["PI-11"]','[]','["CRC-19"]',NULL,datetime('now')),
('EV-2022-101','2022-05-13','co_paragraph','["兒少自殺"]','A209','兩公約第三次審查 CO','要求強化兒少心理健康、減壓校園文化、擴增輔導人力','https://covenantswatch.org.tw/2021-third-review-on-iccpr-and-icescr/','["PI-11"]','["CO-3"]','["ICESCR-12"]',NULL,datetime('now')),
('EV-2022-102','2022-11','co_paragraph','["兒少自殺"]','A209','CRC 第二次國家報告 CO','指出生育率低但兒少死亡率高，肯定政策但點出結構性壓力（學業／霸凌／不當對待）','https://crc.sfaa.gov.tw/Document?folderid=479','["PI-11"]','["CRC-CO2"]','["CRC-6","CRC-19","CRC-24"]',NULL,datetime('now')),
('EV-2023-101','2023-05-25','committee_question','["兒少自殺"]','A211','立院「兒少自殺原因回溯調查機制」公聽會','跨部會檢討三級輔導與死因回溯','https://www.mohw.gov.tw/dl-83665-55bc5bfa-1734-4b9f-8dd0-2e9ba7dcb0cd.html','["PI-11"]','["CO-3"]','["ICESCR-12"]',NULL,datetime('now')),
('EV-2023-102','2023','govt_response','["兒少自殺"]','A206','「年輕族群心理健康支持方案」1.07 億元','15-30 歲免費 3 次心理諮商試辦','https://dep.mohw.gov.tw/DOMHAOH/cp-509-79500-107.html','["PI-11"]','["CO-3"]','["ICESCR-12"]',1,datetime('now')),
('EV-2024-101','2024-08-01','govt_response','["兒少自殺"]','A206','「15-45 歲青壯世代心理健康支持方案」啟動','擴大年齡上限至 45 歲，預估 6 萬人次','https://www.mohw.gov.tw/cp-16-79502-1.html','["PI-11"]','["CO-3"]','["ICESCR-12"]',1,datetime('now')),
('EV-2024-102','2024-12-18','legislation','["兒少自殺"]','A207','學生輔導法修正公布','大專師生比 1200:1→900:1；國中小增逾 600 名專輔教師','https://udn.com/news/story/6885/8392812','["PI-11"]','["CO-3","CRC-CO2"]','["ICESCR-12","ICESCR-13"]',1,datetime('now')),
('EV-2025-101','2025-01','govt_response','["兒少自殺"]','A206','全民心理健康韌性計畫（2025-2030）核定','6 年 56.3 億元、6 大策略','https://dep.mohw.gov.tw/DOMHAOH/lp-329-107.html','["PI-11"]','["CO-3"]','["ICESCR-12"]',1,datetime('now'));

-- =========================================================================
-- 三、因果鏈（每條附反證 + 並列原因）
-- =========================================================================
INSERT INTO causal_link (from_event, to_event, link_type, evidence_strength, chain_depth, counter_evidence, multi_causal_note, note, created_at) VALUES
('EV-2014-101','EV-2019-102','parallels','contested',1,'2014 學輔法施行後 2018-2019 自殺率仍上升 22.4%，顯示制度上路不等於降低風險','並列原因：(a) 網路／社群擴張；(b) 家庭結構變化；(c) 通報率提升而非真實上升','制度建置與結果指標未呈現預期負相關',datetime('now')),
('EV-2017-102','EV-2019-101','triggered_by','indirect',1,'《自殺防治法》立法主要動因為國內死因統計與民間倡議，CRC CO 為間接背景','並列原因：(a) 國內自殺率長年居高；(b) WHO 自殺防治倡議；(c) 民間長期遊說','CO 對立法時點具加速作用',datetime('now')),
('EV-2019-102','EV-2021-101','parallels','indirect',1,'個案成因多元，未必可歸因於整體自殺率上升趨勢','並列原因：(a) 校園文化／管教方式；(b) 個別情境；(c) 媒體效應','個案與統計趨勢屬不同層次',datetime('now')),
('EV-2021-101','EV-2022-101','triggered_by','indirect',2,'CO 起草以總體統計與多年期趨勢為主，個案僅為脈絡','並列原因：(a) 民間影子報告；(b) 國家人權委員會獨立評估；(c) 國際比較數據','重大事件提升 CO 對心理健康章節之份量',datetime('now')),
('EV-2022-101','EV-2023-101','triggered_by','direct',1,'即無 CO，立委仍可能因個案輿論召開公聽會','並列原因：(a) 民間團體陳情；(b) 媒體報導；(c) 衛福部主動回應','CO 段落為公聽會召開直接依據之一',datetime('now')),
('EV-2022-102','EV-2024-102','triggered_by','direct',1,'學輔法修正主因為國內輔諮量能不足與民間／立委壓力，CRC CO 為加速因素','並列原因：(a) 諮商心理師公會聯合聲明；(b) 大專校院輔導需求暴增；(c) 縣市輔諮中心人力 83% 達成率瓶頸','CO 對師生比修正提供國際標準依據',datetime('now')),
('EV-2023-101','EV-2023-102','triggered_by','direct',1,'即無公聽會，衛福部仍可能基於青壯自殺率推青年方案','並列原因：(a) 自殺率連 5 年上升；(b) 民間呼籲心理諮商可近性；(c) 行政院預算決策','公聽會強化方案編列正當性',datetime('now')),
('EV-2023-102','EV-2024-101','implements','direct',1,'年齡擴大至 45 歲為政策內生擴張，未必反映 CO 要求','並列原因：(a) 第一年試辦量能評估；(b) 青壯失業／經濟壓力；(c) 民代擴大要求','屬同一政策路線之延伸',datetime('now')),
('EV-2024-102','EV-2025-101','parallels','indirect',2,'韌性計畫架構於 2024 年中即已研擬，與學輔法修正屬不同部會路徑','並列原因：(a) 第二期國民心理健康計畫到期；(b) 跨部會整合需求；(c) 預算週期','兩條政策軌道平行而非因果',datetime('now'));

-- =========================================================================
-- 四、結果指標（每筆含混淆變項）
-- =========================================================================
INSERT OR REPLACE INTO outcome_indicator (indicator_id, event_id, indicator_type, metric_name, before_value, before_year, after_value, after_year, direction, measurement_method, source_url, confounders, note) VALUES
('IND-201','EV-2019-102','statistic','15-24 歲自殺死亡人數','210','2018','257','2019','worsened','衛福部死因統計','https://dep.mohw.gov.tw/domhaoh/fp-4904-8883-107.html','混淆變項：(a) 通報率提升；(b) 社群媒體普及；(c) 家庭結構變化；(d) 經濟景氣','單年增 22.4%'),
('IND-202','EV-2024-101','statistic','青少年自殺率（每 10 萬）','4.5','2021','7.0','2023','worsened','衛福部死因統計／OECD 比較','https://www.cna.com.tw/news/ahel/202504020134.aspx','混淆變項：(a) COVID-19 後遺；(b) 數位使用；(c) 學業壓力；(d) OECD 平均同期亦上升','2023 已超過 OECD 6.5'),
('IND-203','EV-2014-101','statistic','15-19 歲自殺率（每 10 萬）','2.6','2012','5.4','2022','worsened','衛福部死因統計','https://news.pts.org.tw/article/587767','混淆變項：(a) 學輔法效果之滯後；(b) 通報文化改變；(c) 同期 OECD 多國同向上升','10 年增近一倍'),
('IND-204','EV-2024-102','law','大專專輔人員師生比','1200:1','2014','900:1','2024','improved','學生輔導法第 4 條','https://udn.com/news/story/6885/8392971','混淆變項：(a) 員額是否到位仍待追蹤；(b) 縣市輔諮中心 83% 達成率；(c) 師生比為法定上限非實際配置','2024-12 修正公布'),
('IND-205','EV-2025-101','statistic','心理健康政策投入（6 年）','—','—','56.3 億','2025-2030','improved','行政院核定計畫','https://www.ey.gov.tw/Page/5A8A0CB5B41DA11E/8e8835ef-5b07-4e02-8b19-906b6964a10c','混淆變項：(a) 跨部會分配；(b) 兒少專屬比例待釐清；(c) 執行率歷年落差','屬投入端指標非結果端');
