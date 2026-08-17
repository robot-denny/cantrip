---
name: check-uda
description: Analyze Umbraco Deploy schema (.uda) files for conflicts and drift before committing or pushing. Checks git-side conflicts (accidental local regeneration, unpulled remote changes, both-modified files) and, when Live credentials are configured, queries the Deploy Management API for DB-versus-file drift that git diffing cannot see. Produces a risk-rated report with remediation. Run before staging schema changes.
disable-model-invocation: true
allowed-tools: Read, Glob, Grep, Bash(git rev-parse:*), Bash(git fetch:*), Bash(git diff:*), Bash(git ls-files:*), Bash(git status:*), Bash(curl:*), Bash(python3:*)
---

Analyze Umbraco Deploy schema files for potential conflicts and drift before committing or pushing.

## Overview

Deploy stores CMS schema — document types, data types, templates, languages, AI entities — as `.uda`
files in the Deploy revision directory. Problems fall into two buckets, and only the first is visible
to git.

**Git-side conflicts** (local working tree versus the upstream branch):

1. **Accidental local changes** — Umbraco auto-regenerates `.uda` files on startup. Developers stage
   them without realizing.
2. **Remote-ahead** — a teammate, or Umbraco Cloud's own auto-commit, modified schema you haven't
   pulled.
3. **Both-modified** — the same `.uda` changed locally *and* remotely.

