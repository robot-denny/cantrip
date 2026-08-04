---
name: architecture-audit
description: Audit the architectural quality of an Umbraco/.NET codebase against modern .NET, Clean Architecture, Umbraco-version-appropriate best practices, headless suitability, documentation/onboarding quality, resilience, and agentic-coding habitability. Produces a written markdown report with strengths, weaknesses, and prioritized P0/P1/P2 recommendations tailored to the codebase's lifecycle stage (greenfield, growing, mature, or brownfield-inherited). Optionally compares two Umbraco/.NET repos head-to-head. Trigger whenever the user asks to "review the architecture," "audit the codebase," "assess code quality at a structural level," compares scaffolding choices, asks whether their site is set up "the right way," wants to evaluate a colleague's Umbraco repo against theirs, is taking over an unfamiliar codebase, or wonders if their architecture is well-positioned for a future headless move.
---

# Architecture Audit

A skill for producing structured architectural assessments of Umbraco/.NET codebases. The output is a written markdown report — not a chat. Reports cover seven pillars, are tailored to the codebase's lifecycle stage, and can optionally include a head-to-head comparison with a second repo.

This skill assumes the user wants a thoughtful, evidence-cited written deliverable they can share, archive, or use to drive a refactor backlog. If the user wants a quick conversational chat about architecture, this skill is too heavy — say so and offer to skip it.

---

## Workflow

Follow these phases in order. Each phase has clear handoff to the next.

### Phase 1: Establish context

1. **Confirm the target(s).** Default target is the current working directory. If the user has supplied a `--compare <path>` argument, plan for two audits + a head-to-head section. If the user gave a path that doesn't exist, stop and ask.
2. **Detect Umbraco version.** Run `scripts/detect-umbraco-version.sh <target>`. Note the major version. If no Umbraco is detected, ask the user whether they meant to run this skill on a non-Umbraco .NET repo (the skill can still run, but Pillar 3 falls back to generic .NET conventions).
3. **Detect lifecycle stage.** Run `scripts/detect-stage.sh <target>`. The script emits one of: `greenfield`, `growing`, `mature`, `brownfield`, or `ambiguous`. If `ambiguous`, ask the user once: "How would you describe this codebase: greenfield (just started), growing (under active development), mature (stable, slower change), or brownfield (you inherited it)?" Accept their answer.
4. **Collect signals.** Run `scripts/collect-signals.sh <target>`. This produces deterministic counts (LOC, `.cs` file counts inside vs outside `Views/`, Composer count, test counts, doc counts, git age and contributor diversity). Keep the output — it goes in the report appendix.
5. **Note optional inspections.** Detect whether the project has any of:
   - Installed Umbraco backoffice skills (look at `.claude/settings.json` for `umbraco-cms-backoffice-skills@*` or similar enabled plugins).
   - Umbraco MCP credentials (look at `.env` for `UMBRACO_CLIENT_ID` / `UMBRACO_CLIENT_SECRET` plus a base URL).
   - Git history.
   Note in the report which were available; never error when they're missing.

### Phase 2: Read the references

Before drafting any findings, read the reference files for the pillars you'll score. Each reference describes the positive signals, negative signals, and detection recipes for that pillar.

- [references/dotnet-hygiene.md](references/dotnet-hygiene.md) — Pillar 1
- [references/architectural-separation.md](references/architectural-separation.md) — Pillar 2
- [references/umbraco-version-agnostic.md](references/umbraco-version-agnostic.md) — Pillar 3 baseline; *enrich with installed Umbraco backoffice skills / MCP knowledge when present*
- [references/headless-suitability.md](references/headless-suitability.md) — Pillar 4
- [references/documentation-and-onboarding.md](references/documentation-and-onboarding.md) — Pillar 5
- [references/resilience-and-ops.md](references/resilience-and-ops.md) — Pillar 6
- [references/lifecycle-stages.md](references/lifecycle-stages.md) — applies to all pillars; gates how recommendations are framed
- [references/scoring-rubric.md](references/scoring-rubric.md) — the 1–5 anchors per pillar

Scalability & refactorability (Pillar 7) is synthesized from signals across multiple pillars; it doesn't have its own reference file by design.

### Phase 3: Gather evidence

For each pillar, walk the codebase and collect evidence. Always cite file paths and (where useful) line numbers. Evidence is the most important thing — a finding without evidence is hand-waving.

- Read entry-point files first: `Program.cs`, `Startup.cs` if present, root `.csproj` files, Composers.
- Read a representative sample of business logic — controllers, services, view components, partials. Don't read every file; a representative sample is enough.
- For Pillar 4 (headless), run `grep -ri "DeliveryApi" <target>` and inspect any frontend project siblings.
- For Pillar 5 (docs), look for *patterns*: any of `CLAUDE.md`, `AGENTS.md`, `AGENT.md`, `.cursor/`, `.continue/`, `.aider*`, `_specs/`, `_plans/`, `_features/`, `adr/`, `docs/adr/`, README sections, in-file XML doc comments. **Reward whatever exists; do not penalize specific names that are missing.**
- For Pillar 6 (resilience), look for: `try/catch` patterns, retry libraries (Polly), structured logging adapters (Serilog), `appsettings.*.json` discipline, secrets handling, CI/CD configs (`.github/workflows/`, `.gitlab-ci.yml`, `azure-pipelines.yml`, etc.), `.editorconfig`, pre-commit hooks.

