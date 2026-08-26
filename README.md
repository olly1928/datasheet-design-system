# Box data sheet design system

Generate on-brand, two-page Box data sheets for a named customer or prospect — with
their logo in the header, their language in the copy, and an AI-disclosure line in
the footer.

The design lives here. The agent only writes content. That split is the whole idea:
**layout cannot drift, because the model never touches it.**

```
you  →  "make a Box data sheet for Meridian Financial"
        ChatGPT reads AGENT.md + VOICE.md + BLOCKS.md      (~4k tokens in)
        writes content/meridian-financial.json             (~700 tokens out)
        runs scripts/build.py                              (validates, then renders)
        →  out/meridian-financial-box-datasheet.html       (print to PDF)
```

## Try it

```bash
python3 scripts/build.py content/_example-frasers-brief.json
open out/frasers-group-box-datasheet.html
```

Print with **Letter, margins None, "Background graphics" ON**.

---

## What's here

| Path | |
|---|---|
| **`AGENT.md`** | The operating contract. The only long file the agent reads every run. |
| `content/_example-frasers-brief.json` | A worked **solution brief** — one named use case |
| `content/_example-meridian.json` | A worked **data sheet** — the product, angled at one customer |
| `template/datasheet.html` | The whole template — layout, palette, blocks, renderer. One self-contained file. |
| `template/content.schema.json` | Field names, types, character limits |
| `content/` | One JSON per customer |
| `brand/VOICE.md` | Box voice: rules and rewrite examples |
| `brand/BLOCKS.md` | The block library |
| `brand/LOGO-RULES.md` | Logo treatment ladder and clearance rules |
| `brand/SOURCING.md` | **Where to find logos and graphics on box.com**, and how to fetch them |
| `brand/SNIPPETS.md` | Pre-approved boilerplate |
| `assets/logos/manifest.json` | The record of which logos are in use and where each came from |
| `assets/cache/` | Assets fetched from box.com, plus `provenance.json` |
| `legal/disclaimer.md` | The AI-disclosure wording. Legal owns this file. |
| `scripts/build.py` | Resolve assets, validate, then render |
| `scripts/fetch_asset.py` | Cache an image from box.com, with provenance |
| `scripts/validate.py` | Character budgets and page-fit arithmetic |
| `reference/` | Source PDF, page renders, measured design spec. **Never read at generation time.** |

## Two sheet types

Both share identical styling; the type sets the band eyebrow and the content shape.

- **`solution-brief`** (default) — one named use case for one customer. The stronger
  of the two: a sheet about a real workflow beats a general product sheet with the
  customer's name dropped in.
- **`datasheet`** — the product as a whole, angled at one customer.

The band carries a modest title naming the document; the big headline lives in the
body, in the `hero` block, and carries the argument. That split is what makes the
page read.

## Design values

All measured from the source artwork, not estimated — see
`reference/DESIGN-SPEC.md`.

- **US Letter**, 816 × 1056 px @ 96dpi (A4 available via `"size": "a4"`)
- **Inter** — Regular, SemiBold, Light, and Inter Display for the hero
- Box blue `#0061D5` · band gradient `#002959 → #003C83` · ink `#151F26`
  · body `#636D78` · panel `#F5F6F8` · card `#E5EFFA` · label `#9AA1AA`
- Grid: 48px margin · main column 478 · gutter 27 · sidebar 263, bleeding right

---

## Wiring up ChatGPT

**Point it at the repo.** Connect the GitHub connector and give it the repo, or paste
the raw URL of `AGENT.md` and let it follow the links. Either way the instruction is
just:

> Read AGENT.md in this repo and follow it. Make a Box data sheet for [customer].

`AGENT.md` sends it to the two other files it needs and explicitly fences off
`reference/`. Keeping that fence is what keeps the token cost flat as the repo grows.

**Connect the Box folder.** With Box MCP on your corporate instance, the agent can
read the approved-logos folder and the customer references directly. Two things to
know:

- **Code Interpreter has no internet access**, so it cannot fetch a logo by URL at
  generation time. Assets have to arrive as *content*, not as a link.
- **SVG relays cheaply, raster does not.** An SVG logo is a few KB of text the model
  can read, recolour to white, and inline. A PNG has to travel as base64 — roughly 7k
  tokens for a small one, and it can't be recoloured cleanly.

So: **Box is the approval source of truth, this repo is the build cache.** Sync
approved logos in as SVG, prepare the white variant once, record the clearance in
`manifest.json`. Every future sheet for that customer is then instant, identical, and
already cleared. Anything not yet cached still works — drop the file into the chat,
or let the agent pull it over MCP — just more slowly.

That is also what makes the white-on-blue treatment reliable: you verify it once when
you cache it, instead of hoping the model gets it right live.

## Getting a PDF

The build always produces HTML. For the PDF:

- **Print from the browser** — Letter, margins None, Background graphics ON. Works
  everywhere, and it's the path to assume.
- **`--pdf`** if Playwright happens to be installed locally. Don't install anything
  just for this.

The HTML is self-contained apart from the Google Fonts link, so it travels fine.

## Assets from box.com

Box publishes most of what a sheet needs — the industry page for a sector carries a
customer logo strip and sector-specific product graphics. The Frasers example was
built almost entirely from the Box retail page.

```bash
python3 scripts/fetch_asset.py "https://images.ctfassets.net/.../retail-hero.png"
```

Downloads to `assets/cache/`, and records the URL, size, checksum and date in
`assets/cache/provenance.json` — so for any asset on any sheet you can say where it
came from. Fetching is restricted to the hosts in `assets/cache/allowlist.txt`, and
re-checked on every redirect.

You can also put a box.com URL straight into a content file. The build tries to cache
it; if it has no network it leaves the URL in place and the browser loads it when the
sheet is opened. Declare `"aspect"` on the figure when you do, since the validator
cannot measure an image it has not downloaded.

**`brand/SOURCING.md`** covers where to look, what not to take, and the sector sweep
that makes the second sheet for a sector free.

## Adding a customer logo

1. Get the file into `assets/logos/` (or fetch it from box.com into `assets/cache/`) —
   SVG if at all possible.
2. If a white version exists, use it. If not, and the mark is mono-safe, make one by
   rewriting the fills to `#FFFFFF`.
3. Add a `manifest.json` entry with `aspect`, `reverse_permitted`, and where you got
   it — `source_url` and `source_page`.

`brand/LOGO-RULES.md` has the full ladder and the cases where reversing to white is
not allowed.

## Changing the legal wording

Edit `legal/disclaimer.md`. That's the only place. Every sheet generated afterwards
picks it up. It currently carries a visible `[LEGAL TO SUPPLY FINAL WORDING]` marker
so an unapproved sheet can't quietly go out.

---

## Why the build refuses

`scripts/validate.py` runs before anything renders and fails on two things:

- **A column over 100% fill** — the sheet would overflow the page.
- **A character limit exceeded** — measured against *rendered* text, so markdown
  syntax and link URLs are not counted against you.

It also *warns* below 72% fill, because a half-empty column is what made the original
page 2 read clunky — unless the column ends in a `"pin": "bottom"` block, where the
gap is deliberate. The template then measures the real layout in the browser and
paints a red rule if anything still overflows.

Two layers, because arithmetic before render is cheap and catches most of it, and
only the browser knows the truth. Estimates land within about ±4% of a real render,
which is why the recipes aim for 88–95% rather than 99%.
