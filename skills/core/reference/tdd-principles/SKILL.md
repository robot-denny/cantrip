---
name: tdd-principles
description: How to write a test that proves behavior and survives refactoring — asserting observable behavior rather than implementation artifacts, sourcing expected values independently, one behavior per cycle, and what serves as a RED→GREEN signal in a project with no harness. Consult when writing a test, filling a step's Test-first block, judging what a test should assert, or diagnosing a test that broke without a behavior change.
---

# Test-driven development principles

The *sequencing* of TDD is already enforced elsewhere: `/plan` writes the test before the
implementation it covers, and `/implement-step` requires the RED run before the GREEN one. This file
is about something sequencing does not determine — **what the test actually asserts.**

The distinction is load-bearing. A test can be written first, go red, then go green, and still be a bad
test. Correct order does not imply a correct assertion.

## What this owns, and what it does not

| Concern | Where it lives |
|---|---|
| *What* behavior to specify, before code exists — discovery, examples, Given/When/Then | `bdd-principles`, consumed by `/spec` |
| *How* to write a test that proves it and keeps proving it | here, consumed by `/plan` and `/implement-step` |
| The idiom of a particular test library — its API, its mocking utilities, its fixture builders | a stack pack, or whatever documents that library |

The dividing line for the third row: **this file owns what makes a test correct and durable; a pack owns
what makes it idiomatic to a specific library version.** The first outlives package upgrades. The second
does not, which is why copying it here would go stale invisibly.

## Assert observable behavior, not implementation artifacts

Test through the interface where the behavior can actually be observed. The implementation behind it
should be free to change entirely without the test changing at all.

This is an axis the toolkit already draws one stage earlier: `/spec` and `/feature` both exclude
implementation details from behavior docs. Same line, later — **what a feature doc must not describe, a
test must not couple to.**

The diagnostic is sharp: **a test that fails when the behavior did not change is testing the wrong
thing.** Refactoring is the usual trigger, and the usual mistake is to fix the test.

Concretely, prefer:

- the value a user observes over the file or artifact that produces it
- a return value or rendered result over an internal call count
- the public entry point over a private helper
- state read back through the same interface that wrote it over state read straight out of storage

## The presence assertion

Called out on its own because it is the most common instance and it fails in a specific, expensive way.

**A test asserting that a rule, class, string, or file merely *exists* is fragile by construction.** It
couples to the artifact instead of the behavior, so it fails in both directions:

- it **passes** when the artifact is present and does not work
- it **fails** when the artifact is correctly removed or renamed

The second costs more. It turns a correct deletion into a failure, and such a test usually lives nowhere
near the thing it guards, so the suite covering the changed code runs green while another goes red.

`reviewer-discipline` carries the review-time counterpart, and `/implement-step`'s envelope carries the
search-before-done rule. **Both of those catch this after it has been written. This is the rule that
keeps it from being written.**

Ask what the artifact is *for*, and assert that instead.

**When you genuinely must assert on text** — a generated file, a serialized payload, output with no
observable surface — assert on a normalized or pattern-matched form rather than an exact string.
Whitespace, key order, and minification all change without the behavior changing, so an exact-match
assertion converts every formatting change into a failure and trains the team to update expected values
without reading them. Match the part that carries the meaning; ignore the rest.

## Expected values come from an independent source

A test that computes its expected value the same way the implementation does passes by construction. It
can never disagree with the code, which is the only thing a test is for.

The expected value has to come from somewhere the implementation did not:

- a literal lifted from the spec's scenarios
- a worked example computed by hand
- a known-good result captured before the change

**This is one of the things `/spec` is for.** Example Mapping produces scenarios with concrete values,
and those literals are exactly the independent source this rule needs — so a test derived from a spec
scenario is tautology-proof for free, while one invented at implementation time is not.

Where no specified value exists, write the literal down and record where it came from.

## One behavior per test, one behavior per cycle

Work vertically: one behavior's test, then that behavior's implementation, then the next one.

**Vertical is about breadth, not co-location.** `/plan` may put a test and its implementation in separate
steps when the implementation is large — every step has to fit a fresh context, and that allowance is
deliberate. What must not happen is tests for *several* behaviors written before *any* of them is
implemented. That tests imagined behavior rather than observed behavior, and commits to a structure
before anything has exercised it.

So splitting one behavior across two steps is fine. Batching many behaviors into one test-writing step
is not.

## When the project has no harness

Not every project has a test runner, and a new one usually does not yet. **An instruction that assumes
one is unusable in exactly the case where guidance matters most.**

Where there is none, treat **a build plus one concrete, written-down manual check** as the RED→GREEN
signal: state what you expect to see before the change and what you expect after, then verify both.
Author the target test file anyway, so it is ready the moment a harness lands.

Resolving *whether* a project has a harness is not this file's job — `/plan` and `/setup` read that from
the project's configuration, and they own its fallback. This section is only about what stands in for a
test when there is nothing to read.

A manual check only counts if it was written down **before** implementing. Recalled afterwards, it is a
rationalization, and it will agree with whatever the code does.

## Evidence, not attestation

When a check cannot be run mechanically, **produce an artifact — never a claim.** "Verified" and "looks
correct" are indistinguishable from real results and cost nothing to write, which is what makes them
worthless.

Capture the output, save the rendered result, print the actual values. If evidence requires a fixture
that does not exist, create one, capture, then clean it up. Then say plainly which checks are evidenced
and which are not: **an unevidenced check reported as passing is worse than one reported as
unverifiable**, because the second can be followed up and the first cannot.

## Agreement on what to test happens before implementation

What is worth testing is a judgment call, and it belongs to the human. Everything cannot be tested, so
deciding at implementation time means deciding alone and late.

In this toolkit that agreement already has a home: the plan's **Test first** blocks, agreed when the plan
is agreed. **Do not add a confirmation step during implementation.** A dispatched worker has no access to
the user and cannot ask — a question raised there either stalls or gets answered by the worker on the
user's behalf, which is the same thing as not asking.

If the plan is silent about a behavior that clearly warrants a test, say so in the report rather than
quietly widening scope.

## Tests written after the code

Sometimes the code comes first — a change that skipped the flow, or a capability documented from code
alone. Two rules still hold:

- **A test written after the code has to fail first anyway.** Break the behavior, or assert a wrong
  value, and watch it go red. A test that has never failed proves only that it runs.
- **A rule read out of code is not a tested rule.** `/feature`'s coverage vocabulary keeps these apart —
  `Covered`, `Not covered`, and `Not covered (code-derived)`. Do not promote the third into the first by
  writing a test that asserts whatever the code currently happens to do. That is the tautology above
  with extra steps.

## Refactoring is a review concern

Keep the red-green cycle to making the test pass. Improving the surrounding code belongs to review, where
`reviewer-discipline` holds a refactor to a measurable bar.

The spells are already arranged this way — `/implement-step` scopes its worker to the step and forbids
drive-by refactoring, and review is where the rest is raised.

## What not to do

- **Do not assert on an implementation artifact** when the behavior itself is observable.
- **Do not compute the expected value the way the implementation computes it.**
- **Do not write tests for several behaviors** before implementing any of them.
- **Do not report a check as passing** when you produced no evidence for it.
- **Do not test a private helper** because the public path is awkward. The awkwardness is the finding.
- **Do not skip the failing run.** A test that has never been red is unproven, whenever it was written.
