# Spec for editor-facing-guides

> This spec captures initial requirements and design rationale. For **current system
> behavior**, see the doc named on the **Work type** line below.

branch: editor-facing-guides
design reference (if any): none — this work ships no markup by design

**Work type**: new-capability
**Feature doc**: `_features/editor-guides.md`

<!--
  Classified new-capability: nothing in the toolkit generates editor-facing guides today. The
  acceptance criteria read as standing behavior ("a QA can run the audit and see which blocks lack a
  guide"), not as transitions, which is the tell.

  The feature doc is named `editor-guides` — the area — while the increment is
  `editor-facing-guides`. They are close enough to look like derivation, so the reason is recorded:
  later increments (a fourth extraction rung, page-type inventory, a second CMS pack) amend the same
  area doc. Naming the doc for the area rather than for this increment is what lets them.

  Revised 2026-08-25 from `notes/spec-revisions.md`, after a review conversation. The substantive
  change is that the component guide and the how-to guide merged into one page per component, with a
  derived index in place of the single large page. Discovery's story 2 is deliberately restated
  rather than drifted from; the reason is in the Summary.
-->

## Summary

A team building a CMS site hand-builds its editor-facing reference and hand-maintains it afterwards.
It costs enough that it is first against the wall when scope tightens. This increment automates the
first pass from what the codebase already knows, adds an audit that reports what is undocumented,
and leaves every judgment call and every word a human wrote intact.

**Scope: stories 2–4 of discovery's four.** A browsable index, a guide page per component, and the
audit. **The styleguide — story 1 — is deferred to its own spec and the increment after this one.**
It is the only story requiring new element types, new views, and a pre-existing design system, while
the other three share one dossier and one audit; discovery named it as the cut line and nothing
since has argued otherwise. What was already decided about it is carried forward in
`notes/deferred-styleguide.md` so its spec starts from those decisions rather than re-deriving them.

Discovery is at `_work/shipped/editor-facing-guides/discovery.md` and its framing is not repeated here. Four
of its findings govern this spec:

- **Skills define what a guide must show; the codebase defines how it renders.** This toolkit ships
  no markup, no CSS classes, and no front-end patterns. It was the decisive reframe, and the pack
  already has the mechanism — `/block` resolves rendering by reading exemplars and palettes by
  reading the project's own data types.
- **One extraction, one page.** A single dossier per component produces a single guide page carrying
  that component's purpose, its examples, and its property tables. Discovery framed this as one
  extraction feeding *two* renderings — a component-guide entry and a separate how-to guide — and
  named drift between them as a risk to solve. The merged page dissolves the risk rather than
  solving it: there is only one place for the purpose sentence to live.
- **The audit is what makes it survive a real project.** On a new site the report stays short; on an
  existing one its first run is the backlog.
- **Humans own the CMS.** Editor-authored prose, screenshots, and block arrangements are the part
  that makes a guide good. Automation must preserve them, not route around them.

**One deliberate revision to discovery's story 2.** Discovery asked for "a component guide page that
puts blocks and their variations on a page alongside rich-text descriptions" — one large page. This
spec ships a guide page per component plus a derived index instead, on three grounds: page weight
(twenty components at three variations each is sixty rendered blocks on one page), the UX cost once
components have variations, and the value of linking to exactly one component for UAT, training, and
reference. The intent of story 2 — an editor can see what is available and what each thing does — is
served in a different shape. Recorded here so it reads as a decision rather than as a drift.

## Functional Requirements

### The dossier

- One extraction per component produces a **dossier**: name, alias, kind, description, icon, the
  full property structure by tab and group with sort order, required flags, editor types, option
  lists with default markers, and resolved compositions.
- The dossier is **normalized on the alias**, whichever serialization it was read from.
- The dossier records **which rung of the extraction ladder it was read at**, alongside a schema
  version for the dossier format itself.
- **One dossier produces one guide page.** There is no second rendering; the index is derived
  separately and reads no dossier.
- **A component and a page type are the same concept in the CMS**, filling different roles — one
  rendered by a template at a URL, one rendered as an element inside a block editor. Extraction
  reads both roles with the same parser and produces the same dossier. This is why the requirements
  below say "a block or a page type" rather than treating them as two mechanisms.
- Generation writes a **stored reference** onto the guide page recording **alias, kind, source
  signature, and extraction rung**. Kind is recorded at generation time so the index never has to
  resolve aliases against the schema while rendering.

### Extraction, as an adapter seam

- Which adapter runs is a **slot with a detection recipe**, resolved once at setup and overridable
  by a human — not re-sniffed per invocation.
- The ladder, in order: on-disk Deploy artifacts, on-disk uSync configuration, the running
  instance's management API, then generated model classes.
- **An adapter that finds no properties fails loudly.** A folder present but holding no match for
  the requested alias is a partial export, not an empty schema, and must be reported as such.
- **The two on-disk formats declare their version differently, so refusal takes two shapes.** Deploy
  stamps a version on every artifact and one project holds a mix of them, because artifacts only
  re-serialize when touched — so the check is **per file**, and an unreadable artifact is skipped
  and reported while the rest of the read continues. uSync declares one format version for the whole
  export in a single settings file — so the check is **a single gate up front**, and an unrecognized
  format refuses the entire read. A single refusal rule cannot describe both, and applying Deploy's
  rule to uSync (or the reverse) either rejects a normal project over one stale file or reads an
  unsupported export as though it were understood.
- **The kind is not in the filename, and the two formats disagree on how they mark it.** One writes
  the element flag only when true; the other always writes it. A reader that assumes symmetry
  reports an empty inventory on a project full of blocks, which is the silent-empty failure this
  ladder's fail-loudly rule exists to prevent.
- The lowest rung yields aliases, names, and some descriptions but no tabs, groups, required flags,
  or option lists. It still produces a guide, with structure flattened and the gap stated.

### What counts as a documentable unit

The audit's primary output is a set difference, so the inventory's definition decides whether it is
useful or noise. **The element flag is not that definition.** On one measured project the flag
matched 125 of 174 content types, while the number an editor would recognize as blocks was 52.

- **A block is a component that appears in a block editor's palette as a content block.** The
  palette is read from the project's own block-editor configuration, which the block workflow
  already does — this reuses that seam rather than adding a source.
- **A settings model is not a documentable unit.** Where a palette entry names a separate element
  type as its settings, that type is the settings half of a block already in the inventory, not a
  block of its own. It is distinguishable only by the role it holds in the palette entry — nothing
  on the type itself says so. On the measured project, 17 element types were settings models.
- **A composition is not a documentable unit.** It is schema a guide *reads* — the dossier resolves
  compositions into the owning component's property tables — never schema a guide documents. On the
  measured project, 56 element types appeared in no palette and were overwhelmingly compositions.
- **A page type is documentable; a folder, a container, and an abstract base are not.** No
  structural flag separates them, and template assignment does not either — on the measured project
  only 8 of 49 non-element types carried a template while 21 were recognizably pages. The signals
  available are the project's own: tree reachability, naming convention, and template presence. **So
  this is a judgment the tooling proposes and a human confirms**, not one it decides silently.
- **The inventory is reported before it is acted on.** Given the gap between a naive count and a
  useful one, the counts and the rule that produced them are stated, so a wrong determiner is
  visible immediately rather than after a hundred guides have been proposed.

### Rendering — what this toolkit does not supply

- No markup, no class names, no styling framework, no view locations, no model binding conventions.
- Where a guide's content must become markup, the shape is taken from the project's existing
  components by reading them, exactly as block authoring already does.
- Where a page must be composed from blocks, the available palette is read from the project's own
  block-editor configuration rather than assumed.
- **The governing principle: conform where it shows, standardize where it does not.** Markup must
  match the project, because visitors and editors see it. Schema should be predictable, because
  nobody sees it — and one shape is what lets a single shared reference describe one thing.
- **The greenfield guard applies to every rendering decision, at two intensities.** Copying a
  structure that already exists is cheap: any project with pages demonstrates a rich-text body and a
  block area, so the guide page's own template and the index's listing markup have near-certain
  exemplars. Inventing rendering that exists nowhere is the expensive case — and every rendering
  decision in this increment falls on the cheap side of that line, which is part of why the
  styleguide separates cleanly from it.
- Where a project has no components or templates to read from, the work **stops and says so** rather
  than inventing a convention the project would then inherit. Discovery's cost gradient put this
  guard on the styleguide alone; that was too clean. Every page type needs a template, and a
  template is markup — so the guide page and the index need exemplars too, even with the styleguide
  out of scope.

### Where guides live

- **The location slot stores the guides node's key, not its route.** This is the one decision that
  keeps the section's name, URL, and tree position free permanently. A route-based slot would break
  the moment an editor renamed the section, locking the name in by accident.
- **Detect on document type, never on name.** A project may already have a "Guides" folder for
  something unrelated. Look for a node containing pages of the guide type; where none exists, ask
  rather than adopt.
- **The tooling never creates a public URL without confirmation.**
- What is rigid and what is not:

| | Visible to | Rigidity |
|---|---|---|
| Node name in the tree | Editors | Free, permanently — rename at any stage |
| URL segment | Visitors | Free until something links to it |
| Tree position | Editors | Free, permanently |
| **Document type aliases** | Nobody | **Fixed — the only rigid thing** |

- **Each document type alias is a slot with a default, not a constant.** A project may already use
  the standard name for something unrelated, and two types cannot share an alias. Use the standard
  name normally and a prefixed alternative when it is taken; record which was used either way.
- **Guides are grouped by kind in the content tree, not merely visually on the index.** Thirty-plus
  siblings in creation order is the mess this avoids, and the backoffice navigation cost is paid
  daily by exactly the people this capability is for.
- The mechanism is **a small container document type marked with its kind**, found as a child of the
  one guides pointer. This keeps configuration at one slot rather than three, with no name matching.
- **Ordering within a group is not specified.** The CMS already provides sort order, and promoting
  frequently-used guides is editor judgment.

### The guide page

- One page per component, carrying its purpose, when to use it, its examples, and its full property
  tables organized by tab and group as the editor sees them.
- **The unit of documentation is the component, not the variation.** Variations are content within a
  component's page.
- **A live example is an instance of the block, placed in the page's content area and rendered by
  the site like any other block.** It is not generated media.
- **The tooling never generates or writes media.** Screenshots are uploaded by a human, always. They
  complement live examples rather than substituting for them: a live example shows front-end output,
  while a screenshot covers what cannot be rendered live — a backoffice property panel, a settings
  screen, a workflow step.
- **Enumerable variants are seeded from the dossier's option lists.** Where a variation is a value
  of a variant or style property, the option list already carries the set, so seeding one instance
  per variant needs no new source.
- Where variations are **combinations of independent toggles**, the set is combinatorial and not
  enumerable. Seed one instance at the default values and say that a human curates which
  combinations are worth showing.
- Where variations are expressed as **separate element types**, they are not variations. They are
  separate components, each earning its own guide page.
- **Every seeded instance is seeded-once.** The audit reports when a variant set has changed; it
  never replaces an arrangement.

### The index

- **Derived at render time. Never seeded, never hand-maintained.** No signature, no ownership
  declaration, no audit coverage — there is nothing on it that can go stale. Publish a guide and it
  appears; delete one and it is gone.
- It lists **three kinds**: components, code-driven page types, and hand-authored editorial guides.
  Kind comes from the stored reference, which is why the reference records it.
- **The index page itself has no machine-owned fields** — human framing copy plus a derived list.
- **Editorial control lives on the guide page, not on the index.** Hiding uses the visibility
  settings already available; promoting uses the CMS sort order; wording comes from the guide's own
  purpose sentence. Every lever sits where the editor already is, and none of them can disagree with
  the guide it describes.
- An optional short-blurb override field on the guide page is permitted where a project wants the
  index to read differently from the guide. It is a field on the guide, never on the index.

### Content ownership

- **Ownership is a property of the page's provenance, not of the field's declaration.** A page
  carrying a stored reference has machine-owned fields; a page with no stored reference has none —
  every field on it is human-owned. Ownership declared per field cannot describe both kinds on one
  document type, which is what this replaces.
- On a page with a stored reference, every field the tooling can write is exactly one of:
  - **Machine-owned** — regenerated when the source signature changes, presented as a diff, written
    only after approval.
  - **Seeded-once** — written at creation and never touched again. Reported when stale, never
    replaced.
  - **Never-touched** — page name, address, visibility settings, and everything not named above.
- **One document type serves every guide, including editorial ones.** Hand-authored guides that
  document nothing in code — image sizing standards, cross-system syncing — use the same type.
- **Every machine-populated field is optional**, the stored reference included. A mandatory
  reference field would make it impossible for an editor to hand-create a guide in the backoffice at
  all.
- **A guide is matched to its source by the stored reference, never by address.** Address matching
  would let an editorial guide named "How to use image sizing" occupy the address a future
  `imageSizing` component would claim, and the tooling would then adopt and overwrite someone's
  work.
- **An adoption path exists.** Where the tooling finds a guide for a component carrying no stored
  reference, it offers the property tables as a diff, keeps the human's prose, and writes a stored
  reference only on approval. This path exists only because there is one document type; with two,
  adoption would mean changing a page's document type.

### The audit

- Reports **features present in code with no guide page** — the primary output. One question per
  feature: it has a guide page or it does not.
- Reports **guides claiming a source that no longer exists** (orphans).
- Reports **machine-owned content whose source signature no longer matches**, which includes a
  seeded example whose variant set has changed.
- Judges structural completeness **relative to the rung the dossier was read at**, reporting
  thinness once as a report-level statement rather than per guide.
- Excludes guides that claim no source at all, so hand-authored editorial guides are never reported
  as orphans.
- **Warns; never blocks. The audit always exits successfully**, whatever it found. Failing a build
  over a missing guide is how guides get cut from scope again, louder — and an audit that exits
  non-zero on findings fails a build by default wherever it is wired into CI, whether or not anyone
  chose that. A team that wants a gate opts in explicitly; the opt-in is the only path to a
  non-zero exit.

### What ships

The capability is split on one line: **deterministic and model-free work ships as an executable
script; work needing a model or a judgment call stays in the spell.** That line is not new — the
degradation order already draws it, and this makes it structural rather than aspirational.

- **A script in the pack owns the deterministic half** — extraction across the ladder, the dossier,
  the inventory determiner, and the audit's arithmetic and report. Shipping executable code from a
  pack is established: the codebase-audit reference already does it. This is also what gives the
  testing guidelines below a subject to run against.
- **A spell owns the model-dependent half** — the purpose and when-to-use prose, the
  diff-and-approve conversation, and the rendering decisions that come from reading the project's
  exemplars. One spell, taking a component alias; the audit is a mode on it, not a separate one.
- **The script reads slots and hardcodes nothing** — paths, the adapter choice, and the guides
  location are all slots. A hardcoded path would be a layer-contract violation, and portability is
  the entire point of the extraction seam.
- **The split matches the degradation order exactly.** The script alone yields property tables plus
  marked gaps, which is the lowest rung already specified. Nothing degrades by losing the script;
  everything degrades by losing the model.
- **Where the CMS writes sit is a plan-time decision.** Reading, computing, and reporting are
  unambiguously the script's. Writing pages involves an approval conversation, so whether the script
  writes under instruction or the spell writes from the script's output is left to the plan rather
  than guessed here.
- Shared scaffolding (the guide page type, the container types, the derived index) is described once
  in a reference the spell cites rather than inline. The deferred styleguide increment is that
  reference's second caller, which is why it is a reference from the start rather than after a
  duplication appears.

### Degradation

The capability degrades in a defined order: full generation where a model service and a CMS
connection are both available; rendering to files where the CMS cannot be written; property tables
plus marked gaps where no model is available at all. Property tables are a deterministic transform
and never depend on a model.

### Voice and tone

Resolved by ladder: project references where they are discoverable or pointed at; the CMS's own AI
contexts where the platform provides them; otherwise a generic descriptor shipped with the skill.

## Possible Edge Cases

- A project with no components and no page templates yet, so there is nothing to take conventions
  from and nothing to document.
- A project with no page templates to copy from, so even the guide page type has no exemplar.
- A serialization folder present but holding no file for the requested alias.
- A serialization format version the adapter does not recognize — as a whole-export declaration, and
  as one stale artifact among many that are readable.
- A block whose settings are a separate element type, which is half of a component rather than a
  component.
- An element type that appears in no palette, which is a composition rather than a block.
- A project whose page types carry no template, so template presence cannot identify a page.
- A project running neither on-disk format, with the site not running.
- A component documented by hand before the tooling existed, with no stored reference — the adoption
  case.
- A hand-written guide *about a component*, which reads as editorial on the index while the audit
  reports that component as undocumented. Both statements are accurate, and adoption resolves it; it
  is a transient oddity rather than a defect to fix.
- A guide about something with no code source at all — image sizing standards, cross-system syncing.
- A component removed from code while its guide remains published.
- A block whose variant set changed after its live examples were seeded.
- Variations expressed as separate element types, which are separate components rather than
  variations.
- Variations expressed as combinations of independent toggles, which are combinatorial and not
  enumerable.
- A project that already has a "Guides" folder for something unrelated — citizen-facing downloads,
  for instance.
- A document type alias already taken by something unrelated in the project.
- Two components whose display names collide.
- A project whose blocks are offered in more than one palette, or in a palette scoped to a single
  parent.
- A page type rather than a block — same structure, but absent from a block-only inventory.

## Acceptance Criteria

1. A QA can browse an index listing every published guide, grouped by kind, derived at render time
   rather than generated — so publishing a guide adds it and deleting one removes it.
2. A QA can generate one guide page per component — a block or a page type — carrying its purpose,
   when to use it, live examples, and every property organized as the editor sees them. A live
   example is an instance of the block placed as page content, never generated media.
3. A QA can run an audit that reports features present in code with no guide page.
4. Re-running any generation never silently overwrites content a human wrote or arranged.
5. The tooling supplies no markup; every rendering decision comes from the project's own codebase.
6. Extraction degrades across a defined ladder, and a read that finds nothing fails loudly rather
   than reporting an empty result.
7. The audit judges completeness relative to the source it was able to read.
8. Guides with no code source are never reported as orphans.
9. **The audit always exits successfully.** Gating a build on its findings is available only as an
   explicit opt-in, never the default.
10. A guide a person wrote by hand before the tooling covered its component can be adopted —
    property tables offered as a diff, the person's prose kept, a stored reference written only on
    approval.

## Scenarios (Draft)

Draft BDD scenarios derived from the acceptance criteria using Example Mapping. Each Rule maps to an
acceptance criterion; scenarios use concrete examples. These get verified and refined after
implementation — the feature doc holds the verified version.

### Rule: The index is derived, never maintained

```scenario
Scenario: Publishing a guide adds it to the index
  Given the guides index lists eleven guides
  When a twelfth guide page is published
  Then the index lists twelve guides on the next page load
  And no regeneration of the index was run
```

```scenario
Scenario: Guides are grouped by kind rather than listed as one flat set of siblings
  Given a project has guides for blocks, guides for page types, and a hand-written editorial guide
  When an editor opens the guides section in the backoffice
  Then each kind sits under its own container
  And the index lists the three kinds separately
```

### Rule: The tooling supplies no markup — the codebase supplies it

```scenario
Scenario: Two projects with different front-end conventions each get conforming output
  Given one project styles its components with utility classes
  And another project styles its components with named component classes
  When a guide page is generated on each
  Then each guide's markup follows the conventions already present in that project
  And neither guide contains markup shipped by the toolkit
```

```scenario
Scenario: A greenfield project stops rather than inventing conventions
  Given a project has no page templates and no blocks yet
  When a QA asks for the guides section to be created
  Then the work stops and reports that there is no existing page to take conventions from
  And no guide page is created
```

### Rule: A component's guide page carries its purpose, its examples, and every property

```scenario
Scenario: A block with tabs and required fields
  Given the "Alert Banner" block has a Content tab with a required "Heading" field and an optional "Dismissible" toggle
  And it has a Settings tab with a "Severity" dropdown offering Info, Warning, and Critical, defaulting to Info
  When a guide page is generated for it
  Then the guide lists the Content tab before the Settings tab, in the order the editor sees them
  And "Heading" is marked required and "Dismissible" is marked optional
  And the Severity options are listed with Info marked as the default
```

```scenario
Scenario: A page type is documented the same way as a block
  Given an "Article Page" page type has a Content tab and an SEO tab
  When a guide page is generated for it
  Then the guide lists both tabs and every property within them
```

```scenario
Scenario: Inherited properties appear alongside the component's own
  Given the "Article Page" page type inherits a "Meta Description" field from a shared composition
  When a guide page is generated for it
  Then "Meta Description" appears in the guide in its inherited tab
```

```scenario
Scenario: One live example is seeded per enumerable variation
  Given the "Alert Banner" block has a "Severity" property offering Info, Warning, and Critical
  When a guide page is generated for it
  Then the page carries three examples of the block, one per severity
  And each example is an instance of the block rendered by the site rather than an image
```

```scenario
Scenario: A block whose look comes from independent toggles gets one example
  Given the "Hero" block has four independent toggles whose values combine freely
  When a guide page is generated for it
  Then one example is placed using the block's default values
  And the guide says that further combinations worth showing are a person's to add
```

### Rule: The inventory counts components an editor can place

```scenario
Scenario: A block's settings model is not counted as a component
  Given the "Alert Banner" block takes its settings from a separate "Alert Banner Settings" element type
  When a QA runs the audit
  Then "Alert Banner" is named as one component
  And "Alert Banner Settings" is not named as an undocumented component
```

```scenario
Scenario: A composition is read but never documented on its own
  Given the "Article Page" page type inherits a "Meta Description" field from a "Base Settings" composition
  When a QA runs the audit
  Then "Base Settings" is not named as an undocumented component
  And the "Article Page" guide lists "Meta Description" among its properties
```

```scenario
Scenario: The rule that produced the inventory is stated with it
  Given a project has 174 content types, 52 of which appear in a block editor's palette
  When a QA runs the audit
  Then the report states that it counted 52 components and how it decided
  And the remaining types are not listed as undocumented
```

### Rule: Regeneration never silently overwrites human work

```scenario
Scenario: An editor's screenshot survives a regeneration
  Given a guide page for "Alert Banner" has an editor-uploaded screenshot
  And the block has since gained a new property
  When the guide is regenerated
  Then the property tables are updated to include the new property
  And the screenshot is unchanged
```

```scenario
Scenario: Rewriting machine-owned prose requires approval
  Given a guide page's description was generated three weeks ago
  And the block's properties have since changed
  When the guide is regenerated
  Then the proposed new description is shown as a difference against the current one
  And nothing is written until a person approves it
```

```scenario
Scenario: A live example an editor arranged is never replaced
  Given the "Image Carousel" guide page shows an example an editor configured with three slides
  And the Image Carousel block has since gained a new property
  When the guide is regenerated
  Then the editor's three-slide example is left exactly as arranged
  And the audit reports that the example may no longer reflect the block
```

```scenario
Scenario: Nothing changes when the source has not changed
  Given a guide page whose stored source signature matches the block's current shape
  When the guide is regenerated
  Then no change is proposed and nothing is written
```

### Rule: A hand-written guide is adopted rather than replaced

```scenario
Scenario: The tooling reaches a component a person already documented
  Given a QA hand-wrote a guide for the "Alert Banner" block before the tooling covered it
  And that guide carries no stored reference to any component
  When a guide is generated for "Alert Banner"
  Then the property tables are offered as a difference against the existing page
  And the QA's prose is left unchanged
  And the stored reference is written only after a person approves
```

### Rule: The audit reports what is undocumented

```scenario
Scenario: A newly added block has no guide yet
  Given a project has fourteen blocks
  And thirteen of them have a guide page
  When a QA runs the audit
  Then the report names the fourteenth block as undocumented
```

```scenario
Scenario: A healthy project produces a short report
  Given every block in the project has a guide page
  When a QA runs the audit
  Then the report states that nothing is undocumented
```

```scenario
Scenario: The first run on an existing site is the backlog
  Given a project has forty blocks and no guides at all
  When a QA runs the audit
  Then the report names all forty as undocumented
```

```scenario
Scenario: A removed block leaves an orphaned guide
  Given a guide page exists for a "Testimonial Slider" block that has since been deleted from the codebase
  When a QA runs the audit
  Then the report names that guide as documenting something no longer present
```

### Rule: Guides with no code source are never reported as orphans

```scenario
Scenario: A hand-written standards guide is left alone
  Given a QA has hand-written a guide called "Image Sizing Standards" that documents no component
  When a QA runs the audit
  Then that guide is not reported as an orphan
  And it is not reported as undocumented
```

### Rule: A read that finds nothing fails loudly

```scenario
Scenario: A partial export is reported rather than read as empty
  Given the project's serialized schema folder exists
  And it contains no file for the "Alert Banner" block
  When a guide is generated for "Alert Banner"
  Then the work stops and reports that the schema for that block could not be found
  And no guide is written claiming the block has no properties
```

```scenario
Scenario: An export declaring an unrecognized format version is refused whole
  Given the project's serialized schema declares one format version for the entire export
  And that version is not one the adapter recognizes
  When a guide is generated
  Then the work stops and names the format it found
  And no component is read from that export
```

```scenario
Scenario: One unreadable artifact does not stop the rest of the read
  Given a project's serialized schema stamps a format version on each artifact separately
  And the artifacts carry a mix of versions, one of which the adapter does not recognize
  When a QA runs the audit
  Then the unrecognized artifact is named as unread
  And every other component is still reported on
```

### Rule: Completeness is judged relative to the source that was read

```scenario
Scenario: A project readable only from generated models reports thinness once
  Given a project's schema can only be read from generated model classes
  And guides exist for all twelve of its blocks
  When a QA runs the audit
  Then the report states once that structure is unavailable from this source and names what is missing
  And no individual guide is reported as incomplete
```

### Rule: The audit warns and never blocks

```scenario
Scenario: Undocumented blocks do not fail a build
  Given three blocks have no guide
  When the audit runs as part of an automated check
  Then the gaps are reported
  And the check does not fail the build
```

```scenario
Scenario: A team that wants a gate asks for one
  Given three blocks have no guide
  And a team has opted in to gating their build on the audit
  When the audit runs as part of an automated check
  Then the gaps are reported
  And the check fails the build
```

## Open Questions

### Resolved since discovery

- **How a guide is matched to its feature — by stored reference, never by address.** Forced by the
  editorial-guide collision case: address matching would let the tooling adopt and overwrite a
  hand-written guide that happened to sit at the address a future component would claim.
- **The inventory widens to page types — yes.** A page type is the same concept as a block filling a
  different role, extraction already reads both, and page types are a listed kind with their own
  guides.
- **A variation is not a documented unit.** The component is the unit; variations are content on its
  page.
- **One large component guide page, or several — several, plus a derived index.** The three grounds
  are in the Summary.
- **Editorial guides do not need their own document type.** One type serves every guide; provenance
  is carried by the presence or absence of a stored reference.
- **Both on-disk formats are verified, and they need opposite refusal rules.** One stamps a version
  per artifact and mixes them within a project, so its check is per file and skips what it cannot
  read; the other declares one format version per export, so its check is a single gate. The
  element-type flag is also asymmetric between them. The extraction guidance was corrected against
  real projects in both formats on 2026-08-25; its previously unverified element names are now
  confirmed, and one outright error — a filename-based kind test that would have found zero blocks
  on any Deploy project — was removed.
- **What ships: a script for the deterministic half, a spell for the model-dependent half.** The
  spec specified behavior thoroughly and was silent on the deliverable, which left three readings
  all consistent with it — pure guidance, a shipped script, or guidance for building a per-project
  CLI. Pure guidance would have made every testing guideline an eval, and this repo's eval files
  have no runner. The prior art is a CLI with tests, and a pack shipping scripts is established.
  Choosing the script also settles who builds the extraction adapter the roadmap lists separately:
  this increment does.
- **The increment ships stories 2–4; the styleguide is deferred to its own spec.** It is the only
  story requiring new element types, new views, and a pre-existing design system, and the only one
  whose rendering has no exemplar to copy anywhere in a typical project. Stories 2–4 share one
  dossier and one audit and stand alone without it. Carry-forward in `notes/deferred-styleguide.md`.
- **The audit always exits zero; gating is opt-in.** Prior art returned non-zero on findings, which
  fails a build by default anywhere it is wired into CI — the outcome the warns-never-blocks rule
  exists to prevent, arriving through the exit code rather than through the report.
- **The planned test spell is a separate spell, not a mode on the feature spell.** So the two
  capabilities share no machinery, and the gap-report shape they both need is a smaller coincidence
  than it looked: this increment owns its report shape rather than extracting a core reference for a
  second caller that will not use it. It is still written as **a self-contained section of the
  shared scaffolding reference** rather than inline in the spell, so a later extraction to core is a
  move rather than a rewrite if the shapes do converge.
- **The styleguide is a spell, not a reference.** Recorded here because it was decided here; it
  governs the deferred increment, not this one. No case against it survived review. `/block` is
  already a noun-named spell in the same pack, so a second one does not strain the verbs-are-spells
  convention; contract check 16's ten-spell ceiling governs the core spellbook and pack spell counts
  are ungated, so the count is not a constraint here; and the styleguide's job is an action with a
  precondition, which is spell-shaped. If the roadmap's ungated-pack question closes by extending
  the ceiling to packs, this is a decision to revisit rather than one that blocks.
- **A browsable visual gallery is out of scope for this increment, and expected in a later one.**
  The merged shape removes the page where twenty components rendered side by side answered "what
  could I put here?", and a text index does not answer it. The only version surviving the
  page-weight objection is a human-uploaded thumbnail per component, shown on the index. Deferring
  means that field gets added to an existing document type later rather than shipped with it; the
  pack already has a document-editing workflow for exactly that, so the deferral is cheap rather
  than free. It is recorded in the feature doc's Increments as expected, not as a parking-lot maybe.

### Resolved in this increment

- **How voice and tone guidance is discovered — a four-rung ladder in the spell, and no new slot.**
  Settled 2026-08-29 by Step 16. Rung 1 is the project's own editor-facing writing where it is
  discoverable — published guides, backoffice help text, an editorial style guide, a design-system
  skill's writing section — taken by the same find-the-closest-exemplar rule the rest of the spell
  uses. Rung 2 is a reference somebody points at, when nothing is discoverable. Rung 3 is the
  platform's own AI contexts, which on Umbraco are real records that serialize alongside the rest of
  the schema, and it is **read regardless of whether an earlier rung answered**, because it is the
  only rung that says what *not* to write. Rung 4 is a generic descriptor shipped with the spell,
  and a run that reaches it says in its report that the voice was read from nowhere. No slot,
  because every rung is a discovery the spell can make, and a slot would only record an answer the
  project already carries in its own writing.
- **Where degraded file output lands — temporal by default, and the question is asked rather than
  assumed.** Settled 2026-08-29 by Step 16, per the `workflow` skill's durable-or-temporal
  convention. Guides rendered to files are a staging artifact — they exist to become CMS content —
  so they default to a git-ignored scratch location, and where the answer is durable the run must
  say what makes it so. The audit's report goes the other way and defaults durable, to a dated file
  in the project's audit directory, because a backlog is read again later. In both cases the
  location carries the answer, so commit status is not a separate decision.

### Still open

Carried from discovery:

- **Which format version values the adapter accepts.** Where the version lives and how refusal works
  are now settled and verified in both formats, and the extraction guidance carries the specifics.
  What remains is the accepted set itself — the evidence base is three projects, all on one CMS
  major, two of them on one host, which is narrow for a portability claim.
- **Whether the audit's report shape belongs in core.** The output contract itself is settled and
  shipped — three counted sections, `alias (Display Name)` items, the report-level rung statement,
  exit zero with `--strict` as the only opt-in — written as a self-contained section of
  `umbraco-17-guide-scaffolding` that names no CMS, no serialization format and no file. **The half
  this bullet used to carry is closed**: the shape did survive contact with the inventory
  determiner, whose count and rule went into the report header ahead of the findings, so a wrong
  determiner is visible before a hundred guides are proposed. What remains is placement, which
  needs a second caller to answer: the planned test spell was the candidate, and the decision to
  make it a separate spell means the two share no machinery. Recorded in `ROADMAP.md`, which states
  it the same way.

Raised by this spec:

- **Where the shared guide-page scaffolding reference lives** relative to the spell that cites it,
  given the rule against a unit restating what it could cite. The deferred styleguide increment is
  its second caller, so the placement should anticipate that rather than assume a single consumer.
- **Whether creating a document type is confirmed rather than silent.** Proposed on the same
  reasoning as never creating a public URL without confirmation, but not yet agreed.

## Testing Guidelines

**The subject under test is the script**, which is what makes these runnable rather than a
description of intended behavior. One precondition: the repo's harness currently takes a single
hardcoded subject, so parameterizing it is a first step in the plan rather than part of the
capability. Prose the model produces is reviewed by a human and is not tested here.

Meaningful tests for the cases below, without going too heavy:

- **Extraction is deterministic and format-blind.** Given the same component serialized in each
  supported on-disk format, the dossier produced is equivalent — same properties, same tabs, same
  order, same compositions resolved to the same aliases. This is the highest-value test in the set,
  because it is what makes the adapter seam real rather than aspirational.
- **A read finding nothing fails.** Assert the loud failure, not the empty result. This is the
  silent-pass shape the toolkit has been bitten by before, so it earns an explicit test rather than
  trusting the adapter.
- **Ownership is honored.** Regenerating a guide whose seeded-once and never-touched fields carry
  known values leaves those values byte-identical, and updates only the machine-owned ones.
- **Provenance decides ownership.** A page with no stored reference has no machine-owned fields, so
  a generation run against it proposes rather than writes — the adoption path, asserted as a diff
  offered and nothing written until approval.
- **The no-op path writes nothing.** A matching signature produces no model call and no write.
- **Audit arithmetic.** Given a known inventory and a known set of guides, the report names exactly
  the expected undocumented items and the expected orphans — including that a source-less guide
  appears in neither list.
- **The inventory determiner holds.** Given a fixture with element types split across palette
  content blocks, palette settings models, and compositions used by neither, the inventory names
  exactly the content blocks. This is the audit's whole value — a determiner that over-counts by
  two-and-a-half times makes the primary output noise rather than a backlog.
- **A mixed-version read is partial, not failed.** A set of artifacts where one version is
  unrecognized reads the rest and names the one it skipped.
- **Variant seeding is derived, not invented.** A dossier carrying a three-value option list seeds
  three instances; a dossier carrying independent toggles seeds one.
- **Rung-relative completeness.** A dossier recorded at the lowest rung produces one report-level
  statement rather than one finding per guide.
- **Greenfield refusal.** With no page to take conventions from, the work stops rather than creating
  a guide page from an invented convention.
- **The exit code is zero on findings.** Assert the default explicitly, and assert that the opt-in
  flag is the only thing that changes it. This is a one-line behavior whose absence fails builds
  silently in exactly the projects that wired the audit in early.

Not worth testing here: the wording a model produces for purpose and when-to-use prose. That is
reviewed by a human by design, and asserting on generated prose produces brittle tests that fail on
rewording rather than on regression. The index needs no staleness test either — it is derived at
render time, so there is nothing on it that can go stale.
