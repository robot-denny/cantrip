---
name: testify
description: Read a capability's Test Coverage table as a work queue — report which of its documented scenarios nothing proves, separate the ones that can be tested now from the ones blocked on missing test infrastructure, then write and run tests only for the rows a person approves and record in the doc what each run established. Use when asked what is untested, for the missing tests for a capability, or to close the gap between what a capability doc claims and what anything actually verifies.
disable-model-invocation: true
argument-hint: "<capability> — the name of a documented capability"
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
---

The user's argument: **$ARGUMENTS** — the name of a capability this project documents.

This spell asks one question and only one: **what does this project claim to do that nothing
proves?** Every other spell in the chain either decides what to build or builds it. This one reads
what has already been decided and reports where the evidence is missing.

The queue is not something this spell invents. A capability doc already ends with a **Test Coverage**
table mapping each of its scenarios to the test that proves it and to a status. That table is the
work queue, and reading it is the whole of the input.

Artifact locations follow the layout in the `workflow` skill — consult it rather than assuming paths.

## What this spell does not own

Three boundaries, and each of them is a place where a plausible next step belongs to somebody else.

- **It holds no knowledge of any test library.** How a test is written for this project's technology
  is a stack pack's answer, or the project's own tests'. Ask; never assume.
- **It never establishes the project's testing architecture.** Where proving a scenario needs a
  harness the project does not have, it says what is needed and stops. Deciding to adopt one is
  spec-sized work.
- **It never writes a scenario.** The doc's scenarios are `/feature`'s, and behavior that was never
  written as a scenario is invisible here. Where this spell notices such behavior in passing, it
  names it and points at `/feature` — it does not quietly add a row to make its own queue longer.

## Step 1 — Resolve the argument to a capability doc

The argument names a **capability** — an area of the system, the way capability docs are named.
Resolve it against the workspace layout described in the `workflow` skill.

Match loosely on the way people actually type a capability's name: casing, spacing, and hyphenation
are all noise. "article card", "Article Card", and `article-card` name one doc.

**When nothing resolves, the usual cause is that the argument named an increment rather than an
area.** The `workflow` skill records that the two are routinely different — an increment called
`placeholder-graphics-imageless-cards` amends a doc called `article-card`. So do not treat an
unresolved name as a missing capability to go and document, and do not quietly work on the nearest
doc as though it had been the one asked for. Instead:

- Say plainly that no capability of that name is documented.
- Offer the documented capabilities whose names are nearest to what was asked for, and let the
  person say which was meant.
- If the project documents no capabilities at all, say that instead, and name writing the first
  capability doc as the thing that has to happen before this spell has anything to read.

In every one of those cases, read no further and write nothing.

## Step 2 — Read the Test Coverage table

Read the whole doc, not only its table. The scenarios under the `Rule:` headings are what a test
would have to assert; the table only records what is currently proved. One without the other is not
enough to propose anything.

Then pair each table row with the scenario it names, and read its status. **The capability doc
template in the `workflow` skill is the authority on what each status claims** — read it there rather
than re-deriving it. What matters here is narrower: what each status means for this queue.

| The row says | What it is to this spell |
|---|---|
| `Covered` | Already proved. Not work. Leave the row alone. |
| `Test failing` | A test already asserts this scenario and did not pass last time it ran. Something exists; this is not a missing test. |
| `Not covered` | Specified, and nothing asserts it. **This is the queue.** |
| `Not covered (code-derived)` | Nobody specified this — it is a reading of the code. Unproved, but not unproved in the same way, and it is never mixed in with the rows above. |
| `Not coverable — <reason>` | The project has already decided. Skip it, never propose it, and carry its recorded reason forward so a reader can judge whether it still holds. |

**Four of those record an observation; the last records a decision.** The rows are listed in the
template's order, which puts three statuses beginning "Not cover-" together, and the third of them
means the opposite of the two above it — somebody weighed this scenario and chose, rather than nobody
having reached it yet. Read the whole of "Not coverable —" before treating a row as an ordinary gap.
Turning one into a proposal quietly converts a decision into a backlog item.

A scenario with no row at all is unproved and belongs in the queue. A row naming a scenario the doc
no longer contains is drift rather than work — note it and move on.

