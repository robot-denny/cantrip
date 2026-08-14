---
name: dotnet-conventions
description: Modern C# and .NET authoring conventions — naming and casing by code element, async and `CancellationToken` discipline, structured logging with `ILogger`, `System.Text.Json` serialization and camelCase DTOs, nullable reference types, and the modern syntax that is now the default (collection expressions, primary constructors, target-typed `new`, records). Consult whenever writing or refactoring a `.cs` or `.csproj` file, or planning a step that adds a service, DTO, endpoint, controller, or record — including when the request only says "add a service" and never mentions C# or .NET at all.
---

# Writing C# and .NET

Per-file authoring guidance: what should be true of the `.cs` or `.csproj` file you are about to write or
change. This file is deliberately opinionated about the platform's own defaults and deliberately silent
about the choices a project owns. **The resolution order below is what makes those two halves safe to
hold at once** — without it, every asserted default becomes an argument with a project that decided
otherwise.

## What this owns, and what it does not

| Concern | Where it lives |
|---|---|
| Is this repo's .NET foundation sound? DI wiring, package pinning, config and secrets posture, lifecycle-staged priorities, the evidence a score rests on | a repo-level .NET architecture audit, where one is installed — `architecture-audit` is one such reference. Where none is, that question is simply out of scope here rather than answered here |
| Is this file, this method, this change correct and idiomatic? | here |
| What makes something a defect at all — an error passed on with its origin lost, a log call that folds its values into the message, an unvalidated input | core's reviewer guidance. This file supplies the **C# form** of those defects, not the argument for why they matter |
| What to look for in a C# diff, and at what severity | `dotnet-review-rules`, where it is installed. Where it is not, a reviewer falls back to its own checklist and to core's — this file is not a substitute for either |

The dividing line for the first row is repo-level versus per-file: **an audit asks whether the
foundation is sound; this file asks whether the code in front of you is right.** Where both could speak,
defer rather than restate — two installed files disagreeing about the same rule is worse than either
being absent.

## Where a convention comes from

Everything asserted below is a **default, not a mandate.** Resolve each one in this order and stop at the
first rung that answers:

1. **`.editorconfig`, where it speaks.** Machine-checkable, already in the repo, and read by the same
   analyzers that will judge the code. For declaration style that is literally
   `csharp_style_var_*`; for namespace form, `csharp_style_namespace_declarations`. Read the answer
   rather than assuming one.
2. **A decision the project recorded** in its own configuration (the slot below).
3. **This file's default**, when neither of the above answered.
4. **The dominant style of the file you are in**, when even that does not fit.

**This order arbitrates shape, not correctness.** It governs how code is *formed* — declaration style,
namespace form, ordering, sealing. It is not a general override chain: an interpolated log message still
loses its fields, `throw ex;` still resets the stack trace, and an unvalidated payload is still
unvalidated, whatever any configuration file says. Those are not defaults that yield, and treating the
order as though they were turns it into a way to opt out of correctness.

Casing by code element sits with them. A formatter can encode it and a project can override it, but the
convention is platform-wide rather than local taste, so this file states it outright rather than offering
it as a default to be settled per project.

**Slot:** `.agents/config/conventions.md` → `## .NET style decisions`
**If empty:** apply the resolution order above — `.editorconfig` first, then this file's defaults, then
the dominant style of the surrounding file. Do not assert a convention you cannot evidence, and do not
reformat conforming code to a preference nothing in the project states.
**Detect:** read `.editorconfig` first — its `csharp_style_*` and `dotnet_naming_*` keys settle whatever
they set, and nothing below needs checking for those. For what remains unset, sample rather than exhaust:
across roughly fifty `.cs` files, the ratio of `var` to explicit local declarations, whether types carry
`sealed`, and whether static fields carry a prefix. A margin past about four to one is already the
answer; anything closer is genuinely mixed and belongs in the fallback's hands, not asserted.

## Naming, by code element

These are .NET-wide conventions rather than preferences, which is why a reviewer can cite them without
arguing. They exist so a reader can tell what a name *is* without looking it up.

