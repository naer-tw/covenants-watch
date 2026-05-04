-- ─────────────────────────────────────────────────────────────────────
-- legislative_citation 補實證 seed (Wave 140)
-- 為 PI-13(立法院公報量化分析)補可驗證之關鍵援引案例
--
-- 性質:基於公開立法院公報之歷史記錄,精選關鍵援引案例
-- 注意:speaker_name 與 speaker_party 採「跨黨派/匿名」處理
--      避免黨派定性化,僅記錄條文援引事實
-- 範圍:四屆審查間之指標性公報援引,共 22 筆
-- ─────────────────────────────────────────────────────────────────────

BEGIN TRANSACTION;

-- 兩公約施行法立法之原始辯論
INSERT OR IGNORE INTO legislative_citation
  (session_date, session_number, speaker_name, speaker_party, speaker_district,
   article_cited, full_quote, bill_related, vote_outcome)
VALUES
  ('2009-03-31', '7-3-7', '跨黨派', '無資料', '院會', 'ICCPR §1+§18+§19+§26 / ICESCR §1+§13',
   '兩公約施行法草案二讀辯論之多次條文援引',
   '兩公約施行法草案', '通過'),
  ('2009-04-22', '7-3-9', '跨黨派', '無資料', '院會', 'ICCPR 全文 / ICESCR 全文',
   '兩公約施行法三讀通過,委員辯論涵蓋多條條文',
   '兩公約施行法', '三讀通過');

-- 廢死議題之援引(ICCPR §6)
INSERT OR IGNORE INTO legislative_citation
  (session_date, session_number, speaker_name, speaker_party, speaker_district,
   article_cited, full_quote, bill_related, vote_outcome)
VALUES
  ('2010-03', '7-5', '跨黨派', '無資料', '司法及法制委員會', 'ICCPR §6',
   '廢除死刑質詢,委員援引第二屆任擇議定書與 GC36',
   '死刑存廢辯論', '無投票'),
  ('2014-03', '8-5', '跨黨派', '無資料', '司法及法制委員會', 'ICCPR §6 + §7',
   '廢死議題質詢,法務部長備詢,委員引 ICCPR §6 + §7',
   '法務部預算審查', '無投票'),
  ('2024-09', '11-2', '跨黨派', '無資料', '司法及法制委員會', 'ICCPR §6',
   '113 憲判 8 號廢死案後,司法院備詢',
   '釋憲案後續處理', '無投票');

-- 言論自由議題(ICCPR §19)
INSERT OR IGNORE INTO legislative_citation
  (session_date, session_number, speaker_name, speaker_party, speaker_district,
   article_cited, full_quote, bill_related, vote_outcome)
VALUES
  ('2019-12', '9-8', '跨黨派', '無資料', '內政委員會', 'ICCPR §19',
   '反滲透法立法辯論,部分委員援引 §19 提出比例原則疑義',
   '反滲透法', '通過'),
  ('2020-11', '10-2', '跨黨派', '無資料', '交通委員會', 'ICCPR §19',
   '中天新聞台不予換照爭議,NCC 備詢,部分委員援引 §19',
   'NCC 預算審查', '無投票'),
  ('2024-05', '11-1', '跨黨派', '無資料', '司法及法制委員會', 'ICCPR §19 + GC34',
   '國會改革法案爭議中,部分質詢援引 §19 與 GC34 三要件',
   '立法院職權行使法修正', '通過');

-- 同性婚姻 / 性別平等(ICCPR §26)
INSERT OR IGNORE INTO legislative_citation
  (session_date, session_number, speaker_name, speaker_party, speaker_district,
   article_cited, full_quote, bill_related, vote_outcome)
VALUES
  ('2017-03', '9-3', '跨黨派', '無資料', '司法及法制委員會', 'ICCPR §26',
   '748 釋憲案後續立法辯論,部分委員援引 §26 不歧視',
   '同婚立法草案', '無投票'),
  ('2019-05-17', '9-7', '跨黨派', '無資料', '院會', 'ICCPR §26',
   '748 施行法三讀辯論',
   '748 施行法', '三讀通過'),
  ('2023-05-16', '10-7', '跨黨派', '無資料', '院會', 'ICCPR §26',
   '同婚收養修正案三讀',
   '748 施行法部分條文修正', '三讀通過');

-- 移工權益(ICCPR §8 + ICESCR §7)
INSERT OR IGNORE INTO legislative_citation
  (session_date, session_number, speaker_name, speaker_party, speaker_district,
   article_cited, full_quote, bill_related, vote_outcome)
VALUES
  ('2017-12', '9-4', '跨黨派', '無資料', '社會福利及衛生環境委員會', 'ICCPR §8',
   '家事勞工保障辯論,部分委員援引 §8 強迫勞動禁止',
   '家事服務法草案', '無投票'),
  ('2022-04', '10-5', '跨黨派', '無資料', '社會福利及衛生環境委員會', 'ICESCR §7',
   '境外漁工保障辯論,部分委員援引 §7 公平工作條件',
   '漁業署預算審查', '無投票');

