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
#
# A fourth custom property joined tokens-custom-properties in Step 2: `--role-primary`, whose
# declared value is `var(--brand-primary)`. It introduces NO new literal, which is why tokens-none
# needs no matching addition — the three shared values are still the whole of what the pairing
# rests on, and the fourth property tests something the pair was never about.

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
# That trap is sprung by `expected-tokens.json`, added in Step 2 once the report format existed
# to state. `contains:` and `not_contains:` are presence checks — nothing in that grammar counts
# occurrences, so a subject reporting a token once and one reporting it three times satisfy
# `contains: --brand-ink` identically, and `--brand-ink` is declared once here and used twice. The
# golden file states the whole document, so a subject emitting a row per USE rather than per
# DECLARATION fails on the row count while passing every substring line in this expect file.
#
# The fourth property, `--role-primary: var(--brand-primary)`, is the one-hop alias rule. Its
# declared value is a `var()`, so its value SHAPE says nothing about what it is; it is a color
# only because `--brand-primary` was collected in the same read and is one. Three things have to
# hold at once, and the golden holds all three — group `color`, `aliasOf` naming the target, and
# `value` still the verbatim `var(--brand-primary)`. Classification alone would also pass against
# a subject that resolved the chain to `#0B5FFF`, so the verbatim value is what proves it did not.
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
  --role-primary: var(--brand-primary);
}

.site-header {
  color: var(--brand-ink);
  background-color: var(--brand-primary);
  padding-block: var(--space-3);
}

.site-header__title {
  color: var(--brand-ink);
  border-block-end-color: var(--role-primary);
}

/* Not a token: a literal this project never lifted into the palette. It must not be
   reported, because a styleguide swatch for it could never follow a re-theme. */
.legacy-callout {
  border-color: #C2410C;
}
EOF
# The expected report — hand-authored, from the stylesheet above and nothing else.
#
# Written the way tests/make-guide-fixtures.sh authors its expected dossiers: from intent, not
# captured from a run. A golden captured from output asserts that the code still does what it
# did; one authored from the fixture asserts that it does what was asked. Every value below was
# read off the stylesheet by hand — the line numbers included.
#
# It fixes the report's serialization as well as its content, and one choice in there is
# deliberate enough to name: **one line per declaration**. The rest of the document is
# two-space-indented JSON like every other document this toolkit emits, but a token list is a
# table, and a row per line is what lets a substring assertion bind a name to its value and its
# group — `contains: {"name": "--space-3", "value": "0.75rem", "group": "unclassified"` says
# something that four separate `contains:` lines cannot. It also makes a golden diff point at the
# token that changed instead of at a field three tokens away.
#
# Nothing is masked. Every value here is read from the fixture or counted from it, so there is no
# environment-dependent line to neutralize — unlike guide-check's dossiers, whose signature is a
# hash the subject computes and therefore cannot be hand-authored.
#
# `stylesheetsRead` states the path relative to --project-root, which is what keeps this file
# machine-independent, and it is what tokens-none leans on to say the read happened at all.
cat > "$C/expected-tokens.json" <<'EOF'
{
  "tokensVersion": 1,
  "layer": "custom-properties",
  "stylesheetsRead": [
    "src/Web/wwwroot/css/site.css"
  ],
  "counts": {
    "declarations": 4,
    "names": 4,
    "color": 3,
    "unclassified": 1,
    "aliases": 1
  },
  "byFile": [
    {"file": "src/Web/wwwroot/css/site.css", "declarations": 4, "names": 4}
  ],
  "declarations": [
    {"name": "--brand-primary", "value": "#0B5FFF", "group": "color", "aliasOf": null, "file": "src/Web/wwwroot/css/site.css", "line": 2},
    {"name": "--brand-ink", "value": "#101828", "group": "color", "aliasOf": null, "file": "src/Web/wwwroot/css/site.css", "line": 3},
    {"name": "--space-3", "value": "0.75rem", "group": "unclassified", "aliasOf": null, "file": "src/Web/wwwroot/css/site.css", "line": 4},
    {"name": "--role-primary", "value": "var(--brand-primary)", "group": "color", "aliasOf": "--brand-primary", "file": "src/Web/wwwroot/css/site.css", "line": 5}
  ]
}
EOF
# The substring lines are not redundant with the golden — they are what a failure reads as. A
# golden mismatch prints a diff; these print the claim that broke. The three bare values are the
# pairing's half (see tokens-none), and the four row lines are the classification claims.
expect "$C" \
  "exit: 0" \
  "args: tokens" \
  "stdout_matches: expected-tokens.json" \
  "contains: #0B5FFF" \
  "contains: #101828" \
  "contains: 0.75rem" \
  "contains: {\"name\": \"--brand-primary\", \"value\": \"#0B5FFF\", \"group\": \"color\", \"aliasOf\": null" \
  "contains: {\"name\": \"--brand-ink\", \"value\": \"#101828\", \"group\": \"color\", \"aliasOf\": null" \
  "contains: {\"name\": \"--space-3\", \"value\": \"0.75rem\", \"group\": \"unclassified\", \"aliasOf\": null" \
  "contains: {\"name\": \"--role-primary\", \"value\": \"var(--brand-primary)\", \"group\": \"color\", \"aliasOf\": \"--brand-primary\"" \
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
# The positive half arrived with Step 2, as `expected-tokens.json`: the whole empty document,
# stating that the stylesheet WAS read and declared nothing. That is exactly what the four
# not_contains lines cannot say — a subject that crashed before opening a single file, or one
# that never found the stylesheet, satisfies all four of them.
#
# Note the pairing of `stylesheetsRead` with an EMPTY `byFile`: one file was read, and no file
# declared anything. Those two lines together are the whole claim of this case, and no single
# line states it — a report naming no stylesheet at all would be the crash, and a report with a
# byFile entry would mean something was found.
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
cat > "$C/expected-tokens.json" <<'EOF'
{
  "tokensVersion": 1,
  "layer": "custom-properties",
  "stylesheetsRead": [
    "src/Web/wwwroot/css/site.css"
  ],
  "counts": {
    "declarations": 0,
    "names": 0,
    "color": 0,
    "unclassified": 0,
    "aliases": 0
  },
  "byFile": [],
  "declarations": []
}
EOF
expect "$C" \
  "exit: 0" \
  "args: tokens" \
  "stdout_matches: expected-tokens.json" \
  "not_contains: #0B5FFF" \
  "not_contains: #101828" \
  "not_contains: 0.75rem" \
  "not_contains: #C2410C"

