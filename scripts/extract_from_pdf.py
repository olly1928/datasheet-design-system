#!/usr/bin/env python3
"""Cut a graphic out of a Box PDF and key its flat background to transparency.

Many Box PDFs are exported as one full-page raster per page. That makes them a
usable source for product screenshots, diagrams and illustrations when box.com
is not reachable - the Frasers product screenshot came out of a PDF this way.

    # what rasters does this PDF hold?
    python3 scripts/extract_from_pdf.py brief.pdf --list

    # where is the ink in a region? (CSS px, page assumed 816 wide)
    python3 scripts/extract_from_pdf.py brief.pdf --page 1 \
            --detect 556,690,816,1010

    # cut one out, keying the panel colour to alpha
    python3 scripts/extract_from_pdf.py brief.pdf --page 1 \
            --box 643,781,718,809 --bg F5F6F8 --out assets/graphic.png

Coordinates are CSS pixels on a 96dpi page (Letter is 816x1056), matching the
numbers used everywhere else in this repo. stdlib only.
"""
import argparse, re, struct, sys, zlib
from pathlib import Path

# ---------- PDF: pull out the full-page rasters ------------------------------
def page_rasters(pdf_bytes, min_w=1200, min_h=1600):
    """Full-page DeviceRGB images, in the order they appear in the file.

    That order is normally page order. It is not guaranteed by the format, so
    --list prints a sample pixel from each to tell them apart.
    """
    out = []
    for m in re.finditer(rb"/Subtype\s*/Image", pdf_bytes):
        start = pdf_bytes.rfind(b" obj", 0, m.start())
        strm = pdf_bytes.find(b"stream", m.end())
        if start < 0 or strm < 0:
            continue
        hdr = pdf_bytes[start:strm]
        W = re.search(rb"/Width\s+(\d+)", hdr)
        H = re.search(rb"/Height\s+(\d+)", hdr)
        CS = re.search(rb"/ColorSpace\s*/(\w+)", hdr)
        FL = re.search(rb"/Filter\s*/(\w+)", hdr)
        if not (W and H):
            continue
        w, h = int(W.group(1)), int(H.group(1))
        if w < min_w or h < min_h:
            continue
        if (CS.group(1).decode() if CS else "") != "DeviceRGB":
            continue
        if (FL.group(1).decode() if FL else "") != "FlateDecode":
            continue
        s = pdf_bytes.find(b"\n", strm) + 1
        e = pdf_bytes.find(b"endstream", s)
        try:
            raw = zlib.decompress(pdf_bytes[s:e])
        except zlib.error:
            continue
        if len(raw) != w * h * 3:
            continue
        out.append((w, h, raw))
    return out

def px(buf, w, x, y):
    o = (y * w + x) * 3
    return buf[o], buf[o + 1], buf[o + 2]

# ---------- PNG out ----------------------------------------------------------
def _chunk(tag, data):
    return (struct.pack(">I", len(data)) + tag + data
            + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF))

def write_png(path, w, h, pixels, alpha):
    n = 4 if alpha else 3
    raw = bytearray()
    for y in range(h):
        raw.append(0)
        raw += pixels[y * w * n:(y + 1) * w * n]
    png = (b"\x89PNG\r\n\x1a\n"
           + _chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 6 if alpha else 2, 0, 0, 0))
           + _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
           + _chunk(b"IEND", b""))
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_bytes(png)
    return len(png)

