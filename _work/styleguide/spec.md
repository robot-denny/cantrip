# Spec for styleguide

> This spec captures initial requirements and design rationale. For **current system
> behavior**, see the doc named on the **Work type** line below.

branch: feature/styleguide
design reference (if any): none shipped — by design, this work reads the *consuming project's*
design system and ships no markup of its own

**Work type**: change-to editor-guides
**Feature doc**: `_features/editor-guides.md`

<!--
  Classified change-to, not new-capability, on the naming tell. The area a stakeholder would name is
  "editor-facing guides", and that area already has a doc — one whose summary and Increments list
  already claim the styleguide as the capability's next increment. A styleguide page is a guide page:
  it uses the guide document type, sits under a kind container in the same guides section, appears in
  the same derived index, and inherits provenance-based content ownership unchanged. A separate
  `styleguide.md` doc would be a behavior-named file splitting one area in two, and the workflow
  skill's classifier biases toward amend.

  What is genuinely new here is the *element types and views* that render tokens — but those are the
  implementation of a Rule inside the area, not an area of their own.

  Carried forward from `_work/shipped/editor-facing-guides/notes/deferred-styleguide.md`, written on
  2026-08-25 as carry-forward material when this story was cut from the guides increment. The five
  decisions recorded there are treated as settled, not re-litigated. Discovery is
  `_work/shipped/editor-facing-guides/discovery.md`, story 1 of four.
-->

## Summary

The editor-facing guides capability shipped its guides section, its guide page type, its derived
index, and the audit — scoped to stories 2–4 of discovery's four. **This increment ships story 1: the
styleguide.**

A styleguide is the one guide page that documents no component. It shows the site's colors, type
scale, and common elements — the things an editor, a designer, and a QA all need to point at, and the
things that are hand-built and hand-maintained on every project exactly like the component guides
were. Its distinguishing property is that its showcase sections **read the project's design tokens at
render time**, so changing a brand color in the codebase changes the styleguide on the next page load
with no regeneration run.

**Why it was cut into its own increment, and why that reasoning still holds.** Stories 2–4 share one
dossier and one audit; this one shares only the guide-page scaffolding. It is the only story
requiring new element types, new views, and a pre-existing design system — and the only one whose
rendering has **no exemplar to copy in a typical project**. Every other story reads a structure any
project with pages already demonstrates: a rich-text body and a block area. A token-reading swatch
block has no analogue anywhere.

**The correction to discovery's cost gradient, which still applies** (recorded in
`_work/shipped/editor-facing-guides/notes/spec-revisions.md` §7): discovery claimed only the
styleguide needs an established design system, and that was too clean. Every *page* type needs a
template, and a template is markup, so the guide page and the index needed exemplars too. The real
line is **copying a structure that already exists** (cheap) versus **inventing rendering that exists
nowhere** (expensive). The styleguide is the only story on the expensive side of that line, which is
what makes it separable — and what makes its greenfield refusal the most intense in the capability.

### Decisions carried forward, not reopened

Five, from the deferred note. Re-deriving them is the specific waste that file exists to prevent.

- **It is a spell, not a reference.** No case against it survived review: `/block` is already a
  noun-named spell in the same pack, so a second one does not strain the verbs-are-spells convention;
  ADR 0010's ten-spell ceiling governs the **core** spellbook and pack spell counts are ungated
  ([ROADMAP.md](../../ROADMAP.md)); and its job is an action with a precondition, which is
  spell-shaped. Revisit only if the ungated-pack question closes by extending the ceiling to packs.
- **It states its precondition rather than assuming it.** An established design system is required,
  and the spell says so instead of producing plausible output from nothing.
- **It delegates view authoring to `/block`** rather than shipping markup, on the same reasoning as
  the rest of the capability.
- **It scaffolds three things**: the element types that showcase design tokens, the page itself, and —
  already shipped — the guide-page scaffolding it shares with `/guide`. That shared half is why
  `umbraco-17-guide-scaffolding` was written as a cited reference rather than folded into `/guide`;
  this increment is its second caller, as intended.
