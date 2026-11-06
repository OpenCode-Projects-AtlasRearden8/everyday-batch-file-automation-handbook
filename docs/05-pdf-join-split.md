# Chapter 5 — Merging and Splitting PDFs

CE certificates, invoices, scan bundles, chapter drafts — PDFs pile up in exactly the two shapes: you have *many and want one* (merge), or you have *one 400-page scan and need to send page 38* (split).

## One-time setup

These two scripts use one free helper (Python's tool installer is covered in the pypdf error message if you skip this):

```bash
pip install pypdf        # Mac: pip3 install pypdf
```

In Windows PowerShell, if `pip install pypdf` says it isn't a command, use `python -m pip install pypdf`.

## Merging: `scripts/join_pdfs.py`

**Two ways to list the inputs.** Name them in the exact merge order:

```bash
python scripts/join_pdfs.py jan-invoices.pdf feb-invoices.pdf --out q1-invoices.pdf
```

or take a whole folder, alphabetically:

```bash
python scripts/join_pdfs.py --folder ~/Desktop/invoices --out ~/Desktop/all-2026.pdf
```

Preview → `--do-it`. The preview makes the *order* visible, which matters: merged PDFs read top to bottom in the order listed, and `jan → feb → mar` vs alphabetical `feb → jan → mar` is a very different document.

Free rails: files with mismatched problems (encrypted, unreadable, zero pages) are **skipped and reported**, not silently merged; an existing output file is **refused**, not overwritten.

## Splitting: `scripts/split_pdfs.py`

One output file per page (default), or every N pages as a chunk:

```bash
python scripts/split_pdfs.py ~/Desktop/big-scan.pdf --out ~/Desktop/pages --do-it
python scripts/split_pdfs.py ~/Desktop/big-scan.pdf --every 25 --do-it
```

Output names carry the page ranges (`big-scan_0004-0004.pdf`) so humans can find page 38 below.

## The no-Python fallbacks

**Mac** ships a PDF hammer built in — `sips` and Quartz. This one-liner merges PDFs right in Terminal and has existed for years (still the most reliable on most Macs):

```bash
"/System/Library/Automator/Combine PDF Pages.action/Contents/MacOS/join" -o merged.pdf *.pdf
```

Macs also merge in Preview.app by hand: open the first PDF, View > Thumbnails, drag the other PDFs into the sidebar. Hand-merging is fine for 3 files; at 30 files the command wins.

**Windows** has no built-in merge; the free classic is **PDF24 Creator** (offline desktop app). If you'd rather not install anything, that's what this handbook's script is for: `pip install pypdf` once, then you never think about it again.

Splitting PDFs server-side via random websites deserves a special warning:

> **Do not upload documents with personal or client data to free online PDF tools.** "Just this once" is how incidents happen. Local tools, local data.

## Verify, don't hope

After a merge, check the page count matches the preview's "Total pages in output":

```bash
# Mac — prints pages-PDF-title per file; Windows PowerShell shows the same via Get-Item .Length comparisons is overkill: just open the file.
mdls -name kMDItemNumberOfPages merged.pdf
```

Or simply open it and look. The preview in the tested script counts pages before writing; trust but spot-check.