| Element | Form |
|---|---|
| Types, records, enums, methods, properties, events, namespaces | `PascalCase` |
| Interfaces | `I` prefix, then `PascalCase` |
| Generic type parameters | `T`, or `TSomething` when there are several |
| Parameters and locals | `camelCase` |
| Private and internal instance fields | `_camelCase` |
| Constants | `PascalCase` |
| Methods returning `Task`, `Task<T>`, or `ValueTask<T>` | `Async` suffix |

The `Async` suffix earns its place because it is the only signal at the call site that a result must be
awaited — a forgotten `await` on a well-named method is visible, on a badly named one it is not.

**Prefer a property to a public field.** A public field cannot be made virtual, cannot carry validation
or a computed value later, and changing it into a property is a binary-breaking change. The rule is
therefore *use a property*; how a public field ought to be cased is a detail of something to avoid
rather than a convention worth having.

**Name constants instead of repeating literals.** A configuration key, a role name, a cache key, or a
route fragment written twice will eventually be written differently, and nothing fails at the point of
divergence — the second one just quietly stops matching. A named constant or an enum makes the mismatch
a compile error.

## Log with named placeholders, not interpolation

`logger.LogInformation("Order {OrderId} failed after {Attempts}", orderId, attempts)` writes `OrderId`
and `Attempts` as queryable fields. `logger.LogInformation($"Order {orderId} failed after {attempts}")`
writes one opaque string, and the data you actually wanted to filter on is gone by the time you need it.
Interpolation also formats eagerly — the cost is paid even when the level is disabled and the message is
discarded.

```csharp
// Loses the fields
_logger.LogWarning($"Import of {fileName} skipped {skipped} rows");

// Keeps them
_logger.LogWarning("Import of {FileName} skipped {SkippedRows} rows", fileName, skipped);
```

Placeholder names are `PascalCase` and positional: the *name* labels the field, the *order* binds the
argument, so reordering the arguments silently relabels the data.

The same reasoning rules out `Console.WriteLine` in a production path: it has no level, no scope, and no
structure, so nothing downstream can route or filter it.

**A value that should not be logged at all is a different problem.** Moving a credential or a personal
detail out of the message and into a named field does not fix it — it makes it a structured, indexed,
queryable leak. Remove it.

## Catch to do something, and rethrow without erasing the origin

```csharp
// Before — two defects in five lines
try
{
    await _payments.CaptureAsync(orderId, cancellationToken);
}
catch (Exception ex)
{
    _logger.LogError(ex, "Capture failed");
    throw ex;
}
```

`throw ex;` restarts the stack trace at the rethrow, so the frame that actually failed is gone and
whoever debugs it later lands on this handler with no trail back. And a catch block whose only actions
are *log* and *rethrow* should usually not exist: every layer that does this logs the same failure
again, so one fault produces a stack of near-identical entries and no layer's entry is the authoritative
one.

```csharp
// After — the call site says what it does, and the failure travels intact
await _payments.CaptureAsync(orderId, cancellationToken);
```

Catch where you can genuinely do something — handle the failure, retry it, or translate it into a
domain-level error. When you translate, pass the original as the inner exception so the origin survives:

```csharp
catch (HttpRequestException ex)
{
    throw new PaymentCaptureFailedException(orderId, ex);   // origin preserved as InnerException
}
```

Where a bare `throw;` is right, use it rather than `throw ex;` — it preserves the original stack trace.
And returning a deliberately sanitized message to an external caller is not this defect at all, so long
as the real origin is still recorded internally.

## Async all the way down, and cancellable at the boundary

An `async` method should be awaited by an `async` caller, up to whatever framework entry point started
the call. Blocking on a `Task` in the middle of that chain consumes a thread-pool thread that is doing
nothing but waiting, and in any context with a synchronization context it can deadlock outright.

**`.Result`, `.Wait()`, and `.GetAwaiter().GetResult()` all block.** They are not three options of
varying safety: `.GetAwaiter().GetResult()` differs only in rethrowing the original exception instead of
wrapping it in an `AggregateException`. It is **not** a deadlock escape hatch, and reaching for it
because a call chain is inconveniently synchronous only relocates the problem. Make the caller async
instead.

