#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIRECTORY="${BASH_SOURCE[0]%/*}"
if [ "$SCRIPT_DIRECTORY" = "${BASH_SOURCE[0]}" ]; then
  SCRIPT_DIRECTORY="."
fi
REPOSITORY_ROOT="$(cd "$SCRIPT_DIRECTORY/.." && pwd)"
EDITION="${1:-}"
DEFAULT_CODE_LINE_LIMIT=95

case "$EDITION" in
  en|zh-TW)
    ;;
  *)
    echo "Usage: bash scripts/build_print.sh {en|zh-TW}" >&2
    exit 2
    ;;
esac

BOOK_ROOT="$REPOSITORY_ROOT/$EDITION"
cd "$BOOK_ROOT"

MANUSCRIPT="build/print/manuscript.md"
TEX="build/print/rust-book-a4.tex"
PDF="book/rust-book-a4.pdf"
CODE_REPORT="build/print/code-lines.txt"
CODE_LINE_LIMIT="${CODE_LINE_LIMIT:-$DEFAULT_CODE_LINE_LIMIT}"
CC_BADGE_PATH="../assets/cc-by-nc-nd-4.0-88x31.png"

mkdir -p build/print book

if [ ! -s "$CC_BADGE_PATH" ]; then
  echo "Creative Commons badge is missing: $CC_BADGE_PATH" >&2
  exit 1
fi

python3 ../scripts/mdbook_to_pandoc.py \
  --language "$EDITION" \
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
  --from markdown+fenced_code_attributes+raw_tex+smart+lists_without_preceding_blankline \
  --top-level-division=chapter \
  --number-sections \
  --metadata-file=print/metadata.yaml \
  --include-in-header=print/header.tex \
  --highlight-style=tango \
  --columns=120 \
  --resource-path=.:src \
  --output "$TEX"

python3 ../scripts/postprocess_print_tex.py "$TEX"

xelatex -interaction=nonstopmode -halt-on-error -output-directory build/print "$TEX"
xelatex -interaction=nonstopmode -halt-on-error -output-directory build/print "$TEX"
cp build/print/rust-book-a4.pdf "$PDF"

echo "PDF: $PDF"
echo "TeX: $TEX"
echo "Code line report: $CODE_REPORT"