- **Greenfield refusal is at its most intense here.** With no components to read from, the work stops.
  The named hazard: a styleguide scaffolded at project setup makes a **color-swatch view the exemplar
  every real block is later copied from.**

### What the shipped increment leaves this one

- The guide page type, its kind containers, and the derived index — scaffolded and in use, so the
  styleguide inherits a working section rather than standing one up.
- The `umbraco-17-guide-scaffolding` reference, whose second caller this was always meant to be.
- Content ownership by provenance, which the styleguide page needs unchanged.

## Functional Requirements

### The spell and its precondition

- **`/styleguide` is a spell in the `umbraco-17` pack**, user-cast only (`disable-model-invocation:
  true`), like every other spell in the spellbook.
- **The precondition is stated at the top of the spell and checked before anything is written**: the
  project must have an established design system — a token layer, and existing components that
  demonstrate how markup in this project consumes it.
- **Where the precondition is not met, the work stops and says which half is missing** — no token
  layer, no exemplar components, or neither. It does not scaffold a partial styleguide, and it does
  not invent a convention "to be replaced later".
- The spell ends with a `Next:` line and never invokes another spell. Where view authoring is needed
  it suggests `/block`; it does not cast it.

### Reading the project's design tokens

- **The token layer is a slot with a detection recipe**, resolved once and overridable by a person —
  the same shape as the guides capability's `## Schema serialization` slot, and for the same reason:
  re-sniffing per invocation makes two runs disagree.
- **Detection prefers being told over guessing.** A project that has a design-system skill in the
  `design-system-authoring` mould already names the stylesheet holding its token definitions; that
  pointer is the first rung. Failing that, detect the token layer from the repository.
- **A token this capability can showcase is one that survives to runtime.** A value that is compiled
  away before the browser sees it cannot be read live by any markup, so the live-reading promise
  applies only to the runtime-resolvable layer. Where a project's tokens are build-time only, the
  spell says so and says what it can offer instead, rather than shipping swatches whose values were
  baked at generation time while the page claims to be live.
- The spell **reads token names and groupings, never their values**, into anything it writes. A
  literal value written into a page is the staleness this increment exists to prevent.

### The showcase element types

- The spell scaffolds **element types whose views render a token rather than a value** — at minimum a
  color swatch, a type-scale specimen, and a common-elements specimen (buttons, lists, tables, form
  fields).
- **This pack ships no markup for them.** The element type and its property shape are scaffolded here;
  the view is authored by following the project's closest existing block, which is `/block` Step 5's
  job and not this spell's.
- Each showcase element carries **the token's name as content**, so the page is a list of names the
  site resolves — not a list of values the page asserts.
- **A showcase section is a block area on the page**, arranged by a person. The set of tokens shown is
  therefore editorial: seeding proposes a starting set, and what stays on the page is whoever last
  arranged it.

### The styleguide page

- The styleguide is **an `editorGuide` page under a kind container in the existing guides section**,
  not a new document type and not a page outside the section. It appears in the derived index like
  any other guide, and needs no index work at all.
- **The styleguide claims no stored source reference.** It documents no component, so per the shipped
  audit contract it is neither orphanable nor stale, and it closes no documentation gap. It is an
  editorial guide whose *content* happens to be generated.
- Consequently **every field on it is human-owned**, which is the shipped fourth ownership class — the
  one a page carrying no reference puts every field in at once. Nothing this spell writes is rewritten
  by a later run; a second run against an existing styleguide proposes and asks, it does not refresh.
- The spell **locates the guides node by its recorded key**, per the shipped scaffolding reference —
  never by route and never by name. An unrecorded guides node is a question to ask, not a section to
  go looking for.

### Greenfield refusal

- **With no existing blocks to take conventions from, the work stops** and reports that there is no
  exemplar. No element type is created, no page is created, and no view is written.
