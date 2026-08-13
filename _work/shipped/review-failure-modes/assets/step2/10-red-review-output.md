# RED run — review output against the checklist BEFORE the edit

Checklist applied: `skills/core/reference/reviewer-discipline/agents/code-reviewer.md` as of branch
`review-failure-modes` at HEAD `00c9d9e`, clean tree — section 2 contains six bullets:

1. Unvalidated or unsanitized user input
2. Missing null and undefined checks before property access
3. Swallowed exceptions and empty catch blocks
4. An error passed onward with its origin no longer recorded anywhere *(Step 1)*
5. Missing error boundaries in async code
6. Responses consumed without checking status codes

Plus the shared contract in `skills/core/reference/reviewer-discipline/SKILL.md`.

Baseline gate at this commit: `scripts/check-contract.sh` → `14 checks passed.`

---

## Diff 1 — `01-positive-interpolated-log.diff` (TypeScript, log message built by interpolation)

### Summary

One added method, 9 lines. No Blocker, Major, Minor or Nit findings. The gateway result is checked
before the failure path runs, the failure reaches the caller as a return value, and no bullet in any
focus area reaches the way the log message is assembled.

### Findings

| # | Severity | File & Line | Issue | Recommended Fix |
|---|----------|-------------|-------|-----------------|
| — | — | — | None | — |

### Findings Detail

None.

### Clean

- **Secrets and security exposure** — no credentials; an order number and a retry count are not
  sensitive, and nothing is serialized into client-visible markup.
- **Input validation and error handling** — walked bullet by bullet:
  - *Unvalidated input* — `orderNumber` and `retryCount` are typed parameters, passed straight to
    the gateway; nothing is concatenated into a query or a path.
  - *Missing null/undefined checks* — `dispatch.accepted` is read from an awaited result, and the
    method branches on it before doing anything else.
  - *Swallowed exceptions / empty catch* — there is no catch block, and the non-accepted case is
    surfaced to the caller as `return false`. Nothing is swallowed.
  - *Lost error origin* — no error object exists on this path. The gateway reports rejection through
    a flag, not by failing, so there is no origin to discard. Step 1's bullet does not reach it.
  - *Missing async error boundaries* — the method is `async` and returns its promise to the caller,
    so a rejection from `gateway.send` propagates rather than becoming an unhandled rejection.
  - *Response status unchecked* — `dispatch.accepted` **is** checked. This is the bullet that comes
    closest to the added lines and it is satisfied.
- **Clarity and readability** — `attemptDispatch`, `orderNumber`, `retryCount`, `accepted` all
  express intent; 9 lines, one concern; no magic number; early return rather than nesting; formatting
  matches `count()` above it.
- **Naming and structure conventions** — camelCase members and locals, `Promise<boolean>` declared,
  consistent with the surrounding class.
- **Duplication** — no repeated logic.
- **Performance** — one call, no loop, no serialization of a large payload.

### Verdict

**Approve**

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

- **Secrets and security exposure** — nothing logged, nothing rendered.
- **Input validation and error handling** — no external input, no error handling on this path,
  nothing consumed without a status check.
- **Clarity and readability** — `warm`, `@cache`, `@pages`, `snapshot` express intent; two
  statements; no magic value.
- **Naming and structure conventions** — snake_case method beside `clear`, matching the file.
- **Duplication** — none.
- **Performance** — one replace call, no per-item loop.

### Verdict

**Approve**

---

## RED result

| # | Expected (written down first) | Actual | Match |
|---|---|---|---|
| 1 | No folded-values finding | **No findings at all.** `this.log.warn(\`Dispatch rejected for order ${orderNumber}, retry ${retryCount}\`)` splices both values into one message string and no bullet in the checklist reaches it | ✅ RED |
| 2 | No finding | No findings | ✅ |

**The premise holds.** Diff 1 carries the defect under test in the open — two runtime values, an
order number and a retry count, spliced into a single message string — and the pre-edit checklist
produces no finding for it. The gap is genuine and not covered indirectly: the nearest existing
bullet, "Responses consumed without checking status codes", is *satisfied* by this diff, and the
clarity focus area has nothing to say about a well-named, correctly formatted log line.

Decisive line from the RED review of diff 1, quoted:

> **Input validation and error handling** — … *Response status unchecked* — `dispatch.accepted`
> **is** checked. This is the bullet that comes closest to the added lines and it is satisfied.
