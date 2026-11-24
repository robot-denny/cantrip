---
name: umbraco-17-guide-generator
description: Blueprint for a backoffice dashboard that generates and refreshes editor guides on Umbraco 17, as a port of the guide spell's script. Consult when a project specs, plans or changes a guide-generator dashboard, or when the dashboard and /guide --audit report different statuses for a component.
---

# Guide generator: a blueprint for Umbraco 17

A guide-generator dashboard lets an administrator write and refresh editor guides from the
backoffice, on any environment, with no developer tooling. It lists every component with a guide
status, drafts a guide with a model, shows a preview, and saves the guide as a draft. Build it once,
in the project, through the normal workflow (`/spec` then `/plan`), with this file as the design
input.

It is a port of the `guide` spell's script, `scripts/guide.py`, into the site's own code. The spell
and the dashboard write into the same guides section and read the same values from it, so a guide
made from either one is a guide the other can refresh. Read `umbraco-17-guide-scaffolding` first.
It declares the guide page, the stored reference, the record of generated text and the ignore list,
and this file restates none of them.

## Assert what the platform decided; ask what the project decides

The project decides, and the spec should record:

- **who may use it**: a configured backoffice user group, optionally narrowed to users whose email
  address is at a configured domain;
- **which environments** may generate. Saving only ever creates or changes a draft, so every
  environment can be safe, Live included. Decide which environment owns guides, because a draft
  made on one and a copy transferred from another overwrite each other;
- **where the model key lives** on each environment, and which model it calls. Both are
  configuration, never code;
- **which section hosts the dashboard**, usually Settings;
- **the global blocks the name rule misses**: the document types built as reusable blocks whose name
  does not end in the word "Block". List them in the `## Editor guides` slot, where the spell reads
  them, and give the dashboard the same list, from the slot or from configuration the project keeps
  in step with it;
- **where the project's guide style rules live**, so the model is given them and the style check
  reads them.

## Why it is a port, and how it stays equal to `guide.py`

An Umbraco host may not run Python, and the dashboard needs the script's answers at request time.
So the deterministic half is ported, and the port is held equal to the script by tests rather than
by care.

**Port these, and nothing else:** the Deploy adapter's extraction, the dossier and its signature,
the inventory's documentable rule and its global-block rule, the audit's decision, the change plan's
rows and per-field states, `record` and `mark`. Leave out the uSync and models adapters, the live
rung and report rendering.

**Read the schema from the `.uda` files, not from `IContentTypeService`.** Guides the spell wrote
carry a signature taken at the `deploy` rung. Reading the content type service is the live rung,
which signs the same component differently by design, so no stored signature would ever match. Read
the files under `umbraco/Deploy/Revision/` once and cache the catalog. Keep the accepted Deploy
`__version` values in one constant, updated whenever the script's `ACCEPTED_DEPLOY_VERSIONS`
changes.

**Cache the work, not just the files.** Store each component's dossier and signature with the
catalog, and compute them again only when the catalog rebuilds. The change check is the newest
write time across the files under the schema folder. A folder's own timestamp does not change when
a file inside it is edited, so it is the wrong thing to watch. Check on a short interval or through
a file watcher, never by walking the folder on every request. Build the new catalog off to the side
and swap it in as one reference, so a request never sees a half-built one.

**Sign exactly as the script signs.** The signature is `sha256:` plus the hex SHA-256 of the
canonical dossier serialized as Python's `json.dumps(..., sort_keys=True, separators=(",", ":"),
ensure_ascii=False)` writes it: keys sorted at every level, no whitespace, non-ASCII left
unescaped. `System.Text.Json`'s default encoder escapes `<`, `>`, `&`, `'` and non-ASCII, so write
the canonical form with a small writer of your own. A fingerprint in the record is simpler:
`sha256:` plus the hex SHA-256 of the stored value's UTF-8 bytes, with nothing normalized.

**Reference output comes from the script's own commands**, run against a fixed fixture tree: a
small copy of `.uda` files committed beside the tests. Put the tree in a folder whose name starts
with a dot, because the script skips dot-folders, so the copy never collides with the real schema
when the script runs from the project root.

