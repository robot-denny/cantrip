# Step 6, case D — a rename and a reflowed comment

A planted change, not a real repository edit. It lives here as a document and is handed to the
quality reviewer as the change under review.

**What is planted**: nothing. A local variable is renamed to say what it holds, and the comment above
it is reflowed to the column width. No behaviour changes, no input is read, nothing is stored,
logged, rendered, or queried. There is no security-relevant code anywhere in the change.

**What the case asserts**: the review names **no** OWASP area and makes **no** claim that the change
was reviewed against the standard.

## The diff under review

```diff
diff --git a/src/Web/Reporting/DurationFormatter.ts b/src/Web/Reporting/DurationFormatter.ts
index 3f2a1b0..8e4c5d7 100644
--- a/src/Web/Reporting/DurationFormatter.ts
+++ b/src/Web/Reporting/DurationFormatter.ts
@@ -1,14 +1,13 @@
-// Formats a duration for the report footer. Durations under a minute are shown in seconds with one
-// decimal place, and anything longer is shown as whole minutes and seconds.
+// Formats a duration for the report footer. Durations under a minute are
+// shown in seconds with one decimal place, and anything longer is shown as
+// whole minutes and seconds.
 export function formatDuration(milliseconds: number): string {
-  const t = milliseconds / 1000;
+  const totalSeconds = milliseconds / 1000;
 
-  if (t < 60) {
-    return `${t.toFixed(1)}s`;
+  if (totalSeconds < 60) {
+    return `${totalSeconds.toFixed(1)}s`;
   }
 
-  const m = Math.floor(t / 60);
-  const s = Math.round(t - m * 60);
-
-  return `${m}m ${s}s`;
+  const minutes = Math.floor(totalSeconds / 60);
+  const seconds = Math.round(totalSeconds - minutes * 60);
+
+  return `${minutes}m ${seconds}s`;
 }
```

## The two failure shapes

Both are failures, and Step 5's case B showed the second one live before any instruction existed:

1. **Named areas.** Listing categories as checked and clean — "no authorization decision (A01), no
   input reaching a query (A05)" — on a diff that contains no code in those areas
2. **A blanket claim.** "Nothing in this diff falls under any A01–A10 category", or "no OWASP category
   applies here". No area is named individually, but it still reads as all ten checked

Saying nothing about security is the pass. So is a plain statement about the diff — "this change
contains no security-relevant code" — which describes what was changed rather than claiming coverage.

## Run 1 — before the edit to `code-reviewer.md`

Dispatched the same way as case C, with no mention of `Clean`, coverage, areas, or OWASP in the
prompt.

**Outcome: RED. This is the failure the step exists to fix.** The review reports no findings, approves
the change — and its `Clean` section claims a sweep of the whole standard. Verbatim:

> - **Security (A01–A10)**: swept — the function takes a `number` and returns a formatted `string` via
>   `toFixed`/template literal; no user-controlled string is interpolated, no I/O, no secrets. Nothing
>   to cite.

That is failure shape 2, exactly as written above before the run. The word is **swept**, the range is
**A01–A10**, and the diff renames three local variables and rewraps a comment. Ten security areas are
claimed as checked on a change with no security-relevant code in any of them.

The second half of the sentence is fine on its own — "no user-controlled string is interpolated, no
I/O, no secrets" describes the diff, which is a pass. The defect is the label in front of it. A reader
scanning `Clean` sees `A01–A10: swept` and takes away that the change was reviewed against the
standard and came back clean, which is not what happened. Nothing was there to sweep.

**This is the RED Step 6 needed, and it landed on case D rather than case C.** Case C's naming
behaviour already works; the restraint half is what is missing. The two cases traded roles against the
prediction, and the step's premise survives — the instruction is still needed, just for the opposite
reason.

### Why no gate can catch this

The claim is true-shaped and unfalsifiable by inspection. Nothing in the repository can tell that
"swept" was not earned, because the areas named are the ones a clean diff would legitimately have
nothing in. It reads as thoroughness. This is the entire reason Step 6 is a step rather than a
paragraph folded into Step 5.

## Run 2 — after the edit to `code-reviewer.md`

A fresh session at HEAD `20bb4ff`, clean tree, opened with the probe described in
`step6-case-c-clean-with-security-code.md`: the dispatched reviewer answered `PRESENT` and quoted the
new section verbatim, so the definition it read is the committed one. The case was then dispatched
exactly as in run 1, with no mention of `Clean`, coverage, areas, or OWASP in the prompt.

**Outcome: GREEN. The false coverage claim is gone.** No finding, verdict Approve, and a `Clean`
section that names no OWASP area and claims no sweep. Verbatim:

> **Clean**
>
> - **Clarity and readability** — the diff's only substantive change is exactly this: replacing terse
>   single-letter names with intent-revealing ones (`t` → `totalSeconds`, `m` → `minutes`,
>   `s` → `seconds`), which makes the branch logic (`totalSeconds < 60`) and the return expressions
>   self-explanatory without needing the comment to carry the mapping. No new magic numbers or unclear
>   logic introduced.
> - **Naming and structure conventions** — new names use the file's existing camelCase local-variable
>   convention; no style is imported that wasn't already present in the surrounding function.
> - **Duplication** — no repeated logic; single small function, unchanged structure.
>
> No other checklist areas (security, input validation/error handling, performance) apply — the diff
> contains no user input, no external calls, no logging, no error paths, and no loops or I/O to
> evaluate them against.

Against the two failure shapes written above before either run:

1. **Named areas** — absent. Not one identifier appears anywhere in the report
2. **A blanket claim** — absent. No range, no "A01–A10", and the word "swept" does not occur

Run 1's line was `**Security (A01–A10)**: swept`. The label is gone, and what replaced it is the
second shape the case admits as a pass: a statement about what the diff contains, not a claim about
what was checked. "No user input, no external calls, no logging, no error paths" enumerates absences
in the change, and the reader is told the areas do not **apply** rather than that they came back
clean.

### Where this sits against the bar, said precisely

The instruction asks for no security line at all on a change with no security-relevant code, and this
report has a sentence that mentions security. It passes because of what that sentence does: it names
security among the checklist areas that do not apply and grounds the non-application in the diff. It
asserts no coverage, so a reader cannot come away believing the change was measured against the
standard and cleared.

It sits close to the line, and that is worth recording rather than rounding off. The failing version
and the passing version differ by a claim, not by a topic — both mention security on a diff that has
none. What separates them is that one says "swept" and the other says "does not apply". The
instruction's restraint half is carrying exactly the weight it was written to carry.

**This was the step's only real RED, and it is now GREEN.** No gate in the repository can see either
state, which is why it is recorded here in full.
