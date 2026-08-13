# Step 3 — validation log

Working tree: branch `review-failure-modes`, HEAD `fc86fc4`, one file modified, not committed.

```
$ git status --short
 M skills/core/reference/reviewer-discipline/SKILL.md

$ git diff --stat
 skills/core/reference/reviewer-discipline/SKILL.md | 20 ++++++++++++++++++++
 1 file changed, 20 insertions(+)
```

## Added lines (the entire change)

```
+### Where two domains abut
+
+Mapping a domain onto the scale settles severity. It does not settle the cases where two domains
+genuinely touch, and there **one reviewer owns the rule and the others stay silent.**
+
+Cancellation and timeouts on long-running work belong to the **performance reviewer** — whether an
+operation can be abandoned, and whether the wait on it is bounded, are its findings. The quality
+reviewer does not also raise them. It still raises what is its own on that same call — a failure it
+swallows, an async path with no error boundary — because those are different defects that happen to
+share a line, and two defects on one line are two findings.
+
+The reason is the merge. Three reviews become one ranked list, so a rule held in two reviewers
+reaches the reader twice: same line, same fix, two rows, an inflated count, and one defect occupying
+two slots in the ranking. Neither reviewer can see this, because each raised exactly one finding —
+the duplication exists only in the merged report, which is why the boundary is recorded here rather
+than in either checklist. Distinct from the "Reporting balance" rule against repeating one issue
+across many files: that governs a single reviewer repeating itself, this governs two reviewers
+repeating each other. When authoring a reviewer, check that a rule you are about to add is not
+already another's.
```

Placed at the end of the `## Severity scale` section, immediately after the "Do not invent additional
levels" paragraph, so the two scale-mechanics paragraphs stay together and the new material sits in
the same section as the domain-mapping sentence it extends. Its first sentence links back to that
sentence textually, so the adjacency is not merely positional. Line widths 85–101, within the file's
existing prose range (pre-existing max 104).

## [Automated] `scripts/check-contract.sh`

```
$ bash scripts/check-contract.sh

14 checks passed.
exit: 0
```

Pass. Same 14 as the pre-edit baseline in `00-expectations.md`, so nothing regressed — check 8 (no
technology names in L0) included.

## [Automated] `grep -rn "cancel" .../agents/code-reviewer.md` — the revert proof

```
$ grep -rn "cancel" skills/core/reference/reviewer-discipline/agents/code-reviewer.md
exit: 1 (no match)
```

Pass. Two further, stronger proofs of the same thing:

```
$ git diff --name-only
skills/core/reference/reviewer-discipline/SKILL.md

$ git diff --exit-code -- skills/core/reference/reviewer-discipline/agents/code-reviewer.md
IDENTICAL to fc86fc4
```

`code-reviewer.md` is byte-identical to the Step 2 commit — not merely free of the word "cancel", but
untouched. Steps 1 and 2's entries are intact and unmodified.

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
exit: 0
```

Pass, 14/14. Expected — this harness exercises `check-install.sh`, untouched here.

## [Manual] Eye-check for a technology name check 8 would miss

Check 8's pattern contains no framework cancellation type or interface name, so the added lines were
also grepped mechanically for the ones a cancellation rule would most plausibly reach for:

```
$ git diff -U0 | grep '^+' | grep -v '^+++' | grep -inE \
  'cancellationtoken|abortsignal|abortcontroller|ilogger|serilog|nlog|goroutine|c#|dotnet|\.net|javascript|typescript|python|java|golang|axios|fetch\(|httpclient|task\.|promise|threadpool'
