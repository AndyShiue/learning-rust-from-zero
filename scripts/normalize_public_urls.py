#!/usr/bin/env python3
"""Create stable public HTML URLs without renaming mdBook source files.

mdBook uses the source filenames when it writes HTML files. The source files
in this repository intentionally keep their numeric/letter prefixes because
those prefixes make the reading order explicit in SUMMARY.md. This script
adds cleaner public aliases after both books have been assembled:

* chapter6/06_move_closure.html -> chapter6/move_closure.html
* appendix1/a_number_literals.html -> appendix1/number_literals.html

The old paths become small client-side redirects so URLs that were already
shared or indexed continue to work. Relative links in the book are rewritten
to the aliases before the redirect pages are written.
"""

from __future__ import annotations

import json
import posixpath
import re
import sys
from html import escape
from pathlib import Path, PurePosixPath
from urllib.parse import quote

from edition_config import EDITION_CODES, load_edition_config


SITE_URL = "https://andyshiue.github.io/learning-rust-from-zero"
EDITIONS = {code: load_edition_config(code) for code in EDITION_CODES}
EXCLUDED_NAMES = {"404.html", "print.html"}
REDIRECT_MARKER = "<!-- URL_ALIAS_REDIRECT -->"
URL_SAFE = "/:@-._~!$&'()*+,;="

CHAPTER_DIRECTORY = re.compile(r"chapter\d+")
APPENDIX_DIRECTORY = re.compile(r"appendix\d+")
CHAPTER_FILENAME = re.compile(r"\d+_(.+\.html)")
APPENDIX_FILENAME = re.compile(r"[a-zA-Z]_(.+\.html)")
HREF = re.compile(
    r'(?P<prefix>\bhref\s*=\s*)(?P<quote>["\'])(?P<url>[^"\']*)(?P=quote)',
    re.IGNORECASE,
)
URL_SCHEME = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")


def is_excluded(path: Path) -> bool:
    return path.name in EXCLUDED_NAMES


def is_redirect_page(path: Path) -> bool:
    """Return whether path is one of our legacy URL redirect pages."""
    try:
        with path.open("r", encoding="utf-8", errors="ignore") as stream:
            return REDIRECT_MARKER in stream.read(256)
    except OSError:
        return False


def public_alias(relative_path: str) -> str:
    """Return the public alias for a language-relative HTML path."""
    path = PurePosixPath(relative_path)
    if len(path.parts) < 2:
        return relative_path

    directory = path.parts[-2]
    filename = path.name
    replacement: str | None = None

    if CHAPTER_DIRECTORY.fullmatch(directory):
        match = CHAPTER_FILENAME.fullmatch(filename)
        if match:
            replacement = match.group(1)
    elif APPENDIX_DIRECTORY.fullmatch(directory):
        match = APPENDIX_FILENAME.fullmatch(filename)
        if match:
            replacement = match.group(1)

    if replacement is None:
        return relative_path
    return path.with_name(replacement).as_posix()


def collect_mapping(language_dir: Path) -> dict[str, str]:
    """Collect source-output paths and their public aliases."""
    mapping: dict[str, str] = {}
    for path in sorted(language_dir.rglob("*.html")):
        if is_excluded(path) or is_redirect_page(path):
            continue
        relative = path.relative_to(language_dir).as_posix()
        mapping[relative] = public_alias(relative)

    original_paths = set(mapping)
    targets: dict[str, str] = {}
    for source, target in mapping.items():
        previous = targets.setdefault(target, source)
        if previous != source:
            raise ValueError(
                f"Public URL collision in {language_dir}: {previous} and {source} "
                f"both map to {target}"
            )
        if target != source and target in original_paths:
            raise ValueError(
                f"Public URL collision in {language_dir}: {source} maps to "
                f"existing output {target}"
            )
    return mapping


def canonical_url(language: str, relative_path: str) -> str:
    encoded = quote(f"{language}/{relative_path}", safe=URL_SAFE)
    return f"{SITE_URL}/{encoded}"


def relative_target(source: str, target: str) -> str:
    parent = PurePosixPath(source).parent.as_posix()
    return posixpath.relpath(target, parent if parent != "." else ".")


