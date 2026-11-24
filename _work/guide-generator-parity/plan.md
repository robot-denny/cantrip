# Plan: Guide Generator Parity

**Spec**: `_work/guide-generator-parity/spec.md`
**Branch**: `robot-denny/guide-generator-port`
**Work type**: change-to editor-guides
**Feature doc**: editor-guides

## Context

`/guide` (`skills/umbraco-17/spellbook/guide/`) writes editor guides from a developer's machine:
`scripts/guide.py` computes (extract, signature, inventory, audit, plan) and the spell writes
through MCP after approval. A client project ported the script to C# behind a backoffice dashboard
and added three behaviors: an ignore list, "mark up to date", and refreshing AI-written text nobody
edited. This increment brings those to the script and spell, accepts two more Deploy format
versions, adds global-block grouping to the inventory, documents the new fields in
`umbraco-17-guide-scaffolding`, and adds a reference blueprint for the dashboard. The unit of work
is a script capability with its fixture cases, then the spell prose that drives it.

---

## Key Decisions

- **The record of AI-written text lives on the guide page**, in a new machine-owned field,
  `guideGenerated` (default alias; the `## Editor guides` slot can rename it). It travels with
  Deploy, and the spell and a dashboard read one record. The client keeps it per environment; this
  repo deliberately differs. (User decision, 2026-11-24.)
- **A fingerprint is `sha256:` plus the hex SHA-256 of the field's exact stored value**, UTF-8, no
  normalization. Simple to port identically. (User decision.)
- **Fingerprint what the CMS stored, not what was sent.** The spell already reads every written
  field back (Step 8). The record is computed from those read-back values, so a rich text editor
  that reformats markup on save does not make freshly written text read as "edited" next time.
- **The record's shape**: `{"recordVersion": 1, "fields": {"guidePurpose": "<fp>", "guideWhenToUse":
  "<fp>"}, "rows": {"<property alias>": "<fp of its information note>"}}`. Rows are keyed by the
  property alias, not the label, so a renamed label keeps its note's protection. A field or row with
  no entry has **no record** and is kept.
- **Three states per model-authored field**: `asGenerated` (matches its fingerprint, so it is
  rewritten), `edited` (differs, so it is kept and nothing is proposed), `noRecord` (no fingerprint,
  so it is kept). `guidePurpose`, `guideWhenToUse` and each row's `information` note are the
  model-authored fields. `guideExamples` stays seeded-once and is never refreshed.
- **Page file version 2.** `plan`'s page file gains a structural `generated` key beside `source`:
  `null` means the page holds no record, and an absent key is refused, the same discipline as
  `source`. `ACCEPTED_PAGE_VERSIONS` becomes `(1, 2)`; a version-1 file reads as `generated: null`,
  so existing callers keep working.
- **Guides file version 2.** The audit's guides file gains a top-level `ignored` list of aliases,
  read from the guides node's `guideIgnored` field (default alias). Version 1 reads as nothing
  ignored.
- **Commands.** `/guide --ignore <alias>`, `/guide --unignore <alias>` and `/guide --mark-current
  <alias>` are new modes of the existing spell, beside `--audit`. (User decision.) The script gains
  `record` (builds a record from read-back values) and `mark` (validates a mark-up-to-date and
  emits the new `source`), so each refusal is tested in the script rather than only described in
  prose.
- **Deploy versions.** 17.3.1 is accepted after re-measuring it on the client project's files
  (read-only) against 17.2.1, the way the existing comment records. 17.0.1 is accepted only if the
  demo project's files (`~/Projects/umbraco-17-demo-site`, read-only) carry the same fields as an
  accepted version; if they do not, the step records what differs and leaves it unaccepted. The
  comment beside the list names neither project ("a production Umbraco Cloud project", "the demo
  project").
- **Global blocks.** A document type whose name ends in the word "Block", or whose alias the
  project lists, is a global block: a reusable block stored as a document. The inventory reports
  global blocks in their own section, as documentable, and files their guides with blocks. Listed
  aliases arrive through a repeatable `--global-block <alias>` flag, read by the spell from the
  `## Editor guides` slot, so the project fact stays in the project. The name rule is reported, like
  the excluded palette, so a count it changes is never silent.
