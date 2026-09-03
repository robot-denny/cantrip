---
name: prose-discipline
description: How toolkit prose should read for an audience that includes non-developers: plain language, sentence rhythm, the em-dash budget, the rule governing when magic vocabulary earns its place, and the constructions that make writing sound machine-generated. Consult when writing or editing a README, a concepts or installation doc, a feature doc, a spec summary, a skill description, release notes, or any prose a person outside the implementing team will read; and when reviewing changed markdown.
---

# Prose discipline

Documentation has one job before any other. It has to let a person who did not build the thing
decide whether to try it. That person is usually not the developer who will maintain it.

This file is the standard for prose the toolkit writes and for prose written about it. The rules
are checkable on purpose. "Make it warmer" is not a rule anyone can apply twice and get the same
answer.

## Who you are writing for

Write for a designer, product manager, or QA lead. Capable, curious, short on time. They will
install the toolkit and cast a spell. They will not read the source to work out what a sentence
meant.

That reader changes three things:

- **They cannot decode compression.** A sentence carrying three claims in one clause is fine for
  someone who already holds the model in their head. For someone building that model as they read,
  it is a wall.
- **They do not share your vocabulary.** Slot, diff, retrofit, Given/When/Then. All learnable, none
  free. A coined term costs the reader something the first time, so it has to buy something back.
- **They quit quietly.** Nobody files an issue saying the README was tiring.

Aim each document at the moment just before someone decides. Explain enough to make that decision,
and put the rest one link away.

**Slot:** `.agents/config/conventions.md` → `## Documentation voice`
**If empty:** apply this file as written.
**Detect:** a prose linter's configuration first, since one file settles the question and makes the
rest of the scan unnecessary. Failing that, the register of the prose the project already ships in
its README and top-level docs: average sentence length, whether it addresses the reader as "you",
and whether it glosses its own terms on first use.

## When the project has its own voice

A project with a brand voice, a content style guide, or a prose linter has already answered most of
this file. Voice belongs to the project. This file supplies a default, not an override.

The rules here fall into two kinds, and they behave differently when the slot is full.

| Kind | Sections | What happens on conflict |
|---|---|---|
| **Legibility** | Say it plainly, Shape a document task-first | Applies regardless. A guideline that forbids defining a term on first use is a guideline with a bug |
| **Voice** | Vary the rhythm, The em-dash budget, the hedge list, magic vocabulary | The project wins, in full, with no negotiation |

Three rules follow.

**The project's declared voice is authoritative on every conflict.** Where a project states a
preference this file contradicts, follow the project and do not mention the disagreement in the
output. Never rewrite a project's own voice documentation to match this file.

**A configured prose linter is the authority, not a peer.** If a project runs one, it holds the voice
rules. Do not duplicate its checks, contradict its verdicts, or apply the numeric targets below to
files it governs.

**Scope belongs to the project too.** A brand voice usually governs product and marketing copy and
may say nothing about a README, a runbook, or a feature doc. Do not stretch marketing guidelines
over internal documentation. Where the slot does not say which documents it covers, apply it to
reader-facing docs and apply this file's legibility rules to the rest.

## Say it plainly

**Explain a term the first time you use it, in the same sentence.** Not in a glossary, not in a
later section. "A slot is a section of your own config that a spell reads, so `/plan` can find your
test command without being told twice."

**Prefer the verb.** "Classifies the work" beats "performs a classification of the work".
Nominalizations are how a sentence gets heavy without getting more precise.

**One idea per sentence.** When a sentence has a main clause and two qualifying clauses, it usually
wants to be two sentences. Split it.

**Address the reader as "you" for anything they do.** Describe the system in the third person. Mixing
the two inside one sentence is what produces the passive fog that makes docs feel authorless.

**Give the example before the rule.** A reader who has seen one concrete case can absorb the general
statement in half the words. A reader who meets the abstraction first has to hold it, unexplained,
until an example arrives.

**Cut the hedges and the flatterers.** Simply, just, of course, obviously, powerful, seamless,
robust. None of them survive a read-aloud.

## Vary the rhythm

Uniform density reads as machine-written even when every individual sentence is good. This is the
tell most people notice and cannot name.

Targets, measured across the prose in a file and not its tables or code blocks:

| Measure | Target |
|---|---|
| Mean sentence length | 14 to 18 words |
| Sentences under 8 words | at least one in every four |
| Sentences over 30 words | none |
| Consecutive sentences within 3 words of each other | at most two |
| Sentences per paragraph | four, at the outside |

