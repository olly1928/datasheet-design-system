#!/usr/bin/env python3
"""Pre-render checks: character budgets and page-height arithmetic.

Runs before anything is drawn, using only the content JSON, so a sheet that
cannot fit - or one so short it will read empty - is caught before it reaches a
customer. The template does a second, real measurement in the browser and paints
a red rule if content still overflows.

stdlib only, so it runs in any Python sandbox.
"""
import json, math, re, struct, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# ---- page geometry, mirroring template/datasheet.html -----------------------
GEO = {
    "letter": {"ph": 1056, "band": 219, "foot": 26, "main_w": 478, "aside_w": 193},
    "a4":     {"ph": 1123, "band": 219, "foot": 26, "main_w": 462, "aside_w": 187},
}
PAD = 54           # main/aside top+bottom padding
BLOCK_GAP = 26     # --s5, the gap between blocks in a column
# Per-block estimates land within about +/-4% of a real render. The hard failure
# sits at 100%; aim for <=95% so a sheet keeps slack for font fallback. The
# template's own overflow rule, drawn in the browser, is the final word.
FILL_MIN = 0.72
FILL_MAX = 1.00

LIMITS = {
    "meta.title": 74, "meta.standfirst": 110, "meta.eyebrow": 28,
    "hero.headline": 66, "hero.deck": 130,
    "steps.item.title": 42, "steps.item.body": 120,
    "deflist.item.term": 30, "deflist.item.body": 90,
    "featurelist.item.title": 34, "featurelist.item.body": 120,
    "caps.item.title": 38, "caps.item.body": 190, "caps.item.listitem": 44,
    "cards.item.title": 52, "cards.item.para": 190,
    "quote.text": 210, "statlist.item.value": 8, "statlist.item.label": 70,
    "stats.item.value": 8, "stats.item.label": 62,
    "panel.heading": 62, "figure.caption": 120, "learnmore.text": 90,
    "cta.heading": 58, "cta.body": 150,
    "bullets.item": 150, "linklist.body": 110, "note.text": 200,
    "pills.item": 30, "label": 26, "legal": 340,
}

# ---- text metrics -----------------------------------------------------------
# Inter's mean advance per character, as a fraction of em. Semibold is
# measurably wider than regular, so the two cannot share one constant.
ADVANCE = 0.50
ADVANCE_BOLD = 0.545

def strip_md(text):
    """Count what renders, not what is typed: **bold** markers and the URL half
    of [label](url) never reach the page."""
    t = str(text or "")
    t = re.sub(r"\[(.+?)\]\((.+?)\)", r"\1", t)
    return t.replace("**", "")

def lines(text, width, size=12.4, bold=False):
    """Line count for a run of copy at a column width."""
    if not text:
        return 0
    cpl = max(1, width / ((ADVANCE_BOLD if bold else ADVANCE) * size))
    return max(1, math.ceil(len(strip_md(text)) / cpl))

def img_size(src):
    """Real pixel size of an asset, so a figure is estimated rather than guessed."""
    if not src or src.startswith(("data:", "http")):
        return None
    for d in (ROOT / "assets", ROOT / "assets" / "logos"):
        f = d / src
        if not f.is_file():
            continue
        b = f.read_bytes()
        if b[:8] == b"\x89PNG\r\n\x1a\n":
            w, h = struct.unpack(">II", b[16:24]); return w, h
        if b[:2] == b"\xff\xd8":                       # JPEG
            i = 2
            while i < len(b) - 9:
                if b[i] != 0xFF: i += 1; continue
                m = b[i + 1]
                if m in (0xC0, 0xC1, 0xC2):
                    h, w = struct.unpack(">HH", b[i + 5:i + 9]); return w, h
                i += 2 + struct.unpack(">H", b[i + 2:i + 4])[0]
    return None

def _paras(b):
    return [p for p in (b.get("paragraphs") or [b.get("body") or b.get("text")]) if p]

