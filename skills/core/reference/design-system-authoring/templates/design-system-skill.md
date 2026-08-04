---
name: design-system
description: >-
  <ENUMERATE THE ARTIFACTS AND VERBS. This description decides whether the skill ever loads,
  so write it long. Cover every verb — create, scaffold, build, add, extend, restyle, match —
  and every artifact that renders UI, by file type and by component kind (cards, banners,
  alerts, callouts, heroes, listings, grids, sections, variants). Include the casual
  phrasings verbatim: "whip up a banner", "build a component", "make a new variant", "match
  the rest of the site" — including ones that name no design system at all, because those are
  exactly when conventions get bypassed. Then state the SKIP conditions: back-end logic,
  query or API fixes, anything that changes nothing visual. A skill that loads constantly
  gets ignored.>
---

# <Project> Design System

<One paragraph: this project has an established design system, fixed conventions, and
whichever load-bearing mechanism Step 1 identified. New UI must slot into all of them.>

**The goal of this skill is not novel design — it is faithful conformance**, so that new work looks and
behaves exactly like what exists. There is one right look here, it is already in the codebase, and the
job is to find it and match it.

## The one thing you must not break: <mechanism>

<Name the load-bearing mechanism. Explain what it does in one or two sentences — what it lets someone
change, and how it works: the indirection, the wrapper, the resolved value.>

<Then the wrong version and the right version, concretely:>

Writing `<the literal, hardcoded form>` instead of `<the indirected form>` means the new UI **silently
ignores <what the mechanism controls>**. It will look correct in the default state and break the moment
someone <exercises the mechanism>.

**That regression is the main thing this skill exists to prevent.** Read `<the reference file covering
it>` before writing any <affected kind of> markup.

## Workflow

Work pointer-first: **the codebase is the source of truth, not this skill.** The conventions live in
`<where>` and in the existing components, and they evolve — so read them fresh each time rather than
trusting a remembered snapshot.

1. **Find the closest existing exemplar.** Before writing anything, read two or three existing
   components nearest in layout and purpose to what you are building — `<name 3–5 representative
   ones>`. Copy their structure, their wiring of <the mechanism>, and their class vocabulary. Matching
   a sibling is faster and more correct than composing from first principles.

2. **Load the conventions you will touch:**
   - `<reference file>` — **always**, for anything involving <the mechanism>. This is the
     highest-value file.
   - `<reference file>` — <what it covers: components, type scale, spacing, iconography>.
   - `<reference file>` — **only when** <the narrower condition>.

3. **Build it, matching the exemplar** — <the layers this project's components span>.

4. **Self-check against the checklist below** before declaring done.

## Non-negotiable checklist

<Derive these from what actually goes wrong in this project — review findings and reviewer memory are
better sources than the system's documentation, because they cover what people get wrong rather than
what the system intends. Each item must be verifiable by looking at the diff, and must name the
artifact rather than the intention. Keep it short enough to actually be run.>

- [ ] **<Values come from the indirection, never literals.>** <The concrete form required, and the
      forms that are forbidden.>
- [ ] **<The wrapper carries what it must carry.>**
- [ ] **<Runtime-resolved state is read, respected, and passed down.>**
- [ ] **<Existing component classes are reused, not reinvented.>** <Name them.>
- [ ] **<Spacing, radius, elevation, motion match siblings.>**
- [ ] **<Iconography comes from the project's one set.>**
- [ ] **<Semantics are correct independent of visual size>** — pick the element for the document's
      structure, then style it; never pick a tag for how big it looks.
- [ ] **<Any structural requirement this project's build imposes.>**
- [ ] **<If it is author-configurable: the wiring that gives editors the same controls existing
      components have.>**

## A correct component at a glance

From `<path to a representative component>` — **note the pattern, not the specifics:**

```
<A real, complete, short example. Choose a representative component rather than a clever one; an
exemplar with an unusual exception teaches the exception.>
```

<One line naming what to notice: which mechanism is wired where, which shared classes are reused.>

## See it in the browser

<If there is a living style guide, name its path and say to render or read it.>

**The real test:** <switch the mechanism — change the theme, toggle the mode — and confirm the UI
responds.> Reading the diff cannot catch the silent failure described above; only exercising the
mechanism can.
