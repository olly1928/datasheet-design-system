#!/usr/bin/env python3
"""Box data sheet builder - the whole design system in one file.

    python3 box-datasheet-builder.py acme.json

Writes acme-box-datasheet.html next to the JSON. Open it and print to PDF:
margins None, "Background graphics" ON. The page size comes from the sheet.

    --pdf                 also print to PDF, if a headless Chrome is available
    --compliance <file>   use a fresher credential list than the embedded one
    --force               build despite validation errors (don't)

GENERATED FILE - do not edit. It is built from the design system repo by
scripts/bundle.py, and any edit here is lost on the next build. Change the
repo and re-run the bundler.

Source revision: 18587dcd8ad1
Embedded compliance list checked: 2026-08-26
"""
import argparse, base64, json, re, subprocess, sys, tempfile, types, zlib
from pathlib import Path

def _unpack(chunks):
    return zlib.decompress(base64.b64decode("".join(chunks))).decode("utf-8")

_TEMPLATE = (
    "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"
)
_VALIDATOR = (
    "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"
)
_COMPLIANCE = (
    "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"
)

TEMPLATE = _unpack(_TEMPLATE)
COMPLIANCE = _unpack(_COMPLIANCE)

def _load_validator(compliance_text):
    """Bring validate.py up as a module, with brand/compliance.json served from
    memory instead of from disk - the bundle has no repo around it."""
    mod = types.ModuleType("validate")
    mod.__dict__["__file__"] = str(Path(__file__).resolve())
    exec(compile(_unpack(_VALIDATOR), "validate.py", "exec"), mod.__dict__)
    data = json.loads(compliance_text)
    mod.approved_pills = lambda: (
        {z["label"] for z in data.get("residencyZones", [])} |
        {c["label"] for c in data.get("certifications", [])})
    mod.approved_assurances = lambda: {a["title"]: a["body"] for a in data.get("assurances", [])}
    return mod

MARK = re.compile(r'(<script id="content" type="application/json">)(.*?)(</script>)', re.S)

def _slug(s):
    return re.sub(r"[^a-z0-9]+", "-", str(s).lower()).strip("-") or "datasheet"

def _inline_assets(node, base, seen):
    """Resolve a bare `src` filename against the JSON's own folder and inline it,
    so a sheet built in a sandbox is self-contained. A remote URL is left alone -
    the browser loads it when the sheet is opened."""
    import base64 as _b64, mimetypes
    if isinstance(node, list):
        for v in node:
            _inline_assets(v, base, seen)
        return
    if not isinstance(node, dict):
        return
    src = node.get("src")
    if isinstance(src, str) and not src.startswith(("data:", "http://", "https://", "//")):
        hit = next((d / src for d in (base, base / "assets", base / "assets" / "logos")
                    if (d / src).is_file()), None)
        if hit is None:
            seen.setdefault("missing", []).append(src)
        else:
            raw = hit.read_bytes()
            mime = mimetypes.guess_type(hit.name)[0] or "application/octet-stream"
            node["src"] = "data:%s;base64,%s" % (mime, _b64.b64encode(raw).decode())
            seen.setdefault("inlined", []).append("%s (%.0f KB)" % (src, len(raw) / 1024))
    for v in node.values():
        _inline_assets(v, base, seen)

def build(doc, dest):
    payload = json.dumps(doc, ensure_ascii=False, indent=1).replace("</", "<\\/")
    if not MARK.search(TEMPLATE):
        raise SystemExit("the embedded template is damaged - rebuild the bundle")
    html = MARK.sub(lambda m: m.group(1) + "\n" + payload + "\n" + m.group(3), TEMPLATE, count=1)
    dest.write_text(html, encoding="utf-8")
    return dest

def main():
    ap = argparse.ArgumentParser(add_help=True, description="Build a Box data sheet.")
    ap.add_argument("content", nargs="?", help="the content JSON")
    ap.add_argument("--pdf", action="store_true")
    ap.add_argument("--compliance", metavar="FILE",
                    help="override the embedded credential list")
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    if not a.content:
        ap.print_help()
        return 2

    src = Path(a.content).resolve()
    doc = json.loads(src.read_text(encoding="utf-8"))

    compliance = COMPLIANCE
    if a.compliance:
        compliance = Path(a.compliance).read_text(encoding="utf-8")
        print(f"  using credential list from {a.compliance}")
    else:
        try:
            print("  credential list checked "
                  + json.loads(COMPLIANCE)["_verification"]["checked"]
                  + " — re-verify quarterly against box.com/trust")
        except Exception:
            pass

    assets = {}
    _inline_assets(doc, src.parent, assets)
    for x in assets.get("inlined", []):
        print(f"  inlined asset {x}")
    for x in assets.get("missing", []):
        print(f"  ! asset not found next to {src.name}: {x} — it will render as a broken image")

    V = _load_validator(compliance)
    errs, warns, report = V.validate(doc)
    print("\n".join(report))
    for w in warns:
        print(f"  ! {w}")
    for e in errs:
        print(f"  \u2717 {e}")
    if errs and not a.force:
        print("\nrefusing to build — fix the errors above\n")
        return 1

    dest = build(doc, src.parent / f"{_slug(doc.get('customer'))}-box-datasheet.html")
    print(f"wrote {dest.name}  ({dest.stat().st_size:,} bytes)")

    if a.pdf:
        import shutil, os
        exe = next((shutil.which(n) for n in
                    ("google-chrome", "google-chrome-stable", "chromium",
                     "chromium-browser", "chrome") if shutil.which(n)), None)
        if not exe:
            print("  ! no Chrome found — open the HTML and print to PDF "
                  "(margins None, Background graphics ON)")
        else:
            pdf = dest.with_suffix(".pdf")
            with tempfile.TemporaryDirectory() as tmp:
                subprocess.run([exe, "--headless", "--disable-gpu", "--no-sandbox",
                                f"--user-data-dir={tmp}", "--no-pdf-header-footer",
                                "--virtual-time-budget=8000",
                                f"--print-to-pdf={pdf}", dest.as_uri()],
                               capture_output=True, timeout=120)
            print(f"  wrote {pdf.name}" if pdf.is_file() else
                  "  ! PDF step failed — print from the browser instead")
    return 0

if __name__ == "__main__":
    sys.exit(main())
