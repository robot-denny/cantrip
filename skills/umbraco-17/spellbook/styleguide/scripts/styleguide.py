#!/usr/bin/env python3
"""styleguide.py — the deterministic half of the /styleguide spell.

Everything about a project's design tokens that has one right answer lives here: finding the
stylesheets, reading the custom-property declarations out of them, and classifying each one by
the shape of its value. The spell owns the rest — the prose, the page, and every write to the
CMS. Nothing in this script writes anything, anywhere.

The split is the one guide.py settled and this script inherits: a model asked to read a palette
out of a stylesheet will paraphrase it, and a paraphrased hex is wrong in a way nobody notices
until a swatch ships the wrong brand color. A script asked to name a token group produces
`--space-brand: 1rem` filed under colors. So the read is code and the naming is not.

## What counts as a design token here

**A value that survives to the browser.** That is not the general definition of the term — a
preprocessor variable is a real design token by any normal usage — it is the only definition
under which "reads the project's design tokens live, without regeneration" can be true. A
styleguide page that renders a swatch from `var(--brand-primary)` follows a re-theme by itself;
one that renders a hex the build inlined three months ago does not, and looks identical.

So in practice: **CSS custom properties**. Everything else is a different layer — real design
tokens by any normal usage, and still not ones a page can read — which makes "what layers does
this project hold, and which of them is authoritative" a question with an answer of its own,
below.

## The layers a project holds, and which one is authoritative

**Every layer found is recorded, and the authoritative one is named.** That is the rule
`umbraco-17-guide-scaffolding`'s `## Schema serialization` recipe already states about
serialization formats, kept here for the reason it gives: a project can hold more than one, and
stopping at the first reads a fallback as the whole answer.

Two layers are recognized:

    custom-properties        `--name:` declarations in a `.css` file      runtime-resolvable
    preprocessor-variables   `$name:` in `.scss`/`.sass`, `@name:`        build-time only
                             in `.less`

**Custom properties are authoritative whenever present**, because they are the only layer whose
values survive to the browser. The common shape — a `.scss` holding the palette and emitting a
`:root` block from it — holds both, is read from the custom properties, and is told the other
layer is there, because that is where a person edits the palette.

The authoritative layer is named in its own key rather than left to be inferred from the order of
the table. An order is a convention a reader has to be told; a key is not.

**Finding a preprocessor layer is not parsing one.** Its counts come from one anchored regular
expression per sigil, applied to lines that begin outside any paren group and with `/* */`
comments blanked first. No value is read, and no `@import` is followed. What the report needs is
that the layer is *present* and roughly how large, because that is what decides whether a palette
can be read at render time; what is *in* it would need a second parser for a second syntax, to
produce values this script has already promised not to use. A `.scss` declaring no `$` is not a
preprocessor layer at all — a file that merely emits custom properties is the bridge between the
layers, not a layer of its own.

**The count is still approximate, and it errs in both directions.** Stating that precisely matters
more than the error does, because a number documented as wrong in one direction gets trusted in
the other:

- **Under**, by design: a declaration written mid-line after a `;` — `color: red; $foo: bar;` — is
  not counted, because the pattern is anchored to the start of a line. Closing that would mean
  finding statement boundaries inside a line, which is the second parser this section refuses, for
  a shape almost nothing writes.
- **Over**, in one narrow case: a `//` line comment is not stripped, so a `$name:` reached through
  one — which takes a `/*` block opening mid-line — can still be counted.

Neither moves the answer this number exists to give. A project is over or under by a few on a count
whose only job is "is this layer here, and is it big", and the shapes that fool it are shapes that
still mark a project holding a preprocessor palette.

### A layer that cannot be read at render time is refused, not baked

A project holding layers of which **none is runtime-resolvable** — a preprocessor palette with no
custom-property layer anywhere — gets a `refusal` in its report and **exit 3**. The read
completed; the answer is negative.

**The alternative was a clearly-labelled baked snapshot, and it is worse than useless.** Reading
the preprocessor values and emitting them would produce a report that looks exactly like a good
one, and a page built from it would be right on the day it shipped and silently wrong from the
first palette edit onward. That is the failure this capability exists to refuse, and a label
saying "these values may be stale" does not survive being copied into a swatch. So the refusal
carries **no token value at all** — the message is built from the layer names and the counts,
which is why nothing here ever opens a preprocessor file for a value.

**What it gives instead is the remedy**, stated concretely enough to act on: a custom-property
layer that the existing variables feed. That is an afternoon of front-end work, it moves no
palette entry out of the file it lives in today, and after it every claim this script makes about
a project becomes true. Naming it is the difference between a refusal and a dead end.

Two adjacent states are deliberately **not** this refusal:

- **No layers at all** — a project writing every color where it is used — is a completed read
  reporting nothing, exit 0. That is the common starting state, and the project this capability
  most needs to be able to talk to.
- **A build-time layer beside a runtime one** is exit 0 as well. The gate fires on the absence of
  something readable, never on the presence of something build-time; the commonest good shape in
  the wild is a preprocessor palette that emits a `:root` block.

### Why a utility framework's theme configuration is not a third layer

It is absent deliberately, not pending.

A utility framework's theme now commonly lives in an `@theme { }` block *inside a `.css` file*,
declaring ordinary custom properties that ship to the browser — so the scan below already reports
it, correctly, as part of the runtime layer. Counting it again as build-time would say the
opposite of what is true.

The older shape — a theme in a JavaScript config that never reaches the browser — cannot be told
from the newer one by looking at the filesystem, because a project may keep that config and have
its values compiled into custom properties regardless. Detecting it would take a list of framework
config filenames, which is the kind of list `SKIP_DIRS` below refuses for going stale, and the
list would be wrong about runtime-resolvability on exactly the projects that migrated. So what
gets reported is the layer a person can act on, and a framework config emitting nothing readable
reports as no layer — which is what is on disk.

## What it reads, and what it does not

Walked from `--project-root`, skipping build output and dependency trees (`SKIP_DIRS`). Two
consequences worth stating plainly rather than discovering:

- **A `.scss` or `.less` source is never read for values**, even though a custom property
  declared in one survives compilation perfectly well. Those files are counted for layer
  discovery and nothing more. Reading them for values here would collapse two layers into one
  number, and it would take a second parser besides: `//` line comments are not CSS, and a
  scanner that stripped them would have to tell a comment from the `//` in a `url(https://…)`.

- **A committed vendor stylesheet contributes its properties**, because it is a stylesheet in
  the project and its properties do resolve at render time. Every declaration carries the file
  it was read from, so a person can tell a framework's palette from the project's own; guessing
  by path would need a project fact this pack must not hold.

A project whose compiled CSS is not committed therefore reports nothing found. That is a
completed read of what is on disk, not a failure, and it is the honest answer — the remedy is a
committed stylesheet or a build, and neither is this script's to perform.

## Classification: the value's shape, never the property's name

A declaration is reported in one of two groups:

    color           the whole declared value is unambiguously a color
    unclassified    everything else, reported WITH its declared value

There is no third group, and the absence is the point. `--space-brand` and `--brand-radius`
read as colors to any name-based classifier, and a swatch grid built from that output is wrong
in a way that looks deliberate. Colors are the one group whose value shape is unambiguous, so
colors are the one group this script names; every other grouping is a person's job, and
`unclassified` carries the value so it is a job they can do from the report.

"The whole declared value" is load bearing. `--shadow-1: 0 1px 2px rgba(16,24,40,.08)` is a
shadow, not a color, and a classifier matching `rgba(` anywhere in the value files it under
colors. So a color is: a hex literal, or a named CSS color, or a *sole* color-function call
whose closing paren is the last character of the value.

## var(): reported, never resolved — and classified by exactly one hop

A declared value of the form `var(--other)` is emitted **verbatim** and marked `aliasOf:
"--other"`. The chain is never walked to a literal. Resolving it would be a second
implementation of what the browser already does, and the two would eventually disagree.

**One exception to verbatim, and it is the only one.** A comment *inside* a value is blanked to
spaces rather than removed, because removing it would move every line number after it (see
`strip_comments`). So `--brand-primary: #0B5FFF /* Pantone 2728C */` reports its value with that
run of spaces still in it. Collapsing them would be a second transformation of a value this
script promised not to transform, and preserving the comment text would report a value no
browser ever sees; blanking is the least-wrong of the three, and it is recorded here rather than
left for a reader to discover in a diff.

But an alias whose target was collected in this same read, and whose target's own declared value
is a color, is reported as a **color**. That is a lookup among what is already in hand, not a
resolution: the reported `value` stays `var(--other)` and `aliasOf` stays set.

Without that rule the classifier inverts on exactly the projects that theme well. A two-tier
system — a fixed palette of literals, plus role tokens that alias into it and are what a theme
re-points — would classify every fixed entry and drop every role token into `unclassified`,
because a role token's declared value is a `var()`. On a measured project that is 99 fixed
entries reported and 33 re-pointable ones buried, and the buried set is the one a styleguide
most needs to show, because it is the one that changes.

**One hop, not transitivity.** A three-tier chain — role aliases role aliases literal — leaves
its outermost token `unclassified`, with the `var()` visible for a person to follow. That is the
deliberate limit: the rule answers "what kind of thing is this", and each additional hop it
walked would be one step closer to answering "what color is this", which is the browser's
question and not this script's.

## Usage

    styleguide.py tokens [--project-root DIR]

`tokens` prints one JSON document on stdout and nothing else. `--project-root` defaults to the
current directory. No path, host, or version is hardcoded; the spell reads the project's slots
and passes what it finds.

The document is two-space-indented JSON with **one line per row** in each of its tables —
`layers`, `byFile`, `declarations` — because each of those is a table: a row per line keeps a
token's name, value, group, and origin legible together, and a diff of two reports points at the
token that changed rather than at a field three tokens away.

Exit: 0 on a completed read — including a read that found nothing, which is the common starting
state and not an error — 1 when the read could not be completed, 2 on a usage error, and 3 when
the read completed and the answer is negative: the project holds token layers and none of them
can be read at render time. The document is printed in every one of those cases except the usage
error, so a caller stopping on 3 has the refusal and its remedy in hand.

**3 is unconditional here**, unlike `guide.py`'s, which is gated behind `--strict`. The asymmetry
is deliberate: an audit's findings are a backlog someone works through, and failing a build on
one would fail it in exactly the projects that wired the audit in early. This is a stop. A caller
that ignored it would build a styleguide out of values it invented or baked.
"""

