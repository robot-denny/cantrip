"""The inventory determiner — which of a project's components are worth documenting.

Every other stage reads one named component. This one classifies them all, and it is the only
stage whose failure is invisible in its own output: a wrong dossier looks wrong, while a
determiner that over-counts by two and a half times produces a perfectly well-formed report
that turns the audit's primary output from a backlog into noise.

## The rule, and why the obvious rule is wrong

**The element-type flag is not the definition of a documentable component.** It is the closest
thing to one on the type itself, which is exactly why it is tempting. Measured:

    demo project      68 content types    34 carry the flag    23 are content blocks
    a second project 174 content types   125 carry the flag    52 are content blocks

A flag-based inventory would therefore propose 34 guides where 23 are wanted, and 125 where 52
are. The 2.4x over-count on the second project is the spec's headline number.

What separates them is the project's own **block-editor palettes**. A block editor data type
carries a `blocks[]` array, and each entry states two element types by name:
`contentElementTypeKey` is the block an editor places, `settingsElementTypeKey` is its settings
half. So:

- **A component is a content type named as a palette entry's content block.** De-duplicated on
  the alias, because the same block appears in several palettes and in several entries — 58
  Deploy entries on the demo project resolve to 23 distinct components.
- **A settings model is excluded, and it is a set difference rather than a flag.** One element
  type can be the settings half of one entry and a content block of another; nothing on the
  type says which, so the exclusion is computed once the whole project has been read.
- **An element type in no palette is excluded as a composition.** It is schema a guide *reads* —
  the dossier resolves compositions into the owning component's property tables — never schema
  a guide documents.

The palette read itself is the seam `/block` already established for registering a new block;
this reuses it rather than adding a source. `guidelib/dossier.py` owns the payload's shape,
since both formats carry the same JSON, and each adapter owns resolving the keys.

## Page types: proposed, never decided

A page type is documentable and a folder, a container, and an abstract base are not — and **no
structural flag separates them.** Nor does any single signal:

- **Template presence** is the strongest signal and still misses badly. On the second project
  only 9 of 49 non-element types carried a template while 21 were recognizably pages.
- **Tree reachability** is nearly useless as a gate, because a folder is reachable by
  definition: 45 of those same 49 were reachable, including every folder and container.
- **Naming convention** is a project's own, not this toolkit's. On the second project 21 of the
  49 aliases end in `Page`; on the demo project no suffix is shared by even a fifth of them. So
  the convention is **derived from the project** — the trailing alias segment shared by at least
  half of the types that do carry a template — or reported as not derived.

A type is therefore **proposed** when it carries a template or matches the derived convention,
and reachability is reported as supporting evidence rather than used as a gate. Applied to the
two projects that rule proposes 16 of 34 and 23 of 49, against 45 for reachability alone.

**And a proposal is all it is.** The report says so, names the signals behind every entry, and
splits what it did not propose into the two shapes it distinguishes — reachable but untemplated
(a folder or a container) and reachable from nowhere (an abstract base). A wrong determiner that
states its rule is fixable by the person reading it; one that decides quietly is not.

## Why the counts are reported before anything acts on them

The audit's primary output is a set difference against this inventory, so the report states
every count and the rule that produced it. That is not documentation for its own sake: a
determiner reading the flag rather than the palette produces a plausible report, and the only
place the mistake is visible is beside the number it should not have matched.

## What the adapters must provide

Two accessors past `extract`, in format-blind terms, so nothing here learns that one format
spells a reference as a UDI and the other as a GUID:

    palettes(catalog)     -> [{"name", "editor", "entries": [{"content", "settings"}]}]
    components(catalog)   -> [{"alias", "name", "kind", "hasTemplate", "allowAtRoot",
                               "children"}]

**The models rung answers neither, and refuses rather than returning empty.** A generated model
carries no palette, no template assignment and no tree structure, so an empty result there would
read as "this project offers no blocks" — indistinguishable from the truth on a project that
offers none. The refusal and its reasoning live in `guidelib/models.py`.

One catalog is built per run and passed to every extraction. Measured on the demo project: 3.03s
for a fresh catalog per component against 0.045s sharing one, across 68 components; on a uSync
project of 182, 4.78s against 30ms.
"""

import re
import textwrap

from guidelib import dossier
from guidelib import note
# Aliased, because both renderers define a function called `report` and the bare
# module name would be shadowed by it inside exactly the function that needs it.
from guidelib import report as rpt

INVENTORY_VERSION = 1

