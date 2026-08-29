#!/usr/bin/env python3
"""Print a built sheet to PDF, if a headless browser happens to be available.

    python3 scripts/topdf.py out/acme-box-datasheet.html [out/acme.pdf]

Two routes, tried in order: Playwright if it is installed, otherwise any Chrome
or Chromium already on this machine, driven with --headless --print-to-pdf (no
dependency - the repo stays stdlib-only).

This is the optional path. The path to assume is opening the HTML in a browser
and printing it - that works everywhere and needs nothing installed. Do not
install anything just for this.

`preferCSSPageSize` is the important flag: the template writes an @page rule for
the size the content file asked for, and without it Chromium prints A4 artwork
onto a Letter sheet and spills a two-page sheet across four.

Exits non-zero (and says why) when Playwright is unavailable, which is what
build.py falls back on.
"""
import os, shutil, subprocess, sys, tempfile
from pathlib import Path

FALLBACK = ("open the HTML and print to PDF instead — "
            "margins None, \"Background graphics\" ON")

# Names Chrome/Chromium ships under, plus the copy Playwright downloads.
CHROME_NAMES = [
    "google-chrome", "google-chrome-stable", "chromium", "chromium-browser",
    "chrome", "microsoft-edge",
]

def find_chrome():
    """A Chrome/Chromium binary on PATH, in PLAYWRIGHT_BROWSERS_PATH, or in the
    usual macOS/Linux install spots."""
    for n in CHROME_NAMES:
        hit = shutil.which(n)
        if hit:
            return hit
    roots = [Path(os.environ["PLAYWRIGHT_BROWSERS_PATH"])] if os.environ.get(
        "PLAYWRIGHT_BROWSERS_PATH") else []
    roots += [Path.home() / ".cache" / "ms-playwright"]
    for root in roots:
        if root.is_dir():
            for pat in ("chromium*/chrome-linux/chrome",
                        "chromium*/chrome-mac*/Chromium.app/Contents/MacOS/Chromium",
                        "chromium_headless_shell*/chrome-linux/headless_shell"):
                hit = sorted(root.glob(pat))
                if hit:
                    return str(hit[-1])
    mac = Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
    return str(mac) if mac.is_file() else None

def via_chrome(src, dest):
    """--print-to-pdf honours the template's @page rule, so the sheet comes out at
    the size the content file asked for rather than the browser's default."""
    exe = find_chrome()
    if not exe:
        return False, "no Chrome or Chromium found"
    with tempfile.TemporaryDirectory() as tmp:
        cmd = [exe, "--headless", "--disable-gpu", "--no-sandbox",
               f"--user-data-dir={tmp}", "--no-pdf-header-footer",
               "--virtual-time-budget=8000",
               f"--print-to-pdf={dest}", src.as_uri()]
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if dest.is_file() and dest.stat().st_size > 0:
        return True, exe
    return False, (r.stderr or r.stdout or "chrome produced no output").strip()[:200]

def main():
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    if not args:
        print(__doc__)
        return 2
    src = Path(args[0]).resolve()
    if not src.is_file():
        print(f"  ! no such file: {src}")
        return 2
    dest = Path(args[1]).resolve() if len(args) > 1 else src.with_suffix(".pdf")

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        ok, detail = via_chrome(src, dest)
        if ok:
            print(f"  wrote {dest}  (via {detail})")
            return 0
        print(f"  ! no Playwright, and {detail} — {FALLBACK}")
        return 3

    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch()
            try:
                page = browser.new_page()
                page.goto(src.as_uri())
                # the renderer builds the pages and injects @page on load; the web
                # font decides the final line breaks, so wait for both
                page.wait_for_selector(".page", timeout=15000)
                page.evaluate("document.fonts.ready")
                page.pdf(path=str(dest), prefer_css_page_size=True, print_background=True)
            finally:
                browser.close()
    except Exception as exc:
        ok, detail = via_chrome(src, dest)
        if ok:
            print(f"  wrote {dest}  (via {detail})")
            return 0
        print(f"  ! Playwright failed ({exc.__class__.__name__}: {exc}) — {FALLBACK}")
        return 4

    print(f"  wrote {dest}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
