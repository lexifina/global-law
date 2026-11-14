# Round 7, agent `doctrine`: notes

Times from `date` (Git Bash; the clock prints "GMTST").

- 22:49 start. Read DESIGN7 (§0, §2, §4), DESIGN5 §0/§4 (R5-8), improvement_plan (doctrine misses), r6lib/r6scan,
  recog_common, reader common.py, cue_table.json keys (no doctrine lists yet). Brown (node 5994537) checked: tie
  sentence "The doctrine of “separate but equal” did not make its appearance ... in the case of Plessy v. Ferguson".
- The round-6 cache holds only history records (citation windows of reviewees, disposition sentences), not doctrine
  sentences, so one new corpus pass is needed (dscan.py), streaming git as r6scan does.
- 22:59-23:13 dscan.py over all 6,892,454 decisions (317 tasks, 22 procs, ~17k cpu-s): 147,520 tie records,
  247,611 rejection sentences (court parts only), 102,654 name maps. Output scan/*.jsonl.gz.
- build_registry.py: ties resolved (cite 30,387; name 22,598; unresolved/ambiguous the rest). Registry (strict ties
  only = the brief's forms: verb tie, "the D doctrine of X", "X's D doctrine"): 7,199 unique keys, 2,133 ambiguous,
  3,282 plain-only. First version also counted plain "the D doctrine in X" ties for ambiguity: those are mostly
  "the demise of D in Y" (Y the rejecting case) and made separate-but-equal, deliberate bypass etc. ambiguous; dropped.
- Candidates (W tier L = court of last resort incl. SCOTUS, label unique, date(X) < date(W), X in W's system or W
  SCOTUS): 956 sentences, 759 W. make_items.py: tie sentence in W found for 245; rule-ok 37.
- Own measurement of the rule on the 37 rule-ok items (+14 earlier dropped by rule fixes): 23/37 yes (62%).
- certify7 dry run (all 37 as if read yes): 20 admitted; 11 noCue (lean doctrine_reject lacks "hereby reject",
  "depart from", "unsound", "be overruled", ...), 4 joinedRelation (tie list), 2 duplicate.
- 23:29 packs: pack_001 (stratum A = rule ok, 37 items), pack_002..008 (stratum B = tie found, rule said no;
  208 items, for the rule's recall). READER_BRIEF_DOCTRINE.md written. Readers spawned (opus, 4 x 2 packs).
- 23:31 cue_counts.py -> work/cue_counts.json (proposed doctrine_reject / doctrine_tie additions, corpus and
  item counts). report_counts.py, answers_to_rows.py written. Registry: 7,199 unique keys (1,271 tied by >= 2
  decisions), 2,133 ambiguous (e.g. balancing test, exclusionary rule, harmless error, deliberate bypass, mere evidence,
  clear and present danger), 3,282 plain-only.
- 23:3x readers (opus, 4 at once) read packs 001-008 (245 items); fixes after reading: possessive pre-labels
  ("court of appeals' voluntariness") dropped from registry and candidates (build_registry.possessive_core); the tie
  sentence choice now prefers a quote without a disqualifier (make_items pri). 12 items whose tie changed went to
  packs 009-010 (read by a fifth reader). Read-time items kept: work/items_read1.jsonl (packs 1-8),
  work/items_new2.jsonl (packs 9-10); answers_to_rows maps each pack to its own items file.
- Answers: stratum A (rule ok) 38 read, reject 22, tie 29, both 18; stratum B (rule no) 206 read (+1 unread typo id),
  both 12. 1 yes item dropped (label no longer a candidate: Bisner). rows.jsonl: 29 rows (21 W/X pairs).
- certify7 (cert/): 12 admitted (12 pairs: scotus 3, state last resort 9); rejects: noCue 9 (8 pass with the
  proposed doctrine_reject additions, the 9th needs the stem "overrule": "we, therefore, overrule"), joinedDisqualified 5 (Duvall "urges" x4, Harris
  "as stated in"), duplicate 3.
- 18 of the 21 pairs already have an explicit row by W on X in the base (overruled/abrogated); new information for
  Brown->Plessy and Lingle->Agins (base has only witness rows) and Mexicali Rose->Mix, Micallef->Campo,
  Krummenacher->Rowell (no base row).
- 23:40 report written; nothing committed; no processes left running.