- **No separate "golden output" command.** A port's reference output is what the existing commands
  (`extract`, `signature`, `inventory --json`, `plan --json`) plus `record` and `mark` print for a
  fixed fixture tree. The blueprint lists the commands; each is deterministic, and fixture cases
  already pin its output.
- **Tests** follow the existing convention: cases are declared in `tests/make-guide-fixtures.sh`,
  regenerated into `tests/guide-check/`, and run with `tests/run.sh guide-check`. Every step adds
  its cases to the generator first, regenerates, and confirms RED before implementing.
- **Gates**: `tests/run.sh` (all suites) and `scripts/check-contract.sh`, both run at the end of
  every step.
- **Public-repo rule.** No client name, organization, email domain, model version or setting key
  from the client project appears in any shipped file. Step 11 adds the dashboard reference, which
  is where this is most at risk.

---

## Steps

Each step is designed to be completed independently in its own context window.
The step heading contains a ready-to-use prompt you can paste into a new session.

---

### Step 1 — Accept Deploy 17.3.1 and, if it measures the same, 17.0.1

> **Prompt**: Implement Step 1 of `_work/guide-generator-parity/plan.md`. In
> `skills/umbraco-17/spellbook/guide/scripts/guidelib/__init__.py`, `ACCEPTED_DEPLOY_VERSIONS` lists
> the Deploy `__version` values the script reads. Measure two more, read-only: the client project's
> 17.3.1 document-type and data-type `.uda` files (under `~/Projects/AHIMA/Umbraco17`) against its
> 17.2.1 ones, and the demo project's 17.0.1 files (`~/Projects/umbraco-17-demo-site`) against the
> closest accepted version. Compare top-level keys, property keys and group keys. Accept each version
> whose shape matches what the script reads; for one that does not, record the difference in the
> validation log and leave it out. Write the reason beside the list in the existing comment's style,
> naming neither project. Add fixture cases to `tests/make-guide-fixtures.sh` first, regenerate, and
> confirm RED; then edit the list. Run `tests/run.sh` and `scripts/check-contract.sh`.

**What to build**:
- `scripts/guidelib/__init__.py`: extend `ACCEPTED_DEPLOY_VERSIONS` and its comment.
- `tests/make-guide-fixtures.sh`: a case extracting a component from a tree declaring 17.3.1, and
  one for 17.0.1 if accepted. Keep `deploy-requested-version-skipped` (an unknown version is still
  skipped and named).
