# state8 notes (round 8, move 5: state-court gaps)

## Log
- 00:18 Started. Read DESIGN8, COMMON, BRIEF, state tables SOURCE/MAPPING/DISAGREEMENTS, ROUND7. Infra not ready
  (no round8/bench_h0). Reading DESIGN7 and the pipeline meanwhile.
- 00:20-00:26 Pipeline read (no key): reader = data/reader_work cand (family regex) -> res rejects (rules.py: procedural,
  not-act-shaped, past, report, separate-opinion, no-target) -> items -> llm main/hard -> treatments; round-3 own-act
  queue (work/round3/queue/queue_snapshot.tsv, 31,803 rejected-candidate ids) belongs to agent `ownact`.
  Wrote common8.py (index = staged v3 cite_index over graph index; WIDE_RX + r6cite.resolve), trace.py (per pair:
  mention / cue sentences / reader stage / queue membership / v3 rows + verdict / X status), tested on 3 base rows.
  Observed in georgia rejects (no key): rules.py NOISE_BEFORE ("ruling(s)", "error", "ground"... within 60 chars)
  sends "the decision/rulings in X ... are overruled" to `procedural`; PASSIVE_ADV misses "are, therefore, now
  overruled", "must be, and hereby are, overruled", ", on review thereof,". Checked 00:29: of rejected candidates
  with a case reference + "is/are ... overruled|disapproved" (no "by/in" after), only a minority are in the ownact
  queue (georgia 38/198, ga-app 40/281, california 30/283, new-york 5/66); "separate-opinion" rejects are large
  (ga 55, ga-app 136, cal 106).
  Alias probe (alias_probe.py): "N Kelly P" (Ga. 1-3) in georgia texts: 664 occurrences, 218 agree / 6 auto-disagree
  (pin cites) / 288 no first-page key / 152 unverifiable. Small.
  noauth.py: 2,073 v3 treatments rows noAuthority; mostly panels under strong horizontal rules (NY App Div 172, Fla DCA
  244, Tex 93, federal circuits); Ga App 1906-16 (3-4 judges) and Ala Ct App (3 judges) "panel" bench by default.
- 00:29 round8/bench_h0/READY. v3 h0 state tables: recall 13/132, recall_any 15/132; 117 nothing, 2 other_actor.
  Misses -> 154 (X, listed Y) pairs (work/h0_miss_pairs.tsv, read by trace.py only for diagnosis).