- The refusal names the same two escape hatches `/block` offers: point at another codebase to take
  conventions from, or establish the convention explicitly and say plainly that you are establishing
  rather than following it.
- **Scaffolding this at project setup is refused as a matter of policy, not capability.** The spell is
  invoked explicitly, once a design system exists. This is the split-the-timing-by-artifact decision
  from discovery, and the styleguide is the artifact it was made for.

## Design Reference (only if one exists)

None, and the absence is the point. Cantrip ships no markup, no CSS classes, and no front-end
patterns; the consuming project's own components are the design reference every time this spell runs.

## Possible Edge Cases

- **A project whose tokens are build-time only** (preprocessor variables compiled to literals). The
  live-reading promise cannot be kept; the spell must say so rather than quietly baking values.
- **A project with more than one token layer** — a preprocessor layer feeding a runtime layer, or a
  utility framework's config beside hand-written custom properties. Which one is authoritative is a
  project fact, so it is what the slot records.
- **Themed projects, where a token resolves differently per theme or per colour scheme.** A swatch
  reading one token shows one theme's value; a styleguide claiming to show "the palette" while
  rendering inside one theme is accurate but incomplete.
- **A token added or removed after the page was arranged.** Live reading covers a token's *value*
  changing. It does not cover the *set* changing — a new brand color does not add its own swatch.
- **A token that no longer exists**, whose swatch now resolves to nothing. The page renders a blank
  or a fallback and looks like a styling bug rather than a missing token.
- **A project that already has a hand-built styleguide page** outside the guides section. Adopting it
  is the same shape as the shipped hand-authored-guide adoption, but the page is not an `editorGuide`
  and adoption would be a retype rather than a property write.
- **A guides section whose kind containers do not include one for a styleguide.** Per the shipped
  reference, a kind with no container is a container to create, not a name to go looking for.
- **Two styleguide pages.** Nothing forbids it and nothing should — but the audit's duplicate rules
  were written for stored source references, and a styleguide carries none.

## Acceptance Criteria

The criterion carried verbatim from the deferred note, which the drafted scenarios prove:

> A team member can generate a styleguide page whose showcase sections read the project's design
> tokens live, so it reflects current styles without regeneration.

Added here:

- A team member can cast `/styleguide` on a project with existing blocks and a token layer, and get a
  published styleguide page in the existing guides section, listed in the derived index, with sections
  for colors, type scale, and common elements.
- Every showcase section's markup follows the conventions of the project's existing blocks, and no
  markup ships from this toolkit.
- On a project with no blocks to copy from, the work stops and reports why, having created nothing.
- On a project whose token layer cannot be read at runtime, the spell says so and does not present
  baked values as live ones.
- Nothing a person wrote or arranged on the styleguide page is rewritten by a later run.
- The styleguide is never reported by the audit as undocumented, orphaned, or stale.

## Scenarios (Draft)

Draft BDD scenarios derived from the acceptance criteria using Example Mapping. Each Rule maps to an
acceptance criterion; scenarios use concrete examples. These get verified and refined after
implementation — the feature doc holds the verified version.

**The first three are carried verbatim from the deferred note**, where they were parked when this
story was cut. They are not re-derived, and any change to them is a decision to record rather than an
edit to make quietly.

### Rule: A styleguide reflects current styles without a regeneration

```scenario
Scenario: A designer changes a brand color and the styleguide follows
  Given a styleguide page is published with a color palette section
  And the project's primary brand color is defined in the codebase as a design token
  When a designer changes that token's value and the site is deployed
  Then the styleguide's palette section shows the new color on the next page load
  And no guide regeneration was run
```

```scenario
Scenario: A type scale specimen follows a changed font size
  Given a styleguide page is published with a type scale section showing six heading levels
  And the project defines each heading size as a design token
  When a designer changes the level-two heading token from 2rem to 2.25rem and the site is deployed
  Then the level-two specimen renders at the new size on the next page load
  And no guide regeneration was run
```

### Rule: A styleguide is scaffolded from the project's own conventions, never from shipped markup