exit: 1 (no matches)
```

The statement's whole vocabulary is `cancellation`, `timeouts`, `long-running work`, `operation`,
`abandoned`, `bounded`, `async path`, `error boundary`, `reviewer`, `finding`, `merged report`. No
type, interface, library, language, or API shape. `async` appears as an adjective describing a code
path, which is the same usage already in `code-reviewer.md` §2 and `perf-reviewer.md` dimension 5, and
names no technology.

No project fact either: no client, no host, no organization, no version, no path.

## [Manual] Recorded twice-then-once result

- RED: `10-red-review-output.md` — with a cancellation bullet temporarily in the quality reviewer,
  the merged report carries **four** rows for **three** defects. Rows 2 and 3 both cite
  `src/sync/refresh-catalog.ts` line 13, both name the same missing cancellation and missing bound,
  and both recommend the same fix.
- GREEN: `20-green-review-output.md` — with the bullet reverted and the statement in place, the merged
  report carries **three** rows for three defects. The cancellation defect appears once, attributed to
  the performance reviewer.

Recorded honestly in the GREEN artifact: reverting the bullet is what restored the single row, and the
statement changes no output on this fixture. Its value is prospective — it makes that edit contradict
a written rule both reviewers follow, so a future author's version is refusable at review time. That
is exactly why the plan specified an induced RED rather than an assertion about the current state.

## [Manual] The lesson-3 guard

The fixture deliberately places a swallowed failure on the *same* long-running call. In the GREEN run
the quality reviewer still raises it as a Blocker. The statement therefore scopes to the cancellation
and timeout concern, not to "anything about long-running work" — and it says so in the text, naming a
swallowed failure and an async path with no error boundary as things the quality reviewer still
raises.

A subtler version of the same risk, caught while writing the GREEN pass: a *deferral note* in the
quality reviewer's Clean section ("cancellation — left to the performance reviewer") would put the
same defect back into the merged report in a softer form. The statement's wording is "stay silent",
not "cross-reference the other reviewer", which forecloses it, and it also keeps the scope rule intact
— a reviewer must not comment on what another reviewer will say.

## [Manual] Cross-check against the rest of the file, and the sibling agents

Read the whole of `SKILL.md` plus all three agent files after editing, looking for something the new
statement contradicts:

| Existing text | Interaction | Resolution |
|---|---|---|
| `SKILL.md` "Reporting balance" → "Do not repeat one issue across many files unless the pattern itself is the finding" | Nearest neighbour, easy to conflate. Governs **one reviewer repeating itself across files**; the new statement governs **two reviewers repeating each other on one line** — a different axis, invisible to either reviewer alone | The statement names the distinction explicitly in its last paragraph, so a reader meeting either one is not left to guess whether it is the other |
| `SKILL.md` severity → "Each reviewer maps its own domain onto these…" | The anchor. Assigns domains; the statement extends it to one boundary where two domains abut | Same section, same vocabulary of domains, opening sentence refers back to it |
| `SKILL.md` scope rule → "You review only the code explicitly present in the diff" | A reviewer that defers must not widen scope or narrate another reviewer's job | "Stay silent" rather than "defer to", and no instruction to cross-reference |
| `SKILL.md` "Report structure" → the Clean section's purpose | Clean makes coverage legible; could be misread as a place to log the deferral | Clean names *that* reviewer's areas. Cancellation is not one of the quality reviewer's areas, so it appears in neither its findings nor its Clean |
| `code-reviewer.md` §2 → "Missing error boundaries in async code — unhandled rejections, absent try/catch" | Sits closest to what the statement removes from this reviewer's reach, and could have been read as also removed | Deliberately named in the statement as something the quality reviewer **still** raises |
| `code-reviewer.md` §6 → "Flag the obvious cases and leave depth to the performance reviewer" | Already an ownership deferral, and consistent with the statement — but a deferral about **depth**, not about who owns a specific rule | Left alone. The statement generalizes the instinct §6 shows without duplicating it |
| `perf-reviewer.md` dimension 5 + "Streams and long-running outbound calls … must propagate cancellation, and must carry a timeout" | Already owns cancellation and timeouts, so the statement records existing behavior rather than changing it | No edit. The plan puts a matching statement in `perf-reviewer.md` out of scope, and the spec records it as an open question |

Also checked: `reviewer-discipline` is a single source, symlinked into `.claude/skills/` and
`.claude/agents/`, so there is no second copy to keep in sync.

```
$ grep -rln "Do not invent additional levels" . | grep -v '^\./\.git/'
skills/core/reference/reviewer-discipline/SKILL.md
```

## Not done, deliberately

- **No `CHANGELOG.md` entry.** Steps 1 and 2 added none either, and nothing user-observable changed
  here — the statement prevents a future regression. The plan routes this increment's recording
  through `/feature update code-review`, and explicitly says the cancellation statement is not a Rule.
- **No matching statement in `perf-reviewer.md`.** Out of scope per the plan; open question in the spec.
- **No rebalancing of `code-reviewer.md` section 2.** Out of scope by the user's decision.
