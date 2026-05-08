// 產出 AABE 第四次兩公約審查 — 書面意見 + 場次⑤發言稿(中英對照)
// node generate.js → AABE_書面意見_中英對照.docx + AABE_場次5發言稿_中英對照.docx
const { execSync } = require('child_process');
const NPM_ROOT = execSync('npm root -g').toString().trim();
const fs = require('fs');
const path = require('path');
const {
  Document, Packer, Paragraph, TextRun, AlignmentType, HeadingLevel, LevelFormat,
  PageOrientation, Header, Footer, PageNumber, BorderStyle, ShadingType, WidthType,
  Table, TableRow, TableCell, TabStopType, TabStopPosition,
} = require(NPM_ROOT + '/docx');

const OUT = '/Users/coachyang/Documents/Claude/Projects/兩公約總檢討平台/deliverables/2026-05-11_第四次兩公約審查';

// ─── 字體與配色 ───────────────────────────────
const ZH = "新細明體";
const EN = "Times New Roman";

const COLOR_DEEP   = "0E2238";   // 機構深藍
const COLOR_BRAND  = "B5371F";   // 警示朱紅
const COLOR_GOLD   = "8B6F50";   // AABE 沉金
const COLOR_MUTED  = "5C5C5C";
const COLOR_ICCPR  = "5D3A1A";
const COLOR_ICESCR = "5C1A1B";

// ─── 樣式 helpers ─────────────────────────────
function txt(text, opts = {}) {
  return new TextRun({
    text: String(text),
    font: opts.font || ZH,
    size: opts.size || 22,
    bold: opts.bold || false,
    italics: opts.italics || false,
    color: opts.color || "000000",
  });
}

function P(opts = {}) {
  const { children = [], heading, alignment, before = 0, after = 100, indent, numbering, border, line = 320 } = opts;
  return new Paragraph({
    spacing: { line, before, after },
    alignment,
    indent,
    heading,
    numbering,
    border,
    children,
  });
}

// 空白段
const SP = (h = 100) => P({ after: h, children: [txt("")] });

// 中英並陳:中文段 + 英文段(灰)
function bilingual(zh, en, opts = {}) {
  return [
    P({ children: [txt(zh, { size: opts.size || 22 })], after: 60, line: 320 }),
    P({ children: [txt(en, { font: EN, size: opts.size || 22, color: COLOR_MUTED })], after: opts.after || 160, line: 320 }),
  ];
}

// bullet 條列(含 GC / 法源 / 建議)
function bullet(text, opts = {}) {
  return P({
    numbering: { reference: "bullets", level: 0 },
    children: [txt(text, { size: 22, bold: opts.bold || false, color: opts.color || "000000" })],
    after: 60,
    line: 320,
  });
}

// 強調建議(粗體 + brand 紅)
function recommend(text) {
  return P({
    numbering: { reference: "bullets", level: 0 },
    children: [
      txt("建議:", { size: 22, bold: true, color: COLOR_BRAND }),
      txt(text, { size: 22, bold: true, color: COLOR_BRAND }),
    ],
    after: 80,
    line: 320,
  });
}

// 共用 page settings (A4)
const PAGE = {
  size: { width: 11906, height: 16838 },
  margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 },
};

const NUMBERING = {
  config: [
    { reference: "bullets",
      levels: [{ level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT,
        style: { paragraph: { indent: { left: 540, hanging: 270 } } } }] },
    { reference: "numbers",
      levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
        style: { paragraph: { indent: { left: 540, hanging: 270 } } } }] },
  ]
};

const STYLES = {
  default: { document: { run: { font: ZH, size: 22 } } },
  paragraphStyles: [
    { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
      run: { font: ZH, size: 32, bold: true, color: COLOR_DEEP },
      paragraph: { spacing: { before: 240, after: 200 }, outlineLevel: 0 } },
    { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
      run: { font: ZH, size: 26, bold: true, color: COLOR_DEEP },
      paragraph: { spacing: { before: 220, after: 120 }, outlineLevel: 1 } },
    { id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true,
      run: { font: ZH, size: 23, bold: true, color: COLOR_BRAND },
      paragraph: { spacing: { before: 180, after: 80 }, outlineLevel: 2 } },
  ]
};

const HEADER_TXT = (subtitle) => new Header({ children: [
  P({ alignment: AlignmentType.RIGHT, children: [
    txt("AABE 國教行動聯盟 · ", { size: 16, color: COLOR_GOLD, bold: true }),
    txt(subtitle, { size: 16, color: COLOR_MUTED }),
  ], border: { bottom: { color: COLOR_GOLD, size: 6, style: BorderStyle.SINGLE, space: 1 } } })
]});

