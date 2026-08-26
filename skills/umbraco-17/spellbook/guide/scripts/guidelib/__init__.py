"""Support modules for guide.py — one module per stage of the deterministic pipeline.

Nothing here is importable as an installed package: guide.py puts its own directory on
sys.path and imports `guidelib.<module>` from there. That is deliberate — a pack ships
files, not wheels, and a consuming project must be able to run the script straight out of
the skill directory.

The shared exception lives here because every stage raises the same one: a read that cannot
be completed is reported to the operator, never papered over with an empty result.
"""


class GuideError(Exception):
    """A read or a lookup could not be completed, with a message for the operator.

    Raised rather than returned so no caller can mistake a failed read for an empty
    component. guide.py catches it, prints it, and exits non-zero.
    """


def missing_alias_error(source, alias, locations, declared_count):
    """The refusal every adapter owes an operator who asked for an alias nobody declares.

    Written once rather than once per adapter. The two adapters answer the same question, so
    a difference in their wording would read as a difference in meaning — and the operator
    reading it has no way to tell which. Widening the message later then means editing one
    place instead of remembering there were two.

    The message has to serve two readings without asserting either, because the artifact
    cannot tell them apart: the alias may be misspelled, or the export may genuinely not
    contain the component. So it names both and gives the next action for each.

    `declared_count` is the number of components that *were* found in those locations, and it
    is the part that does real work. "Nothing to read here" and "read fine, your component is
    not in it" want different responses, and only the second is worth a re-export.
    """
    return GuideError(
        "no %s under %s declares the alias '%s'.\n"
        "  Read %d %s there, and none of them carries that alias — so either the alias is "
        "misspelled (they are matched case-insensitively), or the export is partial and this "
        "component was left out of it.\n"
        "  Re-export the project's content types, or point --project-root at the export that "
        "holds this one."
        % (source, ", ".join(locations), alias,
           declared_count, "component" if declared_count == 1 else "components"))
