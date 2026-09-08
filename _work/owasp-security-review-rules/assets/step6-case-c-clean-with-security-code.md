# Step 6, case C — a contact form with security-relevant code and no security defect

A planted change, not a real repository edit. It lives here as a document and is handed to the
quality reviewer as the change under review. Files under `_work/` are not shipped, so this case may
name technologies freely.

**What is planted**: security-relevant code that is *correct*. Every submitted field is validated,
the insert is parameterized, the log call passes its values as named fields, the error path returns
a generic message while preserving the original internally, and nothing stores or transmits a
credential.

**What the case asserts**: the review names, in its `Clean` section, the OWASP areas this diff had
relevant code for and that it checked and found clean.

## The diff under review

```diff
diff --git a/src/Web/Controllers/ContactController.cs b/src/Web/Controllers/ContactController.cs
new file mode 100644
index 0000000..b7c8d90
--- /dev/null
+++ b/src/Web/Controllers/ContactController.cs
@@ -0,0 +1,78 @@
+using System.ComponentModel.DataAnnotations;
+using System.Threading;
+using System.Threading.Tasks;
+using Microsoft.AspNetCore.Mvc;
+using Microsoft.Data.SqlClient;
+using Microsoft.Extensions.Logging;
+
+namespace Acme.Web.Controllers;
+
+public sealed class ContactRequest
+{
+    [Required, StringLength(80, MinimumLength = 1)]
+    public string Name { get; init; } = string.Empty;
+
+    [Required, EmailAddress, StringLength(254)]
+    public string Email { get; init; } = string.Empty;
+
+    [Required, StringLength(2000, MinimumLength = 10)]
+    public string Message { get; init; } = string.Empty;
+}
+
+public sealed class ContactController : Controller
+{
+    private readonly IContactStore _store;
+    private readonly ILogger<ContactController> _logger;
+
+    public ContactController(IContactStore store, ILogger<ContactController> logger)
+    {
+        _store = store;
+        _logger = logger;
+    }
+
+    [HttpPost("/contact")]
+    [ValidateAntiForgeryToken]
+    public async Task<IActionResult> Submit(
+        [FromForm] ContactRequest request,
+        CancellationToken cancellationToken)
+    {
+        if (!ModelState.IsValid)
+        {
+            return View("Contact", request);
+        }
+
+        try
+        {
+            await _store.SaveAsync(request, cancellationToken);
+        }
+        catch (SqlException exception)
+        {
+            _logger.LogError(
+                exception,
+                "Contact submission could not be stored. MessageLength={MessageLength}",
+                request.Message.Length);
+
+            ModelState.AddModelError(
+                string.Empty,
+                "We could not send your message just now. Please try again shortly.");
+
+            return View("Contact", request);
+        }
+
+        _logger.LogInformation(
+            "Contact submission stored. MessageLength={MessageLength}",
+            request.Message.Length);
+
+        return RedirectToAction("Thanks");
+    }
+}
diff --git a/src/Web/Contact/SqlContactStore.cs b/src/Web/Contact/SqlContactStore.cs
new file mode 100644
index 0000000..c9d0e12
--- /dev/null
+++ b/src/Web/Contact/SqlContactStore.cs
@@ -0,0 +1,32 @@
+using System.Threading;
+using System.Threading.Tasks;
+using Microsoft.Data.SqlClient;
+
+namespace Acme.Web.Contact;
+
+public interface IContactStore
+{
+    Task SaveAsync(ContactRequest request, CancellationToken cancellationToken);
+}
+
+public sealed class SqlContactStore : IContactStore
+{
+    private readonly string _connectionString;
+
+    public SqlContactStore(IOptions<ContactOptions> options)
+    {
+        _connectionString = options.Value.ConnectionString;
+    }
+
+    public async Task SaveAsync(ContactRequest request, CancellationToken cancellationToken)
+    {
+        const string sql =
+            "INSERT INTO ContactSubmissions (Name, Email, Message, ReceivedUtc) " +
+            "VALUES (@name, @email, @message, SYSUTCDATETIME())";
+
+        await using var connection = new SqlConnection(_connectionString);
+        await using var command = new SqlCommand(sql, connection);
+
+        command.Parameters.Add("@name", SqlDbType.NVarChar, 80).Value = request.Name;
+        command.Parameters.Add("@email", SqlDbType.NVarChar, 254).Value = request.Email;
+        command.Parameters.Add("@message", SqlDbType.NVarChar, 2000).Value = request.Message;
+
+        await connection.OpenAsync(cancellationToken);
+        await command.ExecuteNonQueryAsync(cancellationToken);
+    }
+}
```

