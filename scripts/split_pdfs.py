"""Split a PDF file into smaller PDFs. Dry-run by default; add --do-it to actually write.

Examples:
    python scripts/split_pdfs.py ~/Desktop/table.pdf --every 1
    python scripts/split_pdfs.py ~/Desktop/table.pdf --every 10 --out ~/Desktop/chunks --do-it
"""
import argparse
import sys
from pathlib import Path


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pdf", help="the PDF file to split")
    ap.add_argument("--every", type=int, default=1, help="pages per output file (default: 1)")
    ap.add_argument("--out", help="folder for the output pieces (default: folder of the input file)")
    ap.add_argument("--do-it", action="store_true", help="actually write the pieces (omit to preview only)")
    args = ap.parse_args(argv)

    try:
        from pypdf import PdfReader, PdfWriter
    except ImportError:
        print("This script needs the free helper 'pypdf'. Install it with:\n    pip install pypdf", file=sys.stderr)
        return 3

    src = Path(args.pdf).expanduser().resolve()
    if not src.is_file():
        ap.error(f"not a file: {src}")
    if args.every < 1:
        ap.error("--every must be at least 1")
    outdir = Path(args.out).expanduser().resolve() if args.out else src.parent

    try:
        reader = PdfReader(str(src))
        if reader.is_encrypted:
                try:
                    reader.decrypt("")
                except Exception:
                    print("CANCELLED: this PDF is password-protected; can't split it.", file=sys.stderr)
                    return 2
        total = len(reader.pages)
    except Exception as exc:
        ap.error(f"could not read this PDF ({type(exc).__name__}: {exc})")

    chunks = [(i, min(i + args.every, total)) for i in range(0, total, args.every)]
    names = [src.stem + f"_{start + 1:04d}-{end:04d}.pdf" for start, end in chunks]
    for name in names:
        target = outdir / name
        if target.exists():
            ap.error(f"piece already exists, refusing to overwrite: {target}")

    print(f"Input: {src.name} ({total} page(s))")
    print(f"Output folder: {outdir}")
    print(f"Will write {len(chunks)} piece(s), {args.every} page(s) each:")
    for name, (start, end) in zip(names, chunks):
        print(f"  {name}  (pages {start + 1}-{end})")

    if not args.do_it:
        print("\nDry run: nothing was written yet. Happy? Add --do-it.")
        return 0

    outdir.mkdir(parents=True, exist_ok=True)
    for name, (start, end) in zip(names, chunks):
        writer = PdfWriter()
        for idx in range(start, end):
            writer.add_page(reader.pages[idx])
        with (outdir / name).open("wb") as f:
            writer.write(f)

    print(f"\nDone: wrote {len(chunks)} piece(s) to {outdir}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
