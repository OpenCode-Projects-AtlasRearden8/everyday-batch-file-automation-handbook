# Chapter 8 — Folder Rules: Taming a Wild Downloads Folder

A Downloads folder with 900 items is a to-do list written in someone else's handwriting. The fix is rules: *this kind of file lives there; this kind goes here; anything I don't recognize waits in one pile I'll see.* One command, run occasionally, forever.

## The tested script: `scripts/sort_folder.py`

```bash
python scripts/sort_folder.py ~/Downloads
```

```
Plan for Downloads — 312 file(s) would move:
  archives/    <- 19 file(s)
  bookkeeping/ <- 6 file(s)
  code/        <- 2 file(s)
  data/        <- 41 file(s)
  documents/   <- 113 file(s)
  images/      <- 87 file(s)
  media/       <- 22 file(s)
  _unsorted/   <- 22 file(s)

Dry run: nothing changed yet. Contents are moved, never deleted or edited.
Happy? Run the same command again with --do-it at the end.
```

Then add `--do-it` when the plan reads right.

## The rules, in plain view

| File ends in... | Lands in |
| --- | --- |
| jpg, png, gif, psd, heic... | `images/` |
| pdf, docx, txt, epub, md... | `documents/` |
| csv, xlsx, json... | `data/` |
| mp4, mp3, wav, mov... | `media/` |
| zip, rar, 7z, dmg, exe... | `archives/` |
| py, js, html, bat... | `code/` |
| qbo, ofx, qif (bank/QuickBooks exports) | `bookkeeping/` |
| anything else | `_unsorted/` |

Rails, all present: extensions never deleted; name collisions get `-1`, `-2` suffixes instead of overwrites; anything weird is parked in `_unsorted/` where you can see it. Add `--by-year` to sort *inside* each rule folder by year (`documents/2024/`, `documents/2025/`) — the difference between "2026 tax box" and archival dirt.

## The zero-Python snapshots

**Mac bash:**

```bash
mkdir -p pdfs images other
for f in *.pdf; do echo mv "$f" pdfs/; done   # preview
for f in *.pdf; do mv "$f" pdfs/; done
for f in *.jpg *.png; do mv "$f" images/; done
for f in *; do mv "$f" other/; done 2>/dev/null   # leftovers, never delete
```

**Windows PowerShell:**

```powershell
New-Item -ItemType Directory -Force pdfs
Get-ChildItem *.pdf | Move-Item -Destination pdfs
```

Both versions move-only. If you catch yourself writing `rm`, `del`, or `-Force` into a folder-cleanup command, close the laptop and start over (Chapter 2).

## Why `_unsorted/` is the whole design

The mistake old cleanup scripts made: `else` bucket = delete. Unknown file types are exactly the files that matter — the odd `.eml` your pension provider sent, the `.qbx` Accountant's Copy, the `.pem` you shouldn't have on the Desktop at all. Park everything you can't classify in plain sight, and *decide by hand*. Sorting folders is a checklist, not a shredder.

## Make it a habit, not a vigil

Run the preview weekly. It's 3 seconds. If the plan is boring, say so and do nothing — a dry run that shows "already tidy" is the automation equivalent of a smoke detector that is silent.
