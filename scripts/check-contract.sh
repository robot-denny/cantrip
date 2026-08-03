#!/usr/bin/env bash
#
# check-contract.sh — the automated half of every Cantrip checkpoint.
#
# Enforces the layer contract (docs/contract.md, ADR 0001) and the packaging shape
# (ADR 0002) so a human reviewing an extracted file only has to read the failures.
#
# Usage:  scripts/check-contract.sh [--verbose]
# Exit:   0 = clean, 1 = one or more violations
#
# Checks 1 is repo-wide, because "public from day one, no private staging period" applies
# to every file here, not just shipped skills. Checks 2-6 apply to shipped units only.

set -uo pipefail
cd "$(dirname "$0")/.." || exit 2

VERBOSE=0
[[ "${1:-}" == "--verbose" ]] && VERBOSE=1

FAILURES=0
CHECKS_RUN=0

# Shipped units — what actually installs into a consuming project.
SHIPPED_DIRS=(skills agents)
# Repo-wide scan skips itself (it necessarily names the patterns it hunts for) and git internals.
PRUNE=(-name .git -o -name node_modules -o -path ./scripts)

report_fail() {
  FAILURES=$((FAILURES + 1))
  printf '\n\033[31mFAIL\033[0m  %s\n' "$1"
  shift
  local msg
  for msg in "$@"; do
    if [[ -z "$msg" ]]; then
      printf '\n'
    else
      # Indent every line, so multi-line hit lists stay readable.
      printf '%s\n' "$msg" | sed 's/^/      /'
    fi
  done
}

report_pass() {
  [[ $VERBOSE -eq 1 ]] && printf '\033[32mok\033[0m    %s\n' "$1"
  return 0
}

begin() {
  CHECKS_RUN=$((CHECKS_RUN + 1))
  CURRENT="$1"
}

# Collect files, honoring prunes. Prints nothing if none exist yet.
repo_md_files() {
  find . \( "${PRUNE[@]}" \) -prune -o -name '*.md' -type f -print 2>/dev/null
}

shipped_md_files() {
  local d
  for d in "${SHIPPED_DIRS[@]}"; do
    [[ -d "$d" ]] && find "$d" -name '*.md' -type f -print 2>/dev/null
  done
}

skill_files() {
  [[ -d skills ]] && find skills -name 'SKILL.md' -type f -print 2>/dev/null
}

# ---------------------------------------------------------------------------
# 1. Client-identifying information — repo-wide, the hard gate
# ---------------------------------------------------------------------------
begin "no client-identifying information (repo-wide)"
CLIENT_PATTERN='kittitas|wearediagram|diagram-et|CCASyndication|robotregime|scm\.umbraco\.io'
hits=$(repo_md_files | xargs grep -inE "$CLIENT_PATTERN" 2>/dev/null)
if [[ -n "$hits" ]]; then
  report_fail "$CURRENT" \
    "Client-identifying terms found. This repo is public with no staging period —" \
    "scrub before committing (see AGENTS.md)." \
    "" "$hits"
else
  report_pass "$CURRENT"
fi

# ---------------------------------------------------------------------------
# 2. Absolute paths and home references — shipped units
# ---------------------------------------------------------------------------
begin "no absolute paths in shipped units"
hits=$(shipped_md_files | xargs grep -inE '/Users/|/home/[a-z]|\$HOME|~/\.|[A-Z]:\\\\' 2>/dev/null)
if [[ -n "$hits" ]]; then
  report_fail "$CURRENT" \
    "Absolute or home-relative paths belong in the stack.md slot, not a shipped file." \
    "" "$hits"
else
  report_pass "$CURRENT"
fi

# ---------------------------------------------------------------------------
# 3. Hostnames and ports — shipped units
# ---------------------------------------------------------------------------
begin "no hostnames or ports in shipped units"
hits=$(shipped_md_files | xargs grep -inE 'localhost:[0-9]+|127\.0\.0\.1|https?://[a-z0-9.-]+\.(local|test|dev)\b' 2>/dev/null)
if [[ -n "$hits" ]]; then
  report_fail "$CURRENT" \
    "Local URLs are project facts — move to the stack.md slot." \
    "" "$hits"
else
  report_pass "$CURRENT"
fi

# ---------------------------------------------------------------------------
# 4. Every **Slot:** has an adjacent **If empty:** — the contract's core rule
# ---------------------------------------------------------------------------
begin "every slot reference has a fallback"
unpaired=""
while IFS= read -r f; do
  [[ -z "$f" ]] && continue
  # For each **Slot:** line, require **If empty:** within the next 3 lines.
  while IFS=: read -r lineno _; do
    [[ -z "$lineno" ]] && continue
    window=$(sed -n "${lineno},$((lineno + 3))p" "$f")
    if ! grep -q '\*\*If empty:\*\*' <<<"$window"; then
      unpaired+="$f:$lineno: **Slot:** with no **If empty:** within 3 lines"$'\n'
    fi
  done < <(grep -n '\*\*Slot:\*\*' "$f" 2>/dev/null)
