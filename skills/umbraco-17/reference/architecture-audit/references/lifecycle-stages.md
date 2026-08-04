# Lifecycle Stages

The stage of the codebase shapes every recommendation. The audit must classify the stage first and tailor findings accordingly. Without this, the report becomes generic and ignorable.

## The four stages

### Greenfield

The codebase was created recently and hasn't accumulated significant non-starter material yet.

**Heuristics**:
- First commit < ~60 days old.
- Total commits < ~50.
- Starter-template fingerprints still recognizable (boilerplate files unchanged, default README sections).
- Few or no custom services / controllers / business logic files beyond the starter.

**How to tailor**:
- Be ambitious. Foundational P0s are cheap right now.
- Recommend doc/spec/ADR scaffolding even if the user hasn't asked.
- Recommend layering, anti-corruption seams, CI, and pre-commit hooks now — every week of delay makes them harder to add.
- The report can run shorter; there's less codebase to evidence.

### Growing

The codebase is under active development. Custom code is being added regularly. Starter fingerprints are visible but being overridden.

**Heuristics**:
- Active commits in the last 30 days.
- More than ~50 commits total.
- Multiple contributors (or one prolific contributor with sustained activity).
- Custom services, controllers, or features extend beyond the starter.
- Test coverage is partial or absent (often a tell — tests come last during growth).

**How to tailor**:
- "Lock in good patterns before they ossify" is the frame.
- Identify where the starter scaffolding is being outgrown — the seams that are starting to hurt.
- Recommend one or two concrete refactors that pay off most. Avoid wholesale architectural overhauls.
- Note which P0s would have been cheaper at greenfield stage but are still worth doing.

### Mature

The codebase is stable. Structural change is slow; most commits are content / config / bug-fix.

**Heuristics**:
- First commit > ~12 months old.
- Recent structural churn is low (few new top-level folders, few new top-level files).
- Tests exist (or their absence is a long-standing accepted fact).
- A clear "shape" — anyone familiar with the codebase could draw the architecture from memory.

**How to tailor**:
- Bias toward small, scope-limited, high-leverage recommendations.
- Heavy refactor P0s should be rare and *well-justified* — name the specific risk being mitigated.
- Audit for the things mature codebases tend to drift on: retry/timeout coverage, doc freshness, secret hygiene, dependency churn.
- Recommendations should fit into a normal sprint, not a quarter.

### Brownfield-inherited

The codebase is being assessed by someone who didn't build it. The user is taking ownership of unfamiliar code.

**Heuristics**:
- The user mentions inheriting, taking over, or being new to the codebase. **This signal is decisive — if the user says it, classify as brownfield regardless of age.**
- Often: long gaps in commit history (months of stillness, then sudden activity) — suggests an ownership transition.
- Often: undocumented patterns or naming conventions that don't match anything in `docs/`.

**How to tailor**:
- **Map first, recommend second.** The audit's most valuable section in brownfield mode is the codebase map — what lives where, what each component is responsible for, where the surprises are.
- Lead with "understand before changing."
- Risk-prioritize findings: flag things that could break, before things that are aesthetic.
- Recommend the new owner write down what they're learning — even an informal `BROWNFIELD-NOTES.md` is valuable.
- Be honest about what you *don't* know about the codebase. The new owner is in the same boat.

## Detection

`scripts/detect-stage.sh` implements an automatic classifier. It outputs one of: `greenfield`, `growing`, `mature`, `brownfield`, or `ambiguous`. If `ambiguous`, the skill asks the user once.

The user can also pass `--stage <name>` to override the classifier — this is the right move when the user knows the context better than the heuristics can.

## Why this matters

Without stage tailoring, audits become useless in two opposite ways:
- For a greenfield codebase, a generic audit produces obvious recommendations the user already knew.
- For a mature codebase, a generic audit reads as "rewrite everything," which is unactionable and gets ignored.

Stage-tailored recommendations land. Generic ones don't.

## Cross-pillar gating rules

Some recommendations are *only* appropriate at certain stages:

| Recommendation | Greenfield | Growing | Mature | Brownfield |
|---|---|---|---|---|
| Adopt Clean Architecture layering | OK | OK if leverage is named | Rarely | Never on first pass |
| Switch logging frameworks | OK | OK if structured is missing | Rarely | Never on first pass |
| Wholesale rename to feature folders | OK | OK if growth pattern fits | Rarely | Never |
| Add ADRs | OK | OK | OK (and overdue) | OK (and especially valuable) |
| Add CI/pre-commit hooks | OK (P0) | OK (P0 if missing) | OK | OK |
| Map the codebase | Skip | Skip | Skip | First |
| Headless migration | OK to plan | OK to plan | Only if business case | Never recommend unsolicited |

The skill should consult this matrix when prioritizing recommendations.
