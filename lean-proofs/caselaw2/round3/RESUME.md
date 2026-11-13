# Round 3 resume: rules for every item agent (read after BRIEF.md)

The first round-3 coordinator and all of its agents were cut off by a usage limit at about 22:55 on 12 Nov 2026,
25 minutes in. You are resuming ONE item. Your predecessor's partial work is in `C2/work/round3/<item>/` and, for
some items, in `lean-proofs/tools/caselaw2/` (scripts dated after 22:39). `BRIEF.md` still binds, with these changes.

1. First establish the state from files: what your predecessor finished, what was installed into `C2/data/`
   (compare live files with `*.pre_round3.tsv` and with the `delta/` or `installed_*` files in your folder), what is
   half done. Scripts may be mid-edit: read before you run. Do not redo finished work. Do not re-read packs that have
   a complete answer file.
2. Write `C2/round3/<item>.md` NOW with the state you found, and update it after every stage (before/after numbers,
   files, row counts, validation, what is left). You may be cut off too: a stage that is not in the log and not in a
   file is lost. Reader subagents must write their answer files incrementally and one file per pack, so a re-run
   skips finished packs.
3. Time box: 30 minutes of wall clock from your start (`date`). At 25 minutes stop starting new work, install what is
   finished and validated, finish the log. Anything not started that would take more than the remaining time: list
   it under "Next round" and do not start it.
4. There is no `lean` agent. Lean, the WSL mirror, `tools/caselaw2/ref/` (reference engine), `audit/`, `out/`,
   `eval/score_final.txt`, `ROUND3.md` and the report belong to the coordinator. Do not build or run Lean or WSL.
   You may run the Python reference on PRIVATE copies to measure (hard-link the live data files into your folder as
   `queue/measure.py` does), at most two reference runs in total (each 2-6 minutes, 2 GB), and only if your item
   changes status or findings. The coordinator's final run gives the integrated numbers.
5. Installs: deltas by key under `C2/data/.install.lock` exactly as BRIEF rule 12. Write `<name>.tsv.tmp`, check the
   row and column counts, then rename. Never leave a `.tmp` or a truncated file. `*.pre_round3.tsv` backups already
   exist for treatments, treatments_items, cert_text, window_sha, cite_index, reader_rejects: do not overwrite them.
   Save one for any other file before you first change it.
6. Only certificate rows that pass the current checker rules go in (`reader/certify2.py` or your item's own verify
   script). The witness format of `round3/implicit_schema.md` is NOT supported by the checkers this round: no row
   may depend on `data/treatment_witness.tsv`.
7. Subagents: spawn Claude subagents (Agent tool) for reading and blind audits, in parallel batches (up to about 12
   at a time). No external model. Blind auditors get the text and the row only.
8. Do not kill processes you did not start. No git commits. Python edits keep LF.
9. Final message to the coordinator, under 300 words: state found, what you did, before/after numbers, exact file
   paths, what is installed, what is left. Plain facts.
