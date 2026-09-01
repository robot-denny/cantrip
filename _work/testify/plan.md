# Plan: Testify — The Coverage Spell

**Spec**: `_work/testify/spec.md`
**Branch**: `robot-denny/feature/testify`
**Work type**: `new-capability` — copied verbatim from the spec's `**Work type**:` line; this decides
how the final step records behavior
**Feature doc**: `test-coverage` (`_features/test-coverage.md`) — copied from the spec; the final step
targets this, not the increment slug

## Context

`/testify` is the ninth workflow spell and the first QA-owned verb: it reads a capability doc's Test
Coverage table as a work queue, reports what nothing proves, writes and runs tests on approval, and
records what each run established. Its audit mode sweeps every capability doc and reports drift in
both directions. The roadmap decided on 2026-08-25 that this is a separate spell rather than a mode
on `/feature`, so the two share no machinery.

The unit of work in this repo is **a shipped unit plus its registration**, established by
`install-verification` and followed by the guides and styleguide increments. This increment ships
**one new core unit** (`skills/core/spellbook/testify/SKILL.md`) plus **amendments to four shipped
units**: `templates/feature.md` gains two coverage statuses, `/feature` and `/spec` learn to write
them, and `/plan` and `/block` have their shared `## Tests` fallback reworded so a third caller can
adopt it.

**Unlike every previous spellbook increment, this one ships no script.** `skills/core/` contains
nothing but `SKILL.md` files and templates — core has never shipped an executable, and nothing here
justifies being the first. That decision shapes the whole plan: there is no fixture suite, because
`tests/run.sh` needs an executable `subject`, and the RED signals come from `scripts/check-contract.sh`
instead.

---

## Key Decisions

- **No script, and therefore no fixture suite.** Every file under `skills/core/` today is a `SKILL.md`
  or a template. The drift detection in audit mode is the one part that would benefit from an
  executable, but it would have to parse comment headers in arbitrary languages to be useful, which is
  precisely the stack knowledge an L0 unit may not hold. A pack may ship one later; core does not.
  Consequence: `tests/run.sh` gains no suite, and every step below is gated by
  `./scripts/check-contract.sh` and by reading.

- **The `## Tests` slot fallback has to be reworded before `/testify` can read that slot.**
  Contract check 9 ("the same slot always gets the same fallback") fails when two shipped files give the same
  slot different fallbacks. `/plan` and `/block` currently share this wording verbatim:

  > infer from existing test files; if the project has no tests yet, propose a location in Key
  > Decisions and flag it as a new convention being established.

  `/testify` writes no Key Decisions — it routes convention-setting to `/spec` — so it can neither
  copy that wording honestly nor diverge from it without tripping the gate. **The fallback is
  reworded once, for all three callers**, to name the obligation rather than the destination:

  > infer from existing test files. If the project has no tests yet, propose a location and flag
  > plainly that you are establishing a convention rather than following one — never settle it
  > silently.

  Each spell's own surrounding prose then says where its proposal goes: Key Decisions for `/plan` and
  `/block`, the gap report and a hand-off to `/spec` for `/testify`. This is the check doing its job —
  it caught a real divergence at authoring time.

- **The `## Build` fallback is reused verbatim** — "infer the build and test commands from the repo
  root and state which you used; if genuinely ambiguous, ask rather than guessing" — which is already
  true for a spell that runs tests. No amendment needed.

- **Two new statuses, both named for an observation rather than a diagnosis.** `Test failing` and
  `Not coverable — <reason>`. The reasoning behind the first is the increment's main shaping decision
  and gets an ADR: a test that fails may mean not-built-yet, a regression, or a wrong doc, and the
  spell cannot tell those apart, so it records what it saw and lets the Draft banner and the report
  supply the interpretation.

- **The Draft banner is report framing, never control flow.** `/plan` phases work and
  `/implement-step` runs one step at a time, so a partly-built capability with some scenarios
  genuinely passing is the normal middle state of the flow. A mode that demanded a red run from a
  draft doc would misreport every legitimately-passing test in a half-built increment. Guarding
  against a vacuously-passing test is the assertion probes' job, and they run on every path.

