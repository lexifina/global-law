# Loophole and mistake hunt over US case law

**Summary.** Six patterns were searched over the corpus (6.9 million decisions, 191,045 runner findings), each first
checked against known cases, then run, then blind-audited by Claude subagents reading the decision text. The five
strongest findings: (1) **courts still apply overruled Supreme Court law**: *In re Odyssey Healthcare*, 310 S.W.3d 419
(Tex. 2010) applies the *National League of Cities* test 25 years after *Garcia* overruled it, and *United States v.
Helsey*, 463 F. Supp. 1111 (D. Mont. 1979) rests on *Hammer v. Dagenhart*, overruled in 1941; across the corpus we
estimate 1,800 to 4,200 such unacknowledged reliances on negated decisions, and the two-reader pattern is right 86% of
the time (19 of 22, 95% interval 67-95%). (2) **Our own data mislabelled 7,342 reporter-printed decisions as not
published** (first reported here as 77,575; see section 2); every audited "unpublished opinion treated as binding"
report (0 of 20) was this error, which also sat under the runner's `citesNotCitable` findings (38,803 then, 5,701
after the label fix). (3) **Lower courts keep citing the losing side after the Supreme
Court resolves a split**: *United States v. Armstrong*, 550 F.3d 382 (5th Cir. 2008) requires an overt act for a
§ 1956(h) conspiracy three years after *Whitfield*; 12 instances confirmed. (4) **Panels do overrule panels**: 18
confirmed, among them *Tarrant Appraisal Dist. v. Tarrant Reg'l Water Dist.*, 547 S.W.3d 917 (Tex. App. 2018), but the
runner's 1,960 `panelDepartsWithoutEnBanc` findings are mostly en banc decisions and circulated opinions (first-read
precision 10%). (5) **The rules themselves turn on one day and one forum**: a Fifth Circuit decision of 30 Sep 1981
binds the Eleventh Circuit and one of 1 Oct 1981 does not, and it stays binding there after the Fifth Circuit en banc
overrules it (37 such overrulings, 63 later Eleventh Circuit citations, 10 of which our runner wrongly reports as
citing overruled law).

Numbers for the report generator: `hunt/summary.json`. Predicates: `LegalProofs/CaseLaw2/Hunt.lean` (compiled).

## Method and readers

As in the tax-code loophole work: recreate known mistakes, run the validated pattern, blind-audit.

- **Candidates** come from the runner (`out/findings.tsv`, `out/status.tsv`, `out/splits.tsv`), the gold tables and the
  citation edges. The citing passage (± 900 characters around each citation) is read from the git objects.
- **Readers.** Two, labelled in every `work/*_out.jsonl` row (`model`):
  - `azure gpt-5.4-mini`: the first pass before the hand-over (pattern 1: 5,389 rows; pattern 2: 1,598; pattern 3:
    1,860; split sides: 394). Kept, not extended.
  - `claude-subagent`: everything after (pattern 2 remainder 602, pattern 4 all 799, pattern 5 all 725, second reads
    of patterns 1, 2 and 3: 466 + 256 + 409) and every audit. No external model was called after the hand-over.
- **Blind audit.** Per pattern, about 20 reported instances at random, the candidates for the top list, and decoys the
  pattern did not report, shuffled, 7 per auditor. The auditor gets the decision text (the negating decision's own
  passage for pattern 1), not the first reader's verdict, and answers limb by limb. Intervals are Wilson 95%.
  No decoy was confirmed in patterns 1, 2, 4 and 5 (0 of 42); pattern 3 is the exception (below).
- **What the audits changed.** The first reader was too generous in patterns 1 and 3. A second read with the
  negating court's words (pattern 1) and the judges line and circulation footnotes (pattern 3) raised precision from
  20-40% to 86% and from 10% to 64%. Both precisions are reported; the second is the pattern's.

