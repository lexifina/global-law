# Testing and improving the 38 models: protocol (binding for every agent; read first)

Goal (Alan, 2026-11-19): test the 38 Lean tax models against as much OECD data and as much country-specific data as
possible, make the implementation as good as possible, keep a record of everything, and make sure we both improve the
models and run **fair** tests on each dataset.

## 1. Datasets are registered before they are used
`~/cmp20/tests/REGISTRY.md` lists every dataset: id, publisher, URL, version/vintage, fetch date, sha256 of the raw
file, countries, what it measures (which output lines), the household/grid definition, and its **role**:
- `dev`: may be looked at while improving models;
- `holdout`: may only be scored by the test-infrastructure agent, at most once per evaluation round; nobody improving a
  model reads its values or per-case diffs (only the aggregate score is published until the round is closed).
Raw files live in `~/cmp20/tests/data/<id>/` and are never edited; parsers write normalised JSONL next to them.
*Holdout files (round 14):* for a dataset split into dev and holdout, every file that holds a holdout household's referee value lives only under `~/cmp20/tests/quarantine/` (software grids: `quarantine/software/<grid>/`; registered copies: `quarantine/candidates/`). Folders outside it hold dev rows only (`software/<area>/<grid>/cases_dev.jsonl`, `tests/data/<base>/raw/`, `tools/strip_raw.py`). Nobody improving a model opens anything under `quarantine/`, even to filter it to dev ids.
*Released (round 15):* the final round is closed; every holdout's per-case details are in `tests/released/round15/` and the holdout parts are dev from now on (rule 7).

## 2. Fair-test rules
1. **Fix from the statute, never from the referee.** Every model change cites the provision (and dated text) that
   requires it. A referee disagreement is a *pointer*, not a reason. Changes that only make a number match are not
   allowed.
2. **Statute mode and convention mode are scored separately.** Where a referee follows a convention that differs from
   the statute (rounding, annualisation, an average municipal rate, an assumed pension), the model may reproduce it
   only behind an explicit flag (e.g. `--oecd`), and both scores are reported. The headline score is statute mode.
3. **Frozen evaluation.** Each evaluation round runs frozen copies of all 38 exes (`harness/freeze.py`), records each
   binary's sha256 and the model sources' hash, and is appended to `~/cmp20/tests/LEDGER.jsonl` (one line per
   country × dataset × mode: round, date, hashes, cases, exact, within 1 %, max abs diff, metric definition id).
4. **Metrics fixed in advance** (`tests/METRICS.md`): exact = |diff| ≤ 1 currency unit per line (or ≤ 0.01 pp for
   rates); within 1 %; per-line and per-household; plus coverage = share of the dataset's cases the model can
   represent (unsupported cases are counted, not dropped).
5. **No silent exclusions.** A case left out must be listed with the reason (feature not modelled, referee error with
   evidence, out of scope); referee errors need the statute that shows it.
6. **Report regressions.** Every round compares with the previous one per country and dataset; a fix that improves one
   dataset and worsens another is reported as such.
7. **Holdout discipline.** Holdout sets are scored only at the end of a round (baseline round 0, then after
   improvements). Their per-case details are released into `dev` only after the round is closed, and are then no
   longer holdout.
