# Pillar 4: Headless Suitability

Reports the codebase's *current orientation* (traditional / hybrid / headless) and its *migration readiness* (well-positioned / neutral / firmly traditional) for a future headless move.

## Orientation: how to classify

### Traditional

- All (or nearly all) rendering happens server-side via Razor templates.
- No Delivery API surface exposed.
- No separate frontend project consuming Umbraco content.
- Content access patterns assume MVC view models (`IPublishedContent`, `UmbracoViewPage<T>`).

### Hybrid

- Razor templates still render the main site.
- *Some* content is exposed via Delivery API, custom API controllers, or GraphQL middleware for use by a SPA component, mobile app, or partner integration.
- Frontend may still ship some MVC pages but also includes a TypeScript/Vite-built widget or two.

### Headless

- Razor templates are minimal or absent; the rendered site is a separate frontend project (Next.js, Astro, Nuxt, etc.).
- Delivery API or Management API is the primary content surface.
- Backoffice serves as a content authoring tool only; presentation has no MVC role.

## Migration readiness: how to assess

For codebases currently in **traditional** or **hybrid** orientation, the audit reports how *positioned* they are for a future headless move on a three-step scale:

| Rating | Signals |
|---|---|
| **Well-positioned** | Content fetches in Razor go through services or extension methods (not direct DB queries). Block components are pure-display (no business logic). Models are typed. View models are separated from `IPublishedContent`. The Delivery API is already enabled or trivially enableable. |
| **Neutral** | Some leakage of Umbraco APIs into business logic; would require non-trivial refactoring at content-access seams before headless would be clean. Block components have mild conditional/business logic. |
| **Firmly traditional** | Razor templates encode significant business logic. Direct `IPublishedContentQuery` / examine queries in views. Display assumes server-side composition. Going headless would be a near-total rewrite. |

## Positive signals (well-positioned)

- Delivery API is enabled (or its presence in the project's package list is detected).
- Content access is mediated through services or repositories — Razor templates use injected helpers, not direct queries.
- View models exist alongside `IPublishedContent` (separation of read model from CMS model).
- Block components are *pure* presentation: they receive data, they render markup, they don't fetch.
- The frontend has a JS/TS build step (Vite, esbuild, Webpack) — signals that a partial-decoupling already exists.
- API controllers or minimal-API endpoints exist that expose content. These are the seeds of a headless surface.
- Models Builder is set to source-generated mode (vs. in-memory) — types are accessible to other consumers.

## Negative signals (firmly traditional)

- Razor templates execute multiple content queries with branching logic.
- Business rules (eligibility, pricing, conditional content visibility) live in templates.
- No JS/TS build step exists; all interactivity is jQuery snippets embedded in Razor.
- Models are used only via `dynamic` (`Umbraco.AssignedContentItem.Property`) — no typed access.
- Cross-cutting view logic depends on `HttpContext` access inside partials.

## Detection recipes

```bash
# Delivery API enablement
grep -rn "DeliveryApi" <target>/src --include="*.cs" --include="*.json"

# JS/TS build presence
find <target> -maxdepth 3 -name "package.json" -not -path "*/node_modules/*"
find <target> -maxdepth 3 -name "vite.config.*" -o -name "webpack.config.*"

# Multiple content queries in single view (smell)
grep -rEn "ContentCache\.|PublishedContentQuery\.|Umbraco\.Content\(" <target>/src --include="*.cshtml" | \
  cut -d: -f1 | sort | uniq -c | sort -rn | head

# Business logic in templates (heuristic: if statements counted per view)
for f in $(find <target>/src -name "*.cshtml"); do
  count=$(grep -c "^\s*@if\|^\s*if (" "$f" 2>/dev/null || echo 0)
  echo "$count $f"
done | sort -rn | head

# Frontend project siblings (decoupled UI)
find <target> -maxdepth 2 -type d \( -name "frontend" -o -name "web" -o -name "ui" -o -name "client" \)

# Dynamic content access (less type-safe, harder to expose headless)
grep -rln "dynamic " <target>/src --include="*.cshtml"
```

## What the report should produce for Pillar 4

A dedicated **Headless trajectory** subsection in the report:

```
### Headless trajectory

- **Current orientation**: <traditional | hybrid | headless>
- **Migration readiness**: <well-positioned | neutral | firmly traditional>
- **Migration cost estimate** (if user moved toward headless tomorrow):
  - <S/M/L> for content access refactoring
  - <S/M/L> for business logic extraction from templates
  - <S/M/L> for frontend rewrite
- **Key changes that would be required**:
  - ...
- **What you'd want to preserve**:
  - ...
```

## Lifecycle-stage adjustments

- **Greenfield**: If the user has *any* aspiration toward headless, recommend they start with the seams in place — even if they choose to render server-side initially. Cheap to do now, painful later.
- **Growing**: If orientation is hybrid and trending more headless, recommend formalizing the boundary now. If trending more traditional, just note it.
- **Mature**: Firmly-traditional mature codebases are usually *fine* — don't recommend a headless migration the user didn't ask for. Just rate the readiness honestly.
- **Brownfield**: Do not recommend going headless. Note the orientation and readiness. Let the new owner decide based on business needs.

## Cite canonical sources

- Umbraco Delivery API documentation
- Umbraco Headless / Heartcore documentation (where applicable to the version)
- Jamstack architectural overviews
