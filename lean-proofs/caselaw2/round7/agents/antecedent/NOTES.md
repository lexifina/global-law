# Round 7, agent `antecedent`: notes

Times are from `date` (Git Bash; the clock prints "GMTST").

Task: DESIGN7 §2.2 class (i): overrulings stated across two adjacent sentences (act sentence with an anaphor; the
target named in the sentence(s) just before, gap ≤ 300 characters), plus one-sentence acts (rule
`antecedent:onesentence`). Output: DESIGN7 §4 rows (`rows.jsonl`).

- 22:44 start. Read DESIGN7 (§0, §2, §4), DESIGN5 §0–3, r6lib.py, r6scan.py, recog_common.py, reader common.py and
  cue_table.py, cue_table.json (no `anaphor` / `disqualify_joined` / `joined_gap_max` list yet: the lean agent adds
  them; my scan uses its own anaphor regex, see `antescan.py`, and the rows must be re-checked against the final list).
- The round-6 cache holds only decisions with a history signal (zones, citation windows near same-case cues); it does
  not hold the sentences around an overruling cue, so a new (light) corpus pass is needed: `antescan.py`.
- 22:46 `antescan.py` written; alaska test: 7,585 decisions, 328 raw candidate sentences, 10 s.
- 22:47 full scan started (`--procs 22`), log `scan.log`; 22:59 done: 6,892,454 decisions (317 tasks, 0 errors,
  3.9 CPU-h), 139,340 raw act sentences (cue + anaphor, opinion-of-the-court part, no disqualify_treat phrase, no
  procedural object) in 121,571 decisions.
- 22:5x `antecands.py` (resolve citations: staged final2 cite index first, else graph index when unique; names of
  decisions cited elsewhere in the opinion, a caption word shared by two cited decisions dropped; power filter: same
  court / SCOTUS over federal / same system lower tier; date order) -> `cands.jsonl.gz`. `antesel.py` -> tiers.
- 23:05 `antecands.py` done: 139,340 act sentences -> 49,595 candidates with >= 1 near or in-act decision
  (cite_unresolved 160,708 citations, cite_nopower 226,185); 10,917 already have an admitted explicit base row for a
  near/in-act pair (`cands_stats.json`).
- 23:07 `antesel.py` v1 (report/neg/link) and rule sample 1 (`rule_sample_A.md`, seed 11): rule precision on 39
  firing items ~ 12-15 right: the pool was full of "unless overruled en banc", "asks us to overrule", "See X
  (overruling ...)", "the trial court overruled". Added OWN / NOT_OWN (own present act form required).
- 23:12 `antesel.py` v2: tier A 5,123 (2,683 with a base pair), B 1,175, C 479; dropped report 7,362, neg 13,727,
  nolink 5,823, notown 11,133, B-with-base 3,768, other 1,005 (`sel_stats.json`).
  Rule sample 2 (seed 12, 40 tier-A items, read by me): the rule fires on 38; 27 items right with no wrong target
  (71%), 8 wrong (point of error, report "the effect of these cases is to overrule", parenthetical quote, a quoted
  older court, "propositions are overruled", target picked from the wrong sentence), 3 mixed (a cert-denied
  history citation taken as a target; a case followed taken with the overruled one). Misses: earlier sentences of
  a plural referent (Lucus in item 5; Hamilton..Curtis in item 13). => target choice needs the reader.
- 23:14 packs: items whose every near/in-act decision already has a base pair are not read (781 A + 23 C);
  5,973 items in 150 packs (`packs/pack_001..150.md`, `packs/index.tsv`, `packs/map.jsonl`): A = 001-109,
  B = 109-138, C = 138-150. Window 1000 before / 300 after.
- 23:16 lead accepted anaphor_proposal.json (full list -> cue_table anaphor via lean). Packs 091-150 handed to the lead's readers; I read 001-090 (wave 1: 001-030, 6 opus readers x 5 packs, started 23:15).
- 23:18 `answers_to_rows.py` v2: per target, tries in order (first that passes the self-check wins):
  one-sentence (evidence in the act quote) -> joined (naming sentence; shorter starts after a clause boundary;
  from the naming up to the act sentence start, <= 1200 chars) with the reader's act quote, then the full act
  sentence -> plain window row (`antecedent:window`, evidence within [start-400, end+400), as round 4 admits).
- certify7.py crashes on an admitted row without joined lines (KeyError 'joined', line 822): reported to the lead;
  `certify7_local.py` = copy with `pay.get("joined", ())` (paths adjusted), used until infra fixes it.
- 23:18 first 18 packs answered: 720 answers, 363 act true; 173 rows; certify7_local: 125 admitted (59 joined,
  48 one-sentence, 18 window), 48 skipped as already in base, 0 rejected.
- 23:19 lead fixed certify7.py (joined .get); local copy deleted; real certify7 used from now on. Anaphor list (D7-8) pending regeneration by lean: re-certify when the lead says so.
- 23:25 wave 1 (packs 001-030) done (6 readers, ~5-6 min each). Further launches refused: global
  "concurrent subagent limit (40)"; packs 031-090 handed to the lead (lead launches as slots free; 091-150 too).
- Own check of 35 certified rows (20 joined, 15 plain; seed 5; own_check_sample.md): 34 right, 1 wrong: a citation
  key that the index maps to another decision (Clevinger v. Board of Educ., 789 S.W.2d 5 -> node of "Kentucky Bar
  Ass'n v. Klapheke"). => two general guards in answers_to_rows.py:
  citeCaptionMismatch (the caption printed just before the citation shares no word, OCR-tolerant, with the target's
  caption) and nameCollision (a name: word that stands only inside another case's caption). On 3,397 answers they
  reject 26 + 2 (most read as true index collisions; a few OCR variants lost, e.g. Zutter/Zeitler, Pay sen/Paysen).
- Joined rows carry jlen / gap in the row note (lead asked: audit strata <=300 / 301-600 / >600).
- 23:39 all 150 packs answered (5,973 items; 3,048 act true: A 2,358/4,342, B 521/1,175, C 169/456).
  Cue table regenerated (anaphor list 70 phrases, D7-8). answers_to_rows: 1,747 rows (699 joined, 939 one-sentence,
  109 window); per-target rejects: base_has_pair 2,719, joinedGap 61, citeCaptionMismatch 38, noAnaphor 26,
  duplicate_pair 17, nameCollision 3, joinedDisqualified 3.
  certify7 (real, fixed): 1,305 admitted (606 joined, 614 one-sentence, 85 window), 0 rejected, 442 skipped as
  (by, target, kind) already in base. Kinds: overruled 977, disapproved 278, recededFrom 47, abrogated 3.
  Scope: partialUnknown 1,124, all 181. Groups (acting court): state L 941, state A 263, federal A 74, federal S 15,
  scotus 4, other 8.
  Audit sub-classes (subclass_ids.py): A joined 489 (ids_A_joined.tsv; jlen <=300 187 / 301-600 150 / >600 152, all
  gaps <=300), B one-sentence 574 (ids_B_onesentence.tsv), D window-plain 63 (ids_D_window.tsv), C weak verbs 179
  (ids_C_weak.tsv).