### Phase 4: Score and draft

1. Score each pillar 1–5 using the anchors in `scoring-rubric.md`. Be honest — fives are rare. Most healthy codebases land in the 2–4 range across pillars.
2. For each pillar, draft: rationale, at least one strength, at least one weakness, evidence (file paths).
3. Identify recommendations. Prioritize P0/P1/P2 using `lifecycle-stages.md` guidance:
   - **Greenfield**: foundational P0s are cheap to apply now. Be ambitious.
   - **Growing**: emphasize "lock in good patterns before they ossify." Identify where the starter scaffolding is being outgrown.
   - **Mature**: prefer small, scope-limited, high-leverage P1s and P2s. Heavy refactor P0s should be rare and well-justified.
   - **Brownfield**: lead with "understand before changing." Produce the map; then risk-prioritize.
4. For Pillar 4, produce a separate **Headless trajectory** subsection: current orientation (traditional / hybrid / headless), migration readiness (well-positioned / neutral / firmly traditional), and what would have to change to move toward headless.
5. If a comparison target is in play, run `scripts/compare-repos.sh <report-a> <report-b>` after both audits are written; it merges them into a head-to-head section.

### Phase 5: Write the report

Use `assets/report-template.md` as the skeleton. Fill in every section. The report goes to the project's audit location — `docs/audits/<YYYY-MM-DD>-<slug>.md` by default, per the `workflow` skill's layout (create the directory if absent; never overwrite a file — if a same-named report exists, append `-2`, `-3`, etc.).

If the user passed `--out <path>`, honor that path.

After writing, summarize the report to the user in 3–5 sentences (executive summary), name the saved path, and stop. Do not chat through the recommendations unless the user asks.

---

## Pillars

| # | Pillar | Reference | Notes |
|---|---|---|---|
| 1 | Modern .NET hygiene | dotnet-hygiene.md | Version-agnostic |
| 2 | Architectural separation | architectural-separation.md | Layering, depth, ACL |
| 3 | Umbraco-version-appropriate patterns | umbraco-version-agnostic.md (+ installed Umbraco skills/MCP when present) | Version-aware |
| 4 | Headless suitability | headless-suitability.md | Includes migration readiness |
| 5 | Documentation & onboarding | documentation-and-onboarding.md | Pattern-detected, not filename-coupled |
| 6 | Resilience & operations | resilience-and-ops.md | CI/CD, observability, secrets |
| 7 | Scalability & refactorability | (synthesized; no reference file) | Cross-cuts other pillars |

## Inputs (recognized arguments)

- *(no arg)* — audit the current working directory.
- `--compare <path>` — audit a second target; produce a head-to-head section.
- `--stage greenfield|growing|mature|brownfield` — override the detected stage.
- `--out <path>` — override the default report path.

If the user invokes the skill without an explicit argument syntax (most cases), infer from their prompt and confirm only if ambiguous.

## Portability rules

This skill must work in any Umbraco/.NET repo, not just the one it was authored in. Follow these rules strictly:

- **Never** require a specific filename. Detect patterns instead. For example: don't require `CLAUDE.md`; look for *any* of `CLAUDE.md`, `AGENTS.md`, `AGENT.md`, `.cursor/`, `.continue/`, `.aider*`, etc. Reward whatever exists.
- **Never** require a specific folder layout. Detect patterns: spec/plan/feature dirs may be `_specs/`, `specs/`, `docs/specs/`, etc.
- **Never** require a specific package set. Detect from `.csproj` references and adapt expectations to the detected Umbraco major version.
- **Never** require the existence of optional tools (MCP, backoffice skills, git). Note their presence as bonuses; degrade gracefully when absent.
- **Never** name a project-specific identifier (e.g., a particular composer class name) in user-facing report text. The signals you detect must apply to any Umbraco/.NET site.

## Output format

See [assets/report-template.md](assets/report-template.md) for the full skeleton. Key constraints:

- Report length: aim for 800–2,000 lines. Brownfield reports may run longer (the map adds bulk).
- Every pillar score must cite at least two pieces of evidence (file paths or signal counts).
- Every recommendation must specify: rationale, scope-of-change estimate (S/M/L), lifecycle-stage appropriateness note, and which pillar(s) it improves.
- Strengths are not optional. If the codebase has fewer than three strengths worth naming, find more — every codebase has them.

## When NOT to use this skill

- The user wants a line-level code review of a diff or PR. That's a different concern — point them at any existing diff-review tooling in the project.
- The user wants a quick gut check, not a written report. Offer to discuss informally and skip the skill.
- The user has a non-.NET codebase. Politely decline; this skill is .NET-focused and especially Umbraco-aware.

## Skill maintenance notes

- Reference files are version-agnostic by design. When new Umbraco majors ship, prefer enriching detection via installed Umbraco backoffice skills / MCP rather than re-writing static references.
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
