---
name: umbraco-17-planning
description: Stack-specific planning guidance for Umbraco 17 projects — how to inspect live backoffice schema before designing schema steps, which authoritative backoffice-extension skill to consult for dashboards, property editors, workspaces, modals, trees, context API, entry points, entity actions, and block editor custom views, the layer vocabulary an Umbraco feature spans, and the step order that usually works. Consult when planning or sequencing work on an Umbraco project, especially anything touching document types, element types, compositions, data types, or a backoffice extension.
---

# Planning guidance for Umbraco 17

Supplements the generic planning engine with what is specific to this stack. Everything here is
additive — the generic sequencing rules still apply.

## Inspect live backoffice state before designing schema steps

If the work involves document types, element types, compositions, or data types, **query the
live Umbraco instance via MCP tools before designing the schema steps.** This surfaces real IDs,
existing property editors, and reusable compositions that cannot be reliably derived from `.uda`
files alone.

Useful MCP tools for planning:

| Tool | What it gives you |
|---|---|
| `mcp__umbraco-mcp__get-all-document-types` | Every existing document type and composition |
| `mcp__umbraco-mcp__get-all-data-types` | Reusable data types by name, rather than hardcoding IDs |
| `mcp__umbraco-mcp__get-document-type-by-id` | A specific type's properties and groups |
| `mcp__umbraco-mcp__get-data-type-root` / `get-data-type-children` | Browsing the data type tree |

**Record any IDs or aliases discovered here in the plan's Key Decisions section**, so
implementers don't need to look them up again.

The `.uda` files remain the committed source of truth for property structure.

**Slot:** `.agents/config/paths.md` → `## Umbraco`
**If empty:** locate each by search — the Deploy revision directory by its `*.uda` files,
views by their `*.cshtml` files, and the extension root by its `umbraco-package.json`. If no
`*.uda` files exist, the project is not using Deploy — read schema from the running instance
via MCP instead.

## Route backoffice extension work to its authoritative skill

If the work involves a backoffice extension — dashboards, property editors, workspaces, modals,
trees, context API, entry points, or any TypeScript/Lit component under the extension root —
**consult the matching skill before writing the plan.** Umbraco 17 uses Lit web components and a
specific extension registry pattern; these skills carry authoritative current documentation that
training data may not cover accurately.

| Extension type | Skill to consult |
|---|---|
| Dashboard | `umbraco-cms-backoffice-skills:umbraco-dashboard` |
| Property editor UI | `umbraco-cms-backoffice-skills:umbraco-property-editor-ui` |
| Workspace | `umbraco-cms-backoffice-skills:umbraco-workspace` |
| Modal / dialog | `umbraco-cms-backoffice-skills:umbraco-modals` |
| Tree / tree item | `umbraco-cms-backoffice-skills:umbraco-tree` / `umbraco-tree-item` |
| Context API | `umbraco-cms-backoffice-skills:umbraco-context-api` |
| Entry point | `umbraco-cms-backoffice-skills:umbraco-entry-point` |
| Entity actions | `umbraco-cms-backoffice-skills:umbraco-entity-actions` |
| Block editor custom view | `umbraco-cms-backoffice-skills:umbraco-block-editor-custom-view` |

**Testing an extension routes to a second skill set**, `umbraco-cms-backoffice-testing-skills`, which
covers end-to-end and integration setup for backoffice extensions. Consult it when a plan's Test-first
steps target an extension rather than server-side code — it ships from the same marketplace as the
skills above and is separately enabled, so one being present does not mean both are.

**Skip these skills for:** Management API or content CRUD, C#/Razor/.NET patterns, or any task
where the pattern is already clearly visible in the codebase.

### If these skills are not available

They ship as Claude Code plugins, enabled per project, and are **recommended companions rather than
requirements** — this pack plans without them. But do not let the absence pass silently:

- **Plan from the codebase's existing extension patterns instead**, and name the closest analogue you
  used, so a reviewer can see what the plan was modelled on.
- **Record it in Key Decisions naming what is missing and how to fix it** — not merely that a skill was
  unavailable. Something like *"planned the dashboard from the existing `<name>` extension because
  `umbraco-cms-backoffice-skills` is not enabled; enabling it would give authoritative registry and
  manifest guidance."* A note that says what would improve the plan is actionable; one that only records
  an absence reads as a shrug.
- **If the project has no existing extension of that type either**, say so explicitly and treat the
  plan's extension steps as unvalidated. That is the case where the absence actually costs something: no
  authoritative guidance *and* no local precedent means the manifest and registry details are being
  inferred, and inferred registry wiring fails at runtime rather than at build.

### Declared companions

**Companion:** `umbraco-cms-backoffice-skills` — authoritative guidance for the backoffice extension
types in the routing table above
**Companion:** `umbraco-cms-backoffice-testing-skills` — end-to-end and integration test setup for those
extensions

`/setup` reads these declarations to report which are enabled, the same self-describing mechanism it uses
to find `**Slot:**` declarations. **A pack declares its own companions; core never names them** — which is
what keeps core technology-agnostic while still making an external dependency visible at install time.

## The layer vocabulary an Umbraco feature spans

| Layer | Governing constraint |
|---|---|
| **Schema** | `.uda` files are the source of truth. Author via the backoffice or Management API, not by hand-editing. **Schema leads** — nothing downstream compiles against types that don't exist. |
| **Slice (block or page type)** | A view model plus its Razor view, and for page types a controller. Follow the closest existing analogue in the project rather than a generic MVC split. If the project has no analogue yet, say so in Key Decisions and establish the shape deliberately rather than assuming one — the first slice sets the convention. |
| **Client-side components** | Built and bundled separately. Prefer a plain component; reach for a framework runtime only when reactivity justifies the cost. |
| **Backoffice extension** | Loaded by the backoffice host via a package manifest — see the routing table above. |
| **Tests** | Browser and Management API level. Deploy schema is environment-coupled, so prefer API lookups over hardcoded identifiers. |

## Step order that usually works

1. **Schema** — author the types, then regenerate models if the project commits generated models.
2. **Slice** — view model plus view (or controller plus view), then a build check.
3. **Integration** — layout or registration wiring, then a build plus browser check.
4. **Client-side assets** — component plus its mount point, then a build plus browser check.
5. **Tests** — write to RED, confirm GREEN after the prior steps.
6. **Record behavior** — per the generic Step 4 rule 5.

**Backoffice extensions follow their own order** — schema is usually not needed. Sequence as:
extension registration → component → context and state → tests → record behavior.

**Slot:** `.agents/config/stack.md` → `## Models`
**If empty:** check whether `*.generated.cs` model files are committed to the repo. If they are,
the project regenerates them manually; if they are absent, models are generated at build or run
time and cannot be read from source.

When models are committed, a regeneration step belongs in the plan after any schema change; when
they are not, no such step is needed.
