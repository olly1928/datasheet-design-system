# Logo rules

Two different logo jobs appear on a data sheet. Keep them straight:

1. **The customer's logo**, top-right of the blue band — *this sheet is for you*.
2. **Peer logos**, in the `logogrid` on the right panel — *companies like you already
   run Box*.

Both are governed by the same authority.

---

## The manifest is the only authority

`assets/logos/manifest.json` decides what may be used. One entry per company:

```jsonc
"acme": {
  "name": "Acme Corp",
  "files": { "white": "acme-white.svg", "colour": "acme-colour.svg" },
  "aspect": "wordmark",            // wordmark | mark | stacked
  "reverse_permitted": true,       // may this be flattened to white?
  "shareable": "approved",         // approved | internal-only | expired
  "source": "Box /Brand/Approved Customer Logos",
  "approved_by": "...",
  "reviewed": "2026-08-01"
}
```

**No entry → add one, or fall back to tier 4.** If you sourced the logo from box.com,
write the entry (see *Sourcing from box.com* below) and use it. If you cannot say
where it came from, do not use it: typeset the customer's name instead and omit the
peer from the grid.

`"shareable": "internal-only"` and `"expired"` are both **no**, the same as absent.

### Sourcing from box.com

**box.com is a legitimate source, and the best one.** Where Box publishes a customer
logo on its own site — the industry pages carry logo strips per sector — Box is
publicly claiming that relationship. Reusing that logo on a Box sales document is a
reasonable extension of the same claim.

So the manifest is **a record, not a gate**. Its job is to let you show where a logo
came from:

```jsonc
"source": "box.com",
"source_url":  "https://images.ctfassets.net/.../nike.svg",
"source_page": "https://www.box.com/en-gb/industries/retail",
"reviewed": "2026-08-26"
```

"Found on box.com/industries/retail on this date" is the evidence. A logo you cannot
attribute to a page is the one to leave out.

**`brand/SOURCING.md` covers where to look and how to fetch.** Do a sector sweep once
and every later sheet for that sector costs nothing.

Anywhere other than Box's own site — a competitor's customer page, a logo
aggregator, an image search — carries none of that, so it is out.

---

## The treatment ladder

Stop at the first tier you can genuinely satisfy.

### Tier 1 — `white`: a true reversed asset
The one that looks deliberate. The logo sits directly on the blue with no container.
If the manifest has a `white` file, use it.

With inline SVG you can often *make* this tier: take the colour asset and rewrite
every `fill` and `stroke` to `#FFFFFF`. For a single-colour mark this is exactly what
a designer would hand you. Only do it when `reverse_permitted` is true.

### Tier 2 — `reverse`: flatten a mono-safe asset
`filter: brightness(0) invert(1)` renders any transparent asset pure white. Cheap and
effective for single-colour marks.

**Do not use this when colour carries meaning.** Multi-colour logos where the colours
*are* the identity — think of any mark whose segments are deliberately different
hues — become an unreadable white blob, and flattening them usually breaks that
company's own brand rules. `reverse_permitted: false` means exactly this. Go to tier 3.

### Tier 3 — `plate`: a white plate
Full-colour logo on a white rounded rectangle with even padding and a soft shadow.
It reads as a deliberate design element rather than a paste. This is the workhorse —
most full-colour logos land here and it looks good.

Padding must be **even on all four sides**. A logo crammed against one edge is the
single clearest tell that a machine placed it.

### Tier 4 — `wordmark`: typeset the name
No approved asset. Set the customer's name in the sheet's own typeface. Restrained,
honest, and it never looks broken.

**Never fabricate a logo.** Do not draw an approximation, do not pull one off a
search result, do not generate one. Tier 4 exists precisely so you never have to.

---

## Optical sizing

A wide wordmark and a square mark set to the same pixel height do not read as the
same size — the square one will look much heavier. The template handles this if you
tag the asset correctly:

| `aspect` | Shape | Rendered height |
|---|---|---|
| `wordmark` | Wide and short (name set as text) | 31px |
| `mark` | Roughly square (a symbol) | 46px |
| `stacked` | Symbol above text | 58px |

Choose by the asset's actual proportions, not by what the company calls it.

---

## Peer logos in the grid

The `logogrid` on page 1 answers "do companies like me use this?". So choose for
**relevance over fame**: four recognisable names from the prospect's own sector beat
ten famous ones from everywhere.

- Six is a good number. Ten is a wall.
- Every one needs a manifest entry, same as above.
- Prefer a consistent visual weight. One enormous wordmark beside five small marks
  looks like an accident.
- The grid renders them greyscale at a common height — do not try to defeat this.
