# Mapping: Brace & Hall state supreme court disposition → expected model status of the decision below

Written 2026-11-14 (round 9, dataset agent `bench_bh`) after reading the Brace & Hall codebook (Revised Codebook 8-05,
its hints appendix and the project's coding rules), the marginal frequencies of the source variables, and
`benchmarks/fjc_idb_appeals/MAPPING.md` (whose model classes and style this follows), and **before** any source or
corpus row was joined to any model row. No model output (`round*/out/`, `status.tsv`, `history.tsv`, `certs.tsv`)
is read by the parser or the linker. Changes after the first scoring, if any, are appended at the end with both
results.

## Unit

- Source item: one record of the Brace & Hall case file (`NSF 95-98 Beta Version_July 2005.tab`, row number in the
  file = `bh:<row>`): one state court of last resort decision of 1995–1998 (for multi-docket opinions the record
  describes the first docket listed, coding rules). The disposition variable (`ca_disp` criminal, `cg_disp` civil
  government, `cp_disp` civil private, `jv_disp` juvenile; the one matching `genissue`, else the non-missing ones)
  is "the Supreme Court's disposition of the lower court", the lower court being `rev_ct` ("court being reviewed by
  the state supreme court").
- Scored unit: one **decision below in our corpus** (node) — the intermediate appellate decision (or trial decision)
  the court of last resort reviewed — linked from one or more source items (rules in `LINKING`). The expected status
  is that node's decision-level status. The supreme court decision itself is not scored (the source says nothing
  about what later happened to it).

## Model side (what is read)

Exactly as `round6/shepardized/MAPPING.md`, via `benchmarks/common/benchlib.load_status`: decision-level rows of
`status.tsv` (`issue` = `-`, `holding` = `-`) live at the as-of date; no row = `good`.

| Model class | Definition |
|---|---|
| `NEG_HIST` | `neg:*` with `path` = `history` (reversed, vacated, withdrawn, …) |
| `UNK_HIST` | `unknown:*` with `path` = `history` |
| `NEG_OTHER`, `UNK_OTHER` | negative / unknown by another path (overruled etc. by a different case) |
| `GOOD` | `good`, or no row |

The source records only the same-case outcome, so `NEG_OTHER`, `UNK_OTHER` and `GOOD` together form `CLEAN`
("no same-case negative shown").

As-of date: `benchlib.DEFAULT_ASOF` (2026-11-12). The source records the 1995–1998 decision only; a later
same-case event (rehearing granted, US Supreme Court review of the state decision, a later decision on remand) can
make the model differ legitimately; the disagreement reading counts these. `score.py --asof` re-runs for another
date.

## Source side: outcome class of each record

| Class | Codes of the disposition variable | Expected model output for the decision below |
|---|---|---|
| `NEG` | 2 "Reversed (or vacated)"; 3 "Reversed (or vacated) and remanded" | `NEG_HIST` |
| `PART` | 4 "Affirmed in part and reversed in part (or modified, or affirmed and modified)"; 5 "… and remanded" | `NEG_HIST` **or** `UNK_HIST`; `CLEAN` is a disagreement |
| `CLEAN` | 1 "Affirmed" | `CLEAN` (`GOOD`, `NEG_OTHER`, `UNK_OTHER`) |
| `OTHER` | 6 "Petition or motion granted", 7 "… denied", 55 "Other" (the coding rules put "affirmed and remanded" here), 88 not relevant, undefined codes (8, 9), all missing | not scored |

A record with several non-missing disposition variables (78 rows) uses the one matching `genissue`; if none
matches, all of them, combined as below.

Key items: records with class `NEG` / `PART` / `CLEAN` and `rev_ct` ∈ {1, 2, 3} (state trial court of limited or
general jurisdiction, state intermediate appellate court). `rev_ct` 4 (the supreme court itself), 5–7 (federal
courts), 55, 88 (an agency or another body not on the state court chart), 99 / missing: excluded (no state court
decision below). **Primary key population: `rev_ct` = 3** (intermediate appellate decision reviewed) — the
decisions our corpus mostly holds. Trial-court items (`rev_ct` 1, 2) are linked by the same rules and reported as a
secondary population.

Several items linked to the same decision below are combined per decision: all `NEG` → `NEG`; all `CLEAN` →
`CLEAN`; any other mix → `PART`.

## Populations (fixed in advance)

- **Primary (`cited`)**: linked decisions below that the linked supreme court decision cites (graph `edges.bin` +
  round-6 `citeforms/edges_delta.tsv.gz`; corpus citation graph, not model output). The model's history rows come
  from the text of a published reviewing decision that cites the decision it reviews (`data/READER.md`, round 6),
  so this is where a same-case negative is detectable.
- **Secondary (`caption`)**: linked decisions below found by caption + date only (not cited by the supreme court
  decision). Reported as `*_all` metrics over every linked unit (cited or not); low recall there is expected by
  construction.

## Scoring rules fixed in advance

- **Recall** (primary): of `NEG` units, share the model shows `NEG_HIST`. `recall_lenient`: `NEG_HIST` or
  `UNK_HIST`.
- **Precision**: of scored (`NEG`/`PART`/`CLEAN`) units the model shows `NEG_HIST`, share the source has `NEG`;
  `precision_lenient`: `NEG` or `PART`.
- **Clean**: of `CLEAN` units, share the model shows `CLEAN`.
- **PART agreement** (`part`): of `PART` units, share the model shows `NEG_HIST` or `UNK_HIST`.
- **Link rate** (`link_rate`): of key items with `rev_ct` = 3, the share linked to exactly one corpus supreme court
  decision and exactly one decision below (cited or caption). `link_rate_cited`: the same, cited links only.
  `link_rate_all`: the same over all key items (`rev_ct` 1–3). Failures counted by reason.
- Metrics above on the `cited` population; the same metrics with suffix `_all` over every linked unit; `_ia`
  (intermediate appellate units only, `rev_ct` = 3 items) is reported in the notes.
- Halves: `benchlib.split_half("brace_hall_state", "below:<node>")` for linked units (the scoring unit),
  `"bh:<row>"` for unlinked items. Assigned in `link.py` before any model row is read. Reported h0, h1, all.
- Wilson 95% for every metric (`benchlib.metric`).
- Known artefacts stated before scoring:
  - Review supersedes the decision below in some states (notably California in 1995–1998: a grant of review
    supersedes the Court of Appeal opinion, which then is not citable). Where the corpus still holds such an opinion,
    a model that marks it superseded/depublished shows `NEG_*` for an affirmed decision. Not corrected; counted in
    the disagreement reading, and the per-state breakdown is in the cases file.
  - "Reversed" is relative to `rev_ct`. When `rev_ct` = 3 and the intermediate court had itself reversed the trial
    court, the source class is about the intermediate decision (the unit), which is what is scored. A coder who
    coded relative to the trial court instead is a source error.
  - Multi-docket opinions: the record describes the first docket; the disposition of other dockets may differ.

## LINKING (rules; written before linking, never tuned on model output)

Corpus: `graph/nodes.tsv` (node, repo, path, court, date, citations, name). State repos: `<slug>` (the court of last
resort repo, e.g. `alabama`; `texas` and `oklahoma` hold both courts of last resort), `<slug>-appellate`
(New York: `new-york-appellate-1934-1991`, `new-york-appellate-1992-2018`), `<slug>-other-courts`.

1. **Supreme court decision.** Source citation = regional reporter (`reporter` code → A.2d, N.E.2d, N.W.2d, P.2d,
   S.E.2d, So.2d, S.W.2d; all in their 2d series in 1995–1998) + `rep_vol` + `rep_page`, normalised as in
   `fjc_idb_appeals` (`670 so2d 908`). Candidates: nodes of the state's `<slug>` repo carrying that citation, dated
   within 366 days of the source decision date (`decs_yr/mo/day`; any date if missing). Exactly one → linked
   (`cite`). Several → keep those with the exact source date, then those sharing a distinctive party token (rule 4)
   with the source title; exactly one → linked, else `ssc_ambiguous`. No citation hit → fallback: nodes of the
   `<slug>` repo with exactly the source date that share a distinctive party token with the source title; exactly
   one → linked (`date+caption`); several → `ssc_ambiguous`; none → `ssc_not_in_corpus`.
2. **Decision below candidates.** Nodes of the state's `<slug>-appellate` repo(s) when `rev_ct` = 3, of its
   `<slug>-other-courts` repo when `rev_ct` ∈ {1, 2}; dated from 5 years (1826 days) before the supreme court
   decision's corpus date to one day before it; sharing at least one distinctive party token with the source title
   (`title_p1` + `title_p2`) or the linked supreme court node's name.
3. **Choice.** Cited candidates (cited by the linked supreme court node): exactly one → linked (`cite`); several →
   the latest-dated one if its date is unique among them (`cite+latest`: the court reviews the latest lower
   decision in the case; earlier cited ones are earlier rounds), else `below_several_cited`. No cited candidate →
   uncited candidates sharing at least **two** distinctive party tokens with the source title / supreme court name:
   exactly one → linked (`caption`, secondary population); several → `below_several_uncited`; none →
   `below_not_found` (decision below unpublished, not in the corpus, or captioned differently). For `rev_ct` 1/2 the
   same reasons carry the prefix `trial_`.
4. **Distinctive party tokens**: lower-cased alphabetic tokens of length ≥ 3 after removing a fixed stop list
   (state, people, commonwealth, city, county, inc, co, company, corp, insurance, department, board, estate, in re,
   ex parte, matter, the state's own name words, …; see `link.py` `STOP`).
5. Link figures (rates, reasons) use only the source and the corpus. A link is never chosen by looking at a model
   row.

## Amendment 1 (2026-11-14, before any scoring; no model row had been read)

A read of 24 sampled linked pairs of the first link run (source titles vs corpus captions only) found false links
through generic words ("coal", "education", "commerce") and through a match on one party only (e.g. a law firm
suing two different clients; a county as party to two different cases). Rules 3–4 were tightened before any model
row was joined:

- Party **sides** are taken from the corpus caption of the linked supreme court decision (`A v. B`), whose names are
  cleaner than the coders' abbreviated titles; a caption without " v. " (In re X, Ex parte X) is a single side, with
  the source title words added. The stop list gained generic institutional words (education, transportation,
  commerce, health, workers, compensation, coal, park, cabinet, trustees, com, appeal, superior (after a second
  40-pair read found "People v. Superior Court" linked by that word alone), …; full list in `link.py`).
- **Cited** candidates must share one token with each side (two distinct tokens), or the shared surname of
  same-name parties (Smith v. Smith), or — when the caption has only one side with tokens (State v. X, In re X,
  Department v. X) — at least one token. Single-side matches where both sides have tokens are not accepted.
- **Uncited** (caption-only) candidates must share one token with each side (two distinct tokens); with a one-sided
  caption, at least two shared tokens.
- Everything else (window, levels, `cite+latest`, populations, classes, metrics) unchanged.
