# Dataset agent `bench10` (round 10): ONE new fresh held-out key, if it can be built cheaply

You build a held-out test that nobody has touched. You are a dataset agent under `benchmarks/CONTRACT.md` (read it
first, and `benchmarks/common/benchlib.py`). Root `C2 = ~\Documents\us-caselaw-lean-work\caselaw-lean-2`.
Notes in `round10/agents/bench10/NOTES.md` (truthful clock times from `date`, a line at least every 15 minutes).

**Isolation (binding):** never open anything under `round10/agents/` except this folder; never talk to the round-10
track agents; never score any model build (no `score.py` run on any `out/` dir at all — the lead scores v9c and the
frozen round-10 build once, after the freeze); never read model output (`round*/out/`, `status.tsv`, `history.tsv`,
`certs.tsv`, `treatments.tsv`) for linking. Write only in your new `benchmarks/<new>/` folder and
`round10/agents/bench10/`. No external model; reading by local opus sub-agents only if needed. **Disk:** C: is tight
(`df -h /c` first; stop under 8 GB); keep raw downloads small (< 300 MB total); no corpus copies. Web: at most 25
searches/fetches in total; prefer the data host's API directly.

## Pick the source (first 20 minutes)
The key must be untouched by every earlier round (not FJC IDB, Shadow Docket, SCDB, state overruled tables, Songer,
Kuersten–Haire, Brace & Hall, CRS, the fresh lists, the Shepardized set, the SCOTUS 2021 time split — see
`benchmarks/*/SOURCE.md` and `benchmarks/existing/`), openly downloadable with terms that allow this use (no data-use
agreement needing the user's signature: Lindquist is out), and linkable to the corpus (`graph/nodes.tsv`: decisions
to about 2020 for most repos). Candidates from `round6/research/lower_court_sources.md` (§3c Spill Solberg
"Shepardizing the Courts of Appeals Database", §3d en banc data sets, §3e circuit lists of overruled/abrogated circuit
precedent, §3f Federal Circuit, §4a modern official state lists) and `round6/research/scotus_sources.md`; or a part of
an already-used source that was demonstrably never in any key (e.g. years or variables outside every existing
MAPPING.md's population — check the MAPPING.md files; a variable of the same rows the model was tuned on does not
count as untouched). Choose the one with the best (test value × open terms) / effort; write the choice and the
rejected ones (with reasons) in NOTES.md. If nothing can be built in ~90 minutes, stop and report that.

## Build (as `round9/agents/bench_bh/BRIEF.md` did; read it and `benchmarks/brace_hall_state/SOURCE.md` /
`MAPPING.md` / `link.py` / `score.py` as the model — they are dataset files, allowed to you)
1. Download into `benchmarks/<new>/raw/<file>/` (each file its own new folder; untrusted; parse with `python -I`);
   `SOURCE.md` (URLs, access date, sha256 of every file, licence quoted, variables used).
2. `MAPPING.md` written BEFORE any linking result is looked at against anything model-side: source outcome → expected
   model class (NEG_HIST / NEG_OTHER / CLEAN …, as the existing keys), as-of date, metrics (recall, precision, clean,
   link_rate; Wilson 95%), populations. Link rules written before linking (corpus + source only).
3. `key.tsv` with split half from `benchlib.split_half("<new>", <unit key>)`; `score.py --out <dir> --data <dir>
   --label <x>` per CONTRACT (results/<label>.{h0,h1,all}.json + cases TSV), tested ONLY on a synthetic build under
   `round10/agents/bench10/fake/`. `REPORT.md` with link figures only. `READY` when the self-test passes.
Report to the lead: source chosen (and why), n items, n linked, link-failure reasons, n per half, expected-class
counts, the score command — and nothing else about the key's contents.