| pattern | candidates | reported | audit precision (95%) | recall on known | confirmed |
|---|---|---|---|---|---|
| 1 zombie precedent | 73,568 | est. 1,815-4,184 | 19/22 = 86% (67-95%), two readers; first reader alone 4/20 and 4/10 | 21/42 literature overrulings marked negative (50%); 0/3 later-court call-outs | 30 |
| 2 unpublished as binding | 2,880 | 375, then 2 | 0/20 (0-16%); refined 1/2 | known case cites a decision not in the corpus | 1 |
| 3 panel overrules panel | 1,869 | 409, then 58 | 14/22 = 64% (43-80%), two readers; first reader alone 2/20 | 0/2 (second read against audit-confirmed) | 18 |
| 4 two-date error | 13,605 | 26 (runner), 2 (reader) | runner 0/20 (0-16%); reader 1/2; unsettled candidates 2/24 | runner's 26 are not instances | 3 |
| 5 losing side after resolution | 6,506 | 35 of 725 read | 6/20 = 30% (15-52%); top list 6/12 | 164/304 losing-side labels confirmed by later courts (54%) | 12 |
| 6 rules | rule tables | see below | not a sample | - | - |

## 1. Zombie precedent

**Predicate** (`Hunt.zombie`): the status of the cited issue on the citing date is overruled, abrogated, reversed,
vacated or withdrawn; the citing court relies on it for the negated proposition; it does not note the history; it is
not the same case. Every instance is a `citesOverruled`, `citesVacated` or `citesWithdrawn` finding
(`zombie_is_spec_finding`).

**Known cases.** 42 overrulings from the CRS table and casebooks (`data/known_overrulings.tsv`): all 42 targets
resolve; the status layer marks 21 negative from the right date (50%, 36-65%) and 3 more as partly negative. The 18
it misses are partial or implicit overrulings (*Plessy*, *Lochner*, *Swift v. Tyson*, *Wolf*, *Ohio v. Roberts*,
*Conley*) and overrulers after the corpus ends (*Dobbs*, *Loper Bright*). For the 21, every later citer is a finding.
Later courts' own call-outs ("the court below relied on X, which had been overruled"): 146 notes, 3 resolvable
instances, none in the findings (the targets carry a partial status). The first reader called 3 of 20 such known
citations zombies. So recall is bounded by the status layer, about one half.

**Corpus.** 38,778 `citesOverruled` + 36,020 `citesVacated` findings; 73,568 with metadata; citation located in
71,919. Silent citations (no history word, negating decision not cited): 16,718 overruled, 11,110 reversed/vacated.
First reader on a weighted sample of 5,389: 50% and 57% of silent citations called zombies. Second reader confirms
12% (30/250) and 17.5% (21/120) of those. Estimated true instances: **1,815** counting only what both readers accept
(a lower figure: the second reader rejected 6 of 11 instances the audit confirmed) to **4,184** (first reader ×
audit precision).

**Audit.** First reader alone: overruled 4/20 (8-42%), reversed/vacated 4/10 (17-69%). The usual failure (15 of the 16
rejected): the decision was overruled on another point. Both readers: 19/22 (67-95%). Decoys 0/14.

**Top instances (all audit-confirmed).**

1. *In re Odyssey Healthcare*, 310 S.W.3d 419 (Tex. 2010) ← *National League of Cities v. Usery*, 426 U.S. 833:
   applies its "traditional governmental functions" test; *Garcia* (1985) overruled it and is not cited.
2. *United States v. Helsey*, 463 F. Supp. 1111 (D. Mont. 1979) ← *Hammer v. Dagenhart*, 247 U.S. 251: quoted as
   authority to hold a federal statute beyond Congress's power; overruled by *Darby* (1941).
3. *State v. Loudon*, 857 S.W.2d 878 (Tenn. Crim. App. 1993) ← *Minersville v. Gobitis*, 310 U.S. 586: quoted as the
   Court's view on religious exemptions; overruled by *Barnette* (1943).
4. *International Ass'n of Machinists v. Sandsberry*, 277 S.W.2d 776 (Tex. Civ. App. 1954) ← *Grovey v. Townsend*, 295
   U.S. 45: cited for no state action; overruled on that by *Smith v. Allwright* (1944).
5. *United States v. Thomas*, 305 F. App'x 960 (4th Cir. 2009) ← *United States v. MacDonald*, 635 F.2d 1115: speedy-trial
   point from a judgment the Supreme Court reversed in 1982.
