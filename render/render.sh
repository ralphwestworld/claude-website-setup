#!/usr/bin/env bash
# Render the Buckeye Law Group :30 commercial via JSON2Video API.
#
# Prereqs:
#   1. JSON2Video account + API key (https://json2video.com — free tier covers a 30s render)
#   2. Voice recording uploaded somewhere with a public URL (Drive share link, Dropbox, S3)
#   3. Stock B-roll clip URLs filled into commercial.json (six PASTE_STOCK_URL_SCENE*.mp4 slots)
#   4. Buckeye logo PNG URL filled into commercial.json (PASTE_LOGO_URL.png slot)
#
# Usage:
#   export JSON2VIDEO_API_KEY="your-key-here"
#   ./render/render.sh
#
# The script submits the movie spec, polls for completion, and prints the
# final MP4 URL when ready.

set -euo pipefail

JSON_FILE="$(dirname "$0")/commercial.json"

if [[ -z "${JSON2VIDEO_API_KEY:-}" ]]; then
  echo "ERROR: set JSON2VIDEO_API_KEY env var first" >&2
  exit 1
fi

if grep -q "PASTE_" "$JSON_FILE"; then
  echo "ERROR: commercial.json still has PASTE_* placeholders. Fill them in first." >&2
  echo "Unfilled slots:" >&2
  grep -n "PASTE_" "$JSON_FILE" >&2
  exit 1
fi

echo "Submitting movie spec to JSON2Video..."
SUBMIT=$(curl -sS -X POST "https://api.json2video.com/v2/movies" \
  -H "x-api-key: ${JSON2VIDEO_API_KEY}" \
  -H "Content-Type: application/json" \
  --data-binary "@${JSON_FILE}")

PROJECT=$(echo "$SUBMIT" | python3 -c "import sys,json;print(json.load(sys.stdin)['project'])")
echo "Project: $PROJECT — polling for completion..."

while true; do
  STATUS=$(curl -sS "https://api.json2video.com/v2/movies?project=${PROJECT}" \
    -H "x-api-key: ${JSON2VIDEO_API_KEY}")
  STATE=$(echo "$STATUS" | python3 -c "import sys,json;print(json.load(sys.stdin)['movie']['status'])")
  echo "  status: $STATE"
  if [[ "$STATE" == "done" ]]; then
    URL=$(echo "$STATUS" | python3 -c "import sys,json;print(json.load(sys.stdin)['movie']['url'])")
    echo ""
    echo "Render complete:"
    echo "$URL"
    exit 0
  fi
  if [[ "$STATE" == "error" ]]; then
    echo "$STATUS" >&2
    exit 1
  fi
  sleep 5
done
