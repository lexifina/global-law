# Performance and test record

How fast and how right the tools are, run by run, and what each deep test of the repository found.

- `index.html`: the record, newest run last. Open it in a browser; it needs no network.
- `bench.py`: measures this clone and adds a run. It times reading each corpus, `show`, `log`, `blame`, `words`, `diff`,
  `world` and `laws`, and it checks:
  - the fixture tests;
  - that today's text equals the pinned file;
  - that blame covers the text;
  - `verify.py`;
  - `describe.py --check`.
- `runs.jsonl`: every run, one JSON object a line (machine, tree commit, corpora read, timings, checks).
- `findings.json`: what each deep test found and what became of it (fixed, open, or handed to a corpus's builder).
- `report.py`: writes `index.html` from the two files above.

```sh
python tools/countries.py add --no-files czechia romania united-states/federal/usc   # the corpora to measure
python performance/bench.py            # run, record, rewrite index.html (then commit the three files)
python performance/bench.py --no-record
```

A run measures only the corpora checked out in its clone, so compare runs of the same corpora. Each column of the page
says how many there were. `bench.py` names a fixed set of provisions (BENCH), so the same corpora always give comparable
numbers.
