# Courts and decisions: validation (agent: courts, 2026-11-12)

The data covers 6,892,454 decisions (every node of `graph/nodes.tsv`, each exactly once). `text_sha` is present for all of them (0 missing).

Each file was read once from git (`git cat-file --batch`) in a single pass, run detached with 10 processes:
- 152 repos in 3,798 s, an aggregate of 1,815 files/s (per process 170–530 files/s).
- Throughput per repo is in `work/courts/logs/scan.log`.

## 1. Precision (reviewed headers)

- **Method:** every label was checked by reading the decision's header region (front matter, the first 2,200–3,000 characters of the body, and the last 500 characters).
- **Readers:** subagent readers, each given the same written brief (label definitions as in COURTS.md).
- **Samples:** drawn at random per predicted value.
- **Volume:** 817 headers in 5 rounds:
  - round 1: 433, every value;
  - round 2: 164, after the first rule fixes;
  - round 3: 85;
  - round 4: 40;
  - round 5: 95 (limit fixes, §5).
- **Formula:** precision = correct / (correct + wrong). "Unclear" verdicts (the header does not show the answer) are left out of the ratio.
- **Which round counts:** each value shows the round that tested the rule as shipped. Values with no fix after round 1 keep their round-1 figure.
- **Re-scored samples:** for equallyDivided, the round-3 and round-4 samples were re-scored under the final rule, which is deterministic: samples it now drops are excluded.

### bench

| value | count | precision (n) | round | note |
|---|---|---|---|---|
| panel | 3,293,353 | 93% (13/14) | 1 | default for appellate, BAP and appellate-division tiers |
| wholeCourt | 400,001 | 100% (8/8, 2 unclear) | 2 | 384,140 SCOTUS and 15,850 CCPA by rule; 11 from text |
| enBanc | 10,496 | 77% (17/22) | 3 | errors are mostly orders granting or denying rehearing en banc that list every judge |
| limitedEnBanc | 815 | 80% (8/10) | 3 | Ninth Circuit en banc on or after 1980 |
| division | 1,334 | 100% (12/12) | 1 | |
| conflictPanel | 100 | 60% (3/5) | 1 | Michigan; errors are the convening order or the original panel |
| circulated | 92 | 90% (18/20) | 2+3 | |
| unknown | 3,186,263 | – | – | state courts of last resort, trial and special courts with no header cue |

- **Evidence for enBanc and limitedEnBanc (11,311 decisions):**
  - front-matter `judges` says en banc: 4,106 (100% in samples);
  - 7 or more judges in the "Before" line of a federal circuit: 5,397 (100% in samples);
  - a strong caption line ("Argued and Submitted En Banc", "EN BANC", "sitting en banc", …): 1,310;
  - strict prose ("On rehearing en banc", "this case … heard en banc"): 498.

### publication

| value | count | precision (n) | round |
|---|---|---|---|
| published | 6,345,178 | 90% (27/30) | 1+2; the 1,648 OK/MN rows moved here from memorandum: 100% (15/15), round 5 |
| unpublished | 393,696 | 100% (40/40) | 1 |
| summaryOrder | 32,324 | 100% (10/10) | 1 |
| table | 50,755 | 93% (25/27) | 1+2 |
| memorandum | 4,356 | 93% (28/30) | 5, after the Oklahoma/Minnesota rule (§5); the 2 errors are a Vermont entry order and a Tax Court opinion citing T.C. Memo. |
| unknown | 66,145 | – | no status field, no banner, no reporter |

### form

| value | count | precision (n) | round |
|---|---|---|---|
| full | 4,631,326 | 90% (9/10) | 1 |
| perCuriam | 699,399 | 90% (18/20) | 1 |
| memorandum | 1,187,798 | 100% (10/10) round 1; short orders 100% (50/50) round 5 | 272,740 SCOTUS "memorandum order" from `decision_type`; 643,590 short orders outside SCOTUS (§5) |
| summaryAffirmance | 1,669 | 93% (14/15) | 2 |
| certifiedAnswer | 864 | 87% (13/15) | 3 |
| plurality | 199 | 77% (10/13, 2 unclear) | 3 |
| equallyDivided | 94 | 88% (21/24) | 3+4, re-scored |
| unknown | 371,105 | – | stubs under 600 characters with no form cue and no order language (162,692 have no opinion text at all) |