6. *In re FedEx Ground Package System*, 283 F.R.D. 427 (N.D. Ind. 2012) ← *Wilkinson v. Palmetto State Transp.*, 371
   S.C. 365 (App. 2006): quoted for South Carolina's right-to-control test; reversed by the state supreme court in 2009.
7. *Stacy v. Merrill*, 191 N.C. App. 131 (2008) ← *Stein v. Asheville City Bd. of Educ.*, 168 N.C. App. 243: quoted on
   jurisdiction two years after the N.C. Supreme Court reversed it.
8. *Miller v. International Diving & Consulting Services*, 669 So. 2d 1246 (La. App. 1996) ← *Holmes v. J. Ray
   McDermott*, 734 F.2d 1110: punitive damages for maintenance and cure, overruled by *Guevara* (5th Cir. en banc 1995).
9. *Kimoktoak v. State*, 578 P.2d 594 (Alaska 1978) ← *United States v. Panczko*, 353 F.2d 676: adopts the per se
   jury-separation rule 18 days after the Seventh Circuit overruled it.
10. *Proctor v. Hoage*, 81 F.2d 555 (D.C. Cir. 1935) ← *Inglish v. Industrial Commission*, 125 Ohio St. 494: course of
    employment, overruled by Ohio the year before.

All 59 rows both readers accept: `data/p1_zombies.tsv`. Audit sheets: `audit/p1/audit.tsv`, `audit/p1b/audit.tsv`.

## 2. Unpublished or not-citable opinions treated as binding

**Predicate** (`Hunt.unpublishedAsBinding`): the cited decision is not published, its force on the citing court under
the issuing court's rule at its date is below `bindingAbsentConflict`, the citing court treats it as binding, and it is
not the same case.

**Known cases.** *Anastasoff v. United States*, 223 F.3d 898 (8th Cir. 2000) is the textbook instance; the unpublished
*Christie* it follows is not in the corpus, so it cannot be recreated. The rule windows behave: the 49 Fifth Circuit
unpublished decisions before 1996, which the rule makes precedent, are not reported.

**Corpus.** 93,362 later same-system citations of non-published decisions; 42,633 same-court citations of non-binding
ones; 2,880 with binding language. Read: 2,200 (Azure 1,598, Claude 602): 375 reported.

**Audit.** 0 of 20 (0-16%), and 0 of 12 top candidates. In 32 of 32 the cited decision is in fact **published**: a
reasoned opinion in F.3d, Ill. 2d or So. 2d that attaches or reviews an unpublished order (*United States v.
Slaughter*, 238 F.3d 580, alone accounts for 6 of the 20). The citing courts were right to treat them as binding.

**The mistake found is ours.** `decisions2.pub` marks 481,131 decisions as unpublished, table, summary order or
memorandum; **77,575 (16%) are printed in a reporter of published opinions** (`data/p2_pub_labels.tsv`: 50,755
"table", 22,412 "unpublished", 4,352 "memorandum"). This feeds every unpublished-opinion cap and the 38,803
`citesNotCitable` findings. `Hunt.mislabelled` states it; `Hunt.unpublishedAsBinding'` is the pattern on corrected
labels.

**Correction (12 Nov, label fix 2; `data/courts_validation.md` §6).** The 77,575 figure counts every non-published
label on a decision printed in a reporter of published opinions. Most of those labels are right: 50,512 are Florida
per curiam affirmances without opinion and about 11,600 are T.C. Memo. and Summary Opinions, which are printed and
are not precedent. **7,342 were really mislabelled**, and `labels_fix2.py` corrected them; 8,022 more reporter-cited
decisions stay non-published because they say so themselves or are entries under 600 characters. After the fix
`citesNotCitable` fell from 35,071 to 5,701.

**Refined run.** Citations of decisions printed only in the Federal Appendix, with binding language: 256, read by
Claude: 2 reported, 3 more are law of the case. Audit: 1 confirmed.

- *United States v. Beuns*, 614 F. App'x 284 (6th Cir. 2015) ← *United States v. Gilmore*, 431 F. App'x 428: "our
  precedent, which holds", citing only the unpublished decision.
