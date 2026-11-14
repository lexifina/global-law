# Round 6 research: how to move the benchmark scores towards 100% without fitting the answer keys

Written 13 Nov 2026. Read-only research: local files plus 17 web searches. Nothing else was edited, Lean was not
run, nothing was committed. `round5/gold_fresh/sealed/` was not opened; sealed-half figures below are the aggregate
lines of `round5/results/final/fresh_test.txt` and `ROUND5.md` only.

Marks on web claims: [confirmed] = seen in a search result or fetched page today; [project notes] = taken from
`research/prior_art.md`, not re-checked today; [memory] = not checked; [not confirmed] = searched, not found.

## 0. Short answer

- No principal benchmark can reach 100%, and for three different reasons: (a) 11% of the fresh key's open half is
  doubtful as a list entry (18 of 165); (b) 13–20% of entries were never stated in words by any court with power;
  (c) "strict" asks for a whole-case negative from the overruling decision's date, which is wrong for real partial
  overrulings and impossible by design for recognised ones.
- Under the current principle, with engineering only, the realistic ceilings are about: fresh lists lenient 71–72%
  (now 65.5% open / 60.6% sealed); SCDB about 72–80% (now 63% counting recognised rows); notes on pairs a court
  with power also states perhaps 60–70% (now 35%); notes overall stays low because 72% of the pool is stated only
  by courts without power.
- On entries that two or more lists agree on, the model is already at 79% (open) and 80% (sealed) lenient. The
  single-list entries score 56% and 47%. A large part of the gap to 100% is list noise.
- The three biggest legitimate gains: finish the reading that is already queued (reader recall, unread packs);
  repair and install the operative-words class behind a real audit; resolve doctrine targets by a two-quote
  certificate. The biggest non-gain that looks like a gain: letting courts without power feed the model (it
  consumes the only independent test).

## Part A. Miss budget

### A1. Fresh lists, open half (165 pairs), frozen build

Sources: `round5/gold_fresh/dev/results/final.pairs.tsv` (outcome per pair) joined to `round5/diag2/dev_misses.tsv`
(cause per pair, diagnosed on the 113 round-4 misses), `round5/results/dev_shares.json`.

Outcomes: a 50 (strict), a_date 30, b 5, c 23, e 57. Strict 30.3%, lenient 65.5%.

| Cause of a strict miss | Pairs | Now scored | Fix class | Gain if fully fixed |
|---|---|---|---|---|
| Date convention: right overruler, whole case, negative only from the later court's date | 30 | a_date (lenient hit) | 13 have the overruling court's own "overrule" word (reader miss 2, scope 4, found only through a later court 7): (1) engineering. The other 17 (other verb 10, doctrine 5, contrary 2): (3) the R5-3 timeline, or a reporting view | strict +13 (engineering), +30 (reporting from date(Y)) |
| Scope left partial or unknown, right overruler | 23 (22 name the listed overruler) | c (lenient hit) | 13: the Court really overruled part; the key lists it flatly (5 of them the key itself marks partial): (4) key/metric. 4 arguable. 6 not assessed for scope | strict +4 to +10 at most; 13 are not errors |
| Negative by another decision | 5 | b (lenient hit) | 2 doubtful entries, 1 doctrine, 2 not diagnosed | 0 |
| List entry doubtful (same case on rehearing, a later Court credits another decision, nothing overruled) | 15 (+3 already lenient hits) | e | (4) the key | 0 |
| Nothing in words, or only "contrary to X" with no verb on X's authority | 12 | e | (3) needs inference from inconsistency (kind E, R5-11) | lenient +12 |
| Own operative verb ("rejected", "cannot be considered as expressing the law"); class built, failed its audit | 10 (+7 sitting in c) | e | within the principle; blocked by precision (79% part, 27% whole) | lenient +10 |
| Doctrine or field is the target, case not acted on by name | 10 | e | (3) R5-8: a doctrine is a target only when tied to one case in the same quote | lenient +10 |
| Reader recall: the Court says "overrule" and we missed it (target by anaphora or far away 7, OCR 2, several cases in one sentence 1, companion-case name 1, slip-opinion chunk 1) | 9 (+3 already lenient) | e | (1) engineering | lenient +9, strict +9 |
| A later Court says so, row not yet installed | 1 | e | (1) engineering | lenient +1 |

