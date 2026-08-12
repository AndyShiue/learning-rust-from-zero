#!/usr/bin/env python3
"""Add search and sharing metadata to the assembled mdBook site."""

from __future__ import annotations

import re
import sys
from html import escape, unescape
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import quote


SITE_URL = "https://andyshiue.github.io/learning-rust-from-zero"
SITE_NAME = "Learning Rust from Zero / 從零開始學 Rust"
ROOT_DESCRIPTION = (
    "A Rust tutorial for absolute beginners, from basic syntax and ownership "
    "to async programming."
)
LANGUAGES = {
    "en": {"hreflang": "en", "locale": "en_US"},
    "zh-TW": {"hreflang": "zh-TW", "locale": "zh_TW"},
}
EXCLUDED_NAMES = {"404.html", "print.html"}
REDIRECT_MARKER = "<!-- URL_ALIAS_REDIRECT -->"
URL_SAFE = "/:@-._~!$&'()*+,;="


class MainParagraphParser(HTMLParser):
    """Collect prose paragraphs from mdBook's main content."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.main_depth = 0
        self.skip_depth = 0
        self.current_tag: str | None = None
        self.current_parts: list[str] = []
        self.paragraphs: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "main":
            self.main_depth += 1
            return

        if not self.main_depth:
            return

        if tag in {"script", "style", "pre", "nav"}:
            self.skip_depth += 1
        elif tag == "p" and not self.skip_depth and self.current_tag is None:
            self.current_tag = tag
            self.current_parts = []

    def handle_endtag(self, tag: str) -> None:
        if tag == "main":
            self.main_depth = max(0, self.main_depth - 1)
            return

        if not self.main_depth:
            return

        if tag in {"script", "style", "pre", "nav"} and self.skip_depth:
            self.skip_depth -= 1
        elif tag == self.current_tag:
            text = re.sub(r"\s+", " ", "".join(self.current_parts)).strip()
            if text:
                self.paragraphs.append(text)
            self.current_tag = None
            self.current_parts = []

    def handle_data(self, data: str) -> None:
        if self.current_tag is not None and not self.skip_depth:
            self.current_parts.append(data)


def shorten(text: str, limit: int = 160) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "…"


def extract_title(document: str) -> str:
    match = re.search(r"<title\b[^>]*>(.*?)</title>", document, re.I | re.S)
    if not match:
        return SITE_NAME
    return re.sub(r"\s+", " ", unescape(re.sub(r"<[^>]+>", "", match.group(1)))).strip()


def extract_description(document: str, title: str, language: str | None) -> str:
    if language is None:
        return ROOT_DESCRIPTION

    parser = MainParagraphParser()
    parser.feed(document)
    paragraphs = parser.paragraphs

    description = ""
    for paragraph in paragraphs:
        candidate = f"{description} {paragraph}".strip()
        description = candidate
        if len(description) >= 120:
            break

    if not description:
        if language == "zh-TW":
            description = f"從零開始學 Rust：{title}。"
        else:
            description = f"Learn Rust from zero: {title}."
    return shorten(description)


def page_url(public_dir: Path, path: Path) -> str:
    relative = path.relative_to(public_dir).as_posix()
    if relative == "index.html":
        return f"{SITE_URL}/"
    if relative.endswith("/index.html"):
        relative = relative[: -len("index.html")]
    return f"{SITE_URL}/{quote(relative, safe=URL_SAFE)}"


def page_info(public_dir: Path, path: Path) -> tuple[str | None, str]:
    relative = path.relative_to(public_dir).as_posix()
    if relative == "index.html":
        return None, "index.html"

    parts = relative.split("/", 1)
    if parts[0] in LANGUAGES:
        language = parts[0]
        language_relative = parts[1] if len(parts) == 2 else "index.html"
        return language, language_relative
    return None, relative


def insert_before_head_end(document: str, tags: list[str]) -> str:
    if not tags:
        return document
    match = re.search(r"</head>", document, re.I)
    if not match:
        raise ValueError("HTML document has no </head> element")
    prefix = "" if document[: match.start()].endswith("\n") else "\n"
    addition = prefix + "\n".join(f"  {tag}" for tag in tags) + "\n"
    return document[: match.start()] + addition + document[match.start() :]


def upsert_meta(document: str, attr: str, key: str, tag: str) -> str:
    pattern = (
        rf'<meta\b(?=[^>]*\b{re.escape(attr)}\s*=\s*["\']'
        rf"{re.escape(key)}[\"'])[^>]*>"
    )
    document, count = re.subn(pattern, tag, document, count=1, flags=re.I | re.S)
    if count:
        return document
    return insert_before_head_end(document, [tag])


def upsert_link(document: str, rel: str, tag: str) -> str:
    pattern = (
        rf'<link\b(?=[^>]*\brel\s*=\s*["\']{re.escape(rel)}[\"\'])[^>]*>'
    )
    document, count = re.subn(pattern, tag, document, count=1, flags=re.I | re.S)
    if count:
        return document
    return insert_before_head_end(document, [tag])


def remove_alternate_links(document: str) -> str:
    pattern = (
        r'\s*<link\b(?=[^>]*\brel\s*=\s*["\']alternate["\'])'
        r'(?=[^>]*\bhreflang\s*=)[^>]*>\s*'
    )
    return re.sub(pattern, "", document, flags=re.I | re.S)


def add_metadata(public_dir: Path, path: Path) -> None:
    if path.name in EXCLUDED_NAMES or is_redirect_page(path):
        return

    document = path.read_text(encoding="utf-8")
    language, language_relative = page_info(public_dir, path)
    url = page_url(public_dir, path)
    title = extract_title(document)
    description = extract_description(document, title, language)
    locale = LANGUAGES.get(language, {}).get("locale", "en_US")
    page_type = "article" if language is not None else "website"

    document = upsert_meta(
        document,
        "name",
        "description",
        f'<meta name="description" content="{escape(description, quote=True)}">',
    )
    document = upsert_link(
        document,
        "canonical",
        f'<link rel="canonical" href="{escape(url, quote=True)}">',
    )

    metadata = [
        (
            "property",
            "og:type",
            f'<meta property="og:type" content="{page_type}">',
        ),
        (
            "property",
            "og:site_name",
            f'<meta property="og:site_name" content="{escape(SITE_NAME, quote=True)}">',
        ),
        (
            "property",
            "og:title",
            f'<meta property="og:title" content="{escape(title, quote=True)}">',
        ),
        (
            "property",
            "og:description",
            f'<meta property="og:description" content="{escape(description, quote=True)}">',
        ),
        (
            "property",
            "og:url",
            f'<meta property="og:url" content="{escape(url, quote=True)}">',
        ),
        (
            "property",
            "og:locale",
            f'<meta property="og:locale" content="{locale}">',
        ),
        ("name", "twitter:card", '<meta name="twitter:card" content="summary">'),
        (
            "name",
            "twitter:title",
            f'<meta name="twitter:title" content="{escape(title, quote=True)}">',
        ),
        (
            "name",
            "twitter:description",
            f'<meta name="twitter:description" content="{escape(description, quote=True)}">',
        ),
    ]
    for attr, key, tag in metadata:
        document = upsert_meta(document, attr, key, tag)

    document = remove_alternate_links(document)
    alternate_tags: list[str] = []
    if language is None:
        candidates = {
            "en": public_dir / "en" / "index.html",
            "zh-TW": public_dir / "zh-TW" / "index.html",
        }
        x_default = url
    else:
        candidates = {
            code: public_dir / code / language_relative for code in LANGUAGES
        }
        x_default = page_url(public_dir, candidates["en"])

    for code, candidate in candidates.items():
        if candidate.exists():
            alternate_tags.append(
                f'<link rel="alternate" hreflang="{LANGUAGES[code]["hreflang"]}" '
                f'href="{escape(page_url(public_dir, candidate), quote=True)}">'
            )
    alternate_tags.append(
        f'<link rel="alternate" hreflang="x-default" '
        f'href="{escape(x_default, quote=True)}">'
    )

    document = insert_before_head_end(document, alternate_tags)
    path.write_text(document, encoding="utf-8")


def is_redirect_page(path: Path) -> bool:
    """Skip legacy URL compatibility pages when adding SEO metadata."""
    try:
        with path.open("r", encoding="utf-8", errors="ignore") as stream:
            return REDIRECT_MARKER in stream.read(256)
    except OSError:
        return False


def main() -> None:
    public_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("public")
    for path in sorted(public_dir.rglob("*.html")):
        add_metadata(public_dir, path)
    print("Added SEO metadata to the assembled HTML pages")


if __name__ == "__main__":
    main()
