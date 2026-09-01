---
name: umbraco-17-guide-scaffolding
description: The schema an editor-facing guides section needs in Umbraco 17 — the single guide document type that serves generated and hand-authored guides alike, the property-row element type and which of its six columns tooling may write, the showcase element types a token-reading styleguide page is built from, the stored source reference, and why ownership follows a page's provenance rather than a field's declaration. Consult when creating or changing a guides section's document types, when scaffolding or rendering a styleguide page, when deciding whether a value on a guide page may be overwritten, or when building anything that reads or writes editor-facing guide pages.
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
| `styleguideColorSwatch` | element type | One color from the palette, on a styleguide page: the token's name, never its value |
| `styleguideTypeSpecimen` | element type | One level of the type scale, set from the token that defines it |
| `styleguideElementSpecimen` | element type | The common elements — buttons, links, lists, tables, blockquotes, form fields — rendered as themselves |

**Seven types, and the two that are absent are absent on purpose.** There is no per-tab or per-group
container — a guide's property rows are flat and the template does the grouping — and there is no
stored index list, because the index derives its own.

**The last three are the styleguide's, and a section holding no styleguide holds none of them.** They
are showcase elements a styleguide page's content area carries, created when a styleguide is first
scaffolded and not before — so a guides section is complete at four, and *The showcase element types*
below says what the other three are for. They are listed in the roster rather than kept in a table of
their own because they are element types in the same section, subject to the same rule about aliases
being defaults, and a second roster is a second place for a project's alias to be recorded wrongly.

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

## The showcase element types

A styleguide is a guide page like any other — an `editorGuide` under a kind container, carrying no
stored reference, so every field on it is human-owned (see *Ownership is a consequence of
provenance*) and the audit has nothing to say about it in any of its three sections. What makes it a
styleguide is what its content area holds: showcase elements, each demonstrating part of the design
system rather than describing a component.

| Alias | What it shows | What it stores |
|---|---|---|
| `styleguideColorSwatch` | one color from the palette | the token's name, and an optional caption |
| `styleguideTypeSpecimen` | one level of the type scale | the token's name, the sample words to set in it, and an optional caption |
| `styleguideElementSpecimen` | the common elements an editor can produce — buttons, links, lists, tables, blockquotes, form fields | which of them to include, and an optional caption |

**The caption is optional on every one of the three, and it is the only editorial field a showcase
element has.** It is where a person says what a token is *for* — "page background", "the only red
that may sit under body text" — which no token name carries and no generated page can invent. Being
optional is what keeps a scaffolded page saveable before anybody has written one, the same reason
every machine-populated field on a guide page is optional. Nothing regenerates it, and nothing is
reported when it is empty.

It also gives a form-field specimen somewhere to take a visible label from, which is the one case
where an empty caption costs more than a missing sentence — see *A specimen keeps the semantics of
what it shows* below.

**A showcase element stores a name, never a value.** That is the whole of the schema decision here,
and the rest of this section follows from it. A swatch storing a hex literal is a copy of the palette
that stops agreeing with it the day somebody re-themes, and it looks entirely correct while it
disagrees — a wrong brand color rendered confidently. A swatch storing the token's name is a question
the browser answers on every render, which is what "the page reads the system live" has to mean if it
means anything. So no showcase field holds a color, a length, a font stack, or any other resolved
value. It is also why the third type names no token at all: the common elements are styled by the
project's own stylesheet wherever they appear, so listing them *is* showing them.

**This pack ships no view for any of the three.** The element type and its fields are the schema; the
markup that renders one belongs to the project, written by following the conventions of its closest
existing block, exactly as the property table's rendering is left to a project's own template (see
*The field set*). Where a project has no block to follow there is nothing to inherit, and nothing
here supplies a substitute — that is a stop for whatever is doing the writing, not a gap in this
schema.

**Themes need no property, and adding one would be the mistake.** A view rendering a token resolves
it wherever it is placed, so a swatch inside a themed region shows that theme's color with nothing
configured on the element at all: re-theming a region is the project's own CSS re-pointing what the
name means, and a showcase that stores names is already downstream of that. A per-theme value
property would put a second answer beside the browser's, and the two disagree the first time a theme
is edited. The themed region itself comes from whatever mechanism the project already uses to theme a
block — a setting on the block, a wrapper, a section class — which a showcase inherits the same way
it inherits spacing and visibility.

