# Box data sheet design system

Generate on-brand, two-page Box data sheets for a named customer or prospect — with
their logo in the header, their language in the copy, and an AI-disclosure line in
the footer.

The design lives here. The agent only writes content. That split is the whole idea:
**layout cannot drift, because the model never touches it.**

**Generation is two steps.** ChatGPT proposes a plan — angle, headline, block outline,
which peer logos and why, what it will leave as a placeholder — and stops. You approve
or amend, then it builds. That confirmation is what puts a human between a logo
selection and a customer's inbox, and it is what makes the whole thing usable without
a review queue.

```
you   →  "make a Box data sheet for Meridian Financial"
ChatGPT  reads AGENT.md + config + VOICE.md + BLOCKS.md      (~6k tokens in)
         lists the Box approved-logos folder over MCP
      →  SHEET PLAN — angle, headline, outline, logos + why, placeholders
you   →  "go"   (or "swap Aviva for Zurich, and lead on retention")
ChatGPT  reads COMPLIANCE + LOGO-RULES + a worked example    (~8k more)
         writes meridian-financial.json                      (~2.4k tokens out)
         runs box-datasheet-builder.py         (validates, then renders)
      →  meridian-financial-box-datasheet.html              (print to PDF)
```

About **14k tokens in and 2.4k out** for a typical sheet — measured across the
files the agent actually opens, not estimated.

## Start here

**`PROMPT.md`** holds the one file to attach, the prompt to paste, and the four things
to fill in before the first run. Read that first; this file is the reference behind it.

**`dist/box-datasheet-builder.py`** is that file: the template, the validator and the
credential list baked into one stdlib-only script. Attach it to your Custom GPT or
Project once. ChatGPT's GitHub connector and its Code Interpreter are separate
sandboxes — the connector reads this repo, but the sandbox that runs Python cannot see
it, so without the attachment the model would have to retype a 32KB template before it
could build anything.

**`config.json`** is the one file you edit to point the system at your own Box content.

## Try it

```bash
python3 scripts/build.py content/_example-frasers-brief.json
open out/frasers-group-box-datasheet.html
```

Print with **margins None, "Background graphics" ON**. Sheets are **A4** unless the
content file says `"size": "letter"`; the page size travels with the sheet, so the
print dialogue needs nothing set.

---

## What's here

| Path | |
|---|---|
| **`PROMPT.md`** | **The prompt to paste into ChatGPT**, and the pre-flight checklist |
| **`dist/box-datasheet-builder.py`** | **The single file you attach to ChatGPT.** Generated — never edit it |
| **`config.json`** | Your Box logos folder — the one file you edit |
| **`AGENT.md`** | The operating contract. The only long file the agent reads every run. |
| `content/_example-frasers-brief.json` | A worked **solution brief** — one named use case |
| `content/_example-meridian.json` | A worked **data sheet** — the product, angled at one customer |
| `template/datasheet.html` | The whole template — layout, palette, blocks, renderer. One self-contained file. |
| `template/content.schema.json` | Field names, types, character limits |
| `content/` | One JSON per customer |
| `brand/VOICE.md` | Box voice: rules and rewrite examples |
| `brand/BLOCKS.md` | The block library |
| `brand/LOGO-RULES.md` | Logo treatment ladder and clearance rules |
| `brand/SOURCING.md` | Where to find **graphics** on box.com, and the three ways to use one |
| `brand/SNIPPETS.md` | Pre-approved boilerplate |
| `brand/COMPLIANCE.md` | How to pick residency and certifications for a recipient |
| `brand/compliance.json` | **The closed list** of zones and certifications — enforced by the validator |
| `assets/logos/` | A **cache** of logo files — the approved list lives in Box, not here |
| `assets/cache/` | Assets fetched from box.com, plus `provenance.json` |
| `legal/disclaimer.md` | The AI-disclosure wording. Legal owns this file. |
| `scripts/build.py` | Resolve assets, validate, then render |
| `scripts/bundle.py` | Rebuild `dist/`. `--check` fails if it is behind the template |
| `scripts/topdf.py` | Print a built sheet to PDF, if a headless browser is around |
| `scripts/fetch_asset.py` | Cache an image from box.com, with provenance |
| `scripts/extract_from_pdf.py` | Cut a graphic out of a Box PDF, keying its background to alpha |
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

