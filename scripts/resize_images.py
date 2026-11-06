"""Resize a folder of images to a maximum size. Dry-run by default; add --do-it to actually write.

Always writes NEW files next to the originals (with --suffix, default "_small");
originals are never touched unless you also pass --replace.

Examples:
    python scripts/resize_images.py ~/Pictures/batch --max-edge 1600
    python scripts/resize_images.py ~/Pictures/batch --max-edge 1600 --do-it
    python scripts/resize_images.py ~/Pictures/batch --width 800 --format webp --do-it
"""
import argparse
import sys
from pathlib import Path

IMAGE_EXTS = (".jpg", ".jpeg", ".png", ".webp")


def split_base_extension(p: Path):
    stem = p.stem
    parts = stem.rsplit(".", 1)
    if len(parts) == 2 and parts[1].isalpha():
        return parts[0], "." + parts[1]
    return stem, ""


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("folder", help="folder containing the images")
    ap.add_argument("--max-edge", type=int, help="max width OR height; the longer side becomes this (keeps aspect)")
    ap.add_argument("--width", type=int, help="exact output width (keeps aspect ratio)")
    ap.add_argument("--height", type=int, help="exact output height (keeps aspect ratio)")
    ap.add_argument("--format", choices=["png", "jpg", "webp"], help="write in this format (default: same as input)")
    ap.add_argument("--suffix", default="_small", help="text added before the extension of new files (default: _small)")
    ap.add_argument("--quality", type=int, default=85, help="JPEG/WebP quality 1-100 (default: 85)")
    ap.add_argument("--replace", action="store_true", help="with --do-it: overwrite originals instead of making new files")
    ap.add_argument("--do-it", action="store_true", help="actually write images (omit to preview only)")
    args = ap.parse_args(argv)

    try:
        from PIL import Image
    except ImportError:
        print("This script needs the free helper 'Pillow'. Install it with:\n    pip install Pillow", file=sys.stderr)
        return 3

    if not (args.max_edge or args.width or args.height or args.format):
        ap.error("give a size (--max-edge, or --width/--height) and/or --format")
    if args.replace and not args.do_it:
        ap.error("--replace only means something together with --do-it")

    folder = Path(args.folder).expanduser().resolve()
    if not folder.is_dir():
        ap.error(f"not a folder: {folder}")

    images = [p for p in sorted(folder.iterdir()) if p.is_file() and p.suffix.lower() in IMAGE_EXTS]

    jobs, skipped, sizes = [], [], []
    for p in images:
        base, inner_ext = split_base_extension(p)
        if args.suffix and base.endswith(args.suffix):
            skipped.append((p, "looks already processed (name ends with " + args.suffix + ")"))
            continue
        try:
            with Image.open(p) as im:
                w, h = im.size
        except Exception as exc:
            skipped.append((p, f"can't read as image ({type(exc).__name__})"))
            continue
        if args.max_edge:
            scale = min(1.0, args.max_edge / max(w, h))
            new_w, new_h = max(1, round(w * scale)), max(1, round(h * scale))
        elif args.width and args.height:
            new_w, new_h = args.width, args.height
        elif args.width:
            new_w, new_h = args.width, max(1, round(h * args.width / w))
        elif args.height:
            new_w, new_h = max(1, round(w * args.height / h)), args.height
        else:
            new_w, new_h = w, h
        if args.format:
            new_ext = "." + args.format
        elif inner_ext:
            new_ext = p.suffix.lower() if p.suffix.lower() != ".jpeg" else ".jpg"
        else:
            new_ext = ".jpg" if p.suffix.lower() in (".jpg", ".jpeg") else p.suffix.lower()
        target = p if args.replace else p.with_name(base + args.suffix + new_ext)
        if target.exists():
            skipped.append((p, f"output already exists: {target.name}"))
            continue
        if (new_w, new_h) == (w, h) and new_ext == p.suffix.lower():
            skipped.append((p, "already that size and format"))
            continue
        sizes.append((w, h))
        jobs.append((p, target, new_w, new_h, new_ext))

    for p, reason in skipped:
        print(f"  ! skipping {p.name}: {reason}")
    if not jobs:
        print("Nothing to do.")
        return 0
    print(f"{'Overwriting originals for' if args.replace else 'Making new files for'} {len(jobs)} image(s):")
    for p, target, nw, nh, ext in jobs:
        to_name = p.name if args.replace else target.name
        print(f"  {p.name}  ->  {to_name}  ({nw}x{nh}{ext})")
    if not args.do_it:
        print(f"\nDry run: nothing was written yet. Originals stay untouched. Happy? Add --do-it.")
        return 0

    for p, target, nw, nh, ext in jobs:
        with Image.open(p) as im:
            if im.mode not in ("RGB", "RGBA"):
                im = im.convert("RGB" if ext == ".jpg" else im.mode)
            im = im.resize((nw, nh), Image.LANCZOS)
            im.save(target, quality=args.quality)
    print(f"\nDone: {len(jobs)} image(s) written. Originals kept: {'no (you used --replace)' if args.replace else 'yes'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
