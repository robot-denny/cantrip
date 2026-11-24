# Feature: Test Content

A team building a CMS site can get every meaningful way a block or page type can be filled in onto
QA test pages, without building the examples by hand. A developer writes one component's recipe with
the `/test-content` spell, right after building or changing it, and the project's own builder turns
committed recipes into test pages on each environment that allows it. QA owns the site's rules for
what a test page shows; the toolkit owns the general method.

**Source**: no spec; landed out of flow and reconciled by `/retrofit`. Rationale in
[ADR 0020](../adr/0020-test-content-recipes-and-builders.md)
**Last verified**: 2026-11-23

---

## Increments

- [ ] **In review**: test-content recipes. The core method reference and its rules template, and a
      `/test-content` spell and builder blueprint in `umbraco-17` and in the new `optimizely-12` pack.
      No spec; landed out of flow, reconciled by `/retrofit`, and dry-run by hand on the demo
      project's alert banner, with the 4 corrections it found applied
      (`_work/test-content/validation.md`), then reviewed by all three reviewers with the agreed
      fixes applied
- [ ] The client project's builder adopts this format's names: `$storedBlock` becomes `$shared`,
      `$sharedBlock` becomes `$real`, item type `item` becomes `inline` and `storedBlock` becomes
      `shared`, the recipe's `storedBlocks` becomes `sharedBlocks`, and the `themeSwitcher` section
      becomes an `opening` section. Work in that project, not here (no spec yet)
- [ ] An `optimizely-13` pack, copied from `optimizely-12` and checked claim by claim against a real
      CMS 13 project (no spec yet; waits for a CMS 13 project)
- [ ] The Optimizely CMS 12 blueprint checked against the first builder a project builds from it
      (no spec yet). Two review findings wait for that builder, since neither could be verified
      without one: how a rebuild avoids a new version on every publish, and how test content is
      kept out of the public search index without hiding it from the edit UI's own search. The
      second applies to the Umbraco 17 blueprint too, whose legacy search reads the internal index
- [ ] A recipe JSON schema shipped with the core reference, so a validator and an editor can both
      read one definition of the format (parking lot)

---

## Behaviors

### Rule: A recipe records what to test; the project's builder builds it

```scenario
Scenario: The spell writes a recipe and nothing else
  Given an Umbraco 17 project with a test-content builder and a recipes folder
  When a developer casts /test-content cardItem
  Then one file, the cardItem recipe, is written to the recipes folder
  And nothing is created or changed in the CMS
```

```scenario
Scenario: A project with no builder is told where to start
  Given a project with no test-content builder
  When a developer casts /test-content cardItem
  Then the spell stops before writing a recipe
  And it names the pack's builder blueprint as the place to start
```

```scenario
Scenario: A project with a builder but no rules is offered the starter rules
  Given a project with a builder and no test-content rules file
  When a developer casts /test-content cardItem
  Then the spell offers to copy the starter rules
  And it writes no recipe until QA has confirmed them
```

### Rule: Variations follow the general rules and the site's own rules, and each is cited

```scenario
Scenario: Layout settings vary one at a time from a realistic baseline
  Given a card block with 4 backgrounds and an image position of Above or Beside
  When its recipe is written
  Then it has a baseline on the default background with the image above
  And one variation for each other background, and one with the image beside the text
  And each variation is labeled with the one thing it changes
```

```scenario
Scenario: Content stress is combined rather than given a variation each
  Given a card block with an optional teaser and a link
  When its recipe is written
  Then a long title, a long teaser and an external link opening in a new window share one variation
```

```scenario
Scenario: Every rule applied is listed with where it came from
  Given the site's rules file has a rule P3 for widths
  When a recipe is written
  Then the recipe lists G2 with source "skill" and P3 with source "project"
  And the spell's report shows which variations each rule produced
```

### Rule: Gray areas are asked about, one at a time, and the answers are kept

```scenario
Scenario: An unclear field is asked about rather than guessed
  Given a card block whose optional subtitle may or may not change the layout
  When the developer casts /test-content cardItem
  Then the spell asks one question about the subtitle, with the answer it proposes and why
  And it waits for the answer before asking anything else
  And the answer is recorded in the recipe's decisions
```

```scenario
Scenario: A rerun does not ask again
  Given a card recipe whose decisions record the subtitle answer
  And the card's schema has not changed
  When the developer casts /test-content cardItem again
  Then the subtitle question is not asked
```

### Rule: A test page's headings never skip a level

```scenario
Scenario: Section and row headings sit under the page title
  Given a recipe with a "Variations" section holding a row labeled "Backgrounds"
  When the test page is built
  Then the page title is the level-1 heading, "Variations" a level-2 heading, and "Backgrounds" a level-3 heading
  And the rich-text sample's own heading sits below "Backgrounds"
```

### Rule: Test content never points at real content

```scenario
Scenario: A recipe holds names, never ids
  Given a recipe that links to the test-content root and uses a test image
  When the recipe is read
  Then the link is a "$link" token and the image a "$media" token
  And no page id, key or CMS-internal reference appears anywhere in it
```

### Rule: A recipe keeps up with its component

```scenario
Scenario: Refreshing keeps what still applies
  Given a card recipe built with an item "baseline"
  And a new optional field has been added to the card
  When the developer casts /test-content cardItem
  Then the "baseline" item keeps its id
  And the new field is added to what the recipe expects
  And the spell shows the added, changed and removed variations before writing
```

### Rule: On Optimizely CMS 12, the schema is read from the content type's class

```scenario
Scenario: Inherited properties and enum dropdowns are read from code
  Given a CardBlock class that inherits a background enum from its base class
  When the developer casts /test-content CardBlock
  Then the recipe expects the inherited background property
  And it lists every background option by the name an editor sees
```

---

## Edge Cases

### Rule: What cannot be built is left out and said so

```scenario
Scenario: A home page gets no recipe
  Given a page type that exists only once, at the content root
  When the developer casts /test-content on it
  Then the spell says it can't have a recipe and stops
```

```scenario
Scenario: A dropdown whose options come from a service
  Given an Optimizely block whose dropdown options are fetched from a service at edit time
  When its recipe is written
  Then the spell asks how to treat the dropdown and records the answer
  And the dropdown's options are not listed in what the recipe expects
```

---

## Test Coverage

| Scenario | Test File | Status |
|----------|-----------|--------|
| The spell writes a recipe and nothing else | — | Not covered |
| A project with no builder is told where to start | — | Not covered |
| A project with a builder but no rules is offered the starter rules | — | Not covered |
| Layout settings vary one at a time from a realistic baseline | — | Not covered |
| Content stress is combined rather than given a variation each | — | Not covered |
| Every rule applied is listed with where it came from | — | Not covered |
| An unclear field is asked about rather than guessed | — | Not covered |
| A rerun does not ask again | — | Not covered |
| A recipe holds names, never ids | — | Not covered |
| Refreshing keeps what still applies | — | Not covered |
| Inherited properties and enum dropdowns are read from code | — | Not covered |
| Section and row headings sit under the page title | — | Not covered |
| A home page gets no recipe | — | Not covered |
| A dropdown whose options come from a service | — | Not covered |
