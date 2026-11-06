# Chapter 1 — Start Here

Welcome. This handbook is for the day you have *two hundred files* that need the same thing done to them — renamed, resized, merged, split, or sorted — and no software name for what you're doing, because it isn't your job, it's just Tuesday.

You never learned to program and you never will be asked to here. You'll run small, tested commands, one at a time, with a rule so important it gets its own chapter:

> **Nothing changes until you've seen a preview of exactly what would happen, and you say yes.**

## Who this is for

Anyone who works with files and isn't a programmer: nurses wrangling continuing-education PDFs, small-business owners combining monthly CSV exports, authors preparing images for a book, eBay resellers resizing photos. The writing is from Dylan Asdale, RN — he explains AI and automation "like a friend would."

## What you need

One thing: **Python 3**, free, with a friendly installer.

**Windows:**
1. Go to [python.org/downloads](https://www.python.org/downloads/), press the big yellow Download button.
2. Run the installer. **Check the box that says "Add python.exe to PATH"** — this is the step 90% of guides forget to warn you about.
3. Open PowerShell (press Start, type `powershell`, Enter) and check it worked:

```powershell
python --version
```

**Mac:**
1. Python is probably already installed. Open the Terminal app (press Cmd+Space, type `terminal`, Enter) and check:

```bash
python3 --version
```

2. If that says "command not found," get it from [python.org/downloads](https://www.python.org/downloads/) the same way as Windows.

Note the little difference: Windows calls it `python`, Macs usually call it `python3`. This handbook writes `python scripts/...` — Mac readers, read that as `python3 scripts/...`. Chapter 10's cookbook shows both spellings.

## How this handbook works

1. **Read a chapter** about the mess you're in (renames, CSVs, PDFs, images, folders).
2. **Copy the tested command** from that chapter. Each chapter ships with a script in `scripts/` that has automated tests proving it behaves — tests instead of prose, so you don't have to take a paragraph's word for it.
3. **Look at the preview** the script prints (the dry run).
4. **Run the same command again with `--do-it`** when the preview looks right.

Try the verification step right now, from the handbook's folder:

```bash
python -m unittest discover -s tests
```

You should see `OK`. That's you proving, on your own machine, that every recipe in this book works before running any of it on anything you care about.

## What this book is *not*

- **Not set-it-and-forget-it automation.** This is for the one-off jobs. If you want concepts — schedulers, watching folders, cron — read the companion *Automation Friend Guide* instead, then come back.
- **Not a single tool.** The companion *Local File Organizer CLI* does one everyday sorting job forever; this handbook is for the jobs no tool anticipated.
- **Not advice for regulated work.** Nurses and bookkeepers: this is education, not medical or compliance advice. Handle protected data with whatever policies your workplace requires.

## The citizenship rule

Last thing before Chapter 2. Batch jobs are powerful and perfectly safe **when they have three traits**: they preview first, they don't overwrite, and they never delete. Every tested script in this book follows all three. Every snippet you ask an AI co-pilot to write for you should too. Onward.