# --- tokens-string-terminator ---------------------------------------------------
#
# A `;` inside an ordinary property's value must not open a declaration position. Added in Step
# 2 after review found the scanner fabricating tokens: the outer scan reset its
# declaration-position flag on every `;`, `{` and `}` wherever one appeared, including inside a
# quoted string, while only the VALUE reader tracked quotes. So a string holding `; --name:` was
# read as a real declaration, and the reader — starting mid-string with no memory that a quote
# was open — took the string's own closing quote as an opening one and swallowed the rest of the
# file into that token's value.
#
# The cost was the one this script must never pay: the genuine tokens after that point vanished,
# a token nobody declared appeared, and the run exited 0 with well-formed JSON. Nothing about
# the output said it was wrong.
#
# Two shapes, because they fail differently and only one of them was ever broken:
#
#   the quoted string  `content: "Note; --brand-fake: #FF00FF end"` — the reproduction. The
#                      fabricated name is asserted absent, and `--real` present, because a
#                      regression loses the real token as well as inventing the fake one.
#   the data URI       `url(data:image/png;base64,…)` — semicolons at paren depth 1. This shape
#                      never broke, and it is here so a fix that tracks quotes but forgets
#                      parens does not pass.
#
# `--spacing` follows `--real` inside the same block so the case also states that a second
# declaration is still found after the first — a scanner that resynchronized badly could report
# one and drop the other.
C="$CASES/tokens-string-terminator"; mkdir -p "$C"
stylesheet "$C" site.css <<'EOF'
.tooltip::after {
  content: "Note; --brand-fake: #FF00FF end";
}

.icon {
  background: url(data:image/png;base64,iVBORw0KGgo=);
}

