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

**Ownership is a property of the page's provenance, not of a field's declaration.** The three
classes above describe a page that carries a stored reference. A page carrying none has no
machine-owned fields at all — every field on it is human-owned, whichever class the register
puts it in — and the register is read for *what a field is for*, never for permission to write
it. Ownership declared per field cannot describe both kinds of page on one document type,
which is the whole reason it is declared per page here.

## The adoption path: a page nobody generated

A guide page with `"source": null` was written by a person, in the backoffice, about a
component this tooling can also read. One document type serves both, so there is nothing on
the page itself to distinguish "generated and now stale" from "somebody's work" — only the
absent reference. So a plan against it is **propose-only**, and every part of that word is
load bearing:

    the property table    offered as a difference. A hand-written page carries no rows, so
                          every row is `added` — which is the honest answer, not a special
                          case: the table does not exist yet.
    the person's prose    kept, listed with its value reproduced exactly, and nothing is
                          offered in its place. No prose is proposed on this path at all.
    the stored reference  **pending approval**, never proposed. Writing it is what makes
                          this page's machine-owned fields machine-owned from then on, so it
                          is the one value on the page whose write changes every later run.

`provenance` and `proposeOnly` say this in the document, and `comparison` carries a fourth
value, `noReference`, so a consumer never has to infer propose-only from something's absence.
The offered entries carry `proposedOnApproval` rather than `proposed`, and `machineOwned` is
present and **empty** — a positive claim that this page has no machine-owned fields, not an
omission. A consumer walking `machineOwned` for things to write therefore finds nothing to
write, which is the property that has to hold whatever else changes here. It is also
why `planVersion` does not move: no key a consumer already reads means anything new.

**There is no signature to compare, so no adoption run can ever be a no-op.** `noop` is false
on this path always, and `storedSignature` and `storedRung` are null: the comparison did not
fail, there was nothing on the page to compare against. Every run against a hand-written page
is a proposal, and the report says so rather than leaving it to be worked out.

**An absent `source` key still refuses**, and that distinction is not cosmetic: `null` is a
fact about the CMS ("this page claims no source") and an absent key is a fact about the
producer ("the spell did not read one"). Collapsing them would adopt a page that should have
been regenerated. `guidelib.stored_reference` holds that rule for both stages that read a
reference.

## Three kinds of proposal, because "machine-owned" does not mean "this script can write it"

A machine-owned field that is stale but whose value this script cannot produce is the trap
worth naming: an absent proposal reads as "no change needed", which is the opposite of the
truth. So every machine-owned entry declares which kind of proposal it carries.

    computed    a value this script produced in full. Write it as it stands.
    content     rows this script computed, which the SPELL renders into markup. The transform
                is deterministic; the markup is the project's, and this toolkit ships none.
    owed        prose a model writes. The script says so and carries no value, rather than
                being silent about a field it knows has to change.

**No register entry is `owed` today, and the kind is still declared.** Every prose field on a
guide page is seeded once when the page is created — the purpose sentence and the when-to-use
section both — so nothing left in the machine-owned class needs words. What a plan still needs
a model for is the property table's markup, and `STATEMENT_MODEL_NEEDED_NO_PROSE` is the
sentence that says so instead of printing a nought.

The property tables are `content` and not `computed` for the reason the spec gives in one
line: the tooling supplies no markup, no class names, no view conventions. The rows are the
deterministic half — the half the degradation order promises works with no model at all — and
the rendering is read from the project's own components by the spell.

## The live examples: a set derived, never invented

A guide page carries live instances of the component it documents, and `seeding` says which
ones. The set comes out of the source: where exactly one property carries an option list, that
list IS the variant set and there is one instance per option. Where the variations are
combinations instead — several option lists, or independent toggles — the set is a product
rather than a list, so **one** instance is seeded and the plan says in words that curating the
rest is a person's job. `BASIS_ENUMERATED` holds the four answers and the reasoning behind
each; the rule that picked one is printed beside the number it produced, which is the
convention `inventory` set for its determiner and for the same reason.

Two things this stage refuses to do, and both refusals are the point:

    it does not choose the variant property  Which property carries "the" variation is
                                             recorded nowhere. Several option lists are
                                             named as candidates and the set stays
                                             combinatorial.
    it does not supply a default             There is no recorded default for an option list
                                             (measured on two real projects) and nowhere in a
                                             dossier for a toggle's. So a seed with no
                                             variant sets NOTHING, the CMS applies its own
                                             defaults, and the plan says so — a plan implying
                                             this script picked the values would be worse
                                             than the gap it is covering for.

**Every seed is seeded-once**, which is what makes the reporting half of this the whole point.
On a page already carrying an arrangement nothing is seeded and nothing is proposed: the
derived set is printed to be read beside what is on the page, and where the stored signature no
longer matches, the plan says the variant set may have changed with it. It never says which
variants the arrangement holds — an arrangement is markup or a block list, and reading one is
not something this script can do.

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
    `source` is null                          read as a hand-written page: the adoption path
    `source.alias` is not the requested alias  refused: planning a page against the wrong
                                              component is how a guide gets overwritten
                                              (there is no alias to check on the adoption
                                              path — the caller named the component, and the
                                              page claims none)
    no `fields` key                          refused: "the producer read no fields" and "this
                                              page has none" are opposite facts, and the second
                                              would report a page's whole content as absent
    `fields` is not an object                refused
    `fields` names the reference field too   refused: two copies of one value can disagree
    `structureAvailable` is not a boolean    refused: it is what says whether the option
                                             lists were read in full, and the seed set is
                                             derived from those lists
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
# The fourth class, and the only one a page's provenance can put every field in at once. It is
# not a register entry and never will be: no field is declared human-owned, a *page* is.
HUMAN_OWNED = "human-owned"