```scenario
Scenario: Standing up a styleguide on a project that has components to copy from
  Given a project has twelve existing blocks and a design token system
  When a team member asks for a styleguide to be created
  Then a styleguide page is published with sections for colors, type scale, and common elements
  And each showcase section's markup follows the conventions of the existing blocks
```

```scenario
Scenario: Two projects with different front-end conventions each get a conforming styleguide
  Given one project styles its components with utility classes
  And another project styles its components with named component classes
  When a styleguide is created on each
  Then each styleguide's markup follows the conventions already present in that project
  And neither styleguide contains markup shipped by the toolkit
```

### Rule: The precondition is stated, and unmet means stop

```scenario
Scenario: A greenfield project stops rather than inventing conventions
  Given a project has no blocks yet
  When a team member asks for a styleguide to be created
  Then the work stops and reports that there is no existing component to take conventions from
  And no showcase block is created
```

```scenario
Scenario: A project with blocks but no token layer is told which half is missing
  Given a project has twelve existing blocks
  And its components hardcode their colors with no token layer between markup and literal values
  When a team member asks for a styleguide to be created
  Then the work stops and reports that there is no design token layer to read
  And it names the blocks as the half of the precondition that is met
  And no showcase block is created
```

### Rule: A value that cannot be read at runtime is never presented as live

```scenario
Scenario: A build-time-only token layer is reported rather than baked
  Given a project defines its palette as preprocessor variables that compile to literal values
  When a team member asks for a styleguide to be created
  Then the report says the palette cannot be read at render time
  And no swatch is created carrying a copied color value
```

### Rule: A styleguide page belongs to the people who edit it

```scenario
Scenario: An editor's rearranged palette survives a later run
  Given a styleguide page carries a palette section an editor reordered into brand, neutral, and status groups
  When a team member casts the styleguide spell again on the same project
  Then the editor's arrangement is left exactly as it stands
  And any addition is proposed rather than written
```

```scenario
Scenario: A styleguide is listed in the index like any other guide
  Given a guides section lists eleven guides
  When a styleguide page is published in it
  Then the index lists twelve guides on the next page load
  And no regeneration of the index was run
```

### Rule: A styleguide documents no component, so the audit says nothing about it

```scenario
Scenario: The audit passes over a published styleguide
  Given a project has fourteen blocks, each with a guide page
  And the guides section also holds a styleguide page
  When a QA runs the audit
  Then the report states that nothing is undocumented
  And the styleguide is not named as an orphan
  And the styleguide is not named as stale
```

### Rule: The set of tokens shown is a person's to curate

```scenario
Scenario: A newly added brand color does not add its own swatch
  Given a styleguide page carries a palette section showing eight color swatches
  When a designer adds a ninth color token to the codebase and the site is deployed
  Then the eight existing swatches still show their current values
  And the ninth color does not appear until a person adds it
```

```scenario
Scenario: A swatch outliving its token is visible rather than silent
  Given a styleguide page carries a swatch reading a token named for a retired accent color
  When that token is removed from the codebase and the site is deployed
  Then the swatch names the token it could not resolve
  And it does not render as an unexplained blank
```

## Open Questions

Red cards raised while writing the scenarios above, plus the ones the shipped increment left pointing
here.

- **What a design token is, on a project that has not decided.** The runtime-resolvable line is clean
  in principle and messy in practice: a project can have a preprocessor layer feeding a runtime layer,
  a utility framework's config, and hand-written custom properties, all at once. Which is
  authoritative is a project fact the slot records — but the **detection recipe** for the empty-slot
  case is not settled, and it is the part that decides whether this works on a project nobody
  configured.
- **How much a build-time-only project can still be offered.** "Say so and stop" is one answer; "offer
  a styleguide whose values are baked, clearly labelled as a snapshot, with the regeneration cost
  stated" is another. The first is honest and useless to that project; the second reintroduces exactly
  the staleness this increment's headline promise rules out. Not decided.
