# Spec for owasp-security-review-rules

> This spec captures initial requirements and design rationale. For **current system
> behavior**, see the doc named on the **Work type** line below — a new feature doc for a new
> capability, an existing feature doc for a change, or a `docs/` runbook for a fix.

branch: robot-denny/owasp-security-review-rules
design reference (if any): none

**Work type**: change-to code-review
**Feature doc**: code-review

## Summary

Review already covers security — it is the quality reviewer's **first** focus area, and it owns the
rule that a committed secret is a Blocker whose credential must be rotated rather than merely removed.
What review cannot currently do is say *what standard it checked against* or *which security areas it
swept*. So a finding arrives as an assertion rather than as a citation, and a clean review is
indistinguishable from a review that never looked.

This increment adds a technology-agnostic **security reference** to core, holding the OWASP Top 10
taxonomy and the citation convention, and gives the **quality reviewer** explicit ownership of it. Its
security findings then carry an OWASP category, and its `Clean` section names the OWASP areas it swept.

**No fourth reviewer.** Discovery rejected that: security is a split of the quality reviewer's existing
sections rather than an addition, `reviewer-discipline` requires evidence that duplication actually
reaches a reader before a new domain boundary is assigned, and no such evidence exists. The roster
stays three.

**Why core rather than a stack pack**, which was the leading alternative: [ADR
0003](../../adr/0003-how-core-reaches-a-stack-pack.md) forbids an L0 file naming a pack, so the quality
reviewer could only repeat the generic "consult installed pack guidance" line it already carries —
meaning a pack-only version requires no change to the reviewer at all, and delivers no ownership, no
OWASP-naming `Clean` section, and no guaranteed citation. Packs are opt-in besides, which would make
the claim conditional on install.

Full framing, options, and rejected alternatives: [discovery.md](discovery.md).

## Functional Requirements

- **FR1 — A security reference exists in core**, holding the OWASP Top 10 category list, what each
  category means, and what to look for generically. Technology-agnostic: it names no framework,
  templating helper, ORM, or language.
- **FR2 — The quality reviewer owns it.** Its checklist points at the reference, so consulting it is an
  instruction rather than a possibility.
- **FR3 — Every security finding carries its OWASP category** — number and name — alongside the file
  and line the evidence standard already requires.
- **FR4 — A review names the OWASP areas it swept and found clean**, in the `Clean` section that already
  exists to distinguish "checked and fine" from "not checked".
- **FR5 — The OWASP revision is named in exactly one place**, so moving to a new revision is a
  single edit. The accepted maintenance cost is only acceptable while it stays one edit.
- **FR6 — The reference states which categories a change-scoped review cannot reach**, and what would
  cover them instead. Routing must be generic, since core cannot name the unit that covers them.
- **FR7 — The reviewer roster stays three.** No new agent is registered; the install checker,
  `/code-review`, and `/retrofit` are untouched.
- **FR8 — Existing security rules keep their force.** The committed-secret Blocker and its rotation
  requirement are additive targets for citation, never rewritten by it.

## Possible Edge Cases

- **A change with no security-relevant code at all.** The review must not claim OWASP coverage it did
  not perform. A `Clean` section listing areas it had no code to check against is the failure mode that
  makes the whole mechanism dishonest.
- **One defect spanning two categories** — a hardcoded credential is both a secrets exposure and an
  authentication failure. Two citations on one finding, or one chosen and why?
- **A cited category that does not exist in the named revision.** The categories renumber and rename
  between revisions, so a citation drawn from a reviewer's own knowledge can name a category the pinned
  revision does not have. This is the risk the whole citation mechanism rests on.
- **A non-security finding.** A naming or duplication finding must carry no OWASP category; a spurious
  citation is worse than none, because it teaches the reader to discount every citation.
- **The performance reviewer meets a security-shaped line.** It owns bounded waits on outbound calls;
  where an outbound call *goes* is a different defect on the same line. It must not acquire the
  citation convention by proximity.
- **A stack pack raises a security finding.** Until the deferred pack pass lands, one report can carry
  a cited generic finding beside an uncited pack finding. Accepted, but the report should not imply the
  uncited one was unchecked.