import argparse
import json
import os
import re
import sys

# An installed skill directory is not a place to leave build output. A run reads a few files
# and exits, so a bytecode cache saves nothing measurable and would appear as untracked clutter
# inside a consuming project's skills.
sys.dont_write_bytecode = True

PROG = "styleguide.py"

# Bumped when the document's shape changes in a way a consumer has to notice. A consumer reads
# it rather than sniffing for keys, the same way a dossier carries `dossierVersion`.
#
# 2 replaced the singular `layer` key with `declarationsFrom`, `authoritativeLayer` and the
# `layers` table. A consumer of version 1 read one layer name and could not have known there was
# anything else to ask about, which is precisely the notice this number exists to give.
#
# 3 added `refusal`, and with it an exit code a project can now receive where it previously got
# 0. A consumer of version 2 reading a build-time-only project was told a completed read with an
# empty `declarations` table, which is indistinguishable from a project that simply declares
# nothing — the two are now different answers, and the notice is what says so.
TOKENS_VERSION = 3

# The layer the `declarations` table is read from — the only layer this script parses values out
# of. Named in the document rather than left implicit: a consumer holding a two-row `layers`
# table and a `declarations` table has no other way to tell a report that kept the layers apart
# from one that merged them.
LAYER_CUSTOM_PROPERTIES = "custom-properties"
LAYER_PREPROCESSOR = "preprocessor-variables"

