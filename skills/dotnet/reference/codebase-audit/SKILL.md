---
name: codebase-audit
description: Audit a .NET codebase at the structural level — platform hygiene, architectural separation, documentation and onboarding, resilience and operations, and how well it suits agentic coding. Produces a markdown report with prioritized P0/P1/P2 recommendations framed for the codebase's lifecycle stage, and can compare two repositories head-to-head. Use when asked to review or audit an architecture, judge whether a solution is set up the right way, assess a repository being inherited, or compare scaffolding choices — anything wanting a verdict on structure rather than a line-level review of a diff.
---

# Codebase Audit

A skill for producing structured architectural assessments of .NET codebases. The output is a written markdown report — not a chat. Reports cover five pillars, are tailored to the codebase's lifecycle stage, and can optionally include a head-to-head comparison with a second repo.

This skill assumes the user wants a thoughtful, evidence-cited written deliverable they can share, archive, or use to drive a refactor backlog. If the user wants a quick conversational chat about architecture, this skill is too heavy — say so and offer to skip it.

The audit is framework-neutral: it works on a service, a library, a console app, or a web application, with or without a CMS or any other framework on top.

---

## Workflow

Follow these phases in order. Each phase has clear handoff to the next.

### Phase 1: Establish context

1. **Confirm the target(s).** Default target is the current working directory. If the user has supplied a `--compare <path>` argument, plan for two audits + a head-to-head section. If the user gave a path that doesn't exist, stop and ask.
2. **Detect lifecycle stage.** Run `scripts/detect-stage.sh <target>`. The script emits one of: `greenfield`, `growing`, `mature`, `brownfield`, or `ambiguous`. If `ambiguous`, ask the user once: "How would you describe this codebase: greenfield (just started), growing (under active development), mature (stable, slower change), or brownfield (you inherited it)?" Accept their answer.
3. **Collect signals.** Run `scripts/collect-signals.sh <target>`. This produces deterministic counts (LOC, `.cs` file counts inside vs outside `Views/`, test counts, doc counts, git age and contributor diversity). Keep the output — it goes in the report appendix.
4. **Note optional inspections.** Detect whether the project has any of:
   - A framework the project is built on that has its own installed stack guidance — a skill set or MCP server for the CMS, ORM, or application framework in play. Where one is installed, consult it for what idiomatic use of that framework looks like; this skill judges the .NET foundation and the structure around it, not the framework's own conventions.
   - Git history.
   Note in the report which were available; never error when they're missing.

### Phase 2: Read the references

Before drafting any findings, read the reference files for the pillars you'll score. Each describes the positive and negative signals for its pillar.

- [references/dotnet-hygiene.md](references/dotnet-hygiene.md) — Pillar 1, **and the detection recipes for Pillars 3 and 4**
- [references/architectural-separation.md](references/architectural-separation.md) — Pillar 2
- [references/documentation-and-onboarding.md](references/documentation-and-onboarding.md) — Pillar 3
- [references/resilience-and-ops.md](references/resilience-and-ops.md) — Pillar 4
- [references/lifecycle-stages.md](references/lifecycle-stages.md) — applies to all pillars; gates how recommendations are framed
- [references/scoring-rubric.md](references/scoring-rubric.md) — the 1–5 anchors per pillar

**Recipes and criteria are split deliberately.** Four references — lifecycle stages, scoring, documentation and onboarding, resilience and operations — state their criteria without naming any technology, so the same judgement can be reused on a stack that is not .NET. A grep that names nothing matches everything, so the recipes for those pillars sit in `dotnet-hygiene.md` instead. Read both halves for Pillars 3 and 4.

Scalability & refactorability (Pillar 5) is synthesized from signals across multiple pillars; it doesn't have its own reference file by design.

`lifecycle-stages.md`, `documentation-and-onboarding.md`, `resilience-and-ops.md`, and `scoring-rubric.md` deliberately name no technology — what a lifecycle stage is and what resilience means are claims about codebases, not about a platform. The technology-specific signals live in the other two references, and in whatever framework guidance the project has installed.

### Phase 3: Gather evidence

For each pillar, walk the codebase and collect evidence. Always cite file paths and (where useful) line numbers. Evidence is the most important thing — a finding without evidence is hand-waving.

- Read entry-point files first: `Program.cs`, `Startup.cs` if present, root `.csproj` files, and any framework-specific startup or composition types.
- Read a representative sample of business logic — controllers, services, view components, partials. Don't read every file; a representative sample is enough.
- For Pillar 3 (docs), look for *patterns*: any of `CLAUDE.md`, `AGENTS.md`, `AGENT.md`, `.cursor/`, `.continue/`, `.aider*`, `_specs/`, `_plans/`, `_features/`, `adr/`, `docs/adr/`, README sections, in-file XML doc comments. **Reward whatever exists; do not penalize specific names that are missing.**
- For Pillar 4 (resilience), look for: `try/catch` patterns, retry libraries (Polly), structured logging adapters (Serilog), `appsettings.*.json` discipline, secrets handling, CI/CD configs (`.github/workflows/`, `.gitlab-ci.yml`, `azure-pipelines.yml`, etc.), `.editorconfig`, pre-commit hooks.

### Phase 4: Score and draft

