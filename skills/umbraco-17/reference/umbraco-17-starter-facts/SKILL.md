---
name: umbraco-17-starter-facts
description: Verified Umbraco 17 platform facts that are easy to get wrong and often fail silently — Management API shapes and quirks, content-model behaviors where an unset property is indistinguishable from a false one, and AI plus Search configuration traps. Consult when writing or reviewing Umbraco code, authoring E2E tests against the Management API, designing schema, debugging a silent failure, or wondering whether behavior you are seeing is a bug or a platform behavior.
---

# Umbraco 17 starter facts

Facts harvested from production Umbraco 17 work, each carrying provenance so you know when it was
last confirmed and which versions it applies to.

**These are claims to verify, not gospel.** They were true when recorded, against the versions noted.
The first time you encounter one in a project, confirm it holds there — then mark it project-confirmed
in your own memory. That is how starter facts become earned facts.

## Why these facts and not others

The selection criterion is **silent failure**. Every fact here describes something that does not throw,
does not warn, and does not appear in a log — it simply behaves differently than a reasonable person
would expect, and the symptom surfaces somewhere far from the cause.

An error message you can read is not worth a starter fact. A property that returns empty instead of
raising, a rebuild that reports success having indexed nothing, a config key that is silently refused —
those cost hours, and they are what these files are for.

## The topic files

| File | Covers |
|---|---|
| `references/management-api.md` | Management API shapes, auth, and the test-helper package's known quirks |
| `references/content-model.md` | Published content and generated model behaviors, and rendering traps |
| `references/ai-and-search.md` | Umbraco.AI and Cms.Search configuration, and their silent failure modes |

## How each fact is recorded

The format matches the `memory-discipline` entry shape, because that is what these become once a
project confirms them:

```markdown
## <The claim, as a statement>

<Detail.>

**Why:** <what makes this true>
**How to apply:** <what to do differently>
**Type:** pattern | false-positive-suppression | fixed-with-guard
**Applies:** umbraco >=17 <18
**Verified:** 17.x (YYYY-MM)
```

**`Applies:` is a range, and it matters.** A project on a different minor may find a fact no longer
holds — several here were fixed in a later patch, and one describes a bug in a specific beta. Treat a
fact whose range does not cover the project's version as **suspect, not authoritative**, and verify
before acting on it.

## Version hygiene

**On a version bump, re-verify every version-tagged fact.** This is the maintenance cost of shipping
facts at all, and skipping it is how a helpful fact becomes a confidently wrong one.

The facts most likely to expire are the ones describing a bug rather than a design: a test-helper typo
someone will eventually fix, a beta-version crash, a serialization bug corrected in a patch release.
Each of those is marked `fixed-with-guard` or carries a narrow `Applies:` range precisely so a future
reader knows to check rather than trust.

**Slot:** `.agents/config/stack.md` → `## Models`
**If empty:** check whether `*.generated.cs` model files are committed to the repo. If they are, the
project regenerates them manually; if they are absent, models are generated at build or run time and
cannot be read from source.