**`async void` is unawaitable and swallows its own failures.** A caller cannot await it, so nothing can
sequence after it or observe that it finished; and an exception thrown inside it does not surface to the
caller at all — it reaches the synchronization context, which in a server process usually means the
process. `async Task` is the same code with a return type someone can act on. The one genuine exception is
an event handler whose signature you do not control.

**Accept a `CancellationToken` on public async methods and pass it onward** wherever the API you call
takes one — HTTP calls, database commands, streams, queue reads. A token that is accepted and then
dropped is worse than one that was never there, because the signature promises cancellation the
implementation does not deliver. Framework entry points supply one; take it and thread it through rather
than defaulting to `CancellationToken.None`.

## Nullability is a compile-time contract, so enable it fully

Set `<Nullable>enable</Nullable>` in the project file (or once in `Directory.Build.props` for a
multi-project solution), and mark what may be absent as `string?`. Half-enabled is the state worth
avoiding: `warnings`-only, or a few `#nullable enable` islands in an otherwise disabled project, produces
warnings nobody can act on across the whole codebase and protects none of it. The value comes from the
compiler being able to trust the annotations, which requires them everywhere.

`IsNullOrWhiteSpace` is the better **default** over `IsNullOrEmpty` — a value that is present but blank
almost always means the same thing to the caller as one that is absent. It is a default and not an
always: where whitespace is significant the two differ meaningfully, and using the wrong one is a
behavior change rather than a style choice.

## Serialize with one library, or attribute for both

`System.Text.Json` is the platform default and the serializer ASP.NET Core uses, so prefer it for new
work. On a genuinely high-throughput path, or anywhere trimming or ahead-of-time compilation is in play,
a source-generated serializer context is the faster and better-supported form than the reflection-based
default — worth knowing the option exists before a hot endpoint is written without it. Where a dependency drags Newtonsoft.Json in as well, the danger is a DTO carrying attributes for
only one of them:

```csharp
// Before — shape depends on which serializer happens to run
public record ContactDto
{
    [JsonPropertyName("emailAddress")]   // System.Text.Json only
    public required string EmailAddress { get; init; }
}
```

Serialized by `System.Text.Json` this emits `emailAddress`; serialized by Newtonsoft it emits
`EmailAddress`. Nothing throws — the far side simply reads a null for a field it could not match, which
surfaces as a data bug a long way from its cause.

```csharp
// After — one name, whichever serializer runs
public record ContactDto
{
    [System.Text.Json.Serialization.JsonPropertyName("emailAddress")]
    [Newtonsoft.Json.JsonProperty("emailAddress")]
    public required string EmailAddress { get; init; }
}
```

Better still, remove the ambiguity: keep one serializer, or configure a camelCase naming policy once at
startup so individual DTOs need no attributes at all. Attribute pairing is the fix for a codebase that
genuinely has both in play, not a target state.

**Validate what arrives from outside the process, at the boundary.** A DTO bound from a request body,
query string, or queue message is untrusted input, and validating it at the entry point keeps every
service behind that point able to assume a valid value. *Which* mechanism — data annotations, a
validation library, or explicit guard clauses — is the project's call, not this file's.

## Records where the data is immutable

