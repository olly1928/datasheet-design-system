# Sourcing assets from box.com

Box publishes a great deal of usable material: product screenshots, illustrations,
diagrams, and customer logo strips on its industry pages. The Frasers brief in
`content/` was built almost entirely from the Box retail page. This file is how to
find that material again, get it into a sheet, and leave a record of where it came
from.

> **A note on what follows.** The URL patterns below are written from how box.com has
> been structured, but they are **not verified** — the environment this repo was built
> in cannot reach box.com. Treat them as places to start, confirm the real path when
> you browse, and correct this file when you find a better one.

---

## Two different questions

Keep these apart, because they have different answers.

**Box's own graphics** — product screenshots, UI mockups, illustrations, diagrams,
icons. These are Box's to publish and Box's to reuse. Take them freely. Record where
they came from so a later reader can find the original.

**Third-party customer logos** — Nike, M&S, Skechers on the retail page. These are
other companies' marks. Box displays them under agreements Box holds. Reusing one on
a customer-facing document is a reasonable extension of that — Box is publicly
claiming the relationship — but it is worth being able to *show* where you got it.
That is what `assets/logos/manifest.json` is for: not a gate, a record.

So: **box.com is a legitimate source. The manifest is where you write down what you
took and when, so the claim is auditable.** Recording "found on
box.com/industries/retail, 2026-08-26" is the evidence.

---

## Where to look

Work down this list; stop when you have what the sheet needs.

**1. The industry page matching the prospect's sector.** The richest source by far —
it carries a logo strip of customers in that sector plus sector-specific product
graphics, both already framed for that audience.

```
box.com/industries/<sector>
```
Sectors seen in use: `retail`, `financial-services`, `healthcare`, `life-sciences`,
`legal`, `media-entertainment`, `government`, `education`, `manufacturing`, `energy`.
Regional variants exist — the Frasers sheet links `box.com/en-gb/industries/retail`.

**2. The customer story for a named account.** If the prospect asked "who like us
uses this", a story page gives you the logo, the quote, and the metric — all three
already cleared for publication.

```
box.com/customers          ·  box.com/customers/<company>
```

**3. Product and solution pages,** for capability diagrams and UI shots.

```
box.com/<product>          e.g. /box-ai, /sign, /hubs, /shield, /governance
```

**4. The resource library,** for existing data sheets and briefs — useful for
checking how a claim is currently worded before you rewrite it.

```
box.com/resources
```

**5. Box brand assets,** for the Box logo itself in approved forms — see the Box
Support article "Box Branding 101: Guidelines and Assets".

### Searching

```
site:box.com <sector> customers
site:box.com "<company name>"
site:box.com <capability> filetype:pdf
```

If a page renders its images from a CDN, the asset URL is usually on
`images.ctfassets.net` or a `box.com` subdomain — both are on the fetch allowlist.

---

## Getting an asset into a sheet

You have browsing; the build script may not have network access. Both paths work.

### The good path — cache it

```bash
python3 scripts/fetch_asset.py "https://images.ctfassets.net/.../retail-hero.png"
```

Downloads to `assets/cache/`, records the URL, size, checksum and date in
`assets/cache/provenance.json`, and prints the filename to use:

```jsonc
{ "type": "figure", "width": 80,
  "image": { "src": "a1b2c3d4e5-retail-hero.png", "alt": "…" },
  "caption": "…" }
```

Cached assets make the sheet self-contained and identical on every rebuild.

### The fallback — put the URL straight in

```jsonc
{ "type": "figure", "aspect": 2.3,
  "image": { "src": "https://images.ctfassets.net/.../retail-hero.png", "alt": "…" } }
```

`scripts/build.py` tries to cache it. If it cannot reach the network it leaves the URL
in place and says so. **The sheet still works** — the browser loads the image when the
file is opened. The cost is that the PDF then depends on that URL being reachable at
print time, and the file is not portable offline.

**Declare `aspect` (width ÷ height) whenever you use a live URL.** The validator
cannot measure an image it has not downloaded, and without a hint it assumes a tall
one and may reject the page.

### Fetching is restricted

`scripts/fetch_asset.py` only downloads from hosts in `assets/cache/allowlist.txt`,
and re-checks on every redirect so a redirect cannot walk the fetch off-domain. It
refuses anything that is not an image and anything over 8 MB. If you find a genuine
Box-owned host that is not listed, add it to the allowlist and say so in your reply.

---

## Record what you took

For a **logo**, add a manifest entry — this is the part that compounds:

```jsonc
"nike": {
  "name": "Nike",
  "files": { "colour": "cache/7f3a91c0de-nike.svg" },
  "aspect": "mark",
  "reverse_permitted": false,
  "shareable": "approved",
  "source": "box.com",
  "source_url": "https://images.ctfassets.net/.../nike.svg",
  "source_page": "https://www.box.com/en-gb/industries/retail",
  "reviewed": "2026-08-26"
}
```

For a **graphic**, the provenance file already holds the record; nothing else to do.

---

## Do a sector sweep once, not per sheet

The first time you build for a sector, spend the extra minutes doing this — every
later sheet for that sector then costs nothing:

1. Open the industry page for the sector.
2. Cache every customer logo on it with `fetch_asset.py`.
3. Write a manifest entry for each, with `source_page` set to that page.
4. Cache the two or three product graphics worth reusing.
5. Say in your reply what you added, so a human can glance at it.

That turns a per-sheet research cost into a one-off, and it is how the repo gets
more useful over time rather than staying static.

---

## What not to take

- **A logo from anywhere other than Box's own site** — a competitor's customer page,
  a logo aggregator, an image search result. The point of sourcing from box.com is
  that Box is publicly claiming the relationship. Nothing else carries that.
- **Anything behind a login, a form, or a download gate.** If it was gated it was not
  published for reuse.
- **Stock photography**, unless you can see the licence. Box's own illustrations and
  product shots are safe; a stock photo on a blog post may not be.
- **A logo you cannot record.** If you cannot say which page you found it on, do not
  use it — fall back to tier 4 in `brand/LOGO-RULES.md` and typeset the name.
