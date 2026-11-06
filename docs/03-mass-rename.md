# Chapter 3 — Mass Renames

The classic: 214 photos named `IMG_4821.jpg`...`IMG_5034.jpg` that should say what they are. Or receipts named `untitled-1.pdf` when they should say `2026-10-15-crane-supply.pdf`. Renaming by hand is a wrist injury; renaming by rule is one command.

## The tested script: `scripts/batch_rename.py`

Every rename in this chapter is one script with one preview step.

**Preview the plan (dry run — nothing changes):**

```bash
python scripts/batch_rename.py ~/Pictures/shots --action replace --old IMG_ --old2 lab-
```

It prints each planned pair:

```
WOULD RENAME  IMG_4821.jpg  ->  lab-4821.jpg
...
Dry run: 214 file(s) would be renamed. Nothing changed yet.
Happy? Run the same command again with --do-it at the end.
```

**Agree with the plan? Run the identical command with `--do-it`:**

```bash
python scripts/batch_rename.py ~/Pictures/shots --action replace --old IMG_ --old2 lab- --do-it
```

Mac readers: on a Mac use `python3 scripts/...` instead of `python scripts/...` throughout this book.

## All the moves it knows

| Rule | Command |
| --- | --- |
| Replace text in names | `--action replace --old IMG_ --old2 lab-` |
| Add a prefix (`prefix 2026-11- `) | `--action prefix --chunk "2026-11- "` |
| Add a suffix (`taxes_final 2026`) | `--action suffix --chunk " 2026"` |
| All lowercase / uppercase | `--action lower` / `--action upper` |
| Number everything (`Report_001.pdf`) | `--action sequence --chunk "Report_{:04d}"` |
| Only touch some files | add `--match "*.jpg"` to any rule |
| Start numbering at 50 | add `--seq-start 50` |

The sequence placeholder `{:04d}` means "the number, padded so it's four digits" — `1` becomes `0001`. That keeps `Report_0007` sorting before `Report_0012`.

## The image-only, zero-Python paths

**Windows PowerShell** (dry run built in via `-WhatIf`):

```powershell
Get-ChildItem IMG_*.jpg | Rename-Item -WhatIf -NewName { $_.Name -replace 'IMG_','IMG-' }
# happy? remove -WhatIf
Get-ChildItem IMG_*.jpg | Rename-Item -NewName { $_.Name -replace 'IMG_','IMG-' }
```

**Mac bash:**

```bash
for f in IMG_*.jpg; do echo mv "$f" "${f/IMG_/IMG-}"; done   # echo = preview
for f in IMG_*.jpg; do mv "$f" "${f/IMG_/IMG-}"; done
```

Notice both snippets have a preview line and a commit line, exactly like the tested script. Adopt that pattern everywhere — it's the point of Chapter 2.

## Guardrails you get for free

- **Collision cancels the run.** If two files would land on the same name (say, `lower` on `A.txt` and `a.txt`), the script stops with exit code 2 and touches nothing.
- **Existing files are never overwritten.** Rename `IMG_1.jpg` to `IMG-1.jpg` when `IMG-1.jpg` already exists? Refused.
- **Sorted for numbering.** `sequence` numbers files alphabetically, so `mid.jpg` eating `Report_0002` from between `alpha` and `zeta` is a *choice* you can see in the preview.

## When the names are more complicated

When the rule involves dates inside filenames, regex patterns, or pulling names from a spreadsheet, stop and go to **Chapter 9**: hand the mess to an AI co-pilot with the safety rails embedded. Roll-your-own regex on 500 files without a dry run is how weekends vanish.
