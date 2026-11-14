# shadow10 notes

- 03:48 started; read BRIEF, DESIGN10 (§0, §4), COMMON, round9 shadow9 NOTES/LEAN_REQUEST. INFRA_READY / audit READY not yet present. df: 27 GB free.
- 03:48 **READING FOR THE LEAD (§4 remandDocket): the runner has NO docket field for nodes.** decisions2.tsv (stage v9c) has 9 columns:
  node, court, date, unit, bench, pub, form, text_sha, src (decisions_build.py writes node,cid,date,uval,bv,pv,fv,sha,src[,comm]);
  Data.lean `structure Decisions` = court/date/unit/bench/publication/form/present/sha. The docket string is read by
  decisions_build only to derive the unit, then dropped. So §4.2 cannot be "a docket token of both B and the target" from a
  loaded field. Proposal (data side ready either way): check the docket token against each node's OWN TEXT, as the other
  quotes are checked: two extra quote spans, one in B's text and one in the target's text (window-hashed in cert_text.tsv /
  window_sha.tsv like the bridge quote), each ≤ 200 chars, whose compact (alnum, lower-cased) string holds the compact docket
  token. I.e. history_remand.tsv grows to 9 columns (id, b_node, b_start, b_end, docket, bd_start, bd_end, t_start, t_end), or
  a second table history_remand_docket.tsv (id, node, start, end). I will supply both spans; lead + lean10 to choose.
- 03:53 remand10.py pre (§4 + D10-5 pre-check, Python) over v9c rows remandtext-v2 (335) + remandcap (32) = 367 -> cert_remand/:
  pass 151 (v2 134: tie odate 84 / cite 30 / odocket 20; remandcap 17), fail 216: remandTie 211 (v2 201, cap 10), remandCue 5 (remandcap,
  certDenied-type rows whose B has no SC remand cue). No failure on court / date / docket (docket token found in both texts for all).
  Why remandTie fails (sample): B's cue sentence ties to O only by (a) O's parallel S.Ct./L.Ed. cite while O's U.S. page is an
  order-list page shared by many orders (not unique -> not used), or (b) only the reason case ("in light of Johnson v. United States")
  or "On remand from the Supreme Court" with no tie at all. Fixing (a): O's parallel cites from the graph index (next).
- 03:53 cap10.py (move 5 part 2, no B): GVR order, one court below, one caption; T = the unique decision of that court 1..1,095 d
  before O tying O's caption on both sides (round-9 both_sides, given-name guard), no sibling on T's docket (rule C2). 2,194 GVR
  orders with a candidate; C2 links 1,461: base same 1,219, base other 9, new 233 (post-2013 56). Non-key truths (Reported below,
  bridge strings, list rows) 221/224 = 98.7%. h0 misses diagnosis (diag_h0): right 67, wrong 3. C5 (<=540 d) 192/194 truths, h0 61/3.