**How a page presents several themes at once is deliberately not settled here.** A project carrying
many themes is under-served by a showcase that renders one and implies there are no others, and
whether the answer is a section per theme, a switcher, or one representative with the set named
beside it depends on how that project themes things at all. That is a decision for whoever generates
the page, taken from the project's own mechanism; a rule written here would be fitted to whichever
project was in front of the person writing it.

**Nor is how many swatches a page should carry.** A measured palette runs to a few hundred tokens
once every step of every ramp is counted, and a page with one swatch per token is a content area of
that size — which renders perfectly well and reads badly. Whether a styleguide shows every token, one
per ramp, or only the ones a person picks from is an editorial decision belonging to whoever arranges
the page; the schema puts no ceiling on it and no expectation either.

**A swatch is never identified by its color alone.** The view renders the token's name as text
beside the color, on every swatch, whether or not the token resolves — and the caption too where a
person wrote one. A grid of colored squares tells a reader with normal color vision roughly what the
palette looks like and tells everybody else nothing: not which token to use, not what distinguishes
two blues, not whether the swatch in front of them is the one the copy refers to. A styleguide is
read to answer *which name do I write*, and a page that shows only the answer's color has not
answered it. This is the same requirement WCAG states as not conveying information by color alone,
arriving here for an ordinary reason rather than a compliance one: the name is the content, and the
color is the illustration.

**A showcase view must name a token it cannot resolve.** A token gets retired, and the swatch reading
it renders nothing — one empty box among the full ones, which reads as a design decision rather
than as a fault, and which nobody reports because nothing looks broken. What the view must do instead
is print the name it was given, so the page says *this token is gone* in the one place somebody is
looking at the palette. This is a constraint of exactly the shape *The index page*'s
render-as-text-never-as-markup rule is: a requirement on what a project's own component does, stated
here because this is where the requirement is known, and **enforced nowhere** — this pack ships no
view, so nothing in it can check that a project's view honors it. It is written down so a page
failing it fails a review rather than a run.

**A specimen keeps the semantics of what it shows.** A button specimen renders buttons, a form-field
specimen renders labelled fields, a table specimen renders a table with its header cells marked as
header cells. The elements are shown *as themselves*, which means as the elements — not as styled
`div`s that happen to look like them, and not as a screenshot of the real thing. Two reasons, and the
second is the one that makes this a rule rather than a preference:

- A specimen rendered without its semantics is a lie about the system. It shows what a button looks
  like while demonstrating something that is not a button, and the page it appears on is the page a
  team consults to find out what the system does.
- **A styleguide is an exemplar, and exemplars are copied.** The greenfield refusal elsewhere in this
  capability exists because the first thing in a project sets its conventions whether or not anybody
  decided to — and a showcase page full of unlabelled inputs and `div`-buttons is a pattern that
  propagates into every block written after it. A specimen that gets this wrong is not one
  inaccessible page; it is the source every later page copies.

A form field's label is the case with nowhere else to come from, which is what the optional caption
above is for. This is a requirement on a project's own view and **enforced nowhere**, exactly like
the constraint below and the index's render-as-text rule — this pack ships no markup, so nothing in
it can check that a project's specimen honors it. It is written down so a page failing it fails a
review.

