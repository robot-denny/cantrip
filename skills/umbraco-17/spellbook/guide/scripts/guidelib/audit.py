"""The audit — the gap between what a project's code declares and what its guides document.

Every other stage reads a project. This one reads a project *and* a guide set, and the guide
set does not live on disk: it is in a CMS, behind a connection this script deliberately does
not have. So the guides arrive as a JSON file the spell produces, and the arithmetic over them
stays here — deterministic, fixture-testable, and unable to write anything anywhere.

## The three questions, and the one that is none of them

    undocumented   a documentable unit no guide page's stored reference names
    orphaned       a guide naming an alias this project no longer declares
    stale          a guide whose stored signature differs from its source's current one

**A guide claiming no source at all is in none of them.** A hand-written guide about image
sizing standards documents nothing in the schema, so it can be neither an orphan nor stale, and
it does not close a gap either. That exclusion is a functional requirement rather than a
nicety: an audit that reported editorial guides as orphans would train its reader to ignore the
orphan list, which is the list with the destructive remedy.

**A guide for something present in code but not documentable is also in none of them.** A
settings model, a composition, a folder: the guide documents real schema, so it is not an
orphan, and the thing it documents is not a unit this toolkit proposes documenting, so no gap
is open. There is nothing to report, and the audit says nothing.

## Why the guide set is an input file rather than a read

The spec's line is that the script computes and the spell writes. A CMS read needs a base URL
and credentials, which the spell already reaches through MCP; a CMS read here would mean this
module could not be tested without an instance, and the audit's whole value is arithmetic. So
the seam is a file, and the same seam accepts a *supplied* inventory (`--inventory`) for the
rung the script cannot read at all — the running instance's management API.

## Warns, never blocks

The report is a backlog, not a gate. **A completed audit exits 0 whatever it found**, because
an audit that exits non-zero on findings fails a build by default anywhere it is wired into CI
— and guides being cut from scope, louder, is the outcome this capability exists to prevent. A
non-zero exit stays reserved for a read that could not be completed. Opting in to a gate is a
separate, explicit thing.

## What a guides file may not be trusted to be

It is produced by another process, and it is the one input this command cannot check by
re-reading the project. Every malformed shape below therefore **refuses the whole audit**
rather than skipping an entry, because the failure mode of skipping is a report whose numbers
are quietly wrong: a dropped entry moves its component into the undocumented list, and a
backlog with a phantom item in it is worse than no backlog.

    the file is missing or unreadable      refused
    the file is not JSON                   refused, with the parse position
    `guidesVersion` is not one known here  refused, naming the version found
    an entry is not an object              refused, naming its position
    an entry has no `source` key           refused: absent is not the same as "explicitly none"
    a `source` carries no `alias`          refused: a reference to nothing cannot be classified
    a `signature` or `rung` is not a string  refused: an unusable value, not a missing one

Two shapes are **not** refused, because both are answerable:

    two guides claiming one alias         reported as a note; the component is documented
                                          either way, and both pages are checked for staleness
    a `signature` in an unexpected format  compared as an opaque string. The signature's format
                                          belongs to `guidelib/dossier.py`, and a format check
                                          here would be this module inventing a second rule
                                          that could disagree with the first.

The line is the same one the extraction ladder draws: a value that cannot be resolved refuses,
and a value that is merely thin is reported.
"""

import json
import os

from guidelib import GuideError
from guidelib import inventory
from guidelib import note
from guidelib import FIDELITY_FULL
from guidelib import FIDELITY_UNKNOWN
from guidelib import rung_fidelity
from guidelib import rung_gap_lines
from guidelib import rung_gaps
from guidelib import stored_reference
# Aliased, because both renderers define a function called `report` and the bare
# module name would be shadowed by it inside exactly the function that needs it.
from guidelib import report as rpt

AUDIT_VERSION = 1

# The guides-file shapes this module has been written against. One so far, and absence is
# accepted for the reason `version_recognized` gives for a serialization version: absence is
# not a claim to be unrecognized, and refusing over it would rest on nothing.
ACCEPTED_GUIDES_VERSIONS = (1,)

# The label an entry gets when it names no page. Cosmetic — it reaches the report only beside an
# alias that already identifies the finding — so a missing page name is not worth refusing over.
UNNAMED_PAGE = "unnamed guide page"


