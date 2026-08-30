# AI-disclosure wording

**Legal owns this file.** It is the single place the disclaimer is defined; every
generated data sheet copies the approved text below into its footer verbatim.

To change the wording on every future sheet, edit the block below. Nothing else
needs to change — not the template, not any content file.

## Approved text

> This document was generated with the assistance of AI and reviewed by Box
> personnel prior to distribution. [LEGAL TO SUPPLY FINAL WORDING]

## Status

**PLACEHOLDER — not yet approved.** The bracketed marker above is deliberate: it is
visible on the rendered page, so an unapproved sheet cannot quietly reach a customer.
Replace the whole quoted block with Legal's exact wording and delete this section.

## Constraints for whoever drafts it

The strip starts at **26px** — one line at 7.6px — and **grows to fit the wording**,
taking the extra height off page 2's content. Two lines (about 340 characters, the
schema limit) is comfortable and costs the page ~6px.

Nothing is ever clipped. It used to be: the strip was a fixed height with
`overflow:hidden`, so a disclaimer longer than about 170 characters lost its second
half silently — no error, no warning, nothing visible on the page. That is fixed, and
`scripts/validate.py` now measures the real strip height and refuses to build if the
disclosure would need more than 60px, rather than hiding the overflow.

So: **do not trim Legal's wording to fit.** Paste it in full. If it genuinely needs
more than 60px, raise `--foot-h` in `template/datasheet.html` and `FOOT_MAX` in
`scripts/validate.py` together. The wording is the constraint; the layout bends around
it.
