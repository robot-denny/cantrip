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

# A preprocessor source, in a sibling folder to the compiled stylesheets. Sibling rather than
# nested, because a project that commits both keeps them apart, and a case that only passed
# because the .scss sat under the css/ folder would be testing the folder name rather than the
# suffix — the same trap the header note above describes for src/Web/wwwroot/css/ itself.
preprocessor() {  # preprocessor <case-root> <name>  — reads the body from stdin
  local dir="$1/src/Web/wwwroot/scss"
  mkdir -p "$dir"
  cat > "$dir/$2"
}

# A Razor view. `precheck` never opens one — it counts them by suffix — so the body is one line
# of ordinary block markup, enough that a reader can tell a deliberate fixture from a truncated
# one. The subdirectory is a place a project might keep block views and nothing in the subject may
# depend on it: the search is by suffix from the project root, so a case that only passed because
# of the folder name would be testing the folder name.
view() {  # view <case-root> <relative-dir> <name>
  local dir="$1/$2"
  mkdir -p "$dir"
  printf '<section class="%s">\n  <h2>@Model.Content.Value("heading")</h2>\n</section>\n' \
    "${3%.cshtml}" > "$dir/$3"
}

# A file ASP.NET Core reserves by name. Razor syntax, no markup: `_ViewImports.cshtml` carries
# `@using` directives and `_ViewStart.cshtml` sets a layout. Written by its own helper rather than
# by `view` above, because the whole point of the cases that use it is that these two are NOT
# views to copy conventions from.
razor_directive_file() {  # razor_directive_file <case-root> <relative-dir> <name>
  local dir="$1/$2"
  mkdir -p "$dir"
  cat > "$dir/$3"
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
  "tokensVersion": 3,
  "declarationsFrom": "custom-properties",
  "authoritativeLayer": "custom-properties",
  "refusal": null,
  "layers": [
    {"layer": "custom-properties", "runtimeResolvable": true, "files": 1, "declarations": 4, "names": 4}
  ],
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
  "byPreprocessorFile": [],
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
# `layers: []` with `authoritativeLayer: null` is the third statement this case makes, added in
# Step 3: this project holds no token layer at all. It is a different answer from a project whose
# only layer is build-time, and since Step 4 the two have different exit codes — so a fixture
# asserting the empty one is what keeps the layer report from treating "nothing here" and
# "nothing readable" as the same finding.
#
# **This case is one of the two that hold the refusal gate's boundary.** A project writing every
# color where it is used is the commonest starting state and the one this capability most needs to
# be able to talk to, so it must stay `exit: 0` with `refusal: null`. A gate written as "is there
# a runtime-resolvable layer" rather than "are there layers of which none is runtime-resolvable"
# refuses this project too, and passes every assertion in tokens-preprocessor-only while doing it.
# tokens-two-layers holds the other boundary: a build-time layer PRESENT is not a refusal either.
# `declarationsFrom` is null here for the same reason `authoritativeLayer` is: there are no
# declarations, so there is no layer they came from. `stylesheetsRead` is what says the file was
# opened — the two keys answer different questions and only one of them has an answer here.
cat > "$C/expected-tokens.json" <<'EOF'
{
  "tokensVersion": 3,
  "declarationsFrom": null,
  "authoritativeLayer": null,
  "refusal": null,
  "layers": [],
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
  "byPreprocessorFile": [],
  "declarations": []
}
EOF
expect "$C" \
  "exit: 0" \
  "args: tokens" \
  "stdout_matches: expected-tokens.json" \
  "contains: \"refusal\": null" \
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
  "tokensVersion": 3,
  "declarationsFrom": "custom-properties",
  "authoritativeLayer": "custom-properties",
  "refusal": null,
  "layers": [
    {"layer": "custom-properties", "runtimeResolvable": true, "files": 1, "declarations": 2, "names": 2}
  ],
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
  "byPreprocessorFile": [],
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
  "tokensVersion": 3,
  "declarationsFrom": "custom-properties",
  "authoritativeLayer": "custom-properties",
  "refusal": null,
  "layers": [
    {"layer": "custom-properties", "runtimeResolvable": true, "files": 1, "declarations": 1, "names": 1}
  ],
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
  "byPreprocessorFile": [],
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

# --- tokens-two-layers ----------------------------------------------------------
#
# A project holding TWO token layers: an SCSS source whose `$` variables are the palette the
# build reads, and the compiled `:root` block those variables emit. Both are real, and only one
# of them survives to the browser.
#
# The claim is the one `umbraco-17-guide-scaffolding`'s `## Schema serialization` recipe already
# makes about serialization formats — "record every format found and which one is authoritative"
# — applied to token layers. Stopping at the first layer found reads a fallback as the whole
# answer, and here it would be worse than that in one direction and worse in the other:
#
#   stop at the SCSS   the report names a build-time palette as the project's tokens, and every
#                      swatch built from it is a value the browser never sees
#   stop at the CSS    the report is right about what it read and silent about the fact that a
#                      person editing the palette edits the SCSS, not the stylesheet
#
# So both are reported, and `authoritativeLayer` says which one the swatches come from — stated
# as its own key rather than left to be inferred from the order of the table, because an order is
# a convention a reader has to be told and a key is not.
#
# **The `not_contains:` lines are the case.** A reader that merged the two layers — treating
# `$brand-primary: #1F7A5C` as a token because it looks like one — satisfies every `contains:`
# line here, since the compiled custom properties would still be reported alongside. Only the
# absence of the SCSS names says the layers were kept apart.
#
# Two probes, and they fail differently:
#
#   $brand-primary    a variable whose value the compiled CSS DOES carry, under a different
#                     name. A merging reader reports it as a second token with the same value.
#   $legacy-slate     declared, and emitted nowhere. Its value #475467 appears in no committed
#                     stylesheet, so a report carrying that hex could only have got it by
#                     reading the SCSS — which makes it the sharper of the two.
#
# The `:root` block INSIDE the .scss is the third trap, and it is why the golden matters here
# beyond the substring lines. A reader that simply widened its glob to `.scss` would find three
# more declarations there, with `#{$brand-primary}` as their values — six declarations over two
# files rather than three over one. Every `contains:` line still passes; `byFile` and `counts` do
# not.
C="$CASES/tokens-two-layers"; mkdir -p "$C"
preprocessor "$C" _tokens.scss <<'EOF'
/* The build's palette. None of these names survive compilation — a stylesheet can hold a
   var(--brand-primary) that follows a re-theme, and no markup can read a preprocessor
   variable at all. */
$brand-primary: #1F7A5C;
$brand-ink: #1D2939;
$space-4: 1.25rem;
$legacy-slate: #475467;

/* The bridge to the layer that does survive, and the trap for a reader that widened its glob
   instead of discovering a layer: read as CSS, this block declares three more tokens whose
   values are interpolation syntax no browser ever sees. */
:root {
  --brand-primary: #{$brand-primary};
  --brand-ink: #{$brand-ink};
  --space-4: #{$space-4};
}
EOF
stylesheet "$C" site.css <<'EOF'
:root {
  --brand-primary: #1F7A5C;
  --brand-ink: #1D2939;
  --space-4: 1.25rem;
}

.site-header {
  color: var(--brand-ink);
  background-color: var(--brand-primary);
  padding-block: var(--space-4);
}
EOF
# Hand-authored from the two fixture files above, counted by hand.
#
# `layers` holds one row per layer FOUND, and a layer is found when it holds at least one
# declaration — a `.scss` file that only emits custom properties declares no `$` and is not a
# preprocessor layer, which is the distinction the module docstring calls layer discovery.
#
# The preprocessor row carries counts and nothing else. That is deliberate and not an omission:
# knowing a build-time layer is present and roughly how large it is, is what decides whether the
# palette can be read at render time; knowing what is IN it would need a second parser for a
# second syntax, to report values this script has already said it will not use.
#
# The four `$` declarations sit on lines 4 through 7 of the .scss. The comments above them are
# written `/* */` rather than `//` deliberately: `//` is not CSS, so a reader that had merely
# widened its glob to `.scss` would stall on the first one and find nothing in the file at all —
# which would leave this case's `not_contains:` lines passing against the very implementation
# they exist to fail. A CSS-style comment is stripped by such a reader, so the trap below is
# reachable. That was checked by building that reader and watching the case fail, not assumed.
#
# `declarationsFrom` states which layer the `declarations` table below was read from. Without it
# a consumer holding a two-row `layers` table and a `declarations` table has no way to tell a
# report that kept the layers apart from one that merged them.
cat > "$C/expected-tokens.json" <<'EOF'
{
  "tokensVersion": 3,
  "declarationsFrom": "custom-properties",
  "authoritativeLayer": "custom-properties",
  "refusal": null,
  "layers": [
    {"layer": "custom-properties", "runtimeResolvable": true, "files": 1, "declarations": 3, "names": 3},
    {"layer": "preprocessor-variables", "runtimeResolvable": false, "files": 1, "declarations": 4, "names": 4}
  ],
  "stylesheetsRead": [
    "src/Web/wwwroot/css/site.css"
  ],
  "counts": {
    "declarations": 3,
    "names": 3,
    "color": 2,
    "unclassified": 1,
    "aliases": 0
  },
  "byFile": [
    {"file": "src/Web/wwwroot/css/site.css", "declarations": 3, "names": 3}
  ],
  "byPreprocessorFile": [
    {"file": "src/Web/wwwroot/scss/_tokens.scss", "declarations": 4, "names": 4}
  ],
  "declarations": [
    {"name": "--brand-primary", "value": "#1F7A5C", "group": "color", "aliasOf": null, "file": "src/Web/wwwroot/css/site.css", "line": 2},
    {"name": "--brand-ink", "value": "#1D2939", "group": "color", "aliasOf": null, "file": "src/Web/wwwroot/css/site.css", "line": 3},
    {"name": "--space-4", "value": "1.25rem", "group": "unclassified", "aliasOf": null, "file": "src/Web/wwwroot/css/site.css", "line": 4}
  ]
}
EOF
# The substring lines say what a failure means. The two layer rows are "both layers reported",
# `authoritativeLayer` is the manual check the plan asks for — named, not inferred — and the
# three not_contains lines are the claim the golden alone would state less legibly.
#
# `exit: 0` with `refusal: null` is this case's second job, added in Step 4: it holds the other
# side of the refusal gate's boundary. This project carries the same build-time layer that gets
# tokens-preprocessor-only refused, and it is not refused, because it also carries a layer that
# survives to the browser. A gate that fired on the PRESENCE of a build-time layer rather than on
# the absence of a runtime one would refuse the commonest good shape a project can have.
expect "$C" \
  "exit: 0" \
  "args: tokens" \
  "stdout_matches: expected-tokens.json" \
  "contains: {\"layer\": \"custom-properties\", \"runtimeResolvable\": true" \
  "contains: {\"layer\": \"preprocessor-variables\", \"runtimeResolvable\": false" \
  "contains: \"authoritativeLayer\": \"custom-properties\"" \
  "contains: \"refusal\": null" \
  "not_contains: \$brand-primary" \
  "not_contains: \$legacy-slate" \
  "not_contains: #475467"

# --- tokens-preprocessor-only ---------------------------------------------------
#
# A project whose only token layer is build-time: `.scss` variables, no `.css` anywhere. Three
# claims in one case, because they are one situation rather than three.
#
# **A named argument at a call site is not a declaration.** The counting pattern is anchored to
# the start of a line, and review found that anchor insufficient: the idiomatic multi-line
# mixin call puts each named argument alone on its own line, so `$background:` below looks
# exactly like a declaration to a line-anchored pattern. Three of them here, and the file
# declares two variables — a reader that cannot tell them apart says five.
#
# **`not_contains:` cannot state this claim, and adding those lines would be theatre.** The
# preprocessor layer reports counts only — never a variable's name — so `$background` is absent
# from the output whether the count is right or wrong, and an assertion that it is absent passes
# against the bug it was written for. The count in the golden and in the `contains:` line below
# is the only thing that catches it.
#
# **A project whose only layer is build-time is REFUSED — exit 3.** The read completed and the
# answer is negative: the palette cannot be read at render time, so there is nothing here a
# swatch could follow through a re-theme. The build-time layer is still named authoritative,
# because it is the only one there and it is where a person edits the palette; `declarationsFrom`
# is null, because no layer was parsed for values and saying `custom-properties` here would name
# a read that did not happen.
#
# The refusal is unconditional — no flag turns it into a warning. `guide.py`'s exit 3 is gated
# behind `--strict` because its findings are a backlog someone works through; this one is a
# stop, and a caller that carries on produces a styleguide of invented values.
#
# **The three `not_contains:` lines are a guard, not this case's test, and the difference is
# worth saying plainly because the plan's step text got it wrong.** The preprocessor layer has
# been counts-only since Step 3: it reports `files`, `declarations` and `names` and never a
# variable's name or value. So `#1F7A5C` was already absent from this case's output before the
# refusal existed, and an assertion that it is absent could never have gone RED — it passes
# against the very bug it reads as being written for. What actually went RED here was the exit
# code and the refusal text. The lines stay anyway, as a standing guard: they are what fails if
# a later implementation decides to be helpful and prints the values it has just refused to
# trust, which is the staleness this whole capability exists to refuse.
C="$CASES/tokens-preprocessor-only"; mkdir -p "$C"
preprocessor "$C" _tokens.scss <<'EOF'
$brand-primary: #1F7A5C;
$brand-ink: #1D2939;

/* Named arguments, one per line, at two call sites. Not declarations — a caller passing a
   value is not a place a palette is defined, and counting these would report a palette
   larger than the one a person can edit. */
@include button-variant(
  $background: $brand-primary,
  $border: $brand-ink
);

.card {
  @include shadow(
    $color: $brand-ink
  );
}
EOF
# Hand-authored: two declarations, two names, one file. Five would be the bug.
#
# `refusal` carries the whole of the negative answer, and every other case in this suite carries
# it as null — a key a consumer reads rather than a shape it has to sniff for. Its `message`
# names the layers found, which the `layers` table below states again; that is a formatting of
# the same fact rather than a second entry of it, so a relayed one-line refusal stands on its own
# without the table beside it.
cat > "$C/expected-tokens.json" <<'EOF'
{
  "tokensVersion": 3,
  "declarationsFrom": null,
  "authoritativeLayer": "preprocessor-variables",
  "refusal": {
    "reason": "no-runtime-resolvable-layer",
    "message": "The palette cannot be read at render time. The only token layer this project holds is preprocessor-variables, whose values the build resolves and discards, so nothing in the rendered page can read them. A page built from this layer shows the palette as it stood at the last build, and does not follow a re-theme.",
    "remedy": "Add a custom-property layer that the existing variables feed: one :root block declaring a custom property for each palette entry, with that entry's existing variable as its value. The palette stays defined where it is defined today; the block only makes those values readable at render time. Re-run afterwards: the custom-property layer becomes authoritative, and every token reported is one a page can follow through a re-theme."
  },
  "layers": [
    {"layer": "preprocessor-variables", "runtimeResolvable": false, "files": 1, "declarations": 2, "names": 2}
  ],
  "stylesheetsRead": [],
  "counts": {
    "declarations": 0,
    "names": 0,
    "color": 0,
    "unclassified": 0,
    "aliases": 0
  },
  "byFile": [],
  "byPreprocessorFile": [
    {"file": "src/Web/wwwroot/scss/_tokens.scss", "declarations": 2, "names": 2}
  ],
  "declarations": []
}
EOF
# The exit code and the three refusal lines are what went RED. Each states a separate half of
# what the plan asks the refusal to say: that the palette cannot be read at render time, which
# layers were found, and what to do about it. A refusal naming no remedy would satisfy an
# `exit: 3` assertion and leave the project no way forward, which is the failure this pairing
# guards against.
expect "$C" \
  "exit: 3" \
  "args: tokens" \
  "stdout_matches: expected-tokens.json" \
  "contains: \"reason\": \"no-runtime-resolvable-layer\"" \
  "contains: The palette cannot be read at render time." \
  "contains: The only token layer this project holds is preprocessor-variables" \
  "contains: Add a custom-property layer that the existing variables feed" \
  "contains: {\"layer\": \"preprocessor-variables\", \"runtimeResolvable\": false, \"files\": 1, \"declarations\": 2, \"names\": 2}" \
  "contains: \"declarationsFrom\": null" \
  "contains: {\"file\": \"src/Web/wwwroot/scss/_tokens.scss\", \"declarations\": 2, \"names\": 2}" \
  "not_contains: #1F7A5C" \
  "not_contains: #1D2939" \
  "not_contains: \$brand-primary"

# ==============================================================================
# The three precheck fixtures are one claim seen from three sides
# ==============================================================================
#
# `precheck` answers the spell's precondition in two independent halves — is there a token layer
# a page can read at render time, and is there an existing block view to copy conventions from —
# and the behavior under test is that it names **both**, met or unmet, rather than listing only
# what failed.
#
# That is why three cases and not two. An implementation that printed failures alone passes
# `exit: 3` on both negative cases and leaves the caster unable to tell "this project has views
# and no tokens" from "this project has nothing at all" — which are different situations with
# different remedies, and the second is the one where generating anything at all is harmful. So
# each negative case asserts the MET half by name as well as the unmet one, and the positive case
# asserts both met:
#
#   precheck-both        both halves met            exit 0
#   precheck-no-tokens   views met, tokens unmet    exit 3
#   precheck-greenfield  tokens met, views unmet    exit 3
#
# The two negative cases are deliberately opposite: whichever half an implementation forgets to
# report, one of them fails. A single negative case cannot state that, because the half it happens
# to name is the half that got implemented.
#
# **One branch of `precheck`'s token half has no case here, on purpose.** A project whose only
# layer is build-time gets the token half unmet by relaying `tokens`' existing refusal and remedy,
# and the plan names exactly three precheck fixtures. tokens-preprocessor-only covers the refusal
# itself; what is uncovered is precheck RELAYING it. Recorded rather than quietly left out.

# --- precheck-both --------------------------------------------------------------
#
# The project the spell is for: a palette in custom properties, and blocks whose views already
# establish the conventions a new showcase view will follow. Both halves met, exit 0.
#
# Two views rather than one, so `examples` has an order to get wrong: they are reported in path
# order, and callout sorts before hero while the generator writes hero first. A subject reporting
# walk order rather than sorted order fails the golden here and nowhere else in this suite.
C="$CASES/precheck-both"; mkdir -p "$C"
stylesheet "$C" site.css <<'EOF'
:root {
  --brand-primary: #0B5FFF;
  --brand-ink: #101828;
}

.site-header {
  color: var(--brand-ink);
  background-color: var(--brand-primary);
}
EOF
view "$C" src/Web/Views/Partials/blocks hero.cshtml
view "$C" src/Web/Views/Partials/blocks callout.cshtml
# Hand-authored from the tree above. The token counts are read off the stylesheet; the view count
# is the two files written above, and `examples` is those two paths sorted.
cat > "$C/expected-precheck.json" <<'EOF'
{
  "precheckVersion": 1,
  "preconditionMet": true,
  "halves": [
    {"half": "runtime-resolvable-token-layer", "met": true, "statement": "A token layer that resolves at render time is present: custom-properties (declarations: 2, files: 1). A swatch reading one of these names follows a re-theme with no regeneration.", "remedy": null},
    {"half": "exemplar-block-views", "met": true, "statement": "Razor views on disk: 2. An existing block view is available to copy conventions from: view location, model binding, settings handling and styling approach.", "remedy": null}
  ],
  "tokenLayers": [
    {"layer": "custom-properties", "runtimeResolvable": true, "files": 1, "declarations": 2, "names": 2}
  ],
  "authoritativeLayer": "custom-properties",
  "exemplarViews": {
    "rule": "Counted: every *.cshtml under the project root, except _ViewImports.cshtml, _ViewStart.cshtml (reserved by name) and anything under a skipped directory. No other exclusion: a page template and a partial count as readily as a block view. 'examples' lists the first 5 in path order; 'files' is the total.",
    "files": 2,
    "examples": [
      "src/Web/Views/Partials/blocks/callout.cshtml",
      "src/Web/Views/Partials/blocks/hero.cshtml"
    ]
  }
}
EOF
# The two row lines bind each half's NAME to its met flag on one line, which is what a bare
# `contains: "met": true` cannot do — two halves and one flag each, and a transposition satisfies
# a bag of values found anywhere in the output.
expect "$C" \
  "exit: 0" \
  "args: precheck" \
  "stdout_matches: expected-precheck.json" \
  "contains: \"preconditionMet\": true" \
  "contains: {\"half\": \"runtime-resolvable-token-layer\", \"met\": true," \
  "contains: {\"half\": \"exemplar-block-views\", \"met\": true,"

# --- precheck-no-tokens ---------------------------------------------------------
#
# Twelve block views and not one design token: every color written out where it is used. This is
# the commonest real project, and the half it fails is the one the whole capability rests on.
#
# **Twelve, not one.** A single view would leave `files` at a number an off-by-one or a
# walk-order bug could still produce by accident; twelve is a count that has to have come from
# counting, and it is also what makes the `examples` cap observable — five paths beside `files:
# 12` says the list is a sample rather than the whole set.
#
# The token half here is the NO-LAYERS branch, not the refusal branch: there is no preprocessor
# source in this tree, so `tokens` would report `layers: []` and exit 0. That state has no remedy
# text in `tokens`, because a project with no palette at all has done nothing wrong — it has not
# started. `precheck` is where it becomes a stop, and the remedy asserted below is the one written
# for it.
C="$CASES/precheck-no-tokens"; mkdir -p "$C"
stylesheet "$C" site.css <<'EOF'
.site-header {
  color: #101828;
  background-color: #0B5FFF;
}

.callout {
  border-color: #C2410C;
  padding-block: 0.75rem;
}
EOF
for v in accordion banner callout carousel cta faq gallery hero quote rich-text stats video; do
  view "$C" src/Web/Views/Partials/blocks "$v.cshtml"
done
# Hand-authored. Twelve views were written above and `examples` is the first five in path order;
# the stylesheet declares no custom property, so `tokenLayers` is empty and there is no
# authoritative layer to name.
cat > "$C/expected-precheck.json" <<'EOF'
{
  "precheckVersion": 1,
  "preconditionMet": false,
  "halves": [
    {"half": "runtime-resolvable-token-layer", "met": false, "statement": "This project holds no token layer at all: no custom properties, and no preprocessor variables either. There is nothing to read, so every value a styleguide showed would be one it invented.", "remedy": "Establish the palette first, as a :root block declaring one custom property per entry, and re-run. This is the precondition the spell states rather than assumes: a styleguide generated before a design system exists documents its own invented values back to the people who were meant to supply them."},
    {"half": "exemplar-block-views", "met": true, "statement": "Razor views on disk: 12. An existing block view is available to copy conventions from: view location, model binding, settings handling and styling approach.", "remedy": null}
  ],
  "tokenLayers": [],
  "authoritativeLayer": null,
  "exemplarViews": {
    "rule": "Counted: every *.cshtml under the project root, except _ViewImports.cshtml, _ViewStart.cshtml (reserved by name) and anything under a skipped directory. No other exclusion: a page template and a partial count as readily as a block view. 'examples' lists the first 5 in path order; 'files' is the total.",
    "files": 12,
    "examples": [
      "src/Web/Views/Partials/blocks/accordion.cshtml",
      "src/Web/Views/Partials/blocks/banner.cshtml",
      "src/Web/Views/Partials/blocks/callout.cshtml",
      "src/Web/Views/Partials/blocks/carousel.cshtml",
      "src/Web/Views/Partials/blocks/cta.cshtml"
    ]
  }
}
EOF
# The met half is asserted by name, and that line is this case's reason for existing: an
# implementation that reported only what failed satisfies every other assertion here.
#
# **The three hex lines are a standing guard, not this case's test**, and saying so is the point of
# this note. `precheck` reports a precondition and no declaration table at all, so those literals
# were absent from its output before the first line of it was written — the assertions could not
# have gone RED and catch no implementation anybody would write today. They stay because they are
# what fails if a later version decides to be helpful and prints the palette beside the verdict,
# which is the leak this capability refuses everywhere else.
expect "$C" \
  "exit: 3" \
  "args: precheck" \
  "stdout_matches: expected-precheck.json" \
  "contains: \"preconditionMet\": false" \
  "contains: {\"half\": \"exemplar-block-views\", \"met\": true," \
  "contains: {\"half\": \"runtime-resolvable-token-layer\", \"met\": false," \
  "contains: \"files\": 12" \
  "contains: Establish the palette first" \
  "not_contains: #0B5FFF" \
  "not_contains: #101828" \
  "not_contains: #C2410C"

# --- precheck-greenfield --------------------------------------------------------
#
# The refusal at its most intense: a palette already in custom properties, and no block view
# anywhere. There is nothing to copy, so a generated showcase view would ESTABLISH this project's
# conventions rather than follow them — and every real block written afterwards gets copied from a
# page of color swatches. That is the hazard this half exists to guard, and it is worst on a
# project at setup time, which is exactly when a styleguide looks like a cheap first win.
#
# **The two Razor files in the tree are the case's sharp edge.** `_ViewImports.cshtml` and
# `_ViewStart.cshtml` are `.cshtml` files, they are what a fresh scaffold ships, and they are not
# views to copy anything from: ASP.NET Core reserves both names, and they carry directives rather
# than markup. A subject counting every `.cshtml` reports two views here, calls this half met, and
# exits 0 — so the exit code, the met flag and `files: 0` all fail together on the one
# implementation that is easiest to write.
C="$CASES/precheck-greenfield"; mkdir -p "$C"
stylesheet "$C" site.css <<'EOF'
:root {
  --brand-primary: #0B5FFF;
  --brand-ink: #101828;
}
EOF
razor_directive_file "$C" src/Web/Views _ViewImports.cshtml <<'EOF'
@using Umbraco.Cms.Web.Common.PublishedModels
@inject IPublishedValueFallback PublishedValueFallback
EOF
razor_directive_file "$C" src/Web/Views _ViewStart.cshtml <<'EOF'
@{
    Layout = "master.cshtml";
}
EOF
# Hand-authored. `files: 0` with two `.cshtml` files on disk is the whole claim of this case, and
# `examples: []` is its other half — a subject that counted zero and still listed a path would be
# reporting two different answers at once.
cat > "$C/expected-precheck.json" <<'EOF'
{
  "precheckVersion": 1,
  "preconditionMet": false,
  "halves": [
    {"half": "runtime-resolvable-token-layer", "met": true, "statement": "A token layer that resolves at render time is present: custom-properties (declarations: 2, files: 1). A swatch reading one of these names follows a re-theme with no regeneration.", "remedy": null},
    {"half": "exemplar-block-views", "met": false, "statement": "No Razor view is on disk, so there is no existing markup convention to copy.", "remedy": "Author at least one real block view before generating a styleguide, or take the conventions from another codebase and say which. With nothing to copy, the styleguide's own showcase view becomes the exemplar every later block is copied from, which sets the project's conventions from a color-swatch page rather than from its content."}
  ],
  "tokenLayers": [
    {"layer": "custom-properties", "runtimeResolvable": true, "files": 1, "declarations": 2, "names": 2}
  ],
  "authoritativeLayer": "custom-properties",
  "exemplarViews": {
    "rule": "Counted: every *.cshtml under the project root, except _ViewImports.cshtml, _ViewStart.cshtml (reserved by name) and anything under a skipped directory. No other exclusion: a page template and a partial count as readily as a block view. 'examples' lists the first 5 in path order; 'files' is the total.",
    "files": 0,
    "examples": []
  }
}
EOF
# `files: 0` and `examples: []` are the exclusion's whole assertion, and there is deliberately no
# `not_contains: _ViewImports` beside them: the rule string names both reserved files, as it must
# to be checkable, so an assertion that the name is absent would fail on a correct report. The met
# half is named here too, so a caster reading this report can tell it from precheck-no-tokens.
expect "$C" \
  "exit: 3" \
  "args: precheck" \
  "stdout_matches: expected-precheck.json" \
  "contains: \"preconditionMet\": false" \
  "contains: {\"half\": \"runtime-resolvable-token-layer\", \"met\": true," \
  "contains: {\"half\": \"exemplar-block-views\", \"met\": false," \
  "contains: \"files\": 0" \
  "contains: \"examples\": []" \
  "contains: Author at least one real block view"

# --- precheck-build-time-tokens -------------------------------------------------
#
# The third state of the token half: a palette exists, and no rendered page can read it. Views
# are present, so this is the one case where the token half fails for a reason that has a
# remedy already written for it.
#
# Added after Step 5's review, and the plan named only three precheck cases. The reason it earns
# a fourth: this branch relays wording `tokens` owns — `refusal["message"]` and
# `refusal["remedy"]` — and nothing else in the suite exercised the relay. A rename on either
# side would have passed every test and surfaced as a traceback on the one path a project reaches
# when its palette exists but cannot be read. The golden below holds the relayed text verbatim,
# so the relay is what breaks the case rather than being what nobody checks.
#
# Both strings are read off the script's REFUSAL_MESSAGE and REFUSAL_REMEDY constants by hand,
# with the layer phrase filled in for a single build-time layer. That is the point: if this
# golden and those constants disagree, one of them changed without the other.
C="$CASES/precheck-build-time-tokens"; mkdir -p "$C"
view "$C" src/Web/Views/Partials/blocks hero.cshtml
view "$C" src/Web/Views/Partials/blocks callout.cshtml
preprocessor "$C" _tokens.scss <<'EOF'
$brand-primary: #1F7A5C;
$brand-ink: #1D2939;
EOF
cat > "$C/expected-precheck.json" <<'EOF'
{
  "precheckVersion": 1,
  "preconditionMet": false,
  "halves": [
    {"half": "runtime-resolvable-token-layer", "met": false, "statement": "The palette cannot be read at render time. The only token layer this project holds is preprocessor-variables, whose values the build resolves and discards, so nothing in the rendered page can read them. A page built from this layer shows the palette as it stood at the last build, and does not follow a re-theme.", "remedy": "Add a custom-property layer that the existing variables feed: one :root block declaring a custom property for each palette entry, with that entry's existing variable as its value. The palette stays defined where it is defined today; the block only makes those values readable at render time. Re-run afterwards: the custom-property layer becomes authoritative, and every token reported is one a page can follow through a re-theme."},
    {"half": "exemplar-block-views", "met": true, "statement": "Razor views on disk: 2. An existing block view is available to copy conventions from: view location, model binding, settings handling and styling approach.", "remedy": null}
  ],
  "tokenLayers": [
    {"layer": "preprocessor-variables", "runtimeResolvable": false, "files": 1, "declarations": 2, "names": 2}
  ],
  "authoritativeLayer": "preprocessor-variables",
  "exemplarViews": {
    "rule": "Counted: every *.cshtml under the project root, except _ViewImports.cshtml, _ViewStart.cshtml (reserved by name) and anything under a skipped directory. No other exclusion: a page template and a partial count as readily as a block view. 'examples' lists the first 5 in path order; 'files' is the total.",
    "files": 2,
    "examples": [
      "src/Web/Views/Partials/blocks/callout.cshtml",
      "src/Web/Views/Partials/blocks/hero.cshtml"
    ]
  }
}
EOF
# No `not_contains:` on the SCSS hex values here. They would pass whatever the relay did — the
# preprocessor layer reports counts only — and an assertion that cannot fail is not a guard on
# this case, it is decoration. What holds this case is the golden.
expect "$C" \
  "exit: 3" \
  "args: precheck" \
  "stdout_matches: expected-precheck.json" \
  "contains: {\"half\": \"runtime-resolvable-token-layer\", \"met\": false," \
  "contains: {\"half\": \"exemplar-block-views\", \"met\": true," \
  "contains: whose values the build resolves and discards" \
  "contains: Add a custom-property layer that the existing variables feed"

echo "regenerated $(find "$CASES" -mindepth 1 -maxdepth 1 -type d | wc -l | tr -d ' ') fixtures"