# ---- per-block height estimates --------------------------------------------
def est(b, w):
    t = b.get("type")
    h = 25 if b.get("label") else 0

    if t == "rule":
        return 1
    if t == "hero":
        h += lines(b.get("headline"), w, 34, bold=True) * 38.4 + 16
        h += lines(b.get("deck"), w, 17, bold=True) * 22.4
        return h
    if b.get("heading"):
        h += 48 if t in ("featurelist", "caps", "cards", "stats", "cta") or b.get("level") == 2 else 34
        if t == "section" and b.get("level") != 3:
            h = h - 34 + 48 if b.get("level") is None else h

    if t in ("text", "section"):
        ps = _paras(b)
        h += sum(lines(p, w) * 18.85 for p in ps) + 12 * max(0, len(ps) - 1)
    elif t == "steps":
        items = b.get("items", [])
        cols = min(3, max(1, len(items)))
        cw = (w - 16 * (cols - 1)) / cols
        tall = 0
        for i in items:
            ih = 21 + 11 + lines(i.get("title"), cw, 12.4, bold=True) * 16.1 + 8 + lines(i.get("body"), cw) * 18.6
            tall = max(tall, ih)
        h += tall
    elif t == "deflist":
        items = b.get("items", [])
        for i in items:
            h += lines(f"{i.get('term','')}: {i.get('body','')}", w) * 18
        h += 11 * max(0, len(items) - 1)
    elif t == "featurelist":
        items = b.get("items", [])
        cols = 1 if b.get("columns") == 1 else 2
        cw = (w - 16 * (cols - 1)) / cols - 30
        rows = [items[i:i + cols] for i in range(0, len(items), cols)]
        for r in rows:
            h += max(16 + 3 + lines(i.get("body"), cw) * 18.4 for i in r) + 22
        h -= 22 if rows else 0
    elif t == "caps":
        items = b.get("items", [])
        cols = b.get("columns", 3)
        cw = (w - 16 * (cols - 1)) / cols
        rows = [items[i:i + cols] for i in range(0, len(items), cols)]
        for r in rows:
            tall = 0
            for i in r:
                # the icon sits inline, so the title wraps in a narrower box
                hd = max(32, lines(i.get("title"), cw - 21, 12.4, bold=True) * 15.5)
                ih = hd + 7 + lines(i.get("body"), cw, 12) * 17.8
                if i.get("list"): ih += 12 + len(i["list"]) * 18.9
                tall = max(tall, ih)
            h += tall + 22
        h -= 22 if rows else 0
    elif t == "cards":
        items = b.get("items", [])
        cols = 1 if len(items) == 1 else 2
        cw = (w - 16 * (cols - 1)) / cols - 32
        rows = [items[i:i + cols] for i in range(0, len(items), cols)]
        for r in rows:
            tall = 0
            for i in r:
                ps = _paras(i)
                # .card is a flex column with a 10px gap between every child
                ih = 22                                              # icon
                ih += lines(i.get("title"), cw, 12.4, bold=True) * 16.1
                ih += sum(lines(p, cw, 11.8) * 17.5 for p in ps)
                ih += 10 * (1 + len(ps))                             # gaps
                tall = max(tall, ih + 44)                            # padding
            h += tall + 16
        h -= 16 if rows else 0
    elif t == "panel":
        inner = w - 44
        h += 44
        ps = _paras(b)
        h += sum(lines(p, inner) * 18.85 for p in ps) + 12 * max(0, len(ps) - 1)
        if b.get("logos"): h += 22 + 22
    elif t == "figure":
        dim = img_size((b.get("image") or {}).get("src"))
        ratio = (dim[1] / dim[0]) if dim else 0.47
        fw = w * (min(100, float(b.get("width", 100))) / 100)
        h += fw * ratio + (10 + lines(b.get("caption"), w, 10.6) * 15.4 if b.get("caption") else 0)
    elif t == "learnmore":
        h += lines(b.get("text"), w) * 18.85
    elif t == "quote":
        h += lines(b.get("text"), w, 14.5, bold=True) * 20 + 11 + 32
    elif t == "statlist":
        items = b.get("items", [])
        for i in items: h += 27 + 6 + lines(i.get("label"), w) * 18
        h += 22 * max(0, len(items) - 1)
    elif t == "stats":
        h += 92
    elif t == "logostack":
        n = len(b.get("logos", []))
        h += n * 24 + BLOCK_GAP * max(0, n - 1)
    elif t == "logogrid":
        h += math.ceil(len(b.get("logos", [])) / 2) * 42
    elif t == "logobar":
        h += 34
    elif t == "pills":
        row, rows = 0.0, 1
        for i in b.get("items", []):
            txt = i.get("text") if isinstance(i, dict) else i
            pw = len(strip_md(txt)) * 11 * ADVANCE + 22 + 8
            if row + pw > w and row > 0:
                rows += 1; row = pw
            else:
                row += pw
        h += rows * 30
    elif t == "bullets":
        for i in b.get("items", []): h += lines(i, w - 12) * 18 + 10
    elif t == "linklist":
        items = b.get("items", [])
        for i in items: h += 16 + 3 + lines(i.get("body"), w - 30, 12) * 17.4
        h += 22 * max(0, len(items) - 1)
    elif t == "note":
        h += lines(b.get("text") or b.get("body"), w, 11.6) * 17.4
    elif t == "cta":
        h += 22 + lines(b.get("body"), w - 44, 12) * 17.5 + 24 + 44
    elif t == "footnote":
        h += 26
    return h