8. **Per-dataset conventions need the referee's published methodology.** A convention flag that applies to one dataset only, or a
   dataset excluded from a model's convention flags, is allowed only when its reason cites the referee's published methodology
   (document and section). A reason inferred from the referee's own figures, or the flag's effect on a score, is not enough. The test
   agent audits each one (`tests/convention_policy.json`) and removes the others at freeze time. (Added 2026-11-19 after round 4;
   tightened before round 5: inferred reasons no longer qualify.)
   *Note (round 10):* Eurostat's own methodology note (ESMS earn_net 10.6) says its net earnings follow the OECD's Taxing Wages
   methodology, so Eurostat convention mode uses every model's Taxing Wages convention set, plus the start-of-fiscal-year flags
   ESMS 3.4 documents, for all countries alike (`tests/convention_policy.json`, `eurostat_convention_mode`).
   *Note (round 14):* one EUROMOD policy for every `*_open_euromod_grid` (dev and holdout ids alike, every country): legislative parameters are those of 30 June of the policy year (EUROMOD 'Nowcasting prices' note, Feb 2025, sections 1.3-1.4), except where the country's EUROMOD country report states how a specific policy is treated (a schedule stated for the whole year, a full-year adjustment on in the baseline), when that section governs. It applies to every country with a mid-year change whatever the effect on the score; a group may not decline it, or a 30-June flag, because of failures. A parameters-workbook row is a value, not a methodology: a convention needs a country-report or technical-note section (`tests/convention_policy.json`, `euromod_convention_mode`).
   *Note (round 15):* on the EUROMOD grids only flags supported by EUROMOD's own documents apply: convention mode there is the grid's declared per-dataset flags, never the model's default set, and never `--oecd` (its basis, ESMS 10.6, is Eurostat's). A country without a declared EUROMOD flag is scored there with no flags.

## 3. Rounds
- **Round 0 (baseline):** register datasets, freeze, score everything (dev + holdout), record.
- **Round 1..n (improve):** family agents work from dev failures and coverage gaps, fix models from the statute,
  add country-specific datasets (registered with a role before use), rebuild; then a frozen re-score of everything.
- Each round closes with a short entry in `~/cmp20/tests/ROUNDS.md` (what changed, scores before/after per dataset,
  regressions, open problems) and in `~/cmp20/JOURNAL.md`. The research page renders `tests/ROUNDS.md`,
  `tests/REGISTRY.md` and a score table from `tests/LEDGER.jsonl`.
- **Number of rounds (Alan, 2026-11-19):** improvement rounds continue up to round 10 as long as rounds keep producing meaningful,
  fairly-tested gains (round 8 is no longer a hard stop). After the last round: a final evaluation (every holdout set scored once
  more on the last frozen exes; a round 0 -> final summary per dataset; all regressions; what still cannot be tested).
- **Phase 2: open-source software benchmarks (rounds 11+; Alan, 2026-11-19).** After round 10 (closed normally,
  with its checks) a few more rounds benchmark the models against open-source tax/benefit software for each
  jurisdiction (as the US blog did with Tax-Calculator and PolicyEngine-US). A software-benchmarks agent inventories,
  installs and runs the software on seeded grids and hands each dataset to the test-infrastructure agent, who alone
  registers (role, 70/30 seeded split for grids, sha256, software version/commit, case building), freezes and
  Phase 2 freeze rule (coordinator): a round freezes when every group given work that round signals READY; a group
  given no work makes no change.
  scores. The final evaluation (every dataset and every holdout once, round 0 -> final, regressions, what cannot be
  tested) moves to the end of Phase 2; holdout per-case details stay sealed until then.

## 4. Datasets to get (as many as possible)
OECD: Taxing Wages country tables 2022-2025 (all 37 OECD members we model: every year and household type), the
decomposition and marginal/average rate tables, the OECD Tax Database (statutory PIT rates and thresholds, social
security contribution rates and ceilings, top rates), and TaxBEN / tax-benefit outputs (net incomes, METR, PTR) where
openly downloadable. Country-specific: official calculators (polite, sequential, no login/bot-protection bypass),
published withholding tables and formulas, worked examples in official guidance, open-source official code, and open
models (PolicyEngine, OpenFisca, GETTSIM, EUROMOD outputs where open).
Split: hold out whole datasets (or a pre-registered random 30 % of cases of a large grid, seed recorded), not
individual awkward cases.

## 5. How it is reported
The research page's section is titled **"Testing and iterating upon the model"** and is written honestly about the
process: what was tested against what; which referees were already used during modelling (and so are not independent)
and which are true holdout; raw counts as well as percentages; every failure cluster; what was changed between rounds
and why (with the statute); what got worse; and what still cannot be tested. No overselling.
- **Phase 2 datasets:** open-source tax/benefit software per jurisdiction (rounds 11+), registered with its version or
  commit, install log and grid seed; software the modellers used as a comparator is marked not independent.

