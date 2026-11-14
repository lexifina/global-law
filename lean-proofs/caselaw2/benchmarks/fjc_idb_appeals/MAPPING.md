# Mapping: FJC IDB appeals `OUTCOME` → expected model status of the district decision reviewed

Written 2026-11-13, after reading the two IDB appeals codebooks (1971–2007 and 2008 forward), the CCAD codebook
(§5.2, crosswalk), the marginal frequencies of `DISP` × `OUTCOME` × era of the crosswalked IDB rows, and
`round6/shepardized/MAPPING.md` (model classes), and **before** any IDB or corpus row was joined to any model row
(`status.tsv`, `history.tsv`). No agreement figure had been computed when this file was written. Changes after that
point, if any, are appended at the end with both results.

## Unit

- Source item: one IDB appeals record (one appeal docket; for criminal appeals one defendant) that CCAD's
  `idb_crosswalk` attaches to a published court of appeals opinion (`caseid`). `OUTCOME` says what the court of
  appeals did to the judgment of the district (or bankruptcy) court identified by `DDIST` + `DDOCKET`.
- Scored unit: one **district/bankruptcy decision in our corpus** (node) linked to one or more such appeals
  (rules in `LINKING` below). The expected status is that node's decision-level status.
- The appellate opinion itself is not scored here (IDB says nothing about what later happened to it).

## Model side (what is read)

Exactly as `round6/shepardized/MAPPING.md`, via `benchmarks/common/benchlib.load_status`: decision-level rows of
`status.tsv` (`issue` = `-`, `holding` = `-`) live at the as-of date; no row = `good`.

| Model class | Definition |
|---|---|
| `NEG_HIST` | `neg:*` with `path` = `history` (reversed, vacated, withdrawn, …) |
| `UNK_HIST` | `unknown:*` with `path` = `history` (partial reversal/vacatur, scope unknown, …) |
| `NEG_OTHER`, `UNK_OTHER` | negative / unknown by another path (overruled etc. by a different case) |
| `GOOD` | `good`, or no row |

