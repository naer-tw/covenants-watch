-- 言論自由議題 trace seed (ICCPR Art.19)
-- 媒體匿名化（個案 1/2/3）

INSERT OR REPLACE INTO actor (actor_id, actor_type, name, affiliation, position_spectrum, active_period, is_anonymized) VALUES
('A501','govt_agency','NCC 國家通訊傳播委員會','獨立機關','監管派','持續',0),
('A502','govt_agency','行政院（言論自由議題）','行政院','支持監管派','持續',0),
('A503','legislator','立法院（多數黨團）','立法院','支持監管派','持續',0),
('A504','court','司法院憲法法庭（言論自由議題）','司法院','權利審查派','持續',0),
('A505','court','台北高等行政法院','司法院','司法審查派','持續',0),
('A506','ngo','媒體改造學社','民間','結構改革派','2003-現在',0),
('A507','ngo','台灣新聞記者協會','民間','新聞自由派','持續',0),
('A508','ngo','卓越新聞獎基金會','民間','自律優先派','持續',0),
('A509','intl_actor','無國界記者組織 RSF','國際 NGO','新聞自由派','持續',0),
('A510','intl_actor','Freedom House','國際 NGO','權利監督派','持續',0),
('A511','committee_member','UN 人權事務委員會（GC34 制定）','聯合國','條約機構','2011',0),
('A512','committee_member','兩公約第三次國際審查委員會（言論自由章）','聯合國體系','條約審查','2022',0),
('A513','private_media','個案媒體 1（2020 不予換照案）','私部門','受處分方','持續',1),
('A514','private_media','個案媒體 2','私部門','受處分方','持續',1),
('A515','private_media','個案媒體 3','私部門','受處分方','持續',1),
('A516','ngo','台灣事實查核中心','民間','自律派','2018-現在',0);

INSERT OR REPLACE INTO event (event_id, event_date, event_type, issue_tags, actor_id, title, summary, source_url, related_pi, related_co, related_article, is_positive_outcome, created_at) VALUES
('EV-2011-501','2011-07-21','co_paragraph','["言論自由"]','A511','UN 人權委員會通過 GC 34','對 ICCPR Art.19 採嚴格詮釋：限制須由法律明定、針對 19(3)(a)(b) 列舉目的、符合必要性與比例原則','https://www.ohchr.org/en/documents/general-comments-and-recommendations/general-comment-no34-article-19-freedoms-opinion-and','["PI-09"]','[]','["ICCPR-19"]',1,datetime('now')),
('EV-2017-502','2017-01-20','co_paragraph','["言論自由","媒體多元"]','A512','兩公約第二次審查結論性意見（媒體章）','建議政府採取預防措施，避免新聞台與報社併購使公眾資訊傳播被過度集中','https://www.humanrights.moj.gov.tw/','["PI-09"]','["CO-2"]','["ICCPR-19"]',NULL,datetime('now')),
('EV-2019-503','2019-12-31','legislation','["言論自由","反滲透"]','A503','反滲透法三讀通過','立法院以 67:4 三讀通過，2020/1/15 公布、2020/1/17 施行','https://zh.wikipedia.org/zh-hk/反滲透法','["PI-09"]','[]','["ICCPR-19"]',NULL,datetime('now')),
('EV-2020-504','2020-11-18','govt_response','["言論自由","媒體換照"]','A501','2020 重大媒體換照爭議（個案 1 不予換照）','NCC 委員一致決議不予換照，理由為違反查證原則累積處分','','["PI-09"]','[]','["ICCPR-19"]',NULL,datetime('now')),
('EV-2022-505','2022-05-13','co_paragraph','["言論自由"]','A512','兩公約第三次審查 92 點 CO（言論自由章）','委員續關切媒體多元、查證義務與假訊息治理之比例原則衝突','https://ncsd.ndc.gov.tw/Fore/News_detail/adb28de6-6a37-4cb6-83f8-eecd05112c28','["PI-03"]','["CO-3"]','["ICCPR-19"]',NULL,datetime('now')),
('EV-2022-506','2022-05-03','intl_actor','["言論自由"]','A509','RSF 2022 方法論重大變更','改採五大面向（政治／法律／經濟／社會文化／安全），2022 起與 2021 以前不可直接比較','https://rsf.org/en/index-methodologie-2022','["PI-09"]','[]','["ICCPR-19"]',NULL,datetime('now')),
('EV-2022-507','2022-06-29','legislation','["言論自由","平台監管"]','A501','NCC 通過數位中介服務法草案','第 18 條等規定使主管機關可於法院裁定前要求平台對被指控不實訊息加註警示','https://zh.wikipedia.org/zh-hant/數位中介服務法爭議事件','["PI-09"]','[]','["ICCPR-19"]',0,datetime('now')),
('EV-2022-508','2022-08-20','govt_response','["言論自由"]','A502','行政院介入暫緩公聽會','行政院長指示 NCC 暫緩原訂 8/25 公聽會；總統公開重申言論自由為憲法權利','','["PI-09"]','[]','["ICCPR-19"]',1,datetime('now')),
('EV-2022-509','2022-09-07','govt_response','["言論自由"]','A501','NCC 撤回數位中介法草案','NCC 宣布全案退回內部工作小組重議，無重新提出時程','','["PI-09"]','[]','["ICCPR-19"]',1,datetime('now')),
('EV-2023-510','2023-05-26','court_ruling','["言論自由","媒體換照"]','A505','高等行政法院撤銷 2020 不予換照處分','撤銷原處分但同時駁回業者請求重新換照與賠償；命 NCC 依判決法律見解另為適法處分','https://udn.com/news/story/121744/7155917','["PI-09"]','[]','["ICCPR-19"]',NULL,datetime('now')),
('EV-2024-511','2024-12-31','intl_actor','["言論自由"]','A510','Freedom House 2024 評等','政治權利 38/40、公民自由 56/60、總分 94/100；網路自由 79/100','https://freedomhouse.org/country/taiwan/freedom-world/2024','["PI-09"]','[]','["ICCPR-19"]',1,datetime('now')),
('EV-2026-512','2026','co_paragraph','["言論自由"]','A512','第 4 屆兩公約國際審查啟動','審查預期再度關切平台監管比例原則 + 假訊息治理','','["PI-03"]','[]','["ICCPR-19"]',NULL,datetime('now'));

