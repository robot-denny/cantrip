# Discovery: OWASP security review rules

_Discovery input for `/spec` — produced by `/explore` on 2026-09-03. Scope: lightweight._

## Problem framing

**Who is affected.** Dev leaders and a technical/business executive who must speak to the
organization's application-security posture — before a sale, to clients who prioritize security, and
after an incident on something the team built. Developers are affected second-hand: an individual
does not know what they do not know, and will not know to ask until there has been a problem.

**What the current situation costs.** Security scrutiny depends on which developer wrote the change
and on the profile of the project. Some have it on their radar; some do not. Nothing records what was
checked, so the exec has no way to say what testing occurred or what guardrails were in place.

**What is worth keeping.** `code-reviewer` already treats security as its **first** focus area —
secrets, sensitive data in client-visible markup, missing authorization, input validation — and owns
the rule that a committed secret is always a Blocker whose credential must be rotated, not merely
removed. The packs already carry substantive stack-specific security rules. None of this is missing;
it is unlabelled and uncited.

**Observed versus assumed.** The exec's difficulty is observed, as is the unevenness across
developers and projects. *Not* observed: that reviews are missing vulnerabilities they should catch.
The gap is legibility and consistency of diligence, not detection rate.

**The problem in one sentence.** Whether a change gets security scrutiny depends on which developer
wrote it, and nothing records what was checked — so we can neither hold a floor under obvious flaws
nor evidence our diligence to a client or after an incident.

**Explicitly out of scope**, stated by the invoker: equalizing security knowledge across the dev team;
building a deterministic security-checking application; producing full codebase vulnerability reports
(that rare need is met by other tooling and a substantive audit, not by this).

## Outcomes sought

Three success criteria, as stated:

1. The exec can respond that we have checks in place that review code against OWASP's top
   recommendations.
2. A developer gets feedback on where code deviates from or creates problems for security, **cited to
   an OWASP standard**.
3. Because OWASP revises only every few years, needing to hand-update the reference to a new revision
   is **accepted** — the same known weakness the WCAG handling already carries.

## Options considered

