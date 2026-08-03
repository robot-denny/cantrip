#!/usr/bin/env bash
#
# Regenerate the install-check fixtures.
#
# Fixtures are generated rather than hand-built so they are reproducible and reviewable:
# a malformed fixture produces a test failure that looks exactly like a real bug, which
# cost real debugging time when these were first assembled by hand.
#
# Each case is a minimal fake project tree plus an `expect` file. They are deliberately
# minimal -- the check is under test, not the installer.
#
# Usage:  tests/make-fixtures.sh

set -euo pipefail
cd "$(dirname "$0")" || exit 2

CASES="install-check"
rm -rf "$CASES"
mkdir -p "$CASES"

CORE=(workflow spec plan code-review)
REVIEWERS=(accessibility-reviewer code-reviewer perf-reviewer)

skill() {   # skill <dir> <name>
  mkdir -p "$1"
  cat > "$1/SKILL.md" <<EOF
---
name: $2
description: A description long enough that the frontmatter completeness check has real content to accept rather than a stub.
---
Body.
EOF
}

templates() {  # templates <workflow-skill-dir>
  mkdir -p "$1/templates"
  printf '# Spec for <slug>\n' > "$1/templates/spec.md"
  printf '# Feature: {Feature Name}\n' > "$1/templates/feature.md"
}

agent_files() {  # agent_files <reviewer-discipline-skill-dir>
  mkdir -p "$1/agents"
  local a
  for a in "${REVIEWERS[@]}"; do
    printf -- '---\nname: %s\ndescription: Reviewer.\n---\n' "$a" > "$1/agents/$a.md"
  done
}

link_agents() {  # link_agents <case-root>
  mkdir -p "$1/.claude/agents"
  local a
  for a in "${REVIEWERS[@]}"; do
    ln -sfn "../skills/reviewer-discipline/agents/$a.md" "$1/.claude/agents/$a.md"
  done
}

# --- copied layout: real files directly under .claude/skills -------------------
build_copied() {  # build_copied <case-root>
  local root=$1 s
  mkdir -p "$root/.claude/skills"
  for s in "${CORE[@]}" reviewer-discipline; do skill "$root/.claude/skills/$s" "$s"; done
  templates "$root/.claude/skills/workflow"
  agent_files "$root/.claude/skills/reviewer-discipline"
  link_agents "$root"
}

# --- canonical layout: .agents/skills real, .claude/skills symlinked -----------
build_canonical() {  # build_canonical <case-root>
  local root=$1 s
  mkdir -p "$root/.agents/skills" "$root/.claude/skills"
  for s in "${CORE[@]}" reviewer-discipline; do
    skill "$root/.agents/skills/$s" "$s"
    ln -sfn "../../.agents/skills/$s" "$root/.claude/skills/$s"
  done
  templates "$root/.agents/skills/workflow"
  agent_files "$root/.agents/skills/reviewer-discipline"
  link_agents "$root"
}

# --- source-symlinked layout: self-hosting shape -------------------------------
build_source_symlinked() {  # build_source_symlinked <case-root>
  local root=$1 s
  mkdir -p "$root/skills/core" "$root/.claude/skills"
  for s in "${CORE[@]}" reviewer-discipline; do
    skill "$root/skills/core/$s" "$s"
    ln -sfn "../../skills/core/$s" "$root/.claude/skills/$s"
  done
  templates "$root/skills/core/workflow"
  agent_files "$root/skills/core/reviewer-discipline"
  link_agents "$root"
}

expect() {  # expect <case-root> <lines...>
  local root=$1; shift
  printf '%s\n' "$@" > "$root/expect"
}

# ==============================================================================
# The ten cases
# ==============================================================================

C="$CASES/canonical-complete";        build_canonical "$C"
expect "$C" "exit: 0" "contains: No problems found"

C="$CASES/copied-complete";           build_copied "$C"
expect "$C" "exit: 0" "contains: No problems found"

C="$CASES/source-symlinked-complete"; build_source_symlinked "$C"
expect "$C" "exit: 0" "contains: No problems found"

# A skill the lockfile declares but that never arrived.
C="$CASES/missing-skill";             build_copied "$C"
rm -rf "$C/.claude/skills/plan"
cat > "$C/skills-lock.json" <<'EOF'
{"version":1,"skills":{"workflow":{"source":"robot-denny/cantrip"},"plan":{"source":"robot-denny/cantrip"}}}
EOF
expect "$C" "exit: 1" "contains: plan" "contains: missing from"

# A skill present but with an asset gone -- invisible to a directory listing.
C="$CASES/missing-template";          build_copied "$C"
rm -f "$C/.claude/skills/workflow/templates/spec.md"
expect "$C" "exit: 1" "contains: templates/spec.md" "contains: broken"

# Canonical layout whose .agents tree was deleted: links resolve to nothing.
C="$CASES/dangling-symlink";          build_canonical "$C"
rm -rf "$C/.agents"
expect "$C" "exit: 1" "contains: points at nothing"

# Degraded, not broken. MUST exit 0 -- the assertion most easily got backwards.
C="$CASES/agents-unlinked";           build_copied "$C"
rm -rf "$C/.claude/agents"
expect "$C" "exit: 0" "contains: not registered" "contains: ln -s" "contains: worth fixing"

# The fresh-install condition: no configuration at all is a WORKING configuration.
C="$CASES/no-config";                 build_copied "$C"
expect "$C" "exit: 0" "contains: Every slot is empty" "contains: working configuration"

# Hand-vendored: no lockfile to cross-check against, which is legitimate.
C="$CASES/no-lockfile";               build_copied "$C"
expect "$C" "exit: 0" "contains: No problems found"

# A project's own skills and agents must not appear in the report.
C="$CASES/foreign-units";             build_copied "$C"
skill "$C/.claude/skills/my-own-project-skill" my-own-project-skill
printf -- '---\nname: my-own-agent\n---\n' > "$C/.claude/agents/my-own-agent.md"
expect "$C" "exit: 0" "not_contains: my-own-project-skill" "not_contains: my-own-agent"

# A deliberate selective install: legitimate, passes, but must say what is absent.
C="$CASES/selective-install"
mkdir -p "$C/.claude/skills"
skill "$C/.claude/skills/spec" spec
expect "$C" "exit: 0" "contains: not installed" "contains: selective install is fine"

echo "regenerated $(find "$CASES" -mindepth 1 -maxdepth 1 -type d | wc -l | tr -d ' ') fixtures"