- 00:31 trace.py over the 154 pairs (work/h0_trace.jsonl), anatomy.py:
  ## Miss anatomy (h0, v3; counts only)
  | stage | pairs (154) | X (119, furthest stage) |
  |---|---|---|
  | (a) X or Y not in corpus | 0 (key links both by construction) | 0 |
  | (b) Y's text has no resolvable cite and no party name of X | 9 | 5 |
  | (b') X cited only in an unresolved reporter form | 0 as sole mention (7 pairs have a name too) | - |
  | (c1) X mentioned, no overrul/disapprov/reced/abrogat sentence within 600 chars | 97 | 84 |
  | (c2) explicit-verb sentence near X, reader rule rejected it / model not asked about X | 48 | 30 |
  | (d) a v3 row by Y on X exists but Lean refused it | 0 | 0 |
  | (e) admitted row, status lacks it | 0 | 0 |
  Of c2 (48 pairs), my reading of the sentences: 11 real own acts by Y on X (4 of them multi-case -> `multicase`;
  1 in the ownact queue), 2 borderline ("must be regarded as overruled"; "In overruling the case of ..."); the other
  35 are reports of another case's act ("was overruled by/in Z"), procedural "overruled" near the mention, or
  "virtually/in effect overruled". Reader-rule causes of the 11: REPORT regex fires on "overruled in so far as"
  (the "in" of "in so far" read as "overruled in <case>") 3; NOISE_BEFORE "ruling" ("ruling in this case is, on
  review, expressly overruled") 1 + queue 1; comma clause between subject/aux and verb ("We, therefore, disapprove",
  "are, therefore, now overruled", "this court now, upon a review of ..., overrules") 3; old-California part map:
  "<judge>, J., delivered the opinion of the Court / <judge>, C. J., concurring." -> the rest of the opinion is
  `concurrence~`, every sentence rejected `separate-opinion` 2 (forms "we have no hesitation in overruling it",
  "it is our duty to overrule it"); target only in an earlier sentence 1. (Counts only; no key row is an input.)
  No pair reached certification: the state-table gap is entirely before the certificate (reader rules + implicit).
- 00:33 partcount.py (cand "d" records): the part-map cut (majority segment < 400 chars then concurrence~ to the end)
  hits 607 decisions with candidates (ca9 311, california 132, idaho 26, ca2 18, ohio-app 15 ...), 1,093 candidate
  sentences (551 overrule-family) -> rule PF.
- 00:35-00:46 Rule R8S (rescue_rules.py: REP / NOI / COM / INF / PF repairs of reader rules.py, docstring there),
  rescue.py over every reader-rejected candidate (2,510,939 rejected sentences, 152 repos; work/rescue/, stats in
  work/rescue_stats.json): 45,841 rescued, of which 41,889 were `no-target` (already act-shaped for the reader; target
  not resolved: round-7 antecedent class, left out), queue 1,620 (ownact), r7-antecedent packed 202, multi-name 188,
  not a status kind 222 -> 1,720 sentences; rescue_cands.py (round-7 antecands resolution, power/date filter):
  427 candidates with a near/in-act target (1,206 none, 87 every near target already a base pair). Tags: we 122,
  passive 110, passive2 87, we2 53, PF 25, extent 16, inf 14. Sample check led to two fixes before packing (modal
  passive needs no argument/negation words before it, as rules.act_shaped; a limiting phrase after the verb is still
  a report in a past/perfect form).
  Coverage check (counts only): the rule reaches 3 h0-miss (X,Y) pairs as candidates with X as a near/in-act target.
- 00:46 packs/pack_001-011 (antepack.py reused; 427 items), READER_BRIEF_RESCUE.md; 5 opus readers launched
  (001-002, 003-004, 005-006, 007-008, 009-011) -> ans/.
- 00:50 Reporter-form aliases (b'): unresolved forms in the h0-miss Y texts: "Cal. Rep." 4, "John." 3, "Park. Cr.
  Rep." 3, "Ga. R." 2, "Geo. R." 1, "Johns. C." 1 (none is the only mention of X: every such pair also names X).
  alias_probe.py on the state's own repos (auto name check, crude: a "disagree" needs any "A v. B" in the 120 chars
  before, often another citation or a pin cite / shared page): calrep->cal 331 occurrences, agree 63, auto-disagree 8
  (63/71 = 0.887); gar->ga 540, 283/301 = 0.940; geor->ga 238, 115/119 = 0.966; kelly->ga (vols 1-3) 664,
  218/224. Read 12 of the auto-disagreements: all are index first-page / shared-page / pin-cite effects that the
  canonical form has too, not reporter confusion; but the round-6 bar (>= 97% with every disagreement read) is not
  met in the time I have, and no h0 miss depends on an alias (stage b' alone = 0). Not built as a delta; reported.
- 00:50 readers done: 427 items (416 distinct ids; 2 packs held a repeated item), act true 258 (answers), false 158.
  answers_to_rows.py (round-7 antecedent tool, unchanged) -> work/rows_raw.jsonl: 267 rows (onesentence 233, joined
  23, window 11); per-target rejects base_has_pair 72, duplicate_pair 8, disqualified 7, joinedGap 2, noAnaphor 1,
  nameCollision 1. split_rows.py: rows.jsonl 169 (single-target answers, one-sentence/joined; class R8S),
  rows_multi.jsonl 94 (answers choosing >= 2 targets: multicase's class, certified apart, not in my variant),
  rows_window.jsonl 4 (window-only naming: not installed form in round 7, left out).
- 00:51 certify8 -> cert/ (R8S): 169 in, 151 admitted, 18 already v3 rows, 0 rejected; 10 joined. cert_multi/: 94 in,
  87 admitted, 7 in v3. stage8 state8_v1 = v3 + cert/. Lean NOBUILD run started.
- 00:56 Lean (NOBUILD, frozen v3 checker) on state8_v1: R8S rows ok 132, noAuthority 19 (panels of intermediate
  courts: Fla DCA 8, Ga App 4, Ala Civ App 2, Ala Ct App 1939 (3 judges) 1, La/Pa Super/Tex 1 each).
  score8.sh state8_v1 vs base (v3): state tables h0 recall 13/132 -> 15/132 (11.4% [7.0, 17.9]), recall_any 15 ->
  17, actor_agreement 15/16; fresh dev strict 51 -> 52/165, lenient 111 -> 112/165; holdout notes precedent Y-named
  strict 771 -> 776/12,354, alsoInFeed negOrPartly 1,038 -> 1,045/2,640, holdoutOnly negOrPartly 574 -> 589/6,734;
  Shepardized dev unchanged (140/254); other h0 keys unchanged except 1 Shadow Docket h0 case CLEAN -> UNK_OTHER
  (model changed, agreement unchanged); no-leak exit 0.
- 00:57 LEAN_REQUEST.md: BENCH-3 data rule (court with <= 3 judges: default panel -> wholeCourt); 30 v3 rows + 1
  R8S row; no h0 effect. Not needed for R8S.
- 00:58 Blind audit r8s01 (make_packs8.py --class R8S --cert cert --lean-certs round8/out/state8_v1/certs.tsv --n 80
  --pack-size 30): 132 Lean-admitted rows, 89 items (80 real + 6 known-wrong + 3 known-right decoys), 3 packs;
  2 opus auditors per pack launched.
- 01:00 Audit r8s01 scored (score_audit8.py; 2 blind opus auditors per pack, strict = every reader right):
  R8S right 77/80 = 0.963 [0.895, 0.987]; right + extent 76/80 = 0.950 [0.878, 0.980]; link 80/80; corpus-weighted
  right 0.977 [0.934, 0.993]. Failures: act 2 (auditors read "limit / modification" where the row says disapproved /
  overruled "should be, and is"), own 1 (one reader of the PF item: old-California "<judge> concurring" opening
  line), extent 1 (whole-scope row, "we overrule X" followed by "X erred in extending ..."). Decoys 16/18 (pack 3:
  both readers missed one known-wrong operative-part decoy). => R8S passes the bar (point >= 0.90): ready to stage.
- Lead (message): BENCH-3 not staged this round (D8-10); recorded as open point.

## State / deliverables
- Delta folder ready to stage: `round8/agents/state8/cert/` (class R8S, 151 certify8-admitted rows, Lean admits 132,
  19 noAuthority). Variant built and scored: `state8_v1` = v3 + cert/.
- Not in my variant: `cert_multi/` (87 admitted rows from answers choosing >= 2 targets: multicase's class; for the
  lead to dedupe against multicase), `rows_window.jsonl` (4 window-only rows, form not installed in round 7).
- Open: the reader's `no-target` rejects (41,889 sentences the reader already took as acts, target not resolved within
  400 characters; round-7 antecedent class) were not read; reporter aliases calrep/gar/geor/kelly measured, not built;
  BENCH-3; implicit overrulings (stage c1, 97 of 154 h0 pairs; 68 have no explicit verb anywhere in Y) need an
  implicit-class reader, not a cue rule. Rehearing sections: the part map already reads "Rehearing"/"On rehearing"
  headings as majority; no h0 miss traced to a rehearing section.
