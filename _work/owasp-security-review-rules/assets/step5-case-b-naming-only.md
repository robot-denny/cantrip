# Step 5, case B — a helper whose only defect is its name

A planted change, not a real repository edit. It lives here as a document and is handed to the
quality reviewer as the change under review.

**The planted defect**: the new helper is called `doStuff`. The logic is sound, the input is an
in-memory collection the caller already holds, nothing is stored, logged, rendered, or queried.
There is no security-relevant code anywhere in the change.

**What the case asserts**: the reviewer reports the name as not expressing intent, and that finding
carries **no** OWASP category.

## The diff under review

```diff
diff --git a/src/Web/Basket/BasketTotals.ts b/src/Web/Basket/BasketTotals.ts
new file mode 100644
index 0000000..d4e5f6a
--- /dev/null
+++ b/src/Web/Basket/BasketTotals.ts
@@ -0,0 +1,16 @@
+export interface BasketLine {
+  readonly quantity: number;
+  readonly unitPriceInCents: number;
+}
+
+/**
+ * Adds up the lines of a basket and returns the total in cents.
+ */
+export function doStuff(lines: readonly BasketLine[]): number {
+  let totalInCents = 0;
+
+  for (const line of lines) {
+    totalInCents += line.quantity * line.unitPriceInCents;
+  }
+
+  return totalInCents;
+}
```

## Run 1 — before the edit to `code-reviewer.md`

Dispatched the same way as case A.

**Outcome: reported, uncited — and this is a pass for the wrong reason.** Before the edit nothing
cites at all, so no result here could have failed. Recorded rather than counted.

Verbatim, the finding:

> **Minor — Function name doesn't express intent (naming/clarity)**
>
> `doStuff` (line 8) gives no indication of what the function does, and directly contradicts its own
> doc comment two lines above ("Adds up the lines of a basket and returns the total in cents.").
> This is the only export in the file, so it's also what every caller will see in autocomplete and
> stack traces. Rename to something intent-revealing, e.g. `calculateBasketTotalInCents` or
> `sumBasketLines`.

The report also raised a Nit about unvalidated numeric inputs, and closed with **Approve with
fixes**. No OWASP category appears anywhere.

## Run 2 — after the edit to `code-reviewer.md`

**Outcome: INVALID, not passed.** The dispatched `code-reviewer` reported the naming finding and
attached no category, which is the predicted result — but the stale-definition probe shows the run
read the pre-edit definition, so it proves nothing about the edit. Asked whether its instructions
carry a citation instruction, it answered:

> My own instructions (the domain checklist and role description under which I am operating for this
> review, as given above) do not contain an instruction to cite a security category on a security
> finding. [...] No such citation requirement appears anywhere in my instructions, so it is absent.

Two independent agents, dispatched after the edit, both reported the instruction absent and both
quoted the committed-secret sentence that sits directly beneath the inserted text. See case A for the
on-disk verification.

## Diagnostic — the same review from the current on-disk definition

**Not evidence for the step's validation**, for the reason given in case A. Same stand-in method: a
`general-purpose` agent read `code-reviewer.md` from disk, read the skills it points at, and reviewed
this diff under them.

The naming finding, verbatim and uncited:

> | # | Severity | File & Line | Issue | Recommended Fix |
> |---|----------|-------------|-------|-----------------|
> | 1 | Minor | `src/Web/Basket/BasketTotals.ts`, line 9 | Exported function is named `doStuff`, which does not express intent | Rename to `calculateBasketTotalInCents` |
> | 2 | Minor | `src/Web/Basket/BasketTotals.ts`, lines 9-16 | New exported behavior arrives with no test in the diff (conditional) | Add a test covering the empty-basket, single-line, and multi-line cases |

Neither finding carries a category, in the table or in its detail block. **The restraint half held on
a report where citing had become available**, which is the assertion this case exists for.

### One observation for Step 6, not a defect in this step

The `Clean` section of this run does name OWASP categories, on a change that is pure arithmetic:

> **Secrets and security exposure.** Nothing here reaches a credential, a config file, or
> client-visible markup. Of the OWASP categories a diff this shape can reach, the relevant ones are
> clean: no authorization decision (A01), no stored or transmitted sensitive value (A04), no input
> reaching an interpreter or a query (A05), no log calls at all (A09), no error path (A10). A03
> Software Supply Chain Failures and A06 Insecure Design are not reachable from a change of this
> scope, and I claim no coverage of them.

That is naming areas the diff had no relevant code for, which is close to the failure mode Step 6's
case D is built to catch. Step 5 asserts nothing about the `Clean` section and this does not change
its result. It does say that Step 6's restraint half is load-bearing, and that a reviewer will reach
for category names in `Clean` from the reference alone, before any instruction tells it to.
