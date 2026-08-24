# How to generate a Box data sheet

**You are generating a two-page Box data sheet for a specific customer or prospect.**
Read this file, `brand/VOICE.md`, and `brand/BLOCKS.md`. That is all you need for a
normal job — roughly 4k tokens. Do not read anything else unless this file sends you.

**Never read `reference/`.** It holds the original PDF and page renders for humans.
It is large and contains nothing you need.

---

## What you produce

**One JSON file** at `content/<customer-slug>.json`. Nothing else. You never write
HTML, never edit `template/`, never touch CSS. The layout is not yours to change —
that is what keeps every sheet looking like Box made it.

Then run:

```bash
python3 scripts/build.py content/<customer-slug>.json
```

It validates, then writes `out/<customer-slug>-box-datasheet.html`. Give the user
that file. To turn it into a PDF: open it and print — **Letter, margins None,
"Background graphics" ON**. If Playwright happens to be installed, `--pdf` does it
for you; do not install anything to get there.

If the build **refuses**, it has told you exactly what is wrong. Fix the JSON and
run it again. Do not pass `--force` to get around a real overflow.

---

## The shape of the file

```jsonc
{
  "customer": "Acme Corp",
  "meta": {
    "size": "letter",                  // or "a4"
    "title": "...",                    // <= 90 chars, appears in the blue band
    "standfirst": "...",               // <= 110 chars
    "footerMeta": "box.com"
  },
  "logo": { ... },                     // see "The customer logo" below
  "legal": "...",                      // see "The legal line" below
  "pages": [
    { "band": true, "main": [ ...blocks ], "aside": [ ...blocks ] },
    {                "main": [ ...blocks ], "aside": [ ...blocks ] }
  ]
}
```

- **Page 1 has `"band": true`** — the blue header with the Box logo, the title, and
  the customer's logo. Page 2 has no band.
- **`main`** is the wide left column. **`aside`** is the grey right panel.
- Block types and what goes in each: `brand/BLOCKS.md`.

Start from `content/_example-meridian.json`. It is a complete, working sheet — copy
it and replace the content rather than building from nothing.

---

## Fitting the page — this is the part that goes wrong

The failure mode of a modular layout is a page that overflows or reads half-empty.
The validator catches both, and it will refuse to build. Aim for **85–98% fill** in
every column.

- **Overflowing?** Cut copy. In a `caps` grid, row height is set by the *tallest*
  item in the row — trimming a short one changes nothing. Trim the long one, or
  drop a list item from it.
- **Sparse?** Add a block rather than padding the copy. A sparse `aside` is the most
  common miss: it wants three or four blocks, not two.

Respect the character limits in `template/content.schema.json`. They exist to stop
overflow *and* to keep your output small — one sheet should cost you ~700 tokens out.

---

## The customer logo

The logo sits top-right in the blue band, above a small "Prepared for" label. Getting
this right is the difference between a sheet that looks commissioned and one that
looks assembled.

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
  "label": "Prepared for",     // "" to hide the label
  "svg": "<svg ...>"           // inline SVG - preferred
  // or "src": "acme-white.svg"
}
```

**Prefer inline `svg`.** It keeps the output self-contained, and it means you can
recolour it yourself: for tier 1, rewrite every `fill`/`stroke` to `#FFFFFF`.

**`aspect` is not decoration.** A wide wordmark and a square mark set to the same
pixel height look nothing alike. Pick the one that matches the asset's proportions.

**Read `brand/LOGO-RULES.md` before choosing a logo.** It covers which logos may be
used at all, when reversing to white is not permitted, and what to do when you cannot
confirm a logo is cleared. The short version: **`assets/logos/manifest.json` is the
only authority. No entry, no logo — use tier 4.** You do not decide shareability.

---

## The legal line

Every sheet carries an AI-disclosure line in the footer. The approved wording lives
in **`legal/disclaimer.md`** — read that file and copy the current text into
`"legal"` verbatim. Do not write your own, do not paraphrase, do not summarise it to
fit. If it does not fit, that is a bug to report, not to edit around.

---

## Voice

`brand/VOICE.md` governs every word you write. Read it. The rewrite examples at the
end are the fastest way to calibrate.

Two rules that override everything else:

- **Never invent a number, a customer name, a quote, or a claim.** Proof comes from
  approved sources. Where you need a fact you do not have, write a visible
  placeholder — `[NAME, TITLE]`, `[ACCOUNT TEAM CONTACT]` — for a human to fill.
- **Never attribute a quote to a real person unless it came from an approved
  reference.** A fabricated customer quote is a legal problem, not a copy problem.
