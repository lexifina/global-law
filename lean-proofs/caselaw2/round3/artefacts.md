# Round 3: artefacts (agent `artefacts`)

Started 22:41, finished 22:55 (12 Nov 2026). No Lean build, no sync, no git. One WSL dry run of the extraction.
Nothing under `report/` outputs, `out/`, `eval/` or `ROUND3.md` was written; all dry-run outputs are in
`work/round3/artefacts/`.

## The one command for the final refresh

After the final build, runs, `wsl/collect.sh`, scoring and `ROUND3.md`:

```bash
cd ~/Documents/us-caselaw-lean-work/caselaw-lean-2 && bash report/refresh_all.sh
```

It runs, in order, and stops with `refresh_all: FAILED at step N` on the first failure:

| Step | Command | Writes | Time (dry run) |
|---|---|---|---|
| 1 | `wsl.exe -d Ubuntu -- bash -l /mnt/c/.../caselaw-lean-2/wsl/r3_artefacts.sh <jsonl>` | `global-law-lean/caselaw-anatomy.jsonl` | 44 s |
| 2 | `python -X utf8 lean-proofs/tools/caselaw/caselaw_v1v2_anatomy.py <jsonl> report/caselaw-v1-v2.svg --json report/caselaw-v1-v2.json --data data` | the figure and its JSON | 6 s |
| 3 | `<venv python> report/heatmaps/compute.py`, then `plot.py` | `report/heatmaps/series/*`, `series.json`, 6 x png/svg/webp, `heatmaps.json` | 25 s + 25 s |
| 4 | `python -X utf8 report/make_report.py --out ~/Documents/html-reports/caselaw-lean-2.html --artefacts report` | the HTML report | 20 s |

Whole driver without step 1: 78 s. With step 1: about 2 minutes.

Overrides: `OUT=<dir>` (everything into `<dir>`, including the jsonl and the HTML; nothing under `report/` is
touched), `REPORT_HTML=<file>`, `SKIP_WSL=1` (reuse the jsonl), `HM_PY`, `PY`. Dry run used:
`SKIP_WSL=1 OUT=work/round3/artefacts bash report/refresh_all.sh`.

Checks the driver makes: required inputs exist; every output is newer than the start of the run; the number of dots
in the SVG equals the declaration count in the JSON and the sum of the columns; the headline numbers appear in the
SVG; the report has no "failed to render" box; it prints the number of pending boxes and warns if a `.lean` file
changed after step 2.

## The extraction (step 1)

`wsl/r3_artefacts.sh [OUT.jsonl]`: `cd ~/caselaw2/lean-proofs && lake env lean
/mnt/c/Users/<you>/Documents/global-law-lean/lean-proofs/tools/CaseLawAnatomy.lean > tmp`, then copies to OUT.
`lake env lean` elaborates the one file against the existing oleans: it does not build. The `.lean` file is read
from the Windows tree, so no sync is needed. It fails if Lean exits non-zero, if any output line is not a JSON
object (a Lean message), or if there are fewer than 1,000 declarations. It prints declarations per module. Output
goes straight to the Windows path given (default `~\Documents\global-law-lean\caselaw-anatomy.jsonl`,
the place the old file was).

Dry run at 22:43 against the build then in the mirror: 2,587 declarations, 25 modules, 42 s. It includes
`Spec.Lines` (71 raw, 42 drawn, 23 theorems). `CaseLawAnatomy.lean` keeps every `LegalProofs.CaseLaw2.*` module
except `Registry` and `Audit`, so a new module imported by `Core.lean` is extracted automatically. `Run.lean` is
not imported by the extraction (it never was), so it is not in the figure although the generator's I/O column names
it. Not changed: I had one dry run and did not want an untested import in the final.

## What was stale and what was fixed

`lean-proofs/tools/caselaw/caselaw_v1v2_anatomy.py`
- `Spec.Lines` was in no column, so it was silently dropped. The existing `report/caselaw-v1-v2.json` (21:31) also
  came from a jsonl without it. Now in the HOLDINGS + STATUS column.
- A module that no column claims now stops the script with its name (or `--allow-unassigned` to warn). A new round-3
  module must be added to `COLS`.
- The v2 run-over line had fixed numbers (260,054 holdings, 31,841 treatments, 54,940 history events). It now counts
  `data/holdings.tsv`, `treatments.tsv`, `history.tsv` (`--data`). Dry run: 260,349 / 32,457 / 54,940.
- Usage in the docstring named another script. Added `--json` (the summary was only printed), with per-module
  counts, `data_rows`, `generated`. Output written with LF.
