"""The change plan — what a regeneration would do, and what it must never touch.

Every other stage answers a question about a project. This one answers a question about a
*page*: if the guide for this component were regenerated right now, which fields would change,
which would be left exactly as they are, and is there anything here worth a model call at all?

**It writes nothing, and it cannot.** The page it plans against arrives as a JSON file the
spell read from the CMS, and every write goes back through the spell after a person approves
it — because approval is a conversation, and a conversation is not a thing a script has.

## The no-op is the point

A guide page stores the signature of the source it was generated from. When that signature
still matches the source's current one, nothing about the component has changed shape, so
**there is nothing to propose and nothing to send to a model**. Saying so plainly is the whole
reason this stage exists ahead of the spell: without it, `/guide` on an unchanged component
costs a model call, every run, forever, to produce prose identical to the prose already there.
`noop` and `modelCallNeeded` are the two fields the spell reads to skip that.

A signature that cannot be compared — no stored signature, or one stored at a different rung —
is **not** a no-op. Two rungs sign one component differently by design, so an unmatched rung
says nothing about whether the source changed; the plan proposes rather than assuming, which
is the safe direction when the only cost of being wrong is a proposal nobody approves.

## The three ownership classes, and where the field set is declared

The spec names the classes; `REGISTER` below names the fields in them, and it is the one place
either is written down. `umbraco-17-guide-scaffolding` cites this table rather than restating
it, because a second copy is a second thing to be wrong about which field an editor's work
lives in.

    machine-owned    regenerated when the source signature changes, presented as a difference,
                     written only after a person approves
    seeded-once      written when the page was created and never touched again; reported when
                     it may have gone stale, never replaced
    never-touched    the page's name, address and visibility settings, the editorial levers,
                     the media a person uploaded, and every field not named above

**Ownership is a property of the page's provenance, not of a field's declaration.** This
increment plans against a page that carries a stored reference. A page carrying none has no
machine-owned fields at all — every field on it is human-owned — and that branch (the adoption
path) refuses here rather than guessing, so nothing offers to overwrite a person's prose
before the path that handles it properly exists.

## Three kinds of proposal, because "machine-owned" does not mean "this script can write it"

A machine-owned field that is stale but whose value this script cannot produce is the trap
worth naming: an absent proposal reads as "no change needed", which is the opposite of the
truth. So every machine-owned entry declares which kind of proposal it carries.

    computed    a value this script produced in full. Write it as it stands.
    content     rows this script computed, which the SPELL renders into markup. The transform
                is deterministic; the markup is the project's, and this toolkit ships none.
    owed        prose a model writes. The script says so and carries no value, rather than
                being silent about a field it knows has to change.

The property tables are `content` and not `computed` for the reason the spec gives in one
line: the tooling supplies no markup, no class names, no view conventions. The rows are the
deterministic half — the half the degradation order promises works with no model at all — and
the rendering is read from the project's own components by the spell.

## Why this stage emits a report and a document both

Same split as `inventory`, and the same reason: a person and a consumer want opposite things
from one answer. The spell wants `--json`, where `noop`, `modelCallNeeded` and each field's
current and proposed values are addressable. A person wants the diff — field, current value,
proposed value — laid out to read. Both are rendered from one document, so they cannot
disagree.

**A value is printed as the page carries it: never wrapped, never shortened.** Report prose is
hand-wrapped to 88 columns like every other report here, but a *value* is data. A value nobody
can read whole is a value nobody can approve, and a truncated diff shown for approval is worse
than no diff at all.

## What a page file may not be trusted to be

The third input produced by another process, after the guides file and the supplied inventory,
and validated the same way: field by field, refusing with a message that names the file, never
crashing with a traceback.

    the file is missing or unreadable        refused
    the file is not JSON, or is not an object  refused
    `pageVersion` is not one known here      refused, naming the version found
    no `source` key                          refused: absent is not "explicitly none"
    `source` is null                          refused for now — that is the adoption path
    `source.alias` is not the requested alias  refused: planning a page against the wrong
                                              component is how a guide gets overwritten
    no `fields` key                          refused: "the producer read no fields" and "this
                                              page has none" are opposite facts, and the second
                                              would report a page's whole content as absent
    `fields` is not an object                refused
    `fields` names the reference field too   refused: two copies of one value can disagree
    a supplied dossier declares another alias  refused, naming both
    a supplied dossier's property tree is malformed  refused, naming the tab, group or row

A field *value* is refused for nothing. A guide page's fields hold markup, block lists,
toggles and numbers, and every one of them is carried through untouched.
"""

import json
import os
import textwrap

from guidelib import GuideError
from guidelib import REFERENCE_CONSEQUENCE_PLAN
from guidelib import dossier
from guidelib import stored_reference
# Aliased, because both renderers define a function called `report` and the bare module name
# would be shadowed by it inside exactly the function that needs it.
from guidelib import report as rpt

PLAN_VERSION = 1

# The page-file shapes this module has been written against. Absence is accepted for the reason
# a serialization version's absence is: absence is not a claim to be unrecognized.
ACCEPTED_PAGE_VERSIONS = (1,)

# The label a page gets when it names itself nothing. Cosmetic — it reaches the output beside an
# alias that already identifies the page — so it is not worth refusing over.
UNNAMED_PAGE = "unnamed guide page"

MACHINE_OWNED = "machine-owned"
SEEDED_ONCE = "seeded-once"
NEVER_TOUCHED = "never-touched"

PROPOSAL_COMPUTED = "computed"
PROPOSAL_CONTENT = "content"
PROPOSAL_OWED = "owed"

# How each kind of proposal is named on a field's own line in the report. The explanation of
# what the three mean is printed once, in the section's rule, rather than repeated per field.
PROPOSAL_LABEL = {
    PROPOSAL_COMPUTED: "computed here",
    PROPOSAL_CONTENT: "content computed here, markup rendered by the spell",
    PROPOSAL_OWED: "owed by the spell, which is where the model is",
}

COMPARISON_MATCHED = "matched"
COMPARISON_DIFFERS = "differs"
COMPARISON_NOT_COMPARABLE = "notComparable"


