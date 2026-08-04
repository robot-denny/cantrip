#!/usr/bin/env bash
# compare-repos.sh — merge two completed audit reports into a head-to-head comparison.
# Read-only on the input reports; emits a comparison section on stdout that the skill
# can splice into the final report.
# Usage: compare-repos.sh <report-a.md> <report-b.md>

set -u

A="${1:-}"
B="${2:-}"

if [ -z "$A" ] || [ -z "$B" ]; then
  echo "Usage: compare-repos.sh <report-a.md> <report-b.md>" >&2
  exit 1
fi

if [ ! -f "$A" ] || [ ! -f "$B" ]; then
  echo "ERROR: one or both report files do not exist" >&2
  exit 1
fi

extract_score() {
  # $1 = report file, $2 = pillar number
  grep -E "^\| $2 \|" "$1" | head -1 | awk -F'|' '{gsub(/^ +| +$/, "", $4); print $4}'
}

extract_name() {
  # Heuristic: use the line after "# Architecture Audit —"
  head -3 "$1" | grep -E "^# " | head -1 | sed 's/^# Architecture Audit — //'
}

NAME_A=$(extract_name "$A")
NAME_B=$(extract_name "$B")

[ -z "$NAME_A" ] && NAME_A=$(basename "$A" .md)
[ -z "$NAME_B" ] && NAME_B=$(basename "$B" .md)

cat <<EOF

## Comparison — $NAME_A vs $NAME_B

### Side-by-side scores

| Pillar | $NAME_A | $NAME_B |
|---|---|---|
| 1 — Modern .NET hygiene | $(extract_score "$A" 1) | $(extract_score "$B" 1) |
| 2 — Architectural separation | $(extract_score "$A" 2) | $(extract_score "$B" 2) |
| 3 — Umbraco-version-appropriate | $(extract_score "$A" 3) | $(extract_score "$B" 3) |
| 4 — Headless suitability | $(extract_score "$A" 4) | $(extract_score "$B" 4) |
| 5 — Documentation & onboarding | $(extract_score "$A" 5) | $(extract_score "$B" 5) |
| 6 — Resilience & operations | $(extract_score "$A" 6) | $(extract_score "$B" 6) |
| 7 — Scalability & refactorability | $(extract_score "$A" 7) | $(extract_score "$B" 7) |

### What to learn from each

> The skill should fill in this section by reading both reports and synthesizing 2–4 bullets per repo —
> "what does this codebase do that the other should consider adopting?"

- **From $NAME_A**:
  - <synthesize from $A's strengths>
- **From $NAME_B**:
  - <synthesize from $B's strengths>

### Pros / cons per pillar

> Per-pillar narrative comparing the two. Write 2–3 sentences each, naming the winner and why.
> Use the strengths/weaknesses captured in each audit's pillar section as input.

- **Pillar 1**: <narrative>
- **Pillar 2**: <narrative>
- **Pillar 3**: <narrative>
- **Pillar 4**: <narrative>
- **Pillar 5**: <narrative>
- **Pillar 6**: <narrative>
- **Pillar 7**: <narrative>

EOF
