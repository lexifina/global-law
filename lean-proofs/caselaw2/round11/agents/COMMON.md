# Round 11: common brief for every track agent

Root `C2 = ~\Documents\us-caselaw-lean-work\caselaw-lean-2` (Git Bash: `~/Documents/us-caselaw-lean-work/caselaw-lean-2`).
Lean/tools tree: `~\Documents\global-law-lean\lean-proofs` (`tools/caselaw2/...`).

1. Read `round11/DESIGN11.md` §0 first: it is binding (rules never rows; no answer-key field; h0 only for the
   round-8 keys; dev only for old keys; Songer / Brace & Hall / Federal Circuit keys CLOSED; nothing about any
   round-11 fresh key; no external model; one Lean writer; **disk rule §0.9: one live variant, clean as soon as
   scored**; your own folder `round11/agents/<you>/` with a truthful `NOTES.md`, a line at least every 10 minutes).
2. Background, read as needed: `round10/ROUND10.md` (state, audits, scores, plateau analysis), `round10/DESIGN10.md`,
   `round10/LOG.md`, the round-10 (and round-9/8) agent folder(s) your brief names (`round10/agents/<x>/NOTES.md`,
   their scripts and `work/` files — reuse them; copy into your folder what you change; never write into round10/).
   The round-10 frozen build is `round10/stage/v10d` (data) + `round10/out/v10d` (Lean output: `status.tsv`,
   `certs.tsv` with verdicts per row id, `classes.tsv`, `findings.tsv`, `summary.tsv`). Corpus text and caches:
   `round6/history/r6lib.py` (`text`, windows), `round6/history/cache`; part zones: `round9/agents/calpart9/`
   (`partzone.py`, `build_zones.py`), `round10/zones10.py`. h0 outcomes of v10d per case:
   `round10/results/v10d/bench/<key>.h0.cases.tsv`.
3. Infrastructure from agent `infra11` (wait for `round11/INFRA_READY` before certifying / staging; poll at most every
   3 minutes and analyse meanwhile; the round-10 tools work for analysis — never write into round10/):
   `round11/certify11.py` (ids `t11:` / `h11:`, base v10d), `round11/stage11.py`, `wsl/r11_run.sh`,
   `round11/score11.sh`, `round11/clean11.sh`; `round11/audit/HOWTO.md` (marker `round11/audit/READY`): blind audit
   packs (≥ 80 items, seeded random from the whole certified class, stratified, ≥ 10% decoys), two blind
   `model: "opus"` auditor sub-agents that see only the pack and the auditor brief. Run names `round11/audit/r11<letter><nn>/`.
4. Measuring your variant: `python -X utf8 round11/stage11.py <you>_<v> --delta <your cert folder>`;
   `df -h /c`; `MSYS_NO_PATHCONV=1 wsl.exe -d Ubuntu -- bash -lc 'NOBUILD=1 bash /mnt/c/Users/$USER/Documents/us-caselaw-lean-work/caselaw-lean-2/wsl/r11_run.sh <name>'`
   (a few minutes; one run of yours at a time; the script queues when two runs are active);
   `bash round11/score11.sh <name> noold`; then `bash round11/clean11.sh <name>` once you have the numbers.
   The effect is measured against v10d (`round10/results/v10d/`).
5. Readers: spawn reader sub-agents with `model: "opus"`, each with a brief file you wrote (in your folder) and its
   own answer file; up to ~12 at once per track. Readers see corpus text only, never a key. A reader silent for 15
   minutes: re-issue its pack to a new reader.
6. Installation bar: a status-changing class is installed only if its blind audit "right" (exact kind + scope,
   DESIGN11 §3) is ≥ ~90% (point estimate), ≥ 80 items (or the whole class when smaller), Wilson 95% reported. If it
   needs a Lean change, write `LEAN_REQUEST.md` (rule, check, effect, theorem) and note it in NOTES.md.
7. Time box: report within ~100 minutes of your start; report early what is ready rather than polish. Final
   message to the lead: what you built, counts, audit result(s) with intervals, the delta folder(s) ready to stage
   (and any `--remove` / `--replace` file), the h0/dev effect you measured vs v10d, open points, and the headroom you
   see left (counts and reasons). Short and factual.