# ---------------------------------------------------------------------------
# The register: every field the tooling can write, in exactly one class
# ---------------------------------------------------------------------------
#
# **The field names are defaults, not constants.** Each is a slot, exactly as the document type
# aliases are, because a project may already use the standard name for something unrelated and
# two properties cannot share an alias. The spell holds the slot (`conventions.md → ## Editor
# guides`), so it translates: a page file speaks the names below, and the spell maps them to
# whatever the project actually used when it reads and when it writes. That keeps one
# vocabulary in this script and no project fact in it.
#
# Matched exactly, not case-insensitively. The keys are written by the spell rather than read
# off a project, so there is no case drift to absorb — and a folded match would silently
# classify a field the register does not name as one it does.
#
# Order is the order the plan lists them, chosen so a reader meets the bookkeeping first, then
# the deterministic content, then the two fields a model owes.
#
# The stored reference is named as a constant because two places have to agree about it: it is
# the one register field whose current value does not come out of `fields`, since the page file
# states it once, structurally, as `source`.
FIELD_SOURCE = "guideSource"
FIELD_PROPERTIES = "guideProperties"

REGISTER = (
    {
        "field": FIELD_SOURCE,
        "ownership": MACHINE_OWNED,
        "proposal": PROPOSAL_COMPUTED,
        "why": "the tooling's own bookkeeping: which component this guide documents, at which "
               "signature, read at which rung. Optional on the document type like every "
               "machine-populated field, so an editor can still hand-create a guide.",
    },
    {
        "field": FIELD_PROPERTIES,
        "ownership": MACHINE_OWNED,
        "proposal": PROPOSAL_CONTENT,
        "why": "the property tables, by tab and group as the editor sees them. A deterministic "
               "transform of the dossier, which is why it needs no model — but the markup "
               "comes from the project's own components, so the spell renders these rows.",
    },
    {
        "field": "guidePurpose",
        "ownership": MACHINE_OWNED,
        "proposal": PROPOSAL_OWED,
        "why": "one sentence saying what this component is for. A script cannot write it, and "
               "a template filled from the alias reads exactly like a template.",
    },
    {
        "field": "guideWhenToUse",
        "ownership": MACHINE_OWNED,
        "proposal": PROPOSAL_OWED,
        "why": "when to reach for this component and when to reach for another. A judgment "
               "call about a project, which is the spell's half of this capability.",
    },
    {
        "field": "guideExamples",
        "ownership": SEEDED_ONCE,
        "proposal": None,
        "why": "live instances of the component, seeded at creation from the option lists. An "
               "editor arranges them; an arrangement is a person's work, so a changed variant "
               "set is reported and never re-seeded over.",
    },
    {
        "field": "guideScreenshots",
        "ownership": NEVER_TOUCHED,
        "proposal": None,
        "why": "media, and this toolkit never generates or writes media. A screenshot covers "
               "what a live example cannot — a property panel, a settings screen — and a "
               "person uploads it, always.",
    },
    {
        "field": "guideBlurb",
        "ownership": NEVER_TOUCHED,
        "proposal": None,
        "why": "the optional index blurb. Editorial by design: a lever that lives on the guide "
               "so it can never disagree with the guide it describes.",
    },
)

BY_FIELD = dict((entry["field"], entry) for entry in REGISTER)

# The reason a field the register does not name is left alone. It is the spec's own catch-all —
# page name, address, visibility settings, and everything not named above — and it is stated per
# field rather than only in the class rule so that the plan's "left alone" list can be read
# straight down without deciding which entries the rule covers.
UNREGISTERED_WHY = ("not named in this register, so no rule here would write it. The page's "
                    "own name, address and visibility settings arrive this way.")


# --- the rules, one per class -------------------------------------------------
#
# Hand-wrapped tuples, exactly as the inventory's and the audit's are, so the report prints them
# as they stand and a golden fixture is authored line for line. Joined with a single space for
# the document, which is the same two-representations-of-one-constant shape `RUNG_GAPS` uses.

RULE_MACHINE_OWNED = (
    "Regenerated when the source signature changes, shown as a difference against the",
    "current value, and written only after a person approves it. This script writes",
    "nothing.",
)
RULE_SEEDED_ONCE = (
    "Written when the page was created and never touched again. Reported when it may have",
    "gone stale, never replaced: an arrangement is a person's work, not a value to",
    "overwrite.",
)
RULE_NEVER_TOUCHED = (
    "The page's own name, address and visibility settings, the editorial levers, the media",
    "a person uploaded, and every field this register does not name.",
)

# Printed inside the machine-owned section, because it is the section it qualifies, and once
# rather than against each field.
RULE_PROPOSALS = (
    "Three kinds of proposal, named per field below:",
    "  computed here — a value produced in full; write it as it stands.",
    "  content computed here — the rows are deterministic and the markup is not, so the",
    "    spell renders them from the project's own components. This toolkit ships no",
    "    markup.",
    "  owed by the spell — prose a model writes. This script cannot propose it and says so,",
    "    because a field left silently out of a plan reads as \"no change needed\".",
)
RULE_VERBATIM = (
    "Every value is printed as the page carries it, never wrapped and never shortened: a",
    "value nobody can read whole is a value nobody can approve.",
)
# The left-alone section's own claim, and a different one from the rule above: there, values are
# printed whole so a person can approve a change to them; here, the value being byte-for-byte
# what the page holds *is* the finding.
RULE_LEFT_ALONE_EXACT = (
    "Every value below is reproduced exactly as the page carries it, which is what \"left",
    "alone\" means here: this plan proposes no write against any of them.",
)

CAPTION_MACHINE_OWNED = "Machine-owned, regenerated and proposed for approval"
CAPTION_LEFT_ALONE = "Left alone"

# --- the statements ----------------------------------------------------------

STATEMENT_MATCHED = (
    "The stored signature matches the source's current signature.",
)
STATEMENT_DIFFERS = (
    "The stored signature differs from the source's current signature: the component",
    "changed shape after this guide was generated, so every machine-owned field is",
    "regenerated below.",
)
# The one statement whose text is not fixed: the reason names the rungs involved, so it is
# wrapped at print time and every other line here stays hand-authored. It goes last, on its own
# lines, rather than interpolated mid-sentence -- a reason this long inside the first line put
# that line past 200 columns.
STATEMENT_NOT_COMPARABLE = (
    "The stored signature cannot be compared with this read, so this run cannot prove the",
    "source is unchanged: it proposes rather than assuming a no-op, and nothing is written",
    "either way. What could not be compared:",
)