**Live-side drift** (local `.uda` files versus the Live environment's database):

4. **Live-only orphans** — entities in Live's DB with no matching `.uda`. Happens when someone
   authors schema directly in a Live backoffice, or when built-in entities were never extracted.
5. **File-only pending** — `.uda` exists but no matching entity in Live's DB. Normal for new schema
   before its first push; a problem if it persists after deploy.
6. **Signature mismatch** — both sides have the entity, but the content diverged.

**Slot:** `.agents/config/paths.md` → `## Umbraco`
**If empty:** locate each by search — the Deploy revision directory by its `*.uda` files, views by
their `*.cshtml` files, and the extension root by its `umbraco-package.json`. If no `*.uda` files
exist, the project is not using Deploy — read schema from the running instance via MCP instead.

## Step 0 — Live credentials (optional, enables Steps 5+)

Load the Live environment's Deploy Management API credentials from the project's environment file:

- `UMBRACO_LIVE_URL` — the Live backoffice base URL
- `UMBRACO_LIVE_CLIENT_ID` — OAuth client ID, created via that backoffice's Settings → OAuth
- `UMBRACO_LIVE_CLIENT_SECRET` — the matching secret

If any are missing, **skip Steps 5+ and degrade gracefully** with a warning:
`⚠️ Live credentials not configured — git-side checks only. Add UMBRACO_LIVE_* entries to enable
Live-drift detection.` The git-side check is fully useful on its own; this is a degradation, not a
failure.

If all are present, fetch a bearer token:

```bash
curl -sk -X POST "${UMBRACO_LIVE_URL}/umbraco/management/api/v1/security/back-office/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=client_credentials&client_id=${UMBRACO_LIVE_CLIENT_ID}&client_secret=${UMBRACO_LIVE_CLIENT_SECRET}"
```

**Tokens expire in 299 seconds.** Re-authenticate before each logical group of calls rather than
reusing one token across a long sequence.

If the token request fails — 401, timeout, network error — warn and degrade to git-only mode.

## Step 1 — Collect git state

Resolve the base branch from the **upstream tracking branch**, not a local branch name. A local
default branch is frequently stale, which would inflate the comparison with everything the local copy
is missing.

```bash
git rev-parse --abbrev-ref HEAD                                    # current branch
git fetch 2>&1                                                     # update remote refs, no merge
git rev-parse --abbrev-ref --symbolic-full-name @{u} 2>/dev/null || echo "NO_UPSTREAM"
git diff --cached --name-only -- "*.uda"                            # staged
git diff --name-only -- "*.uda"                                    # modified, not staged
git ls-files --others --exclude-standard -- "*.uda"                 # untracked
git diff HEAD..@{u} --name-only -- "*.uda" 2>/dev/null || echo "NO_UPSTREAM"   # remote-ahead
```

## Step 2 — Identify git-side conflicts

- **Staged** = the `--cached` list
- **Remote** = the `HEAD..@{u}` list
- **Direct conflicts** = files in **both** lists. These will break the push.

## Step 3 — Read conflicting files for context

For each file in both lists, read it and extract `Name` (human-readable), `Alias` (for document
types), and `__type` (the artifact type).

### Artifact risk table

| Prefix | Risk | Why |
|---|---|---|
| `document-type__` | 🔴 Critical | Breaks content rendering if schema mismatches |
| `data-type__` | 🔴 High | Property editors may stop working |
| `language__` | 🔴 High | Content variants become unreachable if the language is deleted |
| `media-type__` | 🟠 Medium | Media rendering could break |
| `member-type__` | 🟠 Medium | Login and profile pages depend on member types |
| `relation-type__` | 🟡 Medium | Content relationships could orphan |
| `template__` | 🟡 Medium | Template assignments may break |
| `umbraco-ai-connection__` | 🟠 Medium | AI chat and Copilot disabled if misconfigured |
| `umbraco-ai-profile__` | 🟠 Medium | Agents and prompts bound to it will fail |
| `umbraco-ai-context__` | 🟡 Medium | Brand voice and retrieval degraded |
| `umbraco-ai-prompt__` | 🟡 Medium | Individual prompt unavailable |
| `umbraco-ai-settings__` | 🟡 Medium | Default chat and embedding profile selection |
| `umbraco-ai-guardrail__` | 🟡 Medium | Safety guardrail would be missing |
| `*-container__` (document-type, data-type, media-type, member-type) | ✅ Low | Folder organization only |
| `dictionary-item__` | ✅ Low | Translation strings |

## Step 4 — Check for unintentional local changes

Note unstaged and untracked `.uda` files separately — the developer may not have intended them, since
Umbraco writes these on startup. Recommend reviewing before staging, and offer the discard recipe
(Step 7's report includes it).

## Step 5 — Live-drift check *(only if Step 0 got a token)*

Query the Deploy Management API for the schema comparison state — the data backing the Deploy
dashboard:

```bash
curl -sk -H "Authorization: Bearer ${TOKEN}" \
  "${UMBRACO_LIVE_URL}/umbraco/deploy/management/api/v1/schema"
```

Response shape:

```json
{ "comparisonData": {
    "data-type": [ { "udi": {"uriValue": "umb://data-type/..."}, "label": "...",
                     "fileName": "data-type__....uda",
                     "umbracoExists": true, "fileExists": true, "isUpToDate": true } ],
    "document-type": [ ... ] } }
```

Per entity-type category, compute three counts:

- **Live-only orphans** — `umbracoExists && !fileExists`, with no local file at that filename either.
  DB-only entities not tracked in git. Either extract them on Live (dashboard → "Create file", then
  pull), or delete them from the DB if they shouldn't exist.
- **File-only pending** — `!umbracoExists && fileExists`. The `.uda` arrived but Deploy hasn't
  imported it. Usually transient after a push; if it persists, see the remediation reference.
- **Signature mismatch** — `umbracoExists && fileExists && !isUpToDate`. Content diverged. Decide
  which direction wins (usually local, since local is canonical), then see the remediation reference.

Also cross-reference locally: a local `.uda` that Live doesn't list at all is a "pending push" —
expected if it's in an unpushed commit, a warning if pushed and unprocessed.

Summarize per category: `data-type: 0 orphans, 2 pending, 0 mismatch`.

## Step 6 — Block palette drift *(informational, never failing)*

**Reporting only.** This never contributes a severity and never blocks a commit. It surfaces
divergence between block-editor palettes so one-sided membership stays visible — deliberate drift is
common and legitimate, this just makes it explicit.

**Not every pair of palettes is meant to match.** A project typically has a few *page-body* palettes
that should be near-parity, plus several *parent-scoped sub-list* palettes offered only inside one
owning block. Comparing a body palette against a sub-list is meaningless noise — verified against a
real site, comparing all palettes pairwise produced 21 comparisons of which 18 were nonsense.

So identify the peer group first.

**Slot:** `.agents/config/conventions.md` → `## Block palette parity`
**If empty:** infer the peer group — keep only palettes offering more than one block, then compare
only pairs that share at least one block. Sub-list palettes are single-block and drop out; body
palettes overlap heavily and remain. If that leaves fewer than two palettes, skip this step silently.

Computed purely from local files, so no Live credentials are needed. Point the script at the Deploy
revision directory:

```python
import json, glob, os, re, sys, itertools
rev = sys.argv[1]

alias = {}
for f in glob.glob(os.path.join(rev, "document-type__*.uda")):
    try: d = json.load(open(f))
    except Exception: continue
    m = re.search(r'umb://document-type/([0-9a-fA-F]{32})', d.get("Udi", ""))
    if m and "Alias" in d:
        alias[m.group(1).lower()] = d["Alias"]

def norm(k): return k.replace("-", "").lower()

palettes = {}
for f in glob.glob(os.path.join(rev, "data-type__*.uda")):
    try: d = json.load(open(f))
    except Exception: continue
    cfg = d.get("Configuration") or {}
    # Only top-level blocks[] is palette membership. Nested areas[].specifiedAllowance[]
    # entries are area-scoped allowances, not palette offerings.
    if isinstance(cfg.get("blocks"), list) and cfg["blocks"]:
        palettes[d.get("Name", os.path.basename(f))] = {
            alias.get(norm(b.get("contentElementTypeKey", "")), "??" + str(b.get("contentElementTypeKey")))
            for b in cfg["blocks"] if isinstance(b, dict)}

# Peer heuristic: sub-list palettes offer exactly one block; body palettes offer many and
# overlap. Replace this filter with the configured peer group once the slot is filled.
peers = {n: s for n, s in palettes.items() if len(s) > 1}

if len(peers) < 2:
    print("Fewer than two comparable block palettes — nothing to report.")
else:
    for a, b in itertools.combinations(sorted(peers), 2):
        if not (peers[a] & peers[b]):
            continue                      # unrelated palettes, not peers
        only_a, only_b = peers[a] - peers[b], peers[b] - peers[a]
        if not (only_a or only_b):
            print(f"{a} <-> {b}: at parity")
        else:
            print(f"{a} <-> {b}:")
            if only_a: print(f"  only in {a}: {sorted(only_a)}")
            if only_b: print(f"  only in {b}: {sorted(only_b)}")
```

Report one-sided blocks with **no severity attached**. If the peers match, state that they are at
parity. One-sided membership is frequently intentional — a block using grid *areas* cannot work in a
list editor, and a block whose list home is a different palette reads as one-sided here — so the
project's own tests and docs are the authority on which divergences are expected, not this check.

## Step 7 — Generate the report

```markdown
## Umbraco Schema Conflict & Drift Check

**Branch:** {branch}
**Upstream:** {upstream, or "none — push will create a new remote branch"}
**Live API:** {"✓ connected" or "⚠ not configured (git-only mode)"}

### 📋 Local Staged Schema Changes
Each staged `.uda` with entity type, Name, and risk level.
If none: _"No schema files are staged — safe to commit from a Deploy perspective."_

### 🌐 Remote Schema Changes (unpulled)
Each `.uda` changed upstream but unpulled, with entity type and Name.
If none: _"Remote is in sync — no unpulled schema changes."_

### 🔴 Direct Git Conflicts
Files in BOTH staged and remote: filename, entity name and type, why it's risky.
If none: _"✅ No direct git conflicts detected."_

### 🟠 Live-Side Drift  (skipped without Live credentials)
Per-category counts, then the specific entities for each non-zero category:

data-type:      0 orphans  |  0 pending  |  0 mismatch  ✓
document-type:  0 orphans  |  0 pending  |  0 mismatch  ✓
media-type:     1 orphan   |  0 pending  |  0 mismatch  ⚠

### 🧩 Block Palette Drift  (informational — never a conflict)
One-sided palette membership, or _"Body palettes are at parity."_

### ⚠️ Risk Assessment

| Level | Condition |
|---|---|
| ✅ SAFE | No staged `.uda`, no Live drift |
| 🟢 LOW | Staged `.uda`, remote in sync, no Live drift |
| 🟡 MEDIUM | Remote has unpulled schema changes to *different* files |
| 🟠 HIGH | Live has orphans or mismatches, or remote changed the same entity types as yours |
| 🔴 CRITICAL | Direct git conflicts — same files changed locally and upstream |

State the overall level and a one-line summary.

### Recommended Action
### 💡 Unintentional Changes
```

**Recommended action, by level:**

- **SAFE / LOW** — proceed with the commit.
- **MEDIUM** — pull with rebase first, let Umbraco sync locally by running the site and checking the
  Deploy dashboard, then commit.
- **HIGH (Live drift)** — resolve drift on Live *before* pushing local changes on top. Orphans you
  want to keep: extract to `.uda` via the dashboard's per-row "Create file", then pull. Orphans that
  shouldn't exist: delete them in the backoffice. For pending or mismatched entries where local should
  win, see the `umbraco-deploy-facts` reference where installed — without it, the short version is that
  the per-row "Update item" action imports and the bulk button does not.
- **HIGH (remote-ahead on the same entity type)** — coordinate with whoever pushed; on a solo project,
  inspect the remote diff before pulling.
- **CRITICAL** — **do not push without resolving.** Pull with rebase (it will conflict), manually
  merge each `.uda` keeping the JSON that matches the intended schema, run the site locally and verify
  the Deploy dashboard is clean, then commit and push.

**Unintentional changes** — if unstaged or untracked `.uda` files weren't deliberate, Umbraco rewrote
them from the local DB on startup. Offer the discard recipe against the Deploy revision directory:
`git checkout --` for tracked files, and note that untracked ones need `git clean -f` separately.

Only commit `.uda` files when a document type, data type, or template was deliberately changed in the
backoffice — or when bulk-extracting pre-existing built-in defaults.

## When drift won't clear

If Step 5 reports pending or mismatched entries that persist, the remediation paths — including which
dashboard control actually imports and which silently does nothing — are in the `umbraco-deploy-facts`
reference, where installed. Read it rather than guessing; two of the obvious remedies are known not to
work on Cloud.

**If that reference is not installed**, report the states you found and say the remediation guidance
lives in a unit this project does not have, rather than improvising. The two remedies most people try
first — restarting the environment from the portal, and pushing an empty commit — are both known not to
import, so guessing costs time that reading would not.