- Not confirmed: *U.S. Oil Recovery Site PRP Group v. Railroad Comm'n of Texas*, 898 F.3d 497 (5th Cir. 2018) calls
  its unpublished decisions "our precedent", but the citation matched belongs to another case on the same page.

True instances are rare in this corpus: of 256 clean candidates, 1.

## 3. Panel overruling panel without en banc

**Predicate** (`Hunt.panelOverrulesPanel`): the later decision overrules, recedes from or refuses to follow a holding
of the same court (and unit); the court's horizontal rule is strong; the bench is a panel; the court had an en banc
procedure; no recognised exception (intervening higher or en banc authority, statute change, circulation to the full
court, earlier conflicting precedent, dicta).

**Known cases.** No set of later-court call-outs exists: the 5 notes that mention the prior-panel rule beside an
overruling recite the rule (`data/p3_known_callouts.tsv`). Validation is by mechanism: the lawful routes are known,
and the second read rejects each (D.C. Cir. *Irons* footnote, 2d and 1st Cir. circulation, Fed. Cir. en banc
footnote, 9th Cir. *Miller v. Gammie*). Against the 2 instances the first audit confirmed, the second read caught 0;
and 2 of 6 of its rejections were instances. Its recall is poor.

**Corpus.** 1,960 `panelDepartsWithoutEnBanc` findings, 1,869 pairs. First reader: 903 violations, 409 after removing
whole-court benches. Second reader: 58. It rejected 194 as en banc in fact (the bench field is wrong or missing), 25
as circulated to the full court, 20 on intervening higher authority, 32 as dicta, 14 as following earlier precedent. By court: Florida DCA 18, Louisiana 10, Texas 8, D.C. Cir. 6.
Estimated true instances among the 409: 37 to 154.

**Audit.** First reader: 2/20 (3-30%); federal top candidates 0/12. Two readers: 14/22 (43-80%), 2 unclear. All 6
not confirmed fail because the court had no prior-panel rule or en banc procedure then (Ohio before 2010,
Louisiana, the 2d and 10th Circuits in the 1940s): the rule table marks those courts "strong" too early.

**Top instances (audit-confirmed).**

1. *Tarrant Appraisal Dist. v. Tarrant Reg'l Water Dist.*, 547 S.W.3d 917 (Tex. App. Fort Worth 2018) overrules its own
   *Grand Prairie Hospital Authority*, 707 S.W.2d 281; en banc reconsideration denied.
2. *Revell v. Morrison Supply Co.*, 501 S.W.3d 255 (Tex. App. Fort Worth 2016) overrules *Johnson v. Kilpatrick*, 205
   S.W.3d 690, on sister-court criticism.
3. *Sawyer v. State*, 294 S.W.3d 862 (Tex. App. Beaumont 2009) overrules *Jackson v. State*, 990 S.W.2d 879.
4. *In re Hoover, Bax & Slovacek*, 6 S.W.3d 646 (Tex. App. El Paso 1999) overrules *Cass v. Stephens*, 823 S.W.2d 731.
5. *Tracy v. Gleason*, 379 F.2d 469 (D.C. Cir. 1967) overrules *Hahn v. Gray*, 203 F.2d 625, and two more.
6. *Franklin v. Franklin*, 171 F.2d 12 (D.C. Cir. 1948): a divided division says *Caffrey*, *Biscayne Trust* and
   *Lockwood* "should be overruled".
7. *Washington Annapolis Hotel Co. v. Riddle*, 171 F.2d 732 (D.C. Cir. 1948) overrules *Brice v. Curtis*, 38 App. D.C. 304.
8. *McHale v. Farm Bureau Mutual Insurance*, 409 So. 2d 238 (Fla. 3d DCA 1982): its own *Travelers Indemnity* was
   "incorrectly decided".
9. *Nash v. Hunt*, 434 So. 2d 51 (Fla. 3d DCA 1983) recedes from *Gonzalez v. Benoit*, six months old.
10. *Nelson v. Nelson*, 433 So. 2d 1015 (Fla. 3d DCA 1983) recedes from *Trujillo v. Trujillo* in a footnote.

