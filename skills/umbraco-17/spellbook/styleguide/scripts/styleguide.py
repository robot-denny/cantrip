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

So in practice: **CSS custom properties**. Everything else is a different layer, and reporting
which layers a project holds, and which of them is authoritative, is a separate question this
script does not yet answer.

## What it reads, and what it does not

`.css` files only, walked from `--project-root`, skipping build output and dependency trees
(`SKIP_DIRS`). Two consequences worth stating plainly rather than discovering:

- **A `.scss` or `.less` source is not read**, even though a custom property declared in one
  survives compilation perfectly well. Those files are the preprocessor layer, and which layer
  a project's tokens actually live in is a question with its own answer — a project whose
  `.scss` holds `$brand-primary` has a build-time-only palette that no markup can read at
  render time, and telling it apart from one whose `.scss` merely *emits* custom properties is
  layer discovery, not scanning. Reading both here would collapse the two into one number.
  Scanning one syntax also keeps the parser to one syntax: `//` line comments are not CSS, and
  a scanner that stripped them would have to tell a comment from the `//` in a `url(https://…)`.

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

The document is two-space-indented JSON with **one line per declaration**, because a token list
is a table: a row per line keeps a token's name, value, group, and origin legible together, and
a diff of two reports points at the token that changed rather than at a field three tokens away.

Exit: 0 on a completed read — including a read that found nothing, which is the common starting
state and not an error — 1 when the read could not be completed, and 2 on a usage error.
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
TOKENS_VERSION = 1

# The layer this subcommand reads. Named in the document rather than left implicit, because it
# is one layer of several a project may hold and a report that did not say which layer it read
# would be indistinguishable from one claiming to have read them all.
LAYER = "custom-properties"

GROUP_COLOR = "color"
GROUP_UNCLASSIFIED = "unclassified"

# Document keys whose value is a list of uniform rows, rendered one row per line. See `render`
# for why; the set exists so a second table does not get a second copy of that branch.
TABLE_KEYS = frozenset(("byFile", "declarations"))

# `.css` and nothing else — see the module docstring on why a preprocessor source is a
# different question rather than a wider glob.
STYLESHEET_SUFFIXES = (".css",)

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


class StyleguideError(Exception):
    """A read that could not be completed, with a message for the operator.

    Raised rather than returned so no caller can mistake a failed read for a project with no
    tokens — the two are the same empty document otherwise, and only one of them is fine.
    """


# ---------------------------------------------------------------------------
# Finding the stylesheets
# ---------------------------------------------------------------------------

def find_stylesheets(root):
    """Every stylesheet under `root`, as paths relative to it, in sorted order.

    Sorted, and with `/` as the separator whatever the platform uses, because the report is
    compared byte for byte by its tests and read side by side across machines by people. Walk
    order is neither stable nor meaningful.
    """
    found = []
    for dirpath, dirnames, filenames in os.walk(root):
        # In place, which is what prunes the walk rather than merely filtering the listing.
        dirnames[:] = [d for d in dirnames
                       if d not in SKIP_DIRS and not d.startswith(".")]
        for name in filenames:
            if name.lower().endswith(STYLESHEET_SUFFIXES):
                rel = os.path.relpath(os.path.join(dirpath, name), root)
                found.append(rel.replace(os.sep, "/"))
    return sorted(found)


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
# The document
# ---------------------------------------------------------------------------

def read_tokens(root):
    """Every custom-property declaration under `root`, classified, as a report document."""
    stylesheets = find_stylesheets(root)

    scanned = []
    rows = []
    for rel in stylesheets:
        try:
            text = read_text(os.path.join(root, rel))
        except OSError as exc:
            # Named and skipped rather than fatal, and excluded from `stylesheetsRead` so the
            # document never claims a file it could not open. One unreadable sheet should not
            # cost a project every token in the others.
            print("%s: note: could not read %s: %s" % (PROG, rel, exc), file=sys.stderr)
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

    return {
        "tokensVersion": TOKENS_VERSION,
        "layer": LAYER,
        "stylesheetsRead": scanned,
        "counts": {
            # Declarations and names are both reported because they answer different
            # questions: 40 declarations over 30 names means ten are re-declared, which is a
            # theme or a media query and is worth seeing before anyone builds a swatch grid.
            "declarations": len(declarations),
            "names": len(set(d["name"] for d in declarations)),
            GROUP_COLOR: sum(1 for d in declarations if d["group"] == GROUP_COLOR),
            GROUP_UNCLASSIFIED: sum(1 for d in declarations
                                    if d["group"] == GROUP_UNCLASSIFIED),
            "aliases": sum(1 for d in declarations if d["aliasOf"] is not None),
        },
        "byFile": by_file,
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
    print(render(read_tokens(args.project_root)))
    return 0


def build_parser():
    parser = argparse.ArgumentParser(
        prog=PROG,
        description="Read a project's design tokens and report on them, "
                    "without writing anything.")
    subparsers = parser.add_subparsers(dest="command")

    tokens_cmd = subparsers.add_parser(
        "tokens",
        help="report every CSS custom property the project declares, and its group")
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
