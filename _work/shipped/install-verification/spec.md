# Spec for install-verification

> This spec captures initial requirements and design rationale. For **current system
> behavior**, see the doc named on the **Work type** line below — a new feature doc for a new
> capability, an existing feature doc for a change, or a `docs/` runbook for a fix.

branch: feature/install-verification
design reference (if any): none

**Work type**: new-capability
<!--
  Decides which durable artifact this work earns. See the `workflow` skill → "Work types".
  - new-capability     → a new feature doc is created, named by capability, not by work
  - change-to <slug>   → no new file; observable behavior folds into that capability's doc
  - fix-infra          → no feature doc; durable record is a runbook under docs/
  The tell: transition-style acceptance criteria ("goes from… to…", "leaves no trace")
  are NOT new-capability.
-->

## Summary

Someone who installs Cantrip has no way to confirm it landed correctly. The installer reports
success, but success means "files were written" — not "the toolkit is usable here". A consumer is
left to discover problems by casting a spell and watching it fail, which is the worst moment to find
out.

Three things can be silently wrong after a install that reported success: skills can be partially
installed, a skill's bundled assets can be missing so a spell reads a template that isn't there, and
the reviewer agents can be unregistered so review runs degraded without saying why. None of these
announce themselves.

This adds a check a consumer runs to see the actual state of their install, in one pass, with a clear
statement of what is wired, what is degraded but working, and what is genuinely broken. It is the
consumer-facing counterpart to the contract gate that guards this repo.

## Functional Requirements

- **FR1 — Verify the expected skills are present.** Report which of the toolkit's skills resolve and
  which are missing. A partial install is the common failure and must be named specifically, not
  reported as a generic failure.
- **FR2 — Verify bundled assets resolve, not merely that skill directories exist.** A skill whose
  `SKILL.md` is present but whose assets are missing is broken in a way a directory listing hides —
  the templates and the reviewer agent definitions must be readable through the path a spell would
  actually use.
- **FR3 — Work under every install layout.** The installer produces a canonical layout
  (`.agents/skills/` with symlinks from `.claude/skills/`), a copied layout (files directly in
  `.claude/skills/`), or a source-symlinked layout as used when self-hosting. All three are valid and
  must pass.
- **FR4 — Distinguish three outcome classes.** Wired, degraded-but-working, and broken are different
  situations and must not be collapsed. Unregistered reviewer agents are *degraded* — review still
  runs inline — while a missing template is *broken*.
- **FR5 — Report which L2 slots are filled and which are empty.** Every empty slot is legitimate, since
  the toolkit is designed to work with all of them empty. The point is to show the consumer what the
  toolkit currently knows about their project, so an unexpected empty slot becomes visible rather than
  silently degrading a spell.
- **FR6 — Give the fix, not just the finding.** Every degraded or broken result names the specific
  command or file that resolves it.
- **FR7 — Exit non-zero only for genuinely broken state.** A degraded install and an install with every
  slot empty both exit zero, because both are working. Only a broken install fails, so the check is
  safe to run in a pipeline.
- **FR8 — Treat an absent stack pack as normal.** Core-only is the documented baseline, so no pack must
  never read as a problem.

## Design Reference (only if one exists)

- none

## Possible Edge Cases

- **No lockfile present** — a consumer may have vendored the files by hand rather than installing. The
  check should still assess what is there rather than refusing to run.
- **The installer's stray `agent/` directory** — a known cosmetic artifact holding a partial subset of
  skills. It must not be mistaken for a real install location or reported as drift.
- **A skill directory exists but `SKILL.md` is absent** — the shape of a partially-failed copy.
- **A symlink that resolves to nothing** — a canonical-layout install whose `.agents/` tree was
  deleted, leaving dangling links in `.claude/skills/`. A directory listing looks fine; every read
  fails.
- **Reviewer agents linked but pointing at the wrong place** — present in `.claude/agents/` yet
  unreadable, which is worse than absent because it looks configured.
- **A project with its own unrelated skills and agents installed alongside** — the check must report on
  the toolkit's own units and stay silent about everything else.
- **Slot files that exist but are empty, versus slot headings absent from a file that exists** — both
  are "empty" for the toolkit's purposes and should read the same way.

## Acceptance Criteria

- **AC1**: Given a complete install in any of the three supported layouts, when the check runs, then it
  reports every expected skill as present and exits zero.
- **AC2**: Given an install missing one skill, when the check runs, then it names that skill
  specifically and exits non-zero.
