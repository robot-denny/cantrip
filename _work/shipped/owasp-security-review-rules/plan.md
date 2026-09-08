# Plan: OWASP Security Review Rules

**Spec**: `_work/shipped/owasp-security-review-rules/spec.md`
**Branch**: `robot-denny/owasp-security-review-rules`
**Work type**: change-to code-review
**Feature doc**: code-review

## Context

Review already covers security as the quality reviewer's first focus area. What it cannot do is name
the standard it checked against or the areas it swept, so a finding reads as an assertion and a clean
review is indistinguishable from one that never looked. This increment adds a technology-agnostic
`security-review-rules` reference to core and gives `code-reviewer` explicit ownership of it, per
[ADR 0018](../../../adr/0018-where-new-review-substance-goes.md).

**The unit of work in this repo is a shipped unit plus the registrations that make it reachable.**
Five contract gates fire on a new core reference — frontmatter (6), no technology names (8),
self-hosting (11), the install checker's roster (13), README reachability (18) — so authoring and
registering are two halves of one thing, and the gap between them is a real RED. Two further gates are
built here, which is the increment's own new behavior.

Baseline before starting: `./scripts/check-contract.sh` reports 19 checks passed, `tests/run.sh`
reports 110/110 across 3 suites.

---

## Key Decisions

- **The reference is content plus a committed category table, and nothing else.** No `**Slot:**`
  declaration. Project-specific security rules already have a home on `code-reviewer`
  (`.agents/config/reviewer-rules/code.md`), and adding a second slot would trip checks 4 and 9 for no
  gain.
- **Pin the revision by looking it up, not by recall.** This increment exists because a cited category
  drawn from memory can be stale or invented. Authoring its own table from memory would be the same
  defect one level up. Step 1 verifies the current revision and its category list against the OWASP
  source before committing the table, and records in the reference which revision was pinned.
- **AC9 is narrower than the spec states, and deliberately so.** "The table matches the categories of
  the revision it names" is not fully checkable locally: verifying that an identifier really carries
  that name in that revision needs a second copy of the list, which is exactly what AC5 forbids. So the
  gate checks what is checkable without a second copy — a complete and unique identifier sequence, one
  name per identifier, the declared count matching the number of rows, and the revision named once.
  **Name accuracy is verified once by a person at authoring time against the source and is not gated.**
  That is a real limit, recorded here rather than discovered later from a passing gate.
- **The `Clean` section instruction goes in `code-reviewer.md`, not in `reviewer-discipline`.** The
  `Clean` section is defined by the shared contract, but naming OWASP areas is one reviewer's domain.
  Putting an OWASP instruction in the shared contract would hand the rule to all three reviewers and
  recreate the domain-boundary problem ADR 0018 avoids.
- **No contract-check fixture suite exists, and this increment does not build one.**
  `scripts/check-contract.sh` runs `cd "$(dirname "$0")/.."` unconditionally, so `tests/run.sh` — which
  executes a subject inside a case directory — cannot exercise it; the subject would re-scan the real
  repo. Negative verification is therefore a hand-run recorded as a validation log, following the
  `review-failure-modes` precedent (`_work/shipped/review-failure-modes/assets/step3/30-validation-log.md`).
  Making contract checks fixture-testable would mean giving the gate a root argument, which is its own
  increment with its own negative tests. **Both halves are now recorded.** The practice a check author
  needs today is in `AGENTS.md` under *Authoring conventions*; the underlying limitation is filed in
  `ROADMAP.md` under *Later*. The original suggestion was to write it to
  `.agents/config/conventions.md` → `## Planning gotchas`, which this repo has no `.agents/` directory
  for. Creating one would switch on the config layer for four spells and the install checker here, so
  it is a posture decision rather than a note, and it did not belong inside this increment.