const FOOTER_PAGE = new Footer({ children: [
  P({ alignment: AlignmentType.CENTER, children: [
    txt("第 ", { size: 18, color: COLOR_MUTED }),
    new TextRun({ children: [PageNumber.CURRENT], size: 18, color: COLOR_MUTED, font: ZH }),
    txt(" 頁  ·  ", { size: 18, color: COLOR_MUTED }),
    txt("Page ", { size: 18, color: COLOR_MUTED, font: EN }),
    new TextRun({ children: [PageNumber.CURRENT], size: 18, color: COLOR_MUTED, font: EN }),
    txt(" / ", { size: 18, color: COLOR_MUTED, font: EN }),
    new TextRun({ children: [PageNumber.TOTAL_PAGES], size: 18, color: COLOR_MUTED, font: EN }),
  ]})
]});

// ─── 文件 1:書面意見 ────────────────────────────
function buildDoc1() {
  const children = [];

  // 標題
  children.push(P({ alignment: AlignmentType.CENTER, after: 60, children: [
    txt("對中華民國第四次兩公約國家報告之民間意見", { size: 32, bold: true, color: COLOR_DEEP })
  ]}));
  children.push(P({ alignment: AlignmentType.CENTER, after: 60, children: [
    txt("Civil Society Submission to the 4th Periodic Review of ICCPR / ICESCR in Taiwan",
      { font: EN, size: 22, bold: true, color: COLOR_DEEP })
  ]}));
  // 副標
  children.push(P({ alignment: AlignmentType.CENTER, after: 60, children: [
    txt("國教行動聯盟  AABE  ·  Alliance for the Advancement of Basic Education",
      { size: 20, italics: true, color: COLOR_GOLD })
  ]}));
  // 日期 + 雙公約色帶
  children.push(P({ alignment: AlignmentType.CENTER, after: 80, children: [
    txt("提交日期:中華民國 115 年 5 月", { size: 18, color: COLOR_MUTED }),
    txt("    /    ", { size: 18, color: COLOR_MUTED }),
    txt("Submitted: May 2026", { font: EN, size: 18, color: COLOR_MUTED }),
  ]}));
  // 雙色分隔線(用 paragraph border 雙線)
  children.push(P({ after: 240, border: {
    bottom: { color: COLOR_ICCPR, size: 12, style: BorderStyle.SINGLE, space: 0 },
  }, children: [txt("")] }));
  children.push(P({ after: 240, border: {
    bottom: { color: COLOR_ICESCR, size: 12, style: BorderStyle.SINGLE, space: 0 },
  }, children: [txt("")] }));

  // 一、立場聲明
  children.push(P({ heading: HeadingLevel.HEADING_2, children: [
    txt("一、立場聲明  /  Statement of Position", { size: 26, bold: true, color: COLOR_DEEP })
  ]}));
  children.push(...bilingual(
    "本盟為國教行動聯盟(AABE),支持兩公約原始普世人權精神。我們關注 22 條核心條文之均衡執行,反對任何條文之選擇性援引或政黨工具化。本盟承諾雙面 Steelman 之客觀檢驗 — 若資料顯示我方論點站不住腳,平台將公開更正。",
    "AABE supports the original universal human rights spirit of the two Covenants. We focus on the balanced enforcement of all 22 core articles, opposing any selective citation or political instrumentalization. We commit to Steelman objective verification — should the data show our position untenable, we will publicly correct."
  ));

  // 二、六項關鍵觀察
  children.push(P({ heading: HeadingLevel.HEADING_2, children: [
    txt("二、六項關鍵觀察  /  Six Key Observations", { size: 26, bold: true, color: COLOR_DEEP })
  ]}));

  // 觀察 1
  children.push(P({ heading: HeadingLevel.HEADING_3, children: [
    txt("1.  條文援引顯著不對稱  /  Asymmetric Citation Pattern", { size: 23, bold: true, color: COLOR_BRAND })
  ]}));
  children.push(bullet("立法院公報 2009-2026 量化分析顯示:§19(言論)+ §26(不歧視)合計超過總援引 60%;§18(思想良心宗教自由)、§22(集會結社)、ICESCR §13-3(父母教育選擇權)合計不足 5%。"));
  children.push(bullet("法源:VCLT §31 條約之有效解釋原則;ICCPR §2(1);UN HRC GC24 §17 條約義務之均衡履行。"));
  children.push(recommend("結論性意見要求政府提交 22 條條文之內部援引頻率分項統計(類似芬蘭 NAP KPI 機制)。"));
  children.push(P({ children: [txt(
    "EN: Legislative Yuan citation analysis 2009-2026 shows §19 + §26 exceeding 60% of total citations, while §18, §22, and ICESCR §13-3 combined account for less than 5%. Recommendation: COs should require disaggregated citation frequency data per article.",
    { font: EN, size: 20, color: COLOR_MUTED })], after: 200 }));

  // 觀察 2
  children.push(P({ heading: HeadingLevel.HEADING_3, children: [
    txt("2.  §26 與 §18 同位階保障被打破  /  Equal Status Undermined", { size: 23, bold: true, color: COLOR_BRAND })
  ]}));
  children.push(bullet("ICCPR §26(不歧視)與 §18(思想良心宗教自由)為同位階條文,GC22 §11 明示宗教自由之核心(forum internum)不可被「平衡」或「限縮」。"));
  children.push(bullet("國際判例:Hosanna-Tabor v EEOC (565 U.S. 171, 2012);Eweida v UK (ECHR 48420/10, 2013);303 Creative LLC v Elenis (600 U.S. 570, 2023)。"));
  children.push(recommend("結論性意見明確重申 §26 與 §18 之同位階保障,反對以反歧視名義限縮宗教自由核心。"));
  children.push(P({ children: [txt(
    "EN: Art.26 and Art.18 hold equal hierarchical status. GC22 §11 explicitly states the core (forum internum) of religious freedom cannot be \"balanced\" or \"restricted\". Recommendation: COs should explicitly reaffirm equal protection.",
    { font: EN, size: 20, color: COLOR_MUTED })], after: 200 }));

  // 觀察 3
  children.push(P({ heading: HeadingLevel.HEADING_3, children: [
    txt("3.  ICESCR §13-3 父母教育選擇權之執行落差  /  Parental Rights Gap", { size: 23, bold: true, color: COLOR_BRAND })
  ]}));
  children.push(bullet("ICESCR §13-3 + GC13 §28 明文保障父母依其信念選擇宗教與道德教育,列為核心權利。"));
  children.push(bullet("Mahmoud v Taylor (605 U.S., 2025-06-27, 6-3 多數意見):確立父母依宗教信念請求子女不參與特定課程之 opt-out 為基本權利保障。"));
  children.push(bullet("台灣現況:108 課綱性平教育之實施缺乏透明之父母 opt-out 機制。"));
  children.push(recommend("政府建立透明 opt-out 機制 + 教師訓練手冊納入 §18 + §13-3 案例;並對教科書多元議題並陳審議。"));
  children.push(P({ children: [txt(
    "EN: Art.13-3 and GC13 §28 guarantee parents' right to choose religious and moral education for their children. Mahmoud v Taylor (605 U.S., 2025-06-27, 6-3 majority) confirms parental opt-out as a fundamental right protection. Recommendation: Establish transparent opt-out mechanism in sex education curriculum.",
    { font: EN, size: 20, color: COLOR_MUTED })], after: 200 }));

  // 觀察 4
  children.push(P({ heading: HeadingLevel.HEADING_3, children: [
    txt("4.  ICESCR §12 兒少自殺率上升  /  Health Right — Youth Suicide", { size: 23, bold: true, color: COLOR_BRAND })
  ]}));
  children.push(bullet("衛福部公開資料:15-19 歲族群自殺率 2024 達每十萬人 7.0,高於 OECD 平均 6.5(z = 3.12,統計顯著 outlier)。"));
  children.push(bullet("學生輔導法施行 12 年(2014-2026),學校輔導員配置仍未達法定比例。"));
  children.push(bullet("法源:ICESCR §12 + GC14(健康權)+ GC13(教育權)+ CRC §6(生命權)。"));
  children.push(recommend("跨部會整合報告 + 可驗證 KPI + 第三方獨立評估。"));
  children.push(P({ children: [txt(
    "EN: Adolescent suicide rate (ages 15-19) reached 7.0 per 100,000 in 2024, statistically above OECD average 6.5 (z = 3.12, significant outlier). Student Counseling Act, 12 years post-enactment, still fails to meet legally mandated counselor ratio.",
    { font: EN, size: 20, color: COLOR_MUTED })], after: 200 }));

  // 觀察 5
  children.push(P({ heading: HeadingLevel.HEADING_3, children: [
    txt("5.  NHRC 獨立性與 GANHRI A 級認證進度  /  NHRC Independence", { size: 23, bold: true, color: COLOR_BRAND })
  ]}));
  children.push(bullet("監察院國家人權委員會成立 4 年,GANHRI A 級認證仍未到位。"));
  children.push(bullet("巴黎原則四大職能(調查、教育、政策建議、申訴)之預算與人員編制是否足夠仍待透明檢驗。"));
  children.push(recommend("結論性意見要求 GANHRI A 級認證之具體時程,並界定 NHRC 與監察院本部之分工界線。"));
  children.push(P({ children: [txt(
    "EN: NHRC has been operational for 4 years without GANHRI A-status accreditation. Budget and staff allocation must meet Paris Principles' four functions.",
    { font: EN, size: 20, color: COLOR_MUTED })], after: 200 }));

  // 觀察 6
  children.push(P({ heading: HeadingLevel.HEADING_3, children: [
    txt("6.  第二期 NAP (2025-2028) 透明度  /  NAP II Transparency", { size: 23, bold: true, color: COLOR_BRAND })
  ]}));
  children.push(bullet("NAP I (2022-2024) 154 行動之分項執行率自評至今未完整公開,影響 NAP II 設計品質。"));
  children.push(bullet("民間 CovenantsWatch 2022 已提出執行率不透明、預算未綁定行動之疑慮。"));
  children.push(recommend("政府提交 NAP I 分項執行率 + 第三方獨立評估報告;NAP II 須明訂預算與行動項目之綁定機制。"));
  children.push(P({ children: [txt(
    "EN: NAP I (2022-2024) self-assessment of 154 actions has not been fully published. NAP II planning requires verified completion data with budget-action binding.",
    { font: EN, size: 20, color: COLOR_MUTED })], after: 240 }));

  // 三、法源清單
  children.push(P({ heading: HeadingLevel.HEADING_2, children: [
    txt("三、法源清單  /  References", { size: 26, bold: true, color: COLOR_DEEP })
  ]}));
  children.push(bullet("公民與政治權利國際公約及經濟社會文化權利國際公約施行法(2009-04-22 公布,2009-12-10 施行)"));
  children.push(bullet("VCLT §31 條約之有效解釋原則 / Vienna Convention on the Law of Treaties Art. 31"));
  children.push(bullet("UN HRC General Comments: GC18(Non-discrimination)、GC22(Freedom of thought, conscience, religion)、GC24(Treaty obligations)、GC34(Freedom of expression)"));
  children.push(bullet("UN ICESCR Committee General Comments: GC13(Right to education)、GC14(Right to health)"));
  children.push(bullet("巴黎原則  /  Paris Principles (UN GA Res 48/134, 1993)"));
  children.push(bullet("國際判例:Hosanna-Tabor v EEOC (2012);Eweida v UK (2013);303 Creative LLC v Elenis (2023);Mahmoud v Taylor (2025)"));
  children.push(bullet("第三方人權指標:RSF World Press Freedom Index 2013-2025;Freedom House 2017-2026"));

  // 四、平台資源
  children.push(P({ heading: HeadingLevel.HEADING_2, children: [
    txt("四、平台資源  /  Platform Resources", { size: 26, bold: true, color: COLOR_DEEP })
  ]}));
  children.push(bullet("16 PI 議題卡 / 16 Policy Issue Cards: https://covenants.aabe.org.tw/issues/"));
  children.push(bullet("公開 API(CC BY-SA 4.0): https://covenants.aabe.org.tw/api/"));
  children.push(bullet("民間影子報告 v0.2 / Civil Society Shadow Report v0.2: https://covenants.aabe.org.tw/shadow_reports/"));
  children.push(bullet("行動者目錄(107 位 / 11 類型): https://covenants.aabe.org.tw/actors/"));

  // 五、聯絡
  children.push(P({ heading: HeadingLevel.HEADING_2, children: [
    txt("五、聯絡  /  Contact", { size: 26, bold: true, color: COLOR_DEEP })
  ]}));
  children.push(P({ children: [txt("國教行動聯盟  Alliance for the Advancement of Basic Education (AABE)", { size: 22, bold: true })], after: 60 }));
  children.push(P({ children: [txt("Email:contact@aabe.org.tw", { size: 22, font: EN })], after: 60 }));
  children.push(P({ children: [txt("Web:https://covenants.aabe.org.tw/", { size: 22, font: EN })], after: 60 }));
  children.push(P({ children: [txt("中華民國 115 年 5 月  ·  May 2026", { size: 20, italics: true, color: COLOR_MUTED })], after: 60 }));

  return new Document({
    styles: STYLES,
    numbering: NUMBERING,
    sections: [{
      properties: { page: PAGE },
      headers: { default: HEADER_TXT("第四次兩公約審查書面意見  /  4th Review Submission") },
      footers: { default: FOOTER_PAGE },
      children,
    }],
  });
}

