# Mapping: SCDB `caseDisposition` → expected model status of the decision below

Written 2026-11-13 after reading the SCDB codebook pages (`raw/pages/cb_*.html`) and the marginal counts of
`caseDisposition` × `caseDispositionUnusual` in `work/scdb.tsv`, and **before** any SCDB row was joined to any model
row (no `status.tsv`, `history.tsv` or `certs.tsv` of any build had been opened by this benchmark when this was written).
Changes after the first scoring, if any, are appended at the end with both results.

## Unit

- One SCDB case-centred row (Citation file: one row per dispute; modern release 2026_01, 1946–2025 terms, and legacy
  release 07, 1791–1945), identified by `caseId`.
- The tested decision is the **decision below**: the one decision of our corpus that the Supreme Court reviewed in that
  case, found by `link.py` (U.S. Reports cite → our Supreme Court opinion → lower-court citation in that opinion's own
  head matter / opening, confirmed by SCDB `caseSource` (+ `caseSourceState`) and by date). Unlinked rows are reported
  in the link rate and are never scored.
- Split half: `benchlib.split_half("scdb_disposition", caseId)`, fixed in `link.py` for every row, linked or not.

## Model side (what is read)

As in `round6/shepardized/MAPPING.md` (via `benchlib.load_status`): the decision-level row of `status.tsv` live at the
as-of date (default 20261112). Classes `NEG_HIST`, `UNK_HIST`, `NEG_OTHER`, `UNK_OTHER`, `GOOD`.
`NEG_OTHER`, `UNK_OTHER` and `GOOD` together are `CLEAN` ("no same-case negative shown"): SCDB's disposition is the
Supreme Court's action on that same case, not overruling by a later different case.

As-of date: the Supreme Court decision is always years before the model's last date, so the primary as-of is the
default 20261112 (the model's final status). `--asof` re-runs at another date.

## SCDB side: class of each case (from `caseDisposition`; `lcDisposition` is NOT used for the class)

| SCDB `caseDisposition` | codebook label | Class | Expected model output for the decision below | Expected kind (secondary) |
|---|---|---|---|---|
| 3 | reversed | `NEG` (`reversed`) | `NEG_HIST` | `neg:reversed` |
| 4 | reversed and remanded | `NEG` (`reversed`) | `NEG_HIST` | `neg:reversed` |
| 5 | vacated and remanded | `NEG` (`vacated`) | `NEG_HIST` | `neg:vacated` |
| 8 | vacated | `NEG` (`vacated`) | `NEG_HIST` | `neg:vacated` |
| 6 | affirmed and reversed (or vacated) in part | `PART` | `NEG_HIST` or `UNK_HIST`; `CLEAN` is a disagreement | any |
| 7 | affirmed and reversed (or vacated) in part and remanded | `PART` | `NEG_HIST` or `UNK_HIST` | any |
| 2 | affirmed (includes modified) | `CLEAN` (`affirmed`) | `CLEAN` | – |
| 9 | petition denied or appeal dismissed | `CLEAN` (`dismissed`) | `CLEAN` | – |
| 1 | stay, petition, or motion granted | `NS` not scored | – | – |
| 10 | certification to or from a lower court | `NS` not scored (a certificate answers questions; nothing below is affirmed or reversed) | – | – |
| 11 | no disposition | `NS` not scored | – | – |
| blank | (original jurisdiction etc.) | `NS` not scored | – | – |
| any, with `caseDispositionUnusual` = 1 | the Court's language does not fit the code | `NS` not scored (`unusual`) | – | – |

Notes fixed in advance:
- Code 2 "affirmed (includes modified)": a modified decision below stands as modified, so `CLEAN`; a `NEG_HIST`
  there is counted as a disagreement (the disagreement reading says how many were modifications).
- Code 5/8 includes vacatur for mootness (Munsingwear) and GVRs; the decision below is vacated, so `NEG_HIST`.
- Code 9 in the legacy file includes writs of error dismissed; the decision below stands, so `CLEAN`.
- The class is the Supreme Court's disposition of the **whole** case-centred dispute. With consolidated dockets the
  dispositions can differ per docket (codebook); the linker only links when exactly one decision below is found.

## Metrics (fixed in advance)

- **recall**: of linked `NEG` cases, the share the model shows `NEG_HIST` (primary). Also reported (in `notes` / the
  cases TSV): lenient recall counting `UNK_HIST`; kind agreement (`neg:reversed` for 3/4, `neg:vacated` for 5/8) and
  actor agreement (the model's `actor` is our Supreme Court opinion node) among the `NEG_HIST` hits.
- **precision**: of linked cases in a scored class (`NEG`, `PART`, `CLEAN`) where the model shows `NEG_HIST`, the
  share whose SCDB class is `NEG` (strict). Lenient (`NEG` or `PART`) in `notes`.
- **clean**: of linked `CLEAN` cases, the share the model shows `CLEAN`.
- **part** (extra metric): of linked `PART` cases, the share the model shows `NEG_HIST` or `UNK_HIST`.
- **link_rate**: of SCDB rows in a scored class (`NEG`, `PART`, `CLEAN`) whose `caseSource` is a court (not blank),
  the share linked to exactly one decision below in our corpus.
- Wilson 95% intervals via `benchlib.metric`. Results for h0, h1 and all; and the same split by the court of the
  decision below: `scdb_disposition_federal` (federal courts) and `scdb_disposition_state` (state and territorial
  courts, incl. District of Columbia local courts).

A known asymmetry, stated before scoring: the model's history rows come only from the reviewing decision's own text
(and, in round 6, from the `rules/below_sc` / `rules/memo` linkers that read the same "Reported below" / procedural
lines this benchmark's linker reads). So where both link the same pair, a hit tests the model's reading of the
Supreme Court's disposition, not an independent identification of the decision below.

## Changes after first scoring

None yet.
