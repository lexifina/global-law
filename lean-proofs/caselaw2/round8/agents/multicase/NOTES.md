# Round 8, agent `multicase`: notes

Times from `date` (Git Bash; the clock prints "GMTST").

Task (BRIEF.md): one act of the court overruling / disapproving >= 2 named cases in one sentence (or sentence +
predecessor); one treatments row per named case, same main quote; scope partial on a limiting phrase.

- 00:18 start. Read DESIGN8 §0, COMMON, BRIEF, DESIGN7, ROUND7, certify7.py, round7/agents/antecedent (scan +
  candidate tooling to reuse). INFRA_READY / bench_h0 / audit READY not present yet.
- Plain certificate (certify7 / Lean `check`): cue of the kind in the main quote, no disqualifier, evidence in the
  window [start-400, end+400), part majority/plurality/perCuriam, date order; no quote-length bound in the plain
  check (only orderHead has one). A list sentence therefore certifies one row per named case with the same quote as
  long as each case's evidence (cite key or name tokens) lies inside the window. No Lean change expected so far.
- 00:20 `mcscan.py` written (corpus pass, act sentence with a strong verb + >= 2 case references, or >= 1 + 1 in the
  previous sentence with a plural back-reference; opinion-of-the-court parts; no disqualify_treat, no procedural
  object). Alaska test 323 sentences / 7,585 decisions in 11 s. Full scan started 00:20 (`--procs 10`, log scan.log).
  Note: the scan's NAME regex counts "Matter of X v Y" as two refs (alternation order); harmless for the filter,
  mccands requires >= 2 resolved targets or >= 1 resolved in the act sentence with >= 3 scanned refs.
