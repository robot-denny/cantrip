---
name: workflow
description: The workflow spine — how work flows from roadmap through feature, spec, plan, and implementation, and the work-type classification that decides which durable artifacts a piece of work earns. Consult this before creating a spec, plan, or feature doc; when deciding whether work needs a feature doc at all; when classifying work as a new capability, a change to an existing one, or a fix; when a change landed outside the flow and needs reconciling; or when you need to know where a workspace artifact belongs.
---

# The workflow spine

Work flows through five layers, loose-to-tight: **Roadmap → Feature → Spec → Plan →
Implement.** The project-level queue lives in `ROADMAP.md`; per-feature mini-roadmaps live in
the **Increments** section of each feature doc. Each spec covers a single increment, not a
whole feature.

**Slot:** `.agents/config/paths.md` → `## Workspace`
**If empty:** use the default layout described under *Where artifacts live* below.

## Entry points

`/spec <slug>` → `/plan <slug>` → `/implement-step <slug> N` (per step) → `/feature update
<slug>` → `/code-review`

`/implement-step` runs one step at a time against a fresh context so the main thread stays
clean across a long plan — either dispatched to a subagent or by pasting the step's prompt
into a new session, whichever suits the setup.

**Every spell ends with a `Next:` line pointing at the next stage. Spells suggest; they never
invoke each other.** This is what keeps the toolkit a toolbox rather than a funnel, and it is
a hard rule, not a stylistic preference.

## Out-of-flow changes — the `/retrofit` path

Not every change goes through the layers above, and that is fine. Small front-end or admin-UI
tweaks and AI-assistant edits often land directly, verified by eye.

The standing rule: **any change that skipped the flow → run `/retrofit` before committing it**
(or before pushing, if it is already committed). `/retrofit` reconciles what you did against
the actual diff, runs the reviewers, surfaces edge cases, and proposes the tests and doc
updates the change would otherwise skip — then applies only what you confirm.

It is the low-friction path that keeps a codebase documented and testable regardless of how a
change got made, so nobody has to remember to hand-run review, tests, and docs each time. A
bare `/retrofit` works; adding a sentence about what you changed sharpens its
intent-versus-diff reconciliation.

## Work types — which artifacts a piece of work earns

Feature docs are **living documentation of how the system behaves right now** — one file per
*capability*, named for an area of the system, **not** a record of work done.

Before any work earns a feature doc, classify it. The classification is written into the spec
as a `**Work type**:` line and carried through the plan, so the right artifact gets created
and work-named documents never accumulate among the capability docs.

| Work type | Examples | Feature doc? | Where the durable record lives |
|---|---|---|---|
| **`new-capability`** | A new component, page type, or area of behavior the system did not have | **Create** a feature doc named for the capability | The new feature doc (behavior) + spec/plan (why/how) |
| **`change-to <existing-slug>`** | A refactor, an upgrade, a migration, a new field on an existing thing | **Update the existing capability's doc** — never create a `<work-name>` file | Observable behavior folds into the existing feature doc; point-in-time criteria stay in the shipped spec/plan |
| **`fix-infra`** | A CI fix, a dependency bump with no behavior change, cleanup | **No feature doc** | A runbook under `docs/` and/or a section in the project's guidance file; criteria in the shipped spec |

### The tell

If a doc's Rules read as *transitions* — "goes from red to green", "leaves no trace after the
change ships", "nothing the user sees changes", "the old package is removed" — rather than
*standing behavior* a user or operator can exercise — "a visitor can search from /search", "an
editor can pick a theme per page" — then it is a change or fix masquerading as a capability.

Do not create the file. Fold the observable behavior into the affected capability's doc, or
route it to a runbook, and say which and why.

### The naming tell — amend or create

A second tell, for whether work earns a *new* doc or a Rule inside an existing one:

> **If the doc name you would create reads as a behavior rather than an area a stakeholder would
> name, it belongs inside the area's doc.**

`article-card-placeholders` is a behavior. `article-card` is an area. The first is a Rule in the
second's doc, not a file of its own.

This is the same test as the transition tell, applied to the document's name rather than to its Rules —
and it catches the case the transition tell misses, because a behavior-named doc can be full of
perfectly good standing-behavior Rules and still be the wrong file.

### When the area has no doc yet

**A classification must never depend on whether documentation already exists.** The nature of the change
decides it; doc debt does not.

So when work is a genuine `new-capability` but the nearest area is **undocumented**, name the new doc at
**area level**, not at the level of the increment:

- ✅ `article-card` — the area, thin for now
- ❌ `article-card-placeholders` — the increment that happened to be first