Lenient ladder, open half (each step adds to the one before):

| Step | Lenient | Needs |
|---|---|---|
| Now | 108 = 65.5% | – |
| + reader recall and the one missing recognised row | 118 = 71.5% | engineering only; **ceiling under the current principle as installed** |
| + operative words at audit quality | 128 = 77.6% | no principle change; needs a class that passes 90% blind |
| + doctrine / field targets | 138 = 83.6% | principle change (two-quote join, or inference) |
| + inconsistency without words | 150 = 90.9% | abandons the principle |
| Never | 15 pairs = 9.1% | the key's fault |

Strict ladder, open half: now 50 (30.3%). The overruling court uses a term of art in 84 pairs (51%): that is the
hard cap for "whole case, from the overruling decision's date, on its own words". Engineering reaches about 72–79
(44–48%). Reporting recognised overrulings from date(Y) adds the remaining a_date pairs: 80 + 9 = up to about 89–96
(54–58%). Above that, strict punishes correct partial labels: of the 53 pairs now in a_date or c that were
diagnosed, the Court's words dispose of only part of the case in 36.

Other cuts (same files): pairs in 2+ lists 55/70 = 78.6% lenient, single-list pairs 53/95 = 55.8%; pairs a list
calls implied 5/20; pairs outside every CRS edition 5/19 (14 of the 19 are e).

### A2. Fresh lists, sealed half (127 pairs)

Aggregates only (`round5/results/final/fresh_test.txt`): a 32, a_date 25, b 1, c 19, d 4, e 46. Strict 25.2%,
lenient 60.6%. **No cause partition exists and none should be made** (it would unseal the half). By source: Blaustein
38.8% lenient (27 of 49 are e), Gerhardt 75.4%, Wikipedia 76.9%, Payne n.1 94.7%; overruled to 1945: 41.0%; 2+
lists 80.4%, one list 47.4%; implied 5/21. If the open half's shares held (an extrapolation, not a measurement):
engineering ceiling about 70%, the 4 d pairs included.

### A3. Supreme Court Database (278 flagged decisions; burned)

Sources: `eval/score_final.txt`, `round5/results/final/old_by_class.txt`, `round2/recall.md`,
`report/sections/why_recall.html`, `round5/diag/scdb66.tsv`, `round3/scdbaudit.md`.

Found: 141 on the acting court's own words (115 with a term of art, +26 through older operative-wording rows);
175 = 63% with recognised rows. Agreement of the model's Supreme Court overrulings with the flag: 141/152 = 93%
explicit; 175/210 = 83% with recognised rows (the 35 extra are unaudited; in round 3, 11 of 12 unflagged ones were
real acts the database does not code).

| Cause (of the 137 misses before recognition) | Decisions | Fix class | Ceiling gain |
|---|---|---|---|
| No overruling words in the opinion ("wordless"), classified in round 5 | 66 | see next four lines | |
| – a later Court says so with "overrul…" | 10 (7 with both names in one sentence; 6 more weak) | (1); mostly taken in round 5 | +10 (largely already in the 175) |
| – own operative verb on the named case | 4 | precision gate | +4 |
| – doctrine / field only (19 more only state the contrary) | 19 | (3) R5-8 | +19 |
| – nothing (25 have no words about the earlier case at all) | 35 | (3) inference / (4) | 0 under any words-based rule |
| – of the 66, list entry itself doubtful | 17 (overlaps the lines above) | (4) | – |
| Words present, scan or filter missed them | about 51 after round 3 (110 at the start of round 2, 59 recovered "almost all from this row") | (1) | up to +51 minus what recognition already took |
| Target not resolved to one decision | 11 at the start of round 2 | (1) partly | a few |
| Other (same page, rehearing, labelled "declined to follow") / checker | 8 / 1 | (1) / (4) | a few |