# --- the rules, one per counted section ---------------------------------------
#
# Each is a tuple of report lines wrapped by hand, exactly as the inventory's are, so the
# report prints them as they stand and a golden fixture can be authored against them. Every
# count prints its rule beside it *when it has findings*, because a rule exists to make a wrong
# finding diagnosable and an empty section has no finding to diagnose. The determiner behind the
# primary count is named in the header instead, which always prints.

RULE_UNDOCUMENTED = (
    "A documentable unit that no guide page's stored reference names: a component an editor",
    "can place from a block-editor palette, or a document type proposed as a page. Matched",
    "on the alias, case-insensitively, never on a page's name or its address.",
)
RULE_ORPHANED = (
    "A guide whose stored reference names an alias no content type in this read declares. A",
    "guide claiming no source at all is never an orphan, because a hand-written guide",
    "documents something that was never in the schema. Each is named as alias (the guide",
    "page's own name), since the source it claims has no name left to print.",
)
RULE_STALE = (
    "A guide whose stored signature differs from its source's current signature, so the",
    "source changed shape after the guide was generated. Compared only where the guide",
    "records a signature and was stored at this read's rung: two rungs sign one component",
    "differently by design, so comparing across them would report every guide as stale.",
)

# The determiner behind the documentable count, stated in the header rather than in the
# undocumented section, because it is the count most worth doubting and the header always
# prints. It defers to `inventory` rather than restating that rule, which lives there.
RULE_DOCUMENTABLE = (
    "Counted from the project's own block-editor palettes and the page types it proposes,",
    "never from the element-type flag. Run inventory for that rule in full, with its own",
    "counts.",
)

# Completeness is judged relative to the rung the inventory was read at, and where that rung
# cannot report a field, the report says so **once, for the whole report**. Never per guide: a
# guide whose property table has no required flags because the source records none is not an
# incomplete guide, and twelve findings saying otherwise would be twelve pieces of work nobody
# can do. The per-field text is `RUNG_GAPS` in `guidelib/__init__.py` — the same statements a
# dossier read at that rung carries in `structureGaps`, so the two documents cannot disagree.
#
# Hand-wrapped like every rule above, count and plural interpolated into the first line only so
# the rest sit at a width a reader can rely on.
STATEMENT_STRUCTURE = (
    "Structure unavailable from this source: %d dossier %s this rung cannot report in",
    "full, so completeness below is judged against what it can. Stated here once, and",
    "never against a guide: a guide is not incomplete for a field its source never",
    "recorded, and every line below is a limit of the read rather than work for anyone.",
)

# The third fidelity answer. A rung this script has no record for may read everything or
# almost nothing, and the old registry answered "nothing missing" for it -- the same words it
# uses for a source that genuinely reports in full. Saying so is the whole fix.
STATEMENT_UNKNOWN_RUNG = (
    "Structure completeness unknown: this read reports the rung '%s', which this script",
    "has no fidelity record for. Completeness below is therefore judged against a source",
    "whose limits are not known here — treat a clean result as unconfirmed rather than as",
    "a source that reported everything.",
)

CAPTION_UNDOCUMENTED = "Undocumented, present in code with no guide page"
CAPTION_ORPHANED = "Orphaned, claiming a source this project no longer holds"
CAPTION_STALE = "Stale, whose stored signature no longer matches its source"


# ---------------------------------------------------------------------------
# The guides file
# ---------------------------------------------------------------------------

