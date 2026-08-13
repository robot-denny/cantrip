# RED run — review output against the checklist BEFORE the edit

Checklist applied: `skills/core/reference/reviewer-discipline/agents/code-reviewer.md` as of
branch `review-failure-modes` at HEAD `59be473`, clean tree, file last modified by `42b28a8`
— section 2 contains five bullets, the nearest being "Swallowed exceptions and empty catch
blocks". Plus the shared contract in
`skills/core/reference/reviewer-discipline/SKILL.md`.

Baseline gate at this commit: `scripts/check-contract.sh` → `14 checks passed.`

---

## Diff 1 — `01-positive-throwing.diff` (Java, throws)

### Summary

One added method, 8 lines. No Blocker, Major, Minor or Nit findings. The added method has a
try/catch that does propagate a failure to the caller, so the swallowed-exception bullet does
not reach it, and no other focus area has relevant code in the diff.

### Findings

| # | Severity | File & Line | Issue | Recommended Fix |
|---|----------|-------------|-------|-----------------|
| — | — | — | None | — |

### Findings Detail

None.

### Clean

- **Secrets and security exposure** — no credentials, no data serialized to client markup.
- **Input validation and error handling** — the `catch (TransportFailure failure)` block
  raises `InvoiceUnavailable`, so the failure reaches the caller. Not a swallowed exception
  and not an empty catch block. Nothing in this focus area applies.
- **Clarity and readability** — `byReference`, `reference`, `InvoiceUnavailable` all express
  intent; 8 lines, one concern.
- **Naming and structure conventions** — camelCase members, PascalCase types, consistent with
  `outstanding()` above it.
- **Duplication** — no repeated logic.
- **Performance** — one call, no loop.

### Verdict

**Approve**

---

## Diff 2 — `02-positive-returning.diff` (Go, returns errors)

### Summary

One added method, 10 lines. No findings. The returned `err` is checked before use and a
non-nil error is returned on the failure path, so the error-handling bullets do not reach it.

### Findings

| # | Severity | File & Line | Issue | Recommended Fix |
|---|----------|-------------|-------|-----------------|
| — | — | — | None | — |

### Findings Detail

None.

### Clean

- **Secrets and security exposure** — `activeForList` is a named query constant and `listID`
  is passed as a parameter, not concatenated into SQL.
- **Input validation and error handling** — `err` is checked immediately, the failure path
  returns a non-nil error, and `rows.Close()` is deferred. Nothing swallowed, no empty
  handler, no unchecked response.
- **Clarity and readability** — `ActiveFor`, `listID`, `scanSubscribers` express intent.
- **Naming and structure conventions** — exported PascalCase method beside `Count` and
  `Deactivate`; matches the file's visible style.
- **Duplication** — no repeated logic.
- **Performance** — one query, no per-row lookup.

### Verdict

**Approve**

---

## Diff 3 — `03-negative-wrapped.diff` (Go, returns errors, wraps carrying the original)

### Summary

One added method, 10 lines. No findings.

### Findings

| # | Severity | File & Line | Issue | Recommended Fix |
|---|----------|-------------|-------|-----------------|
| — | — | — | None | — |

### Findings Detail

None.

### Clean

Same six areas as diff 2, all clean. Error handling in particular: `err` is checked, and the
returned error is built from it rather than in place of it.

### Verdict

**Approve**

---

## Diff 4 — `04-negative-log-and-continue.diff` (Python, logs and continues)

### Summary

One added method, 9 lines. **One Major finding**: the handler logs the publish failure and
continues, so the caller is told every event was published. This is the diff's single most
impactful problem and the only finding.

### Findings

| # | Severity | File & Line | Issue | Recommended Fix |
|---|----------|-------------|-------|-----------------|
| 1 | Major | `importer/events.py`, the `except PublishFailure` block in `publish_all` | The failure is logged and discarded, and `publish_all` still returns `len(events)`, so a partial failure is indistinguishable from a clean run | Bind the exception, count failures, and either return the count of successes or raise once the loop finishes |

### Findings Detail

#### Finding 1 — Publish failure is swallowed (Major)

**File**: `importer/events.py`, the `except PublishFailure:` block inside `publish_all`
**Issue**: The handler logs a fixed warning and continues. Nothing propagates to the caller,
and the method's `return len(events)` reports every event as published regardless of how many
failed. This is the "swallowed exceptions and empty catch blocks" focus area — the block is
not empty, but its effect is the same: the failure does not reach the caller.
**Impact**: An operator running the importer sees a success return and a warning buried in
logs. Silent partial data loss on every failed event.
**Fix**: Bind the exception and track failures, then let the caller see them:

```python
failed = 0
for event in events:
    try:
        self.publisher.publish(event)
    except PublishFailure:
        self.log.warning("Could not publish event")
        failed += 1
if failed:
    raise PartialPublishFailure(failed, len(events))
return len(events) - failed
```

### Clean

- **Secrets and security exposure** — nothing logged that is sensitive.
- **Clarity and readability** — `publish_all`, `events`, `event` express intent; 9 lines.
- **Naming and structure conventions** — snake_case throughout, matching `load` below it.
- **Duplication** — no repeated logic.
- **Performance** — one call per event, which is inherent to the operation.

### Verdict

**Request changes**

---

## RED result

| # | Expected (written down first) | Actual | Match |
|---|---|---|---|
| 1 | No lost-origin finding | No findings at all — `catch (TransportFailure failure)` drops `failure` and no bullet in the checklist reaches it | ✅ RED |
| 2 | No lost-origin finding | No findings at all — `errors.New(...)` discards `err` and no bullet reaches it | ✅ RED |
| 3 | No lost-origin finding | No findings | ✅ |
| 4 | Exactly one finding, swallowed exception | Exactly one finding, Major, swallowed exception | ✅ |

**The premise holds.** Both positives carry a real defect — diff 1 throws
`InvoiceUnavailable` with `failure` bound and never used; diff 2 returns `errors.New(...)`
with `err` checked and then thrown away — and the pre-edit checklist produces no finding for
either. The gap is genuine, not already covered by the swallowed-exception bullet: in both
positives the failure *does* propagate, which is exactly why that bullet does not fire.