# How many templated document types it takes before a shared alias suffix means anything, and
# how large a share of them the suffix has to cover. Two and a half: one templated type shares
# its suffix with itself, which would "derive" a convention from a single example and then apply
# it to the whole project.
MIN_TEMPLATED_FOR_CONVENTION = 2
CONVENTION_SHARE_DENOMINATOR = 2

# The alias's trailing camelCase segment is its suffix. `articlePage` -> "page",
# `mediaRowSettings` -> "settings", `xMLSitemap` -> "sitemap", and a single-segment alias is its
# own suffix so `homepage` -> "homepage" rather than matching a "page" convention it only
# resembles. The first alternative keeps an acronym together: without it `xMLSitemap` would end
# at "map".
ALIAS_SEGMENT_RE = re.compile(r"[A-Z]+(?![a-z])|[A-Z][a-z0-9]*|[a-z0-9]+")

# The reason codes attached to a document type this determiner did not propose. Codes rather
# than sentences, because a consumer branches on them; the sentences are below.
REASON_CONTAINER = "folder-or-container"
REASON_BASE = "abstract-base-or-composition"

# --- the rules, stated once and rendered twice ---------------------------------
#
# Each rule is a tuple of report lines, wrapped by hand rather than by `textwrap`. The report
# prints the lines as they stand and the JSON document joins them into one string, so the two
# renderings cannot drift and neither has to reproduce the other's wording. Hand-wrapping is
# what makes the report's golden fixture authorable at all: a computed wrap would have to be
# reproduced by hand in the fixture, which is asserting the implementation against itself.

RULE_COMPONENTS = (
    "A content type named as a palette entry's content block, in one of the project's",
    "block-editor data types. Read from the palette, never from the element-type flag.",
)
RULE_SETTINGS = (
    "An element type named only as a palette entry's settings model and never as a content",
    "block. The settings half of a block already counted, not a block of its own.",
)
RULE_UNPALETTED = (
    "An element type no palette offers. Read into an owning component's property table as a",
    "composition, never documented on its own.",
)
RULE_UNRESOLVED = (
    "A palette offers a content type this export does not hold, so its name and its fields",
    "cannot be read and it is counted here rather than among the components. An element type",
    "is a database row, never a class, so a package that creates one at boot can legitimately",
    "leave it out: the export may ignore that package's schema deliberately, the environment",
    "may not be a schema source at all, or the type may exist only where nobody booted",
    "locally. Re-export from an environment that holds it to document these.",
)

RULE_PAGE_TYPES = (
    "PROPOSED, not decided. No flag separates a page type from a folder, a container, or an",
    "abstract base, so a document type is proposed when it carries a template or matches the",
    "project's own page-naming convention. Tree reachability is read as evidence and is not a",
    "gate, because a folder is reachable by definition.",
)
REASON_SENTENCES = {
    REASON_CONTAINER:
        "Reachable in the content tree, but carries no template and matches no naming convention.",
    REASON_BASE:
        "Neither reachable in the content tree nor carrying a template.",
}

# Section captions. Here rather than inline so the report's shape is readable in one place.
CAPTION_COMPONENTS = "Components an editor can place"
CAPTION_SETTINGS = "Excluded, the settings half of a block"
CAPTION_UNPALETTED = "Excluded, offered by no palette"
CAPTION_UNRESOLVED = "Offered by a palette, absent from this export"

CAPTION_PAGE_TYPES = "Page types PROPOSED for a human to confirm"
CAPTION_NOT_PROPOSED = {
    REASON_CONTAINER: "Not proposed, a folder or a container",
    REASON_BASE: "Not proposed, an abstract base or a composition",
}


