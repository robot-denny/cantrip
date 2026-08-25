# Feature: Editor-Facing Guides

A team building a CMS site gets the editor-facing reference their content editors actually use — a
browsable index of everything documented, grouped by kind, and one guide page per component or page
type carrying its purpose, live examples of it, and every field an editor can fill. A styleguide
showing the site's colors, type, and common elements is the capability's next increment. The first
pass is derived from what the codebase already knows, an audit reports anything built but
undocumented, and everything a person writes or arranges afterwards is left alone.

**Source**: `_work/editor-facing-guides/spec.md`
**Last verified**: —

> **Draft** — These scenarios have not yet been verified against an implementation. They will be
> refined during planning and verified after implementation.

---

## Increments

The per-feature mini-roadmap: shipped increments, planned increments, and parking-lot ideas.
Newest planned items first. When an item ships, flip the checkbox and point it at the archived
increment.

- [ ] **Expected next**: a browsable visual gallery — one human-uploaded thumbnail per component,
      shown on the index. It answers "what could I put here?", which a text index does not, and it
      is the only version of the old side-by-side component page that survives the page-weight
      objection. Deliberately out of the first increment; it adds a field to a document type that
      already exists by then
- [ ] **Next increment, cut from the first on 2026-08-25**: the styleguide — a page whose showcase
      sections read the project's design tokens live. It is the only story requiring new element
      types, new views, and a pre-existing design system, and the only one whose rendering has no
      exemplar to copy in a typical project. Earns its own spec; the decisions already made about
      it, and the three scenarios drafted before the cut, are carried in
      `_work/editor-facing-guides/notes/deferred-styleguide.md`
- [ ] 2026-08-24 — The capability's first increment, scoped to stories 2–4: the dossier and its
      extraction ladder, one guide page per component or page type, the derived index, the guide
      spell and its audit mode, and provenance-based content ownership
      (`_work/editor-facing-guides/spec.md`, no plan yet)
- [x] **Prerequisite, landed 2026-08-24**: schema is read from on-disk serialization rather than a
      live instance, and a partial export reports itself instead of reading as an empty schema. It
      shipped as a direct amendment to the extraction guidance with no increment bundle, so its
      behavior belongs to that guidance rather than to this doc (see `CHANGELOG.md`, 2026-08-24)
- [ ] Parking lot: detecting staleness in human-authored prose — deliberately rejected for the first
      increment because it would put a model call in the audit path, which must stay cheap
- [ ] **Known gap**: the supported serialization format versions are unsettled, and one format's
      element names are carried as unverified in the extraction guidance

<!-- Page types were a parking-lot item until 2026-08-25, when the spec revision put them in scope:
     a page type is the same concept as a block filling a different role, and extraction already
     reads both. -->

---

## Behaviors

Scenarios are grouped by Rule — the business rule the scenarios prove. Use concrete values and
business language. See the `bdd-principles` skill for guidance.

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

---

## Edge Cases

### Rule: A project with nothing to copy from stops rather than inventing conventions

```scenario
Scenario: A greenfield project stops rather than inventing conventions
  Given a project has no page templates and no blocks yet
  When a QA asks for the guides section to be created
  Then the work stops and reports that there is no existing page to take conventions from
  And no guide page is created
```

### Rule: Variations that cannot be enumerated seed one example, not every combination

```scenario
Scenario: A block whose look comes from independent toggles gets one example
  Given the "Hero" block has four independent toggles whose values combine freely
  When a guide page is generated for it
  Then one example is placed using the block's default values
  And the guide says that further combinations worth showing are a person's to add
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

---

## Test Coverage

| Scenario | Test File | Status |
|----------|-----------|--------|
| Publishing a guide adds it to the index | — | Not covered |
| Guides are grouped by kind rather than listed as one flat set of siblings | — | Not covered |
| Two projects with different front-end conventions each get conforming output | — | Not covered |
| A block with tabs and required fields | — | Not covered |
| A page type is documented the same way as a block | — | Not covered |
| Inherited properties appear alongside the component's own | — | Not covered |
| One live example is seeded per enumerable variation | — | Not covered |
| A block's settings model is not counted as a component | — | Not covered |
| A composition is read but never documented on its own | — | Not covered |
| The rule that produced the inventory is stated with it | — | Not covered |
| An editor's screenshot survives a regeneration | — | Not covered |
| Rewriting machine-owned prose requires approval | — | Not covered |
| A live example an editor arranged is never replaced | — | Not covered |
| Nothing changes when the source has not changed | — | Not covered |
| The tooling reaches a component a person already documented | — | Not covered |
| A newly added block has no guide yet | — | Not covered |
| A healthy project produces a short report | — | Not covered |
| The first run on an existing site is the backlog | — | Not covered |
| A removed block leaves an orphaned guide | — | Not covered |
| Undocumented blocks do not fail a build | — | Not covered |
| A team that wants a gate asks for one | — | Not covered |
| A greenfield project stops rather than inventing conventions | — | Not covered |
| A block whose look comes from independent toggles gets one example | — | Not covered |
| A hand-written standards guide is left alone | — | Not covered |
| A partial export is reported rather than read as empty | — | Not covered |
| An export declaring an unrecognized format version is refused whole | — | Not covered |
| One unreadable artifact does not stop the rest of the read | — | Not covered |
| A project readable only from generated models reports thinness once | — | Not covered |

<!-- Covered: a test asserts it. Not covered: specified, untested. Not covered (code-derived):
     inferred from reading the code, never specified and never tested — the weakest claim here.
     Keeping the third distinct is what lets a reader tell verified behavior from inferred. -->

---

## Revision Notes

- 2026-08-24: Draft scenarios from initial spec
- 2026-08-25: Revised from `_work/editor-facing-guides/notes/spec-revisions.md`. The component guide
  and the how-to guide merged into one guide page per component, with a derived index replacing the
  single large page — so "The purpose sentence is identical in both places" was removed as obsolete
  rather than failing. Added scenarios for the derived index, grouping by kind, per-variant example
  seeding, non-enumerable variations, and adopting a hand-written guide. Page types moved from the
  parking lot into scope
- 2026-08-25: Amended after verifying both serialization formats against real projects. The two
  formats declare their version differently and need opposite refusal rules, so the single refusal
  scenario split into two. Added the inventory determiner: a component is one an editor can place
  from a block editor's palette, which excludes settings models and compositions — the element-type
  flag over-counted by roughly two and a half times on a measured project
- 2026-08-25: Scoped to stories 2–4. The styleguide was cut to its own increment, so its rule and
  two scenarios moved to `_work/editor-facing-guides/notes/deferred-styleguide.md`, and the
  greenfield scenario was retargeted from the styleguide to the guides section itself. Added the
  opt-in gating scenario: the audit always exits successfully, and only an explicit opt-in makes it
  fail a build
