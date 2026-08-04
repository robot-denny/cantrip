# Scoring Rubric

Anchors for the 1–5 score given to each pillar. The rubric is intentionally honest: most healthy codebases land in the 2–4 range across pillars. 5s are rare. 1s are also rare (real codebases that survived have *something* going for them).

## General scale

| Score | Meaning |
|---|---|
| 5 | Exemplary — the pattern is followed with intention, consistency, and craft. Worth copying. |
| 4 | Strong — the pattern is mostly in place with minor gaps. Recommendations are tuning, not restructuring. |
| 3 | Adequate — the pattern is present but uneven. Some areas exemplary, others weak. Average mature .NET codebase. |
| 2 | Weak — the pattern is *named* (e.g., DI is used) but not used well. Significant inconsistency. |
| 1 | Absent — the pattern is missing or actively worked against. Often a starter-template artifact that was never developed. |

## Per-pillar anchors

### Pillar 1: Modern .NET hygiene

| Score | Anchor |
|---|---|
| 5 | DI cohesive, async correct everywhere, nullable on with warnings-as-errors, structured logging, secrets externalized, central package management, `.editorconfig` enforced. |
| 4 | DI cohesive, async correct in most paths, nullable on, structured logging via `ILogger<T>`, secrets externalized. Minor gaps (one or two `.Result` calls in legacy code). |
| 3 | DI used but registration spread across multiple files. Some `.Result` calls. Logging mixed (ILogger + occasional Console). Nullable on but warnings ignored. |
| 2 | DI present but inconsistently. Logging is mostly Console or string-concat. Secrets in committed config (gitignored but committed). Nullable disabled. |
| 1 | Service-locator pattern instead of DI. Sync-over-async dominant. `Console.WriteLine` for logging. |

### Pillar 2: Architectural separation

| Score | Anchor |
|---|---|
| 5 | Clean layering or vertical-slice organization with the dependency rule enforced. Anti-corruption interfaces around third-party SDKs. Deep modules at the right seams. Domain models carry behavior. |
| 4 | Layering visible (folders or projects). One or two ACLs in place. Mostly deep modules. Some anemic models where typed views are appropriate. |
| 3 | Loose layering (folders only, dependency rule not enforced). Some shallow modules. Domain models anemic but functional. |
| 2 | Flat structure with grab-bag `Helpers/` / `Utils/`. Razor + business logic mingled. No ACLs. |
| 1 | View templates do everything — content fetching, business rules, external API calls. No layering or interfaces. |

### Pillar 3: Umbraco-version-appropriate patterns

| Score | Anchor |
|---|---|
| 5 | Composers used appropriately. Notification handlers. All schema artifacts committed (including built-in defaults). Pre-commit drift check. Block partials focused. Cached partials. Secret placeholders. |
| 4 | Composers used. Most schema committed. Block organization clean. Some built-in defaults not extracted (drift on Deploy dashboard). |
| 3 | Partial composer adoption. Schema mostly committed but with periodic drift. Block partials present but inconsistently focused. |
| 2 | Service registration mostly in `Program.cs`. Schema inconsistent. Block partials with embedded business logic. |
| 1 | Legacy event handlers. Schema rarely committed. Direct examine/SQL in views. Secrets pasted into backoffice connection forms. |

### Pillar 4: Headless suitability

This pillar splits orientation from readiness; the *score* reflects readiness for any future direction the user might choose.

| Score | Anchor |
|---|---|
| 5 | Already headless, or hybrid with a clean Delivery API surface. Content access fully mediated. Frontend independent. |
| 4 | Hybrid with most Razor templates as pure presentation. Content access via services. JS/TS build present. Headless migration would be M-effort. |
| 3 | Traditional with some seams in place. View models exist. A few partials still query directly. Headless would be L-effort but achievable. |
| 2 | Traditional. Multiple content queries per view. Business logic in templates. Headless migration would be XL-effort. |
| 1 | Traditional. Business rules deeply embedded in Razor. `dynamic` content access. No frontend build. Headless is effectively a rewrite. |

### Pillar 5: Documentation & onboarding

| Score | Anchor |
|---|---|
| 5 | 4+ doc categories present (agentic, onboarding, ADRs, specs/plans, glossary, in-code, auto-generated). Recently updated. Build/run instructions clear. Domain language is consistent. |
| 4 | 3 categories present, recently updated. README + at least one of ADR / spec / glossary. |
| 3 | 2 categories. README adequate. In-code "why" comments at non-obvious points. ADRs missing or in commit messages only. |
| 2 | 1 category (usually a README). No ADRs. Comments are mostly "what" not "why." Domain language unclear. |
| 1 | Default README only. No build instructions. No domain documentation. Comments restate code. |

### Pillar 6: Resilience & operations

| Score | Anchor |
|---|---|
| 5 | CI green on every push. Pre-commit hooks. Structured logging with correlation IDs. OpenTelemetry / metrics. Polly on outbound. Health checks. Secrets externalized. |
| 4 | CI in place. Structured logging. Polly on critical outbound calls. Secrets externalized. Some observability but not OpenTelemetry. |
| 3 | CI in place (build + test). ILogger used but not structured. No retry library. Secrets externalized. |
| 2 | No CI or CI broken. Logging via Console mixed with ILogger. No retry/timeout discipline. Some secrets in committed config. |
| 1 | No CI. Errors swallowed with `catch { }`. Secrets in committed source. No environment parity. |

### Pillar 7: Scalability & refactorability

Synthesized — not directly scored from a single signal set. The score reflects:

| Score | Anchor |
|---|---|
| 5 | Cached partials, indexes correct, test coverage strong (unit + integration), dependencies pinned and stable, deep modules at seams that make refactoring cheap. |
| 4 | Caching strategic, indexes correct, integration tests present, deep modules at most seams. |
| 3 | Some caching. Index strategy ad-hoc. E2E tests only. Refactoring would be moderate effort due to shallow modules in some places. |
| 2 | Minimal caching. No test coverage worth mentioning. Refactoring expensive due to coupling. |
| 1 | No caching. No tests. Coupling means even small changes cascade. |

## Honest scoring rule

- Most healthy codebases land in the **2–4** range per pillar.
- If your draft has 5s on three or more pillars, scrutinize — you may be grading by potential rather than evidence.
- If your draft has 1s on three or more pillars, scrutinize too — you're either looking at a catastrophic codebase (rare) or grading uncharitably.

The score is a calibration anchor, not the deliverable. The *recommendations* are the deliverable.
