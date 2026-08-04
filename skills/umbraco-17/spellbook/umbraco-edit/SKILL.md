---
name: umbraco-edit
description: Edit Umbraco document properties, or invoke a configured AI agent, via the Management API from outside the backoffice UI. Use when asked to change content on a page, update SEO fields, modify a property value, or have an AI agent generate content — anything that would normally happen in the backoffice browser but needs doing from the terminal.
disable-model-invocation: true
allowed-tools: Read, Glob, Grep, Bash(curl:*)
---

Use this when the user asks to change content on a page, update SEO fields, modify a property value,
or call an AI agent to generate content — anything that would normally happen in the backoffice
browser UI but needs to be done from here.

The Umbraco MCP server's tools are designed for the backoffice browser. From a terminal we call the
REST Management API directly, using the same OAuth client credentials.

**Slot:** `.agents/config/stack.md` → `## Local URL`
**If empty:** infer the local base URL from the project's launch profile
(`Properties/launchSettings.json`) or its `.env`; if neither resolves, ask rather than guessing — a
wrong host silently fails auth and looks like a credentials problem.

## Step 1 — Authenticate

**Tokens expire in 299 seconds.** Re-authenticate before each logical group of operations rather than
relying on one token across a long workflow. This is the single most common cause of a sequence that
works at the start and fails partway through.

```bash
curl -sk -X POST "${UMBRACO_BASE_URL}/umbraco/management/api/v1/security/back-office/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=client_credentials&client_id=${UMBRACO_CLIENT_ID}&client_secret=${UMBRACO_CLIENT_SECRET}"
# Returns: { "access_token": "...", "token_type": "Bearer", "expires_in": 299 }
```

Credentials live in the project's environment file — create the OAuth client via the local
backoffice's **Settings → OAuth → Add client**, granting the scopes the work needs. All endpoints
below require `Authorization: Bearer {token}`.

## Step 2 — Key Management API endpoints

| Action | Method | Endpoint |
|---|---|---|
| Document tree root | GET | `/umbraco/management/api/v1/tree/document/root?skip=0&take=100` |
| Document tree children | GET | `/umbraco/management/api/v1/tree/document/children?parentId={id}&skip=0&take=100` |
| Get document | GET | `/umbraco/management/api/v1/document/{id}` |
| Update document | PUT | `/umbraco/management/api/v1/document/{id}` |
| Document type tree root | GET | `/umbraco/management/api/v1/tree/document-type/root?skip=0&take=100` |
| Document type tree children | GET | `/umbraco/management/api/v1/tree/document-type/children?parentId={id}&skip=0&take=100` |
| Get document type | GET | `/umbraco/management/api/v1/document-type/{id}` |

## Step 3 — Workflow for updating page properties

1. **Find the document.** Walk the tree — `/tree/document/root`, then
   `/tree/document/children?parentId=...` — to locate the target page by name.
   **Never hardcode a document ID**; they differ between environments.

2. **Read the document.** `GET /document/{id}` for current values. The response includes a `values`
   array of `{ "alias": "...", "value": "..." }`.

3. **Look up the property aliases — do not assume them.** Pages typically compose their fields from
   document-type compositions, and aliases differ per document type. Always `GET` the document type
   and walk its `CompositionContentTypes`, or read the relevant `.uda`, to discover the real aliases
   before building a payload.

   Two facts that catch people here:
   - The Management API returns properties as a **flat `properties` array** on the document type.
     There is no `groups` nesting in the API response, whatever the backoffice UI suggests.
   - **Avoid reserved and unprefixed generic aliases.** `level` is reserved by the published content
     model; unprefixed generics like `content`, `value`, and `title` collide silently. Prefix with the
     element name instead.

4. **Build the update payload.** The `PUT` body requires `template`, `values`, and `variants` from the
   original document. Modify or add entries in `values`, using the aliases discovered in step 3:

   ```json
   {
     "template": { "id": "..." },
     "values": [
       { "alias": "<lookedUpAlias>", "culture": null, "segment": null, "value": "New value" }
     ],
     "variants": [{ "culture": null, "segment": null, "name": "Page Name", "state": "Draft" }]
   }
   ```

5. **Update the document.** `PUT /document/{id}`. HTTP 200 is success. **This saves a draft; it does
   not publish.**

## Step 4 — Optionally invoke an AI agent for content generation

Agents configured in the backoffice can be invoked via the Agent API, under
`/umbraco/ai/management/api/v1/agents/`:

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | List all agents |
| GET | `/{idOrAlias}` | Get an agent by ID or alias |
| POST | `/{idOrAlias}/run` | Run an agent (SSE stream) |

**Look up the agent alias first** — `GET /` lists what is configured — rather than hardcoding one.
Agents are environment-specific, so a hardcoded alias works on one environment and 404s on the next.

**Agent tools are client-side.** Tools such as page-info lookup, property setting, and search only
work inside the browser Copilot UI. When calling from a terminal, provide the page content directly
in the message and parse the agent's text response yourself — do not expect the agent to read or write
content on your behalf.

```bash
curl -sk -N -X POST "${UMBRACO_BASE_URL}/umbraco/ai/management/api/v1/agents/{lookedUpAlias}/run" \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{"threadId":"t1","runId":"r1","messages":[{"id":"m1","role":"user","content":"..."}]}'
```

The response is a Server-Sent Events stream. Extract text from `TEXT_MESSAGE_CHUNK` events and
concatenate every `delta` value to assemble the full response:

```
data: {"type":"TEXT_MESSAGE_CHUNK","messageId":"...","role":"assistant","delta":"partial text"}
```

## Step 5 — Confirm before destructive edits

Reading documents is safe. Writing them changes content the user may not have asked you to touch.

Before issuing a `PUT`:

- **Show the exact payload** — at minimum the `values` entries being added or changed.
- **For bulk updates, confirm the scope first**: "about to update N documents under `<path>` —
  proceed?"
- **After the update, fetch the document again** and confirm the new values persisted. A 200 means the
  request was accepted, not that the value is what you intended.
