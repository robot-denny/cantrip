# Step 5, case A — a search term reaching a data query

A planted change, not a real repository edit. It lives here as a document and is handed to the
quality reviewer as the change under review. Files under `_work/` are not shipped, so this case may
name technologies freely.

**The planted defect**: the handler concatenates a visitor's search term into a query string. One
defect, one category.

**What the case asserts**: the reviewer reports the defect, and the finding names its OWASP category
by number and name alongside the file and line.

## The diff under review

```diff
diff --git a/src/Web/Controllers/SiteSearchController.cs b/src/Web/Controllers/SiteSearchController.cs
new file mode 100644
index 0000000..a1b2c3d
--- /dev/null
+++ b/src/Web/Controllers/SiteSearchController.cs
@@ -0,0 +1,34 @@
+using System.Collections.Generic;
+using System.Data.SqlClient;
+using Microsoft.AspNetCore.Mvc;
+
+namespace Acme.Web.Controllers;
+
+public sealed class SiteSearchController : Controller
+{
+    private readonly string _connectionString;
+
+    public SiteSearchController(IConfiguration configuration)
+    {
+        _connectionString = configuration.GetConnectionString("Site");
+    }
+
+    [HttpGet("/search")]
+    public IActionResult Search(string q)
+    {
+        var results = new List<string>();
+
+        using var connection = new SqlConnection(_connectionString);
+        connection.Open();
+
+        var sql = "SELECT Title FROM Pages WHERE Title LIKE '%" + q + "%' ORDER BY Published DESC";
+
+        using var command = new SqlCommand(sql, connection);
+        using var reader = command.ExecuteReader();
+        while (reader.Read())
+        {
+            results.Add(reader.GetString(0));
+        }
+
+        return View("SearchResults", results);
+    }
+}
```

## Run 1 — before the edit to `code-reviewer.md`

Dispatched as the real `code-reviewer` agent (Agent tool, `subagent_type: code-reviewer`) with the
diff above as the whole change under review, and with file writes disallowed for the run.

**Outcome: RED, as predicted.** The defect is reported as a Blocker with its file and its lines. No
OWASP category appears anywhere in the report — not on this finding, not on any other.

Verbatim, the finding:

> ### 1. Secrets and security exposure
>
> **Blocker — SQL injection via unparameterized query (lines 24, 26)**
>
> The `q` query-string parameter is concatenated directly into the SQL text with no sanitization,
> escaping, or parameterization. Any caller can inject arbitrary SQL through `/search?q=...` (e.g.
> `%' UNION SELECT ... --`), enabling data exfiltration from any table the connection's credentials
> can reach, or destructive statements if the account has write/DDL rights.
>
> This is the classic case the checklist calls out directly ("Unvalidated or unsanitized user
> input... from query strings") escalated to a security Blocker because it is a live injection path,
> not just a validation gap.

And the verdict:

> **Request changes** — the SQL injection is a Blocker, and it must be remediated (parameterized
> query) before this can merge.

The rest of the report raised a missing error boundary, a synchronous blocking call, an unbounded
result set, and two nits. None of those carried a category either, which is correct but not yet
evidence of restraint: nothing was citing at all.

Grepping the report for a category identifier returns nothing. `A05`, `A01`, `OWASP`, and `Top 10`
are all absent.

## Run 2 — after the edit, in a session that started with the edit committed

Dispatched the same way as run 1: the real `code-reviewer` agent, the diff above as the whole change
under review, file writes disallowed. The instruction to cite was nowhere in the prompt — the diff was
handed over on its own, exactly as in run 1.

**Outcome: GREEN.** The injection Blocker carries `A05 Injection`, number and name, in the findings
table and again on a `**Category**:` line directly above the file and line.

The table row:

> | # | Severity | File & Line | Issue | Recommended Fix |
> |---|----------|-------------|-------|-----------------|
> | 1 | Blocker | `SiteSearchController.cs:24` | User input concatenated directly into a SQL string (A05 Injection) | Parameterize the query |

And the detail block:

> #### Finding 1 — SQL injection via string concatenation (Blocker)
>
> **Category**: A05 Injection
>
> **File**: `SiteSearchController.cs`, line 24

That is AC1: the category by number and name, alongside the file and the line.

### The restraint half, on the same report

Six findings were reported. Four carry no category at all — the missing error boundary's synchronous
sibling (Major), the unbounded result set (Minor), the unescaped `LIKE` wildcards (Minor), and the
unguarded `NULL` read (Minor). Citing was available on every one of them and none took it.

One finding sits on the line and is worth recording rather than smoothing over. Finding 2, "No error
handling around database access", is a Major reported for reliability, and its **Impact** paragraph
names a category conditionally:

> IF the hosting environment has the developer exception page or a verbose error handler enabled (not
> visible in this diff), this would also disclose internal exception details to the caller — A10
> Mishandling of Exceptional Conditions.

This is not over-citation as AC3 defines it. The citation is attached to a stated security
consequence, hedged on a condition the diff does not show, and the reviewer did not put it on the
finding's `**Category**:` line — the finding has no such line. A reader can tell which half of that
finding is the security claim. Recorded because it is the closest this report comes to the failure
mode, and a later reader should see it was looked at rather than missed.

### Superseded: the earlier invalid run

An earlier attempt at run 2, made in the session that performed the edit, was **invalid rather than
failed**. The dispatched reviewer read an agent definition snapshotted at session start and reported
the citation instruction absent, quoting the committed-secret sentence that sits directly beneath the
inserted paragraphs as the closest related text. The edit was on disk and reachable through the only
registered path:

```
$ ls -l .claude/agents/code-reviewer.md
lrwxr-xr-x  .claude/agents/code-reviewer.md -> ../../skills/core/reference/reviewer-discipline/agents/code-reviewer.md

$ grep -c "names its category by number and name" .claude/agents/code-reviewer.md
1
```

Agent definitions do not hot-reload. The run above was made in a new session, after the edit was
committed, and the probe below confirms the definition it read is the current one. A `general-purpose`
stand-in was used at the time to check the wording in isolation; it is no longer the evidence for this
case and has been dropped.

### The probe, run before either case

Before either diff was handed over, a `code-reviewer` was dispatched and asked one question about its
own instructions — no diff, no review. It answered:

> 1. PRESENT.
>
> 2. Verbatim lines stating the citation rule:
>
> "Read the `security-review-rules` reference before you report. It carries the category table you cite
> from, so the category on a finding comes from a lookup rather than from your recall."
>
> "**Every security finding names its category by number and name**, alongside the file and line the
> evidence standard already requires. Write `A05 Injection`, never the number on its own."
>
> "**A finding that is not a security defect carries no category.** [...]"
>
> 3. Reference file: `security-review-rules`.
>
> 4. Yes, still required. Verbatim: "A committed secret is always a **Blocker**, and the finding must
> note that the credential should be considered compromised and rotated — not merely removed."

This is what separates a real pass from a stale one. Without it, run 2 reading the current definition
and run 2 reading a snapshot would look identical.
