# Chapter 9 — AI as Your Script Co-Pilot

Everything so far used tested scripts that ship with this handbook. The very next job you'll meet isn't in here — "rename each file with the date hidden inside its filename," "split this CSV only when column B changes." That's where AI earns its keep: as the co-pilot who writes the script, while *you* stay the pilot who previews and says yes.

## The five-sentence request (copy this whole thing)

> I need a short Python 3 script. It should: (1) work from the command line with plain `argparse`; (2) do a **dry run by default** that prints exactly which files it would change and to what; (3) only act when I pass `--do-it`; (4) **never overwrite an existing file** and **never delete anything** — if a result name is taken, cancel the run with a clear message; (5) exit with a nonzero code if anything looks wrong. The job: [DESCRIBE YOUR MESS HERE]. Then write five `unittest` tests for it, including a dry-run-changes-nothing test and a collision-cancels test.

Those five wants are the entirety of Chapter 2's rails turned into an instruction. Run tests with:

```bash
python -m unittest discover -s tests
```

If the AI's script fails them, that's a *good* outcome — you found the bug on a scratch folder, not on your tax records.

## Prompting habits that separate pilots from passengers

**Describe the mess, not the code.** "Files arrive named `LAB-4821.jpg` but our software demands `2026-03-04-4821.jpg` where the date comes from an adjacent `shots.csv`" beats "write a Python script with os.walk."

**Ask for the preview to be human-readable.** "The dry run should print `old name → new name` pairs and a count" is a stronger prompt than a vague preview request. You'll be reading that list with your own eyes at decision speed.

**Give one sample of good output.** "One output line for `IMG_4821.jpg` should look like: `IMG_4821.jpg -> 2026-03-04-4821.jpg`" removes whole categories of misunderstanding.

**Make it write tests.** The sentence "tests instead of prose" is the culture here: a script whose behavior is *demonstrated* beats a confidently-worded paragraph every time. If an AI's tests only test the happy path, ask: "add the case where the folder has an unexpected file, and one where I run it twice."

**Refuse the unsafe on sight.** The co-pilot may propose `shutil.rmtree`, `os.remove`, or an `-Force`/overwrite flag "to keep it simple." Your reply: *"No deletion, no overwrite. Use the five rules from my first message."* A good co-pilot complies in one breath; a sloppy one argues. Models that argue about Phase-2-safety rails are the ones to write dry runs about.

## Review the script like a pilot, not a passenger

Three things, 90 seconds, every time:

1. **Find the no-touch guarantee.** Search the script for `.remove(`, `.rmtree(`, `unlink(`, `"w"` open modes against input files, `Remove-Item`, `rm `, `-Force`. Nothing in a compliant plan should be there.
2. **Find where `--do-it` is checked.** You want to see the check *before* any file action happens, not after.
3. **Then run it — on a copy.** Chapter 2's rehearsal folder: ten sample files, full preview-then-`--do-it` cycle, eyeball the ten results. Only then point it at the real pile.

## Prompt to turn any chapter into your job

> Take this script from the handbook: [PASTE SCRIPT]. Adapt it so [NEW REQUIREMENT]. Keep all five rails intact — dry-run-by-default, `--do-it` to commit, never overwrite, never delete, nonzero exit on failure — and keep the same argument names so the handbook's docs still apply. List any behavior you couldn't preserve.

That last sentence ("list what you couldn't preserve") is where you catch the corner cases that turn into losses — write down the list before running anything.

## When NOT to co-pilot

Regulated money, health information, court documents: if it's one file, convert it in the native application (Chapter 7's rule). If a prompt failure could cost a license, the honest speed-up is doing it the slow way. AI co-pilots make *volume* safe; they don't make *stakes* disappear.
