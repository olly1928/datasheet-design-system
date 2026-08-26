# assets/logos

A **cache**, not the approved list.

The authority on which logos may be used is the **Box approved-logos folder**, read
over MCP at generation time — see `brand/LOGO-RULES.md`. This directory holds files
that have been pulled down so a build can run without a round trip.

## What's here now

`nike.png`, `marks-spencer.png`, `skechers.png`, `allbirds.png` — **example assets
only**. They were extracted from `reference/source-frasers-solution-brief.pdf` with
`scripts/extract_from_pdf.py` so the worked example renders as the real sheet does,
rather than showing typeset placeholder names.

**They are not a standing peer set.** The right logos differ for every recipient, and
are chosen against that recipient at proposal time. Do not treat this folder as a
menu.

## Adding one

1. Confirm it is in the Box approved folder.
2. Put the file here — SVG if at all possible; a transparent PNG otherwise.
3. Add a `manifest.json` entry with `aspect`, `reverse_permitted` and where it came
   from.

Transparent PNGs cut from a Box PDF:

```bash
python3 scripts/extract_from_pdf.py <pdf> --page 1 --detect 556,730,816,1040
python3 scripts/extract_from_pdf.py <pdf> --page 1 \
        --box 644,781,718,808 --bg F5F6F8 --out assets/logos/name.png
```