- **A new contract check gates the status vocabulary.** The spec names the failure directly: "a status
  defined in one place and unknown to its writers is worse than no status." Three shipped files must
  agree on the vocabulary — `templates/feature.md` declares it, `/feature` and `/spec` write it. That
  is deterministic and greppable, so it becomes check 17 rather than a thing a reviewer must remember.
  This is one of the "structural gate checks" the roadmap already wants; it is built here because this
  increment is the first to add a status and would otherwise have no RED signal for Step 1.

- **The pre-commit hook blocks a commit on a failing contract gate**, so every step's RED must be
  consumed inside that step. The styleguide increment hit this and had to pull a roster edit forward
  into an earlier commit; Step 2 below keeps creation and registration together for the same reason.
  Do not reach for `--no-verify`.

- **Commands, inferred because there is no `.agents/config/` in this repo.** Recorded here so no later
  step re-derives them: `./scripts/check-contract.sh` (the gate, 17 checks today — sixteen numbered plus 1b — and 18 after Step 1),
  `tests/run.sh` (every fixture suite), `./scripts/check-install.sh --verbose` (the consumer-facing
  install verifier, ungated and verified by reading). There is no build step — the deliverable is
  markdown.

- **The spell census moves from eight to nine**, against ADR 0010's working ceiling of ten. Three
  places state it: contract check 16 computes it, `README.md` says "Eight workflow spells" in prose,
  and `CHANGELOG.md` records the census. Check 16 will pass silently at nine; the other two are
  ungated and are Step 7's responsibility.

---

## Steps

Each step is designed to be completed independently in its own context window.
The step heading contains a ready-to-use prompt you can paste into a new session.

---

### Step 1 — The coverage status vocabulary, and a check that keeps its writers in step

> **Prompt**: Implement Step 1 of `_work/testify/plan.md`. Add two statuses to the Test Coverage
> vocabulary — `Test failing` (a test exists and its last run did not pass; named for the observation,
> not its cause) and `Not coverable — <reason>` (the project has decided this scenario cannot be
> tested here). Write ADR 0016 recording why a coverage status names an observation rather than a
> diagnosis, following the structure of `adr/_template.md` and the tone of the existing ADRs. Update
> `skills/core/reference/workflow/templates/feature.md` so both statuses appear in the table's example
> rows and in the explanatory HTML comment beneath it. Then add contract check 17 to
> `scripts/check-contract.sh`, "coverage statuses are known to every spell that writes them": it reads
> the status vocabulary declared in the template's comment and fails if any status is not also named
> in `skills/core/spellbook/feature/SKILL.md` and `skills/core/spellbook/spec/SKILL.md`. Confirm it
> goes RED, then update those two spells to describe both new statuses and confirm GREEN. Do not
> create the `/testify` spell in this step.

**What to build**: `adr/0016-coverage-status-names-an-observation.md`;
`skills/core/reference/workflow/templates/feature.md` (example rows + the comment block);
`scripts/check-contract.sh` (check 17, plus its entry in the header comment listing which checks
inspect this repo versus shipped units); `skills/core/spellbook/feature/SKILL.md` and
`skills/core/spellbook/spec/SKILL.md` (both describe the new statuses where they describe the table).

**Test first**:
- Add the two statuses to `templates/feature.md` **only**, leaving `/feature` and `/spec` untouched.
- Write check 17 and run `./scripts/check-contract.sh`. **RED is check 17 naming `Test failing` and
  `Not coverable` as declared in the template but absent from both writer spells.** Read the failure
  and confirm it names which spell is missing which status — a check that says only "mismatch" is not
  worth having.
- Then update the two spells and confirm GREEN.
- Assert on the vocabulary the template *declares*, not on a list hardcoded inside the check. A check
  carrying its own copy of the list is a fourth place to keep in step, which is the problem it exists
  to solve.

**Validation**:
- [Automated]: `./scripts/check-contract.sh` — 18 checks pass.
- [Automated]: `tests/run.sh` — every suite unchanged and green.
- [Manual]: delete one status from `/feature` and confirm check 17 goes red naming that spell and that
  status; restore it.
