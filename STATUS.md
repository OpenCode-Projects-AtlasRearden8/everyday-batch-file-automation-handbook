# STATUS — Everyday Batch-File Automation Handbook

Built 2026-11-06 by Asdale Dynamics, LLC (Dylan Asdale, RN turned AI author — plain English, never condescending).

## What was built

A beginner-friendly manual for one-off batch file jobs (mass renames, CSV/PDF join & split, image resize/convert, folder rules, other conversions), with **tested scripts instead of prose promises**, plus a static HTML site generated from the Markdown chapters.

- `docs/` — ten Markdown chapters: start here, safety first (dry-run habit), mass renames, CSV join/split, PDF join/split, image resize/convert, other format conversions, folder rules, AI-as-script-co-pilot, Windows/Mac side-by-side cookbook.
- `scripts/` — eight command-line tools, all following the same safety rails: **dry run by default**, `--do-it` to commit, **never overwrite** (collisions cancel the whole run, exit code 2), **never delete** (unknown files go to `_unsorted/`):
  - `batch_rename.py` — replace/prefix/suffix/case/sequence renames, `--match` filtering, numbered output.
  - `join_csv.py` — merge CSVs with identical headers; mismatched files skipped and reported.
  - `split_csv.py` — chunk a big CSV by data-row count, header repeated in every piece.
  - `join_pdfs.py` — merge PDFs (files in explicit order, or a folder); needs `pypdf`.
  - `split_pdfs.py` — one page per piece or chunks of N pages; needs `pypdf`.
  - `resize_images.py` — max-edge / width / height resizing, format change, `*_small` copies (originals never touched unless `--replace`); needs `Pillow`.
  - `convert_images.py` — png/jpg/webp conversion, originals always kept; needs `Pillow`.
  - `sort_folder.py` — the "folder rules" engine by extension, `_unsorted/` catch-all, optional `--by-year`.
- `build_site.py` — regenerates every page in `site/` from `docs/` + `README.md` with a shared stylesheet and chapter nav.
- `site/` — the 11 built HTML pages (committed).
- `tests/` — 28 automated tests (`unittest`): dry-run-changes-nothing, collision-cancels-everything, no-overwrite-fails-loudly, CSV split/join round-trip, PDF page counts, image dimensions/format, folder rules with `_unsorted/` behavior, plus doc-consistency (every script referenced in docs exists; every promised chapter exists; LICENSE/README credits, site build runs and includes every page).
- `README.md` — credits **Asdale Dynamics, LLC**; quick start; verification; repo layout.
- `LICENSE` — MIT, copyright line exactly `Copyright (c) 2026 Asdale Dynamics, LLC`.

## How to run it

```bash
# Read a chapter, then (from the repo root):
python scripts/batch_rename.py ~/Pictures/shots --action replace --old IMG_ --old2 lab-   # preview
python scripts/batch_rename.py ~/Pictures/shots --action replace --old IMG_ --old2 lab- --do-it   # commit

# Optional helpers (PDF/image chapters print this instruction if missing):
pip install pypdf Pillow

# Site
python build_site.py
```

Macs use `python3` instead of `python`. All scripts show `--help` with examples.

## Verification results

- `python -m unittest discover -s tests` → **Ran 28 tests — OK** (0 failures; PDF/image tests cover the real libraries).
- `python build_site.py` → **Built site/ with 11 pages** and nav verified active-per-page.
- End-to-end sandbox demo run of every script: dry-run previews printed, `--do-it` behaved, join order honored (oct→nov), mismatched CSV skipped and reported, folder sort produced `images/ data/ media/ archives/ documents/ _unsorted/` with nothing deleted.
- Scripts are stdlib-only except pypdf/Pillow chapters; missing helpers produce friendly install instructions instead of tracebacks.

## Known gaps

- Word/Pages/ODT and QuickBooks-format conversions intentionally not scripted (native-application rule, Ch. 7).
- `sort_folder.py` rules are fixed by extension; no `--rules` config file yet (Ch. 9 invites AI co-pilot adaptations).
- Windows PowerShell snippets in the cookbook were reviewed but cannot be executed in this build environment; the tested-and-executed path is the Python scripts.
- Only stdlib tests; no packaging (no pyproject) since these are copy-paste scripts by design.
- No CI config and no remote — committed locally only, per instructions (never pushed, never published).
