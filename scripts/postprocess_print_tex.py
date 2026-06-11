#!/usr/bin/env python3
"""Patch generated print TeX so emoji-like characters use the emoji font.

Code blocks (Highlighting) get fixed-width \\CodeEmoji; everything else in the
document body (prose, headings, inline \\texttt) gets \\Emoji.
"""

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

EMOJI_RANGES = (
    (0x2190, 0x21FF),
    (0x2600, 0x27BF),
    (0x1F000, 0x1FAFF),
)
EMOJI_SEQUENCE_RANGES = (
    (0xFE00, 0xFE0F),
    (0x1F3FB, 0x1F3FF),
)


def is_emoji_like(char: str) -> bool:
    codepoint = ord(char)
    return any(start <= codepoint <= end for start, end in EMOJI_RANGES)


def is_emoji_sequence_char(char: str) -> bool:
    codepoint = ord(char)
    return codepoint == 0x200D or any(
        start <= codepoint <= end for start, end in EMOJI_SEQUENCE_RANGES
    )


def wrap_emoji(text: str, command: str) -> str:
    patched: list[str] = []
    index = 0
    while index < len(text):
        char = text[index]
        if not is_emoji_like(char):
            patched.append(char)
            index += 1
            continue
        sequence = [char]
        index += 1
        while index < len(text) and is_emoji_sequence_char(text[index]):
            # 變體選擇符(U+FE00-FE0F)在印刷版沒有作用,直接丟棄,
            # 避免 xeCJK 把它分給缺這個字的 CJK 字型而產生警告。
            if not 0xFE00 <= ord(text[index]) <= 0xFE0F:
                sequence.append(text[index])
            index += 1
            if sequence and sequence[-1] == chr(0x200D) and index < len(text):
                sequence.append(text[index])
                index += 1
        patched.append(f"\\{command}{{{''.join(sequence)}}}")
    return "".join(patched)


def patch_document(source: str) -> str:
    begin = source.find("\\begin{document}")
    if begin == -1:
        return source
    preamble, body = source[:begin], source[begin:]
    parts: list[str] = []
    last = 0
    for match in HIGHLIGHTING_RE.finditer(body):
        parts.append(wrap_emoji(body[last:match.start()], "Emoji"))
        parts.append(
            match.group("begin")
            + wrap_emoji(match.group("body"), "CodeEmoji")
            + match.group("end")
        )
        last = match.end()
    parts.append(wrap_emoji(body[last:], "Emoji"))
    return preamble + "".join(parts)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("tex", type=Path)
    args = parser.parse_args()

    tex = args.tex
    tex.write_text(patch_document(tex.read_text(encoding="utf-8")), encoding="utf-8")


if __name__ == "__main__":
    main()
