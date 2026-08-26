#!/usr/bin/env python3
"""Fetch an image from box.com into the local asset cache, with provenance.

    python3 scripts/fetch_asset.py <url> [<url> ...]

Downloads are restricted to an allowlist of Box-owned hosts, checked on every
redirect hop so a redirect cannot walk the fetch off-domain. Each file is stored
under assets/cache/ and recorded in assets/cache/provenance.json with its source
URL, checksum and fetch date - so for any asset on any generated sheet you can
say exactly where it came from and when.

Cached files are reused, so a sheet builds identically offline once its assets
have been fetched at least once.

stdlib only.
"""
import hashlib, json, mimetypes, re, sys, urllib.error, urllib.parse, urllib.request
from datetime import date
from pathlib import Path

ROOT   = Path(__file__).resolve().parent.parent
CACHE  = ROOT / "assets" / "cache"
PROV   = CACHE / "provenance.json"
ALLOW  = CACHE / "allowlist.txt"

MAX_BYTES = 8 * 1024 * 1024
UA = "box-datasheet-system/1.0 (+internal asset cache)"

DEFAULT_ALLOW = [
    "box.com", "www.box.com", "cdn.box.com", "www-cdn.box.com", "blog.box.com",
    "images.ctfassets.net", "assets.ctfassets.net", "downloads.ctfassets.net",
]

def allowed_hosts():
    if ALLOW.is_file():
        hosts = [l.strip().lower() for l in ALLOW.read_text().splitlines()
                 if l.strip() and not l.strip().startswith("#")]
        if hosts:
            return hosts
    return DEFAULT_ALLOW

def host_ok(url, hosts):
    h = (urllib.parse.urlparse(url).hostname or "").lower()
    return any(h == a or h.endswith("." + a) for a in hosts)

class _Guard(urllib.request.HTTPRedirectHandler):
    """Validate every redirect hop, not just the URL we started with."""
    def __init__(self, hosts): self.hosts = hosts
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if not host_ok(newurl, self.hosts):
            raise urllib.error.URLError(f"redirect leaves the allowlist: {newurl}")
        return super().redirect_request(req, fp, code, msg, headers, newurl)

def load_prov():
    if PROV.is_file():
        try: return json.loads(PROV.read_text())
        except Exception: pass
    return {}

def cache_name(url, ctype):
    base = Path(urllib.parse.urlparse(url).path).name or "asset"
    base = re.sub(r"[^A-Za-z0-9._-]+", "-", base).strip("-.") or "asset"
    if "." not in base:
        base += mimetypes.guess_extension(ctype or "") or ".bin"
    return f"{hashlib.sha256(url.encode()).hexdigest()[:10]}-{base}"

def fetch(url, quiet=False):
    """Return the cache filename for `url`, downloading it if not already held."""
    prov = load_prov()
    if url in prov and (CACHE / prov[url]["file"]).is_file():
        if not quiet: print(f"  cached  {prov[url]['file']}")
        return prov[url]["file"]

    hosts = allowed_hosts()
    if not host_ok(url, hosts):
        raise ValueError(f"host not on the allowlist: {url}\n"
                         f"  allowed: {', '.join(hosts)}\n"
                         f"  add one to assets/cache/allowlist.txt if it is Box-owned")

    opener = urllib.request.build_opener(_Guard(hosts))
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with opener.open(req, timeout=30) as r:
        if not host_ok(r.geturl(), hosts):
            raise ValueError(f"final URL leaves the allowlist: {r.geturl()}")
        ctype = (r.headers.get("Content-Type") or "").split(";")[0].strip()
        data = r.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES:
        raise ValueError(f"asset is larger than {MAX_BYTES // 1024 // 1024} MB: {url}")
    if ctype and not (ctype.startswith("image/") or ctype == "application/pdf"):
        raise ValueError(f"not an image ({ctype}): {url}")

    CACHE.mkdir(parents=True, exist_ok=True)
    name = cache_name(url, ctype)
    (CACHE / name).write_bytes(data)
    prov[url] = {
        "file": name,
        "bytes": len(data),
        "content_type": ctype,
        "sha256": hashlib.sha256(data).hexdigest(),
        "fetched": date.today().isoformat(),
    }
    PROV.write_text(json.dumps(prov, indent=2, sort_keys=True) + "\n")
    if not quiet: print(f"  fetched {name}  ({len(data)/1024:.0f} KB)  {ctype}")
    return name

def main():
    urls = [a for a in sys.argv[1:] if not a.startswith("-")]
    if not urls:
        print(__doc__); return 2
    rc = 0
    for u in urls:
        try: fetch(u)
        except Exception as e:
            print(f"  ! {e}"); rc = 1
    return rc

if __name__ == "__main__":
    sys.exit(main())
