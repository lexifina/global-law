# Mapping: panel decisions reheard en banc (Beim, Hirsch & Kastellec) → expected model status of the panel decision

Written 2026-11-14 (round 11, dataset agent `bench11`) after reading the deposit's codebook (`raw/bhk_zip_x/Codebook.docx`,
text in `work/codebook.txt`), its readme, the marginal counts of `source_of_cases` × `eb_grant` × `eb_reverse`, the
corpus court list (`graph/courts.tsv`) and the format of `graph/cite_index.tsv`, and `benchmarks/fedcir_dataset/MAPPING.md`
(whose model classes and conventions this follows), and **before** any source row was joined to any corpus row or any
model row. No model output (`round*/out/`, `status.tsv`, `history.tsv`, `certs.tsv`, `treatments.tsv`) is read by the
parser or the linker; `score.py` was run only on a synthetic build. Changes after the first scoring, if any, are appended
at the end with both results.

## Unit

- Source item: one row of `bhk_main_data.csv` whose `source_of_cases` is `bhk_ebs` (coded by Beim, Hirsch & Kastellec)
  or `clark_ebs` (merged from Clark 2009, "A Principal Agent Theory of En Banc Review"), identified by `unique_id_new`
  (`bhk:<unique_id_new>`). Every such row has `eb_grant` = 1: the published three-judge panel decision `p_cite`
  (decided `p_year`-`p_month`-`p_day`, circuit `circuit`, 1986–2002) "was reheard en banc"; `eb_cite` is the en banc
  decision.
- Not items: the 4,818 rows from `songer_1986-1996` / `songer_1997-2002` (the Songer / Kuersten–Haire random sample, the
  population of the `songer_treat` and Shepardized keys). The en banc rows all have an empty `casenum_songer_original`,
  i.e. the source does not place any of them in the Songer sample.
- Scored unit: one **panel decision in our corpus** (node) linked from one or more items. The expected status is that
  node's decision-level status. The en banc decision itself is not scored (it is used only to confirm the link and to
  check who the model names as the actor).

## Source side: class

Every item is source-negative: a panel decision that the full court reheard en banc has been displaced by the en banc
court's decision (vacated on the grant of rehearing en banc under most circuits' rules, and in every circuit superseded by
the en banc judgment). Expected model output at decision level: **`NEG_HIST`** (negative same-case history: vacated /
superseded / reversed on rehearing en banc). `UNK_HIST` counts only in the lenient recall.

Sub-classes (reported, all expected `NEG_HIST`; a unit takes `R` if any of its items is `R`, else `S` if any is `S`):

| Sub-class | Source | Meaning |
|---|---|---|
| `R` | `eb_reverse` = 1 | the en banc decision's direction (liberal/conservative, Songer rules) is opposite to the panel's: the en banc court changed the result |
| `S` | `eb_reverse` = 0 | same direction: the en banc court reached the panel's result on its own reasoning (panel opinion still vacated/superseded) |
| `U` | `eb_reverse` missing | direction not coded |

There are no source-clean items, so **precision and clean are not meaningful and are not reported**.

## Model side (what is read)

As in `fedcir_dataset/MAPPING.md` (via `benchlib.load_status`): the decision-level row of `status.tsv` (`issue` = `-`,
`holding` = `-`) live at the as-of date (default 20261112; every en banc decision is dated 1986–2004, long before). Classes
`NEG_HIST`, `UNK_HIST`, `NEG_OTHER`, `UNK_OTHER`, `GOOD` (no row = `GOOD`). Node ids the key does not hold are ignored.

## Metrics (Wilson 95%, `benchlib.metric`)

Primary population: every linked unit.

- `recall` (primary): units whose model class is `NEG_HIST` / linked units.
- `recall_lenient`: `NEG_HIST` or `UNK_HIST`.
- `recall_R`, `recall_S`, `recall_U`: `recall` within each sub-class.
- `recall_confirmed`: `recall` on units whose en banc decision is also linked and cites the panel node in the corpus
  citation graph (`graph/edges.bin` + `round6/history/citeforms/edges_delta.tsv.gz`).
- `recall_by_enbanc`: of units whose en banc decision is linked, those that are `NEG_HIST` **and** have an admitted
  `history.tsv` row (`certs.tsv` ok) on the panel node whose `by` is the linked en banc node.
- `link_rate`: items linked to exactly one corpus panel decision / all items.

Splits: `h0`, `h1` from `benchlib.split_half("bhk_enbanc", "panel:<node>")` for linked units; unlinked items take
`split_half("bhk_enbanc", "bhk:<unique_id_new>")`. `all` = both. `tests` = same-case, `court` = federal, `blind` = true.

## LINKING (rules fixed before linking; corpus + source only)

Courts: the corpus courts whose name is "United States Court of Appeals for the <ordinal> Circuit" for `circuit` 1–11
(plus the corpus's misspelled variants "…Six Circuit", "…Second Circuitt", "…for the Ninth"), and "…for the District of
Columbia Circuit" / "…for the District of Columbia" for `circuit` 12 (D.C. Circuit).

1. **Panel decision.** `p_cite` is normalised to `<vol> <f2d|f3d> <page>` (spaces, dots and case removed from the reporter;
   `F.` alone, WL, LEXIS or empty → `no_reporter_cite`). Candidates = `cite_index.tsv` nodes for that cite in the circuit's
   courts with a decision date within 400 days of the source's panel date. Several → keep those dated exactly on the
   panel date, then those sharing a caption word (Brace & Hall / fedcir stop list) with the linked en banc decision; still
   several → `panel_ambiguous`. None, but the cite exists in another court → `panel_cite_other_court`; exists only outside
   the date window → `panel_cite_date_mismatch`; absent → `panel_cite_not_in_corpus`.
2. **No reporter cite.** If `p_cite` is not a reporter cite but the en banc decision is linked: candidates = nodes in the
   circuit's courts dated within 3 days of the panel date, cited by the en banc node, sharing at least one caption word
   with it. Exactly one → linked (`via` = `enbanc_citation`); otherwise `no_reporter_cite`.
3. **En banc decision.** Same as rule 1 with `eb_cite` and the `eb_year`-`eb_month`-`eb_day` date (window 400 days;
   when the en banc date is missing the window is panel date to panel date + 6 years). Failure leaves the item linkable by
   rule 1 (the en banc node is only for `recall_confirmed`, `recall_by_enbanc` and rule 2).
4. **Sanity.** If panel node = en banc node → `panel_equals_enbanc` (unlinked). If the en banc node's date is not after
   the panel node's date, the en banc link is dropped (`eb_not_after_panel`), the panel link stays.
5. Items naming the same panel node are pooled into one unit.

## Amendment 1 (2026-11-14, after the first link run, before any model row was read or any build scored)

Reading the 28 linked items whose panel and en banc captions share no word (corpus + source only): most are en banc
decisions that took up several panel cases (and cite the panel), but 7 have an en banc decision that does not cite the
panel decision, i.e. the source's `eb_cite` probably names another case (the panel cite itself still resolves to a decision
of the right circuit and date). Change: `recall_by_enbanc` is computed only on **confirmed** units (the linked en banc
decision cites the panel node), with that en banc node as the expected `by`. Panel links are unchanged.
