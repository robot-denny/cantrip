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
| `Ruled out — <reason>` | The project has already decided. Skip it, never propose it, and carry its recorded reason forward so a reader can judge whether it still holds. |

**Four of those record an observation; the last records a decision.** `Ruled out` is not a gap
nobody has reached yet — somebody weighed the scenario and chose. Turning one into a proposal quietly
converts that decision into a backlog item, which is why the sort below settles it before anything
else.

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

1. **Recorded `Ruled out`?** Settled already. It goes in the closing list described at the end of
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

A row reading `Ruled out — <reason>` records a decision somebody took deliberately. It is not
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

## Step 6 — Put each test to the reader, one row at a time

Only **group 1** reaches this step. Group 2 has no test to offer until somebody decides on the
missing capability, group 3 asks a question about the doc before it asks one about testing, and the
questions and the settled rows are not work at all. Sorting already happened in Step 5 — do not
re-litigate it here by finding a way to squeeze a blocked row through.

**Approval is per row, never per report.** Show the proposed test for one row, ask about that row,
and move to the next. A reader who approves two of five has approved two: write those two, write
nothing for the other three, and leave those three exactly as the report left them — still unproved
in the table, still offered the next time this spell is cast. **Do not read a general "yes, go ahead"
as approval of every row**; ask which, and say why you are asking. Approving a test is agreeing to
what it pins down, and five of those are five decisions wearing one word.

Until a row's own approval, **nothing exists on disk for it** — not the test file, not an empty file
to be filled in later, not the directory it would live in. A file created in anticipation of a yes is
a fait accompli with a polite question attached.

### What to show for each proposed test

Four things, and they fit in a short block per row:

- **The scenario, as the doc words it.** Not paraphrased — the reader is approving a test *for that
  sentence*, and a paraphrase quietly widens or narrows what gets pinned.
- **Where the test would go and what it would be called**, following the conventions Step 4 took from
  the project.
- **The observation it would make**: what it does, what it then looks at, and the value it compares
  against.
- **Where that expected value came from.** It comes from the scenario — the literal the doc already
  wrote down. `tdd-principles` explains why a value derived the way the implementation derives it
  cannot ever disagree with the code; read it there rather than working it out again. Say in the
  report which sentence of the scenario the value was lifted from, so the reader can check the lift.

### The probes — how this test could pass while the behavior is broken

Say this plainly in the report, once: **for behavior that already works there is no red-to-green
signal available here.** This spell writes a test after the fact, so a passing run proves the test
ran; it does not prove the test would have noticed the behavior missing. Do not describe a passing
run as if a red run had preceded it.

**What stands in for the missing signal is assertion review, and it runs on every path** — draft doc
or verified, before a run that will pass or one that will fail. It is not a fallback for the cases
where a red run was unavailable. It is the check, and a red run would not replace it.

So for each proposed test, answer these **about that test, in its own terms** — naming the actual
value, the actual place, the actual artifact this one test depends on. A generic recital of the
questions tells the reader nothing they could disagree with:

- **If the value were wrong, would this test still pass?** Name the wrong value it would tolerate. A
  test that accepts any non-empty text accepts the wrong text.
- **If the thing under test were produced somewhere other than where the scenario puts it, would this
  test still pass?** Name where else it could appear and still satisfy the check.
- **If nothing at all were produced — an empty result, a blank screen, output that failed to build —
  would this test still pass?** Say what specifically fails in that case, and if nothing does, the
  test asserts nothing.
- **Is this check satisfied by the artifact merely existing?** A file being present, a name being
  defined, a rule being declared. `tdd-principles` calls this the presence assertion and explains why
  it fails in both directions; the fix is to ask what the artifact is *for* and assert that instead.
- **Would this test fail if the behavior changed but the implementation stayed the same shape?** The
  inverse is the diagnostic `tdd-principles` gives for coupling to artifacts rather than to observable
  behavior — a test that fails when the behavior did not change is testing the wrong thing.

