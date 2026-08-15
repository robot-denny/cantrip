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

## Backlog

Empty. Add an entry when a decision is deferred rather than made.
