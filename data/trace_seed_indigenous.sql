-- 原住民族議題 trace seed (ICCPR Art.27 + ICESCR Art.15 + Art.1 自決權)
-- agent 蒐集（2026-05-01）
-- 注意：agent 使用了不同 schema 命名（actors / events / causal_links / outcome_indicators），改為符合本平台 schema

INSERT OR REPLACE INTO actor (actor_id, actor_type, name, affiliation, position_spectrum, active_period, is_anonymized, note) VALUES
('A601','govt_agency','原住民族委員會','行政院二級機關','漸進派','持續',0,'主管原住民族行政；負責諮商同意辦法'),
('A602','govt_agency','行政院人權及轉型正義處','行政院','漸進派','持續',0,'督辦兩公約落實之跨部會幕僚'),
('A603','govt_agency','總統府原住民族歷史正義與轉型正義委員會','總統府','漸進派','2016-現在',0,'2016 蔡英文道歉後設置'),
('A604','govt_agency','國家人權委員會（原民議題）','監察院','監督派','2020-現在',0,'撰寫獨立評估意見'),
('A605','ngo','原住民族青年陣線','民間','自決派','持續',0,'凱道部落運動主要組織者，主張 FPIC 絕對論'),
('A606','media','原住民族電視台 / 原文會','民間財團法人','自決派','持續',0,'TITV，原住民族文化事業基金會'),
('A607','ngo','原住民族 16 族聯合會（集合主體）','民間','自決派','持續',0,'含太魯閣、賽德克、撒奇萊雅等正名後族群代表組織'),
('A608','ngo','平埔族復振團體（集合主體）','民間','自決派','持續',0,'西拉雅、馬卡道、噶哈巫等族群復振團體'),
('A609','ngo','私有地主團體（集合主體）','民間','保留派','持續',0,'傳統領域劃設範圍內之非原民地主'),
('A610','legislator','立法院內政委員會（原民法案）','立法院','分歧','持續',0,'原基法、原住民族語言法等審議場域'),
('A611','court','憲法法庭（原民議題）','司法院','法理派','持續',0,'111 憲判 17 號西拉雅案合議庭'),
('A612','committee_member','兩公約國際審查委員會（原民章節）','聯合國體系專家','監督派','2013-現在',0,'歷屆來台審查之國際人權專家'),
('A613','intl_actor','聯合國原住民族常設論壇 (UNPFII)','UN ECOSOC','倡議派','持續',0,'台灣未獲席次但持續關注');

