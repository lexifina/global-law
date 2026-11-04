# How `words` and `blame` match lines from one version to the next

4 November 2026. Script: `line_matching.py` (this folder). Raw results: `line_matching.json` (every method) and
`line_matching_chosen.json` (the change as made, against the old behaviour).

## The problem

The first bench run (tree fc97345) found `words` slow on long, much-amended statutes:

- Czechia's sb/2007/378 (6,896 lines, 44 versions in force) took 79 s;
- sb/1995/247 took 19 s.

`blame` on the same files takes under a second when git's own blame gives the right answer. Where versions must be
replayed (a correction, or an older act committed after a newer one), it took up to 12 s.

## Where the time went

A profile of `words` on sb/2007/378:

- **49 of 54 seconds were the line diff.** Each version is compared with the one before, line by line, with Python's
  `difflib.SequenceMatcher` before any words are compared. `difflib` is quadratic in lines that repeat, and half of
  this statute's lines are blank: 3,445 of 6,896.
- **Word-by-word comparison** of the changed lines took 1.5 s.
- **Starting git processes** looked like 75 s under the profiler, but was 1.5 s when the machine was quiet.
  `law.py` asked git for the tree's HEAD after every second; it now reads it from the `.git` files.

So the question was how to match lines, not how to match words.

## What was tried

Each method replaced `law._line_opcodes` and was run on the same 30 cases:

- the four slow files;
- 26 files with four or more versions, drawn at random from 13 corpora (seed 4).

`blame`'s git fast path was turned off so the replay is what was timed. The answers were compared with plain `difflib`,
the behaviour until now.

| Method | How it matches lines | `words`, 4 slow files | `blame` replay, 4 slow files | `words`, 26 others | Characters credited to another law | Lines `blame` credits to another law |
|---|---|---|---|---|---|---|
| `difflib` (before) | Python's SequenceMatcher on the whole file | 101.9 s | 100.5 s | 45.4 s | 0 of 993,079 | 0 of 14,303 |
| trim | shared first and last lines matched first, `difflib` on the middle | 69.4 s | 60.4 s | 40.0 s | 0 | 37 |
| noblank | `difflib` on the non-blank lines only, blank lines placed after | 21.4 s | 16.5 s | 27.1 s | 22,607 (2.3%) | 644 |
| anchor | patience diff: lines found once in both versions pin the match, `difflib` between them | 21.8 s | 15.9 s | 43.0 s | 20,594 (2.1%) | 566 |
| git, Myers | `git diff --no-index`, git's default algorithm | 26.2 s | 18.1 s | 33.7 s | 46,600 (4.7%) | 903 |
| **git, histogram** | `git diff --no-index --diff-algorithm=histogram` | **14.7 s** | **8.4 s** | **24.8 s** | **1,171 (0.12%)** | 274 |

git's histogram diff was both the fastest and the closest to the old answers:

- the 1,171 characters are all in one file (sb/2007/378);
- of its 274 lines, 254 were blank lines, which hold no words.

## Is the old answer the right one?

The most frequent differing paragraph shows that neither answer is simply right:

- Law 70/2013 wrote "Při předepisování humánních léčivých přípravků jsou lékaři povinni …" as subsection (2).
- Law 262/2019 renumbered it (7) and moved it.
- `words` promises that moved text keeps the law that wrote it, so 70/2013 is the right credit for most of its words.
- `difflib` credited 70/2013 here only because both places fell inside one large changed block; it does not look for
  moved text.
- git's histogram diff saw a deletion in one place and an insertion in another, so it credited 262/2019.

A second try added explicit move detection, under git's histogram diff: an inserted line was compared with every line
removed elsewhere in the same step, keeping the law that wrote it when they were 60% alike.

- It took 8.9 s on sb/2007/378.
- It moved further from `difflib` (2,070 characters), not closer.
- Judged line by line against the version that first held the same wording, neither method was clearly better. The
  disagreements are text that was amended and moved at once, which no line-based rule settles.

The move detection was dropped: it added code without a clear gain.

## What was kept

`law._line_opcodes`:

- **Most files:** `difflib`, exactly as before. Small comparisons are cheap, so their answers do not change.
- **When both versions are long** (more than 1,000,000 line pairs, about 1,000 lines each): git's histogram diff.
- **When git cannot be run:** `difflib`.

The trim step was dropped too. It changed the alignment of trailing blank lines (the 37 lines above) and is not needed
once git handles the long files.

`tests/test_law_fixtures.py` (`LineMatching`) checks three things:

- small comparisons give `difflib`'s exact answer;
- long ones walk both versions end to end and find only the lines that changed;
- without git, `difflib` is used.

## Result

`line_matching_chosen.json`: law.py as changed, against plain `difflib`, on the same 30 cases (same machine,
4 November 2026):

| | `difflib` (before) | law.py now |
|---|---|---|
| `words`, the 4 slow files | 76.0 s | 18.1 s |
| `blame` replay, the 4 slow files | 74.8 s | 10.4 s |
| `words`, the 26 others | 39.1 s | 30.0 s |
| Files whose answers changed | – | 4 of 30, all long |
| Characters credited to another law | – | 1,171 of 993,079, all in sb/2007/378 |
| Lines `blame` credits to another law | – | 268 of 14,303: 261 blank, 7 repeated headings |

Per file:

| File | `words` | `blame` replay |
|---|---|---|
| Czechia sb/2007/378 | 55.6 → 10.9 s | 55.5 → 5.5 s |
| Czechia sb/2000/218 | 20.0 → 11.9 s | 25.2 → 13.1 s |
| Czechia sb/1995/247 | 16.1 → 5.4 s | 15.5 → 3.8 s |
| Canada S-15.3 schedule 1 | 3.8 → 1.4 s | 3.8 → 1.1 s |

The 26 other files give byte-identical answers. The times include reading every version of each file. The slow
remainder on sb/2000/218 is word-by-word comparison of large rewrites, not line matching.

## Left open

- Text that is amended and moved in the same version is credited to the amending law, by both the old and the new
  method, unless the two places happen to fall in one changed stretch. A real fix would need move detection at the
  word level. It is not attempted here.
