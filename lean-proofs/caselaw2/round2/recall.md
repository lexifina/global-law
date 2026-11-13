# Round 2: recall of overrulings (agent `recall`)

Working files: `work/round2/recall/` (snapshot `base/`, scripts, subagent packs). Log written as the work goes.

## 0. Base and baseline (2026-11-12, 21:49)

- Snapshot of the live `data/` inputs: `work/round2/recall/base/` (22 files, taken 21:49). All before/after figures
  are measured on this snapshot, with only the reader files replaced.
- Engine: the Python reference (`ref/precedent_ref.py run --data base --edges lean-in-v3`), output
  `work/round2/recall/out_before/`. Scoring: `eval/score.py --out out_before --data base --results score_before`
  (`--results` added to `score.py`; the default directory is unchanged).
- The reference does not put the power check in the certificate (Lean's `noAuthority`), so it admits 22,882 pairs
  where Lean admits 21,527. The three gold measures are the same on both: SCDB 82/278, CRS current 85/292,
  2016 express 70/243, 2016 all 72/311.

| measure | before |
|---|---|
| hunt 42: negative from the right date | 21 |
| hunt 42: partly negative | 3 |
| CRS current table | 85/292 = 0.291 |
| CRS 2016 express | 70/243 = 0.288 |
| CRS 2016 all | 72/311 = 0.232 |
| SCDB recall | 82/278 = 0.295 |
| SCDB precision | 82/85 = 0.965 |

## 1. Diagnosis

Scripts: `work/round2/recall/diag.py` (trail of every miss: candidate, cheap-rule verdict, model answer, reader
certificate, checker result), then eight Claude subagents read the text of each treating decision for the misses the
trail does not decide (`diag_chunks/`, brief in `diag_chunks/BRIEF.md`). Gold is used here only to locate and classify.

Per-miss table: `round2/recall_misses.tsv` (496 rows: 279 CRS pairs in any of the three CRS sets, 196 SCDB-flagged
decisions, 21 hunt pairs; columns set, by_node, target_node, label, class, cause, wording, target_ref, scope, part,
quote, note). An SCDB decision takes the cause of its CRS pair when it has one.

| class | CRS pairs | SCDB decisions | hunt | all |
|---|---|---|---|---|
| a treating decision not in the corpus | 5 | 0 | 1 | 6 |
| b filtered by a reader rule | 134 | 110 | 16 | 260 |
| c checker rejected (all `noCue`) | 2 | 1 | 0 | 3 |
| d target unresolved | 19 | 11 | 0 | 30 |
| e implicit | 101 | 66 | 2 | 169 |
| f admitted, scope partial | 0 | 0 | 2 | 2 |
| g other | 18 | 8 | 0 | 26 |
| total | 279 | 196 | 21 | 496 |

CRS current table alone (209 misses incl. 2 unresolved): b 128, e 56, d 17, g 5, c 2, a 1.

Class b by rule (260): no scan pattern for the wording 126; not act-shaped 70; separate opinion, where the part map is
wrong 22; report 18; procedural 15; model rejected 4; narrated past act 3; reader certificate stage 2.

Class e (169): the target is discussed but the court has no overruling words 126; only a dissent or concurrence says
the Court overrules 19; the target is never cited by the opinion of the court 15; only the syllabus says overruled 9.

Class g (26): the gold target is a different decision printed on the same page, or the same case on rehearing (15);
gold target not resolved (5); the reader has the row as `declinedToFollow` (6).

Hunt 21: 16 b (Dobbs twice, Loper Bright and Wayfair through the part map; West Coast Hotel, Payne twice, Seminole
Tribe, Daniels, Erie as not act-shaped; Brown, Ferguson v. Skrupa, Twombly, Pearson, Hudson, Hudgens as wordings with
no pattern), 2 e (Mapp/Wolf, Crawford/Roberts), 2 f (Batson/Swain, Monell/Monroe), 1 a (the Ledbetter Act is a
statute). `known.py` did not resolve Dobbs, Loper Bright, Wayfair, Janus, Knick, Hyatt and Ramos to nodes although
they are in the corpus (its citation table lacks them); `graph/cite_index.tsv` has them.

What the b class looks like (the court's own words, from the subagents' quotes; 130 distinct wordings):

- passive with an adverb or a comma: "that case is definitely overruled", "should be, and now are, overruled",
  "should be, and it is, overruled", "must be regarded as overruled", "must be considered as overruled";
- a conclusion with a modal: "we are persuaded that Wirtz must be overruled", "we hold that Roe and Casey must be
  overruled", "we agree and overrule Parratt to the extent that";
- no-longer forms: "can no longer be regarded as the law / as controlling", "is no longer good law", "are no longer to
  be followed", "it should no longer be regarded as mandatory", "we think it no longer tenable";
- other verbs: "we now reject the rule of X", "it is wiser to abandon the two-pronged test", "we therefore overturn",
  "disavow", "cannot survive", "did not survive", "has long since been discarded";
- procedural false rejections: a procedural word within 90 characters before the verb ("despite those objections
  ... we think that the Friedlander case should be overruled");
- hard-wrapped slip opinions: a wrapped citation parenthetical such as "(Stevens, J., concurring in part and
  dissent-" starts a "separate opinion" that runs to the end of the text.

The checker's own losses on existing rows (not gold-located; `out_before/certs.tsv`): 1,043 `noVerb` (613 + 150
"no longer be followed / no longer follow" labelled declinedToFollow, 131 overruled rows whose quote says repudiate,
abandon, no longer follow/adhere/good law), 169 `noTarget` (165 are `name:` evidence with a hyphen or apostrophe in
the token, which the checker splits into two words), 84 `disqualified` (33 "as stated in", 23 "overruled by" inside
a genuine act).

## 2. What changed (time-boxed by the coordinator; one before/after cycle)

Reader code (`tools/caselaw2/reader/`; v1 files untouched except `scan.py` `CAND_DIR` and `common.part_map2`):

- `common.part_map2`: slip-opinion running heads ("Syllabus", "Opinion of the Court", "THOMAS, J., concurring") set
  the part; a separate-opinion line may hold no digit or parenthesis (wrapped citation parentheticals no longer start
  a "dissent").
- `scan2.py` / `run_scan2.py`: full rescan of the 152 repos with the new part map and eight new wording families
  (nolonger, overturn, disavow, reject, abandon, survive, wrongly, depart) -> `data/reader_work/cand2/`.
- `rules2.py`: 14 round-2 act shapes (passive with adverb, "should be, and now is", "must be regarded as overruled",
  decision as subject, "constrained to overrule", "we hold that X must be overruled", no-longer-law, other verbs,
  "we agree and overrule", gerund, reject/abandon the rule of X, cannot survive, wrongly decided, procedural word
  nearby with a named case), with negation / argument / report guards; cue table `CUES2`.
- `resolve2.py`: skips what v1 read; target resolution adds party-name phrases of two or more capitalised words
  ("Union Gas") and, for anaphoric sentences ("that case", "they"), citations and names in the 800 characters before
  the sentence, nearest first; the certificate window then runs from the citation to the quote.
- `pack2.py`, `READER_BRIEF2.md`, `certify2.py`: Claude subagents read packs (v1 prompt plus the round-2 wordings,
  v1 answer format); certificates as `certify.py`; reader label `claude-subagent`. No Azure call.
- `fix_round2.py`: repairs of rows the checker rejected: A 172 `name:` evidences rewritten in the checker's word form;
  B 646 "no longer follow / be followed / adhere" rows relabelled declinedToFollow -> overruled where the treating
  court is the target's own court or a higher court of its system (117 kept); C 62 quotes cut to the act clause.
- `implicit.py`, `READER_BRIEF_IMPLICIT.md`: the `explicit = 0` tier (below).

Cue lists (same edit in `Certificate.lean` `cues` and `ref/precedent_ref.py` `VERBS`; nothing else in Lean touched;
originals saved as `work/round2/recall/Certificate.lean.pre_recall` and `precedent_ref.py.pre_recall`):

- overruled: + "repudiat", "abandon" (v1 reader cues; 78 existing rows), "no longer" ("no longer follow / be
  followed / good law / the law / controlling": 52 existing rows, the 646 relabelled rows, the new no-longer rows),
  "overturn", "disavow", "discard", "reject", "not survive", "cannot survive", "wrongly decided" (round-2 wordings).
  A cue is only a necessary condition on a row a reader produced; it admits no row by itself. The rows that depend
  on the new cues were sampled in the blind audits of section 3.
- declinedToFollow: "refuse to follow" -> "refuse"; + "no longer", "not inclined", "unwilling", "not adhere",
  "not be followed" (soft kind, atRisk only; about 300 existing rows).

Model reading done in this pass: 264 SCOTUS items (every round-2 item of the Supreme Court) and 960 of 1,382 items
of courts of last resort with the eight highest-yield shapes, from the 126 repos resolved when reading started;
1,224 items -> 596 new explicit rows (overruled 472, disapproved 115, abrogated 6, recededFrom 2, questioned 1;
scope all 204, partialUnknown 392). Model scope `issues` is written `partialUnknown` (the reach step has not run on
the new rows).

Implicit tier: 239 SCOTUS items read -> 21 rows (overruled 15, abrogated 4, disapproved 2), reader
`claude-subagent:implicit`, id `ti:<Z>:<X>:<offset>:<Y>`, `explicit = 0`. Design: both checkers require the quote to
be in the by-decision's text, so `by_node` is Z, the LATER decision of the overruling court that states "X was
overruled by Y"; Y is in the id and in `treatments_items.tsv` (`by=<Y>`). Both sides admit the rows with no code
change (reference: 21/21 `ok`, 21 `atRisk inferred:<kind>` findings, no status row; Lean not run by me). For the
citator form "X, overruled by Y" the quote is cut after the participle, because the checker disqualifies
"overruled by" whatever `explicit` is (5 of 21 rows). `score.py` skips the tier in every table and prints
`implicit_tier`.

Installed in `data/` (originals kept as `<name>.pre_round2.<ext>`): treatments.tsv (31,841 -> 32,458 rows),
treatments_items.tsv, cert_text.tsv (+491 windows), window_sha.tsv (+491, each recut from git HEAD and equal),
cite_index.tsv (+244 graph keys for the new `cite:` evidences), reader_rejects.tsv, reader_stats.json (`round2`).
`hunt/data/known_overrulings.tsv` regenerated with `known.py --out work/round2/recall/out_after` (reference output;
rerun on the Lean output after the integrated run; old file kept as `known_overrulings.pre_round2.tsv`).
`known.py`: `--out`, `--write`, both status layouts, overruler lookup through `graph/cite_index.tsv`, `negLate`,
`atRiskOnly`. `score.py`: `--results`, implicit tier.

## 3. Before / after (reference engine, same snapshot; `work/round2/recall/out_before`, `out_after`)

| measure | before | after |
|---|---|---|
| hunt 42: negative from the right date | 21 | 25 |
| hunt 42: partly negative | 3 | 4 |
| hunt 42: atRisk only | 3 | 6 |
| hunt 42: good | 15 | 7 |
| CRS current table | 85/292 = 0.291 | 126/292 = 0.432 |
| CRS 2016 express | 70/243 = 0.288 | 108/243 = 0.444 |
| CRS 2016 all | 72/311 = 0.232 | 112/311 = 0.360 |
| SCDB recall | 82/278 = 0.295 | 113/278 = 0.406 |
| SCDB precision | 82/85 = 0.965 | 113/125 = 0.904 |
| SCOTUS-on-SCOTUS admitted, in CRS | 85/95 | 127/151 |
| admitted pairs (score.py) | 22,882 | 24,393 |
| notes agreed: overruled / disapproved / abrogated | 4,694 / 1,329 / 77 | 4,960 / 1,361 / 130 |
| confirmed among noted: overruled / disapproved | 0.814 / 0.812 | 0.813 / 0.809 |
| checker rejections of treatments (noVerb / noTarget / disqualified) | 1,043 / 169 / 84 | 12 / 4 / 24 |

The "after" column uses the reference with the widened cue lists. New hunt negatives: Adkins (West Coast Hotel),
Booth and Gathers (Payne), Union Gas (Seminole Tribe). Parratt is now partly negative. Wolf, Roberts and Logan
Valley are atRisk through the implicit tier, Saucier through a soft row. Still good: Plessy, Lochner, Swift, Halper,
Quill, Roe, Casey.

New rows by tier and checker outcome (reference): explicit 596, all `ok`; implicit 21, all `ok`. Repaired rows:
874 of 880 now `ok`.

Blind audits (separate Claude subagents; they saw the passage, the sentence and the two decisions, not the label;
Wilson 95%; files in `work/round2/recall/audit/`):

| sample | n | measure | result |
|---|---|---|---|
| new explicit rows | 30 | own act and right target | 30/30 = 1.00 (0.89-1.00) |
| new explicit rows | 30 | and same kind | 28/30 = 0.93 (0.79-0.98) |
| new explicit rows | 30 | scope all/partial agrees | 29/30 = 0.97 (0.83-0.99) |
| relabelled "no longer follow" rows (B) | 25 | own act and right target | 22/25 = 0.88 (0.70-0.96) |
| relabelled rows (B) | 25 | and kind overruled | 21/25 = 0.84 (0.65-0.94) |
| implicit rows (all) | 21 | the later decision states the target was overruled | 21/21 = 1.00 (0.85-1.00) |

Samples are below the 40/20 asked for (coordinator's time box: 20-30 per tier). SCDB precision fell: 12 of the 125
acting decisions are not SCDB-flagged; they were not audited separately.

## 4. Next round

- Read the rest: 422 last-resort items of the eight shapes; about 4,600 last-resort items of the wider shapes
  (no-longer-law 2,000, other-verb 815, reject-rule 777, survive 559, no-target 418); about 12,000 items of
  appellate and trial courts; 25 repos scanned but not resolved (`resolve2.py` resumes). A pack of 80 items takes a
  subagent about two minutes.
- Hard-wrapped slip opinions: `sentence_span` ends a sentence at every line break, so "We hold that Roe and Casey
  must be overruled" has no target in its fragment (Dobbs, Wayfair, Loper Bright stay unread). Join wrapped lines
  before sentence splitting. Three-letter names ("Roe") are not name tokens.
- Wordings still without a pattern: "is rejected" (Brown), "has long since been discarded" (Ferguson v. Skrupa),
  "in disapproving that doctrine" without a named case (Erie), "has earned its retirement", "disavow the method".
- Implicit tier: 1,190 candidate SCOTUS pairs, 239 read; no state court of last resort read.
- Run `holdings/reach.py --treatments` on the 392 new partialUnknown rows.
- The 22 `C_not_curable` and 24 still-disqualified rows; class d anaphora beyond 800 characters.
- Audit the 12 SCOTUS decisions with a new admitted overruling that SCDB does not flag.

## 5. Needed in Lean / ref

- Rebuild Lean: `Certificate.lean` `cues` changed for `.treat .overruled` and `.treat .declinedToFollow` (list
  literals only; the reference has the same lists). Examples or fuzz cases that expect `noCue` for a quote holding
  "no longer", "reject", "abandon", "repudiat", "refuse" under those two kinds will now pass the cue step.
- Optional, to key the implicit tier on the overruling decision (by = Y) instead of the stating decision: let a
  treatment row with `explicit = 0` carry a witness text hash (the stating decision's `text_sha`) that `shaOk`
  accepts in place of the by-decision's, and skip the report disqualifiers ("overruled by", "abrogated by",
  "disapproved by", "as stated in", "as recognized in") when `explicit = 0`. The rows can then be re-keyed from the
  `by=` field of `treatments_items.tsv`.