- `_work/guide-generator-parity/validation.md`: create it, and log the measurement (counts compared,
  keys found, the one difference noted for 17.3.1: a data type's top-level `Parent`).

**Test first**:
- Add the cases, run `tests/make-guide-fixtures.sh && tests/run.sh guide-check`, and confirm the new
  cases fail because the version is skipped.

**Validation**:
- [Automated]: `tests/run.sh` reports every case passing; `scripts/check-contract.sh` passes.
- [Manual]: `python3 skills/umbraco-17/spellbook/guide/scripts/guide.py extract alertBanner
  --project-root ~/Projects/umbraco-17-demo-site` prints the alert banner's dossier if 17.0.1 was
  accepted, or still says the files were skipped if not.

---

### Step 2 — Fingerprints and the `record` command

> **Prompt**: Implement Step 2 of `_work/guide-generator-parity/plan.md`. Add a fingerprint
> function to the guide script's library (`skills/umbraco-17/spellbook/guide/scripts/guidelib/`):
> `sha256:` plus the hex SHA-256 of a field's exact stored value, UTF-8, no normalization. Add a
> `guide.py record` subcommand that reads a page file (the shape `plan` reads, see the spell's
> Step 3) plus the list of model-authored fields and row aliases the spell just wrote, and prints
> the `guideGenerated` record: `{"recordVersion": 1, "fields": {...}, "rows": {...}}`, merged over
> the page's existing record so entries for fields not rewritten are kept unchanged. Refuse a named
> field or row the page file doesn't hold. Write fixture cases in `tests/make-guide-fixtures.sh`
> first and confirm RED; then implement. Run `tests/run.sh` and `scripts/check-contract.sh`.

**What to build**:
- `scripts/guidelib/fingerprint.py` (new): the fingerprint function and the record builder.
- `scripts/guide.py`: a `record` subparser (`--page FILE`, `--field NAME` repeatable, `--row ALIAS`
  repeatable).
- Fixture cases: a record for a purpose sentence and two row notes, with a known expected hash
  computed independently (for example `printf %s 'text' | shasum -a 256` when writing the case);
  a merge that keeps an existing entry; a refusal for a named row the page doesn't hold.

**Test first**:
- The expected fingerprint in each case is computed outside the script, so the test can't agree with
  a wrong hash by construction.

**Validation**:
- [Automated]: `tests/run.sh guide-check` passes, then `tests/run.sh` and
  `scripts/check-contract.sh`.

---

### Step 3 — `plan` reads the record for the page's prose fields

> **Prompt**: Implement Step 3 of `_work/guide-generator-parity/plan.md`. In
> `skills/umbraco-17/spellbook/guide/scripts/guidelib/changeplan.py`, accept page-file version 2
> with a structural `generated` key (`null` or a record from Step 2; absent is refused). A version-1
> file reads as `generated: null`. Add `guideGenerated` to `REGISTER` as machine-owned and computed.
> For `guidePurpose` and `guideWhenToUse`, report each one's state (`asGenerated`, `edited`,
> `noRecord`). An `asGenerated` field is proposed for the model to rewrite, and `modelCallNeeded`
> reflects it. `edited` and `noRecord` are kept, with nothing proposed. Keep a field nobody ever
> wrote reported as today. Update the register's `why` text and the module docstring, which today
> say prose is never regenerated. Cases first, confirm RED, then implement. Run `tests/run.sh` and
> `scripts/check-contract.sh`.

**What to build**:
- `changeplan.py`: page version 2, the `generated` key, a `FIELD_GENERATED` constant, per-field
  state in both the JSON and the human report, an updated rule text for seeded-once prose.
- Fixture cases: purpose `asGenerated` (proposed), purpose edited by one word (kept, nothing
  proposed), no record (kept), a version-1 page file (reads as no record), `generated` absent on
  version 2 (refused), and an unchanged signature with an `asGenerated` purpose (still a no-op: only
  a changed source triggers a refresh).

**Test first**:
- One case per state above, added and regenerated before any code changes; confirm each fails.

**Validation**:
- [Automated]: `tests/run.sh` and `scripts/check-contract.sh` pass, and existing `plan-*` cases
  still pass unchanged.

---

### Step 4 — `plan` reads the record for row notes

> **Prompt**: Implement Step 4 of `_work/guide-generator-parity/plan.md`. Extend `plan` (Step 3
> added page version 2 and prose-field states) so each existing property row's `information` note
> gets a state from the record's `rows`, keyed by property alias: `asGenerated` notes are proposed
> for rewriting; `edited` and `noRecord` notes are kept. A row whose label changed keeps its state,
> because the key is the alias. A removed row's record entry is dropped from the record the spell
> will write. Cases first, confirm RED, then implement in `changeplan.py`. Run `tests/run.sh` and
> `scripts/check-contract.sh`.

**What to build**:
- `changeplan.py`: row-note states in the row comparison, the JSON and the report; a renamed-label
  row keeps its note's state.
- Fixture cases: an `asGenerated` note proposed, an edited note kept, a row with no record kept, a
  renamed label with an `asGenerated` note, a removed row whose note had a record.

**Test first**:
- Each case added and confirmed failing before the row comparison changes.

**Validation**:
- [Automated]: `tests/run.sh` and `scripts/check-contract.sh` pass.