- **A4**, 794 × 1123 px @ 96dpi — the default. US Letter (816 × 1056) via
  `"size": "letter"`, which is the size the source artwork was measured from.
  The template writes a matching `@page` rule, so a sheet prints at the size it
  was laid out for
- **Inter** — one variable face carrying the `opsz` axis, so the 31px hero picks
  up the display optical size automatically (`font-optical-sizing:auto`)
- Box blue `#0061D5` · band gradient `#002959 → #003C83` · ink `#151F26`
  · body `#636D78` · panel `#F5F6F8` · card `#E5EFFA` · label `#9AA1AA`
- Grid: 48px margin · main column 462 (478 on Letter) · gutter 27 · sidebar 257
  (263), bleeding right

---

## Wiring up ChatGPT

**Two halves, and they live in different places.** ChatGPT reads the *process* from
this repo and runs the *build* from an attached file. They cannot be the same thing:
the GitHub connector puts repo files into the model's context, while Code Interpreter
is a separate sandbox that only sees what you upload to it.

- **Point it at the repo** — connect the GitHub connector, or paste the raw URL of
  `AGENT.md` and let it follow the links:

  > Read AGENT.md in this repo and follow it. Make a Box data sheet for [customer].

  `AGENT.md` sends it to the files it needs and explicitly fences off `reference/`.
  Keeping that fence is what keeps the token cost flat as the repo grows.

- **Attach `dist/box-datasheet-builder.py`** to the same GPT or Project. Without it
  the model cannot run a build at all without first retyping the template into the
  sandbox — ~16k tokens a sheet, and a retyped template is drifted layout.

Rebuild the attachment with `python3 scripts/bundle.py` whenever the template or the
credential list changes; `--check` tells you if it has fallen behind. The files you
maintain by hand — the disclaimer, the voice guide, the boilerplate figures, the Box
folder ID — are read live from the repo and never need a rebuild.

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

- **Print from the browser** — margins None, Background graphics ON. Works everywhere,
  and it's the path to assume. The page size is carried by the sheet.
- **`--pdf`** uses Playwright if it is installed, or any Chrome/Chromium already on the
  machine. Don't install anything just for this.

The HTML is self-contained apart from the Google Fonts link, so it travels fine.

## Where logos come from

**The Box approved-logos folder**, read over MCP at proposal time, chosen against the
recipient — same sector and similar size first, direct competitors included because
that is the strongest proof on the page. `assets/logos/` is only a cache; the files in
it today are example assets for the worked example, not a standing set.

If the folder is unreachable, ChatGPT asks you to name the companies rather than
sourcing logos elsewhere.

## Graphics from box.com

Product screenshots, diagrams and illustrations. Three routes — and the first is
usually enough, because **a remote URL just works**: the browser loads it when the
sheet is opened and it prints fine.

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

You can also cut a graphic straight out of a Box PDF:

```bash
python3 scripts/extract_from_pdf.py brief.pdf --page 2 --detect 44,690,552,950
python3 scripts/extract_from_pdf.py brief.pdf --page 2 \
        --box 80,750,506,921 --bg FFFFFF --out assets/portal.png
```

`brand/SOURCING.md` covers all three routes and where to look.

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
- **A compliance pill that is not in `brand/compliance.json`** — the credential list
  is closed, so an invented certification or a residency zone Box does not offer
  cannot reach a customer.
- **A block type or icon name the template cannot draw** — an unknown block used to
  render a red error line onto the finished sheet, and an unknown icon a silent gap.
- **A company name typeset in SVG and passed off as a logo.** `brand/LOGO-RULES.md`
  forbids fabricating a mark; this makes it mechanical. Tier 4 (`"wordmark"`) is the
  honest way to show a customer with no approved asset.
- **A disclosure line that needs a footer taller than 60px** — the strip grows to fit
  Legal's wording rather than clipping it, but not without limit.

It also *warns* below 72% fill, because a half-empty column is what made the original
page 2 read clunky — unless the column ends in a `"pin": "bottom"` block, where the
gap is deliberate. The template then measures the real layout in the browser and
paints a red rule if anything still overflows.

Two layers, because arithmetic before render is cheap and catches most of it, and
only the browser knows the truth. Measured against real renders the estimates run
**0–6% over, never under** — deliberately, so a column that passes the arithmetic
fits on the page. That slack is why the recipes aim for 88–95% rather than 99%.
