#!/usr/bin/env python3
"""Pre-render checks: character budgets and page-height arithmetic.

Runs before anything is drawn, using only the content JSON, so a sheet that
cannot possibly fit is caught before it reaches a customer. The template does
a second, real measurement in the browser and paints a red rule if content
still overflows -- see the overflow detector in template/datasheet.html.

stdlib only, so it runs in any Python sandbox.
"""
import json, math, sys
from pathlib import Path

# ---- page geometry, mirroring template/datasheet.html -----------------------
GEO = {
    "letter": {"ph": 1056, "band": 217, "foot": 44, "main_w": 478, "aside_w": 215},
    "a4":     {"ph": 1123, "band": 217, "foot": 44, "main_w": 462, "aside_w": 209},
}
PAD = 60          # main/aside top+bottom padding
FILL_MIN = 0.72   # below this the page reads sparse -- the page-2 complaint
FILL_MAX = 1.00

# ---- character budgets ------------------------------------------------------
LIMITS = {
    "meta.title":        90,
    "meta.standfirst":  110,
    "caps.item.title":   38,
    "caps.item.body":   190,
    "caps.item.listitem":44,
    "cards.item.title":  52,
    "cards.item.para":  190,
    "quote.text":       190,
    "stats.item.value":   8,
    "stats.item.label":  62,
    "cta.heading":       58,
    "cta.body":         150,
    "bullets.item":     150,
    "linklist.body":     90,
    "legal":            340,
}

def lines(text, width_px, px_per_char=5.35):
    """Rough line count for a run of copy at a given column width."""
    if not text:
        return 0
    cpl = max(1, int(width_px / px_per_char))
    return max(1, math.ceil(len(str(text)) / cpl))

def est(block, w):
    """Estimated rendered height in px for one block at column width w."""
    t = block.get("type")
    h = 0
    if block.get("heading"):
        h += 21 + 16 if t not in ("bullets", "linklist", "logogrid", "logobar") else 19 + 12
    if t == "text":
        for p in block.get("paragraphs") or [block.get("text")]:
            if p: h += lines(p, w) * 18.5 + 12
    elif t == "section":
        for p in block.get("paragraphs", []):
            h += lines(p, w) * 18.5 + 12
    elif t == "caps":
        cols = block.get("columns", 3)
        col_w = (w - 16 * (cols - 1)) / cols
        rows = [block["items"][i:i + cols] for i in range(0, len(block.get("items", [])), cols)]
        for r in rows:
            tall = 0
            for it in r:
                ih = 21 + lines(it.get("body"), col_w, 5.1) * 17 + 6
                if it.get("list"): ih += 12 + len(it["list"]) * 17.9
                tall = max(tall, ih)
            h += tall + 24
        h -= 24 if rows else 0
    elif t == "cards":
        items = block.get("items", [])
        cols = 1 if len(items) == 1 else 2
        col_w = (w - 16 * (cols - 1)) / cols - 32
        rows = [items[i:i + cols] for i in range(0, len(items), cols)]
        for r in rows:
            tall = 0
            for it in r:
                ih = 22 + 12 + 18
                for p in (it.get("paragraphs") or [it.get("body")]):
                    if p: ih += lines(p, col_w, 5.0) * 16.4 + 12
                tall = max(tall, ih + 48)
            h += tall + 16
        h -= 16 if rows else 0
    elif t == "quote":
        h += lines(block.get("text"), w - 19, 6.4) * 20.3 + 12 + 30
    elif t == "stats":
        h += 92
    elif t == "logobar":
        h += 34
    elif t == "logogrid":
        h += math.ceil(len(block.get("logos", [])) / 2) * 42
    elif t == "bullets":
        for i in block.get("items", []):
            h += lines(i, w - 11, 5.0) * 15.9 + 12
    elif t == "linklist":
        for i in block.get("items", []):
            h += 17 + lines(i.get("body"), w, 4.9) * 15.6 + 16
    elif t == "cta":
        h += 22 + lines(block.get("body"), w - 48, 5.0) * 16.7 + 24 + 48
    elif t == "footnote":
        h += 26
    return h

