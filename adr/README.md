# Architecture Decision Records

Cantrip is run like a product: decisions that shape the toolkit are recorded here rather
than living only in chat logs or a direction doc.

## When to write one

Write an ADR when a decision constrains future work — layering and contract rules,
distribution and update mechanics, invocation posture conventions, what ships versus what
stays in the consuming project. Skip it for routine content edits.

Friction discovered while piloting the toolkit on a real project is a prime ADR source;
so are decisions settled in issue threads, which should be harvested here rather than left
buried.

## Convention

- One file per decision: `NNNN-kebab-case-title.md`, numbered sequentially from `0001`.
- Copy [_template.md](_template.md) to start.
- Never rewrite history — supersede instead. Mark the old record `Superseded by NNNN` and
  link both ways.
- **Amend in place when nothing is reversed; supersede when something is.** The test: does the new
  material contradict a decision the record already made, or does it add a rule that decision
  implied but never stated? Adding gets `**Amended, not superseded**` under the status line, a dated
  note saying what was added and why, and new sections numbered after the existing ones. Reversing
  gets a new record. Supersession is the wrong instrument for an addition, because it retires
  reasoning that still holds — and amending is the wrong instrument for a reversal, because a reader
  who acts on the amended record would act on a decision the project has abandoned.
- **A record may describe something whose name later changed elsewhere.** Leave the observed name and
  add a dated note pointing at where the thing lives now. Rewriting it would make the record a less
  accurate account of what was actually seen at the time, which is the one thing an ADR is for.

## Decided

- **0007 — repository ownership.** Stays under a personal account for now. The costs of a later move are
  recorded there, including why they grow with adoption and become payable by consumers rather than by us.
- **0012 — pack companions are recommended, never required.** A pack may route work to external skill
  sets it does not own, declares them machine-readably so `/setup` can report enablement, and documents
  them in the README. Also settles what the pack absorbs versus points at: durability is ours, library
  idiom is theirs.
- **0013 — attribution for adapted external work.** Courtesy credit in the README for the two units
  adapted from published skills, a three-tier rule for when a license notice must ship rather than merely
  be recorded, and the register itself. The one rule here with no automated gate, which it says so.
- **0014 — the `dotnet` pack, and the detection line it needed.** Language and platform guidance is a
  pack of its own rather than part of the CMS pack, which makes it the first real test of 0003's promise
  that a new pack costs nothing in core. Also adds an optional `**Detect:**` line to a slot declaration,
  so a pack can tell `/setup` how to read an answer the repository already holds — the pack owns the
  recipe, core owns the instruction to honour one.

- **0015 — what a stack pack is, and what it owes.** Why a pack is worth having at all: a model's
  knowledge of a platform is every version at once, and a pack pins the one in use so it stops
  interpolating. Also that a pack has no required shape, and the seven rules the `dotnet` increment
  learned by review rather than by design. Records two open questions — how a pack declares the
  version it targets, and what content evals are for.
  **Amended 2026-08-17** with four rules that splitting a pack into three surfaced: the variant axis,
  the replacement operation and its naming rules, where portable criteria end and stack-specific
  detection recipes begin, and registering every reader of a shared slot. An amendment rather than a
  new record because nothing in the original was reversed.

- **0016 — a coverage status names an observation, not a diagnosis.** A failing test may mean unbuilt
  work, a regression, or a wrong doc, and nothing available when the row is written tells those apart —
  so the status records `Test failing` and leaves the cause to the surrounding report. Also admits
  `Ruled out — <reason>` on the grounds that a *decision* is durable where a *blockage* is not, and
  records what the five-status column costs: two independent facts in one cell, with the split parked
  rather than taken.

- **0017 — when a gap earns a runbook.** A three-part conjunctive test — the precondition is mechanical
  and identical everywhere, the toolkit deliberately declines to automate it, and getting it wrong fails
  silently — deciding which gaps get a human-facing runbook in `docs/runbooks/` rather than a README per
  unit or per pack. Also: the guard names the runbook, because discoverability is the deliverable; and a
  runbook cites what it restates. Records that a gate can see an absence clause exists but not that the
  absence it describes is the only one, which is how the guides gap survived [0006](0006-no-unguarded-preconditions.md).

## Backfilled

Five decisions predate this repository, having been settled in a direction document that is not in the
repo. All are now recorded here, so the reasoning lives with the code rather than in a file a consumer
will never see:

| Decision | Where |
|---|---|
| The three-layer split and its contract rules | [0001](0001-layer-contract-and-slots.md) |
| Vendored-copy-plus-lockfile distribution | [0008](0008-vendored-copy-distribution.md) |
| The skills-CLI role split | [0009](0009-skills-cli-role-split.md) |
| Skills rather than commands, with posture in frontmatter | [0010](0010-skills-not-commands.md) |
| Lifecycle-based file layout | [0011](0011-lifecycle-file-layout.md) |

Each is marked *backfilled* with both its decision date and its recording date, and each notes what has
been learned since — several were validated or complicated by things that only surfaced during
extraction.

**0010 amended 2026-08-18.** The spell budget moves from a stated aim of 6–8 to a working ceiling of
ten, leaving room for a new stage without a documentation rewrite. An amendment rather than a new
record because the principle behind the budget — merge or route rather than append — is unchanged, and
nothing about invocation posture is touched.

## Backlog

Empty. Add an entry when a decision is deferred rather than made.
