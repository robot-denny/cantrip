---
name: umbraco-17-guide-scaffolding
description: The schema an editor-facing guides section needs in Umbraco 17 — the single guide document type that serves generated and hand-authored guides alike, the property-row element type and which of its six columns tooling may write, the stored source reference, and why ownership follows a page's provenance rather than a field's declaration. Consult when creating or changing a guides section's document types, when deciding whether a value on a guide page may be overwritten, or when building anything that reads or writes editor-facing guide pages.
---

# Guide scaffolding: the document types a guides section needs

The schema half of an editor-facing guides section: which document types exist, which fields sit on
each, and which of those fields a tool may write. More than one unit needs this — the spell that
generates guides, and anything that later renders or maintains them — so it is described once here
and cited rather than restated.

**Every alias below is a default, not a constant.** Two document types cannot share an alias, and a
project may already be using one of these names for something unrelated, so each name is a slot
whose default is the value given here. Which aliases a project actually used is a project fact and
belongs in that project's `.agents/config/conventions.md`, never in this file.

## The document types

| Alias | Kind | What it is |
|---|---|---|
| `editorGuide` | document type with a template | One guide. One per documented component or page type — and the same type a hand-authored editorial guide uses |
| `editorGuidePropertyRow` | element type | One row of a guide's property table: one field as an editor meets it |
| `editorGuideGroup` | document type | A container marking one kind of guide, carrying a `guideKind` value |
| `editorGuideIndex` | document type with a template | The section's landing page, whose list of guides is derived at render time |

**Four types, and the two that are absent are absent on purpose.** There is no per-tab or per-group
container — a guide's property rows are flat and the template does the grouping — and there is no
stored index list, because the index derives its own.

## The guide page

**One document type serves every guide, whoever wrote it.** A page's provenance is the presence of a
stored reference, not its type (see *Ownership is a consequence of provenance* below). Splitting
generated guides from editorial ones into two types would buy nothing and cost three things: two
templates to keep from drifting, an index that has to read both, and an adoption path that becomes a
retype instead of the write of a single property.

**Every machine-populated field is optional on the document type, the stored reference included.**
Three reasons, and each is a state a mandatory field would make unrepresentable:

- An editor must be able to create a guide with nothing on it but a name, and finish it by hand.
- A generated page is created before anything is generated into it — every write happens after a
  person approves it — so the page has to be saveable while those fields are still empty.
- A page carrying no reference is the signal for "nobody generated this". A required reference erases
  the one fact that distinguishes a hand-authored guide from a stale one.

### The field set

**The field set is declared in exactly one place, and it is not this file.** It is `REGISTER` in the
`guide` spell's `scripts/guidelib/changeplan.py`, which names every field the tooling can write, the
ownership class each one is in, and what each is for. Read it there. A second copy here would be a
second thing to be wrong about which field an editor's work lives in, and being wrong about that
costs somebody their writing.

What a document type needs and the register does not carry is the property editor each field takes.

**The third column is a worked example, not a rule.** It is how one shipped guides section renders
these fields, written down because a project starting from nothing is better off knowing what worked
somewhere than guessing. This pack ships no template, no markup and no class names — a project's own
components decide the rendering — so nothing in that column is a behaviour this pack can be held to,
and a project that renders these fields differently is not doing it wrong.

**Read ownership from the register, never from this table's silence.** Only editor shape and that
example are below. A row that says nothing about who may write the field leaves the question to
`REGISTER`; it is not a row promising the tooling stays out.

| The field | Editor shape | Rendered, in one implementation |
|---|---|---|
| the purpose sentence | rich text | One sentence, first on the page. The index reuses this wording unless a blurb overrides it. **One sentence is what the seeding writes, not a length the field enforces** — an editor can write more, and the index inherits whatever they wrote |
| the when-to-use section | rich text | A *How It Works* section on a component guide; a tip callout on a page-type guide |
| the property rows | a list of `editorGuidePropertyRow` items | Grouped by tab and group **by the template**, never by the stored shape |
| the live examples | the page's own content area | Real instances of the documented component, rendered by the site like any other content |
| the screenshots | media | Shown beside the prose they illustrate — a property panel, a settings screen, something a live example cannot show |
| the index blurb | short text | Optional, and an override of the index's wording only — it changes nothing on the guide itself |

**Screenshots carry their own text alternative, and a guide's template renders it.** A screenshot
here is documentary content rather than decoration — it is often the only place a property panel or a
settings screen appears — so the media item it points at is required to carry alt text. This is a
requirement on the media type and the template, not a field on the guide page: an alternative stored
beside one page's reference would go stale the moment the same screenshot is reused on another, and
nothing in this toolkit generates media or could supply the words for it. It is also the one field
here whose accessibility no later stage can recover, because the person who uploads the image is the
last one who knows what it shows.

## The property row element type

`editorGuidePropertyRow` carries six fields, and **ownership is stated per column rather than per
row**:

