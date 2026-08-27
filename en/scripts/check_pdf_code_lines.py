#!/usr/bin/env python3
"""Fail when a code line in the English PDF exceeds the configured limit."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPOSITORY_SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"
sys.path.insert(0, str(REPOSITORY_SCRIPTS))

from mdbook_to_pandoc import parse_summary, rewrite_markdown


DEFAULT_MAX_CHARACTERS = 95


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--summary", type=Path, default=Path("src/SUMMARY.md"))
    parser.add_argument("--src-dir", type=Path, default=Path("src"))
    parser.add_argument(
        "--max-characters",
        type=int,
        default=DEFAULT_MAX_CHARACTERS,
        help=f"maximum visible code-line width (default: {DEFAULT_MAX_CHARACTERS})",
    )
    return parser.parse_args()


def find_violations(summary: Path, src_dir: Path, max_characters: int) -> list[str]:
    violations: list[str] = []

    for event_type, value, _indent in parse_summary(summary):
        if event_type != "file" or not value:
            continue

        source = src_dir / value
        if not source.exists():
            raise FileNotFoundError(source)

        # Reuse the PDF converter so fenced-code parsing, tab expansion, Unicode
        # width, and mdBook hidden Rust lines match the generated PDF exactly.
        rewrite_markdown(
            source.read_text(encoding="utf-8"),
            source=source,
            heading_shift=0,
            first_heading_attrs=None,
            code_line_limit=max_characters,
            code_report=violations,
        )

    return violations


def main() -> int:
    args = parse_args()
    if args.max_characters < 1:
        print("--max-characters must be at least 1", file=sys.stderr)
        return 2

    violations = find_violations(args.summary, args.src_dir, args.max_characters)
    if violations:
        print(
            f"English PDF code lines must be <= {args.max_characters} characters.",
            file=sys.stderr,
        )
        print("\n".join(violations), file=sys.stderr)
        return 1

    print(f"All English PDF code lines are <= {args.max_characters} characters.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
