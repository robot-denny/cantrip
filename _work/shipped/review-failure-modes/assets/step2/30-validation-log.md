# Step 2 — validation log

Working tree: branch `review-failure-modes`, HEAD `00c9d9e`, one file modified, not committed.

```
$ git diff --stat
 skills/core/reference/reviewer-discipline/agents/code-reviewer.md | 5 +++++
 1 file changed, 5 insertions(+)
```

## Added lines (the entire change)

```
+- A log call that folds its values into the message text instead of passing them alongside it as
+  named fields. Every occurrence becomes a distinct message string, so nobody can filter, group or
+  count on the values afterwards. **A message carrying no values has nothing to separate out and is
+  not this finding**; a value that should not be logged at all is section 1's finding, where the fix
+  is removal rather than relocation
```

Placed between Step 1's lost-origin entry and "Missing error boundaries in async code", inside
section 2. Line widths 96–99 characters, matching the file.

## [Automated] `scripts/check-contract.sh`

```
$ bash scripts/check-contract.sh
14 checks passed.
```

Pass. Same 14 as the pre-edit baseline recorded in `00-expectations.md`, so nothing regressed —
check 8 (no technology names in L0) included.

## [Automated] `tests/run.sh` — regression only

```
$ bash tests/run.sh
ok    agent-name-collision
ok    agents-unlinked
ok    canonical-complete
ok    copied-complete
ok    dangling-symlink
ok    foreign-units
ok    install-scatter
ok    missing-skill
ok    missing-template
ok    no-config
ok    no-lockfile
ok    pack-installed
ok    selective-install
ok    source-symlinked-complete

14/14 cases passed.
```

Pass, 14/14. Expected — this harness exercises `check-install.sh`, which this change does not touch.

## [Manual] Eye-check for a technology name check 8 would miss

Check 8's pattern contains no logging library or interface name, so the added lines were also
grepped by eye and mechanically:

```
$ git diff -U0 | grep '^+' | grep -inE 'ilogger|serilog|log4|logback|monolog|winston|pino|slf4j|nlog|zap|logrus|structlog|console\.|printf|string\.format|f-string|template literal|c#|dotnet|javascript|typescript|python|\.net'
(no matches)
```

The entry's whole vocabulary is `log call`, `message text`, `values`, `named fields`. No interface,
no library, no language keyword, no API shape.

## [Manual] Recorded before/after

- RED: `10-red-review-output.md` — both diffs draw no finding; the positive's defect is invisible to
  the pre-edit checklist.
- GREEN: `20-green-review-output.md` — the positive draws one Minor finding naming what can no longer
  be filtered on; the negative still draws none.

## [Manual] The finding says what is lost

Confirmed in `20-green-review-output.md`. The finding's Impact names two questions that stop being
answerable — every event for one order, and a count of rejections past a retry threshold — and ties
each to the absent field. The word "interpolation" does not appear in the finding.

## [Manual] Cross-check against the rest of the file

Read the whole of `code-reviewer.md` after editing, looking for an entry the new one contradicts:

| Sibling | Interaction | Resolution |
|---|---|---|
| §1 "Sensitive data logged, rendered into markup, or passed to client code" | A credential spliced into a message must be **removed**, not moved into a field. Unqualified, the new entry could have recommended relocation. | The entry's final clause hands that case to section 1 explicitly. This is the same failure mode Step 1's review caught — a new entry contradicting a sibling — checked for deliberately. |
| §2 "Swallowed exceptions and empty catch blocks" | No overlap. That entry is about a failure not reaching the caller; this one is about how a log message is assembled, and does not depend on any failure. | No shared trigger. |
| §2 lost-origin entry (Step 1) | A handler that logs an error folded into a message *and* discards its origin carries two genuinely distinct defects with different fixes. That is unlike Step 1's concern, which was one defect producing two findings. | Left as is; distinct defects on one line are not double-reporting. |
| §6 "Performance" — "Flag the obvious cases and leave depth to the performance reviewer" | The eager-formatting cost of building the string is a cost concern. | Deliberately absent from the entry, per the plan's "What not to build". Recorded in the GREEN output so the omission is legible as a choice. |
