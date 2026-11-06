# Chapter 10 — Cookbook: Windows ↔ Mac Side by Side

No chapter-length tour. Just the moves, labeled, with the preview line and the commit line always shown separately. `python` = Windows PowerShell spelling; Macs use `python3` (Chapter 1).

## Rename

```powershell
# Windows PowerShell - WhatIf previews; Remove it to commit
Get-ChildItem IMG_*.jpg | Rename-Item -WhatIf -NewName { $_.Name -replace 'IMG_','IMG-' }
Get-ChildItem IMG_*.jpg | Rename-Item -NewName { $_.Name -replace 'IMG_','IMG-' }
```
```bash
# Mac bash — echo previews; remove echo to commit
for f in IMG_*.jpg; do echo mv "$f" "${f/IMG_/IMG-}"; done
for f in IMG_*.jpg; do mv "$f" "${f/IMG_/IMG-}"; done
```

Tested one-command version (preview built in; add `--do-it` when happy):

```bash
python scripts/batch_rename.py . --action replace --old IMG_ --old2 IMG-
```

## Join / split CSVs

```bash
# Mac snapshot
cat *.csv > all.csv          # headers get pasted too - see Ch 4 caveat
```
```powershell
# Windows snapshot
Get-Content *.csv | Set-Content all.csv
```

```bash
python scripts/join_csv.py . --out ../all.csv        # tested, one-header, refuses to clobber
python scripts/split_csv.py big.csv --rows 500 --do-it
```

## Merge / split PDFs (`pip install pypdf` first)

```bash
python scripts/join_pdfs.py --folder ~/Desktop/invoices --out ~/Desktop/all.pdf
python scripts/split_pdfs.py ~/Desktop/big-scan.pdf --every 25 --do-it
```

Mac one-liner fallback (prebuilt into macOS):

```bash
"/System/Library/Automator/Combine PDF Pages.action/Contents/MacOS/join" -o merged.pdf *.pdf
```

## Resize images (`pip install Pillow` first)

```bash
python scripts/resize_images.py ~/Pictures/photos --max-edge 1600 --do-it
```

Mac snapshot — note this one *overwrites*, so redirect output:

```bash
mkdir -p small
sips -Z 1600 ~/Pictures/photos/*.jpg --out small
```

(Windows built-ins: see Chapter 6.)

## Unzip a folder

```powershell
Get-ChildItem *.zip | ForEach-Object { Expand-Archive $_.FullName -DestinationPath ($_.BaseName) }
```
```bash
for z in *.zip; do unzip -q "$z" -d "${z%.zip}"; done
```

## Sort the Downloads folder

```bash
python scripts/sort_folder.py ~/Downloads      # preview, then --do-it
python scripts/sort_folder.py ~/Downloads --do-it --by-year
```

```powershell
# Windows snapshot (one rule; the tested script encodes the whole rulebook)
New-Item -ItemType Directory -Force pdfs
Get-ChildItem *.pdf | Move-Item -Destination pdfs
```

## Run all the tests, prove the toolkit to yourself

```bash
python -m unittest discover -s tests        # Mac: python3 -m unittest discover -s tests
```

## The whole book in one sentence

Preview, read it, `--do-it`. Every time, on every tool, forever.