- **Update the spell-card deck in Step 7.** This reverses an earlier decision to defer it, and the
  reason for the reversal is worth recording. Deferring rested on two facts. The file is not gated,
  and it was being rewritten wholesale on the `robot-denny/prose-discipline` branch, so a card added
  here would have met a merge conflict for no gain. **That branch merged on 2026-09-04 and this one
  is rebased onto it, so the conflict is gone.** What remains is an ungated file that misstates what
  the toolkit ships: 33 cards against 34 units, and a stated 17 references against 18. The deck's own
  regeneration note is an instruction for a person to re-count rather than a process that will catch
  this, so deferring to it means deferring to someone remembering.
- **Commands, inferred because this repo has no `.agents/config/`** (it is the toolkit, not a consuming
  project): `./scripts/check-contract.sh` for the gate (add `--verbose` to see per-check names),
  `tests/run.sh` for the fixture suites, `tests/run.sh install-check` for that suite alone. The
  pre-commit hook in `.githooks/pre-commit` runs the gate, so a failing gate blocks a commit already.
- **Frontmatter constraints worth knowing before writing**: check 6 requires `name:` to match the
  directory name exactly and `description:` to be at least 40 characters. Check 8's forbidden pattern
  includes framework and language names, so the reference must describe injection sinks, template
  output, and dependency handling in neutral terms — no language, ORM, templating helper, or package
  manager by name.

---

## Steps

Each step is designed to be completed independently in its own context window.
The step heading contains a ready-to-use prompt you can paste into a new session.

---

### Step 1 — Author the security reference

> **Prompt**: Implement Step 1 of `_work/shipped/owasp-security-review-rules/plan.md`. Create
> `skills/core/reference/security-review-rules/SKILL.md`, a new technology-agnostic core reference. Read
> `_work/shipped/owasp-security-review-rules/spec.md` for FR1, FR1a, FR5, and FR6, and read
> `skills/core/reference/memory-discipline/SKILL.md` for the house structure of a core reference.
> **Look up the current OWASP Top 10 revision and its category list from the OWASP source rather than
> writing it from memory** — this increment exists because recalled citations go stale, so recalling
> the table would reproduce the defect. Commit the category identifiers and names as a literal table,
> name the pinned revision in exactly one place in this file, state which categories a review scoped to
> a single change cannot reach and what kind of assessment covers them instead, and describe the
> citation convention. Keep every word technology-agnostic: check 8 forbids naming a language,
> framework, templating helper, ORM, or package manager. Frontmatter needs `name:
> security-review-rules` matching the directory and a `description:` of at least 40 characters written
> to trigger on security review work. Do not register the unit yet — that is Step 2. Then run
> `./scripts/check-contract.sh` and confirm it fails on checks 11, 13, and 18, each naming this new
> unit.

**What to build**:
- `skills/core/reference/security-review-rules/SKILL.md`, containing:
  - frontmatter: `name: security-review-rules`, a trigger-engineered `description:` over 40 chars
  - the pinned revision, stated **once**
  - a literal table of category identifiers and names, with the declared count
  - what each category means and what to look for, in neutral terms
  - the citation convention: number and name on every security finding, alongside the file and line
    the evidence standard already requires
  - which categories a change-scoped review cannot reach — design-level and dependency-age — and
    generically what covers them, without naming a unit or a product (ADR 0003)
  - a sentence noting a host tool's own security command as a complement, not a dependency

**Test first**:
- The RED is the gate itself. After creating the file and **before** Step 2, run
  `./scripts/check-contract.sh`
- It must fail on check 11 (self-hosting), check 13 (install checker roster), and check 18 (README
  reachability), each naming `security-review-rules`
- This is a genuine RED and it doubles as proof those three registration gates still fire. If any of
  them passes here, that gate has stopped working and is the more urgent finding

**Validation**:
- [Automated]: `./scripts/check-contract.sh` → fails, naming exactly checks 11, 13, 18. Checks 6 and 8
  must **pass**, which is what confirms the frontmatter is complete and no technology name slipped in
