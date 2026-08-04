# 0013. Attribution for adapted external work

**Status:** Accepted
**Date:** 2026-08-04

## Context

Two units here are adaptations of publicly published skills, both by the same author:

| Cantrip unit | Adapted from | Author | License |
|---|---|---|---|
| `tdd-principles` (core reference) | the `tdd` skill | Matt Pocock, `mattpocock/skills` | MIT |
| `/explore` (core spell) | the `grill-me` skill | Matt Pocock, `mattpocock/skills` | MIT |

`/explore` predates this repository. It was written in the demo project in July 2026, and its commit
message there records exactly what was taken — *"one question at a time, branch-by-branch tree walk,
look-before-you-ask"* — then extended with problem-framing and option-generation stages and a
phase-dependent recommendation policy.

**That record lives in another repository's history and did not travel with the extracted skill.** Within
a month of being written down, a real lineage had become invisible in the place the code now lives. This
ADR exists as much for that reason as for the licensing one.

The MIT license requires its notice to accompany *"copies or substantial portions of the Software."* So
the question is not whether to be polite — it is whether either adaptation is a copy.

One structural fact sharpens it: **installs are subpath-scoped to `skills/`.** `LICENSE`, `README.md`, and
`adr/` never reach a consuming project. The three places contract check 1b names as the homes for
attribution are precisely the three a consumer never sees.

## Decision

**Attribute by courtesy in the documentation, and let the tier decide whether anything more is owed.**

Which tier a borrow falls into is determined by *what was taken*, not by how much it felt like borrowing:

| Tier | What was taken | What is required |
|---|---|---|
| **1 — influence** | Ideas, structure, terminology; no expression | Nothing is owed. Credit anyway, in the README and here |
| **2 — adaptation** | Copied or closely adapted expression, permissive license | The notice must travel **with the shipped skill**; an ADR is insufficient |
| **3 — share-alike** | Anything under copyleft terms | Decline, or accept the terms for the whole distribution knowingly |

**Both current adaptations are tier 1**, and neither copied text.

For `tdd-principles`, the concepts are not the source's to license: behavior-over-implementation is Fowler
and *Growing Object-Oriented Software*, red-green-refactor is Beck, tracer bullets are *The Pragmatic
Programmer*, and "tautological test" is long-established vocabulary. What was genuinely the source's was
**selection and arrangement** — and ours went to twelve sections from four, rejected three of its
positions outright, and added a half with no counterpart there (no-harness signal, evidence over
attestation, coverage honesty, agreement-at-plan-time).

For `/explore`, what was borrowed is interview *mechanics*, re-expressed and then extended by two whole
stages that change what the skill is for: the source interrogates a plan you already have, while
`/explore` runs before a decision exists and widens the option space.

So both get credit in `README.md` under Acknowledgements, and the reasoning lives here. No notice ships,
because none is owed.

## Alternatives considered

**Say nothing, since nothing is owed.** Rejected. Attribution is cheap, it is the norm in this ecosystem,
and it does a job beyond courtesy: a reader who wants to re-check a borrowed rule against its source needs
to know there is one. `/explore` is the cautionary case — its lineage was lost to this repo almost
immediately, and nobody noticed until the question was asked directly.

**Put the credit inside the skill files.** Rejected at tier 1. A skill is instructions to a model;
provenance is metadata it does not need while executing, and check 1b already establishes that a shipped
skill is the wrong home for authorship claims. Tier 2 reverses this, which is the whole reason the tiers
are separated rather than collapsed into one rule.

**Build a NOTICE mechanism inside `skills/` now.** Rejected as premature. There is no tier-2 borrow to
carry, and machinery with nothing in it decays unnoticed. Recorded as a known gap instead, so the next
person does not have to rediscover that `adr/` does not ship.

## Consequences

- **The register above must be maintained by hand.** A future adaptation adds a row.
- **There is deliberately no gate for this one.** A script cannot distinguish an adaptation from
  independent authoring — the fact that a borrow happened exists only in the author's head. So this rule
  relies on the ADR being read, which makes it weaker than every other rule in this repo. Stated plainly
  rather than papered over: if adaptations become common, the register will drift, and the mitigation is
  to record the lineage **in the same commit as the adaptation**, which is what `/explore` did right and
  what extraction then discarded.
- **`docs/contract.md` now separates two kinds of attribution** that check 1b's wording had conflated:
  our own authorship, which must never sit in a shipped skill, and a third party's license notice, which
  may be required to.
- **The shipping gap is recorded, not closed.** A tier-2 borrow would need a notice inside the shipped
  tree, and check 1b would need an exemption path rather than a blanket prohibition.
- **This is a common-sense reading of license terms and community norms, not legal advice.** A tier-2
  borrow is the point at which that stops being good enough.