| Command | Reference output it produces |
|---|---|
| `guide.py extract <alias> --project-root <tree>` | one component's dossier |
| `guide.py signature <alias> --project-root <tree>` | its signature, as a bare value |
| `guide.py inventory --json --project-root <tree> [--global-block <alias>]` | the documentable components, global blocks apart |
| `guide.py plan <alias> --page <page.json> --json --project-root <tree>` | the change plan for one guide page, with each field's state |
| `guide.py record --page <page.json> --field <name> --row <alias>` | the record of generated text after a write |
| `guide.py mark <alias> --page <page.json> --project-root <tree> [--ignored <alias>]` | the new stored reference, or the refusal |

Each command is deterministic. Commit its output beside the fixture tree, and write each command in
the header of the test that reads it. **When the script changes, rerun the commands and rerun the
tests.** A failure then means the port and the script disagree, and the port needs the same change.

**Choose fixtures that exercise each rule:** an element type with compositions, a page type, a
global block named by the rule and one named only by the list, a page file whose fields are each
`asGenerated`, `edited` and `noRecord`, and a page whose stored signature differs, so `mark` has a
guide to mark and a guide to refuse.

## The modules

Keep everything but the save pure, so it can be unit tested without a database.

| Module | Job | Umbraco 17 surface |
|---|---|---|
| Schema catalog | Every `.uda` artifact, read once and cached | `IHostEnvironment.ContentRootPath`, `System.Text.Json` |
| Dossier and signature | The ported extraction, the canonical writer and the signature | none |
| Inventory | Documentable components, with global blocks in their own list | none |
| Status | The ported audit decision for each component | none |
| Change plan | The rows to add, remove and update, and each prose field's state | none |
| Record | Fingerprints, and the merged `guideGenerated` value | none |
| Mark | Whether a guide may be marked up to date, and its new reference | none |
| Guide reader | Each guide page's stored reference, record and values; the guides node's ignore list | `IContentService` (drafts included, so a guide saved but never published still counts) |
| Model client | Sends the writing brief, returns the prose, enforces a timeout | `IHttpClientFactory`, an options class bound from configuration |
| Prose brief | The writing task and the project's style rules, shipped with the site | an embedded resource |
| Sanitizer | Strips model output down to the markup a guide's rich text allows | an HTML sanitizer with an allow-list |
| Style check | The project's guide style rules, checked without a model | none |
| Saver | Creates or updates the guide page, saves it, reads it back, writes the record | `IContentService`, `ICoreScopeProvider` |
| Access | User group, then email domain | `IBackOfficeSecurityAccessor`, an options class |
| API | List components; preview; save; ignore; un-ignore; mark up to date | a `ManagementApiControllerBase` controller under `[VersionedApiBackOfficeRoute]` |
| Dashboard | The admin screen | an `umbraco-package.json` with a `dashboard` extension and a `condition` extension that asks the API whether this user may use it |

Register the services in an `IComposer`.

**The list reads guides in one pass.** Read every guide page in one paged query over the guides
node, such as `IContentService.GetPagedDescendants`, and join pages to components by alias once per
request. Never look up a guide per component. The list's response carries only what the list shows:
the stored reference and whether its signature matches. Read the record and the field values at
preview and save only.

**Hide the machine fields from editors where the project can.** `guideGenerated` and `guideIgnored`
hold data for the tooling, so keep them out of the main tab, as a read-only label or behind
property-level permissions.

## Statuses

**The dashboard and `/guide --audit` report the same status for every component.** Both come from
the same rule, so a test pins the port's statuses against the script's audit for the fixture tree.

| Status | When | Action offered |
|---|---|---|
| No guide | No guide page's stored reference names the component | Generate |
| Up to date | The stored signature matches the current one | Open guide |
| Out of date | The stored signature differs | Regenerate; Mark up to date |
| Not comparable | The guide records no signature, or one taken at another rung | Regenerate, saying it proposes rather than proves |
| Ignored | The alias is on the guides node's ignore list | Un-ignore |

Global blocks are listed apart from block items and filed under the block container. A guide naming
a component the project no longer holds is an orphan, listed on its own, never as a component. A
guide that claims no source was written by hand and is never listed or changed.

## Actions

