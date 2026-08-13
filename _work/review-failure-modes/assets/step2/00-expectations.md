# Step 2 — manual check, written down BEFORE editing

Written at the start of the step, before any edit to
`skills/core/reference/reviewer-discipline/agents/code-reviewer.md`.
Tree state at time of writing: branch `review-failure-modes`, HEAD `00c9d9e`, clean.
Baseline gate: `scripts/check-contract.sh` → `14 checks passed.`

## What is under test

**Observable behavior**: whether a review of a given diff *reports a folded-values finding on a
log call*. Not whether a bullet exists in a file — per `tdd-principles`, that is a presence
assertion and fragile by construction.

## Method

There is no automated harness for a review, so the RED→GREEN signal is a recorded before/after
(`tdd-principles` → "When the project has no harness").

The review is performed by applying the checklist in
`skills/core/reference/reviewer-discipline/agents/code-reviewer.md` plus the shared contract in
`skills/core/reference/reviewer-discipline/SKILL.md` to each diff, reporting in the contract's
format.

- **RED run**: apply the checklist **as it exists before the edit** (HEAD `00c9d9e`, section 2
  carries six bullets, the last being Step 1's lost-origin entry).
- **GREEN run**: apply the checklist **as it exists after the edit**.

## The two diffs

| # | File | Language | Shape |
|---|---|---|---|
| 1 | `01-positive-interpolated-log.diff` | TypeScript (Node) | log call builds one message string with an order number and a retry count spliced into it |
| 2 | `02-negative-fixed-message.diff` | Ruby | log call with a fixed message and no values at all |

Neither is .NET. That is deliberate: the claim justifying core ownership is that this defect is
not .NET-shaped, and a .NET diff cannot demonstrate it.

Both diffs are deliberately clean on every other focus area, so that any finding they draw is
attributable to the check under test:

- Diff 1: the gateway result's `accepted` flag is checked before use, the failure is surfaced to
  the caller as a return value (not swallowed, and no error object exists to lose the origin of),
  no loop, no magic number, no credential, names express intent.
- Diff 2: three statements, no loop, no error handling, no values anywhere.

## Expected results — RED (before the edit)

| # | Expected | Reasoning |
|---|---|---|
| 1 | **No folded-values finding** | Section 2's bullets cover unvalidated input, missing null checks, swallowed exceptions, lost error origin, missing async error boundaries, and unchecked response status. None reaches how a log call assembles its message. Section 3 (clarity) covers names, comments, function length, magic values, formatting — none of which this line violates. So no bullet in the checklist reaches it. |
| 2 | **No finding** | Nothing is wrong with it, before or after. |

If diff 1 *does* draw this finding in the RED run, the step's premise is wrong (the check was
already covered) and that must be reported rather than papered over.

## Expected results — GREEN (after the edit)

| # | Expected | Assertion |
|---|---|---|
| 1 | **Folded-values finding raised** | Cites the log line; states what is *lost* — that the order number and retry count can no longer be filtered, grouped, or counted on, because every occurrence is a distinct message string; recommends passing them alongside the message as named fields. Severity from the existing four-level scale. Must not rest on "interpolation was used" alone. |
| 2 | **Still no finding** | The fixed message carries no values, so there is nothing to separate out. The check must be **structurally** unable to fire here — its qualifying condition has to be the presence of at least one value in the call, not the reviewer correctly guessing intent. |

## Guard against a wrong recommendation

A value that should not be logged **at all** — a credential, personal data — is section 1's
exposure finding, whose fix is to remove it, not to move it into a field. The new bullet must not
read as advice to relocate such a value. Checked by eye against section 1 before declaring done.

## Gate expectation

`scripts/check-contract.sh` — 14 checks pass, both before and after. Check 8 (no technology names
in L0) will not catch a logging library or interface name that is absent from its pattern, so the
new bullet also gets read by eye for one.

## Scope note

Section 2's existing entries are mostly one-liners; Step 1's is six lines. Whether this entry aims
short or takes the length correctness needs is a deliberate call, recorded in the final report.
Rebalancing the section is out of scope for this step either way.
