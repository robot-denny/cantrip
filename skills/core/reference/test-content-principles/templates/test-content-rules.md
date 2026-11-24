# Test content: project rules

This site's rules for what goes on a component's test page. **QA owns this file**; developers can
edit it too. The `/test-content` spell reads it every time it writes a recipe, applies every rule
below, and cites each one by its number (`project P3`) in the recipe and in its report. The general
method (a realistic baseline, every dropdown option one at a time, optional fields filled and empty)
lives in the toolkit, not here.

<!--
Starter file. Every rule below is a common default, not a fact about this site. Confirm or change
each one against the real page grid and the builder before relying on it, delete what does not apply,
and keep the numbers stable once recipes cite them: renumbering a rule makes old citations wrong.
-->

The builder does not read this file. Where a rule names a value the builder also holds (the
rich-text sample, the test images, the page grid), change both together.

## Page layout

**P1. Opening rows.** <What, if anything, opens every test page before the first section, such as a
theme or brand switcher, and which components get it. These go in the recipe's `opening` section,
which has no heading. Write "None" if nothing does.>

**P2. Where rows render.** <The page's body areas and the order they render in, when that differs
from the order a recipe lists them. Leave this out if rows render in recipe order.>

<!-- P3 to P5 assume a page body with a column grid and row backgrounds. If this site's body is a
single-column list of components with no widths, delete P3 and P4, keep P5 only if rows have a
background setting, and say so in P2. -->

**P3. Widths.** The layout section shows the baseline at every width the grid allows:

| Width | Span |
|---|---|
| 25% | 3 |
| 33% | 4 |
| 50% | 6 |
| 75% | 9 |
| 100% | 12 |

Each width has its own row, labeled with the width ("25%"), and **filled**: 4 components at 25%, 3 at
33%, 2 at 50%, and at 75% a 25% component beside it. The first is the baseline; the rest mix the
component's other background options. In the Variations section, each variation appears once at
**50% (span 6)**, 2 to a row.

**P4. Row types and backgrounds.** <The row types a recipe may use (`rowType`), the settings each
offers (`settings`, with option text exactly as the schema spells it), and which background and
width combinations the layout section shows the baseline on. A table of row label, setting values
works well.>

**P5. Colored components on colored rows.** When a component has a background or color option, each
of its options except an opaque white one also appears on each tinted row background, together on
one filled row each. That includes a transparent, "none" or inherited option, whose text contrast
depends entirely on the row behind it, and a tint on the same tint, which is where a component
disappears into its row.

## Values

**P6. The rich-text sample.** Every rich text field gets this sample in at least one variation,
through the `{"$richText": "sample"}` token. When the component has a background or color option,
the sample appears once on **every** option, 2 to a row, so QA can check text contrast and the
focus outline on links and the button against each background. Where rows have tinted backgrounds
(P5), the sample also appears once on the darkest of them. Its links point only at the test-content
root page or at `example.com`. The builder holds a copy; change both together. Its heading is
level 4, one below a titled section's level-3 row headings; change it if this site's rows render
their headings at another level. Images and blocks inside rich text can't be set by a recipe, so rich-text
images go untested here; QA checks them on real pages instead.

```html
<h4>Sample rich text</h4>
<p>This paragraph has <strong>bold</strong> and <em>italic</em> text, <a href="/test-content/">a linked phrase that goes to the test-content page</a>, and <a href="https://example.com/" target="_blank" rel="noopener">an external link that opens in a new window</a>.</p>
<ul>
<li>First bulleted item</li>
<li>Second bulleted item, long enough to wrap onto a second line when the component is narrow</li>
<li>Third bulleted item</li>
</ul>
<ol>
<li>First numbered item</li>
<li>Second numbered item</li>
<li>Third numbered item</li>
</ol>
<p><a class="button" href="/test-content/">A button-styled link</a></p>
<table>
<caption>A small sample table</caption>
<thead>
<tr><th scope="col">Name</th><th scope="col">Quantity</th><th scope="col">Notes</th></tr>
</thead>
<tbody>
<tr><td>First row</td><td>1</td><td>Short note</td></tr>
<tr><td>Second row</td><td>10</td><td>A longer note that may wrap</td></tr>
</tbody>
</table>
```

<Replace the button's class with the one this site's rich text editor applies.>

**P7. Images.** Every image field gets a **normal** image and a **tiny** one, in separate variations.
The normal image is the test image closest to the field's recommended size (from its help text). The
tiny one is always the smallest test image. Every test image has its own descriptive alternative
text, never the file name, and one is marked decorative, so QA can check the component handles both.
<List the test images the builder ships, by name, with each one's alternative text.>

**P8. Item counts.** A list of items (tiles, panels, cards) is shown with **1, 2, 3, 4, 5 and 15
items, and the maximum** the field allows. Leave out any count above the maximum. When the field has
no maximum, ask whether 15 is enough.

**P9. Content stress is combined.** The stress cases go into as few variations as possible, usually
one:

- a long title (about 120 characters) and long plain text (about 600 characters), with one long
  unbroken string in the text, such as a full URL, which is what overflows a narrow column;
- missing optional text: the optional text fields no one-at-a-time variation already leaves empty, in
  a second stress variation when one can't be both long and empty;
- an external link that opens in a new window;
- a link with no link text, where the field allows it: an **external** link with no `title`, so no
  page name can stand in for the missing text. QA checks that the component either leaves the link
  out or gives it a non-empty accessible name (a fallback such as "Learn more"); an empty link is a
  defect;
- an image with its alternative text or caption field left empty, where the component has one: QA
  checks the image is then treated as decorative (`alt=""`) or the gap is visible to the editor.

Where the grid has widths (P3), the first stress variation also appears in the layout section at the
narrowest one, since that is where long text overflows. Its row's `description` asks QA to check the
page at 320 pixels wide, at 400% zoom, and with increased text spacing.

**P10. Required fields left empty are not built.** A page holding an invalid component can't be
published, and the schema tests already prove a required field is required. The recipe leaves these
cases out and its rules list says so.

**P11. Extra tokens.** <Any value tokens this site's builder adds beyond the toolkit's, such as a
member group, and what each one may name. Write "None" if there are none.>

**P12. A second language.** <Where the site is built in more than one language: one variation in
a second language, so QA can check the page's language and text direction are marked. Write "None"
for a single-language site.>

## Hand-picked combinations

Combinations QA knows are risky, added on top of the one-at-a-time variations. Add to this list as
bugs are found, one numbered rule per component.

<**P13.** `<componentAlias>`: <the settings to combine, for example an image beside the text, on the
darkest background, at 75%.>>