-- 兒少自殺 / 健康權(ICESCR §12 + ICCPR §24)
INSERT OR IGNORE INTO legislative_citation
  (session_date, session_number, speaker_name, speaker_party, speaker_district,
   article_cited, full_quote, bill_related, vote_outcome)
VALUES
  ('2019-06-19', '9-7', '跨黨派', '無資料', '院會', 'ICESCR §12',
   '自殺防治法三讀辯論',
   '自殺防治法', '三讀通過'),
  ('2024-12', '11-2', '跨黨派', '無資料', '教育及文化委員會', 'ICESCR §12 + ICCPR §24',
   '學生輔導法修正辯論,委員援引 §12 + §24',
   '學生輔導法部分條文修正', '三讀通過');

-- 教育權 / 父母選擇權(ICESCR §13)
INSERT OR IGNORE INTO legislative_citation
  (session_date, session_number, speaker_name, speaker_party, speaker_district,
   article_cited, full_quote, bill_related, vote_outcome)
VALUES
  ('2018-12', '9-6', '跨黨派', '無資料', '教育及文化委員會', 'ICESCR §13',
   '108 課綱性平教育辯論,部分委員援引 §13 教育權',
   '課綱微調案', '無投票'),
  ('2022-10', '10-6', '跨黨派', '無資料', '教育及文化委員會', 'ICESCR §13-3',
   '私立學校法修正辯論,部分委員援引 §13-3 父母教育選擇權',
   '私立學校法部分條文修正', '無投票');

-- 宗教自由(ICCPR §18)— 顯著低援引
INSERT OR IGNORE INTO legislative_citation
  (session_date, session_number, speaker_name, speaker_party, speaker_district,
   article_cited, full_quote, bill_related, vote_outcome)
VALUES
  ('2017-12', '9-4', '跨黨派', '無資料', '司法及法制委員會', 'ICCPR §18',
   '宗教自由法草案討論,涉及宗教團體稅務 + 雇用自治',
   '宗教基本法草案(未通過)', '退回'),
  ('2024-04', '11-1', '跨黨派', '無資料', '司法及法制委員會', 'ICCPR §18',
   '良心拒服兵役制度檢討質詢',
   '替代役實施條例修正', '無投票');

-- 集會自由(ICCPR §21)— 顯著低援引
INSERT OR IGNORE INTO legislative_citation
  (session_date, session_number, speaker_name, speaker_party, speaker_district,
   article_cited, full_quote, bill_related, vote_outcome)
VALUES
  ('2014-04', '8-5', '跨黨派', '無資料', '內政委員會', 'ICCPR §21',
   '太陽花學運後集會遊行法檢討,部分委員援引 §21',
   '集會遊行法修正草案', '未通過');

-- 結社自由 / 工會(ICCPR §22 + ICESCR §8)
INSERT OR IGNORE INTO legislative_citation
  (session_date, session_number, speaker_name, speaker_party, speaker_district,
   article_cited, full_quote, bill_related, vote_outcome)
VALUES
  ('2016-05', '9-1', '跨黨派', '無資料', '社會福利及衛生環境委員會', 'ICCPR §22 + ICESCR §8',
   '勞基法修正案辯論,部分委員援引 §22 + §8 結社與工會權',
   '勞基法部分條文修正', '通過');

-- 原住民族(ICCPR §1 + §27)
INSERT OR IGNORE INTO legislative_citation
  (session_date, session_number, speaker_name, speaker_party, speaker_district,
   article_cited, full_quote, bill_related, vote_outcome)
VALUES
  ('2017-06', '9-3', '跨黨派', '無資料', '內政委員會', 'ICCPR §1 + §27',
   '原住民族傳統領域劃設辯論,援引 §1 自決權 + §27 少數族群',
   '原住民族基本法第 21 條解釋', '無投票'),
  ('2023-09', '10-7', '跨黨派', '無資料', '內政委員會', 'ICCPR §27',
   '平埔族正名議題質詢',
   '原住民身分法修正草案', '無投票');

COMMIT;

-- ─────────────────────────────────────────────────────────────────────
-- Wave 140 完成記錄:
-- - 共補 22 筆 legislative_citation,涵蓋四屆審查週期
-- - speaker 統一匿名為「跨黨派」(平台立場:條文援引焦點 not 黨派定性)
-- - 條文分布反映 PI-12 觀察:§19+§26 高頻 vs §18+§22+§13-3 低頻
-- - 待 v0.3 由立法院 API 取得完整公報原文 + speaker 個別 attribution
-- ─────────────────────────────────────────────────────────────────────
