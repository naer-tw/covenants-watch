-- 移工議題 trace seed (ICESCR Art.6/7 + ICCPR Art.8)

INSERT OR REPLACE INTO actor (actor_id, actor_type, name, affiliation, position_spectrum, active_period, is_anonymized) VALUES
('A401','ngo','台灣國際勞工協會 TIWA','民間','移工權益寬鬆派／結構批判','1999-現在',0),
('A402','ngo','移工聯盟 MENT','民間','移工權益寬鬆派','2003-現在',0),
('A403','ngo','桃園市產業總工會','民間','勞工團結／在地申訴','2000-現在',0),
('A404','ngo','外籍漁工人權保障聯盟','民間','遠洋漁工權益寬鬆派','2018-現在',0),
('A405','ngo','人權公約施行監督聯盟','民間','人權監督中性記錄者','2009-現在',0),
('A406','industry_assoc','工商團體（產業／長照雇主代表聯合）','資方','成本效率嚴格派','持續',0),
('A407','govt_agency','勞動部勞動力發展署','行政院','政策執行','2014-現在',0),
('A408','govt_agency','行政院農業部漁業署','行政院','政策執行（遠洋漁工）','2018-現在',0),
('A409','govt_agency','內政部移民署（失聯移工專案）','行政院','政策執行','持續',0),
('A410','committee_member','兩公約國際審查委員會（移工章節）','聯合國體系專家','國際標準','2013-現在',0),
('A411','govt_agency','監察院／國家人權委員會（移工議題）','獨立監督','人權問責','2020-現在',0),
('A412','intl_actor','美國國務院（TIP Report／DOL 強迫勞動清單）','外國政府','國際問責','持續',0),
('A413','legislator','立法院社會福利及衛生環境委員會','立法院','跨黨派','持續',0);

