# Building the books

This repository contains English (`en/`) and Traditional Chinese (`zh-TW/`)
mdBook editions. Each edition also has a Pandoc-based pipeline for producing an
A4 PDF. The deployment workflow in `.github/workflows/deploy.yml` runs the
tests, builds, packaging, and site-publication steps described here.

## Requirements

CI pins Rust and mdBook so a new upstream release cannot unexpectedly change
the generated books. Install the same versions and select the pinned Rust
toolchain for the current shell:

```bash
rustup toolchain install 1.97.1 --profile minimal --no-self-update
export RUSTUP_TOOLCHAIN=1.97.1
cargo install mdbook --version 0.5.4 --locked
```

Keep these values aligned with `RUST_VERSION`, `RUSTUP_TOOLCHAIN`, and
`MDBOOK_VERSION` in `.github/workflows/deploy.yml`. Update the pins only after
the new versions have passed the tests and builds for both editions.

The complete pipeline also requires Bash, Python 3, `curl`, `zip`, Pandoc,
XeLaTeX, JetBrains Mono, Noto Sans, Noto CJK, and an emoji or symbol font.

On Ubuntu/Debian, install the non-Rust dependencies with:

```bash
sudo apt-get update
sudo apt-get install -y \
  python3 \
  curl \
  zip \
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
brew install python pandoc
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
(cd zh-TW && mdbook test -L ../test-deps/target/debug/deps)
(cd en && mdbook test -L ../test-deps/target/debug/deps)
```

## HTML books

Build both mdBook sites from the repository root:

```bash
(cd zh-TW && mdbook build)
(cd en && mdbook build)
```

The generated sites are written to `zh-TW/book/` and `en/book/`.

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
bash zh-TW/print/build.sh
bash en/print/build.sh
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

The title page of both editions also includes a small Creative Commons
BY-NC-ND 4.0 button in the lower-right corner, with the official license URL
underneath. The standard button is kept at
`assets/cc-by-nc-nd-4.0-88x31.png`, downloaded from the Creative Commons
press-kit URL `https://mirrors.creativecommons.org/presskit/buttons/88x31/png/by-nc-nd.png`.
The PDF link points to `https://creativecommons.org/licenses/by-nc-nd/4.0/`.

The default visible code-line limit is 96 characters for Traditional Chinese
and 95 characters for English. Override it for an individual build when needed:

```bash
CODE_LINE_LIMIT=100 bash en/print/build.sh
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
(cd zh-TW && cp book/rust-book-a4.pdf book/book.pdf)
(cd zh-TW/src && zip -r ../book/rust-book-src.zip .)
(cd en && cp book/rust-book-a4.pdf book/book.pdf)
(cd en/src && zip -r ../book/rust-book-src.zip .)
```

Run these locally when reproducing the complete published artifact or checking
the downloads. The HTML and A4 PDF builds themselves do not depend on them.

## Assemble the published site

The `en/book/` and `zh-TW/book/` directories are intermediate mdBook outputs.
GitHub Pages receives a separate `public/` tree containing both editions,
reader downloads, and the repository's shared landing-page assets. After both
HTML books, PDFs, and reader downloads have been built, assemble that tree from
the repository root:

```bash
rm -rf public
mkdir -p public
cp index.html public/index.html
cp favicon.svg public/favicon.svg
cp 404.html public/404.html
cp robots.txt public/robots.txt
cp -r zh-TW/book public/zh-TW
cp -r en/book public/en
```

Then run the publication scripts in this order:

```bash
python3 scripts/normalize_public_urls.py public
python3 scripts/add_seo_metadata.py public
python3 scripts/generate_sitemap.py public
```

The URL normalizer creates prefix-free lesson aliases, rewrites the generated
HTML and mdBook sidebar links, and leaves redirects at the old numbered paths.
The metadata script then adds canonical, language-alternate, Open Graph, and
Twitter metadata to the canonical pages. Finally, the sitemap generator lists
the canonical pages while excluding redirects, `404.html`, and mdBook's
`print.html` pages. Run all three only after both language directories have
been copied into `public/`; the normalizer requires both editions.

The resulting `public/` directory is the artifact uploaded to GitHub Pages.
It is generated output and can be removed and rebuilt at any time.