# Fidelity order, and the whole of the authoritative-layer rule: the first of these a project
# holds is the authoritative one. Custom properties come first because they are the only layer
# whose values survive to the browser, which is this script's definition of a design token.
#
# Written as a lookup over the layers found rather than as "the first row of the table", so the
# rule survives someone reordering the report for readability.
LAYERS_BY_FIDELITY = (LAYER_CUSTOM_PROPERTIES, LAYER_PREPROCESSOR)

GROUP_COLOR = "color"
GROUP_UNCLASSIFIED = "unclassified"

# The exit code for a read that completed and whose answer is negative. Its own code rather than
# 1, for the reason guide.py gives about its own 3: 1 means the read could not be completed, and
# a caller that cannot tell "this project's palette is unreadable" from "this script broke" will
# treat the second as the first and go looking for a stylesheet to fix.
#
# **Unconditional, and deliberately not behind a flag.** guide.py gates its 3 behind `--strict`
# because an audit's findings are a backlog someone works through; this one is a stop. A caller
# that carried on would produce a page of values it invented or baked, which is the whole failure
# this script exists to refuse.
EXIT_REFUSED = 3

REFUSAL_NO_RUNTIME_LAYER = "no-runtime-resolvable-layer"

# The refusal's two halves, held as constants so the text has one home and the code below reads
# as the rule rather than as the wording.
#
# `%s` is the layers found, phrased in `layers_found_phrase`. The message names them even though
# the `layers` table states them again: a refusal gets relayed as a line on its own, and one that
# says a palette is unreadable without saying what it found instead is a line nobody can act on.
# That is a formatting of a fact held once, not a second entry of it.
REFUSAL_MESSAGE = (
    "The palette cannot be read at render time. %s, whose values the build resolves and "
    "discards, so nothing in the rendered page can read them. A page built from this layer "
    "shows the palette as it stood at the last build, and does not follow a re-theme."
)

# Concrete on purpose, and specific to nothing. It names a CSS language feature and a shape of
# edit, so a project can act on it without this pack knowing a single thing about that project —
# no CMS, no framework, no build tool, no path. The remedy is an afternoon of front-end work,
# after which this command's answer flips and every value reported is one a page can follow.
REFUSAL_REMEDY = (
    "Add a custom-property layer that the existing variables feed: one :root block declaring a "
    "custom property for each palette entry, with that entry's existing variable as its value. "
    "The palette stays defined where it is defined today; the block only makes those values "
    "readable at render time. Re-run afterwards: the custom-property layer becomes "
    "authoritative, and every token reported is one a page can follow through a re-theme."
)

# Document keys whose value is a list of uniform rows, rendered one row per line. See `render`
# for why; the set exists so a second table does not get a second copy of that branch.
TABLE_KEYS = frozenset(("layers", "byFile", "byPreprocessorFile", "declarations"))

# `.css` and nothing else is read for VALUES — see the module docstring on why a preprocessor
# source is a different layer rather than a wider glob.
STYLESHEET_SUFFIXES = (".css",)

# The preprocessor syntaxes, and the sigil a variable declaration carries in each. `.scss` and
# `.sass` are one language in two syntaxes and share `$`; Less uses `@`, which is also its
# at-rule sigil — hence the colon the pattern below insists on, since `@media (min-width: 40em)`
# has no colon where a declaration would put one.
PREPROCESSOR_SIGILS = {
    ".scss": "$",
    ".sass": "$",
    ".less": "@",
}

# Anchored to the start of a line, which is where a variable declaration sits in every one of
# these syntaxes and is also what excludes the two shapes that would otherwise be miscounted: a
# `//` line comment (the `//` is not leading whitespace, so the pattern never reaches the sigil)
# and a USE of a variable inside a value, which always has a property name in front of it.
#
# Deliberately not a parser. It counts declarations; it does not read their values, and nothing
# downstream may treat what it finds as a token.
_PREPROCESSOR_DECLARATION = {
    "$": re.compile(r"^[ \t]*\$([A-Za-z_-][\w-]*)[ \t]*:", re.MULTILINE),
    "@": re.compile(r"^[ \t]*@([A-Za-z_-][\w-]*)[ \t]*:", re.MULTILINE),
}

# Every suffix the walk collects, in one tuple so the tree is walked once. `.scss` does not end
# with `.css`, so bucketing by suffix needs no ordering care.
SOURCE_SUFFIXES = STYLESHEET_SUFFIXES + tuple(sorted(PREPROCESSOR_SIGILS))

# Directory names that hold build output, dependency trees, or version-control internals. A
# vendor token under node_modules is not this project's palette and there may be thousands of
# them; `bin` and `obj` hold copies of files already read from their source.
#
# Names, never paths: a path would be a project fact, and this pack holds none. Hidden
# directories are skipped as a class for the same reason — they are tool state by convention,
# and naming each tool would be a list that goes stale.
SKIP_DIRS = frozenset((
    ".git", ".svn", ".hg",
    "node_modules",
    "bin", "obj",
    "__pycache__",
))


def note_unreadable(rel, exc):
    """One file this script could not open, named on stderr and otherwise skipped.

    One file should never cost a project its whole report, and a silent skip would make a
    permissions problem look like a project with fewer tokens than it has.
    """
    print("%s: note: could not read %s: %s" % (PROG, rel, exc), file=sys.stderr)


