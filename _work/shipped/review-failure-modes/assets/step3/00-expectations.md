# Step 3 — manual check, written down BEFORE editing

Written at the start of the step, before any edit to
`skills/core/reference/reviewer-discipline/SKILL.md` and before the temporary induced-RED bullet
is added to `agents/code-reviewer.md`.

Tree state at time of writing: branch `review-failure-modes`, HEAD `fc86fc4`, clean.
Baseline gate: `scripts/check-contract.sh` → `14 checks passed.`

## What is under test

**Observable behavior**: whether the **merged** report — three reviewers' findings sorted into one
ranking under the shared severity scale — reports the *same* cancellation defect on the *same* line
**twice**.

Not whether a sentence exists in `SKILL.md`. Per `tdd-principles` → "The presence assertion", that
would couple to the artifact rather than the behavior, and would pass while the artifact was present
and useless. The defect this step prevents is only visible **after merging**, which is why a
single-reviewer run cannot be the test.

## Why the RED has to be induced

This behavior **already holds** at HEAD: the quality reviewer's checklist never mentions
cancellation, so the merged report already shows the finding once. Per `tdd-principles` → "Tests
written after the code": *"A test written after the code has to fail first anyway. Break the
behavior, or assert a wrong value, and watch it go red. A test that has never failed proves only
that it runs."*

So the RED is produced by deliberately breaking the boundary — temporarily adding a cancellation
bullet to `agents/code-reviewer.md` section 2, which is exactly the edit a future author would make
if the ownership were not written down. The statement's value is **prospective**: it does not change
today's merged report, it stops that edit from being made.

## Method

There is no automated harness for a review (`tdd-principles` → "When the project has no harness"),
so the signal is a recorded before/after.

Reviewer subagents cannot be dispatched from this context, so all three passes are performed by hand:
read `agents/code-reviewer.md`, `agents/perf-reviewer.md`, `agents/accessibility-reviewer.md` and the
shared contract in `SKILL.md`, apply each checklist to the fixture in turn, then merge under the
shared scale in the contract's report format.

- **RED run**: temporary cancellation bullet present in `agents/code-reviewer.md`, `SKILL.md`
  unchanged.
- **GREEN run**: temporary bullet reverted, ownership statement present in `SKILL.md`.

## The fixture

One change, two files, TypeScript on Node. Deliberately not .NET — the claim justifying core
ownership is that this boundary is not one language's problem.

| File | Content |
|---|---|
| `01-fixture.diff` → `src/sync/refresh-catalog.ts` | pulls a ~40 MB supplier catalog over one outbound call with no timeout and no cancellation signal — long-running work the caller cannot abandon |
| `01-fixture.diff` → `src/sync/hourly-sync.ts` | the scheduled caller, wrapping the pull in a `catch` that discards the failure and returns an empty list |

Kept clean on the other focus areas so any finding is attributable:

- The response status **is** checked before the body is read, so §2's unchecked-response bullet does
  not fire.
- The failure is **thrown onward**, not swallowed, in `refresh-catalog.ts`, and no caught error
  exists there — so Step 1's lost-origin bullet does not fire.
- Every logged value is passed as a **named field**, not folded into the message — so Step 2's
  folded-values bullet does not fire.
- No credential, no user input, no loop, no magic number, no UI, no markup.

**The swallow in `hourly-sync.ts` is deliberate and is the guard for lesson 3.** It sits on the very
same long-running call. The quality reviewer legitimately owns it (§2, "Swallowed exceptions and
empty catch blocks"), so it proves the ownership statement scopes to the *cancellation and timeout*
concern and does not read as "the quality reviewer ignores anything about long-running work".

## Expected results — RED (temporary bullet present)

| Reviewer | Expected on the fixture |
|---|---|
| perf | **Cancellation/timeout finding** on the outbound call in `refresh-catalog.ts` — dimension 5 ("missing cancellation propagation, missing client timeouts") and the heuristic "Streams and long-running outbound calls … must propagate cancellation, and must carry a timeout" |
| quality | **A second cancellation finding on the same line**, from the temporary bullet — plus its legitimate swallowed-exception finding in `hourly-sync.ts` |
| accessibility | **Nothing.** No markup, no component, no client-rendered output. Its Clean section says the checklist met no relevant code |

**Merged expectation — this is the RED**: the ranked findings table carries **three** rows, two of
which are the *same defect on the same line*, differing only in wording and in which reviewer
raised it. A reader working the list top-down fixes it, reaches the duplicate, and has to re-derive
that it is the same line.

If the merged RED report shows the cancellation finding only **once** even with the temporary bullet
in place, the fixture is not exercising the overlap and must be strengthened rather than the result
being accepted.

## Expected results — GREEN (bullet reverted, statement added)

| Reviewer | Expected |
|---|---|
| perf | Same single cancellation finding, unchanged. The statement does not touch the performance reviewer |
| quality | **No cancellation finding.** Its swallowed-exception finding in `hourly-sync.ts` **still fires** — that is the lesson-3 guard |
| accessibility | Nothing, unchanged |

**Merged expectation**: **two** rows. The cancellation defect appears **once**, attributed to the
performance reviewer. The swallow appears once, attributed to the quality reviewer. Two distinct
defects that happen to sit on the same call are two findings — that is not double-reporting, and the
statement must not collapse them.

## Cross-check against the rest of `SKILL.md`, before declaring done

Step 1's review found its first wording contradicted a rule elsewhere in the same file. Checking
prospectively this time:

| Existing text | Interaction | Required resolution |
|---|---|---|
| "Reporting balance" → **"Do not repeat one issue across many files unless the pattern itself is the finding"** | Nearest neighbour, and easy to confuse with this. It governs **one reviewer repeating itself across files**. The new statement governs **two reviewers repeating each other on one line** — a different axis, invisible to either reviewer alone | Complement it, do not restate it. The new statement must be about the boundary *between* reviewers, and must not be phrased as a repetition rule that reads like a weaker duplicate of the existing bullet |
| Severity section → "Each reviewer maps its own domain onto these. An accessibility Blocker is a keyboard trap … a quality Blocker is a committed secret or a crash path." | The statement's anchor. That sentence already assigns domains; this extends it to one boundary where two domains genuinely abut | Sit adjacent to it, in the same vocabulary of domains |
| Scope rule → "You review only the code explicitly present in the diff" | A reviewer deferring must not be read as licence to widen scope, or to comment on what another reviewer will say | The statement must say *stay silent*, not *cross-reference the other reviewer* |
| `perf-reviewer.md` dimension 5 and the streams heuristic | Already own cancellation and timeouts. No edit needed there | Out of scope for this step per the plan; the spec records a matching statement in `perf-reviewer.md` as an open question |

Also required by the plan's lessons: **state the reason, not just the rule** — three reviewers merge
into one ranked report, so a rule held in two reviewers reaches the reader twice.

## Gate expectation

- `scripts/check-contract.sh` — 14 checks pass, before and after. Check 8 (no technology names in L0)
  will not catch a framework's cancellation type or an interface name that is absent from its
  pattern, so the added lines get read by eye and grepped for one.
- `tests/run.sh` — 14/14, regression only. It exercises `check-install.sh`, untouched here.
- `grep -rn "cancel" skills/core/reference/reviewer-discipline/agents/code-reviewer.md` — **no
  match**, proving the induced-RED edit was reverted. The gate does not check for this, so a leftover
  bullet would ship the exact defect this increment exists to prevent, invisibly.
