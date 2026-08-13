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

### Where two domains abut

Mapping a domain onto the scale settles severity. It does not settle the cases where two domains
genuinely touch, and there **one reviewer owns the rule and the others stay silent — in a merged
report.**

Cancellation and timeouts on long-running **outbound and I/O-bound** work belong to the **performance
reviewer**: whether such an operation can be abandoned, and whether the wait on it is bounded, are its
findings. The quality reviewer does not also raise them. It still raises what is its own on that same
call — a failure it swallows, an async path with no error boundary — because those are different
defects that happen to share a line, and two defects on one line are two findings.

The reason is the merge. Three reviews become one ranked list, so a rule held in two reviewers
reaches the reader twice: same line, same fix, two rows, an inflated count, and one defect occupying
two slots in the ranking. Neither reviewer can see this, because each raised exactly one finding —
the duplication exists only in the merged report, which is why the boundary is recorded here rather
than in either checklist.

**A reviewer running alone raises what it would otherwise leave to another.** Silence is only safe
while something else covers the rule; in a single-reviewer pass nothing does, and a finding withheld
is indistinguishable from a finding absent — which is the reason the Clean section exists at all. So
the deferral is a property of the merge, not a permanent narrowing of anyone's domain.

Distinct from the "Reporting balance" rule against repeating one issue across many files: that governs
a single reviewer repeating itself, this governs two reviewers repeating each other.

**One boundary is recorded here, not all of them.** Others are live and unassigned — the clearest is
the quality reviewer's synchronous-blocking-call entry against the performance reviewer's
async-correctness dimension. Leaving them open is deliberate rather than an oversight: each wants
evidence that the duplication actually reaches a reader, the way this one has it. Two cautions when
you do assign one. Check that a rule you are about to add is not already another's — and check that
the reviewer you assign it to genuinely covers it, because a grant wider than the checklist behind it
creates a gap where both reviewers believe the other has it.

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
