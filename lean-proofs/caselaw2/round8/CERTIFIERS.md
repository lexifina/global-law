# Round 8 certifiers (agent `infra`)

Every certifier below checks against the round-8 base: data `round7/stage/v3`, Lean output `round7/out/v3`. Each
writes a delta folder that `round8/stage8.py <name> --delta DIR` takes. No answer-key file is read by any of them.
Run from the root `C2` (`~\Documents\us-caselaw-lean-work\caselaw-lean-2`).

## 1. `round8/certify8.py`: reader / linker rows (round-7 JSON row format, `round7/DESIGN7.md` section 4)

```
python -X utf8 round8/certify8.py --rows round8/agents/<you>/rows.jsonl [--rows ...] --out round8/agents/<you>/cert --procs 10
```

= `round7/certify7.py` with exactly three changes (diff recorded in `round8/agents/infra/NOTES.md`):
the default `--base` is `round7/stage/v3` (live tables for the base skip, `conflictBase`, base doctrine labels,
reserved ids and the cite-index check), new treatments ids are `t8:<by>:<target>:<start>`, new history ids
`h8:<by>:<target>:<kind>`. The `src` / reader columns still read `r7:<rule>` (unchanged code; the id prefix tells the
round). A row whose (by, target, kind) is already a v3 row is skipped (`in_base_skipped`); a history claim on a v3
row is checked on the v3 row's own certificate and written as a claim line for the v3 id. The cue lists come from
`~/Documents/global-law-lean/lean-proofs/tools/caselaw2/cues/cue_table.json` (as round 7; see `cue_source` in
stats.json). Self-test (00:2x): round-7 antecedent rows with `--base round6/history/stage/final2` give every output
file identical to `round7/agents/antecedent/cert/` after `t7:`/`h7:` -> `t8:`/`h8:`; with the v3 base 1,506 of
1,747 rows are skipped as in v3 and the other 241 are exactly the round-7 rows dropped by `round7/stage_drop_v3.txt`.

## 2. `round8/certify_recog8.py`: recognised-overruling answers (round-5 recog format, `READER_BRIEF_RECOG.md`)

```
python -X utf8 round8/certify_recog8.py --answers <dir with ans_*.jsonl> --items <items.jsonl.gz> \
       --index <pack index tsv: item id, pack_<x>.md, ...> --out round8/agents/<you>/cert_recog [--skip-explicit] ...
```

= `round7/agents/queue/certify_recog.py` (itself `round5/recog/certify_recog.py` with paths only), paths only
changed again: `recog_common` is still imported from `round5/recog` (not edited) with `R.DATA = round7/stage/v3`
(decisions2, cite_index, treatments, treatment_witness, window_sha read live from v3); answers / items / pack index
/ out are required arguments. Ids stay `tw:<Y>:<X>:<start>:<W>` (round 5 layout); a live v3 row with the same id is
handled by the certifier's own `live-identical` / `live-kept` / `replaces-live` logic, and `remove_ids.txt` is NOT
applied by stage8 (pass it with `--remove`). Note: `R.explicit_ok_pairs()` (reads `out/certs.tsv`) is not called by
this certifier; `--skip-explicit` uses the items' own `pair_explicit` field. Self-test: the round-7 queue answers
give 317 class lines, all `live-identical` against v3 (they are in v3), 0 new rows.

## 3. `round8/certify_opwords8.py`: operativeWords answers (round-7 opwords format, `READER_BRIEF_OPWORDS7.md`)

```
python -X utf8 round8/certify_opwords8.py --answers <dir with ans_*.jsonl> --index <packs/index.tsv> \
       --items <items .jsonl.gz> --out round8/agents/<you>/cert_opwords [--trim] [--cues FILE]
```

= `round7/agents/opwords/certify_opwords7.py`, paths only: `BASE = round7/stage/v3` (treatments, cite_index),
`OUTB = round7/out/v3` (certs.tsv: an admitted explicit status-changing (by, target) makes the item
`already-admitted`), ids `t8:<by>:<target>:<start>`; answers / index / items / out are required arguments. Cue lists:
`tools/caselaw2/reader/cue_table.py` (as round 7). Self-test: the round-7 opwords answers give 48 rows (the other
round-7 rows are now `already-admitted` in v3).

## 4. Round-6 `certify6.py` / round-5 originals

Not for round 8: they default to older bases (`round5/stage/final`, `data/`). If a track needs one, copy it into its
own folder with the base path changed to `round7/stage/v3` / `round7/out/v3` and say so in its NOTES.
