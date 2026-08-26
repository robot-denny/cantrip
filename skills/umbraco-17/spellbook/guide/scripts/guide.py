#!/usr/bin/env python3
"""guide.py — the deterministic half of the /guide spell.

Everything about an editor-facing guide that has one right answer lives here: reading a
component's schema off disk, normalizing it into a dossier, signing it, and (in later
increments) determining the inventory, running the audit's arithmetic, and emitting a change
plan. The spell owns the rest — the prose, the diff-and-approve conversation, and every write
to the CMS. Nothing in this script writes anything, anywhere.

The split is not tidiness. A model asked to read a serialized schema will paraphrase it, and a
paraphrased property table is wrong in a way nobody notices until an editor follows it. A
script asked to write a purpose sentence produces a template. So the schema read is code and
the sentence is not.

## The rungs

A project's schema is read from whichever source it actually has, in descending fidelity:

    deploy   Umbraco Deploy artifacts, `*.uda` JSON            guidelib/deploy.py
    usync    uSync configuration, `*.config` XML               guidelib/usync.py
    models   committed `*.generated.cs` model classes          guidelib/models.py

`ADAPTERS` below is the live list — ask it rather than this comment.

A fourth rung — the running instance's management API — belongs to the spell, which reaches it
through MCP and hands the result back here as a dossier JSON. Every stage after extraction
consumes a dossier, so the live rung costs no duplicated logic.

The rung a dossier was read at is recorded on it, because completeness is judged relative to
the rung: a missing option list at the models rung is a limit of the source, not a gap in the
component. Where a rung cannot report a field at all, the dossier says so per field in
`structureGaps` rather than leaving a consumer to read an empty list as an answer.

**Two rungs reading one component produce different signatures, and that is correct.** The
signature covers the schema a dossier carries, so a dossier carrying less of it hashes
differently — the equality the adapter seam asserts is between two *formats* of the same
fidelity, never up and down the ladder. A project that gains or loses a serialization format
therefore sees every stored signature move at once, and `rung` is stored beside the signature
so that reads as one change of source rather than a hundred stale components.

A serialization version this toolkit has not been verified against is not read, and what that
costs depends on where the format declares it. uSync declares one `format` for a whole export,
so an unrecognized one refuses the read before anything is parsed. Deploy stamps `__version`
per artifact and one project holds a mix, so the artifact is skipped, named on stderr, and
everything else is still read. The accepted sets, and the narrow evidence behind them, are
declared once in `guidelib/__init__.py`.

## Usage

    guide.py extract   <alias> [--project-root DIR] [--adapter deploy|usync|models]
    guide.py signature <alias> [--project-root DIR] [--adapter deploy|usync|models]

`extract` prints the whole dossier; `signature` prints its `sourceSignature` and nothing else,
which is what makes format-blindness assertable: the same component read through two adapters
prints the same line, and no test has to hardcode a hash to say so.

`--project-root` defaults to the current directory, and the serialization folder is searched
for beneath it (the `paths.md → ## Umbraco` slot's fallback). `--adapter` defaults to whichever
format the project carries. No path, host or version is hardcoded; the spell reads the slots
and passes what it finds.

Exit: 0 on a completed read, 1 when a read cannot be completed, 2 on a usage error.
"""

import argparse
import os
import sys

# An installed skill directory is not a place to leave build output. A run reads a few
# hundred files and exits, so a bytecode cache saves nothing measurable and would appear as
# untracked clutter inside a consuming project's skills.
sys.dont_write_bytecode = True

# Run straight out of the skill directory: the script's own directory holds `guidelib/`, and
# realpath keeps that true when the script is reached through a symlink.
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))

from guidelib import GuideError    # noqa: E402
from guidelib import deploy        # noqa: E402
from guidelib import dossier       # noqa: E402
from guidelib import drain_notes   # noqa: E402
from guidelib import models        # noqa: E402
from guidelib import usync         # noqa: E402