INSERT OR REPLACE INTO event (event_id, event_date, event_type, issue_tags, actor_id, title, summary, source_url, related_pi, related_co, related_article, is_positive_outcome, created_at) VALUES
('EV-2013-401','2013-03-01','co_paragraph','["移工"]','A410','兩公約第一次審查 CO（移工章）','要求檢討家事勞工、漁工排除於勞基法外之合理性，並關注強制體檢、限制轉換雇主與人身自由','https://covenantswatch.org.tw/','["PI-02"]','["CO-1"]','["ICESCR-6","ICESCR-7","ICCPR-8"]',NULL,datetime('now')),
('EV-2017-401','2017-01-20','co_paragraph','["移工"]','A410','兩公約第二次審查 CO §69 §70','§69：強烈建議將所有移工納入勞基法保障；§70：應廢除（abolish）私人就業仲介制度','https://covenantswatch.org.tw/','["PI-02"]','["CO-2-§69","CO-2-§70"]','["ICESCR-6","ICESCR-7","ICCPR-8"]',NULL,datetime('now')),
('EV-2018-401','2018-06-28','intl_actor','["移工","漁工"]','A412','美國 TIP Report 首次點名台灣遠洋漁船強迫勞動','列出 ILO 11 項強迫勞動指標：扣留證件、限制行動、超時工作、暴力、苛扣薪資','https://www.twreporter.org/i/slave-fishermen-human-trafficking-gcs','["PI-13"]','["CO-2"]','["ICCPR-8"]',0,datetime('now')),
('EV-2020-401','2020-09-30','intl_actor','["移工","漁工"]','A412','美國 DOL 將我國遠洋漁獲首列「童工及強迫勞動製品清單」','遠洋漁工長工時、扣證件、苛扣薪資情形未改善','https://www.cy.gov.tw/News_Content.aspx?n=125&s=20285','["PI-13"]','["CO-2"]','["ICCPR-8"]',0,datetime('now')),
('EV-2021-401','2021-05','public_opinion','["移工"]','A402','移工聯盟訴求《家事服務法》 17 年躺立院','工人版草案 2004 年提出，至 2021 年仍卡關；勞動部稱「社會共識不足」推動專法困難','https://www.cna.com.tw/news/ahel/202105020153.aspx','["PI-12"]','["CO-2"]','["ICESCR-6","ICESCR-7"]',0,datetime('now')),
('EV-2022-401','2022-05-13','co_paragraph','["移工"]','A410','兩公約第三次審查 CO（移工段）','再次要求：家事與漁業移工納入勞基法、檢討仲介制度、強制體檢應符 ICESCR Art.12，第三次連續提出','https://covenantswatch.org.tw/2021-third-review-on-iccpr-and-icescr/','["PI-03"]','["CO-3"]','["ICESCR-6","ICESCR-7","ICCPR-8"]',NULL,datetime('now')),
('EV-2023-401','2023-09','outcome','["移工"]','A411','監察院 300 頁失聯移工調查報告','失聯移工 2023 年底達 8.6 萬人新高，列出仲介剝削、轉換雇主限制等 10 大根源','https://rightplus.org/2023/09/08/migrant-worker/','["PI-12"]','["CO-3"]','["ICESCR-7","ICCPR-8"]',0,datetime('now')),
('EV-2023-402','2023-05-30','legislation','["移工"]','A413','《就業服務法》第 46 條修正：80 歲以上長者免巴氏量表','放寬聘僱家庭看護工門檻；同次修法未處理移工自由轉換雇主之 §53 限制','https://news.pts.org.tw/article/731370','["PI-12"]','["CO-3"]','["ICESCR-6"]',1,datetime('now')),
('EV-2024-401','2024-01-15','intl_actor','["移工","漁工"]','A412','美國 TIP Report 第三度將台灣遠洋漁獲列強迫勞動清單','明指「政府調查人力與規定不足，持續阻礙鑑別、調查與起訴」','https://udn.com/news/story/7269/8211015','["PI-13"]','["CO-3"]','["ICCPR-8"]',0,datetime('now')),
('EV-2024-402','2024-07','govt_response','["移工"]','A407','印尼「零付費」政策對台延後實施／擴大產業移工配額','原 2024-01-15 上路延至 07-15；同期增加引進印度移工 MOU 簽署','https://www.cw.com.tw/article/5114219','["PI-12"]','["CO-3"]','["ICESCR-6","ICESCR-7"]',NULL,datetime('now')),
('EV-2024-403','2024-11','govt_response','["移工"]','A407','勞動部優化跨國轉換雇主線上平台','建立線上轉換系統，研擬禁止雇主與仲介扣留證件之條文','https://www.mol.gov.tw/','["PI-12"]','["CO-3"]','["ICESCR-7","ICCPR-8"]',1,datetime('now')),
('EV-2025-401','2025-06-02','outcome','["移工"]','A409','失聯移工年增首見下降 / 累計仍逾 9 萬','2024 新增失聯 25,773 人較前年減 5,783 人；累計失聯尚未出境者仍逾 9 萬','https://www.careforyou.com.tw/post/2025-06-02-01','["PI-12","PI-13"]','["CO-3"]','["ICESCR-7","ICCPR-8"]',NULL,datetime('now'));

