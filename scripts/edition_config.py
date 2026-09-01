#!/usr/bin/env python3
"""Load language-owned settings used by the shared build scripts."""

from __future__ import annotations

import tomllib
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
EDITION_CODES = ("en", "zh-TW")


@dataclass(frozen=True)
class PrintConfig:
    toc_title: str
    generated_label: str
    date_template: str
    month_names: tuple[str, ...]


@dataclass(frozen=True)
class SeoConfig:
    hreflang: str
    locale: str
    fallback_description: str
    redirect_title: str
    redirect_message: str
    redirect_link_text: str


@dataclass(frozen=True)
class LessonConfig:
    goal: str
    main: str
    concept: str
    example: str
    recap: str

    def heading_roles(self) -> dict[str, str]:
        return {
            self.goal: "goal",
            self.main: "main",
            self.concept: "concept",
            self.example: "example",
            self.recap: "recap",
        }


@dataclass(frozen=True)
class EditionConfig:
    code: str
    title: str
    authors: tuple[str, ...]
    print: PrintConfig
    seo: SeoConfig
    lesson: LessonConfig


def _read_toml(path: Path) -> dict[str, object]:
    if not path.is_file():
        raise FileNotFoundError(path)
    with path.open("rb") as stream:
        return tomllib.load(stream)


def _table(
    document: dict[str, object],
    key: str,
    path: Path,
) -> dict[str, object]:
    value = document.get(key)
    if not isinstance(value, dict):
        raise ValueError(f"{path}: [{key}] must be a TOML table")
    return value


def _string(table: dict[str, object], key: str, path: Path) -> str:
    value = table.get(key)
    if not isinstance(value, str) or not value:
        raise ValueError(f"{path}: {key} must be a non-empty string")
    return value


def _strings(
    table: dict[str, object],
    key: str,
    path: Path,
    *,
    required: bool = True,
) -> tuple[str, ...]:
    value = table.get(key)
    if value is None and not required:
        return ()
    if (
        not isinstance(value, list)
        or not value
        or any(not isinstance(item, str) or not item for item in value)
    ):
        raise ValueError(f"{path}: {key} must be a non-empty string array")
    return tuple(value)


def _validate_templates(config: EditionConfig, path: Path) -> None:
    if config.print.month_names and len(config.print.month_names) != 12:
        raise ValueError(f"{path}: print.month_names must contain 12 names")
    if (
        "{month_name}" in config.print.date_template
        and not config.print.month_names
    ):
        raise ValueError(
            f"{path}: print.month_names is required by print.date_template"
        )

    try:
        config.print.date_template.format(
            year=2026,
            month_number=9,
            month_name=(
                config.print.month_names[8]
                if config.print.month_names
                else "9"
            ),
            day=1,
        )
        config.seo.fallback_description.format(title="Example")
    except (IndexError, KeyError, ValueError) as error:
        raise ValueError(f"{path}: invalid format template: {error}") from error

    if config.seo.redirect_message.count("{link}") != 1:
        raise ValueError(
            f"{path}: seo.redirect_message must contain one {{link}} placeholder"
        )


@lru_cache(maxsize=None)
def load_edition_config(code: str) -> EditionConfig:
    if code not in EDITION_CODES:
        raise ValueError(f"Unknown edition: {code}")

    edition_root = REPOSITORY_ROOT / code
    book_path = edition_root / "book.toml"
    edition_path = edition_root / "edition.toml"
    book_document = _read_toml(book_path)
    edition_document = _read_toml(edition_path)

    book = _table(book_document, "book", book_path)
    language = _string(book, "language", book_path)
    if language != code:
        raise ValueError(
            f"{book_path}: book.language is {language!r}, expected {code!r}"
        )

    print_table = _table(edition_document, "print", edition_path)
    seo_table = _table(edition_document, "seo", edition_path)
    lesson_table = _table(edition_document, "lesson", edition_path)

    config = EditionConfig(
        code=code,
        title=_string(book, "title", book_path),
        authors=_strings(book, "authors", book_path),
        print=PrintConfig(
            toc_title=_string(print_table, "toc_title", edition_path),
            generated_label=_string(print_table, "generated_label", edition_path),
            date_template=_string(print_table, "date_template", edition_path),
            month_names=_strings(
                print_table,
                "month_names",
                edition_path,
                required=False,
            ),
        ),
        seo=SeoConfig(
            hreflang=_string(seo_table, "hreflang", edition_path),
            locale=_string(seo_table, "locale", edition_path),
            fallback_description=_string(
                seo_table,
                "fallback_description",
                edition_path,
            ),
            redirect_title=_string(seo_table, "redirect_title", edition_path),
            redirect_message=_string(
                seo_table,
                "redirect_message",
                edition_path,
            ),
            redirect_link_text=_string(
                seo_table,
                "redirect_link_text",
                edition_path,
            ),
        ),
        lesson=LessonConfig(
            goal=_string(lesson_table, "goal", edition_path),
            main=_string(lesson_table, "main", edition_path),
            concept=_string(lesson_table, "concept", edition_path),
            example=_string(lesson_table, "example", edition_path),
            recap=_string(lesson_table, "recap", edition_path),
        ),
    )
    _validate_templates(config, edition_path)
    return config
