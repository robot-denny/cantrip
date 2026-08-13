# GREEN run — review output against the checklist AFTER the edit

Checklist applied: `skills/core/reference/reviewer-discipline/agents/code-reviewer.md` with
section 2 now reading:

```
- Swallowed exceptions and empty catch blocks
- An error passed onward in a form that discards its origin — replaced by a new error that does not
  carry the original, or the same error sent on in a way that resets where it began. **The failure
  still reaches the caller, which is what separates this from a swallowed error**: what is lost is the
  original point of failure, so whoever debugs it later lands on the handler with no trail back. Carry
  the original inside the replacement
- Missing error boundaries in async code — unhandled rejections, absent try/catch
```

Same four diffs, same shared contract, nothing else changed.

---

## Diff 1 — `01-positive-throwing.diff` (Java, throws)

### Summary

One added method, 8 lines. **One Major finding**: the handler replaces `TransportFailure` with
`InvoiceUnavailable` and drops the original, so the reason the transport failed is gone by the
time the error is seen. No Blocker findings.

### Findings

| # | Severity | File & Line | Issue | Recommended Fix |
|---|----------|-------------|-------|-----------------|
| 1 | Major | `src/main/java/billing/InvoiceLookup.java`, the `catch (TransportFailure failure)` block in `byReference` | `InvoiceUnavailable` is raised without the caught `failure` inside it, discarding where the error came from | Pass `failure` as the new error's cause |

### Findings Detail

#### Finding 1 — The original failure's origin is discarded (Major)

**File**: `src/main/java/billing/InvoiceLookup.java`, the `catch (TransportFailure failure)`
block inside `byReference`
**Issue**: `failure` is bound and never used. The error that reaches the caller is
`InvoiceUnavailable("Invoice <ref> could not be loaded")` and it carries nothing from the
original — not its type, not its message, not where it was raised. This is not a swallowed
error: the failure does propagate, and the caller does learn the lookup failed. What is lost is
the original point of failure.
**Impact**: Whoever debugs a production report of this lands on `byReference` and stops there.
Timeout, refused connection, malformed response and authentication rejection all look
identical, so diagnosis needs a reproduction rather than the record already captured.
**Fix**: Carry the original inside the replacement:

```java
} catch (TransportFailure failure) {
    throw new InvoiceUnavailable("Invoice " + reference + " could not be loaded", failure);
}
```

### Clean

- **Secrets and security exposure** — no credentials, nothing serialized to client markup.
- **Clarity and readability** — names express intent; 8 lines, one concern.
- **Naming and structure conventions** — consistent with `outstanding()` above it.
- **Duplication** — none.
- **Performance** — one call, no loop.

### Verdict

**Request changes**

---

## Diff 2 — `02-positive-returning.diff` (Go, returns errors)

### Summary

One added method, 10 lines. **One Major finding**: the query error is replaced by a fresh error
built from scratch, so nothing of the original survives. No Blocker findings.

### Findings

| # | Severity | File & Line | Issue | Recommended Fix |
|---|----------|-------------|-------|-----------------|
| 1 | Major | `internal/subscribers/store.go`, the `if err != nil` block in `ActiveFor` | `errors.New(...)` returns a new error in place of `err`, discarding where the failure came from | Build the returned error from `err` so the original is still reachable |

### Findings Detail

#### Finding 1 — The query error's origin is discarded (Major)

**File**: `internal/subscribers/store.go`, the `if err != nil` block inside `ActiveFor`
**Issue**: `err` is checked and then thrown away. The caller receives
`errors.New("could not load subscribers for list " + listID)`, which contains no part of the
error the query actually produced. As in the throwing case, this is not a swallowed error — the
failure is returned and the caller must handle it. What is lost is the original point of
failure.
**Impact**: Two consequences. A reader debugging later sees only this line, so a bad query, a
closed connection and a cancelled context are indistinguishable. And because the original is
unreachable, a caller can no longer test the returned error against a sentinel or a type to
decide whether to retry — the classification the original carried is gone with it.
**Fix**: Carry the original inside the replacement:

```go
if err != nil {
    return nil, fmt.Errorf("loading subscribers for list %s: %w", listID, err)
}
```

### Clean

- **Secrets and security exposure** — `listID` is passed as a query parameter, not concatenated
  into SQL.
