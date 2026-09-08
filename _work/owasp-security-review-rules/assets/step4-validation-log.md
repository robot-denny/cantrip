# Step 4 — validation log

Working tree: branch `robot-denny/owasp-security-review-rules`, HEAD `998149b`, two files
modified, not committed.

```
$ git status --short
 M scripts/check-contract.sh
 M skills/core/reference/security-review-rules/SKILL.md

$ git diff --stat
 scripts/check-contract.sh                          | 111 ++++++++++++++++++++-
 .../core/reference/security-review-rules/SKILL.md  |   4 +-
 2 files changed, 110 insertions(+), 5 deletions(-)
```

The change adds check 20, "the security category table is well-formed", extends the file header
comment so it covers checks 19 and 20 together, and rewords one sentence in the reference so the
declared category count is a numeral a gate can read.

## What the check enforces, and what it cannot see

The check reads one file by path, reusing `SECURITY_RULES_FILE` from check 19. From that file it
takes two things: the table rows, found as lines opening with an `A<digits>` identifier cell, and
the declared count, found by the literal phrase `lists <n> categories`. It then requires four
things of them.

1. Identifiers run contiguously from `A01` with no gaps.
2. No identifier appears on two rows.
3. Every row pairs its identifier with a non-empty name and non-empty guidance.
4. The number of rows equals the declared count.

**It cannot see whether an identifier carries the right name in the pinned revision.** Verifying
that needs a second copy of the category list, which is exactly what check 19 forbids. So a pass
means the table is well shaped, never that it is accurate. Name accuracy was verified once by a
person against the OWASP source when the table was authored, and nothing re-checks it. The comment
above the check says this in the same words, so a later reader does not mistake a pass for name
verification.

Identifiers in the table are bare — `A01`, not `A01:<year>` — and the check expects that form. A
ten-row table carrying the year would name the pinned revision ten times in the one file that pins
it, which is the defect check 19 exists to prevent.

### Why the declared count changed shape

Before this step the count was the English word "Ten", at the start of the paragraph above the
table. The step's bounded permission to adjust how the count is declared was used: the sentence
now reads "The table below lists 10 categories, one per row." Two reasons for that exact wording.
A numeral is comparable without parsing an English word list. And the phrase has to be more
specific than a bare `<n> categories`, because the file's own frontmatter description says "Top 10
categories" and a looser pattern would read the description as a second declaration. Nothing else
in the reference moved: the identifiers, the category names, the third column, and the
pinned-revision sentence are untouched.

## Direction 0 (the real RED) — the three defects are invisible without the check

Run before check 20 existed, against the 20-check gate. Each breakage was planted, the gate run,
and the file restored.

```
$ perl -i -ne 'print unless /^\| A05 \|/' skills/core/reference/security-review-rules/SKILL.md
$ ./scripts/check-contract.sh
20 checks passed.
exit: 0

$ perl -i -pe 's/^\| A06 \|/| A05 |/' skills/core/reference/security-review-rules/SKILL.md
$ ./scripts/check-contract.sh
20 checks passed.
exit: 0

$ perl -i -pe 's/^Ten categories\./Nine categories./' skills/core/reference/security-review-rules/SKILL.md
$ ./scripts/check-contract.sh
20 checks passed.
exit: 0
```

A reference missing a whole category, a reference with two `A05` rows and no `A06`, and a reference
whose count contradicts its own table all passed the gate clean. That is what check 20 is for.

## Direction 1 (GREEN) — the check passes on the current table

```
$ ./scripts/check-contract.sh --verbose
ok    no client-identifying information (repo-wide)
ok    authoring org is attributed, not embedded in skills
ok    no absolute paths in shipped units
ok    no hostnames or ports in shipped units
ok    every slot reference has a fallback
ok    invocation posture matches taxonomy
ok    skill frontmatter is complete
ok    no loose markdown outside a skill directory
ok    no technology names in L0 core
ok    one slot, one fallback
ok    exemplar instructions handle having no exemplar
ok    self-hosting covers every core skill
ok    declared companions are documented in the README
ok    install checker rosters match skills/
ok    stack-agnostic audit references name no technology
ok    documented install commands disable telemetry
ok    workflow spellbook stays inside its budget
ok    coverage statuses are known to every spell that writes them
ok    every shipped unit is linked from the README
ok    the pinned OWASP revision is named once
ok    the security category table is well-formed

21 checks passed.
exit: 0
```

The new check reports ok by name, and the total is 21 against the step's baseline of 20. Check 19
still passes, which matters because the reworded sentence sits four lines below the one check 19
reads.

## Direction 2 (RED) — three breakages, three distinct failures

Each was planted with the check in place, the gate run, and the file restored from a copy before
the next.

### Breakage 1 — a row dropped

```
$ perl -i -ne 'print unless /^\| A05 \|/' skills/core/reference/security-review-rules/SKILL.md
$ ./scripts/check-contract.sh

FAIL  the security category table is well-formed
      The category identifiers do not run contiguously from A01.
      9 rows means the sequence should be A01 through A09.
      Missing from the sequence: A05. Outside it: A10.
      A gap means a category was dropped, and a review would stop sweeping it with nothing said.

1 of 21 checks failed.
exit: 1
```

Names the missing identifier. The expected sequence is derived from the row count rather than from
the declared count, on purpose: a dropped row also makes the declared count wrong, and deriving
from the declared count would have collapsed breakages 1 and 3 into the same message.

### Breakage 2 — an identifier duplicated

