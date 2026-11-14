# Dataset agent `bench_bh` (round 9): a NEW fresh held-out key — Brace & Hall State Supreme Court Data (CC0)

You build a held-out test that nobody has touched. You are a dataset agent under `benchmarks/CONTRACT.md` (read it
first, and `benchmarks/common/benchlib.py`). Root `C2 = ~\Documents\us-caselaw-lean-work\caselaw-lean-2`.
Work in a NEW folder `benchmarks/brace_hall_state/` (yours alone) and notes in `round9/agents/bench_bh/NOTES.md`
(truthful clock times from `date`, a line at least every 15 minutes).

Isolation (binding): never open anything under `round9/agents/` except this folder and `round9/agents/bench_bh/`;
never talk to the round-9 track agents; never score any model build (no `score.py` run on any `out/` dir at all — the
lead scores v8e and the frozen round-9 build once, after the freeze). Do not write anything outside
`benchmarks/brace_hall_state/` and `round9/agents/bench_bh/`. No external model; reading by local opus sub-agents
only if needed. Web: at most 10 searches; fetch the Dataverse API directly.

## Source
Brace & Hall, State Supreme Court Data Project, Harvard Dataverse doi:10.7910/DVN/Z80F7P (CC0; all 50 states'
courts of last resort, 1995–1998 sessions; see `round6/research/lower_court_sources.md` §… "Brace & Hall"). The
variable of interest: the state supreme court's treatment of the decision below (affirmed / reversed / vacated /
remanded / modified …) per case.

## Do
1. Download into `benchmarks/brace_hall_state/raw/<file>/` (each file its own new folder; untrusted; parse with
   `python -I`); `SOURCE.md` (URLs, access date, sha256 of every file, licence quoted, codebook variables used).
2. Link: each case to the corpus decision of the state supreme court (citation / court / date / caption: look at how
   `benchmarks/scdb_disposition/` and `benchmarks/fjc_idb_appeals/` link, reuse `benchlib`); then the decision below
   (the intermediate appellate or trial decision the court reviewed) where the source or the case's own head matter /
   corpus metadata identifies it (decide the method and write it down BEFORE scoring; a link method must not use any
   model output: never read `round*/out/`, `status.tsv`, `history.tsv`, `certs.tsv`). Record link failures by reason.
3. `MAPPING.md` written BEFORE any scoring: source outcome → expected model class (NEG_HIST for reversed/vacated whole;
   PART for partly; CLEAN for affirmed; what is left out), the as-of date, the metrics (recall of reversed/vacated
   linked pairs; precision; clean; link_rate), following the existing keys' mapping style. `key.tsv` with split half
   h0/h1 from `benchlib.split_half("brace_hall_state", <unit key>)` (50/50 hash).
4. `score.py --out <dir> --data <dir> --label <x>` per CONTRACT (writes `results/<label>.<split>.json` for h0, h1, all
   and `results/<label>.cases.tsv`). Test it ONLY on a synthetic build you make yourself under
   `round9/agents/bench_bh/fake/` (a fake status.tsv / history.tsv / treatments.tsv with a few rows built from the key,
   to check every branch of the scorer), never on a model build. `REPORT.md` with link figures only.
5. Write `benchmarks/brace_hall_state/READY` when the scorer passes its self-test.
Report to the lead: what was built, n items, n linked, link-failure reasons, n per half, expected-class counts,
the score command, and nothing else about the key's contents.
