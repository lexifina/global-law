# MAPPING — `fjc_idb_unpub` (FJC IDB appeals decided without a published opinion)

Written 2026-11-14 by the round-12 dataset agent `bench12`, after reading the FJC Appeals Codebook (FY2008 forward),
`benchmarks/fjc_idb_appeals/MAPPING.md` + `SOURCE.md` (whose model classes, outcome coding and linking rules this
follows) and `benchmarks/common/benchlib.py`, and **before** any source row was joined to any corpus row and before
any model row was read. No `status.tsv`, `history.tsv`, `certs.tsv` or `treatments.tsv` of any build has been opened
by this benchmark. Changes after the first link run, if any, are appended at the end with the reason; changes after
the first scoring are appended with both results.

## Unit

- Source item: one FJC IDB appeals record (SY1971–FY2007 file and FY2008–June 2026 file; one appeal docket, for
  criminal appeals one defendant) that is **not** in the fresh-key population of any earlier benchmark:
  1. not attached by the CCAD `idb_crosswalk` to any published opinion — neither its row number (`idb_idx`, primary
     or alt row) nor its natural key (file, CIRCUIT, DOCKET, DKTDATE, REOPEN, TAPEYEAR) appears in the crosswalk
     (`fjc_idb_appeals` keyed exactly the crosswalked records);
  2. `PUBSTAT` not "published" (2, 4, 6) — the appeal was disposed of by an unpublished written opinion/order, an oral
     disposition, or `PUBSTAT` is missing. (Published-but-not-crosswalked records are dropped: their opinions are the
     population of the Songer / Shepardized / BHK keys.)
- Scored unit: one **district / bankruptcy decision in our corpus** (node) linked to one or more such records.
- Node exclusion (disjointness by construction, computed from source + corpus only): a district node is excluded if
  any of its docket keys (district, 2-digit year, sequence number) equals the (DDIST, DDOCKET) of **any** crosswalked
  or published-PUBSTAT IDB record — so no node that `fjc_idb_appeals` (or a published-opinion key) could have linked
  is scored here.

## Model side (what is read)

Exactly as `fjc_idb_appeals/MAPPING.md`, via `benchlib.load_status`: decision-level rows of `status.tsv` (`issue` =
`-`, `holding` = `-`) live at the as-of date; no row = `good`.

| Model class | Definition |
|---|---|
| `NEG_HIST` | `neg:*` with `path` = `history` (reversed, vacated, withdrawn, …) |
| `UNK_HIST` | `unknown:*` with `path` = `history` |
| `NEG_OTHER`, `UNK_OTHER` | negative / unknown by another path (overruled etc. by a different case) |
| `GOOD` | `good`, or no row |

IDB records only same-case outcomes, so `NEG_OTHER`, `UNK_OTHER` and `GOOD` together form `CLEAN`.
As-of date: `benchlib.DEFAULT_ASOF` (2026-11-12); `score.py --asof` re-runs at another date. A later same-case event
(rehearing, Supreme Court review) is not in the IDB record and can make the model differ legitimately.
Node ids the scorer does not know (absent from the key, e.g. staged Supreme Court order nodes above the corpus node
count) are ignored.

## Source side: outcome class of each record (identical to `fjc_idb_appeals`)

Only appeals from a district or bankruptcy court: `APPTYPE` civil 3, 4, 7; criminal 5, 8, 13–22; bankruptcy 9, 10, 12.
Others excluded. `TAPEYEAR` < 1985 uses the SY71–84 codes, ≥ 1985 the SY85+ codes; in SY85+ `OUTCOME` is used only
when `DISP` ∈ {1, 2, 3} (merits), else `OTHER`.

| Class | IDB codes | Expected model output for the district decision |
|---|---|---|
| `NEG` | `OUTCOME` 2 (reversed / vacated in whole) | `NEG_HIST` |
| `PART` | `OUTCOME` 3 (affirmed in part, reversed/vacated in part) | `NEG_HIST` or `UNK_HIST`; `CLEAN` is a disagreement |
| `CLEAN` | `OUTCOME` 1 (affirmed / enforced, incl. affirmed and remanded) | `CLEAN` (`GOOD`, `NEG_OTHER`, `UNK_OTHER`) |
| `REMAND`, `OTHER` | `OUTCOME` 6; 4, 5, 7, 9, missing, non-merits `DISP` | not scored |

