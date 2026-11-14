# Dataset agent `bench11` (round 11): ONE new fresh held-out key, if it can be built cheaply

You build a held-out test nobody has touched. You are a dataset agent under `benchmarks/CONTRACT.md` (read it first,
and `benchmarks/common/benchlib.py`). Root `C2 = ~\Documents\us-caselaw-lean-work\caselaw-lean-2`.
Notes in `round11/agents/bench11/NOTES.md` (truthful clock times from `date`, a line at least every 10 minutes).

**Isolation (binding):** never open anything under `round11/agents/` except this folder, nor `round11/LOG.md`,
`PROGRESS.md` or other round-11 lead files; never talk to the round-11 track agents; never score any model build (no
`score.py` run on any real `out/` dir — the lead scores v10d and the frozen round-11 build once, after the freeze);
never read model output (`round*/out/`, `status.tsv`, `history.tsv`, `certs.tsv`, `treatments.tsv`) for linking.
Write only in your new `benchmarks/<new>/` folder and `round11/agents/bench11/`. When READY, write the new folder's
name as one line `<name>` into `round11/FRESH_KEYS.txt` (create it) and nowhere else outside your folders. No external
model; reading by local opus sub-agents only if needed. **Disk:** C: is tight (`df -h /c` first; stop under 8 GB);
raw downloads < 300 MB total; no corpus copies. Web: at most 25 searches/fetches in total; prefer the data host's API.

## Pick the source (first 20 minutes)
The key must be untouched by every earlier round: not FJC IDB, Shadow Docket, SCDB, state overruled tables, Songer,
Kuersten–Haire, Brace & Hall, the Federal Circuit Dataset Project, CRS, the fresh lists, the Shepardized set, the
SCOTUS 2021 time split (see `benchmarks/*/SOURCE.md` and `MAPPING.md` — you may read those two files of every key,
for overlap only, never key.tsv / links / work / results — and `benchmarks/existing/`). It must be openly
downloadable with terms allowing this use (no data-use agreement needing the user's signature: Lindquist is out),
and linkable to the corpus (`graph/nodes.tsv`: decisions to about 2020 for most repos). Candidates:
`round6/research/lower_court_sources.md` (§3c Spill Solberg "Shepardizing the Courts of Appeals Database", §3d en banc
data sets, §3e circuit lists of overruled / abrogated circuit precedent, §4a modern official state lists),
`round6/research/scotus_sources.md`, `round6/research/improvement_plan.md`; or a part of an already-used source that
was demonstrably never in any key (years or variables outside every existing MAPPING.md's population; a variable of
rows the model was tuned on does not count). Read `round10/agents/bench10/NOTES.md` for what round 10 considered and
rejected. Choose the best (test value × open terms) / effort; write the choice and rejected ones (with reasons) in
NOTES.md. If nothing can be built in ~90 minutes, stop and report that.

## Build (as round 10's `bench10` did for its key; the four round-8 keys' builders and `score.py` are your models)
1. Download into `benchmarks/<new>/raw/<file>/` (each file its own new folder; untrusted; parse with `python -I`);
   `SOURCE.md` (URLs, access date, sha256 of every file, licence quoted, variables used).
2. `MAPPING.md` written BEFORE any linking result is compared with anything model-side: source outcome → expected
   model class (NEG_HIST / NEG_OTHER / CLEAN …), as-of date, metrics (recall, precision, clean, link_rate; Wilson
   95%), populations. Link rules written before linking (corpus + source only).
3. `key.tsv` with split half from `benchlib.split_half("<new>", <unit key>)`; `score.py --out <dir> --data <dir>
   --label <x>` per CONTRACT (results/<label>.{h0,h1,all}.json + cases TSV), tested ONLY on a synthetic build under
   `round11/agents/bench11/fake/`. The scorer must ignore node ids it does not know (a staged build may hold extra
   Supreme Court order nodes above the corpus node count). `REPORT.md` with link figures only. `READY` when the
   self-test passes.
Report to the lead: source chosen (and why), n items, n linked, link-failure reasons, n per half, expected-class
counts, the score command — and nothing else about the key's contents.
