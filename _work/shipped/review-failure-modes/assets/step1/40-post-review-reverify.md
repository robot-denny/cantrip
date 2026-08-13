# Re-verification after the review rewording

The bullet's wording changed after `/code-review`, which invalidates `20-green-review-output.md` — that
evidence was for the old text. A reworded behavioral instruction needs its evidence refreshed, and
specifically: the added exculpatory clause ("Sanitizing what an external caller is shown is not this
finding, as long as the origin survives internally") could have suppressed a true positive.

Applied the reworded entry to the same four fixtures.

| Fixture | Expected | Result | Why |
|---|---|---|---|
| `01-positive-throwing.diff` | finding | **finding** | `TransportFailure failure` is bound and never used; the new error carries nothing and nothing logs it. Origin recorded nowhere. Failure reaches the caller, so the swallowed-error entry does not apply |
| `02-positive-returning.diff` | finding | **finding** | `errors.New(...)` discards the checked error. Origin recorded nowhere; the failure is returned |
| `03-negative-wrapped.diff` | no finding | **no finding** | the wrap carries the original, so the origin survives |
| `04-negative-log-and-continue.diff` | no finding (falls to swallowed) | **no finding** | the failure never reaches the caller — the loop continues — so this entry's condition fails and the swallowed-exception entry owns it. One finding, not two |

Behavior preserved: 4/4 match the original expectations in `00-expectations.md`.

## The clause was tested, not just added

Fixture 1 is the case that matters here. Its message — `"Invoice " + reference + " could not be loaded"` —
reads exactly like a deliberately sanitized external message, which is the shape the new clause exempts.
It is **still flagged**, because the clause is conditioned on the origin surviving internally and here it
survives nowhere: nothing logs `failure`.

That is the difference between a conditional carve-out and a loophole. Had the clause been written as a
blanket "sanitized responses are fine", fixture 1 would have gone quiet and the review's Finding 1 would
have been traded for a worse defect — a rule that misses the common real case.

## Mechanical checks

- `scripts/check-contract.sh` → `14 checks passed.`
- `tests/run.sh` → `14/14 cases passed.` (regression only)
- Technology-name grep over the added lines, using a pattern far wider than check 8's
  (`throw|raise|catch|except|panic|defer|InnerException|StackTrace|ILogger|Serilog|CancellationToken|async|await|java|python|golang|go|c#|dotnet|node|rust`)
  → no match

## Still open, deliberately not fixed here

The entry is now **six lines** among one-liners. The implementing worker flagged the four-line version as
stylistically uneven; encoding the sanitization scope made it longer, not shorter. Correctness beat brevity,
which is the right trade, but the unevenness is real and gets sharper when Step 2 adds a second long entry.
Worth deciding then whether section 2 wants rebalancing — out of scope for a review fix.
