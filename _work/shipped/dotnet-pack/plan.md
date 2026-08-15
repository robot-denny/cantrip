# Plan: .NET Guidance Pack and Its Core Dependencies

**Spec**: `_work/shipped/dotnet-pack/spec.md`
**Branch**: dotnet-pack
**Work type**: new-capability
**Feature doc**: dotnet-guidance

## Prerequisite landed — what the pack must reference

The blocker that stood here is cleared. `review-failure-modes` merged as PR #2 and is archived at
`_work/shipped/review-failure-modes/`. Its outcome differs from what this plan assumed, in three ways
that change how the pack units are written.

**Two failure modes moved into core, not three.** Cancellation was already owned by the performance
reviewer, so it never moved. Wherever this plan or the spec says "three", read two.

**Where they landed, since the pack must name the C# form without restating the reason:**

| What | Where |
|---|---|
| An error passed onward with its origin no longer recorded anywhere | `agents/code-reviewer.md` §2 |
| A log call that folds its values into the message text | `agents/code-reviewer.md` §2 |
| Cancellation ownership, and the merged-report reasoning | `reviewer-discipline/SKILL.md` → *Where two domains abut* |

That answers the open question this note flagged: the two checks are domain findings and sit in the
agent; the ownership fact is about the boundary between reviewers and sits in the shared contract. The
pack references the agent's entries.

**Both core entries carry an exemption clause, and the pack must not contradict them.** The lost-origin
entry exempts a deliberately sanitized external response so long as the origin survives internally. The
log entry exempts a message carrying no values, and routes a value that should not be logged at all to
the sensitive-data rule, where the fix is removal rather than relocation. A pack entry that tells a
reviewer to move a credential into a named field would contradict core.

**Cancellation is scoped to outbound and I/O-bound work.** The boundary statement was narrowed during
review because the performance checklist only operationalizes cancellation for outbound and stream cases,
and a wider grant created a gap. The pack's own cancellation content still stands — all three reviewers
consult stack-pack guidance, so `dotnet-review-rules` supplies the C# idiom and the performance reviewer
picks it up.

**Two gaps are recorded and unowned** in `_work/shipped/review-failure-modes/spec.md`: the allocation
cost of building an interpolated log message, and cancellation on local long-running work. The pack
should not quietly claim either — each earns its own evidence.

**Unaffected, so do not re-litigate**: the resolution order, the slot mechanics, both validated
descriptions, and Steps 1 and 3–6.

**One thing Step 1 now inherits.** `scripts/check-contract.sh` gained a `.diff` scan fix in the merged
work, in both the git and non-git file lists. Step 1 edits the same file — build on that rather than
reverting it, and if the pack commits eval fixtures as `.diff`, they are now scanned.

---

## Context

The toolkit ships no per-file .NET guidance. This increment adds an opt-in L1 pack of two reference
units — one for authoring C#, one for reviewing a C# diff — plus one core change it enables: an optional
detection line in the slot convention that lets a pack tell `/setup` how a project's own answer can be
read rather than asked for.

**A prerequisite increment must land first.** Three language-agnostic failure modes go into core's
`code-reviewer` separately, because they improve review in any language with no pack installed. The pack's
review guidance names the C# form of defects core describes, so its wording follows theirs. See the spec's
*Depends on a separate increment*.

Everything is markdown. There is no build, no compile step, and the only mechanical checks are
`scripts/check-contract.sh` (14 checks, enforced by `.githooks/pre-commit`) and `tests/run.sh`
(fixture runner for `check-install.sh`). The decisions, the review of the source material, the rejected
alternatives, and measured trigger-eval results are all in `_work/shipped/dotnet-pack/discovery.md` — read it
before Step 2, since it is the substance the pack units are written from.

**Unit of work**: one skill unit, or one core file, plus whatever mechanical check proves it. The
`conventions.md → ## Unit of work` slot is empty (this repo has no `.agents/config/`), and the repo's own
history works this way — one commit per extracted unit with its gate compliance.

---

## Key Decisions

- **Two pack units, not one or three.** Authoring and review load at different times; a single unit makes
  every review pay for the authoring half. A third `dotnet-starter-facts` is deliberately not created —
  language-spec truths are not version-volatile the way CMS behavior is, so version scoping stays inline
  until the conditional set earns a file. (`discovery.md` §3)
- **The pack asserts platform defaults and yields.** Resolution order, stated once in
  `dotnet-conventions`: editor config → a recorded project decision → the pack's default → the
  surrounding file's dominant style. Without this the asserted half becomes a contradiction machine.
  (`discovery.md` §4)
