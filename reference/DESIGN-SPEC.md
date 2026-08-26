# Source design spec — measured, not guessed

Every value here was extracted from `source-datasheet-icm-0425.pdf`
(*Welcome to Intelligent Content Management*, 04/25) — colours sampled from the
rendered artwork pixel by pixel, fonts read from the PDF's embedded font table,
geometry measured off a 152%-scale render. Nothing in this file is an estimate.

**This folder is for humans and Claude. The generator must never read it** — it is
large and would cost the agent tokens for no benefit. `AGENT.md` says so explicitly.

## Page

| | |
|---|---|
| Size | **US Letter — 816 × 1056 px @ 96dpi** (8.5 × 11 in). Not A4. |
| Pages | 2 |
| Outer margin | 48px (0.5in) left; content column starts at x=48 |

## Typeface — Inter

Read from the PDF font table:

| Role | Font | Notes |
|---|---|---|
| H1 (page-1 hero) | `InterDisplay-SemiBold` | The display optical size |
| Headings / bold leads | `Inter-SemiBold` | |
| Body | `Inter-Regular` | |
| Light accents | `Inter-Light` | |

Inter's variable font on Google Fonts carries the `opsz` axis, so a single
stylesheet covers both the text and display cuts:

```
https://fonts.googleapis.com/css2?family=Inter:opsz,wght@14..32,300;14..32,400;14..32,600&display=swap
```

## Palette

| Token | Value | Where |
|---|---|---|
| `--box-blue` | `#0061D5` | Capability headings, icons, links |
| `--band-from` | `#002959` | Header gradient, left stop |
| `--band-to` | `#003C83` | Header gradient, right stop |
| `--ink` | `#000000` | Section headings (H2) |
| `--ink-sidebar` | `#151F26` | Sidebar headings |
| `--body` | `#636D78` | Body copy |
| `--panel` | `#F5F6F8` | Right sidebar background |
| `--card` | `#E5EFFA` | Page-2 feature cards |
| `--page` | `#FFFFFF` | Page background |

The header band is a **horizontal gradient**, not a flat fill — a vertical scan
holds constant at `#002A5B` while a horizontal scan runs `#002959 → #003C83`.
So: `linear-gradient(90deg, #002959, #003C83)`.

## Grid

| | CSS px from page left |
|---|---|
| Content margin | 48 |
| Main column | 48 → 526 (478 wide) |
| Gutter | ~27 |
| Sidebar panel | 553 → 816 — **bleeds to the right page edge** |
| Header band height | ~217 (page 1 only; page 2 has no band) |

## Structure as built

**Page 1** — header band (Box wordmark, H1 over two lines, standfirst, and a
product-screenshot collage bleeding off the right edge) → two columns: main
(intro, `Transform your business with intelligence`, a 3-across capability grid
run over two rows) and sidebar (`Box at a glance` bullets, `Trusted by global
leaders` logo grid 2 across × 5 down) → footnote with a hairline rule.

**Page 2** — no band. Main (`Move at the speed of AI with Box`, intro, a 2×2 grid
of pale-blue cards, then one full-width pale card) and sidebar (`Customer success
and services`, `Industry and Peer Recognition`).

**There is no footer on either page** — no page numbers, no legal line. The
AI-disclosure strip is genuinely new furniture.

## The whitespace problems, specifically

Confirmed against the artwork. These are what "page 2 looks clunky" is made of:

1. **Page 1 — a ~200px band of dead white** between the capability grid and the
   footnote. The largest single offender, and it's on page 1, not page 2.
2. **Page 1 — the capability grid's second row has an empty third cell.**
   Five items in a three-across grid leaves a hole.
3. **Page 2 — cards padded to match their tallest sibling.** Content lengths
   differ a lot, so `Advanced data protection` and `Modern workflow` both carry
   visible dead space at the bottom.
4. **Page 2 — the final full-width card is centre-aligned** while every other
   card is left-aligned. Reads as an afterthought.
5. **Page 2 — the sidebar stops well short of the page bottom,** leaving a tall
   empty grey column.

All five are the same root cause: **fixed slots fed variable-length content, with
no rebalancing.** The block + height-budget system in `template/` is the fix — an
underfull page becomes a validation failure rather than something a reviewer has
to notice.

---

# Second source — Frasers Group solution brief

`source-frasers-solution-brief.pdf`, built in-house. The design the system was
retuned to. Confirmed by parsing: **2 pages, MediaBox 612×792pt = US Letter**, the
same size as the ICM sheet. (An upload notice claiming 18 pages was wrong.) The pages
are **full-page rasters at 300dpi**, which is why there is no embedded font table.

## What matched already

| | Frasers | ICM | Verdict |
|---|---|---|---|
| Page | Letter | Letter | same |
| Band height | 219px | 217px | same |
| Accent | `#0061D5` | `#0061D5` | same |
| Sidebar | `#F5F6F8` | `#F5F6F8` | same |

The palette is one system across both sheets. Only the band and the typography
differed — which is why this was a retune, not a rebuild.

## What changed

| Token | Value | Note |
|---|---|---|
| `--ink` | `#151F26` | Heading ink. The ICM sheet used pure `#000000`. |
| `--label` | `#9AA1AA` | Uppercase letterspaced section labels — new |
| Band | `#C4DBF8 → #F5F6F8 → #E1C2EE` | **Not adopted.** Replaced with the ICM deep blue. |

The band gradient scan, left to right at y=60: `#C4DBF8`, `#D3E4F8`, `#E4EDF9`,
`#F5F6F8`, `#F1EEF6`, `#EDE0F5`, `#E7D0F1`, `#E1C2EE`.

On deep blue, three elements had to flip: the eyebrow (`#0061D5` → `#78ADF7`, a light
tint that keeps the accent role), the band title (`#151F26` → white), and the customer
logo (black → white, which is tier 1 of the logo ladder).

## Type ramp, measured

| Role | Frasers | Previous build |
|---|---|---|
| Hero headline | 34px / 1.13 / 600 | *(none — the title sat in the band)* |
| Deck | 17px / 1.32 / 600 | *(none)* |
| Major heading | 27px | 17px |
| Minor heading | 17px | 14.5px |
| Body | 12.4px / 1.52 | 11.4px / 1.62 |
| Section label | 10px, `.1em`, `#9AA1AA` | *(none)* |

Body line-height barely moves (18.9px against 18.5px) despite the larger size —
bigger type, tighter leading.

## The structural lesson

The band carries a **modest** title naming the document ("Box for the franchise
partner portal"). The **big headline lives in the body** ("Give every franchise
partner one source of truth"), immediately under the band. Two title levels, not one.

That is the single change that most improved the design, and it is why the earlier
build read flat: it put one title in the band and opened the body with a paragraph.

## Blocks this source introduced

`hero`, `steps` (numbered blue circles), `deflist` (bold-lead one-liners),
`featurelist` (icon in a left gutter), `panel` (pale callout with a logo row),
`figure`, `learnmore`, `statlist` (large numerals, stacked), `logostack` (vertical,
centred, full colour), `pills`, `note` — plus `label` and `pin: bottom` as
cross-cutting properties, and duotone icons in place of stroke outlines.
