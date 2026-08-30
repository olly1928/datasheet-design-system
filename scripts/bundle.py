#!/usr/bin/env python3
"""Bake the design system into one file ChatGPT can actually run.

    python3 scripts/bundle.py            # write dist/box-datasheet-builder.py
    python3 scripts/bundle.py --check    # fail if dist/ is behind its sources

Why this exists
---------------
ChatGPT's GitHub connector and its Code Interpreter are separate worlds. The
connector can read this repo; the sandbox that runs Python cannot see it. So
`scripts/build.py content/acme.json` has nothing to run against unless the model
first reproduces the template, the validator and the compliance list into the
sandbox by hand - about 16k tokens per sheet, and a 32KB HTML template retyped by
a language model is exactly the layout drift this repo exists to prevent.

The fix is to hand the sandbox one file instead. Attach dist/box-datasheet-builder.py
to a Custom GPT or Project once; from then on the model writes only the content
JSON and runs one command. The template never passes through the model at all.

What goes in, and what deliberately does not
--------------------------------------------
Embedded, because the build cannot run without them:
  template/datasheet.html      the design
  scripts/validate.py          the page-fit and claim checks
  brand/compliance.json        the closed credential list the validator enforces

NOT embedded:
  legal/disclaimer.md          the wording travels in the content file's "legal"
                               field, so Legal can change it without a rebuild
  brand/VOICE.md, SNIPPETS.md  the model reads these from the repo; they shape
  config.json                  what it writes, not how the build runs

That split is the point: the four files you maintain by hand stay live, and only
the machinery is frozen into the bundle.

stdlib only, in and out.
"""
import argparse, base64, hashlib, json, sys, zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEST = ROOT / "dist" / "box-datasheet-builder.py"

SOURCES = {
    "TEMPLATE":   ROOT / "template" / "datasheet.html",
    "VALIDATOR":  ROOT / "scripts" / "validate.py",
    "COMPLIANCE": ROOT / "brand" / "compliance.json",
}

def pack(text):
    """Deflate + base64 so the payload cannot be accidentally hand-edited in the
    bundle, and so a 32KB template does not dominate the file."""
    return base64.b64encode(zlib.compress(text.encode("utf-8"), 9)).decode("ascii")

def wrap(b64, width=96):
    return "\n".join('    "%s"' % b64[i:i + width] for i in range(0, len(b64), width))

HEADER = '''#!/usr/bin/env python3
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

Source revision: {stamp}
Embedded compliance list checked: {checked}
"""
import argparse, base64, json, re, subprocess, sys, tempfile, types, zlib
from pathlib import Path

def _unpack(chunks):
    return zlib.decompress(base64.b64decode("".join(chunks))).decode("utf-8")

'''

BODY = '''
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
    payload = json.dumps(doc, ensure_ascii=False, indent=1).replace("</", "<\\\\/")
    if not MARK.search(TEMPLATE):
        raise SystemExit("the embedded template is damaged - rebuild the bundle")
    html = MARK.sub(lambda m: m.group(1) + "\\n" + payload + "\\n" + m.group(3), TEMPLATE, count=1)
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
    print("\\n".join(report))
    for w in warns:
        print(f"  ! {w}")
    for e in errs:
        print(f"  \\u2717 {e}")
    if errs and not a.force:
        print("\\nrefusing to build — fix the errors above\\n")
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
'''

def render():
    parts = {k: v.read_text(encoding="utf-8") for k, v in SOURCES.items()}
    stamp = hashlib.sha256(
        "".join(parts[k] for k in sorted(parts)).encode("utf-8")).hexdigest()[:12]
    checked = "unknown"
    try:
        checked = json.loads(parts["COMPLIANCE"])["_verification"]["checked"]
    except Exception:
        pass
    out = [HEADER.format(stamp=stamp, checked=checked)]
    for name in ("TEMPLATE", "VALIDATOR", "COMPLIANCE"):
        out.append(f"_{name} = (\n{wrap(pack(parts[name]))}\n)\n")
    out.append(BODY)
    return "".join(out)

def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--check", action="store_true",
                    help="exit non-zero if dist/ is behind its sources")
    a = ap.parse_args()

    for name, path in SOURCES.items():
        if not path.is_file():
            print(f"  ✗ missing source: {path.relative_to(ROOT)}")
            return 2

    fresh = render()
    if a.check:
        if not DEST.is_file():
            print(f"  ✗ {DEST.relative_to(ROOT)} has never been built — run "
                  f"python3 scripts/bundle.py")
            return 1
        if DEST.read_text(encoding="utf-8") != fresh:
            print(f"  ✗ {DEST.relative_to(ROOT)} is out of date — the template, "
                  f"validator or compliance list has changed since it was built.\n"
                  f"    run: python3 scripts/bundle.py")
            return 1
        print(f"  bundle is in sync with the template, validator and compliance list")
        return 0

    DEST.parent.mkdir(parents=True, exist_ok=True)
    DEST.write_text(fresh, encoding="utf-8")
    print(f"wrote {DEST.relative_to(ROOT)}  ({len(fresh):,} bytes)")
    print("  attach this one file to your Custom GPT / Project — it carries the")
    print("  template, the validator and the credential list, and needs nothing else.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