def determine(adapter, project_root, with_signatures=True):
    """Classify every component in the project and return the inventory document.

    The whole project is read once, through one catalog, which is then handed to every
    extraction. A signature is taken for each documentable unit because that is what the audit
    compares a guide's stored reference against; the excluded lists carry no signature, since
    nothing will ever be stored against them.
    """
    catalog = adapter.Catalog(project_root)
    # First, because it is the one call a rung may refuse outright. Reading the components
    # before finding out the question cannot be answered would parse the whole corpus for
    # nothing and, worse, would report a project's content types beside a refusal.
    palettes = adapter.palettes(catalog)
    listed = adapter.components(catalog)

    by_alias = {}
    for entry in listed:
        by_alias[entry["alias"].lower()] = entry

    content, settings = _palette_roles(palettes)
    # The marker is not an alias. Pulled out before any set arithmetic, or it would appear as a
    # component named "\0unresolved" and be counted as documentable.
    unresolved_content = content.count(dossier.PALETTE_UNRESOLVED) if isinstance(content, list) \
        else (1 if dossier.PALETTE_UNRESOLVED in content else 0)
    content = [a for a in content if a != dossier.PALETTE_UNRESOLVED]
    settings = [a for a in settings if a != dossier.PALETTE_UNRESOLVED]
    palette_names = _palettes_by_component(palettes)

    element_flagged = [e for e in listed if e["kind"] == dossier.KIND_ELEMENT]
    document_types = [e for e in listed if e["kind"] != dossier.KIND_ELEMENT]

    if element_flagged and not palettes:
        # The one condition under which a correct-looking zero is most likely to be a misread.
        # A note rather than a refusal: a project whose element types are all compositions is
        # unusual but real, and refusing it would refuse a true answer. The report's counts say
        # the same thing; this reaches the person watching a terminal.
        note("%d content types carry the element-type flag and no block-editor data type in "
             "this project declares a blocks[] palette, so no component could be counted.\n"
             "  That is the shape a project has when its block-editor data types were left out "
             "of the export — read the count of 0 components as 'not found here', not as 'this "
             "project has none'." % len(element_flagged))

    components = []
    for alias in sorted(content, key=str.lower):
        entry = by_alias.get(alias.lower())
        components.append({
            "alias": alias,
            "name": entry["name"] if entry else "",
            "kind": entry["kind"] if entry else dossier.KIND_ELEMENT,
            "palettes": palette_names.get(alias.lower(), []),
            "signature": _signature(adapter, project_root, catalog, alias)
            if with_signatures else None,
        })

    lower_content = {a.lower() for a in content}
    settings_only = [a for a in sorted(settings, key=str.lower)
                     if a.lower() not in lower_content]
    lower_settings = {a.lower() for a in settings}
    unpaletted = [e["alias"] for e in element_flagged
                  if e["alias"].lower() not in lower_content
                  and e["alias"].lower() not in lower_settings]

    convention = _naming_convention(document_types)
    proposed, not_proposed = _page_types(document_types, listed, convention["suffix"])

    # Only when a machine is going to read them. The text report never prints a signature, so
    # computing one per component there is a full extract each for a value that is discarded.
    if with_signatures:
        for entry in proposed:
            entry["signature"] = _signature(adapter, project_root, catalog, entry["alias"])

    return {
        "inventoryVersion": INVENTORY_VERSION,
        "rung": adapter.RUNG,
        "contentTypesRead": len(listed),
        "elementFlagged": len(element_flagged),
        "documentTypesRead": len(document_types),
        "palettesRead": len(palettes),
        "rule": {
            "components": " ".join(RULE_COMPONENTS),
            "settingsModels": " ".join(RULE_SETTINGS),
            "unpalettedElementTypes": " ".join(RULE_UNPALETTED),
            "unresolvedPaletteEntries": " ".join(RULE_UNRESOLVED),
            "pageTypesProposed": " ".join(RULE_PAGE_TYPES),
        },
        "namingConvention": convention,
        "palettes": [
            {
                "name": palette["name"],
                "editor": palette["editor"],
                "contentBlocks": len([e for e in palette["entries"] if e["content"]]),
                "settingsModels": len([e for e in palette["entries"] if e["settings"]]),
            }
            for palette in sorted(palettes, key=lambda p: (p["name"], p["editor"]))
        ],
        "components": components,
        "settingsModels": [_named(by_alias, alias) for alias in settings_only],
        "unpalettedElementTypes": [_named(by_alias, alias)
                                   for alias in sorted(unpaletted, key=str.lower)],
        "unresolvedPaletteEntries": unresolved_content,
        "pageTypesProposed": proposed,
        "notProposed": not_proposed,
    }


def _signature(adapter, project_root, catalog, alias):
    """One component's source signature, read through the shared catalog.

    The catalog is what makes this affordable: a fresh one per component re-walks and re-parses
    the whole project, measured at 3.03s against 0.045s across 68 components.

    An unresolvable component raises, exactly as a lone `extract` would. That is deliberate: an
    inventory is the input to a hundred guide pages, so a survey quietly one component short is
    the expensive failure here. The refusal names the component, which is the operator's next
    action.
    """
    entry = adapter.extract(project_root, alias, catalog=catalog)
    return entry["sourceSignature"]


def _named(by_alias, alias):
    entry = by_alias.get(alias.lower())
    return {"alias": alias, "name": entry["name"] if entry else ""}