STATEMENT_NOOP = (
    "No model call is needed, and no field is proposed: with the source unchanged since this",
    "guide was generated, there is nothing to regenerate and nothing for the spell to send to",
    "a model. This run is a no-op.",
)
# Both counts and both plurals are interpolated into the first line, which is why it alone can
# run past 88 -- the same shape (and the same reason) as the audit's structure statement. The
# rest sits at a width a reader can rely on.
STATEMENT_MODEL_NEEDED = (
    "A model call is needed. %d machine-owned %s prose this script cannot write, and %d",
    "%s content the spell renders in the project's own markup.",
)
# Unreachable while the register holds two owed fields and one content field, and kept anyway:
# the register is a table someone will edit, and a plan that claimed a model call over a field
# it had computed in full would send the spell to a model for nothing.
STATEMENT_NO_MODEL_NEEDED = (
    "No model call is needed: every machine-owned field below is one this script computed in",
    "full.",
)
STATEMENT_NOTHING_WRITTEN = (
    "Nothing was written. This document is a proposal: every write happens in the spell,",
    "after a person approves it.",
)

# Why a comparison could not be made, interpolated into STATEMENT_NOT_COMPARABLE. Each names
# the side that was silent, because "not comparable" alone tells an operator nothing to act on.
REASON_NO_STORED = "the page's stored reference records no signature"
REASON_NO_STORED_RUNG = ("the stored reference records no rung, and two rungs sign one "
                         "component differently by design")
REASON_OTHER_RUNG = ("the reference was stored at the '%s' rung and this read is at '%s', and "
                     "two rungs sign one component differently by design")
REASON_NO_CURRENT = "this read produced no signature of its own"


# ---------------------------------------------------------------------------
# The page file
# ---------------------------------------------------------------------------

def load_page(path, alias):
    """Read and validate the guide page the spell read from the CMS.

    Returns `{"page": label, "source": {...}, "fields": {...}}`. `alias` is the component the
    caller asked to plan for, and a page whose stored reference names a different one is
    refused: a plan is a list of writes against one page, and one built from the wrong
    component's shape would propose overwriting a guide with another guide's property table.
    """
    payload = _load_object(path, "page")

    declared = payload.get("pageVersion")
    if declared is not None and declared not in ACCEPTED_PAGE_VERSIONS:
        raise GuideError(
            "%s declares pageVersion %r, which this script has not been written against.\n"
            "  Known versions: %s. A version bump means the entry shape changed, so reading it "
            "as though it had not would classify fields silently wrong — and the classes are "
            "what decide whether a value is preserved."
            % (path, declared, ", ".join(str(v) for v in ACCEPTED_PAGE_VERSIONS)))

    name = payload.get("page")
    if name is not None and not isinstance(name, str):
        raise GuideError("%s has a non-string 'page': %r." % (path, name))
    label = (name or "").strip() or UNNAMED_PAGE

    source = stored_reference(path, label, payload,
                              consequence=REFERENCE_CONSEQUENCE_PLAN)
    if source is None:
        raise GuideError(
            "%s ('%s') carries no stored reference, and planning against a page that has none "
            "is the adoption path, which is not implemented yet.\n"
            "  A page with no stored reference has NO machine-owned fields — every field on it "
            "belongs to whoever wrote it — so a plan there is propose-only: the property tables "
            "offered as a difference, the person's prose kept, the reference written only on "
            "approval.\n"
            "  Refusing rather than planning as though the page were generated, because the "
            "difference between those two is somebody's work." % (path, label))

    if source["alias"].lower() != alias.strip().lower():
        raise GuideError(
            "%s ('%s') stores a reference to '%s', and this plan was asked for '%s'.\n"
            "  A plan is a set of writes against one page. Built from another component's "
            "shape it would propose replacing this guide's property tables with a different "
            "component's — so the two have to be the same component, matched on the alias "
            "case-insensitively." % (path, label, source["alias"], alias.strip()))

    if "fields" not in payload:
        raise GuideError(
            "%s ('%s') holds no 'fields' key.\n"
            "  A page with no values on it is written as \"fields\": {}. An absent key cannot be "
            "told from a producer that failed to read them, and the two are opposite facts: the "
            "second would report every value on the page as absent, and a plan whose \"left "
            "alone\" list is empty is a plan that says nothing needs preserving."
            % (path, label))
    fields = payload["fields"]
    if not isinstance(fields, dict):
        raise GuideError("%s ('%s') holds 'fields' as %s, not an object of field values."
                         % (path, label, type(fields).__name__))
    for key in fields:
        if not key.strip():
            raise GuideError("%s ('%s') holds a field with an empty name." % (path, label))
    if FIELD_SOURCE in fields:
        raise GuideError(
            "%s ('%s') states its stored reference twice: as 'source' and as a '%s' field.\n"
            "  It is read from 'source', which is the structured form this script compares "
            "against. Two copies of one value can disagree, and the one that would be believed "
            "is not the one a reader of the file would pick." % (path, label, FIELD_SOURCE))

    return {"page": label, "source": source, "fields": fields}