**When the doc has no Test Coverage table, or the table is empty, say so and stop.** That is not the
same as everything being unproved, and it is not the same as everything being proved: the doc simply
does not say, and this spell has no queue to work from. Do not manufacture one by treating every
scenario as untested — a project may perfectly well have tests the doc never recorded, and reporting
them as gaps would be a guess wearing the clothes of a finding. Building that table is `/feature`'s
job: it matches scenarios to tests across the project and writes the result. Name it and let the
person run it.

**When the doc has a table but no scenarios, there is nothing to prove.** Say that in a sentence
rather than reporting an empty queue as a result.

## Step 3 — Learn where tests live and how they are run

Two facts about the project are needed before anything can be proposed, and neither of them is this
spell's to know.

Where tests live in this project, and what they are named:

**Slot:** `.agents/config/stack.md` → `## Tests`
**If empty:** infer from existing test files. If the project has no tests yet, propose a location and
flag plainly that you are establishing a convention rather than following one — never settle it
silently.

Here that flag goes into the report, before anything is written — and the decision itself is not this
spell's to make. A project with no tests and no recorded place to put them needs somebody to choose a
testing convention deliberately, which is `/spec`'s work, not a side effect of asking for one
capability's missing tests.

How the project's tests are run:

**Slot:** `.agents/config/stack.md` → `## Build`
**If empty:** infer the build and test commands from the repo root and state which you used; if
genuinely ambiguous, ask rather than guessing.

If the way to run tests genuinely cannot be worked out, **say that it could not be determined and
invent nothing.** A command guessed at is worse than an absent one: it fails for a reason that has
nothing to do with the behavior under test, and the failure reads as the capability's.

Running a project's tests means running whatever command those two slots resolve to, which is why
this spell's tool grant is not narrowed to a named command — an installed toolkit cannot know the
command ahead of time, so it cannot name it in the grant. **That makes the boundary this spell's to
hold rather than the permission system's: use the shell only to run the test command the slots above
resolve to, and nothing else.** Not to inspect the project, not to move files, not to clean up after
a run. Every other thing this spell does has a tool of its own.

## Step 4 — Take library idiom from the project, never from this spell

Before proposing anything, find out how this project already writes a test.

If an installed stack pack or project skill offers guidance for the technology in play, consult it:
how tests are named and structured, which kind of test is the cheapest one that proves a given kind
of change, and what a test of each kind is allowed to reach for.

**Its absence is not an error.** Where no such guidance is installed, follow the conventions of the
tests the project already has — **read the ones Step 3 already located rather than searching again**,
since finding where tests live and reading how they are written are two questions about the same
files — and **name the tests you took those conventions from** in the report,
so the person reading it can tell a convention that was observed from one that was assumed. If the
project has no tests at all to read, there is no convention to follow yet — that is the case Step 3's
`## Tests` fallback describes, and it goes to `/spec` rather than being settled here.

## Step 5 — Report the gap, before anything is written

**The report is the first output on every path, and nothing is written before it.** Not a test file,
not a row in the table, not a directory scaffolded in advance of one. Somebody who asked what is
unproved has asked a question, and the report is the answer to it; writing first and reporting
afterwards turns a question into a fait accompli.

Report only the rows the queue picked up. **Do not recite what is already proved.** A report that
lists the five covered rows back buries the three that are the answer, and a reader who has to find
the finding learns to skim.

**Every row lands in exactly one place, and the order these tests are applied in is what makes that
true.** The groups below are not defined on one axis — one by a status the row carries, two by
conditions the project is in — so a row can answer to more than one description at once, and a sort
that does not say which wins will file it twice. Apply these in order and stop at the first match:

1. **Recorded `Not coverable`?** Settled already. It goes in the closing list described at the end of
   this step and nowhere else — not a group, not a question.
2. **Names nothing that can be compared?** A question rather than work, whatever else is true of it.
   It goes in the questions list.
3. **Reading `Not covered (code-derived)`?** Group 3 — and where it is *also* blocked on missing
   infrastructure, note that on the row but leave it in group 3. Whether the project means to promise
   the behavior at all is the cheaper question, and answering it *no* dissolves the other one;
   scoping infrastructure for behavior nobody meant to commit to is the wrong order to spend in.
