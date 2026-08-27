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
# What each rung cannot report
# ---------------------------------------------------------------------------
#
# Keyed by rung name, and here rather than inside the adapter that owns the text, for one
# reason: completeness is judged relative to the rung a dossier was read at, and on the
# `--inventory` seam there is no adapter in play at all. The spell hands the audit a document
# whose `rung` is a bare string read from a running instance, so a lookup that needed the
# module could not answer the one question that seam exists to make answerable.
#
# The accepted-version sets above sit here for the same shape of reason -- a per-format fact
# that more than one stage reads, declared once at the package root and imported back by the
# adapter that owns it. This is that pattern, keyed rather than named.
#
# **Two representations of one constant, and neither is the source of the other's text.** A
# dossier states each gap as one sentence in JSON; a report prints it inside 88 columns. So the
# lines are authored wrapped and joined with a single space for the dossier, exactly the way
# the sentences were assembled from source lines before -- one comma per line break. The
# `models-only-rung` fixture's hand-authored golden file states the joined form, so it is the
# guard that the joining is exact.
#
# **The empty tuples are a positive claim, not an omission.** Deploy and uSync read the whole
# structure, so there is nothing for a report to state, and saying that here is what keeps
# "this rung reads everything" from being inferred from a missing key. A rung absent from this
# table -- the running instance's management API, which only the spell can read -- yields no
# statement either, and that is right rather than a gap: it reads MORE than any file-reading
# rung, so a caveat there would warn about the best source available.
# Every rung this script knows the fidelity of, keyed by the rung's own name. A rung listed
# with `()` reads the whole structure; a rung listed with entries names what it cannot report.
#
# **An unlisted rung is a third answer, not the first.** `.get(rung, ())` gave one answer to two
# different questions, so a mistyped rung in a hand-built `--inventory` document -- or a fourth
# adapter added without an entry here -- printed no caveat and read exactly like a source that
# reports everything. That is the most over-confident thing this report can say. `rung_fidelity`
# below tells the three apart, and the audit says "completeness unknown" for the third.
#
# `live` is registered ahead of the spell that produces it (plan Step 15). It reads the running
# instance through the management API, which reports more than any file rung, so `()` is the
# right entry -- and registering it now means the spell does not have to remember to.
RUNG_GAPS = {
    "deploy": (),
    "usync": (),
    "live": (),
    # Every entry is `field: explanation`, key first, because a consumer rendering a property
    # table needs to know which *column* it cannot fill; "the models rung is thin" does not
    # tell it. ASCII only and short declaratives: these reach a dossier through JSON written
    # with `ensure_ascii`, so a dash or a curly quote would arrive as an escape sequence.
    #
    # Declared in the order the dossier sorts them, so a report printing them as declared and
    # a dossier printing them sorted read the same way round.
    "models": (
        # Two entries, because the dossier has two `description` fields and this rung treats
        # them differently. One entry naming both read as "no descriptions anywhere" to
        # anyone skimming key-first, which is what the `field:` convention invites -- while
        # property descriptions sit populated in the same document.
        ("description (component): not recorded. A generated model's class summary carries",
         "the display name and nothing else."),
        ("description (property): recorded, but as ModelsBuilder escaped it: line breaks",
         "collapsed to spaces, and angle brackets rewritten as braces."),
        # The one entry that is not an absence. The generated C# property type IS the rung's
        # best answer to "what is this field", per `umbraco-17-feature-backfill` -- but it is
        # a different vocabulary from the editor alias the higher rungs put in the same field,
        # so a consumer that pattern-matches on `Umbraco.*` has to be told rather than left to
        # guess.
        ("editor: the generated C# property type, not the data type's editor alias.",),
        ("icon: not recorded. The backoffice icon is not generated into a model.",),
        ("mandatory: not recorded. Every property reads false; required flags",
         "are not generated."),
        ("options: not recorded. Every option list reads empty; an option list lives on the",
         "data type, which this rung does not read."),
        ("sortOrder: not recorded. Every property reads 0, and the unnamed bucket is in",
         "alias order."),
        ("tabs: not recorded. A generated model carries no tab or group structure, so every",
         "property is in the one unnamed bucket."),
    ),
}


# What `rung_fidelity` answers, kept as names rather than as a bare bool so a caller cannot
# collapse the third case back into the first by accident.
FIDELITY_FULL = "full"
FIDELITY_PARTIAL = "partial"
FIDELITY_UNKNOWN = "unknown"


def _fold(rung):
    """The lookup key. Folded because a rung can arrive from a hand-written `--inventory` file,
    where `Models` is a typo and not a different rung -- the same reason a guide's alias is
    folded before it is matched."""
    return (rung or "").strip().lower()