- **AC3**: Given a skill whose bundled asset is missing, when the check runs, then it reports the
  asset as unreadable rather than reporting the skill as present.
- **AC4**: Given an install where the reviewer agents are not registered, when the check runs, then it
  reports review as degraded-but-working, names the linking command, and exits **zero**.
- **AC5**: Given an install with no L2 configuration at all, when the check runs, then it lists every
  slot as empty, states that this is a working configuration, and exits zero.
- **AC6**: Given an install with no stack pack, when the check runs, then no pack-related finding is
  reported.
- **AC7**: Given a `.claude/skills` entry that is a dangling symlink, when the check runs, then it
  reports it as broken rather than present.
- **AC8**: Given a project with unrelated skills and agents present, when the check runs, then only the
  toolkit's own units appear in the report.

## Scenarios (Draft)

Draft BDD scenarios derived from the acceptance criteria using Example Mapping. The actors are the
**consumer** running the check and the **check** itself.

### Rule: A complete install reports as wired, in any supported layout (AC1)

```scenario
Scenario: A canonical-layout install passes
  Given a project where the toolkit was installed with the default command
  And the skills live in .agents/skills with symlinks from .claude/skills
  When the consumer runs the install check
  Then every expected skill is reported present
  And the check exits zero
```

```scenario
Scenario: A self-hosted source-symlinked install passes
  Given a project whose .claude/skills entries symlink directly to toolkit source
  When the consumer runs the install check
  Then every expected skill is reported present
  And the check exits zero
```

### Rule: A partial install names what is missing (AC2)

```scenario
Scenario: One missing skill is named
  Given a complete install with the plan skill removed
  When the consumer runs the install check
  Then the report names plan as missing
  And the check exits non-zero
```

### Rule: Assets are verified by reading, not by listing (AC3, AC7)

```scenario
Scenario: A missing template is caught
  Given an install where the workflow skill's spec template has been deleted
  When the consumer runs the install check
  Then the report says the spec template is unreadable
  And the workflow skill is not reported as simply present
```

```scenario
Scenario: A dangling symlink is broken, not present
  Given a canonical-layout install whose .agents directory has been deleted
  When the consumer runs the install check
  Then each affected skill is reported broken
  And the check exits non-zero
```

### Rule: Degraded is distinguished from broken (AC4)

```scenario
Scenario: Unregistered reviewers are degraded, not broken
  Given a complete install where no reviewer agents are linked into .claude/agents
  When the consumer runs the install check
  Then review is reported as working but degraded to inline passes
  And the report names the command that registers them
  And the check exits zero
```

### Rule: Empty configuration is a working configuration (AC5)

```scenario
Scenario: A fresh install with no slots filled reports as working
  Given a project with no .agents/config directory
  When the consumer runs the install check
  Then every slot is listed as empty
  And the report states that the toolkit works with all slots empty
  And the check exits zero
```

### Rule: The check reports only on the toolkit (AC6, AC8)

```scenario
Scenario: No stack pack is not a finding
  Given a core-only install
  When the consumer runs the install check
  Then no finding mentions a missing pack
```

```scenario
Scenario: Unrelated skills are ignored
  Given a project with three of its own skills and one of its own agents installed
  When the consumer runs the install check
  Then the report covers only the toolkit's own skills and agents
```

## Open Questions

- **Should the check be a script, or a spell?** A script is runnable in a pipeline and needs no agent;
  a spell could read and explain results more helpfully. The spellbook census argued against adding a
  tenth spell without evidence, which points at a script — but confirm that is the right call rather
  than assuming it.
- **How does the check know what to expect?** The set of expected skills could be derived from the
  lockfile, hardcoded, or discovered from the install itself. Deriving it from the lockfile fails for a
  hand-vendored install; hardcoding drifts as the toolkit grows.
- **Should it verify slot *content* or only presence?** Reading whether a slot heading has text under it
  is more useful than checking the file exists, but it edges toward validating the project's own
  configuration, which is not the toolkit's business.

## Testing Guidelines

This is developer-facing tooling, so tests are verification checks rather than a formal suite. Cover,
without over-engineering:

- **A fixture per layout** — canonical, copied, and source-symlinked — each asserted to pass.
- **One deliberate breakage per broken-class AC** — a removed skill, a removed template, a dangling
  symlink — each asserted to be reported specifically and to exit non-zero.
- **The degraded path** — no linked agents, asserted to exit zero and to name the fix.
- **Exit-code discipline**, asserted directly: degraded is zero, broken is non-zero.
