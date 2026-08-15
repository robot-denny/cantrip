#!/usr/bin/env bash
#
# check-install.sh — verify an installed toolkit is actually wired up.
#
# The installer reports that files were written, which is not the same claim as "the
# toolkit is usable here". Three things can be silently wrong after a successful install:
# a partial install, a skill whose bundled assets are missing, and unregistered reviewer
# agents that quietly degrade review. None of them announce themselves.
#
# Outcomes are three classes, not two:
#   wired     — present and readable
#   degraded  — working, but not at full strength (fixable, exits 0)
#   broken    — something a spell will fail on (exits non-zero)
#
# That distinction is why this is safe in a pipeline: a core-only install with no
# configuration and no linked agents is a WORKING install and exits 0.
#
# Usage:  scripts/check-install.sh [--verbose]
# Exit:   0 = wired or degraded, 1 = broken

set -uo pipefail

VERBOSE=0
[[ "${1:-}" == "--verbose" ]] && VERBOSE=1

# Read everything through .claude/skills/. It is the only path that exists under all
# three install layouts -- canonical (.agents/skills + symlinks), copied (real files in
# .claude/skills), and source-symlinked (self-hosting). See ADR 0004.
SKILLS_DIR=".claude/skills"
AGENTS_DIR=".claude/agents"
CONFIG_DIR=".agents/config"

# The toolkit's own roster. Embedded rather than derived: this script ships with the
# toolkit and versions with it, so it cannot drift from what it describes -- and a
# hand-vendored install has no lockfile to derive from. Units outside this list belong to
# the project and are none of our business.
# Hardcoded because this script runs in a CONSUMER project, where skills/core/ does not
# exist to derive from. That makes it a list that can silently fall behind the toolkit --
# and did: setup and design-system-authoring were absent here long after they shipped, so
# this script reported "13 of 13, no problems found" for an install with no /setup in it.
# Contract check 13 now compares this roster against skills/core in the toolkit repo, which
# is the only place the comparison is possible.
ROSTER_CORE=(
  bdd-principles design-system-authoring memory-discipline reviewer-discipline
  tdd-principles workflow
  code-review commit-message explore feature implement-step plan retrofit setup spec
  update-toolkit
)
# Pack units are the toolkit's too, so they must be verified and visible. But core-only is
# the documented baseline, so an ABSENT pack is never reported as missing.
# One flat list across every pack, because the roster's only job is to answer "is this unit
# ours?" -- which pack a unit came from is the installer's business, not this check's.
# This list drifted to two of the eight units that existed, and an unlisted unit is skipped
# entirely by in_roster: not verified when installed, not reported when it is not. Contract
# check 13 now compares it against every SKILL.md outside skills/core.
ROSTER_PACK=(
  umbraco-17-planning umbraco-17-feature-backfill umbraco-17-review-rules
  umbraco-17-starter-facts architecture-audit
  block check-uda umbraco-edit
  dotnet-conventions dotnet-review-rules
)
ROSTER=( "${ROSTER_CORE[@]}" "${ROSTER_PACK[@]}" )

# Assets each skill must be able to read. A skill whose SKILL.md is present but whose
# assets are gone is broken in a way a directory listing hides.
assets_for() {
  case "$1" in
    workflow)            echo "templates/spec.md templates/feature.md" ;;
    reviewer-discipline) echo "agents/accessibility-reviewer.md agents/code-reviewer.md agents/perf-reviewer.md" ;;
    *)                   echo "" ;;
  esac
}

REVIEWERS=(accessibility-reviewer code-reviewer perf-reviewer)

WIRED=0
DEGRADED=()
BROKEN=()
WIRED_NAMES=()

in_roster() {
  local n
  for n in "${ROSTER[@]}"; do [[ "$n" == "$1" ]] && return 0; done
  return 1
}

# ---------------------------------------------------------------------------
# 1. Skills: present, readable, and whole
# ---------------------------------------------------------------------------
if [[ ! -d $SKILLS_DIR ]]; then
  BROKEN+=("no $SKILLS_DIR directory — nothing is installed. Install with: npx skills add robot-denny/cantrip/skills/core --all")
