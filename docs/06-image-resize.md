# Chapter 6 — Resizing and Converting Images the Batch Way

Two everyday jobs: shrink 140 seller photos so your listing page stops crawling, and turn formats so software accepts them (`heic` on a Windows machine, `png` where a JPEG is demanded).

## One-time setup

```bash
pip install Pillow       # Mac: pip3 install Pillow
```

## Resize: `scripts/resize_images.py`

Shrink to a **max edge** (longest side) — this is usually what you want, because it keeps aspect ratio and never enlarges:

```bash
python scripts/resize_images.py ~/Pictures/listing-photos --max-edge 1600
```

```
Making new files for 140 image(s):
  IMG_4821.jpg  ->  IMG_4821_small.jpg  (1600x1067.jpg)
  ...
Dry run: nothing was written yet. Originals stay untouched. Happy? Add --do-it.
```

**Rails that matter for photos**: originals are never touched — new `*_small` files are written beside them (if the target name is taken, it's skipped, not overwritten). Only pass `--replace` (with `--do-it`) when you truly want originals gone, and Chapter 2 says: backup first.

Other moves:

| You want | Command |
| --- | --- |
| Max edge 1200 | `--max-edge 1200` |
| Exact width, keep aspect | `--width 800` |
| Only some files | add `--match "IMG_*.jpg"` |
| Smaller files (lower quality) | add `--quality 70` |
| Also convert format | add `--format webp` (or `jpg`, `png`) |

Already-resized files (`*_small`) are skipped on the next run, so re-running the same command on an already-done folder is safe.

## Convert: `scripts/convert_images.py`

```bash
python scripts/convert_images.py ~/Pictures/scans --to webp
python scripts/convert_images.py ~/Pictures/scans --to jpg --do-it
```

Again: dry run first, then `--do-it`. Originals always kept, existing targets never overwritten.

## Zero-Python built-ins

**Mac `sips`** (no Python needed at all):

```bash
sips -Z 1600 ~/Pictures/listing-photos/*.jpg    # -Z = max edge, overwrites in place!
```

⚠️ Read that comment again: `sips` *overwrites the original file by default* — the exact opposite safety posture from the tested script. Redirect the output folder yourself if you use it widely:

```bash
mkdir -p ~/Pictures/small
sips -Z 1600 -s format jpeg ~/Pictures/listing-photos/*.jpg --out ~/Pictures/small
```

**Mac `sips` also converts formats:** `sips -s format png a.webp --out a.png`

**Windows:** the built-ins for images are famously weak; a safe pattern is one image at a time from the Photos app, or PowerShell with the System.Drawing API (functional but long — this is a case where asking an AI co-pilot for *the exact loop* works well, and where you should refuse `-Force` or in-place overwrites without a backup). Honestly: `pip install Pillow` once and use the tested script.

## One flag that catches everyone: quality

80–85 is the sweet spot for listing photos. Below 60 you'll see smearing; above 95 you'll burn bandwidth for no visible change (except PNG, which is lossless and ignores JPEG-style quality the same way).
