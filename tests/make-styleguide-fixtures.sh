#!/usr/bin/env bash
#
# Regenerate the styleguide-check suite — fixtures for the /styleguide spell's script.
#
# Generated rather than hand-built, for the reason tests/make-fixtures.sh records and
# tests/make-guide-fixtures.sh repeats: a malformed fixture fails exactly like a real bug,
# and the debugging goes to the wrong place first. Regenerating is how you clear that
# suspicion.
#
# Each case is a minimal fake project tree plus an `expect` file. Minimal means: only the
# files the subject has to read. For `tokens` that is stylesheets and nothing else — no
# document types, no serialization folder, no views. A project tree carrying more than the
# subcommand reads invites a later reader to believe the extra files matter.
#
# The stylesheets sit under src/Web/wwwroot/css/, which is where a stylesheet lives in the
# project shape the rest of these fixtures assume. Nothing in the subject may depend on that
# path — a project puts its CSS wherever it likes — so a case that starts passing only
# because of the folder name is a case that has stopped testing anything.
#
# Usage:  tests/make-styleguide-fixtures.sh

set -euo pipefail
cd "$(dirname "$0")" || exit 2

CASES="styleguide-check"
rm -rf "$CASES"
mkdir -p "$CASES"

# The suite's `subject` names the executable under test — a script that does not exist yet.
# Every case therefore fails as "subject missing or not executable", which is this suite's
# RED signal until Step 2 lands. `subject` is regenerated here because this script wipes the
# directory it lives in; a hand-placed one would vanish on the next run and every case would
# then fail pointing nowhere near its cause.
printf 'skills/umbraco-17/spellbook/styleguide/scripts/styleguide.py\n' > "$CASES/subject"

expect() {  # expect <case-root> <lines...>
  local root=$1; shift
  printf '%s\n' "$@" > "$root/expect"
}

stylesheet() {  # stylesheet <case-root> <name>  — reads the body from stdin
  local dir="$1/src/Web/wwwroot/css"
  mkdir -p "$dir"
  cat > "$dir/$2"
}

# ==============================================================================
# The two fixtures are one claim seen from both sides
# ==============================================================================
#
# The behavior under test is: a custom property DECLARATION is a token, and a color literal
# is not — whatever else the stylesheet contains. Neither case can state that alone.
#
# A single positive case passes against a reader that simply greps for hex literals, because
# in a fixture whose only colors are token values the two readings agree. A single negative
# case passes against a reader that prints nothing at all.
#
# So the same three values — #0B5FFF, #101828 and 0.75rem — appear in BOTH trees, declared
# as custom properties in one and written as literal property values in the other, and each
# case asserts the opposite half:
#
#   tokens-custom-properties  every one of the three must be reported
#   tokens-none               not one of the three may appear anywhere in the output
#
# A reader that cannot tell a declaration from a value fails one of the two, whichever way
# round it is wrong. That is the whole point of pairing them, and it is why the values must
# stay identical across the two fixtures — "fixing" one set to a distinct palette would leave
# both cases passing and the claim untested.

# --- tokens-custom-properties --------------------------------------------------
#
# The runtime-resolvable layer: three custom properties on `:root`. Two colors and one that
# is not, because the classifier Step 2 adds must be driven by the VALUE's shape and never by
# the property's name — `--space-3` is the case a name-based classifier gets right by luck and
# `--brand-*` are the ones it gets wrong.
#
# The sheet also uses its own tokens through `var()`, the way a real stylesheet does. That puts
# the declaration-versus-use ambiguity INTO the fixture: each name appears at a declaration and
# again at one or more use sites, so a reader that matches the name anywhere rather than at a
# declaration has something here to get wrong.
#
# What this case does NOT assert is that it got it right. `contains:` and `not_contains:` are
# presence checks — nothing in the grammar counts occurrences, so a subject reporting a token
# once and one reporting it three times satisfy `contains: --brand-ink` identically. The
# assertion that closes this is a `stdout_matches:` golden file, and it cannot be written until
# Step 2 defines the report format. Until then the `var()` usage is realism plus a trap laid for
# an assertion that does not exist yet — which is worth saying plainly, because a comment
# claiming a guard that is not here is how the next reader stops looking for one.
#
# `.legacy-callout` holds a hex the project hardcoded and never made a token. It is the
# not_contains below, and it is what fails a reader that collects colors instead of
# declarations.
C="$CASES/tokens-custom-properties"; mkdir -p "$C"
stylesheet "$C" site.css <<'EOF'
:root {
  --brand-primary: #0B5FFF;
  --brand-ink: #101828;
  --space-3: 0.75rem;
}

.site-header {
  color: var(--brand-ink);
  background-color: var(--brand-primary);
  padding-block: var(--space-3);
}

.site-header__title {
  color: var(--brand-ink);
}

/* Not a token: a literal this project never lifted into the palette. It must not be
   reported, because a styleguide swatch for it could never follow a re-theme. */
.legacy-callout {
  border-color: #C2410C;
}
EOF
expect "$C" \
  "exit: 0" \
  "args: tokens" \
  "contains: --brand-primary" \
  "contains: #0B5FFF" \
  "contains: --brand-ink" \
  "contains: #101828" \
  "contains: --space-3" \
  "contains: 0.75rem" \
  "not_contains: #C2410C"

# --- tokens-none ---------------------------------------------------------------
#
# A project with no token layer at all: every color written out where it is used. This is the
# common starting state, not an error, so the read COMPLETES — exit 0 — and reports nothing.
# A project that simply has no palette yet is not a failed read, and treating it as one would
# make the spell refuse the projects it most needs to talk to.
#
# The assertions are the four not_contains lines. Three are the shared values, which carry the
# declaration-versus-value claim jointly with the case above; on their own they would also pass
# against a subject that printed nothing whatsoever, which is why neither case means much
# without the other. The fourth is `#C2410C`, which is never a token in either fixture and is
# asserted absent in both — a value no case declares should not surface from any of them.
#
# Deliberately NOT asserted here: any wording for "found nothing". The report's phrasing does
# not exist until Step 2, and a fixture that invented one would be asserting a string this
# step made up rather than a behavior anybody asked for. Step 2 adds the positive half.
C="$CASES/tokens-none"; mkdir -p "$C"
stylesheet "$C" site.css <<'EOF'
.site-header {
  color: #101828;
  background-color: #0B5FFF;
  padding-block: 0.75rem;
}

.site-header__title {
  color: #101828;
}

.legacy-callout {
  border-color: #C2410C;
  padding-block: 0.75rem;
}
EOF
expect "$C" \
  "exit: 0" \
  "args: tokens" \
  "not_contains: #0B5FFF" \
  "not_contains: #101828" \
  "not_contains: 0.75rem" \
  "not_contains: #C2410C"

echo "regenerated $(find "$CASES" -mindepth 1 -maxdepth 1 -type d | wc -l | tr -d ' ') fixtures"
