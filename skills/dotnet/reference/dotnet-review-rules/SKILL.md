---
name: dotnet-review-rules
description: What to check when reviewing a C# or .NET diff — the rethrow and swallowed-exception patterns that destroy stack traces, interpolated log messages that defeat structured logging, async paths that block or drop cancellation, unvalidated payloads on endpoints, nullability gaps that warn without protecting, and how to tell a real defect from a house-style preference the project owns rather than the toolkit. Consult when reviewing a diff that touches `.cs`, `.csproj`, or `appsettings` files.
---

# Reviewing C# and .NET code

Supplements the generic reviewer checklists with the C# form of what they already describe. Everything
here is additive — the `reviewer-discipline` contract still governs scope, severity, evidence, and
report structure, and core's own checklist still owns whether something is a defect at all.

**The facts behind these checks live in `dotnet-conventions`, where it is installed.** This file says
*what to look for in a diff and how severe it is*; that one says *why each rule is true* and which
style questions a project owns rather than the toolkit. Consult it rather than re-deriving, and cite
it when a finding rests on platform behavior rather than on the diff alone — "this resets the stack
trace" is a claim a reader will want backing for. Where it is **not** installed, every check below
still stands, but two things go missing: the order that decides whether a style difference is a
finding at all, and the single list of contested items this file refuses to flag. A review running
without it should be correspondingly more reluctant to raise anything about the *shape* of the code.

## Where the severity comes from

Use the shared four-level scale and nothing else — `reviewer-discipline` defines the levels, and a
fifth one, a prefix, or a parallel scale cannot be merged with the other reviewers' output. Where a C#
diff most often lands:

- **Blocker** — an unvalidated value from outside the process reaching a query, a file path, an
  outbound URL, or unbounded work; a blocking call in a request path that can starve the thread pool
  under load.
- **Major** — a failure whose origin is destroyed, a response consumed without checking whether the
  call succeeded, a DTO whose serialized shape depends on which library happens to run.
- **Minor** — a log call nobody can filter afterwards, a null-forgiving operator standing in for a
  guard.
- **Nit** — an older form where a newer one is available and the project's language version supports
  it. Say it once, not per occurrence.

## Exceptions and error paths

**`throw ex;` where `throw;` was meant.** This is the C# form of an error passed onward with its
origin no longer recorded — core's own check, so report the form and the fix rather than re-arguing
the case. The fix is a bare `throw;`, or `throw new DomainException(..., ex)` where the failure is
being translated and the caught exception becomes the inner one. **Major.**

Two things that are *not* this finding: a `catch` returning a deliberately sanitized message to an
external caller, so long as the real origin is still recorded internally; and a `throw;` — which is
correct and needs no comment.

**A catch block whose only actions are log and rethrow.** Cite `dotnet-conventions` for why this
degrades a log rather than restating the reasoning here. This is a **second** finding on the same block when `throw ex;` is also present — two defects sharing
a line are two findings — and **Minor to Major** on its own depending on how many layers do it.

**`catch (Exception)` with an empty body, or one that returns a default.** Core owns swallowed
exceptions; what to look for in C# is the empty block, the `return null;` / `return default;` in a
handler, and the `catch` that filters nothing. Ask what the caller now sees, and say so in the
finding.

**A thrown exception carrying none of what failed.** `throw new InvalidOperationException("failed")`
in a handler discards both the origin and the diagnostic value. Name the argument that should be
carried through.

## Logging

**Values folded into the message text.** `_logger.LogWarning($"Import of {fileName} skipped {n} rows")`
is the C# form of core's check; the fix is
`_logger.LogWarning("Import of {FileName} skipped {SkippedRows} rows", fileName, n)`. Placeholder
names are PascalCase and bind **positionally**, so reordering the arguments silently relabels the
data — worth checking in the fix you propose as well as the code you flag. **Minor**, or **Major**
where the folded values are the ones an operator would need to diagnose the failure.

Two limits on this one. A message carrying no values has nothing to separate out and is not a finding.
And a value that should not be logged **at all** — a credential, a token, a personal detail — is
core's sensitive-data finding, where the fix is **removal**. Moving it into a named field makes it a
structured, indexed, queryable leak; do not propose that as the fix.

**`Console.WriteLine` in a production path.** No level, no scope, no structure, so nothing downstream
can route or filter it. **Minor**, and higher where it replaced a logger call in the same diff.

## Async and cancellation

**`.Result`, `.Wait()`, and `.GetAwaiter().GetResult()`.** All three block; the third differs only in
how it wraps the exception, so treat a comment claiming it avoids the deadlock as part of the finding
rather than a mitigation. **Major**, and **Blocker** in a request path. Core's quality checklist
carries synchronous blocking calls in an async context and the performance reviewer carries async
correctness; `reviewer-discipline` records that boundary as live and unassigned, so raise it where
your own checklist has it and check the merged report rather than assuming the other reviewer did.

**`async void`.** Unawaitable, so nothing can sequence after it or observe that it finished, and an
exception inside it does not reach the caller at all — it goes to the synchronization context, which in
a server process is a crash path. **Major**, and **Blocker** where the diff itself shows nothing between
the method and the process boundary that would catch it. Conditioning on what is visible matters: a
process-level guard is usually somewhere you cannot see from a diff, so assume one exists unless the
change is where it would have to be. The one exemption is an event handler whose signature the author
does not control — check before flagging.