def load_dossier(path, alias):
    """Read a dossier from a file instead of extracting one from the project.

    This is the rung-3 seam, the same one `audit --inventory` opens: the running instance's
    management API belongs to the spell, which reaches it through MCP and hands the result back
    here as a dossier. Without it the change plan could only ever run against a project
    carrying an on-disk serialization, and the ladder would stop one rung short.

    `sourceSignature` is read as an **opaque string**, never recomputed. Same rule the audit
    applies to a supplied inventory's signatures, and the same reason: the signature's format
    belongs to `guidelib/dossier.py`, and a second opinion here could disagree with the first.
    """
    doc = _load_object(path, "dossier")

    declared = doc.get("dossierVersion")
    if declared is not None and declared != dossier.DOSSIER_VERSION:
        raise GuideError(
            "%s declares dossierVersion %r, and this script reads %d.\n"
            "  Re-extract it, or supply a document written by a matching version — the fields "
            "this plan reads are the ones a version bump would move."
            % (path, declared, dossier.DOSSIER_VERSION))

    for key in ("alias", "rung"):
        value = doc.get(key)
        if not isinstance(value, str) or not value.strip():
            raise GuideError("%s declares its '%s' as %r; a dossier states both its alias "
                             "and its rung as non-empty text." % (path, key, value))
    if doc["alias"].strip().lower() != alias.strip().lower():
        raise GuideError(
            "%s describes '%s', and this plan was asked for '%s'.\n"
            "  Extract the component you meant, or drop --dossier and let this read the project."
            % (path, doc["alias"].strip(), alias.strip()))

    signature = doc.get("sourceSignature")
    if signature is not None and not isinstance(signature, str):
        raise GuideError("%s has a non-string 'sourceSignature': %r." % (path, signature))

    _check_tabs(path, doc)
    return doc


def _check_tabs(path, doc):
    """Every level of a supplied dossier's property tree, checked before anything indexes it.

    The property tables are read straight out of this structure, so a tab that is a string or a
    property with no alias would surface as a raw traceback on the one path the spell uses to
    hand back a live read — which is exactly the gap two reviews of the audit's inputs found.
    """
    tabs = doc.get("tabs")
    if tabs is None:
        raise GuideError(
            "%s holds no 'tabs' key.\n"
            "  A component with no editable fields states \"tabs\": [], which is a real shape and "
            "a real answer. An absent key is a document this script cannot read a property "
            "table out of." % path)
    if not isinstance(tabs, list):
        raise GuideError("%s holds 'tabs' as %s, not an array." % (path, type(tabs).__name__))
    for index, tab in enumerate(tabs):
        where = "%s: tabs[%d]" % (path, index)
        _check_level(where, tab, "properties")
        groups = tab.get("groups")
        if groups is None:
            continue
        if not isinstance(groups, list):
            raise GuideError("%s holds 'groups' as %s, not an array."
                             % (where, type(groups).__name__))
        for g_index, group in enumerate(groups):
            _check_level("%s: groups[%d]" % (where, g_index), group, "properties")


def _check_level(where, level, key):
    """One tab or group: an object naming itself, holding properties that name themselves."""
    if not isinstance(level, dict):
        raise GuideError("%s is %s, not an object." % (where, type(level).__name__))
    name = level.get("name")
    if name is not None and not isinstance(name, str):
        raise GuideError("%s has a non-string 'name': %r." % (where, name))
    listed = level.get(key)
    if listed is None:
        return
    if not isinstance(listed, list):
        raise GuideError("%s holds '%s' as %s, not an array."
                         % (where, key, type(listed).__name__))
    for index, prop in enumerate(listed):
        spot = "%s: %s[%d]" % (where, key, index)
        if not isinstance(prop, dict):
            raise GuideError("%s is %s, not an object." % (spot, type(prop).__name__))
        alias = prop.get("alias")
        if not isinstance(alias, str) or not alias.strip():
            raise GuideError(
                "%s names no alias (has %r).\n"
                "  A property with no alias cannot be put in a property table: the alias is what"
                " an editor matches the field in front of them against." % (spot, alias))
        _check_property_fields(spot, prop)


# Every leaf a property row is built from, and the type it has to be. Checked because the first
# version validated the containers and the alias and stopped there: a `--dossier` naming
# `"editor": ["Umbraco.TextBox"]` or `"options": 5` reached the row builder and came out as a raw
# TypeError traceback rather than a refusal. `--dossier` is the seam a live management-API read
# arrives through, so its leaf shapes are exactly what this script cannot control.
PROPERTY_FIELD_TYPES = (
    ("name", str, "a string"),
    ("description", str, "a string"),
    ("editor", str, "a string"),
    ("mandatory", bool, "true or false"),
    ("sortOrder", int, "a whole number"),
    ("inheritedFrom", str, "a string"),
)


def _check_property_fields(spot, prop):
    """One property's leaf fields, typed. `None` passes everywhere: every one of these is optional
    on a dossier, and a rung that cannot report a field says so in `structureGaps` rather than by
    inventing a value."""
    for key, kind, described in PROPERTY_FIELD_TYPES:
        value = prop.get(key)
        if value is None:
            continue
        # bool is a subclass of int, so an explicit guard keeps `"sortOrder": true` from passing.
        if kind is int and isinstance(value, bool):
            raise GuideError("%s has '%s' as true/false, and it has to be %s."
                             % (spot, key, described))
        if not isinstance(value, kind):
            raise GuideError("%s has a non-%s '%s': %r." % (spot, kind.__name__, key, value))
    options = prop.get("options")
    if options is None:
        return
    if not isinstance(options, list):
        raise GuideError("%s holds 'options' as %s, not an array."
                         % (spot, type(options).__name__))
    for index, option in enumerate(options):
        if not isinstance(option, str):
            raise GuideError("%s: options[%d] is %s, not a string — an option list is a list of "
                             "the values an editor can pick."
                             % (spot, index, type(option).__name__))