- 00:22–00:27 `mccands.py` (MC-OWN own-act rule: active "we/this court [adverbs] overrule|disapprove|recede|abrogate|
  repudiate|disavow", passive "is/are/stand(s) [, inserted ,] [adverbs] overruled|...", "must/should/will be
  [regarded/considered as] overruled", minus negation/condition/party-request before the verb and "by"/"on other
  grounds" after it; citation resolution and name resolution as round-7 antecands, power filter, v3 base pairs),
  `mcpack.py` (packs of 40, items whose every target has a v3 base pair are not read), `READER_BRIEF_MULTICASE.md`,
  `mcrows.py` (answers -> rows: plain one-sentence rows for targets in the act sentence, joined antecedent rows for
  targets only in the previous sentence; scope partial on a limiting phrase; round-7 caption guards).
  Partial-scan test (17.8k sentences): 1,164 own-act (6%), 706 candidates; sample read: many good lists ("we disapprove
  of such cases as Maytag ...; Mays ...; Stokes' Estate ..."), plus reports/requests -> readers needed.
- 00:38 scan done: 6,892,454 decisions, 117,259 act sentences with >= 2 refs (or 1 + 1 before with a plural
  back-reference), 0 errors. (Idle 00:39-01:02: my wait monitor misfired; nothing lost.)
- 01:03 mccands: MC-OWN fires on 8,754 (passive 6,668, active 2,086); 4,181 candidates with >= 2 resolved targets
  (or 1 in act + >= 3 scanned refs): 11,612 targets, 5,826 already a v3 base pair; 1,491 items all-base (not read).
- 01:05 mcpack: 2,690 items in 68 packs of 40 (state first, then federal, then SCOTUS).
- 01:05 lead message: state8's cert_multi/ (87 admitted rows from answers choosing >= 2 targets) to be deduped and
  folded into this class before the audit.
- 01:05 17 opus readers launched (4 packs each, packs 001-068; brief READER_BRIEF_MULTICASE.md; answers ans/ans_NNN.jsonl).
- 01:06 h0 diagnosis (h0diag.py; reads only results/v3/bench/state_overruled_tables.h0.cases.tsv; counts): v3 h0 recall
  13/132; of 119 misses: 100 have no scan sentence of a listed overruler naming anything (not list sentences: other
  forms / not found), 14 have a scan sentence of Y but not MC-OWN (mostly reports: "was overruled in", "See X,
  reviewing and overruling A and B", "virtually overruled"), 2 an own candidate not naming X, 3 a read candidate
  naming X. One general own form missing: third person "this court now, upon a review of ..., overrules them" and
  "We, <inserted>, overrule" -> MC-OWN v2 (OWN_ACTIVE3), +37 sentences, +15 new items -> pack_069 (1 reader).
  So the multicase rule can reach at most ~3-4 of the 119 h0 misses.
- 01:11 all 69 packs answered (2,705 items; act true 1,423). mcrows: 2,904 rows (2,865 one-sentence, 39 joined);
  per-target rejects: notInQuoteOrPrev 30, noAnaphor 10, nameCollision 6, citeCaptionMismatch 3; act_quote used 213.
- 01:12 state8's rows_multi.jsonl folded in (87 rows; its 7 `:window:` rows left out: window-only naming was not
  installed in round 7) -> rows_state8_multi.jsonl. certify8 (mine first, then state8's) -> cert/:
  2,991 in, 706 admitted (multicase 659: one-sentence 652, joined 7; state8 47), 2,229 skipped as v3 rows (1,955 ok,
  292 recognised witness tw rows, 181 noAuthority), 56 duplicates (state8 rows already mine, and repeats), 0 rejected.
  Kinds: overruled 498, disapproved 201, recededFrom 7; scope partialUnknown 638 / all 68. State 682, federal 24.
  No Lean change needed (plain and joined certificates admit the list rows).
- 01:12 staged multicase_v1 (stage8 --delta cert); Lean run (NOBUILD=1) started, log run_v1.log.
- 01:13 blind audit r8m01: make_packs8 --class multicase --cert cert --n 80 --pack-size 30 (seed default 7):
  89 items (80 real + 9 decoys) in 3 packs; 6 opus auditors (2 per pack, tags - and b).
- 01:16 audit r8m01 scored (score_audit8.py; 2 readers per pack, strict): right 76/80 = 0.950 [0.878, 0.980];
  right + extent 76/80 = 0.950 [0.878, 0.980]; link 80/80; corpus-weighted 0.943 [0.831, 0.983]; decoys 16/18
  (known wrong 10/12, known right 6/6); readers agree 87/89. Failures (4 rows): "X is overruled, so far as ..., by the
  cases of A, B, C" (a report: the act is by other cases), two "should be overruled" sentences read as not an act,
  one "the old rule of Shaw v Cock (and its progeny ...) should be overruled" read as doctrine rejection. => class
  installable (>= 0.90 point estimate). Lower Wilson bound 0.878.
- 01:18 Lean (NOBUILD frozen r7v3) on multicase_v1: t8 rows 651 ok, 55 noAuthority (authority is Lean's; not mine
  to fix: court-table edges, state8's area). Scored (score8.sh, results round8/results/multicase_v1/, log
  score_v1.log), against base/v3:
  state tables h0 recall 13/132 -> 15/132 (2 cases nothing -> hit; 0 lost); recall_any 15 -> 17; actor_agreement
  13/14 -> 15/16. Fresh dev unchanged (strict 51/165, lenient 111/165). Holdout notes: precedent Y named strict
  771 -> 777 / 12,354; negOrPartly 4,542 -> 4,584; explicitly admitted pairs 3,143 -> 3,194; holdoutOnly negOrPartly
  574 -> 611 / 6,734; alsoInFeed negOrPartly 1,038 -> 1,043. Shepardized dev, FJC, Shadow Docket, SCDB unchanged.
  No-leak exit 0. h0 anatomy after (h0diag.py): of 119 misses, 2 now rows (hits), 1 read with no row (the reader
  chose other targets or act false), 2 own candidates not naming X, 14 Y sentences not own / reports, 100 no list
  sentence of Y at all -> the remaining state-table gap is not list sentences.
- Delta folder ready to stage: round8/agents/multicase/cert (706 rows; 651 admitted by Lean). No LEAN_REQUEST.
- Open: "X is overruled ... by the cases of A, B" (a report form, 1 audit failure) and "should be overruled" (2) could
  be cut by rule if the lead wants a stricter class; 292 rows skipped because a v3 recognised witness row (tw, explicit 0)
  has the same (by, target, kind) — the target is already negative there; 181 skipped rows are v3 noAuthority rows.