def _palette_roles(palettes):
    """The two role sets, as aliases in first-seen order.

    De-duplicated on the alias rather than counted per entry, which is the difference between
    23 components and 58 palette entries on the demo project.
    """
    content, settings = [], []
    seen_content, seen_settings = set(), set()
    for palette in palettes:
        for entry in palette["entries"]:
            alias = entry.get("content")
            if alias and alias.lower() not in seen_content:
                seen_content.add(alias.lower())
                content.append(alias)
            alias = entry.get("settings")
            if alias and alias.lower() not in seen_settings:
                seen_settings.add(alias.lower())
                settings.append(alias)
    return content, settings


def _palettes_by_component(palettes):
    """Which palettes offer each content block, in palette-name order.

    Worth carrying: a block offered by one narrowly-scoped palette and a block offered by the
    page-body palette are different things to an editor, and `/block` already treats them so.
    """
    offered = {}
    for palette in sorted(palettes, key=lambda p: (p["name"], p["editor"])):
        for entry in palette["entries"]:
            alias = entry.get("content")
            if not alias:
                continue
            names = offered.setdefault(alias.lower(), [])
            if palette["name"] not in names:
                names.append(palette["name"])
    return offered


def _suffix_token(alias):
    """The trailing camelCase segment of an alias, lowercased."""
    segments = ALIAS_SEGMENT_RE.findall(alias or "")
    return segments[-1].lower() if segments else (alias or "").lower()


def _naming_convention(document_types):
    """The page-naming convention this project's own templated types demonstrate.

    Derived, never assumed. A hardcoded `Page` suffix would be a project fact in a pack that
    must carry none, and it is also wrong: it holds on one measured project and matches a fifth
    of the other's. So the suffix is measured against the types the project already marks as
    pages by giving them a template, and reported as not derived when the evidence is thin.

    `matched` counts every document type carrying the suffix, templated or not, since that is
    the number the proposal actually uses.
    """
    templated = [e for e in document_types if e["hasTemplate"]]
    count = len(templated)
    verb = "carries" if count == 1 else "carry"
    noun = "document type" if count == 1 else "document types"

    if count < MIN_TEMPLATED_FOR_CONVENTION:
        return {
            "suffix": None,
            "templated": count,
            "matched": 0,
            "why": "not derived. %d %s %s a template, and at least %d are needed to measure a "
                   "shared suffix." % (count, noun, verb, MIN_TEMPLATED_FOR_CONVENTION),
        }

    tally = {}
    for entry in templated:
        token = _suffix_token(entry["alias"])
        tally[token] = tally.get(token, 0) + 1
    # Ties broken on the token so the result does not depend on dict insertion order.
    best, hits = sorted(tally.items(), key=lambda kv: (-kv[1], kv[0]))[0]

    if hits * CONVENTION_SHARE_DENOMINATOR < count:
        return {
            "suffix": None,
            "templated": count,
            "matched": 0,
            "why": "not derived. The most common alias suffix '%s' is shared by only %d of %d "
                   "templated document types, short of half." % (best, hits, count),
        }

    matched = len([e for e in document_types if _suffix_token(e["alias"]) == best])
    return {
        "suffix": best,
        "templated": count,
        "matched": matched,
        "why": "derived. The alias suffix '%s' is shared by %d of %d templated document types."
               % (best, hits, count),
    }


def _page_types(document_types, listed, suffix):
    """Split the document types into proposed pages and the two shapes that are not.

    Reachability is computed here rather than by an adapter because it is a property of the
    whole graph: a type is reachable when something allows it as a child, or when it is allowed
    at the content root.
    """
    reachable = {e["alias"].lower() for e in listed if e["allowAtRoot"]}
    for entry in listed:
        for child in entry["children"]:
            reachable.add(child.lower())

    proposed, not_proposed = [], []
    for entry in sorted(document_types, key=lambda e: e["alias"].lower()):
        signals = []
        if entry["hasTemplate"]:
            signals.append("template")
        if suffix and _suffix_token(entry["alias"]) == suffix:
            signals.append("naming")
        if entry["alias"].lower() in reachable:
            signals.append("reachable")

        if entry["hasTemplate"] or (suffix and _suffix_token(entry["alias"]) == suffix):
            proposed.append({
                "alias": entry["alias"],
                "name": entry["name"],
                "kind": entry["kind"],
                "signals": signals,
            })
        else:
            not_proposed.append({
                "alias": entry["alias"],
                "name": entry["name"],
                "reason": (REASON_CONTAINER if "reachable" in signals else REASON_BASE),
                "signals": signals,
            })
    return proposed, not_proposed