**The three are registered in a palette of their own, and the audit is told that palette's name.**
They are element types an editor can place, which is the audit's own definition of a documentable
unit (see *The audit's report shape*), so a showcase element sitting in a general block palette
becomes a component the audit reports as undocumented — on every run, forever, for a color swatch
nobody is going to write a guide page about. The remedy is one recorded name: the `## Editor guides`
slot below carries the palette, the documentable count leaves that palette's entries out, and the
report says which palette was excluded. **An exclusion that changed a count silently would be worse
than the wrong line it fixes**, which is why the naming is a report line and not an implementation
detail.

**Both readings of the project take the exclusion, and that is worth stating because they are two
readings.** The inventory report and the audit each build a documentable count — the audit derives
its own rather than borrowing the inventory's, so an exclusion wired into one of them is absent from
the other. An implementer who fixes only the inventory leaves the audit reporting showcase elements
as undocumented forever, which is the whole of the problem this row exists to solve, while every
test of the inventory passes. Where the audit is handed a prepared inventory instead of deriving
one, it inherits whatever that inventory excluded; where it derives its own, it must be told the
same palette name. **The exclusion belongs to reading the project, not to one command.**

**A project that has not recorded the palette gets a wrong line, not a wrong count** — its showcases
reported as undocumented, which is visible and has a one-line fix. Why the exclusion never falls back
to the default name is argued at the slot itself, beside the row that carries it.

## The stored reference

`guideSource` records what a guide was generated from, in four values:

| Value | What it is for |
|---|---|
| alias | The component or page type this guide documents. Matched case-folded; a page whose reference names a different component than the one being planned for is refused, never overwritten |
| kind | What sort of thing was documented, recorded at generation time so nothing has to re-derive it from the schema later. Opaque — nothing compares it, and it is **not** what the index groups by (see *Where guides live*) |
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

## Where guides live

**One pointer, and it is a key.** A project records its guides node by the **stored key** the CMS
assigned it — in the `## Editor guides` slot below — never by route and never by path. A guides
section is exactly the node an editor renames in its first week and moves under a different parent
when the tree is reorganized; both change its route and neither changes its key. A tool that finds
guides by route reports an empty guides section on the day somebody tidies the tree, which is the
silent-empty failure this pack refuses everywhere else.

**The node at that key is the index page itself.** It is an `editorGuideIndex`, not a folder holding
one: the roster above names seven types and none of them is a bare container, because a landing page
that holds its own children is one node where two would be a node nobody renders and a node nobody
can link to. So the recorded key is also the thing a main-nav entry points at, and resolving it is
the whole of "find the guides section".

**Under that node sit the kind containers, and everything below is reached by walking.**
`editorGuideGroup` marks one kind of guide and carries a `guideKind` value; guide pages are its
children. So the whole read is the node at the recorded key, its children, and their children — no
path, no route, and no search. **That walk is also where the index gets its list** — there is no
other source, and *The index page* below scopes what it reads from each guide it finds.

**Containers and guide pages are matched on their document type, never on their name.** Three
reasons, and the first two are ordinary editorial life:

- A container's name is copy. It is written to be read by editors, and it gets rewritten.
- Under culture variants there is a name per language, so "the name" is not one value to match.
- A name match can succeed on the *wrong* node. Inside the guides section that is a container an
  editor added and named like a kind, or a guide page named after the kind it sits under — and
  writing into an unrelated node is worse than finding nothing, because finding nothing is
  reportable. The root lookup is already safe from this: it is a key, not a name.

**`guideKind` is the grouping the index reads; `guideSource`'s kind is what the generator recorded.**
They will normally agree, and nothing reconciles them: the stored reference's kind is opaque (see
*The stored reference*), and the container a page actually sits under is where that page appears. So
a guide moved between containers is regrouped by the move alone — no field to update, and no run
needed to make it true.

**A kind with no container is a container to create, not a name to go looking for.** Where no child
of the guides node carries the kind, that container does not exist yet. Falling back to a
similarly-named node is how a guide ends up filed under something unrelated.

**Two containers carrying one kind is reported, and nothing picks between them.** It is a legitimate
state — an editor can create a second container and an import can produce one — and choosing the
first found would file guides into whichever node happened to sort earlier, silently and differently
between runs. So a tool says which kind is duplicated and stops writing into that kind, the same
answer this pack gives a duplicate alias anywhere else: an ambiguity a person can resolve in a minute
is not one a tool should resolve by accident.

## The index page

`editorGuideIndex` is the section's landing page, and **it derives its list at render time**.

**It carries no machine-owned fields and no stored list of guides.** A stored list is a second copy
of the tree, wrong from the moment an editor adds, renames, unpublishes or reorders a guide — so the
index would need a regeneration run to be correct and would be quietly incorrect between runs.
Derived, publishing a guide is the whole of adding it to the index. It follows that an index page
carries no `guideSource` either: nothing generated it, so there is nothing to record.