else
  while IFS= read -r entry; do
    [[ -z "$entry" ]] && continue
    name=$(basename "$entry")
    in_roster "$name" || continue          # a project's own skills are not our concern

    skill_file="$entry/SKILL.md"

    # -r follows symlinks, so a dangling link fails here rather than looking present.
    if [[ ! -r $skill_file ]]; then
      if [[ -L $entry && ! -e $entry ]]; then
        BROKEN+=("$name — symlink points at nothing. Reinstall: npx skills add robot-denny/cantrip/skills/core --skill $name")
      else
        BROKEN+=("$name — SKILL.md is missing or unreadable. Reinstall: npx skills add robot-denny/cantrip/skills/core --skill $name")
      fi
      continue
    fi

    problem=""
    grep -q '^name:[[:space:]]*[^[:space:]]' "$skill_file" || problem="frontmatter has no name"
    grep -q '^description:[[:space:]]*[^[:space:]]' "$skill_file" || problem="frontmatter has no description"

    for asset in $(assets_for "$name"); do
      [[ -r "$entry/$asset" ]] || problem="cannot read asset $asset"
    done

    if [[ -n "$problem" ]]; then
      BROKEN+=("$name — $problem. Reinstall: npx skills add robot-denny/cantrip/skills/core --skill $name")
    else
      WIRED=$((WIRED + 1)); WIRED_NAMES+=("$name")
    fi
  done < <(find "$SKILLS_DIR" -mindepth 1 -maxdepth 1 2>/dev/null | sort)
fi

core_wired=0; pack_wired=0; PACK_NAMES=()
for n in "${WIRED_NAMES[@]:-}"; do
  [[ -z "$n" ]] && continue
  if printf '%s\n' "${ROSTER_PACK[@]}" | grep -qx "$n"; then
    pack_wired=$((pack_wired + 1)); PACK_NAMES+=("$n")
  else
    core_wired=$((core_wired + 1))
  fi
done

# ---------------------------------------------------------------------------
# 2. Roster coverage — informational, never a failure
# ---------------------------------------------------------------------------
# A selective install is legitimate (`--skill a,b`), so an absent skill is not broken.
# But reporting nothing about it would mean "verified present" was only ever checking the
# units that happened to be there. FR1 asks which resolve AND which are missing.
ABSENT=()
for n in "${ROSTER_CORE[@]}"; do
  [[ -r "$SKILLS_DIR/$n/SKILL.md" ]] || ABSENT+=("$n")
done

# ---------------------------------------------------------------------------
# 3. Lockfile cross-check (only when a lockfile exists)
# ---------------------------------------------------------------------------
# A hand-vendored install has no lockfile. That is legitimate, so its absence is not a
# finding -- it just means we cannot detect a skill that never arrived.
if [[ -f skills-lock.json ]]; then
  while IFS= read -r locked; do
    [[ -z "$locked" ]] && continue
    in_roster "$locked" || continue
    if [[ ! -r "$SKILLS_DIR/$locked/SKILL.md" ]]; then
      BROKEN+=("$locked — listed in skills-lock.json but missing from $SKILLS_DIR. Reinstall: npx skills add robot-denny/cantrip/skills/core --skill $locked")
    fi
  # Deliberately a shallow regex parse rather than a jq dependency: skill names are the
  # only keys whose value is an object in this lockfile shape, so matching `"name": {` and
  # dropping the two container keys is sufficient and keeps the script dependency-free.
  done < <(grep -oE '"[a-z0-9-]+":[[:space:]]*\{' skills-lock.json 2>/dev/null \
             | sed -e 's/"//g' -e 's/:.*//' | grep -vE '^(skills|version)$')
fi

# ---------------------------------------------------------------------------
# 4. Reviewer agents — degraded, not broken, when unregistered
# ---------------------------------------------------------------------------
# Unregistered reviewers mean /code-review and /retrofit run their passes inline instead
# of in parallel. That is a working toolkit, so it must not affect the exit code.
LINK_FIX='mkdir -p .claude/agents && for f in .claude/skills/reviewer-discipline/agents/*.md; do n=$(basename "$f"); ln -s "../skills/reviewer-discipline/agents/$n" ".claude/agents/$n"; done'

# A name match is NOT a registration. A project may have its own agent under the same name
# -- verified in the wild: a consumer had its own accessibility-reviewer and perf-reviewer,
# and this check counted them as ours. Worse, the naive "re-link" fix would have clobbered
# 11KB of project-tailored reviewers with our generic skeletons. So compare content against
# the installed copy: that recognizes both a symlink and an honest file copy, and recognizes
# a same-named foreign agent as the distinct situation it is.
registered=0
unreadable=()
collided=()
for r in "${REVIEWERS[@]}"; do
  target="$AGENTS_DIR/$r.md"
  ours="$SKILLS_DIR/reviewer-discipline/agents/$r.md"
  if [[ ! -e $target && ! -L $target ]]; then
    continue                                     # simply not registered
  elif [[ ! -r $target ]]; then
    unreadable+=("$r")                           # present but unreadable -- broken link
  elif [[ -r $ours ]] && cmp -s "$target" "$ours"; then
    registered=$((registered + 1))               # genuinely ours
  else
    collided+=("$r")                             # someone else's agent under our name
  fi
