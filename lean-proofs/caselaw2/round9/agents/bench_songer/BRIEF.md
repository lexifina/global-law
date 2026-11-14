# Dataset agent `bench_songer` (round 9): a NEW fresh held-out key — Songer Courts of Appeals Database TREAT

You build a held-out test that nobody has touched. You are a dataset agent under `benchmarks/CONTRACT.md` (read it
first, and `benchmarks/common/benchlib.py`). Root `C2 = ~\Documents\us-caselaw-lean-work\caselaw-lean-2`.
Work in a NEW folder `benchmarks/songer_treat/` (yours alone) and notes in `round9/agents/bench_songer/NOTES.md`
(truthful clock times from `date`, a line at least every 15 minutes).

Isolation (binding): never open anything under `round9/agents/` except this folder and `round9/agents/bench_songer/`;
never talk to the round-9 track agents; never score any model build (no `score.py` run on any `out/` dir at all — the
lead scores v8e and the frozen round-9 build once, after the freeze). Do not write anything outside
`benchmarks/songer_treat/` and `round9/agents/bench_songer/`. No external model. Web: at most 10 searches.

## Source
Songer U.S. Courts of Appeals Database (1925–1996) and the Kuersten–Haire update (1997–2002): `TREAT` = the court of
appeals' treatment of the decision below (affirmed, reversed, vacated, remanded, …), with the appellate citation.
See `round6/research/lower_court_sources.md` §3b (URLs; the South Carolina site's TLS certificate has expired and
songerproject.org has a name mismatch: try http://, the ICPSR/other public mirrors, the Kuersten–Haire update pages,
Harvard Dataverse; do not bypass a login or a terms page; if the data cannot be fetched openly within ~30 minutes,
write SOURCE.md "not obtained" with what you tried, and stop).

## Freshness
Exclude every case that an earlier key already holds: the Shepardized Courts of Appeals sample (`round6/shepardized/`
— you may read its case list only to exclude), and every appellate or district decision that is a unit of
`benchmarks/fjc_idb_appeals/key_nodes.tsv` (either half; exclusion only). Record the counts excluded.

## Do
1. Download into `benchmarks/songer_treat/raw/<file>/` (own empty folder each; untrusted; `python -I`); `SOURCE.md`.
2. Link: the appellate decision to its corpus node (F./F.2d/F.3d volume+page, date, circuit); the decision below
   (district court decision) only where an independent, non-model source identifies it (e.g. a published decision
   below that the source or the corpus metadata names; or the source's own docket/district fields joined to a
   unique published district decision of that docket within a date window — decide and write the method down before
   scoring; never read model output: `round*/out/`, `status.tsv`, `history.tsv`, `certs.tsv`). Link failures by reason.
   If too few decisions below are linkable (< 200), say so and stop at SOURCE + link report.
3. `MAPPING.md` BEFORE any scoring (TREAT → expected model class; like `benchmarks/fjc_idb_appeals/MAPPING.md`),
   `key.tsv` with h0/h1 from `benchlib.split_half("songer_treat", <unit key>)` (50/50 hash).
4. `score.py` per CONTRACT; test ONLY on a synthetic build under `round9/agents/bench_songer/fake/`, never on a model
   build. `REPORT.md` with link figures only. Write `benchmarks/songer_treat/READY` when the self-test passes.
Report to the lead: what was built, n, linked, failure reasons, n per half, expected-class counts, exclusions, the
score command — nothing else about the key's contents.