- [Manual]: re-read the category table against the OWASP source once, character by character on the
  identifiers and names. This read is the only verification name accuracy gets — see Key Decisions

---

### Step 2 — Register the unit

> **Prompt**: Implement Step 2 of `_work/shipped/owasp-security-review-rules/plan.md`. The reference at
> `skills/core/reference/security-review-rules/SKILL.md` exists but is unregistered, so
> `./scripts/check-contract.sh` currently fails on checks 11, 13, and 18. Register it in three places.
> Create the self-hosting symlink `.claude/skills/security-review-rules` pointing to
> `../../skills/core/reference/security-review-rules` — match the form of the existing entries in that
> directory exactly. Add `security-review-rules` to the `ROSTER_CORE` array in
> `scripts/check-install.sh`, keeping the array to one declaration since contract check 13 reads the
> first and bash uses the last. Add a linked row to the README's core reference table, in prose and not
> inside a fenced block, with the link written as
> `](skills/core/reference/security-review-rules/SKILL.md)`. Then run `./scripts/check-contract.sh` and
> confirm all checks pass, and run `tests/run.sh` and confirm 110/110.

**What to build**:
- `.claude/skills/security-review-rules` → `../../skills/core/reference/security-review-rules`
- `scripts/check-install.sh`: `security-review-rules` added to `ROSTER_CORE`
- `README.md`: a linked row in the core reference table describing what the unit knows

**Validation**:
- [Automated]: `./scripts/check-contract.sh` → all checks pass. Run with `--verbose` and confirm 11,
  13, and 18 each report ok by name — the three that were RED in Step 1
- [Automated]: `tests/run.sh` → 110/110 across 3 suites. The roster change touches the subject of the
  `install-check` suite, so this is not a formality
- [Manual]: `ls -l .claude/skills/security-review-rules` resolves rather than dangling. Check 11 treats
  a broken link as a distinct failure, and a dangling link reads as configured while failing every load

---

### Step 3 — Gate the revision being stated once

> **Prompt**: Implement Step 3 of `_work/shipped/owasp-security-review-rules/plan.md`. Add a new check to
> `scripts/check-contract.sh` enforcing AC5: the OWASP revision this increment pins is named in exactly
> one place across the repo's shipped files. Follow the authoring conventions of the checks already in
> that file — a `begin "<short description>"` call, `report_pass "$CURRENT"` or `report_fail "$CURRENT"`
> with an explanation and a remedy, and a comment above it saying what failure the check exists to
> prevent and how it can silently stop working. Read check 16 (around line 764) as the closest model:
> it guards a hardcoded value with a stated ceiling. The check must fail loudly with the offending files
> listed rather than passing quietly when it finds nothing to inspect. Verify it in both directions:
> confirm the gate passes on the current tree, then add a second mention of the revision year to another
> shipped file, confirm the gate fails and names that file, and revert. Record both observations in
> `_work/shipped/owasp-security-review-rules/assets/step3-validation-log.md`.

**What to build**:
- A new check in `scripts/check-contract.sh`, appended in the numbered sequence, with the file-header
  comment block updated if it enumerates check numbers by role
- `_work/shipped/owasp-security-review-rules/assets/step3-validation-log.md` recording the two-direction
  verification

**Test first**:
- Write the negative case **before** trusting the check: add a second mention of the revision year to a
  shipped file, run the gate, and confirm it fails naming that file
- Then revert and confirm it passes
- A gate observed only in its passing direction is indistinguishable from a gate that never fires. The
  roadmap records exactly this failure twice, in check 10's two under-matching patterns

**Validation**:
- [Automated]: `./scripts/check-contract.sh` → passes, with the new check reporting ok under
  `--verbose` and the total count risen by one
- [Automated]: with a second revision mention planted, the gate exits non-zero and names the file
- [Manual]: the validation log records both directions with the exact commands and output

---

### Step 4 — Gate the category table's shape

