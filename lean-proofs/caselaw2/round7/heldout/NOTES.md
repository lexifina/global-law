# round7/heldout — notes (agent `heldout`)

Times are local clock times from `date`.

## 22:45 start
Read DESIGN7 §0/§8, lower_court_sources.md (Shadow Docket entry), DESIGN6, Shepardized compare.py, GOLD_FRESH.md
(head).

## 22:46–22:48 Shadow Docket Database download (stopped, handed over)
- Downloaded from Harvard Dataverse doi:10.7910/DVN/89VEX8 (v1.0 of the deposit = database v2.0, licence CC0 1.0):
  README.txt, codebook PDF, `shadow_docket_database_v2-0.csv` (MD5s equal the deposit's). See `SOURCES.md`.
- Order-side exploration only (`explore_orders.py`, aggregate counts): corpus Supreme Court order nodes with the
  same docket and the same date exist for almost every order in 1993–2005 and 2010–2020; the corpus holds very few
  Supreme Court nodes in 2006–2009 and after 2020.
- `build_key.py` was written but **never run**: no Shadow key file exists.

## 22:56 change of scope (message from the lead via coordinator)
A separate agent now owns new answer keys in `caselaw-lean-2/benchmarks/` (FJC appeals + crosswalk, Shadow Docket
Database, SCDB disposition fields, pre-1930 state tables). **The Shadow Docket work is handed over**: the files in
`src/` stay as downloaded and are not extended; `build_key.py` / `explore_orders.py` are left as unrun / exploration
code for whoever takes it (they read no model output). `benchmarks/` did not exist at 22:56, so option (2)
(adapter) is not possible now; doing option (1), the time split.

## 22:57–23:16 time-split held-out test (option 1)
- Source: the Supreme Court's own docket JSON (supremecourt.gov, public domain) for every docket number on a corpus
  Supreme Court node dated >= 2021-01-01: 509 records, all HTTP 200, fetched 22:59–23:10 UTC by `fetch_dockets.py`
  (1 req/s, generic client name). Manifest + sha1 in `src_scdocket/`, SOURCES.md.
- Cutoff 2021-01-01: argued in HELDOUT.md §1 (grep of rounds 5–7 briefs/cue lists/notes for post-2020 citation
  forms; only READER_BRIEF3 quotes a 2022 page header as furniture). Builder-seen nodes: `seen_nodes.py` ->
  `work/seen_nodes.txt` (62,892 numbers; sealed folders not walked; bulk files > 5,000 numbers left out).
  Incident, for the record: before the sealed folders were excluded, a first `seen_nodes.py` run and one
  `grep -rl` (file names only, no content printed) walked `round5/gold_fresh/sealed/`; that output was overwritten
  and nothing from it was printed or kept.
- `build_timesplit.py` -> `key/` (256 pairs, 256 Supreme Court nodes; counts in HELDOUT.md §3–4). Judgment parser
  fixed twice on aggregate tallies ("Adjudged to be …" form; "as to" check limited to the judgment clause; cert
  denied with statements added). Spot check 8/8.
- `score_heldout.py` + `fixture/make_and_check.py`: 36 checks pass; guards (FREEZE.md, once per build) tested
  (refusal read nothing). RUNS.log has only fixture-selftest lines. No real model output scored.
- `work/diag_link.py`: aggregate linker diagnosis (court names and counts only).
- Open: the lead should add `round7/heldout/` to DESIGN7 §0.2 (no linker/reader may read it).
