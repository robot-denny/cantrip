# Intended revisions to `spec.md`

_Captured 2026-08-24 from a review conversation held after the spec was written. **Not a new spec** —
a change list for revising `_work/shipped/editor-facing-guides/spec.md` and the draft feature doc at
`_features/editor-guides.md`._

Read `spec.md` and `discovery.md` first. Everything here either changes something in them or closes
something they left open. Where a decision contradicts discovery, that is deliberate and the reason
is given.

**Two files need editing, not one.** The draft feature doc carries the same scenarios as the spec, so
every scenario change below applies to both.

---

## 1. The major change: one guide per component

**The component guide and the how-to guide merge into a single page per component.** What remains of
the "component guide" is a browsable index that lists what exists and links to each guide.

**Driver:** the QA lead's preference, on three grounds — page weight (twenty components at three
variations each is sixty rendered blocks on one page), cumbersome UX once components have variations,
and the value of linking directly to one component for UAT, training, and reference.

**This is a deliberate revision to story 2 as originally stated.** The original wording — "a component
guide page that puts blocks and their variations on a page alongside rich-text descriptions" —
describes the single large page. The merged shape serves the same intent (editors can see what is
available and what each does) in a different form. Recorded so it reads as a decision rather than a
drift.

### What it edits

| Location | Change |
|---|---|
| Summary, governing bullet 2 | "One extraction, two renderings" becomes **one extraction, one rendering**. The drift-prevention rationale disappears rather than being solved — there is only one place for the purpose sentence to live |
| Functional Requirements → The dossier, final bullet | Replace the two-renderings requirement with a single per-component page |
| AC 2 | Becomes the **index**: a browsable list of every guide, grouped by kind |
| AC 3 | Becomes the **merged per-component page**: purpose, when-to-use, live examples, full property tables |
| Scenario "The purpose sentence is identical in both places" | **Obsolete — remove.** It existed to prove drift-prevention between two artifacts that no longer both exist |
| Functional Requirements → The audit | Simplifies: "documented by the component guide, or a how-to guide, or neither" becomes "has a guide page or does not" |
| Open Questions → anchors/collisions | Largely dissolves. Cross-component linking becomes URL linking and the CMS already enforces unique sibling addresses, so "Hero" and "Hero (Dark)" stop being a generator problem. Anchors are still needed *within* a page for tabs, groups, and variations |

**Net effect: the spec gets smaller.** No new concepts; several removed.

---

## 2. Variations

- **The unit of documentation is the component, not the variation.** Variations are content within a
  component's page.
- **Consequence: the audit keeps counting components, so every existing audit scenario survives
  unchanged.** This was expected to force a rewrite and does not.
- Variations are shown as **live block instances** on the component's page, one per variation.
- **Enumerable variants are derivable from the dossier already specified.** Where a variation is a
  value of a variant or style property, the dossier's option lists (with defaults) already carry the
  set — so seeding one instance per variant needs no new source and no new machinery.
- **Two cases where that breaks, both worth naming in Possible Edge Cases:**
  - Variations expressed as *separate element types* are not variations — they are separate
    components, each with its own guide.
  - Variations as *combinations of independent toggles* are combinatorial and not enumerable. Seed
    one default instance; a human curates which combinations are worth showing.
- All seeded instances are **seeded-once**. The audit reports when a variant set changes; it never
  replaces an arrangement.

---

## 3. Live example vs screenshot vs thumbnail

The spec uses "live example" without defining it, which is readable as a rendered image. Tighten it.

| Concept | Definition | Who creates it |
|---|---|---|
| **Live example** | An actual instance of the block, placed in the page's content area and rendered by the site like any other block | Seeded once by the tooling, then editor territory |
| **Screenshot** | An uploaded image | **Human, always.** The tooling never generates or writes media |
| **Thumbnail** | A small representative image for browsing a visual gallery | Does not currently exist — see Open Questions |

**Why screenshots exist at all**, given the live block is present: they are complements, not
alternatives. A live example shows front-end output; a screenshot covers what cannot be rendered live
— a backoffice property panel, a settings screen, a workflow step. Prior art seeds a block instance
for block-kind features and leaves the content area empty for global features, then suggests a human
add a screenshot for exactly those.

**AC 2/3 wording:** say explicitly that a live example is an instance of the block added as content,
not generated media.