**Each probe has to come out "no, this test would fail, because …" before the test is offered.** A
probe that comes out "yes" is not a caveat to note beside the proposal — it is a test that would prove
nothing, and offering it asks the reader to approve a fiction. Rewrite the assertion and probe it
again. Where you cannot get it to "no" for a row, say so and offer no test for that row; an honest
gap beats a filled one.

Then **report the answers with the test — one line per probe, in the order above, all five.** Name
the actual value, the actual place, the actual artifact this test depends on, so each line is
something the reader can disagree with:

- it would fail if the expected text were <the wrong value it would catch>
- it would fail if the thing were produced <the other place it could appear>
- it would fail against an empty result, because <what specifically breaks>
- it asserts <the behavior>, not that <the artifact> is present
- it would fail if <the behavior> changed while the code kept its shape

Those five lines are what the reader is approving, as much as the assertion is. A generic recital
tells them nothing they could push back on.

## Step 7 — Write only what was approved

Write the approved tests, following the conventions Step 4 took from the project's existing tests.
**Where several approved rows belong in the same file — the usual case, since a capability's scenarios
conventionally share one — write them together in one pass** rather than reopening the file once per
row and re-reading its header each time. Nothing else moves: no test for a row that was not approved, no strengthening of a
test that already exists, no tidying of the file you happen to be writing into.

### The provenance header

**Every test file this spell writes opens with a comment carrying three things:**

- **the capability doc these scenarios came from**, named the way that doc is named;
- **every scenario this file covers**, each one word-for-word as the doc words it;
- **the date the tests were written.**

Word-for-word matters more than it looks. The header is what makes the doc-to-test link readable from
both ends, and reading it from the test end is what lets drift be *detected* rather than guessed at by
matching scenario names for resemblance — the guess that breaks precisely when a scenario has been
reworded, which is the moment it was needed. A scenario copied exactly either still matches the doc or
visibly does not.

**Write it as a comment, in whatever way this project's existing tests write comments.** This spell
does not know how a comment is written here and must not decide — take the form from the test files
Step 3 located and Step 4 read, the same way every other convention in this run was taken. Where you
add scenarios to a file that already has a header, **extend its scenario list and set its date to
today** rather than opening a second header beneath the first. The date records when the file was last
written, not when each scenario arrived — the scenario list is what carries which scenarios are
covered, and one header per file is what keeps it readable from the test end.

### Behavior nobody wrote down

Writing a test means reading the code under it, and you will see things no scenario describes.

When you do: **name it in the report** — what the behavior does and where you saw it — and point the
reader at `/feature`, whose from-code mode already owns turning observed behavior into a documented
scenario. **Add nothing to the capability doc yourself: not a scenario, not a row, not a note in the
margin.** A spell that writes its own queue entries decides what the project promises, which is a
decision the doc's author makes and this spell only reads.

## Step 8 — Run the approved tests, and record what that run established

Run the command Step 3 resolved **once**, covering every test approved in this run, and read each
row's result out of that single run's output. **Do not invoke the test command per row.** The command
a project records is the one that runs its tests, not necessarily one that can be narrowed to a named
test — so a per-row reading turns one run into as many full runs as there are approved rows, which on
a capability with a dozen of them is the difference between a wait and an afternoon. Then write the
results into the doc's Test Coverage table.

**One rule, and it has no branches:**

| What the run did | What the row records |
|---|---|
| The test passed | `Covered`, naming the test file |
| The test did not pass | `Test failing`, naming the test file |
| The test could not be run at all | **Unchanged.** The row stays exactly as it was, and the report says the test was written but never run |

Touch only the rows you were approved to test. A row you did not write a test for keeps whatever it
said before, including `Not covered`.

**A failing test is never recorded as `Not covered`.** A test that exists and fails is strictly more
than no test at all; collapsing the two hides the only proof anybody has written and guarantees
somebody writes it again.

