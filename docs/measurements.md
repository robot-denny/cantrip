# Measurements

Sizes and timings the roadmap's open questions rest on, with the date and method for each.

**Why they live here rather than inline.** Every increment that touches a large file or the commit
gate remeasures it, and for a while each remeasurement stayed in the roadmap entry that prompted it.
That grew a queue into a lab notebook: one entry reached 58 lines, of which five sentences were the
decision and the rest was working. So the roadmap now carries **the current figure and the decision**;
this file carries how the figure moved and what was learned measuring it.

**A figure without its date and method is not a measurement.** Machines drift between sessions, and
a whole-gate number taken before a check landed is not comparable with one taken after. Every row
below says when and how.

---

## The commit gate — `scripts/check-contract.sh`

Check 1 (the client-identifier scrub) spawns two or three `grep` processes per scanned file,
unconditionally, so its cost tracks file **count** rather than content. One batched `grep` over the
same list finished in under 0.01s, with per-file exemption filtering then needed only for files that
actually produced a hit — normally none.

| | 2026-08-26 | 2026-08-28 | 2026-08-31 | 2026-09-03 |
|---|---|---|---|---|
| files scanned | 369 | 686 | ≈770 | 787 |
| check 1 alone | ≈3.0s | ≈5.4s | ≈6.0s | — |
| full gate | ≈5.7s | ≈8.0s | ≈9.1s | ≈9.4s |
| check 1's share | 53% | ≈67% | ≈66% | — |

**The 09-03 column is whole-gate only.** Checks 17 and 18 landed between it and 08-31, so an isolated
check-1 figure is not comparable without re-measuring the others.

**Its file count was wrong when first recorded, and the error is instructive.** It read 936, taken
from `git ls-files | wc -l` — the repo's *total tracked files*. Every other column counts what check 1
actually scans, which is that list run through its own extension allowlist minus the script itself:
787. Two different quantities, one label. The corrected growth from 08-31 is **+17 files**, not the
+166 the wrong figure implied, which also disposed of a causal story that was never there. Reproduce
the real number with `repo_md_files`'s own filter, never with a bare file count.

**The projection did not survive contact.** The 08-26 note projected +0.4s to +0.8s for that
increment's fixtures. Actual growth over eleven commits was +2.3s — low by roughly 3x, because the
fixtures arrived as *trees* (`.uda`, `.config`, `.cs`, dossier and audit inputs) rather than one file
per case, and file count is what this check charges for.

**The 08-31 column is the styleguide increment**, and it confirmed the diagnosis rather than adding
to it: one step's three fixture cases carried 33 `.uda` files between them and moved the full gate
**+0.39s on their own** — measured by interleaving stashed and unstashed runs, so session-to-session
drift on this machine could not be mistaken for the diff.

**Per-check millisecond figures are deliberately not kept here.** Four were, briefly, and three were
wrong within a session: two cited costs that a since-applied fix had already removed, and one was
attributed to a check number that had shifted underneath it — the label pointed at a different check
than the figure was taken from. They are volatile, they are numbering-dependent, and none of them
drives an open decision. Measure one when you need it, in isolation over 30 iterations, and cite it
where the decision is rather than storing it here. The one worth knowing without measuring: every
small check is milliseconds against check 1's seconds, so check 1 is the only one in a class of its
own.

---

## Unit sizes

### The guide scaffolding reference

Measured 2026-08-28 at 436 lines / ~28K; **remeasured 2026-09-01 at 623 / 44K**, grown by the
styleguide increment's showcase element types and its `## Design tokens` slot. Against
`umbraco-17-feature-backfill` at 242 / 16K that is 2.6x the next largest reference, up from 1.7x —
and the frontmatter trigger widened with the file, so a schema-only task now pays for the audit's
report format, the document types *and* the showcase schema.

The proposed seam is `## The audit's report shape`: it documents report output rather than schema,
addresses the spell rather than someone creating document types, introduces and uses "documentable
unit" entirely within itself, and would be roughly 110 lines alone.

### Mode-forked spells

`/guide`, measured 2026-08-29 at 564 lines / 36K when it was the largest unit in any pack;
**remeasured 2026-09-01 at 590 / 38K and no longer the largest** — the scaffolding reference is 623
and `/styleguide` 607. Its own growth was slight; what changed is what sits beside it.

| | total | mode A | mode B | cross-cutting | loaded but unused |
|---|---|---|---|---|---|
| `/guide` | 590 | 300 generate | 124 audit | 166 | **49%** for an audit cast |
| `/testify` | 755 | 509 capability | 178 audit | 68 | **33%** for an audit cast, 24% for a capability cast |

**Recounted 2026-09-01.** `/guide`'s split was first recorded as 300/124/166 after an earlier reading
gave 300/103/116 — which sums to 519 against a 590-line file. The generate figure was right, which is
why a 71-line hole survived two readings. Worth keeping as a caution: a three-part split that does not
sum to the whole is the cheapest possible check and it was not run.

**The same shape, not the same arithmetic.** `/testify` wastes proportionally less than `/guide`,
33% against 49%. The pattern is what recurs; the ratio is a property of how much cross-cutting
content each file happens to carry, and citing the two as equivalent makes a weaker case look
stronger. `/testify` is also the largest unit in `skills/core` — 2.3x `/feature` at 334 and 2.2x
`bdd-principles` at 340.
