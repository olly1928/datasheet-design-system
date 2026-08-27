#!/usr/bin/env python3
"""Pull vector artwork out of a vector PDF and write it as SVG.

Box publishes both kinds of PDF. `extract_from_pdf.py` crops artwork out of the
raster kind; this one handles the vector kind, and is the one that gives artwork
worth hardcoding - it scales perfectly and costs a couple of KB.

    # what vector artwork sits in this region? (PDF points, origin BOTTOM-left)
    python3 scripts/extract_vector_from_pdf.py icm.pdf --detect 30,735,85,780

    # convert it
    python3 scripts/extract_vector_from_pdf.py icm.pdf \
            --region 30,735,85,780 --out assets/box-logo-white.svg

PDF points, not CSS pixels: a US Letter page is 612x792pt, and Y counts UP from
the bottom. Multiply pt by 816/612 (1.333) for CSS px. The script flips Y for you.

stdlib only.
"""
import argparse, re, sys, zlib
from pathlib import Path

# a q ... cm ... Q block: artwork placed by a translation matrix
BLOCK = re.compile(r'q\s+([\d.\-]+) ([\d.\-]+) ([\d.\-]+) ([\d.\-]+) ([\d.\-]+) ([\d.\-]+)\s+cm')

def content_streams(pdf_bytes):
    """Every decompressible stream that looks like page content."""
    out = []
    for m in re.finditer(rb"stream\r?\n", pdf_bytes):
        s = m.end()
        e = pdf_bytes.find(b"endstream", s)
        if e < 0:
            continue
        try:
            raw = zlib.decompress(pdf_bytes[s:e])
        except zlib.error:
            continue
        # real content streams carry operators, not just bytes that look like them
        if re.search(rb"\bcm\b", raw) and re.search(rb"\b(re|m)\b", raw):
            out.append(raw.decode("latin1"))
    return out

def blocks_in(streams, region):
    """Path blocks whose placement falls inside the region."""
    x0, y0, x1, y1 = region
    found = []
    for txt in streams:
        for m in BLOCK.finditer(txt):
            a, b, c, dd, tx, ty = (float(g) for g in m.groups())
            if not (x0 <= tx <= x1 and y0 <= ty <= y1):
                continue
            end = txt.find("Q", m.end())
            found.append({"tx": tx, "ty": ty, "scale": (a, b, c, dd),
                          "body": txt[m.end():end if end > 0 else None]})
    return found

def to_path(blk):
    """PDF path operators -> absolute SVG commands, in page coordinates.

    m/l take a point, c takes three, v and y take two (with an implied control
    point), h closes. Everything is offset by the block's translation.
    """
    tx, ty = blk["tx"], blk["ty"]
    toks = blk["body"].replace("\n", " ").split()
    cmds, nums, pts = [], [], []
    cur = (0.0, 0.0)

    def P(i):
        x, y = nums[i] + tx, nums[i + 1] + ty
        pts.append((x, y))
        return x, y

    for t in toks:
        try:
            nums.append(float(t))
            continue
        except ValueError:
            pass
        if t == "m" and len(nums) >= 2:
            cur = P(len(nums) - 2); cmds.append(("M", [cur]))
        elif t == "l" and len(nums) >= 2:
            cur = P(len(nums) - 2); cmds.append(("L", [cur]))
        elif t == "c" and len(nums) >= 6:
            i = len(nums) - 6
            a, b, c = P(i), P(i + 2), P(i + 4)
            cmds.append(("C", [a, b, c])); cur = c
        elif t == "v" and len(nums) >= 4:      # first control point = current
            i = len(nums) - 4
            b, c = P(i), P(i + 2)
            cmds.append(("C", [cur, b, c])); cur = c
        elif t == "y" and len(nums) >= 4:      # second control point = endpoint
            i = len(nums) - 4
            a, c = P(i), P(i + 2)
            cmds.append(("C", [a, c, c])); cur = c
        elif t == "h":
            cmds.append(("Z", []))
        nums = []
    return cmds, pts

def render(all_cmds, bbox, precision=3):
    x0, y0, x1, y1 = bbox
    def fmt(p):
        # PDF Y counts up, SVG counts down: flip about the bounding box
        return f"{p[0]-x0:.{precision}f},{y1-p[1]:.{precision}f}"
    out = []
    for cmds in all_cmds:
        d = "".join(c if c == "Z" else c + " ".join(fmt(p) for p in ps)
                    for c, ps in cmds)
        out.append(d)
    return out

def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pdf")
    ap.add_argument("--detect", metavar="X0,Y0,X1,Y1", help="report artwork in this region")
    ap.add_argument("--region", metavar="X0,Y0,X1,Y1", help="region to convert")
    ap.add_argument("--out", help="destination SVG")
    ap.add_argument("--fill", default="currentColor",
                    help="fill for the paths (default currentColor, so CSS can recolour it)")
    ap.add_argument("--label", default="", help="aria-label for the SVG")
    a = ap.parse_args()

    data = Path(a.pdf).read_bytes()
    streams = content_streams(data)
    if not streams:
        print("no vector content streams found — this PDF is probably a raster export; "
              "use scripts/extract_from_pdf.py instead")
        return 1

    spec = a.detect or a.region
    if not spec:
        ap.print_help(); return 2
    try:
        region = [float(v) for v in spec.replace(" ", "").split(",")]
        assert len(region) == 4
    except Exception:
        print("region must be X0,Y0,X1,Y1 in PDF points"); return 2

    found = blocks_in(streams, region)
    if not found:
        print(f"  no vector artwork placed in {region}")
        return 0

    parsed = [to_path(b) for b in found]
    allpts = [p for _, pts in parsed for p in pts]
    if not allpts:
        print("  found blocks but no path geometry in them"); return 1
    xs = [p[0] for p in allpts]; ys = [p[1] for p in allpts]
    bbox = (min(xs), min(ys), max(xs), max(ys))
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]

    if a.detect:
        print(f"  {len(found)} path block(s) in {region}:")
        for b, (cmds, _) in zip(found, parsed):
            nc = sum(1 for c, _ in cmds if c == "C")
            nm = sum(1 for c, _ in cmds if c == "M")
            print(f"    placed at ({b['tx']:.2f}, {b['ty']:.2f})  "
                  f"{nc} curves, {nm} subpaths")
        print(f"  combined bbox  x {bbox[0]:.2f}..{bbox[2]:.2f}  y {bbox[1]:.2f}..{bbox[3]:.2f}")
        print(f"  size {w:.2f} x {h:.2f} pt   ({w*4/3:.1f} x {h*4/3:.1f} CSS px)")
        print(f"\n  convert it:  --region {spec} --out artwork.svg")
        return 0

    if not a.out:
        print("--region needs --out"); return 2
    paths = render([c for c, _ in parsed], bbox)
    label = f' role="img" aria-label="{a.label}"' if a.label else ' aria-hidden="true"'
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:.2f} {h:.2f}"'
           f'{label} fill="{a.fill}">'
           + "".join(f'<path d="{d}"/>' for d in paths) + "</svg>")
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(svg, encoding="utf-8")
    print(f"wrote {a.out}  viewBox 0 0 {w:.2f} {h:.2f}  {len(svg):,} bytes  "
          f"{len(paths)} path(s)")
    return 0

if __name__ == "__main__":
    sys.exit(main())
