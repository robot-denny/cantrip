# Plan: Pack Boundaries and Succession

**Spec**: `_work/shipped/pack-boundaries-and-succession/spec.md`
**Branch**: pack-boundaries
**Work type**: change-to install-verification
**Feature doc**: `_features/install-verification.md` — plus a second pass on
`_features/dotnet-guidance.md`, because the audit joins the `dotnet` pack

## Context

The `umbraco-17` pack holds three subjects: version-bound CMS facts, Umbraco Deploy and Cloud
knowledge, and a stack-agnostic codebase auditor. This increment moves the latter two out, writes
down the naming rule that lets a future pack replace a current one, and records the boundary test in
ADR 0015.

Nothing is broken today — both real projects are Umbraco 17 *and* Cloud. That sets the bar for
scope: **reorganize and document, do not rewrite guidance.** Discovery is at
`_work/shipped/pack-boundaries-and-succession/discovery.md`.

The unit of work is the skill unit — a directory with a `SKILL.md`, registered in
`scripts/check-install.sh`'s rosters and gated by `scripts/check-contract.sh`.

---

## Key Decisions

- **No rename of `umbraco-17`.** The rule is phrased so the current name already complies: *a
  version-pinned pack carries its major in the pack name.* A future `umbraco-18` is consistent with
  nothing moving today. Decided by the user to avoid breaking the existing install.
- **The Cloud pack ships two units, not three files.** `check-uda` (spell) plus a new
  `umbraco-deploy-facts` reference that merges `deploy-schema.md` and `cloud-remediation.md`. This
  is fewer files than today (2 rather than 3) *and* keeps the facts model-discoverable — burying
  them under the spell's `references/` would make them reachable only by casting the spell. The
  user asked for fewer files where it does not degrade behavior; this satisfies both halves.
- **`headless-suitability.md` moves to `umbraco-17` whole — not split, not deleted.** The user was
  willing to sacrifice it. Moving it intact is *less* work than splitting, keeps the guidance, and
  still leaves `codebase-audit` free of CMS concepts. Spending content was unnecessary.
- **The audit's agnostic half is seam-cut, not promoted.** `lifecycle-stages.md`,
  `documentation-and-onboarding.md`, `resilience-and-ops.md`, `scoring-rubric.md` are held to L0's
  no-technology-names rule now so a later move to core is a `git mv` plus a roster edit. They are
  **not** moved to core in this increment — L0 may name no technology, which would cost the audit
  its concrete signals, and the core→pack delegation contract does not exist yet.
- **A pre-existing slot gap gets fixed here.** `check-uda` declares
  `.agents/config/conventions.md → ## Block palette parity`, and `PACK_SLOTS` does not list it, so
  the install checker never verifies it. The unit is moving anyway; this is the cheap moment.
- **`reinstall_hint()` currently cannot name a pack.** Its fallback is the generic *"reinstall it
  from the pack that provides it — `.../skills/<pack> --all`"*. With three packs this gets worse.
  Step 2 maps each roster to its pack directory so the hint is runnable.
- **Test harness** (inferred — `.agents/config/stack.md` is absent in this repo): `tests/run.sh` with
  fixtures under `tests/install-check/<fixture>/`, and `./scripts/check-contract.sh` as the gate. Both
  run from the repo root. Recorded so the next increment does not re-derive them.
- **RED→GREEN for a move is real, not ceremonial.** Contract check 13 compares `ROSTER_PACK` against
  units on disk. Moving files *first* makes the gate fail for a true reason; updating the roster
  makes it pass. Each step below exploits that rather than inventing a test.

---

## Steps

Each step is designed to be completed independently in its own context window.

---

### Step 1 — Create the `umbraco-cloud` pack

