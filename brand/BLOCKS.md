# Block reference

Blocks are the units a page is assembled from. Pick and order them per customer; the
template owns how each one looks.

`main` is the wide left column (462px on A4, 478 on Letter). `aside` is the grey right
panel (187px / 193px).
Blocks marked **aside** are sized for the narrow column and look wrong in `main`, and
the reverse.

Two properties work on any block:

- **`"label": "Retail on Box"`** — a small uppercase grey label above the block.
  The organising device the sidebar leans on. Sentence case in; it renders uppercase.
- **`"pin": "bottom"`** — anchors the block to the foot of its column. Use it for a
  closing note so a short sidebar ends deliberately instead of trailing off. The
  validator treats such a column as *anchored* and will not call the gap sparse.

`**bold**` and `[label](url)` work in any copy field.

---

## Structure

### `hero` — the page headline *(main, page 1, first)*
```jsonc
{ "type": "hero",
  "headline": "Give every franchise partner one source of truth",
  "deck": "One content layer underneath every system your teams use." }
```
31px headline, bold deck beneath. **Every sheet opens with this.** The band carries a
modest document title; this carries the argument.

### `section` — heading plus copy
```jsonc
{ "type": "section", "level": 3, "heading": "Start with one brand.", "paragraphs": ["…"] }
```
`level: 2` (default) is a major heading at 27px; `level: 3` is 17px.

### `text` — body copy
```jsonc
{ "type": "text", "paragraphs": ["**The challenge:** …", "**The solution:** …"] }
```
The challenge/solution pair is the opening move of a solution brief.

### `rule` — a hairline separator
```jsonc
{ "type": "rule" }
```
Between sections. The sheets lean on these heavily; they are most of what makes the
page feel ordered.

---

## Content

### `steps` — numbered shifts *(main)*
```jsonc
{ "type": "steps", "heading": "Three shifts that change how the portal runs.",
  "items": [ { "title": "From many copies to one source", "body": "…" } ] }
```
Blue numbered circles, three across. **Three is the number** — a fourth wraps onto a
second row and costs about as much height again.

### `deflist` — bold-lead one-liners *(main)*
```jsonc
{ "type": "deflist", "items": [ { "term": "Franchise partners", "body": "one place for the guidelines that apply to them." } ] }
```
The most efficient block on the sheet: one line per audience, naming who gets what.

### `featurelist` — icon-left list *(main)*
```jsonc
{ "type": "featurelist", "heading": "What you get with Box",
  "items": [ { "icon": "layer", "title": "One content layer", "body": "…" } ] }
```
Two columns, small icon in a left gutter. The page-2 workhorse. Six or eight items.

### `caps` — capability grid *(main)*
```jsonc
{ "type": "caps", "heading": "Transform your business with intelligence", "columns": 3,
  "items": [ { "icon": "shield", "title": "Secure collaboration", "body": "…", "list": ["…"] } ] }
```
Three across with a sub-list per item. The `datasheet` alternative to `featurelist`.
Use 3 or 6 items — five leaves a hole. `columns` accepts 2 or 3; anything else renders
three across.

### `cards` — feature cards *(main)*
```jsonc
{ "type": "cards", "items": [ { "icon": "ai", "title": "…", "paragraphs": ["…","…"] } ] }
```
Pale blue cards, two across, four is natural. Cards in a row stretch to match, so keep
paragraph counts equal across a row or the shorter one shows dead space.

### `panel` — pale callout *(main)*
```jsonc
{ "type": "panel", "heading": "Works with the systems your departments already run.",
  "paragraphs": ["…"], "logos": [ { "src": "slack.svg" } ] }
```
Optional logo row along the bottom.

### `figure` — image with caption *(main)*
```jsonc
{ "type": "figure", "width": 80,
  "image": { "src": "portal.png", "alt": "A partner folder in Box" },
  "caption": "A partner folder in Box: the current guidelines and every prior version." }
```
`src` is a **filename**, resolved from `assets/` and inlined at build. Never paste
base64 into a content file. `width` is a percentage — a full-width image is usually
taller than the page can spare.

