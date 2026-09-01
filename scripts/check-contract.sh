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
# Check 17 is shipped-only like 2-10, but pairwise rather than per-file: it reads a vocabulary
# one shipped file declares and requires the two shipped spells that write it to know it. It
# would hold identically in a consumer's checkout — nothing about this repository is involved.
#
# Checks 11, 13, and 16 are the exceptions in the other direction — they inspect this repo
# rather than what it ships. Each guards a hardcoded list that has to be kept in step with
# skills/core by hand: 11 the self-hosting symlinks, 13 the install checker's roster, 16 the
# spells the budget does not count. 11 and 13 were both added after that list had already
# drifted, and each drifted in the same silent way, reporting success for a skill that was
# not there.

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
#
# The extension list is an allow-list, which means it has holes by construction: a file type
# nobody thought of is silently unscanned, and the symptom is a clean run. `.diff` was such a
# hole -- the first increment to commit review-evidence fixtures added eight unscanned files
# and the gate reported success. Two lessons in that. Keep the two lists below in step, since
# only the second runs outside a git checkout. And when adding a fixture in a new format,
# check it is scanned before assuming it is.
#
# `.uda` (Deploy) and `.config` (uSync) were added when the guide-check suite arrived, ahead
# of its first committed fixture: those fixtures carry document-type aliases, property names,
# and folder paths, which is exactly the content check 1 exists to catch. `.cs` followed for
# the generated-models rung, whose fixtures are C# model classes carrying the same aliases and
# property names -- the same hole, found by looking for it this time rather than after a leak.
#
# `.css` was added with the styleguide-check suite, whose fixtures are stylesheets. A token
# name is as identifying as a block alias -- a project's palette is named after the project --
# and the hole was demonstrated before it was filled: a client term planted in a fixture
# stylesheet passed all 17 checks, and fails check 1 once the extension is listed here.
#
# `.scss` followed in the same suite once a fixture needed a preprocessor source: a `$` variable
# is named after the project exactly as a custom property is, and the hole was demonstrated the
# same way before it was filled.
#
# `.cshtml` followed when the same suite gained view fixtures for `precheck`'s greenfield guard. A
# Razor view is the densest client-identifying file type in any of these projects -- it carries
# block aliases, property names, CSS class names, and copy -- and the hole was demonstrated the
# same way: a client term planted in a fixture view passed all 17 checks, and fails check 1 once
# the extension is listed here.
repo_md_files() {
  if git rev-parse --git-dir >/dev/null 2>&1; then
    { git ls-files; git ls-files --others --exclude-standard; } 2>/dev/null \
      | grep -E '\.(md|json|sh|py|txt|diff|uda|config|cs|css|scss|cshtml)$|(^|/)LICENSE$' \
      | grep -vE '^scripts/check-contract\.sh$'
  else
    find . \( "${PRUNE[@]}" \) -prune -o -type f \
      \( -name '*.md' -o -name '*.json' -o -name '*.sh' -o -name '*.py' -o -name '*.txt' \
         -o -name '*.diff' -o -name '*.uda' -o -name '*.config' -o -name '*.cs' \
         -o -name '*.css' -o -name '*.scss' -o -name '*.cshtml' -o -name 'LICENSE' \) \
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
# Third extraction source, added 2026-08-25: the uSync reference project. Org and solution names,
# plus the block aliases distinctive enough to identify it if they were ever copied verbatim.
# Deliberately excludes its generic aliases (articlePage, category, location, quoteBlock) — those
# collide with this repo's own synthetic examples, and a pattern that fires on our own worked
# examples gets deleted rather than obeyed.
CLIENT_PATTERN+='|Houlihan|Lokey'
CLIENT_PATTERN+='|twoColumn2575|mNTPCategorySelector|globalBlockSelectorComposition'
CLIENT_PATTERN+='|headingLabelSectionComposition|calloutWithTableBlock|blankHTMLTemplate'
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
# 13. The install checker's rosters match the skills that exist (this repo only)
# ---------------------------------------------------------------------------
# check-install.sh runs in a consumer project, where skills/ is absent, so its rosters of
# expected skills have to be hardcoded. That makes drift invisible in the one place it
# matters most: a roster missing a skill reports a clean install while that skill is not
# there at all -- an unlisted unit is skipped by the roster filter, so it is neither
# verified when present nor reported when absent.
#
# ROSTER_CORE had already drifted by three when this check was written -- setup,
# design-system-authoring, and tdd-principles -- so a consumer could install core, get no
# /setup, and be told "no problems found". Check 11 catches the same drift for self-hosting;
# this is its missing sibling, which is exactly the recurring shape it was written to stop.
#
# ROSTER_PACK was left uncovered by the first version and drifted the same way, by six of
# eight units. Covering it costs one comparison and turns "remember to register your unit"
# into a gate, which is the only form of that instruction that survives.

# Pull one bash array literal out of check-install.sh, one entry per line.
#
# Handles the single-line form -- NAME=( a b ) -- as well as the multi-line one. The first
# version of this check skipped the opening line and so read nothing at all out of a
# one-line array; pointed at ROSTER_PACK it would have called every listed unit missing,
# which looks exactly like real drift and would have been "fixed" by duplicating entries.
#
# Comments are stripped before anything else, and the order matters. This file's comment
# style is heavily parenthetical -- "(a consumer missing these is told nothing)" a few lines
# down is typical -- so an editor adding an aside inside an array body is likely rather than
# hypothetical, and a `)` in that aside used to end the scan early. The entries after it went
# unread while the comment's own words were reported as stale roster entries: a failure that
# points a maintainer at nonsense while the real drift goes unmentioned.
#
# Double quotes are stripped so a quoted entry compares as its value. Single quotes are not
# handled; no roster entry has ever needed either.
#
# ONE DECLARATION PER ARRAY. This reads the first match and stops, while bash uses the last,
# so a second declaration would make the two disagree silently. The caller guards against it
# rather than this function coping, because the honest response is to fail loudly.
roster_entries() {   # roster_entries <ARRAY_NAME>
  awk -v var="$1" '
    { line = $0; sub(/#.*$/, "", line) }
    index(line, var "=(") == 1 { inside = 1; sub(/^[A-Za-z_]+=\(/, "", line) }
    inside {
      if (index(line, ")")) { sub(/\).*$/, "", line); done = 1 }
      gsub(/"/, "", line)
      n = split(line, w, /[[:space:]]+/)
      for (i = 1; i <= n; i++) if (w[i] != "") print w[i]
      if (done) exit
    }
  ' scripts/check-install.sh | sort -u
}

# Report drift between one roster and the units that actually exist. Prints nothing when
# they agree, so the caller can concatenate both rosters' findings into one failure.
roster_drift() {   # roster_drift <ARRAY_NAME> <where> <actual-names>
  local var="$1" where="$2" actual="$3" roster missing stale out=""
  roster=$(roster_entries "$var")
  missing=$(comm -13 <(printf '%s\n' "$roster") <(printf '%s\n' "$actual") | grep -v '^$')
  stale=$(comm -23 <(printf '%s\n' "$roster") <(printf '%s\n' "$actual") | grep -v '^$')
  [[ -n "$missing" ]] && out+="in $where but not in $var (a consumer missing these is told nothing):"$'\n'"$(printf '%s\n' "$missing" | sed 's/^/  - /')"$'\n'
  [[ -n "$stale" ]] && out+="in $var but no longer in $where:"$'\n'"$(printf '%s\n' "$stale" | sed 's/^/  - /')"$'\n'
  printf '%s' "$out"
}

begin "install checker rosters match skills/"
if [[ -f scripts/check-install.sh && -d skills ]]; then
  core_actual=$(find skills/core -name 'SKILL.md' -type f -print 2>/dev/null \
    | sed -e 's|/SKILL\.md$||' -e 's|.*/||' | sort -u)
  # Every shipped unit outside skills/core belongs to some L1 pack, whichever pack that is.
  # Deriving the set by exclusion rather than naming the packs means a new pack is covered
  # the day its first unit lands, with no second list to keep in step.
  pack_actual=$(find skills -name 'SKILL.md' -type f -print 2>/dev/null \
    | grep -v '^skills/core/' \
    | sed -e 's|/SKILL\.md$||' -e 's|.*/||' | sort -u)

  details=""

  # A roster declared twice is the one input that makes this check lie rather than complain:
  # the parser reads the first block, bash runs with the last, and if the first happens to
  # match reality the gate reports clean while the effective roster is wrong. That is the
  # precise failure this check exists to prevent, so it is caught before any comparison.
  for roster_var in ROSTER_CORE ROSTER_PACK; do
    declared=$(grep -c "^$roster_var=(" scripts/check-install.sh || true)
    [[ "$declared" -gt 1 ]] && details+="$roster_var is declared $declared times in scripts/check-install.sh — this check reads the first, bash uses the last, so they can disagree silently. Keep one declaration."$'\n'
  done

  # Each roster's findings are appended with their own trailing newline, and only when there
  # are any. Command substitution strips trailing newlines whether or not it is quoted, so
  # appending the two results directly ran the second roster's heading onto the first's last
  # bullet -- "- tdd-principlesin a pack under skills/...". Adding the newline unconditionally
  # would be worse: an empty result would still leave `details` non-empty and fail every run.
  if [[ -d skills/core ]]; then
    core_drift=$(roster_drift ROSTER_CORE skills/core "$core_actual")
    [[ -n "$core_drift" ]] && details+="$core_drift"$'\n'
  fi
  pack_drift=$(roster_drift ROSTER_PACK "a pack under skills/" "$pack_actual")
  [[ -n "$pack_drift" ]] && details+="$pack_drift"$'\n'

  if [[ -n "$details" ]]; then
    report_fail "$CURRENT" \
      "The consumer-facing install checker verifies a different set of skills than the toolkit ships." \
      "Update ROSTER_CORE / ROSTER_PACK in scripts/check-install.sh to match skills/." \
      "" "$details"
  else
    report_pass "$CURRENT"
  fi
else
  report_pass "$CURRENT"
fi

# ---------------------------------------------------------------------------
# 14. The audit's stack-agnostic references stay stack-agnostic (the core seam)
# ---------------------------------------------------------------------------
# Check 8's rule, applied one layer early. These four files sit in an L1 pack today and are
# written to L0's standard on purpose: what a lifecycle stage is, which categories of
# documentation exist, what resilience means, and how a score is anchored are claims about
# codebases, not about a platform. Holding them to the rule now means promoting them to core
# later is a `git mv` and a roster edit rather than a rewrite.
#
# Without a gate the seam closes silently and cheaply: the file that motivated this check had
# picked up one CMS-specific scoring anchor, which is all it takes for the four files to stop
# being movable. A reviewer would have to re-read four long references to notice.
#
# The list is by BASENAME, not path, so the check follows the files through the move it is
# meant to protect -- into another pack, or eventually into skills/core. A named file that has
# gone missing is reported rather than skipped, because a vanished entry looks exactly like a
# clean run, which is the failure mode checks 11 and 13 were both written to stop.
begin "stack-agnostic audit references name no technology"
SEAM_FILES=(lifecycle-stages.md documentation-and-onboarding.md resilience-and-ops.md scoring-rubric.md)
# Check 8's pattern plus the platform spellings it never needed: no L0 file has ever had
# occasion to name a project file format or a package manager, so the pattern that guards L0
# does not list them, and these four files are full of detection recipes that would.
SEAM_TECH_PATTERN="$TECH_PATTERN"'|\.net\b|csproj|nuget|msbuild'
if [[ -d skills ]]; then
  # One traversal for every name. A find per name re-walks the whole tree, and this check runs
  # on every commit via .githooks/pre-commit.
  find_expr=()
  for seam_name in "${SEAM_FILES[@]}"; do
    [[ ${#find_expr[@]} -gt 0 ]] && find_expr+=(-o)
    find_expr+=(-name "$seam_name")
  done
  all_seam=$(find skills -type f \( "${find_expr[@]}" \) -print 2>/dev/null)
  seam_paths=""
  seam_missing=""
  for seam_name in "${SEAM_FILES[@]}"; do
    found=$(printf '%s\n' "$all_seam" | grep -F "/$seam_name" || true)
    if [[ -z "$found" ]]; then
      seam_missing+="  - $seam_name (named in SEAM_FILES but nowhere under skills/)"$'\n'
    else
      seam_paths+="$found"$'\n'
    fi
  done
  hits=$(
    while IFS= read -r f; do
      [[ -n "$f" ]] && grep_unexempted "$f" "$SEAM_TECH_PATTERN"
    done <<<"$seam_paths"
  )
  if [[ -n "$hits" || -n "$seam_missing" ]]; then
    details=""
    [[ -n "$hits" ]] && details+="$hits"$'\n'
    [[ -n "$seam_missing" ]] && details+="$seam_missing"
    report_fail "$CURRENT" \
      "These references are written to L0's standard so they can move to core unchanged." \
      "Say it without the technology, or move the technology-specific signal to a pack file." \
      "If a file was renamed or retired on purpose, update SEAM_FILES in this script." \
      "" "$details"
  else
    report_pass "$CURRENT"
  fi
else
  report_pass "$CURRENT"
fi

# ---------------------------------------------------------------------------
# 15. Every documented install command disables telemetry (ADR 0009)
# ---------------------------------------------------------------------------
# ADR 0009: the installer uploads skill file contents by default, so every invocation a
# reader might copy sets DISABLE_TELEMETRY=1. The README's Quick start shipped four bare
# commands for the toolkit's whole life, and check-install printed four more — found by a
# consumer running the toolkit on client work, not by review.
#
# An ALLOWLIST of live authored surface, deliberately not a repo-wide sweep with exclusions.
# Records keep the command as it was run: CHANGELOG.md, adr/, and _work/ are history, and a
# denylist over them would false-fail the moment a new archive appears. A gate that cries
# wolf gets silenced, so this one fails silent instead: a documented invocation in a location
# nobody added here is a coverage gap, not a broken build. Add the location when you make one.
begin "documented install commands disable telemetry"
INVOCATION="npx skills (add|update)"
install_doc_files() {
  local f
  for f in README.md AGENTS.md CLAUDE.md; do [[ -f "$f" ]] && printf '%s\n' "$f"; done
  [[ -d docs ]] && find docs -maxdepth 1 -name '*.md' -type f -print 2>/dev/null
  # scripts/ is pruned from the repo-wide scans (it names the patterns it hunts), but the
  # hints check-install PRINTS are commands a user runs at the moment something is wrong --
  # the highest-value target here. Only this script is skipped, and only because the grep
  # below would match itself.
  [[ -d scripts ]] && find scripts -maxdepth 1 -name '*.sh' -type f \
    ! -name 'check-contract.sh' -print 2>/dev/null
  skill_files
}
hits=$(
  while IFS= read -r f; do
    [[ -n "$f" ]] || continue
    grep -inE "$INVOCATION" "$f" 2>/dev/null | grep -v 'DISABLE_TELEMETRY' | sed "s|^|$f:|"
  done < <(install_doc_files)
)
if [[ -n "$hits" ]]; then
  report_fail "$CURRENT" \
    "ADR 0009: the installer uploads skill file contents, so a copied command must disable it." \
    "Prefix the invocation with DISABLE_TELEMETRY=1." \
    "If this line is a historical record rather than a command to run, it belongs in CHANGELOG.md, adr/, or _work/ — not here." \
    "" "$hits"
else
  report_pass "$CURRENT"
fi

# ---------------------------------------------------------------------------
# 16. The workflow spellbook stays inside its budget (this repo only)
# ---------------------------------------------------------------------------
# ADR 0010 sets a working ceiling of ten workflow spells, amended up from a stated aim of
# 6-8 so a genuinely new stage has somewhere to land. A budget stated only in prose is one
# an author discovers they have broken after the spell is written, reviewed, and documented
# -- which is the point at which nobody merges two stages instead.
#
# The ceiling is on WORKFLOW spells. /setup and /update-toolkit are configuration and
# maintenance, counted separately by the same ADR, so they are excluded by name. That list
# is hardcoded and will drift the way checks 11 and 13 drifted: a third non-workflow spell
# would be counted as a stage and eat budget it does not use. Where that list is wrong the
# comparison fails loud with the count printed rather than passing quietly, which is the safe
# direction for the count. The check as a whole is not silent-pass-proof: like checks 11 and
# 13 it reports ok when the directory it inspects is absent, so moving skills/core/spellbook
# retires this gate without saying so.
begin "workflow spellbook stays inside its budget"
SPELL_CEILING=10
NON_WORKFLOW=(setup update-toolkit)
if [[ -d skills/core/spellbook ]]; then
  workflow_spells=""
  for entry in skills/core/spellbook/*/; do
    [[ -f "$entry/SKILL.md" ]] || continue
    name="${entry%/}"; name="${name##*/}"
    skip=0
    for excluded in "${NON_WORKFLOW[@]}"; do
      [[ "$name" == "$excluded" ]] && skip=1
    done
    (( skip )) || workflow_spells+="$name"$'\n'
  done
  spell_count=$(printf '%s' "$workflow_spells" | grep -c . || true)

  if (( spell_count > SPELL_CEILING )); then
    report_fail "$CURRENT" \
      "ADR 0010: $spell_count workflow spells exceeds the working ceiling of $SPELL_CEILING." \
      "Merge two stages, or add a router spell, rather than appending another." \
      "If the ceiling itself should move, amend ADR 0010 first — the number lives there." \
      "" "$(printf '%s' "$workflow_spells" | sed 's/^/  - /')"
  else
    report_pass "$CURRENT"
  fi
else
  report_pass "$CURRENT"
fi

# ---------------------------------------------------------------------------
# 17. Coverage statuses are known to every spell that writes them
# ---------------------------------------------------------------------------
# The feature template DECLARES the Test Coverage vocabulary; /feature and /spec are the two
# spells that WRITE it. Three shipped files, one vocabulary, and nothing linking them but an
# author's memory. A status defined in one place and unknown to its writers is worse than no
# status at all: the template offers a row no spell will ever produce, and a reader cannot tell
# a status nobody needs from one everybody forgot.
#
# This is a SHIPPED-content check like 2-10, not a this-repo check like 11, 13, and 16. It holds
# three installed files against each other and would hold identically in a consumer's checkout;
# nothing about this repository is involved. What it shares with 11/13/16 is only the failure
# mode they were written against -- a list kept in step by hand.
#
# The vocabulary is READ from the template at run time, never listed here. A copy inside the gate
# would be a fourth place to keep in step, and worse, it would pass against itself while the real
# files drifted. The declaration shape is therefore part of the contract:
#
#   * the vocabulary lives in the HTML comment beneath the template's `## Test Coverage` table
#   * one status per `- Name: description` bullet; a wrapped description line carries no dash
#   * a status may end in a `<placeholder>` for author-supplied text
#
# and so is the way a writer names one: as a backticked literal, `Covered`. Requiring the
# backticks is what keeps `Not covered` from being satisfied by a spell that only ever mentions
# `Not covered (code-derived)` -- the substring match that would quietly excuse the exact drift
# this check exists to catch. A `<placeholder>` matches any text the writer puts there.
#
# The vocabulary has never had fewer than three statuses, so reading fewer than three means the
# declaration moved or changed shape rather than that the project agreed on a shorter list. That
# fails loud, because an empty vocabulary satisfies every writer trivially -- the silent-success
# failure mode checks 11 and 13 were both added after suffering.
begin "coverage statuses are known to every spell that writes them"
COVERAGE_TEMPLATE=skills/core/reference/workflow/templates/feature.md
# Every shipped file that names a status for a reader to act on, not only the two that fill in a
# table. /testify routes on the vocabulary rather than writing it today, and becomes a writer once
# its recording path lands -- gated from the start, because a list kept in step by hand is the
# failure checks 11 and 13 were both added after suffering.
COVERAGE_WRITERS=(
  skills/core/spellbook/feature/SKILL.md
  skills/core/spellbook/spec/SKILL.md
  skills/core/spellbook/testify/SKILL.md
)
if [[ -d skills/core ]]; then
  absent=""
  [[ -f "$COVERAGE_TEMPLATE" ]] || absent+="  - $COVERAGE_TEMPLATE (declares the vocabulary)"$'\n'
  for writer in "${COVERAGE_WRITERS[@]}"; do
    [[ -f "$writer" ]] || absent+="  - $writer (writes the vocabulary)"$'\n'
  done

  if [[ -n "$absent" ]]; then
    report_fail "$CURRENT" \
      "A file this check compares is not where it expects it." \
      "If it was renamed or retired on purpose, update COVERAGE_TEMPLATE / COVERAGE_WRITERS in this script." \
      "" "$absent"
  else
    # Statuses declared in the comment beneath the Test Coverage table.
    vocab=$(awk '/^## Test Coverage/ { in_section = 1 }
                 in_section && /<!--/ { in_comment = 1 }
                 in_comment { print }
                 in_comment && /-->/ { exit }' "$COVERAGE_TEMPLATE" \
            | sed -n 's/^[[:space:]]*-[[:space:]]\{1,\}\([^:]*\):.*/\1/p')
    vocab_count=$(printf '%s\n' "$vocab" | grep -c . || true)

    if (( vocab_count < 3 )); then
      report_fail "$CURRENT" \
        "Read $vocab_count coverage statuses from $COVERAGE_TEMPLATE; the vocabulary has never been that short." \
        "The declaration is the comment beneath that file's '## Test Coverage' table, one status per '- Name: description' bullet." \
        "If it moved or changed shape, teach this check where it lives now — an empty vocabulary would pass against every spell."
    else
      unknown=""
      while IFS= read -r status; do
        [[ -n "$status" ]] || continue
        # Build the literal a writer must carry: the status in backticks, with any
        # <placeholder> standing in for whatever text the writer supplies.
        pattern=$(printf '%s' "$status" \
          | sed -e 's/[][(){}.*+?^$|\]/\\&/g' -e 's/<[^>]*>/[^`]*/g')
        pattern='`'"$pattern"'`'
        for writer in "${COVERAGE_WRITERS[@]}"; do
          grep -qE -- "$pattern" "$writer" 2>/dev/null \
            || unknown+="  - $writer never names \`$status\`"$'\n'
        done
      done <<<"$vocab"

      if [[ -n "$unknown" ]]; then
        report_fail "$CURRENT" \
          "$COVERAGE_TEMPLATE declares $vocab_count coverage statuses; each has to be known to every spell that names one." \
          "Describe the missing status where the spell describes the Test Coverage table, naming it in backticks exactly as the template declares it." \
          "If a status is genuinely not this spell's to write, say so there in one line — silence is indistinguishable from having forgotten it." \
          "" "$unknown"
      else
        report_pass "$CURRENT"
      fi
    fi
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
