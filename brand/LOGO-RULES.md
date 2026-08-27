# Logo rules

Two different logo jobs appear on a sheet. Keep them apart:

1. **The customer's logo**, top right of the blue band — *this sheet is for you*.
2. **Peer logos**, in the `logostack` on the grey panel — *companies like you already
   run Box*.

---

## Where logos come from

**The Box approved-logos folder is the source of record.** Read it over MCP. A logo
that is not in that folder does not go on a sheet.

That rule exists because the folder is the one place someone has actually decided
these are cleared for external use. Nothing else carries that — not a logo on a
competitor's customer page, not an image search result, not a logo aggregator.

Two fallbacks, in order:

- **Folder unreachable** → say so and **ask the user to name the companies** they want
  shown. Do not go looking elsewhere.
- **A named company is not in the folder** → say so in your proposal and leave it out.
  Do not substitute a similar company without saying you did.

---

## Choosing peer logos

The `logostack` answers one question: *do companies like me use this?* So choose for
**relevance to the recipient**, not fame. Work down this ranking:

1. **Same sector, similar size.** The closest analogue to the recipient. This is the
   logo that does the most work.
2. **Direct competitors — include them.** "The people you compete with already run
   Box" is the strongest proof available on the page. **Say so in your proposal** so
   the user can see the choice was deliberate rather than accidental.
3. **Recognisable names in adjacent sectors,** to fill out the set.
4. **Never more than four.** A wall of logos reads as filler and stops being proof.

Give one short clause of reasoning per logo in your proposal. The user is approving
your thinking, not a list of names.

---

## The treatment ladder — the customer's logo

Stop at the first tier the asset can genuinely satisfy.

### Tier 1 — `white`: a true reversed asset
The one that looks deliberate. The logo sits directly on the blue with no container.
With inline SVG you can often *make* this tier: take the colour asset and rewrite every
`fill` and `stroke` to `#FFFFFF`. Only where `reverse_permitted` is true.

### Tier 2 — `reverse`: flatten a mono-safe asset
`filter: brightness(0) invert(1)` renders any transparent asset pure white. Cheap and
effective for single-colour marks.

**Not when colour carries meaning.** A multi-colour mark whose colours *are* the
identity becomes an unreadable white blob, and flattening it usually breaks that
company's own brand rules. Go to tier 3.

### Tier 3 — `plate`: a white plate
Full-colour logo on a white rounded rectangle with even padding and a soft shadow.
It reads as a deliberate design element rather than a paste. This is the workhorse.

Padding must be **even on all four sides**. A logo crammed against one edge is the
clearest tell that a machine placed it.

### Tier 4 — `wordmark`: typeset the name
No approved asset. Set the customer's name in the sheet's own typeface. Restrained,
honest, and it never looks broken.

**Never fabricate a logo.** Do not draw an approximation, pull one off a search
result, or generate one. Tier 4 exists precisely so you never have to.

### That includes Box's own mark

The Box wordmark in the band is **genuine vector artwork**, lifted out of the ICM data
sheet's own path geometry and hardcoded in `template/datasheet.html`. It is not a
drawing of the logo; it is the logo.

It was, briefly, a drawing — an SVG path traced by hand, with the wrong proportions and
a detached-looking `x`. It sat on every sheet the system produced until someone noticed.
The rule against fabricating logos is not only about customer marks, and the mark that
appears on *every* sheet is the worst one to approximate.

**Do not redraw it.** If it ever needs regenerating:

```bash
python3 scripts/extract_vector_from_pdf.py \
        reference/source-datasheet-icm-0425.pdf \
        --region 30,735,85,780 --label Box --fill "#FFFFFF" \
        --out assets/box-logo-white.svg
```

---

## Why full-colour logos cannot go on the band

Not an assertion — this was tested. The four marks in
`content/_example-frasers-brief.json` were composited onto the band blue (`#002959`)
and onto white, side by side:

| | On white | On the band blue |
|---|---|---|
| Nike | clean black swoosh | a dark blob, barely visible |
| Marks & Spencer | fine grey strokes, gold ampersand | unreadable |
| Skechers | navy wordmark | navy on navy — gone |
| Allbirds | clean black script | a dark smudge |

They are perfect on white and unusable on the blue. That is the whole reason the
ladder exists: **peer logos belong on the grey panel** (`#F5F6F8`), where they look
right; a customer logo that must sit in the band needs tier 1 or tier 3.

If you are ever tempted to drop a full-colour logo straight onto the band, this is
what happens.

---

## Optical sizing

A wide wordmark and a square mark set to the same pixel height do not read as the same
size — the square one looks much heavier.

| `aspect` | Shape | Rendered height |
|---|---|---|
| `wordmark` | Wide and short | 30px |
| `mark` | Roughly square | 44px |
| `stacked` | Symbol above text | 56px |

Choose by the asset's actual proportions, not by what the company calls it.

The `logostack` handles this differently, constraining on both axes so a very wide
mark (Skechers) and a squarer one (Nike) end up optically comparable. Nothing to set
per logo.

---

## Recording what you used

`assets/logos/manifest.json` records what is in the repo and where each file came from:

```jsonc
"acme": {
  "name": "Acme Corp",
  "files": { "white": "acme-white.svg", "colour": "acme.png" },
  "aspect": "wordmark",
  "reverse_permitted": true,
  "shareable": "approved",
  "source": "Box /Approved Customer Logos",
  "reviewed": "2026-08-26"
}
```

The repo is a **cache**, not the authority. The Box folder decides what is approved;
the manifest records what was pulled down and when, so a later reader can retrace it.