- **Generate** a guide for a component with none. Rows come from the schema. The model writes only
  the prose the spell's Step 5 asks for: the purpose sentence, how to use it, and one note per row.
  An optional instruction from the administrator is added to the brief.
- **Regenerate** an out-of-date or not-comparable guide. Rows change as the change plan says. Prose
  changes only where its state is `asGenerated`: text still exactly as the tooling stored it.
  `edited` and `noRecord` text is kept, byte for byte, and so is everything a person owns.
- **Ignore** and **Un-ignore** change the guides node's `guideIgnored` list and nothing else on the
  node. Generate, save and mark refuse an ignored component.
- **Mark up to date** writes the new stored reference that `mark` would print, and touches no other
  field. It refuses everything `mark` refuses: an ignored component, a reference naming another
  component, a guide with no reference, a guide already up to date, and a signature that cannot be
  compared. The administrator is told that schema changes since the last generation are not added.

**Every row action re-reads before it writes.** Ignore, Un-ignore and Mark up to date read the
stored value again just before the write. If it moved since the list loaded, they write nothing and
say "changed since you loaded it, refresh", as Save does. Each action's response returns the updated
row, so the screen updates that one row without fetching the list again.

**Ignore and mark up to date follow the spell's publish rule.** Republish the page only when it was
published and had no other unpublished changes. Otherwise save it, and say it was saved but not
published, and why. Check the state before the write, since afterwards every page shows pending
changes.

## Preview, then save as a draft

Generating and regenerating write nothing until the administrator chooses **Save as draft**. The
preview shows each changed field, current text beside the new draft, and which text is kept and
why.

- **A save never publishes.** A new guide is created unpublished in the right kind container, and a
  regenerated guide is saved without publishing. An editor reviews it and publishes it in the
  content editor.
- **Re-read before writing.** Immediately before the save, read the guide's stored reference and
  record again. Where either changed since the preview, write nothing and ask for a fresh preview.
  Check again for an existing guide before creating one, so two administrators cannot create two.
- **Write the stored reference last**, so a save that fails part way leaves a guide that still reads
  as out of date.
- **Fingerprint what the CMS stored.** Read each written field back after the save, and build
  `guideGenerated` from the read-back values, as `record` does. Write the record only for the fields
  the model wrote in this save, merged over the entries the page already held. So Save saves the
  page, reads it back, then writes the record in a second save. This is deliberate: the record
  fingerprints the read-back. Do not merge the two saves into one.
- **Save writes what the preview showed.** Save as draft writes the previewed, sanitized text and
  never calls the model again.
- **A failure leaves nothing behind.** Do the save in one scope, and report a timeout, an empty or
  malformed response, or a response cut off at the length limit in plain words. The administrator
  can try again.

## Model output

**Call the model without holding anything.** Make the call async, and pass the request's
cancellation token to the HTTP call. Hold no scope or content lock while waiting on the model. Cap
how many model calls run at once with a small limit, such as a semaphore.

**Treat the model's output as untrusted.** Ask for a fixed JSON shape naming each field, and refuse
anything else. Sanitize every prose value with an allow-list matching what the guide's rich text
editor permits, before it is shown in the preview and again before it is saved. The preview renders
only sanitized markup.

**Check the guide style without a model, and show what it finds as warnings.** Banned words, a
punctuation rule, the standard wording of a tip: each finding names the field and the rule. A
warning never blocks a save, because the administrator may know better, and the editor reviews the
draft anyway.

**Keep one source for the prose rules.** Embed the project's guide style rules into the site, so a
change to them changes what the dashboard writes. Restate the writing task in a brief the site
owns, and pin it with a test that fails when the brief stops naming a field the spell's Step 5 asks
for.

## The model key

**The model key is a server-side secret, set per environment and never committed.** Set it in each
hosted environment's own settings and in user secrets locally, and read it through the options
class. A test fails when any committed `appsettings*.json` carries a value for it. Without a key the
list still works, and the dashboard says plainly that generation is not set up here and offers no
Generate.

Only a request from a signed-in user who passes the access check reaches the model client. No
anonymous route reaches it, so nobody else can spend the project's model credit or create content.

## Access

