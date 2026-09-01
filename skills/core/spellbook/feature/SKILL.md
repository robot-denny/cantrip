---
name: feature
description: Generate or update a living behavioral doc — BDD Given/When/Then scenarios describing what a capability does right now, grouped under business rules, mapped to tests in a coverage table. Works from specs, plans, and tests, or from code alone when a capability was never documented. Records durable behavior at the end of the spec → plan → implement chain.
disable-model-invocation: true
argument-hint: "[spec path | capability-name | update <slug> | a code entity with no upstream artifacts]"
allowed-tools: Read, Write, Glob, Grep
---

You are generating (or updating) a **living behavioral specification** — a BDD-style doc
describing what a capability does *right now*, using Given/When/Then scenarios. This is the
single source of truth for current system behavior, used by QA for regression testing and by
developers for onboarding.

Artifact locations follow the layout in the `workflow` skill — consult it rather than assuming
paths.

User input: $ARGUMENTS

## What this does

Creates or updates a feature doc that:

- Describes current behavior using BDD scenarios (Given/When/Then)
- Groups scenarios under `Rule:` headings — the business rule each cluster proves
- Maps scenarios to test files in a coverage table
- Uses business language, not technical jargon
- Is **one file per logical capability**, named by area of the system, even when the capability
  spans multiple specs or plans

## Guard — feature docs are for capabilities, not work

Before creating any new file, apply the work-type classification from the *Work types* table in
the `workflow` skill. Feature docs hold **evergreen capability behavior only.**