---

## 4. Where guides live, and how rigid the naming is

- **The location slot stores the node's key, not its route.** This is the single decision that keeps
  the section's name, URL, and tree position free permanently. A route-based slot would break the
  moment an editor renames the section, locking the name by accident.
- **Detect on type, never on name.** A project may already have a "Guides" folder for something
  unrelated — citizen-facing PDF downloads, for instance. Matching on the word would wrongly adopt
  it. Look for a node containing pages of the guide type; if none exists, ask.
- **The tooling never creates a public URL without confirmation.**
- **What is rigid, and what is not:**

| | Visible to | Rigidity |
|---|---|---|
| Node name in the tree | Editors | Free, permanently — rename at any stage |
| URL segment | Visitors | Free until someone links to it |
| Tree position | Editors | Free, permanently |
| **Document type aliases** | Nobody | **Fixed — the only rigid thing** |

- **The alias is a slot with a default, not a constant.** A project may already use `guidePage` for
  something unrelated, and two types cannot share an alias. Standard name normally, prefixed
  alternative when taken, recorded either way.
- **Governing principle, worth stating in the spec: conform where it shows, standardize where it does
  not.** Markup must match the project because it is visible; schema should be predictable because it
  is not, and one shape is what lets a shared reference describe one thing.

---

## 5. One document type for every guide, including editorial ones

Hand-authored guides that document nothing in code — image sizing standards, cross-system syncing —
use **the same `howToGuidePage` type** as generated guides. All three audit directions are already
safe with this, because the orphan check fires only on guides that claim a source.

**The refinement this forces:**

- **Ownership is a property of the page's provenance, not of the field's declaration.** A page
  carrying a stored source reference has machine-owned fields; a page with no stored reference has
  none — every field on it is human-owned. The spec currently declares ownership per field, which
  cannot describe both kinds on one type.
- **Machine-populated fields must be optional.** If the stored-reference field is mandatory, an
  editor cannot hand-create a guide in the backoffice at all.
- **Matching is by stored reference, never by address.** This closes an open question by ruling out
  the alternative: with address matching, an editorial guide named "How to use image sizing" occupies
  the address a future `imageSizing` component would claim, and the tooling would adopt and overwrite
  someone's work.
- **The stored reference records: alias, kind, signature, extraction rung.** Kind is recorded at
  generation time so the index does not have to resolve aliases against the schema at render time.
- **An adoption path exists and is worth specifying.** A human writes a guide for a component before
  the tooling covers it; later the tooling finds an existing page with no stored reference, offers to
  add the property tables as a diff, keeps the human's prose, and writes a reference only on
  approval. This path only exists with one document type — with two, adoption would mean changing a
  page's document type.
- **One transient oddity, worth a line rather than a fix:** a hand-written guide *about a component*
  reads as editorial on the index while the audit reports that component as undocumented. Both are
  accurate; adoption resolves it.

---

## 6. The index page

- **Dynamic, derived at render time. Never seeded, never hand-maintained.** No signature, no
  ownership declaration, no audit coverage — there is nothing that can be stale. Publish a guide and
  it appears; delete one and it is gone. Prior art already derives a table of contents this way, with
  a scenario asserting it updates "without a code change".
- **It lists three kinds:** components, code-driven page types, and editorial guides. Kind comes from
  the stored reference (§5), which is why the reference records it.
- **Editorial control lives on the guide page, not on the index.** Hiding uses the visibility
  composition already specified; promoting uses the CMS sort order; wording comes from the guide's
  purpose sentence, with an optional short-blurb override field on the guide if one is ever wanted.
  Every lever sits where the editor already is, and none can disagree with the guide it describes.
- **The index page itself has no machine-owned fields** — human framing copy plus a derived list.
  Prior art describes its landing page as editor-composed pathways.
- **Grouping is by kind, in the content tree — not merely visually on the listing.** Thirty-plus
  siblings in creation order is the mess this avoids, and the backoffice navigation cost is paid daily
  by the people this feature is for. A reference project already does this, separating blocks from
  page types in its URL structure.
- **Mechanism, consistent with §4: a small container document type marked with its kind**, found as a
  child of the one guides pointer. This keeps the configuration at one slot rather than three, with no
  name matching.
