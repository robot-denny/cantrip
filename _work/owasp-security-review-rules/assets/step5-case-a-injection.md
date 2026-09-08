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

## Run 2 — after the edit to `code-reviewer.md`

**Outcome: INVALID, not failed.** The dispatched `code-reviewer` reported the same defect as run 1
and still cited no category. The stale-definition probe explains why. Asked whether its own
instructions contain an instruction to cite a security category, it answered:

> My own instructions (the agent definition/domain checklist above, not any skill I loaded) do not
> contain an instruction to cite a security category when reporting a security finding. The closest
> related text is the severity guidance: "Blocker — security risk, data exposure, or a crash path"
> and, for section 1, "A committed secret is always a Blocker... and the finding must note that the
> credential should be considered compromised and rotated." Neither of these directs me to name a
> security category [...] that instruction is absent from my instructions as given.

The edit was on disk before this run, and it is reachable through the only path the agent is
registered by:

```
$ ls -l .claude/agents/code-reviewer.md
lrwxr-xr-x  .claude/agents/code-reviewer.md -> ../../skills/core/reference/reviewer-discipline/agents/code-reviewer.md

$ grep -c "names its category by number and name" .claude/agents/code-reviewer.md
1
```

No second copy of the definition exists anywhere on the machine, and `~/.claude/agents/` does not
exist. So the agent read a snapshot taken at session start. The run cannot score the edit.

## Diagnostic — the same review from the current on-disk definition

**Not evidence for the step's validation.** The registered agent is the subject of the test, and this
is a stand-in. It answers a narrower question: does the wording, once actually in front of a
reviewer, produce the citation? It does.

A `general-purpose` agent was told to read `code-reviewer.md` from disk, read the skills that file
instructs it to follow, and review the same diff under those instructions. It reached
`security-review-rules` on its own and opened with:

> I've read the agent definition, `reviewer-discipline`, and `security-review-rules`.

Its findings table:

> | # | Severity | File & Line | Issue | Recommended Fix |
> |---|----------|-------------|-------|-----------------|
> | 1 | Blocker | `src/Web/Controllers/SiteSearchController.cs`, line 24 | **A05 Injection** — `q` concatenated into SQL and executed | Parameterize the pattern and escape `LIKE` wildcards |
> | 2 | Major | `src/Web/Controllers/SiteSearchController.cs`, lines 21–31 | Synchronous blocking DB I/O in the action; no cancellation token | Make the action `async Task<IActionResult>`, use the `*Async` APIs, accept `CancellationToken` |
> | 3 | Major | `src/Web/Controllers/SiteSearchController.cs`, lines 17, 24 | `q` unvalidated: null or empty matches every row, and there is no result cap | Guard for null/whitespace and a minimum length; add `TOP (@take)` |
> | 4 | Major (conditional) | `src/Web/Controllers/SiteSearchController.cs`, line 24 | **A01 Broken Access Control** — orders by `Published` but never filters on it | IF `Pages` holds non-public rows, add the publication predicate to the `WHERE` clause |

And the detail block on the Blocker:

> #### Finding 1 — Query-string value concatenated into SQL (Blocker)
>
> **File**: `src/Web/Controllers/SiteSearchController.cs`, line 24
> **Category**: A05 Injection

Three things worth noting from this run:

- The category is **number and name**, both in the table row and on its own `**Category**:` line, and
  it sits beside the file and the line. That is what AC1 asks for.
- The four non-security findings — blocking I/O, the missing result cap, the null connection string,
  the legacy driver, the using directives — carry **no** category. The restraint half held on a report
  where citing was available.
- The reviewer volunteered the two out-of-reach categories rather than implying coverage: "Two areas
  I cannot reach from a change-scoped review, and claim no coverage on: **A06 Insecure Design** [...]
  and **A03 Software Supply Chain Failures**". That is Step 6's territory, arriving early from the
  reference alone.
