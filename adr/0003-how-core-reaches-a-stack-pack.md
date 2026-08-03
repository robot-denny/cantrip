# 0003. How L0 reaches an L1 stack pack

**Status:** Accepted
**Date:** 2026-08-03

## Context

Extracting `/plan` forced the first real L0→L1 seam. The source command interleaves a generic
planning engine with two substantial stack-specific sections — a live-schema inspection block
naming six Umbraco MCP tools, and a nine-row table routing backoffice extension types to
specific `umbraco-cms-backoffice-skills:*` skills — plus a stack-shaped layer table and a
stack-specific typical step order.

The generic engine has to *use* that guidance when it exists, and work without it when no pack
is installed. But two principles constrain how:

- **L0 contains no fact about any specific technology.** A hardcoded reference to an Umbraco
  pack in core would break the invariant and make the public core-only baseline dishonest.
- **Spells chain by suggestion, never invocation.** A spell that reaches out and invokes another
  unit turns the toolbox into a funnel.

So L0 cannot name the pack, and cannot invoke it.

## Decision

**Packs contribute model-invoked reference skills with trigger-engineered descriptions. L0
spells describe the *kind* of guidance they want and let skill discovery do the routing.**

L0 `/plan` says: consult any installed stack-pack reference skills for stack-specific planning
guidance — live-schema inspection, extension-type routing, typical step order. It never names a
pack, a technology, or a skill.

The pack ships e.g. `umbraco-17-planning` as a reference skill whose description triggers on
planning work touching that stack. When the pack is installed, the guidance loads because the
description matches the work; when it is not, nothing loads and the generic engine proceeds.

This makes pack guidance **additive and invisible when absent** — the same property the slot
mechanism gives project facts, applied one layer up.

## Alternatives considered

**L0 names the pack skill directly** (`consult umbraco-17-planning if installed`). Rejected:
puts a technology fact in core, and core would accumulate a name per pack forever.

**L0 invokes the pack skill.** Rejected on the chain-by-suggestion principle, and it would make
core fail loudly rather than degrade quietly when no pack is present.

**A registry file the pack writes and L0 reads** (`.agents/toolkit/packs.json`). Rejected as
machinery that duplicates what skill descriptions already do. It would also need install-time
maintenance, giving the update flow one more thing to reconcile.

**Fold pack guidance into a slot.** Rejected: slots are for facts the *project* owns, and pack
guidance is authored and versioned by the toolkit. Conflating the two would mean projects
hand-maintaining content that should arrive by update.

## Consequences

- Core stays honestly pack-agnostic, so the core-only public baseline is a real product rather
  than a stripped one.
- Adding a pack later requires no change to any L0 file — the reason `optimizely` or any future
  pack costs nothing in core.
- The cost lands on **description quality**: a pack skill with a weak description silently fails
  to load, and the symptom is a plan that is merely generic rather than an error. Pack skill
  descriptions therefore need the same trigger-engineering rigor as core references, and
  `skill-creator` evals are the check.
- L0 must phrase its asks in terms of the *kind* of guidance wanted, not the technology. That is
  a small ongoing authoring discipline, verifiable by reading any L0 file for technology names.
- Projects can also satisfy these asks with their own L2 skills, since the mechanism does not
  care whether the responding skill came from a pack or the project. That is a free benefit, and
  the same path a project-authored design-system skill already uses.
