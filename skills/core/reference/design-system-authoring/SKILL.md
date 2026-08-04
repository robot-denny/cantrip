---
name: design-system-authoring
description: How to write a project's own design-system skill — one that makes an agent conform to an existing visual system instead of inventing a look. Covers finding the load-bearing mechanism that must not break, writing pointer-first guidance that cannot go stale, deriving a checkable conformance list from the codebase, and engineering the description so it triggers on casual requests too. Consult when creating or updating a design-system skill, when front-end work keeps drifting from established conventions, or when an agent's markup looks plausible but ignores the project's theming or token system.
---

# Authoring a design-system skill

This is a **meta-skill**: it does not describe any design system. It describes how to write the skill
that describes yours.

The output is a project-owned L2 skill. Its content is entirely specific to your codebase and never
ships with the toolkit — only this method does.

## The problem such a skill solves

An agent asked to "build a card" will produce something plausible and wrong. Not broken — *plausible*.
It will look reasonable in isolation and quietly violate the system: hardcoded colors where tokens
were required, a reinvented button class, a heading chosen for its size rather than the document's
structure.

**The failure is silent and delayed.** Nothing errors. It looks fine in the default state and breaks
the moment someone exercises the part the system was built for — switching a theme, toggling a mode,
viewing at another breakpoint. By then the markup has been copied into three more components.

So the skill's goal is **conformance, not creativity**. Say that explicitly in what you write. The
useful framing: *there is one right look here, it already exists in the codebase, and your job is to
find it and match it.* That is the opposite of greenfield aesthetic exploration, and an agent will
default to the latter unless told.

## Step 1 — Find the one thing that must not break

Every mature front-end system has a **load-bearing mechanism** that new UI can silently opt out of.
Find it first; it becomes the spine of the skill.

Look for the thing that is *indirected on purpose*:

- A token or variable layer standing between markup and literal values
- A class applied to a wrapper that changes everything inside it
- A value resolved at runtime and passed down a tree
- A mode or state that branches styling
- A configuration surface that lets a non-developer change appearance

The test for load-bearing: **if new UI ignores it, does anything fail loudly?** If the answer is no —
it just quietly stops responding to the mechanism — that is your spine.

Write it up as its own section, near the top, before the workflow. State the wrong version and the
right version side by side, and **name what breaks and when**: not "use tokens" but "hardcode a color
and the component silently ignores the administrator's theme — it will look correct until someone
switches, then break."

If the project has more than one such mechanism, lead with the one whose violation is hardest to
notice.

## Step 2 — Write pointer-first, not encyclopedia-first

The strong temptation is to document the design system inside the skill. Resist it.

**Conventions live in the code and they evolve. A skill restating them becomes wrong without anyone
noticing** — and a confidently wrong convention is worse than none, because it will be followed.

So point rather than restate:

- Name the files where conventions actually live — the stylesheet holding the token definitions, the
  file defining component classes, the service resolving runtime values.
- Say **read them fresh each time** rather than trusting a remembered snapshot. Make that instruction
  explicit; an agent will otherwise rely on what the skill says.
- Restate inline only what is a *rule* rather than a *value*: "colors come from tokens, never
  literals" is durable; a list of the token names is not.

The line to hold: **the skill teaches where to look and what must be true. The codebase supplies the
particulars.**

## Step 3 — Make the workflow exemplar-first

The single most effective instruction is *copy the closest existing thing*.

Have the skill direct the agent to find two or three existing components nearest in layout and purpose
to what is being built, and to copy their structure, their wiring of the load-bearing mechanism, and
their class vocabulary. **Matching a sibling is faster and more correct than composing from
principles**, and it inherits conventions nobody wrote down.

Name specific exemplars worth copying. Choose ones that are representative rather than clever — an
exemplar with an unusual exception teaches the exception.

## Step 4 — Derive a checkable conformance list

Turn the system's rules into a checklist the agent runs before declaring done. Two properties matter:

- **Each item is checkable by looking at the diff.** "Colors are tokens, never literals" can be
  verified. "Follows the design system" cannot.
- **Each item names the artifact, not the intention.** "The wrapper carries the theme class" beats
  "theming is respected."

Derive the items from what actually goes wrong. If you have review history, memory, or a list of
recurring findings, that is the best possible source — a checklist built from real defects beats one
built from the system's documentation, because it covers what people actually get wrong rather than
what the system intends.

Keep it short enough to be run. A twenty-item checklist is not run; an eight-item one is.

## Step 5 — Show one correct example, and say what to notice

Include one real, complete example from the codebase — and label it explicitly: **note the pattern,
not the specifics.** Without that instruction the example gets copied verbatim, exception and all.

Follow it with one line naming what the example demonstrates, so the reader knows what they were meant
to see.

## Step 6 — Engineer the description to catch casual requests

This is the step most often got wrong, and it decides whether the skill ever loads.

The skill must trigger on **"whip up a banner"** and **"make it match the rest of the site"** — not
only on "follow the design system." Those casual asks are precisely when someone bypasses conventions,
so a description that only matches formal phrasing loads exactly when it is least needed.

A description that triggers reliably:

- **Enumerates the artifacts** — every file type and component kind that renders UI.
- **Enumerates the verbs** — create, scaffold, build, add, extend, restyle, match.
- **Includes casual phrasings** verbatim, including ones that name no system at all.
- **States the skip conditions**, so it does not load for back-end logic, a query fix, or a change
  that alters nothing visual. A skill that loads constantly gets ignored.

Write it long. This is one of the few places where length is the feature.

## Step 7 — Name the visual verification

End with how to *see* the result. If the project has a living style guide, name it. If theming or modes
can be switched, say that switching them and confirming the UI responds **is the real test** — the one
that catches the silent failure from Step 1, which no amount of reading the diff will.

## Assembling it

`templates/design-system-skill.md` in this skill directory is the skeleton, with each section marked
for what to fill from your project.

Where it goes: the project's own skill directory, as **L2 content the toolkit never updates**. That is
deliberate — a design system is the least portable thing a project has, and its skill should be
editable without any concern for reconciling against upstream.

## What not to do

- **Do not describe an aesthetic.** No adjectives about how the site should feel. Conformance to what
  exists, not a direction.
- **Do not duplicate the token list, the class list, or the type scale.** Point at them.
- **Do not write it once and leave it.** When a convention changes, the pointer usually survives and
  the restatement does not — which is the argument for having minimized restatement.
- **Do not make it a spell.** This is guidance an agent should reach for whenever it touches UI, which
  means model-invoked. A user-cast spell only fires when someone remembers to cast it, and the whole
  problem is the request that did not mention design at all.
