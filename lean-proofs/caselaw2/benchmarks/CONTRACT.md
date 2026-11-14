# benchmarks/ — contract for every dataset agent

HELD-OUT. Model-building agents (round 7 and later) must not open, list or grep anything under `benchmarks/`
except `graph/` output. Nobody tunes the model on these keys; both hash halves are pure held-out tests.

## Builds scored (read only; never write into them)

| label | `--out` | `--data` |
|---|---|---|
| `round4` | `caselaw-lean-2/out` | `caselaw-lean-2/data` |
| `round6` | `caselaw-lean-2/round6/history/out/final2` | `caselaw-lean-2/round6/history/stage/final2` |
| `round7` | `round7/out/<name>` after `round7/FREEZE.md` exists (stage dir named in FREEZE.md) | |

`benchmarks/common/benchlib.py` has `BUILDS`, `load_status` (MAPPING.md model classes NEG_HIST / UNK_HIST /
NEG_OTHER / UNK_OTHER / GOOD at an as-of date; default 20261112), `load_history`, `load_treatments`, `wilson`,
`metric`, `split_half(dataset, key)` (h0/h1), `write_result`.

## Folder layout per dataset `benchmarks/<name>/`

- `SOURCE.md` — URL(s), access date, sha1/sha256 of every downloaded file, licence/terms quoted, what the variable is.
- `MAPPING.md` — written BEFORE any model row is joined: source outcome class -> expected model output; never tuned
  after (changes after first scoring are appended with both results).
- `raw/` — downloads, each in its own empty folder, untrusted, parsed with `python -I`. (Large raw files may be
  kept; do not store copyrighted books, only extracted facts.)
- builder script(s), `key.tsv` (the answer key, one row per linked or unlinked item, with link status and the
  split half `h0`/`h1`), `links.tsv` / link report.
- `score.py --out <dir> --data <dir> --label <x> [--asof yyyymmdd]` — writes
  `results/<label>.<split>.json` for split in `h0`, `h1`, `all` and a per-case TSV `results/<label>.cases.tsv`.
- `DISAGREEMENTS.md` — ~30 disagreements read (corpus text) and classified: model missing / model wrong /
  source wrong / link error / mapping artefact; `source_errors.tsv` with quoted evidence.
- `REPORT.md` — short: link rate and why links fail, every metric with Wilson 95% and n, per build.

## Results JSON (one file per dataset × label × split; written with `benchlib.write_result`)

```json
{
 "dataset": "fjc_idb_appeals",
 "label": "round6",                      // round4 | round5 | round6 | round7
 "split": "all",                          // h0 | h1 | all | dev | sealed
 "row_label": "FJC appeals: district decision reversed/vacated",   // short plain label for the graph row
 "tests": "same-case",                    // same-case | overruling
 "court": "federal",                      // supreme | federal | state | mixed  (court of the decision tested)
 "blind": true,                           // false only for keys the model was tuned on / already seen
 "primary": "recall",                     // which metric is the row's main dot
 "metrics": {
   "recall":    {"k":0,"n":0,"p":0,"lo":0,"hi":0},   // of source-negative linked cases, model marks negative
   "precision": {"k":0,"n":0,"p":0,"lo":0,"hi":0},   // of model-negative linked cases, source negative (omit if not meaningful)
   "clean":     {"k":0,"n":0,"p":0,"lo":0,"hi":0},   // of source-clean linked cases, model shows clean
   "link_rate": {"k":0,"n":0,"p":0,"lo":0,"hi":0}    // key items linked to exactly one corpus decision
 },
 "link": {"n_items": 0, "linked": 0, "fail_reasons": {"not in corpus": 0}},
 "build": {"out": "...", "data": "...", "status_sha1": "..."},
 "asof": 20261112,
 "generated": "2026-11-13T00:00:00+00:00",
 "notes": "free text"
}
```

Use `benchlib.metric(k, n)` for every metric (Wilson 95%). Never fabricate or hand-enter a number.