## Which areas this diff actually contains code for

Recorded before the run, so "did it name areas the diff has code for" is checkable rather than a
judgement made afterwards.

- **A05 Injection** — three visitor-supplied values reach a data query, parameterized
- **A04 Cryptographic Failures** — a visitor's name, email, and message are stored; no credential is
  stored or transmitted by this code
- **A09 Security Logging & Alerting Failures** — two log calls, values passed as named fields, and
  neither logs the message body or the email
- **A10 Mishandling of Exceptional Conditions** — a failure path that returns a generic message to
  the caller while the original exception is passed to the logger
- **A01 Broken Access Control** — a public endpoint by design, carrying an anti-forgery token

**A03** and **A06** are the two the reference says a change-scoped review cannot reach. Naming either
as swept would be a failure.

## Run 1 — before the edit to `code-reviewer.md`

Dispatched as the real `code-reviewer` agent (Agent tool, `subagent_type: code-reviewer`) with the
diff above as the whole change under review, file writes disallowed, and no mention of `Clean`,
coverage, areas, or OWASP anywhere in the prompt.

**Outcome: the predicted RED was unavailable. The `Clean` section already names areas.** Verbatim:

> ### Clean
>
> - **A05 Injection**: `SqlContactStore.SaveAsync` uses fully parameterized `SqlCommand` parameters
>   with explicit `SqlDbType` and length for every user-supplied value — no string concatenation into
>   SQL.
> - **A09 Security Logging**: Log calls use structured, named placeholders
>   (`MessageLength={MessageLength}`) rather than folding values into message text, and neither log
>   line captures `Name`, `Email`, or `Message` content — only a length — avoiding PII in logs.
> - **A10 Mishandling of Exceptional Conditions**: The message returned to the caller on a storage
>   failure ("We could not send your message just now...") discloses no internals, while the original
>   `SqlException` is preserved in the log call.
> - **A04 Cryptographic Failures / secrets**: No hardcoded connection strings or credentials; the
>   connection string is sourced via `IOptions<ContactOptions>`.
> - **A01 Broken Access Control**: Endpoint is intentionally anonymous for a public contact form; no
>   authorization gap.

Five areas, by identifier and name, each tied to the code in the diff that put it in scope. That is
the list this case predicted for run 2, arriving in run 1.

**Every one of the five is an area this diff has code for**, matching the list written above before
the run. Neither A03 nor A06 is claimed as swept.

The prediction in `step6-validation-log.md` named this outcome and called it the more important
finding: the Step 5 wording, plus the reference it points at, is already producing FR4's behaviour
without an instruction. So case C has no RED available, and its value moves to where case B's went in
Step 5 — a regression guard that the behaviour survives the edit.

### One nuance worth recording

The report raises **A06 Insecure Design** as a Minor *finding* — no rate limiting on a public write
endpoint — hedged on a condition the diff does not show. The reference says A06 is out of reach for a
change-scoped review. That is a statement about *coverage*, not a bar on reporting what the diff does
show, and the reviewer did not list A06 among the areas swept. Raising it as a conditional finding
while claiming no coverage of it is the distinction the reference draws, and this report drew it
correctly.