def rung_fidelity(rung):
    """Whether this script knows how completely the named rung reads a project.

    Three answers, because there are three states and two of them used to share one. A rung
    this table does not name is `unknown`: it may read everything or nothing, and saying
    nothing about it is the one thing that misleads.
    """
    key = _fold(rung)
    if key not in RUNG_GAPS:
        return FIDELITY_UNKNOWN
    return FIDELITY_PARTIAL if RUNG_GAPS[key] else FIDELITY_FULL


def rung_gap_lines(rung):
    """What a rung cannot report in full, as lines a report prints inside its own width.

    Empty for a rung that reads the whole structure AND for one this table does not name --
    ask `rung_fidelity` to tell those apart before deciding what to print.
    """
    return RUNG_GAPS.get(_fold(rung), ())


def rung_gaps(rung):
    """The same statements, one sentence each, for a dossier or an audit document to carry."""
    return tuple(" ".join(lines) for lines in rung_gap_lines(rung))


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


# ---------------------------------------------------------------------------
# The stored reference
# ---------------------------------------------------------------------------
#
# A guide page records which component it documents, at which signature, read at which rung.
# Two stages read that reference from two different files produced by the same spell -- the
# audit reads a whole guide set, the change plan reads one page -- so what a reference IS,
# and which shapes of it are refused, is declared once here rather than twice.
#
# It was twice. The audit's version was written first and reviewed twice, and both reviews
# found gaps in exactly this validation; a second hand-rolled copy in the change plan would
# have been a third chance to miss the same ones. The consequence clause of the first refusal
# is the only caller-specific part, so it is a parameter and the rest is one message.

# What an absent `source` key costs, in the words of the stage that is asking. Absent and
# `null` are different facts -- one is about the CMS, the other about the producer -- and the
# reason that difference matters is not the same for both readers.
REFERENCE_CONSEQUENCE_REPORT = ("the two land a guide in opposite sections of this report")
REFERENCE_CONSEQUENCE_PLAN = (
    "the two decide whether this page is regenerated or adopted, which is the difference "
    "between updating a guide and overwriting work somebody did by hand")


def stored_reference(where, label, raw, consequence=REFERENCE_CONSEQUENCE_REPORT):
    """One guide page's stored reference, validated and normalized, or None for "no source".

    Returns `{"alias", "kind", "signature", "rung"}` with every field but `alias` optionally
    None, or `None` when the entry states explicitly that it carries no reference.

    `source: null` and a missing `source` key are **not** the same thing, and the difference
    is why an absent key refuses rather than defaulting. "This page carries no stored
    reference" is a fact about the CMS; "this file does not mention a reference" is a fact
    about the producer. Defaulting the second to the first turns a spell that failed to read
    the property into a report saying every guide was written by hand, or into a plan that
    adopts a page it should have regenerated.

    `where` locates the entry (a path, plus a position where a file holds many) and `label`
    names the page, because the entry that is broken is often the one whose name did not come
    through either.
    """
    if "source" not in raw:
        raise GuideError(
            "%s ('%s') has no 'source' key.\n"
            "  Every entry states its stored reference or states explicitly that it has none "
            "(\"source\": null). An absent key cannot be told from a reference the producer "
            "failed to read, and %s."
            % (where, label, consequence))
    source = raw["source"]
    if source is None:
        return None
    if not isinstance(source, dict):
        raise GuideError("%s ('%s') has a 'source' that is %s, not an object or null."
                         % (where, label, type(source).__name__))

    alias = source.get("alias")
    if not isinstance(alias, str) or not alias.strip():
        raise GuideError(
            "%s ('%s') has a stored reference with no alias.\n"
            "  A reference naming nothing cannot be classified: it may be a guide whose source "
            "was deleted, or a page that was never generated from one, and those belong in "
            "different sections. Write \"source\": null for a guide that claims no source."
            % (where, label))

    return {
        "alias": alias.strip(),
        "kind": _reference_string(where, label, source, "kind"),
        # Compared as an opaque string, never parsed. The signature's format belongs to
        # guidelib/dossier.py, and a format check in a consumer would be a second rule that
        # could disagree with the first.
        "signature": _reference_string(where, label, source, "signature"),
        "rung": _reference_string(where, label, source, "rung"),
    }


def _reference_string(where, label, source, key):
    """A stored-reference field that may be absent, may be null, and must otherwise be text.

    Absent and null both mean "the reference does not record this", which is answerable. A
    number or an object means the producer wrote something no consumer can compare and none
    can print, which is not -- so it refuses rather than coercing a value into a comparison
    whose result would be meaningless.
    """
    value = source.get(key)
    if value is None:
        return None
    if not isinstance(value, str):
        raise GuideError("%s ('%s') has a non-string '%s': %r." % (where, label, key, value))
    return value.strip() or None