- If the slug names a **change to an existing capability** (a migration, upgrade, refactor, "add
  X to existing Y") — for instance it starts with `migrate-` / `upgrade-` / `extract-` / `bump-`,
  or its draft Rules read as *transitions* ("goes from red to…", "after the change ships…",
  "compiles on the stable stack") rather than standing behavior — **do not create a new file.**
  Find the existing capability doc it changes (grep the feature docs by area) and update *that*,
  folding in the evergreen behavior. Point-in-time acceptance criteria stay in the shipped spec.

  **If no doc exists for that area yet**, do not fall back to creating one named after this work.
  Create the doc **at area level** and populate it with only what this increment establishes — thin, and
  flagged for from-code backfill. See the `workflow` skill's naming tell; the classification must not
  depend on whether documentation already exists.
- If the slug names a **fix, infra, CI, or cleanup** effort (`fix-`, `triage-`, a dependency bump
  with no behavior change) — **do not create a feature doc at all.** Durable residue belongs in a
  runbook under `docs/` and/or a section in the project's guidance file.
- Only a genuinely **new capability** earns a new feature doc.

If the argument points at a change or fix slug, **stop** and tell the user which existing
capability doc (or runbook) should receive the content instead, rather than creating a
transition-style feature doc.

Only proceed past this guard when the work is a genuine new capability, or an update adding
standing behavior to an existing capability's doc. Architecture and migration criteria — "the
service is unit-testable", "the build is zero-warning", "the package leaves no trace" — are
point-in-time. They never become Rules in a capability doc.

**From-code mode also runs this Guard.** A code entity is usually a genuine capability — a type
or component that renders standing behavior — so it normally earns a doc. But if the code exists
only to serve a fix or infra concern, or is a change to an existing capability, fold it per the
rules above instead of drafting a cold-start doc.

## Before you start

1. Consult the `bdd-principles` skill for scenario-writing guidance — especially **Example
   Mapping** (Rules → Scenarios), **Specification by Example** (concrete values, not
   abstractions), and **Ubiquitous Language** (business terms like "content editor", "visitor",
   "page" — not "document type", "controller", "API endpoint").
2. Read the `templates/feature.md` asset in the `workflow` skill to understand the output format.

## Step 1 — Parse the argument

Resolve `$ARGUMENTS` in this **precedence order**, stopping at the first branch that matches. The
richer artifact-driven path always wins when artifacts exist — from-code is strictly the fallback
for the zero-artifact cold-start case. A code entity that *does* have a spec takes the
artifact-driven path, not the thinner code-only one.

1. **`update` directive** (starts with `update`) → **update mode.** Update the existing feature
   doc named after it.

2. **Artifact-driven** — the argument is a spec path, or a token resolving to an existing feature
   doc or a locatable spec, plan, or **behavioral** test. A behavioral test asserts observable
   Given/When/Then behavior that would populate the coverage table; a pure visual-regression
   baseline does **not** count, so a component whose only test is a screenshot comparison remains
   a from-code cold-start target.

   - **Spec path**: read the spec's `**Work type**:` line first. For `new-capability`, create a
     new doc (extract the slug from the filename). For `change-to <existing>`, update that
     existing capability's doc instead of creating a new file. For `fix-infra`, create no doc —
     apply the Guard. If the spec has no work-type line, classify it yourself per the Guard.
   - **Capability name** (no path separators): look for an existing doc by that name. If found,
     update it. Otherwise look for a locatable spec, plan, or behavioral test. If any exist, apply
     the Guard before creating — only create when the work is a new capability.

   Follow **Steps 2–7** below.

3. **From-code (fallback)** — only if nothing above resolves *and* the token resolves to code,
   with **no** upstream spec, plan, behavioral test, or existing feature doc. The presence of only
   a visual-regression baseline does not disqualify this mode. Reverse-engineer a draft from the
   implementation using **From-code mode** below in place of Steps 2–6, then finish with **Step 7
   — Report**.

## From-code: a mode, and also a technique

**Two uses, and the second is the one that makes brownfield adoption work.**

- **As a mode** (branch 3 above) — the cold start: a capability exists in code with no spec, plan,
  tests, or doc at all. The whole doc is reverse-engineered.
- **As a technique, inside update mode** — an existing doc **under-describes** what the code actually
  does. This is the ordinary condition of a real codebase: one increment documented its own change and
  left the rest of the capability undocumented. Apply F1–F4 to the *undocumented parts* while leaving
  the verified parts alone.

The second use is the brownfield backfill path, and it is a **tool for onboarding an existing project**
rather than a fallback for when nothing else works. Reach for it whenever a doc covers less than the
code does.

Reverse-engineers a **draft** doc when a capability exists in code but has no spec, plan, tests,
or doc to work from. The output is the same template shape as every other mode — it just
self-identifies as reverse-engineered and not-yet-verified, because code is the only source.

Run the **Guard** first. This mode still classifies the work and only proceeds for a genuine
capability.

This is also the path for adopting the toolkit on an existing codebase: it backfills behavioral
documentation for capabilities that predate any spec.

### F1 — Read the code sources

Resolve the argument to the thing being documented, then read its implementation from up to three
sources, in this order of authority:

1. **The schema definition** — whatever declares the capability's shape and its author-editable
   fields. Read it for the human-readable name, the field labels and identifiers, which fields are
   required, any per-field help text, and anything inherited from a shared composition.
2. **The typed model** — if the project has a generated or hand-written model exposing those
   fields as typed properties, **use the property types as the primary signal** for what each
   field is. A strongly-typed property is more reliable and more repo-native than reverse-mapping
   a schema-level editor identifier.
3. **The view or template** — whatever renders it. Read it for **conditional branches** —
   `if`/`else`, null and empty checks, collection-emptiness guards, toggle guards — and write one
   scenario per branch, with the true and the false path each becoming an outcome.

If a stack pack or project skill offers guidance on where these three live for this technology,
and how to map schema-level field types to readable labels, consult it. Without such guidance,
locate the sources by finding the closest documented analogue and following its structure.

**Slot:** `.agents/config/paths.md` → `## Code layout`
**If empty:** infer the layout by finding the closest existing analogue to what you are looking
for and following its structure; if nothing analogous exists, say so in your output rather than
inventing a convention.

Where any of the three sources cannot be found, proceed with what resolved and record the gap per
F3 — never guess at a missing source's contents.

If nothing resolves for the token, say so and ask the user to confirm the name rather than
guessing.

### F2 — Derive Rules from each field

One `### Rule:` per meaningful field or behavior cluster — **not** one Rule per field blindly.
Derive the scenario shape from the field's kind:

| Field kind | Scenarios to write |
|---|---|
| **Required** | "renders when set" **and** "fails validation when missing" |
| **Optional text or rich text** | "renders when set" **and** "renders nothing when blank" |
| **Boolean / toggle** | "shows X when enabled" **and** "hides X when disabled" |
| **Media or asset reference** | "renders the asset when set" **and** "no asset or a placeholder when blank" |
| **Collection of child items** | "renders children when present" **and** "renders no container when empty" |
| **Reference to other content** | "renders the link when set" **and** "renders nothing when unset" |
| **Every conditional branch found in the view** | one scenario per side of the branch |

Write scenarios in Given/When/Then with concrete values and business language, exactly as Step 4
describes — no CSS classes, file paths, or field identifiers inside the scenarios themselves.

### F3 — Flag what code can't prove

Where the exact observable proof — the precise element, text, or selector a test would assert —
**cannot** be derived from the sources alone, do **not** invent it. Append this line to that
scenario:

`> needs human input: exact element/selector — confirm what proves this outcome.`

Also flag any field whose kind stayed unrecognized, and note if no view was found, since scenarios
may then be incomplete.

### F4 — Provenance and coverage

Emit the standard template, with these from-code specifics:

- **Draft banner**, immediately under the `# Feature:` heading: `> **Draft** — Reverse-engineered
  from code; these scenarios have not been verified against a running implementation or any test.
  Refine and verify before relying on them.` This is the from-code counterpart to the banner
  `/spec` adds; a later `/feature update` removes it once verified.
- **Source line** → `derived from implementation ({today's date}) — no originating spec;
  reverse-engineered from code.`
- **Last verified** → today's date. The draft banner, not this field, carries the unverified
  signal.
- **Increments** → a single placeholder: `- [ ] (no shipped increments recorded —
  reverse-engineered baseline)`.
- **Test Coverage** → every row starts **Not covered (code-derived)**, not plain `Not covered`. The
  distinction is load-bearing: these rules were inferred from code, never specified and never tested.
- **Edge Cases** → pull genuinely boundary or unusual scenarios (missing content, invalid input,
  empty collections) out of Behaviors into here, using the same `Rule:` and scenario shape.
- **Revision Notes** → `{today's date}: Initial draft reverse-engineered from {name} — not yet
  human-verified.`
- If reading the model or view surfaced a genuine bug or dead code — a field nothing reads, a
  mismatched identifier — and not merely a documentation gap, add a short `## Open Issues` section
  of numbered prose bullets before Behaviors. Omit it entirely otherwise.

Save the doc with a slug derived from the capability's identifier in kebab-case. Then go to **Step
7 — Report**, pointing the `Next:` line at spells that actually exist in this project.

## Step 2 — Locate all related artifacts

Search for everything related to this capability:

1. **Spec(s)** — the increment's spec, and any sub-specs
2. **Plan(s)** — there may be several for one capability
3. **Test files** — matching the capability's name or slug
4. **Source files** — the views, styles, scripts, or code implementing it; use the plan's file
   summary if one exists

Read everything located.

**Then compare the doc against the code, not just against the artifacts.** If the code does more than
the doc describes — fields with no Rule, conditional branches with no scenario — **apply the from-code
technique (F1–F4) to the undocumented parts.** Leave the verified parts as they are; you are filling
gaps, not rewriting.

That comparison is the whole brownfield backfill path, and skipping it is how a doc stays permanently
partial: each increment documents its own change and nothing ever documents what was already there.

## Step 3 — Resolve behavioral truth

When sources disagree about behavior — which happens as capabilities evolve — use this precedence:

1. **Test assertions** are the strongest signal. They describe what the code actually does.
2. **Plan descriptions** are second. They reflect the most recent intent.
3. **Spec descriptions** are third. They reflect the original intent.

Note any conflict in the output summary. The doc should reflect **reality** (test behavior), not
**aspiration** (spec or plan).

## Step 4 — Derive Rules and write scenarios

For each distinct behavior:

1. **Identify the Rule** — the business rule or acceptance criterion, framed from the user's
   perspective. Good: "Only visible pages appear in section navigation." Bad: "Pages with a
   hide-flag are filtered by a LINQ Where clause."
2. **Write scenarios** under that Rule in Given/When/Then:
   - **Concrete values**: "Given a page with 3 visible siblings", not "Given a page with siblings"
   - **Business language**: "content editor", "visitor", "page" — not internal type names
   - One scenario per distinct behavior or example
   - Edge cases get their own Rule section under Edge Cases
3. **No implementation details** — no CSS classes, file paths, endpoints, or code patterns. Those
   live in plans.

## Step 5 — Build the test coverage table

For each scenario, find the corresponding test if one exists:

| Scenario | Test File | Status |
|----------|-----------|--------|
| Scenario name | `path/to/test:L42` | Covered |
| Scenario name | `path/to/test:L58` | Test failing |
| Scenario name | — | Not covered |
| Scenario name | — | Not covered (code-derived) |
| Scenario name | — | Ruled out — why it cannot be proved here |

**Five states, each a claim about what is proved — not a stage in a process.** Four record an
observation; the fifth records a decision, and is set apart below because that is a different kind of
claim and deserves to be read as one.

- **`Covered`** — a test asserts it and its last run passed.
- **`Test failing`** — a test asserts it and its last run did not pass. Name the test anyway. The
  status is named for what was observed, not for its cause: the behavior may not be built yet, it may
  have regressed, or the doc may simply be wrong, and the table is not the place that decides which.
  Do not downgrade such a row to `Not covered` — that erases a proof somebody already wrote.
- **`Not covered`** — it was specified and no test asserts it.
- **`Not covered (code-derived)`** — the rule is *your reading of the code*, never specified and never
  tested, and therefore the weakest claim in the document.

And the one that is not an observation at all:

- **`Ruled out — <reason>`** — the project has already decided this scenario cannot be proved
  here. Carry the row and its reason through unchanged. **This spell never makes that decision**; it
  only preserves one the doc already records. Never treat such a row as an ordinary gap — it is the
  opposite of one, and folding it back into `Not covered` quietly converts somebody's deliberate
  decision into a backlog item.

Keeping these distinct is what makes a backfilled doc honest. A reader can then tell verified behavior
from inferred behavior at a glance — and a gap somebody chose from a gap nobody has got to yet —
instead of a partially-backfilled doc presenting all of it with equal confidence.

Match by **behavioral intent, not exact wording.** A scenario about "mobile toggle collapses
navigation" maps to a test named "click toggle hides nav list" even though the wording differs.

## Step 6 — Assemble and save

Use the template structure:

- **Summary** — 2–3 sentences, user perspective, business language
- **Source** — path to the originating spec
- **Last verified** — today's date
- **Behaviors** — Rule-grouped scenarios
- **Edge Cases** — Rule-grouped edge-case scenarios
- **Test Coverage** — the table from Step 5
- **Revision Notes** — "Initial feature doc from spec + implementation" for a new doc, or a
  description of what changed for an update

For a **new** doc, save it under the capability's slug. For an **update**, overwrite the existing
file and add a revision note dated today.

If the doc carries a "Draft" banner from `/spec` or from from-code mode, **remove it** — this is
the verified version.

## Step 7 — Report

Print a short summary:

```
Feature doc: <path>
Scenarios: {count}
Test coverage: {covered}/{total} scenarios covered
Conflicts resolved: {list any behavioral conflicts and how they were resolved, or "None"}
Next: /code-review before merge
```

Do not print the full doc to chat unless the user asks. The doc lives in the file.
