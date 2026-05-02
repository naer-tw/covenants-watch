-- 健康權議題 trace seed (ICESCR Art.12，排除已建之兒少自殺)

INSERT OR REPLACE INTO actor (actor_id, actor_type, name, affiliation, position_spectrum, active_period, is_anonymized) VALUES
('A801','govt_agency','衛福部國民健康署','行政院','公衛派','持續',0),
('A802','govt_agency','衛福部中央健康保險署','行政院','公衛派','持續',0),
('A803','govt_agency','衛福部疾病管制署','行政院','公衛派','持續',0),
('A804','govt_agency','衛福部長期照顧司','行政院','公衛派','持續',0),
('A805','govt_agency','法務部（毒品防制業務）','行政院','公衛派','持續',0),
('A806','govt_agency','內政部警政署（毒品執法）','行政院','公衛派','持續',0),
('A807','govt_agency','教育部學特司（藥物濫用防制）','行政院','公衛派','持續',0),
('A808','ngo','董氏基金會','民間','公衛派','持續',0),
('A809','ngo','台灣醫療改革基金會','民間','公衛派','持續',0),
('A810','ngo','台灣拒菸聯盟','民間','公衛派','持續',0),
('A811','industry_assoc','加熱菸／電子煙產業團體','民間','經濟產業派','持續',0),
('A812','ngo','台灣人權促進會（防疫人權）','民間','個人權利派','持續',0),
('A813','ngo','醫療藥物使用者權益團體','民間','個人權利派','持續',0),
('A814','ngo','全國教師會／國教行動聯盟（校園藥物）','民間','公衛派','持續',0),
('A815','ngo','長照家屬／病友自助團體','民間','個人權利派','持續',0),
('A816','committee_member','CESCR 審查委員會（健康權章）','聯合國','公衛派','2022',0);

INSERT OR REPLACE INTO event (event_id, event_date, event_type, issue_tags, actor_id, title, summary, source_url, related_pi, related_co, related_article, is_positive_outcome, created_at) VALUES
('EV-2009-801','2009-12-10','legislation','["健康權"]','A816','兩公約施行法生效，健康權內國法化','ICESCR 第 12 條經施行法引入內國法體系，並依 GC14 認定健康權包含可獲得性／可近性／可接受性／品質四要素','https://covenantswatch.org.tw/iccpr-icescr/','["PI-01"]','[]','["ICESCR-12"]',1,datetime('now')),
('EV-2009-802','2009-01-23','legislation','["菸害"]','A801','菸害防制法第二次大修上路','室內公共場所全面禁菸、菸品稅捐調升、菸盒警示圖文 35%','https://www.hpa.gov.tw/Pages/List.aspx?nodeid=4721','["PI-11"]','[]','["ICESCR-12"]',1,datetime('now')),
('EV-2013-803','2013-01-01','govt_response','["健保"]','A802','二代健保上路：補充保費與財務永續改革','健保財源由薪資為主改採經常性所得＋6 類補充保費','https://www.nhi.gov.tw/ch/cp-2841-baaa2-3150-1.html','["PI-11"]','[]','["ICESCR-12"]',1,datetime('now')),
('EV-2017-804','2017-06-03','govt_response','["長照"]','A804','長照 2.0 全面上路：ABC 三級服務體系','從 1.0 機構式擴大為社區整合（A）／複合式（B）／巷弄站（C）','https://1966.gov.tw/LTC/cp-6572-85008-207.html','["PI-11"]','[]','["ICESCR-12"]',1,datetime('now')),
('EV-2020-805','2020-02-25','legislation','["疫情","健康權"]','A803','《嚴重特殊傳染性肺炎防治及紓困振興特別條例》通過','邊境管制、居家隔離、口罩配售、手機定位追蹤等措施引發法源依據與比例原則爭議','https://www.twreporter.org/a/prevention-and-control-covid-19-policies-violate-human-rights-law-issue-1','["PI-11"]','[]','["ICESCR-12","ICCPR-9","ICCPR-12"]',NULL,datetime('now')),
('EV-2021-806','2021-07-19','govt_response','["疫情","疫苗"]','A803','高端疫苗 EUA 通過程序爭議','食藥署於解盲日同步公告審查標準，名單與會議過程不公開，引發 ICESCR 健康權「可接受性／資訊透明」面向質疑','https://covid19.nctu.edu.tw/article/12678','["PI-11"]','[]','["ICESCR-12"]',NULL,datetime('now')),
('EV-2022-807','2022-05-13','co_paragraph','["健康權"]','A816','兩公約第三次審查 92 點 CO（健康權章）','國際審查委員就健康權提出多項建議，含長照給付公平、心理衛生、傳染病期間人權平衡與健康資訊近用','https://covenantswatch.org.tw/2021-third-review-on-iccpr-and-icescr/','["PI-03"]','["CO-3"]','["ICESCR-12"]',NULL,datetime('now')),
('EV-2023-808','2023-03-22','legislation','["菸害"]','A801','菸害防制法新法施行：禁電子煙、加熱菸納健康風險評估','全面禁類菸品、加熱菸採「健康風險評估審查制」、吸菸年齡提升至 20 歲、警示圖文擴至 50%','https://www.mohw.gov.tw/cp-16-74078-1.html','["PI-11"]','[]','["ICESCR-12"]',1,datetime('now')),
('EV-2024-809','2024-11-20','govt_response','["毒駕","校園菸毒"]','A806','毒品唾液快篩執法上路','攔檢現場唾液快篩，陽性後血液／尿液二層確認；拒測罰 18 萬','https://www.cna.com.tw/news/ahel/202511200071.aspx','["PI-11"]','[]','["ICESCR-12","ICCPR-17"]',NULL,datetime('now')),
('EV-2025-810','2025-01-01','govt_response','["長照"]','A804','長照 2.0 擴及青壯年失智 / 啟動長照 3.0 籌備','服務對象擴大、整合醫療長照、強化家庭支持','https://1966.gov.tw/LTC/cp-6572-85008-207.html','["PI-11"]','[]','["ICESCR-12"]',1,datetime('now')),
('EV-2025-811','2025-11-17','public_opinion','["菸害","校園"]','A810','NGO 籲全面下架加味菸品，質疑加熱菸成兒少入口','民團指 4 成青少年使用加味菸品','https://www.chinatimes.com/realtimenews/20251117002300-260405','["PI-11"]','[]','["ICESCR-12"]',NULL,datetime('now')),
('EV-2026-812','2026-03-01','legislation','["健保"]','A802','健保補充保費修法爭議：年領 2 萬即課徵之提案暫緩','行政院因社會反彈暫緩補充保費年度累計新制','https://money.udn.com/money/story/124512/9121255','["PI-11"]','[]','["ICESCR-12"]',NULL,datetime('now'));