**Not in the files:** a partition of the 103 decisions still missed by the frozen build. Recognition added 34; at
most 10 of those can be wordless ones, so at least 24 came from the worded rows. Bounds: hard cap under the current
principle 278 − 56 = 222 (80%); realistic 200–210 (72–76%); with a sound operative class +4; with doctrine targets
+19 (about 245, 88%); the last 35 (12.6%) need inference or are the database's. The database's own codebook counts
"disapproved" and "no longer good law", and also flags a decision because a *later* opinion says it overruled
[confirmed, scdb.la.psu.edu codebook]. Its rule is therefore self-announced + operative + recognised: the same three
classes. Its 35 "nothing" flags fall outside its own rule (24 of the 66 are stated only in a separate opinion, 6
only in the syllabus).

### A4. Constitution Annotated, current table (292 pairs; burned)

162 explicit; 195 = 66.8% with recognised rows; 97 missed. Round-2 partition of the then 209 misses
(`round2/recall.md`): filtered by a reader rule 128, implicit 56, target unresolved 17, other 5, checker 2, treating
decision not in the corpus 1. **Not in the files:** the partition of today's 97. The 56 implicit pairs bound the
current-principle ceiling at about 236/292 = 81% before recognition; recognition has taken some of them (11–14 CRS
pairs of any edition were covered by the witness tier in round 4).

### A5. Later-court notes

Sources: `eval/score_final.txt`, `round5/tests/TESTS.md`, `round5/results/final/holdout.txt`,
`report/sections/why_recall.html`.

Overall agreement 7,161/25,485 = 28.1% (overruled 34%, disapproved 46%, receded 46%, abrogated 3.4%).

| Cause | Size | Fix class | Ceiling |
|---|---|---|---|
| The named decision never says it in its own majority words | 76 of 120 notes read blind (63%); 30 of 34 "abrogated by" | recognition (installed) reaches these only when the speaker has power | own-words ceiling about 37% of notes; we are at 28% |
| "On other grounds" / "in part": a whole-case negative would be wrong | 6,699 of the 9,374 testable pairs; 10,406 of 15,768 "overruled" notes | (4) metric: score these as "partly negative by Y" | – |
| Our regex reading of the note is wrong (target, overruler or kind) | 16% in a blind check | (1) | caps any score near 84% |
| Pairs a court with power also states, still nothing | 1,438 of 2,640 (35.3% now negative or partly) | (1) reading: 1,807 of 89,542 feed statements were read, plus 4,685 pattern rows; 246 packs unread | perhaps 60–70% (not measured) |
| Pairs stated only by courts without power | 6,734 (5.5% now) | (3) "a court with power" | stays near 5% by design; 80%+ only by spending the held-out set |

### A6. Same-case history (reversed, vacated)

Held-out pairs with the reviewing decision named: 20,843; negative by it 8.0%, negative or partly 11.7%, nothing
17,759. Causes named in `data/READER.md`: decisions reviewing an unpublished or non-corpus judgment yield nothing;
Supreme Court memorandum orders without "reported below" yield nothing; head-matter history notes are not used;
36,254 history rows were dropped because the target was cited too far from the disposition; certificates refused
(`score_final.txt`): noAuthority 3,452, noCue 2,926, targetUnresolved 386. **Not in the files:** how the 17,759
split across these causes. Fix class: (1) for head matter and the 36,254 dropped rows; (2) new data for orders and
unpublished judgments. No principle change: a reversal is always in words.

### A7. Circuit splits, holdings audit, treatments audit

- Splits 171/714 = 23.9% by section; node level 9/464, 0 opposite. `round2/splits.md` partitions the misses of the
  reference run (459): section never read for splits 251 + 42; read but no appellate split holding before the
  resolution 14; one circuit only 7; no shared issue key 50; shared key, answers not coded opposite 94; engine 1.
  The reference already scores 35.7% with round-2 work that the live build never installed; 45 answered reader
  batches are also uninstalled. All (1). The section-level figure is inflated by much-litigated sections; the
  node-level figure is the honest one.
