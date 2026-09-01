#!/usr/bin/env python3
"""Check that the English and Traditional Chinese mdBook sources stay mirrored.

This check intentionally verifies structure rather than translated prose. It
compares source paths, SUMMARY.md order, heading levels, code-fence attributes,
local Markdown links, and the standard lesson skeleton. Translation accuracy
and code semantics still require human review.
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import unquote, urlsplit

from edition_config import load_edition_config


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
ZH_ROOT = REPOSITORY_ROOT / "zh-TW" / "src"
EN_ROOT = REPOSITORY_ROOT / "en" / "src"

IGNORED_DIRECTORIES = {"__pycache__"}
IGNORED_SUFFIXES = {".pyc", ".pyo"}

FENCE_OPEN = re.compile(
    r"^ {0,3}(?P<marker>`{3,}|~{3,})(?P<info>.*)$"
)
HEADING = re.compile(r"^ {0,3}(?P<marks>#{1,6})(?:[ \t]+|$)(?P<title>.*)$")
# Match from the label's final closing bracket so titles such as `[T]` inside
# backticks do not hide the surrounding Markdown link.
MARKDOWN_LINK = re.compile(r"\]\((?P<target>[^)\n]+)\)")
LESSON_PATH = re.compile(
    r"^(?:chapter\d+/\d{2}_[^/]+|appendix\d+/[a-z]_[^/]+)\.md$"
)

ZH_LESSON_ROLES = load_edition_config("zh-TW").lesson.heading_roles()
EN_LESSON_ROLES = load_edition_config("en").lesson.heading_roles()
VALID_LESSON_ROLE_SEQUENCES = {
    ("goal", "main", "recap"),
    ("goal", "concept", "example", "recap"),
}


@dataclass(frozen=True)
class Heading:
    level: int
    title: str
    line: int


@dataclass(frozen=True)
class MarkdownStructure:
    headings: tuple[Heading, ...]
    fence_infos: tuple[str, ...]
    markdown_links: tuple[str, ...]
    unclosed_fence_line: int | None


def collect_source_files(root: Path) -> dict[str, Path]:
    """Return non-generated source files keyed by POSIX relative path."""
    files: dict[str, Path] = {}
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(root)
        if any(part in IGNORED_DIRECTORIES for part in relative.parts):
            continue
        if path.suffix.lower() in IGNORED_SUFFIXES:
            continue
        files[relative.as_posix()] = path
    return files


def is_closing_fence(line: str, marker_character: str, length: int) -> bool:
    stripped = line.lstrip(" ")
    if len(line) - len(stripped) > 3:
        return False
    stripped = stripped.rstrip()
    return (
        len(stripped) >= length
        and set(stripped) == {marker_character}
    )


def normalize_link_target(raw_target: str) -> str:
    """Remove an optional Markdown title and normalize path separators."""
    target = raw_target.strip()
    if target.startswith("<") and ">" in target:
        target = target[1 : target.index(">")]
    else:
        target = target.split(maxsplit=1)[0]
    return target.replace("\\", "/")


def is_local_markdown_link(target: str) -> bool:
    if target.startswith("/"):
        return False
    parsed = urlsplit(target)
    return (
        not parsed.scheme
        and not parsed.netloc
        and unquote(parsed.path).lower().endswith(".md")
    )


def scan_markdown(path: Path) -> MarkdownStructure:
    """Extract comparable Markdown structure while ignoring fenced contents."""
    headings: list[Heading] = []
    fence_infos: list[str] = []
    markdown_links: list[str] = []
    open_fence: tuple[str, int, int] | None = None

    for line_number, line in enumerate(
        path.read_text(encoding="utf-8").splitlines(),
        start=1,
    ):
        if open_fence is not None:
            marker_character, length, _ = open_fence
            if is_closing_fence(line, marker_character, length):
                open_fence = None
            continue

        fence_match = FENCE_OPEN.match(line)
        if fence_match:
            marker = fence_match.group("marker")
            fence_infos.append(fence_match.group("info").strip())
            open_fence = (marker[0], len(marker), line_number)
            continue

        heading_match = HEADING.match(line)
        if heading_match:
            title = heading_match.group("title").strip()
            title = re.sub(r"[ \t]+#+[ \t]*$", "", title)
            headings.append(
                Heading(
                    level=len(heading_match.group("marks")),
                    title=title,
                    line=line_number,
                )
            )

        for link_match in MARKDOWN_LINK.finditer(line):
            target = normalize_link_target(link_match.group("target"))
            if is_local_markdown_link(target):
                markdown_links.append(target)

    unclosed_line = open_fence[2] if open_fence is not None else None
    return MarkdownStructure(
        headings=tuple(headings),
        fence_infos=tuple(fence_infos),
        markdown_links=tuple(markdown_links),
        unclosed_fence_line=unclosed_line,
    )


def first_sequence_difference(
    label: str,
    zh_values: tuple[object, ...],
    en_values: tuple[object, ...],
) -> str | None:
    if zh_values == en_values:
        return None

    common_length = min(len(zh_values), len(en_values))
    difference_index = common_length
    for index in range(common_length):
        if zh_values[index] != en_values[index]:
            difference_index = index
            break

    zh_value = (
        repr(zh_values[difference_index])
        if difference_index < len(zh_values)
        else "<end>"
    )
    en_value = (
        repr(en_values[difference_index])
        if difference_index < len(en_values)
        else "<end>"
    )
    return (
        f"{label} differs at item {difference_index + 1}: "
        f"zh-TW={zh_value}, en={en_value} "
        f"(counts {len(zh_values)} vs {len(en_values)})"
    )


def validate_local_links(
    language: str,
    source_path: Path,
    structure: MarkdownStructure,
    errors: list[str],
) -> None:
    for target in structure.markdown_links:
        parsed = urlsplit(target)
        linked_path = (source_path.parent / unquote(parsed.path)).resolve()
        if not linked_path.is_file():
            source = source_path.relative_to(REPOSITORY_ROOT).as_posix()
            errors.append(
                f"{language}: broken Markdown link in {source}: {target}"
            )


def validate_lesson(
    relative_path: str,
    language: str,
    structure: MarkdownStructure,
    role_names: dict[str, str],
    errors: list[str],
) -> tuple[str, ...]:
    h1_headings = [heading for heading in structure.headings if heading.level == 1]
    if len(h1_headings) != 1:
        errors.append(
            f"{language}: {relative_path} must contain exactly one H1; "
            f"found {len(h1_headings)}"
        )

    h2_headings = [heading for heading in structure.headings if heading.level == 2]
    h2_titles = [heading.title for heading in h2_headings]
    goal_title = next(title for title, role in role_names.items() if role == "goal")
    recap_title = next(title for title, role in role_names.items() if role == "recap")

    if not h2_titles or h2_titles[0] != goal_title:
        errors.append(
            f"{language}: {relative_path} must start its H2 structure "
            f"with {goal_title!r}"
        )
    if not h2_titles or h2_titles[-1] != recap_title:
        errors.append(
            f"{language}: {relative_path} must end its H2 structure "
            f"with {recap_title!r}"
        )

    roles = tuple(
        role_names[heading.title]
        for heading in h2_headings
        if heading.title in role_names
    )
    if roles not in VALID_LESSON_ROLE_SEQUENCES:
        errors.append(
            f"{language}: {relative_path} has an invalid lesson role "
            f"sequence: {roles}"
        )
    return roles


def check_mirror() -> tuple[list[str], dict[str, int]]:
    errors: list[str] = []
    zh_files = collect_source_files(ZH_ROOT)
    en_files = collect_source_files(EN_ROOT)

    zh_paths = set(zh_files)
    en_paths = set(en_files)
    for relative_path in sorted(zh_paths - en_paths):
        errors.append(f"source path exists only in zh-TW: {relative_path}")
    for relative_path in sorted(en_paths - zh_paths):
        errors.append(f"source path exists only in en: {relative_path}")

    matched_paths = sorted(zh_paths & en_paths)
    lesson_count = 0
    summary_link_count = 0

    for relative_path in matched_paths:
        zh_path = zh_files[relative_path]
        en_path = en_files[relative_path]
        if zh_path.suffix.lower() != ".md":
            continue

        zh_structure = scan_markdown(zh_path)
        en_structure = scan_markdown(en_path)

        if zh_structure.unclosed_fence_line is not None:
            errors.append(
                f"zh-TW: unclosed fence in {relative_path}:"
                f"{zh_structure.unclosed_fence_line}"
            )
        if en_structure.unclosed_fence_line is not None:
            errors.append(
                f"en: unclosed fence in {relative_path}:"
                f"{en_structure.unclosed_fence_line}"
            )

        comparisons = (
            (
                "heading-level sequence",
                tuple(heading.level for heading in zh_structure.headings),
                tuple(heading.level for heading in en_structure.headings),
            ),
            (
                "code-fence info sequence",
                zh_structure.fence_infos,
                en_structure.fence_infos,
            ),
            (
                "local Markdown-link sequence",
                zh_structure.markdown_links,
                en_structure.markdown_links,
            ),
        )
        for label, zh_values, en_values in comparisons:
            difference = first_sequence_difference(label, zh_values, en_values)
            if difference is not None:
                errors.append(f"{relative_path}: {difference}")

        validate_local_links("zh-TW", zh_path, zh_structure, errors)
        validate_local_links("en", en_path, en_structure, errors)

        if relative_path == "SUMMARY.md":
            summary_link_count = len(zh_structure.markdown_links)

        if LESSON_PATH.fullmatch(relative_path):
            lesson_count += 1
            zh_roles = validate_lesson(
                relative_path,
                "zh-TW",
                zh_structure,
                ZH_LESSON_ROLES,
                errors,
            )
            en_roles = validate_lesson(
                relative_path,
                "en",
                en_structure,
                EN_LESSON_ROLES,
                errors,
            )
            if zh_roles != en_roles:
                errors.append(
                    f"{relative_path}: lesson role sequence differs: "
                    f"zh-TW={zh_roles}, en={en_roles}"
                )

    statistics = {
        "source_files_per_language": len(zh_files),
        "summary_links": summary_link_count,
        "lesson_files": lesson_count,
    }
    return errors, statistics


def main() -> None:
    errors, statistics = check_mirror()
    if errors:
        print("Bilingual mirror check failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        raise SystemExit(1)

    print("Bilingual mirror check passed:")
    print(
        "- source files: "
        f"{statistics['source_files_per_language']} per language"
    )
    print(f"- SUMMARY.md links: {statistics['summary_links']}")
    print(f"- lesson files: {statistics['lesson_files']}")
    print("- path, heading, fence, and local-link sequences match")


if __name__ == "__main__":
    main()