- **The pack declares its own slot heading**, `conventions.md → ## .NET style decisions`, rather than
  reusing `## Implementation rules`. That heading is owned by `/implement-step`, and gate check 9 forces
  an identical fallback for a repeated slot line — `/implement-step`'s wording is authoring-shaped and
  meaningless to a reviewer. Both consumers reach the new heading through the pack skill instead.
  (`discovery.md` §4)
- **Core takes the failure mode; the pack takes the idiom.** Delivered by the prerequisite increment, not
  here. Recorded because it governs how this pack is worded: the pack names the C# form and does not
  restate why the defect matters. (`discovery.md` §9a)
- **`dotnet-hygiene.md` stays in the CMS pack.** It is Pillar 1 of a seven-pillar scored audit whose
  anchors live in `scoring-rubric.md`; moving it splits a pillar's signals from its anchors across two
  packs. The overlap is resolved by ownership instead. (`discovery.md` §5)
- **No new gate check for the detection line.** It is optional by design, so there is nothing to pair it
  with the way check 4 pairs `**Slot:**` with `**If empty:**`. The spec raises the risk that an
  unenforced mechanism quietly stops being used; the mitigation is the ADR plus `/setup`'s own
  instruction, and the risk is recorded in the feature doc's parking lot rather than solved with
  machinery. Revisit if a second pack declines to declare one.
- **Commands, all inferred — the `stack.md` slots are empty because this repo has no `.agents/config/`.**
  Gate: `scripts/check-contract.sh`. Fixture tests: `tests/run.sh [case]`. Install survey:
  `scripts/check-install.sh`. There is no build command; the deliverable is markdown. Worth recording in
  a `stack.md` slot if this repo ever grows one.
- **The content check is run by hand, not in CI.** An eval that needs a model run is nondeterministic and
  costs money, which does not fit a test harness whose stated virtue is dependency-free bash. Eval cases
  are committed as `evals/evals.json` following the `architecture-audit` precedent — a committed
  *definition*, not a runner.
- **Gate the pack roster (Step 1).** `check-install.sh` carries `ROSTER_PACK` and `PACK_SLOTS` separately
  from core, and neither is gated. `ROSTER_PACK` lists 2 of the CMS pack's 8 units and has already
  drifted. Since an unlisted pack unit installs and verifies as though absent, extending check 13 to
  cover pack rosters comes first — it then *forces* Steps 2 and 3 to register their own units instead of
  relying on anyone remembering.

---

## Steps

Each step is designed to be completed independently in its own context window.
The step heading contains a ready-to-use prompt you can paste into a new session.

---

### Step 1 — Gate the pack roster, and fix the drift it exposes

> **Prompt**: Implement Step 1 of `_work/shipped/dotnet-pack/plan.md`. In `scripts/check-contract.sh`, extend
> check 13 so it compares `check-install.sh`'s `ROSTER_PACK` against the skills that actually exist
> under `skills/` outside `skills/core/`, the same way it already compares `ROSTER_CORE` against
> `skills/core/`. Run `scripts/check-contract.sh` and confirm it now FAILS, naming the CMS pack units
> missing from the roster. Then add those missing unit names to `ROSTER_PACK` in
> `scripts/check-install.sh` so the check passes. Do not add any `dotnet-*` unit yet — those arrive in
> Steps 2 and 3, and the gate failing for them is the intended forcing function. Finish with
> `scripts/check-contract.sh` green and `tests/run.sh` still green.

**What to build**:
- `scripts/check-contract.sh` — extend check 13 to cover the pack roster alongside the core roster.
  Report missing and stale entries separately, matching the existing message shape.
- `scripts/check-install.sh` — add the CMS pack units absent from `ROSTER_PACK`. **Measured at planning
  time: 8 pack units exist, `ROSTER_PACK` lists 2, so exactly these six are missing** —
  `architecture-audit`, `block`, `check-uda`, `umbraco-17-review-rules`, `umbraco-17-starter-facts`,
  `umbraco-edit`. There are no stale entries. Re-derive from the failure output anyway; if the count
  differs, something changed since this plan was written and that is worth knowing before proceeding.

**Test first**:
- Extend check 13 **before** touching the roster, and run `scripts/check-contract.sh`
- It should fail, naming each pack unit present in `skills/` but absent from `ROSTER_PACK`
- Confirm RED before adding roster entries. If it passes immediately, the check is not comparing what it
  claims to and the step is not done

**Validation**:
- [Automated]: `scripts/check-contract.sh` — 14 checks pass (check 13 now covers both rosters)
- [Automated]: `tests/run.sh` — every fixture case still passes; the roster change must not alter what
  `check-install.sh` reports for a core-only install
