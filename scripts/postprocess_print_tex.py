#!/usr/bin/env python3
"""Patch generated print TeX for font fallback inside highlighted code blocks."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


HIGHLIGHTING_RE = re.compile(
    r"(?P<begin>\\begin\{Highlighting\}(?:\[[^\]]*\])?\n)"
    r"(?P<body>.*?)"
    r"(?P<end>\n\\end\{Highlighting\})",
    re.DOTALL,
)

CODE_SYMBOLS = {
    "✅",
    "❌",
    "⚠",
    "✓",
    "✗",
    "←",
    "→",
    "⇒",
    "🎉",
    "🚀",
    "🦀",
    "😊",
    "🐟",
}


def patch_code_symbols(text: str) -> str:
    patched: list[str] = []
    index = 0
    while index < len(text):
        char = text[index]
        if char in CODE_SYMBOLS:
            sequence = char
            index += 1
            if index < len(text) and text[index] == "\ufe0f":
                sequence += text[index]
                index += 1
            patched.append(f"\\CodeEmoji{{{sequence}}}")
            continue
        patched.append(char)
        index += 1
    return "".join(patched)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("tex", type=Path)
    args = parser.parse_args()

    tex = args.tex
    source = tex.read_text(encoding="utf-8")

    def replace(match: re.Match[str]) -> str:
        return (
            match.group("begin")
            + patch_code_symbols(match.group("body"))
            + match.group("end")
        )

    patched = HIGHLIGHTING_RE.sub(replace, source)
    tex.write_text(patched, encoding="utf-8")


if __name__ == "__main__":
    main()
