# Building the books

This repository contains English (`en/`) and Traditional Chinese (`zh-tw/`)
mdBook editions. Each edition also has a Pandoc-based pipeline for producing an
A4 PDF. The deployment workflow in `.github/workflows/deploy.yml` runs the same
tests and builds described here, plus the two packaging steps under
[Reader downloads](#reader-downloads).

## Requirements

Install the stable Rust toolchain and mdBook:

```bash
rustup update stable
cargo install mdbook
```

The PDF builds additionally require Pandoc, XeLaTeX, JetBrains Mono, Noto Sans,
Noto CJK, and an emoji or symbol font.

On Ubuntu/Debian, these packages match the GitHub Actions environment:

```bash
sudo apt-get update
sudo apt-get install -y \
  pandoc \
  texlive-xetex \
  texlive-latex-extra \
  texlive-lang-chinese \
  texlive-fonts-recommended \
  fonts-jetbrains-mono \
  fonts-noto-core \
  fonts-noto-cjk \
  fonts-symbola
```

On macOS:

```bash
brew install pandoc
brew install --cask \
  mactex-no-gui \
  font-jetbrains-mono \
  font-noto-sans \
  font-noto-sans-cjk-tc \
  font-noto-sans-mono-cjk-tc \
  font-noto-color-emoji
```

After installing MacTeX, restart the terminal. If `xelatex` is still not found,
refresh the shell paths with:

```bash
eval "$(/usr/libexec/path_helper)"
```

## Test dependencies

Both editions share the external crates declared in the root `test-deps/`
crate. Build them once before running the mdBook tests:

```bash
cargo build --manifest-path test-deps/Cargo.toml
```

Then test both editions against the same compiled dependencies:

```bash
(cd zh-tw && mdbook test -L ../test-deps/target/debug/deps)
(cd en && mdbook test -L ../test-deps/target/debug/deps)
```

## HTML books

Build both mdBook sites from the repository root:

```bash
(cd zh-tw && mdbook build)
(cd en && mdbook build)
```

The generated sites are written to `zh-tw/book/` and `en/book/`.

## Shared PDF fonts

GitHub Actions downloads the following Traditional Chinese font files into the
root `build/fonts/` directory:

- `NotoSansCJKtc-Regular.otf`
- `NotoSansCJKtc-Bold.otf`
- `NotoSansMonoCJKtc-Regular.otf`

Both editions' `print/header.tex` files load these shared files when present.
This prevents Ubuntu from resolving the Pan-CJK Noto collection to Japanese
faces such as `NotoSansCJKjp-*`.

Installed Noto CJK fonts are usually sufficient for local builds. To reproduce
the GitHub Actions font selection exactly, download the same three files into
`build/fonts/`. The root `build/` directory is ignored by Git.

## A4 PDFs

Run either print pipeline from the repository root:

```bash
./zh-tw/print/build.sh
./en/print/build.sh
```

Each edition writes these files beneath its own directory:

- `book/rust-book-a4.pdf`
- `build/print/rust-book-a4.tex`
- `build/print/manuscript.md`
- `build/print/code-lines.txt`

The print pipeline uses that edition's `src/SUMMARY.md` as its source of truth:

- first-level summary items become chapters and start on a new page;
- nested lesson files become sections and do not force page breaks;
- `Part I` and `Part II` (or `第一部` and `第二部`) become centered part pages.

The default visible code-line limit is 96 characters for Traditional Chinese
and 95 characters for English. Override it for an individual build when needed:

```bash
CODE_LINE_LIMIT=100 ./en/print/build.sh
```

Before deploying, the workflow also applies the fixed 95-character English PDF
gate:

```bash
(cd en && python3 scripts/check_pdf_code_lines.py)
```

## Reader downloads

Each edition's `foreword.md` points readers at a `book.pdf` and a
`rust-book-src.zip`. Neither name is produced by the commands above: the
deployment workflow creates them after the print pipeline runs, by copying the
A4 PDF to a stable name and zipping that edition's `src/`.

```bash
(cd zh-tw && cp book/rust-book-a4.pdf book/book.pdf)
(cd zh-tw/src && zip -r ../book/rust-book-src.zip .)
(cd en && cp book/rust-book-a4.pdf book/book.pdf)
(cd en/src && zip -r ../book/rust-book-src.zip .)
```

Run these locally only when you want to check those two downloads; nothing else
in the build depends on them.
