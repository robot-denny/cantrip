# Pillar 1: Modern platform hygiene — the .NET form

Version-agnostic signals for the quality of the .NET foundation. Things that hold across .NET 6, 7, 8, 9, 10+.

## What "good" looks like

- DI is the default seam for cross-cutting concerns. Services are registered in one cohesive place — program startup, or whatever registration seam the application framework on top adds — not scattered.
- `async` / `await` used consistently. `Task` returned from async methods; no `.Result` / `.Wait()` blocking on async code; `CancellationToken` accepted at API boundaries that could take time.
- Configuration lives in `appsettings.*.json` (or `IOptions<T>` strongly typed). Secrets are *not* in committed config — they come from environment variables, user secrets, or a secret manager.
- Logging is structured (Serilog, `ILogger<T>`). Not `Console.WriteLine` and not string-concatenated log messages with PII risk.
- NuGet versions are pinned to specific majors and minors. Floating ranges (`*` or `>=`) are flagged unless deliberately documented.
- The project compiles with nullable reference types enabled and `<TreatWarningsAsErrors>true</TreatWarningsAsErrors>` (or close to it).
- `.editorconfig` defines mechanical style; no ad-hoc reformat wars.
- A `Directory.Build.props` / `Directory.Packages.props` exists when multiple `.csproj` files share settings — central package management is a positive signal in multi-project solutions.

## What "bad" looks like

- Service registration sprawled across files with no obvious owner.
- Async methods that don't accept `CancellationToken` at long-running boundaries.
- `task.Result` / `task.Wait()` in non-startup, non-test code.
- Secrets pasted into `appsettings.json` or `appsettings.Development.json` committed to git.
- `Console.WriteLine` in production paths.
- Wildcard NuGet version ranges (`<PackageReference Version="*" />`) without a documented reason.
- Nullable disabled or warnings ignored.
- No `.editorconfig`.

## Detection recipes

```bash
# Find startup wiring
grep -rln "AddSingleton\|AddScoped\|AddTransient\|builder\.Services\." <target>/src --include="*.cs" | head

# Find registration seams the framework on top adds (where the project has installed
# guidance for its framework, take the interface name to grep for from there)
grep -rln "IServiceCollection " <target>/src --include="*.cs"

# Async blocking smells
grep -rEn "\.Result\b|\.Wait\(\)" <target>/src --include="*.cs" --exclude-dir=obj --exclude-dir=bin

# Console writes in non-startup, non-test
grep -rln "Console\.WriteLine" <target>/src --include="*.cs"

# Nullable enable status
grep -rln "<Nullable>" <target>/src --include="*.csproj"

# Wildcard versions
grep -En 'Version="\*"|Version=">' <target>/**/*.csproj

# Editorconfig presence
test -f <target>/.editorconfig && echo "present" || echo "missing"

# Central package management
test -f <target>/Directory.Packages.props && echo "central" || echo "per-project"
```

## Lifecycle-stage adjustments

- **Greenfield**: enabling nullable, `<TreatWarningsAsErrors>`, and central package management are *cheap P0s*.
- **Growing**: blocking async calls are *P1s* — they compound under load.
- **Mature**: don't propose ripping out structured logging if `ILogger` is in use but not Serilog; the leverage isn't worth the churn. Focus on the highest-frequency hot paths.
- **Brownfield**: don't make recommendations here until you've understood *why* a pattern is in place. Older codebases often have legitimate reasons for `.Result` (sync interop boundaries).

## Detection recipes for the seam references

The stack-agnostic references — `lifecycle-stages.md`, `scoring-rubric.md`,
`documentation-and-onboarding.md`, `resilience-and-ops.md` — state their judgement criteria in
technology-neutral terms, so the same criteria can be reused on a stack that is not .NET.

**A detection recipe cannot be technology-neutral and still be useful.** It has to name the
identifiers it looks for. `grep -rniE "logger|logging"` matches nearly every file in nearly every
codebase; `grep -rn "Serilog\|UseSerilog\|ILogger<"` finds the thing you asked about. So the
recipes live here, on the .NET side of that seam, and the criteria live there.

Every recipe takes `<target>` as the repository root.

### Resilience and operations

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

### Documentation and onboarding

```bash
# Agentic-collaboration docs
for f in CLAUDE.md AGENTS.md AGENT.md CONVENTIONS.md .github/copilot-instructions.md; do
  test -f "<target>/$f" && echo "present: $f"
done
test -d "<target>/.claude/commands" && echo "present: .claude/commands/"
test -d "<target>/.claude/agents"  && echo "present: .claude/agents/"
test -d "<target>/.claude/skills"  && echo "present: .claude/skills/"
test -d "<target>/.cursor"          && echo "present: .cursor/"
test -d "<target>/.aider"           && echo "present: .aider/"

# ADR locations
for d in docs/adr adr decisions RFCs RFCS; do
  test -d "<target>/$d" && echo "present: $d/"
done

# Spec/plan/feature folders
for d in _specs specs docs/specs _plans plans docs/plans _features features docs/features _prds prds; do
  test -d "<target>/$d" && echo "present: $d/"
done

# Glossary / domain language docs
for f in GLOSSARY.md CONTEXT.md DOMAIN.md docs/glossary.md docs/context.md; do
  test -f "<target>/$f" && echo "present: $f"
done

# README quality (length is a weak signal but worth knowing)
wc -l "<target>/README.md" 2>/dev/null

# XML doc comments on public APIs
grep -rln "/// <summary>" <target>/src --include="*.cs" | wc -l

# OpenAPI / Swagger
grep -rn "AddSwaggerGen\|AddOpenApi\|Swashbuckle" <target>/src --include="*.cs" --include="*.csproj"
```

## Cite canonical sources

When the report calls out a recommendation, cite the canonical doc (don't paraphrase it) — links like:
- Microsoft Learn — Dependency injection in ASP.NET Core
- Microsoft Learn — Async programming best practices
- Microsoft Learn — Configuration in ASP.NET Core
- Microsoft Learn — Logging in .NET
