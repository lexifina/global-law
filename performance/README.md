# Performance and test record

How fast and how right the tools are, run by run, what each deep test of the repository found, and what was tried to
make the slow paths faster.

- `index.html`: the record. Open it in a browser; it needs no network. It starts with what needs attention in the
  latest run: a failed check, a timing slower than the last comparable run, a command over its budget.
- `bench.py`: measures this clone and adds a run.
  - It times reading each corpus, and `show`, `log`, `blame`, `words`, `diff`, `world` and `laws`. Each command is
    run three times on fixed provisions and the median kept.
  - It checks the fixture tests, that today's text equals the pinned file, that blame covers the text, `verify.py`
    and `describe.py --check`.
  - It records each corpus's commit, the version of `law.py`, and each index cache's size, so a slower run can be
    traced to the code or to the data.
- `runs.jsonl`: every run, one JSON object a line.
- `findings.json`: the before-and-after speeds, each experiment's conclusion, and what each deep test found and what
  became of it (fixed, open, or handed to a corpus's builder).
- `report.py`: writes `index.html` from the two files above.
- `experiments/`: one script and one write-up per experiment, with the script's raw results beside them.

```sh
python tools/countries.py add --no-files czechia romania united-states/federal/usc   # the corpora to measure
python performance/bench.py            # run, record, rewrite index.html (then commit runs.jsonl and index.html)
python performance/bench.py --quick    # one try a command, no fixture tests or describe --check
python performance/bench.py --no-record
```

`bench.py` exits 1 when a check fails or a timing is more than 1.5 times and 1 second slower than the last run on the
same corpora, so a scheduled job can watch it; the run is still recorded.

## Budgets

What a reader should wait at most for one command, as the median of three tries:

| Command | Budget |
|---|---|
| `show`, `log`, `diff` | 3 s |
| `blame` | 5 s |
| `words` | 10 s |
| loading a corpus's index | 3 s |
| `world`, `laws` over every corpus checked out | 60 s |

A command over its budget is outlined on the page and listed at the top. Change a budget in `bench.py` (`BUDGET`) and
`report.py`, and say why in `CHANGELOG.md`.

## Comparing runs

A run measures only the corpora checked out in its clone, so compare runs of the same corpora: regressions are counted
only against the last run that measured exactly the same set. The fixed provisions (`BENCH` in `bench.py`) keep the
same corpora giving comparable numbers. Times include starting Python and git, which on some machines varies by
seconds from one try to the next; that is why each command is tried three times.

## Adding a deep test or an experiment

- A deep test: add an entry to `deep_tests` in `findings.json` (when, title, how, and items with a status of clean,
  fixed, open or handed), then run `python performance/report.py`.
- An experiment: put its script and a write-up in `experiments/`, add an entry to `experiments` in `findings.json`
  (question, result, decision, file), and rerun `report.py`.
