# 0010. Ship skills, not commands — and encode invocation posture in frontmatter

**Status:** Accepted — backfilled 2026-08-04; decided before this repository existed
**Date:** 2026-07-30 (decision) / 2026-08-04 (recorded) — amended 2026-08-18

> **Amended, not superseded.** The spell budget recorded in the last consequence below was stated as
> 6–8; it is now a working ceiling of ten. The reasoning it served is untouched — a spellbook has to
> stay learnable, and the answer to crowding is still to merge two stages or add a router rather than
> keep appending — but a budget already at its limit makes the first genuinely new stage a
> documentation rewrite, which is a cost the aim was never meant to impose. Nothing about posture, the
> verb/noun split, or the directory convention changes. A relaxed budget is not a reversed decision, so
> this is an amendment under [adr/README.md](README.md).

## Context

Both source projects implemented their workflow as **commands** — files under a commands directory, cast
as `/<name>`. Commands are being deprecated in favor of skills, so the toolkit had to ship skills.

That created a design problem the sources did not have. A command is *only* user-cast: it never fires on
its own, and the "spellbook" quality — a deliberate, side-effectful thing you choose to invoke — came for
free from where the file lived. **Skills are model-invoked by default**, so a straight port would turn
eight deliberate spells into eight things an agent might decide to run unprompted.

## Decision

**Ship skills, and move the spellbook affordance from file location into invocation posture.**

| Posture | Mechanism | Contents |
|---|---|---|
| **Spell** | `disable-model-invocation: true` — invisible to the model, cast only as `/<name>` | The orchestration chain: side-effectful and deliberate |
| **Reference** | A trigger-engineered description, loaded when it matches the work | Discipline and knowledge an agent should reach for |
| **Worker** | A subagent with its own context | The reviewers |

Supported by two conventions that make the split legible rather than arbitrary:

- **Verbs are spells; nouns are references.** `/spec`, `/plan`, `/retrofit` versus `bdd-principles`,
  `workflow`, `memory-discipline`.
- **The directory mirrors the taxonomy** — `spellbook/` and `reference/`.

## Why the directory convention earned its place three times over

It was adopted for legibility. It turned out to also:

1. **Make posture mechanically checkable** — gate check 5 asserts everything under `spellbook/` is
   user-cast-only and nothing under `reference/` is. A convention a check can enforce beats one that only
   reads well.
2. **Provide the install-scoping mechanism** — subpath-scoped installs are what deliver a core-only
   public baseline (ADR 0004), and they work because the taxonomy is a directory.

Neither was anticipated.

## Consequences

- `disable-model-invocation` is Claude-specific. It degrades gracefully elsewhere: a spell becomes a
  model-invocable skill rather than breaking, and the verb/noun naming plus the README catalog carry the
  intent to other agents.
- **Reference descriptions become load-bearing.** A reference with a weak description silently never
  loads, and the symptom is merely-generic output rather than an error — which is why descriptions here
  are long, and why the same rigor is demanded of pack skills (ADR 0003).
- Keeping spells at 6–8 was the stated aim; **amended 2026-08-18 to a working ceiling of ten**, so
  that a genuinely new stage has somewhere to land. The workflow set is nine as of 2026-09-01, when
  `/testify` shipped as the QA verb the raised ceiling was raised for; two further spells —
  `update-toolkit` and `setup` — are maintenance and onboarding rather than workflow stages, and are
  counted separately for that reason. Past the ceiling the answer is to merge two stages or add a
  router, not to append another.
