# How to generate a Box data sheet

**You are generating a two-page Box sheet for a specific customer or prospect.**
Read this file, `brand/VOICE.md`, and `brand/BLOCKS.md`. That is all you need for a
normal job — roughly 4k tokens. Add `brand/SOURCING.md` when you need a logo or a
graphic from box.com. Do not read anything else unless this file sends you.

**Never read `reference/`.** It holds source PDFs and page renders for humans. It is
large and contains nothing you need.

---

## What you produce

**One JSON file** at `content/<customer-slug>.json`. Nothing else. You never write
HTML, never edit `template/`, never touch CSS. The layout is not yours to change —
that is what keeps every sheet looking like Box made it.

Then run:

```bash
python3 scripts/build.py content/<customer-slug>.json
```

It validates, resolves any assets, and writes `out/<customer-slug>-box-datasheet.html`.
Give the user that file. For a PDF: open it and print — **Letter, margins None,
"Background graphics" ON**.

If the build **refuses**, it has told you exactly what is wrong. Fix the JSON and run
it again. Do not pass `--force` to get around a real overflow.

---

## Pick a sheet type

Both share identical styling. The type sets the eyebrow in the blue band and decides
which shape the content takes.

| `meta.type` | For | Eyebrow |
|---|---|---|
| `solution-brief` *(default)* | One named use case for one customer — "the franchise partner portal" | SOLUTION BRIEF |
| `datasheet` | The product as a whole, angled at one customer | DATA SHEET |

**Prefer `solution-brief`.** A sheet about one real workflow beats a general product
sheet with the customer's name dropped in, and it is what the strongest examples do.

### Recipes

Follow one. These are the block orders that fit and read well.

**solution-brief** — `content/_example-frasers-brief.json`
```
page 1 main   hero → text (challenge / solution) → rule → steps → rule → deflist
page 1 aside  statlist → rule → quote → rule → logostack
page 2 main   featurelist → rule → panel → section → figure → learnmore
page 2 aside  linklist → rule → pills → note (pinned bottom)
```

**datasheet** — `content/_example-meridian.json`
```
page 1 main   hero → text → rule → caps → rule → deflist
page 1 aside  statlist → rule → quote → rule → logostack
page 2 main   featurelist → cards → panel → section → learnmore
page 2 aside  linklist → rule → pills → note (pinned bottom)
```

Copy the matching example and replace the content. Do not build from nothing.

---

## The shape of the file

```jsonc
{
  "customer": "Acme Corp",
  "meta": {
    "size": "letter",            // or "a4"
    "type": "solution-brief",
    "title": "Box for the claims intake process",   // <= 74 chars, sits in the band
    "footerMeta": "box.com"
  },
  "logo": { ... },               // see "The customer logo"
  "legal": "...",                // see "The legal line"
  "pages": [
    { "band": true, "main": [ ...blocks ], "aside": [ ...blocks ] },
    {                "main": [ ...blocks ], "aside": [ ...blocks ] }
  ]
}
```

### Two titles, not one

This is the thing to get right. The band carries a **modest** title saying what the
document *is*. The big headline lives in the body, in the `hero` block, and says what
it is *worth*:

```jsonc
"meta": { "title": "Box for the franchise partner portal" }        // the band
{ "type": "hero",
  "headline": "Give every franchise partner one source of truth",  // the page
  "deck": "One content layer underneath every system your teams use, so partners see only their own content." }
```

The band title names the document. The hero headline makes the argument. Never put
the argument in the band, and never open the body with a paragraph.

---

## Fitting the page

Every column must land under **100%** fill or the build refuses. **Aim for 88–95%** —
the estimate carries about ±4%, and slack absorbs the difference when a font falls
back. The built page also draws a red rule in the browser if anything still overflows,
so a human opening the file will see it.

