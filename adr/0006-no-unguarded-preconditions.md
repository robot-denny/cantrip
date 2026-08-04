# 0006. No instruction may assume its precondition exists

**Status:** Accepted
**Date:** 2026-08-04

## Context

ADR 0005 fixed a classifier that behaved correctly on well-documented repositories and incorrectly on
under-documented ones. That fix was good, but it was a **patch to one instruction**. The owner observed
that the underlying property — *resilience when something is not available or known up front* — should
be a principle guiding every decision, not a case-by-case repair.

Auditing the skills against that idea produced a sharp structural finding.

**Every slot fallback is guarded for absence. Almost no non-slot instruction is.**

| Precondition | Guarded? |
|---|---|
| `paths.md → Code layout` empty, no analogue exists | ✅ "if nothing analogous exists, say so rather than inventing a convention" |
| `stack.md → Tests` empty, project has no tests | ✅ "propose a location and flag it as a new convention" |
| `conventions.md → Branch naming` empty, no convention visible | ✅ "use `feature/<slug>`" |
| `conventions.md → Commit format` empty, history inconsistent | ✅ "plain imperative subject under ~72 chars" |
| `/block` Step 5 — "find the closest existing block and follow it exactly" | ⚠️ partial |
| `umbraco-17-planning` — "follow the closest existing analogue" | ⚠️ one clause |
| `design-system-authoring` Steps 1 and 3 — find the mechanism, copy the exemplar | ❌ **zero absence clauses** |
| `/feature` Guard — "find the existing capability doc and update *that*" | ❌ **no case for not finding it** |

The cause is not carelessness. **Slots have a forcing function and non-slot instructions do not.** Check
4 refuses a `**Slot:**` without an adjacent `**If empty:**`, so writing a slot *made* me think about
absence, every time, without discipline being involved. Nothing forced the same question for "copy the
closest existing component" — so the thinking happened only when I happened to remember, and mostly I
did not.

That the `/feature` Guard is on the unguarded list is the sharpest evidence: it is the exact instruction
ADR 0005 was about. I fixed the classifier in the `workflow` skill and left the local instruction that
depends on the same precondition untouched, one increment earlier.

## Decision

**No instruction may assume its precondition exists.** Any instruction depending on something being
present — a document, an exemplar, a harness, a convention, a history, an established mechanism — must
state what to do when it is not.

And the response follows a **defined ladder**, most to least preferred:

| Rung | Response | When |
|---|---|---|
| 1 | **Infer from the project** | Something comparable exists to read |
| 2 | **Borrow from a named external reference** | The user can point at another codebase, published documentation, or a sibling project. Never assume one exists — ask for it, and never silently import conventions from elsewhere as though they were the project's. |
| 3 | **Seed thin, marked to grow** | The artifact can be created minimally now and accrete through use |
| 4 | **Proceed without, and say so** | The step is genuinely optional; name what was skipped |
| 5 | **Ask** | Nothing above applies, and proceeding wrongly would be costly |

And one hard prohibition, which is the whole point: **never fabricate.** Never invent a convention, a
layout, or a mechanism and present it as the project's own. A stated gap is recoverable; an invented
convention gets followed, copied, and becomes the project's real convention by accident.

## Rung 3 is the interesting one, and it already runs through the toolkit

"Seed thin, accrete through use" turns out to be a pattern the toolkit had already adopted three times
without naming it:

- **ADR 0005** — an undocumented area gets a thin area-level doc now, flagged for from-code backfill.
- **`memory-discipline`** — starter facts ship as *claims to verify*, and become earned facts once a
  project confirms them.
- **`/plan`'s Tests fallback** — a project with no harness gets a proposed location recorded as a new
  convention rather than a refusal.

Naming it makes it reachable deliberately rather than by luck. **The generalization: where a precondition
is missing but creatable, create it thin and make the thinness visible.** Visible debt with a known
remedy beats both a hard failure and a confident invention.

## Consequences

- Four unguarded instructions fixed, including the `/feature` Guard that ADR 0005 should have caught.
- **A forcing function added**, because the audit's whole lesson is that a principle without one gets
  applied inconsistently. Gate check 10 requires an exemplar-dependent instruction to carry an absence
  clause nearby — narrow, but it is the exact pattern that slipped twice.
- The greenfield case is now explicitly in scope rather than implicitly out of it. The pilot next month
  starts with no blocks, no design system, and no feature docs — every rung-3 path exists for that.
- Cost: instructions get longer, and some absence branches will be speculative until a real greenfield
  project exercises them. Preferable to the alternative, where the branch does not exist at all and an
  agent invents its way past the gap.
