# Round 2: common rules for every agent (read first)

Project: `~\Documents\us-caselaw-lean-work\caselaw-lean-2\` (called C2 below). A Lean model of US
precedent, an independent Python reference, data tables, a reader pipeline and an evaluation.
- Lean: `~\Documents\global-law-lean\lean-proofs\LegalProofs\CaseLaw2\`
- Reference engine: `...\lean-proofs\tools\caselaw2\ref\` (precedent_ref.py, diff.py, drt.py, gen.py, REF_NOTES)
- Tools: `...\lean-proofs\tools\caselaw2\` (reader/, holdings/, eval/score.py, hunt/, courts scripts)
- Docs to read as far as your task needs: C2 `LEAN.md`, `TRUST.md`, `DEVIATIONS.md` (60-73), `DIFFTEST.md` §8,
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
   agents: experiment on a private copy under `C2/work/round2/<your-name>/`, and install a finished file into
   `C2/data/` by writing `<name>.tsv.tmp` and renaming, after saving the original once as
   `<name>.pre_round2.tsv`. Python edits keep LF line endings (open files with newline='\n'). TSVs are UTF-8, LF,
   no header unless SCHEMA says so.
5. Held-out rule: readers never read `gold/`, `events_v3/reports.tsv`, `lean-in-v3/reports.tsv`; gold is used
   only to MEASURE and to classify misses, never to pick rows to admit (except where your task says an
   explicitly separated tier is allowed).
6. Never weaken or edit a locked theorem statement. New theorems go through the registry
   (`audit/audit.py lock`, reason in `wsl/lock_reason.txt`). No `sorry`, `axiom`, `native_decide`.
7. Searches: never recurse over all of `~/Documents`; stay inside the paths above; use timeouts. Do not kill
   processes you did not start. No visible console windows; no background PowerShell scans.
8. Web search only if your task grants a budget; primary sources first.
9. Do not write to `C2/ROUND2.md`, `C2/out/`, `eval/score_final.txt` or the report: the coordinator does the
   final integrated build, runs, scoring and report. Write your log to `C2/round2/<your-name>.md`: before and
   after numbers, what changed (files, scripts, row counts), how it was validated, what is left, and any text
   you want added to DEVIATIONS.md / LEAN.md that you do not own. Your final message to the coordinator: the
   same, in under 400 words, with exact file paths.
10. Plain factual prose in docs (no marketing language). Short sentences.
