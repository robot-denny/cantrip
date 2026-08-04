# Pillar 6: Resilience & Operations

How the codebase behaves when things go wrong, and how operations are wired (CI/CD, observability, secrets, environment parity).

## What "good" looks like

### Error handling

- Exceptions caught at the right *level*: at the boundary where a sensible response can be produced (controller, middleware, background-job dispatcher). Not at every method.
- Custom exception types for distinguishable failure modes (e.g., `ContentNotPublishedException` vs `ContentNotFoundException`).
- `try/catch` with `catch (Exception)` only at the outermost boundary; specific catches inward.
- No swallowed exceptions (`catch { }` with no logging/handling).

### Retries & resilience

- A retry/circuit-breaker library (Polly is the .NET canonical choice) is used for external calls — HTTP, third-party APIs, transient database errors.
- Timeouts are set explicitly on outbound HTTP / DB calls. Not "infinite" defaults.
- Idempotency considered on write operations.

### Observability

- Structured logging (Serilog or `ILogger<T>` with structured properties — not concatenated strings).
- Correlation IDs propagated across requests / background work.
- Metrics surfaced (OpenTelemetry, Application Insights, Datadog, or equivalent) — at least request counts and latencies.
- Health-check endpoints exposed.

### Secrets management

- Secrets not in committed config.
- Per-environment secrets via the hosting platform's app-settings or a secret manager.
- Secret placeholders in committed schema/config artifacts (e.g., `$OpenAI:ApiKey`) — never raw values.

### CI/CD

- A CI pipeline (`.github/workflows/`, `.gitlab-ci.yml`, `azure-pipelines.yml`, `bitbucket-pipelines.yml`, etc.) runs on every push.
- Build + test + lint at minimum. Deploy automation present when the platform supports it.
- A pre-commit hook (`.githooks/`, `husky`, `pre-commit` framework) catches common issues before push.

### Environment parity

- `appsettings.{Development,Staging,Production}.json` (or equivalent) capture per-environment values.
- Development environment is bootable on a fresh clone without a long-tail of out-of-repo configuration steps.
- Database / storage state is reproducible — migrations versioned, seed data documented.

## What "bad" looks like

- `catch (Exception) { /* eat */ }` in business paths.
- Outbound HTTP calls without timeouts or retry policy.
- `Console.WriteLine` instead of structured logging.
- Secrets in committed `appsettings.*.json` (especially `*Development*.json` if it's committed).
- No CI pipeline visible.
- "Works on my machine" symptoms: undocumented env vars, hard-coded local paths, no clear bootstrap path.

## Detection recipes

```bash
# Swallowed exceptions
grep -rEn "catch\s*\(\s*Exception[^)]*\)\s*\{[^}]*\}" <target>/src --include="*.cs"

# Polly / retry policy
grep -rn "AddPolicyHandler\|Polly\.\|RetryAsync\|CircuitBreaker" <target>/src --include="*.cs" --include="*.csproj"

# HTTP timeouts
grep -rn "HttpClient\|TimeSpan\.FromSeconds\|TimeSpan\.FromMinutes" <target>/src --include="*.cs"

# Structured logging
grep -rn "Serilog\|UseSerilog\|ILogger<" <target>/src --include="*.cs"

# OpenTelemetry / metrics
grep -rn "OpenTelemetry\|Application[Ii]nsights\|Datadog\|UseExceptionHandler" <target>/src --include="*.cs"

# Health checks
grep -rn "AddHealthChecks\|MapHealthChecks" <target>/src --include="*.cs"

# CI configs
for d in .github/workflows .gitlab-ci.yml azure-pipelines.yml bitbucket-pipelines.yml .circleci; do
  test -e "<target>/$d" && echo "present: $d"
done

# Pre-commit hooks
test -d "<target>/.githooks" && echo "present: .githooks/"
test -f "<target>/.husky" && echo "present: .husky/"
test -f "<target>/.pre-commit-config.yaml" && echo "present: .pre-commit-config.yaml"

# Env-specific config files
ls <target>/src/**/appsettings.*.json 2>/dev/null

# Secrets in committed config (sensitive — only print presence/absence)
if grep -rEln "(sk-[A-Za-z0-9]{20,}|ANTHROPIC_[A-Z]+|AKIA[0-9A-Z]{16}|password\s*=\s*\"[^\"$]{4,})" <target>/src 2>/dev/null; then
  echo "SECRETS DETECTED IN SOURCE — investigate carefully"
fi
```

## Lifecycle-stage adjustments

- **Greenfield**: Recommend setting up CI, pre-commit hooks, and Serilog *now*. They become 10× harder to retrofit later. Adding Polly later is cheaper than CI later.
- **Growing**: If CI is missing, that's a P0 regardless of stage. If observability is "ILogger only," recommend adding metrics + correlation IDs as a P1.
- **Mature**: Don't recommend ripping out a working logging stack. Audit retry/timeout coverage on outbound calls (often the hidden weakness in mature codebases). Recommend health-check endpoints if absent.
- **Brownfield**: Resilience audit is *especially valuable* — older codebases often have heroic error suppression that the new owner needs to know about. Map the swallowed-exception sites before recommending changes.

## Special note: secrets

The audit must flag any secret pattern detected in committed source, but must not *print the secret value* in the report. The report should say "secret detected in <file>" with the line number, not the secret itself.

If the detection scan returns matches, this is the highest-severity finding the skill can produce. Surface it before any other recommendation.

## Cite canonical sources

- Polly documentation (resilience patterns)
- OpenTelemetry .NET documentation
- Microsoft Learn — Health checks in ASP.NET Core
- The Twelve-Factor App methodology
