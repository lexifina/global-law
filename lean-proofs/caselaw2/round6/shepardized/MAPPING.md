# Mapping: Shepardized Courts of Appeals Database → expected model status

Written 2026-11-13, after reading the codebook and the marginal frequencies of each Shepardized variable and of
`out/status.tsv`, and **before** any Shepardized row was joined to any model row. No agreement figure had been
computed when this file was written. Changes after that point, if any, are listed at the end with both results.

## Unit and date

- Unit: one Songer case = one published court of appeals decision, identified by `citation` (e.g. `0842 f 2d 0556`).
  The outcome variables describe what happened to **that decision** afterwards.
- "As of" date. The codebook gives no Shepardizing date. It quotes an email of 11 September 2008 about Shepard's
  categories, and the data file's internal time stamp is 19 November 2010 (the web page says "Last Update: November 19,
  2010"). The primary as-of date is **2010-11-19** (the latest date the coding can reflect). `compare.py --asof` re-runs
  it for another date; 2008-09-11 is reported as a sensitivity check.
- The Shepardized file has **no event dates**. The only date-like information is the U.S. Reports citation of the
  Supreme Court decision (`us1`, `us2`). The "date check" is therefore: where the model is negative and names an actor,
  and the Shepardized row names a Supreme Court decision, is the model's actor that decision (same node, hence same date)?

## Model side (what is read)

From `out/status.tsv`, the decision-level rows only (`issue` = `-`, `holding` = `-`), the row whose interval
`from ≤ asof ≤ to`. A decision with no row is `good` (the file holds only decisions with an admitted event or holding).

| Model class | Definition |
|---|---|
| `NEG_HIST` | status `neg:*` and `path` = `history` (same-case reason: reversed, vacated, withdrawn, reviewPending, depublished) |
| `UNK_HIST` | status `unknown:*` and `path` = `history` (partial reversal/vacatur; en banc rule unknown) |
| `NEG_OTHER` | status `neg:*` with `path` = `treatment`, `prospective` or `supersession` (overruled etc. by a different case) |
| `UNK_OTHER` | status `unknown:*` with a non-history path |
| `GOOD` | `good`, or no row |

Shepard's same-case history says nothing about overruling by a later, different case. So for this comparison
`NEG_OTHER` and `UNK_OTHER` count as **"no same-case negative shown"**, the same as `GOOD` (collapsed class `CLEAN`).
The status file shows only the most severe live effect, so a same-case event can be hidden behind an overruling; as a
secondary check `compare.py` also reads `data/history.tsv` + `out/certs.tsv` and reports how many `NEG_OTHER`/`UNK_OTHER`
decisions also have an admitted (`ok`) reversed/vacated/withdrawn history row dated on or before the as-of date. That
check does not change the primary table.

## Shepardized side: outcome class of each case

Variables used: `appeal`, `coarehear`, `coaenbanc`, `scappeal`, `scresult`. `appaftre1`–`5` (history after remand)
describe later proceedings about the trial court's new judgment, not the sampled decision; they do not change the
expected status and are ignored. `screhear`, `subhist` are not used.

Each case gets every flag that applies; its class is the first in this order: `NEG`, `PART`, `AMBIG`, `MOD`, `CLEAN`.

