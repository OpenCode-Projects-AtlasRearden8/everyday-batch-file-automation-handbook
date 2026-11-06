"""Join several PDF files into one. Dry-run by default; add --do-it to actually merge.

Examples:
    python scripts/join_pdfs.py ~/Desktop/invoices --out ~/Desktop/2026.pdf
    python scripts/join_pdfs.py a.pdf b.pdf c.pdf --out combined.pdf --do-it
    python scripts/join_pdfs.py ~/Desktop/invoices --match "INV*" --out invoices.pdf --do-it
"""
import argparse
import fnmatch
import sys
from pathlib import Path


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("inputs", nargs="*", help="PDF files to join, in the order you want them merged")
    ap.add_argument("--folder", help="take all matching PDFs from this folder instead of listing files")
    ap.add_argument("--match", default="*.pdf", help="with --folder: which files to take (default: *.pdf)")
    ap.add_argument("--out", required=True, help="path of the merged output file")
    ap.add_argument("--do-it", action="store_true", help="actually write the merged file (omit to preview only)")
    args = ap.parse_args(argv)

    try:
        from pypdf import PdfReader, PdfWriter
    except ImportError:
        print("This script needs the free helper 'pypdf'. Install it with:\n    pip install pypdf", file=sys.stderr)
        return 3

    if args.folder:
        folder = Path(args.folder).expanduser().resolve()
        if not folder.is_dir():
            ap.error(f"not a folder: {folder}")
        files = sorted(p for p in folder.iterdir() if p.is_file() and fnmatch.fnmatch(p.name.lower(), args.match.lower()) and p.suffix.lower() == ".pdf")
    elif args.inputs:
        files = [Path(f).expanduser().resolve() for f in args.inputs]
    else:
        ap.error("give PDF files as arguments, or use --folder FOLDER")
    out = Path(args.out).expanduser().resolve()
    if out.exists():
        ap.error(f"output already exists, refusing to overwrite: {out}")
    files = [p for p in files if p.suffix.lower() == ".pdf"]
    nonpdf = [p for p in (Path(i).expanduser() for i in args.inputs) if p.suffix.lower() != ".pdf"]
    for p in nonpdf:
        print(f"  ! skipping {p.name}: not a .pdf file", file=sys.stderr)
    files = [p for p in files if p.exists()]
    if not files:
        print("Nothing to join: no PDF files found.")
        return 0

    writers, pages, problems = [], [], []
    for p in files:
        try:
            reader = PdfReader(str(p))
            if len(reader.pages) < 1:
                problems.append((p, "has 0 pages"))
                continue
            if reader.is_encrypted:
                try:
                    reader.decrypt("")
                except Exception:
                    problems.append((p, "is password-protected"))
                    continue
            pages.append((p, len(reader.pages)))
            writers.append(reader)
        except Exception as exc:
            problems.append((p, f"could not read it ({type(exc).__name__}: {exc})"))

    order = " -> ".join(p.name for p, _ in pages)
    total = sum(n for _, n in pages)
    print(f"Merging {len(pages)} PDF(s) into: {out}")
    for p, n in pages:
        print(f"  {p.name}  ({n} page(s))")
    if order:
        print(f"Order kept: files come in the order listed above ({order}).")
    for p, reason in problems:
        print(f"  ! skipping {p.name}: {reason}", file=sys.stderr)
    print(f"Total pages in output: {total}")

    if len(writers) < len(files) or not writers:
        print("\nNot every file can be merged; dry run shown above. Nothing written.", file=sys.stderr if not args.do_it else sys.stdout)
        if not writers:
            return 2

    if not args.do_it:
        print("\nDry run: nothing was written yet. Happy? Add --do-it.")
        return 0

    merged = PdfWriter()
    for reader in writers:
        merged.append(reader)
    with out.open("wb") as f:
        merged.write(f)
    print(f"\nDone: wrote {out.name} with {total} page(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
