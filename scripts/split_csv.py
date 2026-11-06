"""Split one big CSV file into smaller CSV files. Dry-run by default.

Examples:
    python scripts/split_csv.py ~/Desktop/orders/orders.csv --rows 500
    python scripts/split_csv.py ~/Desktop/orders/orders.csv --rows 500 --do-it
"""
import argparse
import csv
import sys
from pathlib import Path


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("csvfile", help="the big CSV file to split")
    ap.add_argument("--rows", type=int, required=True, help="data rows per output file (header not counted)")
    ap.add_argument("--out", help="folder for the output pieces (default: folder of the input file)")
    ap.add_argument("--do-it", action="store_true", help="actually write the pieces (omit to preview only)")
    args = ap.parse_args(argv)

    src = Path(args.csvfile).expanduser().resolve()
    if not src.is_file():
        ap.error(f"not a file: {src}")
    if args.rows < 1:
        ap.error("--rows must be at least 1")
    outdir = Path(args.out).expanduser().resolve() if args.out else src.parent

    with src.open("r", newline="", encoding="utf-8-sig") as f:
        header = next(csv.reader(f), None)
        all_rows = [row for row in csv.reader(f) if any(cell.strip() for cell in row)]
    if header is None:
        ap.error(f"that file has no rows to split: {src}")

    chunks = [all_rows[i:i + args.rows] for i in range(0, len(all_rows), args.rows)]
    names = [src.stem + f"_{i + 1:03d}.csv" for i in range(len(chunks))]
    for name in names:
        target = outdir / name
        if target.exists():
            ap.error(f"piece already exists, refusing to overwrite: {target}")

    print(f"Input: {src.name} ({len(all_rows)} data rows)")
    print(f"Output folder: {outdir}")
    print(f"Will write {len(chunks)} piece(s), up to {args.rows} data rows each:")
    for name, chunk in zip(names, chunks):
        print(f"  {name}  (header + {len(chunk)} data rows)")
    print("Every piece keeps the original header row.")

    if not args.do_it:
        print("\nDry run: nothing was written yet. Happy? Add --do-it.")
        return 0

    outdir.mkdir(parents=True, exist_ok=True)
    with src.open("r", newline="", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        header_real = next(reader, None)
        for i, name in enumerate(names):
            with (outdir / name).open("w", newline="", encoding="utf-8") as out:
                writer = csv.writer(out)
                if header_real:
                    writer.writerow(header_real)
                for row in chunks[i]:
                    writer.writerow(row)

    print(f"\nDone: wrote {len(chunks)} piece(s) to {outdir}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
