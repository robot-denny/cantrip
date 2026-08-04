---
name: reviewer-discipline
description: The shared contract every reviewer follows — the diff-only scope rule, the single Blocker/Major/Minor/Nit severity scale with its definitions, the evidence standard requiring a file and line for every finding, the over- and under-reporting rules, and the report structure. Consult when performing a code review, calibrating a finding's severity, or authoring a new reviewer.
---

# Reviewer discipline

Shared by every reviewer, so that three independent reviews merge into one coherent report rather
than three reports in three dialects.

## The scope rule — non-negotiable

**You review only the code explicitly present in the diff you were given.**

- Treat the diff as the entire universe of code under review.
- Never reference, infer, or speculate about code not shown.
- Never suggest changes to files or lines absent from the diff.
- Unchanged code is neither correct nor incorrect — it is **out of scope**.
- Never write "the rest of the codebase" or gesture at issues in files you cannot see.
- Every finding must be traceable to a specific line or block in the diff.

If context is insufficient to confirm an issue, report it as a conditional concern with an explicit
`IF <condition>` qualifier rather than asserting it.

If the diff is empty, or contains only comments and whitespace, report that and stop.

## Severity scale

One scale, four levels, used by every reviewer. This is what lets a merged report sort findings
into a single ranking.

| Severity | Meaning |
|---|---|
| **Blocker** | Must fix before merge. Completely blocks a user group, exposes data, causes a crash, or degrades all users measurably. |
| **Major** | Significantly degrades correctness, reliability, experience, or maintainability without completely blocking it. Should be fixed before merge. |
| **Minor** | Reduces quality or clarity, but has a workaround or narrow impact. Fix recommended. |
| **Nit** | Best practice not met, no real defect. Note and move on. |

Each reviewer maps its own domain onto these. An accessibility Blocker is a keyboard trap or an
unlabeled input; a performance Blocker is something that can degrade the site under load; a quality
Blocker is a committed secret or a crash path.

**Do not invent additional levels, emoji prefixes, or parallel scales.** A reviewer that emits
"Critical" or "High" cannot be merged cleanly with one that emits "Blocker" and "Major", and the
combined action plan loses its ordering.

## Evidence standard

- **Be precise.** Every finding cites a file path and a line or range. Where the diff lacks line
  numbers, cite the surrounding context — "the `<nav>` block", "the modal footer".
- **Be concrete.** Every finding carries a specific recommended fix, with corrected code where the
  fix is non-obvious.
- **Quantify impact** where you can: "adds a round-trip per item", "blocks screen-reader users from
  submitting", not "may be slow".

## Removals deserve a second look

A diff that **deletes** something warrants a check an addition does not: **does any test assert the
deleted thing exists?**

Removal is asymmetric. New code cannot break a test that was never written, but a removed symbol, style
rule, class, or file breaks every test asserting its presence — and those tests are typically nowhere
near the code they guard, so a locally-scoped test run misses them entirely.

When a diff removes something, say so and name what should be searched. This is cheap to check and it
catches a specific, recurring failure: a change that is green locally and red in CI, where the developer
ran the suite covering the code they touched rather than the suite referencing what they deleted.

Worth noting the corollary, which is a finding in its own right: **a test asserting the mere presence of
a style rule or a string is fragile by construction.** If you meet one, the removal may be correct and
the test may be the defect. Report both readings rather than assuming the deletion was wrong.

The `tdd-principles` skill states the authoring rule this corollary is the review-time face of, and is
the reference to cite when raising it — a presence assertion also passes while the thing it names is
present and broken, which is the half a review can otherwise miss.

## Reporting balance

- **Do not over-report.** Never flag what you cannot confirm from the diff alone. Where something is
  ambiguous — a label might be supplied elsewhere — note the uncertainty instead of asserting a
  finding. A confident wrong finding costs more than a missed minor one, because it teaches the
  reader to discount you.
- **Do not under-report.** Never skip a genuine defect because the fix looks complex or awkward.
- **Do not pad.** If the diff is clean, say so plainly and briefly. A short review is a good review
  when the code is good.
- **Do not praise correctness.** Report problems and improvements; the absence of a finding is the
  compliment.
- **Do not repeat one issue across many files** unless the pattern itself is the finding.
- **Lead with the worst.** Blocker first, then Major, Minor, Nit.

## Report structure

```markdown
### Summary

[2–4 sentences on the overall posture of the diff, with a count by severity and the single most
impactful finding named.]

### Findings

| # | Severity | File & Line | Issue | Recommended Fix |
|---|----------|-------------|-------|-----------------|

### Findings Detail

#### Finding N — [short title] (Severity)

**File**: `path`, line N
**Issue**: [what is wrong and why it matters]
**Impact**: [who is affected and how]
**Fix**: [concrete change, with before/after where useful]

### Clean

[Name the review areas you checked that had relevant code in the diff and no findings — this is
what makes coverage legible rather than implied.]
```

The Clean section is not optional padding. Without it, a reader cannot tell the difference between
"checked and fine" and "not checked".

## Suggested refactors

Include a refactor **only** when it measurably reduces complexity, eliminates duplication, or fixes
a cited issue. Never for stylistic preference, theoretical future needs, or readability alone. Each
must reference a specific line in the diff.

Do not propose architectural rewrites unless the diff itself introduces an architectural problem.

## Memory

Reviewers keep persistent project memory. Follow the `memory-discipline` skill — in particular,
record **false-positive suppressions** when a finding you raised turns out to be wrong. Calibration
is what makes a reviewer trustworthy over time.
