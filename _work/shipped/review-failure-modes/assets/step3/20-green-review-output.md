# Step 3 — GREEN run

Checklist state for this run:

- `agents/code-reviewer.md` — **temporary bullet reverted.** `git status` reports the file unmodified
  against `fc86fc4`, and `grep -rn "cancel"` over it returns no match.
- `agents/perf-reviewer.md`, `agents/accessibility-reviewer.md` — unchanged.
- `SKILL.md` — **ownership statement present**, as the new `### Where two domains abut` subsection at
  the end of the severity section.

Same fixture, `01-fixture.diff`. Same three passes, by hand.

---

## Pass 1 — quality reviewer

### Summary

Two files added to a scheduled catalog-sync path. One finding, a Blocker: the catch in
`hourly-sync.ts` discards the failure and then hands an empty list to the store, so a transient
supplier outage silently empties the live catalog.

### Findings

| # | Severity | File & Line | Issue | Recommended Fix |
|---|----------|-------------|-------|-----------------|
| Q1 | Blocker | `src/sync/hourly-sync.ts`, 11–13 | `catch { entries = []; }` discards the failure entirely, and the empty list is then written over the stored catalog | Do not write on failure. Log the error and return, leaving the previous catalog in place |

### Findings Detail

#### Finding Q1 — Failure discarded, then the catalog overwritten with nothing (Blocker)

Unchanged from the RED run — same file, same lines, same severity, same fix. Reproduced in full in
`10-red-review-output.md`.

**This is the lesson-3 guard, and it holds.** The swallow sits on the very same long-running call the
performance reviewer flags. The ownership statement did not silence it, because the statement scopes
to *cancellation and timeouts* and says so explicitly, then names a swallowed failure as an example of
what the quality reviewer still raises on that same call.

### Clean

As in the RED run, minus one line: **cancellation is no longer among this reviewer's areas**, so it
appears neither as a finding nor in Clean. Clean names the areas *this* reviewer checked; listing a
deferral there would put the same defect back into the merged report in a softer form, which is the
failure the statement exists to prevent. "Stay silent" in the statement is deliberate wording — not
"cross-reference the other reviewer".

Otherwise identical: §1 secrets, §2 response status, §2 folded log values, §2 lost error origin, §3
clarity, §4/§5 naming, structure and duplication all checked with no findings, and §6 leaves the
buffered payload to the performance reviewer as its own text already instructs.

### Verdict

**Request changes** — one Blocker.

---

## Pass 2 — performance reviewer

**Byte-for-byte unchanged from the RED run.** The statement assigns cancellation *to* this reviewer,
so nothing about its pass moves. Risk level **High**; findings P1 (Major, cancellation and timeout,
`refresh-catalog.ts` line 13) and P2 (Major, buffered payload, line 23), reproduced in full in
`10-red-review-output.md`.

---

## Pass 3 — accessibility reviewer

**Unchanged.** No findings; no area had relevant code.

---

## MERGED REPORT — GREEN

### Summary

Three reviewers, **three findings** across two files: one Blocker and two Majors. The catalog-sync
path needs a failure policy, and the pull needs bounding in both time and memory.

### Findings

| # | Severity | Raised by | File & Line | Issue |
|---|----------|-----------|-------------|-------|
| 1 | Blocker | quality | `src/sync/hourly-sync.ts`, 11–13 | Failure discarded, then the stored catalog overwritten with an empty list |
| 2 | Major | performance | `src/sync/refresh-catalog.ts`, 13 | Long-running outbound call with no cancellation propagation and no client timeout |
| 3 | Major | performance | `src/sync/refresh-catalog.ts`, 23 | Whole ~40 MB payload buffered as one string before parsing |

### THE GREEN — the cancellation defect appears once

Row 2 is the only cancellation finding, and it is attributed to the **performance reviewer**. RED's
row 3 — the quality reviewer's duplicate of it — is gone. Three findings, three defects; the count is
now honest and no defect occupies two slots in the ranking.

Two findings still land on `refresh-catalog.ts` (rows 2 and 3) and two defects still share the
long-running call (rows 1 and 2). Both are correct. The rule is one *rule* per reviewer, not one
finding per file or per line.

### Expectations check

| From `00-expectations.md` | Actual | Match |
|---|---|---|
| perf raises the same single cancellation finding, unchanged | P1, identical to RED | yes |
| quality raises **no** cancellation finding | absent | yes |
| quality's swallowed-exception finding still fires | Q1, Blocker | yes — lesson-3 guard holds |
| accessibility unchanged, nothing | as recorded | yes |
| **merged report: two defects on the shared call, cancellation once, attributed to perf** | rows 1–3 | yes |

Expected two rows in `00-expectations.md`; got three, because that table forecast only the two
findings the check is about and did not enumerate perf's buffered-payload finding. The count differs,
the behavior under test does not: cancellation appears exactly once, attributed to the performance
reviewer, and the quality reviewer's co-located finding survives. Recorded rather than quietly
reconciled.

### What the statement actually buys — and what it does not

Reverting the temporary bullet is what restored the single row. The statement changed no output on
this fixture, and claiming otherwise would be false.

Its value is **prospective**, which is exactly why the plan called for an induced RED. Before it, an
author reasoning "async correctness is the quality reviewer's domain, and an unbounded wait is an
async correctness problem" would add that bullet, and nothing in the toolkit would say otherwise —
neither reviewer's own report would look wrong, because the defect appears only after merging. After
it, the same edit contradicts a written rule in the shared contract that both reviewers follow, so it
is catchable at review time on the toolkit's own diff.

The RED is the evidence that the failure is real and reachable. The statement is what makes it
refusable.
