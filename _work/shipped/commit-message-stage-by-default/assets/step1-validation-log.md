# Step 1 — validation log

Working tree: branch `robot-denny/commit-message-stage-by-default`, HEAD `2c01082`.

The spell under test is `skills/core/spellbook/commit-message/SKILL.md`. Each expectation below
asserts on what the developer sees: whether the spell stops, which files the proposal says it
would add, whether a commit is made, and what `git status` shows afterwards. None asserts on the
spell's wording. The expected values come from the spec's draft scenarios and edge cases
(`_work/commit-message-stage-by-default/spec.md`), not from the edit.

"Proposal" means what the spell shows before asking for approval: the message, plus the list of
files it would stage. "Files to add" is that list; files already staged are not in it.

## Expected, written before the edit

### 1. Nothing staged, one edited file

Given `README.md` is edited and nothing is staged, the developer casts `/commit-message`.

- The spell does not stop. No message says that nothing is staged.
- The proposal shows a commit message and lists `README.md` as a file to add.
- Before the developer answers, `git status` still shows `README.md` under "Changes not staged
  for commit". Nothing was staged by proposing.
- On approval, the commit is made with `README.md` in it (`git show --stat HEAD` lists it), and
  `git status` no longer lists `README.md`.
- Staging runs with no permission prompt. (Real cast only; a stand-in cannot observe prompts.)

### 2. A staged spell edit and its unstaged changelog entry

Given `skills/core/spellbook/commit-message/SKILL.md` is staged and `CHANGELOG.md` has an
unstaged edit describing that same change, the developer casts `/commit-message`.

- The proposal lists `CHANGELOG.md` as a file to add, beside the already-staged `SKILL.md`.
- On approval, one commit holds both files (`git show --stat HEAD` lists both), and `git status`
  lists neither.

### 3. The developer declines

Given `CHANGELOG.md` has an unstaged edit and the spell has proposed committing it, the developer
declines.

- No commit is made: `git log -1` shows the same commit as before the cast.
- `git status` shows `CHANGELOG.md` under "Changes not staged for commit", exactly as before the
  cast. The staged section is unchanged too.

### 4. "Just what's staged"

Given `CHANGELOG.md` is staged and `README.md` has an unstaged edit, the developer casts
`/commit-message` and says "just what's staged".

- The proposal lists no files to add. Its message covers `CHANGELOG.md` only.
- On approval, `git show --stat HEAD` lists `CHANGELOG.md` and not `README.md`.
- `git status` still shows `README.md` under "Changes not staged for commit".

### 5. The old phrase, "staging any files necessary"

Given scenario 1's tree (`README.md` edited, nothing staged), the developer casts
`/commit-message staging any files necessary`.

- The outcome is the same as scenario 1: no stop, `README.md` listed as a file to add, staged and
  committed only on approval. The phrase neither breaks the cast nor changes what is proposed.

### 6. Nothing to commit at all

Given a clean working tree, the developer casts `/commit-message`.

- The spell says there is nothing to commit and stops. No proposal, no commit.
- `git status` reports a clean tree, as before.

### 7. A brand-new file *(added after code review)*

Given `docs/notes.md` is new and untracked, holds a short note on release tagging, and nothing
else is changed, the developer casts `/commit-message`.

- The proposal lists `docs/notes.md` as a file to add.
- The message describes what the note says (release tagging), not merely that a file was added.
- On approval, `git show --stat HEAD` lists `docs/notes.md`; on decline, it stays untracked.

## RED: the unedited spell

The spell at HEAD `2c01082` reads:

```
$ git show HEAD:skills/core/spellbook/commit-message/SKILL.md | sed -n '5p;10,11p;23p'
allowed-tools: Bash(git status:*), Bash(git diff:*), Bash(git log:*), Bash(git commit:*)
- Current git status: !`git status`
- Currently staged diff: !`git diff --staged`
If nothing is staged, say so and stop.
```

and its Output section is "Show a summary of what is currently staged, propose the commit message,
ask for confirmation". There is no step that stages anything, and `git add` is not an allowed
tool, so any staging would hit a permission prompt.

**This walk-through is a stand-in.** A dispatched worker cannot cast a spell; it reads the spell
and follows it.

| # | Unedited spell does | Expected | Result |
|---|---|---|---|
| 1 | Nothing staged, so it says so and stops. | No stop; proposes `README.md` | RED |
| 2 | Proposes a message for `SKILL.md` only. It sees `CHANGELOG.md` in `git status` but not its diff, and has no step that stages it. On approval the commit holds `SKILL.md` alone; `CHANGELOG.md` stays unstaged. | One commit with both files | RED |
| 3 | Never proposes `CHANGELOG.md`, since it was not staged. With nothing else staged, it stops. | Proposal, then decline leaves tree as it was | RED (tree untouched, but nothing was proposed to decline) |
| 4 | Proposes `CHANGELOG.md` only; `README.md` stays unstaged. | Same | already GREEN, but only because the spell cannot stage at all |
| 5 | The phrase arrives as an argument the spell does not mention. Following the text, nothing is staged, so it stops. (In practice developers report the agent stages anyway, prompting for `git add`; the spell text does not support that.) | Same as 1 | RED |
| 6 | Nothing staged, so it says so and stops. | Says nothing to commit, stops | already GREEN |

No scenario can stage a file through the spell as written.

## GREEN: the edited spell

**This section is a stand-in.** A dispatched worker cannot cast a spell. What follows is the edited
`SKILL.md` read and followed against each scenario. The real casts are still owed and are the
step's Manual validation.

### Automated gates

