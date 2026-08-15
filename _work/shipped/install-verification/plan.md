# Plan: Install Verification

**Spec**: `_work/shipped/install-verification/spec.md`
**Branch**: `feature/install-verification`
**Work type**: new-capability — copied verbatim from the spec's `**Work type**:` line; this decides how
the final step records behavior (see Step 4)

## Context

A consumer who installs the toolkit cannot tell whether it landed usably. The installer reports that
files were written, which is not the same claim. Three states are silently indistinguishable after a
"successful" install: partial installs, skills whose bundled assets are missing, and unregistered
reviewer agents that quietly degrade review.

This adds `scripts/check-install.sh` — the consumer-facing counterpart to `check-contract.sh`, which
guards this repo. It builds on the layout knowledge established in ADR 0004: three install layouts are
valid, and the only layout-independent path into a skill's assets is through `.claude/skills/`.

The unit of work is a single shell script plus its fixtures, so there are no layers to sequence beyond
test-then-implement.

---

## Key Decisions

- **A script, not a spell.** Resolves the spec's first open question. A script runs in a pipeline with
  no agent present, which is where install verification is most useful, and the Checkpoint C census
  argued against a tenth spell absent evidence. If reading the output later proves to need explaining,
  a spell can wrap the script — the reverse is not true.
- **Expected skills are discovered, not hardcoded or read from the lockfile.** Deriving from
  `skills-lock.json` fails for a hand-vendored install (a spec edge case), and hardcoding drifts as the
  toolkit grows. The script instead enumerates what is installed and verifies each unit it finds is
  *whole* — which catches the real failure (a broken unit) without needing to know the full roster. A
  missing-skill check then compares against the lockfile only when one exists, as a bonus rather than a
  prerequisite.
- **Assets are verified by reading, never by listing** (FR2). `test -r` through the `.claude/skills/`
  path, because that path exists under all three layouts while `.agents/` does not. This is the same
  reference-by-skill-path rule ADR 0004 settled for spells.
- **Three outcome classes, and exit code follows severity, not count** (FR4, FR7). Degraded exits zero.
  This is the decision that makes the script safe to put in a pipeline, and getting it backwards would
  make every core-only install look like a failure.
- **Test convention established here, flagged as new.** The `stack.md → ## Tests` slot is empty and the
  repo has **no tests at all** — `check-contract.sh` has only ever been checked by ad-hoc manual
  probing. Proposing `tests/install-check/` with one fixture directory per scenario, plus
  `tests/run.sh` as the runner. This is a new convention for this repo, established by this increment.
- **Build and test commands, inferred because the slot is empty**: there is no build system; the gate is
  `./scripts/check-contract.sh`, syntax checking is `bash -n`, and the new suite is `tests/run.sh`.
- **Structural requirement evident from the codebase** (the *Planning gotchas* slot is empty, so this is
  observation, not an invented rule): scripts must be executable and the pre-commit hook runs the
  contract gate, so a non-executable script or a gate failure blocks the commit.

---

## Steps

Each step is designed to be completed independently in its own context window.
The step heading contains a ready-to-use prompt you can paste into a new session.

---

### Step 1 — Test harness and fixtures (RED apparatus)

> **Prompt**: Implement Step 1 of `_work/shipped/install-verification/plan.md`. Create `tests/run.sh`, a
> dependency-free bash runner that executes each `tests/install-check/<case>/` fixture and compares
> `scripts/check-install.sh`'s actual exit code and output against the case's expectations. Create
> fixture directories for these cases: `canonical-complete`, `source-symlinked-complete`,
> `copied-complete`, `missing-skill`, `missing-template`, `dangling-symlink`, `agents-unlinked`,
> `no-config`, `no-lockfile`, `foreign-units`. Each fixture is a minimal fake project tree — a few
> `.claude/skills/<name>/SKILL.md` files is enough, not the real toolkit. Each carries an
> `expect` file declaring the expected exit code and one or more substrings the output must contain.
> Do **not** create `scripts/check-install.sh` yet. Run `tests/run.sh` and confirm every case fails
> because the script is absent — that is the RED state this step is establishing.

**What to build**: `tests/run.sh` (executable), `tests/install-check/<case>/` for the ten cases above,
each with a fixture tree and an `expect` file. A short `tests/README.md` stating the convention, since
this is the repo's first test harness.

**Test first**: this step *is* the test apparatus. The RED signal is every case failing for the right
reason — script absent, not fixture malformed. Confirm the distinction by reading one failure message.

**Validation**:
- [Automated]: `bash -n tests/run.sh` passes; `tests/run.sh` runs and reports 10 cases, all failing.
- [Automated]: `./scripts/check-contract.sh` still passes — fixtures live outside shipped units, so
  they must not trip any check.
- [Manual]: read one failure and confirm it names a missing script rather than a broken fixture.

---

### Step 2 — Skill presence and asset resolution

> **Prompt**: Implement Step 2 of `_work/shipped/install-verification/plan.md`. Create
> `scripts/check-install.sh`, following the structure of `scripts/check-contract.sh` — numbered checks,
> `report_*` helpers, a summary line, meaningful exit code. Implement only the skill-and-asset checks
> for now: enumerate installed toolkit units under `.claude/skills/`, and for each verify `SKILL.md` is
> **readable** (not merely present), that its frontmatter has `name` and `description`, and that any
> `templates/` or `agents/` assets it declares are readable. Read through the `.claude/skills/` path
> only — never `.agents/` — since that is the sole layout-independent route (ADR 0004). Report a
> dangling symlink as broken, not present. If `skills-lock.json` exists, additionally report any skill
> it lists that is absent; if it does not, skip that comparison without complaint. Make the four
> complete-install and broken-install fixtures pass: `canonical-complete`,
> `source-symlinked-complete`, `copied-complete`, `missing-skill`, `missing-template`,
> `dangling-symlink`.

