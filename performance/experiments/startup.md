# What a short read costs before it reads any law

4 November 2026. Script: `startup.py` (this folder), which times two versions of `law.py` end to end and counts the
git processes each command starts. Raw results: `startup.json`.

## The question

After the line-matching work, most commands on the bench took 0.6 to 2 s whatever they read. The time went on the
work every command did before it touched the provision asked about. A trace of `show` on 8 U.S.C. §1182 found:

- **12 git processes** for a one-file read, each costing 30 to 50 ms on this machine:
  - 5 read the tree's HEAD commit: `manifest.json`, `data/moved-paths.tsv`, `data/legacy-dates.tsv`, the pins
    (`git ls-tree -r -d`, twice) and `.gitmodules`;
  - 6 checked the corpus: three `git cat-file -e` for the same commit, `rev-parse` for its HEAD, whether it is
    shallow, and where the cache folder is;
  - only 1 read law: the `git cat-file --batch` reader.
- On Romania, a further **0.7 s inside Python**:
  - 0.25 s loading the corpus index (a 33 MB pickle) for one file;
  - 0.3 s parsing the whole of `data/credits.csv` (8,500 rows) and `data/laws.csv` to find the credits for one act.

## What was changed

| Change | Effect |
|---|---|
| What every command reads from the tree's HEAD commit is kept on disk per commit (`global-law-cache/root-<commit>.json`, the last eight kept) | after the first read of a commit, no git process for it |
| HEAD, the cache folder, a corpus's HEAD and whether it is shallow are read from the `.git` files, as git itself would | no process each |
| "Does this checkout have that commit?" is asked of the batch reader the command starts anyway, once per commit | three processes fewer |
| The index is kept in 64 pieces by path (`<corpus>.index`); one file's lookup loads one piece; a command that needs every file reads all of them, in the order they were indexed | Romania: 0.25 s → about 0.03 s for one file; `world` reads only the commits, never the files |
| Garbage collection is paused while an index piece is unpickled | a fifth of the load |
| `data/credits.csv` is parsed for the act asked about only (all of it when a field is quoted) | 0.3 s → a few ms |
| An old one-piece index is converted once instead of rebuilt | no 10 s rebuild on upgrade |

Two quadratic steps in `words` were found on the way and removed (`word_matching.md`).

## Result

Every answer is unchanged. 644 commands on 16 corpora gave byte-identical output from the old and the new `law.py`:
show on two dates, log, blame on two dates, words, diff and today for five files per corpus, plus world on two dates
and laws over two windows. The only differences were three tracebacks printed when a batch reader was slow to exit
on a busy machine. Those were fixed: the reader is now stopped without a traceback.

| | before | after |
|---|---|---|
| git processes, `show` on one file | 12 | 1 |
| `show` 8 U.S.C. §1182 (in the process, after start-up) | 0.79 s | 0.20 s |
| `log` Romania lege/2003/571 art. 47 (end to end) | 1.56 s | 0.43 s |
| `world`, 16 corpora | 7.2 s | 1.1 s |
| `words` Czechia sb/2007/378 | 9.2 s | 4.1 s |
| the 644 commands, 6 at a time | 770 s | 231 s |

`startup.json` has the end-to-end medians for each fixed provision of `bench.py`.

## Left open

- `words` on Czechia's long statutes is still the slowest read, now spent comparing changed words, not starting
  processes or matching lines.
- A corpus read for the first time still builds its index from its whole history: 10 s for Romania, about 90 s for
  France. Shipping prebuilt indexes would remove that.