---

### Step 5 — The spell refreshes unedited text and records what it wrote

> **Prompt**: Implement Step 5 of `_work/guide-generator-parity/plan.md`. Update
> `skills/umbraco-17/spellbook/guide/SKILL.md` for Steps 2 to 4's script behavior: Step 3's page
> file is version 2 and carries `generated` (read from the `guideGenerated` field, translated
> through the `## Editor guides` slot); Step 5 writes the prose `plan` marks `asGenerated` as well
> as creation-time prose; Step 7 shows rewritten text in the difference; Step 8 re-reads each field
> immediately before writing it and skips one that no longer matches what the plan saw (reported as
> "changed after the plan"), then, after the read-back, runs `guide.py record` over the read-back
> values and writes `guideGenerated` just before `guideSource`. Keep the rules that main body
> content, live examples, screenshots and page settings are never touched. No script changes in
> this step. Run `scripts/check-contract.sh`.

**What to build**:
- `skills/umbraco-17/spellbook/guide/SKILL.md`: Steps 3, 5, 7, 8 and 9 (the report names fields
  rewritten, kept as edited, kept with no record, and skipped as changed after the plan).

**Test first**: none; prose only. The behavior it drives is pinned by Steps 2 to 4.

**Validation**:
- [Automated]: `scripts/check-contract.sh` passes.
- [Manual]: read Step 8's write order aloud against Key Decisions: page, creation prose, rows,
  refreshed prose, `guideGenerated`, then `guideSource` last.

---

### Step 6 — The audit honors an ignore list

> **Prompt**: Implement Step 6 of `_work/guide-generator-parity/plan.md`. In
> `skills/umbraco-17/spellbook/guide/scripts/guidelib/audit.py`, accept guides-file version 2 with a
> top-level `ignored` list of aliases (version 1 reads as nothing ignored). An ignored component is
> reported in its own section by name, and is never counted as undocumented, stale or orphaned. An
> ignored alias naming no component is reported as naming nothing. Cases first, confirm RED, then
> implement. Run `tests/run.sh` and `scripts/check-contract.sh`.

**What to build**:
- `audit.py`: guides version 2, the `ignored` list with the same strictness as other lists (a
  non-string entry refuses the file), an "Ignored" section in the report and the JSON.
- Fixture cases: an ignored undocumented component, an ignored component with a guide, an ignored
  alias naming nothing, version 1 unchanged, a malformed `ignored`.

**Test first**:
- Cases added and confirmed failing before `audit.py` changes.

**Validation**:
- [Automated]: `tests/run.sh` and `scripts/check-contract.sh` pass; existing `audit-*` cases are
  unchanged.

---

### Step 7 — The `mark` command for "mark up to date"

> **Prompt**: Implement Step 7 of `_work/guide-generator-parity/plan.md`. Add `guide.py mark <alias>
> --page FILE` (plus the usual source flags) to the guide script. It reads the component's current
> signature and the page file, and prints the new `source` value to write (the same alias, kind and
> rung, with the current signature) only when the comparison is `differs`. It refuses, saying why,
> when the page has no reference, when the signatures already match, when the stored rung differs,
> when the schema can't be read, or when `--ignored` names the alias. Cases first, confirm RED, then
> implement. Run `tests/run.sh` and `scripts/check-contract.sh`.

**What to build**:
- `scripts/guide.py` and a small function in `changeplan.py` or a new `guidelib/mark.py`: reuse the
  plan's comparison rather than re-deriving it.
- Fixture cases: a stale page marked (prints the new `source`), and one refusal per reason above.

**Test first**:
- Cases added and confirmed failing before the subcommand exists.

**Validation**:
- [Automated]: `tests/run.sh` and `scripts/check-contract.sh` pass.

---

### Step 8 — The spell's ignore, un-ignore and mark-current modes