- Holdings audit 43/60 = 72% (is a holding 83%; `data/HOLDINGS.md`). A miss partition is not in the files read.
- Treatments 82%: the only matching figure found is "admitted overruled rows confirmed among noted" 81.6%
  (`score_final.txt`). If a separate blind audit gave 82%, it was not among the files read.

### A8. What each relaxation buys

| Rule | Fresh open lenient | SCDB | Notes, also-in-feed | Notes, holdout-only |
|---|---|---|---|---|
| Current principle, as installed, engineering done | about 71.5% | about 72–80% | perhaps 60–70% | about 5% |
| + operative verbs of the acting court (same principle, wider words) | about 77.6% | +4 | small | – |
| + doctrine targets via a second quote naming the case | about 83.6% | up to about 88% | small | – |
| + any court's report counts (citator mode) | little (the Supreme Court is already read) | little | – | up to about 84%, test destroyed |
| + inconsistency with no words | about 90.9% | up to 100% minus bad entries | – | – |

## Part B. What others do

1. **Commercial and open citators.**
   - Shepard's and KeyCite: editors assign treatments. KeyCite Overruling Risk (orange) is machine-made, flags a
     point of law that depends on an overruled or invalidated decision with no direct citing relationship
     [confirmed, Thomson Reuters pages]. Thomson Reuters' own help pages describe its scope in two different ways;
     no accuracy figure is published [confirmed]. A patent application (Custis and others) describes the mechanism:
     a triple (overruling case, overruled case, a third case citationally related to the second) scored by a
     classifier; no metrics found [confirmed; assignee not confirmed].
   - Casetext SmartCite: tags from the signals and words of later citing cases; red = reversed, overruled, vacated,
     withdrawn or superseded in whole or part; orange = relies on a case later overruled; yellow from "but see",
     "contra" [confirmed, LawNext 2019/2024, archived product page]. No accuracy figures.
   - Fastcase Bad Law Bot: purely "negative history as reported by the courts" in citations; a case overturned but
     never cited again is not flagged; Fastcase says no flag does not mean good law [confirmed].
   - vLex Cert: citations + language patterns + appellate history, editors validate; some links carry no editorial
     label [confirmed]. Bloomberg BCite: nothing new found today [not confirmed].
   - CourtListener / Free Law Project: citator in progress, negative treatments only; benchmark built by two
     readers per citation, a third breaking ties, with explicit "Ambiguous" and "Unverifiable" classes; 180+
     Supreme Court cases, 7,600 citations so far; first experiment used the 149 CRS overruled opinions (Claude 3.5
     Sonnet recall above 90%, F1 above 80%) [confirmed, free.law May and Sept 2025].
   - Take: every automated citator uses later courts' reports from any court. That is our "recognised" class
     without the power test. None claims implicit overruling except as a risk flag.

2. **Measured accuracy of automatic detection.**
   - CaseHOLD Overruling (2,400 sentences, Casetext-labelled): F1 about 95.8 BERT, 96.3 Legal-BERT, 97.4 custom
     Legal-BERT; BiLSTM 0.91 [confirmed from secondary listings, not the paper's table]. It is sentence
     classification of explicit sentences: the easy part.
   - LegalBench overruling: same task; per-model figure [not confirmed].
   - Zhang, Savelka, Ashley, "Do LLMs truly understand when a precedent is overruled?" (JURIX 2025): 236 explicit
     pairs from the Constitution Annotated; GPT-5 71% (name the overruled case) and 75% (confirm the pair);
     35% for 1810–1881 against 82% for 1954–2025 [confirmed, arXiv 2510.20941]. Implicit pairs are excluded.
   - Demir and Canbaz 2026: 239 expert-labelled citations, best model 79% coarse, 68% fine-grained [confirmed,
     arXiv 2605.17691].
   - No published precision or recall for implicit overruling was found [not confirmed that none exists].
   - Categories of non-announced overruling: Friedman's stealth overruling (the Court knows it overrules and hides
     it) [confirmed]; Re's narrowing (declining to apply a precedent where it is best read to apply; between
     distinguishing and overruling, and in Re's view legitimate) [confirmed]; Bradley and Grove's five signals of
     disfavour: disparaging statements, narrowing, failure to cite, inconsistent decisions in related areas,
     methodological shifts, with the advice that lower courts act only on the first two and only from binding
     majority opinions [confirmed, Va. L. Rev.]. Kozel [memory, not searched]. Mechanically detectable: signals 1–2
     (words); signal 3 weakly (citation graph, our behavioural test); 4–5 not without a model of the doctrine.
     Agostini / Rodriguez de Quijas: only the Supreme Court overrules its own decisions, even when later cases
     undermine them [confirmed]. That is the legal basis for the power test.