def redirect_document(language: str, source: str, target: str) -> str:
    edition = EDITIONS[language]
    target_href = relative_target(source, target)
    target_json = json.dumps(target_href, ensure_ascii=False)
    target_url = canonical_url(language, target)
    escaped_target = escape(target_href, quote=True)
    escaped_url = escape(target_url, quote=True)
    redirect_link = (
        f'<a href="{escaped_target}">'
        f"{escape(edition.seo.redirect_link_text)}</a>"
    )
    redirect_message = escape(edition.seo.redirect_message).replace(
        "{link}",
        redirect_link,
    )
    return f"""{REDIRECT_MARKER}
<!doctype html>
<html lang="{escape(language)}">
<head>
  <meta charset="utf-8">
  <meta name="robots" content="noindex">
  <meta http-equiv="refresh" content="0; url={escaped_target}">
  <link rel="canonical" href="{escaped_url}">
  <title>{escape(edition.seo.redirect_title)}</title>
</head>
<body>
  <p>{redirect_message}</p>
  <script>window.location.replace({target_json});</script>
</body>
</html>
"""


def rewrite_href_value(
    value: str,
    current_path: str,
    mapping: dict[str, str],
) -> str:
    """Rewrite one relative HTML href if it points at a renamed page."""
    if (
        not value
        or value.startswith(("#", "/", "//"))
        or URL_SCHEME.match(value)
    ):
        return value

    match = re.match(r"([^?#]*)(.*)", value, re.DOTALL)
    if match is None:
        return value
    path_part, suffix = match.groups()
    if not path_part or path_part.endswith("/"):
        return value

    parent = PurePosixPath(current_path).parent.as_posix()
    resolved = posixpath.normpath(posixpath.join(parent, path_part))
    if resolved == ".." or resolved.startswith("../"):
        return value

    target = mapping.get(resolved)
    if target is None or target == resolved:
        return value

    replacement = posixpath.relpath(target, parent if parent != "." else ".")
    return f"{replacement}{suffix}"


def rewrite_links(
    document: str,
    current_path: str,
    mapping: dict[str, str],
) -> str:
    def replace(match: re.Match[str]) -> str:
        value = match.group("url")
        rewritten = rewrite_href_value(value, current_path, mapping)
        return (
            f"{match.group('prefix')}{match.group('quote')}"
            f"{rewritten}{match.group('quote')}"
        )

    return HREF.sub(replace, document)


def normalize_language(language_dir: Path) -> int:
    mapping = collect_mapping(language_dir)
    renamed = {
        source: target for source, target in mapping.items() if source != target
    }

    for source, target in renamed.items():
        source_path = language_dir / source
        target_path = language_dir / target
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_bytes(source_path.read_bytes())

    for path in sorted(language_dir.rglob("*.html")):
        if is_excluded(path) or is_redirect_page(path):
            continue
        relative = path.relative_to(language_dir).as_posix()
        document = path.read_text(encoding="utf-8")
        rewritten = rewrite_links(document, relative, mapping)
        if rewritten != document:
            path.write_text(rewritten, encoding="utf-8")

    # Recent mdBook versions populate the visible sidebar from a hashed
    # JavaScript bundle instead of relying only on toc.html. It contains the
    # same relative hrefs, so it must be rewritten as part of the public URL
    # migration too.
    for path in sorted(language_dir.glob("toc-*.js")):
        relative = path.relative_to(language_dir).as_posix()
        document = path.read_text(encoding="utf-8")
        rewritten = rewrite_links(document, relative, mapping)
        if rewritten != document:
            path.write_text(rewritten, encoding="utf-8")

    for source, target in renamed.items():
        source_path = language_dir / source
        source_path.write_text(
            redirect_document(
                language_dir.name,
                source,
                target,
            ),
            encoding="utf-8",
        )

    return len(renamed)


def main() -> None:
    public_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("public")
    total = 0
    for language in EDITION_CODES:
        language_dir = public_dir / language
        if not language_dir.is_dir():
            raise FileNotFoundError(
                f"Missing assembled language directory: {language_dir}"
            )
        renamed = normalize_language(language_dir)
        total += renamed
        print(f"Normalized {renamed} public URLs in {language}/")
    print(f"Normalized {total} public URLs in total")


if __name__ == "__main__":
    main()
