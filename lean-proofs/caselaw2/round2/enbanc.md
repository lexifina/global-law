# Round 2: agent enbanc (bench by court size)

## Before and after

| measure | before | after |
|---|---|---|
| bench panel | 3,292,462 | 3,292,250 |
| bench unknown | 3,186,254 | 3,182,649 |
| bench wholeCourt | 400,001 | 403,778 |
| bench enBanc | 11,284 | 11,324 |
| reference `panelDepartsWithoutEnBanc` (same engine version) | 677 | 543 |
| reference status rows | 69,384 | 69,734 |
| reference findings, all kinds | 142,365 | 142,211 |
| hunt second read, 161 "en banc in fact" decisions labelled en banc / whole court | 123 (76%) | 135 (84%) |
| full-court decisions labelled panel, overruling decisions of intermediate courts (estimate) | 31% | 17% (wide interval: 4–49%) |

The first baseline run, on the reference as it was at the start, gave 671 findings and 69,256 status rows; the reference script changed during the round, so the table uses a rerun of the baseline (`ref_before2`). The Lean figure of 696 was not re-measured (Lean is not mine to run).

## What changed

- New `data/court_size.tsv`: 23,399 rows, 218 courts (tiers L and A), 17,474 court-years. Tags U 22,485, S 818, L 96. Documented in `data/COURTS.md` ("Bench by court size").
- New `tools/caselaw2/bench_size_fix.py` (in `global-law-lean/lean-proofs/tools/caselaw2/`): `scan1` (git re-read, up to 24 processes) → `work/courts/bench3.tsv` (939,751 rows); `table` → `work/round2/enbanc/court_size.tsv`; `decide` → `work/round2/enbanc/relabel.tsv`, `kept.tsv`; `install-table`; `apply` (stream, `.tmp` + rename, backup once, idempotent).
- `data/decisions2.tsv`: 3,817 rows changed in bench and src only (panel → wholeCourt 172, panel → enBanc 40, unknown → wholeCourt 3,605). Columns 1–4 and 6–8 are byte-identical to the input (checked with cmp). Input kept as `data/decisions2.pre_round2.tsv`. A second apply changes nothing.
- src form: `b:size:<sitting>[+<k>out]/<size>[+u<unit>]+was:<old value>/<old evidence>`.
- Appended sections: `data/COURTS.md` ("Bench by court size"), `data/courts_validation.md` §8.

## Scope

The 19,478 decisions of tiers L and A that overrule, disapprove, recede from or decline to follow (by-nodes of `treatments.tsv` plus the citing decisions of `hunt/data/p3_panel.tsv`). The bulk pass over small or always-full intermediate courts (`scan3`) exists in the script but was not run (time box).

## Validation

One blind round, 60 decisions, 4 Claude subagent readers (`claude-subagent`), no labels shown. Wilson 95%.

- Relabels: 29/30 full court, 97% (83–99%). Intermediate courts 24/25, 96% (80–99%): federal 6/6, Alabama 6/6, Louisiana 5/5, other state 7/8. Courts of last resort 5/5.
- The one error was an Arizona division (three of three division judges). Arizona, Washington, Oklahoma Civ. App., Indiana and Tennessee were excluded afterwards (16 relabels dropped); no second sample was drawn.
- Left as panel: 1 full court in 18 scored (6%, 1–26%), 2 unclear.
- Existing enBanc: 9/10 (60–98%); the error is a Michigan conflict panel.
- Files: `work/round2/enbanc/audit/r1/` (sheets, `key.tsv`, `verdict_*.jsonl`, `scored.tsv`, `score.txt`), `audit/make_sheets.py`, `audit/score.py`.

The samples are below the sizes first asked for (60 / 30 / 20); the coordinator cut them to one round of 30 / 20 / 10.

## What is left (next round)

1. Decisions with no judges line (only the author). This is most of the 26 hunt decisions still labelled panel and most pre-1950 opinions. A rule "court size ≤ 3 at the date, so any decision is the whole court" would cover them; the task excluded it for this round.
2. The bulk pass (`scan3`): every panel decision of intermediate courts with size ≤ 3 or a full-court year. Not run; no effect on findings, which arise only from treating decisions.
3. bench is unknown for 3.18M decisions; only overruling decisions of courts of last resort were read.
4. OCR variants of judge names inflate the size (Ohio 1960s). A merge of rare near-duplicates was designed but not built.
5. Federal sizes are authorised judgeships from memory (96 L rows where the data disagree); vacancies cause misses. A check against the Federal Judicial Center tables would settle them.
6. Louisiana five-judge panels remain panel. Whether such a panel may overrule circuit precedent is a doctrine question, not a label question.
7. A larger second blind sample, especially for "left as panel" (n = 18 gives 1–26%).
8. The Michigan conflict panel labelled enBanc (node 3619279) belongs to the conflictPanel rule.

## For the Lean owner

- Nothing in Lean or the reference needs to change: both already treat enBanc and wholeCourt as en banc equivalents.
- Suggestion only: `court_size.tsv` could back a rule "a court of at most 3 judges has no panel", which would remove the need for a label on author-only decisions of small courts.

## Text for docs I do not own

- DEVIATIONS 71: "The bench of overruling decisions is also decided by court size (`data/court_size.tsv`, `tools/caselaw2/bench_size_fix.py`): a decision whose judges line names every regular judge of the court is wholeCourt or enBanc. Reference: `panelDepartsWithoutEnBanc` 677 → 543."
- HUNT §3 / "What to fix" 3: 135 of the 161 decisions the second reader called en banc are now labelled en banc or whole court (was 123).
