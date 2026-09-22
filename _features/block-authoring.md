# Feature: Block Authoring

> **Draft** — These scenarios have not yet been verified against an implementation. They will be
> refined during planning and verified after implementation.

A team building an Umbraco site can add a block to it through the normal flow of spec, plan, and
implement, and the plan and the workers that carry it out follow the discipline a block needs: the
block is proved to exist by a test before it is built, its view copies the closest block the project
already has instead of inventing a shape, which palette it joins is treated as the team's decision,
and the block counts as done when its test passes. A developer who wants one block without a spec
can still cast a single spell and get the same result.

**Source**: `_work/umbraco-block-authoring-reference/spec.md`
**Last verified**: 2026-09-22

---

## Increments

The per-feature mini-roadmap: shipped increments, planned increments, and parking-lot ideas.
Newest planned items first. When an item ships, flip the checkbox and point it at the archived
increment.

- [ ] The block-authoring reference: extract `/block`'s discipline into a model-invoked reference,
      route block work to it from the pack's planning guidance, and thin `/block` to a cast that
      follows it (`_work/umbraco-block-authoring-reference/spec.md` and `plan.md`)
- [ ] Backfill this doc from code: `/block` has shipped since the phase-5 pack increment and this
      doc covers only what the reference increment establishes. Run `/feature`'s from-code mode over
      the spell to record the behavior it already had (no spec yet)

---

## Behaviors

Scenarios are grouped by Rule — the business rule or acceptance criterion the scenarios prove.
Use concrete values (Specification by Example) and business language (Ubiquitous Language). See
the `bdd-principles` skill for guidance.

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

---

## Edge Cases

### Rule: A project without the pack, or with its own block guidance, is left alone

```scenario
Scenario: A project without the umbraco-17 pack plans as before
  Given a project with only the core workflow installed
  When the developer casts /plan on a spec that adds a component
  Then the plan carries no block-authoring guidance and nothing in core routes to it
```

```scenario
Scenario: A project's own block conventions win
  Given a project whose AGENTS.md has a "Where a new block goes" section that names a flat views folder
  When the worker authors the "Testimonial" view
  Then the view lands in the flat folder the project named
  And the worker does not propose the per-block layout the reference describes as one common shape
```

---

## Test Coverage

| Scenario | Test File | Status |
|----------|-----------|--------|
| Planning a Testimonial block names the guidance in every block step | — | Not covered |
| Block work is planned as ordinary steps, not as a spell to cast | — | Not covered |
| The test for the Testimonial block asserts presence with truthiness | — | Not covered |
| The Testimonial view follows the existing Quote block | — | Not covered |
| The first block in a project is established deliberately, not absorbed | — | Not covered |
| Registering in one of two parity-kept palettes is confirmed first | — | Not covered |
| A one-block palette is not reported as drift | — | Not covered |
| The Testimonial block is created through the API, not by editing files | — | Not covered |
| A one-line cast produces the same block as before | — | Not covered |
| The styleguide's handoff still reaches view authoring | — | Not covered |
| The reference cites facts instead of restating them | — | Not covered |
| The spell cites the reference instead of restating it | — | Not covered |
| A consuming project sees the new reference as wired | — | Not covered |
| Core does not change | — | Not covered |
| A project without the umbraco-17 pack plans as before | — | Not covered |
| A project's own block conventions win | — | Not covered |

<!-- Status vocabulary. Each status is a claim about what is proved, not a stage in a process:
     read a row as its answer to "what does this entitle me to believe?"

     FOUR STATUSES RECORD AN OBSERVATION — what was seen, or that nothing was:

     - Covered: a test asserts this scenario, and its last run passed.
     - Test failing: a test asserts this scenario, and its last run did not pass. Named for what was
       observed rather than for its cause, because the cause may be behavior not built yet, a
       regression, or a doc that is simply wrong, and the row cannot tell those apart. Whatever
       reported the run is where the cause gets argued.
     - Not covered: the scenario is specified, and nothing asserts it.
     - Not covered (code-derived): the rule was inferred by reading the code — never specified and
       never tested, and so the weakest claim in this table.

     ONE STATUS RECORDS A DECISION, and it is the only one a person writes deliberately:

     - Ruled out — <reason>: the project has decided this scenario cannot be proved here, and
       the reason travels in the row so a later reader can judge whether it still holds.

     The split is the point. The four above say what happened; this one says somebody chose — the
     difference between a gap nobody has reached yet and a gap the project decided to live with. It is
     named unlike the other four on purpose: an earlier draft called it "Not coverable", which sat one
     syllable from "Not covered" and was misread as an ordinary gap every time somebody skimmed the
     table. A status that records a decision should not look like a status that records an absence. -->

---

## Revision Notes

- 2026-09-22: Draft scenarios from initial spec
