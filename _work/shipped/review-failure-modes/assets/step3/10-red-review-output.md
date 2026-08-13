# Step 3 — RED run (induced)

Checklist state for this run:

- `agents/code-reviewer.md` — **temporary cancellation bullet present** in section 2, between the
  folded-values entry and "Missing error boundaries in async code". Exact text in
  `02-temporary-red-bullet.diff`.
- `agents/perf-reviewer.md` — unchanged.
- `agents/accessibility-reviewer.md` — unchanged.
- `SKILL.md` — **unchanged** (no ownership statement).

Fixture: `01-fixture.diff`. Line numbers below refer to the post-image of each new file.

All three passes performed by hand against the checklists as they stand in the working tree.

---

## Pass 1 — quality reviewer (`agents/code-reviewer.md`)

### Summary

Two files added to a scheduled catalog-sync path. Two findings: one Blocker, one Major. The most
impactful is the catch in `hourly-sync.ts` that discards the failure and then hands an empty list to
the store — a transient supplier outage silently empties the live catalog.

### Findings

| # | Severity | File & Line | Issue | Recommended Fix |
|---|----------|-------------|-------|-----------------|
| Q1 | Blocker | `src/sync/hourly-sync.ts`, 11–13 | `catch { entries = []; }` discards the failure entirely, and the empty list is then written over the stored catalog | Do not write on failure. Log the error and return, leaving the previous catalog in place |
| Q2 | Major | `src/sync/refresh-catalog.ts`, 13 | The outbound call has no cancellation path and no bound on how long it can wait, on a pull documented as running for minutes | Thread a cancellation signal from the caller into the call and bound the wait |

### Findings Detail

#### Finding Q1 — Failure discarded, then the catalog overwritten with nothing (Blocker)

**File**: `src/sync/hourly-sync.ts`, lines 11–13
**Issue**: The `catch` has no body beyond resetting `entries` to an empty array. Nothing is logged and
nothing is rethrown, so the failure leaves no trace. Execution then falls through to line 15, which
replaces the stored catalog with that empty list.
**Impact**: Any transient failure of the supplier feed — a 503, a dropped connection — empties the
catalog for every user until the next successful hourly run. The operator sees no error, because the
only record of the failure was thrown away.
**Fix**: Log the caught error with its details as fields and return without writing:

```ts
} catch (error) {
  logger.error("Hourly catalog refresh failed; keeping the previous catalog", { feedUrl, error });
  return;
}
```

Note this is the swallowed-exception finding, **not** the lost-origin finding. The section 2
lost-origin entry states that the failure still reaching the caller is what separates the two; here it
reaches nobody, so it draws one finding, not both.

#### Finding Q2 — Long-running work the caller cannot stop (Major)

**File**: `src/sync/refresh-catalog.ts`, line 13
**Issue**: `const response = await fetch(feedUrl);` starts a pull the file's own comment describes as
"roughly 40 MB" and "several minutes". No cancellation path is threaded through to the operation, and
nothing bounds how long the wait can last.
**Impact**: A caller that has given up — a redeployed scheduler, a shutting-down process — keeps
waiting, and the work keeps running. There is no way to abandon it.
**Fix**: Accept a cancellation signal as a parameter, pass it into the call, and bound the wait.

### Clean

- **§1 Secrets and security exposure** — `feedUrl` is a parameter, not a hardcoded value; no
  credentials, tokens, or connection strings in either file; nothing sensitive logged or rendered.
- **§2 Response status handling** — line 15 checks `response.ok` before line 23 reads the body.
- **§2 Folded log values** — all four log calls pass their values as named fields (`feedUrl`,
  `status`, `entryCount`), never spliced into the message text. The Step 2 entry does not fire.
- **§2 Lost error origin** — `refresh-catalog.ts` catches nothing, so there is no origin to lose.
- **§3 Clarity** — names express intent, the multi-minute cost is documented at the declaration, no
  magic values.
- **§4/§5 Naming, structure, duplication** — consistent, no repetition.
- **§6 Performance** — the ~40 MB body materialized as one string at line 23 is visible here, but
  section 6 says to leave depth to the performance reviewer, and this is a cost question rather than
  a correctness one. Not reported.

### Verdict

**Request changes** — one Blocker and one Major.

---

## Pass 2 — performance reviewer (`agents/perf-reviewer.md`)

### Risk level

**High.** A multi-minute outbound pull with no cancellation and no timeout sits on a scheduled path,
and its whole payload is materialized in memory before parsing. Either can hold a worker indefinitely.

### Summary

Two findings, both Major, both on `refresh-catalog.ts`. The catalog pull is unbounded in time and
unbounded in memory.

### Findings

| # | Severity | File & Line | Issue | Recommended Fix |
|---|----------|-------------|-------|-----------------|
| P1 | Major | `src/sync/refresh-catalog.ts`, 13 | Long-running outbound call with no cancellation propagation and no client timeout | Accept and forward a cancellation signal; set an explicit request timeout |
| P2 | Major | `src/sync/refresh-catalog.ts`, 23 | The entire ~40 MB response is materialized as one string before parsing | Stream the response into the parser instead of buffering it whole |