**What to build**: `scripts/check-install.sh` with the presence and asset checks, executable.

**Test first**: the fixtures from Step 1 are already RED. Implement until those six go GREEN; do not
touch the other four cases yet.

**Validation**:
- [Automated]: `tests/run.sh` — the six named cases pass, the remaining four still fail.
- [Automated]: `bash -n scripts/check-install.sh`; `./scripts/check-contract.sh` passes.
- [Manual]: run `scripts/check-install.sh` in this repo, which is a real source-symlinked install, and
  confirm it reports all 13 skills present.

---

### Step 3 — Degraded versus broken, and the reviewer agents

> **Prompt**: Implement Step 3 of `_work/shipped/install-verification/plan.md`. Add the three-class outcome
> model to `scripts/check-install.sh`: wired, degraded, broken. Reviewer agents that are not registered
> in `.claude/agents/` are **degraded** — review still runs inline — so they must be reported as
> working-but-degraded, must name the exact linking command from the README as the fix, and must **not**
> affect the exit code. Reviewer agent files that are present but unreadable are **broken**. Every
> degraded or broken finding must name the specific command or file that resolves it (FR6). Make the
> `agents-unlinked` fixture pass.

**What to build**: the outcome classification, the reviewer-agent check, and fix-text on every non-wired
finding.

**Test first**: `agents-unlinked` is RED and asserts exit code zero — the assertion most likely to be
implemented backwards. Confirm it fails on the exit code before implementing, so the GREEN is meaningful.

**Validation**:
- [Automated]: `tests/run.sh` — seven cases pass. `agents-unlinked` exits **zero**.
- [Manual]: temporarily move `.claude/agents/` aside in this repo, run the script, confirm it reports
  degraded and exits zero, then restore.

---

### Step 4 — Slot reporting, pack tolerance, and foreign-unit isolation

> **Prompt**: Implement Step 4 of `_work/shipped/install-verification/plan.md`. Add slot reporting to
> `scripts/check-install.sh`: for each slot the toolkit reads — the headings under
> `.agents/config/paths.md`, `stack.md`, `conventions.md`, and the `reviewer-rules/` files — report
> filled or empty. Treat a missing file and a file lacking that heading identically. State explicitly
> in the output that an all-empty configuration is a **working** configuration, and do not let empty
> slots affect the exit code (FR5). An absent stack pack must produce no finding at all (FR8). Skills
> and agents that are not the toolkit's own must not appear in the report (AC8). Make the `no-config`,
> `no-lockfile`, and `foreign-units` fixtures pass.

**What to build**: the slot survey, pack tolerance, and a filter restricting the report to toolkit-owned
units.

**Test first**: `no-config` asserts exit zero with every slot empty — the fresh-install case that must
never read as failure. `foreign-units` asserts the report stays silent about a project's own skills.

**Validation**:
- [Automated]: `tests/run.sh` — all ten cases pass.
- [Manual]: run in this repo and confirm the slot survey reports every slot empty, since Cantrip has no
  `.agents/config/`, and still exits zero.

---

### Step 5 — Report assembly and exit-code discipline

> **Prompt**: Implement Step 5 of `_work/shipped/install-verification/plan.md`. Finalize
> `scripts/check-install.sh`'s output: a summary counting wired, degraded, and broken units, followed by
> only the degraded and broken findings with their fixes, so a healthy install produces a short report
> rather than a wall of green. Exit non-zero **only** when something is broken (FR7). Add a
> `--verbose` flag that also lists what is wired, matching `check-contract.sh`'s existing convention.
> Re-run the full suite and confirm all ten cases still pass. Then document the script in README under
> the install section, and add a line to CHANGELOG.

**What to build**: report assembly, `--verbose`, README and CHANGELOG entries.

**Validation**:
- [Automated]: `tests/run.sh` — ten of ten. `./scripts/check-contract.sh` passes.
- [Automated]: run the script in this repo and assert exit zero; break something deliberately and assert
  non-zero; restore.
- [Manual]: read the default output as a first-time consumer and judge whether it says what to do next.

---

### Step 6 — Record the durable behavior

> **Prompt**: Run `/feature update install-verification` to verify the living behavioral doc reflects
> the actual implementation. Review each scenario against the code and test results. Update any
> scenario where the implementation diverged from the draft. Fill in the test coverage table with real
> fixture paths, replacing every "Not covered". Remove the "Draft" banner. Commit the verified doc.
>
> **Validation**: Every scenario matches observable behavior; the coverage table has no unexpected
> "Not covered" gaps.

---

## File Summary

| Action | File |
|--------|------|
| Create | `scripts/check-install.sh` |
| Create | `tests/run.sh` |
| Create | `tests/README.md` |
| Create | `tests/install-check/<case>/` × 10 |
| Modify | `README.md` (document the check) |
| Modify | `CHANGELOG.md` |
| _(work type: `new-capability`)_ Update | `_features/install-verification.md` (verify scenarios, fill coverage, drop the Draft banner) |
