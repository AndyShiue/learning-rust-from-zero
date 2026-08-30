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
rustup toolchain install 1.98.0 --profile minimal --no-self-update
export RUSTUP_TOOLCHAIN=1.98.0
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
sudo apt-get install -y --no-install-recommends \
  python3 \
  curl \
  zip \
  pandoc \
  texlive-xetex \
  texlive-lang-chinese \
  lmodern \
  fonts-jetbrains-mono \
  fonts-noto-core \
  fonts-noto-cjk \
  fonts-symbola
```

CI omits `fonts-noto-cjk` because it downloads and verifies the pinned
Traditional Chinese font files described below. Keep the system package for
local builds unless you download those files too.

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

## Bilingual source mirror

Before testing or building the books, verify that the English and Traditional
Chinese source trees still have matching paths and structure:

```bash
python3 scripts/check_bilingual_mirror.py
```

The check compares the source paths, ordered `SUMMARY.md` links, heading-level
sequences, code-fence attributes, local Markdown links, and standard lesson
sections. It also rejects broken local Markdown links. It does not judge
translation accuracy or whether localized code comments and messages have the
same meaning; those still require human review.

## Shared mdBook theme assets

Both editions use the same favicon, code-block fixes, and sharing interface.
Their single source of truth is the root `favicon.svg` plus `assets/mdbook/`.
Populate the generated, Git-ignored edition `theme/` directories after a fresh
checkout or whenever one of those shared files changes:

```bash
python3 -B scripts/prepare_mdbook_assets.py
```

Run this before `mdbook build` or `mdbook serve`. The deployment workflow runs
it automatically.

## Test dependencies

Both editions share the external crates declared in the root `test-deps/`
crate. The committed `test-deps/Cargo.lock` keeps CI dependency resolution
reproducible. Build the locked dependencies once before running the mdBook
tests:

```bash
cargo build --locked --manifest-path test-deps/Cargo.toml
```

Then test both editions against the same compiled dependencies:

```bash
(cd zh-TW && mdbook test -L ../test-deps/target/debug/deps)
(cd en && mdbook test -L ../test-deps/target/debug/deps)
```

## HTML books

Build both mdBook sites from the repository root:

```bash
python3 -B scripts/prepare_mdbook_assets.py
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

The workflow pins these files to Noto CJK revision
`f8d157532fbfaeda587e826d4cd5b21a49186f7c` and verifies their SHA-256 checksums
before building either PDF.

The shared `print/header.tex` loads these files when present; each edition keeps
a tiny wrapper that supplies its localized chapter label. This prevents Ubuntu
from resolving the Pan-CJK Noto collection to Japanese faces such as
`NotoSansCJKjp-*`.

Installed Noto CJK fonts are usually sufficient for local builds. To reproduce
the GitHub Actions font selection exactly, download the same three files into
`build/fonts/`. The root `build/` directory is ignored by Git.

## A4 PDFs

Run either print pipeline from the repository root:

```bash
bash scripts/build_print.sh zh-TW
bash scripts/build_print.sh en
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

The default visible code-line limit is 95 characters for both editions.
Override it for an individual build when needed:

```bash
CODE_LINE_LIMIT=100 bash scripts/build_print.sh en
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

## IndexNow notifications

The deployment workflow notifies IndexNow after GitHub Pages has published the
new artifact. Configure an Actions repository secret named `INDEXNOW_KEY`
before running the workflow. Its value must contain 8-128 letters, numbers, or
hyphens. With the GitHub CLI, run the following command and enter the key at the
prompt so it is not stored in the repository:

```bash
gh secret set INDEXNOW_KEY
```

During deployment, the workflow writes the verification file to the root of
the project site inside `public/`, deploys it with the rest of the site, and
then runs:

```bash
python3 scripts/submit_indexnow.py public --before <base-commit> --after <head-commit>
```

The checkout uses full Git history so the script can compare the two commits.
Ordinary deployments notify IndexNow only about added, changed, deleted, or
renamed public pages. Changes to the URL normalization, SEO metadata, sitemap,
or IndexNow scripts submit all canonical sitemap URLs. Noncanonical foreword
aliases are excluded. A newly deployed key may briefly return HTTP 403 while
the verification file propagates, so the script retries that response.
If the key is missing or invalid, the workflow skips the IndexNow notification
and deploys Pages with a warning. A later IndexNow submission failure is also
reported as a warning without changing the successful Pages deployment result.

To inspect the selected URLs locally without sending a notification, first
assemble `public/` and generate its sitemap, then run:

```bash
python3 scripts/submit_indexnow.py public --before <base-commit> --after <head-commit> --dry-run
python3 scripts/submit_indexnow.py public --all --dry-run
```
