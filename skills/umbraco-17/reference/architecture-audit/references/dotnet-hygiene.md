# Pillar 1: Modern .NET Hygiene

Version-agnostic signals for the quality of the .NET foundation. Things that hold across .NET 6, 7, 8, 9, 10+.

## What "good" looks like

- DI is the default seam for cross-cutting concerns. Services are registered in one cohesive place (program startup or `IComposer`s in Umbraco), not scattered.
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

# Find Composers (Umbraco DI extension)
grep -rln "IComposer\|: ComposeAfter" <target>/src --include="*.cs"

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

## Cite canonical sources

When the report calls out a recommendation, cite the canonical doc (don't paraphrase it) — links like:
- Microsoft Learn — Dependency injection in ASP.NET Core
- Microsoft Learn — Async programming best practices
- Microsoft Learn — Configuration in ASP.NET Core
- Microsoft Learn — Logging in .NET