INSERT INTO causal_link (from_event, to_event, link_type, evidence_strength, chain_depth, counter_evidence, multi_causal_note, note, created_at) VALUES
('EV-2009-801','EV-2009-802','triggered_by','indirect',1,'禁菸主張在 2009 之前已由 WHO FCTC（2003 簽署）推動','並列原因：(a) 國際公衛趨勢；(b) 國內倡議；(c) 司法判決','GC14 為比例原則基礎',datetime('now')),
('EV-2009-802','EV-2023-808','parallels','direct',2,'產業團體主張新型菸品屬「減害替代」，與傳統紙菸性質不同','並列原因：(a) 國際 WHO FCTC；(b) 國內公衛倡議；(c) 兒少入口風險','禁菸邏輯延伸至新型菸品',datetime('now')),
('EV-2017-804','EV-2025-810','triggered_by','direct',2,'部分研究指 2.0 已使長照給付人次成長 5 倍以上，3.0 是延伸而非彌補','並列原因：(a) 高齡化；(b) 失智症數成長；(c) 跨部會整合需求','服務缺口推動 3.0',datetime('now')),
('EV-2020-805','EV-2021-806','parallels','contested',1,'高端 EUA 在當時供應斷鏈下屬合理變通；亦有公衛專家指 PCR/隔離決策有 CDC 既有 SOP','並列原因：(a) 疫情緊急；(b) 行政決策慣性；(c) 國際比較','疫情期間之資訊透明缺口',datetime('now')),
('EV-2022-807','EV-2026-812','triggered_by','contested',2,'行政院暫緩主要考量為輿論與選舉因素，與 ICESCR 結論性意見之直接連動有限','並列原因：(a) 社會反彈；(b) 政治考量；(c) 財政學者意見','CO 與政治決定之間接關聯',datetime('now')),
('EV-2024-809','EV-2025-811','triggered_by','direct',1,'唾液快篩偽陽性率高於血液檢測，貿然導入校園恐造成標籤化','並列原因：(a) 毒駕新制執法；(b) 校園藥物防制需求；(c) NGO 倡議','政策延伸至校園',datetime('now')),
('EV-2009-801','EV-2020-805','triggered_by','indirect',2,'傳染病防治法本即提供緊急權限，兩公約僅是宣示性框架','並列原因：(a) 傳染病防治法；(b) 緊急行政需求；(c) 比例原則檢視','兩公約為規範背景',datetime('now'));

INSERT OR REPLACE INTO outcome_indicator (indicator_id, event_id, indicator_type, metric_name, before_value, before_year, after_value, after_year, direction, measurement_method, source_url, confounders, note) VALUES
('IND-801','EV-2023-808','statistic','青少年（國中）電子煙使用率','6.6','2021','8.0+','2024','worsened','國健署青少年吸菸行為調查','https://news.pts.org.tw/article/686460','混淆變項：(a) 執法力度；(b) 校園端落差；(c) 加味菸品流通','菸防新法施行後一年仍見上升'),
('IND-802','EV-2013-803','statistic','健保涵蓋率','99.9','2013','99.9','2025','unchanged','健保署統計','https://www.nhi.gov.tw/','可近性高 vs 永續性低之張力未解','長期高點維持'),
('IND-803','EV-2017-804','statistic','長照 2.0 服務涵蓋率','35','2017','78','2024','improved','衛福部長照司','https://1966.gov.tw/LTC/cp-6572-85008-207.html','官方統計，3.0 目標推進至 90%；NGO 指實際使用體感與數字落差','正面進展'),
('IND-804','EV-2024-809','case','毒駕拒測率／陽性率','—','2023','待 2025 年底揭露','2025','contested','警政署統計','https://www.npa.gov.tw/','需追蹤陽性對應血液確認比例與兒少占比','偽陽性風險');