Five more confirmed Florida instances date from 1980-83, just after the en banc rule (Fla. R. App. P. 9.331) began.
All 58: `work/p3b_out.jsonl`; audit sheets `audit/p3/audit.tsv`, `audit/p3b/audit.tsv`.

## 4. Superseded holdings applied after the statute's date

**Predicate** (`Hunt.twoDateError`): the citing court applies the holding the statute overrode, to conduct (or a claim
or filing) on or after the date from which the statute governs, without accounting for the statute.
`earlier_conduct_no_error` is prospectivity.

**Known cases.** The runner's 26 `appliesSupersededHolding` findings (all citing the Eleventh Circuit *Ledbetter*).
Audit: **0 of 20** (0-16%). They cite *Ledbetter* for points the Fair Pay Act did not touch (weighing evidence, the
180-day period). The runner uses the citing date as the conduct date and matches the issue too loosely, so the known
set holds no mistake to recreate.

**Corpus.** 36 Supreme Court decisions Congress overrode (Christiansen & Eskridge; Hasen), 13,605 later citations
after the effective date, 3,205 located and sampled, 799 read by Claude with the scope of each override stated. The old
rule is applied in 68; in 32 of those the conduct predates the statute (correct). Reported errors: 2. Candidates
where the passage did not give the conduct date: 24.

**Audit.** Reported 1/2; candidates 2/24; decoys 0/6. **Three confirmed instances** in all:

1. *Nadel v. Shinseki*, 57 F. Supp. 3d 288 (S.D.N.Y. 2014) ← *Toyota v. Williams*: applies the "permanent or long-term"
   standard to 2010-11 employment; the ADA Amendments Act (from 1 Jan 2009) is not mentioned.
2. *El Paso County v. Vasquez*, 508 S.W.3d 626 (Tex. App. 2016) ← *Toyota*: same standard for a 2013 discharge (the
   claim is under Texas Chapter 21, which follows the ADA).
3. *United States v. Mayle*, 334 F.3d 552 (6th Cir. 1 Jul 2003) ← *Koon*: abuse-of-discretion review of a departure
   two months after the PROTECT Act required de novo review.

The pattern is rare where it can be checked: 3 in 799 read. The ADA Amendments Act is where it happens.

## 5. Inconsistent binding bases and persisting splits

**Predicates.** `Hunt.inconsistentBase` (Horty, pair form: opposite outcomes, each reason present in the other's
facts); `Hunt.persistingSplit` (`Spec.split`); `Hunt.losingSideAfterResolution`.

**Horty.** 354 Supreme Court holdings with factors in 53 question families: **4 conflicting pairs, all in express
pre-emption** (`data/p5_horty.tsv`). *Aloha Airlines v. Director of Taxation* (1983) holds the state tax pre-empted
because the clause names the regulated transaction, with a state-authority exception present; *Anderson v. Pacific
Coast S.S.* (1912), *City of Columbus v. Ours Garage* (2002), *Chamber of Commerce v. Whiting* (2011) and one 2026
decision give the exception priority with the same two factors present. At this factor grain the base binding every
federal court orders the two reasons both ways. The other 52 families are consistent. The factor vocabulary is
coarse (about one factor per case), so this is a lead, not a holding.

**Persisting splits.** `out/splits.tsv`: 335 split rows (opposite good-law answers by circuits that do not bind each
other; 123 under Title 18, 80 under Title 8, 56 under Title 28) and 139 conflict rows (one court bound by both
answers). Not audited. Spot check: several are stale because the resolving Supreme Court holding is not in
`holdings.tsv` (*Wideman* v. *Burger* on Title VII retaliation, resolved by *Burlington Northern v. White*;
*Banuelos-Galviz* v. *Garcia-Romo*, resolved by *Niz-Chavez*).

**Losing side after resolution.** 809 Supreme Court resolutions in gold, 394 with conflict decisions named; sides
read from the Court's words (Azure): 678 losing, 691 winning, 63 unclear. **Known check:** of 304 losing-side
decisions with later citations, later courts' own notes mark 164 (54%, 48-60%) as overruled, abrogated or reversed by
that Supreme Court decision. Later citations: 6,506; with no mention of the Supreme Court decision anywhere: 2,087;
read by Claude: 725; reported 35 (weighted 130 in the pool; about 39 after audit precision).