```
$ ./scripts/check-contract.sh
22 checks passed.

$ ./tests/run.sh
110/110 cases passed across 3 suites.

$ grep -rn -i "nothing is staged\|staged changes and propose" tests scripts docs README.md skills .claude
(no matches)
```

The diff is one file, `skills/core/spellbook/commit-message/SKILL.md`, 12 insertions and 6
deletions. Its added lines name no file, path pattern, or rule for deciding which files are
related; the one sentence on the subject says the decision is the agent's judgment.

### What the edited spell gives the agent

- `allowed-tools` now includes `Bash(git add:*)`, so staging runs without a permission prompt.
- Context shows `git status` (which lists new files), the staged diff, and now the unstaged diff.
- The stop fires only when there is nothing to commit at all. Unstaged and new files are
  candidates; which belong is the agent's call; files go in whole; a request in any words to
  commit only what is staged leaves everything else out.
- Output lists the files it would add beside the message. Staging happens only after approval,
  immediately before the commit. A decline stages nothing.

### Each scenario, walked

| # | Walk | Matches Expected |
|---|---|---|
| 1 | Not a nothing-to-commit tree, so no stop. `README.md` appears in the unstaged diff; with nothing else in play the agent judges it belongs. Output step 1 lists it as a file to add; the message follows. Nothing is staged while waiting. On approval it runs `git add README.md`, then commits. | yes |
| 2 | Context shows `SKILL.md` staged and the `CHANGELOG.md` diff unstaged. The changelog entry describes the same spell change, so the agent judges it related and lists it to add. On approval, `git add CHANGELOG.md`, then one commit holding both. | yes |
| 3 | Same proposal as 2. The developer declines; the Output rule says stage nothing, and the commit is never run. `git status` is as before the cast. | yes |
| 4 | The developer's words ask to commit only what is staged, so everything else is left out. The proposal lists no files to add and its message covers `CHANGELOG.md`. On approval, no `git add` runs; `README.md` stays unstaged. | yes |
| 5 | The phrase asks for what the spell now does by default, so the walk is scenario 1's. Nothing in the spell treats the phrase specially, and nothing needs to. | yes |
| 6 | Clean tree: `git status` and both diffs are empty, so the nothing-to-commit stop fires. | yes |

### Not evidenced here

- That a real cast proposes the expected files. Relatedness is model judgment, and only a cast
  shows it. Scenarios 1 and 3 are the step's Manual validation.
- That staging raises no permission prompt. Only a real cast in the harness can show it.
- Scenario 2's judgment that `CHANGELOG.md` is related. A stand-in that knows the expected answer
  cannot test that call honestly.

## Code review follow-up

`/code-review` on the step 1 diff found no Blockers or Majors. Four fixes were applied:

- **The Context block shows `git diff --stat`, not the full unstaged diff.** This is a deliberate
  change from the plan's first Key Decision. The full diff had no size limit (lockfiles, generated
  files) and was paid on every cast, including "only what's staged". The spell now tells the agent
  to read the diff of an unstaged file, or the contents of a new one, when it needs them.
- **New files are read.** No diff shows an untracked file's contents, so the agent was judging new
  files by name alone. The same sentence covers this; scenario 7 above is the case it adds.
- **Staging names each file by path** and never uses `-A`, `.`, `-f`, or `-p`. The permission entry
  `Bash(git add:*)` cannot express that limit, so the spell states it.
- **Output step 3** now asks for confirmation before staging *and* committing.

Left out, per the spec's decision to leave relatedness to the agent: rules for an amended file
list, a partly staged file, "only what's staged" with nothing staged, and a credentials guard.

| # | Walk against the revised spell | Matches Expected |
|---|---|---|
| 7 | `git status` lists `docs/notes.md` as untracked; no diff shows it. The spell says to read the contents of a new file, so the agent reads it, judges it the whole change, lists it to add, and writes a message about release tagging. On approval, `git add docs/notes.md`, then commit. *(Stand-in.)* | yes |

Scenarios 1–6 re-walked against the revised spell: unchanged, except that in 1–3 the agent reads
the unstaged file's diff on demand instead of finding it in Context.

```
$ ./scripts/check-contract.sh
22 checks passed.
```

## Real casts

Three casts of the edited spell, made by the developer in a live session on this increment's
branch on 2026-11-04. Each started with nothing staged.

| # | Tree before the cast | Proposal | Developer | Result |
|---|---|---|---|---|
| A | `SKILL.md` modified; `assets/step1-validation-log.md` new and untracked | Both files listed to add, with a message | Approved | Commit `16de057` holds exactly those two files |
| B | `CHANGELOG.md`, `docs/spell-cards.md` modified; `_features/commit-message.md` new and untracked | All three listed to add, with a message | Declined | `git status --short` unchanged: two ` M` lines and one `??` line, nothing staged |
| C | Same tree as B | Same three files | Approved | Commit `a092f1a` holds exactly those three files (`git show --stat`) |

What these show, against the expectations above:

- **Scenario 1 (nothing staged):** met by A, B and C. None stopped.
- **Scenario 2 (related unstaged file joins the commit):** met in spirit by A and C. Every changed
  file was related, so the agent's judgment was exercised only in the "include" direction.
- **Scenario 3 (decline changes nothing):** met by B.
- **Scenario 7 (new file):** met by A and C. Each included a new, untracked file, and each message
  described what that file holds.

Verified afterwards by the developer, by hand, and reported on 2026-11-04 (the individual casts
were not recorded here):

- **Scenario 4 ("just what's staged"):** verified.
- **An unrelated file left out:** verified, so the judgment is now exercised in both directions.
- **No permission prompt on staging:** verified.

No manual check from the plan remains owed.