> **Prompt**: Implement Step 4 of `_work/shipped/owasp-security-review-rules/plan.md`. Add a second new check to
> `scripts/check-contract.sh` enforcing the checkable part of AC9: the category table in
> `skills/core/reference/security-review-rules/SKILL.md` is well-formed. **Read the Key Decisions
> section of the plan first** — this check deliberately does not verify that an identifier carries the
> right name in the pinned revision, because doing so requires a second copy of the list and AC5
> forbids one. What it does verify: the identifier sequence is complete and has no duplicates, every
> identifier is paired with exactly one name, and the number of rows matches the count the reference
> declares. Follow the same authoring conventions as Step 3, and say in the comment above the check
> what it cannot see, so a later reader does not mistake a pass for name verification. Verify in both
> directions: confirm it passes on the current table, then break the table three ways in turn — drop a
> row, duplicate an identifier, and change the declared count — confirming a distinct failure each time,
> and revert. Record all four observations in
> `_work/shipped/owasp-security-review-rules/assets/step4-validation-log.md`.

**What to build**:
- A second new check in `scripts/check-contract.sh`
- `_work/shipped/owasp-security-review-rules/assets/step4-validation-log.md`

**Test first**:
- Three negative cases, each planted and reverted in turn: a dropped row, a duplicated identifier, a
  declared count that no longer matches
- Each must produce a failure that names what is wrong, not a generic one. A gate that fails
  identically for three different defects sends the reader hunting

**Validation**:
- [Automated]: `./scripts/check-contract.sh` → passes, total count risen by one again
- [Automated]: each of the three planted breakages exits non-zero with a distinct message
- [Manual]: the comment above the check states plainly that name accuracy is out of its reach

---

### Step 5 — Make security findings carry a citation, and only security findings

> **Prompt**: Implement Step 5 of `_work/shipped/owasp-security-review-rules/plan.md`. This step tests before it
> edits, so **do the observation first**. Write two small planted changes and record the outcome you
> expect from each in
> `_work/shipped/owasp-security-review-rules/assets/step5-validation-log.md` *before* running anything. Case A:
> a change whose handler passes a visitor's search term straight into a data query — a security defect,
> which should be reported *with* its OWASP category by number and name. Case B: a change whose only
> defect is a helper named `doStuff`, with no security defect anywhere — the naming problem should be
> reported carrying **no** category. Run the quality reviewer over both now and confirm case A is RED:
> the defect is reported but no category is cited, because nothing yet instructs it to. Then amend
> `skills/core/reference/reviewer-discipline/agents/code-reviewer.md` — read spec FR2, FR3, and FR8
> first. In focus area 1 ("Secrets and security exposure"), point at the `security-review-rules`
> reference as guidance to consult, phrased as an instruction rather than a possibility, and state the
> citation convention: every security finding names its category by number and name alongside the file
> and line the evidence standard already requires, and a finding that is not a security defect carries
> no category. **Do not weaken the existing committed-secret rule** — it stays a Blocker requiring
> rotation and gains a citation on top. This file is L0, so check 8 applies: name no language,
> framework, or ORM. Re-run both cases and confirm case A now cites and case B still does not. Commit
> the planted diffs, the review output, and the log.

**What to build**:
- `skills/core/reference/reviewer-discipline/agents/code-reviewer.md`, modified in focus area 1: the
  pointer to the reference, and the citation convention including its restraint half
- `_work/shipped/owasp-security-review-rules/assets/step5-case-a-injection.md` — planted diff and both review
  runs
- `_work/shipped/owasp-security-review-rules/assets/step5-case-b-naming-only.md` — the same
- `_work/shipped/owasp-security-review-rules/assets/step5-validation-log.md`

**Test first**:
- Write both expected outcomes into the log **before** running the reviewer. Scoring a review after
  reading its output is how a marginal result becomes a pass
- Run both cases against the unmodified reviewer and confirm **case A is RED** — the defect reported,
  no category cited