# Rung name -> adapter module. The name is the `--adapter` value, the recorded `rung`, and the
# module, all the same string, so a project's declared serialization needs no translation
# table. Later rungs register here and change nothing else.
ADAPTERS = {
    deploy.RUNG: deploy,
    usync.RUNG: usync,
    models.RUNG: models,
}

# Detection order — highest fidelity first, so a project holding two serializations is read
# from the better one. Each adapter answers for its own format; this dispatcher knows no file
# names or extensions, which is what keeps a new rung to one registration.
#
# `models` is last because it is the fallback, not an alternative: a project committing both
# Deploy artifacts and generated models (the demo project does) must be read from the artifacts,
# which carry the tabs and the required flags the models cannot. A project with only models is
# read from them rather than refused.
DETECT_ORDER = (deploy.RUNG, usync.RUNG, models.RUNG)

PROG = "guide.py"


def resolve_adapter(project_root, requested):
    """Pick the adapter, either as asked or by what the project carries."""
    if requested:
        if requested not in ADAPTERS:
            raise GuideError(
                "adapter '%s' is not implemented; available: %s"
                % (requested, ", ".join(sorted(ADAPTERS))))
        return ADAPTERS[requested]

    for name in DETECT_ORDER:
        if ADAPTERS[name].present(project_root):
            return ADAPTERS[name]

    raise GuideError(
        "no readable schema serialization under %s; adapters available: %s. "
        "Point --project-root at the solution root, or pass --adapter."
        % (os.path.abspath(project_root), ", ".join(sorted(ADAPTERS))))


def note_if_propertyless(entry):
    """Say so when a completed read describes a component with no editable fields.

    A note, not a refusal, and the difference is the whole of this behavior.

    The refusing rule the ladder does enforce is "never answer a question you could not
    read", and every way an export can be partial *and* visible in what was read already
    raises before a dossier exists: a composition whose base was not exported, a Deploy
    property whose data type was not exported, a folder holding no artifact for the requested
    alias. So the line is drawn on **resolvability**, never on how thin the result is.

    Thinness cannot be the line, because thin and healthy are the same document. Two shapes
    among the demo project's 68 document types have no fields and are perfectly correct: a
    taxonomy-style node carrying only a name, and a type declaring one empty tab that a
    composition or a later change fills. Refusing an empty property list would refuse both,
    and a guide set missing its taxonomy nodes is a worse outcome than one that reports them
    plainly.

    **The limit, stated rather than guessed at:** a truncated export whose artifact exists and
    declares nothing is *not* distinguishable from a genuinely property-less component by
    reading the artifact. There is one weak signal -- Deploy writes `PropertyGroups` and
    `PropertyTypes` even when empty, on all 68 of the demo project's artifacts, so an artifact
    missing the keys entirely was probably not written by the serializer -- and it is not used
    here. It rests on one project, and no equivalent has been observed for uSync at all, so
    implementing it would refuse on evidence too narrow to name in the message and would leave
    the two adapters asymmetric for no stated reason. The note goes to the one reader who can
    actually resolve the ambiguity instead.

    stderr, so stdout stays the dossier and nothing else: a caller that already knew this
    component has no fields is unaffected, and a person running the command by hand sees it.
    """
    if dossier.count_properties(entry):
        return
    # One clause per line, the same shape the refusal uses. These messages are read side by
    # side in a scrollback or a log, and a wall of wrapped prose beside an indented list reads
    # as two different kinds of thing when they are two halves of one rule.
    print(
        "%s: note: '%s' declares no editable properties.\n"
        "  Every reference in its export resolved, so this is the component's own shape "
        "rather than a gap in the export \u2014 a taxonomy-style node, or a type contributing "
        "one empty tab, reads exactly like this.\n"
        "  If you expected fields, look for them on a composition this project does not "
        "export, or under a different alias."
        % (PROG, entry.get("alias")), file=sys.stderr)