- **Do not specify ordering within a group.** The CMS already provides sort order and promoting
  frequently-used guides is editor judgment — consistent with the ownership principle.
- **Markup cost is low.** Listing children with a title and summary is the most common pattern in any
  CMS site, so an exemplar is near-guaranteed — unlike the token-reading swatch blocks, which have no
  analogue anywhere.

---

## 7. Umbraco terminology, and a correction to discovery's cost gradient

**One concept: Document Type.** "Page type" is informal shorthand for a document type used as a page.
The same concept fills several roles — page (template and URL), element type (`isElement`, rendered by
a partial), composition, and container. One serialization format writes separate filenames for two of
these; another writes both to one folder distinguished by a flag, which shows the underlying truth.

This is why the spec says "a block or a page type": extraction reads both roles with the same parser
and produces the same dossier.

**The correction:** discovery's cost gradient says only the styleguide needs an established design
system. That is too clean. Every *page* type needs a template, and a template is markup — so the guide
page types need exemplars too. The real line is **copying a structure that already exists** (cheap; any
project with pages demonstrates a rich-text body and a block area) versus **inventing rendering that
does not exist anywhere** (the token-reading swatch blocks). The greenfield guard therefore applies
more broadly than the spec implies, at lower intensity.

---

## 8. Open questions now closed

| Question | Resolution |
|---|---|
| How a guide is matched to its feature | **Stored reference, never address.** Forced by the editorial-guide collision case (§5) |
| Whether the inventory widens to page types | **Yes** — page types are a listed kind with their own guides |
| Whether a variation is a documented unit | **No** — the component is the unit (§2) |
| One large component guide page or several | **Per-component pages plus a derived index** (§1) |
| Whether editorial guides need their own type | **No** — one type, provenance carried by the stored reference (§5) |

---

## 9. Still open

Carried forward, unchanged:

- Which serialization format versions the adapter supports, and how it refuses an unrecognized one.
- Whether the styleguide is a spell or a reference.
- The audit's exact output contract — categories, exit behavior, rung statement rendering.
- Overlap with the planned test spell.
- How voice and tone guidance is discovered.
- Whether all four stories ship as one increment; the styleguide remains the cut line.

Raised in this conversation and **not** resolved:

- **Does a browsable visual gallery matter enough to keep?** The merged shape removes the page where
  twenty components rendered side by side answered "what could I put here?" — a question a text index
  does not answer. The only version surviving the performance objection is a thumbnail image per
  component, human-uploaded, shown on the index. That is a field on the page type, so it is cheaper to
  decide now than to add later. **Asked and not answered.**
- **Where degraded file output lands** when there is no CMS connection to write to. The workflow
  layout forces a durable-versus-temporal choice and guides-rendered-to-files sit awkwardly between
  them, being a staging artifact.
- **Whether creating a document type is confirmed rather than silent.** Proposed; not explicitly
  agreed.

---

## 10. Editing checklist

1. Summary → governing bullet 2: two renderings becomes one.
2. Functional Requirements → The dossier: single per-component page; stored reference records alias,
   kind, signature, rung.
3. Functional Requirements → new subsection for the index page (derived, not generated).
4. Functional Requirements → Content ownership: ownership follows page provenance, not field
   declaration; machine fields optional; matching by stored reference; adoption path.
5. Functional Requirements → The audit: single-question form; drop the two-artifact phrasing.
6. Functional Requirements → Rendering: add "conform where it shows, standardize where it does not";
   extend the greenfield guard to page templates at lower intensity.
7. Functional Requirements → new subsection or additions covering location by key, detect-on-type,
   alias-as-slot-with-default, grouping by kind in the tree via a container type.
8. Possible Edge Cases → add: separate element types are not variations; combinatorial variations are
   not enumerable; an existing unrelated guides folder; an alias already taken; a hand-written guide
   awaiting adoption.
9. Acceptance Criteria → rewrite 2 and 3 per §1; define "live example" per §3.
10. Scenarios → remove "The purpose sentence is identical in both places"; add scenarios for
    variation seeding, adoption of a hand-written guide, the derived index, and grouping by kind.
11. Open Questions → move the five closed items out with their resolutions; add the three unresolved
    items from §9.
12. **Mirror every scenario change into `_features/editor-guides.md`**, including its Test Coverage
    table rows.