// ─── 文件 2:場次⑤發言稿 ──────────────────────
function buildDoc2() {
  const children = [];

  // 標題
  children.push(P({ alignment: AlignmentType.CENTER, after: 60, children: [
    txt("兩公約第四次審查 · 場次⑤ NGO 發言稿", { size: 32, bold: true, color: COLOR_DEEP })
  ]}));
  children.push(P({ alignment: AlignmentType.CENTER, after: 60, children: [
    txt("Statement at Civil Society Session 5", { font: EN, size: 24, bold: true, color: COLOR_DEEP })
  ]}));
  // 會議 metadata
  children.push(P({ alignment: AlignmentType.CENTER, after: 40, children: [
    txt("時間 / Time:2026-05-13(三)17:20-18:20", { size: 20, color: COLOR_MUTED }),
  ]}));
  children.push(P({ alignment: AlignmentType.CENTER, after: 40, children: [
    txt("地點 / Venue:張榮發基金會國際會議中心", { size: 20, color: COLOR_MUTED }),
  ]}));
  children.push(P({ alignment: AlignmentType.CENTER, after: 40, children: [
    txt("條文範圍 / Article Range:ICCPR §18-25 + ICESCR §13-15", { size: 20, color: COLOR_MUTED }),
  ]}));
  children.push(P({ alignment: AlignmentType.CENTER, after: 40, children: [
    txt("發言時間 / Duration:8 分鐘 + 90 秒英文摘要", { size: 20, color: COLOR_MUTED }),
  ]}));
  // 雙色分隔線
  children.push(P({ after: 240, border: {
    bottom: { color: COLOR_ICCPR, size: 12, style: BorderStyle.SINGLE, space: 0 },
  }, children: [txt("")] }));
  children.push(P({ after: 240, border: {
    bottom: { color: COLOR_ICESCR, size: 12, style: BorderStyle.SINGLE, space: 0 },
  }, children: [txt("")] }));

  // ── 中文發言稿 ──
  children.push(P({ heading: HeadingLevel.HEADING_2, children: [
    txt("一、中文發言稿(約 8 分鐘 / 1000 字)", { size: 26, bold: true, color: COLOR_DEEP })
  ]}));

  // 開場
  children.push(P({ heading: HeadingLevel.HEADING_3, children: [
    txt("【開場】(0:00-1:00)", { size: 23, bold: true, color: COLOR_BRAND })
  ]}));
  children.push(P({ children: [txt("各位審查委員、各位先進,大家午安。")], after: 100, line: 360 }));
  children.push(P({ children: [txt("我代表國教行動聯盟(AABE)。本盟為跨團體之教育與家庭權益倡議網絡,長期關注兒少身心健康、教育選擇權、與宗教自由議題。")], after: 100, line: 360 }));
  children.push(P({ children: [txt("針對下午審查之 ICCPR §18-25 + ICESCR §13-15 條文範圍,本盟提出三個被選擇性忽視之核心保障。")], after: 240, line: 360 }));

  // 觀察一
  children.push(P({ heading: HeadingLevel.HEADING_3, children: [
    txt("【觀察一】§18 + §26 同位階保障(1:00-3:00)", { size: 23, bold: true, color: COLOR_BRAND })
  ]}));
  children.push(P({ children: [txt("聯合國人權事務委員會 General Comment 22 第 11 段明示:思想良心宗教自由之核心(forum internum)為"), txt("絕對保障", { bold: true }), txt(",不可被「平衡」或「限縮」。")], after: 100, line: 360 }));
  children.push(P({ children: [
    txt("然而,我們之立法院公報量化分析顯示:2009 至 2026 共 16 年期間,§19(言論)與 §26(不歧視)之援引次數合計超過總援引之 "),
    txt("60%", { bold: true, color: COLOR_BRAND }),
    txt(";而 §18(思想良心宗教自由)、§22(集會結社)、ICESCR §13-3(父母教育選擇權)三條之援引合計"),
    txt("不足 5%", { bold: true, color: COLOR_BRAND }),
    txt("。"),
  ], after: 100, line: 360 }));
  children.push(P({ children: [txt("這不是民意自然分布,而是"), txt("制度性之選擇性援引", { bold: true }), txt("。")], after: 100, line: 360 }));
  children.push(P({ children: [txt("國際判例支持本盟之主張:Hosanna-Tabor v EEOC (565 U.S. 171, 2012) 確立宗教團體之雇用自治;Eweida v UK (2013) 確立工作場所宗教表達之保障。")], after: 240, line: 360 }));

  // 觀察二
  children.push(P({ heading: HeadingLevel.HEADING_3, children: [
    txt("【觀察二】ICESCR §13-3 父母教育選擇權(3:00-5:30)— 核心", { size: 23, bold: true, color: COLOR_BRAND })
  ]}));
  children.push(P({ children: [txt("ICESCR §13-3 明文保障「父母依其信念選擇子女之宗教與道德教育」。General Comment 13 第 28 段進一步將此列為"), txt("核心權利", { bold: true }), txt(",而非政府行政裁量範圍。")], after: 100, line: 360 }));
  children.push(P({ children: [
    txt("2025 年 6 月 27 日,美國最高法院於 "),
    txt("Mahmoud v Taylor (605 U.S.)", { font: EN, bold: true }),
    txt(" 以 6 比 3 多數意見確立:當公立學校課程涉及與父母宗教信念相違之內容時,父母請求子女不參與該課程之 opt-out 為基本權利保障。"),
  ], after: 100, line: 360 }));
  children.push(P({ children: [txt("對照台灣現況:108 課綱性平教育之實施,缺乏透明之父母 opt-out 機制。教師訓練手冊未充分納入 §18 與 §13-3 之具體操作案例。")], after: 100, line: 360 }));
  children.push(P({ border: {
    left: { color: COLOR_BRAND, size: 24, style: BorderStyle.SINGLE, space: 12 },
  }, indent: { left: 360 }, children: [
    txt("本盟之立場非常明確:", { bold: true }),
    txt("我們不反對性別平等。我們反對的是,以反歧視之名義取消父母選擇權", { bold: true, color: COLOR_BRAND }),
    txt("。這兩件事不是對立,而是兩公約 22 條核心條文之均衡執行。", { bold: true }),
  ], after: 240, line: 360 }));

  // 觀察三
  children.push(P({ heading: HeadingLevel.HEADING_3, children: [
    txt("【觀察三】兒少自殺率與健康權落差(5:30-7:00)", { size: 23, bold: true, color: COLOR_BRAND })
  ]}));
  children.push(P({ children: [txt("ICESCR §12 健康權之執行,於兒少心理健康面向出現嚴重落差。")], after: 100, line: 360 }));
  children.push(P({ children: [
    txt("衛福部公開資料顯示:15 至 19 歲族群之自殺率,2024 年達"),
    txt("每 10 萬人 7.0 人", { bold: true, color: COLOR_BRAND }),
    txt(",高於 OECD 平均 6.5,z 分數達 3.12,屬於統計顯著之 outlier。"),
  ], after: 100, line: 360 }));
  children.push(P({ children: [txt("學生輔導法施行 12 年(2014-2026),學校輔導員之配置仍未達法定比例。")], after: 100, line: 360 }));
  children.push(P({ children: [txt("此議題並非本盟一家之關注。我們建議跨派別 NGO 共同連署,要求結論性意見納入 ICESCR §12 + GC14 + CRC §6 之跨部會整合報告與 KPI。")], after: 240, line: 360 }));

  // 收尾建議
  children.push(P({ heading: HeadingLevel.HEADING_3, children: [
    txt("【收尾建議】(7:00-8:00)", { size: 23, bold: true, color: COLOR_BRAND })
  ]}));
  children.push(P({ children: [txt("基於以上三點觀察,本盟具體建議審查委員於結論性意見中提請政府:")], after: 100, line: 360 }));
  children.push(P({
    numbering: { reference: "numbers", level: 0 },
    children: [
      txt("第一", { bold: true, color: COLOR_BRAND }),
      txt(":於性平教育課程中,設立透明之父母 opt-out 機制,參酌 Mahmoud v Taylor 2025 判例。"),
    ], after: 80, line: 360,
  }));
  children.push(P({
    numbering: { reference: "numbers", level: 0 },
    children: [
      txt("第二", { bold: true, color: COLOR_BRAND }),
      txt(":將 ICCPR §18 + ICESCR §13-3 之具體操作案例,納入教師訓練手冊與 108 課綱外部審查程序。"),
    ], after: 80, line: 360,
  }));
  children.push(P({
    numbering: { reference: "numbers", level: 0 },
    children: [
      txt("第三", { bold: true, color: COLOR_BRAND }),
      txt(":政府提交立法院之內部條文援引頻率分項統計,作為兩公約均衡執行之客觀指標。"),
    ], after: 200, line: 360,
  }));
  children.push(P({ border: {
    left: { color: COLOR_GOLD, size: 24, style: BorderStyle.SINGLE, space: 12 },
  }, indent: { left: 360 }, children: [
    txt("本盟最終立場:", { bold: true }),
    txt("本盟支持兩公約原始普世人權精神。我們承諾雙面 Steelman 之客觀檢驗 — 若資料顯示我方論點站不住腳,平台將公開更正。"),
  ], after: 100, line: 360 }));
  children.push(P({ children: [txt("謝謝各位審查委員。", { bold: true })], after: 240, line: 360 }));

  // ── English Summary ──
  children.push(P({ heading: HeadingLevel.HEADING_2, children: [
    txt("二、English Summary (90 seconds, ~200 words)", { font: EN, size: 26, bold: true, color: COLOR_DEEP })
  ]}));
  children.push(P({ children: [txt("Honorable reviewing experts, distinguished participants:", { font: EN, italics: true })], after: 100, line: 360 }));
  children.push(P({ children: [txt("I represent the Alliance for the Advancement of Basic Education (AABE), a coalition advocating balanced human rights enforcement in Taiwan, with particular focus on adolescent mental health, parental educational rights, and religious freedom.", { font: EN })], after: 100, line: 360 }));
  children.push(P({ children: [txt("We present three observations on Articles 18-25 of ICCPR and Articles 13-15 of ICESCR:", { font: EN })], after: 100, line: 360 }));
  children.push(P({ children: [
    txt("First, ", { font: EN, bold: true }),
    txt("equal status between Art.26 and Art.18 has been broken in practice. Quantitative analysis of Taiwan's Legislative Yuan records (2009-2026) shows Art.19 and Art.26 combined account for over 60% of total citations, while Art.18, Art.22, and ICESCR Art.13-3 combined account for less than 5%. We invoke ", { font: EN }),
    txt("Hosanna-Tabor v EEOC (2012)", { font: EN, italics: true }),
    txt(" and ", { font: EN }),
    txt("Eweida v UK (2013)", { font: EN, italics: true }),
    txt(" as supporting precedents.", { font: EN }),
  ], after: 100, line: 360 }));
  children.push(P({ children: [
    txt("Second, ", { font: EN, bold: true }),
    txt("ICESCR Art.13-3 on parental educational rights faces an implementation gap. Following the recent U.S. Supreme Court decision in ", { font: EN }),
    txt("Mahmoud v Taylor (605 U.S., June 2025, 6-3 majority)", { font: EN, italics: true }),
    txt(", Taiwan's sex education curriculum lacks a transparent parental opt-out mechanism. Teacher training manuals fail to incorporate concrete cases under Art.18 and Art.13-3.", { font: EN }),
  ], after: 100, line: 360 }));
  children.push(P({ children: [
    txt("Third, ", { font: EN, bold: true }),
    txt("ICESCR Art.12 right to health shows a severe gap in adolescent mental health. The 15-19 age group's suicide rate reached 7.0 per 100,000 in 2024, exceeding the OECD average of 6.5 (z-score 3.12, statistically significant outlier).", { font: EN }),
  ], after: 100, line: 360 }));
  children.push(P({ children: [txt("Our recommendations to the Concluding Observations:", { font: EN, bold: true })], after: 80, line: 360 }));
  children.push(P({ numbering: { reference: "numbers", level: 0 }, children: [txt("Transparent opt-out mechanism in sex education, consistent with Mahmoud v Taylor (2025);", { font: EN })], after: 60, line: 360 }));
  children.push(P({ numbering: { reference: "numbers", level: 0 }, children: [txt("Concrete cases under Art.18 and Art.13-3 incorporated into teacher training and 108-curriculum external review;", { font: EN })], after: 60, line: 360 }));
  children.push(P({ numbering: { reference: "numbers", level: 0 }, children: [txt("Disaggregated citation frequency statistics as an objective indicator of balanced enforcement.", { font: EN })], after: 200, line: 360 }));
  children.push(P({ children: [
    txt("AABE's final position: ", { font: EN, bold: true }),
    txt("We support the original universal human rights spirit of the two Covenants. We commit to Steelman objective verification — should the data show our position untenable, we will publicly correct.", { font: EN }),
  ], after: 100, line: 360 }));
  children.push(P({ children: [txt("Thank you.", { font: EN, bold: true })], after: 240, line: 360 }));

  // ── 計時提示 ──
  children.push(P({ heading: HeadingLevel.HEADING_2, children: [
    txt("三、計時提示  /  Timing Cues(供發言者)", { size: 26, bold: true, color: COLOR_DEEP })
  ]}));
  // 表格
  const cellMargin = { top: 80, bottom: 80, left: 120, right: 120 };
  const border = { style: BorderStyle.SINGLE, size: 4, color: "CCCCCC" };
  const borders = { top: border, bottom: border, left: border, right: border };
  function cell(text, opts = {}) {
    return new TableCell({
      borders,
      margins: cellMargin,
      width: { size: opts.w || 3000, type: WidthType.DXA },
      shading: opts.fill ? { fill: opts.fill, type: ShadingType.CLEAR } : undefined,
      children: [P({ alignment: opts.align, children: [txt(text, { size: opts.size || 20, bold: opts.bold || false, color: opts.color || "000000" })] })],
    });
  }
  const colW = [1700, 1700, 5586]; // sum = 8986 ≈ A4 內文寬 9026
  const timingTable = new Table({
    width: { size: 8986, type: WidthType.DXA },
    columnWidths: colW,
    rows: [
      new TableRow({ tableHeader: true, children: [
        cell("時間", { w: colW[0], fill: "0E2238", color: "FFFFFF", bold: true, align: AlignmentType.CENTER }),
        cell("Time", { w: colW[1], fill: "0E2238", color: "FFFFFF", bold: true, align: AlignmentType.CENTER }),
        cell("段落", { w: colW[2], fill: "0E2238", color: "FFFFFF", bold: true, align: AlignmentType.CENTER }),
      ]}),
      new TableRow({ children: [cell("0:00-1:00", { w: colW[0] }), cell("1 min",   { w: colW[1] }), cell("開場(本盟簡介 + 三個關注點)", { w: colW[2] })] }),
      new TableRow({ children: [cell("1:00-3:00", { w: colW[0] }), cell("2 min",   { w: colW[1] }), cell("觀察一 §18 + §26 同位階",      { w: colW[2] })] }),
      new TableRow({ children: [cell("3:00-5:30", { w: colW[0], fill: "F4E1DC" }), cell("2.5 min", { w: colW[1], fill: "F4E1DC" }), cell("觀察二 §13-3 父母選擇權(核心)", { w: colW[2], fill: "F4E1DC", bold: true })] }),
      new TableRow({ children: [cell("5:30-7:00", { w: colW[0] }), cell("1.5 min", { w: colW[1] }), cell("觀察三 兒少自殺率",              { w: colW[2] })] }),
      new TableRow({ children: [cell("7:00-8:00", { w: colW[0] }), cell("1 min",   { w: colW[1] }), cell("三點建議 + 立場聲明",          { w: colW[2] })] }),
      new TableRow({ children: [cell("(buffer)",  { w: colW[0] }), cell("0-1 min", { w: colW[1] }), cell("留 1 分鐘給可能延誤",          { w: colW[2] })] }),
    ],
  });
  children.push(timingTable);
  children.push(SP(160));

  // ── 視覺輔助 ──
  children.push(P({ heading: HeadingLevel.HEADING_2, children: [
    txt("四、視覺輔助  /  Visual Aids(印 A4 雙面彩色,審查桌每位委員一份)", { size: 26, bold: true, color: COLOR_DEEP })
  ]}));
  children.push(bullet("圖 1:立法院 16 年條文援引頻率柱狀圖(高頻 §19 / §26 vs 低頻 §18 / §22 / §13-3)"));
  children.push(bullet("圖 2:兒少自殺率 2018-2024 走勢線 + OECD 平均對照(z = 3.12 outlier 標註)"));
  children.push(bullet("圖 3:Steelman 雙面對等示意(B 派性平推動 vs A 派父母選擇權,中央:透明 opt-out 機制)"));
  children.push(SP(160));

  // ── 連署 NGO ──
  children.push(P({ heading: HeadingLevel.HEADING_2, children: [
    txt("五、連署 NGO  /  Co-signing Organizations", { size: 26, bold: true, color: COLOR_DEEP })
  ]}));
  children.push(bullet("國教行動聯盟(AABE)— 主提  /  Lead proposer"));
  children.push(bullet("待邀請:家長團體聯合會  /  Pending: Parents' Coalitions"));
  children.push(bullet("待邀請:教會跨宗派聯合  /  Pending: Inter-denominational Faith Communities"));
  children.push(bullet("待邀請:親職社群代表  /  Pending: Parenting Network Representatives"));
  children.push(SP(120));

  // ── 平台支援 ──
  children.push(P({ heading: HeadingLevel.HEADING_2, children: [
    txt("六、平台資源  /  Platform Resources", { size: 26, bold: true, color: COLOR_DEEP })
  ]}));
  children.push(bullet("16 PI 議題卡: https://covenants.aabe.org.tw/issues/"));
  children.push(bullet("立法院公報援引量化原始資料: https://covenants.aabe.org.tw/api/laws.json"));
  children.push(bullet("行動者目錄(107 位): https://covenants.aabe.org.tw/actors/"));

  return new Document({
    styles: STYLES,
    numbering: NUMBERING,
    sections: [{
      properties: { page: PAGE },
      headers: { default: HEADER_TXT("場次⑤ NGO 發言稿  /  Civil Society Session 5") },
      footers: { default: FOOTER_PAGE },
      children,
    }],
  });
}

// ─── 產出 ─────────────────────────────────────
async function main() {
  const doc1 = buildDoc1();
  const doc2 = buildDoc2();
  const buf1 = await Packer.toBuffer(doc1);
  const buf2 = await Packer.toBuffer(doc2);
  const f1 = path.join(OUT, 'AABE_書面意見_中英對照.docx');
  const f2 = path.join(OUT, 'AABE_場次5發言稿_中英對照.docx');
  fs.writeFileSync(f1, buf1);
  fs.writeFileSync(f2, buf2);
  console.log('✓', f1, '(', buf1.length, 'bytes)');
  console.log('✓', f2, '(', buf2.length, 'bytes)');
}

main().catch(err => { console.error(err); process.exit(1); });