INSERT INTO causal_link (from_event, to_event, link_type, evidence_strength, chain_depth, counter_evidence, multi_causal_note, note, created_at) VALUES
('EV-2013-401','EV-2017-401','parallels','contested',1,'CO-1 至 CO-2 之間勞動部曾推動家事勞工保障法草案，並非完全未動','並列原因：(a) 國內 NGO 倡議；(b) 人口販運報告壓力；(c) 工商團體反對使政院版難出爐','CO-1 之要求未獲實質回應導致 CO-2 加重力道',datetime('now')),
('EV-2017-401','EV-2021-401','triggered_by','indirect',2,'家事服務法卡關主因為勞雇實務型態爭議與工商團體反對，CO §69 §70 為國際背景','並列原因：(a) 工商團體強調 24 小時照護不適用工時規範；(b) 預算成本；(c) 移工團體版本與政府版本落差','CO §69 §70 為民間倡議論述提供國際標準依據',datetime('now')),
('EV-2018-401','EV-2020-401','triggered_by','direct',1,'TIP 至 DOL 清單為兩個獨立程序，但 ILO 11 指標未改善為共同基礎','並列原因：(a) 民間調查報告累積；(b) 國際漁業 NGO 倡議；(c) 美國國內供應鏈合規壓力','TIP 連年未改善累積成入清單條件',datetime('now')),
('EV-2020-401','EV-2022-401','parallels','indirect',2,'第三次 CO 涉及多軌議題，遠洋漁工僅其中一支','並列原因：(a) 國家人權委員會 2020 成立後獨立評估；(b) 民間影子報告；(c) 國際 NGO 證詞','美方清單列入提升 CO 對 ICCPR-8 章節之關注',datetime('now')),
('EV-2022-401','EV-2023-401','triggered_by','direct',1,'即無 CO，監察院仍可依其職權對失聯移工率新高發動調查','並列原因：(a) 失聯人數連年破紀錄；(b) 媒體深度報導；(c) 立委質詢','CO 為調查報告援引之國際標準依據之一',datetime('now')),
('EV-2023-401','EV-2024-403','triggered_by','indirect',2,'線上轉換平台政策路線早於 2022 年即在規劃，監院報告為加速因素','並列原因：(a) 1955 專線申訴累積；(b) 印尼來源國壓力；(c) 數位治理計畫','監院報告強化勞動部加速時程之正當性',datetime('now')),
('EV-2024-401','EV-2024-403','parallels','contested',1,'禁止扣留證件條文研擬與 TIP 報告同步，難判斷直接因果；遠洋漁工管理屬漁業署非勞發署','並列原因：(a) 國際供應鏈合規；(b) 國內 NGO 倡議；(c) 跨部會壓力','TIP 為政策時程外部壓力之一',datetime('now')),
('EV-2024-402','EV-2025-401','triggered_by','direct',1,'失聯減少亦可能受查緝面影響，非單純來源國政策貢獻','並列原因：(a) 印度移工 MOU；(b) 印尼配額調整；(c) 越南仲介費高漲使來台誘因下降','來源國管理直接影響新進與失聯流量',datetime('now'));

INSERT OR REPLACE INTO outcome_indicator (indicator_id, event_id, indicator_type, metric_name, before_value, before_year, after_value, after_year, direction, measurement_method, source_url, confounders, note) VALUES
('IND-401','EV-2023-401','statistic','失聯移工累計人數','52000','2019','86352','2023','worsened','移民署統計','https://rightplus.org/2023/09/08/migrant-worker/','混淆變項：(a) 引進總量擴大；(b) 通報定義；(c) 來源國政策；(d) 仲介費高漲','2023 為史上新高'),
('IND-402','EV-2017-401','law','家事移工納入勞基法之進度','未納入','2017','未納入','2026','unchanged','勞基法施行細則','https://www.mol.gov.tw/announcement/27179/16779/','混淆變項：(a) 工商團體反對；(b) 24 小時照護工時計算困難；(c) 家事服務法替代路徑','**CO §69 連續三屆未實現**'),
('IND-403','EV-2017-401','law','私人就業仲介廢除進度','存續','2017','存續（轉直聘為輔）','2026','unchanged','就業服務法第 34 條','https://fw.wda.gov.tw/','混淆變項：(a) 直聘中心使用率低；(b) 仲介產業遊說；(c) 來源國仲介結構','**CO §70「廢除」目標未達**'),
('IND-404','EV-2024-401','case','美國 DOL 強迫勞動清單入列次數','0','2019','3','2024','worsened','美國勞工部清單','https://udn.com/news/story/7238/8212146','混淆變項：(a) 美方查核強度；(b) 國際漁業治理變化；(c) 我國通報透明度','遠洋漁獲三度入列');