**The editorial levers live on the guide page, not on the index** — the index blurb (`guideBlurb`),
the guide's own name, and its sort order among its siblings. Two reasons. A lever on the index is a
second place to edit one thing, and it is the place an editor looking at a guide will not think to
open. And a lever on the guide travels with the guide when it moves to another container.

### What the index reads per guide

**Three values, and the scope is a requirement rather than an optimization: the guide's name, its
URL, and the blurb-or-purpose line.** Explicitly **not** the property rows, and **not** the live
examples.

A derived index built the obvious way asks each listed guide for its content and takes what it needs
for a teaser — which resolves every listed guide's whole content model, property rows included. On
forty guides of twenty rows that is **eight hundred row objects materialized on every render of a
public page**, plus every live example each guide carries, to print forty names and forty sentences.
Scoped to three values it is one cheap read per guide. That is the difference one sentence in a
template makes, and it is the reason the sentence is written down here.

The blurb-or-purpose line is the blurb where a guide carries one and the purpose sentence otherwise
(see *The field set*) — one field either way, never both, and never the rest of the page.

**The index renders that line as text, never as markup.** The purpose sentence is rich text and its
length is not enforced (see *The field set*), so what arrives may carry paragraphs, lists or a link.
An index entry is normally itself a link to the guide, and a link inside a link is invalid markup
that leaves both unreachable from a keyboard and ambiguous to a screen reader. Taking the text and
truncating it is the whole fix, and it belongs here because the index is the one place a guide's own
prose is rendered somewhere other than the guide.

This pack ships no template, so this is a constraint on what a project's own index component may
resolve, not markup a project has to adopt.

## The three slots a guides section needs

**All three are declared here and nowhere else.** The spells that read them and their scripts cite
this file rather than re-declaring any of them, because one slot has one point of authority: a second
declaration would have to reproduce the fallback — and the detection recipe folded into it — word for
word, and would diverge the first time one copy was edited.

**The third is needed only where the section holds a styleguide**, and a project without one can
leave it empty for as long as that stays true. It is declared here rather than beside the spell that
reads it for the reason just given: a slot's authority does not move to whichever unit happens to
read it most.

**Slot:** `.agents/config/stack.md` → `## Schema serialization`
**If empty:** detect it from what the repository holds, in fidelity order — Deploy artifacts
(`*.uda`), then a uSync export (a `usync.config` beside the serialized folders), then committed
generated models (`*.generated.cs`) — and read from the first that matches. Generated models are the
fallback rather than an alternative: they carry no tabs and no required flags, so a project holding
artifacts *and* models is read from the artifacts. A project holding none of the three can be read
only from a running instance.
**Detect:** look for all three markers rather than stopping at the first, because a project can
commit more than one and stopping early reads the fallback as the whole answer. `*.uda`
anywhere under the project means Deploy; a `usync.config` means a uSync export, and it also declares
that export's `format` version, which is the thing to gate on rather than the package version or the
folder name; `*.generated.cs` files mean models are committed rather than generated at build time.
Record every format found and which one is authoritative. A serialized folder holding no matching
file is a partial export, not an absent format.

**Slot:** `.agents/config/conventions.md` → `## Editor guides`
**If empty:** read every alias below as its default, and treat the guides node — and the showcase
palette, for the reason the table gives beside it — as **not recorded**, which is not the same as not
existing. Do not go looking for it by name — a section a project already
has is a fact to be told, and its key is one question worth asking. Until it is supplied, there is no
guides node to read and nothing may be written into one.

The slot records the guides node's key and the aliases the project actually used:

| What the slot records | Default |
|---|---|
| the guides node | **no default** — a stored key, which only the project can supply |
| guide page type | `editorGuide` |
| property row element type | `editorGuidePropertyRow` |
| kind container type | `editorGuideGroup` |
| the kind value on a container | `guideKind` |
| index page type | `editorGuideIndex` |
| stored reference property | `guideSource` |
| index blurb property | `guideBlurb` |
| showcase element types | `styleguideColorSwatch`, `styleguideTypeSpecimen`, `styleguideElementSpecimen` |
| the styleguide's showcase palette | `styleguideShowcase` **to create, never to assume** — see below |

Every row is a default, for the reason this file opens with: two document types cannot share an
alias, so a project that already used one of these names for something unrelated picked another, and
**the name it picked is the fact**. The slot records what was used, never what should be used.