INSERT OR REPLACE INTO event (event_id, event_date, event_type, issue_tags, actor_id, title, summary, source_url, related_pi, related_co, related_article, is_positive_outcome, created_at) VALUES
('EV-2007-601','2007-09-13','co_paragraph','["原住民族","自決權"]','A613','UNDRIP 聯合國通過原住民族權利宣言','確立 FPIC、自決、文化權；台灣雖非會員，原民會 2008 年中譯','https://www.un.org/esa/socdev/unpfii/documents/DRIPS_zh.pdf','["PI-12"]','[]','["ICCPR-1","ICCPR-27","ICESCR-15"]',1,datetime('now')),
('EV-2013-602','2013-03-01','co_paragraph','["原住民族"]','A612','兩公約第一次國際審查 — 點名 FPIC 落差','首次審查結論性意見要求政府落實原基法 §21 諮商同意，並參酌 UNDRIP','https://www.president.gov.tw/Page/594','["PI-02"]','["CO-1-§76"]','["ICCPR-27","ICESCR-15"]',NULL,datetime('now')),
('EV-2016-603','2016-08-01','govt_response','["原住民族"]','A603','蔡總統代表政府向原住民族道歉','總統府成立歷史正義與轉型正義委員會，提出語言法、自治法、土海法、平埔正名等九項承諾','https://www.president.gov.tw/NEWS/20603','["PI-12"]','[]','["ICCPR-27"]',1,datetime('now')),
('EV-2017-604','2017-02-18','govt_response','["原住民族","傳統領域"]','A601','原民會公告諮商同意辦法 — 排除私有地','《原住民族土地或部落範圍土地劃設辦法》排除私有地，引爆團體反彈','https://eventsinfocus.org/issues/1814','["PI-12"]','["CO-1-§78"]','["ICCPR-27","ICESCR-15"]',0,datetime('now')),
('EV-2017-605','2017-02-23','public_opinion','["原住民族","集會"]','A605','凱道部落運動展開','原住民族團體在凱達格蘭大道紮營抗議諮商同意辦法排除私有地，後遭驅離至二二八公園，持續逾百日','https://zh.wikipedia.org/zh-hant/凱道部落','["PI-12"]','[]','["ICCPR-21","ICCPR-27"]',NULL,datetime('now')),
('EV-2017-606','2017-06-14','legislation','["原住民族","語言"]','A610','原住民族語言發展法施行 — 列為國家語言','正式承認 16 族語為國家語言，落實道歉文承諾之一','https://law.moj.gov.tw/LawClass/LawAll.aspx?pcode=D0130037','["PI-12"]','[]','["ICCPR-27","ICESCR-15"]',1,datetime('now')),
('EV-2017-607','2017-12-01','co_paragraph','["原住民族"]','A612','兩公約第二次審查 — CO §76/§78 升級','結論性意見再次點名 FPIC 程序不完備，並指諮商同意辦法限縮傳統領域違反公約精神','https://www.humanrights.moj.gov.tw/17725/17733/17745/17755/Nodelist','["PI-02"]','["CO-2-§76","CO-2-§78"]','["ICCPR-1","ICCPR-27"]',NULL,datetime('now')),
('EV-2019-608','2019-01-09','legislation','["原住民族","語言"]','A610','國家語言發展法公布施行','確立各固有族群自然語言一律平等，原民語、客語、台語、手語並列','https://www.moc.gov.tw/information_250_95831.html','["PI-12"]','[]','["ICCPR-27","ICESCR-15"]',1,datetime('now')),
('EV-2022-609','2022-05-13','co_paragraph','["原住民族"]','A612','兩公約第三次審查 — 92 點 CO 重申 §76','92 點結論性意見第三度要求修正諮商同意辦法、落實 FPIC、檢討傳統領域排除私有地','https://ncsd.ndc.gov.tw/Fore/News_detail/adb28de6-6a37-4cb6-83f8-eecd05112c28','["PI-03"]','["CO-3-§76"]','["ICCPR-1","ICCPR-27","ICESCR-15"]',NULL,datetime('now')),
('EV-2022-610','2022-10-28','court_ruling','["原住民族","平埔正名"]','A611','憲法法庭 111 憲判 17 號 — 西拉雅案','15 位大法官全體一致判《原住民身分法》§2 違憲，命 3 年內修法','https://www.cna.com.tw/news/ahel/202210280173.aspx','["PI-12"]','[]','["ICCPR-27"]',1,datetime('now')),
('EV-2025-611','2025-10-28','outcome','["原住民族","平埔正名"]','A610','身分法修法期限屆至 — 立法進度落後','憲判限期屆至，行政院修正草案在立法院僵局；平埔族正名仍未到位','https://www.twreporter.org/a/taiwan-aborigines-siraya-constitutional-interpretation','["PI-12"]','[]','["ICCPR-27"]',0,datetime('now')),
('EV-2026-612','2026-04-15','co_paragraph','["原住民族"]','A612','CO §76 第四度於審查中被重申（預期）','第四次兩公約審查預期再次點名 FPIC、傳統領域、平埔身分修法三項未竟事項','https://www.mofa.gov.tw/cp.aspx?n=2421','["PI-03"]','[]','["ICCPR-1","ICCPR-27"]',NULL,datetime('now'));

