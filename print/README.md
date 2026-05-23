# A4 print build

This directory contains the Pandoc-based print pipeline for the A4 paper edition.

## Requirements

GitHub Actions builds the PDF on Ubuntu with the dependencies declared in
`.github/workflows/build-print.yml`. For local builds, install Pandoc, XeLaTeX,
and Noto CJK fonts.

On Ubuntu/Debian:

```bash
sudo apt-get update
sudo apt-get install -y \
  pandoc \
  poppler-utils \
  texlive-xetex \
  texlive-latex-extra \
  texlive-lang-chinese \
  texlive-fonts-recommended \
  fonts-noto \
  fonts-noto-cjk
```

On macOS:

```bash
brew install pandoc
brew install --cask mactex-no-gui
brew install --cask font-noto-serif font-noto-sans font-noto-sans-mono-cjk-tc font-noto-serif-cjk-tc
```

If `xelatex` is not found after installing MacTeX, add this to your shell profile:

```bash
export PATH="/Library/TeX/texbin:$PATH"
```

## Build

```bash
./print/build.sh
```

Outputs:

- `book/rust-book-a4.pdf`
- `build/print/rust-book-a4.tex`
- `build/print/manuscript.md`
- `build/print/code-lines.txt`

The build uses `src/SUMMARY.md` as the source of truth:

- first-level summary items become chapters and start on a new page;
- nested lesson files become sections and do not force page breaks;
- `第壹部` and `第貳部` become standalone centered part pages.

The code line report lists visible code lines wider than the configured A4 line limit. Override the limit when needed:

```bash
CODE_LINE_LIMIT=100 ./print/build.sh
```