## 5. Order we tested in (record; Alan's hypothesis below)
1. Statute build (each model from its statute; round-0 freeze 2026-11-19 12:29 UTC).
2. OECD Taxing Wages (dev; the modellers' own target), then its holdout siblings (marginal rates, the decomposition), the Tax Database and TaxBEN (round 0).
3. Other official datasets and country tables (Eurostat, official calculators, withholding tables; rounds 1-9).
4. Open-model grids for five countries (PolicyEngine-US/UK/Canada, GETTSIM, OpenFisca-France; rounds 2-3).
5. Open-source software for every jurisdiction (Phase 2, rounds 11+).
**Hypothesis (Alan, not tested):** running the software benchmarks first would probably have scored better on the datasets sooner. Evidence from the record, mixed: the open-model grids, within two rounds of registration, surfaced 8 case-building errors of our own (round 3: US additional Medicare, UK HICBC, DE Abgeltungsteuer, CA tax year and cohabiting, FR case T, birthdays and N-2 income, couples' investment income) and one statute line-definition fix (DE-4, round 4: GETTSIM grid dev 4,066 -> 5,068 exact) that changed no OECD line; the largest statute fix with a holdout effect (CA ITA s.122.6, round 7: holdout decomposition 3,291 -> 3,547 exact) came from an OECD dev gap (CA F14) open since round 0. Statute-mode holdout scores did not rise over rounds 0-9 (decomposition 103,489 -> 102,735 exact, from deliberate statute fixes); the gains were earlier years (dev), convention modes and country tables.

## 6. World expansion: how the 159 new countries are tested (2026-11-20; CONTRACTWORLD.md)

Everything in §§1-5 applies unchanged (registration before use, dev/holdout, statute vs convention mode, frozen rounds,
fixes from the statute only, rule 8, no holdout peeking, quarantine). Only the order and the bookkeeping are new.

1. **Build** (done per batch): every model from the statute only; no referee value was looked at while modelling. The
   official tables a grade-B model was built from are recorded in its summary.json and are **not independent** when
   they come back as datasets.
2. **Open-source software first** (rounds W1, W2, ...): for each country with a candidate (`world/SOFTWARE.md`,
   `world/STATUS.md`), the software is installed and probed on three or four households; if it is right on its face, a
   seeded grid is built with `~/cmp20/software/grids.py` (`rich_grid`, plus `apply_world_inputs` for the optional
   inputs a world model declares in `world/data/inputs.json`), in local currency, 70/30 split by case id with seed =
   int(sha256("<cc>_<name>")[:8], 16). Dev rows go to `world/software/<grid>/cases_dev.jsonl`; holdout cases and every
   referee row of a holdout household only to `~/cmp20/tests/quarantine/software/<grid>/` (round-14 layout). Hand-off:
   `world/software/HANDOFF.md` (format of `software/HANDOFF.md`).
3. **Register, freeze, score**: the test-infrastructure role registers each grid in `tests/REGISTRY.md` (`registry.json`)
   with role, sha256, software version/commit and seed; freezes the world exes (`harness/freeze.py`, the world exes are
   found through `common20.WORLD`) into `tests/frozen/W<n>/`; scores once per round into `tests/LEDGER.jsonl` with the
   round named `W<n>` (M1 and M2 metrics, statute mode as headline). Batch agents then fix from the statute (rule 1)
   from dev failures only; the next round re-freezes and re-scores.
4. **Datasets only after that** (rounds D1, D2, ...): OECD Taxing Wages 2022-2025, the Tax Database and TaxBEN for CL CO
   CR IL TR (raw already in `tests/quarantine/world/datasets_raw/`), then official withholding tables, calculators and
   worked examples per country (`world/DATASETS.md`), each registered with a role before anyone reads it; same freeze
   and score cycle.
5. **Record for Alan's hypothesis**: per country, which software and datasets were used in which round, and the dataset
   scores (exact / within 1 %) at the first dataset round, so countries tested against software first can be compared
   with those that went straight to datasets (118 countries have no open software).
6. **Scale**: harness amounts in "AW" for a world country use its statutory reference wage (`world/data/refwage.json`,
   `scale.json`), never a referee's average wage; grids for scoring are in local currency.