- [Manual]: read the template's comment block as someone filling a coverage table for the first time,
  and confirm the five statuses are told apart by what each *claims*, not by when each is used.

---

### Step 2 — The spell exists, reads its inputs, and the gate is green

> **Prompt**: Implement Step 2 of `_work/testify/plan.md`. Create
> `skills/core/spellbook/testify/SKILL.md` with complete frontmatter — `name: testify`, a
> trigger-engineered `description`, `disable-model-invocation: true` (every spellbook unit sets it),
> `argument-hint`, and an `allowed-tools` list. Write only the spell's opening: how it resolves its
> argument to a capability doc under the workspace layout (consult the `workflow` skill for the
> layout rather than hardcoding `_features/`), how it reads that doc's Test Coverage table, what it
> does when the argument names an increment slug rather than an area, and what it does when the doc
> has no table. Declare the two slots it reads — `.agents/config/stack.md` → `## Tests` and
> `## Build` — each with an `**If empty:**` line. **Use the reworded `## Tests` fallback from the
> plan's Key Decisions, and reword `/plan` and `/block` to match it**; contract check 10 fails until
> all three agree word for word. Then register the unit: `ln -s
> ../../skills/core/spellbook/testify .claude/skills/testify`, and add `testify` to `ROSTER_CORE` in
> `scripts/check-install.sh`. Do not write the gap report, the write path, or audit mode yet.

**What to build**: `skills/core/spellbook/testify/SKILL.md` (frontmatter, argument resolution, table
reading, both slot declarations); `skills/core/spellbook/plan/SKILL.md` and
`skills/umbraco-17/spellbook/block/SKILL.md` (the `## Tests` fallback, reworded);
`.claude/skills/testify` (symlink); `scripts/check-install.sh` (`ROSTER_CORE`).

