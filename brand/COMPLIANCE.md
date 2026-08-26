# Compliance and residency

The `pills` block in the page-2 sidebar. It replaces what used to say "Enterprise
Plus" — a plan name, which tells a buyer nothing — with the credentials a security or
procurement reviewer actually asks for.

**`brand/compliance.json` is the closed list.** Pick from it. Never write a credential
of your own, and never adjust a label to fit. `scripts/validate.py` fails the build if
a pill is not in that file, so a guessed certification cannot reach a customer.

---

## What to show

**One residency pill, then three to five certifications. Six pills total, maximum.**
Beyond that it stops reading as proof and starts reading as a list.

### 1. Residency — match the recipient's HQ

There are **ten zones and no more**: United Kingdom, European Union, France,
Switzerland, United States, Canada, Australia, Japan, Singapore, Israel.

Match the recipient's headquarters country to a zone using the `countries` array in
`compliance.json`:

- UK company → **UK data residency**
- German, Dutch, Spanish, Italian, Irish company → **EU data residency**
  *(there is no dedicated Germany or Netherlands zone — they are served by the EU zone)*
- French company → **France data residency**
- US company → **US data residency**

**A country that is not in any `countries` array has no zone.** Do not invent one. Route
it to EU or US, whichever is the better fit, and say which one you chose in your sheet
plan so the user can correct you. Writing "India data residency" because the customer
is Indian would be a false claim about the product.

Where the customer operates across regions, one pill for their HQ is enough. Multiple
residency pills read as hedging.

### 2. Certifications — match the sector

Start with the two that every reviewer knows, then add what the sector asks for:

| Always | `ISO 27001` · `SOC 2 Type II` |
|---|---|
| Anything EU/UK, or privacy-led | add `GDPR`, and `ISO 27018` if privacy is the theme |
| Financial services | `FINRA / SEC 17a-4`, `SOC 1 Type II` |
| Healthcare (US) | `HIPAA / HITECH` |
| Life sciences | `GxP validation` |
| Retail, hospitality, anything taking card payments | `PCI DSS` |
| US federal, state or local government | `FedRAMP High` |
| German regulated or public sector | `C5` |

**Do not show FedRAMP to a commercial buyer.** It is a US government authorisation and
means nothing to a retailer — it just spends a slot. The same discipline applies
throughout: a credential that does not speak to this reader is filler.

`ISO 27017` is worth adding when the conversation is specifically about cloud security
posture. Otherwise `ISO 27001` carries it.

---

## Two things to be careful about

**GDPR is a regulation, not a certification.** It is fine on a pill, because everyone
reads a GDPR pill as "this is handled". It is not fine in body copy to say Box is
"GDPR certified" — no such certification exists. Say "supports GDPR compliance".

**Absence is not evidence.** `compliance.json` carries a `notConfirmed` list — IRAP,
Cyber Essentials, NHS DSPT and others. Those are not there because nobody has verified
them, **not** because Box lacks them. If a customer asks about one, that is a question
for the account team, not something to assert either way.

---

## Say it in the plan

List the pills you have chosen in your sheet plan, with the reason, exactly as you do
for logos:

```
Compliance
  UK data residency      Acme is UK-headquartered
  ISO 27001              baseline, every reviewer knows it
  SOC 2 Type II          baseline
  FINRA / SEC 17a-4      they are a broker-dealer — the one that matters here
  GDPR                   UK/EU customer data
```

That is the whole point of the two-step flow: the user sees which claims are about to
go on a document with their name on it, before it goes.

---

## Keeping it current

Certification scope and zone coverage both change — three zones were added in June
2026 alone. `compliance.json` records when it was last checked and how.

**It was compiled from web search, not from box.com**, which the build environment
cannot reach. Verify against **box.com/trust** and **box.com/zones** before the first
customer-facing sheet, and re-check quarterly. Update the JSON, not this file — this
one only explains how to choose.