### `learnmore` — the closing line *(main)*
```jsonc
{ "type": "learnmore", "text": "Learn more at [box.com/industries/retail](https://box.com/industries/retail)" }
```
How both sheets end. Quieter and better than a heavy call-to-action panel.

### `cta` — dark call-to-action panel *(main)*
Available, but `learnmore` is the house style. Use only when the sheet needs a hard ask.

---

## Proof and sidebar

### `statlist` — large numerals *(aside)*
```jsonc
{ "type": "statlist", "items": [ { "value": "68%", "label": "of the Fortune 500 manage content on Box." } ] }
```
Two of them, at the top of the page-1 sidebar. Every figure needs an approved source.

### `quote` — customer proof *(aside)*
```jsonc
{ "type": "quote", "text": "…", "name": "Jane Okafor", "role": "VP Operations, Acme" }
```
Bold dark text, no border. Approved references only — never attribute an invented
quote to a real person.

### `logostack` — peer logos *(aside)*
```jsonc
{ "type": "logostack", "label": "Retail on Box", "logos": [ { "src": "nike.svg" } ] }
```
Stacked, centred, full colour. Four is right. Relevance beats fame: four names from
the prospect's own sector beat ten from everywhere. Manifest rules apply —
`brand/LOGO-RULES.md`.

### `linklist` — services *(aside)*
```jsonc
{ "type": "linklist", "heading": "Customer success and services",
  "items": [ { "icon": "people", "title": "Consulting", "body": "…" } ] }
```

### `pills` — compliance and residency *(aside)*
```jsonc
{ "type": "pills", "label": "Compliance", "items": [
  { "text": "UK data residency", "tone": "blue" },
  { "text": "ISO 27001",         "tone": "plain" },
  { "text": "SOC 2 Type II",     "tone": "plain" },
  { "text": "PCI DSS",           "tone": "plain" },
  { "text": "GDPR",              "tone": "plain" } ] }
```
One residency pill matched to the recipient's HQ country, then three to five
certifications matched to their sector. Six total, maximum.

**Every label must come from `brand/compliance.json`** — a closed list of ten
residency zones and the confirmed certifications. The validator fails the build on
anything else, so a guessed credential cannot ship. `brand/COMPLIANCE.md` has the
selection rules; read it before filling this block.

Convention: **blue for the residency pill** (the customer-specific one), plain for the
certifications.

### `assurances` — what a certificate cannot say *(aside)*
```jsonc
{ "type": "assurances", "items": [
  { "icon": "lock", "title": "Your keys, not ours", "body": "…" },
  { "icon": "ai",   "title": "AI that doesn't learn from you", "body": "…" } ] }
```
Sits directly under the compliance pills. Two short statements answering the questions
a certification list leaves open: who holds the encryption keys, and what happens to
content when AI touches it.

**Wording comes verbatim from `brand/compliance.json`** — the validator fails the build
if it has been reworded. See `brand/COMPLIANCE.md`.

### `note` — closing note *(aside)*
```jsonc
{ "type": "note", "label": "Related", "pin": "bottom", "text": "…" }
```
Pin it. That is what stops the sidebar ending in mid-air.

### `bullets` — a short list *(both)*
```jsonc
{ "type": "bullets", "heading": "Box at a glance", "items": ["…"] }
```

### `stats` — boxed tiles *(main)* · `logogrid` / `logobar` — alternative logo layouts
Available for variety; the stacked and inline versions above are the house style.

### `footnote` — sources *(main)*
```jsonc
{ "type": "footnote", "items": ["¹ Source: Congruity 360"] }
```

---

## Icons

`layer` `shield` `link` `doc` `meta` `hub` `stack` `chart` `ai` `lock` `chat` `flow`
`portal` `pen` `cloud` `check` `globe` `people` `bulb` `help` `edu`

Duotone, one consistent style. There are no others — pick the nearest rather than
inventing a name, which renders nothing.

---

## Fitting a column

Under **100%** or the build refuses; **aim for 88–95%**. The estimate runs a few
percent generous rather than short, and the slack absorbs font fallback.

If a column is sparse, add a block. Padding copy to fill space is exactly what made
the original sheets read clunky.
