# caselaw-lean-2: evaluation and audit plan

Owner: eval agent. The eval agent alone reads later courts' notes. The reader, holdings and Lean agents must never read
`gold/`, `eval/audits/*/key.json` or this folder's results until their outputs are frozen.

## Gold (`gold/`, see gold/README.md)
| File | What it judges | Level |
|---|---|---|
| reports_typed.tsv / reports_typed_pairs.tsv | later courts' notes: overruled (in part / on other grounds), abrogated, superseded by enactment, disapproved, receded from, vacated, reversed | pair (target, by, kind, scope) |
| scdb.tsv | SCDB `precedentAlteration` (SCOTUS decision overrules one of its own); `basis` for statutory vs constitutional | SCOTUS decision |
| crs_overruled.tsv | CRS/CONAN table (2016 + current 2022 edition + 2026 supplement) | SCOTUS pair |
| congress_overrides.tsv | Christiansen–Eskridge / Hasen overrides of SCOTUS statutory decisions | decision + statute |
| splits_resolved.tsv | SCOTUS decisions since 1995 granted to resolve a circuit conflict, with US Code subsection and circuits | issue |
| authority_cases.tsv | hand-built authority facts (Kentucky, Bonner, South Corp, California, Pardo, Michigan 1990, unpublished) | unit tests |

## Harness
`python lean-proofs/tools/caselaw2/eval/score.py` writes `eval/results.json` and `eval/tables/*.tsv`.
`score.py --v1` scores v1 (lean-out-v3) on the same gold, as the baseline (`results_v1.json`).

Metrics:
1. **Recall of notes by Lean status.** Count named notes (by ≠ -1) of the status-changing kinds. Each lands in one of
   three outcomes, as v1 did: agree (Lean has a negative status for the target from the same treating decision, no
   later than the first note); another (a negative status from a different decision); none. Broken down by kind,
   scope, system and decade.
2. **Precision of admitted treatments against notes.** For each admitted (by, target), one of: a note names the same
   by; a note on the target names another or none; no note. Most targets are never noted, so this is a lower bound.
   The real precision comes from audit C.
3. **SCDB.** Decision-level recall: flagged SCOTUS decisions with at least one admitted overruling of a SCOTUS
   decision. Precision: the reverse.
4. **CRS.** Pair-level recall on the current table, the 2016 express rows and all 2016 rows. Also the admitted
   SCOTUS-on-SCOTUS pairs found in CRS.
5. **Splits.** Recall of `splits_resolved` (statutory=1): a split detected on the same section (and subsection, and
   ≥ 2 of the named circuits) dated before the SCOTUS decision. Also: splits still reported on or after the
   resolving decision (should be 0 under the resolution theorem).
6. **Certificates.** Rejection reasons by file. Audit D samples per reason.
7. **v1 comparison.** v1's published figures (97% of agreements stated by the overruling decision; about half of
   express overrulings found; 27% of named notes agreed; CRS 70/236 express) are set beside v2's, and beside v1
   re-scored on the new gold.

## Blind audits (`lean-proofs/tools/caselaw2/eval/sampler.py <audit> <n>`)
Every audit writes packets (`in_k.json`) that do not reveal the answer, plus a `key.json`. Subagents read the
packets blind, one shard each, and return JSON. The eval agent scores the answers against the key. Seeds are fixed
(20261112) and sizes are chosen in advance:

| Audit | n | Question | Scores |
|---|---|---|---|
| A gold-notes | 120 (stratified by kind) | Is the note read right: target, by, kind, scope? | precision of the gold itself (per kind) |
| B notes-blind | 120 named negative notes | Does the treating decision itself say it (express / implicit / mentions / absent)? | v1's 66% express. Lean's recall on express notes; agreement precision (v1: 36/37) |
| C admitted | 120 admitted treatments | Is it this court acting on this target (vs report, procedural, separate opinion, wrong target)? Kind, scope? | v2 precision (v1 held-out: 94/120 overruling, 79/120 right target) |
| D rejected | 10 per rejection reason | Was the rejection right? | false-rejection rate per reason |
| E splits (after splits.tsv) | 40 detected + 40 missed gold | Are the two lower decisions really on the same question with opposite answers? | split precision; reasons for misses |

Rules:
- Auditors never see Lean's verdict or the gold label in the packet.
- C and D are drawn only after the reader is frozen, so the sample is held out from the reader's development.
- Each audit is scored once. Re-reading after a model change needs a new seed.

## Status
- Gold built 2026-11-12.
- **Audit A done** (126 notes, 18 per kind; Sonnet reader, blind). Scores are in audits/gold-notes/score.json and
  are against the rebuilt gold (key_rebuilt.json).
  - 106/126 right on target, by and kind (84%); kind 120/126 (95%); scope 120/126; 4 not notes.
  - After the first reading, two general fixes were made: a citation inside a closed parenthetical is never the
    target, and qualifiers after the phrase now count for scope. Audit A is therefore a development check, not a
    held-out one; a fresh-seed re-audit would be the held-out figure.
  - Remaining target misses are mostly subsequent-history chains ("X, aff'd, Y, rev'd on other grounds"), where
    the gold picks the last decision in the chain and the reader picked the first.
- **Audit B done** (120 named negative notes, 3 blind Opus readers; audits/notes-blind/score.json). The named
  decision's own majority:
  - says it in words in 44 (37%); rejects the holding without saying so in 13; only mentions or reports it in 38;
    the target is absent from the excerpts in 25;
  - by kind: overruled 35/72 express; abrogated 4/34 (abrogation is mostly a later court's judgment).
  - v1 on the same pairs: 19 agreements, 18 of them stated expressly (95%; published 36/37). It found 18 of the
    44 express (41%; published "about half").
- C, D, E and metrics 1–6 wait for `data/treatments.tsv`, `out/status.tsv`, `out/certs.tsv`, `out/splits.tsv`.
  LEAN.md marks these outputs as planned; the Lean core is on hold.
