# Roadmap

Now / Next / Later for the toolkit itself. Consuming projects keep their own; this one is about
what Cantrip ships.

An item earns a place here when it is a decision or a piece of work someone would otherwise
rediscover. Loose ends that only matter inside one increment stay in that increment's spec.

---

## Now

Nothing in flight. The `dotnet` pack shipped and is archived at
`_work/shipped/dotnet-pack/`.

---

## Next

**Pack-authoring meta-skill.** The direct parallel to `design-system-authoring`: a model-invoked
reference that fires when someone sets out to add a pack, turning [ADR 0015](adr/0015-what-a-stack-pack-is-and-what-it-owes.md)'s
rules into something followed rather than remembered. This is the highest-leverage item here,
because every other pack-related cost is paid per pack until it exists.

**Structural gate checks for pack discipline.** Four of the `dotnet` increment's real findings were
caught by greps run by hand — a pack restating core's reasoning instead of citing it, naming a
sibling pack's file path, duplicating its own project-owned list across two units, drifting off the
shared severity scale. Each is deterministic and cheap, and each currently depends on a reviewer
happening to think of it. As checks they run on every commit and cost nothing per additional pack.

**A contributor path for packs.** The intent is that people outside this repository write packs for
the stacks and versions they work in — an `umbraco-13` beside the `umbraco-17`, an Episerver, a
Python. That makes two things load-bearing that are currently optional: the authoring skill above,
and something a contributor can run to check their pack before proposing it. Worth deciding how far
that goes — a template and a checklist, or a conformance script, or an accepted-packs list.

---

## Later

**Resolve the content evals.** `dotnet-review-rules` ships eight cases describing what a review of a
planted defect should produce, and nothing runs them. Their value is highest while authoring a pack
and lowest as regression protection, so the answer probably falls out of the authoring skill above
rather than being a separate piece of work. Until then they are a specification for a test, and the
feature doc says so.

**A pack conformance check.** `scripts/check-pack.sh` — could someone outside this repository ship a
pack that works? Only worth building if third-party packs are ever a goal; noted so the question is
asked deliberately rather than answered by drift.

**Backfill the capability docs.** `_features/dotnet-guidance.md` and `_features/code-review.md` are
both thin by design and say so. `/feature`'s from-code mode is the intended remedy. Neither is
urgent; both get less accurate as the units they describe grow.

**An evidence convention.** Two increments have now finished by asking whether their captured
before-and-after artifacts earn a commit, and answered differently — `review-failure-modes` committed
140K, `dotnet-pack` left 364K uncommitted and said why. Whatever the rule turns out to be, the two
should end up consistent. Recorded in `_work/shipped/review-failure-modes/spec.md` with the reasoning
on both sides.

---

## Settled, no work outstanding

- **How a pack declares the version it targets** — [ADR 0015](adr/0015-what-a-stack-pack-is-and-what-it-owes.md)
  §3. One pack per major where majors break, per-feature annotation where they add, decided by
  whether a project on an older major would get *correct* guidance from the pack. `umbraco-17` and
  `dotnet` were both already right; the rule that made them right was not written down.

---

## Recently shipped

- **2026-08-15** — The `dotnet` pack: authoring and review guidance for C#, an optional detection
  line letting a pack tell `/setup` how to read an answer from the repository, and a gated pack
  roster that had drifted to two of eight units
  (`_work/shipped/dotnet-pack/spec.md`, [ADR 0014](adr/0014-dotnet-pack-and-the-detection-line.md))
- **2026-08-13** — Two language-agnostic review failure modes into core, and the domain boundary that
  stops one defect drawing two rows in a merged report
  (`_work/shipped/review-failure-modes/spec.md`)
