# shadow11 NOTES

- 05:13 start. Read BRIEF, DESIGN11 §0/§4, COMMON. Disk 24G free. No INFRA_READY/NODES_READY yet; data_orders empty.
- 05:16 read shadow10 NOTES/cap10/build10, rules9, memo orders.py. Wrote olink11.py (C6 port over an order spec: caption normaliser for order-list 'SURNAME, GIVEN' style, kind/courts from the node's own text). Testing on corpus 2010-19 GVRs.
- 05:24 **olink11 test (part A port) on corpus GVR orders 2010-19 (712 specs; text = caption line + the order's own words):**
  reporter captions: round-10 C6 links 283/283 reproduced (0 lost, 0 other) + 8 extra links where the memo parse resolved the
  court only as ('ca','*') (its remand-to regex cut "United States Court of Appeals | for the Eleventh Circuit"); olink11's
  remand-clause regex takes the whole court name. Synthetic order-list captions ("SURNAME, GIVEN V. ..."; norm_caption ->
  reporter style): 280/283 (+1 new); the 3 lost are artifacts of my synthetic converter on mixed-case org names.
  Court only from the remand clause / "judgment of" (as an order list prints it): 267/283; the 16 lost are U.S.-Reports-style
  texts that say "C. A. 10th Cir. ... remanded for further consideration" without naming the court (order lists name it).
- 05:24 part B design (from shadow10 NOTES failure descriptions + corpus text only; r10k02/03 items not opened):
  sub-rule C10 = natural-person side (given + surname; no organisation/office words; no office designation chunk such as
  ", Warden" / ", Attorney General"), person-name match in the text head allowing middle names / "Surname, Given" order,
  uniqueness over a WIDE pool (every decision of the court below in 1..1,095 d whose title holds the surname, not only the
  both-sides candidates: a frequent litigant's name is then never unique), the unique one must be a both-sides candidate,
  no sibling, and a date tie to the order's own docket number (T dated before the end of the docket's term year).
- 05:25 build11.py written (rows from data_orders nodes.tsv/text via olink11; node ids via nodes11 or N0+file order per FORMAT.md; nodes duplicating a corpus SC order (docket+date) skipped). narrow11.py cand running.
- 05:27 narrow11.py cand: GVR orders (one court, one caption) 3,877; natural-person side 640 (3,237 have none:
  "Smith v. United States" style, or organisation / official parties); wide pools 451 orders, 6,630 heads read.
  agree (non-key truths = Reported below / bridge strings / list rows; base = v10d history):
  C10 (pool-unique person match, both-sides, no sib, term-year date): linked 247, new 4 (prec 56/57).
  V4 (pool-unique, no both-sides requirement): new 26, 62/63. **C11 = V4 + no sibling + dated before the end of the
  order's docket term year: linked 273, base same 249, base other 2, new 22 (post-2013 18), truths 62/63 (not-C6 8/8).**
  h0 diagnosis of the 22 new targets (h0-only file): NEG/gvr|vacated model GOOD 6, NEG_HIST already 1, CLEAN/cert_denied 1
  (likely another suit of the same person), not h0 14.
- 05:27 buildc11.py -> rows_c11.jsonl: 21 rows (vacated 21, post-2013 17; 1 refused no name evidence). Waiting for
  INFRA_READY to certify; audit = whole class (21 + decoys, fresh; r10k01-03 never sampled from C11 by construction: new rows only).
- 05:30 olink11 remand-bridge port (round-9 K9 v2 over an injected order: T by caption token, B on T's docket
  0..1,826 d after, signals from B's text + B's out-edges; rules9.pick K9 JOIN+SURNAME): corpus GVR 2010-19 vs round-9
  k9_links_v2: with O's page cites through the graph (as round 9) 261/261 same + 8 new (court-name fix); without them
  (what an order-list node has: no cite, no out-edges) 241/261 (20 rested on citeBO / graph reason only) + 7 new.
  build_tokidx() rebuilds the (court, token) index for the new nodes' caption tokens/courts (round-9 index covers only
  corpus GVR captions). INFRA_READY seen.
- 05:30 certify11 rows_c11 -> cert_c11/: 20 admitted (1 orderHeadNotAllowed). Audit r11k01 = whole class (20 + 3 decoys, 1 pack, --exclude r10k01-03 samples), 2 opus auditors running. Staging shadow11_b = v10d + cert_c11.
- 05:33 **audit r11k01 (class C11, whole class 20 + 3 decoys, fresh, --exclude r10k01-03): right 17/20 = 0.850
  [0.640, 0.948]** (link same), decoys 6/6, reader agreement 22/23. Strata: 2010s 17/18, 1970s 0/1, 2020s 0/1. Below the
  0.90 bar -> **C11 NOT installed**; the whole class is read, so no cut can be re-audited on a fresh sample (D9-11): stop.
  Errors not opened item by item (score.md counts only: 'link' failures).
- 05:33 part A pipeline test: mk_synth.py (12 corpus C6 orders rewritten as order-list nodes: date heading,
  "docket SURNAME, GIVEN V. ..." caption, disposition) -> build11.py --keep-dup -> 12/12 rows olist-C6 (K9 agrees on 5).
- 05:33 gap11.py written (h0-only diagnosis of the gap orders vs nodes/links). certify11 --nodes on the synthetic rows: 12/12 admitted (targets = round-10 C6 targets 12/12). Lean shadow11_b queued (two other runs active). Monitor on data markers armed.
- 05:37 lead: make_packs11 --exclude of round-10 samples matched nothing (h10 vs h11 ids). Overlap by (by, target):
  C11 rows vs round-10 classes: C2 (cert_cap_a) 0, C6 0, **C9 (cert_wide) 8 -> all 8 in r10k03's sample** (r10k01/02: 0).
  So r11k01 is fresh on 12 items only: fresh 10/12 = 0.833 [0.552, 0.953]; overlap items 7/8. Either way below 0.90:
  C11 stays NOT installed (no change of decision). The overlap is expected: C11 is C9 narrowed (person side, no office).
- 05:45 shadow11_b (= v10d + cert_c11, NOBUILD) scored noold, for the record only (C11 not installed): Shadow h0
  recall 514 -> 519/1059 (48.5% -> 49.0%), precision 92.0% -> 91.9% (519/565), **clean 43774 -> 43773 (-1)** (the CLEAN/cert_denied
  target foreseen in the h0 diagnosis); holdout notes history 5204/6305 -> 5204/6307 (+0 of +2); SCDB/FJC/state/dev unchanged.
  clean11 shadow11_b done (results kept). Disk 20G free. Waiting for order-list data.
- 05:48 NODES_READY seen; data_orders still has no nodes.tsv.
- 05:54 DATA_READY_PARTIAL: 980 nodes (2006-09, 2020-25; Journal style, title-case captions), nodes11 --check ok. Running build11.
- 05:56 build11 on the partial data -> rows_olist_p.jsonl: **431 rows (olist-C6 395, olist-K9 36; all vacated;
  scope unknown 32)**. Nodes 980: in corpus 2, not GVR kind 11, no disposition parsed 30, not one court 3, no both-sides 310,
  not unique 182, C6/K9 disagree 8 (no row), no name evidence 1. Gap diagnosis (h0-only): 286 h0 NEG/PART cases whose order
  is not in the corpus -> linked to the h0 decision 188, linked elsewhere 1, no node 10, node not linked 87 (no both-sides 43,
  not unique 39, rules disagree 4, no disposition 1).
- 05:57 certify11 --nodes -> cert_olist/: 431/431 admitted. Audits: r11k02 = olist-C6 (395; 80 + 9 decoys, 3 packs), r11k03 = olist-K9 (whole 36 + 4 decoys); 8 opus auditors running. Staging shadow11_c = v10d + cert_olist --nodes.
- 05:57 DATA_READY: same 980 nodes and bytes as the partial -> rows/cert unchanged. shadow11_c Lean run started; auditors r11k02 p1a/p1b/p3a done.
- 05:58 **audit r11k02 (olist-C6 on order-list nodes, population 395; 80 + 9 decoys, 3 packs, --nodes)**: right
  **80/80 = 1.000 [0.954, 1.000]** (link, effect, extent same; corpus-weighted 1.000 [0.962, 1.000]); decoys 18/18; readers agree
  89/89. Passes.
  **audit r11k03 (olist-K9 remand bridge on order-list nodes, whole class 36 + 4 decoys)**: right **35/36 = 0.972 [0.858, 0.995]**
  (1 'link' failure); decoys 8/8; readers agree 40/40. Point estimate passes the ~0.90 bar (interval lower bound 0.858).
  Both classes installable: delta cert_olist (431 rows) with --nodes round11/data_orders.
- 06:03 **shadow11_c (= v10d + cert_olist, --nodes round11/data_orders; NOBUILD): all 431 h11 rows ok.** vs v10d:
  Shadow Docket h0 recall **514 -> 684/1059 (48.5% -> 64.6%)**, precision 92.0% -> 93.3% (684/733), clean 43774 -> 43771 (-3);
  SCDB h0 clean 1998 -> 1997/2052 (-1), recall unchanged; holdout notes history 5204/6305 -> 5204/6314 (+0 of +9), precedent
  byAnyone 941 -> 945; fresh dev / Shepardized dev / FJC / state tables unchanged. clean11 shadow11_c done (results kept).
- FINAL: delta round11/agents/shadow11/cert_olist (431 rows: olist-C6 395 r11k02 80/80, olist-K9 36 r11k03 35/36), staged with
  --nodes round11/data_orders; no --remove. NOT for staging: cert_c11 (r11k01 0.850). Gap orders (h0 NEG/PART not in corpus,
  286): linked right 188, other 1, no node 10 (2005/2010/2015 orders, and 5 of 2020), node unlinked 87 (no both-sides caption
  candidate 43, several full-name candidates 39, C6/K9 disagree 4, no disposition parsed 1).
- 06:04 lead follow-up (D11-10 installed cert_olist): run olist-C6/K9 on the nodes orders11b appends (DATA_READY2), cert_olist2 new rows only, own audit, effect on lead/v11b.args; deadline 06:30 for the marker. Saved the 980 first-batch local ids (work/olist1_ids.txt).
- 06:24 DATA_READY2: 1,045 nodes (first 980 unchanged, verified); building olist2 on the 65 new nodes only.
- 06:25 olist2: 65 new nodes -> 28 rows (C6 27, K9 1; 2010 1, 2020 4, 2026 23); 1 in corpus, no both-sides 21, not unique 15. certify11 --nodes -> cert_olist2/ 28/28 admitted. Audit r11k04 = whole class (28 + 4 decoys, --exclude r11k02/03), 2 opus auditors. Staging shadow11_d = v11b.args + cert_olist2.
- 06:25 gap diagnosis olist2: of the 10 gap cases with no node before, 8 now have a node: 4 linked right, 4 unlinked (not unique 3, no both-sides 1); 2 still without a node (2005, 2006). shadow11_d stage/run/score running in background.
- 06:26 **audit r11k04 (olist2, whole class 28 + 4 decoys, excl. r11k02/03): right 27/28 = 0.964 [0.823, 0.994]**, decoys 8/8, readers agree 32/32. Passes the point-estimate bar. shadow11_d Lean run in progress.
- 06:28 **shadow11_d (= lead v11b.args + cert_olist2; NOBUILD; all 1,197 h11 rows ok) vs round11/results/v11b:** Shadow
  Docket h0 recall 684 -> **688/1059 (64.6% -> 65.0%)**, precision 93.2% (688/738), clean 43770 unchanged; every other line of
  the summary identical. clean11 shadow11_d done. FINAL follow-up: delta round11/agents/shadow11/cert_olist2 (28 rows, olist-C6 27
  + olist-K9 1; audit r11k04 27/28 = 0.964 [0.823, 0.994]); stage with --nodes round11/data_orders (1,045 nodes).
