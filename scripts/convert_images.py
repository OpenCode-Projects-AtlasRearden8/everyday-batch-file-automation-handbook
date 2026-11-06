"""Convert a folder of images to a new format (png, jpg, or webp). Dry-run by default.

Never touches the originals — new files get "--toformat-style" suffix? No: new files
keep the same base name with the new extension. If the target name is taken, it is skipped.

Examples:
    python scripts/convert_images.py ~/Pictures/scan --to jpg
    python scripts/convert_images.py ~/Pictures/scan --to webp --do-it
"""
import argparse
import sys
from pathlib import Path

IMAGE_EXTS = (".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff", ".gif")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("folder", help="folder containing the images")
    ap.add_argument("--to", choices=["png", "jpg", "webp"], required=True, help="target format")
    ap.add_argument("--out", help="folder for converted files (default: alongside originals)")
    ap.add_argument("--quality", type=int, default=85, help="JPEG/WebP quality 1-100 (default: 85)")
    ap.add_argument("--do-it", action="store_true", help="actually convert (omit to preview only)")
    args = ap.parse_args(argv)

    try:
        from PIL import Image
    except ImportError:
        print("This script needs the free helper 'Pillow'. Install it with:\n    pip install Pillow", file=sys.stderr)
        return 3

    folder = Path(args.folder).expanduser().resolve()
    outdir = Path(args.out).expanduser().resolve() if args.out else folder
    if not folder.is_dir():
        ap.error(f"not a folder: {folder}")

    images = [p for p in sorted(folder.iterdir()) if p.is_file() and p.suffix.lower() in IMAGE_EXTS]
    if not images:
        print("Nothing to do: no image files found there.")
        return 0

    jobs, skipped = [], []
    ext = "." + args.to
    for p in images:
        if p.suffix.lower() == (".jpeg" if args.to == "jpg" else ext):
            skipped.append((p, f"already {args.to}"))
            continue
        target = outdir / (p.stem + ext)
        if target.exists():
            skipped.append((p, f"output already exists: {target.name}"))
            continue
        jobs.append((p, target))

    for p, reason in skipped:
        print(f"  ! skipping {p.name}: {reason}")
    if not jobs:
        print("Nothing to convert.")
        return 0
    print(f"Converting {len(jobs)} image(s) to {args.to}:")
    for p, target in jobs:
        print(f"  {p.name}  ->  {target.name}")
    if not args.do_it:
        print("\nDry run: nothing was written yet (originals always kept). Happy? Add --do-it.")
        return 0

    outdir.mkdir(parents=True, exist_ok=True)
    for p, target in jobs:
        with Image.open(p) as im:
            if ext in (".jpg", ".webp"):
                im = im.convert("RGB") if im.mode != "RGB" else im
            im.save(target, quality=args.quality)
    print(f"\nDone: {len(jobs)} image(s) converted. Originals kept.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
