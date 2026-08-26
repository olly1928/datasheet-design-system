# How to generate a Box data sheet

## The one rule

**Never generate a sheet on the first turn.**

You propose. The user confirms. Then you build. Every time — including when the brief
looks complete, when the user sounds like they are in a hurry, and when you are
confident. The confirmation step is what puts a human between a logo selection and a
customer's inbox, and it is the reason this system can be used at all.

If you find yourself writing a content file before the user has approved a plan, stop.

---

## Turn 1 — gather, then propose

**1. Read the brief.** Who is this going to? What use case? What have they already
been told? If the brief names a workflow, that workflow is the sheet.

**2. Look at the approved logos.** Read `config.json` for the Box folder, then list it
over the Box connector. Note what exists for the recipient's sector. **That folder is
the only source for logos** — see `brand/LOGO-RULES.md`.

If `boxLogosFolder.folderId` is blank, or you cannot reach the folder, say so plainly
and **ask the user to name the companies** they want shown. Do not source logos from
anywhere else, and do not quietly carry on without them.

**3. Work out the sheet.** Type, angle, headline, block outline, proof, logo set.
`brand/BLOCKS.md` has the recipes; `brand/VOICE.md` governs every word you draft.

**4. Print the plan and stop.** Do not write files. Do not run the build.

### The proposal

```
SHEET PLAN — Acme Corp

Type      Solution brief
Angle     Claims intake — the workflow they raised on the call
Headline  "Settle a claim without chasing the file"
Deck      One content layer under the systems adjusters already use.

Page 1    hero → challenge/solution → three shifts → who gets what
Page 2    what you get (8) → integrations panel → figure → learn more

Peer logos — from Box /Approved Customer Logos
  Zurich     direct competitor, same market — strongest proof on the sheet
  Aviva      same sector, UK, similar size
  Admiral    direct competitor, UK motor
  AXA        sector match, high recognition
Customer logo   acme-white.svg is in the folder — tier 1, sits straight on the blue

Proof
  Quote     no approved insurance reference — I'll leave a placeholder
  Stats     68% of Fortune 500 · 1,500+ integrations (both from SNIPPETS.md)

Compliance
  UK data residency      Acme is UK-headquartered
  ISO 27001              baseline, every reviewer knows it
  SOC 2 Type II          baseline
  FINRA / SEC 17a-4      they're a broker-dealer — the one that matters here
  GDPR                   UK/EU customer data
  + assurances: "Your keys, not ours" and "AI that doesn't learn from you"

Placeholders you'll need to fill
  [ACCOUNT TEAM CONTACT]
  [CLAIMS CYCLE-TIME METRIC — SOURCE REQUIRED]

Reply "go" to build, or tell me what to change.
```

Two parts of that are not optional:

- **Why each logo was chosen.** The user is approving your reasoning, not a list. One
  short clause each. Where you have picked a direct competitor, say so — it is the
  strongest proof available and the user should see the call was deliberate.
- **Which compliance credentials you will claim, and why.** These are assertions about
  the product on a document with the user's name on it. Pick them from
  `brand/compliance.json` — a closed list — and match residency to the recipient's HQ
  country. There are ten zones and no more; a country outside them has no zone, so
  route it to EU or US and say which you chose. `brand/COMPLIANCE.md` has the rules.
- **What you will leave as a placeholder.** Anything you could not source. This is how
  an unapproved claim gets caught before it ships, not after.

Keep it to that shape. It should be readable in fifteen seconds.

## Turn 2 — build

On approval: write `content/<customer-slug>.json`, then

```bash
python3 scripts/build.py content/<customer-slug>.json
```

It validates, resolves assets, and writes `out/<customer-slug>-box-datasheet.html`.
Hand the user that file. For a PDF: open it and print — **Letter, margins None,
"Background graphics" ON**.

If the user amended anything, **take the amendment as final and build.** Do not
re-propose; they have already made the decision.

If the build **refuses**, it has told you exactly what is wrong. Fix the JSON and run
it again. Do not pass `--force` to get around a real overflow.

---

## What to read

This file, `config.json`, `brand/VOICE.md`, and `brand/BLOCKS.md` — about 4k tokens,
enough for a normal job. Add `brand/COMPLIANCE.md` and `brand/compliance.json` when
filling the compliance pills. Add `brand/LOGO-RULES.md` when choosing logos and `brand/SOURCING.md` when
you need a graphic. **Never read `reference/`**: it holds source PDFs and page renders
for humans, it is large, and it contains nothing you need.

## Pick a sheet type

