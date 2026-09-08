# Step 3 — validation log

Working tree: branch `robot-denny/prose-discipline`, HEAD `685cc95`, one file modified, not
committed.

```
$ git status --short
 M scripts/check-contract.sh

$ git diff --stat
 scripts/check-contract.sh | 82 +++++++++++++++++++++++++++++++++++++++++++++++
 1 file changed, 82 insertions(+)
```

The change adds check 19, "the pinned OWASP revision is named once", plus three lines in the file
header comment recording that the new check is shipped-scoped but reads one unit by path.

## What the check enforces, and what it reads

The check does not hardcode the revision. It reads the year out of
`skills/core/reference/security-review-rules/SKILL.md` by looking for the literal phrase
`Top 10:<year>`, then counts occurrences of that year across `shipped_md_files`, the same scope
check 9 reads. That scope covers `skills/` and `agents/` markdown, so the increment's own planning
notes under `_work/` stay out of range. Exactly one occurrence passes, and it has to be in the
reference itself.

Occurrences that look like dates (`2025-07`, `2026-2025`) are skipped on purpose. Starter facts
stamp verification dates, and a fact verified during the pinned year is not a second citation of
the standard. The cost of that exclusion is recorded in the comment above the check: a second
mention written in date shape would slip past.

## Direction 1 (RED) — a second mention planted in a shipped file

Planted line, appended to a shipped L0 agent file:

```
$ printf '\nSecurity findings cite the OWASP Top 10:2025 categories.\n' \
    >> skills/core/reference/reviewer-discipline/agents/code-reviewer.md
```

Gate run with the plant in place:

```
$ ./scripts/check-contract.sh

FAIL  the pinned OWASP revision is named once
      The pinned OWASP revision (2025) is named 2 times across shipped files.
      It belongs in exactly one place, so moving to the next revision stays a single edit.
      Remove the extra mentions and let them resolve against skills/core/reference/security-review-rules/SKILL.md instead.

        - skills/core/reference/reviewer-discipline/agents/code-reviewer.md:124:Security findings cite the OWASP Top 10:2025 categories.
        - skills/core/reference/security-review-rules/SKILL.md:17:Categories below are the **OWASP Top 10:2025** list, the eighth installment of the standard.

1 of 20 checks failed.
exit: 1
```

Fails, non-zero exit, and names the planted file with its line number and the offending text. Both
locations are printed, not just the count, so the reader does not have to hunt for which mention is
the extra one.

## Direction 2 (GREEN) — plant reverted

```
$ git checkout -- skills/core/reference/reviewer-discipline/agents/code-reviewer.md
$ git status --porcelain
 M scripts/check-contract.sh

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

20 checks passed.
exit: 0
```

Passes. The new check reports ok by name, and the total is 20 against the step's baseline of 19.

## The three loud-fail paths, exercised rather than assumed

A check that cannot inspect anything must fail rather than report ok. All three of its
cannot-inspect paths were run.

**Reference missing.** The file was moved aside and the gate rerun:

```
$ mv skills/core/reference/security-review-rules/SKILL.md <scratch>/SKILL.md.away
$ ./scripts/check-contract.sh

FAIL  the pinned OWASP revision is named once
      The security reference is missing: skills/core/reference/security-review-rules/SKILL.md
      This check reads the pinned OWASP revision out of that file, so without it there is
      nothing to enforce — and an empty inspection reporting ok is indistinguishable from a
      clean one. Restore the file, or retire this check deliberately if the unit is going.

3 of 20 checks failed.
exit: 1
```

Three failures rather than one, because checks 11 and 18 also fire on the absent unit. That is the
expected shape and it confirms the registration gates still work. File restored afterwards.

**Revision unreadable.** The pinned sentence was restyled from `**OWASP Top 10:2025**` to
`**OWASP Top Ten, 2025 edition**`, which is the way the extraction can break:

```
$ ./scripts/check-contract.sh

FAIL  the pinned OWASP revision is named once
      Could not read one pinned OWASP revision from skills/core/reference/security-review-rules/SKILL.md.
      The check looks for the literal phrase "Top 10:<year>" and found 0.
      Either the sentence naming the revision was restyled, or the file now names two.
      Restore a single "OWASP Top 10:<year>" mention, or update the pattern in this check.

1 of 20 checks failed.
exit: 1
```

Fails loudly, states which phrase it looked for, and offers both remedies. Reverted afterwards.

**No shipped files.** Not run destructively. This path is guarded by the `scanned == 0` branch,
which fires when `shipped_md_files` returns nothing. It is unreachable while `skills/` exists, and
the two paths above cover the same class of defect. Recorded here as reasoned rather than evidenced.

## The date-shape exclusion, demonstrated

The exclusion is deliberate, so it was confirmed rather than assumed:

```
$ printf '\n**Verified:** 2025-07\n' \
    >> skills/core/reference/reviewer-discipline/agents/code-reviewer.md
$ ./scripts/check-contract.sh

20 checks passed.
exit: 0
```

A verification stamp carrying the pinned year does not trip the check. Reverted afterwards.

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

## What is evidenced and what is not

Evidenced by captured output: the failing direction with the offending file named, the passing
direction with the new check reporting ok and the count at 20, the missing-file and
unreadable-revision failure paths, the date-shape exclusion, the fixture suites, and the syntax
check.

Not evidenced: the empty-scope branch, for the reason given above.