| Class | Shepardized codes | Expected model output (decision level) | Expected kind |
|---|---|---|---|
| `NEG` (sub: `sc_reversed`) | `scresult` 2 (reversed), 3 (reversed and remanded) | `NEG_HIST` | `neg:reversed` |
| `NEG` (sub: `sc_vacated`) | `scresult` 4 (vacated and remanded — includes "vacated and remanded for reconsideration in light of …"), 7 (vacated) | `NEG_HIST` | `neg:vacated` |
| `NEG` (sub: `panel_withdrawn`) | `coarehear` 6 (decision withdrawn or vacated), 3 (rehearing granted, different result) | `NEG_HIST` | `neg:withdrawn` or `neg:vacated` (or `neg:reversed`) |
| `NEG` (sub: `enbanc_different`) | `coaenbanc` 3 (rehearing en banc granted, different result) | `NEG_HIST` | `neg:vacated`, `neg:withdrawn` or `neg:reversed` |
| `PART` | `scresult` 5 (affirmed in part and reversed in part, or modified), 6 (same + remanded) | `NEG_HIST` **or** `UNK_HIST` (partly negative). `CLEAN` is a disagreement. | any |
| `AMBIG` | `coaenbanc` 2 (granted, same result), 4 (granted, result unknown), 5 (granted, appeal dismissed); `coarehear` 2 (granted, same result), 7 (granted, result unknown); `scappeal` 3 or 5 (granted) with `scresult` 99 or blank; `scresult` 0 or 9; `scappeal` 6 (other) | not scored: whether the original opinion survives depends on a circuit rule or on facts the code does not record. Reported in the table, excluded from agreement. | – |
| `MOD` | `coarehear` 4 or 5 (decision modified) | `CLEAN` or `UNK_HIST` (the decision stands as modified). `NEG_HIST` is a disagreement. | – |
| `CLEAN` (sub: `none`) | `appeal` = 0 | `CLEAN` | – |
| `CLEAN` (sub: `related_only`) | `appeal` without the digit 1 (2, 3, 4, 5, 23, 34: same case / connected case / later proceeding only; no outcome variable is coded for these) | `CLEAN` | – |
| `CLEAN` (sub: `sc_affirmed`) | `scresult` 1 (affirmed) | `CLEAN` | – |
| `CLEAN` (sub: `cert_denied`) | `scappeal` 1, 2, 12, 4 (cert denied/dismissed, appeal dismissed) or `scresult` 8, and nothing above | `CLEAN` | – |
| `CLEAN` (sub: `rehearing_denied`) | `coarehear` 1 or `coaenbanc` 1 and nothing above | `CLEAN` | – |
| `CLEAN` (sub: `other_history`) | `appeal` has the digit 1 and nothing above applies (e.g. only history after remand) | `CLEAN` | – |

Rows with `appeal` containing 1 but blank outcome variables: class `AMBIG` (uncoded).

## Scoring rules fixed in advance

- **Agreement** (scored classes `NEG`, `PART`, `MOD`, `CLEAN`): the model output is one of the expected outputs above.
- **(a) Recall on negative history:** of `NEG` cases, the share the model shows `NEG_HIST`. Reported also with
  `UNK_HIST` counted (lenient) and by sub-class.
- **(b) Precision:** of linked cases the model shows `NEG_HIST`, the share Shepardized has `NEG` (strict) and
  `NEG` or `PART` (lenient). `AMBIG` cases are left out of the denominator and counted separately.
- **(c) Clean agreement:** of `CLEAN` cases, the share the model shows `CLEAN` (`GOOD`, `NEG_OTHER` or `UNK_OTHER`).
- Intervals: Wilson 95%.
- A known asymmetry, stated before scoring: the model's history rows come only from the text of a **published
  reviewing decision that is in the corpus and cites the decision it reviews**. Supreme Court memorandum orders with
  no "reported below" citation, and unpublished orders withdrawing or vacating an opinion, are known blind spots
  (`data/READER.md`). Low recall would not be a surprise; the disagreement reading says how much of it they explain.

## Changes after first scoring

None. The mapping above is what `compare.py` scored, and it was not changed after the first run.

One correction was made to `compare.py` after the first run, outside the mapping: the actor check compared node ids
through the one-node-per-citation index and reported 12 of 13; several decisions share a U.S. Reports page, and
compared by the actor's own citation the figure is 13 of 13. No class or agreement figure moved.

Reading the disagreements showed two places where the mapping is imperfect; they are left as written and reported in
`SHEPARDIZED.md` rather than tuned:

- `scresult` 5/6 includes "modified". In 3 of the 26 `PART` cases read, the modification left the appeals decision
  with its full force.
- `coarehear` 3 ("rehearing granted, different result") was taken as negative. In 1 of the 40 `NEG` cases read the
  court adhered to its view and only amended the decree.
