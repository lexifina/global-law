# Local performance and checks

A one-time, general indicator of how fast the tools answer on your own clone, and what they were checked for. It is
not a record to compare over time: timings depend on the machine, its load and the corpora checked out. The hosted
service ([global-law.lexifina.com](https://lexifina.com/api/global-law)) keeps warm caches and text snapshots, so it
answers faster than a fresh clone, text searches especially.

## What to expect on your own machine

From a light run on 15 November 2026 (three small corpora, Antigua and Barbuda, Lazio and New Zealand, one try of
each command on a busy Windows machine) and a fuller run on 4 November 2026 (16 corpora, Romania, Czechia and the US
Code among them):

| What | Typical time |
|---|---|
| A provision on a date, its history, a diff (`show`, `log`, `diff`) | under 1 s |
| The law behind each line (`blame`) | under 1 s |
| The law behind each word (`words`) | under 1 s; 2 to 3 s on long Czech acts |
| The first read of a corpus (its index is built once) | under 1 s for small corpora; 3 to 9 s for the largest |
| `world` and `laws` over every corpus checked out | about 1 s for 3 corpora, 4 s for 16 |

Times include starting Python and git. A text search across a large corpus is the slow path on a clone (it can take
minutes on Romania) and is where the hosted service helps most.

## Files

- `index.html`: the full record of the runs, the checks and what each deep test found. Download it and open it in a
  browser; it needs no network.
- `bench.py`: measures this clone. It times reading each corpus and `show`, `log`, `blame`, `words`, `diff`, `world`
  and `laws` on fixed provisions, and checks that today's text equals the pinned file, that blame covers the text,
  `verify.py`, and (in a full run) the fixture tests and `describe.py --check`.
- `findings.json`: what each speed experiment and deep test found, and what became of it (fixed, open, or handed to a
  corpus's builder). `experiments/` holds each experiment's script, results and write-up.
- `runs.jsonl` and `report.py`: the runs so far, and the script that writes `index.html` from them.

```sh
python tools/countries.py add antigua-and-barbuda/national/acts new-zealand/national/acts   # small corpora to measure
python performance/bench.py --quick --no-record    # one try of each command, nothing written
python performance/bench.py --no-record            # three tries, the fixture tests and describe --check
```

## Budgets

What a reader should wait at most for one command:

| Command | Budget |
|---|---|
| `show`, `log`, `diff` | 3 s |
| `blame` | 5 s |
| `words` | 10 s |
| Loading a corpus's index | 3 s |
| `world`, `laws` over every corpus checked out | 60 s |

## Adding a deep test or an experiment

- A deep test: add an entry to `deep_tests` in `findings.json` (when, title, how, and items with a status of clean,
  fixed, open or handed), then run `python performance/report.py`.
- An experiment: put its script and a write-up in `experiments/`, add an entry to `experiments` in `findings.json`
  (question, result, decision, file), and rerun `report.py`.