Naming at area level makes the `new-capability` path converge on the same artifact `change-to` would
have produced. The classification stops being a fork with two outcomes and becomes one outcome with two
entry points. The debt then shows up honestly, as an area doc covering only what this increment
established — flag it for `/feature`'s from-code mode to backfill the rest.

**A thin doc is visible debt with a known remedy. A misnamed doc is invisible debt that pollutes the
catalog permanently.**

### Splitting a doc is editorial, not classification

Deciding that one capability doc has grown unwieldy and should become several is a **readability
judgment made deliberately**, not an output of classifying an increment.

**The classifier biases toward amend.** When in doubt between appending a Rule and creating a file,
append — splitting later is cheap and reversible, while un-polluting a capability catalog is neither.

### The key judgment

When a `change-to` ships, only its **user- or operator-observable** behavior folds into the
capability doc.

**Architecture and migration acceptance criteria** — "the service is unit-testable", "the
build is zero-warning", "the package leaves no trace" — stay in the shipped spec. They are
point-in-time criteria, not standing behavior. This is the line that keeps capability docs
evergreen instead of letting them decay into changelogs.

## Where artifacts live

Default layout. Every path is a default, overridable via the `paths.md` slot above.

| Path | Holds | Lifecycle |
|---|---|---|
| `ROADMAP.md` | Now / Next / Later / Recently shipped | Evergreen |
| `_features/<area>.md` | One file per capability, named by area of the system | Evergreen |
| `_work/<slug>/` | One directory per increment: `spec.md`, `plan.md`, `discovery.md`, `notes/`, `assets/` | Temporal |
| `_work/shipped/<slug>/` | Archived increments, moved as a unit | Temporal, closed |
| `docs/` | Durable human reference: runbooks, testing guides | Evergreen |
| `docs/audits/` | Dated audit reports, committed | Evergreen |
| `_scratch/` | Disposable artifacts — git-ignored wholesale | Throwaway |

Two things this layout is teaching, both deliberate:

**Lifecycle over type.** The temporal/evergreen split is the core of the method, so the
structure makes it physical. `_features/` stays root-prominent because that visibility is the
point — capability docs are the cross-functional artifact. Specs and plans mid-flight are
developer- and agent-facing and lose nothing by sitting one level down.

**The increment bundle.** A spec, its plan, its discovery notes, and its assets are created,
reviewed, and archived together, so they live together and archive with one move. If the
spec-to-plan relationship stops being one-to-one, that is absorbed inside the directory
without restructuring anything. Every spell's contract is just "look in `_work/<slug>/`."

**Artifact disposition.** Any spell that produces a report ends by asking whether the output
is **durable or temporal** → `docs/audits/` (committed) or `_scratch/` (git-ignored). Location
enforces commit status, so there is no separate decision to remember.

**Assets live with the artifact whose lifecycle they share.** Increment-scoped material goes
in `_work/<slug>/assets/` and archives with the bundle. Anything that outlives the increment
graduates to `docs/` or into the codebase when the work ships; `/feature update` prompts for
that as part of closing the loop.

## Feature docs

- One file per **capability**, named for an area of the system — never named after a piece of
  work (a migration, a refactor, a fix). See *Work types* above for what earns one.
- **The doc's name is independent of the increment's slug.** An increment called
  `placeholder-graphics-imageless-cards` can perfectly well amend a doc called `article-card`. Because
  they differ routinely, the spec records an explicit `feature-doc:` field naming the doc, which `/plan`
  and `/feature` carry through rather than deriving from the slug.
- Given/When/Then scenarios grouped under `Rule:` headings, in business language.
- **The source of truth for what the system does right now** — used for QA regression testing
  and developer onboarding.
- Draft scenarios come from `/spec`; they are verified and updated as the final step of every
  `/plan`.
- `/feature` creates or updates them. It also has a from-code mode for capabilities that
  already exist in the codebase but were never documented.
- Follows the `bdd-principles` reference skill: Example Mapping, Specification by Example,
  Ubiquitous Language.
- Specs remain historical records of original requirements and design rationale. Feature docs
  are current behavior. Keep the two straight — that distinction is load-bearing.

## Templates

`templates/spec.md` and `templates/feature.md` in this skill directory. Plans are generated
from their spec rather than templated.

## Project framing

Projects often have their own useful framing for what a unit of work is — a vertical slice
through particular layers, a component plus its schema and tests, whatever the architecture
makes natural. Where such a framing exists, plan and verify along it.

**Slot:** `.agents/config/conventions.md` → `## Unit of work`
**If empty:** infer the natural slice from the repo's own structure; if it is not obvious, plan
along the layers the spec actually touches and do not invent a framing.
