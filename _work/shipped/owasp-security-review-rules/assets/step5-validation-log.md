# Step 5 — validation log

Working tree: branch `robot-denny/owasp-security-review-rules`, HEAD `156b64d`. Three files were
already modified before this step began (`AGENTS.md`, `ROADMAP.md`, and the plan) from separate
record-keeping work, and they are left alone. Baseline gate: `./scripts/check-contract.sh` reports
21 checks passed.

The two planted changes are documents under `_work/`, handed to the quality reviewer as the change
under review. Nothing is edited in the repository to create them.

- Case A: `step5-case-a-injection.md` — a handler concatenating a visitor's search term into a query
- Case B: `step5-case-b-naming-only.md` — a helper named `doStuff`, no security-relevant code at all

## Predictions, written before any reviewer ran

These are recorded first on purpose. A prediction written after reading the output is not a
prediction, and scoring a review once you have seen it is how a marginal result becomes a pass.

### Case A, run 1 (before the edit)

The reviewer reports the concatenated search term as a Blocker or Major finding, with the file and
the line, because unvalidated user input reaching a query is already covered by focus areas 1 and 2.
It names **no** OWASP category, because nothing in `code-reviewer.md` yet instructs it to cite one
and the reference is not yet pointed at from the checklist. **That absence is the RED this step
needs.** If a category appears here, the RED is unavailable and the step's premise is wrong, which is
the more important finding.

### Case B, run 1 (before the edit)

The reviewer reports `doStuff` as a name that does not express intent, at Minor or Nit, and attaches
no OWASP category.

**This is a pass for the wrong reason and is not counted as one.** Before the edit nothing cites at
all, so case B cannot fail. It has no available RED. Its value begins after the edit, when
over-citation becomes possible for the first time, and it then serves as the regression guard on the
restraint half of the convention.

### Case A, run 2 (after the edit)

The same defect is reported, and the finding now names `A05 Injection` — number and name — alongside
the file and the line. A citation of the number alone, or of a category the pinned table does not
carry, is a failure.

### Case B, run 2 (after the edit)

The naming finding is still reported and still carries **no** OWASP category, and no other finding in
the report carries one either. Over-citation is what teaches a reader to discount every citation, so
this is the more important of the two assertions after the edit.

### The stale-definition risk

Agent definitions may be loaded once at session start. If so, editing `code-reviewer.md` would not
change the behaviour of a reviewer dispatched later in the same session, and run 2 would silently
read the old definition. A stale pass and a real failure would look the same.

So run 2 asks the reviewer to report verbatim whether its own instructions contain an instruction to
cite an OWASP category, and to quote the line. If it reports the instruction absent after the edit is
in place, run 2 is invalid rather than failed.

## Observations

### Case A, run 1 — RED, as predicted

The defect is reported as a Blocker with its file and its lines. No category appears anywhere in the
report. `A05`, `A01`, `OWASP`, and `Top 10` are all absent from it. Full output in
`step5-case-a-injection.md`.

This is the RED the step needed, and it also confirms the defect was always reportable. What was
missing was the citation, not the finding.

### Case B, run 1 — reported and uncited, which is not a pass

The naming finding arrived at Minor with its file and line, carrying no category. Recorded rather
than counted: nothing was citing at all, so no result here could have failed.

### The edit

`skills/core/reference/reviewer-discipline/agents/code-reviewer.md`, focus area 1, three paragraphs
added between the bullet list and the committed-secret rule:

- an instruction to read the `security-review-rules` reference before reporting, with the reason
  (the category comes from a lookup rather than from recall), and a line saying security is the
  reviewer's across the whole checklist rather than only in section 1
- the citation convention: every security finding names its category by number and name, alongside
  the file and line the evidence standard already requires
- the restraint half: a finding that is not a security defect carries no category

**The committed-secret rule was re-read after the edit and is intact.** Its sentence is unchanged,
word for word, and unqualified: a committed secret is always a Blocker, and the finding must note the
credential should be considered compromised and rotated rather than merely removed. One sentence was
added after it saying the citation is added on top of that rule and displaces no part of it. Nothing
above or around it makes the rotation requirement conditional on anything. FR8 holds.