4. **Blocked on missing infrastructure?** Group 2.
5. **Anything left** — group 1.

A row appearing twice, or disappearing without a reason given, is a sorting error rather than a style
choice.

**When nothing is unproved, say so and stop.** A sentence or two: every scenario in this doc names a
test that proves it, and there is nothing here to do. Do not propose a second test for a scenario
that already has one, do not offer to strengthen the tests that exist, and do not go reading code for
behavior the doc never described in order to have something to report. A short answer to a question
whose answer is short is the right result, not a thin one.

### The three groups

Where there is work, group it — and **group it because each group asks the reader for a different
decision**, not because three headings look tidier than one list. Print the group's question with the
group, so somebody who stops at the heading still knows what is being put to them. Leave an empty
group out rather than printing an empty heading.

#### 1. Writable now

The project already has everything these tests need: somewhere they go, a way to
run them, and a way to make the observation the scenario describes. *The decision this group asks
for: approve this test, or don't.* Nothing else stands between the row and a test, which is why these
are the only rows the approval step can act on.

#### 2. Blocked on missing test infrastructure

The scenario is specific enough to test, but the
project has no means of making the observation it demands. **Name what each blocked row needs,
individually** — a way to exercise the system as a whole rather than one piece of it, a way to
observe what a person sees on screen, a way to put the system into a known starting state and take it
back afterwards, a way to run the thing under test apart from what it depends on. Describe the *kind*
of capability that is missing and what it would let a test do. **Where several rows are blocked on
the same missing capability, describe it once and list the rows beneath it** — a paragraph repeated
per row pads the report without telling the reader anything the second time. **Never name a product, a library, or
a tool**: which one to adopt is the project's decision informed by whatever stack guidance it has
installed, and a name dropped into this report reads as a recommendation this spell is in no position
to make. *The decision this group asks for: whether to take on that capability at all.* That is a
different size of question from approving a test, which is why no test is offered for these rows and
none is written for them.

#### 3. Inferred rather than specified

The rows reading `Not covered (code-derived)`. Keep them apart
from group 1 even where they are just as writable, and carry the warning with the group: **proving
one of these promotes somebody's reading of the code into a contract the project never agreed to.** A
test does not only observe behavior, it pins it — after this, the next person to change that behavior
argues with a failing test rather than with a paragraph. *The decision this group asks for: whether
this behavior is something the project means to promise.* That is a question about the doc rather
than about testing, and the honest answer to some of them is that the scenario should be specified
properly first.

### The scenario too vague to test

Some rows describe an outcome nothing can check. **The test for that is not taste. Apply it
literally: does the scenario name a value something could be compared against, or anything at all
that distinguishes the outcome being present from its being absent?** "A card with no image shows a
placeholder" names something that is either there or not. "A card looks right on mobile" names
neither — there is nothing to compare it to, and no observation that could come back "no".

Where a row fails that test, **report it as a question for whoever wrote the doc, and propose no test
for it.** Name the scenario, say that it names nothing that can be compared, and ask the specific
question that would fix it — what should be on screen, what value should it hold, what would somebody
see if the behavior were broken. Then leave it alone.

**Do not quietly file a vague row under group 1 with an assertion you supplied for it.** A guessed
assertion is worse than an empty row because it fills one: the table goes on to read as proved, the
coverage report agrees, and what is actually pinned down is whatever you happened to guess — which
nobody agreed to and nobody will re-read. An empty row is at least honest that nothing has been
decided.

These are not a fourth group of work. They are questions going back, and they belong in a short list
of their own beneath the groups.

### The rows already decided against

A row reading `Not coverable — <reason>` records a decision somebody took deliberately. It is not
work. **Do not offer it, do not sort it into a group, and do not raise it again on the next run** — a
spell that re-proposes a settled question every time it is cast teaches people to stop reading its
reports.

Do say they are there. Close the report with a short list — one entry per row, naming the scenario
and **the recorded reason repeated as the doc words it**, not summarized. A count on its own hides
them, and a single crowded line stops being readable the moment one reason runs past a clause; give
each row its own entry, the way the questions above get theirs.

The reason is what a reader judges the decision by. One written because nothing here could render a
page, say, stops being true the day something can. A reason nobody is shown is a decision nobody can
revisit.