def report_read_notes():
    """Print whatever the adapters recorded about the read itself, to stderr.

    Before the dossier, because these are caveats about the document that follows: an
    artifact the read declined to open changes how much the reader should trust a gap in it.
    The two streams are separate, so a caller piping stdout is unaffected either way — this
    is for the person watching a terminal.

    stderr, and never stdout, for the reason `signature` exists at all: stdout carries the
    document and nothing else, so a byte comparison of two runs compares what was read
    rather than what was said about the reading.

    Called from a `finally`, so a failed read still reports what it noticed on the way. A
    refusal is then two messages -- the note, then the error -- and that order is deliberate:
    the note is the context the error is missing.
    """
    for message in drain_notes():
        print("%s: note: %s" % (PROG, message), file=sys.stderr)


def cmd_extract(args):
    adapter = resolve_adapter(args.project_root, args.adapter)
    # `finally`, because the read's own caveats matter most when the read then fails. The
    # case that forced this: the requested alias IS the artifact skipped for its version, so
    # the lookup finds nothing and raises -- and the note explaining exactly why it found
    # nothing was computed, queued, and then thrown away with the exception. What the
    # operator saw was "either the alias is misspelled, or the export is partial", with no
    # mention of the version the tool had already read and rejected.
    try:
        entry = adapter.extract(args.project_root, args.alias)
    finally:
        report_read_notes()
    print(dossier.render(entry))
    note_if_propertyless(entry)
    return 0


def cmd_signature(args):
    """The dossier's signature, alone on a line.

    Alone because the assertion that two formats agree is a byte comparison of two runs, and
    anything else printed would be compared too. It is also what a caller stores against a
    guide page, so a bare value is what a shell pipeline wants.
    """
    adapter = resolve_adapter(args.project_root, args.adapter)
    try:
        entry = adapter.extract(args.project_root, args.alias)
    finally:
        report_read_notes()
    print(entry["sourceSignature"])
    # Noted here too, not only under `extract`. A caller may only ever ask for the signature,
    # and a signature over a component with no fields is a value worth knowing is thin.
    note_if_propertyless(entry)
    return 0


def build_parser():
    parser = argparse.ArgumentParser(
        prog=PROG,
        description="Read an Umbraco component's schema and report on it, without writing anything.")
    subparsers = parser.add_subparsers(dest="command")

    extract = subparsers.add_parser(
        "extract", help="print one component's dossier as JSON")
    extract.add_argument("alias", help="the component's document-type or element-type alias")
    extract.set_defaults(handler=cmd_extract)

    signature = subparsers.add_parser(
        "signature", help="print one component's source signature and nothing else")
    signature.add_argument("alias", help="the component's document-type or element-type alias")
    signature.set_defaults(handler=cmd_signature)

    # Shared by every subcommand that reads the project rather than a supplied JSON file.
    for sub in (extract, signature):
        sub.add_argument(
            "--project-root", default=".", metavar="DIR",
            help="the project to read (default: the current directory)")
        sub.add_argument(
            "--adapter", default=None, metavar="RUNG",
            help="force a serialization format instead of detecting one: %s"
                 % ", ".join(sorted(ADAPTERS)))
    return parser


def main(argv):
    parser = build_parser()
    args = parser.parse_args(argv)
    if not getattr(args, "handler", None):
        parser.print_help(sys.stderr)
        return 2
    # Checked here rather than in each adapter: a mistyped root would otherwise surface as
    # "no schema found", which reads like a project problem instead of a typo. `getattr`
    # because later subcommands take a supplied JSON file and no project root at all.
    root = getattr(args, "project_root", None)
    if root is not None and not os.path.isdir(root):
        print("%s: error: no such directory: %s" % (PROG, root), file=sys.stderr)
        return 1
    try:
        return args.handler(args)
    except GuideError as exc:
        print("%s: error: %s" % (PROG, exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