- **A reviewer running alone.** `reviewer-discipline` says a lone reviewer raises what it would
  otherwise leave to another. Citation is per-finding, so it should be unaffected — worth confirming
  rather than assuming.
- **An empty diff.** Existing behavior stands: report and stop, with no security claim either way.

## Acceptance Criteria

- **AC1** — A change containing a security defect yields a finding naming the OWASP category, number
  and name, alongside its file and line.
- **AC2** — A review of a change that contained security-relevant code names, in its `Clean` section,
  the OWASP areas it checked and found clean.
- **AC3** — A finding that is not a security defect carries no OWASP category.
- **AC4** — A committed secret is still reported as a Blocker requiring rotation, now additionally
  carrying its category.
- **AC5** — The OWASP revision is named in exactly one place across every file this increment touches;
  changing revision is one edit.
- **AC6** — The reference names which OWASP categories a change-scoped review cannot reach and what
  covers them instead, naming no technology.
- **AC7** — The reference ships as a core unit under the same gates as every other, all five of which
  fail before the work and pass after: frontmatter completeness (check 6), no technology names in L0
  core (check 8), self-hosting coverage (check 11), the install checker's core roster (check 13), and
  README reachability (check 18).
- **AC8** — The reviewer roster is still three: no agent added, and `scripts/check-install.sh`'s
  reviewer list, `/code-review`'s role table and merge sections, and `/retrofit`'s dispatch are
  unchanged.

## Scenarios (Draft)

Draft BDD scenarios derived from the acceptance criteria using Example Mapping. Each Rule maps
to an acceptance criterion; scenarios use concrete examples. These get verified and refined
after implementation — the feature doc holds the verified version.

### Rule: A security finding names the standard it is measured against

```scenario
Scenario: A finding on unvalidated input reaching a query names its category
  Given a change whose search handler passes a visitor's search term straight into a data query
  When the change is reviewed
  Then the review reports the unvalidated term reaching the query
  And the finding names the injection category by number and name
  And it names the file and the line
```

```scenario
Scenario: A finding on an endpoint with no authorization decision names its category
  Given a change adding an endpoint that deletes a saved report and makes no authorization decision
  When the change is reviewed
  Then the review reports the missing authorization decision as a Blocker
  And the finding names the broken-access-control category by number and name
```

### Rule: A review names the security areas it swept and found clean

```scenario
Scenario: A change with security-relevant code and no security defects says what was checked
  Given a change adding a contact form that validates every submitted field and stores no credentials
  When the change is reviewed
  Then the review reports no security findings
  And it names the security areas it checked and found clean, including input handling and secrets
```

```scenario
Scenario: A change with no security-relevant code claims no security coverage
  Given a change that only renames a variable and reflows a comment
  When the change is reviewed
  Then the review names no security areas as checked and clean
  And it does not state that the change was reviewed against the security standard
```

### Rule: Only a security defect carries a security category

```scenario
Scenario: A naming finding carries no category
  Given a change whose new helper is named "doStuff" and whose logic is otherwise sound
  When the change is reviewed
  Then the review reports the name as not expressing intent
  And that finding names no security category
```

### Rule: Citation is added to the existing secrets rule, not substituted for it

```scenario
Scenario: A committed credential keeps its rotation requirement and gains a citation
  Given a change that commits a live third-party access token into a tracked settings file
  When the change is reviewed
  Then the review reports the committed token as a Blocker
  And it states the credential must be considered compromised and rotated, not merely removed
  And the finding names its security category by number and name
```

### Rule: The standard's revision is stated in one place

```scenario
Scenario: Moving to a newer revision is a single edit
  Given the security reference naming the revision of the standard it follows
  When a reader searches every file this increment touched for a revision year
  Then the revision appears in exactly one place
```

### Rule: The review says which parts of the standard it cannot reach

```scenario
Scenario: A reader learns that dependency age is out of reach
  Given a reader consulting the security reference to see what a review covers
  When they look for the category covering out-of-date dependencies
  Then the reference states that a review of a single change cannot reach it
  And it names the kind of assessment that can, without naming a product or a technology
```