**The key and the aliases share one heading because they are read together.** Anything that touches
a guide needs both — where to look and what to look for — so two headings would let one be filled
and the other forgotten, and a filled alias list against an unrecorded node reads as a configured
project that finds no guides.

**The showcase palette is the one row here that is read rather than written.** The other rows tell a
tool what to create and where; this one tells whatever counts documentable units what to leave out —
both the inventory report and the audit, which count separately (see *The showcase element types*).
It is a palette name rather than the three element aliases beside it because one name is one thing to
record, and a fourth showcase element added later inherits the exclusion without a fifth line
anywhere. **Its default is a default for creating a palette, never for assuming one.** Those look like the same
fact and are not. A tool scaffolding a styleguide with nothing recorded creates the palette under the
default name and writes back what it created, which is how the slot comes to be filled. A tool
*reading* the slot to exclude a palette and finding nothing excludes nothing — because assuming the
default on the read side would drop a palette's components from the count on a project that used that
name for something else entirely, and a count quietly too small is the one outcome the audit's report
shape refuses (see *The audit's report shape*). So a project that has not recorded the palette gets a
wrong line rather than a wrong count: its showcases are reported as undocumented, which is visible
and has a one-line fix. That is the same direction this file chose for the guides node's key — a fact
only the project can supply is asked for rather than guessed at, and its absence shows.

**Slot:** `.agents/config/stack.md` → `## Design tokens`
**If empty:** detect the token layers the repository holds and read from the authoritative one. **A
design token here is a value that survives to the browser** — in practice a CSS custom property. A
preprocessor variable is a real design token by any normal usage and is still not one of these,
because no markup can read it at render time, and reading it at render time is the whole of what a
page showing the system live has to do. **Custom properties are authoritative whenever present.**
Record every layer found and name which one is authoritative rather than stopping at the first — a
project can hold more than one, and stopping early reads a fallback as the whole answer, the same
rule `## Schema serialization` states above. **Layers of which none is readable at render time are a
stop, not a snapshot:** the read completed and the answer is negative, so what comes back is the
remedy — a runtime layer the existing definitions feed — and no token value at all. A project
holding no layer anywhere is a completed read that found nothing, which is a common starting state
rather than a failure, and it is a different answer from the refusal.
**Detect:** a `--name:` declaration in a `.css` file is the runtime layer; a `$name:` in a
`.scss`/`.sass` or an `@name:` in a `.less` is the preprocessor layer. Those two markers are the
whole vocabulary, and they are named here so this fallback is something a person can act on with a
terminal and nothing else — the way `## Schema serialization`'s markers are. What is *not* here is
the procedure: which directories are walked and skipped, how a declaration is told from a use, and
why a utility framework's theme configuration is not a layer of its own. That recipe is implemented,
and argued line by line, in the `/styleguide` spell's
`scripts/styleguide.py` — which files are walked and which are skipped, which sigil marks which
layer, why a utility framework's theme configuration is not a layer of its own, and why a
build-time-only layer is refused rather than baked (*A layer that cannot be read at render time is
refused, not baked*). Read it there. A second copy of the recipe here would be a second thing to be
wrong about, and what it would be wrong about is whether a project's swatches are live.

## The audit's report shape

The audit compares what a project's code declares against what its guides document. **Its report is
its whole interface** — there is no machine-readable form of it — so the shape is written here, once,
for the spell that renders around it and for anything that later reads it.

**Nothing in this section names a CMS, a serialization format, or a file.** That is deliberate: none
of this shape is Umbraco's, and the audit is a candidate for later extraction to the
technology-agnostic layer. Written this way, that extraction is a move rather than a rewrite.

### Three counted sections

Fixed order, one question each:

| Section | What is in it |
|---|---|
| undocumented | a documentable unit that no guide page's stored reference names |
| orphaned | a guide naming an alias the project no longer declares |
| stale | a guide whose stored signature differs from its source's current one |

**A guide claiming no source at all is in none of them.** A hand-written guide documents something
that was never in the schema, so it can be neither orphaned nor stale, and it closes no gap either.
That exclusion is functional rather than tidy: an audit reporting editorial guides as orphans would
train its reader to ignore the orphan list, which is the list whose remedy is destructive.

**A guide for something present in code but not documentable is also in none of them** — the guide
documents real schema, so it is no orphan, and the thing it documents is not a unit anyone proposed
documenting, so no gap is open. There is nothing to report and the audit says nothing.

**Every count prints; a section's explanation and its items print only when it has findings.** An
audit wired into a routine is read hundreds of times and acted on a handful, so three headed sections
of explanation reading zero would teach its reader to skip past the part carrying the counts.

### One way of naming a thing to a person

`alias (Display Name)` — and the bare alias where there is no display name to print. That is rarer
than it sounds: an orphan names the guide *page* in the parentheses, because the source it claims is
gone and the page is what an operator acts on, and a page with no name of its own is labelled rather
than left blank. What does print bare is a documentable unit the project's own types do not declare —
a block palette naming an alias nothing defines — which the inventory reports rather than refuses,
and which therefore has no name anywhere to read.

Items are sorted case-insensitively by alias, because the two inputs arrive in unrelated orders — a
project's files and a CMS's pages — and a report whose lines move between runs cannot be diffed.

### The header, and the report-level rung statement

The header states, in order: the rung the read was made at; the documentable count split into
components plus proposed page types, with the determiner's rule beside it (counted from the project's
own block-editor palettes, never from the element-type flag); the number of guide pages read, split
into those claiming a source and those claiming none; and one `Not compared:` line for each reason a
staleness comparison did not happen — the guide records no signature, the source records none, or the
guide was stored at another rung *or at none this read can name*, which is one reason rather than two
because the remedy is the same.

