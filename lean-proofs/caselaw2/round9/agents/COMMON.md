# Round 9: common brief for every track agent

Root `C2 = ~\Documents\us-caselaw-lean-work\caselaw-lean-2` (Git Bash: `~/Documents/us-caselaw-lean-work/caselaw-lean-2`).
Lean/tools tree: `~\Documents\global-law-lean\lean-proofs` (`tools/caselaw2/...`).

1. Read `round9/DESIGN9.md` §0 first: it is binding (rules never rows; no answer-key field; h0 only for the round-8
   keys; dev only for the old keys; never anything about the round-9 fresh keys; no external model; one Lean writer;
   don't touch data/, out/, earlier rounds, benchmarks/; your own folder `round9/agents/<you>/` with a truthful
   `NOTES.md`, a line at least every 15 minutes).
2. Background, read as needed: `round8/ROUND8.md` (state, audits, scores, next moves), `round8/DESIGN8.md`,
   `round8/LOG.md`, the round-8 agent folder(s) your brief names (`round8/agents/<x>/NOTES.md`, their scripts and
   `work/` files — reuse them; copy into your folder what you change). The round-8 frozen build is `round8/stage/v8e`
   (data) + `round8/out/v8e` (Lean output: `status.tsv`, `certs.tsv` with verdicts per row id, `classes.tsv`,
   `findings.tsv`). Corpus text and caches: `round6/history/r6lib.py` (`text`, windows, zones), `round6/history/cache`.
   h0 outcomes of v8e per case: `round8/results/v8e/bench/<key>.h0.cases.tsv`.
3. Infrastructure from agent `infra9` (wait for the marker before using it; poll at most every 3 minutes, analyse
   meanwhile; the round-8 tools work for analysis in the meantime):
   - `round9/INFRA_READY`: `round9/certify9.py` (= certify8 with ids `t9:` / `h9:`, base v8e), `round9/stage9.py`,
     `wsl/r9_run.sh`, `round9/score9.sh`.
   - `python round8/bench_h0/score_h0.py --out <outdir> --data <stagedir> --label <x> --results <dir>` scores any
     build on h0 (score9.sh does this into `round9/results/<name>/bench/`).
   - `round9/audit/READY`: `round9/audit/HOWTO.md` — blind audit packs (≥ 80 items, seeded random from the whole
     certified class, stratified, ≥ 10% decoys) run with two blind `model: "opus"` auditor sub-agents that see only the
     pack and the auditor brief. Run names `round9/audit/r9<letter><nn>/`; letters: fjc9 f, scdb9 b, calpart9 p,
     shadow9 k, state9 s, nj9 j, lead a, infra9 x.
4. Measuring your own variant: `python -X utf8 round9/stage9.py <you>_<v> --delta <your cert folder>`;
   `MSYS_NO_PATHCONV=1 wsl.exe -d Ubuntu -- bash -lc 'NOBUILD=1 bash /mnt/c/Users/$USER/Documents/us-caselaw-lean-work/caselaw-lean-2/wsl/r9_run.sh <name>'`
   (2–3 minutes, 8 cores; one run of yours at a time; the script queues when two runs are active);
   `bash round9/score9.sh <name>` (add `noold` to skip the burned lists).
5. Readers: spawn reader sub-agents with `model: "opus"`, each with a brief file you wrote (in your folder) and its
   own answer file; up to ~16 at once per track. Readers see corpus text only, never a key. If a reader is silent for
   20 minutes, stop waiting and re-issue its pack to a new reader.
6. Installation bar: a status-changing class is installed only if its blind audit is ≥ ~90% (point estimate), ≥ 80
   items (or the whole class when smaller), Wilson 95% reported. If it needs a Lean change, write `LEAN_REQUEST.md`
   (rule, check, effect, theorem) and note it in NOTES.md; the lead decides.
7. Time box: aim to report within ~100 minutes of your start. Report early what is ready rather than polish.
   Final message to the lead: what you built, counts, audit result(s) with intervals, the delta folder(s) ready to
   stage (and any `--remove` file), the h0/dev effect you measured, open points. Short and factual.
