# Round 12: common brief for every track agent

Root `C2 = ~\Documents\us-caselaw-lean-work\caselaw-lean-2` (Git Bash: `~/Documents/us-caselaw-lean-work/caselaw-lean-2`).
Lean/tools tree: `~\Documents\global-law-lean\lean-proofs` (`tools/caselaw2/...`), read-only for you.

1. Read `round12/DESIGN12.md` §0 first: it is binding (rules never rows; no answer-key field; h0 only for the
   round-8 keys; dev only for old keys; Songer / Brace & Hall / Federal Circuit / bhk_enbanc keys CLOSED; nothing
   about any round-12 fresh key; no external model; no Lean change unless the lead decides one; **disk rule §0.9: one
   live variant, clean as soon as scored**; your own folder `round12/agents/<you>/` with a truthful `NOTES.md`, a line
   at least every 10 minutes; never idle on background work without a deadline).
2. Background, read as needed: `round11/ROUND11.md` (state, audits, scores, plateau analysis, ranked moves),
   `round11/DESIGN11.md`, `round11/LOG.md`, and the round-11 agent folder(s) your brief names
   (`round11/agents/<x>/NOTES.md`, their scripts and `work/` files — reuse them; copy into your folder what you
   change; never write into round11/ or earlier). The round-11 frozen build is `round11/stage/v11d` (data) +
   `round11/out/v11d` (Lean output: `status.tsv`, `certs.tsv` with verdicts per row id, `classes.tsv`,
   `findings.tsv`, `summary.tsv`). Corpus text and caches: `round6/history/r6lib.py` (`text`, windows),
   `round6/history/cache`; part zones: `round9/agents/calpart9/`, `round11/zones11.py`. h0 outcomes of v11d per case:
   `round11/results/v11d/bench/<key>.h0.cases.tsv`.
3. Infrastructure from agent `infra12` (wait for `round12/INFRA_READY` before certifying / staging; poll at most every
   3 minutes and analyse meanwhile — the round-11 tools work for analysis on v10d paths; never write into round11/):
   `round12/certify12.py` (ids `t12:` / `h12:`, base v11d), `round12/stage12.py`, `wsl/r12_run.sh`,
   `round12/score12.sh`, `round12/clean12.sh`; `round12/audit/HOWTO.md` (marker `round12/audit/READY`): blind audit
   packs (≥ 80 items, seeded random from the whole certified class, stratified, ≥ 10% decoys), two blind
   `model: "opus"` auditor sub-agents that see only the pack and the auditor brief; `--exclude <earlier sample.tsv>`
   matches by (table, by, target, kind). Run names `round12/audit/r12<letter><nn>/`.
4. Measuring your variant: `python -X utf8 round12/stage12.py <you>_<v> --delta <your cert folder>`;
   `df -h /c`; `MSYS_NO_PATHCONV=1 wsl.exe -d Ubuntu -- bash -lc 'NOBUILD=1 bash /mnt/c/Users/$USER/Documents/us-caselaw-lean-work/caselaw-lean-2/wsl/r12_run.sh <name>'`
   (a few minutes; one run of yours at a time; the script queues when two runs are active);
   `bash round12/score12.sh <name> noold`; then `bash round12/clean12.sh <name>` once you have the numbers.
   The effect is measured against v11d (`round11/results/v11d/`).
5. Readers: spawn reader sub-agents with `model: "opus"`, each with a brief file you wrote (in your folder) and its
   own answer file; up to ~10 at once per track. Readers see corpus text only, never a key. A reader silent for 15
   minutes: re-issue its pack to a new reader.
6. Installation bar: a status-changing class is installed only if its blind audit "right" (exact kind + scope,
   DESIGN12 §3) is ≥ ~0.90 (point estimate), ≥ 80 items (or the whole class when smaller), Wilson 95% reported. If it
   needs a Lean change, write `LEAN_REQUEST.md` (rule, check, effect, theorem) and note it in NOTES.md — and tell the
   lead early (final-message style is not needed for that: write the file; the lead watches folders).
7. Time box: report within ~90 minutes of your start; report early what is ready rather than polish. Final message to
   the lead: what you built, counts, audit result(s) with intervals, the delta folder(s) ready to stage (and any
   `--remove` / `--drop` / `--replace` file), the h0/dev effect you measured vs v11d, open points, and the headroom
   you see left (counts and reasons). Short and factual.
