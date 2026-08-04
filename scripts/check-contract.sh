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
# Check 1 is repo-wide, because "public from day one, no private staging period" applies
# to every file here, not just shipped skills. Checks 2-10 apply to shipped units only.
# Check 12 spans both: it pairs a declaration inside a shipped pack against the README.
#
# Checks 11 and 13 are the exceptions in the other direction — they inspect this repo rather
# than what it ships. Both guard a hardcoded list that has to be kept in step with
# skills/core by hand: 11 the self-hosting symlinks, 13 the install checker's roster. Each
# was added after that list had already drifted, and each drifted in the same silent way,
# reporting success for a skill that was not there.

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
# Everything a leak could hide in -- not only markdown. A client name in a script, a
# lockfile, or an eval fixture is the same leak; only the extension differs.
#
# Scoped to what could actually be PUBLISHED: tracked files plus untracked-but-not-ignored
# ones. A git-ignored file cannot leak, and scanning it produces noise about something
# unpublishable -- which is how this scan first reported the git-ignored local settings
# file that legitimately names a source repo path.
repo_md_files() {
  if git rev-parse --git-dir >/dev/null 2>&1; then
    { git ls-files; git ls-files --others --exclude-standard; } 2>/dev/null \
      | grep -E '\.(md|json|sh|py|txt)$|(^|/)LICENSE$' \
      | grep -vE '^scripts/check-contract\.sh$'
  else
    find . \( "${PRUNE[@]}" \) -prune -o -type f \
      \( -name '*.md' -o -name '*.json' -o -name '*.sh' -o -name '*.py' -o -name '*.txt' -o -name 'LICENSE' \) \
      -print 2>/dev/null
  fi
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

# A file may exempt specific patterns with an auditable inline declaration:
#   <!-- contract-allow: <pattern> — reason -->
# Honored by both scrub checks (1 and 8). Needed because the documents that DEFINE these
# rules necessarily quote the terms they forbid -- AGENTS.md's naming table and the
# contract's own checklist both matched on the first exhaustive sweep.
allowed_patterns_for() {
  grep -oE '<!--[[:space:]]*contract-allow:[[:space:]]*[^ ]+' "$1" 2>/dev/null \
    | sed -e 's/.*contract-allow:[[:space:]]*//' | paste -sd'|' -
}

# Grep a file for a pattern, minus anything it has exempted.
grep_unexempted() {   # grep_unexempted <file> <pattern>
  local f="$1" pat="$2" allowed
  allowed=$(allowed_patterns_for "$f")
  if [[ -n "$allowed" ]]; then
    grep -inE "$pat" "$f" 2>/dev/null | grep -viE "$allowed" | sed "s|^|$f:|"
  else
    grep -inE "$pat" "$f" 2>/dev/null | sed "s|^|$f:|"
  fi
}

# ---------------------------------------------------------------------------
# 1. Client-identifying information — repo-wide, the hard gate
# ---------------------------------------------------------------------------
# Broadened at Checkpoint F. Client and agency names were never sufficient: harvested
# content also carries assembly names, component names, block aliases, project config
# values, branch slugs, and test-artifact filenames -- each of which identifies the
# source project as surely as its name.
begin "no client-identifying information (repo-wide)"
CLIENT_PATTERN='kittitas|CCASyndication|robotregime|scm\.umbraco\.io'
CLIENT_PATTERN+='|UmbracoProject|HelloWorld|Kittitas\.(Web|Features)'
CLIENT_PATTERN+='|SearchSummary|HeaderSearch|HeaderViewModel|ViewModelFactory|ServicesAggregate'
CLIENT_PATTERN+='|GuideToc|NotFoundContentFinder|SitemapRewriteMiddleware'
CLIENT_PATTERN+='|pillarSection|showcaseHero|categoryPaletteEntry|imageCarouselSlide'
CLIENT_PATTERN+='|contentSectionRow|iconLinkRow|guideSection'
CLIENT_PATTERN+='|UmbAI_Search|openai-embeddings|text-embedding-3-small'
CLIENT_PATTERN+='|claude/(feature|fix)/|migrate-ai-search|remove-seotoolkit|fix-e2e-dev-only'
CLIENT_PATTERN+='|ai-search-editor-content|blockParity|_umbracoApi'
CLIENT_PATTERN+='|\bcounty\b|\bdepartment\b'
hits=$(while IFS= read -r f; do [[ -n "$f" ]] && grep_unexempted "$f" "$CLIENT_PATTERN"; done < <(repo_md_files))
if [[ -n "$hits" ]]; then
  report_fail "$CURRENT" \
    "Client-identifying terms found. This repo is public with no staging period —" \
    "scrub before committing (see AGENTS.md)." \
    "" "$hits"
else
  report_pass "$CURRENT"
fi

# ---------------------------------------------------------------------------
# 1b. The authoring org may be attributed, but never inside a shipped skill
# ---------------------------------------------------------------------------
# A different rule from check 1, because it protects something different. The org is the
# AUTHOR -- naming it in a license, a README, or a decision record is intentional. Naming
# it inside a shipped skill is a project fact in L0: "this is how <org> does it" is exactly
# what the layer contract forbids, whoever the org is.
begin "authoring org is attributed, not embedded in skills"
AGENCY_PATTERN='wearediagram|diagram-et|\bdiagram\b'
hits=$(while IFS= read -r f; do [[ -n "$f" ]] && grep_unexempted "$f" "$AGENCY_PATTERN"; done < <(shipped_md_files))
if [[ -n "$hits" ]]; then
  report_fail "$CURRENT" \
    "The authoring org is named inside a shipped skill. Attribution belongs in LICENSE," \
    "README, or an ADR — a skill stating how one org works is a project fact in L0." \
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
  # Anchored to line start (leading indent allowed -- a declaration inside a bullet is
  # indented). Unanchored, this also matched prose *about* the mechanism: a file explaining
  # that /setup discovers `**Slot:**` declarations was read as making one, and was asked for
  # a fallback to a slot it never referenced.
  done < <(grep -n '^[[:space:]]*\*\*Slot:\*\*' "$f" 2>/dev/null)
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
# Agents ship as core too (ADR 0002 puts them at repo-root agents/), so they are L0 and
# must be technology-agnostic exactly like skills/core. A pack adds rules to a reviewer
# via its L2 reviewer-rules slot; it never names its technology in the agent itself.
L0_DIRS=()
[[ -d skills/core ]] && L0_DIRS+=(skills/core)
[[ -d agents ]] && L0_DIRS+=(agents)
if [[ ${#L0_DIRS[@]} -gt 0 ]]; then
  # A file may exempt specific patterns with an auditable inline declaration:
  #   <!-- contract-allow: npx — reason the exemption is legitimate -->
  # Needed because a few patterns are dual-use: `npx` is a project build command when a
  # spell hardcodes one (what this check is for), but it is also the toolkit's OWN
  # installer, which /update-toolkit must name. The reason travels with the exemption so
  # a reviewer can judge it, and the exemption is scoped to the one file that declares it.
  hits=$(
    while IFS= read -r f; do
      [[ -n "$f" ]] && grep_unexempted "$f" "$TECH_PATTERN"
    done < <(find "${L0_DIRS[@]}" -name '*.md' -type f -print 2>/dev/null)
  )
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
# 9. The same slot always gets the same fallback (docs/contract.md)
# ---------------------------------------------------------------------------
# A slot may legitimately have several independent consumers -- /plan and /retrofit both
# need the build command, and retrofit has no plan to inherit it from. What must never
# happen is two files declaring DIFFERENT fallbacks for one slot, because the behaviors
# then diverge silently whenever that slot is empty. That is the drift the rule exists to
# prevent, and it is worse than plain duplication.
begin "one slot, one fallback"
if [[ ${#SHIPPED_DIRS[@]} -gt 0 ]]; then
  # Emit "<slot>\t<fallback>" per pairing, then look for slots with >1 distinct fallback.
  inconsistent=$(
    while IFS= read -r f; do
      [[ -z "$f" ]] && continue
      while IFS=: read -r lineno _; do
        [[ -z "$lineno" ]] && continue
        slot=$(sed -n "${lineno}p" "$f" \
          | sed -e 's/.*\*\*Slot:\*\*[[:space:]]*//' -e 's/[[:space:]]*$//')
        # The fallback may wrap, so join the window and cut at the next blank line.
        fb=$(sed -n "$((lineno + 1)),$((lineno + 6))p" "$f" \
          | sed -n '/\*\*If empty:\*\*/,/^[[:space:]]*$/p' \
          | tr '\n' ' ' \
          | sed -e 's/.*\*\*If empty:\*\*[[:space:]]*//' -e 's/[[:space:]]\{1,\}/ /g' -e 's/[[:space:]]*$//')
        [[ -n "$slot" && -n "$fb" ]] && printf '%s\t%s\n' "$slot" "$fb"
      done < <(grep -n '^[[:space:]]*\*\*Slot:\*\*' "$f" 2>/dev/null)
    done < <(shipped_md_files) \
      | sort -u \
      | awk -F'\t' '{c[$1]++; ex[$1]=ex[$1]"\n        - "$2} END {for (s in c) if (c[s]>1) printf "%s has %d different fallbacks:%s\n", s, c[s], ex[s]}'
  )
  if [[ -n "$inconsistent" ]]; then
    report_fail "$CURRENT" \
      "Two files give the same slot different fallbacks — behavior diverges when it is empty." \
      "Make the fallback wording identical (docs/contract.md → one slot, one point of authority)." \
      "" "$inconsistent"
  else
    report_pass "$CURRENT"
  fi
else
  report_pass "$CURRENT"
fi

# ---------------------------------------------------------------------------
# 10. Exemplar-dependent instructions carry an absence clause (ADR 0006)
# ---------------------------------------------------------------------------
# "No instruction may assume its precondition exists." The general principle needs
# authoring discipline, but ONE pattern slipped twice and is greppable: telling the agent
# to copy or follow the closest existing thing, with no case for there being none.
#
# This exists because of an asymmetry the Checkpoint-F-era audit found: every SLOT
# fallback was guarded for absence, because check 4 refuses a **Slot:** without an
# **If empty:** and so forced the question. Nothing forced it for exemplar instructions,
# and three of four were unguarded. A principle without a forcing function gets applied
# when the author happens to remember.
begin "exemplar instructions handle having no exemplar"
EXEMPLAR_PAT='closest existing|existing exemplar|copy the closest|follow it exactly'
ABSENCE_PAT='if (none|no |nothing|there is no|the project has no)|when (none|no )|no doc exists|not yet established|nothing analogous|has no '
# Proximity matters. A first version asked only whether the file contained an absence
# clause ANYWHERE -- which every skill carrying a slot does, so it passed trivially and
# failed its own negative test silently. Require the clause near the instruction it
# guards, the same way check 4 requires a fallback beside its slot.
WINDOW=18
exemplar_errs=""
while IFS= read -r f; do
  [[ -z "$f" ]] && continue
  # Frontmatter is excluded: a description is a trigger string, not an instruction, so
  # requiring a caveat inside one would cost triggering accuracy for no benefit.
  fm_end=$(grep -n '^---$' "$f" 2>/dev/null | sed -n '2s/:.*//p')
  [[ -z "$fm_end" ]] && fm_end=0
  while IFS= read -r lineno; do
    [[ -z "$lineno" ]] && continue
    (( lineno <= fm_end )) && continue
    lo=1
    (( lineno > WINDOW )) && lo=$(( lineno - WINDOW ))
    if ! sed -n "${lo},$((lineno + WINDOW))p" "$f" | grep -qiE "$ABSENCE_PAT"; then
      exemplar_errs+="$f:$lineno: exemplar instruction with no absence clause within $WINDOW lines"$'\n'
    fi
  done < <(grep -niE "$EXEMPLAR_PAT" "$f" 2>/dev/null | cut -d: -f1 | sort -un)
done < <(shipped_md_files)
if [[ -n "$exemplar_errs" ]]; then
  report_fail "$CURRENT" \
    "An exemplar-first instruction needs an answer for a greenfield project (ADR 0006)." \
    "Offer a named external reference, seed thin and mark it to grow, or say the step does not apply." \
    "" "$exemplar_errs"
else
  report_pass "$CURRENT"
fi

# ---------------------------------------------------------------------------
# 11. Self-hosting covers every core skill (this repo only)
# ---------------------------------------------------------------------------
# The only check here about THIS repo rather than shipped content, and it earns its place
# the same way check 10 did: a principle with no forcing function gets applied when the
# author happens to remember. Adding a core skill takes three unlinked steps -- write it,
# link it into .claude/skills/, correct the README count -- and steps 2 and 3 were both
# missed twice in a row. /setup and design-system-authoring landed uncastable, so the repo
# dogfooding the toolkit could not run the spell that configures it.
#
# Scoped to skills/core deliberately. A pack must NOT be linked: this repo is not an
# Umbraco project, and linking the pack would put stack spells in a toolkit's own spellbook.
#
# Only symlinks pointing back into skills/core are ours. A consumer's own skills sit in the
# same directory and are none of this check's business -- the same name-match-is-not-ours
# distinction check-install.sh makes about reviewer agents.
begin "self-hosting covers every core skill"
if [[ -d .claude/skills && -d skills/core ]]; then
  core_names=$(find skills/core -name 'SKILL.md' -type f -print 2>/dev/null \
    | sed -e 's|/SKILL\.md$||' -e 's|.*/||' | sort -u)

  linked_names=""
  broken_links=""
  for entry in .claude/skills/*; do
    [[ -L "$entry" ]] || continue
    target=$(readlink "$entry")
    [[ -e "$entry" ]] || broken_links+="$(basename "$entry") -> $target"$'\n'
    [[ "$target" == *skills/core/* ]] && linked_names+="$(basename "$entry")"$'\n'
  done
  linked_names=$(printf '%s' "$linked_names" | sort -u)

  unlinked=$(comm -23 <(printf '%s\n' "$core_names") <(printf '%s\n' "$linked_names") | grep -v '^$')

  if [[ -n "$unlinked" || -n "$broken_links" ]]; then
    details=""
    [[ -n "$unlinked" ]] && details+="not linked into .claude/skills/:"$'\n'"$(printf '%s\n' "$unlinked" | sed 's/^/  - /')"$'\n'
    [[ -n "$broken_links" ]] && details+="dangling symlink:"$'\n'"$(printf '%s' "$broken_links" | sed 's/^/  - /')"
    report_fail "$CURRENT" \
      "A core skill this repo cannot cast on itself is untested by the work that authors it." \
      "Link it: ln -s ../../skills/core/<spellbook|reference>/<name> .claude/skills/<name>" \
      "Then check the skill count in README.md still matches." \
      "" "$details"
  else
    report_pass "$CURRENT"
  fi
else
  report_pass "$CURRENT"
fi

# ---------------------------------------------------------------------------
# 12. A declared companion is documented where a consumer will see it
# ---------------------------------------------------------------------------
# A pack may recommend external skill sets it routes work to (ADR 0012). Those are
# companions, not requirements -- but an undeclared external dependency is how a consumer
# installs a pack, casts a spell, and gets thinner guidance with no way to know why.
#
# The gap this closes was found in exactly that state: the pack had routed extension work
# to a marketplace since Phase 5 and named it in two skill files, while the README -- the
# only file a consumer reads before installing -- mentioned no marketplace at all. Both
# halves were individually reasonable, which is why nothing caught it.
#
# So the rule is: if a pack declares a companion, the README names it. The declaration is
# the machine-readable half (/setup reads it to report enablement); the README is the human
# half. This check is the only thing that keeps them in sync.
begin "declared companions are documented in the README"
companions=$(grep -rhoE '^\*\*Companion:\*\* +`[^`]+`' skills/ 2>/dev/null \
  | sed -e 's/^\*\*Companion:\*\* *//' -e 's/`//g' | sort -u)

if [[ -z "$companions" ]]; then
  report_pass "$CURRENT"
elif [[ ! -f README.md ]]; then
  report_fail "$CURRENT" \
    "A companion is declared but there is no README to document it in." \
    "Create README.md and name each declared companion." "" "" "$companions"
else
  # Fenced code blocks are stripped first. A companion named only inside a config snippet
  # is not documented -- it is demonstrated, which is a different thing and leaves a
  # consumer no way to learn the dependency exists or that it is optional. Found by
  # negative-testing this check: deleting the prose row left the JSON example, and a plain
  # substring match over the whole file still reported the companion as documented.
  readme_prose=$(awk '/^[[:space:]]*```/{fence=!fence; next} !fence' README.md)
  undocumented=""
  while IFS= read -r c; do
    [[ -z "$c" ]] && continue
    grep -qF -- "$c" <<<"$readme_prose" || undocumented+="  - $c"$'\n'
  done <<< "$companions"

  if [[ -n "$undocumented" ]]; then
    report_fail "$CURRENT" \
      "A consumer reads the README before installing; an external dependency absent from it is invisible until guidance is already thinner." \
      "Name each companion in README.md, and say it is recommended rather than required." \
      "Keep the pack's **Companion:** declaration as the machine-readable half -- /setup reads it." \
      "" "declared but not in README.md:"$'\n'"$undocumented"
  else
    report_pass "$CURRENT"
  fi
fi

# ---------------------------------------------------------------------------
# 13. The install checker's roster matches the core skills that exist (this repo only)
# ---------------------------------------------------------------------------
# check-install.sh runs in a consumer project, where skills/core/ is absent, so its roster
# of expected skills has to be hardcoded. That makes drift invisible in the one place it
# matters most: a roster missing a skill reports a clean install while that skill is not
# there at all.
#
# It had already drifted by three when this check was written -- setup,
# design-system-authoring, and tdd-principles -- so a consumer could install core, get no
# /setup, and be told "no problems found". Check 11 catches the same drift for self-hosting;
# this is its missing sibling, which is exactly the recurring shape it was written to stop.
begin "install checker roster matches skills/core"
if [[ -f scripts/check-install.sh && -d skills/core ]]; then
  roster=$(awk '/^ROSTER_CORE=\(/{f=1;next} f&&/^\)/{exit} f' scripts/check-install.sh \
    | tr ' ' '\n' | sed '/^$/d' | sort -u)
  actual=$(find skills/core -name 'SKILL.md' -type f -print 2>/dev/null \
    | sed -e 's|/SKILL\.md$||' -e 's|.*/||' | sort -u)

  missing=$(comm -13 <(printf '%s\n' "$roster") <(printf '%s\n' "$actual") | grep -v '^$')
  stale=$(comm -23 <(printf '%s\n' "$roster") <(printf '%s\n' "$actual") | grep -v '^$')

  if [[ -n "$missing" || -n "$stale" ]]; then
    details=""
    [[ -n "$missing" ]] && details+="in skills/core but not in ROSTER_CORE (a consumer missing these is told nothing):"$'\n'"$(printf '%s\n' "$missing" | sed 's/^/  - /')"$'\n'
    [[ -n "$stale" ]] && details+="in ROSTER_CORE but no longer in skills/core:"$'\n'"$(printf '%s\n' "$stale" | sed 's/^/  - /')"
    report_fail "$CURRENT" \
      "The consumer-facing install checker verifies a different set of skills than the toolkit ships." \
      "Update ROSTER_CORE in scripts/check-install.sh to match skills/core." \
      "" "$details"
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
