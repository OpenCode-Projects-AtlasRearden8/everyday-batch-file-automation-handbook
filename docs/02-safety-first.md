# Chapter 2 — Safety First: The Dry-Run Habit

You can run every recipe in this book without fear, because of one habit that costs five extra seconds and has saved more careers than we can count:

1. **Run the command with nothing extra** — it only *previews*.
2. **Read the preview.** Does the list match the files you care about? Numbers look sane?
3. **Only then add `--do-it`** and run it again.

Script authors call step 1 a **dry run** — like running the tap before you jump in the shower. In this handbook, *the dry run is not an option you might forget; it is the default*. The script physically cannot touch a file unless you say `--do-it`.

Windows has its own built-in flavor of this in PowerShell, spelled `-WhatIf`:

```powershell
Rename-Item -WhatIf ...
```

`-WhatIf` means *print what you would do, do nothing*. Same tap-before-shower rule, built into PowerShell itself. When you ask an AI co-pilot for PowerShell (Chapter 9), make `-WhatIf` part of the request.

## Four rails, all standard on the tested scripts

| Rail | What it means |
| --- | --- |
| **Dry run by default** | No preview, no `--do-it`, no changes. Ever. |
| **Never overwrite** | If the result name already exists, the script *cancels the whole run* rather than stomping an older file. |
| **Never delete** | Moving and renaming only. The `_unsorted/` bucket exists so unknown files have a home instead of a shredder. |
| **Atomic cancel** | If *any* file in the run would collide, *nothing* happens — not a half-finished mess. |

## The staging folder trick

Before a big job, copy a handful of sample files into a scratch folder and dry-run against that:

```bash
mkdir /tmp/rehearsal        # Mac: any scratch spot
```
```powershell
New-Item -ItemType Directory -Force rehearsal   # Windows
```

Run the full command (preview, then `--do-it`) on ten sample files. If the ten come out right, the two hundred will too. This takes two minutes and eliminates that heart-drop feeling.

## The backup question

The tested scripts never delete anything, so *worst case* after a mistake is: files are sitting somewhere unexpected, with `-1` suffixes or in `_unsorted/`. That's recoverable by hand. Still, for genuinely precious data (tax records, patient-facing documents, book scans with no re-scan), make a copy first. A cheap `zip` of the source folder before a big job is the adult version of a helmet:

```bash
# Mac
zip -r pictures-backup.zip ~/Pictures/batch
```
```powershell
# Windows
Compress-Archive -Path $HOME\Pictures\batch -Destination Pictures-backup.zip
```

## What to refuse, every time

- Any script whose *first* move is `Remove-Item` / `rm` / `del`.
- Any AI-generated command with `> $null` or `2>&1` hiding the preview output. You must be able to see the plan.
- Any command containing the word "remove," "delete," "clean up," or "purge" run against your only copy of important files.
- Overwrite-anything flags (`-Force`, `--force`, `--overwrite`) without a backup, unless you fully understand them.

If an AI proposes something that deletes or overwrites, ask it to add the same rails here. Chapter 9 gives you the exact words.