class StyleguideError(Exception):
    """A read that could not be completed, with a message for the operator.

    Raised rather than returned so no caller can mistake a failed read for a project with no
    tokens — the two are the same empty document otherwise, and only one of them is fine.
    """


# ---------------------------------------------------------------------------
# Finding the stylesheets
# ---------------------------------------------------------------------------

def find_sources(root):
    """Every file under `root` this script may open, bucketed by suffix.

    One walk for every suffix rather than one per layer: a project's tree is walked once and
    the buckets decide what each file is for. A `.scss` in the preprocessor bucket is counted,
    never parsed — the buckets are what keeps that distinction structural instead of a rule
    somebody has to remember.

    Each bucket is sorted, with `/` as the separator whatever the platform uses, because the
    report is compared byte for byte by its tests and read side by side across machines by
    people. Walk order is neither stable nor meaningful.
    """
    found = dict((suffix, []) for suffix in SOURCE_SUFFIXES)
    for dirpath, dirnames, filenames in os.walk(root):
        # In place, which is what prunes the walk rather than merely filtering the listing.
        dirnames[:] = [d for d in dirnames
                       if d not in SKIP_DIRS and not d.startswith(".")]
        for name in filenames:
            lowered = name.lower()
            # One C-level check against the whole tuple before the per-suffix loop, which then
            # only runs for a file that is going to land in some bucket.
            if not lowered.endswith(SOURCE_SUFFIXES):
                continue
            for suffix in SOURCE_SUFFIXES:
                if lowered.endswith(suffix):
                    rel = os.path.relpath(os.path.join(dirpath, name), root)
                    found[suffix].append(rel.replace(os.sep, "/"))
                    break
    return dict((suffix, sorted(paths)) for suffix, paths in found.items())


def read_text(path):
    """A stylesheet's text, with undecodable bytes replaced rather than fatal.

    A stylesheet is not always UTF-8 — a legacy sheet may be latin-1, and a byte this script
    cannot decode sits in a comment or a content string far more often than in a property name.
    Refusing the whole file would drop every token in it over one character.
    """
    with open(path, "r", encoding="utf-8", errors="replace") as handle:
        return handle.read()


# ---------------------------------------------------------------------------
# Reading the declarations
# ---------------------------------------------------------------------------
#
# A declaration is not a name. `--brand-ink` appears once as a declaration and twice as a
# `var()` use in a stylesheet of fifteen lines, and a reader that matches the name anywhere
# reports one token three times. So the scanner tracks *position*: a custom property name is
# only a declaration when it sits where a declaration can start — at the top of a file or just
# after `{`, `}`, or `;` — and is followed by a colon. A name inside a value is consumed with
# the value it sits in and never looked at again.

_COMMENT = re.compile(r"/\*.*?\*/", re.DOTALL)

# Deliberately narrow. A custom property name may contain almost anything CSS can escape, but
# a name holding whitespace, a colon, a brace, a paren, or a quote is not a name this scanner
# can tell from the syntax around it — and every one of those characters is a terminator it
# relies on.
_NAME = re.compile(r"--[^\s:;{}()\"'\\]+")

# A function call at the very start of a value. Whether it is also the WHOLE value is decided by
# finding its closing paren, which a regex cannot do.
_FUNCTION_HEAD = re.compile(r"([A-Za-z][A-Za-z0-9-]*)\(")

# The first custom property named inside a `var()`.
_VAR_TARGET = re.compile(r"\s*(--[^\s,)]+)")


def strip_comments(text):
    """Comments blanked out, with every newline and every offset preserved.

    Blanked rather than removed so the line number of everything after a comment stays true,
    and so a commented-out declaration cannot be read as a live one. A stylesheet's palette is
    exactly the kind of block that gets commented out during a re-theme.
    """
    return _COMMENT.sub(lambda m: re.sub(r"[^\n]", " ", m.group(0)), text)


def read_value(text, start):
    """One declaration's value, and the offset of the terminator that ended it.

    Strings and nested parens are tracked, because a `;` inside `content: "a;b"` or inside
    `url(data:…;base64,…)` does not end a declaration. The terminator itself is not consumed —
    the caller's loop sees it and knows a new declaration may begin.
    """
    i, n = start, len(text)
    depth = 0
    quote = None
    while i < n:
        ch = text[i]
        if quote is not None:
            if ch == "\\":
                i += 2
                continue
            if ch == quote:
                quote = None
            i += 1
            continue
        if ch == "\\":
            # Escaped outside a string too: `\;` is a literal semicolon and does not end the
            # declaration, the same rule the outer scan follows.
            i += 2
            continue
        if ch in "\"'":
            quote = ch
        elif ch == "(":
            depth += 1
        elif ch == ")":
            depth = max(0, depth - 1)
        elif depth == 0 and ch in ";}":
            break
        i += 1
    return text[start:i].strip(), i


