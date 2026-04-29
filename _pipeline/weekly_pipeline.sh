#!/usr/bin/env bash
# weekly_pipeline.sh — IDEATECH LLMO weekly orchestration (in-repo layout).
#
# Layout: this script lives at <repo>/_pipeline/weekly_pipeline.sh.
# It builds <repo>/index.html (the GitHub Pages site) and commits/pushes it.
#
# The scheduled-task session is expected to:
#   1) call ahrefs Brand Radar MCP for chatgpt and save JSON to /tmp/br/br_chatgpt.json
#   2) git clone https://github.com/hibiki-nabetani-ideatech/ideatech-llmo-dashboard.git
#   3) cd into the clone and run `_pipeline/weekly_pipeline.sh`
#
# Steps:
#   1) snapshot _pipeline/data_v3.json → _pipeline/data_v3_prev.json
#   2) merge Brand Radar responses into _pipeline/data_v3.json
#   3) compute the diff
#   4) build the HTML dashboard → ../index.html (repo root)
#   5) commit + push (data + html)
#   6) ChatWork notification
#
# Required env vars (for live operation):
#   CHATWORK_API_TOKEN   — ChatWork API token
#   CHATWORK_ROOM_ID     — destination room ID
# Optional:
#   BR_DIR               — directory containing br_<llm>.json (default /tmp/br)
#   DASHBOARD_URL        — public URL (default GitHub Pages link)
#   SKIP_NOTIFY=1        — skip the ChatWork POST (for testing)
#   SKIP_DEPLOY=1        — skip git push (for testing)

set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"             # <repo>/_pipeline
SITE_DIR="$(cd "$ROOT/.." && pwd)"                # <repo>
cd "$ROOT"

BR_DIR="${BR_DIR:-/tmp/br}"
ASOF="$(date '+%Y-%m-%d %H:%M JST')"

echo "=== weekly_pipeline @ $ASOF ==="
echo "    ROOT=$ROOT"
echo "    SITE_DIR=$SITE_DIR"

# 1) Snapshot
if [[ -f data_v3.json ]]; then
  cp data_v3.json data_v3_prev.json
  echo "[1/7] snapshot: data_v3.json → data_v3_prev.json"
else
  echo "ERR: data_v3.json missing in $ROOT" >&2
  exit 1
fi

# 2) Merge Brand Radar (skip if no input dir / no files)
if [[ -d "$BR_DIR" ]] && ls "$BR_DIR"/*.json >/dev/null 2>&1; then
  echo "[2/7] merging Brand Radar from $BR_DIR …"
  python3 merge_brand_radar.py --in-dir "$BR_DIR"
else
  echo "[2/7] WARN: no Brand Radar files in $BR_DIR — skipping merge"
fi

# 3) Fetch ⑤ AI Topics (skip silently if ANTHROPIC_API_KEY unset; keeps prior entries on any error)
echo "[3/7] fetching AI Topics …"
python3 fetch_ai_topics.py || echo "[3/7] WARN: fetch_ai_topics.py exited non-zero; continuing"

# 4) Diff
echo "[4/7] computing diff …"
python3 compute_diff.py

# 5) Build HTML directly into repo root
echo "[5/7] building HTML …"
python3 build_html_v3.py --out "$SITE_DIR/index.html"

# 6) Deploy
if [[ -z "${SKIP_DEPLOY:-}" ]]; then
  echo "[6/7] committing & pushing …"
  cd "$SITE_DIR"
  git add index.html _pipeline/data_v3.json _pipeline/data_v3_prev.json
  if ! git diff --cached --quiet; then
    git -c user.name="ideatech-llmo-bot" -c user.email="bot@ideatech.local" \
        commit -m "weekly: $(date '+%Y-%m-%d') data refresh"
    git push
    echo "[6/7] pushed"
  else
    echo "[6/7] no diff — skipping commit"
  fi
  cd "$ROOT"
else
  echo "[6/7] SKIP_DEPLOY set — skipping push"
fi

# 7) Notify
if [[ -z "${SKIP_NOTIFY:-}" ]]; then
  if [[ -n "${CHATWORK_API_TOKEN:-}" && -n "${CHATWORK_ROOM_ID:-}" ]]; then
    echo "[7/7] sending ChatWork notification …"
    python3 chatwork_notify.py
  else
    echo "[7/7] WARN: CHATWORK_API_TOKEN / CHATWORK_ROOM_ID unset — skipping notify"
  fi
else
  echo "[7/7] SKIP_NOTIFY set — skipping ChatWork"
fi

echo "=== done ==="