A record (C# 9+) exists for value equality and `with`-expressions, not for brevity. Reach for one when you would
otherwise hand-write `Equals`, `GetHashCode`, and a copy constructor — a DTO, a query result, a
configuration binding, a value object. A record whose properties are all settable gets you the
declaration form without the guarantee, which is the worst of both.

One cost worth knowing before a record becomes a dictionary key or gets compared inside a loop: the
generated `Equals` and `GetHashCode` are structural, walking every public property on every call. That is
the behaviour you asked for, and it is not free.

## The modern syntax that is now the default

Modern syntax, with one precondition: **check the project's target framework and `<LangVersion>` before
using it.** On a project targeting an older framework these do not compile, and the older form there is
correct rather than stale.

**Collection expressions** (C# 12+) replace the repetition of stating a collection type twice:

```csharp
// Before
private static readonly string[] Roles = new string[] { "editor", "administrator" };
List<int> ids = new List<int>();

// After
private static readonly string[] Roles = ["editor", "administrator"];
List<int> ids = [];
```

**Target-typed `new()`** (C# 9+, so it is available well before the two above) does the same for a
single object where the type is already on the left:
`Dictionary<string, List<int>> index = new();`

**Primary constructors** (C# 12+) remove the parameter-plus-field-plus-assignment boilerplate from a
service whose constructor only stores its injected dependencies. One caveat that catches people: a
primary constructor parameter is a captured variable in scope for the whole type, **not** a `readonly`
field. Where you need it to be readonly, or need to guard the argument before storing it, declare the
field explicitly.

## One public type per file, named for the file

A reader who knows the type name should be able to find the file, which is the whole point. This is not
a rule about counting types: nested types, `file`-local types, and a small private companion class beside
the type that uses it all belong in the same file. What to avoid is two independently used public types
sharing a file, because then the filename stops predicting anything.

## What the project decides, and this file does not

Each of these is defensible in more than one direction, so **this file asserts no answer for any of
them.** Read the project's answer through the resolution order; where nothing answers, match the file you
are working in and do not raise it as a finding.

- **`var` versus an explicit type.** Style guides genuinely disagree and the platform takes no position.
  A codebase that is consistently one way should not acquire the other.
- **`sealed` by default.** There is a real devirtualization benefit, and a real cost: it blocks mocking
  of concrete classes and proxy-based ORM patterns. That makes it a policy, not a fact.
- **Member ordering and `using` placement.** Any consistent order works — constants → fields →
  constructors → properties → public methods → private methods is one common choice. State it in
  `.editorconfig` and let the analyzers hold it.
- **Which validation mechanism to use.** *Validate at the boundary* is the durable rule; the library is
  a project choice.
- **An `s_` prefix on static fields.** This is the `dotnet/runtime` repository's internal convention
  rather than general .NET guidance. Perfectly good house style; not a platform fact.
- **When a repeated expression earns a helper method.** Any numeric threshold is arbitrary, and the real
  question is whether the repetition has one name and one reason to change.

**Namespace form is deliberately not in this list**, and the distinction matters. File-scoped
namespaces arrived in C# 10, the SDK templates emit them, and they remove a level of indentation from
every file — so this file's **default** is file-scoped. But it is a default that yields at rungs 1 and 2
like any other. A project that prefers block-scoped for its diff behavior states that once, most likely
already in `.editorconfig`, and gets no argument. The difference between the two cases is having no
position at all versus having one that can be overruled.

### Where the formatter already decides

Casing, `using` placement, member ordering, and namespace form are enforced better by `.editorconfig`
plus the Roslyn analyzers than by re-deriving them from prose. **Where an `.editorconfig` speaks it is
the authority.** Do not reformat against it, and do not spend attention on something the formatter would
have fixed on save. The naming table above is here so a finding can be grounded in shared vocabulary —
not so this file can become a second formatter with a different opinion.

## What not to do

- **Do not rewrite conforming code** to a default here when `.editorconfig` or a recorded project
  decision already answered. That is the contradiction the resolution order exists to prevent.
- **Do not treat the resolution order as an opt-out from correctness.** It settles shape, never whether
  a defect is a defect.
- **Do not reach for `.GetAwaiter().GetResult()`** to escape a deadlock. It blocks exactly like
  `.Result`.
- **Do not add a catch block that only logs and rethrows**, and do not use `throw ex;` where `throw;`
  is meant.
- **Do not put the values inside the log message.** Pass them as named placeholder arguments.
- **Do not assume a newer form compiles.** Check the language version first — the forms here span
  C# 9 through C# 12, and they did not all arrive together.
- **Do not assert a convention this file leaves to the project.** Silence here is a decision, not an
  omission to fill in.
