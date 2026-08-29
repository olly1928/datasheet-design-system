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

def approved_pills():
    """Every credential that may appear on a pill. brand/compliance.json is a closed
    list: the agent selects from it, so a guessed certification fails the build."""
    f = ROOT / "brand" / "compliance.json"
    if not f.is_file():
        return None
    try:
        d = json.loads(f.read_text(encoding="utf-8"))
    except Exception:
        return None
    return {z["label"] for z in d.get("residencyZones", [])} | \
           {c["label"] for c in d.get("certifications", [])}

def approved_assurances():
    """Pre-approved assurance wording, keyed by title. Same closed-list rule as pills:
    these are claims about the product, so the agent picks rather than composes."""
    f = ROOT / "brand" / "compliance.json"
    if not f.is_file():
        return None
    try:
        d = json.loads(f.read_text(encoding="utf-8"))
    except Exception:
        return None
    return {a["title"]: a["body"] for a in d.get("assurances", [])}

# ---- what the template can actually render ----------------------------------
# Mirrors template/content.schema.json's block enum and the <symbol id="i-..."> set
# in template/datasheet.html. `validate.py --selfcheck` proves these still agree, so
# they cannot drift apart silently.
BLOCK_TYPES = {
    "hero", "text", "section", "rule", "steps", "deflist", "featurelist", "caps",
    "cards", "panel", "figure", "learnmore", "quote", "statlist", "stats",
    "logostack", "logogrid", "logobar", "pills", "bullets", "linklist",
    "assurances", "note", "cta", "footnote",
}
ICONS = {
    "layer", "shield", "link", "doc", "meta", "hub", "stack", "chart", "ai", "lock",
    "chat", "flow", "portal", "pen", "cloud", "check", "globe", "people", "bulb",
    "help", "edu",
}
PILL_TONES = {"blue", "green", "plain"}
LOGO_TIERS = {"white", "reverse", "plate", "wordmark", "none"}
LOGO_ASPECTS = {"wordmark", "mark", "stacked"}

# ---- page geometry, mirroring template/datasheet.html -----------------------
# A4 is the default page size; "letter" is the override. pw is carried so the
# disclosure strip can be measured rather than assumed.
GEO = {
    "a4":     {"pw": 794, "ph": 1123, "band": 219, "main_w": 462, "aside_w": 187},
    "letter": {"pw": 816, "ph": 1056, "band": 219, "main_w": 478, "aside_w": 193},
}
DEFAULT_SIZE = "a4"
FOOT_MIN = 26      # --foot-h: the strip's minimum height
FOOT_MAX = 60      # past this the disclosure is eating page-2 content
FOOT_PAD = 11      # 5px top + 5px bottom + 1px top border
PAD = 54           # main/aside top+bottom padding
BLOCK_GAP = 26     # --s5, the gap between blocks in a column
# Estimates are deliberately conservative: measured against real Chromium renders
# they run 0-6% OVER, never under, so a column that passes here fits on the page.
# The hard failure sits at 100%; aim for <=95% so a sheet keeps slack for font
# fallback. The template's own overflow rule, drawn in the browser, is the final word.
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
    """Line count for a run of copy at a column width.

    Wraps word by word rather than dividing characters by a chars-per-line figure.
    Text wraps on spaces, so a line almost never fills to its last pixel, and in a
    narrow column that ragged edge is worth a whole extra line - the page-1 sidebar
    quote came out a line short under the old arithmetic."""
    if not text:
        return 0
    adv = (ADVANCE_BOLD if bold else ADVANCE) * size
    words = strip_md(text).split()
    if not words:
        return 0
    n, cur = 1, 0.0
    for w in words:
        ww = len(w) * adv
        if cur and cur + adv + ww > width:      # adv doubles as the space width
            n, cur = n + 1, ww
        else:
            cur += (adv if cur else 0) + ww
    return n

def img_size(src):
    """Real pixel size of an asset, so a figure is estimated rather than guessed.

    Handles a data URI (assets are inlined before validation) and a plain
    filename. A live http(s) URL cannot be measured - declare "aspect" on the
    figure instead."""
    if not src:
        return None
    if src.startswith("data:"):
        import base64 as _b64
        try:
            head, b64 = src.split(",", 1)
            b = _b64.b64decode(b64[:64], validate=False)
        except Exception:
            return None
        if b[:8] == b"\x89PNG\r\n\x1a\n":
            w, h = struct.unpack(">II", b[16:24]); return w, h
        if b[:2] == b"\xff\xd8":
            return None
        return None
    if src.startswith("http"):
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