def declarations_in(text):
    """Yield `(name, value, line)` for every custom-property declaration in one stylesheet.

    The scan tracks quotes and paren depth, and that is not symmetry with `read_value` for its
    own sake — it is the difference between a correct report and a silently corrupt one.

    A `;`, `{` or `}` only opens a declaration position at **top level**: outside every string
    and every paren. Without that, `content: "Note; --brand-fake: #FF00FF"` re-opened the
    position at the semicolon *inside the string*, read `--brand-fake:` as a real declaration,
    and then handed `read_value` a starting point mid-string — where the string's own closing
    quote reads as an opening one, so the value ran on and swallowed every genuine declaration
    after it. The run exited 0 with well-formed JSON naming a token nobody wrote and omitting
    the ones they did.

    That is the one wrong answer this script must never give, so the guard lives here rather
    than in a caller: a value reader cannot recover a position that was already wrong.
    """
    text = strip_comments(text)
    i, n = 0, len(text)
    line = 1
    # The top of a file is a place a declaration can start, which matters for a fragment
    # included into a rule rather than holding its own.
    at_start = True
    depth = 0
    quote = None
    while i < n:
        ch = text[i]

        # Inside a string nothing is syntax: not a terminator, not a property name.
        if quote is not None:
            if ch == "\\":
                # An escape can span a newline, and the line count has to survive it.
                line += text.count("\n", i, min(i + 2, n))
                i += 2
                continue
            if ch == quote:
                quote = None
            elif ch == "\n":
                line += 1
            i += 1
            continue

        # A backslash escapes the next character ANYWHERE in CSS, not only inside a string.
        # Tailwind-style class names carry escaped parens by the hundred —
        # `.scrollbar-thumb-\(--t-a-700\)` — and counting those as groups leaves the depth
        # wrong for the rest of the file, so the `{` that follows never reads as top level and
        # every declaration in that rule is skipped. Measured on one real bundle: 80 real
        # declarations silently dropped, which is the same class of wrong answer as reporting
        # one that was never written.
        if ch == "\\":
            line += text.count("\n", i, min(i + 2, n))
            i += 2
            continue
        if ch == "\n":
            line += 1
            i += 1
            continue
        if ch in " \t\r\f":
            # Whitespace neither opens nor closes a declaration position.
            i += 1
            continue
        if ch in "\"'":
            quote = ch
            at_start = False
            i += 1
            continue
        if ch == "(":
            depth += 1
            at_start = False
            i += 1
            continue
        if ch == ")":
            # Clamped, because a stray `)` is a malformed sheet and not a reason to read the
            # rest of the file as though it were nested one level deeper forever.
            depth = max(0, depth - 1)
            at_start = False
            i += 1
            continue
        if depth == 0 and ch in "{};":
            at_start = True
            i += 1
            continue
        if depth == 0 and at_start and text.startswith("--", i):
            match = _NAME.match(text, i)
            if match:
                after = match.end()
                while after < n and text[after] in " \t\r\n\f":
                    after += 1
                if after < n and text[after] == ":":
                    value, end = read_value(text, after + 1)
                    yield match.group(0), value, line
                    line += text.count("\n", i, end)
                    i = end
                    continue
        at_start = False
        i += 1


# ---------------------------------------------------------------------------
# Classifying by the value's shape
# ---------------------------------------------------------------------------

# `#rgb`, `#rgba`, `#rrggbb`, `#rrggbbaa`. Anchored at both ends: a hex somewhere inside a
# longer value is part of that value, not the value.
_HEX = re.compile(r"#(?:[0-9a-fA-F]{3,4}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})\Z")

# A function whose result is a color and nothing else, so a sole call to one IS a color.
#
# The first six are the set the plan enumerated. The rest are the same rule rather than an
# extension of it — every one of them is a CSS color function, and leaving them out would file
# `lab(52% 40 59)` under `unclassified` while filing `hsl(210 90% 52%)` under colors, which
# reads as a bug in the tool rather than as a deliberate line.
COLOR_FUNCTIONS = frozenset((
    "rgb", "rgba", "hsl", "hsla", "oklch", "oklab",
    "hwb", "lab", "lch", "color", "color-mix",
))

# The CSS Color Module Level 4 named colors, plus the two keywords that name a color without
# naming a hue. `transparent` and `currentcolor` are colors: a swatch for either is odd, but
# filing them under `unclassified` would tell a person to go and group a value that is already
# grouped.
NAMED_COLORS = frozenset((
    "aliceblue", "antiquewhite", "aqua", "aquamarine", "azure", "beige", "bisque", "black",
    "blanchedalmond", "blue", "blueviolet", "brown", "burlywood", "cadetblue", "chartreuse",
    "chocolate", "coral", "cornflowerblue", "cornsilk", "crimson", "cyan", "darkblue",
    "darkcyan", "darkgoldenrod", "darkgray", "darkgreen", "darkgrey", "darkkhaki",
    "darkmagenta", "darkolivegreen", "darkorange", "darkorchid", "darkred", "darksalmon",
    "darkseagreen", "darkslateblue", "darkslategray", "darkslategrey", "darkturquoise",
    "darkviolet", "deeppink", "deepskyblue", "dimgray", "dimgrey", "dodgerblue", "firebrick",
    "floralwhite", "forestgreen", "fuchsia", "gainsboro", "ghostwhite", "gold", "goldenrod",
    "gray", "green", "greenyellow", "grey", "honeydew", "hotpink", "indianred", "indigo",
    "ivory", "khaki", "lavender", "lavenderblush", "lawngreen", "lemonchiffon", "lightblue",
    "lightcoral", "lightcyan", "lightgoldenrodyellow", "lightgray", "lightgreen", "lightgrey",
    "lightpink", "lightsalmon", "lightseagreen", "lightskyblue", "lightslategray",
    "lightslategrey", "lightsteelblue", "lightyellow", "lime", "limegreen", "linen", "magenta",
    "maroon", "mediumaquamarine", "mediumblue", "mediumorchid", "mediumpurple",
    "mediumseagreen", "mediumslateblue", "mediumspringgreen", "mediumturquoise",
    "mediumvioletred", "midnightblue", "mintcream", "mistyrose", "moccasin", "navajowhite",
    "navy", "oldlace", "olive", "olivedrab", "orange", "orangered", "orchid", "palegoldenrod",
    "palegreen", "paleturquoise", "palevioletred", "papayawhip", "peachpuff", "peru", "pink",
    "plum", "powderblue", "purple", "rebeccapurple", "red", "rosybrown", "royalblue",
    "saddlebrown", "salmon", "sandybrown", "seagreen", "seashell", "sienna", "silver",
    "skyblue", "slateblue", "slategray", "slategrey", "snow", "springgreen", "steelblue",
    "tan", "teal", "thistle", "tomato", "turquoise", "violet", "wheat", "white", "whitesmoke",
    "yellow", "yellowgreen",
    "transparent", "currentcolor",
))