**Audit.** 6/20 (15-52%), top list 6/12, decoys 0/8. The usual failure (13 of the 14 rejected): the losing-side decision is
cited for another point.

**Top instances (audit-confirmed).**

1. *United States v. Armstrong*, 550 F.3d 382 (5th Cir. 2008) ← *United States v. Wilson*, 249 F.3d 366: overt act for a
   § 1956(h) conspiracy; *Whitfield* (2005) held none is needed.
2. *Hvizdak v. Linn*, 190 A.3d 1213 (Pa. Super. 2018) ← *Sikes v. Teleline*, 281 F.3d 1350: first-party reliance in civil
   RICO, dismissing on it; *Bridge v. Phoenix Bond* (2008) rejected the rule.
3. *Barry v. Santander Bank (In re Liberty State Benefits)*, 541 B.R. 219 (Bankr. D. Del. 2015) ← *United States v.
   Thomas*, 315 F.3d 190: intent to defraud the bank; *Loughrin* (2014).
4. *Wade v. Gaither*, 623 F. Supp. 2d 1277 (D. Utah 2009) ← *Bath v. Bushkin* and *Bivens Gardens*: injury-and-pattern
   accrual for civil RICO; *Rotella v. Wood* (2000).
5. *Waddell & Reed Financial v. Torchmark*, 243 F. Supp. 2d 1232 (D. Kan. 2003) ← *Bath*: the same.
6. *City of O'Fallon v. CenturyLink*, 491 S.W.3d 276 (Mo. App. 2016) ← *Guthrie v. Evans*, 815 F.2d 626: unnamed class
   members cannot appeal; *Devlin v. Scardelletti* (2002). Alternative ground.
7. *Oracle USA v. Rimini Street*, 6 F. Supp. 3d 1108 (D. Nev. 2014) ← Ninth Circuit *Petrella*: laches against a timely
   copyright claim, three months after the Supreme Court reversed.
8. *Durthaler v. Accounts Receivable Management*, 854 F. Supp. 2d 485 (S.D. Ohio 2012) ← Sixth Circuit *Jerman*: bona
   fide error covers mistakes of law; reversed in 2010. Not outcome-determinative.
9. *Hooker v. Hoover (In re Hoover)*, 289 B.R. 340 (Bankr. N.D. Ohio 2003) ← *Perkins v. Scharffe*, 817 F.2d 392:
   "willful" under § 523(a)(6); *Kawaauhau v. Geiger* (1998).
10. *Miller v. Westfield Steel (In re Elrod)*, 426 B.R. 106 (Bankr. D. Del. 2010) ← *Fobian*, 951 F.2d 1149: no fees for
    bankruptcy-law issues; *Travelers v. PG&E* (2007).

All 35: `data/p5_losing_side.tsv`; audit sheet `audit/p5/audit.tsv`.

## 6. Loopholes in the rules of precedent

Found by running the reference engine (`ref/precedent_ref.py`) over the rule tables and counting the decisions each
combination touches (`p6_rules.py`, `p6_more.py`; `data/p6*.tsv`). These are properties of the rules as we model
them; each names the doctrine it rests on.

**a. Forum choice.** A holding binds in one forum and not its sibling (`Hunt.forumDependent`).
- Federal law in state court: 50 systems treat their circuit as persuasive, 4 as binding, 2 as strongly persuasive.
  The same circuit holding binds the federal district court and not the state court across the street.
- State trial courts: 36 systems statewide, 3 choose on conflict, 3 own-district-then-any (Florida, Illinois), 3
  own-district only. Under the Florida and Illinois rule one district's panel binds every trial court in the state
  until the home district speaks, while it does not bind the other districts' appellate courts.
- 1,442 treatments in which a court declines to follow or "overrules" a court of another system (670 state-state,
  527 state courts on federal courts, 245 federal on state); none has power, so both answers stand.
- 13 systems have a first-in-time rule; the rest let the later panel prevail in practice.