- Case B has no available RED: before the edit nothing cites at all, so it passes for the wrong reason.
  Record that plainly rather than counting it as a pass. Its value is as a regression guard after the
  edit, when over-citation becomes possible for the first time

**Validation**:
- [Automated]: `./scripts/check-contract.sh` → all checks pass, check 8 included; an agent file is L0
- [Manual]: case A's finding names the category by number and name, with its file and line
- [Manual]: case B's naming finding carries no category. Over-citation is what teaches a reader to
  discount every citation, so this is the more important of the two after the edit
- [Manual]: re-read the committed-secret paragraph and confirm the rotation requirement is intact and
  unqualified. FR8 exists because additive edits to a Blocker rule are where force gets quietly lost

---

### Step 6 — Make a review name the areas it swept, and claim no more

> **Prompt**: Implement Step 6 of `_work/shipped/owasp-security-review-rules/plan.md`. Same shape as Step 5 —
> observe first, then edit. Write two planted changes and record the expected outcome of each in
> `_work/shipped/owasp-security-review-rules/assets/step6-validation-log.md` before running anything. Case C: a
> change adding a contact form that validates every submitted field and stores no credentials — security-
> relevant code with no security defect, so the review should name the security areas it checked and
> found clean. Case D: a change that only renames a variable and reflows a comment — no security-relevant
> code at all, so the review must name **no** security areas and must not state the change was reviewed
> against the standard. Run the quality reviewer over both and confirm case C is RED: no security areas
> are named in the `Clean` section, because nothing yet instructs it to name them. Then amend
> `skills/core/reference/reviewer-discipline/agents/code-reviewer.md` with the `Clean` section
> instruction from spec FR4 — name the security areas checked and found clean, and claim no coverage for
> areas the change had no relevant code for. **Do not touch
> `skills/core/reference/reviewer-discipline/SKILL.md`**: the `Clean` section is defined by the shared
> contract, but naming OWASP areas is one reviewer's domain, and putting the instruction in the contract
> would hand it to all three reviewers. See the plan's Key Decisions. Re-run both cases and confirm case
> C now names areas and case D still names none.

**What to build**:
- `skills/core/reference/reviewer-discipline/agents/code-reviewer.md`, modified once more: the `Clean`
  section instruction and its restraint half
- `_work/shipped/owasp-security-review-rules/assets/step6-case-c-clean-with-security-code.md`
- `_work/shipped/owasp-security-review-rules/assets/step6-case-d-no-security-code.md`
- `_work/shipped/owasp-security-review-rules/assets/step6-validation-log.md`

**Test first**:
- Both expected outcomes written into the log before the reviewer runs
- Run both against the reviewer as Step 5 left it and confirm **case C is RED** — no security areas
  named
- Case D, like case B, has no available RED, and for the same reason. Record that; its value begins
  after the edit, when a false coverage claim becomes possible

**Validation**:
- [Automated]: `./scripts/check-contract.sh` → all checks pass
- [Manual]: case C's `Clean` section names the security areas checked, and they are areas the diff
  actually contained code for
- [Manual]: case D claims no security coverage whatsoever. This is the dishonesty case and no gate in
  the repo can see it — it is the single reason this step exists rather than being folded into Step 5
- [Manual]: `git diff --stat` does not list `reviewer-discipline/SKILL.md`

---

### Step 7 — Record the change for consumers

> **Prompt**: Implement Step 7 of `_work/shipped/owasp-security-review-rules/plan.md`. Add a `CHANGELOG.md`
> entry under `## [Unreleased]`, written so it reads as "what will change in my project when I update"
> — a consuming project gains a security reference its quality reviewer consults, and security findings
> start carrying an OWASP category. Match the density and voice of the entries already there. Then add a
> sentence to the "Code review and its guardrails" section of `docs/concepts.md` noting that security
> findings are cited to the standard, keeping it to a sentence. Then update `docs/spell-cards.md`: add
> a card for `security-review-rules` in the core reference section, matching the field structure the
> sibling cards use, and correct the two stated counts — "Seven opinions the toolkit holds" becomes
> eight, and "16 spells and 17 references, 33 in all" becomes 18 references and 34 in all. Verify both
> numbers by counting rather than by arithmetic. **Name no year in any of these three files.** Check 19
> enforces that the pinned revision appears once across shipped files, and its scope covers `skills/`
> and `agents/` only, so `CHANGELOG.md`, `docs/concepts.md`, and `docs/spell-cards.md` are all outside
> what the gate can see. Then run `./scripts/check-contract.sh` and `tests/run.sh`.