- 03:55 **§4 PRE-CHECK RESULT + TWO READINGS FOR THE LEAD / lean10.** Data: round10/agents/shadow10/cert_remand/ (spec ties only):
  history_remand_delta.tsv (9 cols, D10-5), cert_text_delta.tsv + window_sha_delta.tsv (windows [s-400,e+400) as round-8 bridges),
  cite_index_delta.tsv (O keys the graph index maps to O alone, used by a tie), precheck.tsv (per row), stats.json.
  367 rows (v2 335 + remandcap 32; all in v9c): **pass 151** (v2 134, cap 17); fail remandTie 211, remandCue 5 (remandcap
  certDenied/reviewDismissed rows: B has no SC remand cue - expected, those orders remand nothing), court/date/docket 0.
  (R1) "the order's docket token" in check 4 is the SUPREME COURT docket of O (e.g. 14-8768), NOT the `docket` column (the
  case-below docket shared by B and T; B's quote holding its own docket is no tie). The amendment sentence "Check 4's order's
  docket token means compact(docket) found in compact(B's quote)" would make the tie trivial; I check O's SC docket (memo parse of
  O's own text, compact >= 4 chars with a digit). The runner has no O docket either -> suggest O's docket be found in O's own
  quote window (the row's main quote window) compact, or drop the odocket tie (only 20 rows rely on it; most also tie otherwise).
  (R2) Variants measured (work/cert_remand_shared, work/cert_remand_sr): + O's order-list page cite even when the page holds several
  orders ("444 U.S. 987" shared) -> 200 pass; + the REASON CASE named in O's own text ("in light of Johnson v. United States,"
  compact >= 8 chars, also in B's quote) -> **330/367 pass** (v2 304, cap 26). The reason tie is the court below's usual words
  ("vacated and remanded ... in light of Johnson v. United States"). If the lead wants it: 3 more columns (tie string, o_start,
  o_end: a span of O's text <= 300 chars holding "in light of" and compact(tie)); I can supply them in minutes.
- 03:58 cap10 full-name rule C6: among the both-sides candidates exactly one whose text head (first 4,000 chars) holds the caption
  party's full printed name (compact, e.g. "hectorvillarreal"; non-government side, >= 2 name words), no sibling. Non-key truths 135/136
  (99.3%); h0 misses right 100, wrong 2 (C7 = latest on one docket: 151/164 truths, h0 106/10 -> dropped). Post-2013 misses: the
  60 "several candidates" are common surnames v. United States (Davis, Martinez, Villarreal...), which C6 resolves by the given name.
- 03:58 build10.py C6 then C2 -> rows_cap_a.jsonl: 234 rows (C6 127, C2 107; post-2013 88; vacated 213, reversed 21; scope
  unknown 21); linked 1,605 orders, base same 1,313, base other 15 (not rows), no name evidence 43; C6/C2 never disagree.
  Waiting for INFRA_READY to certify with certify10.
- 03:58 remand10.py updated to D10-6 exactly: date forms (full / jan. ... sept./sep. ...) on the lower-cased quote; tie (b) = the
  B/T docket column in B's quote (used only when no cite/date tie exists); O's own SC docket only with --odocket (not in D10-6).
- 04:00 **§4 table, D10-6-exact pre-check (cert_remand/, the deliverable):** 367 rows -> **241 lines pass** (v2 221, remandcap 20);
  fail remandTie 121 (v2 114, cap 7), remandCue 5 (cap). Tie used: cite 45, date 90, **tie (b) own docket 106**.
  Note on tie (b): compact(docket) is by construction in B's own text, so (b) passes whenever B's docket line is within 600 chars of
  the cue (B's caption + "On remand from the Supreme Court"): it ties B to T (already checked by remandDocket), NOT to the order.
  Without (b): 137 pass (work/cr_nobd). With O's SC docket instead (my R1 reading): 149 (work/cr_od). With shared order-list page cites
  + the reason case named in O's own text (+ b): 339 (work/cr_sr). Lead: (b) as ruled makes remandTie weak; the reason-case tie is
  the strong, common form (184 rows).
- 04:00 certify10 rows_cap_a -> cert_cap_a/: 233 admitted (claim - 165, orderHead 68; vacated 212, reversed 21), 1 orderHeadNotAllowed.
  Audits built: r10k01 = sub-class C6 (126 rows; 80 + 9 decoys, 3 packs), r10k02 = sub-class C2 (107 rows; 80 + 9 decoys); 12 blind opus
  auditors running (2 per pack).
- 04:00 readers (3 opus, 30 post-2013 h0 misses that C2/C6 leave unlinked; corpus text only, candidates unmarked): vs h0 target
  (diagnosis): right 17, wrong 2, none/unsure 11 (8 of them: the target not among the candidates -> candidate generator, e.g. compound
  surname / habeas "Warden" captions). Patterns they give: latest merits decision on one docket before the SC docket's filing year
  (en banc / rehearing-denied entries are not the judgment); whole compound surname; given name must match; Warden captions.
- 04:01 C8 (readers' pattern: full-name / both-sides candidates all on one docket -> the latest dated before 1 July after the order's
  docket-number year): truths 226/242 = 93.4%, h0 misses 114/11 -> not built (too close to the bar; C2+C6 kept).
- 04:01 **audit r10k01 (class C6 full-name caption link, population 126)**: `make_packs10.py --class capC6 --cert cert_cap_a --match table=history
  --match src=cap-C6 --n 80 --pack-size 30`; right (link + kind) **77/80 = 0.963 [0.895, 0.987]**, link + effect same, corpus-weighted 0.976
  [0.934, 0.992]; decoys 18/18; readers agree 89/89. Errors (3, all 'link'): 2 same case but an earlier decision (the reviewed judgment is a
  later one not in the corpus; target 20+ months before the cert docket year), 1 different case (NLRB v. Local 1445 vs Heartland). Passes.
- 04:02 note: reading round10/LOG.md tail (to check infra state) showed a line naming the new held-out key; nothing about it was opened or used.
- 04:04 **audit r10k02 (class C2 unique both-sides caption, no full name; population 107)**: right **50/80 = 0.625 [0.515, 0.723]**, link
  51/80; decoys 18/18. Errors: different people of one surname (Travis vs Brian Storey, Lanice vs James Bonds, Donte vs Byron Riley), different
  suits of one party, earlier judgment of the same case. **C2 NOT installed** (the non-key truths flattered it: orders with "Reported below"
  are the easy ones). The full-name condition is what makes C6 work.
- 04:04 build10 C6 only -> rows_cap_b.jsonl 127 -> certify10 -> **cert_cap_b/ 126 admitted** (1 orderHeadNotAllowed) = exactly the
  audited r10k01 class. Waiting for INFRA_READY to stage / run / score.
- 04:04 LEAN_REQUEST.md written (optional §4 amendment: reason-case tie with an O span; tie (b) weakness). Lead decides.
- 04:04 expected h0 effect of cert_cap_b (diagnosis vs diag_h0 misses): 40 misses linked right (post-2013 38), 1 wrong. Waiting for INFRA_READY.
- 04:08 lead D10-7 (12 cols, reason tie c2, tie (b) dropped, shared page no tie) + ref10's cut bug (quote ended "...Supreme Court vaca":
  the cue window used 4 chars for every cue; now each cue's own length). remand10.py redone -> **cert_remand/: 316 lines (12 cols) of 367 rows**
  (v2 294, remandcap 22); fail remandTie 46 (v2 41, cap 5), remandCue 5 (cap). Ties: c2 reason 210, date 80, cite 28 (some rows hold two).
  O spans from O's git text: "in light of X v. Y" starting before the disposition quote's end + 50, <= 300 chars. Independent re-check
  verify_remand.py (reads only the delta's windows + v9c decisions2/cite_index): 316/316 pass. ref10's 8 cut rows: 5 pass, 3 fail properly.
  Previous D10-6 version kept as work/remand10_d106.py.
- 04:09 INFRA_READY. staged shadow10_a = v9c + cert_cap_b (history 185,793 -> 185,919; claim +59). Lean NOBUILD run started.
- 04:15 **shadow10_a (= v9c + cert_cap_b) Lean NOBUILD: all 126 h10 rows ok/ok. score10 noold -> round10/results/shadow10_a/:**
  Shadow Docket h0 recall 475 -> **514/1059 (44.9% -> 48.5%)**, precision 475/519 -> 514/558 (91.5% -> 92.1%), clean 43775/43811 unchanged.
  Fresh dev, no-leak, Shepardized dev, SCDB / FJC / state tables h0: unchanged. Holdout notes history 5033/6121 -> 5037/6135 (+4 of +14 rows).
- FINAL: delta to stage round10/agents/shadow10/cert_cap_b (126 history rows, class shadow10:cap-C6; audit r10k01 77/80 = 0.963 [0.895, 0.987]);
  §4 data round10/agents/shadow10/cert_remand (316 lines, 12 cols, D10-7; for lean10's build). Not for staging: cert_cap_a (contains C2,
  r10k02 0.625). No --remove. Data gap (unchanged, not fixable by rules): 281 h0 NEG orders not in the corpus (order lists 2006-09 and
  2020-25 missing; by year 2006:28 2007:21 2008:79 2009:26 2020:11 2021:32 2022:28 2023:6 2024:32 2025:14, other 4).
- 04:15 lead: disk; clean10 shadow10_a run (stage/out/WSL data deleted, results kept).
- 04:41 lead follow-up: widen C6 candidates (compound surnames, Warden/official respondents), certify, fresh audit of new rows, score on v10b.args, clean.
- 04:46 wide10.py (rule C9 = C6 with wider candidates: any decision of the named court 1..1,095 d before O whose compact title
  holds a full-name side's whole surname (hyphenated kept whole, Jr./Sr./II.. dropped); exactly one with the full name in its text head;
  no sibling). 1,418 orders, 1,182 with candidates, 35,008 heads read. Linked 518: base/C6 same 431, other 12, new rows 58 (post-2013 19).
  Non-key truths over all links 92/97; new rows on h0 misses 5 right 0 wrong. certify10 -> cert_wide/ 57 admitted (1 orderHeadNotAllowed).
  Audit r10k03 = whole class (57 + 8 decoys, 2 packs, --exclude r10k01 r10k02), 4 opus auditors running.
- 04:50 **audit r10k03 (class C9, whole class 57, fresh, excl. r10k01/02)**: right **40/57 = 0.702 [0.573, 0.805]**, decoys 16/16.
  Errors: the one-side "full name" is often the frequent litigant (an organisation, union, official, diocese, Ashcroft), so the unique
  full-name hit is another suit of the same party. **C9 NOT installed.** A cut (full name of the petitioner side only) would be designed
  on this audit's errors and the class has no fresh sample left -> not done (D9-11). shadow10_b (v10b.args + cert_wide) Lean run going
  for the record only.
- 04:55 shadow10_b (= v10b.args + cert_wide, binary 43efb994): 57 h10 C9 rows; remand_checked 316 failed 0. vs v10a/v10b status:
  Shadow Docket h0 recall 514 -> 518/1059, precision 92.0% -> 91.8% (518/564), **clean 43774 -> 43773 (-1)**; SCDB h0 part 44 -> 45/75,
  precision 1824/1870 -> 1824/1871; holdout notes history 5164/6264 -> 5164/6270 (+0 of +6). Clean drops and audit 0.702 -> C9 rejected.
  clean10 shadow10_b done (results kept). FINAL unchanged: cert_cap_b (C6) + cert_remand (D10-7) are the deltas; cert_wide NOT for staging.