# Which kind of page a plan was computed against, said in the document rather than left to be
# inferred from a null signature. Only the adoption document carries the key: a regeneration
# plan's shape is unchanged by this path, and `comparison` already tells the two apart on every
# plan either way, so there is no second value to declare here and none is invented.
PROVENANCE_HAND_WRITTEN = "hand-written"

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
# The fourth value, and the marker that tells an adoption plan from a regeneration plan. A
# distinct value rather than `notComparable`: that one means "two signatures could not be set
# against each other", and here there was never a second signature to try. The difference is
# the difference between a stale page and somebody's own writing.
COMPARISON_NO_REFERENCE = "noReference"


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
# the deterministic content, then the prose in the order a guide page displays it, then the
# fields nothing here rewrites. No entry names a field a model owes: every prose field on a
# guide page is seeded once, which is what `STATEMENT_MODEL_NEEDED_NO_PROSE` reports.
# Grouped by class rather than by subject, because the plan prints the machine-owned fields and
# the left-alone ones in two separate sections and each reads down in this order.
#
# The stored reference is named as a constant because two places have to agree about it: it is
# the one register field whose current value does not come out of `fields`, since the page file
# states it once, structurally, as `source`.
FIELD_SOURCE = "guideSource"
FIELD_PROPERTIES = "guideProperties"
# Named for the same reason, one line further on: the seed derivation below and the register
# both speak about this one field, and two spellings of it would let a plan seed instances
# into a field the register classifies under the other name.
FIELD_EXAMPLES = "guideExamples"

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
        "ownership": SEEDED_ONCE,
        "proposal": None,
        "why": "one sentence saying what this component is for, written when the page is "
               "created. A script cannot write it and a model only drafts it: the sentence an "
               "editor reads first is the one they rewrite in their own words, and words "
               "somebody chose are not a value to regenerate over.",
    },
    {
        "field": "guideWhenToUse",
        "ownership": SEEDED_ONCE,
        "proposal": None,
        "why": "when to reach for this component and when to reach for another, written when "
               "the page is created. A judgment call about a project, so a model drafts it and "
               "an editor rewrites it for the editors they know — and a rewrite is not a value "
               "to regenerate over, which is the whole of why the prose on a guide page is "
               "seeded rather than machine-owned.",
    },
    {
        "field": FIELD_EXAMPLES,
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

# The reason a field is kept on the adoption path, and it is the same reason for every field
# there — which is exactly why it is one constant and not the register's per-field `why`. On a
# page with no stored reference the register does not decide anything: provenance does, and a
# consumer reading a per-field explanation there would be reading the wrong rule.
KEPT_WHY = ("kept exactly as it stands. This page carries no stored reference, so this value "
            "is somebody's writing rather than something the tooling generated, and nothing "
            "in this plan proposes a write against it.")

# What the stored reference's consequence is, carried on its entry so a consumer that renders
# one field at a time still says it. The one value on the page whose write changes what every
# later run is allowed to do.
#
# **One constant for both paths, not one worded per path.** An adoption offers this reference on
# a page somebody wrote by hand; a creation proposes it on a page that does not exist yet. The
# fact is the same fact either way -- after the write, every later run compares this signature
# and regenerates the machine-owned columns -- and it is the one approval on a guide page that
# editing cannot undo. A second constant would be a second wording of that, which is precisely
# the drift a canonical text exists to stop: the spell cites this rather than paraphrasing it,
# and cannot then paraphrase it differently on one path than on the other.
#
# So the path-specific clause came OUT of it. It read "Pending approval, never proposed, and
# never written here", which is true of an adoption's entry and false of a creation's -- that
# one is keyed `proposed`, like every other machine-owned field on a regeneration, and a
# sentence saying "never proposed" under a key called `proposed` teaches its reader to stop
# trusting the sentence. What replaced it holds on both paths. Nothing was lost: "pending, not
# proposed" is what an adoption entry's own `pendingApproval` and `proposedOnApproval` keys say
# structurally, and what `RULE_OFFERED` says in words to the person reading the report.
REFERENCE_WRITE_CONSEQUENCE = (
    "writing this reference is what makes this page's machine-owned fields machine-owned from "
    "that point on: every later run compares its signature and regenerates them. Nothing here "
    "writes it, and no later edit takes that consequence back — the field itself can be changed "
    "like any other, but the page has been a generated page since the moment it was approved. "
    "Every other yes on a guide page is undone by a person changing a field back.")


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
# Class-generic deliberately. This rule is the ONLY explanation a person reading the report
# gets -- the per-field `why` is carried in the document and not printed (see the comment in the
# renderer) -- so it has to describe every member. It named "an arrangement" while the class held
# only the live-example field, and went wrong the moment a sentence of prose joined it.
RULE_SEEDED_ONCE = (
    "Written when the page was created and never touched again. Reported when it may have",
    "gone stale, never replaced: what somebody wrote is their work, not a value to",
    "overwrite.",
)
# The third answer this list needs and neither rule above gives. A seeded field the page does
# not carry is not "left alone" -- there is no value to leave -- and it is not proposed, because
# a seeded value's only write is at page creation and a plan run creates nothing.
#
# `_machine_owned` reaches the opposite conclusion from the same premise, and that is the point:
# it proposes a machine-owned field the page is missing, on the grounds that a missing field is
# exactly the field most in need of a value. The reasoning carries here and only the remedy
# differs -- a machine-owned field can be proposed and a seeded one cannot -- so what is owed is
# a report rather than a proposal.
RULE_UNWRITTEN = (
    "Written when a page is created and never again, so a run against a page that already",
    "exists has no occasion to write it: this is reported and proposed nowhere. The page was",
    "created without it, and it stays empty until a person writes one.",
)
RULE_NEVER_TOUCHED = (
    "The page's own name, address and visibility settings, the editorial levers, the media",
    "a person uploaded, and every field this register does not name.",
)
# The adoption path's two rules. They replace the three above rather than joining them, and the
# report prints them instead: on a page nobody generated there is no machine-owned section to
# qualify, and printing the seeded-once rule beside a field nothing will ever seed would teach
# its reader that the rules here do not mean what they say.
RULE_HUMAN_OWNED = (
    "Every field on this page is human-owned. With no stored reference nothing here was",
    "generated, so nothing here is the tooling's to replace: the three ownership classes",
    "describe a page that carries a reference, and this page carries none.",
)
RULE_OFFERED = (
    "Offered, not written. Each value below is a difference for a person to accept or",
    "refuse, and this script has written nothing either way. The stored reference is the",
    "one to read twice: writing it is what makes this page's machine-owned fields",
    "machine-owned from that point on, so it is pending your approval rather than",
    "proposed. No prose is offered — the words on this page are somebody's.",
)

# Printed inside the machine-owned section, because it is the section it qualifies, and once
# rather than against each field.
#
# **Split per kind, and only the kinds present are printed.** `_class_rules` already applies
# this discipline to the ownership classes, for the reason written there: an explanation with
# nothing under it teaches its reader to skip explanations. It was not applied here, and the
# moment the register held no `owed` field the section explained a kind of proposal no field
# below it could carry — a bullet about prose a model writes, printed on a plan that proposes no
# prose at all. The caption counts what it is about to explain, so a reader can see the list is
# a selection rather than a fixed three.
CAPTION_PROPOSALS = "%s of proposal, named per field below:"
RULE_PROPOSAL_KIND = {
    PROPOSAL_COMPUTED: (
        "  computed here — a value produced in full; write it as it stands.",
    ),
    PROPOSAL_CONTENT: (
        "  content computed here — the rows are deterministic and the markup is not, so the",
        "    spell renders them from the project's own components. This toolkit ships no",
        "    markup.",
    ),
    PROPOSAL_OWED: (
        "  owed by the spell — prose a model writes. This script cannot propose it and says so,",
        "    because a field left silently out of a plan reads as \"no change needed\".",
    ),
}
# The order the kinds are explained in, which is the register's own order rather than the
# dictionary's: a reader meets the explanations in the order the fields below them appear.
PROPOSAL_ORDER = (PROPOSAL_COMPUTED, PROPOSAL_CONTENT, PROPOSAL_OWED)
# One phrase per possible number of kinds. A spelled number reads better than a digit mid-
# sentence, and the set of kinds is closed at three, so the list is exhaustive by construction:
# the caller selects from `PROPOSAL_ORDER` and returns early on none, which leaves 1, 2 or 3.
PROPOSAL_COUNT_PHRASE = ("", "One kind", "Two kinds", "Three kinds")
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
# The same claim on the adoption path, and one clause further: there, a field left alone had a
# proposal made for its machine-owned neighbours; here nothing is offered in its place at all.
RULE_KEPT = (
    "Every value below is reproduced exactly as the page carries it, and this plan",
    "proposes no write against any of them. Nothing is offered in their place: a page",
    "with no stored reference was written by a person, and their words are not a value",
    "to regenerate.",
)

CAPTION_MACHINE_OWNED = "Machine-owned, regenerated and proposed for approval"
# Printed above the stored reference's consequence, on the one shape that carries it. The label
# is the finding rather than a heading: a reader skimming a list of fields needs to know which
# line is the one they cannot take back.
CAPTION_CONSEQUENCE = "not reversible by editing —"
CAPTION_LEFT_ALONE = "Left alone"
# Printed only when a page is missing a seeded field, which is a state a report must not answer
# with silence: nothing proposes it and nothing lists it, so a reader of an otherwise complete
# plan would take an empty field for a finished one.
CAPTION_UNWRITTEN = "Seeded once, and never written on this page"
# Two captions the adoption path needs and the regeneration path has no use for. "Offered" and
# "pending your approval" are both in the first deliberately: a caption is what a reader skims,
# and "proposed" is the word this section must never be summarized with.
CAPTION_OFFERED = "Offered as a difference, pending your approval"
CAPTION_KEPT = "Kept exactly as it stands, every field human-owned"

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

STATEMENT_NO_REFERENCE = (
    "This page carries no stored reference, so nothing on it was generated: it has NO",
    "machine-owned fields, and every field on it belongs to whoever wrote it. There is no",
    "stored signature to compare either, so no run against this page can be a no-op — every",
    "one of them is a proposal.",
)
# The adoption path's headline, in the slot the model-call statement occupies on a regeneration
# plan. It states what a consumer is holding before it reads a single field, because this is the
# document whose whole risk is being read as though it were the other one.
STATEMENT_ADOPTION = (
    "Nothing here is a write. The property table is offered as a difference, and the stored",
    "reference is pending your approval — approving it is what makes this page's",
    "machine-owned fields machine-owned from that point on. Every word already on the page",
    "is kept exactly as it stands.",
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
# The form the register actually lands on, and the reason there are two forms rather than one
# sentence with a nought in it.
#
# **The count stays in the arithmetic; the wording gets a second form.** With no owed field in
# the register, the sentence above renders "0 machine-owned fields need prose this script
# cannot write, and 1 carries content" -- true, and it reads as a bug in the tool, which is the
# one thing a report whose whole job is to be believed cannot afford. The other way out was to
# drop `owed` from the arithmetic and count content alone. That is rejected for the reason
# `STATEMENT_NO_MODEL_NEEDED` below is kept unreachable: the register is a table someone will
# edit, and a class it can be edited back into needs the count that reports it. Deleting the
# count makes the next field that owes prose an arithmetic change instead of a register entry,
# which is exactly the coupling the register exists to avoid.
#
# So the nought is not printed and the fact behind it is: a model is needed here, and not for
# words. Every prose field on a guide page is seeded once when the page is created and left
# alone from then on, so what is left for a model is the property table's markup -- which comes
# from the project's own components, and is why that field is `content` and not `computed`.
# Saying so is worth the second constant: "a model call is needed" with no prose owed invites
# the reader to go looking for the prose it is needed for.
# **"Left alone" is not available to this sentence**, and that is a rule rather than a word
# choice. The left-alone section means a field whose value is on the page and stays there; a
# seeded field the page never got is reported in a section of its own for exactly that reason
# (see `RULE_UNWRITTEN`). This sentence prints above both, on a page that may carry either, so
# it can state the policy and must not describe a value: the first wording said "every prose
# field is written once when the page is created and left alone" fifty lines above a section
# naming a prose field never written at all.
STATEMENT_MODEL_NEEDED_NO_PROSE = (
    "A model call is needed, and not for prose. %d machine-owned %s content the",
    "spell renders in the project's own markup. No prose on a guide page is regenerated at",
    "all: a prose field is written once, when the page is created, and this script never",
    "rewrites one afterwards — so whether each one carries words yet is reported below.",
)
# The mirror of the form above, and unreachable for the mirror reason: no register entry can
# leave `content` nought while something still owes prose. Written anyway, because "unreachable
# today" is a fact about the register rather than about this function, and the register is a
# table someone will edit -- which is the argument the form above already makes for keeping the
# count. A guard on one direction and a nought on the other would be the same defect twice.
STATEMENT_MODEL_NEEDED_NO_CONTENT = (
    "A model call is needed, and only for prose. %d machine-owned %s words this script",
    "cannot write. Nothing here needs the project's own markup: every value below this",
    "script produced in full.",
)
# Unreachable while the register holds a content field -- the property table's, which every
# plan that is not a no-op proposes -- and kept anyway: the register is a table someone will
# edit, and a plan that claimed a model call over a field it had computed in full would send
# the spell to a model for nothing. The owed field this comment used to name is gone, and its
# absence does not reach here: `model_needed` is true on the strength of either count.
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
# Live examples: the seed set, derived from the source's own variation axis
# ---------------------------------------------------------------------------
#
# A guide page carries live instances of the component it documents, and the set of them comes
# out of the source rather than out of a judgment made here. Four answers, and the rule that
# picked between them is printed beside the number it produced -- the same convention
# `inventory` follows with its determiner, and for the same reason: a wrong rule has to be
# visible next to its count or nobody can tell it is wrong.
#
#   enumerated       exactly one property carries an option list, so that list IS the variant
#                    set. One instance per option, nothing else on the instance set.
#   combinatorial    several option lists, or independent toggles: the set is a product, not a
#                    list, and which combinations are worth showing is a person's judgment.
#                    One instance, and the plan says the curating is somebody's job.
#   unvaried         no option list and no toggle: the source records no variation at all, so
#                    there is one instance of the component itself and nothing to enumerate.
#   notDerivable     the dossier does not report its option lists in full. `"options": []`
#                    cannot be told from a component with no choices, so one instance reported
#                    as the whole set would be a guess dressed as an answer.
#
# **Where several properties carry option lists, this script does not pick one.** Which
# property is "the variant property" is recorded nowhere -- not in either serialization format,
# not in a dossier -- and a `style` list beside a `size` list is a product either way. So the
# lists are named in the output as candidates and the set is left combinatorial, which is this
# codebase's standing preference: say what cannot be decided rather than deciding it quietly.
#
# **"One instance at the default values" cannot mean values this script supplies.** Step 6
# measured two real projects and found no dropdown carrying a default, which is why an option
# is a plain string in a dossier with no marker among them; a toggle's default is a real value
# with nowhere in the dossier to hold it, recorded in `guidelib/dossier.py` as a known gap. So
# a seed with no variant sets NOTHING, the CMS applies its own defaults, and the plan says so
# in those words. A plan implying this script chose the values would be worse than the gap.
#
# **Every seed is seeded-once**, which is what makes the reporting half of this the point. On a
# page that already carries an arrangement nothing is seeded and nothing is proposed: the
# derived set is printed to be read beside what is on the page, and where the stored signature
# no longer matches, the plan says the variant set may have changed with it. It never says
# which variants the arrangement holds -- an arrangement is markup or a block list, and reading
# one is not something this script can do or should claim to.

BASIS_ENUMERATED = "enumerated"
BASIS_COMBINATORIAL = "combinatorial"
BASIS_UNVARIED = "unvaried"
BASIS_NOT_DERIVABLE = "notDerivable"

# What the plan would do with the set, said as a value rather than left to be inferred from
# whether the page carries examples. `reportOnly` is the arrangement-preserving answer.
SEED_CREATE = "create"
SEED_REPORT_ONLY = "reportOnly"

# The editors whose values are a pair rather than a list. The alias is the CMS's own, not a
# project's, so naming it here is not a project fact leaking into the script -- and it is the
# one editor two measured projects recorded a `default` on, which is exactly why a toggle's
# variations are the combinatorial case rather than the enumerable one.
#
# Folded before matching: a dossier can arrive through `--dossier` from the live rung, whose
# spelling of an editor alias is not something this script controls.
TOGGLE_EDITORS = ("umbraco.truefalse",)

CAPTION_SEEDS = "Live examples the source's variant set implies"
# Printed where the count goes when there is no set to count. Not `0`: a nought under this
# caption reads as "this component needs no live examples", which is the one thing a dossier
# that cannot report its option lists is unable to say.
SEEDS_NOT_DERIVABLE = "not derivable from this dossier"

RULE_SEEDING = (
    "Seeded once, when the page is created, and never re-seeded: an editor arranges these",
    "instances, and an arrangement is a person's work rather than a value to overwrite. The",
    "set is derived from the source's own variation axis, and the rule that derived it is",
    "printed with it — a wrong rule has to be visible beside the number it produced.",
)

RULE_BASIS = {
    BASIS_ENUMERATED: (
        "Exactly one property on this component carries an option list, so that list IS the",
        "variant set: one instance per option, with nothing else on the instance set.",
    ),
    BASIS_COMBINATORIAL: (
        "This component's variations are combinations rather than one list — several option",
        "lists, or independent toggles — so the set is a product and not enumerable from the",
        "schema. One instance is seeded and no combination is chosen here.",
    ),
    BASIS_UNVARIED: (
        "No property on this component carries an option list and none of them is a toggle,",
        "so the source records no variation to enumerate: one instance of the component",
        "itself, which is the least a guide page can show an editor.",
    ),
    BASIS_NOT_DERIVABLE: (
        "The set is derived from the source's option lists, and this dossier does not report",
        "them in full — so it cannot be derived here. An option list read as empty cannot be",
        "told from a component with no choices, and one instance reported as the whole set",
        "would be a guess dressed as an answer. What is missing:",
    ),
}

# Why the option lists could not be read, wrapped into the not-derivable rule above. Two
# reasons rather than one, because a dossier declaring itself thin and a dossier declaring
# nothing are different facts about the producer, and the second is a document to go and fix.
REASON_SEED_STRUCTURE_INCOMPLETE = (
    "this dossier declares structureAvailable: false, so the read behind it could not report "
    "every field, and an option list is one of the fields a thin rung leaves empty")
REASON_SEED_STRUCTURE_UNDECLARED = (
    "this dossier does not declare structureAvailable at all, so nothing in it says whether "
    "its option lists were read in full or left empty")

# Printed where a seed sets no value, which is every seed but an enumerated one.
#
# Said of the instance rather than of a creation, because this prints on both paths: an
# already-arranged page lists the set without proposing any of it, and "is created" there names
# a write nothing in the plan is proposing. The old wording only escaped notice because no
# fixture reached a valueless seed on an arranged page.
STATEMENT_SEED_NO_VALUES = (
    "The instance above sets nothing, so its values are whatever the CMS applies. This",
    "script records no default for an option list or a toggle — two real projects carry",
    "none — so it has none to apply and does not invent one: the values that instance",
    "ends up with are the CMS's, not this plan's.",
)
# Both numbers are the fixture's own arithmetic over the dossier, which is what makes the
# refusal to enumerate assertable: a plan that multiplied the toggles out would print the
# product as its count instead of beside it.
#
# **"None of them" is the remaining combinations, and the sentence has to say so.** This
# statement prints wherever the source describes more combinations than the plan lists, which
# includes the shape that is enumerable AND combinatorial at once -- one option list beside a
# toggle. There it sits directly under the instances the option list enumerated, so a bare
# "this plan seeds none of them" denies the three seeds a reader can see, and contradicts the
# count in its own first clause. It also prints on an already-arranged page, where nothing is
# seeded by anything: "listed above" is true on both paths where "seeded here" is true on one.
STATEMENT_SEED_COMBINATIONS = (
    "The properties above describe %d combinations in total, against the %d %s",
    "listed above. Which of the remaining combinations are worth showing is",
    "a person's judgment, so this plan proposes no others — curating them is somebody's",
    "job rather than a set a script can derive.",
)
STATEMENT_SEED_CREATE = (
    "This page carries no live examples, so every instance above would be created — after",
    "approval, in the spell, like every other write this plan proposes.",
)
STATEMENT_SEED_KEPT = (
    "This page already carries an arrangement, so nothing above is seeded and nothing",
    "above is proposed: the set is listed to be read beside what is on the page. Which",
    "variants that arrangement holds is not something this script can read — an",
    "arrangement is markup or a block list, and it is a person's work either way.",
)
# Printed where a page already arranged meets a component recording no variation axis and a
# signature that no longer matches. **The one transition a silence here would hide**: the
# arrangement was built when there was a set to build it from, and there is not one now, so the
# instances on the page may show an option list the component no longer carries.
#
# Hedged because a hedge is the whole truth available. Nothing records the shape the source had
# when the page was seeded -- only a hash of it -- so "the axis was removed" cannot be told
# from "the axis never existed and something else moved". Both are worth a person's look and
# neither is worth a write, which is what makes the hedge actionable rather than evasive.
STATEMENT_SEED_AXIS_GONE = (
    "This component records no variation axis now, and the stored signature says its schema",
    "moved since this page was seeded — so the arrangement on the page may be built from an",
    "option list the component no longer carries. Which of those it is cannot be read here,",
    "and the arrangement is left alone either way — this prints so a person goes and looks.",
)
STATEMENT_SEED_CHANGED = (
    "The stored signature no longer matches, and the signature covers every option list, so",
    "the variant set may have changed since this page was seeded. That is reported here and",
    "acted on nowhere: a changed set is a thing for a person to look at, never a reason to",
    "replace an arrangement.",
)

# The two lists a reader needs named rather than counted. The first is the whole of "this
# script does not choose the variant property"; the second is what turns a list into a product.
CAPTION_SEED_CANDIDATES = (
    "Option lists on this component, any of which could be the variant property. Nothing",
    "records which one it is, so this plan does not choose:",
)
CAPTION_SEED_TOGGLES = (
    "Independent toggles, which multiply the set rather than enumerating it:",
)


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

    # `None` here is the adoption path, not a failure: the page states explicitly that it
    # claims no source, which is a page somebody wrote by hand. An *absent* `source` key is
    # still refused, inside `stored_reference` — one is a fact about the CMS and the other a
    # fact about the producer, and adopting a page because a read failed is the mistake that
    # costs somebody their work.
    source = stored_reference(path, label, payload,
                              consequence=REFERENCE_CONSEQUENCE_PLAN)

    # No alias to match on the adoption path, and none is wanted: the page claims no component,
    # so there is nothing here that could disagree with the alias the caller asked for. The
    # check below exists to catch a page that claims a *different* component, and a page
    # claiming none cannot.
    if source is not None and source["alias"].lower() != alias.strip().lower():
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

    # Typed because the seed set turns on it, and a truthy string would read as "read in full"
    # from a document saying the opposite. Absence is not refused: it is answered, by declining
    # to derive a set from option lists nothing vouches for.
    available = doc.get("structureAvailable")
    if available is not None and not isinstance(available, bool):
        raise GuideError(
            "%s declares 'structureAvailable' as %r, and it is true or false.\n"
            "  It is what says whether this dossier's option lists were read in full, and the "
            "live-example seed set is derived from those lists — so a value that is neither "
            "would decide it by accident." % (path, available))

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

    Two branches, and the page's **provenance** picks between them — never a field's
    declaration. A page carrying a stored reference is planned as a regeneration; a page
    carrying none is planned as an adoption, where the register still says what each field is
    for and says nothing at all about permission to write it.
    """
    if page["source"] is None:
        return _adoption(page, dossier_doc)

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
    # A no-op leaves this empty for the same reason as the other two: there is no regeneration
    # for a field to be pending against, and a no-op that listed an unwritten field would be
    # reporting work on the one path whose whole value is that no work is needed. The field is
    # still unwritten, and the run that is not a no-op says so.
    machine_owned, left_alone, unwritten = [], [], []
    if not noop:
        machine_owned = _machine_owned(page, dossier_doc, current, reason)
        left_alone = _left_alone(page)
        unwritten = _unwritten(page)

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

    # A no-op derives no seed set, and the key is absent rather than null. The source has not
    # changed shape since this page was generated, so the set is the set the page was seeded
    # with and there is nothing about it to report -- the same reason the two lists above are
    # empty on this path rather than full.
    seeding = None if noop else _seeding(page, dossier_doc, comparison)

    doc = {
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
            "unwritten": _joined(RULE_UNWRITTEN),
        },
        "machineOwned": machine_owned,
        "leftAlone": left_alone,
        # Always present, empty where there is nothing pending -- unlike `seeding`, which is the
        # whole answer or absent. A consumer walking for work to do reads a list either way, and
        # an empty list is the answer "nothing is unwritten" rather than a shape to recognize.
        "unwritten": unwritten,
    }
    # Absent, not null, where there is nothing to say: a null under a key a consumer walks is
    # one more shape it has to recognize, and `seeding` is the whole answer or it is not there.
    if seeding is not None:
        doc["seeding"] = seeding
    return doc


def _adoption(page, dossier_doc):
    """The plan for a page nobody generated: everything offered, nothing owned, nothing written.

    **The document's key set is the regeneration branch's plus three** — `provenance`,
    `proposeOnly` and `offered` — and no shared key changes what it means. `machineOwned` is
    present and empty; `leftAlone` carries every field the page holds; `comparison` carries its
    fourth value. So the list a consumer walks looking for writes is empty, which is the true
    answer and not a shape it has to recognize first. `rule` is the one shared key whose
    entries differ, and they differ because the rules do.

    The offer keys its value `proposedOnApproval` rather than `proposed`, so a consumer
    scanning an adoption plan for a value to write finds no such key anywhere in it — least of
    all on the stored reference, whose write is the one that changes what every later run may
    do.

    **`noop` is false, always.** There is no stored signature, so nothing was compared and
    nothing could be: an adoption is a proposal every time it is asked for, and reporting one
    as a no-op would be reporting a page as up to date with a source it never claimed.

    **No seed set is derived here, and `seeding` is absent.** A seed is an instance created on
    a page, and on this path nothing is created: the offer is the property table and the stored
    reference, and adding live examples to a page somebody wrote by hand is a write like any
    other. Once the reference is approved the page has a provenance, and the next run derives
    the set on the regeneration branch where it belongs.
    """
    current = dossier_doc.get("sourceSignature")
    offered = _offered(page, dossier_doc, current)
    # Only the `content` kind is counted, because it is the only kind an offer can be. A
    # regeneration counts `owed` alongside it -- prose a model writes -- and mirroring that
    # here read as though unwritten prose might make a model call necessary. It cannot:
    # `_offered` skips every OWED entry, since a field somebody wrote is not a field this
    # script proposes prose for. The mirrored sum was structurally zero, and dead arithmetic
    # that looks live costs a reader more than the symmetry was worth.
    content = sum(1 for entry in offered if entry["proposal"] == PROPOSAL_CONTENT)

    return {
        "planVersion": PLAN_VERSION,
        "alias": dossier_doc["alias"].strip(),
        "name": dossier_doc.get("name") or "",
        "page": page["page"],
        "rung": dossier_doc["rung"].strip(),
        "provenance": PROVENANCE_HAND_WRITTEN,
        "proposeOnly": True,
        "storedSignature": None,
        "storedRung": None,
        "currentSignature": current,
        "comparison": COMPARISON_NO_REFERENCE,
        "noop": False,
        # The property table still has to be rendered in the project's own markup, and that is
        # the spell's half. Counted the same way a regeneration counts it, so a consumer
        # deciding whether to load a renderer reads one field on either path.
        "modelCallNeeded": bool(content),
        "statements": [_joined(STATEMENT_NO_REFERENCE),
                       _joined(STATEMENT_ADOPTION),
                       _joined(STATEMENT_NOTHING_WRITTEN)],
        # The three class rules are absent rather than empty: they describe a page that carries
        # a reference, and a consumer rendering them here would be quoting a rule that does not
        # apply to the page in front of it.
        "rule": {
            "humanOwned": _joined(RULE_HUMAN_OWNED),
            "offered": _joined(RULE_OFFERED),
            "kept": _joined(RULE_KEPT),
        },
        "machineOwned": [],
        "offered": offered,
        "leftAlone": _kept(page),
    }


# The two register fields an adoption offers, and therefore the two it does not list as kept. A
# tuple rather than a test against the proposal kind, because the two lists have to agree about
# it: a field in both would read as offered and preserved at once.
OFFERED_FIELDS = (FIELD_SOURCE, FIELD_PROPERTIES)


def _offered(page, dossier_doc, current):
    """What an adoption offers: the values this script can compute, and nothing else.

    The prose is skipped deliberately and that is the rule, not an omission — prose is what a
    person writes, and on a page they wrote there is nothing to improve on. Every prose field
    in the register is seeded-once, so the first clause of the test below skips all of it; the
    second clause is what would skip a machine-owned field owing prose, and the register names
    none today. So the offer is the property table and the stored reference, and the plan says
    in words that no prose is proposed rather than leaving a reader to notice the prose
    missing.
    """
    entries = []
    for spec in REGISTER:
        if spec["ownership"] != MACHINE_OWNED or spec["proposal"] == PROPOSAL_OWED:
            continue
        if spec["field"] == FIELD_SOURCE:
            # By definition on this path: the page states `"source": null`, and `load_page`
            # refuses a page that also carries a `guideSource` field.
            present, value = False, None
        else:
            present = spec["field"] in page["fields"]
            value = page["fields"].get(spec["field"])
        entry = {
            "field": spec["field"],
            # Not the register's class. The register says what the field is for; provenance
            # says who owns it, and on this page that answer is the same for every field.
            "ownership": HUMAN_OWNED,
            "proposal": spec["proposal"],
            "why": spec["why"],
            "current": value,
            "onPage": present,
            "pendingApproval": True,
            # Never keyed `proposed`. A consumer looking for a value to write finds no such key
            # anywhere in an adoption plan, which is the property this path exists to hold.
            "proposedOnApproval": _proposed(spec, dossier_doc, current),
        }
        if spec["field"] == FIELD_SOURCE:
            entry["consequence"] = REFERENCE_WRITE_CONSEQUENCE
        if spec["field"] == FIELD_PROPERTIES:
            # **A page carrying no table at all is an empty table, not an incomparable one.**
            # A hand-written page has no rows, so every proposed row is `added` — which is the
            # honest summary and the reason this must not fall through to the not-comparable
            # note or, worse, to a comparison that finds nothing to report and prints "the
            # table matches the source". The table does not exist yet.
            if isinstance(value, list):
                rows = value
            elif not present:
                rows = []
            else:
                rows = None
            entry["rowChanges"] = (compare_rows(rows, proposed_rows(dossier_doc))
                                   if rows is not None else None)
            entry["rowsNotComparable"] = rows is None
        entries.append(entry)
    return entries


def _kept(page):
    """Every field the page carries that this plan proposes nothing against, human-owned.

    Register fields in register order then the rest in alias order, the same ordering the
    regeneration branch uses and for the same reason: a plan whose lines move between runs
    cannot be diffed. The class in the register is not consulted — on a page with no stored
    reference, a seeded-once field and an editorial one are equally somebody's.
    """
    entries = []
    for spec in REGISTER:
        if spec["field"] in OFFERED_FIELDS or spec["field"] not in page["fields"]:
            continue
        entries.append({
            "field": spec["field"],
            "ownership": HUMAN_OWNED,
            "why": KEPT_WHY,
            "current": page["fields"][spec["field"]],
        })
    for field in sorted(page["fields"], key=lambda f: f.lower()):
        if field in BY_FIELD:
            continue
        entries.append({
            "field": field,
            "ownership": HUMAN_OWNED,
            "why": KEPT_WHY,
            "current": page["fields"][field],
        })
    return entries


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
    a page whose signature was stamped at creation but whose prose was never written reads as a
    no-op until the component's shape changes. Nothing here can tell that from a page somebody
    deliberately left short, and the field register has no notion of "required to be
    non-empty". Every prose field is seeded-once now, so the only write that could have filled
    them was the creation that stamped the signature -- which makes this shape a creation that
    stopped half way rather than a regeneration that skipped something. The honest fix, if it
    ever arises, is a seeded-at marker rather than guessing from emptiness; the unwritten
    section reports it meanwhile, on any run that is not a no-op.
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


def _machine_owned(page, dossier_doc, current, reason):
    """One entry per machine-owned field in the register, whether the page carries it or not.

    A regeneration proposes all of them: a field the page is missing entirely is exactly the
    field most in need of a value, and leaving it out of the plan because the page had nothing
    to diff against would hide it.

    `reason` is `_compare`'s, and it is here for one field on one shape: the stored reference's
    consequence, on the page that has no stored signature yet.
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
        # Only where this page has NO stored signature, which is the shape the spell's creation
        # path sends: a page that does not exist yet, declaring the reference it is about to
        # write. That write is a first write, and it is the same irreversible fact an adoption
        # offers, so it carries the same text rather than being said again in the spell's words.
        #
        # `notComparable` has four causes and this is the only one that is a first write. A page
        # stored at another rung, or with no rung recorded, already carries a reference: writing
        # a new one over it changes which signature is compared and nothing about what the tool
        # is allowed to do, so warning there would be an explanation with nothing under it --
        # what `_class_rules` refuses to print for a class no field is in.
        #
        # Keyed on the reason rather than on `page["source"]["signature"]` being empty: that
        # test is `_compare`'s first clause, and a second copy of it here is a second rule that
        # could disagree with the first. The reason alone is the whole condition, because
        # `REASON_NO_STORED` is returned beside `COMPARISON_NOT_COMPARABLE` and nowhere else.
        if spec["field"] == FIELD_SOURCE and reason == REASON_NO_STORED:
            entry["consequence"] = REFERENCE_WRITE_CONSEQUENCE
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


def _unwritten(page):
    """Seeded-once register fields the page carries no value for at all.

    Reported because silence reads as completeness. A field here is in neither of the other two
    lists by construction: `_left_alone` reproduces the value a field holds and this one holds
    none, and the machine-owned sections propose values this script or a model can produce,
    which a seeded value is not -- its only write is at page creation.

    **The live-example field is excluded, and only because something else already answers for
    it.** The seeding section reports an absent arrangement as a set that would be created, in
    words, with the set beside it. Naming it here as well would give one field two answers in
    one report, and the more detailed answer is the one already written.
    """
    return [{"field": spec["field"], "ownership": spec["ownership"], "why": spec["why"]}
            for spec in REGISTER
            if spec["ownership"] == SEEDED_ONCE
            and spec["field"] != FIELD_EXAMPLES
            and spec["field"] not in page["fields"]]


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


def _seeding(page, dossier_doc, comparison):
    """The live-example seed set, or None where there is nothing about seeding to say.

    Derived, never chosen: the option list on the source carries the variant set already, and
    where the variations are combinations instead of a list this returns ONE instance and says
    that curating the rest is a person's job. The four bases and the reasoning behind each are
    written down beside `BASIS_ENUMERATED`.

    **None means the section is absent, and the silence is narrow.** A page already carrying an
    arrangement, for a component whose schema records no variation axis, AND a comparison that
    did not find a difference: there is no set to seed and nothing saying anything moved, so a
    heading with a nought under it would be a reader's time spent to learn nothing.

    **A comparison that DIFFERS breaks the silence, and that is the whole of this rule.** "No
    variation axis now" is not the same fact as "no variation axis ever": where the signature
    says the schema moved, the arrangement on the page may have been built from an option list
    the source has since dropped, and that is the most consequential thing this section can
    report. Reading it as "nothing could have changed" cost the report exactly that case — the
    stale arrangement printed under `Left alone` and nothing anywhere said why to look at it.
    Every other combination prints — including a set that cannot be derived, which is a finding
    rather than a silence.

    A matched comparison never reaches here: the whole run is a no-op and the caller skips this
    stage. So in practice the silence is the not-comparable one, where a failed comparison says
    nothing about whether the variant set moved and claiming it had would be the same "no
    information read as a change" mistake the rung test exists to prevent.

    **A page carrying the field EMPTY counts as arranged**, and that is the deliberate reading
    rather than a shortcut. This module already holds that a field the page does not carry and
    a field carrying an empty value are different facts — one has nothing yet, the other was
    emptied by somebody — and for a seeded-once field the second is a decision: an editor who
    removed every instance is a person who chose to, and re-seeding them would be replacing an
    arrangement with the set they just rejected. The consequence belongs in the spell's hands:
    a page created with an empty `guideExamples` will never be offered seeds again, so a
    creation should either seed the set or leave the field off the page entirely.
    """
    already = FIELD_EXAMPLES in page["fields"]
    derivable, reason = _structure_read(dossier_doc)
    option_props, toggles = _variation_axis(dossier_doc)

    if not derivable:
        basis = BASIS_NOT_DERIVABLE
    elif len(option_props) == 1:
        basis = BASIS_ENUMERATED
    elif option_props or toggles:
        basis = BASIS_COMBINATORIAL
    else:
        basis = BASIS_UNVARIED

    if already and basis == BASIS_UNVARIED and comparison != COMPARISON_DIFFERS:
        return None

    seeds = _seeds(basis, option_props)
    combinations = _combinations(option_props, toggles) if derivable else None
    # Curation is owed wherever the source describes more combinations than this plan seeds.
    # Stated as arithmetic rather than as a basis test, so the one case that is enumerable AND
    # combinatorial -- a single option list beside a toggle -- is not silently treated as
    # settled: the options are enumerated, and the toggles are still somebody's judgment.
    curation = bool(seeds and combinations is not None and combinations > len(seeds))

    seeding = {
        "field": FIELD_EXAMPLES,
        # The register's class, and here it is the finding rather than bookkeeping: seeded-once
        # is why a changed set is reported instead of applied.
        "ownership": SEEDED_ONCE,
        "basis": basis,
        "rule": _joined(RULE_SEEDING),
        # The reason a set could not be derived is part of the rule it qualifies rather than a
        # statement of its own: the rule's last line is "What is missing:", and an explanation
        # printed twice teaches a reader to skip explanations.
        "basisRule": _joined(RULE_BASIS[basis] + (_wrapped(reason) if reason else ())),
        "derivable": derivable,
        "notDerivableReason": reason,
        # `None` rather than `[]` where the set cannot be derived. An empty list reads as "no
        # seeds needed", which is exactly the claim a dossier that cannot report its option
        # lists is unable to make -- the same trap as an empty `options`.
        "seeds": seeds,
        # A copy, its option list included: the same entry is in `optionProperties` below, and
        # two keys of one document sharing a list is a shape a consumer can edit by accident.
        "variantProperty": (_copied(option_props[0]) if basis == BASIS_ENUMERATED else None),
        "optionProperties": option_props,
        "toggleProperties": toggles,
        "combinations": combinations,
        "curationNeeded": curation,
        "alreadySeeded": already,
        # `None` where there is no set: "create" beside `"seeds": null` would name an action
        # against nothing, and a consumer walking for work to do would find a verb and no
        # object. What to do about a set that could not be derived is in the rule.
        "action": None if seeds is None else (SEED_REPORT_ONLY if already else SEED_CREATE),
    }
    # Built from the document rather than beside it, so the report and the document cannot
    # select different statements -- the same shape `_statement_lines` uses for the plan's own
    # three. `comparison` is the one fact the section needs and does not hold: it belongs to
    # the plan, and copying it in would put two answers to one question in one document.
    seeding["statements"] = [_joined(lines)
                            for lines in _seed_statement_lines(seeding, comparison)]
    return seeding


def _seed_statement_lines(seeding, comparison):
    """Which statements this seed set owes its reader, as the lines a report prints.

    One selection, read by both renderings. The not-derivable basis owes none of these: its
    whole finding is in the rule, which names what was missing and stops there rather than
    going on to say what would have happened to a set nobody has.
    """
    if seeding["seeds"] is None:
        # The rule carries the whole finding here — what was missing, and why one instance
        # reported as the set would be a guess. There is no set for anything to happen to, so
        # neither "these would be created" nor "these are kept" would be a true thing to add,
        # and the report and the document would then disagree about which is which.
        return []

    statements = []
    # Every seed but an enumerated one sets nothing, and that has to be said in words: "one
    # instance at the defaults" read as "this script chose the defaults" is the one misreading
    # of this section that would put invented values into a project.
    if any(not seed["values"] for seed in seeding["seeds"]):
        statements.append(STATEMENT_SEED_NO_VALUES)
    if seeding["curationNeeded"]:
        statements.append(_combination_statement(seeding["combinations"],
                                                 len(seeding["seeds"])))
    if seeding["alreadySeeded"]:
        statements.append(STATEMENT_SEED_KEPT)
        # Only where the comparison actually found a difference. A signature that could not be
        # compared says nothing about whether the variant set moved, and claiming it had is the
        # same "no information read as a change" mistake the rung test exists to prevent.
        #
        # One drift statement, and the more specific one wins. Where the component records no
        # variation axis at all, "the variant set may have changed" understates what the reader
        # needs: the set is not merely different, there is none, so the instances on the page
        # answer to nothing in the source. Printing both would say it twice and make the
        # weaker sentence the one a skimming reader stops at.
        if comparison == COMPARISON_DIFFERS:
            statements.append(STATEMENT_SEED_AXIS_GONE
                              if seeding["basis"] == BASIS_UNVARIED
                              else STATEMENT_SEED_CHANGED)
    else:
        statements.append(STATEMENT_SEED_CREATE)
    return statements


def _structure_read(dossier_doc):
    """Whether this dossier's option lists can be believed, and why not where they cannot.

    Derivability turns on the dossier's own `structureAvailable`, which is the one field that
    already means "everything here was read in full". The models rung sets it false and names
    `options` among its gaps, and there `"options": []` is on every property whether the
    component has choices or not -- so a seed set derived from it would report one instance for
    every component in a project and look like an answer.
    """
    if "structureAvailable" not in dossier_doc:
        return False, REASON_SEED_STRUCTURE_UNDECLARED
    if not dossier_doc["structureAvailable"]:
        return False, REASON_SEED_STRUCTURE_INCOMPLETE
    return True, None


def _variation_axis(dossier_doc):
    """The properties a variation could live on: the option lists, and the toggles.

    Both in the editor's own order, tabs before groups, so a report's lines do not move between
    runs. Inherited properties are counted like any other: a `spacing` list arriving from a
    composition varies the rendering exactly as much as one declared here, and where the
    variant property is inherited that is a fact about the project rather than a reason to
    ignore it.
    """
    option_props, toggles = [], []
    for prop in _properties(dossier_doc):
        entry = {"alias": prop["alias"], "name": prop.get("name") or ""}
        options = _unique(prop.get("options") or [])
        if options:
            entry["options"] = options
            option_props.append(entry)
        elif (prop.get("editor") or "").strip().lower() in TOGGLE_EDITORS:
            toggles.append(entry)
    return option_props, toggles


def _properties(dossier_doc):
    """Every property on the component, tab level then group level, tab by tab.

    The same walk `proposed_rows` makes, kept separate because that one is building rows for a
    page and this one is reading a schema. Sharing it would tie the seed set's order to the
    property table's shape.
    """
    for tab in dossier_doc.get("tabs") or []:
        for prop in tab.get("properties") or []:
            yield prop
        for group in tab.get("groups") or []:
            for prop in group.get("properties") or []:
                yield prop


def _unique(options):
    """An option list with its duplicates dropped, in the order it declared them.

    Two identical options are one variant: seeding two instances of the same value would put a
    duplicate on a guide page and count it as coverage. A data type CAN list a value twice --
    nothing in either format stops it -- so this is a real shape rather than a defensive
    flourish.

    **Matched exactly, never case-folded.** An option's text IS the value written to the
    property, so "Neutral" and "neutral" are two values and two variants, however unlikely a
    pair. Folding them drops a variant from a guide page and says nothing; keeping them puts a
    near-duplicate in front of a person, who can delete one. Visible over silent, which is the
    line this module holds everywhere else — and the reason a fold cannot be justified by the
    duplicate rule above is that exact matching already covers every case that rule describes.
    """
    seen, kept = set(), []
    for option in options:
        # Exact as the key, and only the empty test looks past the exact text: an option that
        # is nothing but whitespace is no variant to seed, while two options differing by
        # whitespace are two strings the CMS would write.
        if option.strip() and option not in seen:
            seen.add(option)
            kept.append(option)
    return kept


def _seeds(basis, option_props):
    """The instances the basis implies, each carrying what it sets and what it is called.

    An enumerated seed sets exactly one value: the variant property's option, and nothing else.
    Every other seed sets **nothing at all**, and `values` is empty rather than filled with a
    default this script does not have -- see `STATEMENT_SEED_NO_VALUES`, which is printed
    beside it so no reader takes the empty instance for a chosen one.
    """
    if basis == BASIS_NOT_DERIVABLE:
        return None
    if basis == BASIS_ENUMERATED:
        prop = option_props[0]
        return [{"variant": option,
                 "property": prop["alias"],
                 "name": prop["name"],
                 "values": {prop["alias"]: option}} for option in prop["options"]]
    return [{"variant": None, "property": None, "name": None, "values": {}}]


def _copied(prop):
    """One property entry, deep enough that its option list is its own."""
    entry = dict(prop)
    if "options" in entry:
        entry["options"] = list(entry["options"])
    return entry


def _combinations(option_props, toggles):
    """How many distinct instances the source's variation axis actually describes.

    Printed beside the number seeded, never as it. This is the arithmetic that makes "not
    enumerable" a measurement rather than an opinion: four independent toggles are sixteen
    combinations, and sixteen live instances on a page an editor reads is not documentation.
    """
    total = 1
    for prop in option_props:
        total *= len(prop["options"])
    return total * (2 ** len(toggles))


def _combination_statement(combinations, seeded):
    return (STATEMENT_SEED_COMBINATIONS[0]
            % (combinations, seeded, rpt.plural(seeded, "instance", "instances")),
            ) + STATEMENT_SEED_COMBINATIONS[1:]


# Two columns narrower than the report's width, because these lines are printed two columns
# in. The joined sentence a document carries is the same string whatever width the lines were
# wrapped at, so wrapping for the rendering costs the document nothing.
SEED_REASON_WIDTH = rpt.WRAP_WIDTH - 2


def _wrapped(reason):
    """A reason as report lines, at the width the hand-authored lines around it were written
    for. The same treatment `STATEMENT_NOT_COMPARABLE`'s reason gets, and the same reason: the
    text names things this module does not choose, so its length is not knowable here."""
    return tuple(textwrap.wrap("%s." % reason, SEED_REASON_WIDTH) or ["%s." % reason])


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
    """The model-call sentence, in the form the two counts can honestly carry.

    **Neither count is printed as a nought, and both directions are guarded.** The first form
    was added when the register stopped owing prose; the mirror was left unguarded because no
    register entry can make `content` nought today. That is the same "unreachable today" the
    comment beside these constants refuses to rely on for the arithmetic, and relying on it for
    the wording would have been the same bug facing the other way. Three forms, so a register
    edit in either direction gets a true sentence rather than a nought in a sentence.

    The reasoning for keeping both counts in the arithmetic sits beside the constants.
    """
    if not owed:
        return (STATEMENT_MODEL_NEEDED_NO_PROSE[0]
                % (content, rpt.plural(content, "field carries", "fields carry")),
                ) + STATEMENT_MODEL_NEEDED_NO_PROSE[1:]
    if not content:
        return (STATEMENT_MODEL_NEEDED_NO_CONTENT[0]
                % (owed, rpt.plural(owed, "field needs", "fields need")),
                ) + STATEMENT_MODEL_NEEDED_NO_CONTENT[1:]
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

    **An adoption gets its own rendering, not a variant of this one.** Every heading, rule and
    label in the two differs, because they are saying different things — and a reader who has
    seen one of them has to be able to tell at a glance which of the two is in front of them.
    """
    if doc.get("provenance") == PROVENANCE_HAND_WRITTEN:
        return _adoption_report(doc)

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
        _proposal_rules(lines, doc["machineOwned"])
        lines.extend("  " + line for line in RULE_VERBATIM)
        for entry in doc["machineOwned"]:
            lines.append("    %s: %s" % (entry["field"], PROPOSAL_LABEL[entry["proposal"]]))
            # **Printed here, not left to `--json`.** The person reading this report is the
            # person being asked, and a warning only a consumer can see is a warning they do not
            # get. It reaches one entry on one shape -- the stored reference on a page that has
            # none yet -- so it is attached to the field rather than stated for the section.
            #
            # The adoption report does not need this and does not get it: that whole report is
            # about this one approval, and says so in `STATEMENT_ADOPTION` and `RULE_OFFERED`
            # before any field is listed. Here the same write is one field among several in a
            # regeneration, which is exactly why it has to be marked where it sits.
            if entry.get("consequence"):
                lines.append("      %s" % CAPTION_CONSEQUENCE)
                # `break_on_hyphens=False`, or the wrap splits "machine-owned" across two
                # lines in the one sentence whose subject is machine-owned fields.
                lines.extend("        " + line for line in
                             textwrap.wrap(entry["consequence"], rpt.WRAP_WIDTH - 8,
                                           break_on_hyphens=False))
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

    # Printed only when there is one, and with no count in the caption. Every other section here
    # heads with a number because a reader needs to know a nought was computed rather than
    # skipped; this one is the exception, because a nought is the normal state and a section
    # reading zero in every report is the line that teaches a reader to skip the ones above it.
    if doc.get("unwritten"):
        lines.append("")
        lines.append("%s:" % CAPTION_UNWRITTEN)
        lines.extend("  " + line for line in RULE_UNWRITTEN)
        for entry in doc["unwritten"]:
            lines.append("    %s (%s)" % (entry["field"], entry["ownership"]))

    # After the field sections and before the closing statement, which is the order the
    # plan itself names them in: what would be written, what would not, and what would be
    # created beside them.
    if doc.get("seeding"):
        lines.append("")
        lines.extend(_seed_section_lines(doc["seeding"], doc["comparison"]))

    lines.append("")
    lines.extend(_statement_lines(doc, 2))
    return "\n".join(lines)


# What the report prints where a generated page prints its stored reference's four fields.
# Named as the absence of a reference rather than as the absence of a value: "the page carries
# no value for this field" is true of a field somebody has not filled in yet, and this is not
# that — it is the fact the whole plan turns on.
NO_REFERENCE_VALUE = "(this page carries no stored reference)"

# Where a regeneration report prints the stored signature and the rung it was recorded at.
# Neither exists here, and "none recorded" beside a field labelled "Stored signature" would
# read as a reference whose signature went missing rather than as a page that claims no source.
ADOPTION_REFERENCE_LINE = ("  Stored reference: none — this page claims no source, so it was "
                           "written by hand.")


def _adoption_report(doc):
    """The human rendering of an adoption: offered, kept, and nothing written.

    Same three-part shape as a regeneration report — header, headline, sections — so a reader
    finds the counts in the same place. Every word around them is different, which is the
    point: the risk this document carries is being skimmed as though it were the other one.
    """
    lines = []
    lines.append("Change plan for %s, read at the %s rung."
                 % (rpt.item({"alias": doc["alias"], "name": doc["name"]}), doc["rung"]))
    lines.append("  Guide page: %s" % doc["page"])
    lines.append(ADOPTION_REFERENCE_LINE)
    lines.append("  Current signature: %s" % (doc["currentSignature"] or "none"))
    lines.extend("  " + line for line in STATEMENT_NO_REFERENCE)

    lines.append("")
    lines.extend(STATEMENT_ADOPTION)

    # Printed with its zero, and printed first, in the place a regeneration puts the fields it
    # proposes to write. A reader looking for "what will this change" reads a nought.
    lines.append("")
    lines.append("%s: %d" % (CAPTION_MACHINE_OWNED, len(doc["machineOwned"])))

    lines.append("")
    lines.append("%s: %d" % (CAPTION_OFFERED, len(doc["offered"])))
    if doc["offered"]:
        lines.extend("  " + line for line in RULE_HUMAN_OWNED)
        lines.extend("  " + line for line in RULE_OFFERED)
        lines.extend("  " + line for line in RULE_VERBATIM)
        for entry in doc["offered"]:
            # The class is on the field's own line here, where a regeneration report leaves it
            # to the section heading. On this path the class is the finding — the section says
            # nothing is machine-owned, and each field then says what it is instead.
            lines.append("    %s (%s): %s" % (entry["field"], entry["ownership"],
                                              PROPOSAL_LABEL[entry["proposal"]]))
            if entry.get("rowChanges") is not None:
                lines.append("      changes:")
                lines.extend(row_summary_lines(entry["rowChanges"], "        "))
                continue
            if entry.get("rowsNotComparable"):
                lines.append("      changes:")
                lines.extend("        " + line for line in ROWS_NOT_COMPARABLE)
                continue
            lines.append("      current:")
            lines.extend(_offered_current_lines(entry, "        "))
            # Never "proposed:". The label a person reads has to say the same thing the
            # document's keys say, or the two disagree about what this run did.
            lines.append("      pending your approval:")
            lines.extend(_side_lines(entry, entry["proposedOnApproval"], True, "        "))

    lines.append("")
    lines.append("%s: %d" % (CAPTION_KEPT, len(doc["leftAlone"])))
    if doc["leftAlone"]:
        lines.extend("  " + line for line in RULE_KEPT)
        # No per-class rules: there is one class here, and the section's own rule states it.
        for entry in doc["leftAlone"]:
            lines.append("    %s (%s)" % (entry["field"], entry["ownership"]))
            lines.extend(_value_lines(entry["current"], True, "      "))

    lines.append("")
    lines.extend(STATEMENT_NOTHING_WRITTEN)
    return "\n".join(lines)


def _offered_current_lines(entry, indent):
    """The current side of one offered field, with the stored reference named as absent.

    `_side_lines` would say "the page carries no value for this field" here, which is true of
    any empty field and says nothing about the one thing a reader of an adoption plan needs to
    know: there is no reference, which is why this is an adoption.
    """
    if entry["field"] == FIELD_SOURCE and not entry["onPage"]:
        return ["%s%s" % (indent, NO_REFERENCE_VALUE)]
    return _side_lines(entry, entry["current"], entry["onPage"], indent)


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


def _proposal_rules(lines, entries):
    """The explanation for each kind of proposal present below, and no others.

    The same discipline `_class_rules` applies to the ownership classes, and the same reason: a
    plan that proposes no prose should not carry a paragraph about prose a model writes. The
    count is in the caption because a reader who has seen three kinds explained before needs to
    know that two is a selection and not a field gone missing.
    """
    present = set(entry["proposal"] for entry in entries)
    kinds = [kind for kind in PROPOSAL_ORDER if kind in present]
    if not kinds:
        return
    lines.append("  " + CAPTION_PROPOSALS % PROPOSAL_COUNT_PHRASE[len(kinds)])
    for kind in kinds:
        lines.extend("  " + line for line in RULE_PROPOSAL_KIND[kind])


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


def _seed_section_lines(seeding, comparison):
    """The live-example set, as a person reads it: the count, the rule that produced it, the
    instances, and what would happen to them.

    The rule prints with the number for the reason `inventory` prints its determiner's rule
    with its count: a set derived by the wrong rule is a plausible number, and the only thing
    that makes it checkable is the rule sitting next to it.
    """
    if seeding["seeds"] is None:
        lines = ["%s: %s" % (CAPTION_SEEDS, SEEDS_NOT_DERIVABLE)]
    else:
        lines = ["%s: %d" % (CAPTION_SEEDS, len(seeding["seeds"]))]
    lines.extend("  " + line for line in RULE_SEEDING)
    lines.extend("  " + line for line in RULE_BASIS[seeding["basis"]])

    if seeding["seeds"] is None:
        lines.extend("  " + line for line in _wrapped(seeding["notDerivableReason"]))
        return lines

    for seed in seeding["seeds"]:
        lines.append("    %s" % _seed_line(seed))
    # Named only where naming them is the finding. One option list needs no candidate list --
    # the seeds above already name the property they set.
    if len(seeding["optionProperties"]) > 1:
        lines.extend("  " + line for line in CAPTION_SEED_CANDIDATES)
        for prop in seeding["optionProperties"]:
            lines.append("    %s: %s" % (rpt.item(prop), " | ".join(prop["options"])))
    if seeding["toggleProperties"]:
        lines.extend("  " + line for line in CAPTION_SEED_TOGGLES)
        for prop in seeding["toggleProperties"]:
            lines.append("    %s" % rpt.item(prop))
    for statement in _seed_statement_lines(seeding, comparison):
        lines.extend("  " + line for line in statement)
    return lines


def _seed_line(seed):
    """One instance: what it is called, and what it sets.

    The variant is printed as the seed's name AND as the value it sets, which is not a
    repetition worth removing: the name is how a person refers to the instance on the page, and
    the value is the write. A seed that sets nothing says so in the same place, because a blank
    there would read as an instance whose values were chosen and not shown.
    """
    if not seed["values"]:
        return "(one instance, nothing set — the CMS applies its own defaults)"
    return "%s — sets %s to %s" % (
        seed["variant"],
        rpt.item({"alias": seed["property"], "name": seed["name"]}),
        json.dumps(seed["values"][seed["property"]]))


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
