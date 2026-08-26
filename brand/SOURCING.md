# Sourcing graphics

**Logos are not covered here.** They come from the Box approved-logos folder, chosen
per recipient — `brand/LOGO-RULES.md`. This file is about the other imagery: product
screenshots, diagrams, illustrations.

---

## The three routes

Start at the top. Most of the time the first one is all you need.

| Route | Effort | Self-contained? | Use when |
|---|---|---|---|
| **Put the URL in `src`** | none | no | Default |
| **`scripts/fetch_asset.py <url>`** | one command | yes | Must survive offline |
| **`scripts/extract_from_pdf.py`** | one command | yes | box.com unreachable, PDF in hand |

### 1. Link it — usually enough

```jsonc
{ "type": "figure", "aspect": 2.3,
  "image": { "src": "https://images.ctfassets.net/.../retail-hero.png", "alt": "…" } }
```

**A remote `src` is not a problem.** The browser fetches it when the sheet is opened,
and it prints to PDF exactly as an embedded image would. `build.py` tries to cache it;
if it has no network it leaves the URL alone and says so. The sheet still works.

The cost is only that the file is not portable offline, and that the PDF depends on
that URL still resolving at print time. For a sheet you are sending this week, neither
matters.

**Declare `aspect`** (width ÷ height) whenever you use a live URL. The validator cannot
measure an image it has not downloaded and will otherwise assume a tall one and reject
the page.

### 2. Cache it — when it has to last

```bash
python3 scripts/fetch_asset.py "https://images.ctfassets.net/.../retail-hero.png"
```

Downloads to `assets/cache/`, records the URL, size, checksum and date in
`assets/cache/provenance.json`, and prints a filename to use as `src`. Restricted to
the hosts in `assets/cache/allowlist.txt`, re-checked on every redirect, images only,
8 MB cap.

### 3. Cut it out of a Box PDF

Box publishes a lot of PDFs, and many are exported as one full-page raster per page —
which makes them a usable source when box.com is not reachable. The product screenshot
in the Frasers example came out of a PDF this way.

```bash
# what's in this PDF?
python3 scripts/extract_from_pdf.py brief.pdf --list

# find the artwork (CSS px, page assumed 816 wide)
python3 scripts/extract_from_pdf.py brief.pdf --page 2 --detect 44,690,552,950

# cut it out, keying the flat background to transparency
python3 scripts/extract_from_pdf.py brief.pdf --page 2 \
        --box 80,750,506,921 --bg FFFFFF --out assets/portal.png
```

`--detect` prints ready-to-paste `--box` values, so you locate artwork rather than
guessing at it. Omit `--bg` to keep the crop opaque.

---

## Where to look on box.com

> The paths below are written from how box.com has been structured but are **not
> verified** — the environment this repo was built in cannot reach box.com. Confirm
> the real path when you browse, and correct this file when you find a better one.

**1. The industry page for the recipient's sector** — the richest source, carrying
sector-specific product graphics already framed for that audience.

```
box.com/industries/<sector>
```
Sectors seen in use: `retail`, `financial-services`, `healthcare`, `life-sciences`,
`legal`, `media-entertainment`, `government`, `education`, `manufacturing`, `energy`.
Regional variants exist — the Frasers sheet links `box.com/en-gb/industries/retail`.

**2. Product and solution pages,** for capability diagrams and UI shots.

```
box.com/<product>          e.g. /box-ai, /sign, /hubs, /shield, /governance
```

**3. The resource library,** for existing sheets and briefs — useful for checking how
a claim is currently worded before you rewrite it, and a source of PDFs for route 3.

```
box.com/resources
```

### Searching

```
site:box.com <sector> customers
site:box.com <capability> filetype:pdf
```

Page imagery usually resolves to `images.ctfassets.net` or a `box.com` subdomain —
both already on the fetch allowlist.

---

## What not to use

- **Anything behind a login, a form, or a download gate.** If it was gated it was not
  published for reuse.
- **Stock photography**, unless you can see the licence. Box's own illustrations and
  product shots are safe; a stock photo on a blog post may not be.
- **Screenshots showing real customer data.** Box's published mockups use invented
  content. Anything that looks like a real account is not for reuse.
- **Logos.** Not from here. `brand/LOGO-RULES.md`.
