# GREEN run — review output against the checklist AFTER the edit

Checklist applied: `skills/core/reference/reviewer-discipline/agents/code-reviewer.md` with the new
section 2 entry in place (uncommitted, working tree). Section 2 now carries seven bullets; the new
one sits between Step 1's lost-origin entry and "Missing error boundaries in async code":

> - A log call that folds its values into the message text instead of passing them alongside it as
>   named fields. Every occurrence becomes a distinct message string, so nobody can filter, group or
>   count on the values afterwards. **A message carrying no values has nothing to separate out and is
>   not this finding**; a value that should not be logged at all is section 1's finding, where the fix
>   is removal rather than relocation

Plus the shared contract in `skills/core/reference/reviewer-discipline/SKILL.md`.

Same two diffs, unchanged.

---

## Diff 1 — `01-positive-interpolated-log.diff` (TypeScript, log message built by interpolation)

### Summary

One added method, 9 lines. **One Minor finding**: the failure log builds a single message string with
the order number and the retry count spliced into it, so neither value survives as anything a reader
can query on later. Everything else in the method is sound — the gateway result is checked before the
failure path runs and the failure reaches the caller as a return value.

### Findings

| # | Severity | File & Line | Issue | Recommended Fix |
|---|----------|-------------|-------|-----------------|
| 1 | Minor | `src/fulfilment/dispatch-queue.ts`, the `log.warn` line in `attemptDispatch` | The order number and retry count are folded into the message text, so every rejection produces a distinct message string and neither value can be filtered, grouped or counted on afterwards | Pass the message with placeholders and hand the two values alongside it as named fields — `orderNumber` and `retryCount` |

### Findings Detail

#### Finding 1 — Log values folded into the message text (Minor)

**File**: `src/fulfilment/dispatch-queue.ts`, the `this.log.warn(...)` line inside `attemptDispatch`
**Issue**: The call assembles one message string with `${orderNumber}` and `${retryCount}` spliced
into it. By the time the line is written, the two values are indistinguishable from the surrounding
words. Every rejection therefore emits a *different* message, so what is lost is any later handle on
the values themselves.
**Impact**: Two concrete questions become unanswerable from the logs. "Show every dispatch event for
this one order" needs an equality match on an order number, and there is no order-number field to
match — only a substring search across free text that will also hit any other message quoting the
same digits. "How many rejections are on their third retry or beyond" needs an aggregation over a
numeric field, and there is no field to aggregate. Grouping identical events also stops working,
because no two of these messages are identical.
**Fix**: Keep the message fixed and pass the values beside it as named fields, so the message stays
one groupable value and each number stays queryable in its own right:

```ts
// before
this.log.warn(`Dispatch rejected for order ${orderNumber}, retry ${retryCount}`);

// after — message constant, values named and separate
this.log.warn("Dispatch rejected", { orderNumber, retryCount });
```

*(Exact call shape depends on the project's logging idiom; what matters is that the two values arrive
as separate named fields rather than inside the message text.)*

### Clean

- **Secrets and security exposure** — no credentials. Neither value is sensitive, so this is not
  section 1's exposure finding and the fix is to relocate the values, not remove them.
- **Input validation and error handling** — other than the finding above: `orderNumber` and
  `retryCount` are typed parameters passed straight to the gateway; `dispatch.accepted` is checked
  before the failure path runs; nothing is swallowed, since the caller gets `false`; no error object
  exists on this path, so Step 1's lost-origin bullet does not reach it; the `async` method returns
  its promise, so a rejection propagates rather than going unhandled.
- **Clarity and readability** — names express intent, 9 lines, one concern, no magic number.
- **Naming and structure conventions** — camelCase members and locals, consistent with the class.
- **Duplication** — none.
- **Performance** — one call, no loop. **Note**: the cost of building the string eagerly is *not*
  part of this finding. Cost belongs to the performance reviewer.

### Verdict

**Approve with fixes**

---

## Diff 2 — `02-negative-fixed-message.diff` (Ruby, fixed log message, no values)

### Summary

One added method, 5 lines. No findings.

### Findings

| # | Severity | File & Line | Issue | Recommended Fix |
|---|----------|-------------|-------|-----------------|
| — | — | — | None | — |

### Findings Detail

None.

### Clean

- **Secrets and security exposure** — nothing sensitive logged, nothing rendered.
- **Input validation and error handling** — walked against the new bullet explicitly:
  `@log.info("Cache warm started")` passes a fixed message and **no values at all**. The bullet's
  qualifying condition is that the call has values folded into the message; with none present there
  is nothing to separate out, so the check cannot fire here. It is excluded by the shape of the call,
  not by a judgment about intent. Nothing else in this focus area applies — no external input, no
  error handling, no consumed response.
- **Clarity and readability** — `warm`, `@cache`, `snapshot` express intent; two statements.
- **Naming and structure conventions** — snake_case method beside `clear`, matching the file.
- **Duplication** — none.
- **Performance** — one replace call, no per-item loop.

### Verdict

**Approve**

---

## GREEN result

| # | Expected (written down first) | Actual | Match |
|---|---|---|---|
| 1 | Folded-values finding raised, naming what can no longer be filtered on | **One Minor finding raised**, citing the `log.warn` line, stating that the order number and retry count can no longer be filtered, grouped or counted on because every occurrence is a distinct message string, and recommending they be passed as named fields | ✅ GREEN |
| 2 | Still no finding | No findings. The call has no values, so the bullet's qualifying condition is not met | ✅ |

### The negative is excluded structurally, not by intent

The bullet's subject is "a log call that folds **its values** into the message text". A call with no
values has no values to fold, so there is no reading of the sentence under which
`@log.info("Cache warm started")` matches it. The explicit clause — *"A message carrying no values
has nothing to separate out and is not this finding"* — states the same exclusion a second time for
a reader skimming the list. Neither depends on the reviewer inferring an unwritten intent.

### The finding states what is lost, not that interpolation was used

Checked against the plan's third validation item. The finding's Impact paragraph names two specific
questions that stop being answerable — retrieving every event for one order, and counting rejections
past a retry threshold — and ties each to the missing field. The word "interpolation" does not appear
in the finding at all; the defect is described as the values becoming unqueryable. A reader who
disagrees can check the claim against their own log tooling, which is what makes it actionable.

### Cost is deliberately absent

Per the plan's "What not to build", the eager-formatting cost of building the string is not mentioned
as part of the defect. The performance reviewer owns cost; the note in diff 1's Clean section records
that the omission is deliberate rather than overlooked.