done < <(shipped_md_files)
if [[ -n "$unpaired" ]]; then
  report_fail "$CURRENT" \
    "A slot without a fallback turns an unfilled slot into a broken spell (ADR 0001)." \
    "" "$unpaired"
else
  report_pass "$CURRENT"
fi

# ---------------------------------------------------------------------------
# 5. Invocation posture matches directory taxonomy (ADR 0002)
# ---------------------------------------------------------------------------
begin "invocation posture matches taxonomy"
posture_errs=""
while IFS= read -r f; do
  [[ -z "$f" ]] && continue
  has_disable=$(grep -c '^disable-model-invocation:[[:space:]]*true' "$f" 2>/dev/null || true)
  case "$f" in
    */spellbook/*)
      [[ "$has_disable" -eq 0 ]] && \
        posture_errs+="$f: spell missing 'disable-model-invocation: true' (would be model-visible)"$'\n' ;;
    */reference/*)
      [[ "$has_disable" -gt 0 ]] && \
        posture_errs+="$f: reference sets 'disable-model-invocation: true' (would never load)"$'\n' ;;
  esac
done < <(skill_files)
if [[ -n "$posture_errs" ]]; then
  report_fail "$CURRENT" \
    "Verbs are spells (user-cast only), nouns are reference (model-invoked)." \
    "" "$posture_errs"
else
  report_pass "$CURRENT"
fi

# ---------------------------------------------------------------------------
# 6. Frontmatter completeness
# ---------------------------------------------------------------------------
begin "skill frontmatter is complete"
fm_errs=""
while IFS= read -r f; do
  [[ -z "$f" ]] && continue
  head -1 "$f" | grep -q '^---$' || { fm_errs+="$f: missing opening frontmatter delimiter"$'\n'; continue; }
  grep -q '^name:[[:space:]]*[^[:space:]]' "$f" || fm_errs+="$f: no 'name:' in frontmatter"$'\n'
  desc=$(grep -m1 '^description:[[:space:]]*' "$f" | sed 's/^description:[[:space:]]*//')
  if [[ -z "$desc" ]]; then
    fm_errs+="$f: no 'description:' in frontmatter"$'\n'
  elif [[ ${#desc} -lt 40 ]]; then
    fm_errs+="$f: description is ${#desc} chars — too thin to trigger reliably"$'\n'
  fi
  # Directory name should match the declared skill name, since install flattens by name.
  dir=$(basename "$(dirname "$f")")
  name=$(grep -m1 '^name:[[:space:]]*' "$f" | sed 's/^name:[[:space:]]*//' | tr -d '\r')
  [[ -n "$name" && "$name" != "$dir" ]] && \
    fm_errs+="$f: name '$name' does not match directory '$dir'"$'\n'
done < <(skill_files)
if [[ -n "$fm_errs" ]]; then
  report_fail "$CURRENT" "" "$fm_errs"
else
  report_pass "$CURRENT"
fi

# ---------------------------------------------------------------------------
# 7. No loose files at a shipped skill root (ADR 0002)
# ---------------------------------------------------------------------------
begin "no loose markdown outside a skill directory"
loose=""
for tier in skills/core/spellbook skills/core/reference; do
  [[ -d "$tier" ]] || continue
  while IFS= read -r f; do
    [[ -z "$f" ]] && continue
    loose+="$f: loose file — every shipped unit is a skill directory with a SKILL.md"$'\n'
  done < <(find "$tier" -maxdepth 1 -name '*.md' -type f -print 2>/dev/null)
done
if [[ -n "$loose" ]]; then
  report_fail "$CURRENT" "" "$loose"
else
  report_pass "$CURRENT"
fi

# ---------------------------------------------------------------------------
# 8. No technology names in L0 core (ADR 0003)
# ---------------------------------------------------------------------------
# L1 packs name their technology freely; core must not. Core asks for a *kind* of
# guidance and lets skill discovery route it to whichever pack can answer.
begin "no technology names in L0 core"
TECH_PATTERN='umbraco|\.uda\b|razor|cshtml|\bvue\b|dotnet|\bnpm\b|\bnpx\b|playwright|backoffice|modelsbuilder|app_plugins|mcp__|xunit|\bvite\b|tailwind|\bc#'
if [[ -d skills/core ]]; then
  hits=$(find skills/core -name '*.md' -type f -print0 2>/dev/null | xargs -0 grep -inE "$TECH_PATTERN" 2>/dev/null)
  if [[ -n "$hits" ]]; then
    report_fail "$CURRENT" \
      "L0 must ask for a KIND of guidance, not name a technology (ADR 0003)." \
      "Move the fact to a stack pack under skills/<pack>/, or generalize the wording." \
      "" "$hits"
  else
    report_pass "$CURRENT"
  fi
else
  report_pass "$CURRENT"
fi

# ---------------------------------------------------------------------------
printf '\n'
if [[ $FAILURES -eq 0 ]]; then
  printf '\033[32m%s checks passed.\033[0m\n' "$CHECKS_RUN"
  exit 0
fi
printf '\033[31m%d of %d checks failed.\033[0m\n' "$FAILURES" "$CHECKS_RUN"
exit 1