1. Score each pillar 1–5 using the anchors in `scoring-rubric.md`. Be honest — fives are rare. Most healthy codebases land in the 2–4 range across pillars.
2. For each pillar, draft: rationale, at least one strength, at least one weakness, evidence (file paths).
3. Identify recommendations. Prioritize P0/P1/P2 using `lifecycle-stages.md` guidance:
   - **Greenfield**: foundational P0s are cheap to apply now. Be ambitious.
   - **Growing**: emphasize "lock in good patterns before they ossify." Identify where the starter scaffolding is being outgrown.
   - **Mature**: prefer small, scope-limited, high-leverage P1s and P2s. Heavy refactor P0s should be rare and well-justified.
   - **Brownfield**: lead with "understand before changing." Produce the map; then risk-prioritize.
4. If a comparison target is in play, run `scripts/compare-repos.sh <report-a> <report-b>` after both audits are written; it merges them into a head-to-head section.

### Phase 5: Write the report

Use `assets/report-template.md` as the skeleton. Fill in every section. The report goes to the project's audit location — `docs/audits/<YYYY-MM-DD>-<slug>.md` by default, per the `workflow` skill's layout (create the directory if absent; never overwrite a file — if a same-named report exists, append `-2`, `-3`, etc.).

If the user passed `--out <path>`, honor that path.

After writing, summarize the report to the user in 3–5 sentences (executive summary), name the saved path, and stop. Do not chat through the recommendations unless the user asks.

---

## Pillars

| # | Pillar | Reference | Notes |
|---|---|---|---|
| 1 | Modern platform hygiene | dotnet-hygiene.md | DI, async, config, package discipline |
| 2 | Architectural separation | architectural-separation.md | Layering, depth, ACL |
| 3 | Documentation & onboarding | documentation-and-onboarding.md | Pattern-detected, not filename-coupled |
| 4 | Resilience & operations | resilience-and-ops.md | CI/CD, observability, secrets |
| 5 | Scalability & refactorability | (synthesized; no reference file) | Cross-cuts other pillars |

Framework-idiomatic use — whether the CMS, ORM, or application framework on top is used the way its maintainers intend — is **not** a pillar here. It is version-specific and platform-specific, which is what a stack pack for that framework is for. Where one is installed, cite it; where none is, say so in the report rather than guessing.

## Inputs (recognized arguments)

- *(no arg)* — audit the current working directory.
- `--compare <path>` — audit a second target; produce a head-to-head section.
- `--stage greenfield|growing|mature|brownfield` — override the detected stage.
- `--out <path>` — override the default report path.

If the user invokes the skill without an explicit argument syntax (most cases), infer from their prompt and confirm only if ambiguous.

## Portability rules

This skill must work in any .NET repo, not just the one it was authored in. Follow these rules strictly:

- **Never** require a specific filename. Detect patterns instead. For example: don't require `CLAUDE.md`; look for *any* of `CLAUDE.md`, `AGENTS.md`, `AGENT.md`, `.cursor/`, `.continue/`, `.aider*`, etc. Reward whatever exists.
- **Never** require a specific folder layout. Detect patterns: spec/plan/feature dirs may be `_specs/`, `specs/`, `docs/specs/`, etc.
- **Never** require a specific package set. Detect from `.csproj` references and adapt expectations to what the project actually depends on.
- **Never** require the existence of optional tools (an MCP server, installed framework skills, git). Note their presence as bonuses; degrade gracefully when absent.
- **Never** name a project-specific identifier (e.g., a particular startup or registration class name) in user-facing report text. The signals you detect must apply to any .NET codebase.

## Output format

See [assets/report-template.md](assets/report-template.md) for the full skeleton. Key constraints:

- Report length: aim for 800–2,000 lines. Brownfield reports may run longer (the map adds bulk).
- Every pillar score must cite at least two pieces of evidence (file paths or signal counts).
- Every recommendation must specify: rationale, scope-of-change estimate (S/M/L), lifecycle-stage appropriateness note, and which pillar(s) it improves.
- Strengths are not optional. If the codebase has fewer than three strengths worth naming, find more — every codebase has them.

## When NOT to use this skill

- The user wants a line-level code review of a diff or PR. That's a different concern — point them at any existing diff-review tooling in the project.
- The user wants a quick gut check, not a written report. Offer to discuss informally and skip the skill.
- The user has a non-.NET codebase. Politely decline; this skill's detection recipes and hygiene signals are .NET-specific.

## Skill maintenance notes

- The two technology-specific references are written against .NET rather than against a framework version. When a framework the project uses ships a new major, prefer enriching detection via that framework's installed guidance rather than adding version branches here.
- Lifecycle heuristics in `detect-stage.sh` will need periodic tuning as the skill is used against more fixtures. Treat the script as data, not gospel — if the detection is wrong, ask the user.
- The skill should never *modify* the target codebase. Read-only, plus writing the report to the project's audit location (see the `workflow` skill).

## Where the report goes

This skill produces a report, so it follows the toolkit's artifact-disposition convention: **ask
whether the output is durable or temporal.**

- **Durable** → the project's audit directory, committed. `docs/audits/<YYYY-MM-DD>-<slug>.md` is the
  default layout; the `workflow` skill is the authority if the project has overridden it.
- **Temporal** → a git-ignored scratch location.

Location enforces commit status, so there is no separate decision to remember. Date the filename
either way — an audit is a point-in-time snapshot, and an undated one gets mistaken for current truth.