Both share identical styling. The type sets the eyebrow in the blue band and decides
the shape of the content.

| `meta.type` | For | Eyebrow |
|---|---|---|
| `solution-brief` *(default)* | One named use case for one customer | SOLUTION BRIEF |
| `datasheet` | The product as a whole, angled at one customer | DATA SHEET |

**Prefer `solution-brief`.** A sheet about one real workflow beats a general product
sheet with the customer's name dropped in.

Recipes live in `brand/BLOCKS.md`. Copy the matching example —
`content/_example-frasers-brief.json` or `content/_example-meridian.json` — and
replace the content. Do not build from nothing.

## The shape of the file

```jsonc
{
  "customer": "Acme Corp",
  "meta": {
    "size": "letter",            // or "a4"
    "type": "solution-brief",
    "title": "Box for the claims intake process",   // <= 74 chars, sits in the band
    "footerMeta": "box.com"
  },
  "logo": { ... },
  "legal": "...",
  "pages": [
    { "band": true, "main": [ ...blocks ], "aside": [ ...blocks ] },
    {                "main": [ ...blocks ], "aside": [ ...blocks ] }
  ]
}
```

### Two titles, not one

The band carries a **modest** title saying what the document *is*. The big headline
lives in the body, in the `hero` block, and says what it is *worth*:

```jsonc
"meta": { "title": "Box for the franchise partner portal" }        // the band
{ "type": "hero",
  "headline": "Give every franchise partner one source of truth",  // the page
  "deck": "One content layer underneath every system your teams use." }
```

Never put the argument in the band, and never open the body with a paragraph.

## Fitting the page

Every column must land under **100%** fill or the build refuses. **Aim for 88–95%** —
the estimate carries about ±4%, and slack absorbs the difference when a font falls
back. The built page also draws a red rule in the browser if anything still overflows.

- **Overflowing?** Cut copy. In `caps`, `cards`, `featurelist` and `steps`, row height
  is set by the *tallest* item in the row — trimming a short one changes nothing.
- **Sparse?** Add a block rather than padding copy. A column ending in a
  `"pin": "bottom"` block is *anchored*, not sparse, and the validator knows that.

Character limits live in `template/content.schema.json` and are measured against
rendered text, so markdown syntax does not count against you.

## The customer logo

Top right of the band, under a small "Prepared for" label.

| Tier | `"tier"` | When | Result |
|---|---|---|---|
| 1 | `white` | A genuine white/reversed asset exists | Sits straight on the blue. Best. |
| 2 | `reverse` | Mono-safe asset, any colour | CSS flattens it to pure white |
| 3 | `plate` | Full-colour asset, colour is meaningful | White rounded plate on the blue |
| 4 | `wordmark` | No approved asset | The name, typeset. Never fake a logo. |

```jsonc
"logo": { "tier": "white", "aspect": "wordmark", "alt": "Acme Corp",
          "label": "Prepared for", "src": "acme-white.svg" }
```

`aspect` (`wordmark` | `mark` | `stacked`) is not decoration — a wide wordmark and a
square mark at one pixel height look nothing alike. Full details, and the ranking for
choosing *peer* logos, are in `brand/LOGO-RULES.md`.

## Images

**Three routes, and the first one is usually enough:**

| Route | Self-contained? | Use when |
|---|---|---|
| **Put the URL in `src`** | no | Default. It just works. |
| **`scripts/fetch_asset.py <url>`** | yes | The sheet must survive offline |
| **`scripts/extract_from_pdf.py`** | yes | box.com unreachable, Box PDF in hand |

**A remote `src` is not a problem.** The browser loads it when the sheet is opened and
it prints fine. Caching is an upgrade, not a prerequisite. When you do use a live URL,
declare `"aspect"` (width ÷ height) — the validator cannot measure an image it has not
downloaded and will otherwise assume a tall one.

Never paste base64 into a content file. `brand/SOURCING.md` covers where to look.

## The legal line

The AI-disclosure line sits in the footer of **page 2**. Copy the text from
`legal/disclaimer.md` **verbatim** into `"legal"`. Do not write your own, paraphrase,
or trim it to fit. If it does not fit, that is a bug to report, not to edit around.

## Voice

`brand/VOICE.md` governs every word. Two rules override everything:

- **Never invent a number, customer name, quote, or claim.** Write a visible
  placeholder — `[NAME, TITLE]`, `[METRIC — SOURCE REQUIRED]` — and list it in your
  proposal so the user knows it is coming.
- **Never attribute a quote to a real person** unless it came from an approved
  reference. A fabricated customer quote is a legal problem, not a copy problem.