```scenario
Scenario: A change that updates a dependency is still reviewed
  Given a change that raises a dependency to a version with a known advisory
  When the change is reviewed
  Then the review reports the raised dependency, because the change itself is in scope
  And it does not claim to have assessed the dependencies the change did not touch
```

### Rule: Security review adds no reviewer

```scenario
Scenario: A developer running review still gets three reviewers
  Given a project with the toolkit installed and its reviewers registered
  When a developer asks for a change to be reviewed
  Then three reviewers cover the change
  And the security findings arrive among the quality reviewer's findings
  And no separate security reviewer is dispatched
```

## Open Questions

- **How much of the standard the reference carries, versus relying on the reviewer's own knowledge.**
  The accessibility precedent ships no criterion text at all and attaches citations from the model's
  knowledge. The recommendation here is to ship the **category list** — number, name, one-line meaning,
  and what to look for generically — because that is what makes a citation checkable and makes FR5's
  single-edit revision bump possible, while leaving the standard's prose unshipped. **Untested, and it
  is the mechanism AC1 rests on:** whether an agent-authored citation is accurate enough to put in
  front of a client has never been measured here. `/plan` should include a step that checks citations
  against the pinned revision rather than assuming them.
- **Which revision to pin.** The mechanism is settled by FR5; the choice is an authoring decision for
  `/plan`. Whichever is current at authoring, and stated once.
- **Whether the `Clean` section names every category or only the ones with relevant code.**
  `reviewer-discipline` says to evaluate "only where relevant code appears in the diff", so listing all
  ten every time would be padding — but a `Clean` section naming three areas is weaker evidence than
  one naming eight, and evidence is the whole point. Consider whether the reference should distinguish
  *checked and clean* from *considered and not applicable*.
- **Whether the category belongs on the quality reviewer's severity mapping as well as on each
  finding.** The accessibility reviewer does both — its severity table maps Blocker to a Level A
  failure. Doing the same here would re-pin the revision in a second place and break AC5, so the two
  precedents conflict and one has to give.
- **Whether the routing line for the out-of-reach categories is useful once it is generic enough to
  pass check 8.** ADR 0003 permits describing a *kind* of guidance only. "A repo-level assessment
  covers this" may be too vague to act on, in which case saying plainly that it is out of reach is
  better than routing nowhere.
- **Whether this increment ships review evals.** The roadmap already carries an unresolved item —
  `dotnet-review-rules` ships eight review cases and nothing runs them. Planting a defect per category
  here would multiply that debt if the answer is still unsettled, so this may be a reason to sample
  rather than cover.
- **Whether the pack pass is genuinely deferrable.** Discovery accepted one report carrying a cited
  generic finding beside an uncited pack finding. If that reads as *unchecked* rather than *uncited*, it
  undermines the evidence AC2 exists to produce, and the deferral is wrong.

## Testing Guidelines

Meaningful tests for the cases below, without going too heavy:

- **The five contract gates, run before and after.** Checks 6, 8, 11, 13, and 18 each fail on a core
  reference that is added without its frontmatter, with a technology name, without its self-hosting
  symlink, without its roster entry, or without its README row. Running `scripts/check-contract.sh`
  before the corresponding edit is a genuine RED, and each is deterministic — this is the increment's
  primary RED→GREEN signal, and it needs no new harness.
- **Planted-defect review artifacts**, following the `review-failure-modes` precedent of committing
  before-and-after review outputs under `_work/<slug>/assets/`. One planted defect per scenario group
  is enough; a defect per category is the over-coverage the evals open question warns about.
- **A negative test on AC3** — a change with a naming defect and no security defect, confirming no
  category is attached. Over-citation is the failure mode that discredits the mechanism, and nothing
  else in the suite would catch it.
- **A negative test on AC2's second scenario** — a comment-and-rename change, confirming the review
  claims no security coverage. This is the dishonesty case, and it is invisible to every gate above.
- **A grep for the revision year across the increment's touched files**, which is AC5 stated as a
  command.
- **No new fixture case in `tests/`.** `tests/make-fixtures.sh` samples four core skills rather than
  enumerating them, so a new reference needs no fixture — confirm that rather than assume it.
