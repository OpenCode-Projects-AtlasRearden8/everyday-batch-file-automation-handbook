"""Join several CSV files into one. Dry-run by default; add --do-it to actually write.

Examples:
    python scripts/join_csv.py ~/Desktop/january --out ~/Desktop/q1.csv
    python scripts/join_csv.py ~/Desktop/january --out ~/Desktop/q1.csv --do-it
"""
import argparse
import fnmatch
import csv
import sys
from pathlib import Path


def read_rows(path: Path):
    with path.open("r", newline="", encoding="utf-8-sig") as f:
        return [row for row in csv.reader(f) if any(cell.strip() for cell in row)]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("folder", help="folder containing the CSV files to join")
    ap.add_argument("--match", default="*.csv", help="only join files matching this glob (default: *.csv)")
    ap.add_argument("--out", required=True, help="path of the combined output file")
    ap.add_argument("--do-it", action="store_true", help="actually write the output (omit to preview only)")
    args = ap.parse_args(argv)

    folder = Path(args.folder).expanduser().resolve()
    out = Path(args.out).expanduser().resolve()
    if not folder.is_dir():
        ap.error(f"not a folder: {folder}")

    files = sorted(p for p in folder.iterdir() if p.is_file() and fnmatch.fnmatch(p.name.lower(), args.match.lower()))
    if not files:
        print("Nothing to do: no matching files found in that folder.")
        return 0
    if out.exists():
        ap.error(f"output file already exists, refusing to overwrite: {out}")
    if any(p.samefile(out.resolve()) if out.exists() else False for p in files) or files[0].resolve() == out:
        ap.error(f"output would overwrite an input file: {out}")

    header = None
    accepted, problems = [], []
    for p in files:
        try:
            rows = read_rows(p)
        except (UnicodeDecodeError, csv.Error) as exc:
            problems.append((p, f"could not read it ({type(exc).__name__})"))
            continue
        if not rows:
            problems.append((p, "file is empty"))
            continue
        if header is None:
            header = rows[0]
        if rows[0] != header:
            problems.append((p, f"header differs from {files[0].name}"))
            continue
        accepted.append((p, rows))

    total_rows = sum(len(rows) - 1 for _, rows in accepted)
    print(f"Files to join: {len(files)}")
    for p in files:
        print(f"  {p.name}")
    for p, reason in problems:
        print(f"  ! skipping {p.name}: {reason}", file=sys.stderr)
    if problems:
        print(f"({len(problems)} file(s) will be skipped, above.)")
    if header:
        print(f"Header: {','.join(header)}")
    print(f"Data rows in output: {total_rows}")
    print(f"Output file: {out}")

    if not args.do_it:
        print("\nDry run: nothing was written yet. Happy? Add --do-it.")
        return 0

    with out.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        for _, rows in accepted:
            for row in rows[1:]:
                writer.writerow(row)

    print(f"\nDone: wrote {out.name} from {len(accepted)} file(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
