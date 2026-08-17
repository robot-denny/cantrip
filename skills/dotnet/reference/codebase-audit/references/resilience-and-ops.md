# Pillar 4: Resilience & Operations

How the codebase behaves when things go wrong, and how operations are wired (CI/CD, observability, secrets, environment parity).

This file names signals, not packages. The canonical retry library, logging library, telemetry exporter, and per-environment config format differ by platform — take those from the audit's Phase 3 checklist, and from the project's installed platform guidance where there is any. The detection recipes below use `<source-glob>` for whatever the project's source file pattern is.

## What "good" looks like

### Error handling

- Exceptions caught at the right *level*: at the boundary where a sensible response can be produced (request handler, middleware, background-job dispatcher). Not at every method.
- Custom exception types for distinguishable failure modes, so a caller can tell "not found" from "found but not available".
- A catch-all only at the outermost boundary; specific catches inward.
- No swallowed exceptions — an empty catch block with no logging and no handling.

### Retries & resilience

- A retry/circuit-breaker library is used for external calls — HTTP, third-party APIs, transient database errors. Prefer the platform's canonical choice over a hand-rolled loop.
- Timeouts are set explicitly on outbound network and database calls. Not "infinite" defaults.
- Idempotency considered on write operations.

### Observability

- Structured logging: log calls carry named properties rather than pre-concatenated strings.
- Correlation IDs propagated across requests / background work.
- Metrics surfaced — at least request counts and latencies — through whatever collector the hosting environment offers.
- Health-check endpoints exposed.

### Secrets management

- Secrets not in committed config.
- Per-environment secrets via the hosting platform's app-settings or a secret manager.
- Secret placeholders in committed schema/config artifacts — a named reference to the value, never the value.

### CI/CD

- A CI pipeline (`.github/workflows/`, `.gitlab-ci.yml`, `azure-pipelines.yml`, `bitbucket-pipelines.yml`, etc.) runs on every push.
- Build + test + lint at minimum. Deploy automation present when the platform supports it.
- A pre-commit hook (`.githooks/`, `husky`, `pre-commit` framework) catches common issues before push.

### Environment parity

- Per-environment configuration files (development / staging / production) capture per-environment values.
- Development environment is bootable on a fresh clone without a long-tail of out-of-repo configuration steps.
- Database / storage state is reproducible — migrations versioned, seed data documented.

## What "bad" looks like

- An empty or comment-only catch block in a business path.
- Outbound network calls without timeouts or retry policy.
- Writes to stdout instead of structured logging.
- Secrets in committed per-environment config (especially a committed development config).
- No CI pipeline visible.
- "Works on my machine" symptoms: undocumented env vars, hard-coded local paths, no clear bootstrap path.

## Detection recipes

**The recipes for this pillar live with the platform-hygiene reference in this unit, not here** — the
unit's own guide says which file that is. This file states what to judge; a recipe has to name the
identifiers it greps for, and naming them is exactly what this file may not do. Splitting them that
way keeps the criteria reusable on another stack without blunting the search that gathers the
evidence.

## Lifecycle-stage adjustments

- **Greenfield**: Recommend setting up CI, pre-commit hooks, and structured logging *now*. They become 10× harder to retrofit later. Adding a retry library later is cheaper than adding CI later.
- **Growing**: If CI is missing, that's a P0 regardless of stage. If observability is "log lines only," recommend adding metrics + correlation IDs as a P1.
- **Mature**: Don't recommend ripping out a working logging stack. Audit retry/timeout coverage on outbound calls (often the hidden weakness in mature codebases). Recommend health-check endpoints if absent.
- **Brownfield**: Resilience audit is *especially valuable* — older codebases often have heroic error suppression that the new owner needs to know about. Map the swallowed-exception sites before recommending changes.

## Special note: secrets

The audit must flag any secret pattern detected in committed source, but must not *print the secret value* in the report. The report should say "secret detected in <file>" with the line number, not the secret itself.

If the detection scan returns matches, this is the highest-severity finding the skill can produce. Surface it before any other recommendation.

## Cite canonical sources

- The documentation for whichever resilience library the platform treats as canonical
- The vendor documentation for the project's telemetry and health-check surfaces
- The Twelve-Factor App methodology
