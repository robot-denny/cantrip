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

## Run 2 — after the edit, in a session that started with the edit committed

Dispatched the same way as run 1: the real `code-reviewer` agent, the diff above as the whole change
under review, file writes disallowed, and no mention of citation anywhere in the prompt. The probe
recorded in `step5-case-a-injection.md` ran first and confirmed the dispatched reviewer's instructions
carry the citation rule, so citing was available on this report.

**Outcome: GREEN.** One finding, and it carries no category.

> | # | Severity | File & Line | Issue | Recommended Fix |
> |---|----------|-------------|-------|-----------------|
> | 1 | Minor | `src/Web/Basket/BasketTotals.ts:9` | Exported function named `doStuff` doesn't express intent | Rename to something like `calculateBasketTotal` or `sumBasketLines` |

Its detail block carries no `**Category**:` line either — the naming finding is reported as a naming
finding and nothing more. **The restraint half held on a report where citing was available**, which is
the assertion this case exists for. That is AC3.

### Superseded: the earlier invalid run

The first attempt at run 2 was made in the session that performed the edit, and was **invalid rather
than passed**: two independently dispatched reviewers both reported the citation instruction absent
from their own instructions, having read a definition snapshotted at session start. A
`general-purpose` stand-in was used at the time to check the wording in isolation, and is no longer
the evidence for this case. See case A for the on-disk verification and the probe.

## What run 2 changed about Step 6's case D

The stand-in's `Clean` section named five specific categories on this pure-arithmetic diff — A01, A04,
A05, A09, A10 — and disclaimed two more. That was the live failure mode Step 6's case D is built to
catch, and it was worth flagging.

The real reviewer does something different, and milder. It makes one blanket claim:

> **Security**: no user input, no interpreter reached, no secrets, no auth surface — nothing in this
> diff falls under any A01–A10 category.

No category is named individually, so this is not the stand-in's behaviour. But it is still a coverage
claim spanning the whole standard, volunteered on a diff with no security-relevant code and before any
instruction asks for one. **Case D's failure mode is live, in a weaker form**: the risk is not a list
of invented areas but a range claim that reads as "all ten checked". Step 6's restraint half has to
rule out both.