**b. Successor-court gaps** (`Hunt.orphaned`, `Hunt.cutoffWindow`). 37 successions.
- **New Jersey 1948.** The Court of Errors and Appeals binds the new trial and appellate courts. The old *Supreme
  Court* (an intermediate court, 21,129 decisions) has no adoption row: persuasive on the new Supreme Court and on
  the Appellate Division, binding (absent conflict) only on trial courts.
- **D.C. 1971** (*M.A.P. v. Ryan*). A D.C. Circuit decision of 29 Jan 1971 binds the D.C. trial courts; one of 2 Feb
  1971 is persuasive. On the D.C. Court of Appeals itself the engine gives "strongly persuasive" (a court of last
  resort is not bound by itself), although *M.A.P.* binds its divisions: a gap in our rule, not in the law.
- **Kentucky 1976.** No gap: the old Court of Appeals binds the new one and every circuit court.
- **Tenth Circuit 1929.** The same kind of split as 1981, the opposite answer: 7,364 Eighth Circuit decisions bind
  nobody in the Tenth (18,141 later citations there).
- **Court of Claims 1982.** 17,104 decisions carry "unknown" force on the Federal Circuit, because *South Corp.*
  excludes trial-division decisions and the data cannot separate them.
- Without any binding successor: Kansas Court of Appeals 1895-1901 (1,744 decisions), Court of Appeals of Indian
  Territory (574), New Jersey Court of Chancery (10,882). Five old courts, 37,668 decisions, 68,680 later citations.

**c. Dual high courts** (`Hunt.dualHighCourtConflict`). Texas and Oklahoma: both courts bind the intermediate courts
and neither has power over the other. 8 treatments cross the line (Texas 4, Oklahoma 4), 7 styled "overruled", for
example *Jackson v. State*, 548 S.W.2d 685 (Tex. Crim. App. 1977) on *State v. Olsen*, 360 S.W.2d 398 (Tex. 1962).
All have power "no" (`H2.dualLastResort`), so status never changes and an intermediate court is bound by both.

**d. Unpublished-opinion windows.** 40 windows (`data/p6d_unpublished_windows.tsv`). The 49 Fifth Circuit unpublished
decisions before 1996 are precedent there, and those before Oct 1981 also bind the Eleventh Circuit, whose own
unpublished opinions never bind; 41 later ones bind the Fifth and are persuasive in the Eleventh. 600 Texas civil appeals decisions are binding though unpublished. Territorial adopters (Guam, the Northern
Marianas, the Virgin Islands) inherit 69,218 and 15,149 Ninth and Third Circuit unpublished decisions as persuasive.

**e. Adoption chains carrying overruled law** (`Hunt.adoptionCarriesOverruled`). 48 overrulings of pre-split decisions
by one heir: the Fifth Circuit en banc overruled 37 old-Fifth decisions that still bind the Eleventh (63 later
Eleventh Circuit citations); the Eleventh overruled 8 that still bind the Fifth (30); D.C. 3 (5). Example: *United
States v. Salinas*, 654 F.2d 319 (5th Cir. Aug 1981), overruled by *United States v. Adamson*, 700 F.2d 953 (5th Cir.
1983) (en banc), cited 11 times since by the Eleventh Circuit. **Our Spec gets this wrong**: status is global
(`Spec.citesOverruled`: "not relative to the citing court"), so the runner reports 25 of these 98 citations as citing
overruled law. Status after an adoption cut should be per heir.

**f. Commission opinions** (`Hunt.commissionForce`). The notation decides: "opinion adopted" binds as the Supreme
Court's own, "judgment adopted" is result only, none is persuasive. Of 4,676 Texas Commission of Appeals decisions
only 955 carry a notation row (945 "opinion adopted"); the other 3,721 fall to the default. On lower courts the engine
gives the probe (a 1943 Commission decision) full vertical force (`binding:H1`): the notation limits only the
adopter. 7,004 Missouri and 3,242 Texas criminal commissioner opinions are typed "other" or "opinion approved" and
treated as the court's own.

## Lean

`LegalProofs/CaseLaw2/Hunt.lean` (a module of its own): the predicates above, 14 theorems, 44 `#guard`s
on the cases named here and on the near misses. Compiled 2026-11-12 in WSL (Lean 4.35.0) against the built
`LegalProofs.CaseLaw2` oleans: exit 0, no messages. A copy is in `~/caselaw2/lean-proofs/LegalProofs/CaseLaw2/`.

    wsl.exe -d Ubuntu -- bash /mnt/c/Users/<you>/Documents/global-law-lean/lean-proofs/tools/caselaw2/hunt/hunt_lean.sh