No language, framework, or ORM is named in the added prose, and no revision year, so checks 8 and 19
are unaffected.

### Run 2, first attempt — INVALID, not failed

Both dispatched reviewers reported that their own instructions contain no citation instruction. Both
quoted the committed-secret sentence as the closest related text, which is the sentence directly
beneath the inserted paragraphs.

The edit was on disk before either run, and the registered path resolves to it:

```
$ ls -l .claude/agents/code-reviewer.md
lrwxr-xr-x  .claude/agents/code-reviewer.md -> ../../skills/core/reference/reviewer-discipline/agents/code-reviewer.md

$ grep -c "names its category by number and name" .claude/agents/code-reviewer.md
1
```

No other copy of the definition exists on the machine, and `~/.claude/agents/` does not exist. So the
agent definition was snapshotted at session start and does not hot-reload. **That attempt is invalid
rather than failed**, and the probe is the only reason the two are distinguishable. Without it, a
stale pass and a real failure would have looked identical.

A `general-purpose` stand-in was run at the time to check that the wording works when a reviewer
actually reads it. It did — but the registered agent is the subject of the test, so that run was
recorded as a diagnostic and never as evidence. It has been superseded by run 2 proper and dropped
from both case files.

### Run 2, re-run in a fresh session — GREEN on both cases

The edit was committed as `3d8af37` and this session started after it, so the dispatched reviewers
read the committed definition rather than a pre-edit snapshot.

**The probe ran first.** A `code-reviewer` was dispatched with no diff and one question about its own
instructions. It answered `PRESENT`, quoted all three paragraphs of the citation rule including the
restraint half, named `security-review-rules` as the reference it is told to read before reporting,
and confirmed the committed-secret rule is intact, quoting it verbatim. The stale-definition risk is
closed for this session, and every result below is scored against a reviewer that can see the rule.

Both cases were then dispatched exactly as in run 1 — the diff handed over as the whole change under
review, file writes disallowed, no mention of citation, categories, or OWASP anywhere in the prompt.

**Case A — GREEN.** The injection Blocker carries `A05 Injection`, number and name, in the findings
table and again on a `**Category**:` line beside its file and line. **AC1 holds.** Four of the five
non-security findings carry no category. The fifth, a Major about a missing error boundary, names
`A10 Mishandling of Exceptional Conditions` in its Impact paragraph, hedged on a hosting condition
the diff does not show — a security consequence stated as one, not a category stamped on a
reliability finding. Recorded in the case file rather than smoothed over, because it is the closest
this report comes to the failure mode AC3 guards.

**Case B — GREEN.** The single finding, the `doStuff` name, carries no category in the table and no
`**Category**:` line in its detail block. Citing was available and was not taken. **AC3 holds**, and
this is the assertion that matters most: over-citation is what teaches a reader to discount every
citation in a report.

Full output for both in `step5-case-a-injection.md` and `step5-case-b-naming-only.md`.

### Gates

```
$ ./scripts/check-contract.sh
21 checks passed.
exit: 0

$ tests/run.sh
110/110 cases passed across 3 suites.
```

Check 8 is among the 21, and an agent file under `skills/core/` is L0, so the added prose is covered
by it.

### One note for Step 6

Case B's `Clean` section makes a security claim on a change that is pure arithmetic, unprompted:

> **Security**: no user input, no interpreter reached, no secrets, no auth surface — nothing in this
> diff falls under any A01–A10 category.

No individual category is named, which is milder than the stand-in's behaviour — that run listed five
categories by identifier and disclaimed two more. But a range claim spanning the whole standard still
reads as "all ten checked" on a diff that contained nothing to check. Step 5 asserts nothing about
`Clean`, so this does not change its result.

It does mean **Step 6's case D has a live failure mode rather than a hypothetical one**, and that the
restraint half has to rule out two shapes: a list of named areas the diff had no code for, and a
blanket claim of coverage across the standard. Details in `step5-case-b-naming-only.md`.
