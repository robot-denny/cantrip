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

## Backlog

The pre-repo direction doc locked in several decisions that still need to be recorded
here: the three-layer split and its contract rules, vendored-copy-plus-lockfile
distribution, the skills-CLI role split, skills-over-commands, and the lifecycle-based
file layout.
