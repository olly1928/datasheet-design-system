# Box voice — working rules

> **Status: derived, not official.** Every rule below was reverse-engineered from the
> copy in the ICM data sheet (04/25). It is accurate to that artefact but it is *not*
> Box's brand language guide. Drop the official guide into `reference/` and this file
> gets rewritten from it. Until then, treat the observed patterns as binding and the
> gaps as gaps.

Written for a model, not a human: short, imperative, example-led. The rewrites at the
end teach voice faster than any adjective.

---

## Voice in one line

Confident about the category, plain about the mechanics, always in the customer's
terms. Box explains what content can do for *you* — it does not celebrate itself.

## Sentence shape

- **Second person.** "your files", "your content", "your workflows" — not "clients'
  files" or "the organisation's content".
- **Verb-first for capabilities.** "Create, iterate, and share…", "Manage, retain,
  and govern…", "Automate your tasks…". Start with the thing the customer does.
- **Serial comma.** "manage, protect, and extract value".
- **Spaced em-dash for the aside.** "with anyone (including external parties) — with
  AI-powered collaboration on any device."
- **Bold lead-in, colon, then the detail.** "**Enterprise-first:** Access AI right
  where your enterprise content lives." Used throughout page 2. In content JSON write
  it as `**Enterprise-first:**` — the template renders the bold.
- Sentences run long in body copy and short in card copy. Match the block.

## Naming and capitalisation

| Write | Not |
|---|---|
| Intelligent Content Management | intelligent content management, ICM on first use |
| Content + AI | Content and AI, content+AI |
| Box | BOX, box (except in the logo) |
| AI agents | agents, Agents |
| Box AI | BoxAI, Box's AI |
| e-signatures | eSignatures, E-Signatures (mid-sentence) |

- Spell out **Intelligent Content Management** on first use. `ICM` is acceptable
  afterwards in body copy, never in a heading.
- Analyst awards carry the trademark mark: `Gartner Magic Quadrant™`,
  `The Forrester Wave™`, `IDC MarketScape™`.
- Product surface names are capitalised as products: Portals, Box Sign. Generic
  capabilities are not: secure collaboration, document management.

## Words to avoid

**Never:** revolutionary, game-changing, best-in-class *(as a bare claim)*, seamless,
robust, leverage synergies, cutting-edge, unlock the power of *(as a headline)*,
frictionless, turnkey, world-class, unparalleled.

**Careful:** "leading" is used in the source ("the leading Intelligent Content
Management platform") — it is house style and permitted, but only about Box's
category position, never about an unproven attribute.

**Never hedge a fact:** no "up to", "as much as", or "helps reduce" wrapped around a
number you cannot source.

## Claims — the hard rule

Every number, customer name, quote, and competitive statement must come from an
approved source. `brand/SNIPPETS.md` holds cleared boilerplate; use it verbatim
rather than composing a new version of the same claim.

Where you need a fact you do not have, **write a visible placeholder** —
`[NAME, TITLE]`, `[ACCOUNT TEAM CONTACT]`, `[METRIC — SOURCE REQUIRED]`. A bracketed
gap gets filled by a human. An invented number gets sent to a customer.

Never attribute a quote to a named person unless it came from an approved reference.

## Writing for a specific customer

This is what makes the sheet worth generating:

- **Name their work, not their industry.** "the suitability files that satisfy
  regulators" beats "documents in financial services".
- **Substitute their nouns.** Where the general sheet says "sales contracts", a
  hospital's sheet says "consent forms". Same sentence shape, their vocabulary.
- **One customer-specific `aside` block** — a "Why [customer], specifically" list —
  is the highest-value personalisation on the page. Three lines, concrete.
- **Do not invent their pain.** If you do not know what they struggle with, write the
  capability plainly rather than guessing at a problem.

---

## Rewrites

**1 — feature, not outcome**
✗ Box provides a robust, best-in-class repository for enterprise file storage.
✓ Manage, retain, and govern your files in one secure place, and add structure to
  your content with AI-powered data extraction.

**2 — invented number**
✗ Customers see up to 40% faster onboarding.
✓ [ONBOARDING METRIC — SOURCE REQUIRED]

**3 — company-centric**
✗ We are excited to partner with organisations on their AI journey.
✓ Access AI right where your enterprise content lives; ask any questions, generate
  content, and get instant insights.

**4 — hollow adjectives**
✗ A seamless, frictionless, cutting-edge collaboration experience.
✓ Create, iterate, and share files from anywhere, with anyone — including external
  parties — on any device.

**5 — generic where it should be specific**
✗ Box helps businesses in every industry manage their documents.
✓ Box gives Meridian one governed place for advisory agreements, suitability files,
  and client records.

**6 — headline that says nothing**
✗ Unlock the Power of Your Content Today
✓ Intelligent Content Management for Meridian Financial

**7 — fabricated proof**
✗ "Box transformed our business overnight." — CTO, Global Bank
✓ "[QUOTE from approved references]" — [NAME, TITLE], [CUSTOMER]

**8 — mangled product naming**
✗ Box's ICM platform uses BoxAI and eSignatures.
✓ The Box Intelligent Content Management platform brings Box AI and e-signatures to
  your content.
