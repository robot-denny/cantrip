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


# The two clauses of the refusal below that depend on what the rung actually reads. Both
# formats measured are *exports*, and their wording is the default; a rung reading something
# that is not an export overrides them rather than telling an operator to re-export a project
# that has nothing to re-export.
PARTIAL_EXPORT = "the export is partial and this component was left out of it"
REEXPORT_REMEDY = ("Re-export the project's content types, or point --project-root at the "
                   "export that holds this one.")


def missing_alias_error(source, alias, locations, declared_count,
                        partial=PARTIAL_EXPORT, remedy=REEXPORT_REMEDY):
    """The refusal every adapter owes an operator who asked for an alias nobody declares.

    Written once rather than once per adapter. The adapters answer the same question, so a
    difference in their wording would read as a difference in meaning — and the operator
    reading it has no way to tell which. Widening the message later then means editing one
    place instead of remembering there were three.

    The message has to serve two readings without asserting either, because the artifact
    cannot tell them apart: the alias may be misspelled, or the source may genuinely not
    contain the component. So it names both and gives the next action for each.

    `declared_count` is the number of components that *were* found in those locations, and it
    is the part that does real work. "Nothing to read here" and "read fine, your component is
    not in it" want different responses, and only the second is worth a re-export.

    `partial` and `remedy` exist because the third rung is not an export. Telling someone whose
    project has no serialization folder to "re-export the project's content types" names an
    action they cannot take, which is worse than saying nothing — so the two clauses that
    assume an export are the two a rung can replace, and the rest of the message stays one
    message.
    """
    return GuideError(
        "no %s under %s declares the alias '%s'.\n"
        "  Read %d %s there, and none of them carries that alias — so either the alias is "
        "misspelled (they are matched case-insensitively), or %s.\n"
        "  %s"
        % (source, ", ".join(locations), alias,
           declared_count, "component" if declared_count == 1 else "components",
           partial, remedy))


# ---------------------------------------------------------------------------
# The serialization versions this toolkit has been verified against
# ---------------------------------------------------------------------------
#
# Declared here, for both formats, in one place. Not because the two checks are the same
# check -- they are not, and the next comment is about exactly that -- but because the
# *evidence* is one body of measurement, and a set that lives beside its evidence gets
# widened deliberately instead of one adapter at a time.
#
# **The evidence base is narrow: three projects, all on one CMS major, two of them measured
# directly here.** Deploy's values come from the demo project (47 artifacts at 17.1.0, 16 at
# 17.2.0, 5 at 17.2.1 on its 68 document types, plus 17.0.2 on nine artifacts of other
# kinds) and from the second Deploy project the extraction reference measured, which held the
# same four side by side. uSync's single value comes from the one uSync project available,
# whose export declares format 10.7.0 across 174 content types and 150 data types.
#
# So this is a list of what has been *seen and read correctly*, not a claim about what the
# formats can contain. **Widening it is a known open question, carried in the spec** — a
# newer serialization is far more likely to be readable than not, and refusing it costs a
# whole project's guides. Until someone measures a fourth project, an unrecognized version
# is reported rather than trusted, because a shape read as though it were understood puts
# wrong fields in a guide an editor then follows.
#
# **A version that is not declared at all is read, and nothing is said about it.** Absence
# is not a claim to be unrecognized: every one of the 340 artifacts measured carries
# `__version` and every uSync export measured carries `usync.config`, so a file without one
# is outside the measured evidence entirely and refusing it would rest on nothing. Both
# formats treat absence the same way, so the rule stays one rule.
ACCEPTED_DEPLOY_VERSIONS = ("17.0.2", "17.1.0", "17.2.0", "17.2.1")
ACCEPTED_USYNC_FORMATS = ("10.7.0",)


def version_recognized(declared, accepted):
    """Whether a declared version is one this toolkit has been verified against.

    An undeclared version -- absent, empty, whitespace -- is recognized, per the note above.
    """
    value = (declared or "").strip()
    return not value or value in accepted


def usync_format_refusal(path, declared, accepted):
    """The refusal a uSync export earns when its one format declaration is unrecognized.

    uSync declares the format once for the whole export, so there is no partial answer to
    give: every content type in the folder was written by the serializer that stamped this
    number. Refusing before a single file is parsed is what makes the message truthful -- it
    says nothing was read, and nothing was.
    """
    return GuideError(
        "%s declares format '%s', which this toolkit has not been verified against — "
        "refusing the whole export rather than reading it as though it were understood.\n"
        "  uSync declares one format for the entire export, so there is no half of this "
        "read that is safe; no content type was parsed.\n"
        "  Verified formats: %s. If this export is known good, widen the accepted set in "
        "guidelib/__init__.py and say which project it was measured on."
        % (path, declared, ", ".join(accepted)))


def unread_artifacts_note(unread, accepted):
    """The note a Deploy read owes for every artifact it declined to read.

    Deploy stamps a version per artifact and one project holds a mix, so refusing the whole
    read over one stale file would reject the normal case. The artifact is skipped instead,
    and named -- an artifact dropped silently is how a component goes missing from a guide
    with nothing in the output to say so.

    Named as *unread* rather than as *missing*, because the two call for different responses:
    the file is there and can be re-serialized, which is a smaller job than finding out why
    an export left something out.
    """
    listed = "\n".join("    %s declares __version %s" % (path, version)
                       for path, version in unread)
    # Agreement matters here more than it looks. A whole project can land in this branch --
    # narrowing the accepted set by one value put 45 of the demo project's artifacts in it --
    # so the plural is the case a reader is most likely to meet, not an edge one.
    many = len(unread) != 1
    return (
        "%d Deploy %s %s not read — %s __version is not a serialization shape this "
        "toolkit has been verified against:\n%s\n"
        "  Every other artifact was read, so a component that does not depend on %s is "
        "unaffected. Verified versions: %s.\n"
        "  Re-serialize %s, or widen the accepted set in guidelib/__init__.py and say which "
        "project it was measured on."
        % (len(unread),
           "artifacts" if many else "artifact",
           "were" if many else "was",
           "their" if many else "its",
           listed,
           "any of them" if many else "this one",
           ", ".join(accepted),
           "them" if many else "the artifact"))


# ---------------------------------------------------------------------------
# Diagnostics about the read
# ---------------------------------------------------------------------------
#
# A note is neither a return value nor part of the dossier, and both exclusions are load
# bearing. It cannot go in the dossier: the signature covers every field of one, so a
# diagnostic about how the read went would make two adapters reading the same component
# disagree about its shape. And a library does not get to choose a stream -- stdout carries
# the dossier and nothing else, which is the CLI's rule to keep.
_NOTES = []


def note(message):
    """Record a diagnostic about the read for the CLI to print."""
    _NOTES.append(str(message))


def drain_notes():
    """Every note recorded since the last drain, oldest first, clearing the list."""
    notes = list(_NOTES)
    del _NOTES[:]
    return notes