### Findings Detail

#### Finding P1 — Outbound call with no cancellation and no timeout (Major)

**File**: `src/sync/refresh-catalog.ts`, line 13
**Issue**: `await fetch(feedUrl)` carries neither a cancellation signal nor a timeout. Review
dimension 5 covers exactly this ("missing cancellation propagation, missing client timeouts"), and
the recurring heuristic is explicit: long-running outbound calls must propagate cancellation and must
carry a timeout.
**Impact**: A supplier that accepts the connection and then stalls holds this worker for as long as
it likes — the documented several minutes is the *happy* path. Under a scheduler that fires hourly,
stalled runs accumulate and each one holds a connection from the pool.
**Fix**: Take a cancellation signal as a parameter, forward it into the call, and bound the request
with an explicit timeout so a stalled supplier fails fast instead of pinning a worker.

#### Finding P2 — Whole payload buffered before parsing (Major)

**File**: `src/sync/refresh-catalog.ts`, line 23
**Issue**: `await response.text()` buffers the complete ~40 MB feed into a single string, which
`parseCatalog` then walks. Peak memory is the payload plus the parsed result.
**Impact**: Roughly 40 MB of transient allocation per run, in one large object, before any entry is
available. Concurrent runs multiply it.
**Fix**: Stream the response body into the parser so entries are produced incrementally and peak
memory is bounded by the buffer, not the feed.

### Clean

- **Dimensions 1, 2** — nothing on a request or render path; this is a scheduled job.
- **Dimension 4 Data efficiency** — one call, no per-item lookups, no loop.
- **Dimension 6 Throughput** — no singleton state, no cacheable per-request computation.
- **Dimensions 7, 8** — no frontend, no client code, no assets.
- **Dimension 9 Stability** — the failure path at line 15 is checked, and the caller does handle the
  thrown error. That the handling is *wrong* is a correctness question, not a stability one.

---

## Pass 3 — accessibility reviewer (`agents/accessibility-reviewer.md`)

### Summary

No findings. The diff adds two server-side modules with no markup, no components, and no
client-rendered output.

### Findings

None.

### Clean

The checklist is scoped to "each area **only where relevant code appears in the diff**". No area had
relevant code: no semantic HTML, no ARIA, no labels, no headings, no focus management, no keyboard
interaction, no images, no forms, no error messaging surfaced to a user, no live regions, and no
client-hydrated components. Nothing was skipped; there was nothing in scope.

---

## MERGED REPORT — RED

Merged under the shared scale in `SKILL.md`, worst first, as the contract's "Lead with the worst"
rule requires.

### Summary

Three reviewers, **four findings** across two files: one Blocker and three Majors. The catalog-sync
path needs a failure policy and needs bounding.

### Findings

| # | Severity | Raised by | File & Line | Issue |
|---|----------|-----------|-------------|-------|
| 1 | Blocker | quality | `src/sync/hourly-sync.ts`, 11–13 | Failure discarded, then the stored catalog overwritten with an empty list |
| 2 | Major | performance | `src/sync/refresh-catalog.ts`, 13 | Long-running outbound call with no cancellation propagation and no client timeout |
| 3 | Major | quality | `src/sync/refresh-catalog.ts`, 13 | Long-running work with no cancellation path threaded through and no bound on the wait |
| 4 | Major | performance | `src/sync/refresh-catalog.ts`, 23 | Whole ~40 MB payload buffered as one string before parsing |

### THE RED — rows 2 and 3 are the same defect

Both cite `src/sync/refresh-catalog.ts` line 13. Both are about the same missing cancellation signal
and the same missing bound on the same call. Both recommend the same fix. They differ only in
wording and in which reviewer's name is attached:

> | 2 | Major | performance | `src/sync/refresh-catalog.ts`, 13 | Long-running outbound call with no cancellation propagation and no client timeout |
> | 3 | Major | quality | `src/sync/refresh-catalog.ts`, 13 | Long-running work with no cancellation path threaded through and no bound on the wait |

A reader working the list top-down fixes row 2, arrives at row 3, and has to re-read both to
establish that it is the same line and already dealt with. The count is inflated — the merged report
claims four findings where there are three defects — and severity ranking is distorted, because one
defect now occupies two of the four slots.

**Neither reviewer can see this.** Each produced one finding on that line, which is correct behavior
under its own checklist. The duplication exists only in the merged artifact, which is why the rule
that prevents it has to live in the shared contract rather than in either agent.

### Expectations check

| From `00-expectations.md` | Actual | Match |
|---|---|---|
| perf raises a cancellation/timeout finding on the outbound call | P1, Major, line 13 | yes |
| quality raises a second cancellation finding on the same line | Q2, Major, line 13 | yes |
| quality's legitimate swallowed-exception finding still fires | Q1, Blocker | yes |
| accessibility reports nothing, Clean says no relevant code | as recorded | yes |
| **merged report shows the cancellation defect twice** | **rows 2 and 3** | **yes — RED confirmed** |

The fixture did exercise the overlap, so it does not need strengthening.