def walk_limits(doc, errs):
    def chk(key, val, where):
        lim = LIMITS.get(key)
        if lim and val and len(str(val)) > lim:
            errs.append(f"{where}: {len(str(val))} chars, limit {lim} — {str(val)[:56]}…")
    m = doc.get("meta", {})
    chk("meta.title", m.get("title"), "meta.title")
    chk("meta.standfirst", m.get("standfirst"), "meta.standfirst")
    chk("legal", doc.get("legal"), "legal")
    for pi, page in enumerate(doc.get("pages", []), 1):
        for col in ("main", "aside"):
            for bi, b in enumerate(page.get(col, [])):
                loc = f"page {pi} {col}[{bi}] {b.get('type')}"
                t = b.get("type")
                for ii, it in enumerate(b.get("items", [])):
                    if t == "caps":
                        chk("caps.item.title", it.get("title"), f"{loc}.items[{ii}].title")
                        chk("caps.item.body", it.get("body"), f"{loc}.items[{ii}].body")
                        for li, l in enumerate(it.get("list", [])):
                            chk("caps.item.listitem", l, f"{loc}.items[{ii}].list[{li}]")
                    elif t == "cards":
                        chk("cards.item.title", it.get("title"), f"{loc}.items[{ii}].title")
                        for pj, p in enumerate(it.get("paragraphs") or []):
                            chk("cards.item.para", p, f"{loc}.items[{ii}].paragraphs[{pj}]")
                    elif t == "stats":
                        chk("stats.item.value", it.get("value"), f"{loc}.items[{ii}].value")
                        chk("stats.item.label", it.get("label"), f"{loc}.items[{ii}].label")
                    elif t == "bullets":
                        chk("bullets.item", it, f"{loc}.items[{ii}]")
                    elif t == "linklist":
                        chk("linklist.body", it.get("body"), f"{loc}.items[{ii}].body")
                if t == "quote": chk("quote.text", b.get("text"), f"{loc}.text")
                if t == "cta":
                    chk("cta.heading", b.get("heading"), f"{loc}.heading")
                    chk("cta.body", b.get("body"), f"{loc}.body")

def validate(doc):
    errs, warns, report = [], [], []
    size = (doc.get("meta") or {}).get("size", "letter")
    g = GEO.get(size, GEO["letter"])
    walk_limits(doc, errs)

    if not doc.get("legal"):
        warns.append("legal: no AI-disclosure text set — the footer will render empty")

    for pi, page in enumerate(doc.get("pages", []), 1):
        avail = g["ph"] - (g["band"] if page.get("band") else 0) - g["foot"] - PAD
        for col, w in (("main", g["main_w"]), ("aside", g["aside_w"])):
            blocks = page.get(col, [])
            gaps = 32 * max(0, len(blocks) - 1)
            used = sum(est(b, w) for b in blocks) + gaps
            fill = used / avail if avail else 0
            report.append(f"  page {pi} {col:5s}  {used:6.0f} / {avail} px   {fill*100:5.1f}%")
            if fill > FILL_MAX:
                errs.append(f"page {pi} {col} overflows: ~{used:.0f}px of {avail}px "
                            f"({fill*100:.0f}%) — cut copy or drop a block")
            elif fill < FILL_MIN:
                warns.append(f"page {pi} {col} is sparse: ~{used:.0f}px of {avail}px "
                             f"({fill*100:.0f}%) — the page will read empty; add a block or expand copy")
    return errs, warns, report

def main():
    if len(sys.argv) < 2:
        print("usage: validate.py content/<customer>.json"); return 2
    p = Path(sys.argv[1])
    doc = json.loads(p.read_text(encoding="utf-8"))
    errs, warns, report = validate(doc)
    print(f"\nvalidating {p.name}   ({doc.get('customer','?')})")
    print("\n".join(report))
    for w in warns: print(f"  ! {w}")
    for e in errs:  print(f"  ✗ {e}")
    if errs:
        print(f"\nFAILED — {len(errs)} error(s), {len(warns)} warning(s)\n"); return 1
    print(f"\nOK — {len(warns)} warning(s)\n"); return 0

if __name__ == "__main__":
    sys.exit(main())
