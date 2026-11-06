# Chapter 4 — Joining and Splitting CSV Files

Every shipper, bank, and eBay seller exports spreadsheets by the month. Then Q1 tax prep arrives and you need one file with all three. Or: an online store happily accepts 500 rows at a time, and your export has 4,000. Join and split, by rule, not by dozens of copy-pastes.

## Joining: `scripts/join_csv.py`

**Preview:**

```bash
python scripts/join_csv.py ~/Desktop/bookkeeping --out ~/Desktop/q1-combined.csv
```

```
Files to join: 3
  jan.csv
  feb.csv
  mar.csv
Header: date,description,amount
Data rows in output: 412
Output file: ~/Desktop/q1-combined.csv

Dry run: nothing was written yet. Happy? Add --do-it.
```

**Commit with `--do-it`.** Two built-in rails worth knowing:

- **Header matching.** Every file's header row must be identical, or that file is *skipped* and reported — a mismatched file can't silently corrupt the combined table.
- **No clobbering.** If `q1-combined.csv` already exists, the script refuses instead of overwriting it.

Only join files whose headers really are the same (same columns, same order). The script enforces this; do the same by eye when you use the snapshots below.

**Windows PowerShell snapshot:**

```powershell
Get-Content jan.csv, feb.csv, mar.csv | Set-Content q1-combined.csv
```

Caveat: this pastes every file's *header* too, so you'll get three header rows total. Fine for re-opening in Excel and deleting two junk rows; not fine for pricing software. The tested script keeps exactly one header. (Notice which option you choose for tax files.)

**Mac bash snapshot:** `cat jan.csv feb.csv mar.csv > q1-combined.csv` — same header caveat, same remedy.

## Splitting: `scripts/split_csv.py`

Split a big CSV into pieces of N data rows (the header row is repeated in every piece — required for them to each still open sanely):

```bash
python scripts/split_csv.py ~/Desktop/orders/all-orders.csv --rows 500
```

```
Input: all-orders.csv (4,000 data rows)
Will write 8 piece(s), up to 500 data rows each:
  all-orders_001.csv  (500 rows, header + 500 lines)
  ...
Dry run: nothing was written yet. Happy? Add --do-it.
```

Refuses to overwrite existing pieces; run twice, nothing twice-written.

## Verify, don't hope

After joining, sanity-check by line count:

```bash
# Mac
wc -l ~/Desktop/q1-combined.csv
```
```powershell
# Windows
(Get-Content $HOME\Desktop\q1-combined.csv).Count
```

Data rows should equal the sum the preview promised. A bookkeeping file that's short by 37 rows is a job for now, not tax season.

## One more rail: character sets

Exports from older systems sometimes aren't UTF-8, and accented names (`José`, `naïve`) find out. The tested script reads with a tolerant decoder and writes UTF-8. If you ever get weird single-character garbage at the start of a file (`ï»¿`), that's a byte-order mark left by Windows software; the handled scripts swallow it, most plain `cat` joins don't.
