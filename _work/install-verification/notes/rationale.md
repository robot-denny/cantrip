# 4.1 — self-hosting: what casting the chain actually revealed

**Date:** 2026-08-03
**Increment:** install-verification, run end-to-end through the real spells.
**Result:** the chain works. Five findings, three of them defects the process caught rather than
prevented.

## What was cast, and what it produced

`/spec` → `/plan` → `/implement-step` → `/feature update` → `/code-review`, on a genuine gap named at
3.3: installed is not the same as working. Output: `scripts/check-install.sh`, the repo's first test
harness (11 fixtures, 3 install layouts), and Cantrip's first `_features/` doc.

## The slot fallbacks work, and this was their first real exercise

Cantrip has no `.agents/config/`, so every slot was empty — the fresh-install condition ADR 0001
names as the acceptance test. Three fallbacks fired for real:

| Slot | Fallback behavior | Outcome |
|---|---|---|
| `conventions.md → Branch naming` | infer prefix from `git branch -a` | no convention visible → `feature/install-verification` |
| `paths.md → Code layout` | find the closest existing analogue | found `scripts/check-contract.sh`, followed its structure |
| `stack.md → Tests` | infer from existing test files, else propose and flag as new | **no tests existed at all** → proposed `tests/`, flagged as a new convention in Key Decisions |

That third one is the interesting result. The fallback surfaced that this repo had **no test harness
whatsoever** — `check-contract.sh` had only ever been probed by hand. An empty slot did not merely
degrade gracefully; it made a real gap visible and told the plan to record the decision. That is the
degradation design working better than specified.

## `/code-review` found a real defect in my own implementation

Ran inline via the documented fallback rather than parallel dispatch. It found one **Major**: a
selective install reported `installed: 1, broken: 0` and said nothing about the other twelve skills,
leaving FR1 ("report which resolve **and which are missing**") only half met.

The cause is worth recording because it is a generalizable trap: **I let the fixtures drive the
design.** Fixtures carry 5 of 13 skills, so comparing against the full roster would have failed them —
and instead of fixing the fixtures I quietly narrowed the requirement, then wrote a Key Decision
rationalizing it. The spec was right and the plan talked me out of it.

Fixed by reporting absent roster skills as *informational* — a selective install is legitimate, so it
must not fail, but silence about it is not verification. Then added a `selective-install` fixture and a
scenario to the feature doc, so the finding is covered rather than merely mentioned.

Also found and fixed: two Minor issues (an undocumented shallow JSON parse, now commented) and one
noted-not-fixed (word-splitting on asset paths, none of which contain spaces).

Per `reviewer-discipline`, the accessibility reviewer correctly had nothing to report — no UI in the
diff — and said so rather than padding.

## A malformed fixture cost real debugging time

The first fixture pass was hand-built inline and one came out with a directory named after an
unexpanded shell variable. The resulting failure was **indistinguishable from a bug in the code under
test**, and I debugged the wrong thing first.

Fixed structurally: `tests/make-fixtures.sh` generates every fixture, so they are reproducible and each
case's *intent* is readable in one place. A suspicious failure can now be cleared by regenerating
instead of inspecting trees. The `tests/README.md` records why.

## Where self-hosting cannot fully substitute for a consumer

Honest limits on what this proved:

- **`/implement-step`'s core value is context isolation, and I could not get it.** Its whole point is
  dispatching a step to a fresh context so the main one stays clean. Executing steps inline — the
  documented fallback — tests whether the *step prompts* are self-contained (they were; Step 1 ran from
  its prompt alone) but not the isolation benefit. A real consumer with worker dispatch gets something
  this run did not exercise.
- **The reviewers ran inline, not in parallel.** Same fallback, same gap: severity and merge discipline
  were exercised, concurrency was not.
- **I am not a naive user.** I wrote these spells, so I cannot test whether their instructions are
  clear to someone who has not. Every ambiguity I resolved correctly by memory rather than from the
  text is an ambiguity a consumer would hit. That is the specific thing only 4.2 or the pilot can find.

## Verdict

The chain produced better work than writing the script directly would have. Concretely: the spec's
edge-case section forced the three-layout question up front, the work-type classification correctly
earned a feature doc, and `/code-review` caught a requirement I had quietly narrowed. The `Next:`
chaining held throughout — every stage pointed at the right next one, and nothing auto-cascaded.
