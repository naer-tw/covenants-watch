#!/usr/bin/env bash
# transcribe_audio.sh — 音檔(m4a/mp3/wav)轉中文逐字稿
# 兩種引擎:Groq Whisper API(預設,推薦)+ 本地 whisper.cpp(無 key 時 fallback)
#
# 用法:
#   bash scripts/transcribe_audio.sh /path/to/audio.m4a              # 自動選引擎
#   bash scripts/transcribe_audio.sh /path/to/audio.m4a groq         # 強制 Groq
#   bash scripts/transcribe_audio.sh /path/to/audio.m4a local        # 強制本地 small
#   bash scripts/transcribe_audio.sh /path/to/audio.m4a local medium # 本地 medium

set -euo pipefail
cd "$(dirname "$0")/.."

# SOP §3.2:轉錄完成(或失敗)時印倫理提示
ethics_warn() {
  cat <<'EOF' >&2

────────────────────────────────────────────────────────
⚠ 倫理提示(governance/transcript_citation_sop.md §3.2)
  本逐字稿含原始未校對內容,可能有:
  · Whisper 同音誤判(人名 / 機構名)
  · 受訪者對第三人之未經查證評價
  · 內部工作壓力 / 商業敏感之透露

  在引用至議題卡片或影子報告前必須:
  1. 製作中性摘要 *_制度面摘要.md(SOP §2.2)
  2. 評估受訪者書面同意狀況(SOP §2.3)
  3. 第三人姓名雙重核對(SOP §2.4)

  原始 .txt / .srt 不得直接 hyperlink 進議題卡片(SOP §2.1)
  詳見 governance/transcript_citation_sop.md
────────────────────────────────────────────────────────
EOF
}
trap ethics_warn EXIT

INPUT="${1:?請指定音檔路徑}"
ENGINE="${2:-auto}"          # auto / groq / local
LOCAL_MODEL="${3:-small}"    # tiny / base / small / medium / large-v3

GROQ_KEY_FILE="$HOME/.clawdbot/secrets/groq-key"
BASE=$(basename "$INPUT")
NAME="${BASE%.*}"
OUT_DIR="data/sources"
mkdir -p "$OUT_DIR"

# === auto 引擎判斷 ===
if [ "$ENGINE" = "auto" ]; then
  if [ -f "$GROQ_KEY_FILE" ] || [ -n "${GROQ_API_KEY:-}" ]; then
    ENGINE="groq"
  else
    ENGINE="local"
  fi
fi

# === GROQ 模式 ===
if [ "$ENGINE" = "groq" ]; then
  KEY="${GROQ_API_KEY:-$(cat "$GROQ_KEY_FILE" 2>/dev/null || true)}"
  [ -z "$KEY" ] && { echo "❌ Groq key 未找到(預期在 $GROQ_KEY_FILE 或 \$GROQ_API_KEY)"; exit 1; }
  SIZE=$(stat -f%z "$INPUT" 2>/dev/null || stat -c%s "$INPUT")

  if [ "$SIZE" -gt 25000000 ]; then
    # 超過 25MB,先壓成 mp3 q4
    echo "▶ 檔案 $((SIZE/1024/1024))MB 超過 Groq 25MB 上限,先壓 mp3..."
    MP3="/tmp/${NAME}_compressed.mp3"
    ffmpeg -y -i "$INPUT" -vn -acodec libmp3lame -q:a 4 "$MP3" 2>&1 | tail -1
    NEW_SIZE=$(stat -f%z "$MP3" 2>/dev/null || stat -c%s "$MP3")
    if [ "$NEW_SIZE" -gt 25000000 ]; then
      # 仍超過,分段(每段 20 分鐘)
      echo "▶ 壓縮後仍 $((NEW_SIZE/1024/1024))MB,分 20 分鐘段..."
      DURATION=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$INPUT" 2>/dev/null | awk '{print int($1)}')
      SEGMENTS=$((DURATION / 1200 + 1))
      > "$OUT_DIR/${NAME}_groq.txt"
      for i in $(seq 0 $((SEGMENTS - 1))); do
        START=$((i * 1200))
        SEG="/tmp/${NAME}_seg_$i.mp3"
        echo "  段 $((i+1))/$SEGMENTS..."
        ffmpeg -y -i "$INPUT" -ss $START -t 1200 -vn -acodec libmp3lame -q:a 4 "$SEG" 2>/dev/null
        curl -s -X POST "https://api.groq.com/openai/v1/audio/transcriptions" \
          -H "Authorization: Bearer $KEY" \
          -F "file=@$SEG" \
          -F "model=whisper-large-v3" \
          -F "language=zh" \
          -F "response_format=text" \
          --max-time 120 \
          >> "$OUT_DIR/${NAME}_groq.txt"
        echo "" >> "$OUT_DIR/${NAME}_groq.txt"
      done
      echo "✓ ${OUT_DIR}/${NAME}_groq.txt"
      exit 0
    fi
    INPUT="$MP3"
  fi

  echo "▶ Groq whisper-large-v3 轉錄(預估 < 10s)..."
  RESP=$(curl -s -X POST "https://api.groq.com/openai/v1/audio/transcriptions" \
    -H "Authorization: Bearer $KEY" \
    -F "file=@$INPUT" \
    -F "model=whisper-large-v3" \
    -F "language=zh" \
    -F "response_format=verbose_json" \
    --max-time 120)
  echo "$RESP" > "$OUT_DIR/${NAME}_groq.json"
  python3 -c "
import json, sys
data = json.load(open('$OUT_DIR/${NAME}_groq.json'))
text = data.get('text', '')
open('$OUT_DIR/${NAME}_groq.txt', 'w').write(text)
def fmt(s): h=int(s//3600); m=int((s%3600)//60); sec=s%60; return f'{h:02d}:{m:02d}:{sec:06.3f}'.replace('.', ',')
srt = []
for i, seg in enumerate(data.get('segments', []), 1):
    srt.append(f\"{i}\n{fmt(seg['start'])} --> {fmt(seg['end'])}\n{seg['text'].strip()}\n\")
open('$OUT_DIR/${NAME}_groq.srt', 'w').write('\n'.join(srt))
print(f'✓ {len(text)} 字、{len(data.get(\"segments\", []))} segments')
"
  echo "✓ ${OUT_DIR}/${NAME}_groq.txt + .srt"
  exit 0
fi

# === LOCAL whisper.cpp 模式 ===
MODEL=".whisper-models/ggml-${LOCAL_MODEL}.bin"
if [ ! -f "$MODEL" ]; then
  echo "▶ 下載 ${LOCAL_MODEL} 模型..."
  mkdir -p .whisper-models
  curl -fsL -o "$MODEL" \
    "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-${LOCAL_MODEL}.bin"
fi
WAV="/tmp/${NAME}.wav"
echo "▶ 轉 wav 16kHz..."
ffmpeg -y -i "$INPUT" -ar 16000 -ac 1 -c:a pcm_s16le "$WAV" 2>&1 | tail -1
echo "▶ 本地 whisper-cpp 轉錄(${LOCAL_MODEL} 模型)..."
whisper-cli -m "$MODEL" -f "$WAV" -l zh --output-txt --output-srt -of "/tmp/${NAME}"
mv "/tmp/${NAME}.txt" "${OUT_DIR}/${NAME}_whisper-${LOCAL_MODEL}.txt"
mv "/tmp/${NAME}.srt" "${OUT_DIR}/${NAME}_whisper-${LOCAL_MODEL}.srt"
echo "✓ ${OUT_DIR}/${NAME}_whisper-${LOCAL_MODEL}.txt"