> **Prompt**: Implement Step 8 of `_work/guide-generator-parity/plan.md`. Add three modes to
> `skills/umbraco-17/spellbook/guide/SKILL.md` beside `--audit`: `--ignore <alias>` and
> `--unignore <alias>` (read the guides node's `guideIgnored` field, show the changed list, write
> only on approval, save and republish only when the node has no other unpublished changes, else
> say why it wasn't published; with no such field, stop and point at the scaffolding reference),
> and `--mark-current <alias>` (run `guide.py mark`, show that only the stored signature changes and
> that schema changes since the last generation are not added, write only `guideSource` on approval,
> the same publish rule). The generate path stops on an ignored alias. The audit's guides file
> becomes version 2 with `ignored`. Update the frontmatter's description and `argument-hint`. No
> script changes. Run `scripts/check-contract.sh`.

**What to build**:
- `SKILL.md`: the three modes, the ignored-alias stop on the generate path, A2's guides file
  version 2.

**Test first**: none; prose only. The script behavior is pinned by Steps 6 and 7.

**Validation**:
- [Automated]: `scripts/check-contract.sh` passes (each new slot reference keeps its
  `**If empty:**`).
- [Manual]: the description still fits on one line of the skill listing, and names the three new
  modes.

---

### Step 9 — Global blocks in the inventory

> **Prompt**: Implement Step 9 of `_work/guide-generator-parity/plan.md`. In
> `skills/umbraco-17/spellbook/guide/scripts/guidelib/inventory.py`, classify a document type as a
> global block when its name ends in the word "Block" or its alias is passed with a new repeatable
> `--global-block <alias>` flag (on `inventory` and `audit`). Report global blocks in their own
> section as documentable components, state the name rule and any listed aliases in the report, and
> keep them out of the page-type proposals. The audit counts them like blocks. Bump the inventory
> version if a consumer-visible key is added, and accept the old one where `audit --inventory` reads
> it. Cases first, confirm RED, then implement. Run `tests/run.sh` and `scripts/check-contract.sh`.

**What to build**:
- `inventory.py`, `audit.py`, `guide.py`: the classification, the flag, the section, the version
  handling.
- Fixture cases: "Promo Block" document type (global block), "Site Settings" listed by flag (global
  block), "Blockade Page" (not one: "Block" is not the last word), an element type named "Card
  Block" (still a palette block, not a global block), the audit counting a global block with no
  guide as undocumented.

**Test first**:
- Cases added and confirmed failing before `inventory.py` changes.

**Validation**:
- [Automated]: `tests/run.sh` and `scripts/check-contract.sh` pass.

---

### Step 10 — The scaffolding reference documents the new fields

> **Prompt**: Implement Step 10 of `_work/guide-generator-parity/plan.md`. Update
> `skills/umbraco-17/reference/umbraco-17-guide-scaffolding/SKILL.md`: add `guideGenerated` to the
> guide page's field set (machine-owned, read-only to editors, a plain text or label editor holding
> JSON, its shape per the plan's Key Decisions) and `guideIgnored` to the guides node (read-only to
> editors, a list of aliases); add both to the slot table of defaults; explain that "ownership
> follows provenance" now has a third input, the record, which decides whether a seeded prose field
> may be refreshed; say where global-block guides are filed (with blocks). Update the spell's
> `## Editor guides` slot description, wherever it lists the field names, so the two agree. Run
> `scripts/check-contract.sh`.

**What to build**:
- `reference/umbraco-17-guide-scaffolding/SKILL.md`, and the slot's field list wherever
  `check-contract.sh` requires it to match.

**Test first**: none; reference prose. The contract check pins slot and fallback consistency.

**Validation**:
- [Automated]: `scripts/check-contract.sh` and `tests/run.sh` pass.

---

### Step 11 — The dashboard blueprint, its registration, and the docs