**A missing or dropped `CancellationToken` on outbound and I/O-bound work.** Per
`reviewer-discipline`, cancellation and timeouts on that work are the **performance reviewer's**
finding, and this file supplies the idiom rather than a severity: the token belongs on the public
async signature, and it must be passed to the overload that takes one — `HttpClient`, database
commands, streams, queue reads. A token accepted and then not passed on is the easier of the two to miss, because the
signature promises what the implementation does not deliver, and it is easy to miss precisely because
the parameter is right there. In a merged report the quality reviewer does not also raise it; running
alone it raises what it would otherwise leave to another. Scope the finding to the outbound call you
can see in the diff.

**A response consumed without checking whether the call succeeded.** `await
response.Content.ReadFromJsonAsync<T>()` with no status check reads the error body as though it were
the payload, and `ReadFromJsonAsync` returns `null` for an empty body — so the null-forgiving operator
that silences the warning turns a failed call into a `NullReferenceException` somewhere else.
**Major.**

## Boundaries and payloads

**A DTO bound from outside the process and used without validation.** A `[FromBody]` parameter, a
query-string binding, a queue message: check that something between the entry point and the first
service call establishes the value is usable. `[ApiController]` returns 400 automatically only for
annotations that are actually present, so a DTO with no attributes and an action with no guard is
unvalidated however it is decorated. **Major**, or **Blocker** where the unvalidated value reaches a
query, a path, an outbound URL, or drives unbounded work.

**State that validation is missing; do not prescribe the mechanism.** Data annotations, a validation
library, and explicit guard clauses are all acceptable, and which one a project uses is on
`dotnet-conventions`'s list of decisions the project owns. A finding that requires a particular
library is a finding the project is right to reject.

**A collection or string bound from a request with no upper bound.** One request driving an
unbounded loop of outbound calls is the shape to watch for; it is both a validation finding and a
per-item-call finding, and the second is the performance reviewer's.

## Nullability and serialization

**`!` used to silence a warning the code has not answered.** The null-forgiving operator asserts to
the compiler what the diff does not establish. Ask what happens when the value genuinely is null, and
propose the guard instead. **Minor**, or **Major** where the dereference is on a path a request can
reach.

**Nullability half-enabled in a `.csproj` in the diff.** `warnings`-only, or a project where
annotations exist without `<Nullable>enable</Nullable>`, produces warnings nobody can act on and
protects nothing. **Minor**, and worth stating as one finding for the project file rather than per
annotation.

**A DTO carrying attributes for one serializer where two are in play.** The shape then depends on
which library runs, nothing throws, and the far side reads a null for a field it could not match.
**Major** — and cite `dotnet-conventions` for the mechanism, since it is not visible in the diff.

## What is not a finding

The half of a review that earns trust. A review that only ever adds findings will argue with a
project's own decisions on every diff, and a reader who has been argued with three times stops
reading.

**Style questions the project owns.** `dotnet-conventions` carries a single list of the style
questions it deliberately asserts no answer for. **Read it there and raise nothing on it.** That list
is not repeated here on purpose — two copies drift, and the copy a reviewer happens to read would then
be flagging something the pack has since stopped asserting. Where the surrounding code is consistently
one way, hold the diff to that and say nothing more.

**A style the project has already answered, even where it contradicts a default.**
`dotnet-conventions` states the order in which a convention resolves, and which sources count as an
answer; read it there rather than reconstructing it. The consequence for a reviewer is one line: where
the project has already answered, a finding against its answer is wrong even when a default differs.
Reading the repo's `.editorconfig` costs one file read, and it is not a scope violation — the scope
rule governs what you may *report on*, not what you may consult to judge what is in the diff.
Namespace form is where this comes up most — a repo whose `.editorconfig` sets
`csharp_style_namespace_declarations` has decided, and a review that raises it anyway will raise it
again on the next diff and the one after.

**What the formatter already enforces.** Where an `.editorconfig` plus the Roslyn analyzers hold a
mechanical rule, a reviewer re-deriving it from prose adds nothing and risks proposing a change the
next save reverts. Casing is worth citing when it grounds a finding about something else; it is not
worth a finding of its own on a project whose analyzers already fail the build for it.

**A newer syntax form the project cannot compile.** Collection expressions, primary constructors, and
target-typed `new()` arrived in different language versions. Check the target framework and
`<LangVersion>` before calling the older form stale; on a project that cannot use the newer one, the
older form is correct rather than out of date.

**Repo-level .NET posture.** Whether dependency injection is wired sensibly, whether packages are
pinned, whether secrets are configured correctly across environments — those are questions about the
repository, not about the diff, and `reviewer-discipline`'s scope rule puts them out of bounds here.
A repo-level .NET audit reference is where that belongs, where one is installed.

**A rule another installed pack states in its own terms.** This file states the general rule for
outbound async work — cancellable, bounded by a timeout, not consumed synchronously. Where another
pack names the same rule for one of its own surfaces, the reader should see it once; attribute it to
whichever states it more specifically and leave the other silent.
