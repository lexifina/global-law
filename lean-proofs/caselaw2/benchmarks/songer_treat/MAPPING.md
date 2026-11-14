# Mapping: Songer / Kuersten–Haire `TREAT` → expected model status of the decision below

Written 2026-11-14 by the round-9 dataset agent `bench_songer`, after reading the Songer codebook
(`cta96_codebook.pdf`: CITE/VOL/BEGINPG, DOCNUM, METHOD, CIRCUIT, STATE, DISTRICT, ORIGIN, SOURCE, PRIORPUB, TREAT),
the Kuersten–Haire update codebook (same fields; TREAT adds code 11), `benchmarks/CONTRACT.md`,
`benchmarks/common/benchlib.py` and `benchmarks/fjc_idb_appeals/MAPPING.md` (model classes and conventions), and
**before** any source or corpus row was joined to any model row. No model output (`status.tsv`, `history.tsv`,
`certs.tsv`, any `out/` directory) has been or will be read by this agent; the self-test of `score.py` runs only on a
synthetic build. Changes after first scoring, if any, are appended at the end with both results.

## Unit

- Source item: one Songer (1925–1996) or Kuersten–Haire (1997–2002) case = one published court of appeals decision,
  with `TREAT` = what that decision did to the decision below, and `PRIORPUB` = the citation of "the most recent (if
  any) published opinion of some other court or a prior decision of the courts of appeals for this same case".
- Scored unit: one **federal district or bankruptcy court decision in our corpus** (node) that `PRIORPUB` names
  (LINKING below). The expected status is that node's decision-level status.
- The appellate decision itself is not scored here (its own later history is what the Shepardized key tested).

## Model side (what is read by score.py)

Exactly as `fjc_idb_appeals/MAPPING.md`, via `benchlib.load_status`: decision-level rows of `status.tsv` (`issue` =
`-`, `holding` = `-`) live at the as-of date; no row = `good`.

| Model class | Definition |
|---|---|
| `NEG_HIST` | `neg:*` with `path` = `history` (reversed, vacated, withdrawn, …) |
| `UNK_HIST` | `unknown:*` with `path` = `history` |
| `NEG_OTHER`, `UNK_OTHER` | negative / unknown by another path |
| `GOOD` | `good`, or no row |

TREAT records only the same-case outcome, so `NEG_OTHER`, `UNK_OTHER` and `GOOD` together form `CLEAN`.
As-of date: `benchlib.DEFAULT_ASOF` (2026-11-12). TREAT is the outcome when the appellate decision issued; a later
event in the same litigation (rehearing en banc, Supreme Court review of the appellate decision) can make the model
differ legitimately; the disagreement reading must count these. `score.py --asof` re-runs for another date.

## Source side: TREAT → class (both codebooks; code 11 only in the update)

| Class | TREAT codes | Expected model output for the decision below |
|---|---|---|
| `NEG` | 2 reversed (incl. reversed & vacated); 3 reversed and remanded (or just remanded); 4 vacated and remanded (also set aside & remanded; modified and remanded); 7 vacated | `NEG_HIST` |
| `PART` | 5 affirmed in part and reversed in part (or modified, or affirmed and modified); 6 affirmed in part, reversed/vacated in part, and remanded; 11 affirmed, vacated (no mention of reverse), and remanded | `NEG_HIST` **or** `UNK_HIST`; `CLEAN` is a disagreement |
| `CLEAN` | 1 affirmed; or affirmed and petition denied | `CLEAN` (`GOOD`, `NEG_OTHER`, `UNK_OTHER`) |
| `OTHER` | 0 stay/petition/motion granted; 8 petition denied or appeal dismissed; 9 certification to another court; 10 not ascertained; missing | not scored; model distribution reported |

Known source artefacts stated in advance: code 3 includes "just remanded" (a remand that does not disturb the
judgment cannot be separated); code 4 includes "modified and remanded"; code 5 includes "modified" and "affirmed and
modified" (scored `PART`, where `UNK_HIST` or `NEG_HIST` is accepted).

Several Songer cases linked to the same decision below (successive appeals, consolidated cases) are combined per
decision: all scored cases `NEG` → `NEG`; all `CLEAN` → `CLEAN`; any other mix of `NEG`/`PART`/`CLEAN` → `PART`;
unscored cases are ignored when a scored one exists; only unscored → `OTHER`.

## Populations (fixed in advance)

- **Primary (`cited`)**: linked decisions below that the linked appellate decision cites in the citation graph
  (`graph/edges.bin` + `round6/history/citeforms/edges_delta.tsv.gz`), as in the FJC key. The model can only read a
  same-case history event from the text of a reviewing decision that is in the corpus and cites the decision it
  reviews, so this is where the model can be expected to see the event. Uses only source + corpus, never the model.
- **Secondary (`any`)**: every linked decision below (cited or not), reported as `*_any` metrics in the same files.

## Scoring rules fixed in advance

- **Recall** (primary metric): of `NEG` decisions, share the model shows `NEG_HIST`. `recall_lenient`: `NEG_HIST` or
  `UNK_HIST`.
