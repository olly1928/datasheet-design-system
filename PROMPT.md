# The prompt

Two things go into ChatGPT: **one file to attach**, and **one prompt to paste**. Do the
attachment once; the prompt is the same every time.

---

## 1. Attach the builder

Download **`dist/box-datasheet-builder.py`** from this repo and attach it to your Custom
GPT (*Configure → Knowledge*) or Project (*Files*). Attach it once and forget it.

That single file carries the whole design system — the template, the page-fit
validator, and the closed list of compliance credentials. It exists because ChatGPT's
GitHub connector and its Code Interpreter are separate: the connector can *read* this
repo, but the sandbox that runs Python cannot see it. Without the attachment, ChatGPT
has to retype a 32KB HTML template into the sandbox before it can build anything —
about 16k tokens a sheet, and a template retyped by a language model is exactly the
layout drift this repo exists to prevent.

With it attached, the model never touches the design at all. It writes the content and
runs one command.

> Re-download it whenever the template or the credential list changes. Everything else
> you maintain by hand — the disclaimer wording, the voice guide, the boilerplate
> figures, the Box folder ID — stays live in the repo and needs **no** re-download.

## 2. Paste the prompt

Use it as the instructions for a Custom GPT / Project if you want it permanently, or
paste it at the top of a normal chat.

```
You generate Box customer data sheets from a design system held in GitHub.

Repo:  olly1928/datasheet-design-system

Before doing anything else, read AGENT.md in that repo and follow it exactly.
It is the operating contract, and it will send you to the other files you need.
Do not read anything it does not name, and never read the reference/ folder.

Three things that override any instinct to be quick or helpful:

1. NEVER generate a sheet on the first turn. Read my brief, look at the approved
   logos, then print a SHEET PLAN and STOP. I approve or amend it before you
   write a single file. If my brief looks complete, that is not permission to
   skip this.

2. Logos come only from my Box approved-logos folder, through the Box connector.
   The folder is identified in config.json in the repo. Never take a logo from
   anywhere else, and never typeset a company name in SVG and pass it off as a
   logo — the build rejects that. If you cannot reach the folder, say so and ask
   me to name the companies I want shown.

3. Never invent a number, customer name, quote or claim. Where you do not have a
   fact, write a bracketed placeholder like [METRIC — SOURCE REQUIRED] and list
   every one of them in your plan, so I can see what is coming.

When I approve the plan: write <customer-slug>.json, then build it with the
box-datasheet-builder.py file attached to this project:

    python3 box-datasheet-builder.py <customer-slug>.json

Do not rebuild or retype the template — it is inside that file. Give me the HTML
it produces. If I amended anything, take my amendment as final and build — do
not propose again.
```

---

## What happens next

You say: *"Make a data sheet for Acme Corp — retail bank, we talked about claims
intake, they're on SharePoint and Dropbox today."*

ChatGPT reads the repo, lists your Box logos folder, and comes back with a **sheet
plan**: the angle, the headline, the block outline for both pages, which peer logos it
wants to use **and why it picked each one**, and a list of everything it will leave as
a placeholder for you to fill.

You reply `go`, or `swap Aviva for Zurich and lead on retention instead`.

Then it builds and hands you an HTML file. Open it and print — **margins None,
"Background graphics" ON** — and you have your PDF. Sheets are **A4** unless the
content file says `"size": "letter"`.

## Before the first run

Four things need filling in. All four are marked in the files themselves, so nothing
goes out silently unfinished — and none of them requires re-downloading the builder.

| What | Where | Why it matters |
|---|---|---|
| **The Box folder ID** | `config.json` | Without it the agent has to ask you for logo names every time |
| **Legal's disclaimer wording** | `legal/disclaimer.md` | Currently shows `[LEGAL TO SUPPLY FINAL WORDING]` on the page |
| **The real Box voice guide** | `brand/VOICE.md` | Currently reverse-engineered from your ICM sheet, not the official guide |
| **Check the boilerplate figures** | `brand/SNIPPETS.md` | Customer counts and analyst awards are quoted on every sheet and go stale |

The last one is easy to miss: `SNIPPETS.md` holds "120K+ customers", "66% of the
Fortune 500", and the 2024/Q1-2025 analyst awards. Those appear on every sheet you
generate, so they are worth a glance now and a diary note later.

One more worth a look before a sheet goes to a customer: `brand/compliance.json` was
compiled from web search rather than from box.com, and it says so. Confirm it against
**box.com/trust** and **box.com/zones**.