3. **Disagreement between citators (measurement ceiling).**
   - Hellyer 2018 (Law Library Journal 110:4): 357 citing relationships flagged negative by at least one of three
     citators; Shepard's and KeyCite each missed or mislabelled about a third, BCite over two thirds [confirmed].
     "All three agreed in 53 of 357; no agreement in 85%" [project notes, not re-confirmed].
   - Spriggs and Hansford 2000: Shepard's coding "quite reliable", with notable variance across categories
     [confirmed, abstract only; no kappa seen].
   - A Mart study of citator disagreement [not confirmed; the search found none. Her known work is on search
     algorithms, memory].
   - Our own lists: Wikipedia lacks 87 of Gerhardt's 145 pairs; Gerhardt lacks 63 of Blaustein's 121 in the common
     period (part of that is scope: Gerhardt is constitutional only); 20 pairs differ on "in part"; 171 of 292
     pairs are in one list only (`GOLD_FRESH.md`).
   - Consequence: a single list cannot show a system above roughly 65–80%. Only multi-source or adjudicated
     entries can.

4. **Formal models.**
   - Horty's reason model, Rigoni, Prakken, Broughton (vertical precedent): constraint on a consistent case base;
     Horty and Bench-Capon note that a later opinion giving new reasons may be distinguishing, not overruling
     [confirmed]. Canavotto 2022: constraint from inconsistent case bases [confirmed]. Di Florio, Dong, Rotolo,
     "When Precedents Clash" (2024): adds hierarchy and time, formalises overruled and per incuriam cases, and
     *defines* overruling as a court with power deciding differently from a binding precedent [confirmed, arXiv
     2410.10567]. That is kind E as a definition.
   - Empirical use of consistency checks to detect implied overruling: none found [not confirmed that none
     exists]. Our own run (`LIMITS.md` 6): 44 binding bases, 43 consistent, 1 inconsistent. With today's factor
     data the check finds almost nothing.

5. **Evaluation design.** Legal NLP benchmarks mostly use random splits; recent work argues for time splits and
   "inputs available at the time" [confirmed, 2026 preprints]. A sealed set still leaks through repeated scoring
   [confirmed]. Annotation agreement on legal labels averages kappa about 0.68–0.76 over 29 studies; a French
   implicit-citation benchmark has kappa 0.33 [confirmed]. Implicit categories are where experts disagree.

## Part C. Ranked plan

Gains are in pairs or points on the open half unless stated; "basis" names the count in Part A.