def sole_function(value):
    """`(name, inner)` when the whole value is one function call, `(None, None)` otherwise.

    "The whole value" is the entire claim. `0 1px 2px rgba(16,24,40,.08)` contains a color
    function and is a shadow, and a classifier that matched the call anywhere would report it
    as a color — so the closing paren has to be the value's last character.
    """
    head = _FUNCTION_HEAD.match(value)
    if not head:
        return None, None
    i = head.end() - 1          # the opening paren itself
    depth = 0
    quote = None
    n = len(value)
    while i < n:
        ch = value[i]
        if quote is not None:
            if ch == "\\":
                i += 2
                continue
            if ch == quote:
                quote = None
            i += 1
            continue
        if ch in "\"'":
            quote = ch
        elif ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0:
                if i == n - 1:
                    return head.group(1).lower(), value[head.end():i]
                return None, None
        i += 1
    return None, None


def classify_literal(value):
    """The group a value's own shape puts it in, knowing nothing about any other token."""
    text = value.strip()
    if not text:
        return GROUP_UNCLASSIFIED
    if _HEX.match(text):
        return GROUP_COLOR
    if text.lower() in NAMED_COLORS:
        return GROUP_COLOR
    name, _ = sole_function(text)
    if name in COLOR_FUNCTIONS:
        return GROUP_COLOR
    return GROUP_UNCLASSIFIED


def alias_target(value):
    """The custom property this value aliases, or None when it is not a sole `var()`.

    A sole `var()`, for the same reason a color must be a sole call: `1px solid var(--line)` is
    a border shorthand that happens to read a token, not an alias of one.
    """
    name, inner = sole_function(value.strip())
    if name != "var":
        return None
    target = _VAR_TARGET.match(inner or "")
    return target.group(1) if target else None


# ---------------------------------------------------------------------------
# Layer discovery
# ---------------------------------------------------------------------------

def declarations_at_top_level(text, pattern):
    """Variable names declared at paren depth zero, with comments removed first.

    Two shapes this excludes, and the second is why the line anchor alone was not enough:

        // $muted: #ccc                  a line comment — the anchor already rejects it
        /* $muted: #ccc; */              a block comment — `strip_comments` blanks it
        @include button-variant(
          $background: $primary,         a named ARGUMENT at a call site, alone on its line
        );                               and therefore anchored exactly like a declaration

    A caller passing a value is not a place a palette is defined. Counting those reports a
    palette larger than the one a person can edit, and on a file holding only such a call it
    reports a build-time layer that is not there at all — which would send Step 4's refusal to a
    project whose real answer is "no token layer", a different problem with a different remedy.

    **Depth resets at every statement boundary**, and that is correctness before it is caution: a
    paren group cannot span a `;`, `{` or `}` in any of these syntaxes, so a call's parens have
    closed by the time its statement ends. It also bounds the damage from a paren this line-level
    count cannot see — one inside a string, or inside a `//` comment — to the statement it sits
    in, rather than pegging the depth and silently dropping every declaration in the rest of the
    file. That failure mode has already been paid for once in this script's CSS scanner.
    """
    names = []
    depth = 0
    for line in strip_comments(text).splitlines():
        if depth == 0:
            match = pattern.match(line)
            if match:
                names.append(match.group(1))
        depth = max(0, depth + line.count("(") - line.count(")"))
        if line.rstrip().endswith((";", "{", "}")):
            depth = 0
    return names


def count_preprocessor_variables(root, sources):
    """`(rows, declarations, names)` for the preprocessor layer — counted, never parsed.

    `rows` carries one entry per file that declared something, in the shape `byFile` uses for
    stylesheets. That provenance is not decoration: a vendored `.scss` bundle sitting beside a
    project's own palette inflates this layer exactly the way a vendored icon font inflated the
    custom-property one, and a consumer handed a total with no files behind it cannot tell the
    two apart. The paths cost nothing extra — they are already in hand here.

    A file contributes only if it declares at least one variable, so a `.scss` that holds no
    `$` and merely emits a `:root` block is not a preprocessor layer. That file is the bridge
    between the two layers, and counting it as a layer of its own would report a build-time
    palette in a project that has already lifted its palette out of one.

    Names are kept sigil-and-all. A project mixing syntaxes is unusual, but `$brand` in a
    `.scss` and `@brand` in a `.less` are two declarations in two languages, and folding them
    into one name would undercount the layer for the sake of a collision nobody meant.
    """
    rows = []
    declarations = 0
    names = set()
    for suffix in sorted(PREPROCESSOR_SIGILS):
        sigil = PREPROCESSOR_SIGILS[suffix]
        pattern = _PREPROCESSOR_DECLARATION[sigil]
        for rel in sources.get(suffix, ()):
            try:
                text = read_text(os.path.join(root, rel))
            except OSError as exc:
                note_unreadable(rel, exc)
                continue
            found = declarations_at_top_level(text, pattern)
            if not found:
                continue
            here = set(sigil + name for name in found)
            rows.append({
                "file": rel,
                "declarations": len(found),
                "names": len(here),
            })
            declarations += len(found)
            names.update(here)
    rows.sort(key=lambda row: row["file"])
    return rows, declarations, names


def layer_row(name, runtime_resolvable, files, declarations, names):
    """One row of the `layers` table.

    Uniform across layers on purpose. The row says how much of a layer there is and whether its
    values reach the browser, and it says nothing about what is in it — the counts are what
    decides whether a palette can be read at render time, and only the authoritative layer's
    contents are reported anywhere in this document.
    """
    return {
        "layer": name,
        "runtimeResolvable": runtime_resolvable,
        "files": files,
        "declarations": declarations,
        "names": names,
    }


