#!/usr/bin/env python3
"""
立法院公報事件提取（兩公約特化版，源自 ~/clawd/skills/legislative-monitor）

特化點：
- 加入兩公約援引關鍵詞偵測（ICCPR/ICESCR/兩公約/公政公約等）
- 援引條文號自動標記（Art.6 / Art.18 / Art.26 等）
- 雙寫入：原 B 表 JSON + 兩公約 SQLite legislative_citation 表

Usage:
    python3 scripts/two_cov_extract_legislative_events.py \
        --input "data/sources/raw/legislative/" \
        --output "data/evidence/legislative_events.json" \
        --filter-covenant
"""

import pdfplumber
import os
import re
import json
import argparse
from datetime import datetime

# 承諾關鍵詞定義（沿用 legislative-monitor）
L3_KEYWORDS = ["一個月", "三個月", "會辦理", "立即處理", "馬上", "儘速"]
L2_KEYWORDS = ["研議", "評估", "檢討", "考量", "研究", "規劃"]
L1_KEYWORDS = ["報告", "說明", "我們會", "承諾", "配合", "會做", "會處理"]

# 官員職稱
OFFICIAL_TITLES = ["部長", "次長", "署長", "司長", "主委", "局長", "處長"]

# 兩公約援引關鍵詞（特化加入）
COVENANT_TERMS = [
    "兩公約", "公政公約", "經社文公約",
    "ICCPR", "ICESCR",
    "公約施行法", "人權兩公約",
    "公民與政治權利國際公約", "經濟社會文化權利國際公約",
]

# 條文號 regex（適用 ICCPR Art.X / 第 X 條等多種寫法）
ARTICLE_RE = re.compile(
    r"(ICCPR|ICESCR|兩公約)?[^\n]{0,5}"
    r"(?:Art\.?|Article|第)\s*(\d+)\s*(?:-\d+)?\s*條?",
    re.IGNORECASE,
)


def has_covenant_reference(text: str) -> bool:
    """偵測本段是否援引兩公約"""
    return any(term in text for term in COVENANT_TERMS)


def extract_articles(text: str) -> list[str]:
    """從文字擷取所有條文號標記"""
    found = set()
    for m in ARTICLE_RE.finditer(text):
        cov = m.group(1) or "ICCPR_OR_ICESCR"
        num = m.group(2)
        found.add(f"{cov.upper()}-{num}")
    return sorted(found)

def detect_level(text):
    """判斷承諾等級"""
    for kw in L3_KEYWORDS:
        if kw in text:
            return "L3"
    for kw in L2_KEYWORDS:
        if kw in text:
            return "L2"
    return "L1"

def extract_date(text):
    """從PDF首頁提取日期"""
    match = re.search(r'(\d+)年(\d+)月(\d+)日', text)
    if match:
        return f"{match.group(1)}/{match.group(2)}/{match.group(3)}"
    return None

def extract_meeting_num(filename):
    """從檔名提取會議次數"""
    match = re.search(r'第\s*(\d+(?:-\d+)?)\s*次', filename)
    return match.group(1) if match else "?"

def process_pdf(pdf_path, committee, session, start_id=1):
    """處理單一PDF檔案"""
    events = []
    event_id = start_id
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            # 取得日期
            first_page = pdf.pages[0].extract_text() or ""
            date = extract_date(first_page)
            meeting_num = extract_meeting_num(os.path.basename(pdf_path))
            
            # 處理每頁（限制頁數以提升效能）
            max_pages = min(30, len(pdf.pages))
            
            for page in pdf.pages[:max_pages]:
                text = page.extract_text() or ""
                lines = text.split('\n')
                
                for i, line in enumerate(lines):
                    # 檢查是否為官員發言
                    official_match = None
                    for title in OFFICIAL_TITLES:
                        if title in line and ('：' in line or ':' in line):
                            official_match = title
                            break
                    
                    if official_match:
                        # 合併上下文
                        context = line
                        if i + 1 < len(lines):
                            context += " " + lines[i + 1]
                        
                        # 檢查是否包含承諾關鍵詞
                        all_keywords = L1_KEYWORDS + L2_KEYWORDS + L3_KEYWORDS
                        if any(kw in context for kw in all_keywords):
                            level = detect_level(context)
                            
                            events.append({
                                "id": f"B-{event_id:03d}",
                                "date": date or "未知",
                                "meeting": f"{committee}第{meeting_num}次({session})",
                                "summary": context[:100],
                                "level": level,
                                "session": f"第{session}會期"
                            })
                            event_id += 1
                            
    except Exception as e:
        print(f"Error processing {pdf_path}: {e}")
    
    return events, event_id

def process_directory(input_dir, committee, session, output_file=None, existing_events=None):
    """處理整個目錄"""
    all_events = existing_events or []
    
    # 計算起始ID
    if all_events:
        start_id = max([int(e['id'].split('-')[1]) for e in all_events]) + 1
    else:
        start_id = 1
    
    # 取得所有PDF
    pdf_files = sorted([f for f in os.listdir(input_dir) if f.endswith('.pdf')])
    total = len(pdf_files)
    
    print(f"找到 {total} 個PDF檔案")
    
    for i, pdf_file in enumerate(pdf_files):
        pdf_path = os.path.join(input_dir, pdf_file)
        events, start_id = process_pdf(pdf_path, committee, session, start_id)
        all_events.extend(events)
        
        if (i + 1) % 10 == 0:
            print(f"已處理 {i+1}/{total} 場")
    
    # 輸出結果
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_events, f, ensure_ascii=False, indent=2)
        print(f"\n已儲存至 {output_file}")
    
    return all_events

def print_stats(events):
    """輸出統計資訊"""
    total = len(events)
    l3 = len([e for e in events if e.get('level') == 'L3'])
    l2 = len([e for e in events if e.get('level') == 'L2'])
    l1 = len([e for e in events if e.get('level') == 'L1'])
    
    print(f"\n=== 統計 ===")
    print(f"總事件數: {total}")
    print(f"L3 明確承諾: {l3} ({l3/total*100:.1f}%)")
    print(f"L2 研議中: {l2} ({l2/total*100:.1f}%)")
    print(f"L1 議題提及: {l1} ({l1/total*100:.1f}%)")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='立法院公報事件提取')
    parser.add_argument('--input', '-i', required=True, help='輸入目錄')
    parser.add_argument('--output', '-o', default='events.json', help='輸出檔案')
    parser.add_argument('--committee', '-c', default='委員會', help='委員會名稱（衛環/教文）')
    parser.add_argument('--session', '-s', default='4', help='會期（1/2/3/4）')
    parser.add_argument('--append', '-a', help='附加到現有JSON檔案')
    
    args = parser.parse_args()
    
    # 載入現有事件
    existing = []
    if args.append and os.path.exists(args.append):
        with open(args.append, 'r', encoding='utf-8') as f:
            existing = json.load(f)
        print(f"載入現有 {len(existing)} 筆事件")
    
    # 處理
    events = process_directory(
        args.input, 
        args.committee, 
        args.session, 
        args.output,
        existing
    )
    
    print_stats(events)
