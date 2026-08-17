# Pillar 2: Architectural Separation

Layering, depth, anti-corruption, and module organization. The vocabulary borrows from Clean Architecture (Bob Martin), DDD (Eric Evans), and Ousterhout's *A Philosophy of Software Design* (depth, leverage).

## What "good" looks like

- Code is organized to **resist coupling between layers**. A "layer" might be a folder (`Domain/`, `Application/`, `Infrastructure/`, `Presentation/`), a project (separate `.csproj` per layer), or a vertical slice per feature (`Features/Articles/`). All three are valid; what matters is that dependencies flow inward (or one direction).
- Third-party SDKs — a CMS, a payment provider, a model vendor's client — are **wrapped in anti-corruption interfaces** at module seams. The codebase's own domain code doesn't call the vendor's query type everywhere; it goes through a repository or gateway interface of its own that abstracts the dependency.
- **Module depth** is favored — small interfaces that hide significant implementations. A `IPaymentProcessor` with one `Charge(amount)` method that internally handles retries, idempotency, and provider fallback is *deep*. A class with 30 public methods that each do one tiny thing is *shallow* — and should be flagged.
- **Domain models carry behavior**, not just data. A `Order` class with `CanRefund()` and `MarkShipped()` methods beats an anemic `OrderDto` with bare properties. (Exception: read-side projections and view models are *supposed* to be anemic.)
- **Feature folders or vertical slices** are present when the domain is non-trivial. Cross-cutting concerns (auth, logging) stay in technical folders.
- The **dependency rule** is observable: domain references nothing; application references domain; infrastructure references both but is referenced by nothing inward.

## What "bad" looks like

- View templates directly invoke vendor SDK clients, data-access types, or static helpers that read globals. The view becomes a coupling sink.
- Service classes named `*Manager` / `*Helper` / `*Utils` with grab-bag methods. Often shallow modules.
- A `Models/` or `DTOs/` folder full of anemic classes plus a parallel `Services/` folder where all the behavior lives. Anemic domain anti-pattern.
- Domain code references `Microsoft.AspNetCore.*`, or the root namespace of whatever framework sits on top, directly. The dependency rule is broken.
- Cyclic project references (one of the worst smells — leads to god projects).

## The deletion test (Ousterhout-inspired)

For any module / interface / class that *seems* questionable: ask, "If I deleted this and inlined its callers, would complexity *concentrate* (good — the module was earning its keep) or merely *move* (bad — the module was shallow)?" Suspected shallow modules are candidates for inlining or merging.

Use this lens for recommendations. Don't propose creating new modules without naming the leverage they buy.

## Detection recipes

```bash
# Project structure
find <target>/src -maxdepth 3 -name "*.csproj"

# Layer folders within a single project
find <target>/src -maxdepth 3 -type d -name "Domain" -o -name "Application" -o -name "Infrastructure" -o -name "Presentation" -o -name "Features" -o -name "UseCases"

# View templates calling the framework's APIs directly (coupling sink).
# <FrameworkNamespace> is the root namespace of the framework on top; where the project has
# installed guidance for that framework, take the namespace from there.
grep -rln "<FrameworkNamespace>\." <target>/src --include="*.cshtml" | head

# Manager/Helper/Utils smell
find <target>/src -type f -name "*Manager.cs" -o -name "*Helper.cs" -o -name "*Utils.cs" | head

# Static classes (often grab-bag containers)
grep -rln "public static class" <target>/src --include="*.cs"

# Dependency rule check: do domain/business folders reference web/MVC types?
grep -rln "using Microsoft.AspNetCore\|using <FrameworkNamespace>" <target>/src/**/Domain/ 2>/dev/null
```

## Lifecycle-stage adjustments

- **Greenfield**: Recommend a minimal layering plan now (even if it's just `Web/Domain/Infrastructure` folders inside one project). Cheap.
- **Growing**: Identify the first place where coupling has begun to hurt (e.g., a partial that's accumulated three different data fetches). Suggest extracting the seam.
- **Mature**: Avoid recommending full Clean Architecture refactors. Look for one high-leverage seam to introduce — usually an anti-corruption interface around a third-party dependency that's painful to test.
- **Brownfield**: Map first. Recommend introducing a single seam only after understanding the existing coupling pattern. Premature refactoring of inherited code is the canonical brownfield mistake.

## When the framework itself couples the view to the data

Some frameworks — content-managed ones especially — intentionally encourage view-coupled data access, exposing the current record to the template as ambient state. **That is not automatically a smell; it is the framework's own seam,** and scoring it as a violation of the dependency rule produces a report the team will rightly ignore.

The audit's question is narrower: has *business logic* (not display logic) leaked into the view layer?

- Extension or helper methods that classify or read the current record for display are fine.
- Conditional logic that decides what to render based on several separate data queries is borderline.
- Direct database or search-index queries from a template are a clear smell in any framework.

Which of a framework's access patterns are idiomatic is a fact about that framework, not about this pillar. Where the project has installed guidance for its framework, defer to it for the idiomatic form and cite it; where it has none, say in the report that the framework's own conventions were not assessed.

## Cite canonical sources

- Robert C. Martin — *Clean Architecture*
- Eric Evans — *Domain-Driven Design*
- John Ousterhout — *A Philosophy of Software Design* (modules, depth, leverage)
- Vaughn Vernon — *Implementing Domain-Driven Design* (anti-corruption layer)
