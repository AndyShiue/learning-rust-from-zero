#!/usr/bin/env python3
"""Submit changed public pages to the IndexNow API after deployment."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
from pathlib import Path, PurePosixPath
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

from normalize_public_urls import public_alias


SITE_URL = "https://andyshiue.github.io/learning-rust-from-zero"
HOST = "andyshiue.github.io"
ENDPOINT = "https://api.indexnow.org/indexnow"
LANGUAGES = {"en", "zh-TW"}
KEY_PATTERN = re.compile(r"[A-Za-z0-9-]{8,128}")
ZERO_SHA = "0" * 40
URL_SAFE = "/:@-._~!$&'()*+,;="
NON_CANONICAL_URLS = {
    f"{SITE_URL}/en/foreword.html",
    f"{SITE_URL}/zh-TW/foreword.html",
}
FULL_SITE_PATHS = {
    "scripts/add_seo_metadata.py",
    "scripts/generate_sitemap.py",
    "scripts/normalize_public_urls.py",
    "scripts/submit_indexnow.py",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("public_dir", type=Path)
    parser.add_argument("--before", default="")
    parser.add_argument("--after", default="HEAD")
    parser.add_argument(
        "--all",
        action="store_true",
        help="Submit every canonical URL in the sitemap.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print selected URLs without contacting IndexNow.",
    )
    return parser.parse_args()


def sitemap_urls(public_dir: Path) -> list[str]:
    root = ET.parse(public_dir / "sitemap.xml").getroot()
    urls: list[str] = []
    seen: set[str] = set()
    for element in root.iter():
        if element.tag.rsplit("}", 1)[-1] != "loc" or not element.text:
            continue
        url = element.text.strip()
        if (
            url.startswith(f"{SITE_URL}/")
            and url not in NON_CANONICAL_URLS
            and url not in seen
        ):
            seen.add(url)
            urls.append(url)
    return urls


def changed_paths(before: str, after: str) -> set[str] | None:
    if not before or before == ZERO_SHA:
        return None

    result = subprocess.run(
        ["git", "diff", "--name-status", "--find-renames", before, after],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode:
        return None

    paths: set[str] = set()
    for line in result.stdout.splitlines():
        fields = line.split("\t")
        if len(fields) < 2:
            continue
        status = fields[0]
        if status.startswith(("R", "C")) and len(fields) >= 3:
            paths.update((fields[1], fields[2]))
        else:
            paths.add(fields[1])
    return paths


def public_url(language: str, relative_html: PurePosixPath) -> str:
    relative = f"{language}/{relative_html.as_posix()}"
    if relative.endswith("/index.html"):
        relative = relative[: -len("index.html")]
    encoded = quote(relative, safe=URL_SAFE)
    return f"{SITE_URL}/{encoded}"


def source_page_url(path: str) -> str | None:
    source = PurePosixPath(path)
    if len(source.parts) < 3 or source.parts[0] not in LANGUAGES:
        return None
    if source.parts[1] != "src" or source.suffix != ".md":
        return None

    relative = PurePosixPath(*source.parts[2:])
    if relative.name == "SUMMARY.md":
        return None
    if relative.name == "README.md":
        relative_html = relative.with_name("index.html")
    else:
        relative_html = relative.with_suffix(".html")

    alias = PurePosixPath(public_alias(relative_html.as_posix()))
    url = public_url(source.parts[0], alias)
    if url in NON_CANONICAL_URLS:
        return f"{SITE_URL}/{source.parts[0]}/"
    return url


def language_wide_change(path: str) -> str | None:
    source = PurePosixPath(path)
    if not source.parts or source.parts[0] not in LANGUAGES:
        return None
    if len(source.parts) == 2 and source.parts[1] == "book.toml":
        return source.parts[0]
    if len(source.parts) >= 3 and source.parts[1] == "theme":
        return source.parts[0]
    if len(source.parts) == 3 and source.parts[1:] == ("src", "SUMMARY.md"):
        return source.parts[0]
    return None


def select_urls(
    all_urls: list[str],
    paths: set[str] | None,
    submit_all: bool = False,
) -> list[str]:
    if submit_all or paths is None or paths.intersection(FULL_SITE_PATHS):
        return all_urls

    selected: set[str] = set()
    full_languages = {
        language
        for path in paths
        if (language := language_wide_change(path)) is not None
    }
    for url in all_urls:
        if any(url.startswith(f"{SITE_URL}/{language}/") for language in full_languages):
            selected.add(url)

    for path in paths:
        url = source_page_url(path)
        if url is not None:
            selected.add(url)
        elif path == "index.html":
            selected.add(f"{SITE_URL}/")

    known_urls = set(all_urls)
    # Deleted or renamed pages no longer appear in the current sitemap, but
    # IndexNow still accepts their old URLs so search engines can recrawl them.
    return sorted(selected, key=lambda url: (url not in known_urls, url))


def validate_key(key: str) -> None:
    if KEY_PATTERN.fullmatch(key) is None:
        raise ValueError(
            "INDEXNOW_KEY must contain 8-128 letters, numbers, or hyphens"
        )


def verify_key_file(key: str, attempts: int = 6) -> str:
    key_location = f"{SITE_URL}/{key}.txt"
    for attempt in range(attempts):
        try:
            with urlopen(key_location, timeout=15) as response:
                if response.read().decode("utf-8").strip() == key:
                    return key_location
        except (HTTPError, URLError, TimeoutError, UnicodeError):
            pass
        if attempt + 1 < attempts:
            time.sleep(10)
    raise RuntimeError("The deployed IndexNow key file could not be verified")


def submit(urls: list[str], key: str, attempts: int = 6) -> int:
    if len(urls) > 10_000:
        raise ValueError("IndexNow accepts at most 10,000 URLs per request")

    key_location = verify_key_file(key)
    payload = json.dumps(
        {
            "host": HOST,
            "key": key,
            "keyLocation": key_location,
            "urlList": urls,
        }
    ).encode("utf-8")
    for attempt in range(attempts):
        request = Request(
            ENDPOINT,
            data=payload,
            headers={"Content-Type": "application/json; charset=utf-8"},
            method="POST",
        )
        try:
            with urlopen(request, timeout=30) as response:
                status = response.status
        except HTTPError as error:
            status = error.code
        except (URLError, TimeoutError) as error:
            raise RuntimeError("IndexNow request failed") from error

        if status in {200, 202}:
            return status
        if status != 403 or attempt + 1 == attempts:
            raise RuntimeError(f"IndexNow returned HTTP {status}")
        time.sleep(10)

    raise RuntimeError("IndexNow submission attempts were exhausted")


def main() -> None:
    args = parse_args()
    all_urls = sitemap_urls(args.public_dir)
    paths = changed_paths(args.before, args.after)
    urls = select_urls(all_urls, paths, args.all)

    if args.dry_run:
        print(f"Selected {len(urls)} URL(s) for IndexNow")
        for url in urls:
            print(url)
        return
    if not urls:
        print("No indexable URL changes detected; skipping IndexNow")
        return

    key = os.environ.get("INDEXNOW_KEY", "")
    validate_key(key)
    status = submit(urls, key)
    print(f"IndexNow accepted {len(urls)} URL(s) with HTTP {status}")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, RuntimeError, ET.ParseError) as error:
        print(f"IndexNow submission failed: {error}", file=sys.stderr)
        raise SystemExit(1) from error
