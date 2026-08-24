# Block reference

Blocks are the units a page is assembled from. Pick and order them per customer; the
template owns how each one looks.

`main` is the wide left column. `aside` is the grey right panel. Most blocks work in
either, but the ones marked **aside** are sized for the narrow column and will look
wrong in `main`, and vice versa.

Every block takes an optional `"heading"`.

---

## `text` — body copy
```jsonc
{ "type": "text", "paragraphs": ["…", "…"] }
```
The opening paragraphs. `**bold**` is supported inside any copy field.

## `section` — heading plus copy
```jsonc
{ "type": "section", "heading": "Move at the speed of AI with Box", "paragraphs": ["…"] }
```

## `caps` — the capability grid *(main)*
```jsonc
{ "type": "caps", "heading": "Transform your business with intelligence",
  "columns": 3,
  "items": [ { "icon": "shield", "title": "Secure collaboration",
               "body": "…", "list": ["…", "…"] } ] }
```
The signature block of page 1. Three across by default, `"columns": 2` for wider items.

**Row height is set by the tallest item in the row.** Trimming a short item changes
nothing. Keep items in a row roughly equal or the grid gets airy.

Fill the grid: 3 or 6 items with `columns: 3`. Five leaves a visible hole.

## `cards` — feature cards *(main)*
```jsonc
{ "type": "cards", "items": [ { "icon": "ai", "title": "…", "paragraphs": ["…","…"] } ] }
```
Pale blue rounded cards, two across. Four is the natural number. A single item
renders full width.

Cards in a row stretch to match — so uneven copy shows as dead space at the bottom of
the shorter card. Keep paragraph counts equal across a row.

## `quote` — customer proof
```jsonc
{ "type": "quote", "text": "…", "name": "Jane Okafor, VP Operations", "role": " — Acme Corp" }
```
Only from an approved reference. Never attribute an invented quote to a real person.

## `stats` — outcome numbers
```jsonc
{ "type": "stats", "heading": "…",
  "items": [ { "value": "90%", "label": "of enterprise data is unstructured" } ] }
```
Two or three. Every figure needs an approved source or a `[SOURCE REQUIRED]` marker.

## `logogrid` — peer logos *(aside)*
```jsonc
{ "type": "logogrid", "heading": "Trusted by global leaders",
  "logos": [ { "svg": "<svg…>" }, { "src": "acme.svg", "alt": "Acme" } ] }
```
Two across, greyscale, common height. Six is right. Manifest rules apply —
`brand/LOGO-RULES.md`.

## `logobar` — peer logos in a row *(main)*
Same inputs, laid out horizontally. Use when the proof belongs in the main column.

## `bullets` — a short list
```jsonc
{ "type": "bullets", "heading": "Box at a glance", "items": ["…", "…"] }
```
Works in either column. The "Why [customer], specifically" block is a `bullets` in
the `aside` — the highest-value personalisation on the sheet.

## `linklist` — titled entries *(aside)*
```jsonc
{ "type": "linklist", "heading": "Customer success and services",
  "items": [ { "title": "Consulting", "body": "…" } ] }
```

## `cta` — the closing call *(main)*
```jsonc
{ "type": "cta", "heading": "…", "body": "…", "action": "box.com/contact · [CONTACT]" }
```
Dark navy panel. **Put it last on page 2** — it anchors the bottom of the sheet, which
is what stops the page reading unfinished.

## `footnote` — sources
```jsonc
{ "type": "footnote", "items": ["¹ Source: Congruity 360"] }
```
Sits at the foot of the column above a hairline rule.

---

## Icons

`shield` `doc` `flow` `portal` `pen` `ai` `lock` `chat` `layers` `cloud` `check` `globe`

Stroke-drawn, one consistent style. There are no others — pick the nearest rather
than inventing a name, which renders nothing.

---

## Composing a page that fits

The validator wants **85–98% fill** per column and will refuse to build outside that.

A page-1 `main` that works: `text` → `caps` (6 items) → `quote` → `footnote`.
A page-2 `main` that works: `section` → `cards` (4) → `stats` → `cta`.
An `aside` that works: three or four blocks. Two leaves the panel visibly empty.

If a column is sparse, add a block. Padding the copy to fill space is the thing that
made the original page 2 read clunky.