| # | Improvement | Moves | Basis | Cost | Overfitting risk and guard | Principle |
|---|---|---|---|---|---|---|
| 1 | **Adjudicated key and scope-aware scoring.** Three blind readers plus adjudication on every list pair: express / operative / recognised-only / doctrine / none / bad entry, and whole or part. Score "right overruler and right extent"; report 2+-list and adjudicated-express subsets as headline | Removes 18 bad entries and 13 correct-partial "misses" from the open half's 115 strict misses (27%); same for SCDB's 17 | A1, A3 | 3 readers × 570 entries; one day | Readers never see model output; the sealed half is adjudicated by the sealed-side agent only | none |
| 2 | **Reader recall**: anaphora beyond one sentence, OCR-tolerant names, several cases in one sentence, companion-case names, slip-opinion page chunks, the opinion-part map (one Justice announcing the judgment) | open +9 lenient, +9 to +22 strict; SCDB and CRS: a share of about 51 worded misses | 12 pairs in `dev_misses.tsv`; round-2 class b | code + re-read; days | Write rules, not rows; no pair-specific patterns; confirm on sealed and on the post-cutoff set | none |
| 3 | **Read what is queued**: 246 unread packs; the remaining feed statements (89,542, of which 1,807 read) | notes also-in-feed 35% → perhaps 60–70%; SCDB/CRS a few | A5 | agent time only | Selection is by speaker's power, never by list; leak check stays | none |
| 4 | **Two timelines in reports**: keep "unknown from Y, negative from W" in the model; add an "as attributed today" view counted from date(Y) | strict open 30.3% → up to 48.5%; sealed 25.2% → up to 44.9% | a_date 30 and 25 | small | None, but it is a convention, not a gain: always print both | reporting only |
| 5 | **Operative-words class, repaired**: require a present-tense act of the speaking court, refuse sentences with an intervening cause (statute, rule, another decision), default to part, two readers must agree, decoys in the audit. Re-audit the 2,315 legacy rows first | open +10 lenient; SCDB wordless +4; the legacy re-audit may *lower* SCDB (26 of the 141 rest on such rows) | A1, A3 | medium | Cue lists frozen before any score; pass = 90% blind on a stratum not used for tuning | none (wider words, same speaker) |
| 6 | **Doctrine targets by two certificates**: (i) the acting court rejects doctrine D in words; (ii) a court with power says in words that D is the rule of case X. Effect always "part" | open +10 lenient; SCDB up to +19 | A1, A3 | high: a doctrine registry | Registry built from court text only; audit the join | yes, R5-8: one quote → a join of two quotes |
| 7 | **Recognition across sentences**: both names within a paragraph, with anaphora | SCDB +3 (10 against 7), some of the 9 open-half c pairs | `scdb66.tsv` D_weak | small | audit to the same 90% bar | none |
| 8 | **Scope resolution**: single-holding cases and flat "X is overruled" become whole; decide the Payne footnote reading | strict +2 to +6 | scope_error yes 2, arguable 13 | small | decide the rule on text, before scoring | none |
| 9 | **History sources**: head-matter history lines, relink the 36,254 dropped rows, Supreme Court order lists, a docket source for unpublished judgments | history 11.7% → unknown; the pool is 17,759 pairs | A6 | medium; new data | score on held-out notes only | none |
| 10 | **Install the split work** already done; read the 293 unread sections; score at node level | section recall 23.9% → 35.7% already measured on the reference | A7 | medium | the section-level figure flatters; report node level | none |
| 11 | **Audit what round 5 added to precision**: the 35 recognised Supreme Court rows the database does not flag; fix date-0 and successor-court defects | protects the 83–93% precision figures | A3 | small | – | none |
| 12 | **Inconsistency tier as "at risk" only**: citation-graph triples in the style of Overruling Risk, plus the Horty check where factors exist. Score as recall of an at-risk flag on the "nothing" class | open: 12 pairs; SCDB: 35 | A1, A3 | research | never a status; separate metric | none while it stays a flag |
| 13 | **Courts without power as a display-only "reported by n courts" signal** | notes holdout-only, display only | A5 | small | Feeding these to status spends the held-out test. If ever wanted, first carve a new held-out set by time | yes if it changes status |
| 14 | **Behavioural check for every new class** (already built) | validation only | TESTS.md Test 4 | none | label-free | none |

## Part D. Evaluation protocol for round 6

1. **Freeze first.** Cue tables, checker, reader briefs hashed before any scoring (as `FREEZE.md`).
2. **Used for building:** the open half of the fresh key, the 66-decision diagnosis, the feed side of the notes.
   SCDB, CRS and the open half are burned: reported, never called blind.