def load_guides(path):
    """Read and validate a guides file, returning one normalized entry per guide page.

    Each entry is `{"page": label, "source": None | {"alias", "kind", "signature", "rung"}}`.

    `source: null` and a missing `source` key are **not** the same thing, and the difference is
    the reason this refuses rather than defaulting. "This page carries no stored reference" is a
    fact about the CMS that decides whether the page can ever be an orphan; "this file does not
    mention a reference" is a fact about the producer. Defaulting the second to the first would
    turn a spell that failed to read the property into a report saying every guide was written
    by hand — every orphan and every stale guide silently gone from a report whose job is to
    name them.
    """
    if not os.path.isfile(path):
        raise GuideError(
            "no guides file at %s.\n"
            "  The guide set is read from the CMS by the spell and handed to this script as "
            "JSON; this script holds no connection and cannot read it itself.\n"
            "  Pass --guides pointing at that file, or run with an empty guide set to see the "
            "whole inventory as a backlog." % os.path.abspath(path))
    try:
        with open(path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (ValueError, OSError) as exc:
        raise GuideError(
            "%s is not readable JSON: %s.\n"
            "  Refusing rather than reading what parsed: a guides file half-read reports the "
            "components its dropped entries documented as undocumented, and nothing in the "
            "report would say so." % (path, exc))

    # A bare array is what a one-line shell filter over an API response produces, and the
    # object form is what carries a version. Both are accepted; nothing else is, because a
    # third shape would be a guess about which key held the guides.
    if isinstance(payload, list):
        listed = payload
    elif isinstance(payload, dict):
        declared = payload.get("guidesVersion")
        if declared is not None and declared not in ACCEPTED_GUIDES_VERSIONS:
            raise GuideError(
                "%s declares guidesVersion %r, which this script has not been written "
                "against.\n"
                "  Known versions: %s. A version bump means the entry shape changed, so "
                "reading it as though it had not would misclassify guides silently."
                % (path, declared,
                   ", ".join(str(v) for v in ACCEPTED_GUIDES_VERSIONS)))
        listed = payload.get("guides")
        if listed is None:
            raise GuideError(
                "%s holds no 'guides' key.\n"
                "  A guides file is either {\"guides\": [...]} or a bare array of entries. An "
                "empty guide set is written as an empty array, which reports the whole "
                "inventory as a backlog — that is a different statement from a missing key."
                % path)
    else:
        raise GuideError(
            "%s holds %s at the top level, not an object or an array of guide entries."
            % (path, type(payload).__name__))

    if not isinstance(listed, list):
        raise GuideError("%s: 'guides' holds %s, not an array of guide entries."
                         % (path, type(listed).__name__))

    entries = [_entry(path, index, raw) for index, raw in enumerate(listed)]
    _note_duplicates(entries)
    return entries


def _entry(path, index, raw):
    """One guides-file entry, validated and normalized.

    `index` is in the message rather than only the page name, because the entry that is broken
    is often the one whose name did not come through either.
    """
    where = "%s: guide %d" % (path, index + 1)
    if not isinstance(raw, dict):
        raise GuideError("%s is %s, not an object." % (where, type(raw).__name__))

    page = raw.get("page")
    if page is not None and not isinstance(page, str):
        raise GuideError("%s has a non-string 'page': %r." % (where, page))
    label = (page or "").strip() or UNNAMED_PAGE

    # What a stored reference is, and which of its shapes are refused, is declared once in
    # guidelib/__init__.py. The change plan reads the same reference off a single page, and two
    # hand-rolled validations of one shape drift in exactly the places the two reviews of this
    # one found gaps.
    return {"page": label, "source": stored_reference(where, label, raw)}


def _note_duplicates(entries):
    """Say so when two guide pages claim one source, without refusing.

    Answerable, unlike the refusals above: the component is documented either way, so no count
    in the report changes, and both pages are compared for staleness. It is still worth saying,
    because two pages for one component is the shape an editor's duplicate leaves behind and
    the index will list both.
    """
    pages = {}
    for entry in entries:
        if entry["source"]:
            pages.setdefault(entry["source"]["alias"].lower(), []).append(entry["page"])
    for alias, named in sorted(pages.items()):
        if len(named) > 1:
            # One page per line, and each clause on its own, matching `unread_artifacts_note`.
            # Joined inline the first line reached 306 characters on four plausible page
            # titles -- and a title is free text a person types, so there is no length to
            # rely on.
            lines = ["%d guide pages claim the source '%s':" % (len(named), alias)]
            lines.extend("    %s" % page for page in named)
            lines.append("  Neither count in the audit changes, since the component is "
                         "documented.")
            lines.append("  But the index lists every one of them, and only one is the one "
                         "to keep.")
            note("\n".join(lines))


# ---------------------------------------------------------------------------
# The inventory this audits against
# ---------------------------------------------------------------------------

def load_inventory(path):
    """Read a pre-computed inventory document, as `inventory --json` emits one.

    This is the rung-3 seam: the running instance's management API belongs to the spell, which
    reaches it through MCP and hands the result back here. Without it the audit could only ever
    run on a project carrying an on-disk serialization, and the ladder would stop one rung
    short of where it was specified to reach.

    Validated the same way a guides file is, and for the same reason: it arrives from another
    process. The version is checked against the determiner's own constant, so a document written
    by a newer inventory is refused here rather than misread.
    """
    if not os.path.isfile(path):
        raise GuideError("no inventory file at %s." % os.path.abspath(path))
    try:
        with open(path, "r", encoding="utf-8") as handle:
            doc = json.load(handle)
    except (ValueError, OSError) as exc:
        raise GuideError("%s is not readable JSON: %s." % (path, exc))
    if not isinstance(doc, dict):
        raise GuideError("%s holds %s at the top level, not an inventory document."
                         % (path, type(doc).__name__))

    declared = doc.get("inventoryVersion")
    if declared != inventory.INVENTORY_VERSION:
        raise GuideError(
            "%s declares inventoryVersion %r, and this script reads %d.\n"
            "  Regenerate it with `inventory --json`, or supply a document written by a "
            "matching version — the lists this audit reads are the ones a version bump would "
            "move." % (path, declared, inventory.INVENTORY_VERSION))
    for key in ("rung", "components", "pageTypesProposed"):
        if key not in doc:
            raise GuideError("%s holds no '%s' key; that is not an inventory document."
                             % (path, key))
    if not isinstance(doc["rung"], str) or not doc["rung"].strip():
        raise GuideError("%s declares a 'rung' of %r; a rung is a non-empty string."
                         % (path, doc["rung"]))
    # Optional — most inventories exclude nothing — but refused rather than ignored where it
    # is present and unreadable. The report prints this name to explain a count it cannot
    # otherwise justify, so a document that carries the exclusion without a name to print
    # would produce the silent count the exclusion exists to prevent.
    if doc.get("excludedPalette") is not None:
        if not isinstance(doc["excludedPalette"], str) or not doc["excludedPalette"].strip():
            raise GuideError(
                "%s declares an 'excludedPalette' of %r; an excluded palette is named by a "
                "non-empty string, and its name is what the report prints to explain the "
                "documentable count." % (path, doc["excludedPalette"]))
    for key in DECLARED_LISTS:
        if key in doc:
            # Replaced, not merely checked: every count downstream reads these lists, so the
            # deduped version has to be the one they read or the report's own arithmetic can
            # disagree with itself.
            doc[key] = _check_named_list(path, key, doc[key])
    return doc


def _check_named_list(path, key, value):
    """Every item in one of an inventory's content-type lists is an object naming an alias.

    Checked field by field, the way a guides entry is, and for the same reason -- this document
    also arrives from another process. The first version checked four top-level keys and
    stopped, and `run` then indexed `item["alias"]` directly: an item with a name and no alias
    produced a raw KeyError traceback rather than the refusal every other bad input here gets,
    on the one path the spell will use to hand back a live read.
    """
    if not isinstance(value, list):
        raise GuideError("%s holds '%s' as %s; an inventory list is an array."
                         % (path, key, type(value).__name__))
    seen = {}
    kept = []
    for index, item in enumerate(value):
        where = "%s: %s[%d]" % (path, key, index)
        if not isinstance(item, dict):
            raise GuideError("%s is %s, not an object." % (where, type(item).__name__))
        alias = item.get("alias")
        if not isinstance(alias, str) or not alias.strip():
            raise GuideError(
                "%s names no alias (has %r).\n"
                "  Every entry in an inventory list is a content type, and its alias is what "
                "this audit matches a guide against. An entry without one cannot be compared "
                "to anything." % (where, alias))
        signature = item.get("signature")
        if signature is not None and not isinstance(signature, str):
            raise GuideError("%s has a non-string 'signature': %r." % (where, signature))
        # Deduped on the lowercased alias, because the determiner dedupes by construction and
        # a supplied document has no such guarantee. Left in, the report contradicted its own
        # arithmetic: two entries differing only in case printed "1 documentable unit: 2
        # components + 0 proposed page types", since the unit count is deduped and the
        # component count beside it was a raw list length.
        folded = alias.strip().lower()
        if folded in seen:
            note("%s and %s both name the alias '%s', which is one content type.\n"
                 "  Counted once. An inventory this script writes cannot hold a duplicate, so "
                 "a supplied one that does was assembled somewhere else."
                 % (seen[folded], where, alias.strip()))
            continue
        seen[folded] = where
        kept.append(item)
    return kept


# Every list in an inventory document that names a content type the project declares. Their
# union is what an orphan is measured against: a guide for a settings model, a composition, or
# a folder documents schema that is really there, so it is not an orphan even though its
# subject is not a documentable unit.
# `excludedPaletteComponents` is here and not in the pair below, and the split is the point: a
# showcase element a project excluded by palette is still a content type that project declares,
# so a guide naming one is no orphan — it simply closes no gap, which is the same answer this
# audit already gives a guide for a settings model or a composition.
DECLARED_LISTS = ("components", "pageTypesProposed", "settingsModels",
                  "unpalettedElementTypes", "notProposed", "excludedPaletteComponents")

# The two lists a guide can close a gap in. The inventory's own summary line adds exactly these
# two, so the audit's documentable count and the inventory's cannot drift.
DOCUMENTABLE_LISTS = ("components", "pageTypesProposed")


def run(inventory_doc, guides):
    """Compute the audit document from an inventory and a guide set.

    Pure arithmetic over two inputs: no file is read here and none is written anywhere, so a
    caller can hand this a hand-authored pair and get the report a project would have produced.
    """
    units = {}
    for key in DOCUMENTABLE_LISTS:
        for item in inventory_doc.get(key) or []:
            units[item["alias"].lower()] = item
    declared = set()
    for key in DECLARED_LISTS:
        for item in inventory_doc.get(key) or []:
            declared.add(item["alias"].lower())

    read_rung = inventory_doc.get("rung")
    documented, orphaned, stale = set(), [], []
    no_signature = no_current = other_rung = 0
    sourced = 0

    for entry in guides:
        source = entry["source"]
        if not source:
            continue
        sourced += 1
        alias = source["alias"]
        folded = alias.lower()
        if folded not in declared:
            # An orphan names the page rather than a display name: the source it claims is gone,
            # so there is no name left to read, and the page is what the operator acts on.
            orphaned.append({"alias": alias, "name": entry["page"]})
            continue
        unit = units.get(folded)
        if unit is None:
            # The alias is declared but is not a documentable unit: a settings model, a
            # composition, a folder. The guide documents schema that is really there, so it is
            # no orphan; the thing it documents is not one this toolkit proposes documenting,
            # so it closes no gap and there is no current signature to compare. Silence is the
            # whole finding. Counted nowhere but the guide-pages total, deliberately — putting
            # it in the not-compared line would say the reference lacked a signature when what
            # it lacks is a unit on the other side.
            continue
        documented.add(folded)
        current = unit.get("signature")
        if not source["signature"]:
            no_signature += 1
            continue
        if not current:
            # The INVENTORY has no signature to compare against, which is a different fact from
            # the guide not recording one. Counted apart, because the header used to say "N
            # record no stored signature" for both and that names the wrong side: a guide can
            # carry a perfectly good signature and still be uncomparable.
            no_current += 1
            continue
        # A signature stored at another rung is not comparable, and neither is one whose rung
        # was never recorded. The `rung` field is optional on a stored reference, so requiring
        # it to be present AND different let a signature with no rung through to the comparison
        # -- reported as stale against a rung that may not be the one that produced it, while
        # the printed rule claimed comparison happened only at this read's rung. Two rungs sign
        # the same component differently by design, so an unknown rung is unknown, not this one.
        if not source["rung"] or (read_rung and source["rung"] != read_rung):
            other_rung += 1
            continue
        if source["signature"] != current:
            stale.append({"alias": alias,
                          "name": (unit or {}).get("name") or entry["page"]})

    undocumented = [units[folded] for folded in units if folded not in documented]

    return {
        "auditVersion": AUDIT_VERSION,
        "rung": read_rung,
        # Carried on the document for the reason a dossier carries the same list: it is a
        # statement about the read, and a consumer holding the audit's arithmetic without it
        # would read every count as though the source had been complete. Looked up by the rung
        # name alone, which is all a supplied inventory holds — see `RUNG_GAPS`.
        "structureGaps": list(rung_gaps(read_rung)),
        "componentsRead": len(inventory_doc.get("components") or []),
        "pageTypesProposed": len(inventory_doc.get("pageTypesProposed") or []),
        "documentableUnits": len(units),
        # Carried through rather than recomputed. Where the inventory arrived as a file this
        # audit did not derive, the exclusion it was read under is the supplied document's to
        # state — and stating it is not optional, because it is what makes the count above
        # explicable.
        "excludedPalette": inventory_doc.get("excludedPalette"),
        "excludedPaletteComponents": list(inventory_doc.get("excludedPaletteComponents") or []),
        "guidePagesRead": len(guides),
        "claimingASource": sourced,
        "claimingNoSource": len(guides) - sourced,
        "notComparedNoSignature": no_signature,
        "notComparedNoCurrent": no_current,
        "notComparedOtherRung": other_rung,
        "rule": {
            "documentableUnits": " ".join(RULE_DOCUMENTABLE),
            "undocumented": " ".join(RULE_UNDOCUMENTED),
            "orphaned": " ".join(RULE_ORPHANED),
            "stale": " ".join(RULE_STALE),
        },
        "undocumented": _sorted(undocumented),
        "orphaned": _sorted(orphaned),
        "stale": _sorted(stale),
    }


def findings(doc):
    """How many findings an audit document holds, across all three sections.

    One definition, read by the report's closing line and by the caller deciding an exit code
    under `--strict`. Two would be a gate that could fail a build over a number the report it
    printed did not show.

    Deliberately not a count of everything the report mentions: a not-compared signature, a
    duplicate source, and a guide for schema that is real but not documentable are all facts
    about the read rather than work for anyone, and a gate that failed on them would fail on
    a project with nothing to fix.
    """
    return len(doc["undocumented"]) + len(doc["orphaned"]) + len(doc["stale"])


def _sorted(items):
    """Items as `{"alias", "name"}`, in case-insensitive alias order.

    Sorted rather than left in the order they were found, because the two inputs arrive in
    unrelated orders — a project's files and a CMS's pages — and a report whose lines move
    between runs cannot be diffed.
    """
    return [{"alias": item["alias"], "name": item.get("name") or ""}
            for item in sorted(items, key=lambda i: i["alias"].lower())]


# ---------------------------------------------------------------------------
# The report
# ---------------------------------------------------------------------------



def report(doc):
    """The human report: three counted sections, and a header that says what was compared.

    **A healthy project gets a short report.** Every count prints; a section's rule and its
    items print only when it has findings. That is not brevity for its own sake — an audit
    wired into a routine is read hundreds of times and acted on a handful, so three headed
    sections of explanation reading zero would teach its reader to skip the part that carries
    the counts.
    """
    lines = []
    lines.append("Guide audit, read at the %s rung." % doc["rung"])
    lines.append("  %d documentable %s: %d component%s + %d proposed page type%s."
                 % (doc["documentableUnits"],
                    rpt.plural(doc["documentableUnits"], "unit", "units"),
                    doc["componentsRead"], "" if doc["componentsRead"] == 1 else "s",
                    doc["pageTypesProposed"],
                    "" if doc["pageTypesProposed"] == 1 else "s"))
    lines.extend("  " + line for line in RULE_DOCUMENTABLE)
    # With the determiner's rule, because it is part of that rule: the count above left a
    # palette out, and the one place a reader looks to find out how the count was reached is
    # the line that explains it. Rendered by `inventory` so the two reports cannot word one
    # exclusion two ways.
    lines.extend("  " + line for line in inventory.excluded_palette_lines(doc))
    lines.append("  %d guide %s read: %d %s a source, %d %s none."
                 % (doc["guidePagesRead"],
                    rpt.plural(doc["guidePagesRead"], "page", "pages"),
                    doc["claimingASource"],
                    rpt.plural(doc["claimingASource"], "claims", "claim"),
                    doc["claimingNoSource"],
                    rpt.plural(doc["claimingNoSource"], "claims", "claim")))
    # In the header rather than as a fourth section: nothing here is a finding, but a guide set
    # nothing was compared against would otherwise report zero stale guides and look healthy.
    # Three reasons a signature went uncompared, kept apart because they name different sides.
    # One line each rather than one crowded line: a reader deciding whether to trust the stale
    # count needs to know which side was silent, and the earlier single line said "records no
    # stored signature" for a guide that recorded one perfectly well.
    if doc["notComparedNoSignature"]:
        lines.append("  Not compared: %d %s %s no stored signature."
                     % (doc["notComparedNoSignature"],
                        rpt.plural(doc["notComparedNoSignature"], "guide", "guides"),
                        rpt.plural(doc["notComparedNoSignature"], "records", "record")))
    if doc["notComparedNoCurrent"]:
        lines.append("  Not compared: %d %s %s a source that records no signature of its own."
                     % (doc["notComparedNoCurrent"],
                        rpt.plural(doc["notComparedNoCurrent"], "guide", "guides"),
                        rpt.plural(doc["notComparedNoCurrent"], "claims", "claim")))
    if doc["notComparedOtherRung"]:
        lines.append("  Not compared: %d %s stored at another rung, or at none this read can "
                     "name."
                     % (doc["notComparedOtherRung"],
                        rpt.plural(doc["notComparedOtherRung"], "was", "were")))

    # Last in the header, and the placement is the argument. The `Not compared:` lines above
    # qualify one count; this qualifies every one of them, because it is about the source rather
    # than the comparison — so it sits closest to the sections it applies to, and a reader meets
    # it immediately before the first finding. Printed only when a rung actually has gaps, the
    # way a section's rule prints only when it has findings: at the two full-fidelity rungs
    # there is nothing to state, and a line saying so in every report is a line that gets
    # skipped along with the ones that matter.
    _structure_statement(lines, doc["rung"])

    _section(lines, CAPTION_UNDOCUMENTED, RULE_UNDOCUMENTED, doc["undocumented"])
    _section(lines, CAPTION_ORPHANED, RULE_ORPHANED, doc["orphaned"])
    _section(lines, CAPTION_STALE, RULE_STALE, doc["stale"])

    lines.append("")
    if findings(doc):
        lines.append("Findings: %d undocumented, %d orphaned, %d stale."
                     % (len(doc["undocumented"]), len(doc["orphaned"]), len(doc["stale"])))
    else:
        lines.append("Findings: none. Every documentable unit has a guide page, and every "
                     "stored source still")
        lines.append("resolves and matches.")
    return "\n".join(lines)


def _structure_statement(lines, rung):
    """The one report-level statement of what the rung this was read at cannot report.

    `gaps` is one entry per field, each already hand-wrapped into the lines a report prints —
    authored at that width rather than wrapped here, so the golden file a fixture states this
    against is hand-authorable line for line, exactly as every rule above it is.

    Read from the registry rather than from the document's own `structureGaps`, which holds the
    same statements as whole sentences for a consumer to carry. Two renderings of one entry, so
    they cannot disagree; a report that re-wrapped the sentence form would be a second wrapper
    to keep inside 88 columns.

    A hanging indent under each field, one level deeper than the prose, because these are the
    statement's items and the report has one way of showing that.
    """
    fidelity = rung_fidelity(rung)
    if fidelity == FIDELITY_FULL:
        return
    # A blank line first. Without it this sat flush against the `Not compared:` lines at the
    # same indent, and only the opening words told a reader that one qualifies a count while
    # the other qualifies the whole source. Two reviewers read it the same wrong way.
    lines.append("")
    if fidelity == FIDELITY_UNKNOWN:
        lines.append("  " + STATEMENT_UNKNOWN_RUNG[0] % (rung,))
        lines.extend("  " + line for line in STATEMENT_UNKNOWN_RUNG[1:])
        return
    gaps = rung_gap_lines(rung)
    lines.append("  " + STATEMENT_STRUCTURE[0]
                 % (len(gaps), rpt.plural(len(gaps), "field", "fields")))
    lines.extend("  " + line for line in STATEMENT_STRUCTURE[1:])
    for gap in gaps:
        lines.append("    " + gap[0])
        lines.extend("      " + line for line in gap[1:])


def _section(lines, caption, rule, items):
    """One counted section: its count always, its rule and its items only when it has some."""
    lines.append("")
    lines.append("%s: %d" % (caption, len(items)))
    if not items:
        return
    lines.extend("  " + line for line in rule)
    for item in items:
        lines.append("    %s" % rpt.item(item))


