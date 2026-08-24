# reference/ — source material

Everything here is **for humans and for Claude when calibrating the template**.

> **The generator must never read this folder.** It is large, and reading it would
> cost the agent thousands of tokens for no benefit. `AGENT.md` fences it off
> explicitly. If you point ChatGPT at this repo, it reads `AGENT.md` — not this.

## What's here

| File | What it is |
|---|---|
| `source-datasheet-icm-0425.pdf` | The original two-page Box ICM data sheet |
| `source-page1.png` | Page 1 rendered at 152% for measurement |
| `source-page2.png` | Page 2 rendered at 152% |
| `DESIGN-SPEC.md` | **Every measured value** — palette, fonts, grid, structure |

## Adding more source material

Drop files straight in via *Add file → Upload files*. Useful additions:

1. **`brand-guidelines.pdf`** — the full Box brand book. It gets distilled into
   `brand/VOICE.md`; the book itself stays here and is never read at generation time.
2. **`figma-tokens.md`** — Figma → Dev Mode → select the frame → copy the CSS panel.
   Plain text, exact values, costs nothing to store.
3. **Newer versions of the data sheet** — name them with the date, e.g.
   `source-datasheet-icm-0126.pdf`, so the lineage stays readable.

**Note on size:** GitHub's web uploader caps at 25 MB per file. Above that, use
`git push` from a terminal, or just upload PNG exports instead — for calibrating
a layout they are better input than the PDF anyway.