3. **Held out, scored once:**
   - the sealed half (it has been run once on the frozen round-5 build; one more run, on the frozen round-6 build);
   - a **time split**: overrulings decided after a cutoff that no rule, cue or reader brief was written against
     (candidates: Supreme Court terms after the corpus's 2018 end; CRS-table additions after the freeze);
   - a **court split**: state courts of last resort that no reader pack or diagnosis has touched;
   - the holdout notes (speakers without power), with `check_no_leak.py` at exit 0.
4. **Adjudicated gold** (plan item 1) built by agents with no access to model output; publish per-category
   agreement between readers. The agreement rate is the noise ceiling: report every score beside it.
5. **Headline numbers:** (a) adjudicated express + operative + recognised entries, right overruler and right
   extent; (b) entries in 2+ lists; (c) precision by blind audit with decoys at the 90% bar; (d) at-risk recall on
   the adjudicated "no words" class, separately. List recall on raw single lists goes in an appendix.
6. **Pre-register** expected movements per item (as TESTS.md did): e.g. item 3 should move also-in-feed pairs and
   leave holdout-only pairs near 5.5%; a jump there is a leak.
7. **Open and sealed halves must move alike** (round 5: +13.3 and +14.1). A gain on the open half that does not
   show on the sealed half, or on the 27 pairs outside CRS, is fit to the key.

## Part E. What cannot reach 100%, plainly

- Fresh lists: 9–11% of entries are doubtful; another 7% need inference from silence. Honest cap about 84% with a
  principle change, about 72–78% without.
- SCDB: 35 flagged decisions (12.6%) have no words anywhere and fall outside the database's own coding rule.
- Strict: capped at 51% on the open half by the overruling courts' own wording; the rest is a dating and scope
  convention.
- Notes: capped near 84% by our reading of the notes and near 37% by what the named decisions actually say.
  "Abrogated by" (3.4%) is almost always a later court's inference.
- Implied pairs (41 in the key): 10 of 41 found. Experts disagree on these (the lists do), so no system can be shown
  right on them.

## Sources (web)

- https://www.lawnext.com/2019/05/casetexts-new-smartcite-citator-is-its-answer-to-shepards-and-keycite.html
- https://www.lawnext.com/2024/07/new-citators-from-vlex-and-paxton-underscore-that-they-are-the-holy-grail-for-legal-research-companies.html
- https://help.heinonline.org/kb/what-is-bad-law-bot/
- https://legal.thomsonreuters.com/en/products/westlaw-edge/keycite-overruling-risk
- https://www.thomsonreuters.com/en-us/help/westlaw-advantage/tools/keycite-overruling-risk
- https://uspto.report/patent/app/20190347748
- https://support.vlex.com/document-types/case-law/cert-tm
- https://free.law/2025/05/01/citator/ and https://free.law/2025/09/30/citator-annotation-updates/
- https://arxiv.org/abs/2104.08671 (CaseHOLD) and https://reglab.stanford.edu/data/casehold-benchmark/
- https://arxiv.org/abs/2308.11462 (LegalBench)
- https://arxiv.org/abs/2510.20941 (Zhang, Savelka, Ashley)
- https://arxiv.org/abs/2605.17691 (Demir, Canbaz)
- https://scholarship.law.wm.edu/libpubs/131 (Hellyer)
- https://sites.ucmerced.edu/hansford/publications/measuring-legal-change-reliability-and-validity-shepards-citations
- https://scdb.la.psu.edu/online-codebook (precedentAlteration)
- https://columbialawreview.org/content/narrowing-precedent-in-the-supreme-court/ (Re)
- https://www.abajournal.com/magazine/article/dead_precedents/ (Friedman, stealth overruling)
- https://virginialawreview.org/articles/disfavored-supreme-court-precedent-in-the-lower-federal-courts/ (Bradley, Grove)
- https://arxiv.org/abs/2410.10567 (Di Florio, Dong, Rotolo) and https://ebooks.iospress.nl/pdf/doi/10.3233/FAIA220445 (Canavotto)
- https://arxiv.org/abs/2603.22973 (implicit citations, kappa 0.33); https://arxiv.org/abs/2605.24452 (temporal splits)
