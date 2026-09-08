---
name: security-review-rules
description: The OWASP Top 10 categories a security review checks against, what each one means, what to look for in a change, and the convention for citing a category on a finding. Consult when reviewing a change for security defects, when deciding which category a defect belongs to, when a review needs to say which security areas it swept and found clean, or when writing a project's own security review rules.
---

# Security review rules

A security finding is worth more when it names the standard it came from. Without one, a finding
reads as an assertion, and a review that found nothing looks exactly like a review that never
looked.

This file holds the category list, so a finding can cite where it belongs and a clean review can say
which areas it actually swept.

## The pinned revision

Categories below are the **OWASP Top 10:2025** list, the eighth installment of the standard.

The revision is named there and nowhere else in this file, which is what makes moving to the next
one a single edit. Identifiers are written bare, as `A01` through `A10`, and the revision above is
what they resolve against.

## The ten categories

The table below lists 10 categories, one per row. Each row gives the identifier, the category
name, and what the category looks like inside a change.

| ID | Category | What to look for in a change |
|---|---|---|
| A01 | Broken Access Control | An authorization decision the caller can influence. An identifier read from the request and trusted, a check present on one path and absent on another, a route relying on being unlinked rather than on a rule, or a request that reaches another origin's resources on the caller's behalf |
| A02 | Security Misconfiguration | Defaults left as shipped, verbose errors reaching a response, permissive transport or cross-origin settings, and features left enabled that the change does not use |
| A03 | Software Supply Chain Failures | A dependency added or bumped with no stated reason, a floating or unpinned version, an unverified source, and build tooling able to run arbitrary code while installing |
| A04 | Cryptographic Failures | Sensitive values stored or sent without protection, a weak or hand-rolled algorithm, a fixed or reused initialization value, and a secret committed to source |
| A05 | Injection | Input reaching an interpreter as part of a command rather than as data. Data queries, shell invocations, path resolution, and template output rendered without escaping |
| A06 | Insecure Design | A control the design never had, rather than one built wrongly. A missing rate limit, an absent trust boundary, and a workflow whose steps can be replayed or reordered |
| A07 | Authentication Failures | Credential handling, session lifetime and invalidation, recovery flows, and any path letting a caller prove identity more cheaply than the primary one does |
| A08 | Software or Data Integrity Failures | Untrusted input deserialized, an update or extension path that does not verify what it loads, and state trusted because it round-tripped through the client |
| A09 | Security Logging & Alerting Failures | A security-relevant event that leaves no record, a log line capturing a secret, and a failure swallowed where nothing can notice it |
| A10 | Mishandling of Exceptional Conditions | An error path that fails open, a partially applied change left behind by a failure, and a message disclosing internals to whoever triggered it |

## What a change-scoped review cannot reach

Two of these are only partly visible in a diff, and a review scoped to one change should say so
rather than imply coverage it cannot have.

**A06 is a property of the whole system.** A diff can show a missing check on the path in front of
you. It cannot show that the trust boundary was drawn in the wrong place three modules away.

**A03 depends on facts outside the change.** A diff shows a version moving. Whether that version
carries a known advisory, and how old the rest of the dependency set has grown, are questions about
the project rather than about the change.

Both need a whole-codebase security assessment, which is a different piece of work with a different
scope. A change-scoped review reaches what the diff contains and claims nothing further.

## Citing a category on a finding

Every security finding names its category by identifier and name, alongside the file and line the
evidence standard already requires. So `A05 Injection` rather than `A05`, and never a number alone.

**A finding that is not a security defect carries no category.** An unclear name, a duplicated
helper, a missing test: none of these get one. Over-citation is worse than none at all, because a
reader who sees one category attached to something that plainly is not a security defect learns to
discount every other citation in the report.

Where a defect genuinely spans two categories, cite the one whose control failed rather than
listing both. An identifier read from the request and trusted is A01, even when the value then
reaches a data query.

## A host tool's own security command

Some agent tools ship a security review command of their own. Where one exists, it is a useful
second pass and finds things a diff-scoped review does not. Nothing here depends on it, and its
absence changes nothing about the rules above.