# ---------------------------------------------------------------------------
# The report
# ---------------------------------------------------------------------------



def report(doc):
    """The human report: every count, and the rule that produced it, beside each other.

    Counts and rules always print; item lists and the excluded subsections print only when they
    have something in them. A healthy project therefore gets a report that is short without
    being silent about how it decided.
    """
    lines = []
    lines.append("Inventory of documentable units, read at the %s rung." % doc["rung"])
    lines.append("  %d content %s read: %d %s the element-type flag, %d %s."
                 % (doc["contentTypesRead"],
                    rpt.plural(doc["contentTypesRead"], "type", "types"),
                    doc["elementFlagged"],
                    rpt.plural(doc["elementFlagged"], "carries", "carry"),
                    doc["documentTypesRead"],
                    rpt.plural(doc["documentTypesRead"], "does not", "do not")))
    lines.append("  %d block-editor data %s %s a block list."
                 % (doc["palettesRead"],
                    rpt.plural(doc["palettesRead"], "type", "types"),
                    rpt.plural(doc["palettesRead"], "carries", "carry")))

    lines.append("")
    lines.append("%s: %d" % (CAPTION_COMPONENTS, len(doc["components"])))
    lines.extend("  " + line for line in RULE_COMPONENTS)
    for item in doc["components"]:
        lines.append("    %s" % rpt.item(item))

    _section(lines, CAPTION_SETTINGS, RULE_SETTINGS, doc["settingsModels"])
    _section(lines, CAPTION_UNPALETTED, RULE_UNPALETTED, doc["unpalettedElementTypes"])
    # A count with no list: the whole point is that these have no readable alias to name.
    if doc.get("unresolvedPaletteEntries"):
        lines.append("")
        lines.append("  %s: %d" % (CAPTION_UNRESOLVED, doc["unresolvedPaletteEntries"]))
        for line in RULE_UNRESOLVED:
            lines.append("    %s" % line)

    lines.append("")
    lines.append("%s: %d of %d document types"
                 % (CAPTION_PAGE_TYPES, len(doc["pageTypesProposed"]),
                    doc["documentTypesRead"]))
    lines.extend("  " + line for line in RULE_PAGE_TYPES)
    # The verdict on the label line, its evidence on the next. Split on the sentence boundary
    # rather than stored as two fields: the JSON carries one readable `why`, and a consumer
    # rendering it as prose should not have to re-join two halves.
    verdict, _, detail = doc["namingConvention"]["why"].partition(". ")
    lines.append("  Naming convention: %s." % verdict)
    # Wrapped, unlike every other explanation in this report, because it is the only one whose
    # text is not fixed: the suffix in it is the project's own alias segment, so the line grows
    # with whatever a project happens to call its pages. Measured at 106 characters on one real
    # project and 138 with a plausible longer suffix, beside rule text hand-capped near 90.
    for line in textwrap.wrap(detail, rpt.WRAP_WIDTH) or [detail]:
        lines.append("    %s" % line)
    for item in doc["pageTypesProposed"]:
        lines.append("    %s: %s" % (rpt.item(item), ", ".join(item["signals"]) or "none"))

    for reason in (REASON_CONTAINER, REASON_BASE):
        held = [i for i in doc["notProposed"] if i["reason"] == reason]
        if not held:
            continue
        lines.append("")
        lines.append("  %s: %d" % (CAPTION_NOT_PROPOSED[reason], len(held)))
        lines.append("    %s" % REASON_SENTENCES[reason])
        for item in held:
            lines.append("      %s" % rpt.item(item))

    lines.append("")
    lines.append("Documentable: %d component%s + %d proposed page type%s = %d."
                 % (len(doc["components"]),
                    "" if len(doc["components"]) == 1 else "s",
                    len(doc["pageTypesProposed"]),
                    "" if len(doc["pageTypesProposed"]) == 1 else "s",
                    len(doc["components"]) + len(doc["pageTypesProposed"])))
    return "\n".join(lines)


def _section(lines, caption, rule, items):
    """One excluded subsection, printed only when it holds something.

    An empty exclusion has nothing to warn anybody about, and three headed sections reading
    zero would train a reader to skip the part of the report that carries the counts.
    """
    if not items:
        return
    lines.append("")
    lines.append("  %s: %d" % (caption, len(items)))
    lines.extend("    " + line for line in rule)
    for item in items:
        lines.append("      %s" % rpt.item(item))