def authoritative_layer(layers):
    """The name of the authoritative layer among those found, or None when none were.

    A lookup over `LAYERS_BY_FIDELITY` rather than `layers[0]`, so the rule is stated where it
    can be read and does not quietly depend on the order the table happens to be built in.
    """
    found = set(row["layer"] for row in layers)
    for name in LAYERS_BY_FIDELITY:
        if name in found:
            return name
    return None


def layers_found_phrase(layers):
    """The layers found, as the subject of a sentence.

    Written from the layer names the report already carries rather than from a table of prose,
    so a layer added later needs no wording of its own.

    **The plural branch is unreachable today, and is written anyway.** Only a refusal calls this,
    a refusal needs every layer found to be build-time, and `custom-properties` — the only other
    layer recognized — is runtime-resolvable by definition. So one layer is the only count that
    can arrive here while two layers exist. A third build-time layer would reach it, and the
    alternative to writing it now is a function that emits a broken sentence on the day that
    happens; the branch costs a line and the failure would cost a report nobody trusts.
    """
    names = [row["layer"] for row in layers]
    if len(names) == 1:
        return "The only token layer this project holds is %s" % names[0]
    return ("The token layers this project holds are %s and %s"
            % (", ".join(names[:-1]), names[-1]))


def refusal(layers):
    """The refusal for a project holding layers of which none is runtime-resolvable, or None.

    **The gate is "layers exist and none of them is readable at render time."** Both halves are
    load bearing, and the second is not the same test as "a build-time layer is present":

    - **No layers at all is not a refusal.** A project that writes every color where it is used
      holds no palette yet. That is the common starting state and the most useful project to
      talk to, so it gets a completed read reporting nothing — refusing it would turn "you have
      not started" into "you did something wrong".
    - **A build-time layer beside a runtime one is not a refusal either.** The commonest good
      shape is a preprocessor palette that emits a `:root` block, and the presence of the
      build-time layer says nothing bad about it. What matters is only whether *something* here
      survives to the browser.

    And the refusal carries **no token value**, which is why it is built from the layer names and
    the counts rather than from anything read out of a file. A baked value presented beside a
    live-reading promise is the silent staleness this whole capability refuses: it would fail the
    headline claim while looking exactly like it passed. So the answer to a project whose palette
    cannot be read at render time is the remedy, and never a snapshot.
    """
    if not layers:
        return None
    if any(row["runtimeResolvable"] for row in layers):
        return None
    return {
        "reason": REFUSAL_NO_RUNTIME_LAYER,
        "message": REFUSAL_MESSAGE % layers_found_phrase(layers),
        "remedy": REFUSAL_REMEDY,
    }


# ---------------------------------------------------------------------------
# The document
# ---------------------------------------------------------------------------