Several records linked to one node combine as in `fjc_idb_appeals`: all `NEG` → `NEG`; all `CLEAN` → `CLEAN`; any other
mix of scored classes → `PART`.

## Populations (fixed in advance)

- **Primary (`reviewed`)**: linked nodes for which the reviewing appellate decision is in the corpus and cites the
  district decision: a corpus decision of the circuit's repo (`ca1`…`ca11`, `cadc`) whose own docket field parses to
  the IDB appeal docket (`DOCKET`: 2-digit year + sequence number) and whose date is within ±14 days of `JUDGDATE`
  (closest date wins; a tie → not found), and whose citations (graph `edges.bin` + round-6
  `citeforms/edges_delta.tsv.gz`) include the district node. This is where a same-case history row is possible from
  the corpus text; it uses only source + corpus, never the model.
- **Secondary (`all`)**: every linked node (`*_all` metrics). Known asymmetry stated before scoring: where the
  unpublished disposition is not in the corpus (oral, judgment orders, unreported), low recall is expected by
  construction.

## Metrics (Wilson 95%, `benchlib.metric`)

- **recall** (primary): of `NEG` units, share the model shows `NEG_HIST`; `recall_lenient`: `NEG_HIST` or `UNK_HIST`.
- **precision**: of scored (`NEG`/`PART`/`CLEAN`) units the model shows `NEG_HIST`, share the source has `NEG`
  (strict); `precision_lenient`: `NEG` or `PART`.
- **clean**: of `CLEAN` units, share the model shows `CLEAN`.
- **part**: of `PART` units, share the model shows `NEG_HIST` or `UNK_HIST`.
- **link_rate**: of key items (records in the Unit above with a district/bankruptcy appeal type and class
  NEG/PART/CLEAN), share linked to exactly one corpus district decision. Failures counted by reason (including
  `excluded_docket`: node removed by the node exclusion).
- Halves: `benchlib.split_half("fjc_idb_unpub", "district:<node>")` for linked units, `"idb:<idb_idx>"` for unlinked
  items; assigned in `link.py` before any model row is read. Reported h0, h1, all.

## LINKING (rules; written before linking, corpus + source only, never tuned on model output)

1. District court: IDB `DDIST` → our district court(s) of that district (`fjc_idb_appeals/build_corpus.py` court map,
   copied); for bankruptcy appeal types also the bankruptcy court of that district.
2. Docket: candidates are decisions of that court whose own docket field (round-6 cache meta) parses to the same
   (2-digit year, sequence number) as `DDOCKET` (`YYNNNNN`), with a compatible type (explicit civil not linked to a
   criminal appeal and vice versa; bankruptcy/adversary numbers only for bankruptcy appeal types). None →
   `no_decision_with_docket`; type → `docket_type_mismatch`.
3. Date window: on or after `DDKTDATE` − 31 days and after the `JUDGDATE` of any earlier IDB appeal from the same
   district docket whose `APPDATE` precedes this one by more than 60 days; on or before the earlier of `APPDATE` + 60
   days and `JUDGDATE` − 1 day (whichever exist; a record with neither `APPDATE` nor `JUDGDATE` → `no_dates`).
   → `outside_date_window`.
4. Identity: the candidate's name/parties share at least one distinctive name token with the IDB appellant/appellee
   names (`fjc_idb_appeals/link.py` `name_tokens` / `upper_tokens`, copied). → `name_mismatch` / `name_unverifiable`.
5. Exactly one candidate → linked (`docket`). Several → if exactly one is cited by the reviewing appellate decision
   found as in Populations → linked (`docket+cite`), else `several_in_docket` (never guessed).
6. Node exclusion (Unit) applied to the linked node → `excluded_docket`.