> **Prompt**: Implement Step 1 of `_work/shipped/pack-boundaries-and-succession/plan.md`. Create a new
> versionless pack at `skills/umbraco-cloud/`. Move `skills/umbraco-17/spellbook/check-uda/` to
> `skills/umbraco-cloud/spellbook/check-uda/` with `git mv`. Create a new reference unit
> `skills/umbraco-cloud/reference/umbraco-deploy-facts/SKILL.md` that merges the content of
> `skills/umbraco-17/reference/umbraco-17-starter-facts/references/deploy-schema.md` and
> `skills/umbraco-cloud/spellbook/check-uda/references/cloud-remediation.md`, then delete both
> source files. The merged unit must be model-invocable — write a frontmatter `description` that
> triggers on Umbraco Deploy schema, `.uda` artifacts, and Cloud dashboard import behavior, and
> that does **not** exclude on-premise Deploy licensees. Point `check-uda`'s remediation section at
> the new reference unit instead of its deleted bundled file. Run `./scripts/check-contract.sh` and
> report every check by name.

**What to build**:
- `skills/umbraco-cloud/spellbook/check-uda/SKILL.md` (moved; remediation pointer updated)
- `skills/umbraco-cloud/reference/umbraco-deploy-facts/SKILL.md` (new, merged)
- Delete `.../umbraco-17-starter-facts/references/deploy-schema.md` and
  `.../check-uda/references/cloud-remediation.md`
- Remove the now-empty `check-uda/references/` directory
- Check whether `umbraco-17-starter-facts/SKILL.md` links `deploy-schema.md`; if so, repoint or drop
  the link

**Test first**:
- Before editing, run `./scripts/check-contract.sh` and record the passing baseline (14/14)
- Perform the moves, then run it again and **confirm RED** — check 13 must fail on roster drift,
  because `check-uda` and the new reference are not in `ROSTER_PACK`. That failure is the signal the
  move was seen; a green gate here means the check is not doing its job, so stop and report it
- The roster is fixed in Step 2, so this step ends RED on check 13 **only**. Any *other* failing
  check is a real problem for this step

**Validation**:
- Automated: `./scripts/check-contract.sh` — every check passes except 13
- Manual: confirm no rule present in `deploy-schema.md` or `cloud-remediation.md` before the merge is
  absent after it. List any rule you deliberately dropped as a duplicate, and say which surviving
  sentence covers it

---

### Step 2 — Register the pack and prove it installs alone

> **Prompt**: Implement Step 2 of `_work/shipped/pack-boundaries-and-succession/plan.md`. In
> `scripts/check-install.sh`: add `check-uda` and `umbraco-deploy-facts` to `ROSTER_PACK` and remove
> nothing else yet; add the missing slot entry `conventions.md|Block palette parity|check-uda` to
> `PACK_SLOTS`; and change `reinstall_hint()` so a pack unit yields a runnable command naming its
> actual pack directory rather than the literal placeholder `<pack>`. Add a test fixture
> `tests/install-check/cloud-only/` modeled on the existing `pack-installed` fixture, representing a
> project with the Cloud pack and no CMS pack. Run `tests/run.sh` and `./scripts/check-contract.sh`.

**What to build**:
- `scripts/check-install.sh`: `ROSTER_PACK` entries, one `PACK_SLOTS` entry, a roster→pack mapping
  behind `reinstall_hint()`
- `tests/install-check/cloud-only/` fixture
- A case in `tests/run.sh` asserting the Cloud pack reports as wired with no CMS pack present

**Test first**:
- Add the `cloud-only` fixture and its assertion **before** touching `check-install.sh`
- The assertion: a project holding only the Cloud pack's units reports a working install, and the
  reinstall hint printed for a *missing* Cloud unit is a command that names `umbraco-cloud`
- Run `tests/run.sh` and **confirm RED** on the new case
- Then implement, and confirm GREEN

**Validation**:
- Automated: `tests/run.sh` — all cases pass including the new one; `./scripts/check-contract.sh` —
  14/14, check 13 now green
- Manual: copy the reinstall hint the checker prints for a missing Cloud unit and confirm it is a
  command someone could actually run — not a placeholder

---

### Step 3 — Extract the audit into the `dotnet` pack