- [Manual]: run `scripts/check-install.sh --verbose` in this repo and confirm the pack units are now
  listed as wired rather than silently absent

---

### Step 2 — The authoring unit: `dotnet-conventions`

> **Prompt**: Implement Step 2 of `_work/shipped/dotnet-pack/plan.md`. Read `_work/shipped/dotnet-pack/discovery.md`
> first — §1 has the reviewed source material bucketed, §2 the namespace correction, §4 the resolution
> order and slot mechanics, §5 the dividing line against the audit pack, §6 the validated description.
> Create `skills/dotnet/reference/dotnet-conventions/SKILL.md` using the description in §6 verbatim; it
> is already trigger-evaluated and must not be retuned. Register the unit in `ROSTER_PACK` and add
> `conventions.md|.NET style decisions|dotnet-conventions` to `PACK_SLOTS` in
> `scripts/check-install.sh`. Finish with `scripts/check-contract.sh` green.

**What to build**:
- `skills/dotnet/reference/dotnet-conventions/SKILL.md` containing:
  - The **asserted defaults** (`discovery.md` §1 bucket A) — written why-first, not as caps-lock
    imperatives. Include the worked before/after examples for the four rules whose wrong form is
    plausible: structured logging, log-and-rethrow, collection expressions, paired JSON attributes.
  - The **resolution order** (§4), stated once, making clear the asserted items are defaults that yield.
  - **One** consolidated "what the project decides" list (§1 bucket B) naming each contested item and
    asserting no answer for any.
  - The `**Slot:**` / `**If empty:**` / `**Detect:**` declaration for
    `conventions.md → ## .NET style decisions`.
  - The **dividing line** against `architecture-audit` (§5) — repo-level signals there, per-file
    guidance here — plus a pointer that where an `.editorconfig` speaks it is the authority.
  - The **nine defects** from §1 fixed rather than carried: no `.GetAwaiter().GetResult()` claim, no
    public-fields row, `IsNullOrWhiteSpace` as a default with its exception, one *public* type per file,
    the `s_` prefix as project-owned, corrected arrows.
- `scripts/check-install.sh` — add `dotnet-conventions` to `ROSTER_PACK`; add the pack-slot entry.

**Test first**:
- The mechanical assertions come from the gate, and Step 1 made the roster one of them. Before writing
  the body, create the directory with frontmatter only and run `scripts/check-contract.sh`
- Expect failures naming: the unit missing from `ROSTER_PACK` (check 13, from Step 1), and — if the
  frontmatter is wrong — a name/directory mismatch or a too-thin description (check 6)
- Confirm RED, then satisfy each. A `**Slot:**` without an adjacent `**If empty:**` fails check 4, so
  write the pair together

**Validation**:
- [Automated]: `scripts/check-contract.sh` — all checks pass, including 4 (slot paired), 5 (a
  `reference/` unit sets no model-invocation suppression), 6 (name matches directory, description long
  enough), 9 (no conflicting fallback for a repeated slot), 13 (roster current)
- [Automated]: `tests/run.sh` — still green
- [Manual]: confirm the contested list asserts no answers, and that the resolution order appears exactly
  once in the pack rather than being restated in the review unit

---

### Step 3 — The review unit: `dotnet-review-rules`, with its eval cases

> **Prompt**: Implement Step 3 of `_work/shipped/dotnet-pack/plan.md`. Create
> `skills/dotnet/reference/dotnet-review-rules/SKILL.md` using the validated description from
> `_work/shipped/dotnet-pack/discovery.md` §6 verbatim. Write `evals/evals.json` **first**, following the shape
> of `skills/umbraco-17/reference/architecture-audit/evals/evals.json`, with one case per planted defect
> from the spec's acceptance criteria. Run those cases against the pack before writing the body and
> record that the defects are **not** reported. Then write the body: what to look for, mapped onto the
> existing Blocker/Major/Minor/Nit scale, deferring to `dotnet-conventions` for the contested list and
> for why each rule is true rather than restating either. Register the unit in `ROSTER_PACK`. Finish with
> `scripts/check-contract.sh` green.

**What to build**:
- `skills/dotnet/reference/dotnet-review-rules/SKILL.md` — the review checklist, severities mapped onto
  the shared scale, explicitly deferring to `dotnet-conventions` for the project-owned list and to
  `reviewer-discipline` for scope, evidence, and report structure.
- `skills/dotnet/reference/dotnet-review-rules/evals/evals.json` — cases for: a rethrow that discards the
  stack trace, an interpolated log message, a missing cancellation path, an unvalidated payload at a
  boundary, and one case asserting **no** finding is raised against a style the project's editor config
  has chosen.
