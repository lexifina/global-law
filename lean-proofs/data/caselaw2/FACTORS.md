# Horty factors for Supreme Court holdings (agent: factors)

Written 2026-11-12 (v2). Scripts: `~\Documents\global-law-lean\lean-proofs\tools\caselaw2\factors\`.
Working files: `data/factors_work/`. What the runner needs to read these factors without a workaround:
`caselaw-lean-2/FACTORS_NEEDS.md`.

**Update (Lean agent, 12 Nov, evening): the Lean Horty check has run on the real factors, under Linux Lean in WSL, with no overlay** (the runner now reads `factor_cases.tsv`; FACTORS_NEEDS.md "Status"). 44 binding bases examined, 43 consistent, 1 inconsistent: `horty:preemption_express` (pair `H5955906.0,H6088866.2`); `horty_py.py` agrees on all 51 sub-family bases. The provisional numbers below are confirmed. The text from here on is as written before the run.

**Status (before the run): the Lean Horty check on the real factors is pending Lean (blocked by WDAC).** Windows Application Control
blocks the compiled runner and `lean.exe`. All consistency numbers below are a **provisional Python recomputation, not
Lean**. The fixture did run in Lean before the block.

## Files

| file | rows | notes |
|---|---|---|
| `factors.tsv` | 345 | **v2.** SCHEMA D9: holding_id, factor, side (pi\|delta), inReason (0/1); 269 holdings, all `H…` rows of `holdings.tsv`. Replaced atomically (tmp + rename). |
| `factor_vocab.tsv` | 654 | v2: factor id, sub-family, family, side, name, definition, src. Ids are sub-family index×100 + k (56 sub-families). |
| `factor_cases.tsv` | 354 | Extra, not SCHEMA: holding_id, node, sub-family, issue key `horty:<sub-family>`, outcome (yes = pi), date, number of factors, reason ids, in_factors (1 = has a reason, so it is in factors.tsv), reader, family. |
| `factors.v1.tsv`, `factor_vocab.v1.tsv`, `factor_cases.v1.tsv` | 10,123 / 233 / 2,399 | v1, superseded: 32% factor precision. |
| `factors_work/factor_quotes.tsv` | 444 | Supporting quote for every kept factor (an exact substring of the decision text). |

## Fixture (done; Lean ran it)

- `fixtures/make_fixtures.py` writes `fixtures/data/factors.tsv`. It adds these fixture rows:
  - issues `fx.hortyA` and `fx.hortyB`;
  - SCOTUS holdings on nodes 1 and 3, both good law;
  - two Fifth Circuit anchors. Without them no court examines a base made only of SCOTUS holdings (FACTORS_NEEDS.md
    item 2).
- **Base A** is the Spec.Horty cA/cC pair (hA1 = ⟨{1,2,3},{1},pi⟩, hA3 = ⟨{1,3},{3},delta⟩). It is **inconsistent**.
- **Base B** has hB3 = ⟨{2,4},{4},delta⟩, which distinguishes it. It is **consistent**.
- **Runner output** (`work/horty_fixture_out/`):
  - `inconsistentBindingBase 367 0 fx.hortyA 2 cases 1 Horty`, from the compiled runner;
  - the interpreted current `Run.lean` also flags court 346;
  - there is no row for fx.hortyB, although `splits.tsv` shows both bases were examined.
- No existing fixture row changed.
- **Differential test:** the Python reference has no Horty check, and the new holdings add `conflict` and status rows,
  so `ref_out` must be regenerated.

## Method

**v1** (superseded): a keyword prefilter over SCOTUS decision holdings; 15 families ranked by frequency
(`factors_work/family_counts.tsv`); gpt-6.1-sol abstract vocabularies; gpt-5.4-mini extraction. It gave 2,399 cases,
but factor precision was 0.32 and reason precision 0.34.

**v2:**

1. **Narrower families** (`vocab2.py`, gpt-6.1-sol, 15 calls).
   - Each family is split into the distinct legal questions it mixes: 56 sub-families, 2–4 per family.
   - **Takings:** physical / regulatory use / permit exactions / market-value compensation.
   - **Free speech:** incitement / public venue permits / commercial promotion / public-employee discipline.
   - **Preemption:** express / field / impossibility / obstacle.
   - **Fourth Amendment:** search occurred / seizure occurred / warrantless home entry / good-faith suppression.
   - **Miranda:** custody / interrogation / warnings and waiver / confession voluntariness.
   - The other families are split in the same way.
   - Each sub-family has one yes/no question and 10–14 **concrete, observable** fact factors; tests and conclusions
     are excluded.
2. **Second pass** (`verify2.py`, gpt-6.1-sol, reasoning low, one call per v1-accepted case, 2,399 calls).
   - The model chooses the sub-family the Court actually decides, or none, and gives the outcome.
   - For **every** factor of that sub-family it gives an explicit present/absent, a verbatim quote, and a reason flag.
3. **Filter** (`build2.py`).
   - A factor is kept only if it is marked present and its quote is an **exact substring of the decision text**. The
     check is made inside one excerpt segment, and each segment is text[s:e] of the normalised text. 6 quotes failed.
   - A case enters `factors.tsv` only if it has at least one reason factor, because in Horty every precedent has a
     reason. In v1, cases with an empty reason caused 68% of the conflicts.

**Funnel:**
- 2,399 cases read.
- 1,333 matched no sub-family. They mostly decide questions outside the narrowed sub-families, e.g. general
  content-based speech rules or Chevron step-one statutory merits.
- 29 were not decided or had an unclear outcome.
- 683 had no factor present.
- 85 had factors but no reason.
- **269 cases enter `factors.tsv`.**
- 444 factors were kept and 11,738 marked absent.

**Coverage is the cost:** 269 cases against v1's 2,399. 45 sub-families have at least 2 cases, and 34 of those have
both outcomes. The largest are miranda_warnings_waiver (19), preemption_express (16), takings_physical (16),
dormant_commerce_nondiscriminatory_tax_burdens (23), standing_personal_injury (13) and agency_deference_statutory_merits
(11).

## Running the Horty check (pending Lean, blocked by WDAC)

- `build2.py` rewrites the overlay `work/horty_real/`. It contains:
  - hard links to `data/`;
  - the 269 holdings re-keyed onto `horty:<sub-family>` question issues, with their answers;
  - one Second Circuit anchor per sub-family;
  - an empty edges directory.
- Once Lean is allowed, run:

```bash
cd ~/Documents/us-caselaw-lean-work/caselaw-lean-2
bash ~/Documents/global-law-lean/lean-proofs/tools/caselaw2/factors/run_noBuild.sh 4 work/horty_real/data work/horty_real/edges work/horty_real/out
#   (INTERP=1 in front for `lake env lean --run`, if the compiled runner stays blocked)
grep inconsistentBindingBase work/horty_real/out/findings.tsv
python ~/Documents/global-law-lean/lean-proofs/tools/caselaw2/factors/horty_py.py   # uses Lean's status.tsv; column `agree` compares with the runner
```

- **Expected:** one finding for preemption_express, at the anchor court 272 and its trial court, and none for the
  other sub-families.

## Consistency (provisional Python recomputation, not Lean)

How it was computed (`horty_py.py`):
- the `Spec.Horty.consistent` pair test on each sub-family's SCOTUS base;
- with no Lean status, good law is approximated by removing holdings that an explicit scope-`all`
  overruling/abrogation targets (none of the 269 is targeted).

Results (`factors_work/horty_bases.tsv`):
- **50 of 51 sub-family bases are consistent.** Of the 34 non-trivial bases (≥ 2 cases, both outcomes), 33 are
  consistent.
- **1 is inconsistent: preemption_express.** It has 16 cases and **4 conflicting pairs**, all through *Aloha Airlines
  v. Director of Taxation* (1983, H6088866.2). Removing that one case makes the base consistent.
- **Why the pairs conflict:** gpt-6.1-sol read all 4 pairs (`conflict_kinds2.jsonl`), and **all 4 are
  coarseVocabulary**. The extractions are right, but the factor "exception names state regulatory subject" does not
  tell an exception that *covers* the challenged law from one that merely *names* the subject. Aloha's tax fell
  outside the saving clause. The pilotage, licensing and safety cases fell inside it.
- **What would fix it:** a finer factor, "challenged law falls within the express saving clause" (delta).
- **Conflict breakdown, v1 → v2:**
  - extraction error 126 → 0;
  - different question 26 → 0;
  - coarse vocabulary 5 → 4;
  - doctrinal change 2 → 0.
  - v1's two doctrinal-change pairs were *Loper Bright* against Chevron-era cases. Those cases did not survive the
    stricter v2 pass.

## Blind spot-check, v2 (30 extractions, 2 per family; 3 Claude subagents; Wilson 95%)

Judges saw the excerpt, the question, the claimed outcome and factors (not the quotes), and no model, confidence or id
(`factors_work/val2/`).

| measure | v2 | 95% CI | v1 |
|---|---|---|---|
| **Factor present (precision)** | **37/40 = 0.93** | 0.80–0.97 | 0.32 |
| **Reason flag correct** | **31/35 = 0.89** | 0.74–0.95 | 0.34 |
| Court decides the question | 28/30 = 0.93 | 0.79–0.98 | 0.87 |
| Outcome correct (of decided) | 28/28 = 1.00 | 0.88–1.00 | 0.88 |
| Item fully right (decides, outcome, every factor and reason) | 26/30 | | 2/30 |

The misses:
- two single-Justice in-chambers stay opinions read as decisions: *California v. Green* on remand, and *INS v.
  Legalization Assistance Project*;
- *Freeman v. Hewit*: a factor stretched to fit, and the Court rested on the direct-tax rule instead;
- *Mullenix*: high-speed flight was present, but the Court relied on other facts.

**Fix still open:** exclude in-chambers opinions, using decisions2 `form` or the "Circuit Justice" heading.

Reading:
- v2 factors and reasons are usable as data. They stay tag U (model reading), never a premise.
- The remaining inconsistency is a vocabulary gap, not extraction noise.
- **Recall is now the limit:** 1,333 decided cases fit no sub-family. A next pass would add sub-families for the
  biggest gaps (general content-based speech, Chevron statutory merits), then re-run `verify2.py` on the cases with
  `subfamily = none`.

## Tokens and cost (assumed list prices)

| pass | job | model | calls | tokens | cost |
|---|---|---|---|---|---|
| v1 | vocabulary | gpt-6.1-sol | 15 | 0.08M | $0.48 |
| v1 | extraction | gpt-5.4-mini | 3,475 | 10.13M | $9.26 |
| v1 | conflict reading | gpt-6.1-sol | 159 | 0.11M | $0.49 |
| v2 | vocabulary | gpt-6.1-sol | 15 | 0.12M | $0.98 |
| v2 | verification | gpt-6.1-sol | 2,399 | 9.91M | $28.72 |
| v2 | conflict reading | gpt-6.1-sol | 4 | 0.003M | $0.01 |
| **total** | | | | **20.36M** | **$39.94** |

v2 used 10.04M of its 25M budget. Everything together used 20.4M tokens.