### unit (by source)

| source | decisions | precision (n) |
|---|---|---|
| court name | 61,229 | 100% (8/8) |
| docket pattern | 356,651 | 96% (24/25) |
| county or parish of origin | 361,182 | 100% (25/25) |
| judge-panel bootstrap | 326,497 | 100% (45/45) by reading; 97–99.96% hold-out agreement (below) |
| Fifth Circuit "Unit A"/"Unit B" in the header | 1,552 | 100% (6/6) |
| header phrase ("Second District" …) | dropped | 67% (10/15) in round 1, so not used |

**Judge-panel bootstrap.** Tokens from judge names (author, panel, "Present —" line) are mapped to units using decisions whose unit came from a direct cue. The mapping is built per family and per 10-year bucket, pooled with the neighbouring buckets. A token counts as a marker when it has at least 8 occurrences with at least 90% purity. A decision is assigned a unit when at least 80% of its marker votes agree; if more than one unit is voted for, the winner needs at least 2 votes. Leave-one-out agreement with the direct cues is in `work/courts/unit_holdout.tsv`:

| family | seeded | predicted | agreement |
|---|---|---|---|
| FL-DCA | 77,397 | 76,899 | 99.96% |
| MO-COA | 64,206 | 63,366 | 99.96% |
| TX-COA | 53,314 | 52,353 | 99.93% |
| WA-COA | 23,268 | 22,940 | 99.39% |
| IL-APP | 35,724 | 30,723 | 98.95% |
| NY-AD | 167,310 | 161,994 | 98.47% |
| CA-COA | 30,014 | 21,481 | 97.92% |
| AZ-COA | 14,890 | 14,047 | 97.91% |
| LA-COA | 43,334 | 38,450 | 97.48% |
| OH-COA | 17,356 | 15,140 | 96.72% |

**Rule changes made because of the review** (the precision above is for the final rules):
- wholeCourt: the Third Circuit footnote "not an opinion of the full Court" fired the cue; it now must refer to this case.
- memorandum publication: headings on federal and territorial trial-court opinions no longer count.
- plurality: a re-read of the header now requires "announced the judgment … delivered an opinion" and no "opinion of the Court (with respect to Parts …)".
- equallyDivided: the deciding court's own affirmance, in a short opinion or the opening of the opinion, with no quorum affirmance or mention of a lower court.
- certifiedAnswer: a federal certifying court and an answering phrase; acceptance-only orders are excluded.
- en banc: rehearing-denial and grant orders, amendment lines, citations and lower tribunals sitting en banc are rejected.
- unit: a unit dated before it existed is dropped (e.g. Texas "15th").

## 2. Counts per field value

| field | values |
|---|---|
| tier (courts2 epoch of each decision) | L 2,589,436 · A 3,284,847 · T 704,253 · S 280,642 · D 30,022 · B 3,254 |
| bench | see §1 |
| publication | see §1 |
| form | see §1 |
| unit ≠ 0 | 1,107,111 (16.1% of all decisions; 62.3% of the 1,773,757 decisions of unit-structured state intermediate courts, see §4) |
| court route (`src c:`) | self 4,102,204 · alias 2,189,628 · canonical 380,528 · era (date-split) 179,759 · fix 40,335 · unmapped 0 |

## 3. Mis-tiering fix

The audit (§5) found 184,794 appeals decisions tiered as trial or special. They are handled as follows:

| court (v2 epoch) | decisions | v1 → v2 |
|---|---|---|
| Texas Courts of Civil Appeals (to 1981-08-31) | 82,827 | T → A |
| Texas Courts of Appeals (from 1981-09-01) | 54,459 | T → A |
| Texas Court of Appeals 1876–1891 (now the first epoch of the Court of Criminal Appeals) | 4,693 | T → L (criminal) |
| Alabama Court of Criminal Appeals (both name spellings) | 19,208 | T → A |
| Massachusetts Appeals Court | 14,433 | T → A |
| Tennessee Court of Criminal Appeals | 3,085 | T → A |
| **re-tiered from the audit group** | **178,705** | |
| Texas Commission of Appeals (4,679) and New York Commission of Appeals (866) | 5,545 | kept S (commissions); their authority comes through `adoption.tsv` (H4) |

