# Chapter 7 — Other Format Conversions (Text, Docs, Archives)

The images, PDFs, and CSVs had their chapters. The stragglers — converting a `.txt` to UTF-8 the fancy reading app accepts, unzipping forty archives, pushing fifty `.pages` documents into something the printer understands — live here. Short chapter, mostly because honest advice is: *these jobs narrow fast, and the tested-script habit is worth carrying into them.*

## The honest map

| Job | Winner |
| --- | --- |
| Text encoding (`latin-1` → UTF-8) | Python one-liner or ask the AI co-pilot |
| Word/Pages/ODT → PDF | The *application*: Word "Save As"; Pages "Export." Batch-converts elegantly when the app can see all files at once |
| `.doc` → `.docx` | Same — the app, not a script |
| Unzip everything in a folder | Built-in zip tools + a loop (below) |
| Image and PDF and CSV conversions | Chapters 4–6 — you've already got them |

## Unzip everything (a classic)

**Mac bash:**

```bash
for z in *.zip; do echo unzip -q "$z" -d "${z%.zip}"; done   # preview
for z in *.zip; do unzip -q "$z" -d "${z%.zip}"; done
```

**Windows PowerShell:**

```powershell
Get-ChildItem *.zip | ForEach-Object { Expand-Archive -Path $_.FullName -DestinationPath $_.Name.Substring(0, $_.Name.Length - 4) }
```

`Expand-Archive` refuses to overwrite an existing `-DestinationPath`, which conveniently behaves like our never-overwrite rail — that's a *feature*, not an error to work around.

## Text encoding, the quiet threat

Symptom: you open a `.txt` and see `ï»¿` or black diamonds (`�`). That's an encoding mismatch, not corruption — the bytes were fine, the reader guessed the wrong dictionary. Fix by re-touching the file as UTF-8:

```bash
# Mac (iconv is preinstalled) — preview first with nm? Just do a couple of test files.
iconv -f WINDOWS-1252 -t UTF-8 one-old-file.txt > one-old-file.utf8.txt
```

No in-place overwrite until a sample file reads correctly in your app. Then it's a loop. (If asking an AI co-pilot, include "preview output before overwriting the original" in the request.)

## When conversions feel like too much

Some formats deserve a script you read carefully rather than one you trust: spreadsheet formats with formulas (`.xlsx` with `.qbo` financial data behind them), anything with digital signatures, anything for court or insurance. The converting disaster mode — dates turning into numbers (`3/1/26` → some integer), leading zeros eaten from ZIP codes — is software-specific and *silent*. When money or signatures are in play, open the files in the native app and export from there, even if it's slower.

## The rule this chapter really teaches

**Prefer converting *from* the original application when there is one.** Python + libraries are wonderful for the pile-shaped jobs (Chapters 3–6, 8). Single-file, high-stakes, format-specific jobs belong to Word, Excel, QuickBooks, and Pages. Knowing which is which *is* the skill.
