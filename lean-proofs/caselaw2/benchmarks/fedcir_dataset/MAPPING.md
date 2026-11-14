# Mapping: Federal Circuit disposition (Federal Circuit Dataset Project) → expected model status of the decision below

Written 2026-11-14 (round 10, dataset agent `bench10`) after reading the project's codebook (2023-01-06 docx; text in
`work/codebook.txt`), the marginal frequencies of the source variables (`explore.py`, `parse_source.py`), the corpus
node list (`graph/nodes.tsv`, `graph/courts.tsv`) and `benchmarks/brace_hall_state/MAPPING.md` (whose model classes,
populations and link rules this follows), and **before** any source or corpus row was joined to any model row. No
model output (`round*/out/`, `status.tsv`, `history.tsv`, `certs.tsv`, `treatments.tsv`) is read by the parser or the
linker. Changes after the first scoring, if any, are appended at the end with both results.

## Unit

- Source item: one document of the Federal Circuit Dataset Project document file (`2025-12-31 CAFC documents annual
  export.tab`), identified by `uniqueID` (`fc:<uniqueID>`). `DispGeneral` is "the appellate court's disposition of the
  appeal", i.e. of the decision of the tribunal of origin (`origin`, `TribOfOrigin`).
- Scored unit: one **decision below in our corpus** (node) — a decision of the tribunal of origin that the Federal
  Circuit reviewed in that document — linked from one or more items (rules in `LINKING`). The expected status is that
  node's decision-level status. The Federal Circuit decision itself is not scored.

## Model side (what is read)

Exactly as `round6/shepardized/MAPPING.md`, via `benchmarks/common/benchlib.load_status`: decision-level rows of
`status.tsv` (`issue` = `-`, `holding` = `-`) live at the as-of date; no row = `good`.

| Model class | Definition |
|---|---|
| `NEG_HIST` | `neg:*` with `path` = `history` (reversed, vacated, withdrawn, …) |
| `UNK_HIST` | `unknown:*` with `path` = `history` |
| `NEG_OTHER`, `UNK_OTHER` | negative / unknown by another path |
| `GOOD` | `good`, or no row |

The source records only the same-case outcome, so `NEG_OTHER`, `UNK_OTHER` and `GOOD` together form `CLEAN`.

As-of date: `benchlib.DEFAULT_ASOF` (2026-11-12); `score.py --asof` re-runs for another date. A later same-case event
(Federal Circuit rehearing, Supreme Court review, a new decision on remand) can make the model differ legitimately;
documents the source itself marks as replaced are excluded (below).

## Source side: outcome class of each item

| Class | `DispGeneral` (codebook meaning) | Expected model output for the decision below |
|---|---|---|
| `NEG` | `Reversed` ("reverses or reverses-and-vacates"; not partial); `Vacated` ("vacates the entirety of the decision being reviewed") | `NEG_HIST` |
| `PART` | `Affirmed-in-part` (affirmed-in-part with reversed- or vacated-in-part) | `NEG_HIST` **or** `UNK_HIST`; `CLEAN` is a disagreement |
| `CLEAN` | `Affirmed` (whole affirmance; also "affirmed-in-part and dismissed-in-part") | `CLEAN` (`GOOD`, `NEG_OTHER`, `UNK_OTHER`) |
| `OTHER` | `Dismissed`, `Denied`, `Granted`, `Granted-in-Part`, `Withdrawn`, `Transferred`, `Remanded`, `Other`, `Unknown`, blank | not scored |

Key items (`parse_source.py`): `origin` ∈ {`DCT` (US district court), `CFC` (Court of Federal Claims), `CIT` (Court of
International Trade), `CAVC` (Court of Appeals for Veterans Claims)} — the tribunals whose decisions the corpus holds
(agency tribunals PTAB/MSPB/ITC/BCA etc. are not in the corpus); `docType` ∈ {`Opinion`, `Rule 36`, `Rule 36
Judgment`, `Order - Merits`}; class `NEG`/`PART`/`CLEAN`; `Replaced` blank (a document later replaced by a revised
panel opinion, taken en banc, reviewed by the Supreme Court or GVR'd no longer states the final disposition of the
decision below); a parseable `docDate`. Rows sourced from CAP (2001–2009 bulk rows) carry no origin/disposition and
fall out by the origin rule.

Several items linked to the same decision below are combined per decision: all `NEG` → `NEG`; all `CLEAN` → `CLEAN`;
any other mix → `PART`.

## Populations (fixed in advance)

- **Primary (`cited`)**: linked decisions below that the linked Federal Circuit decision cites (graph `edges.bin` +
  round-6 `citeforms/edges_delta.tsv.gz`; corpus citation graph, not model output). This is where a same-case
  negative is detectable from the text of the reviewing decision.
- **Secondary (`caption`)**: linked decisions below found by caption + court + date window only. Reported as `*_all`
  metrics over every linked unit (cited or not); low recall there is expected by construction (Rule 36 judgments
  cite nothing).
- Per-tribunal breakdown (`DCT`, `CFC`, `CIT`, `CAVC`) in the notes and cases file.

## Scoring rules fixed in advance

- **Recall** (primary): of `NEG` units, share the model shows `NEG_HIST`. `recall_lenient`: `NEG_HIST` or `UNK_HIST`.
- **Precision**: of scored (`NEG`/`PART`/`CLEAN`) units the model shows `NEG_HIST`, share the source has `NEG`;
  `precision_lenient`: `NEG` or `PART`.
