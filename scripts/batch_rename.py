"""Batch-rename files in a folder. Dry-run by default; add --do-it to actually rename.

Examples:
    python scripts/batch_rename.py ~/Downloads/shots --action replace --old IMG_ --old2 IMG-
    python scripts/batch_rename.py ~/Pictures --action prefix --chunk "2026-11 " --match "*.jpg" --do-it
    python scripts/batch_rename.py ~/Desktop/cases --action sequence --chunk "Report_{:04d}" --match "*.pdf" --do-it
"""
import argparse
import fnmatch
import sys
from pathlib import Path


def plan(folder: Path, args: argparse.Namespace):
    files = [p for p in sorted(folder.iterdir()) if p.is_file()]
    if args.match:
        files = [p for p in files if fnmatch.fnmatch(p.name, args.match)]
    planned = []
    seq = args.seq_start
    for p in files:
        stem, suffix = p.stem, p.suffix
        if args.action == "replace":
            target = p.with_name(p.name.replace(args.old, args.old2))
        elif args.action == "prefix":
            target = p.with_name((args.chunk or "") + p.name)
        elif args.action == "suffix":
            target = p.with_name(stem + (args.chunk or "") + suffix)
        elif args.action == "lower":
            target = p.with_name(p.name.lower())
        elif args.action == "upper":
            target = p.with_name(p.name.upper())
        elif args.action == "sequence":
            target = p.with_name(args.chunk.format(seq) + suffix)
            seq += 1
        if target.name != p.name:
            planned.append((p, target))
    return planned


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("folder", help="folder containing the files to rename")
    ap.add_argument("--action", choices=["replace", "prefix", "suffix", "lower", "upper", "sequence"], default="replace")
    ap.add_argument("--old", help="text to find in names (with --action replace)")
    ap.add_argument("--old2", help="text to put in its place (with --action replace)", default="")
    ap.add_argument("--chunk", help='text to add (prefix/suffix) or sequence pattern like "Report_{:04d}"')
    ap.add_argument("--match", help="only touch files matching this glob, e.g. *.jpg")
    ap.add_argument("--seq-start", type=int, default=1)
    ap.add_argument("--do-it", action="store_true", help="actually rename (omit to preview only)")
    args = ap.parse_args(argv)

    folder = Path(args.folder).expanduser().resolve()
    if not folder.is_dir():
        ap.error(f"not a folder: {folder}")
    if args.action == "sequence" and (not args.chunk or "{" not in args.chunk):
        ap.error('sequence mode needs a pattern with a number placeholder, e.g. --chunk "Report_{:04d}" ({:04d} = 1, 2, 3 as 0001, 0002, 0003)')

    planned = plan(folder, args)
    if not planned:
        print("Nothing to do: no files matched, or names are already correct.")
        return 0

    seen = set()
    for _, target in planned:
        key = target.name.lower()
        if key in seen:
            print(f"CANCELLED: two files would collide as {target.name!r}. Adjust your arguments; nothing was renamed.", file=sys.stderr)
            return 2
        seen.add(key)
        if args.action != "sequence" and target.exists():
            print(f"CANCELLED: {target.name} already exists; renaming would overwrite it. Adjust your arguments; nothing was renamed.", file=sys.stderr)
            return 2

    for src, dst in planned:
        verb = "RENAME" if args.do_it else "WOULD RENAME"
        print(f"{verb}  {src.name}  ->  {dst.name}")
    if not args.do_it:
        print(f"\nDry run: {len(planned)} file(s) would be renamed. Nothing changed yet.")
        print("Happy? Run the same command again with --do-it at the end.")
        return 0

    for src, dst in planned:
        src.rename(dst)
    print(f"\nDone: {len(planned)} file(s) renamed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