- Dry-run figure: v1 56 declarations, 10 theorems; v2 953 declarations (895 before), 161 theorems (138), 22 modules
  (21), 5,483 lines. Rendered with headless Chrome and viewed: no clipped or overlapping labels; 1,009 dots = JSON.
  The figure is dark by design (its own background), unchanged.

`report/heatmaps/compute.py`, `plot.py`
- Output folder override: environment variable `HEATMAPS_OUT` (both scripts). Default unchanged.
- The note's "6.9M decisions" is read from `series.json` (`precision.decisions`).
- Still fixed in the text: "48M citation edges", vmax 40/10/100, the year ranges.
- Dry run on the current `out/` (round 2 final): bad law 47,878 decisions 1990-2019, peak 27 on 30 Jun 2000;
  precedent broken 12,416 events, peak 14 on 14 Feb 1996; US Code unchanged (8,212 / 6,494 / 1,198 / 520). The two
  case-law charts were viewed (WebP): legible on white, no overlap, totals match `heatmaps.json`. The US Code charts
  were not viewed (same inputs and code as before).
- The checked-in `report/heatmaps/*` are older than round 2's `out/` (44,618 and 12,178): stale until the refresh.
- `report/heatmaps/HEATMAPS.md` is hand-written. Its table, totals and peak paragraphs (44,618; 79,065; 29 Jun 2001;
  12,178; 26 Feb 1998) will be wrong after the refresh. The driver prints the new totals and peaks to paste in.

`report/make_report.py`
- New `--artefacts DIR`: where the figure and `heatmaps/` are read (default: the script's folder).
- New last section "14. Improvement rounds": reads every `C2/ROUND<n>.md`, newest first and open, each shown whole
  with its title and modified time. If `round<n>/` exists and `ROUND<n>.md` does not, a pending box. Round 2 had no
  section before (the report only picks up numbers from the docs), so this is new; it sits last so no section
  number changes.
- No "137 theorems", run name (real18, drt9) or round label is hard-coded: those figures come from `Registry.lean`,
  `DIFFTEST.md` §8, `LEAN.md`, `LIMITS.md`, `eval/results.json`, `hunt/summary.json`. `eval/score_final.txt` is not
  read by the report. `wsl/collect.sh` still defaults to `real17` and lists drt up to drt9: pass the round-3 run
  name (not mine to edit).
- Hard-coded and left: the bad-law paragraph calls the peak day "an end-of-term release day" (true for 30 Jun
  2000; check if the peak moves); `"20261112"` as the as-of date in the status table; the heading of
  `limits_table` docstring.
- Dry-run report: 2.36 MB, inputs 93/94 present (missing: `ROUND3.md`), 4 pending boxes (3 old audit boxes + ROUND3),
  no section failed.

## What the coordinator must have in place first, in order

1. Final WSL build (`run_lean_wsl.sh build`) and audit: oleans in `~/caselaw2/lean-proofs`, `Registry.lean` copied
   back. If a new module was added, add it to `COLS` in `caselaw_v1v2_anatomy.py` (step 2 names it otherwise).
2. Final real-data run, copied back: `out/findings.tsv`, `out/status.tsv` (heatmaps), `out/certs.tsv`,
   `summary.tsv`, `splits.tsv`, `status_lines.tsv` (report). Final `data/*.tsv`.
3. `eval/score.py` -> `eval/results.json` (and `results_v1.json`), `hunt/summary.json` if changed.
4. Docs: `ROUND3.md`, and round-3 edits to `LEAN.md`, `DIFFTEST.md` §8, `DEVIATIONS.md`, `LIMITS.md`, `TRUST.md`,
   `data/COURTS.md`, `data/READER.md`.
5. `bash report/refresh_all.sh`.
6. Edit `report/heatmaps/HEATMAPS.md` to the printed totals; re-run step 4 only if wanted (the report does not
   embed that file).

Do not edit a `.lean` file between step 1 and the report: the report then says the figure predates the sources.

## Files

- New: `wsl/r3_artefacts.sh`, `report/refresh_all.sh`, `round3/artefacts.md`.
- Changed: `lean-proofs/tools/caselaw/caselaw_v1v2_anatomy.py`, `report/heatmaps/compute.py`,
  `report/heatmaps/plot.py`, `report/make_report.py` (all LF).
- Scratch: `work/round3/artefacts/` (jsonl, svg, json, `v1v2_check.png`, `heatmaps/`, `caselaw-lean-2.html`).

Not tested: step 1 through the driver (it was run directly, once, as allowed; the driver's path conversion to
`/mnt/c/...` was checked by printing it).
