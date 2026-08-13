# Step 1 — validation log

## Automated

```
$ scripts/check-contract.sh            # before the edit (baseline)
14 checks passed.

$ scripts/check-contract.sh            # after the edit
14 checks passed.

$ tests/run.sh                         # regression
14/14 cases passed.
```

## By-eye check for a technology name check 8 cannot catch

Check 8's `TECH_PATTERN` contains none of `ILogger`, `CancellationToken`, `Serilog`, or any
language keyword, so a green gate is not proof. The added lines were scanned with a much wider
pattern:

```
$ grep -inE 'throw|raise|catch|except|panic|defer|rescue|finally|InnerException|StackTrace|
stack trace|Exception\b|\bErr\b|errorf|%w|wrap\(|ILogger|Serilog|CancellationToken|Task\b|
async|await|golang|\bgo\b|java|python|c#|dotnet|node|promise' added-lines.txt
exit=1   (no match — the pass)
```

The bullet names no keyword, no error type, no interface, and no library. It also avoids
"cause" and "stack trace", both of which lean on one family of languages.

## Manual

| Check | Evidence | Result |
|---|---|---|
| Recorded before/after across four diffs | `00-expectations.md` (written first), `10-red-review-output.md`, `20-green-review-output.md` | Pass — 4/4 matched the written-down expectation in both runs |
| RED genuinely produced no lost-origin finding | `10-red-review-output.md` — diffs 1 and 2 both returned zero findings | Pass — premise holds, the gap was real |
| Log-and-continue diff yields **one** finding, not two | `20-green-review-output.md`, diff 4 → "Why this is one finding and not two" | Pass — the bullet's propagation clause excludes it by construction |
| Positives are not C# | Java (throws) and Go (returns errors) | Pass |
| Severity from the existing four-level scale | Both positives → **Major** | Pass — no new level |