> **Prompt**: Implement Step 3 of `_work/shipped/pack-boundaries-and-succession/plan.md`. `git mv`
> `skills/umbraco-17/reference/architecture-audit/` to `skills/dotnet/reference/codebase-audit/` and
> rename the unit to `codebase-audit` in its frontmatter. Move two references *out* to
> `skills/umbraco-17/reference/umbraco-17-starter-facts/references/`:
> `umbraco-version-agnostic.md` and `headless-suitability.md` — **move `headless-suitability.md`
> whole; do not split it.** Sanitize what remains so no Umbraco fact survives in `codebase-audit`,
> and hold these four files to a strict no-technology-names rule: `lifecycle-stages.md`,
> `documentation-and-onboarding.md`, `resilience-and-ops.md`, `scoring-rubric.md`. Update
> `evals/evals.json` and `scripts/collect-signals.sh` for the removed pillars, and delete
> `scripts/detect-umbraco-version.sh`. Update `ROSTER_PACK`. Run `tests/run.sh` and
> `./scripts/check-contract.sh`.

**What to build**:
- `skills/dotnet/reference/codebase-audit/` — moved and renamed
- Two references relocated into the CMS pack; the audit's `SKILL.md` and `report-template.md`
  updated so they no longer reference removed pillars
- `evals/evals.json` — cases naming Umbraco or headless suitability revised or removed
- `scripts/detect-umbraco-version.sh` deleted; `collect-signals.sh` stripped of Umbraco signals
- `ROSTER_PACK`: `architecture-audit` → `codebase-audit`

**Test first**:
- Write the check before sanitizing: a grep over the four seam-cut files for technology names
  (`umbraco`, `dotnet`, `.net`, `csproj`, `c#`, `nuget`, `msbuild`), asserting zero matches
- Run it and **confirm RED** — `scoring-rubric.md` has at least one Umbraco mention today
- Sanitize, then confirm GREEN. Keep the grep as a shell case in `tests/run.sh` so the seam does not
  silently close later

**Validation**:
- Automated: `tests/run.sh` and `./scripts/check-contract.sh` both green; the new seam grep returns
  no matches
- Manual: read `codebase-audit/SKILL.md` end to end and confirm its description would trigger on a
  .NET repository with no CMS. Confirm the report template names no pillar that no longer exists —
  a dangling pillar produces an audit with an empty section

---

### Step 4 — Close the two CMS-pack loose ends

> **Prompt**: Implement Step 4 of `_work/shipped/pack-boundaries-and-succession/plan.md`. Two edits in
> `skills/umbraco-17/`. First, `spellbook/umbraco-edit/SKILL.md` depends on the Management API,
> which exists only from Umbraco 14, and says so nowhere — add a version-floor annotation in the
> body, per ADR 0015 §3's annotate-per-feature rule. Second, `spellbook/block/SKILL.md` references
> `/check-uda`, which now lives in a different pack — apply ADR 0015's "where installed" hedge, and
> state what the reader would otherwise check by hand so a CMS-only install loses nothing. Run
> `./scripts/check-contract.sh`.

**What to build**:
- `skills/umbraco-17/spellbook/umbraco-edit/SKILL.md` — version floor
- `skills/umbraco-17/spellbook/block/SKILL.md` — hedged cross-pack deferral plus the fallback
  behavior

**Test first**: no automated assertion fits a prose hedge. The concrete manual check, defined before
editing: read `block/SKILL.md` as a reader whose project has **no** Cloud pack, and confirm you learn
what to check and how — not merely that a spell you do not have would have told you. A deferral to
something absent is a silent loss of guidance, which is the failure this step exists to prevent.

**Validation**:
- Automated: `./scripts/check-contract.sh` — 14/14
- Manual: the read-through above; and confirm `umbraco-edit`'s floor names a version, not "recent
  versions"

---

### Step 5 — Record the rules in the ADR and the docs

