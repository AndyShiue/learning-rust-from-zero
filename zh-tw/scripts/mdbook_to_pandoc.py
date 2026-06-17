#!/usr/bin/env python3
"""Build a Pandoc manuscript from an mdBook SUMMARY.md."""

from __future__ import annotations

import argparse
import os
import re
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


SUMMARY_HEADING_RE = re.compile(r"^#\s+(.+?)\s*$")
SUMMARY_LINK_RE = re.compile(r"^(?P<indent>\s*)(?:-\s*)?\[(?P<title>.+?)\]\((?P<path>[^)]+)\)\s*$")
FENCE_RE = re.compile(r"^(?P<fence>`{3,}|~{3,})(?P<info>.*)$")
HEADING_RE = re.compile(r"^(?P<marks>#{1,6})(?P<space>\s+)(?P<title>.*)$")


RUST_CODE_CLASSES = {
    "rust",
    "rs",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--summary", type=Path, default=Path("src/SUMMARY.md"))
    parser.add_argument("--src-dir", type=Path, default=Path("src"))
    parser.add_argument("--output", type=Path, default=Path("build/print/manuscript.md"))
    parser.add_argument("--code-report", type=Path, default=Path("build/print/code-lines.txt"))
    parser.add_argument("--code-line-limit", type=int, default=96)
    return parser.parse_args()


def normalize_code_info(info: str) -> tuple[str, bool]:
    info = info.strip()
    if not info:
        return "", False

    first = re.split(r"[\s,]+", info, maxsplit=1)[0].strip("{}.")
    if first in RUST_CODE_CLASSES:
        return "rust", True
    if first == "ignore":
        return "text", False
    if first == "console":
        return "text", False
    return first, False


def visible_width(line: str) -> int:
    width = 0
    for char in line:
        if char == "\t":
            width += 4 - (width % 4)
        elif ord(char) >= 0x2E80:
            width += 2
        else:
            width += 1
    return width


def normalize_table_escaped_pipes(line: str) -> str:
    stripped = line.strip()
    if not (stripped.startswith("|") and stripped.endswith("|")):
        return line
    return line.replace("`\\|`", "\\|")


def apply_print_markdown_fixes(line: str) -> str:
    # Keep mdBook-facing Markdown untouched; normalize table syntax only for Pandoc.
    return normalize_table_escaped_pipes(line)


def rewrite_markdown(
    text: str,
    *,
    source: Path,
    heading_shift: int,
    first_heading_attrs: str | None,
    code_line_limit: int,
    code_report: list[str],
) -> str:
    lines = text.splitlines()
    rewritten: list[str] = []
    in_fence = False
    rust_fence = False
    fence_marker = ""
    first_heading_seen = False

    for line_number, line in enumerate(lines, start=1):
        fence_match = FENCE_RE.match(line)
        if fence_match:
            fence = fence_match.group("fence")
            if not in_fence:
                language, rust_fence = normalize_code_info(fence_match.group("info"))
                fence_marker = fence[:3]
                rewritten.append(f"{fence_marker}{language}" if language else fence_marker)
                in_fence = True
            else:
                rewritten.append(fence_marker)
                in_fence = False
                rust_fence = False
                fence_marker = ""
            continue

        if in_fence:
            if rust_fence:
                stripped = line.lstrip()
                indent = line[: len(line) - len(stripped)]
                if stripped == "#" or stripped.startswith("# ") or stripped.startswith("#\t"):
                    continue
                if stripped.startswith("##"):
                    line = indent + stripped[1:]

            width = visible_width(line)
            if width > code_line_limit:
                code_report.append(f"{source}:{line_number}: width {width}: {line}")
            rewritten.append(line)
            continue

        line = apply_print_markdown_fixes(line)

        heading_match = HEADING_RE.match(line)
        if heading_match:
            level = len(heading_match.group("marks"))
            shifted_level = min(level + heading_shift, 6)
            attrs = ""
            if not first_heading_seen and first_heading_attrs:
                attrs = f" {first_heading_attrs}"
            first_heading_seen = True
            rewritten.append(
                f"{'#' * shifted_level}{heading_match.group('space')}{heading_match.group('title')}{attrs}"
            )
            continue

        rewritten.append(line)

    return "\n".join(rewritten).strip() + "\n"


def part_page(title: str) -> str:
    escaped_title = title.replace("&", r"\&").replace("%", r"\%")
    return f"""
\\clearpage
\\phantomsection
\\addcontentsline{{toc}}{{part}}{{{escaped_title}}}
\\thispagestyle{{empty}}
\\vspace*{{\\fill}}
\\begin{{center}}
{{\\fontsize{{34pt}}{{42pt}}\\selectfont\\bfseries {escaped_title}}}
\\end{{center}}
\\vspace*{{\\fill}}
\\clearpage
""".strip()


def build_date_text() -> str:
    override = os.environ.get("PRINT_BUILD_DATE")
    if override:
        return override

    timezone = os.environ.get("PRINT_BUILD_TZ", "Asia/Taipei")
    try:
        today = datetime.now(ZoneInfo(timezone)).date()
    except ZoneInfoNotFoundError:
        today = datetime.now().date()
    return f"{today.year} 年 {today.month} 月 {today.day} 日"


def title_page(build_date: str) -> str:
    escaped_date = build_date.replace("&", r"\&").replace("%", r"\%")
    return rf"""
\begin{{titlepage}}
\thispagestyle{{empty}}
\vspace*{{\fill}}
\begin{{center}}
{{\fontsize{{30pt}}{{38pt}}\selectfont\bfseries 從零開始學 Rust}}

\vspace{{2em}}
{{\Large Andy Shiue}}

\vspace{{1.5em}}
{{\large 生成日期：{escaped_date}}}
\end{{center}}
\vspace*{{\fill}}
\end{{titlepage}}
""".strip()


def blank_page() -> str:
    return r"""
\clearpage
\thispagestyle{empty}
\null
\clearpage
""".strip()


def table_of_contents() -> str:
    return r"""
\cleardoublepage
\markboth{目錄}{目錄}
\renewcommand*\contentsname{目錄}
\setcounter{tocdepth}{1}
\tableofcontents
\cleardoublepage
\markboth{}{}
""".strip()


def parse_summary(summary: Path) -> list[tuple[str, str | None, int | None]]:
    events: list[tuple[str, str | None, int | None]] = []
    for raw_line in summary.read_text(encoding="utf-8").splitlines():
        heading = SUMMARY_HEADING_RE.match(raw_line)
        if heading and heading.group(1) != "Summary":
            events.append(("part", heading.group(1), None))
            continue

        link = SUMMARY_LINK_RE.match(raw_line)
        if not link:
            continue

        indent = len(link.group("indent").replace("\t", "    "))
        events.append(("file", link.group("path"), indent))

    return events


def main() -> None:
    args = parse_args()
    summary = args.summary
    src_dir = args.src_dir
    output = args.output
    code_report_path = args.code_report

    output.parent.mkdir(parents=True, exist_ok=True)
    code_report_path.parent.mkdir(parents=True, exist_ok=True)

    chunks: list[str] = [
        "<!-- Generated by scripts/mdbook_to_pandoc.py. Do not edit directly. -->\n",
        r"\pagenumbering{gobble}",
        title_page(build_date_text()),
        blank_page(),
        r"\frontmatter",
    ]
    code_report: list[str] = []
    in_mainmatter = False
    toc_inserted = False
    appendix_active = False

    for event_type, value, indent in parse_summary(summary):
        if event_type == "part":
            if not in_mainmatter:
                if not toc_inserted:
                    chunks.append(table_of_contents())
                    toc_inserted = True
                chunks.append(r"\mainmatter")
                in_mainmatter = True
            chunks.append(part_page(value or ""))
            continue

        if not value:
            continue

        source = src_dir / value
        if not source.exists():
            raise FileNotFoundError(source)

        is_foreword = value == "foreword.md"
        is_chapter = indent == 0
        if is_chapter:
            # 附錄章不顯示「第N章」,只顯示章名(樣式定義在 print/header.tex)
            is_appendix = value.startswith("appendix")
            if is_appendix and not appendix_active:
                chunks.append("\\clearpage\n\\AppendixChapterStyle")
                appendix_active = True
            elif not is_appendix and appendix_active:
                chunks.append("\\clearpage\n\\StandardChapterStyle")
                appendix_active = False
        heading_shift = 0 if is_chapter or is_foreword else 1
        first_heading_attrs = "{.unnumbered}" if is_foreword else None
        chunks.append(
            rewrite_markdown(
                source.read_text(encoding="utf-8"),
                source=source,
                heading_shift=heading_shift,
                first_heading_attrs=first_heading_attrs,
                code_line_limit=args.code_line_limit,
                code_report=code_report,
            )
        )

    output.write_text("\n\n".join(chunks).rstrip() + "\n", encoding="utf-8")

    if code_report:
        header = [
            f"Code lines wider than {args.code_line_limit} cells after mdBook hidden lines are removed:",
            "",
        ]
        code_report_path.write_text("\n".join(header + code_report) + "\n", encoding="utf-8")
    else:
        code_report_path.write_text(
            f"No code lines wider than {args.code_line_limit} cells after mdBook hidden lines are removed.\n",
            encoding="utf-8",
        )


if __name__ == "__main__":
    main()
