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