done

if [[ ${#unreadable[@]} -gt 0 ]]; then
  BROKEN+=("reviewer agents present but unreadable (${unreadable[*]}) — a broken link reads as configured while failing every dispatch. Re-link with: $LINK_FIX")
fi

if [[ ${#collided[@]} -gt 0 ]]; then
  DEGRADED+=("name collision on ${#collided[@]} reviewer agent(s) (${collided[*]}) — your project already has agents under these names and they are NOT the toolkit's. Nothing is broken and nothing was overwritten. Decide per agent: keep yours (the toolkit's stays unregistered), or adopt the toolkit's under a different filename so both remain available. Do NOT force-link over them — that would replace your tailored agents with generic skeletons.")
fi

if [[ $registered -eq 0 && ${#collided[@]} -eq 0 ]]; then
  DEGRADED+=("reviewer agents are not registered — review still runs, but inline instead of in parallel. Register with: $LINK_FIX")
elif [[ $registered -gt 0 && $((registered + ${#collided[@]})) -lt ${#REVIEWERS[@]} ]]; then
  DEGRADED+=("only $registered of ${#REVIEWERS[@]} toolkit reviewer agents are registered — review will be partial. Link the rest with: $LINK_FIX")
fi

# ---------------------------------------------------------------------------
# 4b. Redundant install copies (install scatter)
# ---------------------------------------------------------------------------
# `--all` implies `--agent '*'`, so the installer writes to every target it can detect --
# including a top-level `agent/` directory and, if the project already has a bare `skills/`
# directory, into that as well. Nothing breaks, but the project ends up carrying several
# copies that update will touch unevenly. Reported because a consumer hit this and the
# checker said nothing; only toolkit-roster names are considered, so a project's own
# `skills/` contents are never implicated.
SCATTER=()
if [[ -d agent/skills ]]; then
  n=$(find agent/skills -mindepth 1 -maxdepth 1 -type d 2>/dev/null | wc -l | tr -d ' ')
  [[ "$n" -gt 0 ]] && SCATTER+=("agent/skills/ ($n copies)")
fi
if [[ -d skills ]]; then
  n=0
  for r in "${ROSTER[@]}"; do [[ -e "skills/$r" ]] && n=$((n + 1)); done
  [[ "$n" -gt 0 ]] && SCATTER+=("skills/ ($n toolkit copies alongside the project's own)")
fi
if [[ ${#SCATTER[@]} -gt 0 ]]; then
  DEGRADED+=("redundant install copies in ${SCATTER[*]} — the installer wrote to every agent target it could detect. Nothing is broken, but updates will touch these unevenly. Remove with: git clean -nd agent skills   (preview first; it removes only untracked files, so your own content is safe)")
fi

# ---------------------------------------------------------------------------
# 5. Slot survey — every slot may legitimately be empty
# ---------------------------------------------------------------------------
# Reported for visibility, never for pass/fail. The toolkit is designed to work with all
# slots empty; the point is to show what it currently knows about this project, so an
# unexpectedly empty slot becomes visible instead of silently degrading a spell.
slot_state() {          # slot_state <file> <heading>
  local f="$CONFIG_DIR/$1" h="$2"
  [[ -f $f ]] || { echo empty; return; }
  # Filled means the heading exists AND has non-blank content before the next heading.
  awk -v h="$h" '
    $0 ~ "^## *" h "$" {inside=1; next}
    inside && /^## / {exit}
    inside && NF {found=1; exit}
    END {exit(found?0:1)}' "$f" && echo filled || echo empty
}

# Core slots, read by the core skills. Pack slots are surveyed only when the pack that
# reads them is installed -- a core-only install must not be told to fill a slot no
# installed unit reads. (Found by cross-checking this list against the slots actually
# declared in the skills: `## Models` was being surveyed unconditionally while
# `## Umbraco` was not surveyed at all.)
SLOTS=(
  "paths.md|Workspace" "paths.md|Code layout" "paths.md|Generated output"
  "stack.md|Build" "stack.md|Tests"
  "conventions.md|Branch naming" "conventions.md|Commit format" "conventions.md|Commit trailers"
  "conventions.md|Implementation rules" "conventions.md|Memory"
  "conventions.md|Planning gotchas" "conventions.md|Unit of work"
  "reviewer-rules|Reviewer names"
)
# Pack slot -> the installed skill that makes it relevant.
PACK_SLOTS=(
  "stack.md|Models|umbraco-17-planning"
  "paths.md|Umbraco|umbraco-17-planning"
  "stack.md|Local URL|umbraco-edit"
  "conventions.md|.NET style decisions|dotnet-conventions"
)
for entry in "${PACK_SLOTS[@]}"; do
  IFS='|' read -r pf ph pskill <<<"$entry"
  [[ -r "$SKILLS_DIR/$pskill/SKILL.md" ]] && SLOTS+=("$pf|$ph")
done

slots_filled=0; slots_empty=0; slot_lines=()
for entry in "${SLOTS[@]}"; do
  f="${entry%%|*}"; h="${entry##*|}"
  st=$(slot_state "$f" "$h")
  [[ $st == filled ]] && slots_filled=$((slots_filled + 1)) || slots_empty=$((slots_empty + 1))
  slot_lines+=("$(printf '  %-9s %-22s %s' "$st" "$h" "$f")")
done

reviewer_rules=0
if [[ -d "$CONFIG_DIR/reviewer-rules" ]]; then
  reviewer_rules=$(find "$CONFIG_DIR/reviewer-rules" -name '*.md' -type f 2>/dev/null | wc -l | tr -d ' ')
fi

# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------
# Identify which copy of this script ran. A self-hash needs no maintenance and cannot
# drift from the file it describes -- two different values prove two different scripts.
# Added because a consumer reported "same result as last time" after a fix had landed,
# and there was no way to tell a stale run from a stale copy from stale scrollback.
_self_hash=$(shasum -a 256 "${BASH_SOURCE[0]}" 2>/dev/null | cut -c1-8)
printf 'Toolkit install\n'
printf '  checker:   %s (%s)\n' "${_self_hash:-unknown}" "${BASH_SOURCE[0]}"
printf '  installed: %d of %d core skill(s)\n' "$core_wired" "${#ROSTER_CORE[@]}"
[[ $pack_wired -gt 0 ]] && printf '  pack:      %d skill(s) — %s\n' "$pack_wired" "${PACK_NAMES[*]}"
printf '  degraded:  %d\n' "${#DEGRADED[@]}"
printf '  broken:    %d\n' "${#BROKEN[@]}"

if [[ ${#ABSENT[@]} -gt 0 ]]; then
  printf '  not installed: %d — a selective install is fine; re-run the install command to add them\n' "${#ABSENT[@]}"
  if [[ $VERBOSE -eq 1 ]]; then
    for n in "${ABSENT[@]}"; do printf '    - %s\n' "$n"; done
  fi
fi

if [[ $VERBOSE -eq 1 && $WIRED -gt 0 ]]; then
  printf '\nInstalled and whole:\n'
  for n in "${WIRED_NAMES[@]}"; do printf '  - %s\n' "$n"; done
fi

if [[ ${#BROKEN[@]} -gt 0 ]]; then
  printf '\n\033[31mBroken\033[0m — a spell will fail on these:\n'
  for b in "${BROKEN[@]}"; do printf '  - %s\n' "$b"; done
fi

if [[ ${#DEGRADED[@]} -gt 0 ]]; then
  printf '\n\033[33mDegraded\033[0m — working, but not at full strength:\n'
  for d in "${DEGRADED[@]}"; do printf '  - %s\n' "$d"; done
fi

printf '\nProject configuration (L2 slots): %d filled, %d empty' "$slots_filled" "$slots_empty"
[[ $reviewer_rules -gt 0 ]] && printf ', %d reviewer-rule file(s)' "$reviewer_rules"
printf '\n'
if [[ $slots_filled -eq 0 ]]; then
  printf '  Every slot is empty. This is a working configuration — the toolkit infers what it\n'
  printf '  needs and asks when it cannot. Fill slots in %s to make it project-specific.\n' "$CONFIG_DIR"
elif [[ $VERBOSE -eq 1 ]]; then
  for l in "${slot_lines[@]}"; do printf '%s\n' "$l"; done
fi

printf '\n'
if [[ ${#BROKEN[@]} -gt 0 ]]; then
  printf '\033[31mInstall is broken.\033[0m Fix the items above, then re-run.\n'
  exit 1
fi
if [[ ${#DEGRADED[@]} -gt 0 ]]; then
  printf '\033[33mInstall works, with %d thing(s) worth fixing.\033[0m\n' "${#DEGRADED[@]}"
  exit 0
fi
printf '\033[32mNo problems found.\033[0m\n'
exit 0
