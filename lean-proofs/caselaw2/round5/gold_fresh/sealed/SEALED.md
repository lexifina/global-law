# SEALED — do not read

This folder holds the held-out half of the fresh answer key (round 5) and everything from which it could be rebuilt.

- **No model-building agent may open, list, grep, or otherwise read anything in this folder**: not `test.tsv`, not
  `all_pairs.tsv` / `all_rows.tsv`, not `src/` (the full source lists, which contain both halves), not `results/`,
  not `build_report.json` / `build_stdout.txt`.
- Do not re-fetch or re-read the underlying lists either (Wikipedia "List of overruled United States Supreme Court
  decisions"; Blaustein & Field 1958 appendix; Gerhardt 1991 appendix; Payne v. Tennessee n.1 as a list). They contain
  the test half.
- Model builders use only `../dev/dev.tsv` and `python ../score_fresh.py --split dev ...`.
- The test half is scored **once, at the end**, by the evaluation agent:
  `python round5/gold_fresh/score_fresh.py --split test --status <status.tsv> --label <name>`.
  Every test run appends a line (timestamp, label, arguments, result hash, status.tsv hash) to `TEST_RUNS.log` here.
  A run on the frozen round-4 output (`baseline-round4`) is the expected first line; any further line before the
  final scoring needs an explanation.
- Do not delete or edit `TEST_RUNS.log`.

Split rule: sha1 of the overruled decision's U.S. citation, mod 2 (0 = dev, 1 = test), so an overruled decision is
never in both halves. See `../GOLD_FRESH.md`.
