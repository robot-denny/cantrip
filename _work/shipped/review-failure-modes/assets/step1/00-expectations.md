# Step 1 — manual check, written down BEFORE editing

Written at the start of the step, before any edit to
`skills/core/reference/reviewer-discipline/agents/code-reviewer.md`.

## What is under test

**Observable behavior**: whether a review of a given diff *reports a lost-origin finding*.
Not whether a bullet exists in a file — per `tdd-principles`, that is a presence assertion
and is fragile by construction.

## Method

There is no automated harness for a review, so the RED→GREEN signal is a recorded
before/after (`tdd-principles` → "When the project has no harness").

The review is performed by applying the checklist in
`skills/core/reference/reviewer-discipline/agents/code-reviewer.md` plus the shared contract
in `skills/core/reference/reviewer-discipline/SKILL.md` to each diff, reporting in the
contract's format.

- **RED run**: apply the checklist **as it exists before the edit**.
- **GREEN run**: apply the checklist **as it exists after the edit**.

## The four diffs

| # | File | Language | Error mechanism | Shape |
|---|---|---|---|---|
| 1 | `01-positive-throwing.diff` | Java | throws | handler catches, throws a new exception carrying only the message — original dropped |
| 2 | `02-positive-returning.diff` | Go | returns errors | handler replaces the received error with a fresh one — original dropped |
| 3 | `03-negative-wrapped.diff` | Go | returns errors | handler replaces the error **while carrying the original** |
| 4 | `04-negative-log-and-continue.diff` | Python | throws | handler logs the error and continues — nothing propagates |

Neither positive is C#. That is deliberate: the claim justifying core ownership is that this
defect is not C#-shaped, and a C# diff cannot demonstrate it.

## Expected results — RED (before the edit)

| # | Expected | Reasoning |
|---|---|---|
| 1 | **No** lost-origin finding | Section 2's nearest bullet is "Swallowed exceptions and empty catch blocks". Diff 1 does not swallow — the failure propagates as a new exception — so no bullet in the checklist reaches it. |
| 2 | **No** lost-origin finding | Same: the error is handled and a replacement returned, so nothing is swallowed and no bullet reaches it. |
| 3 | **No** lost-origin finding | Correct practice; nothing should fire before or after. |
| 4 | **Exactly one** finding — swallowed exception | Already covered by the existing bullet. |

If any of diffs 1 or 2 *does* draw a lost-origin finding in the RED run, the step's premise
is wrong (the check was already covered) and that must be reported rather than papered over.

## Expected results — GREEN (after the edit)

| # | Expected | Assertion |
|---|---|---|
| 1 | **Lost-origin finding raised** | Cites the handler line; says the original point of failure is discarded; names carrying the original inside the replacement as the fix. Severity from the existing four-level scale. |
| 2 | **Lost-origin finding raised** | Same, with wording that does not assume exceptions. |
| 3 | **No new finding** | The wrap carries the original, so the check must not fire. |
| 4 | **Still exactly one finding** | The swallowed-exception finding only. **Not** both a swallowed-exception and a lost-origin finding. |

## Gate expectation

`scripts/check-contract.sh` — 14 checks pass, both before and after. Check 8 (no technology
names in L0) will not catch a library or interface name that is not in its pattern, so the
new bullet also gets read by eye for one.
