# How `words` compares the words of the lines that changed

4 November 2026. Script: `word_matching.py` (this folder). Raw results: `word_matching.json`.

## The question

After `line_matching.md`, `words` matches unchanged lines with difflib or git's histogram diff, then compares the
changed stretches word by word with difflib. On Czechia's sb/2007/378 the word comparison had become the larger cost:
4.5 of 9 seconds in a profile, most of it in difflib's `find_longest_match`. Spaces are tokens of their own, so a
long stretch has thousands of identical " " tokens, and difflib walks all of them.

Two costs in `words_on` itself were found on the way and removed, with byte-identical answers:

- the credits of a changed stretch were cut into lines by slicing the remaining list once a line, which copies it
  again and again;
- each run of text was built by adding one token at a time to a string, which copies the run again and again.

With those two gone, `words` on sb/2007/378 went from 9.2 to 4.1 s, and on sb/1995/247 from 3.7 to 2.3 s (one try
each, same machine).

## What was tried

Each method replaced one part of `words` and ran on the same 34 files: five slow files (Czechia sb/2007/378,
sb/2000/218, sb/1995/247, Canada S-15.3 schedule 1, US 8 U.S.C. §1182) and 29 files with four or more versions from 14
corpora (seed 5). Answers were compared with `words` as it was.

| Method | What it changes | `words`, 5 slow files | `words`, 29 others | Characters credited to another law |
|---|---|---|---|---|
| current | difflib on words and spaces | 9.2 s | 4.7 s | 0 of 992,551 |
| ints | the same, on numbers standing for the tokens | 9.4 s | 4.8 s | 0 |
| pair-fast | large rewrites: the new line set once, old lines that cannot beat the best skipped | 10.3 s | 5.2 s | 0 |
| ints + pair-fast | both | 10.4 s | 4.9 s | 0 |
| glued | each word carries the spaces after it, so spaces are not tokens | 6.8 s | 4.2 s | 2,331 (0.23%), 9 files |
| space-junk | spaces may not start a match (difflib's `isjunk`) | 9.9 s | 5.4 s | 49,275 (5.0%), 10 files |
| trim | words shared at the start and end of a stretch matched first | 8.7 s | 4.4 s | 670 (0.07%), 3 files |

## Decision

None was kept.

- The exact methods gave nothing measurable. Hashing strings is already cheap in Python, and few stretches go
  through the large-rewrite path.
- The fastest method, glued, saves about 2.4 s over five slow files, but credits 2,331 characters to another law.
  That is not worth it now that the slowest `words` is about 4 s, within its 10 s budget.
- space-junk was both slower and much further from the old answers.

The two removed costs above, which change no answer, are kept. Spaces as tokens stay the open lead if `words` needs
to be faster again: glued is the method to look at first.
