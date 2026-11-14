# Agent `scdb9` (round 9): SCDB disposition, judgment lines and decisions below (move 2)

Read `round9/DESIGN9.md` and `round9/agents/COMMON.md` first. Folder `round9/agents/scdb9/` (NOTES.md). You may read
`benchmarks/scdb_disposition/SOURCE.md`, `MAPPING.md`, `DISAGREEMENTS.md` and the h0 files
(`round8/results/v8e/bench/scdb_disposition.h0.cases.tsv`, `round9/results/*/bench/`) only.

## Background
v8e SCDB h0 recall 1,809/2,407 = 75.2%, precision 97.5%, clean 97.4%. Round 8 (`round8/agents/scdb8/`: NOTES.md,
`anatomy8.py`, `sc8.py`, `sc8sel.py`, `form_scan.py`, `nodisp_scan.py`, `cycle8.sh`, …) miss anatomy (v3, 726):
cited below without accepted anchor 160, **judgment line not read 131**, anchor without cue 79, linker row not in v3
77, row on another decision of the litigation 64 (rehearing-denial orders), partial 62, trial court refused 41.
Readings D1–D5 audited 67/80 overall (r8b01); D2/D2b installed; **D1/D3/D5 23/32 not installed**: the failures were a
denial-of-rehearing citation inside the sentence (the reading attached the act to the rehearing order) and the
"sole / latest decision below" test; also hyphenated line-break forms ("re- versed", "af- firmed", "va- cated").

## Do
1. Re-run the anatomy on v8e h0 misses; read a fresh sample (~40) with opus readers for "judgment line not read" and
   "cited without accepted anchor".
2. Rules: judgment-line reader repairs (de-hyphenation of line-break splits before matching; the forms readers find);
   D1/D3/D5 fixed: a rehearing-denial citation inside the sentence is never the decision below (the decision below is
   the merits decision the denial is attached to); the sole/latest test restated so a later rehearing order or a
   parallel citation does not defeat it; anchors for "decision below cited without accepted anchor" (forms the
   round-8 `anchor` / `anchorWide` lists already take, or a LEAN_REQUEST).
3. Certify (`round9/certify9.py`), stage, NOBUILD run, score (SCDB h0, Shadow h0, Shepardized dev, fresh dev).
   Blind audit each new class FRESH (≥ 80, two auditors, decoys; `--exclude` every round-8 sample of the same class);
   install at ≥ ~90%.
Report: anatomy, rules, counts, audits with intervals, delta folders (+ remove files), h0/dev effect.
