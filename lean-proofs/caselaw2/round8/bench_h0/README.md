# Round 8 h0 benchmark shadow (agent `infra`)

h0 half only of the four new keys (`fjc_idb_appeals`, `shadow_docket`, `scdb_disposition`,
`state_overruled_tables`). Tune on these; h1 is scored once by the lead after `round8/FREEZE.md`
(`round8/score_sealed8.sh`). Nothing here reads or writes `benchmarks/` at run time.

## Use

```
python round8/bench_h0/score_h0.py --out round8/out/<name> --data round8/stage/<name> --label <name>
python round8/bench_h0/diff_h0.py v3 <name> [--tsv flips.tsv] [--show N]
```

`score_h0.py` writes `round8/results/<label>/bench/`: `<key>.h0.json` (+ `scdb_disposition.federal.h0.json`,
`.state.h0.json`), `<key>.h0.cases.tsv` (one row per h0 unit with the model's class: the per-case outcomes),
`SUMMARY.tsv`, `<key>.h0.log`; it prints the primary metric and sub-metrics per key as k/n = p [Wilson 95%].
`bash round8/score8.sh <name>` runs it as one step. `diff_h0.py A B` prints per-key metric changes and the h0 cases
that flip (A, B = labels under `round8/results/` or folders).

Base-line (v3 = `round7/out/v3` + `round7/stage/v3`): `round8/results/v3/bench/`.

## What is here

- `build_keys.py`: writes `<key>/key*.tsv` from `benchmarks/<key>/key*.tsv` by script (the only reader of those
  files), keeping the h0 rows at the level each scorer splits: FJC units (`key_nodes.tsv`) and items (`key.tsv`) by
  their own `half`; SCDB rows by `half`; Shadow Docket: the unit is the linked lower node, half from its smallest
  `sc_docket`, class pooled over all its linked items, so the h0 file holds every h0 item (link rate) and every linked
  item of an h0 node (some carry `half` h1: they are part of h0 units), plus synthetic stub items `!h1unit-<n>` (no
  key content) that keep nodes whose unit half is h1 out of h0; state tables: the unit is `x_node` with the half of
  its first linked row, so every h0 row plus every linked row of an h0 unit. `KEYS.json`: counts and sha1s.
- `common/benchlib.py`, `shadow_docket/sdlib.py`: copies, ROOT path only.
- `<key>/score.py`: copies of `benchmarks/<key>/score.py`; changes (diff: `round8/agents/infra/bench_h0_scorer.diff`):
  results folder `--results`, file names `<key>.h0.json` / `<key>.h0.cases.tsv`, split loop h0 only, cases tables
  h0 units only, Shadow Docket federal/state files (`all` split) not written. Metric code unchanged.
- `verify_h0.py`: reproduces the published h0 results. Checked 14 Nov 00:27-00:28: on round 6
  (`round6/history/{out,stage}/final2`) and round 4 (`out/`, `data/`) every `metrics`, `extra_metrics` and `link`
  dict is identical to `benchmarks/<key>/results/round{6,4}.h0.json` (and the SCDB federal/state h0 files): VERIFY OK.
