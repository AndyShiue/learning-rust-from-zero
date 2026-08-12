#!/usr/bin/env python3
"""Generate the sitemap for the assembled GitHub Pages site."""

from __future__ import annotations

import sys
from pathlib import Path
from urllib.parse import quote
from xml.sax.saxutils import escape


SITE_URL = "https://andyshiue.github.io/learning-rust-from-zero"
EXCLUDED_PAGES = {"404.html", "print.html"}
REDIRECT_MARKER = "<!-- URL_ALIAS_REDIRECT -->"


def page_url(relative_path: str) -> str:
    """Return the public URL for a file below the assembled site."""
    if relative_path == "index.html":
        return f"{SITE_URL}/"

    if relative_path.endswith("/index.html"):
        relative_path = relative_path[: -len("index.html")]

    encoded_path = quote(
        relative_path,
        safe="/:@-._~!$&'()*+,;=",
    )
    return f"{SITE_URL}/{encoded_path}"


def generate(public_dir: Path) -> str:
    pages = []
    for path in sorted(public_dir.rglob("*.html")):
        relative_path = path.relative_to(public_dir).as_posix()
        if (
            relative_path in EXCLUDED_PAGES
            or path.name in EXCLUDED_PAGES
            or is_redirect_page(path)
        ):
            continue
        pages.append(page_url(relative_path))

    urls = "\n".join(
        f"    <url><loc>{escape(url)}</loc></url>" for url in pages
    )
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{urls}\n"
        "</urlset>\n"
    )


def is_redirect_page(path: Path) -> bool:
    """Skip old prefixed paths that now redirect to clean aliases."""
    try:
        with path.open("r", encoding="utf-8", errors="ignore") as stream:
            return REDIRECT_MARKER in stream.read(256)
    except OSError:
        return False


def main() -> None:
    public_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("public")
    sitemap_path = public_dir / "sitemap.xml"
    sitemap_path.write_text(generate(public_dir), encoding="utf-8")
    print(f"Generated {sitemap_path}")


if __name__ == "__main__":
    main()