# ---- checks -----------------------------------------------------------------
def walk_limits(doc, errs):
    def chk(key, val, where):
        lim = LIMITS.get(key)
        if not (lim and val):
            return
        shown = strip_md(val)          # **bold** and link URLs never reach the page
        if len(shown) > lim:
            errs.append(f"{where}: {len(shown)} chars, limit {lim} — {shown[:52]}…")
    m = doc.get("meta", {})
    chk("meta.title", m.get("title"), "meta.title")
    chk("meta.eyebrow", m.get("eyebrow"), "meta.eyebrow")
    chk("legal", doc.get("legal"), "legal")
    for pi, page in enumerate(doc.get("pages", []), 1):
        for col in ("main", "aside"):
            for bi, b in enumerate(page.get(col, [])):
                loc = f"page {pi} {col}[{bi}] {b.get('type')}"
                t = b.get("type")
                chk("label", b.get("label"), f"{loc}.label")
                if t == "hero":
                    chk("hero.headline", b.get("headline"), f"{loc}.headline")
                    chk("hero.deck", b.get("deck"), f"{loc}.deck")
                elif t == "quote":
                    chk("quote.text", b.get("text"), f"{loc}.text")
                elif t == "panel":
                    chk("panel.heading", b.get("heading"), f"{loc}.heading")
                elif t == "figure":
                    chk("figure.caption", b.get("caption"), f"{loc}.caption")
                elif t == "learnmore":
                    chk("learnmore.text", b.get("text"), f"{loc}.text")
                elif t == "note":
                    chk("note.text", b.get("text") or b.get("body"), f"{loc}.text")
                elif t == "cta":
                    chk("cta.heading", b.get("heading"), f"{loc}.heading")
                    chk("cta.body", b.get("body"), f"{loc}.body")
                for ii, it in enumerate(b.get("items", [])):
                    at = f"{loc}.items[{ii}]"
                    if t == "steps":
                        chk("steps.item.title", it.get("title"), at + ".title")
                        chk("steps.item.body", it.get("body"), at + ".body")
                    elif t == "deflist":
                        chk("deflist.item.term", it.get("term"), at + ".term")
                        chk("deflist.item.body", it.get("body"), at + ".body")
                    elif t == "featurelist":
                        chk("featurelist.item.title", it.get("title"), at + ".title")
                        chk("featurelist.item.body", it.get("body"), at + ".body")
                    elif t == "caps":
                        chk("caps.item.title", it.get("title"), at + ".title")
                        chk("caps.item.body", it.get("body"), at + ".body")
                        for li, l in enumerate(it.get("list", [])):
                            chk("caps.item.listitem", l, at + f".list[{li}]")
                    elif t == "cards":
                        chk("cards.item.title", it.get("title"), at + ".title")
                        for pj, p in enumerate(it.get("paragraphs") or []):
                            chk("cards.item.para", p, at + f".paragraphs[{pj}]")
                    elif t == "statlist":
                        chk("statlist.item.value", it.get("value"), at + ".value")
                        chk("statlist.item.label", it.get("label"), at + ".label")
                    elif t == "stats":
                        chk("stats.item.value", it.get("value"), at + ".value")
                        chk("stats.item.label", it.get("label"), at + ".label")
                    elif t == "bullets":
                        chk("bullets.item", it, at)
                    elif t == "linklist":
                        chk("linklist.body", it.get("body"), at + ".body")
                    elif t == "pills":
                        chk("pills.item", it.get("text") if isinstance(it, dict) else it, at)

def validate(doc):
    errs, warns, report = [], [], []
    size = (doc.get("meta") or {}).get("size", "letter")
    g = GEO.get(size, GEO["letter"])
    walk_limits(doc, errs)

    if not doc.get("legal"):
        warns.append("legal: no AI-disclosure text set — the footer will render empty")

    pages = doc.get("pages", [])
    for pi, page in enumerate(pages, 1):
        # the disclosure strip sits on the last page only
        foot = g["foot"] if pi == len(pages) else 0
        avail = g["ph"] - (g["band"] if page.get("band") else 0) - foot - PAD
        for col, w in (("main", g["main_w"]), ("aside", g["aside_w"])):
            blocks = page.get(col, [])
            used = sum(est(b, w) for b in blocks) + BLOCK_GAP * max(0, len(blocks) - 1)
            fill = used / avail if avail else 0
            # a block pinned to the foot is meant to leave a gap above it, so the
            # column is deliberately anchored rather than accidentally short
            anchored = any(b.get("pin") == "bottom" for b in blocks)
            report.append(f"  page {pi} {col:5s}  {used:6.0f} / {avail} px   {fill*100:5.1f}%"
                          + ("  (anchored)" if anchored else ""))
            if fill > FILL_MAX:
                errs.append(f"page {pi} {col} overflows: ~{used:.0f}px of {avail}px "
                            f"({fill*100:.0f}%) — cut copy or drop a block")
            elif fill < FILL_MIN and not anchored:
                warns.append(f"page {pi} {col} is sparse: ~{used:.0f}px of {avail}px "
                             f"({fill*100:.0f}%) — the page will read empty; add a block")
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
