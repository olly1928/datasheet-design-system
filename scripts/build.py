#!/usr/bin/env python3
"""Build a data sheet: content JSON + template -> a self-contained HTML file.

    python3 scripts/build.py content/acme.json

Writes out/<customer>.html. Open it and print to PDF (Letter, margins None,
"Background graphics" ON) -- or run with --pdf if Playwright is available.

stdlib only for the HTML path, so it runs in any Python sandbox.
"""
import json, re, sys, subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TPL  = ROOT / "template" / "datasheet.html"
OUT  = ROOT / "out"

MARK = re.compile(
    r'(<script id="content" type="application/json">)(.*?)(</script>)',
    re.S)

def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", str(s).lower()).strip("-") or "datasheet"

def build(src, want_pdf=False):
    doc = json.loads(Path(src).read_text(encoding="utf-8"))
    tpl = TPL.read_text(encoding="utf-8")

    payload = json.dumps(doc, ensure_ascii=False, indent=1)
    # a literal </script> inside any string would close the block early
    payload = payload.replace("</", "<\\/")

    if not MARK.search(tpl):
        raise SystemExit("template is missing its content block — is template/datasheet.html intact?")
    html = MARK.sub(lambda m: m.group(1) + "\n" + payload + "\n" + m.group(3), tpl, count=1)

    OUT.mkdir(exist_ok=True)
    dest = OUT / f"{slug(doc.get('customer'))}-box-datasheet.html"
    dest.write_text(html, encoding="utf-8")
    print(f"wrote {dest.relative_to(ROOT)}  ({len(html):,} bytes)")

    if want_pdf:
        pdf = dest.with_suffix(".pdf")
        r = subprocess.run([sys.executable, str(ROOT/"scripts"/"topdf.py"), str(dest), str(pdf)])
        if r.returncode == 0:
            print(f"wrote {pdf.relative_to(ROOT)}")
        else:
            print("PDF step unavailable — open the HTML and print to PDF "
                  "(Letter, margins None, Background graphics ON)")
    return dest

def main():
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    if not args:
        print(__doc__); return 2
    # validate first; refuse to build a sheet that cannot fit
    sys.path.insert(0, str(ROOT / "scripts"))
    import validate as V
    doc = json.loads(Path(args[0]).read_text(encoding="utf-8"))
    errs, warns, report = V.validate(doc)
    print("\n".join(report))
    for w in warns: print(f"  ! {w}")
    for e in errs:  print(f"  ✗ {e}")
    if errs and "--force" not in sys.argv:
        print("\nrefusing to build — fix the errors above, or pass --force\n"); return 1
    build(args[0], want_pdf="--pdf" in sys.argv)
    return 0

if __name__ == "__main__":
    sys.exit(main())
