-- 教育權議題 trace seed (ICESCR Art.13 + 父母教育選擇權 + ICCPR 18-4)

INSERT OR REPLACE INTO actor (actor_id, actor_type, name, affiliation, position_spectrum, active_period, is_anonymized) VALUES
('A701','govt_agency','教育部','行政院','國家義務派','持續',0),
('A702','govt_agency','行政院性別平等處','行政院','性別推動派','持續',0),
('A703','legislator','立法院教育及文化委員會','立法院','分歧','持續',0),
('A704','govt_agency','中央選舉委員會','獨立機關','程序派','持續',0),
('A705','ngo','下一代幸福聯盟','民間','家長 opt-out 派 / 嚴格派','2013-現在',0),
('A706','ngo','台灣性別平等教育協會','民間','性別推動派','持續',0),
('A707','ngo','全國家長團體聯盟','民間','選擇權派','持續',0),
('A708','ngo','國教行動聯盟','民間','選擇權派','2012-現在',0),
('A709','ngo','台灣實驗教育推動中心','民間','選擇權派','持續',0),
('A710','ngo','人權公約施行監督聯盟（教育權）','民間','國家義務派','2009-現在',0),
('A711','committee_member','兩公約第三次審查國際委員會（教育章）','聯合國體系','監督派','2022',0),
('A712','public','高所得家長／國際學校族群','民間','exit option 階級','持續',0);

INSERT OR REPLACE INTO event (event_id, event_date, event_type, issue_tags, actor_id, title, summary, source_url, related_pi, related_co, related_article, is_positive_outcome, created_at) VALUES
('EV-2009-701','2009-12-10','legislation','["教育權"]','A703','兩公約施行法生效，教育權正式內國法化','ICESCR Art.13 經施行法引入內國法體系','https://law.moj.gov.tw/LawClass/LawAll.aspx?pcode=I0020028','["PI-01"]','[]','["ICESCR-13","ICCPR-18-4"]',1,datetime('now')),
('EV-2014-702','2014-11-19','legislation','["教育權","選擇權"]','A703','實驗教育三法三讀','「家長教育選擇權」首次完整法制化（公辦民營/學校型態/非學校型態三軌）','https://www.ey.gov.tw/Page/5A8A0CB5B41DA11E/d0f42a96-289c-4bb2-8c1a-87575a998a50','["PI-16"]','[]','["ICESCR-13-3","CRC-28","CRC-29"]',1,datetime('now')),
('EV-2014-703','2014-11-20','legislation','["教育權"]','A703','兒童權利公約施行法生效','CRC 28/29 與 ICESCR 並行','https://law.moj.gov.tw/LawClass/LawAll.aspx?pcode=D0050193','["PI-01"]','[]','["CRC-28","CRC-29","ICESCR-13"]',1,datetime('now')),
('EV-2018-704','2018-11-24','public_opinion','["性平教育","選擇權"]','A704','公投第 11 案通過：國民教育階段不得實施性平法施行細則所定「同志教育」','宗教與家長團體主導；性平倡議方則認損及學生平等受教權','','["PI-10","PI-16"]','[]','["ICESCR-13-3","ICCPR-18-4"]',NULL,datetime('now')),
('EV-2019-705','2019-08-01','govt_response','["教育權"]','A701','108 課綱施行','議題融入、選修擴大、自主學習','https://www.naer.edu.tw/PageSyllabus?fid=52','["PI-16"]','[]','["ICESCR-13","CRC-29"]',1,datetime('now')),
('EV-2019-706','2019-04-02','govt_response','["性平教育"]','A701','性平法施行細則第 13 條修正','刪「同志教育」字樣，新增「認識尊重不同性傾向/性別認同」','https://www.thenewslens.com/article/116403','["PI-10","PI-16"]','[]','["ICESCR-13-3","ICCPR-18-4"]',NULL,datetime('now')),
('EV-2019-707','2019-04','public_opinion','["性平教育"]','A705','反同/挺同雙方均不滿意修法（換湯不換藥 vs 違反公投）','行政技術調整使雙方陣營皆認立場未受尊重','','["PI-10","PI-16"]','[]','["ICCPR-18-4","ICESCR-13-3"]',NULL,datetime('now')),
('EV-2022-708','2022-05-13','co_paragraph','["教育權"]','A711','兩公約第三次審查 CO（教育章）','涉教育權多項建議，含家長教育選擇權之爭議','https://covenantswatch.org.tw/2021-third-review-on-iccpr-and-icescr/','["PI-03"]','["CO-3"]','["ICESCR-13","ICCPR-18-4"]',NULL,datetime('now')),
('EV-2023-709','2023-08-16','legislation','["性平教育"]','A703','性平教育法第三次大修','禁師生戀、外聘調查、懲罰性賠償；**未引入家長 opt-out 課程選擇權**','https://depart.moe.edu.tw/ED2800/News_Content.aspx?n=9C2F51A0AD31862F&sms=EA52AE3CDCB7AE20&s=D71495741C3D7B2A','["PI-10"]','[]','["ICESCR-13","CEDAW"]',NULL,datetime('now')),
('EV-2024-710','2024','outcome','["教育權"]','A707','高中升學壓力 / 學貸 / 補教文化 — 受教權實質可負擔性持續爭議','長期結構性現象，108 課綱未根本解決','','["PI-16"]','[]','["ICESCR-13-2-e","CRC-28"]',0,datetime('now')),
('EV-2025-711','2025','outcome','["教育權"]','A712','IB / 國際學校 / 雙語高中擴張 — 高所得家長 exit option 制度化','從不足 5,000 人擴至逾 20,000 人','','["PI-16"]','[]','["ICESCR-13-3","ICESCR-2-2"]',NULL,datetime('now')),
('EV-2026-712','2026','outcome','["教育權","選擇權"]','A707','父母教育選擇權與國家義務之憲法級張力持續未決','ICCPR 18-4 與 ICESCR 13-3 之內部衝突未獲制度化解方','','["PI-10","PI-16"]','[]','["ICESCR-13-3","ICCPR-18-4","CRC-29"]',NULL,datetime('now'));

