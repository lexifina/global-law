# Agent `infra10` (round 10): infrastructure

Read `round10/DESIGN10.md` (§0 binding, §2, §9) and `round10/agents/COMMON.md` first. Folder
`round10/agents/infra10/` (NOTES.md). Model: the round-9 infrastructure of agent `infra9`
(`round9/agents/infra9/NOTES.md`, `round9/{certify9,certify_recog9,certify_opwords9,stage9,freeze9,old_by_class9,
sealed_lines9,shep_sealed9,summary9}.py`, `round9/score9.sh`, `round9/score_sealed9.sh`, `wsl/r9_run.sh`,
`round9/audit/`, `round9/lead/live9.py`). Port it to round 10 on base **v9c**; do not change round-9 files.

**DISK (binding):** C: has ~27 GB free and is shared; WSL's ext4 disk also lives on C:, so WSL writes count too.
`df -h /c` before anything big. The new base must NOT be a copy: stage10 uses `round9/stage/v9c` (+ what it points
to) in place, read-only, and writes only changed tables per variant; the WSL base mirror for v9c must be built from
round 9's existing v9c mirror data dir / base mirror by hard links or symlinks (check what `wsl/r9_run.sh` left in
`~/caselaw2/us-caselaw-lean-work/caselaw-lean-2/` — `data_r9_v9c`, `base_r9_v8e` — and reuse; never copy table files
that are unchanged). Report the sizes you add.

## Build (marker `round10/INFRA_READY` when 1–6 are done and self-tested; tell the lead in NOTES.md)
1. `round10/certify10.py` (+ `certify_recog10.py`, `certify_opwords10.py` if they carry the base path): certify9 with
   ids `t10:` / `h10:` and base `round9/stage/v9c`.
2. `round10/stage10.py <name> --delta DIR … [--remove FILE] [--drop FILE] [--replace FILE] [--table NAME=FILE]`:
   base `round9/stage/v9c` (keep the round-9 EXTRA tables: history_bridge, part_zone, adoption, succession, …; add
   `history_remand` as an extra table for DESIGN10 §4). Unchanged tables not copied (TABLES.txt / MANIFEST as round 9).
   **Part zones:** a new row must be zone-checked like round 9's: v9c's `part_zone.tsv` was built over every round-9
   row (`round9/lead/zones_all`, `round9/agents/calpart9/build_zones.py`); make stage10 (or a helper
   `round10/zones10.py`) add zone lines for the acting nodes of new rows that have none (same builder, same rules),
   so a staged variant's zone table covers its rows. Check with the lead's v9c: staging v9c's own rows with no delta
   must reproduce v9c's tables byte for byte.
3. `wsl/r10_run.sh <name> [ref]`: as r9_run.sh, base mirror v9c (`base_r10_v9c`), NOBUILD = the frozen round-9 binary
   (`~/caselaw2/r9_bin/...22bab5cd...` — find the exact file and sha1 from round9/FREEZE.md / LOG; copy to
   `~/caselaw2/r10_bin/caselaw2_r9v9c` and check its sha1 before each run); without NOBUILD refuses unless
   `round10/LEAN_READY`; two run slots machine-wide (own lock names r10_slot*); `R10BIN=` override; `ref` runs the
   Python reference + diff as round 9 (ask nothing of `ref10`, just keep the hook compatible with
   `round9/agents/ref9/difftest9b.sh`-style use; separate difftest folder per variant name — round 9 had a collision).
   Before each run it prints `df -h /mnt/c` and refuses under 8 GB free.
   **Self-test:** `NOBUILD=1 r10_run.sh v9c_check` on a stage with no delta must reproduce `round9/out/v9c` byte for byte
   (compare every output table), then delete that stage/out/WSL data dir.
4. `round10/clean10.sh <name>`: deletes `round10/stage/<name>`, `round10/out/<name>` and its WSL data/difftest dirs;
   keeps results; refuses names listed in `round10/KEEP.txt` (the lead writes base / best / frozen names there).
5. `round10/score10.sh <name> [beh] [noold] [nobench]` (+ `summary10.py`, `old_by_class10.py`): as score9.sh on
   round-10 paths; h0 only for the four round-8 keys; never h1, never a sealed half, never `songer_treat`,
   `brace_hall_state` or any round-10 fresh key. Self-test: score the v9c_check variant (before deleting it) and
   compare the summary to `round9/results/v9c/summary.txt`.
6. `round10/audit/` (HOWTO.md, READY): port of `round9/audit/` (make_packs10.py, score_audit10.py, decoys10.py,
   more_text10.py, AUDITOR_BRIEF10.md, selftest) — base stage v9c, ids t10:/h10:, run names `r10<letter><nn>`
   (letters: fjc10 f, scdb10 b, syl10 y, shadow10 k, stlink10 t, lead a, infra10 x), decoy pools extended with the
   round-9 audits' known answers if the round-9 tool supports it (else round 9's pools byte for byte), and the
   telling-word guard extended with: syllab, recut, state, remand, bridge, named, bare, footnote, review.
7. `round10/freeze10.py` (+ `--check`) and `round10/score_sealed10.sh <frozen name>` (+ `sealed_lines10.py`,
   `shep_sealed10.py`), LEAD ONLY, never run by you except `--help` / a dry self-test that scores nothing:
   1. fresh lists sealed (sixth use, burned); 2. Shepardized sealed (fifth use, burned);
   3. the four round-8 keys, h1 halves, **third use**, `--label round10` (refused if `results/round10.h1.json` exists);
   4. `songer_treat` and `brace_hall_state`, **second use**, frozen build `--label round10` (all three of h0/h1/all;
      refused if `results/round10.*` exists) — the v9c figures exist from round 9 (`round9.*`), not re-run;
   5. new fresh keys from `round10/FRESH_KEYS.txt` (first use): v9c (`round9/out/v9c` + `round9/stage/v9c`) as
      `--label round9v9c` and the frozen build as `--label round10`; refused if those results exist; skipped (and
      logged) without the file.
   Every run appended to `round10/SEALED_LOG.md` from the scorers' own files. freeze10.py hashes the frozen stage
   tables, out tables, the binary, every round-10 agent script and the scorers (as freeze9; exclude NOTES.md and
   logs so a late note does not break the check — round 9 was refused once by a changed agent file).
8. Live page: `round5/report/sections/98_round10.html` (as 97_round9.html: "Round 10 — in progress", a short plan
   list) and a "Round 10" row in `round5/report/processes.json` (atomic edit: write a temp file then rename; keep
   every other row byte for byte), then run `python -X utf8 round5/report/make_overturned.py` and check it still
   builds. A helper `round10/lead/live10.py` (as `round9/lead/live9.py`) so the lead can update the row's note/state.

Time box ~45 minutes for 1–6 (READY first), then 7–8. Report: what exists, self-test results, sizes added, open points.