- **Clarity and readability** — names express intent.
- **Naming and structure conventions** — matches `Count` and `Deactivate`.
- **Duplication** — none.
- **Performance** — one query, no per-row lookup.

### Verdict

**Request changes**

**Note on wording**: the finding above was written without using the words *throw*, *raise*,
*exception*, or *catch*. That is the evidence for the two-language requirement — the same bullet
produced a correct finding for a language that throws and for one that returns errors.

---

## Diff 3 — `03-negative-wrapped.diff` (Go, wraps carrying the original)

### Summary

One added method, 10 lines. No findings.

### Findings

| # | Severity | File & Line | Issue | Recommended Fix |
|---|----------|-------------|-------|-----------------|
| — | — | — | None | — |

### Findings Detail

None.

### Clean

- **Input validation and error handling** — `err` is checked, and
  `fmt.Errorf("loading subscribers for list %s: %w", listID, err)` returns an error *built from*
  the original rather than in place of it. The new bullet asks whether the original is carried
  inside the replacement; it is, so the check does not fire. Adding context while preserving the
  original is the fix the bullet recommends, not the defect it describes.
- **Secrets and security exposure**, **Clarity**, **Naming**, **Duplication**, **Performance** —
  as diff 2, all clean.

### Verdict

**Approve**

---

## Diff 4 — `04-negative-log-and-continue.diff` (Python, logs and continues)

### Summary

One added method, 9 lines. **One Major finding**: the handler logs the publish failure and
continues, so the caller is told every event was published. That is the only finding.

### Findings

| # | Severity | File & Line | Issue | Recommended Fix |
|---|----------|-------------|-------|-----------------|
| 1 | Major | `importer/events.py`, the `except PublishFailure` block in `publish_all` | The failure is logged and discarded, and `publish_all` still returns `len(events)`, so a partial failure is indistinguishable from a clean run | Bind the exception, count failures, and either return the count of successes or raise once the loop finishes |

### Findings Detail

#### Finding 1 — Publish failure is swallowed (Major)

**File**: `importer/events.py`, the `except PublishFailure:` block inside `publish_all`
**Issue**: The handler logs a fixed warning and continues. Nothing propagates to the caller,
and `return len(events)` reports every event as published regardless of how many failed.
**Impact**: An operator sees a success return and a warning buried in logs. Silent partial data
loss on every failed event.
**Fix**: as in the RED run — bind the exception, track failures, and let the caller see them.

**Why this is one finding and not two.** The new lost-origin bullet was considered against this
same block and does **not** apply. Its qualifying condition is that *the failure still reaches
the caller* — that is what distinguishes it from a swallowed error. Here nothing reaches the
caller at all, so the block falls entirely to the swallowed-exception bullet. The two bullets
are mutually exclusive by construction: either the failure propagates (lost origin is possible)
or it does not (swallowed). One handler cannot satisfy both.

### Clean

- **Secrets and security exposure** — nothing sensitive logged.
- **Clarity and readability** — names express intent; 9 lines.
- **Naming and structure conventions** — snake_case, matching `load` below it.
- **Duplication** — none.
- **Performance** — one call per event, inherent to the operation.

### Verdict

**Request changes**

---

## GREEN result

| # | Expected (written down first) | Actual | Match |
|---|---|---|---|
| 1 | Lost-origin finding raised; cites the handler; names carrying the original as the fix; severity from the existing scale | Finding 1, **Major**, cites the `catch (TransportFailure failure)` block, fix is `throw new InvoiceUnavailable(..., failure)` | ✅ GREEN |
| 2 | Lost-origin finding raised, wording not assuming exceptions | Finding 1, **Major**, cites the `if err != nil` block, fix is `%w` wrapping; finding text uses no throw/raise/exception/catch vocabulary | ✅ GREEN |
| 3 | No new finding | No findings; the check was evaluated and did not fire because the original is carried | ✅ |
| 4 | Still exactly one finding — swallowed only, not both | Exactly one finding, Major, swallowed exception. The lost-origin bullet was evaluated and excluded by its own propagation clause | ✅ |

Severities used: **Major** on both positives — "significantly degrades correctness,
reliability, or maintainability" per the shared scale's quality-domain mapping. No new severity
level introduced.