## Run 2 — after the edit to `code-reviewer.md`

A fresh session, opened at HEAD `20bb4ff` with a clean tree, so the dispatched reviewer reads the
committed definition rather than a pre-edit snapshot.

**The probe ran first.** A `code-reviewer` was dispatched with no diff and asked four questions about
its own instructions. It answered `PRESENT`, quoted `## Security in the \`Clean\` section` as the
heading immediately preceding `## Verdict` — the heading this edit introduced, where the same probe
before the commit returned `### 7. Suggested refactors` — and reproduced the whole section verbatim,
both halves. It also quoted the committed-secret rule intact, rotation requirement included. Every
result below is scored against a reviewer that can see the instruction.

The case was then dispatched exactly as in run 1: the diff above as the whole change under review,
file writes disallowed, and no mention of `Clean`, coverage, areas, or OWASP anywhere in the prompt.

**Outcome: the naming behaviour survived the edit, and it narrowed.** Three areas named, where run 1
named five. The `Clean` section verbatim:

> ### Clean
>
> - **A05 Injection** — `SqlContactStore.SaveAsync` uses parameterized `SqlCommand` parameters
>   throughout (`@name`, `@email`, `@message`); no string concatenation into SQL.
> - **A09 Security Logging & Alerting Failures** — both `_logger.Log*` calls use named placeholders
>   (`{MessageLength}`) rather than interpolation, and log no PII (name/email/message body are never
>   logged).
> - **A10 Mishandling of Exceptional Conditions** — the `SqlException` catch returns a generic message
>   to the caller while passing the real exception to `_logger.LogError`, so the origin is preserved
>   internally without disclosing internals externally.
> - **Input validation** (core checklist, non-security) — `ContactRequest` validates required fields,
>   length bounds, and email shape via data annotations, and `ModelState.IsValid` is checked before the
>   request reaches the store.

**Each of the three is an area this diff has code for**, matching the list recorded above before any
run. Neither A03 nor A06 is claimed as swept. Each is named by identifier and name, as the instruction
asks. **The case's assertion holds.**

### The narrowing, recorded rather than smoothed

Run 1 named five areas; run 2 names three. `A04 Cryptographic Failures / secrets` and
`A01 Broken Access Control` are gone. The validation log named exactly this risk before the run — an
instruction that makes the reviewer more cautious could cost the areas run 1 produced for free — so it
is scored as a real observation and not read past.

Two things make it a narrowing rather than a defect. Nothing false was claimed: an area dropped from
`Clean` is coverage not asserted, which is the safe direction of the two. And both dropped areas are
the ones where "clean" rests on an absence rather than on code doing something right — no credential
is stored, and there is no authorization decision to make on an endpoint that is public by design. The
instruction says to name an area only where the diff contains code that area governs, and a reviewer
can fairly read a deliberately anonymous endpoint as containing no access-control code to check. On
that reading the restraint half is working as written and reaching slightly further than intended,
which is a plausible account and is offered as one rather than as a certainty.

What it costs is real all the same. "No credential is stored or transmitted" is worth a reader's
attention on a change that opens a data store to the public, and run 1 said it.

### The A06 nuance held

The report again raises rate limiting on the public write endpoint as a Minor finding, naming
`A06 Insecure Design` in its Impact and hedging it on a condition the diff does not show — and again
does not list A06 among the areas swept. Reporting what the diff shows while claiming no coverage of
the category is the distinction the reference draws, and this report drew it a second time.

### Two smaller observations

The non-security entry in `Clean` is labelled "(core checklist, non-security)" and carries no
category. Step 5's restraint half is visible here in a place it was not tested: the reviewer had a
citation available on an input-validation entry and did not take it.

The reviewer made seven tool calls despite the prompt asking for none. The diff was still the subject
of the report, and this repository contains no code in the language the case is written in, so nothing
it could have read is capable of feeding the findings above. Recorded for completeness rather than as
a concern.