### A ruled-out row is never overwritten

It was never proposed, never approved, and never tested, so there is no run to record against it.
Unlike a `Not covered` row — which is waiting for somebody to get to it — this one is finished: a
person decided the scenario cannot be proved here and wrote down why. Overwriting it discards that
decision and puts the question back in the queue for somebody to answer again.

### The rule does not consult the Draft banner

There is no version of it that does. A draft capability doc is **not** a doc for unbuilt behavior:
`/plan` phases its work and `/implement-step` runs one step at a time, so a draft describing six
scenarios of which four are built and passing is the **normal middle state of the flow**, not an
anomaly to be corrected. Record those four as `Covered` and the remaining two as `Test failing`, and
report exactly that.

**A passing test is never reported as proving nothing because the doc it came from is still a draft.**
What guards against a test that passes vacuously is the probes in Step 6, which already ran on every
one of those tests and run on verified docs too — where a rule demanding a red run would reach nothing
at all.

### How a failure is explained

Here is where the Draft banner earns its place, and it is the only place: it selects a **sentence**,
never a status.

- **The doc still carries its Draft banner.** Explain the failure as expected of a capability still
  being built — the scenario is specified, the test now exists, and the work that makes it pass has
  not landed yet. **Do not say the capability is broken.** Nothing is broken that was never claimed
  finished, and a report that cries regression at ordinary work in flight gets skimmed within a week.
- **The banner is gone.** Explain the same failure as the capability not behaving the way its doc
  claims, and say plainly that one of the two is wrong: either the code has a defect, or the doc
  describes behavior the project no longer has. **Name both possibilities and pick neither** — this
  spell has no way to tell which, and guessing hands somebody a bug report or a doc edit they did not
  ask for.

**Same observation, same status, different sentence.** If you find yourself reading the banner while
deciding what to put in the Status column, you have crossed the line this rule exists to hold. Read it
once, when you write the prose, and never before.

### What else in the doc changes, and what does not

**Set the doc's `Last verified` date to today** whenever this run recorded any result. That field is
what tells a later reader how old the table's claims are, and a table of statuses with no date on them
cannot be told apart from a table nobody has checked in a year.

**Add nothing to Revision Notes.** That section records changes to what the capability *does* —
scenarios added, rules reworded, behavior corrected — and `/feature` maintains it when it makes them.
This spell changes none of that; it records what a run observed about claims that did not change. An
entry per cast would bury the substantive history under a log of test runs. `Last verified` carries
the freshness, Revision Notes carries the history, and this spell writes only the first.

### Close with what actually happened

A short account, not a re-run of the gap report: which rows were approved, which tests were written
and where, what each run did, and — where anything could not be run — that it was written but never
run, and why the command could not be worked out. Then whatever Step 7 turned up that no scenario
describes.

## Where a run stops short

Two states end a run before every unproved row has a test, and **neither of them is a dead end.**
Each names what is missing and which spell owns supplying it. A stop that reports only the obstacle
leaves the reader holding a problem instead of a next move, and the next thing they do is guess.

### A scenario blocked on test infrastructure this project does not have

Step 5's group 2 already named what each blocked row needs. What follows from that naming is the
part this section adds.

**The blocked rows do not hold up the writable ones.** Group 1 goes through Steps 6 to 8 exactly as
it would if nothing were blocked — approval per row, the probes, the run, the recorded status. A
capability that can be half proved today is better half proved today than left wholly unproved
pending a decision nobody has scheduled.

**Every blocked row is left exactly as the table had it.** No test, no status change, no placeholder
row promising one later. Nothing was observed about that scenario, so nothing about it is recorded.

**End pointing at `/spec`.** Taking on a way to make an observation this project currently cannot
make is a change to how the project is built — it gets specified, planned, and implemented like any
other work, and it reliably costs more than it looks like it will from inside a coverage report. So
close the run by naming the missing capability once, listing the scenarios waiting on it, and naming
`/spec` as where that work starts.