| Field | Editor shape | Ownership |
|---|---|---|
| `alias` | text | Machine-owned, and the row's identity |
| `label` | text | Machine-owned |
| `required` | true/false | Machine-owned |
| `tab` | text | Machine-owned |
| `group` | text | Machine-owned |
| `information` | rich text | **Seeded-once** — a person's prose from the moment it is written |

- **The alias is the identity, so it is never rewritten in place.** Rows are matched on the alias,
  case-folded: a label changes, a tab moves, and it is still the same field an editor fills in. A
  changed *alias* is therefore one removed row and one added row, which is the honest reading — the
  field an editor was matching against is gone.
- **Four columns are compared, not five.** `ROW_MACHINE_COLUMNS` in `changeplan.py` holds `label`,
  `required`, `tab`, `group`; the alias is excluded because it is the join key, and `information` is
  excluded because nothing here proposes a value for it.
- **Rows are flat, each carrying its own `tab` and `group` as fields.** So a property moving between
  tabs is a field change on one row rather than a row migrating between nested containers — a smaller
  diff and a smaller schema both.
- **`information` is never compared, never proposed, and never overwritten.** Option lists and
  recommendations belong inside this prose, not in structured sub-fields: no serialization format
  records an option's default, so a structured option field could only ever carry one by inventing
  it. The prose can say `(Default)` because a person put it there.
- **A row's removal is reported, never applied silently, where the row carries an information note.**
  A row can only disappear if somebody's writing disappears with it, so each removal states whether
  a note is present and the decision stays with the person who wrote it.

**Why the table is structured rows and not markup in one rich-text field.** Three reasons, in order
of weight. The second is argued at `compare_rows` in the `guide` spell's
`scripts/guidelib/changeplan.py`, which carries the figures beside the code that produces them; the
first and third are stated here because this file is the only place they are written down.

1. **Ownership works per column instead of per field.** Five columns carry no human writing and
   update freely; the sixth is prose and is seeded once. One rich-text field cannot be half-owned, so
   it would have to be owned by whichever of the two is worse to lose.
2. **A person gets a summary instead of a diff of markup.** Keyed on the alias, a comparison is
   added / removed / changed / unchanged. Compared as one field it is rendered markup beside a list
   of rows — on a real page type roughly sixty lines against nineteen — and an approval nobody can
   read is approval theatre.
3. **A design change is one template edit rather than one edit per guide page.**

## The stored reference

`guideSource` records what a guide was generated from, in four values:

| Value | What it is for |
|---|---|
| alias | The component or page type this guide documents. Matched case-folded; a page whose reference names a different component than the one being planned for is refused, never overwritten |
| kind | What sort of thing was documented, so the index can group guides without matching on names. Opaque — nothing compares it |
| source signature | A hash over the schema-bearing part of the source's shape. **Opaque text: compared, never parsed** — the format belongs to the extractor. An equal signature means the source has not changed shape, which is the entire basis of a no-op run |
| rung | Which adapter produced the signature — `deploy`, `usync`, `models`, `live`. Recorded because two rungs sign one component differently by design, so a signature stored at another rung is *not comparable*, and an incomparable signature proposes rather than assuming a no-op |

**The reference is stored once.** A page states it in one property and nowhere else: two copies of
one value can disagree, and nothing downstream can tell which was written last.

**No reference and no answer are different facts.** A page that carries no reference says so
explicitly; a producer that failed to read the property says nothing at all. Collapsing the two turns
a failed read into "every guide here was written by hand" — so a read that produced nothing is
refused, and an explicit "none" is read as a hand-authored page.

## Ownership is a consequence of provenance

**A field's declaration does not say who owns its value; the page's provenance does.** The model is
implemented in the `guide` spell's `scripts/guidelib/changeplan.py`, whose module docstring argues it
beside the code that acts on it — read that where the two seem to differ, because the code is what
runs. On a page carrying a stored reference, every field the tooling can write is in exactly one
class:

| Class | What it means |
|---|---|
| Machine-owned | Regenerated when the source signature changes, presented as a difference, and written only after a person approves it |
| Seeded-once | Written when the page was created and never touched again. Reported when it may have gone stale, never replaced |
| Never-touched | The page's name, address and visibility settings, the editorial levers, the media a person uploaded, and every field the register does not name |

**On a page carrying no reference there are no machine-owned fields at all.** Nothing on it was
generated, so nothing on it is the tooling's to replace: every field is human-owned, whichever class
the register puts it in. That is the fourth class, and it is the only one a page can put every field
in at once — no field is declared human-owned, a *page* is. Ownership declared per field could not
describe both kinds of page on one document type, which is why one document type is enough.

So the register is read for **what a field is for**, and never for permission to write it.

**The classes apply per column inside a row, not only per field.** One `editorGuidePropertyRow` is
machine-owned in five columns and seeded-once in the sixth, at the same time — which is the property
that lets a table's shape track the schema while the notes in it stay untouched.

**Adopting a hand-authored page is a write of one property, and it changes what every later run may
do.** Such a page has no rows, so the whole table is offered as a difference in which every row is
added — the honest answer, because the table does not exist yet. Approving the reference is what
makes that page's machine-owned columns machine-owned from then on, so it is the one approval on a
guide page that is not undone by editing.
