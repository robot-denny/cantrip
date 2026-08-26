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
    usync    uSync configuration, `*.config` XML               not implemented yet
    models   committed `*.generated.cs` model classes          not implemented yet

`ADAPTERS` below is the live list — ask it rather than this comment.

A fourth rung — the running instance's management API — belongs to the spell, which reaches it
through MCP and hands the result back here as a dossier JSON. Every stage after extraction
consumes a dossier, so the live rung costs no duplicated logic.

The rung a dossier was read at is recorded on it, because completeness is judged relative to
the rung: a missing option list at the models rung is a limit of the source, not a gap in the
component.

## Usage

    guide.py extract <alias> [--project-root DIR] [--adapter deploy]

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

from guidelib import GuideError  # noqa: E402
from guidelib import deploy      # noqa: E402
from guidelib import dossier     # noqa: E402

# Rung name -> adapter module. The name is the `--adapter` value, the recorded `rung`, and the
# module, all the same string, so a project's declared serialization needs no translation
# table. Later rungs register here and change nothing else.
ADAPTERS = {
    deploy.RUNG: deploy,
}

# Detection order — highest fidelity first, so a project holding two serializations is read
# from the better one. Each adapter answers for its own format; this dispatcher knows no file
# names or extensions, which is what keeps a new rung to one registration.
DETECT_ORDER = (deploy.RUNG,)

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


def cmd_extract(args):
    adapter = resolve_adapter(args.project_root, args.adapter)
    entry = adapter.extract(args.project_root, args.alias)
    print(dossier.render(entry))
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

    # Shared by every subcommand that reads the project rather than a supplied JSON file.
    for sub in (extract,):
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
