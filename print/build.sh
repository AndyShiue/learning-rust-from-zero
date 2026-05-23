#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

MANUSCRIPT="build/print/manuscript.md"
TEX="build/print/rust-book-a4.tex"
PDF="book/rust-book-a4.pdf"
CODE_REPORT="build/print/code-lines.txt"
CODE_LINE_LIMIT="${CODE_LINE_LIMIT:-104}"

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
  --syntax-highlighting=tango \
  --resource-path=.:src \
  --output "$TEX"

pandoc "$MANUSCRIPT" \
  --standalone \
  --from markdown+fenced_code_attributes+raw_tex+smart \
  --pdf-engine=xelatex \
  --pdf-engine-opt=-interaction=nonstopmode \
  --top-level-division=chapter \
  --toc \
  --toc-depth=2 \
  --number-sections \
  --metadata-file=print/metadata.yaml \
  --syntax-highlighting=tango \
  --resource-path=.:src \
  --output "$PDF"

echo "PDF: $PDF"
echo "TeX: $TEX"
echo "Code line report: $CODE_REPORT"