**What to build**:
- `CHANGELOG.md`: an entry under `## [Unreleased]`
- `docs/concepts.md`: one sentence in the code-review section
- `docs/spell-cards.md`: a card for `security-review-rules`, plus the two corrected counts

**Validation**:
- [Automated]: `./scripts/check-contract.sh` → passes; `tests/run.sh` → 110/110
- [Automated]: `find skills -name SKILL.md | wc -l` matches the deck's stated total, and
  `grep -c '^### ' docs/spell-cards.md` matches it too. Both were wrong before this step, so a
  passing count is the evidence the step worked
- [Manual]: the changelog entry names the observable change for a consumer, not the increment's
  internal argument
- [Manual]: none of the three files names the pinned revision year, since check 19 cannot see them

---

### Final — Record the durable behavior *(a spell you cast, not an implement-step)*

**Do not number this as an implementation step.** It is cast directly after the implement-step loop
finishes.

> **Prompt**: Run `/feature update code-review`. Fold **only** the user- or operator-observable
> behavior changes from this work into the existing capability doc — do not create a new feature doc.
> The observable changes are: a security finding names its OWASP category; a review names the security
> areas it swept and found clean; a finding that is not a security defect carries no category; a
> committed secret keeps its rotation requirement and gains a citation. Leave the point-in-time criteria
> in the shipped spec — the five registration gates, the two new checks, the roster and README
> registrations, and the reviewer count staying three are all transitions or architecture, and must not
> appear as Rules. Add the increment to the doc's Increments list with today's date, pointing at
> `_work/shipped/owasp-security-review-rules/spec.md`. Add a revision note dated today.
>
> **Validation**: The capability doc describes current behavior with no transition-style ("goes from…
> to…") Rules; no new feature doc was added; the Increments list gained one checked row.

---

## File Summary

| Action | File |
|--------|------|
| Create | `skills/core/reference/security-review-rules/SKILL.md` |
| Create | `.claude/skills/security-review-rules` (symlink) |
| Modify | `scripts/check-install.sh` (`ROSTER_CORE`) |
| Modify | `README.md` (core reference table row) |
| Modify | `scripts/check-contract.sh` (two new checks) |
| Modify | `skills/core/reference/reviewer-discipline/agents/code-reviewer.md` |
| Modify | `CHANGELOG.md` |
| Modify | `docs/concepts.md` |
| Modify | `docs/spell-cards.md` (card for the new unit, plus the two stated counts) |
| Create | `_work/shipped/owasp-security-review-rules/assets/step3-validation-log.md` |
| Create | `_work/shipped/owasp-security-review-rules/assets/step4-validation-log.md` |
| Create | `_work/shipped/owasp-security-review-rules/assets/step5-case-a-injection.md` |
| Create | `_work/shipped/owasp-security-review-rules/assets/step5-case-b-naming-only.md` |
| Create | `_work/shipped/owasp-security-review-rules/assets/step5-validation-log.md` |
| Create | `_work/shipped/owasp-security-review-rules/assets/step6-case-c-clean-with-security-code.md` |
| Create | `_work/shipped/owasp-security-review-rules/assets/step6-case-d-no-security-code.md` |
| Create | `_work/shipped/owasp-security-review-rules/assets/step6-validation-log.md` |
| _(work type: `change-to code-review`)_ Update | `_features/code-review.md` (fold observable behavior only; **no new file**) |