**The statement of what the rung cannot report is made once for the whole report, and never against a
guide.** A guide whose property table carries no required flags because its source records none is
not an incomplete guide, and twelve findings saying otherwise would be twelve pieces of work nobody
can do.

**Three fidelity answers, because there are three states and two of them used to share one:**

| Answer | What the report says |
|---|---|
| full | nothing at all. The source reports the whole structure, and a line saying so in every report is a line that gets skipped along with the ones that matter |
| partial | which fields this rung cannot report, one entry per field and keyed on the field name — a consumer filling a property table needs to know which *column* it cannot fill |
| unknown | that the rung is one this tool has no fidelity record for, so a clean result is unconfirmed rather than complete |

**Unknown is the answer that had to be added.** A rung with no record may read everything or almost
nothing, and answering "nothing missing" for it spends the same words as a source that genuinely
reports in full.

### The closing line and the exit code

The report closes on `Findings: none.` with a sentence saying what that means, or on
`Findings: N undocumented, N orphaned, N stale.`

**Exit 0 whatever it found.** Findings are a backlog, not a gate, and an audit that failed a build by
default would fail it in exactly the projects that wired the audit in early — which is how guides get
cut from scope again. A non-zero exit stays reserved for a read that could not be completed at all,
which is also why both inputs refuse a malformed entry rather than skipping it: a report with a
quietly wrong number in it is the one outcome an exit code cannot distinguish from a healthy project.

**`--strict` is the only opt-in, and the whole of it is the exit code.** The report is identical byte
for byte, computed and printed before the exit is decided, so a team that gates its build reads
exactly what a team that does not reads. Findings exit **3**, not 1: 1 means the read failed, and a
gated job that cannot tell a backlog from a broken tool sends somebody looking for guides to write.

**What counts as a finding is the three sections and nothing else.** A not-compared signature, a
duplicate stored source, and a guide documenting schema that is real but not documentable are all
facts about the read rather than work for anyone, and a gate failing on them would fail on a project
with nothing to fix.

### The shape, end to end

Counts stand in for numbers; the captions and the closing line are verbatim.

```
Guide audit, read at the <rung> rung.
  N documentable units: N components + N proposed page types.
  <the determiner's rule — always printed>
  N guide pages read: N claim a source, N claim none.
  Not compared: …                        (one line per reason, only when non-zero)

  <what this rung cannot report>         (only at a partial or unknown rung)

Undocumented, present in code with no guide page: N
  <the section's rule, then one line per item>      (only when N is not zero)

Orphaned, claiming a source this project no longer holds: N

Stale, whose stored signature no longer matches its source: N

Findings: N undocumented, N orphaned, N stale.
```
