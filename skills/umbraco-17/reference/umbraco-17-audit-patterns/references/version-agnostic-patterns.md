# Umbraco-version-appropriate patterns

Patterns that hold across Umbraco majors. Written as assessment guidance: positive signals, negative signals, and detection recipes for judging whether an existing Umbraco codebase follows the platform's own conventions. A repo-level architecture audit, where one is installed, is the natural consumer — it covers the .NET foundation and the structure around it and leaves framework-idiomatic use to guidance like this. Version-specific signals (which AI/Search/Deploy packages exist in vN, what's deprecated in vN+1, etc.) are *not* baked in here — they should be sourced from the installed Umbraco backoffice skills, the Umbraco MCP server, or the official docs for the detected major version.

## How to use this reference

1. Establish the major version first, because everything version-sensitive below depends on it:

   ```bash
   # Major version from the CMS package reference
   grep -rhoE 'Include="Umbraco\.Cms"[^>]+Version="[0-9]+' <target> --include="*.csproj" \
     | grep -oE '[0-9]+$' | head -1
   ```

   No match and no `Umbraco.*` package reference at all means this file does not apply. A `.umbraco`
   file at the repo root confirms an Umbraco Cloud project but does not reveal the major — ask.
2. Use this file's heuristics for the version-agnostic patterns below.
3. **If installed Umbraco backoffice skills or MCP are available**: prefer their version-current best-practice guidance for anything package-specific or version-sensitive (AI packages, Search, Deploy, Delivery API capabilities, Models Builder modes, Block Grid/List APIs).
4. **If they're not available**: degrade to the version-agnostic baseline below and note in the report that "version-specific Umbraco guidance was unavailable; falling back to general principles."

## Version-agnostic positive signals

### Composition

- `IComposer` implementations exist for cross-cutting service registration and notification handlers. Composition is the canonical Umbraco DI extension seam — using it well is a positive signal.
- Notifications (saved/published/etc.) handled through `INotificationHandler<T>` (in modern majors) or `INotificationAsyncHandler<T>` for async work. Not via legacy global event handlers.

### Content model

- Document types, data types, templates, and (where the version supports it) AI/search/agent entities are serialized to schema artifact files and committed to git. **Schema is treated as code** — that judgement is what this file asserts.
- Something checks for unexpected schema drift before it is committed, whether a hook or a dedicated check.
- Built-in entities are extracted at setup rather than left database-only, so the drift report means something.

**How schema artifacts actually behave — and how to clear drift that will not — is a subject of its own,
covered by dedicated Deploy guidance where installed.** This file judges whether the discipline is in
place; it deliberately does not restate the mechanics.

### Block patterns

- Block List components live in `Views/Partials/blocklist/Components/` (or the version's equivalent path). Block Grid layouts in their own folder.
- Each block has a focused partial with a single responsibility — no god-block partials that render five different shapes based on conditionals.

### Content access

- `IPublishedContentQuery` is used for queries; results are typed (auto-generated `Umbraco.Cms.Web.Common.PublishedModels` classes) rather than passed around as `IPublishedContent`.
- Long content queries are not done inline in Razor — they go through extension methods, a service, or a View Component. Display-level access in Razor is fine.

### Caching

- Navigation, footer, and other expensive partials use `Html.CachedPartialAsync` (or version equivalent) with explicit cache durations. No silent 24-hour assumptions.
- Cache keys account for member context where personalization is in play.

### Members

- Member roles wired through composers + notification handlers (e.g., auto-assignment on save).
- Public access rules expressed in code/schema, not pasted into the backoffice UI by hand on each environment.

### Configuration & secrets

- Per-environment values in `appsettings.{Development,Staging,Production}.json`.
- Secrets referenced via placeholders (`$OpenAI:ApiKey` or environment variables), never pasted raw into backoffice forms (which encrypts them and breaks on Data Protection key rotation).
- Per-environment secret keys configured via the hosting portal's app-settings (double-underscore form for .NET Core when the portal rejects colons).

## Negative signals

- Service registration done in `Program.cs` instead of a Composer — fine for tiny projects, smelly for anything growing.
- Custom event handlers using legacy static event subscriptions.
- Schema artifacts committed inconsistently (some doc types as `.uda`, others created manually per environment).
- Built-in entity drift left unaddressed for months, so the drift report is noise nobody reads.
- Razor views with embedded SQL or `Examine` queries that should live in a service.
- Secrets pasted into backoffice connection forms.
- Long blocks of `if (Model.ContentType.Alias == "...") { ... } else if (...)` in templates — that's the property-editor switch the framework's `partialName` resolution is meant to handle.

## Detection recipes

```bash
# Composer presence and count
grep -rln "IComposer\|: ComposeAfter" <target>/src --include="*.cs"

# Notification handlers (modern Umbraco)
grep -rln "INotificationHandler\|INotificationAsyncHandler" <target>/src --include="*.cs"

# Schema artifact directory
find <target> -type d -name "Deploy" 2>/dev/null
find <target> -name "*.uda" 2>/dev/null | head

# Block partial organization
find <target>/src -type d -path "*/blocklist/Components*"
find <target>/src -type d -path "*/blockgrid*"

# Cached partials
grep -rln "CachedPartialAsync\|CachedPartial" <target>/src --include="*.cshtml"

# Direct examine queries from views (smell)
grep -rln "ExamineManager\|IExamineManager" <target>/src --include="*.cshtml"

# Secrets in committed config (informational — sensitive)
grep -rEln "(sk-[A-Za-z0-9]{20,}|ANTHROPIC_[A-Z]+|AKIA[0-9A-Z]{16})" <target>/src 2>/dev/null
```

## Lifecycle-stage adjustments

- **Greenfield**: Recommend the composer pattern from day one, and a pre-commit schema-drift check from day one. Set up secret-placeholder discipline before the first AI connection is made (saves a Data-Protection-key incident later).
- **Growing**: If composer adoption is partial, recommend consolidating service registration there. If drift is appearing, address built-in entity extraction once.
- **Mature**: Don't recommend a wholesale composer migration if `Program.cs` registration is working. Focus on schema-drift hygiene and cache strategy review.
- **Brownfield**: Pay close attention to schema discipline. Drift in an inherited Umbraco codebase is one of the highest-risk areas, and the remediation is a subject of its own — defer to Deploy guidance where installed rather than improvising.

## Cite canonical sources

- Umbraco Documentation for the detected major version (umbraco.com/docs)
- For anything schema-artifact or deployment specific, the Deploy guidance installed alongside this pack, and failing that the vendor's own Deploy documentation
