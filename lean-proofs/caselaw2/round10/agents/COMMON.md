# Round 10: common brief for every track agent

Root `C2 = ~\Documents\us-caselaw-lean-work\caselaw-lean-2` (Git Bash: `~/Documents/us-caselaw-lean-work/caselaw-lean-2`).
Lean/tools tree: `~\Documents\global-law-lean\lean-proofs` (`tools/caselaw2/...`).

1. Read `round10/DESIGN10.md` §0 first: it is binding (rules never rows; no answer-key field; h0 only for the
   round-8 keys; dev only for the old keys; Songer / Brace & Hall closed; never anything about a round-10 fresh key;
   no external model; one Lean writer; **disk rule §0.10**; your own folder `round10/agents/<you>/` with a truthful
   `NOTES.md`, a line at least every 15 minutes).
2. Background, read as needed: `round9/ROUND9.md` (state, audits, scores, next moves), `round9/DESIGN9.md`,
   `round9/LOG.md`, the round-9 (and round-8) agent folder(s) your brief names (`round9/agents/<x>/NOTES.md`, their
   scripts and `work/` files — reuse them; copy into your folder what you change). The round-9 frozen build is
   `round9/stage/v9c` (data) + `round9/out/v9c` (Lean output: `status.tsv`, `certs.tsv` with verdicts per row id,
   `classes.tsv`, `findings.tsv`, `summary.tsv`). Corpus text and caches: `round6/history/r6lib.py` (`text`,
   windows), `round6/history/cache`; part zones: `round9/lead/zones_all/` and `round9/agents/calpart9/`
   (`partzone.py`, `build_zones.py`). h0 outcomes of v9c per case: `round9/results/v9c/bench/<key>.h0.cases.tsv`.
3. Infrastructure from agent `infra10` (wait for `round10/INFRA_READY` before using it; poll at most every 3 minutes
   and analyse meanwhile; the round-9 tools work for analysis in the meantime — never write into round9/):
   - `round10/certify10.py` (= certify9 with ids `t10:` / `h10:`, base v9c), `round10/stage10.py`,
     `wsl/r10_run.sh`, `round10/score10.sh`, `round10/clean10.sh`.
   - `round10/audit/HOWTO.md` (marker `round10/audit/READY`): blind audit packs (≥ 80 items, seeded random from the
     whole certified class, stratified, ≥ 10% decoys), two blind `model: "opus"` auditor sub-agents that see only the
     pack and the auditor brief. Run names `round10/audit/r10<letter><nn>/`; letters: fjc10 f, scdb10 b, syl10 y,
     shadow10 k, stlink10 t, lead a, infra10 x.
4. Measuring your own variant: `python -X utf8 round10/stage10.py <you>_<v> --delta <your cert folder>`;
   `MSYS_NO_PATHCONV=1 wsl.exe -d Ubuntu -- bash -lc 'NOBUILD=1 bash /mnt/c/Users/$USER/Documents/us-caselaw-lean-work/caselaw-lean-2/wsl/r10_run.sh <name>'`
   (a few minutes, 8 cores; one run of yours at a time; the script queues when two runs are active);
   `bash round10/score10.sh <name> noold` (drop `noold` for the burned lists); then
   `bash round10/clean10.sh <name>` once you have the numbers and the variant is superseded. `df -h /c` first.
5. Readers: spawn reader sub-agents with `model: "opus"`, each with a brief file you wrote (in your folder) and its
   own answer file; up to ~12 at once per track. Readers see corpus text only, never a key. If a reader is silent for
   20 minutes, stop waiting and re-issue its pack to a new reader.
6. Installation bar: a status-changing class is installed only if its blind audit is ≥ ~90% (point estimate), ≥ 80
   items (or the whole class when smaller), Wilson 95% reported. If it needs a Lean change, write `LEAN_REQUEST.md`
   (rule, check, effect, theorem) and note it in NOTES.md; the lead decides.
7. Time box: report within ~100 minutes of your start. Report early what is ready rather than polish.
   Final message to the lead: what you built, counts, audit result(s) with intervals, the delta folder(s) ready to
   stage (and any `--remove` / `--replace` file), the h0/dev effect you measured, open points. Short and factual.