def read_tokens(root):
    """Every custom-property declaration under `root`, classified, as a report document."""
    sources = find_sources(root)
    stylesheets = sources[".css"]

    scanned = []
    rows = []
    for rel in stylesheets:
        try:
            text = read_text(os.path.join(root, rel))
        except OSError as exc:
            # Excluded from `stylesheetsRead` too, so the document never claims a file it
            # could not open.
            note_unreadable(rel, exc)
            continue
        scanned.append(rel)
        for name, value, line in declarations_in(text):
            rows.append({"name": name, "value": value, "line": line, "file": rel})

    # Pass one: what each name's own value shape says. Keyed by name across every file, because
    # the one-hop lookup asks about a token, and a token is a name — the stylesheet it was
    # declared in is not part of the question.
    #
    # A name declared more than once counts as a color if ANY of its declarations is one. Which
    # declaration the browser actually applies is a cascade question, and answering it would be
    # a resolution — the same thing the var() rule refuses. So the report classifies the name
    # generously and reports every declaration, leaving the cascade to the browser.
    #
    # Classified once per row and carried, not recomputed. The two passes ask different
    # questions of the same answer, and on a real project the second call was 22 thousand
    # repetitions of work already done.
    for row in rows:
        row["literalGroup"] = classify_literal(row["value"])
        row["aliasTarget"] = alias_target(row["value"])

    literal_group = {}
    for row in rows:
        group = row["literalGroup"]
        if group == GROUP_COLOR or row["name"] not in literal_group:
            literal_group[row["name"]] = group

    # Pass two: the alias marking, and the one hop.
    declarations = []
    for row in rows:
        group = row["literalGroup"]
        target = row["aliasTarget"]
        if group == GROUP_UNCLASSIFIED and target is not None:
            if literal_group.get(target) == GROUP_COLOR:
                group = GROUP_COLOR
        declarations.append({
            "name": row["name"],
            # Verbatim, with the single documented exception of comment-blanking inside a
            # value. An alias reports `var(--other)` and not what `--other` holds.
            "value": row["value"],
            "group": group,
            "aliasOf": target,
            "file": row["file"],
            "line": row["line"],
        })

    # Where the volume came from, one entry per file that declared something.
    #
    # Measured on a real project: 22,247 declarations across 318 names, of which 20,414 came
    # from one vendored icon-font directory and 19,982 were a single re-declared name. The
    # project's own tokens were the remaining 1,833. Every one of those rows is a real
    # declaration that really resolves at render time, so none of them is wrong to report — but
    # a consumer handed the flat list cannot see that 92% of it is one dependency, and a person
    # reading it cannot find their palette.
    #
    # So the provenance is summarized rather than filtered. Filtering would need to know which
    # directory is a dependency, which is a project fact this pack must not hold; counting needs
    # no such knowledge, and `declarations` beside `names` is what makes a generated file
    # obvious — three names over nineteen thousand declarations is not a palette.
    #
    # Files that declared nothing are omitted; `stylesheetsRead` already names every file read,
    # so listing the silent ones here would pad the summary with the rows carrying no signal.
    by_file = []
    for rel in scanned:
        rows_here = [d for d in declarations if d["file"] == rel]
        if rows_here:
            by_file.append({
                "file": rel,
                "declarations": len(rows_here),
                "names": len(set(d["name"] for d in rows_here)),
            })

    # The layers the project holds, in fidelity order, one row each — and only for layers that
    # actually hold something. An empty `layers` is a project with no token layer at all, which
    # is a different answer from a project whose only layer cannot be read at render time, and
    # the two must not collapse into one.
    #
    # The custom-property row is counted from what was already read: `files` is the number of
    # files that declared something, matching what the preprocessor row counts, so the two rows
    # mean the same thing by the same name.
    distinct_names = set(d["name"] for d in declarations)

    layers = []
    if declarations:
        layers.append(layer_row(
            LAYER_CUSTOM_PROPERTIES, True,
            files=len(by_file),
            declarations=len(declarations),
            names=len(distinct_names),
        ))
    by_preprocessor_file, pre_declarations, pre_names = count_preprocessor_variables(root, sources)
    if pre_declarations:
        layers.append(layer_row(
            LAYER_PREPROCESSOR, False,
            files=len(by_preprocessor_file),
            declarations=pre_declarations,
            names=len(pre_names),
        ))

    return {
        "tokensVersion": TOKENS_VERSION,
        # Null when nothing was parsed for values. The constant would otherwise sit beside an
        # `authoritativeLayer` naming a different layer and an empty `declarations` table, which
        # reads as a claim about a read that did not happen — and a schema fact a consumer
        # cannot see the reasoning for is indistinguishable from a per-run answer.
        "declarationsFrom": LAYER_CUSTOM_PROPERTIES if declarations else None,
        "authoritativeLayer": authoritative_layer(layers),
        # The verdict on the three keys above, placed above every table so nobody reads a count
        # before finding out the read was refused. Null on a completed positive read — a key a
        # consumer reads rather than a shape it has to sniff for, the same choice
        # `declarationsFrom` and `authoritativeLayer` already make.
        "refusal": refusal(layers),
        "layers": layers,
        "stylesheetsRead": scanned,
        "counts": {
            # Declarations and names are both reported because they answer different
            # questions: 40 declarations over 30 names means ten are re-declared, which is a
            # theme or a media query and is worth seeing before anyone builds a swatch grid.
            "declarations": len(declarations),
            "names": len(distinct_names),
            GROUP_COLOR: sum(1 for d in declarations if d["group"] == GROUP_COLOR),
            GROUP_UNCLASSIFIED: sum(1 for d in declarations
                                    if d["group"] == GROUP_UNCLASSIFIED),
            "aliases": sum(1 for d in declarations if d["aliasOf"] is not None),
        },
        "byFile": by_file,
        "byPreprocessorFile": by_preprocessor_file,
        "declarations": declarations,
    }


def render(doc):
    """The document as JSON, with one line per row in each of its tables.

    Valid JSON either way — this is a formatting choice, not a format. A token list is a table,
    and a row per line is what lets a reader, a grep, and a diff each address one token: a
    golden-file mismatch points at the token that changed instead of at a field three tokens
    away, and a substring assertion can bind a name to its value and its group in one line.
    """
    parts = []
    for key, value in doc.items():
        if key in TABLE_KEYS:
            if not value:
                parts.append('  %s: []' % json.dumps(key))
                continue
            rows = ",\n".join("    " + json.dumps(row, separators=(", ", ": "))
                              for row in value)
            parts.append('  %s: [\n%s\n  ]' % (json.dumps(key), rows))
            continue
        # Nested containers come back from json.dumps at column 0, so every line after the
        # first is re-indented to sit inside this document rather than beside it.
        blob = json.dumps(value, indent=2).replace("\n", "\n  ")
        parts.append("  %s: %s" % (json.dumps(key), blob))
    return "{\n" + ",\n".join(parts) + "\n}"


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def cmd_tokens(args):
    doc = read_tokens(args.project_root)
    print(render(doc))
    # After the document, never instead of it, for the reason guide.py gives about its own
    # non-zero exit: the refusal a caller stops on is the one whose remedy someone has to read,
    # and a script that swallowed the report to signal through a status code would leave them
    # with a number and nothing to act on.
    if doc["refusal"] is not None:
        return EXIT_REFUSED
    return 0


def build_parser():
    parser = argparse.ArgumentParser(
        prog=PROG,
        description="Read a project's design tokens and report on them, "
                    "without writing anything.")
    subparsers = parser.add_subparsers(dest="command")

    tokens_cmd = subparsers.add_parser(
        "tokens",
        help="report the token layers the project holds, which one is authoritative, and every "
             "CSS custom property it declares with its group")
    tokens_cmd.set_defaults(handler=cmd_tokens)

    for sub in (tokens_cmd,):
        sub.add_argument(
            "--project-root", default=".", metavar="DIR",
            help="the project to read (default: the current directory)")
    return parser


def main(argv):
    parser = build_parser()
    args = parser.parse_args(argv)
    if not getattr(args, "handler", None):
        parser.print_help(sys.stderr)
        return 2
    # Checked here rather than inside the walk: os.walk on a missing directory yields nothing
    # at all, so a mistyped root would otherwise print a perfectly well-formed report saying
    # the project has no tokens. That is the one wrong answer this script must never give.
    root = getattr(args, "project_root", None)
    if root is not None and not os.path.isdir(root):
        print("%s: error: no such directory: %s" % (PROG, root), file=sys.stderr)
        return 1
    try:
        return args.handler(args)
    except StyleguideError as exc:
        print("%s: error: %s" % (PROG, exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
