#!/usr/bin/env bash
# detect-stage.sh — classify codebase lifecycle stage.
# Heuristic — when uncertain, prints "ambiguous" so the skill asks the user.
# Read-only.
# Usage: detect-stage.sh <target-dir>
# Output: one of: greenfield | growing | mature | brownfield | ambiguous

set -u

TARGET="${1:-.}"

if [ ! -d "$TARGET" ]; then
  echo "ERROR: target directory not found: $TARGET" >&2
  exit 1
fi

cd "$TARGET" || exit 1

# Brownfield isn't automatically detectable from signals alone — the user has to declare
# they inherited the codebase. This script doesn't try; it returns greenfield/growing/mature/ambiguous
# and lets the user override with --stage brownfield.

if [ ! -d ".git" ]; then
  # No git history — fall back to file-count heuristics
  CS_FILES=$(find . -name "*.cs" \
    -not -path "*/bin/*" -not -path "*/obj/*" -not -path "*/TEMP/*" \
    -not -path "*/node_modules/*" 2>/dev/null | wc -l | tr -d ' ')
  if [ "$CS_FILES" -lt 10 ]; then
    echo "greenfield"
  elif [ "$CS_FILES" -lt 100 ]; then
    echo "growing"
  else
    echo "ambiguous"
  fi
  exit 0
fi

# Git-based signals
FIRST_COMMIT_DATE=$(git log --reverse --format=%cI 2>/dev/null | head -1)
LAST_COMMIT_DATE=$(git log -1 --format=%cI 2>/dev/null)
COMMIT_COUNT=$(git rev-list --count HEAD 2>/dev/null || echo 0)
CONTRIB_COUNT=$(git shortlog -sn --all 2>/dev/null | wc -l | tr -d ' ')

if [ -z "$FIRST_COMMIT_DATE" ]; then
  echo "ambiguous"
  exit 0
fi

# Compute age in days from first commit
# macOS `date -j -f` and GNU `date -d` differ; try both.
NOW_EPOCH=$(date +%s)
if FIRST_EPOCH=$(date -j -f "%Y-%m-%dT%H:%M:%S%z" "${FIRST_COMMIT_DATE%??}+0000" "+%s" 2>/dev/null); then
  :
elif FIRST_EPOCH=$(date -d "$FIRST_COMMIT_DATE" "+%s" 2>/dev/null); then
  :
else
  FIRST_EPOCH=
fi

if [ -z "$FIRST_EPOCH" ]; then
  echo "ambiguous"
  exit 0
fi

AGE_DAYS=$(( (NOW_EPOCH - FIRST_EPOCH) / 86400 ))

# Recent activity in last 30 days (proxy for "active" vs "stale")
RECENT_COMMITS=$(git log --since="30 days ago" --format=%H 2>/dev/null | wc -l | tr -d ' ')

# Classification rules
#
#   Greenfield: first commit ≤ 60 days ago AND ≤ 50 commits total
#   Growing:    < 12 months OR active in last 30 days AND > 50 commits
#   Mature:     ≥ 12 months AND > 50 commits AND low recent structural churn
#   Else:       ambiguous (let the user choose)
#
# Brownfield is user-declared. The skill never auto-classifies brownfield from heuristics alone.

if [ "$AGE_DAYS" -lt 60 ] && [ "$COMMIT_COUNT" -lt 50 ]; then
  echo "greenfield"
  exit 0
fi

if [ "$AGE_DAYS" -ge 365 ] && [ "$COMMIT_COUNT" -gt 50 ] && [ "$RECENT_COMMITS" -lt 10 ]; then
  echo "mature"
  exit 0
fi

if [ "$RECENT_COMMITS" -gt 0 ] && [ "$COMMIT_COUNT" -gt 50 ]; then
  echo "growing"
  exit 0
fi

# Inconclusive
echo "ambiguous"
