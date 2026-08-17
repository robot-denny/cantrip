---
name: umbraco-deploy-facts
description: Umbraco Deploy schema mechanics and the remediation paths that actually work — how `.uda` artifacts are written and read, why local files and an environment's database drift apart, which Deploy dashboard control genuinely imports, and the management API calls that clear pending or mismatched entries. Consult when reading or diffing `.uda` files, when the Deploy dashboard reports entries that will not clear, or when a content transfer fails on a schema mismatch. Covers Deploy on Umbraco Cloud and on self-hosted licensed installs, with the Cloud-only behaviors marked as such.
---

# Umbraco Deploy: artifacts, drift, and remediation

Deploy stores CMS schema — document types, data types, templates, languages, AI entities — as `.uda`
artifacts on disk, and reconciles them against each environment's database. Most of what goes wrong
happens quietly: an artifact that was rewritten rather than authored, a dashboard control that reports
success without importing, a restart that changes nothing.

**These are claims to verify, not gospel.** They were true when recorded, against the versions noted.
The first time you encounter one in a project, confirm it holds there — then mark it project-confirmed
in your own memory.

## Where the facts live

Two references, split by task. Read the one matching what you are doing rather than both.

| Reference | Read it when |
|---|---|
| `references/artifact-mechanics.md` | Reading, writing, or diffing `.uda` files; deciding whether an unstaged change was intended; understanding why an environment reports drift that never clears |
| `references/deploy-remediation.md` | The dashboard reports entries that will not clear, or a content transfer is failing on a schema mismatch and you need the path that actually fixes it |

## Cloud and self-hosted

Deploy runs on Umbraco Cloud and as a licensed add-on on a self-hosted install. The artifact mechanics
hold wherever Deploy runs. Facts whose `Applies:` line ends `on Umbraco Cloud` describe the Cloud
dashboard, its bootstrapper, and its build pipeline; a self-hosted licensee should read those as
Cloud-shaped illustrations of the same reconciliation model rather than as claims about their own
deployment.

## How each fact is recorded

Each fact states a claim as a heading, then gives its reasoning, what to do differently, and the
version range it was verified against. **`Applies:` is a range, and it matters** — treat a fact whose
range does not cover the project's version as *suspect, not authoritative*, and verify before acting
on it.