> **Prompt**: Implement Step 5 of `_work/shipped/pack-boundaries-and-succession/plan.md`. Amend
> `adr/0015-what-a-stack-pack-is-and-what-it-owes.md` with two things it lacks: the **variant axis**
> (a pack may be wrong for a project by host or product, not only by version — `check-uda` on a
> non-Cloud install is the worked example) and the **replacement operation** (how a future pack
> supersedes a current one). Add the naming rule — version-prefixed reference names, bare spell
> names, a version-pinned pack carries its major in the pack name — and the constraint that one CMS
> major is installed at a time, with the reasoning that a migration means two codebases. Then update
> `README.md` (the three reference tables and the install section), `CHANGELOG.md`, and
> `ROADMAP.md`. Run `./scripts/check-contract.sh`.

**What to build**:
- `adr/0015-...md` — variant axis, replacement operation, naming rule, one-major constraint
- `README.md` — unit tables reflecting three packs; install commands
- `CHANGELOG.md`, `ROADMAP.md` — the latter moving the pack-boundary items out of Next

**Test first**: the assertion is that documentation matches disk. Before editing, write a throwaway
script that extracts every unit name from `README.md`'s tables and diffs it against
`find skills -name SKILL.md`. Run it and **confirm RED** — the README still lists
`architecture-audit` under Umbraco and omits both new units. Fix the README, confirm GREEN, then
delete the script.

**Validation**:
- Automated: `./scripts/check-contract.sh` — 14/14; `tests/run.sh` — all pass; the throwaway diff
  reports no discrepancy before deletion
- Manual: confirm the ADR states the variant axis as a *test someone can apply*, not only as a
  description of what happened here

---

### Final — Record the durable behavior *(a spell you cast, not an implement-step)*

**Do not number this as an implementation step.**

> **Prompt**: Run `/feature update install-verification`. Fold **only** the operator-observable
> behavior changes from this work into the existing capability doc — that a pack can be verified
> without its siblings present, that a reinstall hint names the pack that provides a unit, and that
> the checker verifies the newly registered slot. Do not create a new feature doc. Leave the move
> mechanics and the ADR decisions in the shipped spec; they are point-in-time and must not appear as
> Rules. Add a revision note dated today.
>
> Then run `/feature update dotnet-guidance` for the audit joining the `dotnet` pack — the standing
> behavior that a .NET project with no CMS can get a structural assessment.
>
> **Validation**: Both capability docs describe current behavior with no transition-style Rules; no
> new feature doc was added.

---

## File Summary

| Action | File |
|--------|------|
| Create | `skills/umbraco-cloud/reference/umbraco-deploy-facts/SKILL.md` |
| Move | `skills/umbraco-17/spellbook/check-uda/` → `skills/umbraco-cloud/spellbook/check-uda/` |
| Move | `skills/umbraco-17/reference/architecture-audit/` → `skills/dotnet/reference/codebase-audit/` |
| Move | `umbraco-version-agnostic.md`, `headless-suitability.md` → `umbraco-17-starter-facts/references/` |
| Delete | `.../umbraco-17-starter-facts/references/deploy-schema.md` (merged) |
| Delete | `.../check-uda/references/cloud-remediation.md` (merged) |
| Delete | `.../codebase-audit/scripts/detect-umbraco-version.sh` |
| Modify | `skills/dotnet/reference/codebase-audit/SKILL.md`, `evals/evals.json`, `assets/report-template.md`, `scripts/collect-signals.sh` |
| Modify | the four seam-cut references (sanitized) |
| Modify | `skills/umbraco-17/spellbook/umbraco-edit/SKILL.md`, `skills/umbraco-17/spellbook/block/SKILL.md` |
| Modify | `skills/umbraco-17/reference/umbraco-17-starter-facts/SKILL.md` |
| Modify | `scripts/check-install.sh` (`ROSTER_PACK`, `PACK_SLOTS`, `reinstall_hint`) |
| Create | `tests/install-check/cloud-only/` fixture |
| Modify | `tests/run.sh` (cloud-only case, seam grep case) |
| Modify | `adr/0015-what-a-stack-pack-is-and-what-it-owes.md`, `README.md`, `CHANGELOG.md`, `ROADMAP.md` |
| Create (delete after running) | the README-versus-disk diff script in Step 5 |
| _(work type: `change-to install-verification`)_ Update | `_features/install-verification.md`, and `_features/dotnet-guidance.md` |
