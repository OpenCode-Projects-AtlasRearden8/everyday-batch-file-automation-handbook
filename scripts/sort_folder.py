"""Sort a messy folder into subfolders by file type ("folder rules"). Dry-run by default.

Rules (by extension): images/, documents/, data/, media/, archives/, code/,
bookkeeping/. Anything that matches no rule goes to _unsorted/ — never deleted,
never renamed, contents always kept.

Examples:
    python scripts/sort_folder.py ~/Downloads
    python scripts/sort_folder.py ~/Downloads --do-it
    python scripts/sort_folder.py ~/Desktop/drop --by-year --do-it
"""
import argparse
import datetime
import shutil
import sys
from pathlib import Path

RULES = {
    "images": (".jpg", ".jpeg", ".png", ".webp", ".gif", ".svg", ".heic", ".tiff", ".bmp", ".psd", ".ai"),
    "documents": (".pdf", ".doc", ".docx", ".txt", ".rtf", ".md", ".odt", ".ppt", ".pptx", ".epub"),
    "data": (".csv", ".xlsx", ".xls", ".json", ".tsv", ".sqlite", ".db"),
    "media": (".mp4", ".mov", ".avi", ".mkv", ".mp3", ".wav", ".m4a", ".aac", ".flac"),
    "archives": (".zip", ".rar", ".7z", ".tar", ".gz", ".dmg", ".exe", ".iso"),
    "code": (".py", ".js", ".html", ".css", ".sh", ".bat", ".ps1", ".ipynb"),
    "bookkeeping": (".qbo", ".qbx", ".ofx", ".qif"),
}


def rule_for(path: Path):
    return next((name for name, exts in RULES.items() if path.suffix.lower() in exts), "_unsorted")


def unique_target(folder: Path, name: str):
    target = folder / name
    if not target.exists():
        return target
    n = 1
    while True:
        candidate = folder / f"{Path(name).stem}-{n}{Path(name).suffix}"
        if not candidate.exists():
            return candidate
        n += 1


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("folder", help="the messy folder to sort")
    ap.add_argument("--by-year", action="store_true", help="group inside each rule folder by year, e.g. documents/2024/")
    ap.add_argument("--do-it", action="store_true", help="actually move files (omit to preview only)")
    args = ap.parse_args(argv)

    root = Path(args.folder).expanduser().resolve()
    if not root.is_dir():
        ap.error(f"not a folder: {root}")

    files = [p for p in sorted(root.iterdir()) if p.is_file() and not p.name.startswith(".")]
    moves = []
    for p in files:
        sub = str(datetime.datetime.fromtimestamp(p.stat().st_mtime).year) if args.by_year else ""
        dest_root = root / rule_for(p) / sub
        dest = unique_target(dest_root, p.name)
        moves.append((p, dest))

    if not moves:
        print("Nothing to move: no loose files in that folder (only folders/dot-files, if any).")
        return 0

    buckets = {}
    for _, dest in moves:
        rel = dest.relative_to(root)
        key = "/".join(rel.parts[:-1])
        buckets[key] = buckets.get(key, 0) + 1

    print(f"Plan for {root.name} — {len(moves)} file(s) would move:")
    if args.by_year:
        for src, dest in moves:
            verb = "RENAME MOVE" if args.do_it else "WOULD MOVE"
            print(f"{verb}  {src.name}  ->  {dest.relative_to(root)}/")
    for key in sorted(buckets):
        print(f"  {key}/   <- {buckets[key]} file(s)")
    if not args.do_it:
        print("\nDry run: nothing changed yet. Contents are moved, never deleted or edited.")
        print("Happy? Run the same command again with --do-it at the end.")
        return 0

    for src, dest in moves:
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(dest))
    print(f"\nDone: moved {len(moves)} file(s). Nothing was deleted or edited.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