INSERT INTO causal_link (from_event, to_event, link_type, evidence_strength, chain_depth, counter_evidence, multi_causal_note, note, created_at) VALUES
('EV-2011-501','EV-2017-502','cites','indirect',1,'第二次審查結論並未直接引用 GC 34 條文編號','並列原因：各國比較法、媒體所有權集中之國際關注','GC 34 為規範依據而非直接觸發',datetime('now')),
('EV-2017-502','EV-2022-505','parallels','direct',1,'2017-2022 期間台灣媒體環境已有重大變化（換照爭議、平台立法）','並列原因：媒體環境變化、政治轉折、國際趨勢','議題持續性',datetime('now')),
('EV-2019-503','EV-2020-504','parallels','contested',1,'NCC 處分依據為《衛廣法》第 27 條查證義務，與反滲透法無直接法律連結','並列原因：(a) 個案違規紀錄累積自 2014；(b) NCC 委員會獨立決定；(c) 政治氛圍','時序相近但法律連結弱',datetime('now')),
('EV-2020-504','EV-2023-510','triggered_by','direct',2,'法院同時駁回復照與賠償，意味司法並未全面否定 NCC 立場','並列原因：(a) 行政訴訟程序；(b) 司法獨立審查；(c) 程序瑕疵認定','司法對行政裁量制衡',datetime('now')),
('EV-2022-507','EV-2022-508','triggered_by','direct',1,'行政院亦可能基於選舉考量而非單純人權考量介入','並列原因：(a) 公民團體強烈反彈；(b) 學界批評；(c) 跨黨派政治壓力；(d) 選舉時程','跨機關政治壓力',datetime('now')),
('EV-2022-508','EV-2022-509','triggered_by','direct',1,'NCC 表示係內部重議，未必等同放棄；無重啟時程亦不等同永久終止','並列原因：行政院政策決定、NCC 內部評估','行政院介入直接造成撤回',datetime('now')),
('EV-2011-501','EV-2022-507','contradicts','indirect',2,'支持方主張警示而非刪除，屬最低度干預，未必觸及 GC 34 紅線','並列原因：(a) GC 34 對事前限制之嚴格審查；(b) 批評者主張違反必要性與比例原則','數位中介法草案測試 GC 34 紅線',datetime('now')),
('EV-2022-506','EV-2024-511','parallels','direct',1,'方法論變更不影響 Freedom House，故跨指標比較仍部分可行；惟 RSF 序列須切段處理','並列原因：兩個獨立指標各有方法論','跨指標交叉驗證之必要',datetime('now'));

INSERT OR REPLACE INTO outcome_indicator (indicator_id, event_id, indicator_type, metric_name, before_value, before_year, after_value, after_year, direction, measurement_method, source_url, confounders, note) VALUES
('IND-501','EV-2024-511','statistic','Freedom House 公民自由分數','—','2013','56/60','2024','improved','Freedom House','https://freedomhouse.org/country/taiwan/freedom-world/2024','長期高分穩定，但內部分項對假訊息治理列警示','9 年穩定維持'),
('IND-502','EV-2024-511','statistic','Freedom House 政治權利分數','—','2013','38/40','2024','improved','Freedom House','https://freedomhouse.org/country/taiwan/freedom-world/2024','亞洲第二（次於日本 96）','長期高分'),
('IND-503','EV-2022-506','statistic','RSF 新聞自由排名（須分段讀）','47','2013','24','2025','improved','RSF（含方法論變更）','https://rsf.org/','**重要警告**：2022 方法論重大變更，2013-2021 序列與 2022-2024 序列須切段比較','跨方法論不可線性對比'),
('IND-504','EV-2020-504','case','NCC 對廣電查證義務裁罰件數','—','2014','累計集中於少數頻道','2023','contested','NCC 新聞稿彙整','https://www.ncc.gov.tw/','單一統計不能等同新聞自由倒退，需與處分理由比例原則交叉檢視','個別案件涉名譽風險，匿名處理');
