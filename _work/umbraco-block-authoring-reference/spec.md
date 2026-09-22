# Spec for umbraco-block-authoring-reference

> This spec captures initial requirements and design rationale. For **current system
> behavior**, see the doc named on the **Work type** line below — a new feature doc for a new
> capability, an existing feature doc for a change, or a `docs/` runbook for a fix.

branch: robot-denny/umbraco-block-authoring-reference
design reference (if any): none. This increment ships guidance and a unit split, no markup.

**Work type**: new-capability
**Feature doc**: `_features/block-authoring.md`
<!--
  Classified new-capability at AREA level, per the workflow skill's "When the area has no doc yet".
  The area a stakeholder would name is "block authoring on an Umbraco project". `/block` has
  carried that capability since the phase-5 pack increment, but it predates feature docs and no
  `_features/` file describes it. The nearest doc, `editor-guides.md`, covers guides and the
  styleguide and only touches blocks where it hands views to `/block`.

  The tell was checked. The acceptance criteria below read as standing behavior: a plan for block
  work routes to the reference, a worker executing a block step follows it, a bare cast of `/block`
  still lands a block. None of them is a transition. So the classification is new-capability, and the
  doc is named `block-authoring` rather than after this increment. It will be thin: it covers what
  this increment establishes, and the spell's pre-existing behavior should be backfilled with
  `/feature`'s from-code mode. That debt is visible on purpose.

  Raised on the roadmap 2026-09-21 ("`/block` holds discipline that `/plan` and `/implement-step`
  cannot see"). Two of the roadmap's premises were checked on 2026-09-22 before this spec was written
  and are corrected in the Summary below.
-->

## Summary

A team on an Umbraco project follows the normal flow: `/spec`, then `/plan`, then `/implement-step`
for each step. When the feature adds a block, the plan and the workers that execute it should carry
the discipline a block needs, without anyone having to know that a spell called `/block` exists.

Today they do not. `/block` holds two kinds of content. One is **procedure**: derive names, write a
failing test, create the element type, register it in a palette, author the view, build, go green.
`/plan` already produces that sequence for any feature. The other is **discipline** that no plan step
re-derives: the shape of the test that proves a block exists, the rule to copy the closest existing
block and never quietly invent a first one, the fact that palette choice is a project decision, the
rule never to hand-edit `.uda` files, and the rule that a block is done when its test goes green and
not when it compiles. A spell is invisible to the model, so a planned block gets none of that, and
`/implement-step` refuses a step that says "cast `/block`" by design.

In the demo project this never showed, because its `AGENTS.md` carried a "Where a new block goes"
section and its conventions slot said the same. A consuming project with empty slots has neither.

**The fix is a unit split, not an edit.** Extract the discipline into a model-invoked reference,
`umbraco-17-block-authoring`, that the planning reference routes to and that a dispatched worker can
load. Thin `/block` to a standalone cast that follows the reference for one block. The spell stays:
`/styleguide` hands view authoring to it at its Step 9, and a block too small to earn a spec still
needs a home.

**Two premises checked before writing this.** First, the roadmap said to verify that a reference
loads inside the worker `/implement-step` dispatches. It does. A general-purpose worker dispatched on
2026-09-22 listed all eight core references, loaded two of them, and saw none of the project's spells.
So the split works by mechanism, and naming the reference in a step prompt is belt-and-braces rather
than the only path. Second, the roadmap said the two assertion traps and the rich-text `using` were
not in any reference. They are. `umbraco-17-starter-facts` already records `getByName()` returning
`false`, properties arriving as a flat array, `isElement: true`, the encoded-string `using`, palette
membership being only the top-level `blocks[]`, the reserved `level` alias, and the dropdown editor
alias. What is genuinely absent from every reference is the discipline that composes those facts:
the test shape, the copy-the-closest-block rule with its greenfield sequence, palette choice as the
project's decision, the `.uda` rule, and the definition of done. The new reference carries those and
cites the facts rather than restating them.

## Functional Requirements

- **FR1. A new reference unit, `umbraco-17-block-authoring`, in the `umbraco-17` pack.** Model-invoked
  (no `disable-model-invocation`), with a description that triggers when work adds, plans, or
  implements a block or element type on an Umbraco project. It holds the discipline named in the
  Summary and nothing that already lives in `umbraco-17-starter-facts`; for those facts it points at
  the starter-facts unit by name, since a unit may name a sibling inside its own pack.
- **FR2. The reference states what the platform decided and names what the project decides without
  answering it**, per ADR 0015 §7. The test shape and the `.uda` rule are platform facts and are
  asserted. Which palette a block joins, where views live, and how models bind are project decisions
  and are named as such, with the trade-off and no verdict.
- **FR3. The reference carries the greenfield sequence.** When a project has no block to copy, it says
  to ask whether another codebase is the reference, otherwise to establish the convention explicitly
  and minimally, to say plainly that a convention is being established, and to record it in the
  plan's Key Decisions and propose it for the paths slot so the second block has an exemplar.
- **FR4. `umbraco-17-planning` routes block work to the reference.** A plan for Umbraco work that adds
  a block consults the reference before the plan is written, and every step that writes the test,
  creates the element type, registers the palette entry, or authors the view names the reference in
  its prompt, the same way the worker envelope already names `tdd-principles`. The planning reference
  also says that block work is planned as ordinary steps, never as a step that casts `/block`.
- **FR5. `/block` is thinned to a standalone cast that follows the reference.** It keeps its
  procedure, its argument hint, its slots, its report, and its `Next:` line. Where it once stated a
  piece of discipline, it cites the reference instead. Its view-authoring step remains the step
  `/styleguide` hands off to, and it still stops on a greenfield project the way the reference says.
- **FR6. Every fact and rule is held once.** No sentence of discipline appears in both the reference
  and the spell, and no starter fact is restated in the reference. Defer rather than duplicate,
  against core and against sibling units.
- **FR7. The unit is registered everywhere a pack unit must be.** `ROSTER_PACK` and `PACK_SOURCE` in
  the install checker, the `umbraco-17` pack table in the README, a card in `docs/spell-cards.md`, and a
  CHANGELOG entry. If the reference reads any slot, each slot it reads gains a `PACK_SLOTS` entry
  naming it as a reader, deduplicated on `file|heading`, with the fallback text identical to the
  other readers'.
- **FR8. Core stays technology-agnostic.** Nothing under `skills/core/` changes to make this work. The
  routing lives in the pack's planning reference, and the worker reaches the reference by the
  mechanism the probe confirmed.
- **FR9. The gate and the suite stay green.** `scripts/check-contract.sh` and `tests/run.sh` pass on
  the increment, with the new unit visible to checks 5, 6, 6b, 7, 9, 10, 13, and 18.

## Design Reference (only if one exists)

- Source: none. The design of the reference follows `umbraco-17-guide-scaffolding`, the pack's
  existing example of a reference that two spells cite rather than restate.
- Component name: n/a
- Key visual constraints: n/a

## Possible Edge Cases

- **The `umbraco-17` pack is not installed.** Nothing changes for that project. Core has no routing
  to add, and a plan for non-Umbraco work is unaffected.
- **The project has no blocks yet.** A planned first block hits the greenfield sequence. The step
  records the established convention in Key Decisions and proposes the paths slot, so the second
  block copies rather than decides.
- **The worker cannot load the reference.** A step prompt pasted into a fresh session on a machine
  without the pack, for instance. The step names the reference, so the worker can say it is missing
  rather than silently improvising. No "where installed" hedge is written for it: the reference is a
  unit of the same pack, and same-pack citation is the pack's precedent.
- **A plan step is written as "cast `/block`".** `/implement-step` refuses it and hands it back. The
  planning reference must make that the wrong shape for block work, so it does not get written.
- **The project's own guidance already covers blocks.** An `AGENTS.md` with a "Where a new block goes"
  section, or a filled conventions slot. The project wins. The reference tells the reader to follow
  the exemplar and the project's declared conventions, and must never contradict them.
- **A palette exists but is scoped to one parent block.** The reference keeps the existing rule:
  compare only palettes that already share a block, so a one-block palette is not reported as drift.
- **`/styleguide` hands off to `/block` after this ships.** The handoff targets a view-authoring step
  that assumes the element types and palette already exist. Thinning the spell must not renumber or
  remove that step's meaning.
- **The reference and the spell drift apart later.** The rule that a sentence of discipline lives in
  exactly one place is a review rule, not a gated one. The plan should say how a reviewer checks it.

## Acceptance Criteria

- **AC1.** Given the `umbraco-17` pack is installed, when `/plan` runs on a spec whose work adds a
  block, the plan's Key Decisions records that `umbraco-17-block-authoring` was consulted, and each
  step that writes the block's test, creates its element type, registers it in a palette, or authors
  its view names the reference in its prompt.
- **AC2.** When `/implement-step` dispatches one of those steps, the worker writes a test that asserts
  the element type's presence with a truthiness check and reads its properties as a flat array, and
  the test is run to RED before the element type is created.
- **AC3.** When a worker authors a block's view in a project that already has blocks, it names the
  existing block it copied and carries that block's model directive, folder placement, settings
  handling, and styling convention rather than inventing any of them.
- **AC4.** When a worker authors the first block in a project with none, it does not pick a shape
  quietly: it asks whether another codebase is the reference, otherwise states that it is
  establishing a convention, and records the convention in Key Decisions with a proposal for the
  paths slot.
- **AC5.** When a worker registers a block in a palette, it treats the choice as the project's: it
  names the candidate palettes, picks based on where the block is meant to appear, and confirms with
  the user before adding to only one palette in a project that keeps its palettes in parity.
- **AC6.** No step, worker, or cast edits a `.uda` file by hand, and a block is reported done only
  after the test that failed before creation passes.
- **AC7.** `/block`, cast alone from a one-line description in a project with existing blocks,
  produces an element type, a palette entry, a view copied from the closest block, and a test that
  went RED then GREEN, exactly as before this increment, and its report ends with the same `Next:`
  line.
- **AC8.** `/styleguide`'s final `Next:` line still lands on a `/block` step that authors a view
  for element types and a palette that already exist.
- **AC9.** Every sentence of block discipline exists in exactly one shipped file. The reference does
  not restate a fact recorded in `umbraco-17-starter-facts`, and the spell does not restate a rule
  recorded in the reference.
- **AC10.** In a consuming project with the pack installed, `check-install.sh` reports
  `umbraco-17-block-authoring` as wired, and the README, spell cards, and rosters list it.
- **AC11.** `git diff --stat main -- skills/core` is empty on the increment's branch.

## Scenarios (Draft)

Draft BDD scenarios derived from the acceptance criteria using Example Mapping. Each Rule maps
to an acceptance criterion; scenarios use concrete examples. These get verified and refined
after implementation — the feature doc holds the verified version.

### Rule: A plan for work that adds a block routes to the block-authoring guidance

```scenario
Scenario: Planning a Testimonial block names the guidance in every block step
  Given an Umbraco project with the umbraco-17 pack installed
  And a spec for a "Testimonial" block with a quote and an author name
  When the developer casts /plan on that spec
  Then the plan's Key Decisions says the block-authoring guidance was consulted
  And the step that writes the block's test names the guidance in its prompt
  And the steps that create the element type, register the palette entry, and author the view each name it too
```

```scenario
Scenario: Block work is planned as ordinary steps, not as a spell to cast
  Given a spec for a "Testimonial" block
  When the developer casts /plan on that spec
  Then no step in the plan reads "cast /block"
  And /implement-step accepts every block step for dispatch
```

### Rule: A worker executing a block step proves the block exists before building it

```scenario
Scenario: The test for the Testimonial block asserts presence with truthiness
  Given a plan whose Step 2 writes the failing test for the "Testimonial" element type
  When the developer casts /implement-step on Step 2
  Then the worker's test asserts the element type is truthy rather than not null
  And it reads the element type's properties as a flat array
  And the worker reports the test ran RED before any element type was created
```

### Rule: A new block copies the closest existing block rather than inventing a shape

```scenario
Scenario: The Testimonial view follows the existing Quote block
  Given a project whose closest existing block is "Quote", bound to the generated typed model in a per-block folder
  When the worker authors the Testimonial view
  Then the worker's report names "Quote" as the block it copied
  And the Testimonial view uses the same model directive, folder placement, settings handling, and styling convention as Quote
```

```scenario
Scenario: The first block in a project is established deliberately, not absorbed
  Given a project with no blocks and no filled paths slot
  When the worker reaches the view-authoring step for the "Testimonial" block
  Then the worker asks whether another codebase should be the reference before writing anything
  And if none is named, the worker states plainly that it is establishing the view location and model binding
  And the plan's Key Decisions records the convention with a proposal for the paths slot
```

### Rule: Which palette a block joins is the project's decision

```scenario
Scenario: Registering in one of two parity-kept palettes is confirmed first
  Given a project with a "Page Body" palette and a "Landing Sections" palette that share six blocks
  When the worker registers the "Testimonial" block
  Then the worker names both palettes as candidates
  And the worker asks before adding Testimonial to only one of them
```

```scenario
Scenario: A one-block palette is not reported as drift
  Given a project with a "Page Body" palette of six blocks and a "Card Items" palette offering only "Card"
  When the worker reads palette state before registering the "Testimonial" block
  Then the worker compares only palettes that already share a block
  And "Card Items" is not reported as drifting from "Page Body"
```

### Rule: Schema files are never hand-edited and a block is done when its test passes

```scenario
Scenario: The Testimonial block is created through the API, not by editing files
  Given a project using Deploy with document-type .uda files committed
  When the worker creates the "Testimonial" element type and registers it in a palette
  Then no .uda file is edited by hand
  And the worker's report shows the test that failed in Step 2 now passing
```

### Rule: Casting /block alone still lands a whole block

```scenario
Scenario: A one-line cast produces the same block as before
  Given a project with existing blocks and a filled paths slot
  When the developer casts /block with "A Testimonial block: quote (rich text), author name (text)"
  Then an element type, a palette entry, a view copied from the closest block, and a passing test exist
  And the report ends with the same Next: line the spell had before this increment
```

```scenario
Scenario: The styleguide's handoff still reaches view authoring
  Given /styleguide has created its three showcase element types and registered them in a palette
  When the developer follows its Next: line and casts /block for the swatch showcase element
  Then the cast authors the view and does not propose creating the element type or the palette entry again
```

### Rule: Every rule is held in exactly one place

```scenario
Scenario: The reference cites facts instead of restating them
  Given the starter facts record that getByName() returns false and that properties are a flat array
  When a reviewer reads the block-authoring reference
  Then it points at the starter facts for both and states neither as its own claim
```

```scenario
Scenario: The spell cites the reference instead of restating it
  Given the block-authoring reference states the copy-the-closest-block rule
  When a reviewer reads the thinned /block spell
  Then the spell names the reference at the step that authors the view and does not re-argue the rule
```

### Rule: The unit is registered, and core is untouched

```scenario
Scenario: A consuming project sees the new reference as wired
  Given a project that installed the umbraco-17 pack after this increment ships
  When the developer runs check-install.sh --verbose
  Then umbraco-17-block-authoring is listed as wired
  And the README's umbraco-17 pack table and the spell cards both carry it
```

```scenario
Scenario: Core does not change
  Given the increment's branch
  When a reviewer diffs skills/core against main
  Then the diff is empty
```

## Open Questions

- **Where does the routing row live in `umbraco-17-planning`?** Its existing table routes to external
  companion plugins and is hedged for their absence. A row pointing at this pack's own unit has no
  such hedge. A short section of its own, "Route block work to this pack's reference", may read more
  honestly than a row in the companion table. Decide in the plan.
- **Does the reference read slots directly?** The spell reads `paths.md → ## Umbraco`,
  `stack.md → ## Tests`, `stack.md → ## Build`, and `conventions.md → ## Planning gotchas`. If the
  discipline about view locations moves to the reference, the reference becomes a reader of the paths
  slot and must be registered in `PACK_SLOTS` with the identical fallback text, per contract check 9.
  If instead the reference states the rule and leaves slot reading to the spell and the plan, no
  registration is needed. The plan decides, and the fixture `shared-slot-two-packs` shows the shape
  if it registers.
- **Does the test's code sample move or stay?** The sample is TypeScript against the Playwright test
  helpers, which is fine inside a pack. It is the one piece of the test shape a worker most needs.
  The plan should decide whether the reference carries it and the spell points at it, or the sample
  stays in the spell and the reference describes the shape in words with a pointer.
- **Should the roadmap entry be corrected as part of this increment?** It names three facts as missing
  from every reference that are present. Shipping this increment moves the entry to Recently shipped,
  which may be correction enough.

## Testing Guidelines

Meaningful tests for the cases below, without going too heavy:

- **The gate.** `scripts/check-contract.sh` passes with the new unit present. Checks 13 and 18 fail on
  an unregistered or unlinked unit, so a green run proves registration. Check 9 fails on a slot
  fallback that differs from its siblings.
- **The suite.** `tests/run.sh` passes. If the reference registers as a slot reader, extend the
  `pack-installed` install-check fixture so the new unit is present and verified there.
- **The worker probe, by hand and recorded.** Dispatch a worker with a step prompt that names the
  reference and confirm it loads and is followed: the test it writes asserts truthiness and reads a
  flat array. Record the prompt and the result in a validation log beside the increment, following
  the convention in `AGENTS.md` for things a gate cannot cover.
- **The standalone cast, by hand.** Cast the thinned `/block` on the demo project and confirm AC7.
  Then walk `/styleguide`'s `Next:` line and confirm AC8.
- **The single-holder rule, by grep.** For each sentence of discipline the reference carries, grep
  the spell and the starter facts for a restatement. Record the greps in the validation log.
- **Core untouched.** `git diff --stat main -- skills/core` is empty.
