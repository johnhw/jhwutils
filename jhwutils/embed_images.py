#!/usr/bin/env python3
import argparse
import base64
import mimetypes
import os
from pathlib import Path
from urllib.parse import urljoin, urlparse

import bs4  # pip install beautifulsoup4
import requests

def read_bytes(url: str, base_dir: Path):
    """Return (bytes, mime) for a possibly relative URL."""
    parsed = urlparse(url)
    # data URIs: pass through (caller skips these)
    if parsed.scheme == "data":
        return None, None

    # Remote
    if parsed.scheme in ("http", "https"):
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        mime = resp.headers.get("Content-Type")
        if mime:
            mime = mime.split(";")[0].strip()
        return resp.content, mime

    # file/relative
    if parsed.scheme == "file":
        path = Path(parsed.path)
    else:
        path = (base_dir / url).resolve()

    data = path.read_bytes()
    mime, _ = mimetypes.guess_type(str(path))
    return data, mime

def to_data_uri(data: bytes, mime: str | None) -> str:
    if not mime:
        mime = "application/octet-stream"
    b64 = base64.b64encode(data).decode("ascii")
    return f"data:{mime};base64,{b64}"

def inline_images(html: str, base_dir: Path) -> str:
    soup = bs4.BeautifulSoup(html, "html.parser")
    print(f"Base dir: {base_dir}")
    # If <base href="..."> is present, respect it
    base_tag = soup.find("base", href=True)
    base_href = base_tag["href"].strip() if base_tag else None

    def resolve(u: str) -> str:
        if base_href:
            return urljoin(base_href, u)
        return u
    
    for img in soup.find_all("img"):
        print(f"Processing <img>: {img}")
        src = (img.get("src") or "").strip()
        if not src or src.startswith("data:"):            
            print("  Skipping (no src or already data URI)")
            continue
        resolved = resolve(src)
        try:
            data, mime = read_bytes(resolved, base_dir)
            if data is None:
                continue
            img["src"] = to_data_uri(data, mime)
        except Exception as e:
            # Leave the original src if anything goes wrong
            print(f"Warning: couldn’t inline {src}: {e}")

        # Optional: drop srcset to avoid external fetches by the browser
        if img.has_attr("srcset"):
            del img["srcset"]

    return str(soup)

def main():
    ap = argparse.ArgumentParser(
        description="Embed <img> resources as base64 data URIs in an HTML file."
    )
    ap.add_argument("input", help="Input HTML file")
    ap.add_argument("-o", "--output", help="Output HTML file (default: alongside input)")
    args = ap.parse_args()

    in_path = Path(args.input)
    html = in_path.read_text(encoding="utf-8", errors="replace")
    out_html = inline_images(html, in_path.parent)

    out_path = Path(args.output) if args.output else in_path.with_suffix(".inlined.html")
    out_path.write_text(out_html, encoding="utf-8")
    print(f"Wrote {out_path}")

if __name__ == "__main__":
    main()