Check the user group first and the email domain second, and say which one refused. Compare the
domain as the whole part after the last `@`, ignoring case, so a look-alike such as
`example.com.evil.test` is refused. The dashboard's condition and the API share one decision, so a
hidden dashboard and a refused request can't disagree. The API answers a refused request with 403.

## A usable admin screen

Build it with the backoffice's own `uui-` components rather than clickable `div`s, which gives
keyboard and screen-reader support for free. The screen must work by keyboard and with a screen
reader:

- the components are a real table (`uui-table`) with column headers and an accessible name or
  caption, and each status is text, not color alone. If the table sorts, mark the sorted column
  with `aria-sort`;
- the Ignored list and the orphan list each have their own heading or label;
- every control is a native button, checkbox or link, and each one's accessible name is a verb plus
  its component ("Generate Card", not a column of "Generate"). "Open guide" goes somewhere, so it is
  a link, not a button;
- one status region, present on the page before its text changes, announces when generating starts
  and how it ended; a refusal (an access check, an ignored component, a guide changed since the
  preview) and a failure are announced as alerts and name what refused;
- updating a row's status after an action does not redraw the list, so focus stays where it was and
  the whole list isn't read out again.

**Show the preview as a labelled region inline, below its row.** A `uui-modal` also works, but pick
one; the inline region is simpler. When the preview opens, focus moves to its heading. When it
closes, by Save as draft or cancel, focus returns to the row's Generate or Regenerate button. When a
save is refused, such as a guide changed since the preview, focus moves to the message that says
why.

**The preview's structure carries its meaning.** Make each field a labelled region, or make the
preview a table with headers such as Current, New draft and Kept because. Say in text whether a
field's text is new or kept, never by color or position alone. Model markup can contain headings,
so demote them or scope them inside the field, so they don't break the page outline. Each
style-check warning carries a text label such as "Style warning", is tied to its field with
`aria-describedby`, and is announced through the status region.

**Long-running work is visible to everyone.** While a model call runs:

- set `aria-busy` on the affected region and show a `uui-loader` with a text label; a spinner alone
  says nothing to a screen reader;
- disable the other Generate buttons, and say in text why they are disabled, since only one draft
  can be previewed at a time;
- for a run longer than a few seconds, update the status text now and then, or offer a Cancel button
  reachable by keyboard;
- announce a timeout. It is never silent.

**Confirm before each write that changes a guide.** Mark up to date, Ignore, Un-ignore and Save as
draft each ask first, in a labelled dialog (`uui-dialog` in a modal) that keeps focus inside it
while it is open. Escape closes it, and focus returns to the button that opened it. The default
button is the safe one. The dialog says what will happen. For Mark up to date, that means saying
schema changes since the last generation are not added.

**Errors stay put.** An error stays visible after it is announced, next to the row or control that
caused it. The optional administrator instruction field has a visible label, not only a
placeholder. A 403 says which check refused: the user group or the email domain.

## Tests that pin it

One test class per pure module, plus the reference-output comparisons above. Stub the model client
in every automated test. Worth pinning in particular:

- the port's `extract`, `signature`, `inventory`, `plan`, `record` and `mark` output equals the
  script's for the fixture tree;
- each status, from fixed schema and guide fixtures, matches what `/guide --audit` reports;
- a global block by the name rule and one by the list are listed apart and filed with blocks;
- regenerating replaces an `asGenerated` note and keeps an `edited` note and a `noRecord` note byte
  for byte;
- the record is built from read-back values, and keeps entries for fields this save did not write;
- mark up to date writes only the stored reference, and refuses each case `mark` refuses;
- ignore, un-ignore and mark up to date publish only a page published with no other unpublished
  changes;
- generating writes nothing; saving creates one unpublished guide, and a second save is refused;
- a guide changed after its preview is not overwritten;
- sanitizing removes a script and an event handler attribute;
- the style check reports each rule as a warning and never blocks;
- access refuses the wrong group, the wrong domain, a look-alike domain and an anonymous request,
  and the model client is never called for them;
- a missing key, a timeout and a malformed response each produce a message and no page;
- no committed settings file carries a model key;
- an automated accessibility check, such as axe, passes on the dashboard's main states: the list,
  a run in progress, an open preview and an error;
- the status region exists in the first render, before any text is put in it.