- `scripts/check-install.sh` — add `dotnet-review-rules` to `ROSTER_PACK`.

**Test first**:
- Write `evals/evals.json` before the body. Each case names the planted defect and the finding expected
- Run the cases against a diff carrying those defects, with the pack's body still absent or stubbed
- Confirm RED: the defects go unreported, or are reported without the severity and reasoning the pack is
  meant to add. Capture the output — this is the only evidence that the body did the work
- Keep the negative case in the same file: a project whose editor config chose a non-default style must
  draw **no** finding. A review unit that only ever adds findings will happily fight a project's
  `.editorconfig`

**Validation**:
- [Automated]: `scripts/check-contract.sh` and `tests/run.sh` — both green
- [Manual]: the recorded before/after eval output, including the negative case
- [Manual]: confirm the unit restates neither the contested list nor the resolution order — a second copy
  is the drift the one-place rule exists to prevent

---

### Step 4 — The detection line: contract, then `/setup`

> **Prompt**: Implement Step 4 of `_work/shipped/dotnet-pack/plan.md`. Document the optional `**Detect:**` line
> in `docs/contract.md`'s reference-pattern section: what it is for, that it is optional, and that it
> carries a detection recipe a pack owns because core may not name a technology. Then add one sentence to
> Step 2 of `skills/core/spellbook/setup/SKILL.md` telling it to honor a pack's `**Detect:**` before
> asking, and one technology-agnostic row to its Step 1 detection table — that where a formatter or
> editor config encodes mechanical style, it is authoritative where it speaks. Keep every word free of
> technology names. Finish with `scripts/check-contract.sh` green.

**What to build**:
- `docs/contract.md` — a short subsection under the reference pattern covering the optional third line,
  and why the recipe cannot live in core.
- `skills/core/spellbook/setup/SKILL.md` — one sentence in Step 2's pack-slot paragraph; one row in Step
  1's detection table.

**Test first**:
- The behavior is FR6: an observable answer gets proposed rather than asked. The manual check, written
  down before editing: run configuration against a repo whose declaration style is visibly uniform, and
  record whether the style answer is **asked** (RED) or **proposed from what the repo shows** (GREEN)
- Step 2 must already exist for this to be exercisable, since the recipe lives in the pack. If Step 2 is
  not done, stop and do it first rather than testing the mechanism against nothing

**Validation**:
- [Automated]: `scripts/check-contract.sh` — check 8 must pass. `.editorconfig` is cross-language and not
  a technology name, but a slip into `.cs` or `dotnet` here fails the gate
- [Automated]: confirm check 4 still passes — a `**Detect:**` line sits outside the `**Slot:**` /
  `**If empty:**` pairing and must not break its three-line window
- [Manual]: the recorded asked-versus-proposed result

---

### Step 5 — The CMS pack defers its general async rule

> **Prompt**: Implement Step 5 of `_work/shipped/dotnet-pack/plan.md`. In
> `skills/umbraco-17/reference/umbraco-17-review-rules/SKILL.md`, narrow the bullet about long-running
> outbound calls so it keeps only the CMS-specific instance — form submission handlers — and defers the
> general async, cancellation, and timeout rule to the .NET pack's review guidance without naming that
> pack's file path. State what still applies when the .NET pack is absent, so a CMS-only install loses
> nothing. Finish with `scripts/check-contract.sh` green.

**What to build**:
- `skills/umbraco-17/reference/umbraco-17-review-rules/SKILL.md` — narrow the general rule to its CMS
  instance and defer the rest. This edits an already-shipped pack, so it is a change rather than an
  addition and the changelog must say so in Step 7.

**Test first**:
- The behavior is FR7's second half: the rule appears **once**. Add the double-reporting case to
  `dotnet-review-rules`'s `evals/evals.json` from Step 4, or record it as a manual check
- Before the edit, run a review of a change with a synchronous uncancellable outbound call in a project
  with both packs, and record whether the finding appears twice (RED)
- After the edit, the same review reports it once (GREEN)

**Validation**:
- [Automated]: `scripts/check-contract.sh` — green
- [Manual]: the recorded once-versus-twice result
- [Manual]: read the narrowed bullet as though the .NET pack were absent, and confirm a CMS-only install
  still has actionable guidance

---

### Step 6 — Documentation: README, changelog, ADR