- **Whether a swatch reading a missing token can report itself at all.** The scenario above asserts it
  names the token rather than rendering blank — but this pack ships no markup, so whether that
  behavior is achievable is a constraint on a project's own view, not something the spell can
  guarantee. Same shape as the index's render-as-text-never-as-markup constraint in the shipped
  scaffolding reference: a requirement on what a project's component may do, stated here and enforced
  nowhere.
- **Themes — the property-shape half is answered; the presentation half is deliberately deferred.**
  The question was whether showing one theme's resolved values is acceptable, or whether the showcase
  views must render per theme, on the grounds that it changes the element type's property shape.

  **It does not change the property shape.** A swatch carrying a *token name* rather than a value is
  re-pointed by whatever the project already uses to theme a region, so no per-theme property is
  needed either way — and the themed region is supplied by the project's existing block-theming
  mechanism, which the showcase inherits by copying the closest existing block.

  **What is deferred is the presentation.** A project with several themes is under-served by a
  showcase rendering one of them silently. Whether that is one section per theme, a switcher, or a
  representative with the set named alongside depends on how the project themes things, and one
  worked example is not enough to write a rule from. The spell therefore instructs the generating
  agent to decide it from the project's own mechanism, the same deferral this capability already
  makes for markup. **Revisit when more worked examples are available across projects** — if they
  converge, this becomes a rule; if they do not, the deferral was correct. Deferring costs nothing
  later precisely because no property depends on the answer.
- **Whether the showcase element types belong in the block palette at all.** They are element types an
  editor can place, which is the shipped audit's definition of a documentable unit — so a palette
  entry for a color swatch would make the swatch itself show up as an undocumented component needing
  its own guide page. Either they stay out of the general palette, or the inventory determiner needs
  an exclusion, and the second is a change to shipped behavior. --whatever is the path of least resistance is preferred. 
- **Whether `/styleguide` should adopt a hand-built styleguide page that already exists.** The shipped
  adoption path is a property write on a page that is already an `editorGuide`; a project's existing
  styleguide is a different document type, so adoption would be a retype. Possibly out of scope, but
  it is the common case on a project mature enough to meet the precondition. --Can it simply be informed by an existing hand-built styleguide, and leave it to the site editors to determine how to handle or deprecate the hand-built version?
- **Overlap with the `design-system-authoring` skill.** A project with a design-system skill has
  already written down where its tokens live and what breaks when they are bypassed. Reading that
  pointer is proposed above as the first detection rung; whether the relationship goes further — a
  styleguide as the rendered form of what that skill describes — is worth checking before either is
  built, and is the same shape as the shipped spec's unresolved `/test` overlap.
- **Where a degraded file output lands** when there is no CMS connection to write into. Carried
  forward unresolved from the shipped increment, and it lands the same way here.

## Testing Guidelines

Meaningful tests for the cases below, without going too heavy. The shipped increment's `guide-check`
fixtures are the precedent: an input tree and an expected report, asserted byte for byte.

- **Precondition detection**, as fixture projects: blocks and tokens present; blocks present and no
  token layer; tokens present and no blocks; neither. Assert which half each report names.
- **Token layer detection** across the recipe's rungs, including a project holding more than one
  layer — assert the report says which it treated as authoritative rather than picking silently.
- **The build-time-only refusal**, asserting that no color value appears anywhere in what would be
  written.
- **Greenfield refusal**, asserting nothing is created — the same assertion shape as the shipped
  greenfield scenario, which is currently uncovered because it describes a spell stopping rather than
  a script computing. Worth checking whether this increment can close both.
- **Audit silence on a styleguide** — a fixture guides section holding one styleguide and N component
  guides, asserting the report's three counts are unaffected by it.

The live-token scenarios (a changed token showing on the next page load) describe **CMS-side rendering
this pack cannot reach**, exactly like the three scenarios the shipped increment left uncovered on
purpose. Expect them to stay uncovered and say so, rather than writing a test that asserts something
weaker and claims the scenario.