After any sentence longer than 25 words, write a short one. The short sentence is where the reader
catches up, and a document with none of them is exhausting to read even when it is correct.

## The em-dash budget

**One em-dash per 300 words of prose, and none of them doing the job of a comma.**

The construction to watch is the appositive dash, where a definition gets folded into the middle of
a sentence between two dashes. It is grammatical and it is compact. It is also the loudest signal
that a machine wrote the text, because a model reaches for it whenever a sentence wants a second
idea. Used once, it is elegant. Used every third sentence, it becomes the only rhythm the document
has.

Four replacements, in order of preference:

1. **A full stop.** The second idea becomes its own sentence. Usually the best answer, and it fixes
   the rhythm problem at the same time.
2. **A colon**, when the second half explains or lists what the first half named.
3. **A comma pair**, when the aside is genuinely parenthetical and short.
4. **Deletion.** A surprising number of dashed asides are restating the clause before them.

Before and after:

> Cantrip separates two kinds of document — the evergreen record of what the system does, which
> stays true, and the temporal record of what you are changing, which does not — so that neither
> one rots.

> Cantrip keeps two kinds of document. One records what the system does today and stays true until
> the behavior changes. The other records the change you are making now, and it stops being true
> the day you ship. Keeping them apart is what stops either one rotting.

Longer by four words. Considerably easier to read.

## When magic vocabulary earns its place

Spell, cast, spellbook, and reference exist to make a distinction easy to hold, not to give the
project a theme. Use them where they carry the concept and nowhere else.

The one distinction they genuinely earn: **you cast a spell, and the model reaches for a
reference.** That is a real difference in how the two behave, and the metaphor makes it stick in a
way that "user-invoked skill" and "model-invoked skill" do not.

**The strip test.** Take the metaphor out of the sentence and read what is left.

- If the sentence still says the same thing, the metaphor was decoration. Cut it.
- If the sentence loses meaning, the metaphor was carrying the explanation. Replace it with the
  literal statement, then decide whether the metaphor still adds anything on top.

A sentence should never require the reader to know how spells work in a game. Cast, spell, spellbook,
and reference are the whole vocabulary. Do not add to it. Incantation, conjure, arcane, ritual,
tome, grimoire, mana, and scroll are off the table however well they fit. Each one is a new term
the reader has to translate before reaching the idea underneath.

One flourish per document is a fair budget. Two is a theme, and a theme is what a reader has to
read around.

## Constructions to avoid

| Avoid | Why | Instead |
|---|---|---|
| The appositive em-dash as a default move | The loudest machine tell in technical prose | A full stop, a colon, or nothing |
| "Not X, it's Y" | A false contrast that manufactures drama from a definition | State Y. Mention X only if someone actually believes it |
| Telegraphic fragments used as sentences | Reads as notes rather than writing | Finish the sentence |
| Bold lead-in declaratives, more than twice per section | A good pattern that becomes a drumbeat | Ordinary sentences between them |
| Noun stacks as the subject | "Review output quality degradation" makes the reader parse before they can read | Break it into a clause with a verb |
| Stacked qualifying clauses | Every clause after the second one is load the reader carries | Two sentences |
| Rhetorical questions as section openers | Delays the answer the reader came for | Open with the answer |
| "It's worth noting that", "at the end of the day" | Words that carry nothing | Delete the phrase and keep the sentence |

## Shape a document task-first

Open with what the reader can do, not with what the thing is. A definition is only meaningful to
someone who already knows why they would want one.

The order that works for the reader described at the top of this file:

1. What this lets you do, in one or two sentences.
2. The smallest real example, complete enough to run or follow.
3. The concepts, once the example has given them something to attach to.
4. The edge cases and the reference material, below or behind a link.

Two more habits worth keeping. Say what a thing is for before you say how it is built. And when a
section runs past a screen, ask whether the second half is reference material that belongs somewhere
a reader can skip.

## Check before you hand it back

Run this on any prose you wrote or edited, before returning it:

- [ ] Count the em-dashes. Under one per 300 words, and none of them replacing a comma.
- [ ] Read the longest sentence aloud. If you run out of breath, split it.
- [ ] Find the shortest sentence in each section. If there isn't one under eight words, add one.
- [ ] First use of every coined term is glossed in the same sentence.
- [ ] Apply the strip test to every magic word. Cut the decorative ones.
- [ ] The opening sentence says what the reader can do, not what the thing is.
- [ ] No sentence you would not say out loud to a colleague.

The last check catches most of what the others miss.
