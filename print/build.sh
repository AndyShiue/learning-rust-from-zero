#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

MANUSCRIPT="build/print/manuscript.md"
TEX="build/print/rust-book-a4.tex"
PDF="book/rust-book-a4.pdf"
CODE_REPORT="build/print/code-lines.txt"
CODE_LINE_LIMIT="${CODE_LINE_LIMIT:-96}"

mkdir -p build/print book

python3 scripts/mdbook_to_pandoc.py \
  --summary src/SUMMARY.md \
  --src-dir src \
  --output "$MANUSCRIPT" \
  --code-report "$CODE_REPORT" \
  --code-line-limit "$CODE_LINE_LIMIT"

if ! command -v pandoc >/dev/null 2>&1; then
  echo "pandoc was not found. Install it with: brew install pandoc" >&2
  exit 127
fi

if ! command -v xelatex >/dev/null 2>&1; then
  echo "xelatex was not found. Install MacTeX or BasicTeX, then ensure /Library/TeX/texbin is in PATH." >&2
  exit 127
fi

pandoc "$MANUSCRIPT" \
  --standalone \
  --from markdown+fenced_code_attributes+raw_tex+smart \
  --top-level-division=chapter \
  --toc \
  --toc-depth=2 \
  --number-sections \
  --metadata-file=print/metadata.yaml \
  --include-in-header=print/header.tex \
  --highlight-style=tango \
  --resource-path=.:src \
  --output "$TEX"

python3 scripts/postprocess_print_tex.py "$TEX"

xelatex -interaction=nonstopmode -halt-on-error -output-directory build/print "$TEX"
xelatex -interaction=nonstopmode -halt-on-error -output-directory build/print "$TEX"
cp build/print/rust-book-a4.pdf "$PDF"

echo "PDF: $PDF"
echo "TeX: $TEX"
echo "Code line report: $CODE_REPORT"