> **Prompt**: Implement Step 6 of `_work/shipped/dotnet-pack/plan.md`. In `README.md`: add the install command
> for the new pack alongside the CMS one, add its two units to the reference list, and correct the claim
> that "a stack pack adds its own spells on top" — this pack adds only references, which that sentence
> currently makes impossible. In `CHANGELOG.md`: record the pack as an addition, and the
> `umbraco-17-review-rules` narrowing plus the core `code-reviewer` additions as changes. Add an ADR
> as `adr/0014-dotnet-pack-and-the-detection-line.md` covering both decisions — why `dotnet` is a peer of `umbraco-17` rather than inside it, and
> why the slot convention gained an optional detection line — following the format of the existing ADRs
> and `adr/_template.md`. Finish with `scripts/check-contract.sh` green.

**What to build**:
- `README.md` — install command, the two units in the references list, and the spells-only claim fixed.
- `CHANGELOG.md` — the addition and the two changes, kept distinct. The README line is load-bearing
  rather than cosmetic: adding a pack is a manual install, so this is the only thing that tells an
  existing project the pack exists.
- `adr/0014-dotnet-pack-and-the-detection-line.md` — one record covering both decisions, with the
  alternatives that were rejected and why, per the existing ADRs' shape. 0014 is the next free number;
  0013 is the most recent.

**Test first**:
- Not a behavior change, so no RED→GREEN. The one check that matters is that the documented command
  actually works: run the README's install command against a scratch directory and confirm it installs
  the two units, rather than assuming the path is right

**Validation**:
- [Automated]: `scripts/check-contract.sh` — green. Check 12 pairs a declared companion against the
  README; this pack declares none, so nothing new is expected there
- [Manual]: the README's install command run for real, and its output showing both units
- [Manual]: read the changelog entry as someone already running the CMS pack, and confirm it tells them
  both what is new and what changed under them

---

### Final — Record the durable behavior *(a spell you cast, not an implement-step)*

**Do not number this as an implementation step.** It is cast directly after the implement-step loop
finishes. Numbering it would invite `/implement-step <plan> N`, which dispatches a code worker to run a
spell — the wrong mechanism, and it blurs the boundary between building and recording.

> **Prompt**: Run `/feature update dotnet-guidance` to verify the living behavioral doc reflects the
> actual implementation. Review each scenario against the code and test results. Update any scenario
> where the implementation diverged from the draft. Fill in the test coverage table with real test paths
> and line numbers, or mark target tests pending if no harness exists yet. Remove the "Draft" banner.
> Commit the verified doc.
>
> **Validation**: Every scenario matches observable behavior; the coverage table has no unexpected "Not
> covered" gaps.

Two specifics for this increment. Most scenarios are proven by a recorded manual check rather than an
automated test, so the coverage table should cite the step whose evidence covers each rather than
claiming a test file that does not exist. And the doc's parking lot already carries the backfill flag
plus the unenforced-detection-line risk — keep both rather than tidying them away.

---

## File Summary

| Action | File |
|--------|------|
| Modify | `scripts/check-contract.sh` (check 13 covers the pack roster) |
| Modify | `scripts/check-install.sh` (`ROSTER_PACK` drift fix, then the two new units; one `PACK_SLOTS` entry) |
| Create | `skills/dotnet/reference/dotnet-conventions/SKILL.md` |
| Create | `skills/dotnet/reference/dotnet-review-rules/SKILL.md` |
| Create | `skills/dotnet/reference/dotnet-review-rules/evals/evals.json` |
| Modify | `docs/contract.md` |
| Modify | `skills/core/spellbook/setup/SKILL.md` |
| Modify | `skills/umbraco-17/reference/umbraco-17-review-rules/SKILL.md` |
| Modify | `README.md` |
| Modify | `CHANGELOG.md` |
| Create | `adr/0014-dotnet-pack-and-the-detection-line.md` |
| _(work type: `new-capability`)_ Update | `_features/dotnet-guidance.md` — verify the draft, remove the banner |

---

## Sequencing notes

**Step 4 is the only L0 change left here**, and it affects every install rather than only adopters. Commit
it separately from the pack so it stays independently reviewable and revertible. **Step 5 edits an
already-shipped pack**, so it is a change rather than an addition — that distinction has to survive into
the changelog.

**Step 1 first is deliberate.** It creates the forcing function that makes Steps 2 and 3 register their
own units. Without it, the roster stays a list someone has to remember, which is how it drifted for core
and how it is drifting for packs right now.

**Step 2 before Step 4.** The detection mechanism cannot be exercised until a pack declares one, which
was also the reason for judging it against a real declaration rather than in the abstract.

**The spec's first open question is settled** (2026-08-13): the generalized failure modes were split into
their own increment by dependency direction, and the detection line stayed here. That is why this plan has
six steps rather than seven.