INSERT INTO causal_link (from_event, to_event, link_type, evidence_strength, chain_depth, counter_evidence, multi_causal_note, note, created_at) VALUES
('EV-2009-701','EV-2014-702','triggered_by','indirect',1,'實驗教育三法直接動因為 2011 年自學家長社群與森林小學運動，兩公約僅為背景敘事','並列原因：(a) 自學家長社群動能；(b) 森林小學等先行案例；(c) 教育多元化趨勢','兩公約為間接規範背景',datetime('now')),
('EV-2014-702','EV-2025-711','triggered_by','contested',2,'IB/國際學校多在私校體系，與實驗教育三法法源不同；exit 行為主要受高等教育國際化驅動','並列原因：(a) 全球化；(b) 高等教育國際化；(c) 階級流動之 exit option','實驗教育與國際學校屬不同管道',datetime('now')),
('EV-2018-704','EV-2019-706','triggered_by','direct',1,'教育部主張修法是依公投結果之「立法形式整理」，性平法母法（含性傾向、性別認同）未變動','並列原因：(a) 公投結果；(b) 行政立法技術；(c) 跨黨派壓力','公投實質效力被技術性架空',datetime('now')),
('EV-2019-706','EV-2019-707','triggered_by','direct',1,'性平推動派認為新文字實質擴張保障；家長 opt-out 派則認為違反公投民意','並列原因：(a) 雙方對「父母選擇權 vs 學生免歧視權」之衡量標準分歧；(b) 立法技術與政治預期落差','非單向因果，雙向不滿',datetime('now')),
('EV-2019-705','EV-2024-710','parallels','contested',2,'升學壓力與補教文化非源於 108 課綱，而為長期結構性現象','並列原因：(a) 升學主義文化；(b) 高教擴張；(c) 少子化財務結構；(d) 學貸壓力','課綱非升學壓力主因',datetime('now')),
('EV-2022-708','EV-2023-709','triggered_by','contested',1,'2023 修法直接動因為 2023 年 5 月 #MeToo 運動連鎖效應','並列原因：(a) 國內 #MeToo 風暴；(b) 立法院跨黨派壓力；(c) 國際比較標準','CO 與 #MeToo 同步推動，非單一觸發',datetime('now'));

INSERT OR REPLACE INTO outcome_indicator (indicator_id, event_id, indicator_type, metric_name, before_value, before_year, after_value, after_year, direction, measurement_method, source_url, confounders, note) VALUES
('IND-701','EV-2014-702','statistic','實驗教育學生數','約 4,000 人','2014','逾 18,000 人','2024','improved','教育部統計','','混淆變項：城鄉/階級可近性差距未受監測','選擇權形式擴張'),
('IND-702','EV-2019-706','qualitative','性平教育法施行細則修訂後同志教育投訴件數','基線未公開','2019','校園性平調查案逐年成長','2024','contested','教育部統計','','雙方陣營對實質教學內容之解讀仍分歧','主管機關未公布教學內容稽核資料'),
('IND-703','EV-2025-711','statistic','高中以下 IB / 國際 / 雙語學校就讀人數','不足 5,000 人','2014','逾 20,000 人','2025','improved','教育部統計','','混淆變項：高所得 exit option 擴張可能侵蝕「機會平等」（ICESCR 13-2-c）','分配公平爭議'),
('IND-704','EV-2022-708','law','兩公約結論性意見涉教育權之回應完成率','0%','2022','部分機關回填；外部驗證薄弱','2025','contested','人約盟追蹤','','混淆變項：機關自評為主，缺第三方稽核','**追蹤機制尚未制度化**');