**Where every unproved row is blocked, the run ends at the report.** There is nothing to approve, so
offer no approval prompt and write nothing at all — not a test, not a directory, not a row. The
report is the entire output: what the missing capability is, which scenarios are waiting on it, and
`/spec` as the next move.

**Do not scope the infrastructure while you are here.** Naming what a test would need to observe is
this spell's job and Step 5 did it. Choosing what to adopt, and weighing what adopting it costs, is
the spec's. A spell that sketches the answer while declining to decide it has decided it anyway,
because whoever writes the spec starts from the sketch.

### A project that has never decided where its tests go

Step 3's `## Tests` fallback already gives the rule: with nothing recorded and no tests to infer
from, propose a location, flag plainly that you would be establishing a convention rather than
following one, and never settle it silently. **This is that same rule at the point where it costs
something** — somebody has asked for a capability's missing tests, and there is nowhere agreed to put
one.

Everywhere else in this spell, how a test is written here is settled by finding the closest existing
test and following it exactly. **That answer is unavailable in this one case, by definition: the
project has no existing test to be closest to**, and whatever gets written now becomes the convention
every later test inherits, whether or not anybody chose it. So, in order:

1. **Ask whether another codebase should be the reference.** A sibling project, or a starter the team
   already trusts, is a far better source than invention, and naming one is a person deciding rather
   than this spell deciding. If one is named, read it, say in the report which conventions you took
   from it, and propose recording them in the `## Tests` slot so the next run does not ask again.

2. **Otherwise stop here.** Concretely, and all four of these:

   - **Say that where tests go has never been decided in this project.** Not that a slot is empty —
     that is a fact about a config file, and it reads as a small thing to go and fix. The fact worth
     reporting is that the project has no testing convention at all.
   - **Decline to decide it, and say you are declining.** Silence would be indistinguishable from
     having no opinion, and the location proposed under Step 3's fallback is a proposal put to a
     person, never a choice acted on.
   - **Point at `/spec` for this project's testing setup.** Where tests live, what runs them, and
     what a test of each kind may reach for are decisions the whole project inherits from whoever
     makes them first. That is spec-sized work, and it is worth someone's deliberate half hour rather
     than a side effect of asking about one capability.
   - **Write no test file.** Not for an approved row, not for the one row that seemed obvious.

The gap report still stands in both branches. Declining to choose a location is not declining to
answer the question that was asked: report the unproved scenarios exactly as Step 5 describes, and
let the stop be about where their tests would go rather than about whether they are missing.

## End with a suggestion, never a cast

Every run that had anything to report closes with a single `Next:` line, and **it is a suggestion.**
This spell casts nothing — it does not run `/code-review` because tests were written, and it does not
run `/spec` because something was blocked. On the page the two look nearly alike; they are not. A
suggestion leaves the next decision with the reader; a cast takes it.

Which line depends on what the run did:

- **Tests were written.** `Next: /code-review` — the tests are code, they were written just now, and
  they earn the same review as anything else this project ships.
- **Anything was blocked** — a scenario waiting on infrastructure, or a project with no testing
  convention. `Next: /spec <the missing capability, or this project's testing setup>`, naming what
  the spec would be for rather than leaving the reader to reconstruct it from the report above.
- **Both.** Print both lines, in that order. The tests that now exist are reviewable today; the spec
  is what unblocks the rest.
- **Only questions came back** — nothing writable, nothing blocked, and every unproved row failed the
  test for naming something that can be compared. `Next: /feature update <the capability>`, because
  what stands between these scenarios and a test is how they are written, and the doc is where that
  gets fixed.
- **Nothing was unproved.** No `Next:` line. Step 5 already said to answer briefly and stop, and a
  suggested next move would manufacture exactly the work that rule refuses to manufacture.