- **Precision**: of scored (`NEG`/`PART`/`CLEAN`) decisions the model shows `NEG_HIST`, share the source has `NEG`
  (`precision`); `precision_lenient`: `NEG` or `PART`.
- **Clean**: of `CLEAN` decisions, share the model shows `CLEAN`.
- **PART agreement** (`part`): of `PART` decisions, share the model shows `NEG_HIST` or `UNK_HIST`.
- **Link rate**: of key items (definition below), the share linked to exactly one corpus appellate decision and
  exactly one corpus district/bankruptcy decision. Failures counted by reason.
- Halves: `benchlib.split_half("songer_treat", "district:<node>")` for linked decisions (the scoring unit),
  `"songer:<casenum>"` for unlinked items. Assigned in `link.py` before any model row is read. Reported h0, h1, all.
- Wilson 95% for every metric (`benchlib.metric`).

## Key items

A Songer case is a **key item** when (a) its TREAT class is `NEG`, `PART` or `CLEAN`, and (b) `PRIORPUB` is present
(not blank, `0` or `000000000`). Cases with a scored TREAT and no `PRIORPUB` (decision below unpublished, or not
recorded) are counted in the link report (`no_priorpub`) but are not key items. `OTHER`-class cases are linked the
same way and reported, but are not key items.

## LINKING (rules written before linking; never tuned on model output)

1. **Appellate decision**: Songer citation → normalised Federal Reporter key. Songer 1925–1996: `VOL` < 3000 →
   `VOL f2d BEGINPG`; `VOL` ≥ 3000 → `(VOL−3000) f3d BEGINPG` (the file codes F.3d volumes as 3001, 3002, …; checked
   against YEAR). Update: `CITEVOL f3d BEGINPAGE`. Candidates: corpus decisions in the circuit's repo (`CIRCUIT` 0 →
   `cadc`, 1–11 → `ca1`…`ca11`) carrying that citation. Exactly one whose date equals the Songer decision date →
   linked; else exactly one in the Songer year → linked; else none → `app_not_in_corpus` (or `app_wrong_year` if the
   citation exists in the repo in another year only, `app_court_mismatch` if only in another repo); several →
   `app_ambiguous`.
2. **Decision below**: `PRIORPUB` parsed as volume, reporter, page (also the compact zero/`z`-padded form, e.g.
   `377fs242z`); reporter normalised (`FS`/`F Supp`/`FSUP`/`FSUPP` → F. Supp.; `FSUPP2D`/`F Supp 2d` → F. Supp. 2d;
   `FRD`; `BR`; `F2nd`/`F2d`; `F3d`; `F`). Unparseable → `priorpub_unparseable`. Candidates: corpus decisions (any
   repo) carrying that citation.
   - none → `below_not_in_corpus`;
   - candidates exist but none is a federal district or bankruptcy court (court table: `federal`, `trial`/`special`,
     name contains "District Court" or "Bankruptcy Court", not an appellate panel) → `below_not_district_court`
     (e.g. `PRIORPUB` is an earlier appellate panel, an agency, a state court or the Supreme Court);
   - keep district/bankruptcy candidates dated on or before the appellate decision and no more than 15 years
     earlier; none left → `below_date_mismatch`;
   - state check: when Songer `STATE` is a state/territory (01–54, 56, 57) and the candidate court name names a
     state, they must agree; none left → `below_state_mismatch`;
   - exactly one left → linked; several → if exactly one of them is cited by the linked appellate decision → linked,
     else `below_ambiguous` (never guessed).
3. The appellate link must succeed for the item to count as linked (step 1 failure reasons take precedence).

## Freshness exclusions (decided before linking)

- `benchmarks/fjc_idb_appeals/key_nodes.tsv` (either half): a linked item is excluded when its decision-below node is
  a `dist_node` there, or its appellate node is one of that file's `app_nodes` (the FJC key already holds that
  appellate → district treatment). Excluded units are dropped from `key_nodes.tsv` and counted.
- `round6/shepardized/` (case list `results/links.tsv`, read only for this): the Shepardized key's units are the
  Songer **appellate** decisions themselves (their later history: rehearing, en banc, Supreme Court), and it holds
  every Songer case. This key's units are the **decisions below**, which the Shepardized key never scored. A linked
  item is excluded when its decision-below node is a node of the Shepardized case list. The number of key appellate
  decisions that are also Shepardized units is reported (expected: all), but they are not excluded, since excluding
  them would remove every case and the question asked (what the appeal did to the decision below) differs.

## Amendment 1 (2026-11-14, after the first link run, before any scoring; no model row has been read)

The first link run (source + corpus only) linked 2,542 cases; in 136 of them the appellate and decision-below names
share no distinctive party-name token (some legitimate: co-defendants, vessel names; some plainly another case, a
coding slip in `PRIORPUB`). Added to LINKING step 2, after the single candidate is chosen: **identity check** — the
appellate decision cites the candidate in the citation graph, or the two corpus case names share at least one
distinctive token (words of 3+ letters minus a fixed stop list of generic party words: United States, State,
Commissioner, Company, Bank, Board, County, City, Railway, Insurance, …; see `link.py` `STOPW`). Otherwise the item
fails as `below_name_mismatch`. Nothing else changed.
