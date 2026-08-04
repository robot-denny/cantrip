# 0007. The repository stays under a personal account for now

**Status:** Accepted
**Date:** 2026-08-04

## Context

The direction doc planned to move the repository under an agency-owned namespace. Checking before
acting on that found three things that reframed the decision:

- **The namespace the doc named does not exist on GitHub** — it returns 404. The doc had used the
  company's trading name, which is not the same as its GitHub organization name.
- **The authenticated account holds `admin` on that real org**, and members may create public repos
  there. So a transfer needs nobody else's involvement, and admin would be retained afterward.
- **Every repository in that org is private.** Cantrip would be its **first public repo** — and one
  carrying scrubbed-but-real content harvested from client work.

So the choice was never "personal versus the name in the doc". It was: keep the personal account, move
to the real agency org, or create a neutral one.

## Decision

**Keep `robot-denny/cantrip`.**

There is no technical reason to move. The install path works, the canary's committed lockfile records
this owner accurately, and a personal namespace is a perfectly ordinary home for a public toolkit.

Moving into the agency org would make it that org's first public repository, which is a posture
decision for the agency rather than a side effect of tidying a URL. It can be made later, deliberately,
with the costs below understood.

## What a later move costs, and why it grows

`skills-lock.json` records the source as a **literal string**, per skill, and consumers commit it. It
is not metadata — `/update-toolkit` reads it to know where to fetch from, so **the recorded string is
the update path.**

Two consequences:

- **The redirect is conditional.** GitHub redirects a transferred repo, so fetches would keep working —
  *unless the old name is ever reoccupied*, at which point every consumer's lockfile silently points at
  a different repository. The failure mode is silent: `update` fetches something and reports success.
- **The string is duplicated into every consumer by design.** Vendoring means there is no central
  registry naming the canonical location, so a stale owner can only be corrected inside each consumer's
  repo — which the toolkit's author has no write access to.

**So the cost is linear in adoption and payable only by other people.** Today it is one consumer, one
committed lockfile, and a handful of file references. After the toolkit is presented publicly, every
installer bakes the string in.

**If a move happens, do it before public distribution, not after** — and re-install in every known
consumer so their lockfiles record the new owner rather than relying on a redirect.

## Consequences

- No work now; the canary stays accurate.
- The README, ADRs, and rationale notes continue naming this owner correctly.
- Revisit **before** any public announcement rather than after. That is the last cheap moment.
- Unverified: the exact behavior of a GitHub transfer redirect against a lockfile naming the old owner.
  If a move is ever seriously considered, test it on a throwaway repo first rather than trusting the
  reasoning above.
