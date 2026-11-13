# Round 3: common rules for every agent (read first)

Project: `~\Documents\us-caselaw-lean-work\caselaw-lean-2\` (called C2 below). A Lean model of US
precedent, an independent Python reference, data tables, a reader pipeline and an evaluation.
- Lean: `~\Documents\global-law-lean\lean-proofs\LegalProofs\CaseLaw2\`
- Reference engine: `...\lean-proofs\tools\caselaw2\ref\` (precedent_ref.py, diff.py, drt.py, gen.py, REF_NOTES)
- Tools: `...\lean-proofs\tools\caselaw2\` (reader/, holdings/, eval/score.py, hunt/, courts scripts)
- Docs to read as far as your task needs: C2 `LEAN.md`, `TRUST.md`, `DEVIATIONS.md` (60-79), `DIFFTEST.md` §8-9, `ROUND2.md` and `round2/*.md` (what round 2 did and left),
  `SCHEMA.md`, `hunt/HUNT.md`, `data/COURTS.md`, `data/HOLDINGS.md`, `data/READER.md`, `eval/score_final.txt`,
  `research/doctrine.md` (110 KB: grep for your sections).

Hard rules
1. No Azure, OpenAI or any external LLM call. Model reading and auditing is done ONLY by Claude subagents (the
   Agent tool; if you cannot spawn agents, read yourself and say so). Label such rows `claude-subagent`.
2. No git commits, no git stash, no worktrees. Do not change Windows settings.
3. Lean builds and runs ONLY in WSL Ubuntu (`C2/run_lean_wsl.sh`, `C2/wsl/*.sh`; mirror `~/caselaw2`). From Git
   Bash prefix with `MSYS_NO_PATHCONV=1`. The WSL VM stops when no wsl.exe is attached: long jobs must be one
   attached `wsl.exe` call run with run_in_background. ONLY the agent told it owns Lean may build/audit/run Lean.
   Everyone else measures with the Python reference on Windows Python
   (`python -X utf8 precedent_ref.py run --data <dir> --edges ../lean-in-v3 --out <dir>`; about 1-3 minutes) and
   `tools/caselaw2/eval/score.py` pointed at that output (read score.py for its paths/arguments; add an
   `--out`-style override if it has none, without changing its default behaviour).
4. File ownership. Edit only the files your task owns. Shared data files in `C2/data/` are live inputs of other
   agents: experiment on a private copy under `C2/work/round3/<your-name>/`, and install a finished file into
   `C2/data/` by writing `<name>.tsv.tmp` and renaming, after saving the original once as
   `<name>.pre_round3.tsv`. Python edits keep LF line endings (open files with newline='\n'). TSVs are UTF-8, LF,
   no header unless SCHEMA says so.
5. Held-out rule: readers never read `gold/`, `events_v3/reports.tsv`, `lean-in-v3/reports.tsv`; gold is used
   only to MEASURE and to classify misses, never to pick rows to admit (except where your task says an
   explicitly separated tier is allowed).
6. Never weaken or edit a locked theorem statement. New theorems go through the registry
   (`audit/audit.py lock`, reason in `wsl/lock_reason.txt`). No `sorry`, `axiom`, `native_decide`.
7. Searches: never recurse over all of `~/Documents`; stay inside the paths above; use timeouts. Do not kill
   processes you did not start. No visible console windows; no background PowerShell scans.
8. Web search only if your task grants a budget; primary sources first.
9. Do not write to `C2/ROUND3.md`, `C2/out/`, `eval/score_final.txt` or the report: the coordinator does the
   final integrated build, runs, scoring and report. Write your log to `C2/round3/<your-name>.md`: before and
   after numbers, what changed (files, scripts, row counts), how it was validated, what is left, and any text
   you want added to DEVIATIONS.md / LEAN.md that you do not own. Your final message to the coordinator: the
   same, in under 400 words, with exact file paths.
10. Plain factual prose in docs (no marketing language). Short sentences.

Round 3 additions
11. Time box: about 35 minutes of wall clock from your start. Check `date` when you begin and at each stage. At
    30 minutes stop starting new work, install what is finished and validated, and write your log. Report what did
    not fit honestly. Unfinished or unvalidated rows are NOT installed.
12. Several agents change the same live files this round (`treatments.tsv` and its companions `cert_text.tsv`,
    `window_sha.tsv`, `treatments_items.tsv`, `reader_rejects.tsv`; `decisions2.tsv`; `courts2.tsv`). So installs
    are DELTAS under a lock, never a whole-file overwrite from a stale copy:
      a. take the lock: `mkdir C2/data/.install.lock` (retry every 5 s, up to 5 minutes; write your name into
         `.install.lock/owner`);
      b. re-read the LIVE file, apply only your own change (append your rows / replace only the rows or the column
         you own, by key), write `<name>.tsv.tmp`, rename over the live file;
      c. `rmdir` the lock (remove `owner` first). Never hold it longer than a minute or two. Never delete another
         agent's lock unless its owner file is older than 10 minutes.
    Keep your delta files under `C2/work/round3/<your-name>/` so the coordinator can re-apply or back them out.
    Save the original once as `<name>.pre_round3.tsv` if that backup does not exist yet.
13. Lean, the Python reference engine (`tools/caselaw2/ref/`) and WSL builds/audits/Lean runs are owned by the
    agent named `lean` only. If you need a checker or engine change, write the exact request to
    `C2/round3/requests_to_lean.md` (append) and continue with what works today.
14. Machine load: other agents are running. Use up to 16 processes for git re-reads only if your task is the
    re-read; otherwise stay at 4-6 processes.
15. Sub-readers: if you can spawn Claude subagents (Agent tool), use them in parallel batches for reading and for
    BLIND audits (the auditor is given the opinion text and the row, never gold and never the reader's reasoning).
    Give each a self-contained brief and a file to write. If you cannot spawn, read yourself and say so.
16. The coordinator runs ONE final integration (WSL build, audit, regression, sweep, real-data diff, score,
    report) after all agents finish. Do not run it, and do not write `ROUND3.md`.
