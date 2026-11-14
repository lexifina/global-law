# Round 8: common brief for every track agent

Root `C2 = ~\Documents\us-caselaw-lean-work\caselaw-lean-2` (Git Bash: `~/Documents/us-caselaw-lean-work/caselaw-lean-2`).
Lean/tools tree: `~\Documents\global-law-lean\lean-proofs` (`tools/caselaw2/...`).

1. Read `round8/DESIGN8.md` §0 first: it is binding (rules never rows; no answer-key field; h0 only for the new
   benchmark keys; dev only for the old keys; no external model; one Lean writer; don't touch data/, out/,
   earlier rounds, benchmarks/; your own folder `round8/agents/<you>/` with a truthful `NOTES.md`).
2. Background, read as needed: `round7/ROUND7.md` (state, audits, scores), `round7/DESIGN7.md` (row format §4,
   certificates, claims), `round7/LOG.md`, the round-7 agent folder(s) your brief names (`round7/agents/<x>/NOTES.md`).
   The round-7 frozen build is `round7/stage/v3` (data) + `round7/out/v3` (Lean output: `status.tsv`, `certs.tsv`
   with verdicts per row id, `classes.tsv`, `findings.tsv`). Corpus text and caches: `round6/history/r6lib.py`
   (`text`, windows, zones), `round6/history/cache`.
3. Infrastructure from agent `infra` (wait for the marker file before using it; poll at most every 3 minutes, do
   your own analysis meanwhile):
   - `round8/INFRA_READY`: `round8/certify8.py` (= round-7 certify7 with round-8 ids `t8:` / `h8:`; same JSON
     input), `round8/stage8.py`, `wsl/r8_run.sh`, `round8/score8.sh`.
   - `round8/bench_h0/READY`: the h0-only benchmark scorers; per-case h0 outcomes of the base build `v3` in
     `round8/results/v3/bench/<key>.h0.cases.tsv` (keys `fjc_idb_appeals`, `shadow_docket`, `scdb_disposition`,
     `state_overruled_tables`) and `python round8/bench_h0/score_h0.py --out <outdir> --data <stagedir> --label <x>`
     to score any build of yours on h0. Read only these h0 files; never the files under `benchmarks/` other than
     `SOURCE.md`, `MAPPING.md`, `DISAGREEMENTS.md`.
   - `round8/audit/READY`: `round8/audit/HOWTO.md` — how to build a blind audit pack (≥ 80 items, random by fixed
     seed from the whole certified class, stratified, ≥ 10% decoys) and run it with blind `model: "opus"` auditor
     sub-agents that see only the pack and the auditor brief. Track agents run their own audits this way; you never
     pick or reorder items by hand and never tell the auditor anything about the rule or expected answer.
4. Measuring your own variant: stage it (`round8/stage8.py <you>_<v> --delta <your cert folder>`), run Lean with
   `NOBUILD=1` unless your rows need a round-8 Lean rule
   (`MSYS_NO_PATHCONV=1 NOBUILD=1 wsl.exe -d Ubuntu -- bash -lc 'NOBUILD=1 bash /mnt/c/.../wsl/r8_run.sh <name>'`),
   score with `bash round8/score8.sh <name>`. One Lean run takes about 2–3 minutes and 8 cores; do not run more
   than one at a time yourself.
5. Readers: spawn reader sub-agents with `model: "opus"`, each with a brief file you wrote (in your folder) and its
   own answer file; up to ~20 at once per track. Readers see corpus text only, never a key.
6. Installation bar: a status-changing class is installed only if its blind audit is about ≥ 90% (point estimate),
   ≥ 80 items (or the whole class when smaller), Wilson 95% reported. If it needs a Lean change, write
   `LEAN_REQUEST.md` in your folder (rule, check, effect, theorem) and say so in your final report.
7. Your final message to the lead: what you built, counts, the audit result(s) with intervals, the delta folder(s)
   that are ready to stage, the h0/dev effect you measured, and open points. Keep it short and factual.