def foot_height(doc, g):
    """Real height of the AI-disclosure strip, from the wording it has to carry.

    The strip used to be a fixed 26px with the text clipped to one line, so half
    of a long disclosure vanished silently. It now grows instead, which means the
    page-fit arithmetic has to know how tall it actually is."""
    legal = (doc.get("legal") or "").strip()
    if not legal:
        return FOOT_MIN
    meta = str((doc.get("meta") or {}).get("footerMeta") or "box.com")
    # page width less both margins, the flex gap, and the right-hand meta label
    w = g["pw"] - 2 * 48 - 16 - len(meta) * 7.6 * ADVANCE
    n = lines(legal, max(1, w), 7.6)
    return max(FOOT_MIN, math.ceil(n * 7.6 * 1.35 + FOOT_PAD))

# ---- per-block height estimates --------------------------------------------
def est(b, w):
    t = b.get("type")
    h = 25 if b.get("label") else 0

    if t == "rule":
        return 1
    if t == "hero":
        h += lines(b.get("headline"), w, 31, bold=True) * 35.7 + 16
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
        cols = 2 if len(items) == 2 else 3      # mirrors .steps / .steps--2
        cw = (w - 16 * (cols - 1)) / cols
        rows = [items[i:i + cols] for i in range(0, len(items), cols)]
        for r in rows:
            tall = 0
            for i in r:
                ih = 21 + 11 + lines(i.get("title"), cw, 12.4, bold=True) * 16.1 + 8 + lines(i.get("body"), cw) * 18.6
                tall = max(tall, ih)
            h += tall + 16
        h -= 16 if rows else 0
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
        cols = 2 if b.get("columns") == 2 else 3   # mirrors .caps / .caps--2
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
        if dim:
            ratio = dim[1] / dim[0]
        elif b.get("aspect"):
            ratio = 1 / float(b["aspect"])          # aspect is width:height
        else:
            ratio = 0.47
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
        items = b.get("items", [])
        cols = 2 if len(items) == 2 else 3      # mirrors .stats / .stats--2
        cw = (w - 16 * (cols - 1)) / cols - 32  # .stat-tile padding
        rows = [items[i:i + cols] for i in range(0, len(items), cols)]
        for r in rows:
            h += max(32 + 27 + 6 + lines(i.get("label"), cw, 11) * 16 for i in r) + 16
        h -= 16 if rows else 0
    elif t == "logostack":
        # .logostack images are capped at max-height:34px and most marks hit that
        # cap; only a very wide wordmark comes out shorter. 34 is the real ceiling,
        # so use it rather than guessing at an average.
        n = len(b.get("logos", []))
        h += n * 34 + BLOCK_GAP * max(0, n - 1)
    elif t == "logogrid":
        h += math.ceil(len(b.get("logos", [])) / 2) * 42
    elif t == "logobar":
        n = len(b.get("logos", []))
        per = 70 + 22                           # a 22px-tall wordmark plus the flex gap
        per_row = max(1, int((w + 22) // per))
        rows = max(1, math.ceil(n / per_row))
        h += rows * 22 + 22 * (rows - 1)
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
    elif t in ("linklist", "assurances"):
        items = b.get("items", [])
        for i in items:
            h += lines(i.get("title"), w - 30, 12.4, bold=True) * 14 + 3 \
                 + lines(i.get("body"), w - 30, 12) * 17.4
        h += 22 * max(0, len(items) - 1)
    elif t == "note":
        h += lines(b.get("text") or b.get("body"), w, 11.6) * 17.4
    elif t == "cta":
        h += 22 + lines(b.get("body"), w - 44, 12) * 17.5 + 24 + 44
    elif t == "footnote":
        items = [i for i in (b.get("items") or [b.get("text")]) if i]
        h += 13 + sum(lines(i, w, 9) * 13.5 for i in items)     # 12px padding + 1px rule
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

TYPESET = re.compile(r"<text\b", re.I)

def check_logo_assets(doc, errs):
    """A company name typeset in SVG is not that company's logo.

    brand/LOGO-RULES.md forbids fabricating a mark, and tier 4 ("wordmark") exists so
    nobody has to. But an inline <svg><text>ACME</text></svg> satisfies every other
    check while looking, to a reader, like a real logo that has been approved. Both
    worked examples used to do exactly this, so it is what a model copies. Catch it."""
    def scan(node, where):
        if isinstance(node, list):
            for i, v in enumerate(node):
                scan(v, f"{where}[{i}]")
            return
        if not isinstance(node, dict):
            return
        svg = node.get("svg")
        if isinstance(svg, str) and TYPESET.search(svg):
            errs.append(
                f"{where}: the inline SVG is a typeset name, not a logo — "
                f"use {{\"tier\": \"wordmark\", \"name\": \"…\"}} for the customer, or a real "
                f"approved asset from the Box folder. See brand/LOGO-RULES.md")
        for k, v in node.items():
            if isinstance(v, (dict, list)):
                scan(v, f"{where}.{k}" if where else k)
    L = doc.get("logo")
    if isinstance(L, dict):
        if L.get("tier") and L["tier"] not in LOGO_TIERS:
            errs.append(f"logo.tier: \"{L['tier']}\" is not one of {sorted(LOGO_TIERS)}")
        if L.get("aspect") and L["aspect"] not in LOGO_ASPECTS:
            errs.append(f"logo.aspect: \"{L['aspect']}\" is not one of {sorted(LOGO_ASPECTS)}")
        scan(L, "logo")
    for pi, page in enumerate(doc.get("pages", []), 1):
        for col in ("main", "aside"):
            for bi, b in enumerate(page.get(col, [])):
                scan(b.get("logos"), f"page {pi} {col}[{bi}].logos")
                scan(b.get("image"), f"page {pi} {col}[{bi}].image")

def check_renderable(doc, errs):
    """Every block type, icon and pill tone must be one the template can draw.

    An unknown block type renders a red "Unknown block type" line straight onto the
    customer's sheet; an unknown icon renders a silent empty gap. Neither used to be
    caught before the file was built."""
    for pi, page in enumerate(doc.get("pages", []), 1):
        for col in ("main", "aside"):
            for bi, b in enumerate(page.get(col, [])):
                loc = f"page {pi} {col}[{bi}]"
                t = b.get("type")
                if t not in BLOCK_TYPES:
                    errs.append(f"{loc}: unknown block type \"{t}\" — it would render as a "
                                f"red error line on the sheet. Pick from: "
                                f"{', '.join(sorted(BLOCK_TYPES))}")
                    continue
                for ii, it in enumerate(b.get("items", []) or []):
                    if not isinstance(it, dict):
                        continue
                    ic = it.get("icon")
                    if ic is not None and ic not in ICONS:
                        errs.append(f"{loc}.items[{ii}].icon: \"{ic}\" is not in the icon set "
                                    f"— it renders as a blank gap. Pick the nearest of: "
                                    f"{', '.join(sorted(ICONS))}")
                    if t == "pills":
                        tone = it.get("tone")
                        if tone is not None and tone not in PILL_TONES:
                            errs.append(f"{loc}.items[{ii}].tone: \"{tone}\" is not one of "
                                        f"{sorted(PILL_TONES)} — the pill renders unstyled")

def validate(doc):
    errs, warns, report = [], [], []
    size = (doc.get("meta") or {}).get("size") or DEFAULT_SIZE
    g = GEO.get(size, GEO[DEFAULT_SIZE])
    check_renderable(doc, errs)
    check_logo_assets(doc, errs)
    fh = foot_height(doc, g)
    if fh > FOOT_MAX:
        errs.append(f"legal: the disclosure needs a {fh}px footer strip (max {FOOT_MAX}px) "
                    f"— it would eat page-2 content. Shorten it with Legal, or raise "
                    f"--foot-h and FOOT_MAX together")
    walk_limits(doc, errs)

    if not doc.get("legal"):
        warns.append("legal: no AI-disclosure text set — the footer will render empty")

    allowed = approved_pills()
    if allowed is None:
        warns.append("brand/compliance.json missing or unreadable — pills not checked")
    else:
        for pi, page in enumerate(doc.get("pages", []), 1):
            for col in ("main", "aside"):
                for b in page.get(col, []):
                    if b.get("type") != "pills":
                        continue
                    for it in b.get("items", []):
                        txt = (it.get("text") if isinstance(it, dict) else it) or ""
                        if txt not in allowed:
                            errs.append(
                                f"page {pi} {col} pills: \"{txt}\" is not in "
                                f"brand/compliance.json — pick from the approved list, "
                                f"do not write your own credential")

    asr = approved_assurances()
    if asr:
        for pi, page in enumerate(doc.get("pages", []), 1):
            for col in ("main", "aside"):
                for b in page.get(col, []):
                    if b.get("type") != "assurances":
                        continue
                    for it in b.get("items", []):
                        t = it.get("title", "")
                        if t not in asr:
                            errs.append(f"page {pi} {col} assurances: \"{t}\" is not in "
                                        f"brand/compliance.json")
                        elif it.get("body", "").strip() != asr[t].strip():
                            errs.append(f"page {pi} {col} assurances: the wording for "
                                        f"\"{t}\" has been altered — use it verbatim")

    pages = doc.get("pages", [])
    for pi, page in enumerate(pages, 1):
        # the disclosure strip sits on the last page only
        foot = fh if pi == len(pages) else 0
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

def selfcheck():
    """Prove the constants above still match the template and the schema.

    validate.py mirrors values that really live in template/datasheet.html and
    template/content.schema.json. Mirrors drift. This is the check that says so
    out loud instead of letting a sheet be measured against stale geometry."""
    bad = []
    tpl = (ROOT / "template" / "datasheet.html").read_text(encoding="utf-8")
    sch = json.loads((ROOT / "template" / "content.schema.json").read_text(encoding="utf-8"))

    def cmp(name, mine, theirs, source):
        if set(mine) != set(theirs):
            only_mine = sorted(set(mine) - set(theirs))
            only_theirs = sorted(set(theirs) - set(mine))
            bad.append(f"{name} disagrees with {source}: "
                       f"only here {only_mine or '-'}, only there {only_theirs or '-'}")

    cmp("BLOCK_TYPES", BLOCK_TYPES, sch["$defs"]["block"]["properties"]["type"]["enum"],
        "content.schema.json")
    cmp("ICONS", ICONS, re.findall(r'<symbol id="i-([a-z0-9-]+)"', tpl),
        "the template's <symbol> set")
    cmp("PILL_TONES", PILL_TONES, re.findall(r"\.pill--([a-z]+)\{", tpl),
        "the template's .pill-- classes")
    cmp("LOGO_TIERS", LOGO_TIERS, sch["properties"]["logo"]["properties"]["tier"]["enum"],
        "content.schema.json")
    cmp("LOGO_ASPECTS", LOGO_ASPECTS, sch["properties"]["logo"]["properties"]["aspect"]["enum"],
        "content.schema.json")

    # page geometry: the CSS is the source of truth for every number in GEO
    # scope to the :root block - the html[data-size="letter"] override follows it
    root = re.search(r":root\{([^}]*)\}", tpl).group(1)
    css = dict(re.findall(r"--(pw|ph|main|aside|gutter|margin|band-h|foot-h):(\d+)px", root))
    letter = dict(re.findall(r"--(pw|ph|main|aside):(\d+)px",
                             re.search(r'html\[data-size="letter"\]\{([^}]*)\}', tpl).group(1)))
    for size, src in (("a4", css), ("letter", {**css, **letter})):
        g, pad = GEO[size], int(css["margin"]) + 22        # aside padding: --margin + --s4
        if g["pw"] != int(src["pw"]) or g["ph"] != int(src["ph"]):
            bad.append(f'GEO["{size}"] page is {g["pw"]}x{g["ph"]}, CSS says {src["pw"]}x{src["ph"]}')
        if g["main_w"] != int(src["main"]):
            bad.append(f'GEO["{size}"].main_w is {g["main_w"]}, CSS --main is {src["main"]}')
        if g["aside_w"] != int(src["aside"]) - pad:
            bad.append(f'GEO["{size}"].aside_w is {g["aside_w"]}, CSS gives {int(src["aside"]) - pad}')
        if g["band"] != int(css["band-h"]):
            bad.append(f'GEO["{size}"].band is {g["band"]}, CSS --band-h is {css["band-h"]}')
    if FOOT_MIN != int(css["foot-h"]):
        bad.append(f"FOOT_MIN is {FOOT_MIN}, CSS --foot-h is {css['foot-h']}")

    # character budgets are published in the schema; they must be the same numbers
    for k, v in sch.get("x-limits", {}).items():
        if k.startswith("_"):
            continue
        if k in LIMITS and LIMITS[k] != v:
            bad.append(f"x-limits[{k}] is {v}, LIMITS says {LIMITS[k]}")
        elif k not in LIMITS:
            bad.append(f"x-limits[{k}] has no matching entry in LIMITS")

    for b in bad:
        print(f"  \u2717 {b}")
    print(f"\nselfcheck: {'FAILED — ' + str(len(bad)) + ' mismatch(es)' if bad else 'OK'}\n")
    return 1 if bad else 0

def main():
    if "--selfcheck" in sys.argv:
        return selfcheck()
    if len(sys.argv) < 2:
        print("usage: validate.py content/<customer>.json | --selfcheck"); return 2
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
