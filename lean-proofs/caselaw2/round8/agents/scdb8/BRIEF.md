# Agent `scdb8` (round 8): Supreme Court merits dispositions (SCDB disposition, h0 diagnosis)

Read `round8/DESIGN8.md` and `round8/agents/COMMON.md` first. Folder: `round8/agents/scdb8/` (NOTES.md).
You may read `benchmarks/scdb_disposition/SOURCE.md`, `MAPPING.md`, `DISAGREEMENTS.md` and the h0 files under
`round8/results/*/bench/` only (never its `key.tsv`, `links.tsv`, `work/`, `raw/`, `results/`). The round-5/7 rule
"SCDB / CRS are burned" concerns the overruling lists under `eval/`; this is a different, new key (same-case
dispositions) and h0 is its dev half.

## Background
SCDB disposition (round 6, h0): recall 1,488/2,407 = 61.8% (Supreme Court reversed/vacated the decision below →
model NEG_HIST), precision 97.8%, clean 98.1%, link rate 32.7%. Round 6 `round6/history/rules/below_sc` (procedural
history sentence, syllabus line, "Reported below", judgment line), round 7 `round7/agents/b4sc/` (B4 a: sole
litigation decision, weak types, modal judgment line; B4 e: re-pointed shared-page citations; R3 nozone/fn/modal 288
rows not installed). Read `benchmarks/scdb_disposition/DISAGREEMENTS.md` for what the round-6 reading found.

## Do
1. After `round8/bench_h0/READY`: from `round8/results/v3/bench/scdb_disposition.h0.cases.tsv` take the h0 misses;
   stratified random sample of ~40 (by era: pre-1900, 1900–45, 1946–90, 1991+, state/federal below), read the Supreme
   Court opinion (corpus), and record where each is lost: no candidate (decision below not cited / cited in a form
   not keyed / old reporters / state court below), candidate without cue, certificate refused (verdict in
   `round7/out/v3/certs.tsv`), linked to the wrong decision of the litigation, partial scope. Counts in NOTES.
2. General rules for the largest causes (run over every SC opinion, not only key cases); guard; certify8.
3. Measure (stage/run/score): SCDB h0, Shepardized dev SC reversed/vacated, Shadow Docket h0 precision, FJC h0
   clean. Blind audit each status-changing class (≥ 80, stratified, decoys; link + effect); install at ≥ ~90%.

Final report: miss anatomy (counts), rules, counts, audits, delta folders, h0/dev effect.
