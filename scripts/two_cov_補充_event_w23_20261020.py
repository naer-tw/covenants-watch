#!/usr/bin/env python3
"""
W2-3 更新員 2026-10-20:補第四次國際審查(2026-05)之後的已查證事件。

沿用 two_cov_補充_event.py 的 E() 與 INSERT OR IGNORE 模式;每筆 source_url 皆為本輪實際抓取過之頁面。
只寫「誰在何時做了什麼」之可核對事實,不下是非判定(is_positive_outcome 一律 None)。

用法: python3 scripts/two_cov_補充_event_w23_20261020.py [--dry-run]
"""
from __future__ import annotations
import importlib.util, sqlite3, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("ev_base", ROOT / "scripts" / "two_cov_補充_event.py")
base = importlib.util.module_from_spec(spec); spec.loader.exec_module(base)
E, DB = base.E, base.DB

HR = "https://www.humanrights.moj.gov.tw/17725/17733/41766/41770/46434/"
CO_PAGE = HR + "46435/46443/post"
PLAN_PAGE = HR + "46447/46452/post"
EV = [
 E("A003","EV-2026-W23-01","2026-05-11","govt_response","第四次國家報告國際審查會議於台北舉行(5/11–5/15)",
   "法務部主辦、12 位國際專家組成審查委員會(ICCPR 組主席 Manfred Nowak、ICESCR 組主席 Heisoo Shin);政府機關各場次出席(CO 第 5 段載明立法院未參與)。",
   tags=["國際審查"], pi=["PI-03"], pos=None, src="https://www.moj.gov.tw/2832/2833/2834/2835/277164/post",
   note="W2-3 2026-10-20 新增;委員名單與出席情形見 CO 第 3、5 段(data/sources/raw/co/co_review_4_2026_en.pdf)"),
 E("A304","EV-2026-W23-02","2026-05-15","co_paragraph","審查委員會通過第四組結論性意見與建議(全文 135 個編號段)",
   "2026-05-15 於台北通過;法務部 5/15 儀式由政務委員林明昕代表政府受領,並稱將啟動行政管考。英文版 2026-09-04、中譯定稿版 2026-09-17 上網。",
   tags=["國際審查","結論性意見"], pi=["PI-03","PI-02"], co=["CO-4-1-FINAL..CO-4-135-FINAL"], pos=None,
   src=CO_PAGE, note="取代審查前預測稿 CO-4-1~10(後者不刪,已加註)。「135 點」為法務部用語;本庫以 PDF 編號段 1–135 逐段入庫,其中 1–10 為緒論。"),
 E("A304","EV-2026-W23-03","2026-05-15","co_paragraph","CO 第 97–101 段:重申呼籲正式宣布暫停執行死刑",
   "委員會表示對以民調作為不宣布暫停之理由深表關切(¶99),並建議政府向公眾溝通死刑與第 6 條之關係(¶100);另載明聯合國秘書長 2025 年報告記錄台灣過去五年執行 1 次(¶97)。",
   tags=["廢死"], pi=["PI-03"], co=["CO-4-97-FINAL","CO-4-98-FINAL","CO-4-99-FINAL","CO-4-100-FINAL","CO-4-101-FINAL"], art=["ICCPR-6","ICCPR-7"],
   pos=None, src="https://www.ettoday.net/news/20260515/3166610.htm", note="另一面:台南殺警案被害人家屬不接受國際建議取代國內法治(udn/LTN 報導),本庫登錄兩面,不下判定。一手=CO PDF。"),
 E("A304","EV-2026-W23-04","2026-05-15","co_paragraph","CO 第 11–14 段:國家人權委員會之制度限制與 2026-07 任期屆滿風險",
   "委員會指出缺乏專屬組織法、預算大幅刪減與人力有限,並關切現任委員 2026 年 7 月任期屆滿後能否有效運作(¶12);建議立法院提供充足預算、總統提名適格委員、人權會與監察院釐清職掌(¶13)。",
   tags=["國家人權機構"], pi=["PI-07"], co=["CO-4-11-FINAL","CO-4-12-FINAL","CO-4-13-FINAL","CO-4-14-FINAL"],
   pos=None, src="https://news.ltn.com.tw/news/politics/breakingnews/5438469", note="一手=CO PDF 第 11–14 段(逐段已讀)。"),
 E("A304","EV-2026-W23-05","2026-05-15","co_paragraph","CO 第 87–92 段:受教育權——融合教育(身心障礙學生)與全面性教育",
   "¶88–89 建議以人權模式主流化融合教育、提供校內常設協助、檢討以低收入戶身分作為支持門檻;¶90 載明委員會聽取家長團體、障礙者團體、LGBTQI+ 團體等多元意見,¶91–92 建議將全面性教育納入師培並以人權與性別平等為框架編修教材。",
   tags=["教育權"], pi=["PI-10"], co=["CO-4-87-FINAL","CO-4-88-FINAL","CO-4-89-FINAL","CO-4-90-FINAL","CO-4-91-FINAL","CO-4-92-FINAL"], art=["ICESCR-13"],
   pos=None, src=CO_PAGE, note="一手=CO PDF 第 87–92 段(逐段已讀)。家長團體對 ¶92 之回應本輪未查到一手資料,待查。"),
 E("A304","EV-2026-W23-06","2026-05-15","co_paragraph","CO 第 123–124 段:宗教自由——宗教團體登記與良心拒服兵役資格",
   "委員會關切宗教團體登記要求、國家對內部事務之監督與公開宗教活動限制(¶123);關切良心拒服兵役資格與官方登記宗教、心理評估之連結,以及私立學校宗教活動須真正自願並符合兒童權利(¶124)。",
   tags=["宗教自由"], pi=["PI-08"], co=["CO-4-123-FINAL","CO-4-124-FINAL"], art=["ICCPR-18"], pos=None, src=CO_PAGE,
   note="一手=CO PDF 第 123–124 段(逐段已讀)。"),
 E("A304","EV-2026-W23-07","2026-05-15","co_paragraph","CO 第 127 段:和平集會自由——禁制區/安全距離與許可制改報備制",
   "委員會關切集會遊行法「禁制區」「安全距離」規定可能與公政公約第 21 條及人權事務委員會第 37 號一般性意見不符,建議評估並諮詢公民社會,並建議以報備制取代許可制。",
   tags=["集會結社"], pi=["PI-12"], co=["CO-4-127-FINAL"], art=["ICCPR-21"], pos=None, src=CO_PAGE, note="一手=CO PDF 第 127 段(逐段已讀)。"),
 E("A312","EV-2026-W23-08","2026-06-11","outcome","總統府公布第 7 屆監察委員提名名單,國家人權委員會存續受關注",
   "第 6 屆監委任期 2026-07-31 屆滿;人權會委員由監委兼任,故監察院人事案成為人權會能否持續運作之前提。人權會副主委紀惠容 6/24 公開表示盼提名獲支持並主張修法使人權會完全獨立。",
   tags=["國家人權機構"], pi=["PI-07"], pos=None, src="https://udn.com/news/story/6656/9585399",
   note="提名人數「29」見 udn 報導;9/29 表決報導列 27 位被提名人(CNA),差異原因本輪未查明,待查。"),
 E("A602","EV-2026-W23-09","2026-08-17","govt_response","行政院人權保障推動小組第 52 次會議確認兩公約第四次結論性意見管考規劃",
   "依法務部 9/7 公告之管考規劃頁,管考規劃於 115 年 8 月 17 日經該小組第 52 次會議確認通過;框架為行政院 2022-09-21 頒布之共通性作業規範。",
   tags=["管考"], pi=["PI-03","PI-06"], pos=None, src=PLAN_PAGE, note="一手=法務部管考規劃公告頁(頁面文字已讀;附件 1–3 PDF 未讀)。"),
 E("A003","EV-2026-W23-10","2026-09-07","govt_response","法務部公布兩公約第四次 135 點結論性意見之落實及管考規劃",
   "將 135 點依議題整併、不逐點獨立列管;附件含各點權責機關表與各機關填寫之行動回應表空白格式。具體辦理期限本輪未取得(在附件內,未讀)。",
   tags=["管考"], pi=["PI-03","PI-06"], pos=None, src=PLAN_PAGE, note="發布 2026-09-07、最後更新 2026-09-22(頁面載明)。"),
 E("A503","EV-2026-W23-11","2026-09-29","legislation","立法院行使監察院人事同意權:院長、副院長及 25 位監委被提名人均未達 57 票門檻",
   "中央社 2026-09-29 報導:藍白兩黨團封殺,同意票確定無法達 57 票(全體立委過半);該報導發布時開票仍在進行、未列最終票數。",
   tags=["國家人權機構"], pi=["PI-07"], pos=None, src="https://cna.com.tw/news/aipl/202609290145.aspx",
   note="對人權會之後續影響本輪未查到一手資料,待查;勿推論人權會已停擺。"),
]

def main():
    dry = "--dry-run" in sys.argv
    cols = ("event_id","event_date","event_type","issue_tags","actor_id","title","summary","full_quote","source_url",
            "source_archive","related_pi","related_co","related_article","is_positive_outcome","note","created_at")
    conn = sqlite3.connect(DB); conn.execute("PRAGMA foreign_keys = ON")
    ins = sk = 0
    for e in EV:
        if dry:
            print(e["event_date"], e["event_id"], e["title"][:40]); continue
        cur = conn.execute(f"INSERT OR IGNORE INTO event ({','.join(cols)}) VALUES ({','.join('?'*len(cols))})", tuple(e[c] for c in cols))
        ins += cur.rowcount; sk += (1 - cur.rowcount)
    if not dry: conn.commit()
    print(f"events in script {len(EV)}; inserted {ins}; skipped {sk}")

if __name__ == "__main__":
    main()