> **Prompt**: Implement Step 11 of `_work/guide-generator-parity/plan.md`. Create
> `skills/umbraco-17/reference/umbraco-17-guide-generator/SKILL.md`, a blueprint for a backoffice
> guide-generator dashboard a project builds through `/spec` and `/plan`, following the structure
> of `umbraco-17-test-content-builder`: what the project decides, why it is a port and how it stays
> equal to `guide.py` (the commands that produce reference output from a fixture tree, and the tests
> that compare against them, rerun when the script changes), the modules and their Umbraco 17
> services, statuses and actions (generate, regenerate, ignore, mark up to date), preview then save
> as draft only, sanitizing model output, the guide-style check shown as warnings, the model key as
> a per-environment server-side secret never committed, access by configured user group optionally
> narrowed by email domain, the accessibility the core test-content reference lists for an admin
> screen, and the tests that pin it. Name no client, organization, domain, model version or setting
> key. Register it in `scripts/check-install.sh` (`ROSTER_PACK`, `PACK_SOURCE`), and update the
> README's `umbraco-17` table, `docs/spell-cards.md` (a card and the counts), `docs/layout.md`
> counts and `CHANGELOG.md` (Unreleased, covering Steps 1 to 11). Run `tests/run.sh` and
> `scripts/check-contract.sh`.

**What to build**:
- `skills/umbraco-17/reference/umbraco-17-guide-generator/SKILL.md` (new).
- `scripts/check-install.sh`, `README.md`, `docs/spell-cards.md`, `docs/layout.md`, `CHANGELOG.md`.

**Test first**:
- Run `scripts/check-contract.sh` and `tests/run.sh install-check` after registering the reference
  and before writing its body, to see the roster accept it.

**Validation**:
- [Automated]: `tests/run.sh` and `scripts/check-contract.sh` pass.
- [Manual]: `grep -rniE "ahima|hcpro|wearediagram|diagram administrator|claude-opus" skills/umbraco-17/reference/umbraco-17-guide-generator`
  finds nothing, and the spell-cards total matches `find skills -name SKILL.md | wc -l`.

---

### Final — Record the durable behavior *(a spell you cast, not an implement-step)*

> **Prompt**: Run `/feature update editor-guides`. Fold **only** the user- or
> operator-observable behavior changes from this work into the existing capability doc — do not
> create a new feature doc. Leave architecture and migration acceptance criteria in the shipped
> spec; they are point-in-time and must not appear as Rules. Amend *Regeneration never silently
> overwrites human work* for unedited AI text, and add rules for ignoring a component, marking a
> guide up to date, and global blocks. Add a revision note dated today describing what changed.
>
> **Validation**: The capability doc describes current behavior with no transition-style ("goes
> from… to…") Rules; no new feature doc was added.

---

## File Summary

| Action | File |
|--------|------|
| Modify | `skills/umbraco-17/spellbook/guide/scripts/guidelib/__init__.py` |
| Create | `skills/umbraco-17/spellbook/guide/scripts/guidelib/fingerprint.py` |
| Modify | `skills/umbraco-17/spellbook/guide/scripts/guidelib/changeplan.py` |
| Modify | `skills/umbraco-17/spellbook/guide/scripts/guidelib/audit.py` |
| Modify | `skills/umbraco-17/spellbook/guide/scripts/guidelib/inventory.py` |
| Create (if not in changeplan.py) | `skills/umbraco-17/spellbook/guide/scripts/guidelib/mark.py` |
| Modify | `skills/umbraco-17/spellbook/guide/scripts/guide.py` |
| Modify | `skills/umbraco-17/spellbook/guide/SKILL.md` |
| Modify | `skills/umbraco-17/reference/umbraco-17-guide-scaffolding/SKILL.md` |
| Create | `skills/umbraco-17/reference/umbraco-17-guide-generator/SKILL.md` |
| Modify | `tests/make-guide-fixtures.sh` (and the regenerated `tests/guide-check/`) |
| Modify | `scripts/check-install.sh` |
| Modify | `README.md`, `docs/spell-cards.md`, `docs/layout.md`, `CHANGELOG.md` |
| Create | `_work/guide-generator-parity/validation.md` |
| Update | `_features/editor-guides.md` (fold observable behavior only; **no new file**) |