(The counts differ slightly from the audit's because the v2 epochs also take in the variant spellings.)

All tier changes from v1 to v2 total 240,038 decisions:
- T → A: 178,428
- A → D: 30,022 (NY Appellate Term, Massachusetts Appellate Division, California appellate division, general terms of trial courts)
- T → L: 10,985 (Hawaii territorial, American Samoa, Virgin Islands, Dakota, Northern Mariana Islands, Texas 1876–91)
- L → A: 8,579 (NY Supreme Court of Judicature; pre-1971 D.C. Court of Appeals; old NJ Supreme Court before 15 Sept 1948)
- A → L: 5,582 (South Carolina Court of Appeals 1824–68; Indian Territory; Special Court of Appeals of Virginia)
- S → B: 3,254 (bankruptcy appellate panels)
- T → S: 2,467 (military Courts of Criminal Appeals; tribal and unmapped names)
- S → L: 717
- L → T: 4

Court-id checks:
- **SCOTUS:** all 384,140 SCOTUS decisions get court_id 2906, the v1 SCOTUS id.
- **Id changes:** court_id differs from `lean-in-v3/decisions.tsv` for 360,174 decisions (312 id pairs). Every change is explained by a row in `court_alias.tsv` (0 unexplained).

## 4. Unit recovery per intermediate court family

| family | decisions | with unit | sources |
|---|---|---|---|
| AZ Court of Appeals (2 divisions) | 15,081 | 100.0% | docket 14,767 · name 231 · judges 80 |
| WA Court of Appeals (3 divisions) | 65,107 | 99.1% | docket 58,015 · county 3,789 · judges 2,317 · name 409 |
| MO Court of Appeals (E/W/S, incl. pre-1972 courts) | 97,879 | 90.2% | docket 36,956 · name 28,266 · judges 23,020 |
| LA Courts of Appeal (5 circuits) | 115,800 | 73.8% | judges 41,876 · docket 30,202 · parish 11,413 · name 1,952 |
| OH Courts of Appeals (12 districts) | 48,000 | 66.6% | county 15,552 · judges 14,549 · name 1,871 |
| NY Appellate Division (4 departments) | 719,090 | 61.4% | county 317,210 · judges 124,052 |
| IL Appellate Court (5 districts) | 124,870 | 60.6% | judges 39,819 · docket 30,455 · Cook County 5,425 |
| FL DCAs (6 districts) | 265,415 | 59.9% | docket 87,642 · judges 46,278 · name 24,977 |
| IN Court of Appeals (5 districts) | 45,163 | 55.8% | docket 25,060 · judges 156 |
| CA Courts of Appeal (6 districts) | 99,718 | 54.9% | judges 23,956 · docket 21,211 · county 7,500 · name 2,051 |
| TX Courts of (Civil) Appeals (15) | 138,847 | 45.4% | docket 52,343 · judges 9,423 · name 1,244 |
| OK Court of Civil Appeals (4 divisions) | 4,853 | 7.8% | judges 254 · name 124 |
| TN Court of Appeals / CCA (grand divisions) | 9,240 / 3,085 | 5.9% / 0.1% | name, judges |
| NY Appellate Term | 21,609 | 2.6% | county, judges |
| Former Fifth Circuit Units A/B (1980-10-01 to 1982-12-31) | – | 1,552 decisions | header |

For comparison, the audit sample recovered: AZ 100, WA 88, MO 56, OH 53, NY 46, FL 40, IN 39, CA 33, TX 62 (including noisy city cues, not used here), LA 17 and IL 10 percent.

## 5. Fixes to validated limits (2026-11-12, `tools/caselaw2/limits_fix.py`)

The fixes are applied to the built files. Each rewritten file was written as `.tmp` and renamed; the originals are kept as `*.pre_fix.tsv` (decisions2, courts2, court_alias, succession, adoption, system_rules, history).

**8. Uncertain dates.** 19 web searches (budget 25), primary sources first:

| item | was | now | tag | source |
|---|---|---|---|---|
| CT Supreme Court of Errors → Supreme Court | 1965-12-30, U | 1965-12-30 | S | Conn. Const. (1965) art. XIV; proclaimed by the governor 1965-12-30 |
| DE Court of Errors and Appeals | "last resort until 1951" | abolished by the 1897 constitution (its decisions end in 1897); succession 609 → 610 dated 1897-06-10 | U (day) | Delaware Public Archives |
| DE separate Supreme Court | 1951-01-01, L | 1951-05-14 | S | Del. Const. art. IV § 35 (48 Del. Laws c. 109) |
| OK Criminal Court of Appeals → Court of Criminal Appeals | 1959-01-01, U | 1959-03-11 | L | 20 O.S. § 31.1 history note (Laws 1959 p. 107, emergency clause); session law not seen |
| IN Appellate Court → Court of Appeals | 1972-01-01, U | 1972-01-01 | S | in.gov court history (amendment ratified 1970-11-03) |
| CA District Courts of Appeal → Courts of Appeal | 1966-11-08, U | unchanged | U | Prop. 1-a adopted 1966-11-08; effective day not confirmed |
| PR Tribunal de Circuito → Tribunal de Apelaciones | 2003-07-01, U | 2003-11-20 | S | Ley 201-2003 art. 9.004 (90 days after 2003-08-22) |
| AR Rule 5-2 (all opinions precedent) | 2009-07-01, U | unchanged | S | 2009 Ark. 330 (per curiam, 2009-05-28) |
| OH reporting rules | 2002-05-01, U | unchanged | L | Rep.Op.R. 4 (2002), renumbered 3.4 in 2012; secondary sources |
| FRAP 35 → restyled FRAP 40 | "check date" | 2024-12-01 (src only) | – | S. Ct. order of 2024-04-02 |
| Guam: 9th Cir. certiorari ends | to 2004-10-29 | unchanged (src) | U (weight) | Pub. L. 108-378 § 2, approved 2004-10-30 |
| CNMI: 9th Cir. review ends | no row | new adoption row to 2004-05-01 | U | 48 U.S.C. § 1824(a) 15-year sunset; Pub. L. 108-378 does not cover the CNMI |
| TRAP 41.3 | – | unresolved (2008 amendments; believed 2008-09-01) | – | no row depends on its date |

Decisions whose epoch changed (same court id and tier): Puerto Rico 68 (2003-07-01 to 11-19), Oklahoma CCA 25 (1959-01-01 to 03-10), Delaware Supreme Court 5 (1951-01-01 to 05-13).

**9. Texas "writ refused".** All 2,288 `writRefused` rows were checked against their certificate windows. 2,287 were the Louisiana Supreme Court's "Writ refused." on Louisiana court-of-appeal judgments (often "On the facts found by the Court of Appeal, there is no error of law"), a refusal to review, not the Texas notation. They are now kind `other`, id `h:<by>:<target>:other`, src `…;relabel:other(...)`. The one Texas row (Texas Supreme Court, 1933, "Writ of error refused.") stays `writRefused`. No row was followed by "n.r.e.", so none was dropped. The reader now labels `writRefused` only for the Texas Supreme Court's "writ refused" / "writ ref'd", drops "n.r.e." / "no reversible error", and never maps "writ denied" / "writ dismissed" to it (`reader/scan.py` k7, `reader/resolve.py`).

**10. Oklahoma and Minnesota "MEMORANDUM OPINION".** Rule: in systems 36 and 23 the heading is not a publication channel, and the form is `full` when the opinion has at least 600 characters. 1,648 decisions publication memorandum → published (by front matter); 1,567 form memorandum → full. Review: the moved rows 100% (15/15, all full opinions in P.2d or N.W.2d); the remaining 4,356 memorandum rows 93% (28/30), up from 78% (14/18).

**11. Courts and systems.**
- The 8 unmapped decisions now have courts: 10109 Department of the Interior (6), 10110 Salina land-office register (1), 10111 Judge's Chambers (*Ex parte Rhodes*, 1816; state not identified, system 999, U). `court_alias.tsv`: 3 routes `unmapped` → `fix:unmapped name (limit 11)`; decisions2 src `c:unmapped` → `c:fix` (route counts: fix 40,335, unmapped 0).
- Tribal: 48 court rows moved from system 61 to one system per tribe, 1000–1022 (COURTS.md table). Pueblo County District Court (579, 7 decisions) was not tribal: it is a Colorado trial court (system 6, tier T).
- Military: 6 adoption rows, CAAF (650) binding on the Army, Navy-Marine Corps, Air Force and Coast Guard Courts of Criminal Appeals, the Navy Court of Military Review and the collective Courts of Military Review (10 U.S.C. §§ 866–867; L).

**13. Short orders.** `orders_scan.py` read the opinion text of the 966,109 decisions outside SCOTUS whose form was unknown. 643,590 have order language in under 1,500 characters and are now form `memorandum` (src `f:order-lt1500`). Review of 50 at random: 100% (50/50; affirmances without opinion, writ and motion denials, dismissals, short ORDERs). 322,519 stay unknown outside SCOTUS (162,692 with no opinion text); with SCOTUS stubs, 371,105 in all. The candidates were mostly New York (375,868), Louisiana (122,784, largely writ denials), Florida and federal courts.

## 6. Label fix 2 (2026-11-12, `tools/caselaw2/labels_fix2.py`): publication against the reporter, bench re-read

Source: `hunt/HUNT.md` "What to fix" 1 and 3. Applied after `limits_fix.py`; the input is kept as `decisions2.pre_pubfix.tsv`. The counts in §1 are the counts before this fix; the current ones are below.

### Publication

**What the hunt counted.** 77,575 non-published rows with a "printed reporter" citation. That class was "anything that is not F. App'x, a database cite or no cite", so it held:
- 50,512 Florida PCAs without opinion (So. 2d / So. 3d, under 300 characters): correctly `table`, kept;
- about 11,600 T.C. Memo. / T.C. Summary Op. decisions: correctly unpublished, kept;
- 15,364 decisions cited in a reporter of published opinions: the candidates of this fix (re-read from git, `work/courts/pub2.tsv`).

**Result on the 15,364 candidates: 7,342 changed to published, 8,022 kept.**

| old value | → published | kept | what was kept |
|---|---|---|---|
| unpublished | 4,550 | 6,190 | Illinois abstracts "Not to be published in full" (5,145), Hawaii summary disposition orders, Alabama "affirmed by unpublished memorandum", Rule 23 / "no precedential value" dispositions |
| memorandum | 2,575 | 1,752 | Indiana "Unpublished Memorandum Decision" entries, Vermont and Delaware entry orders, Hawaii memorandum stubs, Missouri Rule 84.16(b) / 30.25(b), stubs under 600 characters |
| table | 168 | 75 | South Dakota "Unpublished Disposition" entries (74), one Florida table entry |
| summaryOrder | 49 | 5 | Missouri stubs |

The main causes of the 7,342 errors: in federal reporters (2,317 with sentence evidence), mostly "Rule 23(b)" in class-action opinions read as a non-publication rule, and opinions that discuss the citation rules for unpublished decisions; in Illinois (1,260), mostly a published opinion citing an "(unpublished order under Supreme Court Rule 23)"; a "MEMORANDUM OPINION/DECISION" heading on a published opinion (Utah 774, Texas 647, New Hampshire 378, Pennsylvania 144, Tax Court T.C. 150, …); "(table)" in a citation (168); Indiana decisions later ordered published (180).

Values after the fix: published 6,352,520 · unpublished 389,146 · table 50,587 · summaryOrder 32,275 · memorandum 1,781 · unknown 66,145. Non-published labels: 481,131 → 473,789.

**Blind review.** 132 decisions, shuffled, 11 per reader, 12 Claude subagent readers. Each reader saw the case name, citations, court, date and the first 6,000 and last 2,500 characters, not the label and not whether the row had changed. Intervals are Wilson 95%.

| sample | n | label agrees with reader | precision (95%) |
|---|---|---|---|
| changed to published (random of 7,342) | 66 | 66 | 100% (94–100%) |
| reporter-cited, kept non-published (random of 8,022) | 33 | 33 | 100% (90–100%) |
| unchanged non-published, all (random of 465,767) | 33 | 32 | 97% (85–99%) |

The one disagreement is a rule this fix does not touch: a Florida DCA per curiam dismissal of under 300 characters that cites an authority (164 So. 3d 783) is `table` by the PCA rule; the reader calls it published.

### Bench

**Scope.** 15,690 decisions re-read from git (`work/courts/bench2.tsv`): the treating decisions of `treatments.tsv` with kind overruled / disapproved / recededFrom, plus the citing decisions of `hunt/data/p3_panel.tsv`. Only rows with bench panel or unknown can change (14,976); SCOTUS never.

**Result: 900 changed.**

| change | decisions |
|---|---|
| panel → enBanc | 779 |
| panel → circulated | 112 |
| unknown → enBanc (state court of last resort with an "En Banc" caption) | 9 |

| evidence (`b:fix2:…`) | decisions |
|---|---|
| judges lines name ≥ 5 judges (panels-of-three courts) or ≥ 7 (other tier A/B/D) | 580 |
| circulation footnote | 112 |
| self-referring prose anywhere ("Sitting en banc, we …", "we ordered rehearing en banc") | 58 |
| "All the Judges concur" (state intermediate courts) | 51 |
| en banc in the first 1,500 characters (caption 33, prose 28) | 61 |
| en banc in the last 1,500 characters (caption 16, prose 18) | 34 |
| front-matter judges say en banc | 4 |

Values after the fix: panel 3,292,462 · unknown 3,186,254 · wholeCourt 400,001 · enBanc 11,284 · limitedEnBanc 815 · division 1,334 · circulated 204 · conflictPanel 100.

**Against the hunt's sets.**
- Second-read labels (`hunt/work/p3b_out.jsonl`, 344 decisions, all labelled panel before): of 161 the reader called en banc, 123 are now enBanc (76%); of 167 it called panel, 158 stay panel and 9 are now circulated (the reader's own justification for all 9 is "circulated to full court"); none became enBanc. 16 unclear stay panel.
- Audit sheets (`hunt/audit/p3`, `p3b`, 67 decisions): en banc or full court 17 of 22 found; panel 40 of 45 stay panel and 5 are circulated (all 5 circulation footnotes); 0 false enBanc.
- The 38 en banc decisions still labelled panel: the court had three judges, so the panel was the whole court (Texas courts of civil appeals, early federal circuits, the pre-1971 D.C. court), Alabama's two appellate courts, which always sit as a full court, Louisiana five- and six-judge benches, and decisions with no judges line. The text does not say en banc in any of them; they need a court-size rule, not a text rule.

**Fresh blind review.** 40 decisions (30 changed, 10 unchanged panel candidates), shuffled, 4 Claude subagent readers; each saw the judges line, the first 4,000 characters, the passages around en banc / full court / circulated, and the last 3,000 characters.

| sample | n | agrees | wrong | unclear | precision (95%) |
|---|---|---|---|---|---|
| changed (enBanc or circulated) | 30 | 30 | 0 | 0 | 100% (89–100%) |
| unchanged panel | 10 | 7 | 2 | 1 | 78% (45–94%) |

The 2 misses among the unchanged: a Georgia Court of Appeals whole-court decision whose judges are named only at the end of the text (no judges line), and a California Supreme Court decision filed under the Court of Appeal (a court-routing error, not a bench error). So recall on overruling decisions is still incomplete: roughly one in four en banc decisions in this set is still labelled panel.

Review sheets, key and scoring script: `work/courts/verdicts/fix2/`.

## 7. Round 2 (agent courts, 2026-11-12): epoch bounds and the three rule dates

Scripts: `tools/caselaw2/epochs_fix.py`, `tools/caselaw2/rule_dates_fix.py`. Rules and sources: `COURTS.md`, the two "Round 2" sections. Log and reference-run triage: `round2/courts.md`. Originals: `data/*.pre_round2.tsv` (courts2, succession, adoption, system_rules).

**Checks on `courts2.tsv`** (3,106 rows, all with 11 fields, LF):
- decisions dated outside every row of their court: 0 before, 0 after (6,892,454 decisions, none undated). The existing multi-epoch rows did not violate this.
- court ids starting after 0: 86 → 2,671; court ids with an end: 7 → 168.
- 88 cluster rows cover 839 decisions dated after their court's end (47 courts; `work/round2/courts/epoch_clusters.tsv`). Largest: Court of Claims 486, Supreme Court of the Republic of Hawaii 88, Kansas Court of Appeals (1895–1901) 80, Alabama Court of Appeals 21.

**Dates checked** (4 web searches of 8; the decisions themselves were read in the corpus):

| item | result | tag |
|---|---|---|
| Ohio within-district rule | starts 2008-10-02 (*McFadden*), not 2010-07-01 (App.R. 26(A)(2), the procedure) | S |
| Louisiana within-circuit rule | no source gives 1997; statements go back to 1985-03-12 (4th Cir.); date kept at 1997-01-01 (an earlier start loses 15 status rows through missing units) | U (was S) |
| Federal en banc statute | 1948-09-01 confirmed (*Ex parte Collett*; *Western Pacific*) | S (was L) |
| Federal Circuit established | 1982-10-01 confirmed (*South Corp.*) | S (was L) |

## 8. Bench by court size (agent enbanc, round 2, 2026-11-12, `tools/caselaw2/bench_size_fix.py`)

**Scope.** 19,478 overruling decisions of tiers L and A (kinds overruled, disapproved, recededFrom, declinedToFollow, plus `hunt/data/p3_panel.tsv`). Size table: `data/court_size.tsv`, 218 courts, 17,474 court-years, from a sample of 939,751 decisions.

**Result: 3,817 changed.**

| change | decisions |
|---|---|
| unknown → wholeCourt (courts of last resort) | 3,605 |
| panel → wholeCourt (size ≤ 3 or a full-court year) | 172 |
| panel → enBanc | 40 |

By family of the 212 intermediate-court changes: Alabama 74, other state courts 118, federal circuits 15, Louisiana 5.

**Blind review** (one round, before the apply). 60 decisions, shuffled, 4 Claude subagent readers, 15 each. Each saw the court, date, citation, judges lines, the first 3,000 and last 1,500 characters. They did not see the old label, the new label, the stratum or the size table. Intervals are Wilson 95%.

| sample | n | full court (whole or en banc) | not | unclear | share (95%) |
|---|---|---|---|---|---|
| relabelled, all | 30 | 29 | 1 | 0 | 97% (83–99%) |
| relabelled, intermediate courts | 25 | 24 | 1 | 0 | 96% (80–99%) |
| – federal circuits | 6 | 6 | 0 | 0 | 100% (61–100%) |
| – Alabama | 6 | 6 | 0 | 0 | 100% (61–100%) |
| – Louisiana | 5 | 5 | 0 | 0 | 100% (57–100%) |
| – other state intermediate | 8 | 7 | 1 | 0 | 88% (53–98%) |
| relabelled, courts of last resort | 5 | 5 | 0 | 0 | 100% (57–100%) |
| left as panel (overruling, intermediate) | 20 | 1 | 17 | 2 | 6% (1–26%) |
| enBanc before this fix | 10 | 9 | 1 | 0 | 90% (60–98%) |

- The one wrong relabel: Arizona Court of Appeals, Division Two, three of three division judges. A division is not the court. Arizona, Washington, the Oklahoma Court of Civil Appeals, Indiana and Tennessee were then excluded (16 relabels dropped). No second sample was drawn; on the 29 remaining reviewed relabels the share is 29/29 (88–100%).
- The one full court left as panel: Louisiana First Circuit 1935, a three-judge court; the text names only the author and the dissenter.
- The one wrong enBanc label: a Michigan seven-judge conflict panel (it should be conflictPanel).
- The family samples are small (5 to 8 each), so the per-family intervals are wide.

**Full-court decisions labelled panel** (overruling decisions of intermediate courts: 212 relabelled, 4,635 left panel, 1,161 enBanc before). Estimated from the three samples: 31% before → 17% after. The interval is wide because only 18 left-as-panel decisions were scored: with the left-as-panel rate at its 95% bounds (1% and 26%) the figure is 19% → 4% or 57% → 49%.

**Against the hunt's second read** (`hunt/work/p3b_out.jsonl`, 161 decisions the reader called en banc): 123 labelled enBanc before, 135 enBanc or wholeCourt after (84%). Of the 26 left, most name only the author; the rest are Louisiana five-judge panels, OCR-damaged names and vacancies. Of the 167 it called panel, none changed.

**Effect on the reference engine** (same engine version, private copies `work/round2/enbanc/data_before`, `data_after`): `panelDepartsWithoutEnBanc` 677 → 543; status rows 69,384 → 69,734; all findings 142,365 → 142,211.

Sheets, key, verdicts and scoring: `work/round2/enbanc/audit/r1/`, `audit/make_sheets.py`, `audit/score.py`.
