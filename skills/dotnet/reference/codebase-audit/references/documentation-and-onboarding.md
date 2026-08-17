# Pillar 3: Documentation & Onboarding

How friendly the codebase is to a future human or AI collaborator picking it up cold. This is the agentic-coding-habitability pillar, broadened to cover human onboarding too.

This file names signals, not packages. Where a recipe below needs the project's source file pattern it says `<source-glob>`; substitute the project's own.

## Critical rule: detect patterns, not filenames

This pillar must work in any codebase. Do *not* require a file named `CLAUDE.md` or `ROADMAP.md` or `_specs/`. Instead, detect *any* of the following patterns, in any naming variant. Reward whatever exists. Never penalize the absence of a specific filename — only the absence of a *category* of documentation.

## Categories to detect

### Agentic-collaboration docs

- Any of: `CLAUDE.md`, `AGENTS.md`, `AGENT.md`, `.aider*`, `.cursor/`, `.continue/`, `.windsurf*`, `CONVENTIONS.md`, `.github/copilot-instructions.md`.
- A `.claude/` directory with `commands/` and/or `agents/` and/or `skills/` subfolders signals investment in agent-native workflows.

### Onboarding / getting started

- A README with a "Getting Started" / "Quickstart" section.
- A `CONTRIBUTING.md`.
- A `docs/` folder with at least one doc that isn't just an API reference.
- Build/run commands documented (or surfaced in CLAUDE.md / equivalent).

### Architecture decision records (ADRs)

- Any of: `docs/adr/`, `adr/`, `decisions/`, `ARCHITECTURE.md`, `DECISIONS.md`, `RFCS/`.
- Even informal "we chose X because Y" notes in a long-lived doc count.

### Specs / plans / features

- Any of: `_specs/`, `specs/`, `docs/specs/`, `_plans/`, `plans/`, `docs/plans/`, `_features/`, `features/`, `docs/features/`, `_prds/`, `prds/`.
- Living BDD-style feature specs (Given/When/Then) are a strong positive signal regardless of folder name.

### Glossary / domain language

- Any of: `GLOSSARY.md`, `CONTEXT.md`, `DOMAIN.md`, a "Vocabulary" section in README/CLAUDE.
- Inline glossaries (a Markdown file with `## Term` headings) count.

### In-code documentation

- Documentation comments on public APIs, in whatever form the language provides (a doc-comment syntax the toolchain can extract).
- "Why" comments (not "what" comments) at non-obvious points — e.g., "we await this twice because the underlying provider memoizes after the first call."
- Workaround / hack comments that name the specific bug or constraint being worked around.

### Auto-generated docs

- API-schema generation enabled (an OpenAPI document produced from the code).
- A docs-site generator configured.
- Generated reference docs published anywhere (Pages, internal portal).

## What "good" looks like

- At least 3 of the 6 categories above are present and recently updated (commits in the last 90 days for active codebases).
- Build/run instructions in README or CLAUDE-equivalent.
- For greenfield/growing codebases: visible scaffolding for *new* documentation (skill/command for generating ADRs, a `_specs/` template, etc.).
- Names align with the project's domain vocabulary — entities and types use the language a domain expert would use.

## What "bad" looks like

- A README that says "TODO" or still contains only the text the project scaffolder generated.
- No build/run instructions for a non-trivial project.
- ADR-style decisions made in commit messages or PR descriptions only (and therefore lost when the PR archive is hard to search).
- "Helper" / "Manager" / "Util" naming everywhere — signals that domain language hasn't been worked out.
- Comments that restate the code (`// increment counter` above `counter++`).
- Stale docs that contradict the current code (one of the most insidious problems; flag any doc whose mtime is much older than the file it documents).

## Detection recipes

**The recipes for this pillar live with the platform-hygiene reference in this unit, not here** — the
unit's own guide says which file that is. This file states what to judge; a recipe has to name the
identifiers it greps for, and naming them is exactly what this file may not do. Splitting them that
way keeps the criteria reusable on another stack without blunting the search that gathers the
evidence.

## Lifecycle-stage adjustments

- **Greenfield**: Push hard here. Setting up agentic-collaboration docs, ADR scaffolding, and spec folders is *cheap* in a 3-day-old codebase. Recommend specific patterns (e.g., "add a `_specs/` directory and a one-page template").
- **Growing**: Recommend filling the largest gap — usually ADRs. Don't propose a documentation overhaul; that becomes a procrastination project. One concrete improvement.
- **Mature**: Audit for *stale* docs. Recommend a doc-freshness sweep; identify the top 3 most-misleading docs.
- **Brownfield**: This pillar is *especially* important. A brownfield audit's biggest delivered value is often the document that captures what the new owner has just learned about the codebase. Recommend producing that document as the first step.

## Cite canonical sources

- Michael Nygard — *Documenting Architecture Decisions* (the original ADR essay)
- Daniele Procida — *Diátaxis* documentation framework
- The agent vendor's own guidance on collaboration files (when relevant to agentic-collaboration recommendations)