Since the hunt fixes of 12 Nov (evening) the module is imported by `Core.lean`, and its 14 theorems are in the
registry and locked (`STATEMENTS.log`; LEAN.md "Hunt fixes"). It is built and audited with the rest.

## What to fix in caselaw-lean-2 (found here)

1. `decisions2.pub`: reporter-printed decisions labelled not published (77,575 such labels, of which 7,342 were
   wrong). Use the citation as a check. **Done** (label fix 2).
2. `appliesSupersededHolding`: 0 of 20. Needs the conduct date and a holding-level match, not the citing date.
   **Done** (DEVIATIONS 70).
3. `panelDepartsWithoutEnBanc`: bench is wrong or missing for at least 194 of 409 decisions; circulation footnotes
   are not read; `horizontal = strong` is applied before courts had the rule (Ohio, Louisiana, early federal circuits).
4. Status after an adoption cut is global; it should be per heir (25 false `citesOverruled`). **Done** for the
   citation findings (DEVIATIONS 69); round 2 extends it to status rows, splits, conflicts and Horty bases
   (ROUND2.md).
5. The status layer misses half the literature overrulings (partial and implicit ones).
6. D.C. Court of Appeals divisions are bound by *M.A.P. v. Ryan*; the engine gave "strongly persuasive". **Done**
   (DEVIATIONS 68).

Items 3 and 5: the bench re-read, the dated Ohio and Louisiana rules and the 1948 en banc date were done on 12 Nov
(DEVIATIONS 71); the court-size bench rule and the recall of overrulings are round 2 (ROUND2.md).

## Limits

- Passage readers see ± 900 characters; audits see up to 34,000 characters of the citing opinion. Where an auditor
  relied on memory for the negating decision, the explanation says so.
- Audit samples are 20-22 per pattern; intervals are wide. Pattern 2 (refined) and pattern 4 have 2 and 3 instances.
- Pattern 1 and 3 first reads are Azure; second reads and audits are Claude. Patterns 4 and 5 have one Claude read.
- Estimates are for the candidate pools named, not for all US case law. Pattern 1 cannot see overrulings the status
  layer misses; pattern 5 covers only splits whose losing side the Court named; pattern 4 only the 36 listed overrides.
- Persisting splits and the Horty result are unaudited.
- The second reads have low recall (pattern 1: 5 of 11; pattern 3: 0 of 2), so the two-reader counts are floors.

## Files

- `summary.json`: per pattern `precision`, `precision_ci95`, `recall`, `recall_ci95`, `counts`, `known`, `audit`,
  `corpus`, `top`; `p6_rules`; `lean`; `strongest`.
- `data/`: `known_overrulings.tsv`, `p1_candidates.tsv`, `p1_known_callouts.tsv`, `p1_zombies.tsv`, `p2_unpub.tsv`,
  `p2_pub_labels.tsv`, `p3_panel.tsv`, `p3_known_callouts.tsv`, `p4_superseded.tsv`, `p5_losing_side.tsv`,
  `p5_horty.tsv`, `p6a`-`p6h`.
- `audit/<p1|p1b|p2|p2b|p3|p3b|p4|p5>/`: `audit.tsv`, `audit.json`, `key.json`, and each auditor's items and answers.
- `work/`: passages, reader inputs and outputs (`*_out.jsonl`, each row labelled with its reader), `claude/` batches.
- Scripts (`tools/caselaw2/hunt/`): the predecessor's `p1_*`-`p6_rules.py`, `passages.py`, `tasks.py`; added
  `claude_batches.py`, `second_prep.py`, `p1_second.py`, `audit_prep.py`, `p6_more.py`, `hunt_summary.py`,
  `hunt_summary_top.py`, `hunt_lean.sh`. `llm_run.py` (Azure) is kept for the record and was not run.

Rebuild the numbers: `python hunt_summary.py && python hunt_summary_top.py`.