IDB records only same-case outcomes, so `NEG_OTHER`, `UNK_OTHER` and `GOOD` together form `CLEAN` ("no same-case
negative shown").

As-of date: `benchlib.DEFAULT_ASOF` (2026-11-12). The IDB records each appeal's outcome when it terminated; nothing
later in the same litigation (rehearing en banc, Supreme Court review of the appellate decision) is in the record, so
a later same-case event can make the model differ from IDB legitimately; the disagreement reading counts these.
`score.py --asof` re-runs for another date.

## Source side: outcome class of each appeal record

Only appeals from a district or bankruptcy court are used: `APPTYPE` civil 3, 4, 7; criminal 5, 8, 13–22;
bankruptcy 9, 10, 12. Excluded (no district decision reviewed): 1, 2 (agency), 6 (original proceeding),
11 (from a bankruptcy appellate panel), missing.

Era: `TAPEYEAR` < 1985 uses the SY71–SY84 codes, ≥ 1985 the SY85+ codes (the codebook says the field was recoded in
SY85). In the SY85+ era, `OUTCOME` is used only when `DISP` ∈ {1, 2, 3} (termination on the merits); otherwise the
record is `OTHER` (not scored).

| Class | IDB codes | Expected model output for the district decision |
|---|---|---|
| `NEG` | `OUTCOME` 2 (SY85+: "Reversed, Vacated" — whole judgment overturned, incl. reversed and remanded; SY71–84: "Reversed - Vacated - Denied") | `NEG_HIST` |
| `PART` | `OUTCOME` 3 ("Affirmed in part and reversed/vacated in part"; SY71–84 "Affirmed and Reversed") | `NEG_HIST` **or** `UNK_HIST`; `CLEAN` is a disagreement |
| `CLEAN` | `OUTCOME` 1 ("Affirmed - Enforced", incl. affirmed and remanded) | `CLEAN` (`GOOD`, `NEG_OTHER`, `UNK_OTHER`) |
| `REMAND` | `OUTCOME` 6 ("Remanded": whole case sent back, judgment not resolved) | not scored; model distribution reported |
| `OTHER` | `OUTCOME` 4, 5 (dismissed), 7 (other / transferred), 9 (certificate of appealability denied), −8/missing, non-merits `DISP` | not scored |

Several appeal records linked to the same district decision (cross-appeals, consolidated appeals, co-defendants,
successive appeals) are combined per decision: all scored records `NEG` → `NEG`; all `CLEAN` → `CLEAN`; any other mix
of `NEG` / `PART` / `CLEAN` → `PART`. Unscored records are ignored when a scored record exists; a decision with only
unscored records takes `REMAND` if any record is `REMAND`, else `OTHER`.

## Populations (fixed in advance)

- **Primary (`cited`)**: linked decisions whose linked appellate opinion cites the district decision (graph
  `edges.bin` + round-6 `citeforms/edges_delta.tsv.gz`). Rationale: a district docket often holds several rulings,
  and a published ruling that the appellate opinion never cites may not be the judgment the appeal reviewed
  (e.g. an early motion ruling, with the appealed final judgment unpublished). This restriction uses only the
  source and the corpus, never the model.
- **Secondary (`docket`)**: every linked decision (cited or not). Reported in the same results files as extra
  metrics (`*_docket`).

## Scoring rules fixed in advance

- **Recall**: of `NEG` decisions, share the model shows `NEG_HIST`. Lenient variant (notes and `recall_lenient`):
  `NEG_HIST` or `UNK_HIST`.
- **Precision**: of scored (`NEG`/`PART`/`CLEAN`) decisions the model shows `NEG_HIST`, share IDB has `NEG`
  (strict, the `precision` metric); lenient (`precision_lenient`): `NEG` or `PART`.
- **Clean**: of `CLEAN` decisions, share the model shows `CLEAN`.
- **PART agreement** (`part`): of `PART` decisions, share the model shows `NEG_HIST` or `UNK_HIST`.
- **Link rate**: of key items (IDB appeal records in the crosswalk whose class is scored and whose type is a
  district/bankruptcy appeal), the share linked to exactly one corpus district decision (and the appellate opinion
  to exactly one corpus decision). Failures counted by reason.
- Halves: `benchlib.split_half("fjc_idb_appeals", "district:<node>")` for linked decisions (the scoring unit),
  `"idb:<idb_idx>"` for unlinked items. Assigned in `link.py` before any model row is read. Reported h0, h1, all.
- Wilson 95% for every metric (`benchlib.metric`).
- Known asymmetry stated before scoring: the model's history rows come only from the text of a published reviewing
  decision that is in the corpus and cites the decision it reviews (`data/READER.md`, round 6). The `cited`
  population is exactly where that is possible; the `docket` population includes decisions the appellate opinion
  never cites, where low recall is expected by construction.

## LINKING (rules; written before linking, never tuned on model output)

1. Appellate opinion: CCAD `citation` (main file) → our federal appellate decisions with the same normalised
   citation in the circuit's repo (`ca1`…`ca11`, `cadc`; CCAD circuit 0 = D.C.). Exactly one with the CCAD decision
   date → linked; else exactly one in the CCAD year → linked; none → `app_not_in_corpus`; several → `app_ambiguous`.
2. District decision: IDB `DDIST` → our court (district court of that district; for bankruptcy appeal types also
   the bankruptcy court of that district). Candidates: decisions of that court whose own docket field parses to the
   same (2-digit year, sequence number) as `DDOCKET` (`YYNNNNN`), with a compatible case type (an explicit civil
   docket is not linked to a criminal appeal and vice versa; bankruptcy/adversary numbers only for bankruptcy
   appeal types).
3. Date window: after the district filing date `DDKTDATE` (−31 days slack) and after the termination date of any
   earlier IDB appeal from the same district docket whose notice of appeal precedes this one by more than 60 days;
   on or before the earlier of (notice of appeal `APPDATE` + 60 days) and (appellate decision date − 1 day). When
   `APPDATE` is missing, only the appellate decision date bounds it.
4. Identity check: the candidate shares at least one distinctive party-name token with the linked appellate
   decision's name, or with the IDB appellant/appellee names.
5. Exactly one candidate left → linked (`docket`). Several left → if exactly one of them is cited by the linked
   appellate opinion → linked (`docket+cite`), else `several_in_docket` (never guessed).