:root {
  --real: #00AA00;
  --spacing: 1rem;
}
EOF
# Hand-authored from the stylesheet above, line numbers counted by hand: `--real` sits on line
# 10 and `--spacing` on line 11. `byFile` carries one entry because one file declared something.
cat > "$C/expected-tokens.json" <<'EOF'
{
  "tokensVersion": 1,
  "layer": "custom-properties",
  "stylesheetsRead": [
    "src/Web/wwwroot/css/site.css"
  ],
  "counts": {
    "declarations": 2,
    "names": 2,
    "color": 1,
    "unclassified": 1,
    "aliases": 0
  },
  "byFile": [
    {"file": "src/Web/wwwroot/css/site.css", "declarations": 2, "names": 2}
  ],
  "declarations": [
    {"name": "--real", "value": "#00AA00", "group": "color", "aliasOf": null, "file": "src/Web/wwwroot/css/site.css", "line": 10},
    {"name": "--spacing", "value": "1rem", "group": "unclassified", "aliasOf": null, "file": "src/Web/wwwroot/css/site.css", "line": 11}
  ]
}
EOF
# The golden alone would catch this, but the two named lines are what a failure reads as: one
# says the fabricated token is gone, the other that the real one survived. A regression that
# only invented a token and a regression that only lost one are different bugs.
expect "$C" \
  "exit: 0" \
  "args: tokens" \
  "stdout_matches: expected-tokens.json" \
  "not_contains: --brand-fake" \
  "not_contains: #FF00FF" \
  "contains: {\"name\": \"--real\", \"value\": \"#00AA00\", \"group\": \"color\"" \
  "contains: {\"name\": \"--spacing\", \"value\": \"1rem\", \"group\": \"unclassified\""

# --- tokens-escaped-selector ----------------------------------------------------
#
# A backslash escapes the next character everywhere in CSS, not only inside a string, and a
# scanner that tracks paren depth has to honour that or the depth goes wrong and stays wrong.
#
# This case exists because the fix for tokens-string-terminator introduced exactly that bug and
# the suite did not catch it. Gating the declaration position on `depth == 0` was right; counting
# an ESCAPED paren toward the depth was not. Utility-framework class names carry escaped parens
# by the hundred — `.thumb-\(--fake-token\)` below is the shape — so on a real bundle the depth
# never returned to zero at the following `{`, and every declaration in those rules was skipped.
#
# It was caught by checking the report against the stylesheet's own text rather than against the
# previous run: the scanner and its predecessor disagreed by 80 rows, and only counting
# `name:` occurrences in the source said which of them was right. A fixture is the cheaper
# version of that check, which is why this one exists.
#
# The escaped `\.` in the second selector is the same rule in its commoner form. `--fake-token`
# sits inside the escaped parens and is asserted ABSENT: it is part of a class name, never a
# declaration, and a scanner confused about escapes could read it as one.
C="$CASES/tokens-escaped-selector"; mkdir -p "$C"
stylesheet "$C" site.css <<'EOF'
.thumb-\(--fake-token\) {
  color: #112233;
}

:where(.stack-2\.5 > :not(:last-child)) {
  --after-escape: #445566;
}
EOF
# Hand-authored: one real declaration, on line 6. If the depth bookkeeping is wrong this file
# reports nothing at all, which is why `declarations` being 1 rather than 0 is the whole claim.
cat > "$C/expected-tokens.json" <<'EOF'
{
  "tokensVersion": 1,
  "layer": "custom-properties",
  "stylesheetsRead": [
    "src/Web/wwwroot/css/site.css"
  ],
  "counts": {
    "declarations": 1,
    "names": 1,
    "color": 1,
    "unclassified": 0,
    "aliases": 0
  },
  "byFile": [
    {"file": "src/Web/wwwroot/css/site.css", "declarations": 1, "names": 1}
  ],
  "declarations": [
    {"name": "--after-escape", "value": "#445566", "group": "color", "aliasOf": null, "file": "src/Web/wwwroot/css/site.css", "line": 6}
  ]
}
EOF
expect "$C" \
  "exit: 0" \
  "args: tokens" \
  "stdout_matches: expected-tokens.json" \
  "not_contains: --fake-token" \
  "contains: {\"name\": \"--after-escape\", \"value\": \"#445566\", \"group\": \"color\""

echo "regenerated $(find "$CASES" -mindepth 1 -maxdepth 1 -type d | wc -l | tr -d ' ') fixtures"