def _load_object(path, what):
    """A JSON object from a file another process wrote, or a refusal naming the file.

    Both of this stage's inputs arrive the same way and are refused the same way, so the
    preamble is written once here rather than twice a few lines apart.
    """
    if not os.path.isfile(path):
        raise GuideError("no %s file at %s." % (what, os.path.abspath(path)))
    try:
        with open(path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (ValueError, OSError) as exc:
        raise GuideError("%s is not readable JSON: %s." % (path, exc))
    if not isinstance(payload, dict):
        raise GuideError("%s holds %s at the top level, not a %s document."
                         % (path, type(payload).__name__, what))
    return payload


# ---------------------------------------------------------------------------
# The plan
# ---------------------------------------------------------------------------

def run(page, dossier_doc):
    """Compute the change plan from a page and a dossier.

    Pure arithmetic over two inputs: no file is read here, and nothing anywhere is written, so
    a caller can hand this a hand-authored pair and get the document a project would produce.
    """
    stored = page["source"]["signature"]
    stored_rung = page["source"]["rung"]
    current = dossier_doc.get("sourceSignature")
    read_rung = dossier_doc["rung"].strip()

    comparison, reason = _compare(stored, stored_rung, current, read_rung)
    noop = comparison == COMPARISON_MATCHED

    statements = [_joined(_comparison_statement(comparison, reason))]

    # A no-op classifies nothing, and both lists are empty rather than full.
    #
    # That is the honest shape, not a shortcut: the "left alone" list exists to say which values
    # survived a regeneration, and there is no regeneration here for anything to survive. A
    # no-op run that listed every field on the page would read as work done, on the one path
    # whose whole value is that no work is needed.
    machine_owned, left_alone = [], []
    if not noop:
        machine_owned = _machine_owned(page, dossier_doc, current)
        left_alone = _left_alone(page)

    owed = sum(1 for e in machine_owned if e["proposal"] == PROPOSAL_OWED)
    content = sum(1 for e in machine_owned if e["proposal"] == PROPOSAL_CONTENT)
    model_needed = bool(owed or content)

    if noop:
        statements.append(_joined(STATEMENT_NOOP))
    elif model_needed:
        statements.append(_joined(_model_statement(owed, content)))
    else:
        statements.append(_joined(STATEMENT_NO_MODEL_NEEDED))
    statements.append(_joined(STATEMENT_NOTHING_WRITTEN))

    return {
        "planVersion": PLAN_VERSION,
        "alias": dossier_doc["alias"].strip(),
        "name": dossier_doc.get("name") or "",
        "page": page["page"],
        "rung": read_rung,
        "storedSignature": stored,
        "storedRung": stored_rung,
        "currentSignature": current,
        "comparison": comparison,
        "noop": noop,
        "modelCallNeeded": model_needed,
        "statements": statements,
        "rule": {
            "machineOwned": _joined(RULE_MACHINE_OWNED),
            "seededOnce": _joined(RULE_SEEDED_ONCE),
            "neverTouched": _joined(RULE_NEVER_TOUCHED),
        },
        "machineOwned": machine_owned,
        "leftAlone": left_alone,
    }


def _compare(stored, stored_rung, current, read_rung):
    """Whether the stored signature can be compared with this read's, and what it says.

    The rung test is the audit's, clause for clause, deliberately: a signature stored at
    another rung or at none recorded is not comparable, because two rungs sign one component
    differently by design. Two stages disagreeing about when a signature is comparable would
    let `audit` call a guide fresh and `plan` regenerate it in the same minute.

    **The clause ORDER is the audit's too**, which matters for the one input that trips two
    clauses at once: a stored signature with no current one to compare it against AND a rung
    that is not this read's. The audit reports that as "no current signature", so this does
    too — the verdict was always the same either way, but a reader chasing why one stage said
    one thing and the other said another has enough to chase already.

    **One limit, stated rather than guessed at.** A match is decided on the signature alone, so
    a page whose signature was stamped at creation but whose owed prose was never written reads
    as a no-op until the component's shape changes. Nothing here can tell that from a page
    somebody deliberately left short, and the field register has no notion of "required to be
    non-empty". Step 15 only runs `plan` against a page that already completed a write, so the
    shape should not arise; if it ever does, the honest fix is a seeded-at marker rather than
    guessing from emptiness.
    """
    if not stored:
        return COMPARISON_NOT_COMPARABLE, REASON_NO_STORED
    if not current:
        return COMPARISON_NOT_COMPARABLE, REASON_NO_CURRENT
    if not stored_rung:
        return COMPARISON_NOT_COMPARABLE, REASON_NO_STORED_RUNG
    if read_rung and stored_rung != read_rung:
        return COMPARISON_NOT_COMPARABLE, REASON_OTHER_RUNG % (stored_rung, read_rung)
    if stored == current:
        return COMPARISON_MATCHED, None
    return COMPARISON_DIFFERS, None


def _machine_owned(page, dossier_doc, current):
    """One entry per machine-owned field in the register, whether the page carries it or not.

    A regeneration proposes all of them: a field the page is missing entirely is exactly the
    field most in need of a value, and leaving it out of the plan because the page had nothing
    to diff against would hide it.
    """
    entries = []
    for spec in REGISTER:
        if spec["ownership"] != MACHINE_OWNED:
            continue
        # The stored reference's current value is `source`, not a `fields` entry: the page file
        # states it once, in the structured form this stage compares against.
        if spec["field"] == FIELD_SOURCE:
            present, value = True, page["source"]
        else:
            present, value = spec["field"] in page["fields"], \
                page["fields"].get(spec["field"])
        entry = {
            "field": spec["field"],
            "ownership": MACHINE_OWNED,
            "proposal": spec["proposal"],
            "why": spec["why"],
            "current": value,
            "onPage": present,
            "proposed": _proposed(spec, dossier_doc, current),
        }
        if spec["field"] == FIELD_PROPERTIES:
            # The property table is the one field compared row by row. A page storing rows gets
            # a summary; a page storing one value says so rather than offering a comparison it
            # cannot make. Both keys are present either way, so a consumer never has to guess
            # which shape it received from their absence.
            rows = value if isinstance(value, list) else None
            entry["rowChanges"] = (compare_rows(rows, proposed_rows(dossier_doc))
                                   if rows is not None else None)
            entry["rowsNotComparable"] = rows is None and present
        entries.append(entry)
    return entries


def _proposed(spec, dossier_doc, current):
    """The proposed value for one machine-owned field, or None where a model owes it.

    `None` here is never silence: the entry carries `"proposal": "owed"` beside it, and both
    renderings say in words that the value is the spell's to write.
    """
    if spec["proposal"] == PROPOSAL_OWED:
        return None
    if spec["field"] == "guideSource":
        return {
            "alias": dossier_doc["alias"].strip(),
            "kind": dossier_doc.get("kind"),
            "signature": current,
            "rung": dossier_doc["rung"].strip(),
        }
    return property_tables(dossier_doc)


def _left_alone(page):
    """Every field on the page a regeneration does not write, with the reason it does not.

    Register fields first, in register order, then everything else in alias order. The page's
    own key order is not used: it comes from a CMS read, and a plan whose lines move between
    runs cannot be diffed.
    """
    entries = []
    for spec in REGISTER:
        if spec["ownership"] == MACHINE_OWNED or spec["field"] not in page["fields"]:
            continue
        entries.append({
            "field": spec["field"],
            "ownership": spec["ownership"],
            "why": spec["why"],
            "current": page["fields"][spec["field"]],
        })
    for field in sorted(page["fields"], key=lambda f: f.lower()):
        if field in BY_FIELD:
            continue
        entries.append({
            "field": field,
            "ownership": NEVER_TOUCHED,
            "why": UNREGISTERED_WHY,
            "current": page["fields"][field],
        })
    return entries


def property_tables(dossier_doc):
    """The property tables as content: one section per tab and group, in the editor's order.

    The deterministic half of a guide page, and the half the degradation order promises works
    with no model at all. Rows carry `alias` and `name` so `report.item` names a property the
    one way this toolkit names anything.

    A section with no rows is dropped. An empty tab is a real shape — two of the demo project's
    68 document types have one — but a table of no rows documents nothing, and a heading over
    nothing in a guide an editor reads is worse than the tab's absence.

    `gaps` carries what the rung could not report, so a rendered table can mark a column it
    cannot fill rather than printing an empty one as an answer. It is the dossier's own
    `structureGaps`, unchanged.
    """
    sections = []
    for tab in dossier_doc.get("tabs") or []:
        tab_name = tab.get("name") or ""
        rows = [_row(prop) for prop in tab.get("properties") or []]
        if rows:
            sections.append({"tab": tab_name, "group": None, "rows": rows})
        for group in tab.get("groups") or []:
            rows = [_row(prop) for prop in group.get("properties") or []]
            if rows:
                sections.append({"tab": tab_name, "group": group.get("name") or "",
                                 "rows": rows})
    return {"sections": sections, "gaps": list(dossier_doc.get("structureGaps") or [])}


def _row(prop):
    """One property, as a guide's table shows it.

    `required` rather than `mandatory`: the dossier records the schema's own word, and a table
    an editor reads is not a schema. The rest is carried through as read.
    """
    return {
        "alias": prop["alias"],
        "name": prop.get("name") or "",
        "description": prop.get("description") or "",
        "editor": prop.get("editor") or "",
        "required": bool(prop.get("mandatory")),
        "options": list(prop.get("options") or []),
        "inheritedFrom": prop.get("inheritedFrom"),
    }


# What a property-table comparison can say. Keyed on the row alias, because that is the one
# thing a row and a schema property agree on: a label changes, an editor changes, a tab moves,
# and it is still the same field an editor fills in.
ROW_ADDED = "added"
ROW_REMOVED = "removed"
ROW_CHANGED = "changed"
ROW_UNCHANGED = "unchanged"

# The columns a row carries that this script owns. `information` is deliberately absent: it is
# a person's prose from the moment it is seeded, and nothing here proposes a value for it.
ROW_MACHINE_COLUMNS = ("label", "required", "tab", "group")


def compare_rows(current, proposed):
    """The property table as a set difference on the alias, not as two blocks of text.

    This is the whole reason the table is structured rather than markup in a rich-text field.
    Compared as one field, the current value is rendered markup off the page and the proposed
    value is a list of rows -- on a real page type that is roughly sixty lines of markup beside
    nineteen rows, and a person asked to approve that reads the proposed side, sees it looks
    right, and approves. The approval gate becomes theatre. Keyed on the alias it is three
    numbers and a short list, and the question "what changed" has an answer.

    `information` is never compared and never proposed. A removed row is reported rather than
    applied, because a row can only disappear if a person's writing disappears with it.
    """
    by_alias = {}
    for row in current:
        alias = row.get("alias")
        if isinstance(alias, str) and alias.strip():
            by_alias.setdefault(alias.strip().lower(), row)

    changes = []
    seen = set()
    for row in proposed:
        folded = row["alias"].strip().lower()
        seen.add(folded)
        was = by_alias.get(folded)
        if was is None:
            changes.append({"alias": row["alias"], "name": row.get("label") or "",
                            "state": ROW_ADDED, "columns": [], "hasInformation": False})
            continue
        differing = [key for key in ROW_MACHINE_COLUMNS
                     if _column(was, key) != _column(row, key)]
        changes.append({
            "alias": row["alias"],
            "name": row.get("label") or was.get("label") or "",
            "state": ROW_CHANGED if differing else ROW_UNCHANGED,
            "columns": differing,
            "hasInformation": bool(str(was.get("information") or "").strip()),
        })
    for folded, row in sorted(by_alias.items()):
        if folded in seen:
            continue
        changes.append({
            "alias": row.get("alias"),
            "name": row.get("label") or "",
            "state": ROW_REMOVED,
            "columns": [],
            # The one thing that decides whether removal is safe. A row nobody wrote in can go;
            # a row carrying a note is somebody's work and only they can say it is finished with.
            "hasInformation": bool(str(row.get("information") or "").strip()),
        })
    return changes


def _column(row, key):
    """One machine column, normalized so a missing value and an empty one compare equal --
    a page that has never carried a `group` and one carrying `""` describe the same table."""
    value = row.get(key)
    if key == "required":
        return bool(value)
    return (value or "") if isinstance(value, str) or value is None else value


def proposed_rows(dossier_doc):
    """The property table the source implies, as rows in the shape the page stores them.

    Flat, each carrying its tab and group, because the project's template does the grouping --
    so a property moving between tabs is a field change on one row rather than a row migrating
    between nested containers, which is both a smaller diff and a smaller schema.
    """
    rows = []
    for tab in dossier_doc.get("tabs") or []:
        tab_name = tab.get("name") or ""
        for prop in tab.get("properties") or []:
            rows.append(_page_row(prop, tab_name, ""))
        for group in tab.get("groups") or []:
            for prop in group.get("properties") or []:
                rows.append(_page_row(prop, tab_name, group.get("name") or ""))
    return rows


def _page_row(prop, tab, group):
    """One row, machine columns only. `information` is absent rather than empty: this script has
    no value for it, and an empty string would read as "seed it blank"."""
    return {
        "alias": prop["alias"],
        "label": prop.get("name") or "",
        "required": bool(prop.get("mandatory")),
        "tab": tab,
        "group": group,
    }


def _comparison_statement(comparison, reason):
    """What the signature comparison found, as the lines a report prints.

    `reason` is only ever read on the not-comparable path, where it names the side that was
    silent -- "not comparable" on its own tells an operator nothing they can act on.
    """
    if comparison == COMPARISON_MATCHED:
        return STATEMENT_MATCHED
    if comparison == COMPARISON_DIFFERS:
        return STATEMENT_DIFFERS
    # Joined back into one sentence for the document by the caller, which is why the wrapped
    # lines carry no indentation of their own.
    return STATEMENT_NOT_COMPARABLE + tuple(
        textwrap.wrap("%s." % reason, rpt.WRAP_WIDTH) or ["%s." % reason])


def _model_statement(owed, content):
    return (STATEMENT_MODEL_NEEDED[0]
            % (owed, rpt.plural(owed, "field needs", "fields need"), content),
            STATEMENT_MODEL_NEEDED[1]
            % (rpt.plural(content, "carries", "carry"),)) + STATEMENT_MODEL_NEEDED[2:]


def _joined(lines):
    """Hand-wrapped report lines as one sentence, for the document to carry.

    Two representations of one constant, neither derived from the other's text: the lines are
    authored at the width a report prints them, and joined with a single space here. The same
    shape `RUNG_GAPS` uses, and the golden fixtures state the joined form, so the joining is
    guarded rather than assumed.
    """
    return " ".join(lines)


# ---------------------------------------------------------------------------
# The report
# ---------------------------------------------------------------------------

def report(doc):
    """The human rendering: the header, the statement, and the diff.

    **A no-op gets a short report.** Counts always print; a section's rule and its fields print
    only when it has any, exactly as the audit's sections do. A run whose whole finding is
    "nothing to do" should not cost its reader three headed sections of explanation to discover
    that, or they will skip the part that carries the counts next time too.
    """
    lines = []
    lines.append("Change plan for %s, read at the %s rung."
                 % (rpt.item({"alias": doc["alias"], "name": doc["name"]}), doc["rung"]))
    lines.append("  Guide page: %s" % doc["page"])
    lines.append("  Stored signature: %s, %s"
                 % (doc["storedSignature"] or "none recorded",
                    "recorded at the %s rung." % doc["storedRung"] if doc["storedRung"]
                    else "at no rung the reference records."))
    lines.append("  Current signature: %s" % (doc["currentSignature"] or "none"))
    lines.extend("  " + line for line in _statement_lines(doc, 0))

    # The headline the spell reads before deciding whether to spend a model call, so it sits at
    # the left margin with a blank line around it rather than inside the header block.
    lines.append("")
    lines.extend(_statement_lines(doc, 1))

    lines.append("")
    lines.append("%s: %d" % (CAPTION_MACHINE_OWNED, len(doc["machineOwned"])))
    if doc["machineOwned"]:
        lines.extend("  " + line for line in RULE_MACHINE_OWNED)
        lines.extend("  " + line for line in RULE_PROPOSALS)
        lines.extend("  " + line for line in RULE_VERBATIM)
        for entry in doc["machineOwned"]:
            lines.append("    %s: %s" % (entry["field"], PROPOSAL_LABEL[entry["proposal"]]))
            # A property table is reported as what changed, never as two blocks of text set
            # against each other. The caster wants "these properties were added, these were
            # removed"; both sides printed in full is what turned approval into theatre.
            if entry.get("rowChanges") is not None:
                lines.append("      changes:")
                lines.extend(row_summary_lines(entry["rowChanges"], "        "))
                continue
            if entry.get("rowsNotComparable"):
                lines.append("      changes:")
                lines.extend("        " + line for line in ROWS_NOT_COMPARABLE)
                continue
            lines.append("      current:")
            lines.extend(_side_lines(entry, entry["current"], entry["onPage"], "        "))
            lines.append("      proposed:")
            if entry["proposal"] == PROPOSAL_OWED:
                lines.append("        (none here — a model writes this one, in the spell)")
            else:
                lines.extend(_side_lines(entry, entry["proposed"], True, "        "))

    lines.append("")
    lines.append("%s: %d" % (CAPTION_LEFT_ALONE, len(doc["leftAlone"])))
    if doc["leftAlone"]:
        _class_rules(lines, doc["leftAlone"])
        lines.extend("  " + line for line in RULE_LEFT_ALONE_EXACT)
        # The field, its class, and its value. The per-field reason is carried in the document
        # rather than printed: four wrapped explanations under a list of four values is a list
        # nobody reads down, and the spell — which is what says "left alone, because …" to a
        # person — reads `why` out of `--json`.
        for entry in doc["leftAlone"]:
            lines.append("    %s (%s)" % (entry["field"], entry["ownership"]))
            lines.extend(_value_lines(entry["current"], True, "      "))

    lines.append("")
    lines.extend(_statement_lines(doc, 2))
    return "\n".join(lines)


def _statement_lines(doc, index):
    """One of the document's statements, back at the width it was authored for.

    Read from the module's own constants rather than re-wrapped from the joined sentence the
    document carries: a second wrapper is a second thing to keep inside 88 columns, and the
    constants are already there.
    """
    if index == 0:
        return _comparison_statement(doc["comparison"], _reason(doc))
    if index == 1:
        if doc["noop"]:
            return STATEMENT_NOOP
        if doc["modelCallNeeded"]:
            owed = sum(1 for e in doc["machineOwned"] if e["proposal"] == PROPOSAL_OWED)
            content = sum(1 for e in doc["machineOwned"]
                          if e["proposal"] == PROPOSAL_CONTENT)
            return _model_statement(owed, content)
        return STATEMENT_NO_MODEL_NEEDED
    return STATEMENT_NOTHING_WRITTEN


def _reason(doc):
    """The not-comparable reason, recovered from the document rather than stored twice."""
    if doc["comparison"] != COMPARISON_NOT_COMPARABLE:
        return None
    if not doc["storedSignature"]:
        return REASON_NO_STORED
    if not doc["storedRung"]:
        return REASON_NO_STORED_RUNG
    if doc["storedRung"] != doc["rung"]:
        return REASON_OTHER_RUNG % (doc["storedRung"], doc["rung"])
    return REASON_NO_CURRENT


def _class_rules(lines, entries):
    """The rule for each ownership class present in the left-alone list, and no others.

    A page with no seeded example should not be told what seeding means. Same discipline as an
    empty section printing no rule: an explanation with nothing under it teaches its reader to
    skip explanations.
    """
    present = set(entry["ownership"] for entry in entries)
    if SEEDED_ONCE in present:
        lines.extend("  " + line for line in RULE_SEEDED_ONCE)
    if NEVER_TOUCHED in present:
        lines.extend("  " + line for line in RULE_NEVER_TOUCHED)


def _value_lines(value, on_page, indent):
    """A field's value, printed as it stands.

    Never wrapped and never shortened, for the reason `RULE_VERBATIM` states. Multi-line values
    are indented line by line, which is presentation rather than content: the value itself is
    carried through the document untouched, and `--json` is where a consumer reads it.

    A field the page does not carry says so in words. Blank would be indistinguishable from a
    field carrying an empty string, and those are different: one has nothing yet, the other was
    emptied by somebody.
    """
    if not on_page:
        return ["%s(the page carries no value for this field)" % indent]
    if value is None:
        return ["%s(null)" % indent]
    if not isinstance(value, str):
        # A page field can hold a toggle, a number, or a block list. Rendered as JSON, which is
        # what it was in the file, rather than as Python's repr of it.
        return ["%s%s" % (indent, json.dumps(value))]
    if value == "":
        return ["%s(empty)" % indent]
    return ["%s%s" % (indent, line) for line in value.split("\n")]


def _side_lines(entry, value, on_page, indent):
    """One side of one field's difference, rendered the way that field's value reads.

    Dispatched on the field and its proposal kind rather than by sniffing the value's shape, so
    the two sides of a difference are always rendered the same way as each other — a current
    value shown as a table beside a proposed one shown as JSON is not a difference anybody can
    read.
    """
    if not on_page:
        return ["%s(the page carries no value for this field)" % indent]
    if entry["field"] == FIELD_SOURCE:
        return _reference_lines(value, indent)
    if entry["proposal"] == PROPOSAL_CONTENT and isinstance(value, dict):
        return _table_lines(value, indent)
    return _value_lines(value, on_page, indent)


# What the report prints for a property table whose two sides cannot be set against each other:
# the page stores rendered markup and the source implies rows. Said rather than shown, because
# printing both is what made a person diff markup against a row list by eye.
ROWS_NOT_COMPARABLE = (
    "This page stores its property table as one value rather than as rows, so the two sides",
    "cannot be compared field by field and no summary of what changed is available here.",
    "The spell renders the table from the project's own components; a page rebuilt with a",
    "property row list gets an added/removed/changed summary instead of this note.",
)

ROW_STATE_ORDER = (ROW_ADDED, ROW_REMOVED, ROW_CHANGED)

ROW_STATE_WORDS = {
    ROW_ADDED: "added",
    ROW_REMOVED: "removed",
    ROW_CHANGED: "changed",
}


def row_summary_lines(changes, indent):
    """The property table's changes, one line each, in the order they matter to a reader.

    Added first because it is the common case; removed second because it is the one that can
    cost somebody their writing; changed third. Unchanged rows are counted, never listed -- a
    list of what did not happen is the part nobody reads.
    """
    lines = []
    for state in ROW_STATE_ORDER:
        for change in changes:
            if change["state"] != state:
                continue
            line = "%s%-9s %s" % (indent, ROW_STATE_WORDS[state], rpt.item(change))
            if change["state"] == ROW_CHANGED and change["columns"]:
                line += " — %s" % ", ".join(change["columns"])
            lines.append(line)
            # On its own line rather than appended: an alias and a label are free text of any
            # length, so a fixed caveat tacked on the end is the one part of this line whose
            # width nobody controls.
            if change["state"] == ROW_REMOVED and change["hasInformation"]:
                lines.append("%s  carries an information note — removal needs your approval"
                             % indent)
    unchanged = sum(1 for c in changes if c["state"] == ROW_UNCHANGED)
    if unchanged:
        lines.append("%s%d %s unchanged, information notes untouched"
                     % (indent, unchanged, rpt.plural(unchanged, "row", "rows")))
    if not lines:
        lines.append("%s(the table matches the source; no row changes)" % indent)
    return lines


def _reference_lines(reference, indent):
    """A stored reference, one field per line.

    Rather than inline, so a reader comparing the current reference with the proposed one is
    comparing four short lines instead of two long ones — and so the only line on either side
    that a fixture cannot author, the signature, is the only line a fixture has to mask.
    """
    return ["%s%s: %s" % (indent, key,
                          reference.get(key) if reference.get(key) is not None else "none")
            for key in ("alias", "kind", "signature", "rung")]


def _table_lines(content, indent):
    """The property tables, as a person reads them: a heading per section, a line per property.

    Not markup. The rows are what this script owns; the markup is the project's, and the spell
    renders it — so what is printed here is the content being approved, in the plainest shape
    that keeps a column from being lost.
    """
    lines = []
    if not content["sections"]:
        lines.append("%s(no editable properties — the component declares none)" % indent)
    for section in content["sections"]:
        heading = section["tab"] or "(no tab)"
        if section["group"]:
            heading = "%s / %s" % (heading, section["group"])
        lines.append("%s[%s]" % (indent, heading))
        for row in section["rows"]:
            detail = [row["editor"] or "unknown editor",
                      "required" if row["required"] else "optional"]
            if row["options"]:
                detail.append("options: %s" % " | ".join(row["options"]))
            if row["inheritedFrom"]:
                detail.append("inherited from %s" % row["inheritedFrom"])
            lines.append("%s  %s: %s" % (indent, rpt.item(row), ", ".join(detail)))
    if content["gaps"]:
        lines.append("%s(%d %s this rung cannot report; each is named in --json)"
                     % (indent, len(content["gaps"]),
                        rpt.plural(len(content["gaps"]), "field", "fields")))
    return lines
