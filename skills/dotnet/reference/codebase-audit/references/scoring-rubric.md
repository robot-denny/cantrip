# Scoring Rubric

Anchors for the 1–5 score given to each pillar. The rubric is intentionally honest: most healthy codebases land in the 2–4 range across pillars. 5s are rare. 1s are also rare (real codebases that survived have *something* going for them).

This file names signals, not packages. The concrete library, file format, and API names for the platform in play come from the pillar's own platform reference and from the audit's Phase 3 checklist — an anchor written in one ecosystem's vocabulary can only be applied in that ecosystem, and these anchors apply wherever the pillar does.

## General scale

| Score | Meaning |
|---|---|
| 5 | Exemplary — the pattern is followed with intention, consistency, and craft. Worth copying. |
| 4 | Strong — the pattern is mostly in place with minor gaps. Recommendations are tuning, not restructuring. |
| 3 | Adequate — the pattern is present but uneven. Some areas exemplary, others weak. Average mature production codebase. |
| 2 | Weak — the pattern is *named* (e.g., dependency injection is used) but not used well. Significant inconsistency. |
| 1 | Absent — the pattern is missing or actively worked against. Often a starter-template artifact that was never developed. |

## Per-pillar anchors

### Pillar 1: Modern platform hygiene

| Score | Anchor |
|---|---|
| 5 | Dependency injection cohesive, asynchrony correct everywhere, the compiler's strict-safety options on with warnings as errors, structured logging, secrets externalized, dependency versions managed centrally, formatting config enforced. |
| 4 | Injection cohesive, asynchrony correct in most paths, strict-safety options on, structured logging through a logging abstraction, secrets externalized. Minor gaps (one or two blocking calls on async work in legacy code). |
| 3 | Injection used but registration spread across multiple files. Some blocking calls on async work. Logging mixed (an abstraction plus occasional writes to stdout). Strict-safety options on but warnings ignored. |
| 2 | Injection present but inconsistently. Logging is mostly print-to-stdout or string concatenation. Secrets in committed config. Strict-safety options disabled. |
| 1 | Service-locator pattern instead of injection. Synchronous waits on async work dominant. Print-to-stdout logging. |

### Pillar 2: Architectural separation

| Score | Anchor |
|---|---|
| 5 | Clean layering or vertical-slice organization with the dependency rule enforced. Anti-corruption interfaces around third-party SDKs. Deep modules at the right seams. Domain models carry behavior. |
| 4 | Layering visible (folders or projects). One or two anti-corruption layers in place. Mostly deep modules. Some anemic models where typed read models are appropriate. |
| 3 | Loose layering (folders only, dependency rule not enforced). Some shallow modules. Domain models anemic but functional. |
| 2 | Flat structure with grab-bag `Helpers/` / `Utils/`. View templates and business logic mingled. No anti-corruption layers. |
| 1 | View templates do everything — data fetching, business rules, external API calls. No layering or interfaces. |

### Pillar 3: Documentation & onboarding

| Score | Anchor |
|---|---|
| 5 | 4+ doc categories present (agentic, onboarding, decision records, specs/plans, glossary, in-code, auto-generated). Recently updated. Build/run instructions clear. Domain language is consistent. |
| 4 | 3 categories present, recently updated. README + at least one of decision records / spec / glossary. |
| 3 | 2 categories. README adequate. In-code "why" comments at non-obvious points. Decision records missing or in commit messages only. |
| 2 | 1 category (usually a README). No decision records. Comments are mostly "what" not "why." Domain language unclear. |
| 1 | Default README only. No build instructions. No domain documentation. Comments restate code. |

### Pillar 4: Resilience & operations

| Score | Anchor |
|---|---|
| 5 | CI green on every push. Pre-commit hooks. Structured logging with correlation IDs. Metrics and traces exported. Retry/circuit-breaker policy on outbound calls. Health checks. Secrets externalized. |
| 4 | CI in place. Structured logging. Retry policy on critical outbound calls. Secrets externalized. Some observability but no trace export. |
| 3 | CI in place (build + test). A logging abstraction used but messages unstructured. No retry library. Secrets externalized. |
| 2 | No CI or CI broken. Logging to stdout mixed with a logging abstraction. No retry/timeout discipline. Some secrets in committed config. |
| 1 | No CI. Errors swallowed by empty catch blocks. Secrets in committed source. No environment parity. |

### Pillar 5: Scalability & refactorability

Synthesized — not directly scored from a single signal set. The score reflects:

| Score | Anchor |
|---|---|
| 5 | Expensive work cached, data-access indexes correct, test coverage strong (unit + integration), dependencies pinned and stable, deep modules at seams that make refactoring cheap. |
| 4 | Caching strategic, indexes correct, integration tests present, deep modules at most seams. |
| 3 | Some caching. Index strategy ad-hoc. End-to-end tests only. Refactoring would be moderate effort due to shallow modules in some places. |
| 2 | Minimal caching. No test coverage worth mentioning. Refactoring expensive due to coupling. |
| 1 | No caching. No tests. Coupling means even small changes cascade. |

## Honest scoring rule

- Most healthy codebases land in the **2–4** range per pillar.
- If your draft has 5s on three or more pillars, scrutinize — you may be grading by potential rather than evidence.
- If your draft has 1s on three or more pillars, scrutinize too — you're either looking at a catastrophic codebase (rare) or grading uncharitably.

The score is a calibration anchor, not the deliverable. The *recommendations* are the deliverable.