- **Overflowing?** Cut copy. In `caps`, `cards`, `featurelist` and `steps`, row height
  is set by the *tallest* item in the row — trimming a short one changes nothing.
- **Sparse?** Add a block rather than padding copy. A column ending in a
  `"pin": "bottom"` block is *anchored*, not sparse, and the validator knows that.

Character limits live in `template/content.schema.json` and are enforced. They stop
overflow *and* keep your output small — one sheet should cost ~700 tokens out.

---

## The customer logo

Top right of the band, under a small "Prepared for" label. Getting this right is the
difference between a sheet that looks commissioned and one that looks assembled.

**Work down this ladder and stop at the first tier you can actually satisfy.**

| Tier | `"tier"` | When | Result |
|---|---|---|---|
| 1 | `white` | You have a genuine white/reversed asset | Sits straight on the blue. Best. |
| 2 | `reverse` | Mono-safe asset, any colour | CSS flattens it to pure white |
| 3 | `plate` | Full-colour asset, colour is meaningful | White rounded plate on the blue |
| 4 | `wordmark` | No approved asset exists | The name, typeset. Never fake a logo. |

```jsonc
"logo": {
  "tier": "white",
  "aspect": "wordmark",        // wordmark | mark | stacked  - controls optical size
  "alt": "Acme Corp",
  "label": "Prepared for",     // "" to hide
  "svg": "<svg ...>"           // inline SVG - preferred
  // or "src": "acme-white.svg"   resolved from assets/logos/ and inlined at build
}
```

**Prefer inline `svg`** — it keeps output self-contained and you can recolour it
yourself: for tier 1, rewrite every `fill`/`stroke` to `#FFFFFF`.

**`aspect` is not decoration.** A wide wordmark and a square mark at one pixel height
look nothing alike.

**Read `brand/LOGO-RULES.md` before choosing any logo.** The short version:
**`assets/logos/manifest.json` is the only authority. No entry, no logo — use tier 4.**
You do not decide shareability.

---

## Images and logos from box.com

**box.com is your asset library.** The industry page for the prospect's sector carries
a customer logo strip and sector-specific product graphics, both already published by
Box. Search it, take what fits, record where it came from.

**Read `brand/SOURCING.md`** for where to look and what not to take. The short version:

```bash
python3 scripts/fetch_asset.py "https://images.ctfassets.net/.../hero.png"
```

caches the file and prints a filename to use as `src`. Or put the URL straight in and
let the build cache it — if it cannot reach the network it leaves the URL in place and
the browser loads it when the sheet is opened.

**When you use a live URL, declare `"aspect"`** (width ÷ height). The validator cannot
measure an image it has not downloaded and will otherwise assume a tall one.

`figure` takes an asset by **filename**: `{"src": "portal.png"}`, resolved from
`assets/` and inlined at build. Never paste base64 into the content file — that is what
makes a sheet cost thousands of tokens instead of hundreds. Use `"width"` (a
percentage) to size a figure down; a full-width image is often taller than the page can
spare.

**Doing a sector for the first time? Sweep it.** Cache the industry page's logos and
graphics in one pass and write the manifest entries. Every later sheet for that sector
then costs nothing.

---

## The legal line

The AI-disclosure line sits in the footer of **page 2**. The approved wording lives in
**`legal/disclaimer.md`** — read that file and copy its text into `"legal"` verbatim.
Do not write your own, paraphrase, or trim it to fit. If it does not fit, that is a
bug to report, not to edit around.

---

## Voice

`brand/VOICE.md` governs every word. Read it — the rewrite examples calibrate fastest.

Two rules that override everything:

- **Never invent a number, customer name, quote, or claim.** Where you need a fact you
  do not have, write a visible placeholder — `[NAME, TITLE]`, `[METRIC — SOURCE
  REQUIRED]` — for a human to fill.
- **Never attribute a quote to a real person** unless it came from an approved
  reference. A fabricated customer quote is a legal problem, not a copy problem.