**Test first**:
- Create the SKILL.md with its frontmatter and slot blocks, and run `./scripts/check-contract.sh`
  **before** touching anything else. **RED is three checks at once**: check 9 (the `## Tests` slot now
  has two different fallbacks), check 11 (self-hosting — no symlink for the new core skill), and check
  13 (the install checker's roster does not list it). Read all three failures before fixing any.
- Fix them in that order and re-run after each, so each check is observed going green for its own
  reason rather than all three at the end.
- Registration and creation stay in one step deliberately: the pre-commit hook blocks a commit while
  checks 11 and 13 are red, so splitting them would force a `--no-verify`.

**Validation**:
- [Automated]: `./scripts/check-contract.sh` — 18 checks pass, including 5 (invocation posture), 6
  (frontmatter complete), 8 (no technology names in L0), 9, 11, 13, and 16 (the budget, now
  reporting nine workflow spells against a ceiling of ten).
- [Automated]: `./scripts/check-install.sh --verbose` names `testify` among the core units.
- [Automated]: `tests/run.sh` — every suite green; the install-check fixtures use a four-skill core
  subset and `in_roster` filters what it finds rather than demanding every roster entry, so a new
  roster name must not change any case. Confirm rather than assume.
- [Manual]: read the reworded `## Tests` fallback in all three files and confirm it is honest for a
  caller that has no Key Decisions section.

---

### Step 3 — The gap report: three groups, and the scenario too vague to test

> **Prompt**: Implement Step 3 of `_work/testify/plan.md`. Extend
> `skills/core/spellbook/testify/SKILL.md` with the gap report, which is the first output of both
> modes and is produced before anything is written. It groups unproved scenarios into three sets —
> writable now; blocked on missing test infrastructure, naming what each one needs; and inferred from
> code rather than specified, carrying the warning that proving one turns a reading of the code into a
> contract. Add the rule that a scenario naming no specific observable outcome is reported as a
> question for whoever wrote the doc and gets no test at all, because a guessed assertion is worse
> than an empty row. Add the rule that a scenario recorded `Not coverable` is skipped, never
> re-proposed, and its recorded reason repeated in the report. State that a capability whose scenarios
> are all proved gets a short "nothing to do" rather than manufactured work. Read the spec's
> *Scenarios (Draft)* for the rules this step covers and keep the spell's language stack-agnostic —
> contract check 8 forbids technology names in L0.

**What to build**: `skills/core/spellbook/testify/SKILL.md` — the report section and the four rules
above.

**Test first**:
- No automated RED exists for prose. Define the check before writing: take the six spec scenarios
  under the three report rules plus the vague-scenario and not-coverable rules, and for each, name the
  sentence in the spell that produces it. A rule with no sentence is the gap.
- Write the section, then walk the same six scenarios and confirm each now resolves to specific
  instruction rather than to a heading.

**Validation**:
- [Automated]: `./scripts/check-contract.sh` — 18 pass. Check 8 is the one to watch: the blocked-on-
  infrastructure group is where a test-runner name would slip in.
- [Manual]: read the three groups and confirm each names a *different decision the reader has to
  make*. If two groups lead to the same next action, they are one group.
- [Manual]: confirm the vague-scenario rule gives a test for vagueness that does not depend on
  judgment alone — "no value to compare, nothing that distinguishes present from absent".

---

### Step 4 — The write path: approval, the run, and what the row records

> **Prompt**: Implement Step 4 of `_work/testify/plan.md`. Extend
> `skills/core/spellbook/testify/SKILL.md` with everything between approval and the updated table.
> Row-by-row approval, with nothing written until the reader confirms that specific scenario. The
> assertion probes: for each proposed test, report the specific ways it could have passed while the
> behavior was broken — a wrong value, the thing rendering somewhere else, an empty page, a check
> satisfied by the artifact merely existing — alongside the `tdd-principles` failure modes. State that
> no red-to-green signal is available for behavior that already works, and that the probes rather than
> a red run are what guard against a vacuous test. Then the recording rule: a row records what the
> test's last run established — proved when it passed, `Test failing` when it did not, unchanged when
> the test could not be run at all — **whether or not the doc is still a draft**. Add the provenance
> header: every test the spell writes opens with a comment naming the capability doc, the scenarios
> that file covers, and the date; **specify the header's content and that it must be a comment, and
> name no comment syntax of any language** — the syntax is inferred from tests the project already
> has. Finally, the Draft banner as framing: it changes how a failure is *explained*, never what is
> written. Add the rule that behavior noticed with no scenario describing it is named and handed to
> `/feature`, never written into the doc here.

**What to build**: `skills/core/spellbook/testify/SKILL.md` — approval gate, assertion probes, the
recording rule, the provenance header, the Draft-banner framing rule, the hand-off to `/feature`.

**Test first**:
- Define the check first: the spec's "Half a half-built capability passes and the rest fails" scenario
  is the one this step exists to get right. Before writing, state what the spell must say for that
  scenario to come out correct, and confirm afterwards that it says it.
- Then walk the two framing scenarios (a failure against a draft doc, the same failure against a
  verified one) and confirm the spell produces two different sentences and one identical status.
- **The specific thing to check for is a branch that should not exist**: search the section for any
  instruction that reads the Draft banner and then decides what to *write*. There must be none.

**Validation**:
- [Automated]: `./scripts/check-contract.sh` — 18 pass. Check 8 again: the provenance header is the
  likeliest place for a comment syntax to appear, and a `//` or a `#` in an example would be a
  technology name in all but spelling.
- [Manual]: confirm the probes are phrased as questions the reader can answer about a specific
  proposed test, not as a checklist of virtues.
- [Manual]: confirm the recording rule reads as one rule with no draft/verified fork.

---

### Step 5 — Blocked rows, and the refusal to establish a convention

> **Prompt**: Implement Step 5 of `_work/testify/plan.md`. Extend
> `skills/core/spellbook/testify/SKILL.md` with the two places it stops. First: where proving a
> scenario needs test infrastructure the project does not have, name what is needed, write the tests
> that are writable, and end pointing at `/spec` for the infrastructure. Second: where the project has
> no tests at all and no recorded place to put them, decline to decide where tests go — say plainly
> that the convention has never been decided here, and route it to `/spec`. Follow the shape `/block`
> Step 5 uses for a greenfield project with no exemplar block, and note that contract check 10
> ("exemplar instructions handle having no exemplar") exists precisely because this pattern was
> unguarded three times out of four. Then write the spell's `Next:` line. It suggests and never
> invokes: `/code-review` after tests are written, `/spec` when anything was blocked.

**What to build**: `skills/core/spellbook/testify/SKILL.md` — the blocked-infrastructure path, the
no-convention refusal, the `Next:` line.

**Test first**:
- The RED here is a contract check that will fire if the refusal is written carelessly: check 10,
  "exemplar instructions handle having no exemplar". Write the no-convention path referring to the
  project's existing tests as the exemplar, run the gate, and see whether check 10 catches a missing
  absence clause. If it passes on the first write, verify the check actually inspects this file by
  temporarily removing the absence clause and confirming it goes red.
- Then confirm both spec scenarios resolve — the partly-blocked capability and the project with no
  tests at all.

**Validation**:
- [Automated]: `./scripts/check-contract.sh` — 18 pass, check 10 (exemplar absence clause) included.
- [Manual]: confirm neither stop is a dead end — each names the remedy and the spell that owns it.
- [Manual]: confirm the `Next:` line suggests and does not invoke, per the hard rule in `AGENTS.md`.

---

### Step 6 — Audit mode: the project-wide sweep and four kinds of drift

> **Prompt**: Implement Step 6 of `_work/testify/plan.md`. Extend
> `skills/core/spellbook/testify/SKILL.md` with `/testify audit` — read-only across every capability
> doc, writing nothing, touching no test file, and offering no approval prompt. It reports four kinds
> of drift: a scenario no test proves; a test whose scenario has since changed, shown as it was
> written and as it reads now; a test whose scenario has been deleted; and a row claiming proof whose
> named test no longer exists or currently fails. Stale and orphaned detection reads the provenance
> header from Step 4 — say so, and say why matching scenario names as strings is not the fallback: it
> breaks exactly when a scenario is reworded, which is when detection matters most. Rank capabilities
> by how much is unproved. Handle a project with no capability docs by saying so and naming the first
> doc as what has to happen first. Write this as a **self-contained section** naming no CMS, no
> serialization format, and no file, so that if it later converges with the report shape in
> `umbraco-17-guide-scaffolding` the extraction is a move rather than a rewrite — the spec leaves that
> convergence deliberately unanswered, and this is what keeps the option open.

**What to build**: `skills/core/spellbook/testify/SKILL.md` — the audit mode section.

**Test first**:
- Define the check first: the five audit scenarios in the spec — the ranked report, stale, orphaned,
  the row claiming proof whose test has gone, and the project with no docs. Name the sentence
  producing each.
- **Then check the harder property**: read the section as if extracting it into core tomorrow. If any
  sentence depends on something outside the section, it is not self-contained and the extraction
  option the spec is preserving does not actually exist.

**Validation**:
- [Automated]: `./scripts/check-contract.sh` — 18 pass.
- [Manual]: confirm audit mode cannot write. Search the section for any instruction that creates or
  edits a file; there must be none.
- [Manual]: confirm the stale report shows both versions of the scenario. A stale flag that does not
  show what changed makes the reader open two files to learn anything.

---

### Step 7 — Document the spell and correct the census

> **Prompt**: Implement Step 7 of `_work/testify/plan.md`. **None of this is gated by any check** —
> check 16 computes the spell count and will pass silently at nine, and everything below is prose that
> fails silently when wrong. In `README.md`: add a `/testify` row to the spellbook table describing
> what it does for someone deciding whether to cast it, and change "**Eight workflow spells, and the
> count is meant to stay small**" to nine. In `CHANGELOG.md`: describe what shipped under
> `[Unreleased]`, readable as "what will change in my project when I update" — the new spell, the two
> new coverage statuses, the reworded `## Tests` fallback affecting `/plan` and `/block`, and contract
> check 17. Correct the existing census line that says eight workflow spells. In `ROADMAP.md`: move
> "A spell for tests" out of **Next** into **Recently shipped**, and carry forward the questions this
> increment leaves open rather than dropping them — in particular that the audit report shape now has
> its second caller, which is what the editor-guides entry was waiting on, and that answering it also
> settles the scaffolding reference's size entry in **Later**. Then run every gate.

**What to build**: `README.md` (spellbook table row, the census sentence); `CHANGELOG.md` (the
increment, and the corrected census); `ROADMAP.md` (Next → Recently shipped, plus the carried-forward
open questions).

**Test first**:
- **There is no RED signal for this step, and that is the thing to be careful about** — the same
  hazard the styleguide increment recorded at its own Step 10. Check 16 passes at nine whether or not
  the README agrees, so nothing catches a stale prose count.
- Verify by reading rather than by watching a check: `grep -rn "[Ee]ight workflow spells" .` must
  return nothing, and `./scripts/check-contract.sh --verbose` should show check 16 reporting nine.

**Validation**:
- [Automated]: `./scripts/check-contract.sh --verbose` — 18 pass; check 16 lists nine workflow spells.
- [Automated]: `./scripts/check-install.sh --verbose` — `testify` appears among the core units.
- [Automated]: `tests/run.sh` — every suite green.
- [Manual]: read the README row as a consumer deciding whether this spell is worth casting, and
  confirm it says what makes `/testify` different from `/feature` — the two operate on the same doc.
- [Manual]: confirm the roadmap's carried-forward questions are stated where they belong rather than
  left inside a shipped increment's spec.

---

### Final — Record the durable behavior *(a spell you cast, not an implement-step)*

**Do not number this as an implementation step.** It is cast directly after the implement-step loop
finishes. Numbering it would invite `/implement-step <plan> N`, which dispatches a code worker to run
a spell — the wrong mechanism, and it blurs the chain's boundary between building and recording.

> **Prompt**: Run `/feature update test-coverage` to verify `_features/test-coverage.md` against what
> was actually built. Review each of its 26 draft scenarios against the shipped spell and update any
> where the implementation diverged. **Remove the "Draft" banner.** Fill in the Test Coverage table —
> and expect most rows to stay uncovered, honestly: this increment ships no executable, so
> `tests/run.sh` has no suite for it and the only automated coverage is contract check 17, which
> proves the status-vocabulary scenarios and nothing else. Mark the rest **Not covered** rather than
> writing a weaker test and claiming the scenario; the spec's *Testing Guidelines* already rules the
> report-prose scenarios out of harness scope, and that reasoning belongs in the doc where a reader
> will meet the gaps. Flip the `/testify` entry in the doc's **Increments** list from planned to
> shipped and point it at `_work/testify/spec.md`. Leave the four parking-lot entries intact — none is
> closed by this work. Add a revision note dated today.
>
> **Validation**: Every scenario matches observable behavior; the Draft banner is gone; every "Not
> covered" row is one the doc explains rather than one that merely went unfilled.

---

## File Summary

| Action | File |
|--------|------|
| Create | `skills/core/spellbook/testify/SKILL.md` |
| Create | `adr/0016-coverage-status-names-an-observation.md` |
| Create | `.claude/skills/testify` (symlink to `../../skills/core/spellbook/testify`) |
| Modify | `skills/core/reference/workflow/templates/feature.md` (two new statuses, example rows and comment) |
| Modify | `skills/core/spellbook/feature/SKILL.md` (describes the new statuses) |
| Modify | `skills/core/spellbook/spec/SKILL.md` (describes the new statuses) |
| Modify | `skills/core/spellbook/plan/SKILL.md` (`## Tests` fallback, reworded) |
| Modify | `skills/umbraco-17/spellbook/block/SKILL.md` (`## Tests` fallback, reworded) |
| Modify | `scripts/check-contract.sh` (check 17, plus its header-comment entry) |
| Modify | `scripts/check-install.sh` (`ROSTER_CORE`) |
| Modify | `README.md`, `CHANGELOG.md`, `ROADMAP.md` |
| _(work type: `new-capability`)_ Update | `_features/test-coverage.md` — verify against the implementation, drop the Draft banner |