- **Clean**: of `CLEAN` units, share the model shows `CLEAN`.
- **PART agreement** (`part`): of `PART` units, share the model shows `NEG_HIST` or `UNK_HIST`.
- **Link rate** (`link_rate`): of key items, share linked to exactly one corpus Federal Circuit decision and exactly
  one decision below (cited or caption). `link_rate_cited`: the same, cited links only. Failures counted by reason.
  `link_rate_pre2019`: the same over key items whose Federal Circuit document is dated before 2019-01-01 (the lower
  courts' corpus ends 2017–2019, so later items mostly cannot link).
- Metrics above on the `cited` population; the same with suffix `_all` over every linked unit.
- Halves: `benchlib.split_half("fedcir_dataset", "below:<node>")` for linked units, `"fc:<uniqueID>"` for unlinked
  items. Assigned in `link.py` before any model row is read. Reported h0, h1, all.
- Wilson 95% for every metric (`benchlib.metric`).
- Known artefacts stated before scoring:
  - Patent district cases often have several published rulings (claim construction, summary judgment, JMOL, fees).
    The Federal Circuit reviews the judgment; the linked node is the latest cited ruling of that court in the window,
    which may be a ruling the Federal Circuit did not disturb even when the judgment was reversed (and vice versa).
  - CIT trade cases have chains of remand redeterminations; the same latest-cited rule applies.
  - "Affirmed" Rule 36 judgments cite nothing, so they link only by caption (secondary population).
  - CAVC review is limited to questions of law; a "Vacated" CAVC decision is still a same-case negative.

## LINKING (rules; written before linking, never tuned on model output)

Corpus: `graph/nodes.tsv` (node, repo, path, court id, date, citations, name) and `graph/courts.tsv` (court names).

1. **Federal Circuit decision.** Repo `cafc` (court 520). (a) `Full_Cite` normalised (`123 F.3d 456` →
   `123 f3d 456`) against the node citations, date within 366 days of `docDate`: exactly one → linked (`cite`); several
   → keep those with the exact date, then those sharing a distinctive party token; exactly one → linked, else
   `cafc_ambiguous`. (b) No citation or no hit: `cafc` nodes dated exactly `docDate` sharing a distinctive party token
   with `caseName`; exactly one → linked (`date+caption`); several → keep those sharing ≥ 2 tokens, exactly one →
   linked, else `cafc_ambiguous`; none → `cafc_not_in_corpus`.
2. **Decision below candidates.** Nodes of the tribunal of origin dated from 5 years (1826 days) before the Federal
   Circuit node's date to one day before it: `CFC` → court "United States Court of Federal Claims" (and its
   predecessor "United States Claims Court"); `CIT` → "United States Court of International Trade"; `CAVC` → "United
   States Court of Appeals for Veterans Claims" (and "United States Court of Veterans Appeals"); `DCT` → the district
   court named by `TribOfOrigin` (`D.Del.` → "United States District Court for the District of Delaware", `E.D.Tex.` →
   "… for the Eastern District of Texas"; a multi-district or unmappable value or blank → every US district court).
   Candidates must share distinctive party tokens (rule 4) with the Federal Circuit node's caption sides.
3. **Choice.** Party sides from the corpus caption of the linked Federal Circuit node (`A v. B`; a caption without
   " v. " is one side, with `caseName` words added). Cited candidates (cited by the Federal Circuit node) must share one
   token with each side (two distinct tokens), or the shared surname of same-name parties, or — when only one side has
   tokens (X v. United States, X v. Secretary) — at least one token: exactly one → linked (`cite`); several → the
   latest-dated if unique (`cite+latest`), else `below_several_cited`. No cited candidate → uncited candidates sharing
   one token with each side (with a one-sided caption: at least two tokens): exactly one → linked (`caption`); several
   → `below_several_uncited`; none → `below_not_found`.
4. **Distinctive party tokens**: lower-cased alphabetic tokens of length ≥ 3 after removing the Brace & Hall stop list
   plus Federal-Circuit generic words (united, states, america, secretary, veterans, affairs, army, navy, air, force,
   defense, homeland, customs, border, patent, trademark, director, commissioner, international, trade, technologies,
   technology, systems, …) and the surnames of the Secretaries of Veterans Affairs 1989–2025 (derwinski, brown, west,
   gober, principi, nicholson, peake, shinseki, gibson, mcdonald, shulkin, wilkie, mcdonough, collins) — they name the
   respondent in every CAVC case. Full list in `link.py` `STOP`.
5. Link figures (rates, reasons) use only the source and the corpus. A link is never chosen by looking at a model row.

## Amendment 1 (2026-11-14, before any scoring; no model row had been read)

A read of 36 sampled linked pairs of the first link run (source captions vs corpus captions only) found the cited
links sound but two wrong caption-only links among 12 (e.g. "Blue Spike v. Adobe Systems" → "Adobe System Inc. v.
Blue Source Group": one generic token from each side; "IGT v. Alliance Gaming" → "Bally Gaming v. IGT"). Rule 3 for
**uncited** candidates with a two-sided caption is tightened: each side must share at least min(2, number of that
side's distinctive tokens) tokens with the candidate. Cited candidates, one-sided captions, windows, populations,
classes and metrics are unchanged.