**A — A fourth `security-reviewer` agent.** Dispatched in parallel with the existing three.
*Near-term:* satisfies all three criteria, and is the most quotable ("four reviewers, one is
security"). *Long-term:* it is a **split** of `code-reviewer`'s sections 1–2, not an addition, so
`reviewer-discipline`'s *Where two domains abut* must gain a new boundary — and that section sets a bar
for doing so: evidence the duplication actually reaches a reader, which does not exist here. *Worse
at:* cost spread thin and easy to half-do. "Three" is load-bearing in `scripts/check-install.sh`
(REVIEWERS array and the reviewer-discipline asset list), `tests/make-fixtures.sh`, the role table and
numbered merge sections of `/code-review`, the explicit three-name dispatch in `/retrofit`, README ×2,
`docs/concepts.md` ×3, `docs/spell-cards.md`, and four BDD scenarios in `_features/code-review.md`.
Rejected by the invoker directly: no appetite for chopping up `code-reviewer` and `perf-reviewer` to
make room.

**B — Amend `code-reviewer` only.** Harden its existing sections 1–2 into an OWASP-cited checklist
in place. *Near-term:* cheapest possible; satisfies criteria 2 and 3. *Worse at:* criterion 1 is
satisfied only in prose, with no artifact to point at; and it makes security roughly half of one
agent's seven-area checklist, where an agent with seven priorities serves the first one less well.

**C — Point at the Claude Code built-in `/security-review`.** *Near-term:* zero authoring cost.
*Worse at:* all three criteria. It sits outside `reviewer-discipline` — different severity vocabulary,
no per-finding citation, no diff-only scope guarantee, no project memory, no L2 slot — so it cannot
merge, which is the contract's whole purpose. It is also a host-vendor built-in Cantrip neither
controls nor can assume present. Kept as a *mention* in the reference, not a dependency.

**D/E — A core reference owned by `code-reviewer`.** `security-review-rules` in
`skills/core/reference/`, holding the OWASP taxonomy and citation convention; `code-reviewer` amended
to own it, so its findings carry the OWASP category and its `Clean` section names the OWASP areas
swept. *Near-term:* satisfies all three criteria. *Long-term:* the accepted staleness cost is paid in
one file rather than spread across a persona line and a severity table, which is how the WCAG weakness
came about. *Fit with the repo:* this is the pattern already in use — `umbraco-17-review-rules` and
`dotnet-review-rules` feed all three reviewers on the shared severity scale; nobody added a CMS
reviewer or a C# reviewer. It creates no new voice in the merge and therefore no domain boundary to
negotiate. **Chosen.**

**F — Put the whole thing in the `dotnet` pack.** Considered on the grounds that .NET is the primary
audience and pack rules may name their technology, so the rules could be concrete and checkable.
*Rejected on two counts.* First, [ADR 0003](../../../adr/0003-how-core-reaches-a-stack-pack.md) forbids an
L0 file naming a pack; `code-reviewer` could only repeat the generic "consult any installed stack pack
guidance" line it already carries, so pack-only requires **no change to `code-reviewer` at all** — and
delivers no owned domain, no OWASP-naming `Clean` section, and no guaranteed citation. The ownership
that makes criterion 1 evidenced is precisely what pack-only cannot provide. Second, packs are opt-in,
so criterion 1 would become install-conditional — reproducing the framing's pain as "some projects"
instead of "some developers." ADR 0003's own consequence states the principle: core stays
pack-agnostic so the core-only baseline "is a real product rather than a stripped one."

## Trade-offs & second-order effects

**Two of the ten OWASP categories are structurally out of reach.** The diff-only scope rule is
non-negotiable — unchanged code is out of scope — so **A06 Vulnerable and Outdated Components** (a
dependency bump in the diff is reviewable; the existing tree is not) and **A04 Insecure Design** cannot
be covered by any reviewer here. The reference must say so plainly rather than let it be discovered
under pressure. This shapes the claim the exec should make: not "we check our code against the OWASP
Top 10", but **"every code change is reviewed against the OWASP Top 10, with each finding cited to its
category"** — true, defensible, and stronger in a room because it names a repeatable process rather
than claiming completeness. `codebase-audit` is repo-level rather than diff-level and already has a
security finding slot in its report template; A04 and A06 are reachable there, which is also the
substantive-audit path the invoker would reach for on the rare occasion one is wanted.

**Category-to-reviewer mapping is lopsided, which is why single ownership works.** Injection, access
control, cryptographic failures, misconfiguration, auth failures, integrity failures, security logging,
and SSRF all land in `code-reviewer`'s sections 1–2. `perf-reviewer` grazes one — it owns bounded waits
on outbound calls, while SSRF is about *where* the call goes: different defect, same line.
`accessibility-reviewer` gets essentially nothing.

**The layer contract constrains what the reference may say.** `scripts/check-contract.sh` holds core to
technology-agnostic. So the reference cannot name a templating helper, an ORM's raw-SQL path, or a
framework's antiforgery attribute — which are the concrete, checkable forms of A03. Generic in core,
specific in packs, as with every other reviewer. This is the trade the invoker named as "sacrificing
some value," and it is smaller than it appears because the concrete layer already exists in the packs;
what those files lack is category framing and citation, which is taxonomy work and therefore genuinely
generic.

**Indirect benefit:** the reference gives packs and project L2 slots a citation convention to conform
to, so security findings become comparable across stacks rather than each reviewer's own dialect.

**New problem elsewhere:** until the pack follow-on lands, an Umbraco or .NET developer gets an OWASP
citation on generic findings and a bare finding on the pack's existing security rules — inconsistency
*inside* one report. Accepted deliberately as far cheaper than inconsistency across projects.

**Naming.** Do not call the unit `security-review` — it collides with the Claude Code built-in of that
name. `security-review-rules` follows the existing `<scope>-review-rules` convention.

**Reference cost.** One more core reference adds only its description to every session's context
(~3,100 tokens covers the whole toolkit today), and core references install together, so there is no
opt-in question to answer.

## Direction

**Core-only, owned by `code-reviewer`.** One new `security-review-rules` reference in
`skills/core/reference/`, technology-agnostic, carrying the OWASP Top 10 taxonomy, the citation
convention, an explicit statement of which categories a diff-scoped review reaches and which need
something else, and a mention of the host built-in as a complement rather than a dependency.
`code-reviewer` is amended to own it: its checklist points at it, its findings carry the OWASP
category, and its `Clean` section names the OWASP areas swept.

**What carried it.** It satisfies all three success criteria; it needs no new voice in the merged
report and therefore no new domain boundary, which the invoker explicitly did not want; it matches the
pattern the repo already uses to add review substance; and it keeps the accepted staleness cost payable
in one file. Pack-only was the leading alternative and failed on ADR 0003 — it cannot deliver the
ownership that makes criterion 1 evidenced.

**Deliberately deferred: carrying OWASP citations into `dotnet-review-rules` and
`umbraco-17-review-rules`.** A mechanical pass, better done once the core reference has been seen in
use, so the citation convention is not copied into two packs before it has been exercised.

## Open questions for /spec

- **Which OWASP revision, and how it is stated.** 2021 is current with a 2025 revision in circulation.
  Pin the revision in one named place in the reference so the accepted hand-update is a one-line edit,
  and decide whether the `code-reviewer` severity mapping may reference categories at all or must stay
  revision-free.
- **How much OWASP substance the reference carries versus relies on the model for.** The WCAG precedent
  ships no criterion text and attaches citations from the model's own knowledge. Whether an
  agent-authored citation is accurate enough to put in front of a client is untested here, and it is the
  mechanism criterion 2 rests on.
- **Whether the `Clean` section names all ten categories or only those with relevant code in the diff.**
  `reviewer-discipline` says to evaluate "only where relevant code appears in the diff," so ten rows
  every time would be padding — but a `Clean` section that names three is weaker evidence than one
  naming eight. This is the criterion-1 evidence surface and deserves a deliberate answer.
- **Whether A04 and A06 get an explicit routing line to a repo-level audit**, or are simply declared out
  of reach. The audit unit lives in the `dotnet` pack, so a core file cannot name it (ADR 0003) — the
  routing would have to be generic.
- **Whether `_features/code-review.md` needs updating**, given it describes the capability's behavior
  and the roadmap already carries a backfill item against it.