```
$ perl -i -pe 's/^\| A06 \|/| A05 |/' skills/core/reference/security-review-rules/SKILL.md
$ ./scripts/check-contract.sh

FAIL  the security category table is well-formed
      The category table repeats an identifier: A05
      An identifier names one category, so a repeat means one category gets cited twice and
      another cannot be cited at all. Give every row its own identifier.

        - 34:| A05 | Injection | Input reaching an interpreter as part of a command rather than as data. Data queries, shell invocations, pa
        - 35:| A05 | Insecure Design | A control the design never had, rather than one built wrongly. A missing rate limit, an absent trust

1 of 21 checks failed.
exit: 1
```

Names the repeated identifier and prints both rows with their line numbers, so the reader does not
have to work out which of the two is the intruder.

### Breakage 3 — the declared count no longer matches

```
$ perl -i -pe 's/lists 10 categories/lists 9 categories/' skills/core/reference/security-review-rules/SKILL.md
$ ./scripts/check-contract.sh

FAIL  the security category table is well-formed
      The category table has 10 rows, but the reference declares 9 categories.
      One of the two is stale: either a row was added or dropped without the count following,
      or the count was edited without the table. Bring them back into step.

1 of 21 checks failed.
exit: 1
```

Prints both numbers and does not guess which one is wrong.

### Breakage 4 — a guidance cell emptied

Added after review. This branch was the one path this log did not exercise, and it was the one
path that did not work: the check tested the name cell and the field count, so a row keeping its
delimiters with a blank guidance cell still counted five fields and passed. Review caught it by
mutation-testing the branch the log had skipped.

Before the fix, the defect was invisible:

```
$ perl -i -pe 's/^\| A05 \| Injection \|.*\|$/| A05 | Injection |  |/' skills/core/reference/security-review-rules/SKILL.md
$ ./scripts/check-contract.sh
21 checks passed.
exit: 0
```

After adding the guidance cell to the same test:

```
$ ./scripts/check-contract.sh

FAIL  the security category table is well-formed
      A category row does not pair its identifier with both a name and guidance.
      Every row needs three filled cells: the identifier, the category name, and what the
      category looks like inside a change.

exit: 1
```

The name cell still fails as it did before, so widening the test did not trade one half for the
other:

```
$ perl -i -pe 's/^\| A05 \| Injection \|/| A05 |  |/' skills/core/reference/security-review-rules/SKILL.md
$ ./scripts/check-contract.sh >/dev/null 2>&1; echo "exit: $?"
exit: 1
```

**The lesson is about this log, not only about the check.** Four rules were claimed and three were
tested. The untested one was broken, and a passing gate said nothing about it. A rule worth stating
in a comment is worth planting a defect against.

The four messages differ in their first line, in what they name, and in which of the four rules
they cite. None of them sends the reader hunting. Re-run after the fix confirms breakages 1 to 3
still produce their original distinct messages:

```
dropped row        → The category identifiers do not run contiguously from A01.
duplicate id       → The category table repeats an identifier: A05
declared count     → The category table has 10 rows, but the reference declares 9 categories.
no rows at all     → No category rows were found in ... so this check inspected nothing.
```

## The two cannot-inspect paths, exercised rather than assumed

A check that inspected nothing must fail rather than report ok. Both of its vacuity branches were
run.

**No rows found.** Every identifier row was deleted, leaving the heading, the declared count, and
the header separator in place:

```
$ ./scripts/check-contract.sh

FAIL  the security category table is well-formed
      No category rows were found in skills/core/reference/security-review-rules/SKILL.md, so this check inspected nothing.
      It fails rather than reporting ok, because a table nothing matches looks exactly like a
      well-formed one. A row is expected to open with an identifier cell such as "| A01 |".
      Restore the table, or update the row pattern in this check.

1 of 21 checks failed.
exit: 1
```

Only one check failed, which is the point: the declared count was still readable and check 19 still
found its revision, so nothing else noticed that the category list had gone. Restored afterwards.

**Reference missing.** The file was moved aside and the gate rerun:

```
$ mv skills/core/reference/security-review-rules/SKILL.md <scratch>/SKILL.md.moved
$ ./scripts/check-contract.sh

FAIL  the security category table is well-formed
      The security reference is missing: skills/core/reference/security-review-rules/SKILL.md
      This check reads the category table out of that one file, so without it there is nothing
      to inspect — and an empty inspection reporting ok is indistinguishable from a clean one.
      Restore the file, or retire this check deliberately if the unit is going.

exit: 1
```

Four failures in that run rather than one, because checks 11, 18, and 19 also fire on the absent
unit. That is the expected shape. File restored afterwards.

The unreadable-count branch shares its shape with the two above and with check 19's tested
equivalent: if the declaration sentence is restyled, `declared_lines` is 0 and the check fails
naming the phrase it looked for. It was not planted separately, and is recorded here as reasoned
rather than evidenced.

## [Automated] `tests/run.sh`

```
$ tests/run.sh

110/110 cases passed across 3 suites.
exit: 0
```

Pass, unchanged from the step's baseline. The change touches no fixture subject.

## Syntax

```
$ bash -n scripts/check-contract.sh
exit: 0
```

## Tree restored

```
$ git status --short
 M scripts/check-contract.sh
 M skills/core/reference/security-review-rules/SKILL.md
```

Only the two intended files, plus this log under `_work/`.

## What is evidenced and what is not

Evidenced by captured output: the pre-check RED showing all three defects passing a 20-check gate,
the passing direction with the new check reporting ok and the count at 21, the three planted
breakages each with a distinct failure message and a non-zero exit, both vacuity branches, the
fixture suites, and the syntax check.

Not evidenced: the unreadable-count branch, for the reason given above. Also not evidenced, and not
evidenceable by any gate in this repo, is that each identifier carries the right category name in
the pinned revision. That rests on the authoring-time read recorded in Step 1.