INSERT INTO causal_link (from_event, to_event, link_type, evidence_strength, chain_depth, counter_evidence, multi_causal_note, note, created_at) VALUES
('EV-2007-601','EV-2013-602','triggered_by','indirect',1,'台灣非聯合國會員，UNDRIP 對國內無直接拘束力；國家報告自願採行','並列原因：國內 NGO 倡議、國際比較標準、學界推動','UNDRIP 為規範依據而非直接強制',datetime('now')),
('EV-2013-602','EV-2016-603','triggered_by','indirect',2,'蔡英文道歉動因主要係 2016 政黨輪替轉型正義訴求','並列原因：(a) 政黨輪替；(b) 國內 NGO 倡議；(c) 個人政治承諾；CO §76 僅為次要外部依據','政治承諾為主因，CO 為背景',datetime('now')),
('EV-2016-603','EV-2017-604','implements','direct',1,'原民會主張排除私有地係考量地主財產權與行政可行性，並非違背道歉文承諾','並列原因：(a) 私有地主反對；(b) 行政可行性；(c) 司法可訴性風險','道歉文之具體政策落實',datetime('now')),
('EV-2017-604','EV-2017-605','triggered_by','direct',1,'部分族人團體支持原民會折衷立場，凱道團體不能代表全體族群共識','並列原因：(a) 政策不滿；(b) NGO 動員能力；(c) 媒體關注','直接觸發抗爭',datetime('now')),
('EV-2017-607','EV-2019-608','parallels','direct',1,'語言法之主要動因為文化部本位政策與蔡總統 2016 承諾，CO 為輔助理由','並列原因：政府本位政策、社會共識、跨黨派支持','CO 為背景而非觸發',datetime('now')),
('EV-2016-603','EV-2022-610','indirect','indirect',2,'西拉雅案於 2015 年已提起行政訴訟，路徑早於道歉文','並列原因：(a) 訴訟既存路徑；(b) 平埔復振動能；(c) 憲判審查依憲法非政治承諾','訴訟路徑獨立於政治承諾',datetime('now')),
('EV-2022-610','EV-2025-611','triggered_by','contested',2,'部分原住民團體（既存 16 族）反對全面開放平埔正名，立法僵局含實質爭議','並列原因：(a) 16 族與平埔族間之資源分配張力；(b) 行政院草案爭議；(c) 立法院黨團協商','非單純行政怠惰',datetime('now')),
('EV-2022-609','EV-2026-612','parallels','direct',1,'若 2025-2026 完成諮商同意辦法修正並通過自治法，CO §76 將不再列為 follow-up','並列原因：CO 議題延續性、政策進度落後','13 年來未實質改善',datetime('now'));

INSERT OR REPLACE INTO outcome_indicator (indicator_id, event_id, indicator_type, metric_name, before_value, before_year, after_value, after_year, direction, measurement_method, source_url, confounders, note) VALUES
('IND-601','EV-2017-606','statistic','已正名原住民族族數','9','2001','16','2024','improved','原民會公告','https://www.cip.gov.tw/','並非全部 16 族在兩公約期間正名（撒奇萊雅 2007、賽德克 2008 已早於施行法），混淆變項：歷史運動累積、政治意願、法律訴訟','正面進展但部分歸功於施行法之前歷史'),
('IND-602','EV-2017-604','statistic','傳統領域涵蓋面積','約 80 萬公頃公有地','2017','約 80 萬公頃（含私有地之完整 180 萬公頃版本未實現）','2025','unchanged','原民會公告','https://eventsinfocus.org/issues/1814','混淆變項：(a) 私有地主反對；(b) 行政訴訟風險；(c) 跨族群共識','**抗爭 8 年仍卡關**'),
('IND-603','EV-2019-608','statistic','族語認證合格教師人數','約 2,300','2017','約 4,100','2024','improved','教育部統計','https://www.moc.gov.tw/','混淆變項：(a) 教育部本位政策；(b) 族語復振動能；(c) 經費投入','正面進展之少數案例'),
('IND-604','EV-2025-611','law','平埔族取得原民身分法定路徑（憲判後修法）','無','2022','立法僵局，未完成','2025','unchanged','立法院議事系統','https://www.twreporter.org/','混淆變項：16 族與平埔族間資源分配張力','**憲判 3 年期限將屆**');