# ---------- the interesting bit: keying a flat background to alpha -----------
def crop_and_key(buf, w, box_px, bg, tol, soft, step):
    """Crop, and turn a flat background into transparency.

    Alpha comes from Chebyshev distance to the background colour, so a soft
    anti-aliased edge stays soft. Each surviving pixel is then un-premultiplied
    away from the background, which is what stops dark marks picking up a pale
    halo when they later sit on a different ground.
    """
    x0, y0, x1, y1 = box_px
    ow, oh = (x1 - x0) // step, (y1 - y0) // step
    out = bytearray(ow * oh * 4)
    for yy in range(oh):
        sy = y0 + yy * step
        for xx in range(ow):
            sx = x0 + xx * step
            if step == 2:                       # 2x2 box average
                r = g = b = 0
                for dy in (0, 1):
                    for dx in (0, 1):
                        o = ((sy + dy) * w + sx + dx) * 3
                        r += buf[o]; g += buf[o + 1]; b += buf[o + 2]
                r //= 4; g //= 4; b //= 4
            else:
                r, g, b = px(buf, w, sx, sy)
            q = (yy * ow + xx) * 4
            if bg is None:
                out[q:q + 4] = bytes((r, g, b, 255))
                continue
            dist = max(abs(r - bg[0]), abs(g - bg[1]), abs(b - bg[2]))
            a = 0 if dist < tol else min(255, int(dist * 255 / soft))
            if a:
                out[q]     = max(0, min(255, bg[0] + (r - bg[0]) * 255 // a))
                out[q + 1] = max(0, min(255, bg[1] + (g - bg[1]) * 255 // a))
                out[q + 2] = max(0, min(255, bg[2] + (b - bg[2]) * 255 // a))
            out[q + 3] = a
    return ow, oh, out

def detect(buf, w, box_px, thresh, min_run):
    """Report horizontal bands of ink, so a box can be found rather than guessed."""
    x0, y0, x1, y1 = box_px
    rows = []
    for y in range(y0, y1):
        n = sum(1 for x in range(x0, x1, 2) if sum(px(buf, w, x, y)) < thresh)
        rows.append(n > 1)
    bands, s = [], None
    for i, v in enumerate(rows):
        if v and s is None:
            s = i
        elif not v and s is not None:
            if i - s >= min_run:
                bands.append((y0 + s, y0 + i))
            s = None
    if s is not None and len(rows) - s >= min_run:
        bands.append((y0 + s, y1))
    spans = []
    for a, b in bands:
        lo, hi = x1, x0
        for y in range(a, b):
            for x in range(x0, x1):
                if sum(px(buf, w, x, y)) < thresh:
                    lo = min(lo, x); hi = max(hi, x)
        spans.append((lo, a, hi, b))
    return spans

def parse_box(s):
    v = [float(p) for p in s.replace(" ", "").split(",")]
    if len(v) != 4:
        raise argparse.ArgumentTypeError("expected x0,y0,x1,y1")
    return v

def parse_hex(s):
    s = s.lstrip("#")
    if len(s) != 6:
        raise argparse.ArgumentTypeError("expected RRGGBB")
    return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4))

def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pdf")
    ap.add_argument("--list", action="store_true", help="show the rasters this PDF holds")
    ap.add_argument("--page", type=int, default=1, help="1-based, in file order")
    ap.add_argument("--detect", type=parse_box, metavar="X0,Y0,X1,Y1",
                    help="report ink bands in this region")
    ap.add_argument("--box", type=parse_box, metavar="X0,Y0,X1,Y1", help="region to cut")
    ap.add_argument("--bg", type=parse_hex, metavar="RRGGBB",
                    help="background colour to key to transparency; omit to keep opaque")
    ap.add_argument("--out", help="destination PNG")
    ap.add_argument("--pad", type=float, default=6, help="CSS px of margin around --box")
    ap.add_argument("--tol", type=int, default=8, help="distance below which a pixel is background")
    ap.add_argument("--soft", type=int, default=70, help="distance at which a pixel is fully opaque")
    ap.add_argument("--page-width", type=float, default=816, help="page width in CSS px")
    ap.add_argument("--full-res", action="store_true", help="skip the 2x downsample")
    a = ap.parse_args()

    data = Path(a.pdf).read_bytes()
    rasters = page_rasters(data)
    if not rasters:
        print("no full-page RGB rasters found — this PDF is probably vector, "
              "so there is nothing to cut out"); return 1

    if a.list:
        print(f"{len(rasters)} raster(s) in {Path(a.pdf).name}:")
        for i, (w, h, buf) in enumerate(rasters, 1):
            c = px(buf, w, w // 3, h // 40)
            print(f"  --page {i}   {w}x{h}  {w / a.page_width:.3f} px per CSS px"
                  f"   top sample #{c[0]:02X}{c[1]:02X}{c[2]:02X}")
        return 0

    if a.page < 1 or a.page > len(rasters):
        print(f"--page {a.page} out of range: this PDF has {len(rasters)}"); return 1
    w, h, buf = rasters[a.page - 1]
    sc = w / a.page_width

    if a.detect:
        x0, y0, x1, y1 = a.detect
        spans = detect(buf, w, (int(x0 * sc), int(y0 * sc), int(x1 * sc), int(y1 * sc)),
                       thresh=690, min_run=int(4 * sc))
        if not spans:
            print("  no ink found in that region"); return 0
        print(f"  {len(spans)} band(s) — CSS coords, ready to pass to --box:")
        for lo, t, hi, b in spans:
            print(f"    --box {lo/sc:.0f},{t/sc:.0f},{hi/sc:.0f},{b/sc:.0f}"
                  f"      ({(hi-lo)/sc:.0f}x{(b-t)/sc:.0f} CSS)")
        return 0

    if not (a.box and a.out):
        ap.print_help(); return 2

    x0, y0, x1, y1 = a.box
    box = (max(0, int((x0 - a.pad) * sc)), max(0, int((y0 - a.pad) * sc)),
           min(w, int((x1 + a.pad) * sc)), min(h, int((y1 + a.pad) * sc)))
    step = 1 if a.full_res else 2
    ow, oh, pixels = crop_and_key(buf, w, box, a.bg, a.tol, a.soft, step)
    size = write_png(a.out, ow, oh, pixels, alpha=a.bg is not None)
    if a.bg:
        clear = sum(1 for i in range(3, len(pixels), 4) if pixels[i] == 0)
        print(f"wrote {a.out}  {ow}x{oh}  {size/1024:.0f} KB  "
              f"{clear*100//(ow*oh)}% transparent")
    else:
        print(f"wrote {a.out}  {ow}x{oh}  {size/1024:.0f} KB  opaque")
    return 0

if __name__ == "__main__":
    sys.exit(main())
