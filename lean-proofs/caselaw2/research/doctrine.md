# The US law of precedent: a machine-translatable specification (caselaw-lean-2)

Research for v2 of the Lean model in `global-law-lean/lean-proofs/LegalProofs/USCaseLaw/{Courts,Precedent}.lean`.
Compiled 2026-11-12.

## 0. How to read this file

### 0.1 Confidence tags

Every rule has one of these tags:

| Tag | Meaning |
|---|---|
| **[S]** | Checked in this research pass against the rule text, an official court page, or a quotation of the leading case. |
| **[L]** | A leading case, rule or statute given from established knowledge and not re-fetched in this pass. The citation is believed correct; check the pin cite before a proof or table depends on it. |
| **[U]** | Uncertain, contested, or known only from secondary sources. Encode it as a *parameter* (a table row that can be flipped), never as a theorem. |

### 0.2 What v1 models, and what v2 must add

v1 has four ingredients:

- `Court = {id, system, tier, circuit}`.
- `binds` as a Boolean.
- `mayOverrule` as a Boolean.
- Whole-decision `Overruling` events, monotone in time.

Every section below says what v2 must add to that. The short version:

1. **Precedential force is graded**, not Boolean. The grades are:
   - `binding`
   - `bindingAbsentConflict` (Florida, New York, Illinois trial courts)
   - `persuasive`
   - `citableNoWeight`
   - `notCitable`
   - `none`

2. **Force depends on more than the two courts.** It also depends on:
   - the *decision*: published or unpublished; en banc or panel; plurality; equally divided; summary disposition; physical precedent;
   - the *issue*: federal or state law; patent or regional law; dictum;
   - the *date*: rule changes, court successions, and the date of the event.

3. **Status is per issue, not per decision.** Partial overruling, "on other grounds", and abrogation by statute each affect only some holdings.

4. **Two event families must be kept apart:**
   - same-case history: reversed, vacated, cert denied, withdrawn, depublished;
   - later-case treatment: overruled, abrogated, disapproved, receded from, distinguished.

5. **Court identity is a timeline.** "Court of Appeals of Kentucky" is the court of last resort before 1976 and an intermediate court afterwards. "Supreme Court of New Jersey" was *not* the court of last resort before 15 Sept 1948. A court's identity needs a dated name, a dated tier, and successor/adoption edges.

### 0.3 What the corpus gives for detection

From `~/Documents/us-caselaw-repos/*`, each decision file has front matter with these fields:

- `court`
- `decided`
- `docket`
- `citations`: the reporter names reveal the publication channel, e.g. `F. App'x`.
- `judges`: a panel string such as "Before … Circuit Judges", or "en banc".
- `parties`, `cap_id`

Opinion sections are headed `## Majority`, `## Lead`, `## Plurality`, `## Concurrence`, `## Concurrenceinpart`, `## Dissent`, `## Combined`, `## Rehearing`, and so on. In the `supreme-court` repo, `## Lead` occurs 4,968 times; it is CourtListener's "lead opinion" type, a plurality signal.

`decision-relations.tsv` already carries `same-decision-as`. v2 should add relation kinds for same-case history.

---

## 1. Federal courts

### 1.1 Supreme Court: vertical authority

**Rule F1 — SCOTUS binds every court on federal law.**
- Lower courts must follow a directly controlling Supreme Court precedent even if later cases have eroded its reasoning. Only the Court may overrule its own decisions.
- Sources:
  - *Rodriguez de Quijas v. Shearson/American Express*, 490 U.S. 477, 484 (1989) [S, quoted in Walker 2022];
  - *State Oil Co. v. Khan*, 522 U.S. 3, 20 (1997) [L];
  - *Agostini v. Felton*, 521 U.S. 203, 237 (1997) [L];
  - *Hutto v. Davis*, 454 U.S. 370, 375 (1982) (per curiam) [L];
  - *Mallory v. Norfolk Southern Ry.*, 600 U.S. 122, 136 (2023) [L].
- "Vertical stare decisis is absolute": *Ramos v. Louisiana*, 590 U.S. 83, n.5 (Kavanaugh, J., concurring in part; the cite is to the opinion as quoted) [S, quoted in Walker 2022].
- Scope: all federal and state courts, on federal questions only. SCOTUS decisions on *state* law are rare (and generally improper). A SCOTUS reading of state law does not bind the state's highest court.
- Exception (not a rule of precedent, but it limits authority): AEDPA. A federal habeas court reviewing a state conviction may treat as "clearly established Federal law" only *holdings of the Supreme Court* (28 U.S.C. § 2254(d)(1)). Circuit precedent cannot fill the gap.
  - *Parker v. Matthews*, 567 U.S. 37, 48–49 (2012) [L];
  - *Williams v. Taylor*, 529 U.S. 362, 412 (2000) (holdings, not dicta) [L].
  - This is a *context-dependent admissible-authority rule*. Model it as a filter on which sources count, keyed by proceeding type.
- Detection: `court = "Supreme Court of the United States"`.
- Lean: `Court.scotus`. Keep F1 as an axiom-level rule `binds scotus c (issue := federal)`.

**Rule F2 — Summary dispositions on mandatory appeal are precedential, but narrowly.**
- Summary affirmances, and dismissals "for want of a substantial federal question", bind lower courts. They are read as deciding only the precise issues presented and necessarily decided. They affirm the judgment, not the lower court's reasoning.
- Sources:
  - *Hicks v. Miranda*, 422 U.S. 332, 344–45 (1975) [L];
  - *Mandel v. Bradley*, 432 U.S. 173, 176 (1977) (per curiam) [L];
  - *Illinois State Bd. of Elections v. Socialist Workers Party*, 440 U.S. 173, 180–83 (1979) [L].
- Date range: mandatory appellate jurisdiction was mostly abolished by the Supreme Court Case Selections Act, Pub. L. 100-352, 102 Stat. 662, effective 25 Sept 1988 [L]. After that, summary affirmances come almost only from three-judge district courts (28 U.S.C. § 1253).
- Detection: SCOTUS decisions with a very short text and the phrases "The judgment is affirmed" or "appeal is dismissed for want of a substantial federal question". The citation is often only in a U.S. Reports table, with no `## Majority` text of substance.
- Lean: `DecisionForm.summaryAffirmance`. Its issues are the "questions presented" (usually unknown) and its force is `binding` on `necessarilyDecided` issues only. Practically: binding, but with `issueScope := unknownNarrow`.

**Rule F3 — Certiorari denial has no precedential value.**
- *Maryland v. Baltimore Radio Show*, 338 U.S. 912, 917–19 (1950) (Frankfurter, J., respecting denial) [L]; *Teague v. Lane*, 489 U.S. 288, 296 (1989) [L].
- It is a same-case event that leaves the lower decision's status unchanged.
- The same holds for these, which also *do not* add approval:
  - state analogues: Texas CCA "PDR refused"; Oklahoma "cert. denied" to the Court of Civil Appeals, which by rule has no precedential effect [S, OK 2013 order quoted];
  - California "review denied" [L].
- **Exception: Texas civil "writ refused" / "pet. refused" (Rule S-TX-3) *does* add approval.**

**Rule F4 — GVR and other vacaturs strip the lower opinion's precedential effect.**
- A grant, vacate and remand (GVR) does not decide the merits (*Lawrence v. Chater*, 516 U.S. 163, 166–67 (1996) [L]). But it vacates the judgment.
- A vacated judgment's opinion loses precedential effect:
  - *County of Los Angeles v. Davis*, 440 U.S. 625, 634 n.6 (1979) [L];
  - *O'Connor v. Donaldson*, 422 U.S. 563, 577 n.12 (1975) [L].
- Mootness vacatur: *United States v. Munsingwear, Inc.*, 340 U.S. 36 (1950) [L]; limited by *U.S. Bancorp Mortgage Co. v. Bonner Mall P'ship*, 513 U.S. 18 (1994) [L].
- Example: *Anastasoff v. United States*, 223 F.3d 898 (8th Cir. 2000), vacated as moot en banc, 235 F.3d 1054 (2000) [L].
- Lean: a same-case event `vacated (scope := whole | parts P)` sets the status of the affected issues to `vacated` from the event date. Vacatur is *not* overruling: a vacated opinion is not "wrong", only not law. It can be cited as persuasive by some courts [U].

**Rule F5 — Affirmance by an equally divided Court has no precedential weight.**
- The judgment below stands; nothing is decided for other cases.
- Sources:
  - *Durant v. Essex Co.*, 74 U.S. (7 Wall.) 107, 112 (1868) [L];
  - *Hertz v. Woodman*, 218 U.S. 205, 213–14 (1910) [L];
  - *United States v. Pink*, 315 U.S. 203, 216 (1942) [L];
  - *Neil v. Biggers*, 409 U.S. 188, 192 (1972) [L].
- Scope: SCOTUS, en banc courts of appeals, and state high courts. A state court may have a different local rule [U]. For example, in Pennsylvania an affirmance by an evenly divided Supreme Court has no precedential value [L].
- Detection: "affirmed by an equally divided Court", "The judgment is affirmed by an equally divided court", "evenly divided". SCOTUS usually issues a one-line per curiam. The `judges` field may list a recusal.
- Lean: `DecisionForm.equallyDivided`. Its issues all have force `none` beyond the parties. The *lower* decision's status is unchanged: it is affirmed, but gains no approval.

**Rule F6 — Fragmented decisions: the *Marks* rule.**
- "When a fragmented Court decides a case and no single rationale explaining the result enjoys the assent of five Justices, the holding of the Court may be viewed as that position taken by those Members who concurred in the judgments on the narrowest grounds."
  - *Marks v. United States*, 430 U.S. 188, 193 (1977) (quoting *Gregg v. Georgia*, 428 U.S. 153, 169 n.15 (1976)) [L].
- The Court has noted that the rule is hard to apply but declined to clarify it:
  - *Nichols v. United States*, 511 U.S. 738, 745–46 (1994) [L];
  - *Hughes v. United States*, 584 U.S. 675 (2018) [L].
- *Ramos v. Louisiana*, 590 U.S. 83 (2020) [L] split on whether the *Apodaca* plurality/concurrence carried precedential force.
- Circuit readings of *Marks*:
  - "Logical subset". The narrowest opinion must be a logical subset of other opinions that together make a majority; if none is, only the specific result binds. *King v. Palmer*, 950 F.2d 771, 781–82 (D.C. Cir. 1991) (en banc) [L]; *United States v. Davis*, 825 F.3d 1014, 1021–22 (9th Cir. 2016) (en banc) [L].
  - Others count any five votes on a proposition, including dissenters [U: practice varies; e.g. the 3d Cir. has looked to dissents in some cases].
- Parts: a SCOTUS opinion can be "the opinion of the Court with respect to Parts I, II and IV" and a plurality as to Part III. Precedential force is per *part*.
- Scope: SCOTUS. State high courts apply *Marks*-like rules to their own fractured decisions with variation [U].
- Detection:
  - section header `## Lead` or `## Plurality`, or no `## Majority`;
  - the phrase "announced the judgment of the Court and delivered an opinion, in which X and Y joined";
  - "delivered the opinion of the Court with respect to Parts …";
  - "concurring in the judgment".
- Lean:
  - an `Opinion` has `role ∈ {majority, plurality/lead, concurrence, concurrenceInJudgment, dissent, …}`, `joins : List Judge` and `parts : List PartId`;
  - a part is *majority* iff its joiners number more than half of the participating judges;
  - a `marksHolding` is a *data* field (a curated proposition), not something computed;
  - default: a decision with no majority part has issue force `binding` on the *result* only (`resultOnly`) and `persuasive` on reasoning, unless a `marksHolding` row exists.

### 1.2 Courts of appeals: horizontal stare decisis (the "law of the circuit")

**Rule F7 — The prior-panel rule.**
- A published panel decision binds later panels of the same circuit, and the circuit's district courts. It stays binding until:
  - (a) the court en banc overrules it;
  - (b) an intervening Supreme Court decision undermines it (the exact standard varies; see below); or
  - (c) an intervening statute supersedes it.
- [S: compilation of every circuit's leading statement in Walker, *Precedential Power Policies*, 114 Law Libr. J. 167, 174–77 nn.50–54 (2022), https://www.albanylaw.edu/media/18456]

| Circuit | Leading statement | Intervening-authority standard | Conflicting panels | Notes |
|---|---|---|---|---|
| 1st | *Gonzalez-Mesias v. Mukasey*, 529 F.3d 62, 65 (2008); *Igartua v. United States*, 626 F.3d 592, 603 (2010) [S] | A controlling intervening event (SCOTUS, en banc, statutory overruling), or "in extremely rare circumstances" non-controlling but persuasive authority (*Williams v. Ashland Eng'g*, 45 F.3d 588, 592 (1995)) [L] | [U] | The 1st Cir. may circulate an opinion to all active judges before departing [U]. |
| 2d | *United States v. Walker*, 974 F.3d 193, 201 (2020) ("in banc proceeding (or its equivalent)") [S] | SCOTUS or en banc; *In re Zarnel*, 619 F.3d 156, 168 (2010) [L] | [U] | **"Mini en banc"**: a panel circulates its opinion to all active judges and, with no objection, may overrule. Examples: *Shipping Corp. of India v. Jaldhi*, 585 F.3d 58, 67 n.9 (2009); *United States v. Parkes*, 497 F.3d 220, 230 n.7 (2007) [L]. |
| 3d | 3d Cir. I.O.P. 9.1: "the holding of a panel in a precedential opinion is binding on subsequent panels. Thus, no subsequent panel overrules the holding in a precedential opinion of a previous panel. Court en banc consideration is required to do so." [L]; *Karns v. Shanahan*, 879 F.3d 504, 514–15 (2018) [S] | Must yield to a later SCOTUS holding, even for an en banc precedent (*Karns*) | Earliest controls [L: *Holland v. N.J. Dep't of Corr.*, 246 F.3d 267, 278 n.8 (2001)] | Non-precedential opinions do not bind because they do not circulate to the full court (I.O.P. 5.7) [S] |
| 4th | *Williams v. Taylor*, 163 F.3d 860, 866 (1998); *United States v. Collins*, 415 F.3d 304, 311 (2005) [S] | En banc or a "superseding contrary decision of the Supreme Court" | **Earliest controls**: *McMellon v. United States*, 387 F.3d 329, 333 (2004) (en banc) [L] | |
| 5th | "Rule of orderliness": *Jacobs v. Nat'l Drug Intelligence Ctr.*, 548 F.3d 375, 378 (2008) [S] | An intervening change in law by statute, SCOTUS or en banc; the older wording was "unequivocally directed" (*United States v. Zuniga-Salinas*, 945 F.2d 1302, 1306 (1991)) [S] | Earliest controls [L: *Rios v. City of Del Rio*, 444 F.3d 417, 425 n.8 (2006)] | Pre-split Fifth Circuit law stays 5th Cir. law; Unit A/Unit B, see F10 |
| 6th | 6 Cir. R. 32.1(b) [L]; *Salmi v. Sec'y of HHS*, 774 F.2d 685, 689 (1985); *Wright v. Spaulding*, 939 F.3d 695, 700 (2019) [S] | SCOTUS "requires modification", or en banc | Earliest controls: *Darrah v. City of Oak Park*, 255 F.3d 301, 309–10 (2001) [L] | |
| 7th | *De Leon Castellanos v. Holder*, 652 F.3d 762, 765 (2011): "compelling circumstances, or an intervening on-point Supreme Court decision" [S] | Softer: "not bound absolutely; may overturn circuit precedent for compelling reasons" (*Russ v. Watts*, 414 F.3d 783, 788 (2005)) [S] | [U] | **7th Cir. R. 40(e)**: a panel opinion that would overrule circuit precedent or create a conflict is circulated to all active judges, and may issue if a majority does not vote to rehear en banc. It is marked by a footnote [S, quoted in Walker n.54]. The rule's number may have changed with the FRAP 35→40 restyle [U]. |
| 8th | *United States v. Manning*, 786 F.3d 684, 686 (2015) [S] | En banc, or "repudiated or undermined by later authority" (*Dean v. Searcey*, 893 F.3d 504, 511 (2018)) [S] | **Earliest controls**: *Mader v. United States*, 654 F.3d 794, 800 (2011) (en banc) [L] | |
| 9th | *E. Bay Sanctuary Covenant v. Trump*, 950 F.3d 1242, 1261 (2020); *Hart v. Massanari*, 266 F.3d 1155 (2001) [S/L] | **"Clearly irreconcilable"** intervening higher authority frees both panels and district courts: *Miller v. Gammie*, 335 F.3d 889, 899–900 (2003) (en banc) [L] | [U] | **Limited en banc** of 11 judges (Pub. L. 95-486 § 6 (1978); 9th Cir. R. 35-3) [L]. A published opinion binds from filing, before the mandate: *Yong v. INS*, 208 F.3d 1116, 1119 n.2 (2000) [L — not re-verified] |
| 10th | *In re Smith*, 10 F.3d 723, 724 (1993); *Barnes v. United States*, 776 F.3d 1134, 1147 (2015) [S] | En banc or a superseding SCOTUS decision | [U] | **En banc footnote**: a panel may overrule with the full court's approval, recorded in a footnote, e.g. *United States v. Meyers*, 200 F.3d 715, 721 n.3 (2000) [L]. **Not** bound by pre-1929 8th Cir. law: *Estate of McMorris v. Comm'r*, 243 F.3d 1254, 1258 (2001) [S, via Walker ¶17] |
| 11th | *Smith v. GTE Corp.*, 236 F.3d 1292, 1300 n.8 (2001) [L]; *United States v. Dixon*, 901 F.3d 1322, 1347 (2018) [S] | SCOTUS must undermine the precedent "to the point of abrogation": *United States v. Archer*, 531 F.3d 1347, 1352 (2008) [L] | **Earliest controls** (*Dixon*, quoting *United States v. Dailey*, 24 F.3d 1323, 1327 (1994)) [S] | *Bonner*; Unit B (F10) |
| D.C. | *LaShawn A. v. Barry*, 87 F.3d 1389, 1395 (1996) (en banc); *Brewster v. Comm'r*, 607 F.2d 1369, 1373–74 (1979) [S/L] | "Intervening developments … removed or weakened the conceptual underpinnings" (*Allegheny Def. Project v. FERC*, 964 F.3d 1, 18 (2020) (en banc)) [S] | [U] | **Irons footnote**: a panel may overrule with the approval of the full court, marked by a footnote. *Irons v. Diamond*, 670 F.2d 265, 268 n.11 (1981) [L] |
| Fed. | *Deckers Corp. v. United States*, 752 F.3d 949, 959 (2014); *Newell Cos. v. Kenney Mfg.*, 864 F.2d 757, 765 (1988) [S/L] | En banc or SCOTUS | Earliest controls [L: *Newell*] | Predecessor adoption and regional-law choice: F11 |

Detection for F7:

- **En banc**: the `judges` field contains "en banc" / "in banc", or more than 3 judges are listed. The text contains "Before … Chief Judge, and … Circuit Judges" with a large count, "sitting en banc", or "ON REHEARING EN BANC".
- **Irons / en banc / circulation footnote**: phrases such as:
  - "circulated to all active judges";
  - "has been circulated to the full court";
  - "this part of the opinion has been approved by the en banc court";
  - "Irons footnote";
  - "Because this opinion overrules … it has been circulated among all judges of this court in regular active service. No judge favored … a rehearing en banc" (the 7th Cir. formula).
- A decision carrying one of these is treated as an **en banc–equivalent ruling on the circulated issue**.

Lean for F7:
- `Bench := panel | enBanc | enBancLimited | circulatedPanel | fullCourt` (state analogues included).
- `mayOverrule a b` becomes `mayOverrule (by : Decision) (target : Decision) (issue)`. It is true when:
  - `by.court` outranks `target.court`; or
  - same court and `by.bench ≥ enBancEquivalent`; or
  - same court and the state's horizontal rule is `soft` or `none` (see §4); or
  - an intervening higher authority (a separate *abrogation* event, F14).
- **Conflict resolution**: `firstInTimeControls : Circuit → Bool` (true for 3d, 4th, 5th, 6th, 8th, 11th and Fed.; `[U]` elsewhere). The resolver picks the earliest binding panel holding on the issue.

**Rule F8 — The en banc court.**
- Composition: 28 U.S.C. § 46(c) (a majority of the circuit judges in regular active service) [L].
- Procedure was FRAP 35; since **1 Dec 2024** it is merged into restyled FRAP 40 [L — check the exact effective date].
- An en banc decision binds all panels and district courts of the circuit. It may overrule any panel decision, and any earlier en banc decision.
- **A grant of rehearing en banc vacates the panel opinion** in many circuits by local rule. Examples [L/U per circuit]:
  - 3d Cir. I.O.P. 9.5.9;
  - 4th Cir. R. 35(c);
  - 5th Cir. R. 41.3;
  - 6th Cir. R. 35(b) (now under FRAP 40) [U];
  - 10th Cir. R. 35.6;
  - 11th Cir. R. 35-11;
  - in the 9th Cir., the panel opinion "shall not be cited as precedent" (9th Cir. Gen. Order 5.5(d)) [U].
- If the en banc court is equally divided, the district court's judgment is affirmed and there is no circuit precedent (F5). The panel opinion stays vacated where the local rule vacated it [U].
- Detection: subsequent-history strings such as:
  - "reh'g en banc granted, opinion vacated";
  - "vacated and rehearing en banc granted";
  - "opinion withdrawn";
  - a later decision in the same docket with `en banc`.
- Lean: `SameCaseEvent.rehearingEnBancGranted (vacatesPanel : Bool)`, with `vacatesPanel` from a per-circuit table.

**Rule F9 — Unpublished / non-precedential dispositions.**
- FRAP 32.1 (adopted 12 Apr 2006, effective 1 Dec 2006) permits citation of unpublished federal appellate dispositions **"issued on or after January 1, 2007"**. It does *not* decide their precedential weight [S: https://www.fjc.gov/content/citing-unpublished-federal-appellate-opinions-issued-2007; https://www.law.cornell.edu/rules/frap/rule_32-1].
- Per-circuit rules [S: FJC table, Reagan, 9 Mar 2007, 241 F.R.D. 328, https://www.fjc.gov/sites/default/files/2012/CitRules.pdf, plus later rules as noted]:

| Circuit | Rule | Precedential status | Citation before 2007 |
|---|---|---|---|
| 1st | 1st Cir. R. 32.1.0(a) | Not binding [L] | Any date permitted |
| 2d | 2d Cir. R. 32.1.1 (formerly § 0.23) | Summary orders have **no precedential effect** | Before 1 Jan 2007: prohibited except same case / related case / estoppel |
| 3d | I.O.P. 5.7 | Not precedential; "do not circulate to the full court" | Permitted, discouraged |
| 4th | 4th Cir. R. 32.1 | Not binding [L] | Pre-2007 disfavored unless no published opinion "would serve as well" |
| 5th | 5th Cir. R. 47.5.3, 47.5.4 | **Unpublished issued before 1 Jan 1996 ARE precedent; on or after 1 Jan 1996 are NOT** (except res judicata etc.) | Permitted |
| 6th | 6th Cir. R. 32.1(b) (formerly 28(g)) | Not binding [L] | Permitted |
| 7th | 7th Cir. R. 32.1(b), (d) | "Orders" are not precedents | Pre-2007 prohibited except preclusion / law of the case |
| 8th | 8th Cir. R. 32.1A | "They are not precedent" | Pre-2007 "generally should not be cited" |
| 9th | 9th Cir. R. 36-3 | Not precedent | Pre-2007 prohibited except as listed |
| 10th | 10th Cir. R. 32.1(A) | "Not precedential, but may be cited for their persuasive value" | Permitted |
| 11th | 11th Cir. R. 36-2 | "Not considered binding precedent" | Permitted |
| D.C. | D.C. Cir. R. 32.1(b)(1) | Unpublished dispositions **entered on or after 1 Jan 2002 "may be cited as precedent"**; before 2002 "are not to be cited as precedent". D.C. Cir. R. 36(e)(2) adds that a panel's choice not to publish means it "sees no precedential value" [L] | Pre-2002 prohibited |
| Fed. | Fed. Cir. R. 32.1(d) | "Will not give one of its own nonprecedential dispositions the effect of binding precedent" | Pre-2007 discouraged |

- Detection:
  - reporter `F. App'x` / `Fed. Appx.` (2001–);
  - a "Table" citation in F.2d/F.3d (e.g. `52 F.3d 1067 (table)`), the pre-2001 unpublished channel;
  - text banners: "NOT FOR PUBLICATION", "NONPRECEDENTIAL DISPOSITION", "UNPUBLISHED", "NOT PRECEDENTIAL", "SUMMARY ORDER", "Pursuant to 5TH CIR. R. 47.5, the court has determined that this opinion should not be published", "Unpublished opinions are not binding precedent in this circuit";
  - a `WL`-only citation.
- Lean: `Publication := published | unpublished | table | summaryOrder | nonprecedential`. Force is given by `unpubForce : Court → Date → Publication → Force`. The table is date-keyed: the 5th Cir. 1996 cutoff and the D.C. Cir. 2002 cutoff are **date-dependent force**, not just citability.

**Rule F10 — Inherited precedent after circuit splits.**
- **11th Circuit** (created 1 Oct 1981 by the Fifth Circuit Court of Appeals Reorganization Act of 1980, Pub. L. 96-452). It adopted as binding "the decisions of the former Fifth Circuit … handed down prior to the close of business on" **30 Sept 1981**.
  - Source: *Bonner v. City of Prichard*, 661 F.2d 1206, 1209 (11th Cir. 1981) (en banc) [S: https://openjurist.org/661/f2d/1206].
  - Binding on the 11th Cir. itself and on the district and bankruptcy courts of the circuit [S].
  - Only the 11th Cir. en banc can overrule such a decision (*Bonner* at 1209–11) [L].
- **Unit B**: decisions of the former Fifth Circuit's Unit B (the administrative unit for Alabama, Florida and Georgia in its last year) issued *after* 30 Sept 1981 also bind the 11th Cir.
  - *Stein v. Reynolds Securities, Inc.*, 667 F.2d 33, 34 (11th Cir. 1982) [L — not verified this pass].
  - Unit A decisions after the split are 5th Cir. law [L].
- **5th Circuit** keeps all pre-split Fifth Circuit law as its own [L].
- **10th Circuit** (created 1929 from the 8th Cir., Act of 28 Feb 1929, 45 Stat. 1346 [L]). It declined to treat pre-1929 8th Cir. decisions as binding: *Estate of McMorris*, 243 F.3d 1254, 1258 (10th Cir. 2001) [S via Walker].
- Detection:
  - court = "United States Court of Appeals for the Fifth Circuit" with decided ≤ 1981-09-30 → also `inheritedBy ca11`;
  - "Unit B" in the header or text, decided > 1981-09-30 → `inheritedBy ca11`.
- Lean: `Adoption {adopter : CourtId, source : CourtId, upTo : Date, filter : Decision → Bool, force : Force}`. Adopted decisions behave as decisions *of the adopter* for `binds` and `mayOverrule` (only the adopter's en banc may overrule them).

**Rule F11 — The Federal Circuit.**
- (a) **Predecessor adoption.** On its creation, 1 Oct 1982 (Federal Courts Improvement Act of 1982, Pub. L. 97-164), the court adopted as binding "the holdings of our predecessor courts, the United States Court of Claims and the United States Court of Customs and Patent Appeals, announced by those courts before the close of business September 30, 1982".
  - Source: *South Corp. v. United States*, 690 F.2d 1368, 1370 (Fed. Cir. 1982) (en banc) [L].
  - Only the Fed. Cir. en banc may overrule them.
  - Court of Claims *trial division* decisions are not included [L].
- (b) **Subject-matter binding, not geographic.** The Federal Circuit binds:
  - district courts nationwide on issues within its exclusive jurisdiction (patent law; 28 U.S.C. § 1295);
  - the Court of Federal Claims, the Court of International Trade, the Court of Appeals for Veterans Claims, the MSPB and the PTAB.
- On non-patent issues in patent cases, it applies **regional circuit law**:
  - *Panduit Corp. v. All States Plastic Mfg.*, 744 F.2d 1564, 1574–75 (Fed. Cir. 1984) [L];
  - *Atari, Inc. v. JS&A Grp.*, 747 F.2d 1422 (Fed. Cir. 1984) (en banc) [L];
  - *Midwest Indus. v. Karavan Trailers*, 175 F.3d 1356 (Fed. Cir. 1999) (en banc in part) [L].
- So in a patent case, a district court is bound by the Fed. Cir. on patent issues and by its regional circuit on procedure.
- (c) **Successor trial courts.** The Court of Claims trial division became the U.S. Claims Court (1 Oct 1982), renamed the U.S. Court of Federal Claims (29 Oct 1992) [L]. The U.S. Customs Court became the Court of International Trade (1 Nov 1980) [L].
- Lean: `binds a b issue` must take an `IssueDomain` (`federalPatent`, `federalGeneral`, `stateLaw s`, `tax`, …). Each `Court` gets a `jurisdictionalReach : IssueDomain → Set Court` override. Fed. Cir.: `reach federalPatent = all district courts`.

**Rule F12 — The Tax Court (the *Golsen* rule).**
- The Tax Court follows the precedent of the court of appeals to which the case is appealable, which is ordinarily the taxpayer's residence circuit (26 U.S.C. § 7482(b)).
  - *Golsen v. Commissioner*, 54 T.C. 742, 757 (1970), aff'd, 445 F.2d 985 (10th Cir. 1971) [L].
- Its own decisions bind the Tax Court in later cases as a matter of stare decisis. Regular (division) opinions are precedential; memorandum opinions and summary opinions (§ 7463(b)) are not [L].
- History [L]:
  - Board of Tax Appeals (1924);
  - renamed Tax Court of the United States (1942);
  - Article I U.S. Tax Court (1969).
- Lean: `binds (circuit k) taxCourt` *conditional on the case's appeal venue*. That is a per-decision field `appealVenue : Option Circuit`, or a per-issue table.

**Rule F13 — District courts do not bind themselves or each other.**
- "A decision of a federal district court judge is not binding precedent in either a different judicial district, the same judicial district, or even upon the same judge in a different case."
  - *Camreta v. Greene*, 563 U.S. 692, 709 n.7 (2011) (quoting 18 J. Moore et al., Moore's Federal Practice § 134.02[1][d]) [L];
  - *Threadgill v. Armstrong World Indus.*, 928 F.2d 1366, 1371 (3d Cir. 1991) [L].
- Three-judge district courts (28 U.S.C. § 2284) are not precedent beyond the case. A SCOTUS summary affirmance of one is precedent (F2).
- **Bankruptcy courts** are units of the district court (28 U.S.C. § 151). Most courts hold that a district judge's decision does not bind a bankruptcy judge in other cases:
  - *In re Carrozzella & Richardson*, 255 B.R. 267, 272 (D. Conn. 2000) [S, quoted in Walker n.48];
  - *In re Phipps*, 217 B.R. 427, 430 (Bankr. W.D.N.Y. 1998) [S];
  - contra, deferential practice: *In re Shattuc Cable*, 138 B.R. 557, 567 (Bankr. N.D. Ill. 1992) [S].
- **Bankruptcy appellate panels** (28 U.S.C. § 158(b); currently 1st, 6th, 8th, 9th and 10th Cir.; the 2d Cir. BAP ran c.1996–2000 [U]): their effect is **unsettled**.
  - 9th Cir. BAP decisions do not bind district courts: *Bank of Maui v. Estate Analysis, Inc.*, 904 F.2d 470, 472 (9th Cir. 1990) [L].
  - Whether they bind bankruptcy courts is contested, within and across circuits [S: secondary sources; ABI commentary].
  - BAP panels generally treat earlier BAP decisions as near-binding [U].
- Lean:
  - `Tier.trial` courts get `selfBinding := false`;
  - BAP is its own tier `bap` with `bindsBankruptcyCourtsOfCircuit : Circuit → Force`, default `persuasive` with flag `[U]`.

**Rule F14 — Intervening higher authority (abrogation) as a status change.**
- A circuit precedent stops binding when a later SCOTUS (or en banc) decision is "clearly irreconcilable" with it (9th), undermines it "to the point of abrogation" (11th), and so on (F7 table). This holds even if no court has yet said so.
- Courts then write "abrogated by", "abrogated on other grounds by" or "recognized as abrogated by".
- Lean: `Treatment.abrogated (by := higherDecision) (recognizedIn := Option Decision)`.
  - The *effective date* of the status change is the **higher decision's date**, not the recognizing decision's.
  - The recognizing decision is evidence, not cause.
  - This is the main way v1's "overruling by a court with power" misses real status changes: SCOTUS does not name every circuit case it abrogates.

---

## 2. Federal courts on state law; state courts on federal law

**Rule E1 — *Erie*: on state-law issues, federal courts are bound by the state's highest court.**
- *Erie R.R. v. Tompkins*, 304 U.S. 64, 78 (1938), decided **25 Apr 1938** [L], overruling *Swift v. Tyson*, 41 U.S. (16 Pet.) 1 (1842).
- Before 25 Apr 1938, on matters of "general" (common) law, federal courts exercised independent judgment. **Pre-1938 federal decisions on general common law have no authority as state law afterwards.**
- Elaborations [L]:
  - The highest court's decisions are binding.
  - Intermediate state appellate decisions are "datum[s] … not to be disregarded … unless [the federal court] is convinced by other persuasive data that the highest court of the state would decide otherwise": *West v. AT&T*, 311 U.S. 223, 237 (1940); *Fidelity Union Trust Co. v. Field*, 311 U.S. 169 (1940).
  - State trial-court decisions are not controlling: *King v. Order of United Commercial Travelers*, 333 U.S. 153, 160–61 (1948).
  - Absent a highest-court ruling, the federal court predicts, giving "proper regard" to lower state courts: *Comm'r v. Estate of Bosch*, 387 U.S. 456, 465 (1967).
  - Courts of appeals review state-law determinations de novo: *Salve Regina College v. Russell*, 499 U.S. 225, 231 (1991).
- A circuit's *Erie* prediction binds its district courts and later panels, until an intervening decision of the state's highest court (or, in many circuits, a clear intermediate-court line) shows it wrong. A panel may then depart without en banc review [L, general practice; e.g. 9th Cir. *Owen ex rel. Owen v. United States*, 713 F.2d 1461, 1464 (1983); U as to every circuit].
- **Federal decisions on state law never bind state courts.**
- Detection: the issue domain is state law. Hard to detect: it needs the citation targets (state statutes or state cases) or the issue extraction. Diversity jurisdiction ("diversity of citizenship", 28 U.S.C. § 1332) is a strong signal.
- Lean: `binds (stateHigh s) (fedCourt) (stateLaw s) = binding` when `date ≥ 1938-04-25`. Before 1938: `persuasive` for general-law issues, `binding` for "local" law (state statutes, real property), as under *Swift* [L].
- Corollary: `binds (fedCourt) (stateCourt s) (stateLaw s) = persuasive`, always.

**Rule E2 — Certified questions.**
- Federal courts (and some state courts) may certify unsettled state-law questions to the state's highest court:
  - *Lehman Bros. v. Schein*, 416 U.S. 386, 390–91 (1974) [L];
  - *Arizonans for Official English v. Arizona*, 520 U.S. 43, 76–79 (1997) [L];
  - Uniform Certification of Questions of Law Act (1967; revised 1995) [L].
- Almost every state accepts certified questions. North Carolina is the usual exception [U — check per state].
- The answer is a decision of the state's highest court. It is binding state law for all courts, and the certifying court must apply it.
- Example: *Banks v. Int'l Rental & Leasing Corp.*, 55 V.I. 967 (V.I. 2011), answering a 3d Cir. certification; applied at 680 F.3d 296 (3d Cir. 2012) [S].
- Detection: "certified question", "question certified from the United States Court of Appeals", "we answer the certified question"; a state-high-court decision whose caption names a federal court.
- Lean: `DecisionForm.certifiedAnswer (from : CourtId)`. Treat it as an ordinary highest-court decision on the issue, plus a `sameCaseLink` to the certifying federal case.

**Rule E3 — State courts on federal questions: bound only by SCOTUS.**
- Lower federal courts are not binding on state courts on federal law:
  - *Johnson v. Williams*, 568 U.S. 289, 305 (2013) ("the views of the federal courts of appeals do not bind the California Supreme Court when it decides a federal constitutional question") [L];
  - *ASARCO Inc. v. Kadish*, 490 U.S. 605, 617 (1989) (state courts render binding judgments on their own interpretations of federal law) [L];
  - *Lockhart v. Fretwell*, 506 U.S. 364, 375–76 (1993) (Thomas, J., concurring) [L].
- Walker 2022 surveys 46 states as not bound [S: Walker ¶23 and n.75, with a citation for each state].
- **States reported as treating lower federal courts as binding on federal law** [S as to Walker's report; U as to current law, since several citations are old]:

| State | Authority | Note |
|---|---|---|
| Maine | *Littlefield v. State, Dep't of Human Servs.*, 480 A.2d 731, 737 (Me. 1984) | |
| Nebraska | *Anderson v. HMO Neb.*, 1993 WL 61839 (Neb. Ct. App. 1993) | Intermediate court, unpublished |
| New Hampshire | *Desmarais v. Joy Mfg. Co.*, 538 A.2d 1218, 1220 (N.H. 1988) | |
| South Dakota | *Cloud v. Leapley*, 521 N.W.2d 118, 122 (S.D. 1994) | |
| South Carolina | One 2013 Court of Appeals statement that 4th Cir. decisions bind | Contested, single intermediate-court statement [U] |
| Tennessee | Historical Fourth Amendment carve-out: federal search-and-seizure cases "must be abided by" | Older; the general rule is not bound [S via Walker] |

- Lean: `stateFollowsCircuit : State → Date → Option Force`, default `persuasive`. These are table rows with `[U]`. A *reliable* rule is only "SCOTUS binds; all else persuasive".

---

## 3. Courts of last resort: the 50 states, DC and the territories

### 3.1 General rules

**Rule H1 — The highest court binds every court of its system on that system's law.**
- Walker 2022 n.59 gives a citation for every state [S].
- Two quasi-exceptions:
  - **Kansas**: the Court of Appeals has said it may depart from Kansas Supreme Court precedent when there is "some indication" the Supreme Court is departing from it. *State v. Miller*, 629 P.2d 748, 750 (Kan. Ct. App. 1981); recognized by the Kansas Supreme Court in 2016 per Curtis [S: Curtis, *State Court Structure and Precedent*, 45 N.C. Cent. L. Rev. 164, 185–86 (2023), https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4269671].
  - **Louisiana**, a civil-law jurisdiction: in theory *jurisprudence constante* (a consistent line of cases) rather than stare decisis. In practice lower courts follow the Louisiana Supreme Court [L].
- The highest court is *not* bound by itself. It may overrule its own precedent, under its own stare decisis factors.

**Rule H2 — Dual courts of last resort.**
- **Texas**:
  - Supreme Court of Texas: last resort in civil (and juvenile) cases.
  - Court of Criminal Appeals: last resort in criminal cases (Tex. Const. art. V §§ 3, 5) [S via Curtis n.97–99].
  - The CCA has existed under that name since 1891; it was the Court of Appeals from 1876 to 1891, with criminal and some civil jurisdiction [L].
  - Each binds lower courts *in its domain*. On an issue arising in both (e.g. the construction of a statute used civilly and criminally), the two are not bound by each other [L].
- **Oklahoma**:
  - Supreme Court: civil.
  - Court of Criminal Appeals: criminal (Okla. Const. art. VII § 4). It was the "Criminal Court of Appeals" from 1907/08 and renamed in 1959 [L].
  - The Supreme Court decides jurisdictional conflicts between the two [S: art. VII § 4 quoted in Curtis n.100].
- Lean: a system has `lastResort : IssueDomain → CourtId`, keyed by `civil | criminal`. Every decision needs `caseKind : civil | criminal | juvenile | …`; the court ID alone suffices for the CCA, but a Texas court of appeals hears both.

**Rule H3 — Successor courts inherit binding force.**
- When a court of last resort is renamed or replaced, its decisions keep binding force as decisions of the court of last resort. Lower courts must follow them, and only the new highest court may overrule them.
- Kentucky codifies this: "The Court of Appeals is bound by and shall follow applicable precedents established in the opinions of the Supreme Court and its predecessor court." SCR 1.030(8)(a) [S: https://www.courtrules.net/kentucky/kentucky-supreme-court-rules/rule-1-030]; *Smith v. Vilvarajah*, 57 S.W.3d 839, 841 (Ky. App. 2000) [S].
- Lean: `Succession {old : CourtId, new : CourtId, date : Date, kind : rename | replace | split | merge}`. `effectiveCourt (d : Decision)` maps a decision to the court that now holds its authority. `binds` and `mayOverrule` use the *successor* for old decisions, and the *dated tier* for the deciding court at decision time.

### 3.2 Court of last resort by jurisdiction

Name changes and history. Dates are [L] unless marked otherwise. Intermediate courts are in §4.

| Jurisdiction | Court of last resort (current) | History that matters for detection |
|---|---|---|
| Alabama | Supreme Court of Alabama | Unchanged |
| Alaska | Supreme Court of Alaska (1959) | Before statehood: District Court for the Territory of Alaska, with appeals to the 9th Cir. Whether 9th Cir. territorial decisions bind is [U] |
| Arizona | Arizona Supreme Court | Territorial Supreme Court (1864–1912); statehood 14 Feb 1912. Territorial decisions treated as the state's [U] |
| Arkansas | Arkansas Supreme Court | |
| California | Supreme Court of California | 1885–1904: the Supreme Court Commission; commissioners' opinions adopted by the court carry its authority [U] |
| Colorado | Colorado Supreme Court | Territorial Supreme Court (1861–1876) |
| Connecticut | Connecticut Supreme Court | **"Supreme Court of Errors"** until renamed by the 1965 constitution (effective Dec 1965) [L]. Same court |
| Delaware | Delaware Supreme Court (est. 1951) | **"Court of Errors and Appeals"** was the court of last resort until 1951 (const. amendment) [L]. Successor: `replace` |
| District of Columbia | D.C. Court of Appeals | The court of last resort for D.C. local law **from 1 Feb 1971** (D.C. Court Reform and Criminal Procedure Act of 1970). Before that, the D.C. Circuit (and its predecessor, the Court of Appeals of D.C., 1893) was the highest court for D.C. local law. **D.C. Circuit decisions rendered before 1 Feb 1971 bind the D.C. Court of Appeals; later ones do not** (*M.A.P. v. Ryan*, 285 A.2d 310, 312 (D.C. 1971)) [S]. The D.C. Court of Appeals was named the Municipal Court of Appeals before 1962 and was an intermediate court then [L] |
| Florida | Supreme Court of Florida | |
| Georgia | Supreme Court of Georgia (1845/46) | Before 1845 there was no supreme court; the superior courts were the highest [L] |
| Hawaii | Supreme Court of Hawaiʻi | Kingdom → Territory (1900) → State (1959). Kingdom- and territorial-era decisions are treated as the court's own [U] |
| Idaho | Idaho Supreme Court | Territorial court before 1890 |
| Illinois | Supreme Court of Illinois | |
| Indiana | Indiana Supreme Court | |
| Iowa | Iowa Supreme Court | |
| Kansas | Kansas Supreme Court | Supreme Court commissioners (c.1887–1890s, and others) [U] |
| **Kentucky** | Supreme Court of Kentucky | **The "Court of Appeals of Kentucky" was the court of last resort until the 1975 Judicial Article (ratified Nov 1975; effective 1 Jan 1976). From 1976 "Court of Appeals" is the new intermediate court.** The old Court of Appeals' opinions are "predecessor court" precedent that binds the new Court of Appeals (SCR 1.030(8)(a)) [S]. Detection: court name "Court of Appeals of Kentucky" + decided < 1976-01-01 → last resort. The CAP reporter cue: Ky. Reports / S.W.2d with "Ky." vs "Ky. App." |
| Louisiana | Supreme Court of Louisiana | Civil-law jurisdiction; *jurisprudence constante* |
| Maine | Supreme Judicial Court ("sitting as the Law Court" on appeals) | Court name strings vary: "Supreme Judicial Court of Maine" |
| **Maryland** | Supreme Court of Maryland | **"Court of Appeals of Maryland" until 14 Dec 2022**: constitutional amendment approved 8 Nov 2022; the renaming took effect 14 Dec 2022 [L — date widely reported; not re-fetched]. The Court of Special Appeals became the **Appellate Court of Maryland** on the same date. Detection: "Court of Appeals of Maryland" = last resort (all dates); "Court of Special Appeals" = intermediate |
| Massachusetts | Supreme Judicial Court | |
| Michigan | Michigan Supreme Court | |
| Minnesota | Minnesota Supreme Court | |
| Mississippi | Supreme Court of Mississippi | **High Court of Errors and Appeals** (1832–1869/70) was the predecessor [L] |
| Missouri | Supreme Court of Missouri | Sits "en banc" or (historically) in divisions; both are the court of last resort. Commissioners' opinions adopted by the court [U] |
| Montana | Montana Supreme Court | Territorial court before 1889 |
| Nebraska | Nebraska Supreme Court | Supreme Court Commission (c.1890s–1900s) opinions [U] |
| Nevada | Supreme Court of Nevada | |
| New Hampshire | New Hampshire Supreme Court | Pre-1876 names ("Superior Court of Judicature", "Supreme Judicial Court") [U on exact sequence] |
| **New Jersey** | Supreme Court of New Jersey (est. 15 Sept 1948) | **Before 15 Sept 1948, the "Court of Errors and Appeals" was the court of last resort, and the old "Supreme Court of New Jersey" was a lower court** (general jurisdiction, also hearing some appeals). Detection: "Supreme Court of New Jersey" + decided < 1948-09-15 → tier `appellate`/`trial`, *not* last resort. The Court of Chancery and Prerogative Court were abolished in 1948 [L] |
| New Mexico | New Mexico Supreme Court | Territorial before 1912 |
| **New York** | **Court of Appeals** (since 1847) | **Naming quirk: the "Supreme Court" is the general trial court.** Its Appellate Division (since 1 Jan 1896) is the intermediate court; the Appellate Term hears appeals from lower trial courts. Historic hierarchy: the Court for the Trial of Impeachments and the Correction of Errors (1777–1847) was the court of last resort; the Supreme Court of Judicature (1691–1847) was below it; General Term of the Supreme Court (1847–1895) was intermediate. The Commission of Appeals (1870–1875) and the Second Division of the Court of Appeals (1889–1892) decided cases with Court of Appeals authority [U on weight]. Detection must key on the *exact* court string: "Court of Appeals of New York" vs "Supreme Court, Appellate Division, First Department" vs "Supreme Court, New York County" |
| North Carolina | Supreme Court of North Carolina | |
| North Dakota | North Dakota Supreme Court | **Dakota Territory** Supreme Court (1861–1889) is the predecessor of *both* North and South Dakota (a one-to-many succession) [U as to whether each state treats it as binding] |
| Ohio | Supreme Court of Ohio | **Syllabus rule**: before 1 May 2002, only the syllabus stated the law of the case (former S.Ct.R.Rep.Op. 1(B)). Since 2002, the law is in the syllabus *and* the text (Rep.Op.R. 2.2) [L — verify the rule numbers]. This bears directly on the holdings model |
| Oklahoma | Supreme Court (civil) / Court of Criminal Appeals (criminal) | Supreme Court Commission opinions (1909–1930s) [U] |
| Oregon | Oregon Supreme Court | |
| Pennsylvania | Supreme Court of Pennsylvania | An even split affirms with no precedent |
| Rhode Island | Rhode Island Supreme Court | |
| South Carolina | Supreme Court of South Carolina | |
| South Dakota | South Dakota Supreme Court | Dakota Territory predecessor (see ND) |
| Tennessee | Tennessee Supreme Court | |
| **Texas** | Supreme Court (civil) / Court of Criminal Appeals (criminal) | **Commission of Appeals** (1879–1892; 1918–1945). Its opinions marked **"opinion adopted"** carry Supreme Court authority. "**Holding approved**" approves the holding on the questions discussed, not all the reasoning. "**Judgment adopted**" / "judgment approved" approves only the judgment (*McKenzie v. Withers*, 206 S.W. 503 (Tex. 1918) [S]; exact weights [U]). Detection: the court string "Commission of Appeals of Texas" and the notation at the end of the opinion |
| Utah | Utah Supreme Court | Territorial before 1896 |
| Vermont | Vermont Supreme Court | |
| **Virginia** | Supreme Court of Virginia | **"Supreme Court of Appeals of Virginia"** until the 1971 constitution (effective 1 July 1971) [L]. Same court, renamed |
| Washington | Washington Supreme Court | Territorial before 1889 |
| West Virginia | **Supreme Court of Appeals** of West Virginia (still the name) | **Syllabus points**: new points of law are announced in syllabus points (W. Va. Const. art. VIII § 4). Signed opinions with new syllabus points are the highest precedent; memorandum decisions (R.A.P. 21) have limited precedential value: *State v. McKinley*, 234 W. Va. 143, 764 S.E.2d 303 (2014) [L] |
| Wisconsin | Wisconsin Supreme Court | |
| Wyoming | Wyoming Supreme Court | |
| Puerto Rico | Tribunal Supremo de Puerto Rico | **Decisions were reviewable by the 1st Cir. until 30 Aug 1961** (then certiorari to SCOTUS) [L]. 1st Cir. decisions on P.R. law before 1961 [U as to current weight]. Civil-law tradition; opinions mostly in Spanish |
| Guam | Supreme Court of Guam (operational 1996) | Before that, the Appellate Division of the District Court of Guam. **9th Cir. certiorari jurisdiction over the Supreme Court of Guam** existed until Pub. L. 108-378 (2004) [L/U on date]. Ninth Cir. decisions on Guam law [U] |
| Northern Mariana Islands | NMI Supreme Court (1989) | 9th Cir. certiorari phase until 2004 [U] |
| U.S. Virgin Islands | Supreme Court of the Virgin Islands (first sat Jan 2007) | Before: the Appellate Division of the District Court of the V.I., with appeals to the 3d Cir. **3d Cir. certiorari jurisdiction ended 28 Dec 2012** (Pub. L. 112-226) [S: per a reported 3d Cir. en banc statement; not seen in the statute text]. The V.I. Supreme Court is not bound to follow a 3d Cir. reading of local law that it finds "manifestly erroneous", and the 3d Cir. defers to it on local law (*Banks*, 55 V.I. 967 (2011); 680 F.3d 296 (3d Cir. 2012)) [S]. Pre-2007 Appellate Division and 3d Cir. decisions on V.I. law: legacy precedent with reduced force [U] |
| American Samoa | High Court of American Samoa, Appellate Division | No federal appellate review |
| Tribal courts | Separate sovereign systems | Outside the federal/state hierarchy. They bind nothing outside the tribe and are bound only by SCOTUS on federal questions [L]. Model as separate systems |

**Rule H4 — Commission and adoption decisions.**
- Several states had supreme-court commissions or commissioners whose opinions became court opinions only when adopted: Texas, California, Missouri, Nebraska, Oklahoma, Kansas, and New York's Commission of Appeals.
- Lean: `DecisionForm.commission (adoption : adopted | holdingApproved | judgmentOnly | none)`, with force `binding`, `binding (result + discussed questions)`, `resultOnly` and `persuasive` respectively. Weights other than Texas "opinion adopted" are [U].

---

## 4. Intermediate appellate courts, state by state

### 4.1 The dimensions

Every state with an intermediate appellate court (IAC) needs these parameters:

- **H (horizontal)**: does one panel or district bind another?
  - `strong`: a later panel is bound; only en banc, a conflict panel or a higher court may depart.
  - `soft`: the court adheres to its precedent but may overrule it, under a stare decisis test.
  - `none`: other panels, districts or divisions are persuasive only.
  - `withinUnitOnly`: bound within a district or department, not across.
- **V (vertical scope)**: which IAC decisions bind a given trial court?
  - `statewide`: any published IAC decision.
  - `ownUnitThenAny`: the trial court's own district/department first; absent one, any other unit's decision binds; with conflicting other units and none from its own, the trial court chooses.
  - `ownUnitOnly`: its own unit binds; others are persuasive.
  - `statewideChooseOnConflict`: any decision binds; with a conflict, the trial court chooses.
- **U (unpublished)**: the precedential status of unpublished decisions, and any citability cutoff date.
- **C (conflict mechanism)**: how conflicts are resolved — en banc, conflict panel, certification, transfer.

### 4.2 The named patterns (verified detail)

**S-CA — California.**
- H = `none`. There is no horizontal stare decisis among Courts of Appeal districts or divisions, nor within one. "The opinion of another appellate division constitutes, at most, persuasive authority" (*People v. Gourley*, 130 Cal. Rptr. 3d 181, 186 (App. Dep't Super. Ct. 2011)) [S via Walker]. See also *In re Marriage of Shaban*, 88 Cal. App. 4th 398, 409 (2001) [L].
- V = `statewideChooseOnConflict`. All superior courts must follow any published Court of Appeal decision. Where published decisions conflict, the trial court "can and must make a choice": *Auto Equity Sales, Inc. v. Superior Court*, 57 Cal. 2d 450, 455–56 (1962) [L].
- U: unpublished opinions "must not be cited or relied on by a court or a party in any other action", except for law of the case, res judicata or collateral estoppel, or the same defendant (Cal. Rules of Court 8.1115(a)–(b)) [S: https://www.courts.ca.gov/cms/rules/index/eight/rule8_1115].
  - Partial publication: Rule 8.1110 [L].
  - Depublication by order of the Supreme Court: Rule 8.1125. Depublication "is not an expression of the court's opinion of the correctness of the result" [L].
- **Review granted** — date-ranged rule [S]:
  - **Before 1 July 2016**: a grant of review automatically depublished the Court of Appeal opinion. It became uncitable (former Rule 8.1105(e)(1) / former Rule 976).
  - **From 1 July 2016** (Rule 8.1115(e)(1)): a published opinion stays published but, pending review, has "no binding or precedential effect, and may be cited for potentially persuasive value only".
  - After the Supreme Court decides (e)(2), the opinion "is citable and has binding or precedential effect, except to the extent it is inconsistent with the decision of the Supreme Court or is disapproved by that court".
  - The Supreme Court may order otherwise at any time (e)(3).
  - On dismissal of review, the opinion regains binding effect.
  - Administrative Order 2021-04-21: for opinions with review granted on or after 21 Apr 2021, a superior court may cite a review-granted opinion to show a conflict and choose under *Auto Equity*.
  - A transfer with directions to vacate (on or after 21 Apr 2021) makes a published opinion uncitable.
  - Rule history: adopted as Rule 977, effective 1 Jan 2005; renumbered 8.1115 on 1 Jan 2007; (e) added 1 July 2016.
- **"Disapproved"**: when the Supreme Court "disapproves" a Court of Appeal opinion (not under review), that opinion is overruled to the extent of the disapproval.
- Appellate divisions of the superior court: their published opinions bind trial courts in their county; their weight elsewhere is [U].
- Detection:
  - court strings "Court of Appeal, Second District, Division 3, California" (district and division present);
  - `Cal.App.` / `Cal.App.2d…5th` = published; Cal. Rptr.-only citations = possibly unpublished;
  - "review granted", "depublished", "ordered not to be officially published", "Review granted [date], S######", "disapproved on another ground in".
- Lean:
  - `State.horizontal = none`, `trialScope = statewideChooseOnConflict`;
  - `SameCaseEvent.reviewGranted (d)` sets force to `persuasive` from d (or `notCitable` if d < 2016-07-01);
  - `SameCaseEvent.reviewDismissed` restores it;
  - `SameCaseEvent.depublished` sets `notCitable`;
  - `Treatment.disapproved` by the CA Supreme Court counts as `overruledToExtent`.

**S-FL — Florida.**
- Six District Courts of Appeal:
  - 1st–3d created 1957;
  - 4th 1965;
  - 5th 1979;
  - **6th effective 1 Jan 2023** [L].
- H = `withinUnitOnly`:
  - "as between District Courts of Appeal, a sister district's opinion is merely persuasive" (*State v. Hayes*, 333 So. 2d 51, 53 (Fla. 4th DCA 1976), quoted in *Pardo*) [S];
  - within a DCA, panels are bound and only the court **en banc** may "recede" (Fla. R. App. P. 9.331) [L].
- V = `ownUnitThenAny`: "in the absence of interdistrict conflict, district court decisions bind all Florida trial courts" (*Pardo v. State*, 596 So. 2d 665, 666 (Fla. 1992)) [S].
  - With an interdistrict conflict, a trial court follows its own district.
  - Where its own district is silent and the others conflict, it may choose [L, commonly stated; e.g. *State v. Hayes*].
- U: per curiam affirmances without opinion (PCAs) have no precedential value: *Dep't of Legal Affairs v. District Court of Appeal*, 434 So. 2d 310, 311–13 (Fla. 1983) [L].
- C: Florida Supreme Court discretionary review for express and direct conflict, or certified conflict (Fla. Const. art. V § 3(b)(3)–(4)) [L].
- Vocabulary: "**receded from**" means the issuing court overruled its own precedent. "**Disapproved**" (Supreme Court on a DCA decision not under review) and "**quashed**" (the decision under review) are also used.
- Successor issue: when the 6th DCA was created, it adopted a statement on which existing DCA precedent binds it [U — confirm the 6th DCA's first en banc pronouncement; reportedly it treats 2d DCA precedent as non-binding but persuasive].
- Lean: `trialScope = ownUnitThenAny`, `horizontal = withinUnitOnly`, `Treatment.recededFrom` counts as `overruled` (same court, en banc).

**S-IL — Illinois.**
- Appellate Court, five districts (the 1st District has divisions); since 2021 the districts were redrawn [L].
- H = `none`: "the opinion of one district, division, or panel of the appellate court is not binding on other districts, divisions, or panels".
  - *O'Casek v. Children's Home & Aid Soc'y*, 229 Ill. 2d 421, 440 (2008) [L];
  - *People v. Carpenter*, 228 Ill. 2d 250, 259 (2008) [L];
  - "One district of the appellate court is not in all instances bound to follow the decisions of other districts" (*People v. Ward*, 548 N.E.2d 1120, 1127 (Ill. App. 1989)) [S via Walker].
- V = `ownUnitThenAny`: "a circuit court must follow the precedent of the appellate court of its district, if such precedent exists; if no such precedent exists, the circuit court must follow the precedent of other districts" [S, quoted in Curtis].
  - *State Farm Fire & Cas. Co. v. Yapejian*, 152 Ill. 2d 533, 539–40 (1992) [L].
  - When other districts conflict and its own is silent, the circuit court may choose [L].
- U: Rule 23 orders. **Rule 23(b) orders entered on or after 1 Jan 2021 may be cited for persuasive purposes**; earlier ones and Rule 23(c) summary orders may not (Ill. S. Ct. R. 23(e)(1), as amended effective 1 Jan 2021) [S: https://illinoiscourts.gov/News/975].

**S-NY — New York.**
- Appellate Division, four departments since 1896.
- H = `none` across departments: one department is not bound by another [S via secondary: Schlam Stone NYLJ]. Within a department, a later panel follows department precedent [L].
- V = `ownUnitThenAny`. "The doctrine of stare decisis requires trial courts in this department to follow precedents set by the Appellate Division of another department until the Court of Appeals or this court pronounces a contrary rule" (*Mountain View Coach Lines v. Storms*, 102 A.D.2d 663, 664–65 (2d Dep't 1984)) [S].
  - Trial courts follow their own department first.
  - With conflicting other departments and a silent home department, the trial court chooses [S, secondary].
- The Appellate Term binds the lower courts within its district [L].
- Detection: department named in the court string ("Appellate Division of the Supreme Court of New York, Second Department"); the reporter `A.D.`, `A.D.2d`, `A.D.3d`.

**S-TX — Texas.**
- Courts of appeals (14 regional; the **15th Court of Appeals**, statewide, has existed since 1 Sept 2024 with jurisdiction over appeals involving the State [L]). They were the Courts of Civil Appeals until **1 Sept 1981**, when they gained criminal jurisdiction and were renamed [L].
- H = `withinUnitOnly`: each court of appeals follows its own precedent ("This Court is bound by … prior decisions of this Court", *Owen v. Jim Allee Imports*, 380 S.W.3d 276, 284 (Tex. App. 2012)) [S via Walker]. Sister courts' decisions are persuasive.
- **Transfer cases** — Tex. R. App. P. 41.3: in a case transferred under docket equalization (Gov't Code § 73.001), the transferee court "must decide the case in accordance with the precedent of the transferor court under principles of stare decisis if the transferee court's decision otherwise would have been inconsistent with the precedent of the transferor court" [S: rule text quoted at https://syfert.com/texas/sections/RAP/41.3.html].
  - Effective date reported as 1 Sept 2008 [U — not confirmed this pass].
  - A transferee court's decision does not clearly bind the transferor court [S, 5th Court of Appeals discussion].
- V: trial courts follow the court of appeals for their district. Practice on other courts' decisions is [U]: commonly persuasive, and binding absent a conflict in some accounts.
- **Supreme Court review notations** (they determine precedential weight) [S for (c); L for the rest]:
  - **Writ era** (before 1 Sept 1997). "Writ ref'd" meant the Supreme Court approved the opinion: it has the same precedential value as a Supreme Court opinion. "Writ ref'd n.r.e." (no reversible error; from 1927) means no approval of the reasoning. "Writ denied" and "writ dism'd w.o.j." add nothing.
  - **Petition era** (from 1 Sept 1997). Tex. R. App. P. 56.1(c): "Petition Refused … the court of appeals' opinion has the same precedential value as an opinion of the Supreme Court" [S]. "Pet. denied" and "pet. dism'd" add nothing.
  - Criminal: "PDR ref'd" adds no approval [L].
- U: Tex. R. App. P. 47.7. Civil memorandum opinions (from 1 Jan 2003) have precedential value [L]. Older civil "do not publish" opinions have none. Criminal "do not publish" opinions have no precedential value but may be cited (47.7(a)) [L].
- Detection: "Tex. App.—Houston [14th Dist.] 2010, pet. ref'd" style parentheticals inside citing decisions; "transferred from"; "Texas Court of Civil Appeals" + date.
- Lean:
  - `Decision.reviewNotation : Option TXNotation`, mapping `writRefused | petRefused` to force `asHighestCourt` (effectively promoting the opinion to last-resort authority);
  - `transfer (from := CourtId)` makes `binds transferor transferee` true *for that case*.

**S-MI — Michigan.**
- Court of Appeals (1965).
- H = `strong`, date-ranged. A published opinion **issued on or after 1 Nov 1990**, not reversed or modified by the Supreme Court or a special panel, binds later panels (MCR 7.215(J)(1)).
  - Published opinions issued before 1 Nov 1990 do not bind later panels against their judgment [S: secondary quotations of the rule and a Supreme Court order].
- C: **conflict-panel procedure**.
  - A panel that follows a binding opinion only because of (J)(1) must say so (J)(2).
  - The judges are polled on convening a 7-judge special panel (J)(3).
  - The special panel's decision binds (J)(5) [S].
- V = `statewide`.
- U: unpublished opinions are not binding (MCR 7.215(C)(1)) [L].
- Detection: "We follow [X] only because we are required to do so by MCR 7.215(J)(1)"; "conflict panel"; "special panel convened under MCR 7.215(J)".
- Lean:
  - `horizontalAt (state := MI) (date) = if date ≥ 1990-11-01 then strong else soft` — the rule keys on the *precedent's* date, not the later decision's;
  - `Bench.conflictPanel` counts as en banc.

**S-PA — Pennsylvania.**
- Superior Court (1895) and Commonwealth Court (1970), both intermediate, with different subject jurisdiction.
- H within each court = `strong`: a panel is bound by prior published panel decisions, and en banc review is needed to overrule [L, e.g. *Pledger v. Janssen Pharms.*, 198 A.3d 1126 (Pa. Super. 2018), cited in Walker n.60 for vertical force; U for the exact panel-binding cite].
- Across the two courts, neither binds the other; Commonwealth Court decisions are persuasive in Superior Court [L/U].
- U: Pa.R.A.P. 126(b) — non-precedential decisions may be cited for persuasive value. These are unpublished Superior Court memoranda **filed after 1 May 2019** and unreported Commonwealth Court memoranda **filed after 15 Jan 2008** [S: https://www.pabulletin.com/secure/data/vol49/49-18/653.html]. Earlier ones may not be cited (*Commonwealth v. Finnecy*, Pa. 2021) [S, secondary].
- Supreme Court: an evenly divided court affirms with no precedent; plurality opinions are not binding [L].

**S-GA — Georgia.**
- Court of Appeals (1906/07; 15 judges since 2016 [L]).
- **Binding test — date-ranged** [S: Ga. Ct. App. R. 33.2, https://www.courtrules.net/georgia/ga-court-of-appeals/rule-33-2]:
  - **Before 1 Aug 2020**: a division (three-judge) opinion is binding only if **all three judges fully concur**. If any judge concurs in the judgment only, concurs specially without full agreement, or dissents, the opinion (or that portion) is **"physical precedent only (citable as persuasive, but not binding, authority)"**. En banc: a majority fully concurring is binding.
  - **From 1 Aug 2020**: a published opinion "in which a majority of the judges fully concur in the rationale and judgment" is binding, for division and en banc decisions alike.
  - The rule text may still reference physical precedent for portions without a full-concurrence majority [U].
- Unreported decisions are neither physical nor binding precedent (Rule 33.2(b)) [S].
- Overruling: Rule 33.3. A division may overrule a prior decision only by unanimous vote; otherwise the matter goes to the whole court [S secondary; U on current text].
- Whole-court decisions bind divisions [L].
- Detection: concurrence lines at the end of the opinion — "concurs in judgment only", "concurs specially", "Dillard, J., concurs fully and specially" (full concurrence), "dissents"; judge counts; "physical precedent only" when cited.
- Lean:
  - `bindingIf (d) := d.date < 2020-08-01 → unanimousFullConcurrence d.panel ∧ … | majorityFullConcurrence`;
  - force per part = `binding | physicalPrecedent (≈ persuasive)`.

**S-OH — Ohio.**
- Courts of appeals, 12 districts (the 1912 constitution; renamed from circuit courts).
- H = `none` across districts, `soft` within one:
  - "a court of appeals … is not unalterably bound to follow the precedent of a rule previously announced or followed by such court" (*State v. George*, 362 N.E.2d 1223, 1231 (Ohio App. 1975)) [S via Walker];
  - the overruling test is in *Bouher v. Aramark Servs.*, 910 N.E.2d 40, 45 (Ohio App. 2009) [S].
- V = `ownUnitOnly`. Only Supreme Court decisions and reported decisions of the trial court's own district bind it; other districts are persuasive (*Stapleton v. Holstein*, 11th Dist. 1998) [S, secondary summary].
- C: conflict certification to the Supreme Court (Ohio Const. art. IV § 3(B)(4)) [L].
- U: since **1 May 2002**, court of appeals opinions may be cited as legal authority regardless of publication status (Rep.Op.R. 3.4, now 4.x) [L — verify the rule number and the date]. The weight given to unreported opinions before 2002 varied.
- Supreme Court syllabus rule: see §3.2.

**S-LA — Louisiana.**
- Courts of Appeal, five circuits (current structure 1960; 5th Circuit 1982) [L].
- H = `withinUnitOnly`: "law of the circuit" binds panels within a circuit [S]. Sister circuits "are not binding on us, [but] can certainly be persuasive" (*Orillion v. Allstate*, 690 So. 2d 846, 849 (La. App. 1997)) [S].
- V = `ownUnitOnly` (presumed) [U]. There is no clear authority on conflicting circuits for trial courts.
- C: five-judge panels when reversing or modifying with a dissent (La. Const. art. V § 8(B)) [L]; Supreme Court writ grants.
- Civil-law overlay: *jurisprudence constante* [L].

**S-WA — Washington.**
- Court of Appeals (1969), three divisions.
- H = `none`. "One division of the Court of Appeals should give respectful consideration to the decisions of other divisions … but is not bound by them". Conflicts are resolved by Supreme Court review (RCW 2.06.030) (*In re Pers. Restraint of Arnold*, 190 Wn.2d 136, 410 P.3d 1133 (2018)) [S].
- V: trial courts and conflicting divisions [U]. DeForrest, 48 Gonz. L. Rev. 455 (2012/13) discusses this.
- U: GR 14.1. Unpublished opinions filed **on or after 1 Mar 2013** may be cited as nonbinding authority [L].

**S-AZ — Arizona.**
- Court of Appeals (1965), Division One (Phoenix) and Division Two (Tucson), a single court.
- H = `soft`:
  - "while it is true that one division of the Court of Appeals is not bound by a decision of the other division, only the most cogent of reasons will justify a divergence" (*State v. Patterson*, 222 Ariz. 574, 218 P.3d 1031 (App. 2009)) [S];
  - "We consider decisions of coordinate courts as highly persuasive and binding, unless … clearly erroneous" (*Castillo v. Indus. Comm'n*, 520 P.2d 1142, 1148 (Ariz. App. 1974)) [S].
- V = `statewide`. Superior courts are bound by all Court of Appeals decisions regardless of division [S, secondary]. Conflicts [U].
- U: memorandum decisions issued **on or after 1 Jan 2015** may be cited for persuasive value (Ariz. R. Sup. Ct. 111(c)) [L].

**S-MO — Missouri.**
- Missouri Court of Appeals: one court with three districts (Eastern, Western, Southern), unified **1 Jan 1972** under the 1970 constitutional amendment. Before that, there were separate St. Louis (1875), Kansas City (1884) and Springfield (1909) Courts of Appeals [L].
- H = `soft`. A division that would not follow a previous decision of "an appellate court of this state" must go en banc within its district (Mo. Sup. Ct. Operating Rule 22.01) [S].
- Districts: not formally bound by one another [U].
- V: "decisions of a particular district [are] binding on all circuit courts" [S, annotation citing *Akins v. Director of Revenue*, 303 S.W.3d 563 (Mo. banc 2010); U as to the exact wording]. So `statewide`, with conflicts resolved by transfer to the Supreme Court (Mo. Const. art. V § 10) [L].
- Detection: "Missouri Court of Appeals, Eastern District, Division Four"; historic "St. Louis Court of Appeals" + date < 1972.

**S-NJ — New Jersey.**
- Appellate Division of the Superior Court (1948).
- H = `none`: "the decisions of one panel of the Appellate Division are not binding upon the remaining panels" (*David v. GEICO*, 821 A.2d 564, 572 (N.J. Super. App. Div. 2003)) [S].
- V = `statewideChooseOnConflict`: trial courts are bound by the Appellate Division; with conflicting panels they may choose [L].
- U: R. 1:36-3. Unpublished opinions are not precedent and may be cited only with notice [L].

**Other states.**
- Strong horizontal rules — Walker groups these with the federal model [S: Walker ¶21 & n.64]:
  - Alabama: Ala. R. App. P. 15 — no "former adjudication … shall be overruled … except upon consultation of the court as a whole".
  - Kansas: *In re Cray*, 867 P.2d 291, 297 (Kan. 1994) — en banc needed. **But** a Kansas Court of Appeals judge's 2025 article describes panels as able to *disagree with* (not overrule) prior panels (Leben, *Disagreeing with Yourself*, 73 Kan. L. Rev. (2025), https://irlaw.umkc.edu/faculty_works/1012/). Treat Kansas H as `soft` [U].
  - Kentucky: SCR 1.030(7)(d) — a conflict may be reassigned to the full court.
  - North Carolina: *In re Civil Penalty*, 324 N.C. 373, 384 (1989) — a panel is bound by a prior panel [L].
  - Oklahoma: Court of Civil Appeals barred by statute and rule from reexamining its own prior decisions — *Bays Expl. v. Jones*, 230 P.3d 907, 910–11 (Okla. Civ. App. 2010).
  - Tennessee: Tenn. Sup. Ct. R. 4(G)(2) — published opinions are "controlling authority for all purposes unless and until … reversed or modified by a court of competent jurisdiction"; conflicts go en banc under the Court of Appeals IOP [S].
  - Texas: within each court.
  - Virginia: the "interpanel accord" doctrine — *Collins v. Commonwealth*, 517 S.E.2d 277, 280 (Va. App. 1999) [S].
  - Wisconsin: *Cook v. Cook*, 208 Wis. 2d 166, 189–90, 560 N.W.2d 246 (1997) — "the court of appeals may not overrule, modify or withdraw language from a previously published decision of the court of appeals"; only the Supreme Court can [L, S via Walker].
- Soft horizontal rules (a court may overrule its own precedent) [S: Walker n.65]:
  - Alaska (*Joseph v. State*, 293 P.3d 488, 492 (Alaska App. 2012)), Arizona, Connecticut, Florida (within a DCA, en banc), Idaho (*Klosterman v. Rogers*, 973 P.2d 161 (Idaho App. 1999)), Illinois, Indiana (*Leatherwood v. State*, 880 N.E.2d 315, 319 (Ind. App. 2008)), Louisiana, Maryland (*Montgomery Cnty. Career Fire Fighters Ass'n*, 62 A.3d 287, 306 (Md. App. 2013)), Massachusetts, Missouri, New Jersey, Ohio, Oregon (*State v. Roberts*, 172 P.3d 651, 654 (Or. App. 2007): "unless error is plainly shown"), Utah (*State v. Tenorio*, 156 P.3d 854, 857 (Utah App. 2007)), Washington.

### 4.3 The 50-state table

Notes on the columns:
- **IAC (est.)**: the intermediate court and when it was established.
- **Units**: the internal division of the IAC.
- **H, V**: as defined in §4.1. Strong H with no number means panels; "D" = district; "Div" = division; "Dept" = department.
- **U / cutoff**: when unpublished decisions became citable, and with what weight.
- Unmarked cells are [L]; "?" = [U].

| State | IAC (est.) | Units | H | V (trial courts) | U / cutoff | Key source(s) |
|---|---|---|---|---|---|---|
| AL | Ct. Civ. App. & Ct. Crim. App. (1969; Court of Appeals 1911–69) | Separate courts by subject | strong | statewide | No-opinion affirmances: no precedent (Ala. R. App. P. 53(d)) | Ala. R. App. P. 15 [S] |
| AK | Ct. App. (1980), criminal only | Single | soft | statewide | Memorandum opinions not precedent (App. R. 214(d)) | *Joseph* 2012 [S] |
| AZ | Ct. App. (1965) | Div. 1, Div. 2 (one court) | soft | statewide | Memorandum decisions citable from 1 Jan 2015 (R. 111(c)) | *Patterson* 2009 [S] |
| AR | Ct. App. (1979) | Single, panels | ? | statewide | Arkansas reportedly made all opinions precedential from 1 July 2009 (Sup. Ct. R. 5-2) [U] | ? |
| CA | Cts. of Appeal (1905) | 6 districts, divisions | **none** | **statewideChooseOnConflict** | Not citable (8.1115); review-granted rule 2016 | *Auto Equity* 1962; Rule 8.1115 [S] |
| CO | Ct. App. (1970; earlier 1891–1905, 1913–17) | Divisions of 3 | none/soft ? ("one division is not bound by another") | statewide ? | Unpublished not cited (C.A.R. 35) ? | C.R.S. § 13-4-106 [S]; *Mitchell v. Ryder*, 2004 [S] |
| CT | Appellate Ct. (1983) | Panels | soft (panels defer; en banc to overrule) | statewide | Memorandum decisions | *State v. Thompson*, 839 A.2d 622, 641 (Conn. App. 2004) [S] |
| DE | none | — | — | — | — | — |
| FL | DCAs (1957; 6th 2023) | 6 districts | within-D strong; across none | **ownUnitThenAny** | PCAs no precedent | *Pardo* 1992 [S] |
| GA | Ct. App. (1906) | Divisions; whole court | strong-if-binding; **physical precedent** | statewide | Unreported: none | Rule 33.2 (2020 change) [S] |
| HI | ICA (1980) | Single | soft ? | statewide | SDOs not precedent; memorandum opinions after 1 July 2008 persuasive (HRAP 35) ? | ? |
| ID | Ct. App. (1982) | Single | soft | statewide | Unpublished not precedent | *Klosterman* 1999 [S] |
| IL | App. Ct. (1877; modern 1964) | 5 districts + divisions | **none** | **ownUnitThenAny** | Rule 23(b) orders from 1 Jan 2021 persuasive | *O'Casek*/*Carpenter* 2008; *Yapejian* 1992 [S/L] |
| IN | Ct. App. (Appellate Ct. 1891; renamed 1971) | 5 districts (statewide court) | soft | statewide | Memorandum decisions from 1 Jan 2023 persuasive (App. R. 65(D)) | *Leatherwood* 2008 [S]; 65(D) [S] |
| IA | Ct. App. (1976) | Single, cases transferred | ? | statewide | Unpublished not controlling (R. App. P. 6.904(2)(c)) | ? |
| KS | Ct. App. (1977; earlier 1895–1901) | Panels | strong per *Cray* / soft per Leben ? | statewide | Unpublished not binding (R. 7.04) | *In re Cray* 1994 [S]; Leben 2025 [S] |
| KY | Ct. App. (1976 as IAC) | Panels | strong | statewide | RAP 41: unpublished after 1 Jan 2003 citable "for consideration" if no published authority (eff. 1 Jan 2023) ? | SCR 1.030(8)(a) [S] |
| LA | Cts. of Appeal (1960 form) | 5 circuits | within-circuit strong; across none | ownUnitOnly ? | — | *Orillion* 1997 [S] |
| ME | none | — | — | — | — | — |
| MD | Ct. Spec. App. (1966/67) → **Appellate Ct. of Md. (14 Dec 2022)** | Panels | soft | statewide | Unreported after 1 July 2023 citable as persuasive if no reported authority; per curiam excluded (Rule 1-104) | Rule 1-104 [S] |
| MA | Appeals Ct. (1972) | Panels | soft | statewide | Rule 23.0 (formerly 1:28) summary decisions after 25 Feb 2008 persuasive (*Chace v. Curran*, 71 Mass. App. Ct. 258 (2008)) | [L] |
| MI | Ct. App. (1965) | Panels | **strong for opinions on or after 1 Nov 1990**; conflict panel | statewide | Unpublished not binding | MCR 7.215(J) [S] |
| MN | Ct. App. (1983) | Panels | ? (published opinions binding on district courts "immediately upon filing") | statewide | Unpublished not precedential (Minn. Stat. § 480A.08(3)) | [S via Curtis n.?] |
| MS | Ct. App. (1995) | Panels | ? | statewide | — | *Bevis* 2003 [S] (vertical) |
| MO | Ct. App. (unified 1972) | E/W/S districts | soft (en banc in district to depart: OR 22.01) | statewide ? | — | OR 22.01 [S] |
| MT | none | — | — | — | — | — |
| NE | Ct. App. (1991) | Panels | ? | **date-ranged**: 1996–2007 published decisions declared non-binding "dicta at best" (*Metro Renovation v. State*, 543 N.W.2d 715 (Neb. 1996)); disapproved by *State v. Nelson*, 739 N.W.2d 199, 204 (Neb. 2007), after court rule restored vertical force | — | [S via Walker ¶20] |
| NV | Ct. App. (Jan 2015) | Panels | ? | statewide | Unpublished from 1 Jan 2016 persuasive (NRAP 36(c)(3)) | [L] |
| NH | none | — | — | — | — | — |
| NJ | App. Div. (1948) | Parts/panels | **none** | statewideChooseOnConflict | R. 1:36-3 | *David v. GEICO* 2003 [S] |
| NM | Ct. App. (1966) | Panels | ? | statewide | Nonprecedential (Rule 12-405) | *McNeill* 2006 [S] (vertical) |
| NY | App. Div. (1896) | 4 departments | across Dept none | **ownUnitThenAny** | — | *Mountain View* 1984 [S] |
| NC | Ct. App. (1967) | Panels | **strong** | statewide | Unpublished not controlling (App. R. 30(e)(3)) | *In re Civil Penalty* 1989 [L] |
| ND | Temporary Ct. App. (1987) | Assigned panels | ? | statewide | — | N.D.C.C. ch. 27-02.1 [L] |
| OH | Cts. of App. (1912) | 12 districts | across D none; within soft | **ownUnitOnly** | All opinions citable from 1 May 2002 (Rep.Op.R.) ? | *George* 1975; *Stapleton* 1998 [S] |
| OK | Ct. Civ. App. (1968/1970) | 4 divisions | strong (statute/rule) | statewide | Published COCA opinions **persuasive only**, unless released for publication by **Supreme Court order** (then precedential); cert denial no effect; Rule 1.200 amended 2013/2023/2024 | *Bays*; *Brewer v. Murray* 2012; R. 1.200 [S] |
| OR | Ct. App. (1969) | Single (en banc possible) | soft ("unless error is plainly shown") | statewide | — | *Roberts* 2007 [S] |
| PA | Superior (1895), Commonwealth (1970) | Panels | strong within each; none across | statewide (per subject) | Rule 126(b): Super. after 1 May 2019; Commw. after 15 Jan 2008 | [S] |
| RI | none | — | — | — | — | — |
| SC | Ct. App. (1983) | Panels | ? | statewide | Unpublished no precedent (Rule 268(d)(2)) | *Cheeks* 2012 [S] (vertical) |
| SD | none | — | — | — | — | — |
| TN | Ct. App. (1925; Civ. App. 1907) & Ct. Crim. App. (1967) | 3 grand divisions | strong (R. 4(G)(2); en banc IOP) | statewide | Unpublished controlling only between parties, persuasive otherwise (R. 4(G)(1)) | [S] |
| TX | Cts. of App. (Civ. App. 1892; renamed 1 Sept 1981); 15th (2024) | 15 courts | within-court strong; across none; **TRAP 41.3 transfer** | own court ? | TRAP 47.7 (2003) | [S] |
| UT | Ct. App. (1987) | Panels | soft | statewide | Unpublished limited | *Tenorio* 2007 [S] |
| VT | none | — | — | — | — | — |
| VA | Ct. App. (1985; widened jurisdiction 1 Jan 2022) | Panels | **strong** (interpanel accord) | statewide | Unpublished not binding (R. 5A:1(f)) | *Collins* 1999 [S] |
| WA | Ct. App. (1969) | 3 divisions | **none** (*Arnold* 2018) | ? | GR 14.1: unpublished from 1 Mar 2013 nonbinding | [S] |
| WV | ICA (**1 July 2022**) | Single | ? | statewide | — | [L] |
| WI | Ct. App. (1 Aug 1978) | 4 districts (one court) | **strong** (*Cook*) | statewide | Authored unpublished opinions after 1 July 2009 persuasive (Wis. Stat. § 809.23(3)) | [L/S] |
| WY | none | — | — | — | — | — |
| DC | none (Ct. App. is the only appellate court) | Divisions; en banc | Divisions bound; only en banc overrules (*M.A.P. v. Ryan*) | statewide | — | [S] |
| PR | Tribunal de Apelaciones (1992 as Circuit Ct. of App.; renamed 2003) | Regions/panels | ? | ? | — | [U] |

States with no IAC (as of 2026): DE, ME, MT, NH, RI, SD, VT, WY. NV had none before 2015 and WV none before July 2022; ND has only a temporary court.

### 4.4 Trial courts and horizontal force

- State trial courts do not bind each other or themselves, as with F13.
- Exceptions:
  - appellate divisions and terms of trial courts (California appellate divisions, New York Appellate Term, Massachusetts District Court Appellate Division) bind the courts below them within their area;
  - Massachusetts Appellate Division districts do not bind each other ("The principle of Stare Decisis is not applicable among the several Appellate Division Districts", *Chickel v. MBTA*, 2001 Mass. App. Div. 241) [S].
- The Delaware Court of Chancery and Superior Court are trial courts. Their opinions are heavily cited, but are not binding beyond the case [L].

---

## 5. Treatment vocabulary

### 5.1 Two event families

**A. Same-case history (subsequent history).** These are events in the *same* litigation that act on *this* decision's judgment or opinion. Each has a direct effect on precedential status.

| Event | Effect on the decision's precedential status | Detection |
|---|---|---|
| affirmed | none; affirmance does *not* adopt the reasoning unless the higher court says so. Summary affirmance ≠ approval (F2) | "aff'd", a later decision in the same docket with a higher court |
| affirmed by equally divided court | none | F5 |
| affirmed on other grounds | the lower court's reasoning on the ground not reached is not endorsed. Its precedential force stays as before in most systems [L/U per state] | "aff'd on other grounds" |
| reversed | **the lower opinion loses force on the issues reversed**. Courts treat a reversed opinion as not good law on the reversed point. Other issues may survive [L] | "rev'd", "reversed" |
| reversed in part / affirmed in part | loss of force only on the reversed issues | "aff'd in part, rev'd in part" |
| vacated (whole or in part) | **no precedential effect** for the vacated part (F4) | "vacated", "judgment vacated", "vacated as moot" |
| GVR | vacated (F4) | "cert. granted, judgment vacated, and remanded" |
| modified | the opinion stands as modified | "modified", "as modified" |
| cert / review / petition denied | none (F3), except TX "writ ref'd" / "pet. ref'd" (promotion) | "cert. denied" |
| CA review granted | force suspended → persuasive (2016–) or depublished (pre-2016) | S-CA |
| depublished / ordered not published | becomes `notCitable` | "ordered depublished" |
| rehearing granted | the opinion may be withdrawn; status pending | "reh'g granted" |
| rehearing en banc granted | panel opinion vacated where local rule says so (F8) | F8 |
| withdrawn and superseded on rehearing | **the original opinion is a nullity** from the substitution date. The substituted opinion (often the same date of decision, or a new date) carries the force | "opinion withdrawn and the following substituted", "on rehearing", "superseded", "amended opinion" |
| mandate recalled / opinion reinstated | restores status | "reinstated" |

**B. Later-case treatment.** A *different* decision says something about this decision.

| Treatment | Changes status? | Conditions and notes |
|---|---|---|
| **overruled** | **Yes**, for the issues stated (all, if unqualified) | The treating court must have power over the target (v1 `mayOverrule`, refined by bench, adoption and succession) |
| **overruled in part** / "to the extent that" / "insofar as" | **Yes, for the named issues only** | Needs an issue key. Without extraction, mark as `partial(unknown)` |
| **overruled on other grounds** | Yes, for those other grounds; the cited proposition survives | Commonly appears as "(overruled on other grounds by X)" in citing parentheticals |
| **abrogated** (by intervening higher authority) | **Yes** — effective at the *abrogating* decision's date | Often stated by a lower court ("recognized as abrogated by"); that court is not the cause (F14) |
| **superseded by statute / rule / constitutional amendment** | **Yes, prospectively and issue-limited**; see §7 | The holding remains for conduct before the statute's effective date (unless retroactive) and for the unamended text |
| **disapproved** (CA, FL and others: a higher court on a lower-court decision not before it) | **Yes**, to the extent of the disapproval | Functionally overruling |
| **receded from** (FL: a DCA en banc, or the Supreme Court, departing from its *own* precedent) | **Yes** | Functionally overruling |
| **limited** ("limited to its facts") | No formal change; narrows the scope of the holding | Soft negative |
| **questioned** / **criticized** / "called into doubt" | No | Soft negative; may predict overruling |
| **declined to follow** (by a coordinate or other court) | No (that court is not bound) | A conflict signal (Florida, Illinois, New York and others) |
| **distinguished** | No | Neutral |
| **explained** / **harmonized** | No | Neutral |
| **followed** / **relied on** | No | Positive |

### 5.2 Rules

**Rule T1.** Status changes only through:
- (a) a same-case event that reverses or vacates;
- (b) a treatment by a decision whose court has power over the target's issue, at a sufficient bench level (overruled, overruled in part, disapproved, receded from);
- (c) intervening higher authority (abrogation) that *legally* displaces the target, whether or not anyone said so;
- (d) legislation or a constitutional amendment (superseded).

"Limited", "questioned", "criticized" and "distinguished" never change status.

**Rule T2 — A treatment by a court without power is a *claim*, not a status change.** Examples:
- a district court "declines to follow" circuit precedent;
- a state court "disapproves" a federal decision;
- a sister DCA "disagrees".

Keep it as evidence. v1's `invalidOverrulings` already flags the extreme case.

**Rule T3 — Revival.** An overruled decision can regain force if the overruling decision is itself overruled, vacated or withdrawn. The classic example is the reinstatement of an earlier rule by overruling its overruler.

Revival is *not* automatic in all courts: the later court may adopt a third rule [L]. v1's monotonicity theorem `overruledOn_mono` is false in general. v2 should prove monotonicity only for the fragment without reversal, vacatur or withdrawal of overruling decisions.

Detection: "the rule of X is restored", "we return to X".

**Rule T4 — Detection sources.** The corpus holds only opinions, so history comes from three places:
- (i) explicit parentheticals in citing opinions ("overruled by", "abrogated by", "superseded by statute as stated in", "rev'd", "vacated", "disapproved on other grounds by");
- (ii) the treating opinion's own words ("we overrule", "is hereby overruled", "to the extent that X holds …, it is overruled", "we recede from", "we disapprove");
- (iii) same docket and same parties at a higher court within a short interval (affirmed/reversed/vacated). The disposition sentence of the higher decision ("REVERSED", "AFFIRMED", "VACATED and REMANDED") gives the event.

Shepard's/KeyCite vocabulary matches these labels; KeyCite's red flag ("no longer good law for at least one of the points of law it contains") corresponds to "some issue negatively changed" [L].

---

## 6. Timing

**Rule TM1 — An overruling or other precedent takes effect when the decision is filed (announced), not when the mandate issues.**
- 9th Cir.: a published opinion is binding on filing, before the mandate (*Yong v. INS*, 208 F.3d 1116, 1119 n.2 (9th Cir. 2000)) [L — not re-verified].
- The mandate governs the *judgment* between the parties, not precedential force [L].
- The same holds in most states for appellate decisions. Minnesota: "binding on … district courts immediately upon its filing" [S, quoted in Curtis].
- California is a partial exception: a Court of Appeal decision is final 30 days after filing (Rule 8.264(b)), but its precedential force exists from publication, subject to later review-granted and depublication events [L].
- Lean: `Decision.date` (filed) is the effective date. Same-case events carry their own dates. Withdrawal/substitution: TM3.

**Rule TM2 — Retroactivity of overruling decisions (the *Sunburst* doctrine).**
- **Federal law:**
  - *Great Northern Ry. v. Sunburst Oil & Refining Co.*, 287 U.S. 358, 364–66 (1932): the Constitution permits a *state* court to make its overruling prospective-only [L].
  - Federal civil cases:
    - *Chevron Oil Co. v. Huson*, 404 U.S. 97 (1971), allowed prospective application;
    - *James B. Beam Distilling Co. v. Georgia*, 501 U.S. 529 (1991), and *Harper v. Virginia Dep't of Taxation*, 509 U.S. 86, 97 (1993), require full retroactivity to all open cases. This bars selective prospectivity for federal law [L].
  - Federal criminal cases:
    - *Griffith v. Kentucky*, 479 U.S. 314 (1987): new rules apply to all cases on direct review;
    - *Teague v. Lane*, 489 U.S. 288 (1989): generally not on collateral review;
    - *Edwards v. Vannoy*, 593 U.S. 255 (2021): the watershed exception is dead [L].
  - *Danforth v. Minnesota*, 552 U.S. 264 (2008): states may give broader collateral retroactivity to federal rules [L].
- **State law**: states keep *Sunburst* freedom for their own law [S, secondary summaries]:
  - many still use *Chevron*-style balancing (e.g. Wisconsin's *Kurtz* line; Montana; South Dakota) [S, secondary];
  - New Mexico applies a rebuttable presumption of retroactivity [S, secondary];
  - Washington rejects selective prospectivity: *Lunsford v. Saberhagen Holdings*, 166 Wn.2d 264 (2009) [S, secondary];
  - Michigan: *Pohutski v. City of Allen Park*, 465 Mich. 675 (2002) (prospective overruling) [L];
  - Illinois: *Molitor v. Kaneland Cmty. Unit Dist.*, 18 Ill. 2d 11 (1959) (prospective, with the party benefitting) [L].
- Detection: phrases such as:
  - "shall apply prospectively only";
  - "applies only to cases filed after";
  - "to conduct occurring after the date of this opinion";
  - "purely prospective";
  - "with the exception of the parties before us";
  - "the mandate shall be stayed until".
- Lean: `Overruling.temporal : retroactive | prospectiveFrom (d : Date) (includesParties : Bool) | pureProspective`. Then `goodLawFor (x) (issue) (eventDate)`: the status is relative to the *date of the underlying facts/conduct*, not only the date of the question. v2 needs two dates in the query: `asOf` (the legal-knowledge date) and `conductDate` (the transaction date).

**Rule TM3 — Rehearing, withdrawal, substitution.**
- An opinion withdrawn on rehearing and replaced by a substituted opinion is a nullity. Citation to the withdrawn opinion is improper.
- The substituted opinion usually keeps the original docket and often the original date of decision, with "amended" or "on rehearing" dates [L].
- Lean:
  - `SameCaseEvent.withdrawn (by : Option Decision) (date)`;
  - force of the withdrawn opinion = `none` from `date`. Arguably *ab initio* for citation purposes, but not for intermediate reliance; choose `fromDate`, with a flag;
  - for overrulings the withdrawn opinion purported to make: they lapse.
- The corpus may hold both versions (CAP often prints only the final one). Use `same-decision-as`-like relations: `supersedes-on-rehearing`.

**Rule TM4 — California depublication and review**: see S-CA (dated 1 July 2016 and 21 Apr 2021).

**Rule TM5 — Successor and adoption dates** (F10, F11, H3, *M.A.P.*). Authority attaches by *the date of the precedent*, compared with a cutoff:
- 11th Cir.: 30 Sept 1981, close of business;
- Fed. Cir.: 30 Sept 1982;
- D.C.: 1 Feb 1971;
- Kentucky: 1 Jan 1976;
- New Jersey: 15 Sept 1948;
- Erie: 25 Apr 1938;
- Michigan: 1 Nov 1990;
- Georgia: 1 Aug 2020;
- 5th Cir. unpublished: 1 Jan 1996;
- D.C. Cir. unpublished: 1 Jan 2002;
- FRAP 32.1: 1 Jan 2007.

---

## 7. Abrogation by statute or constitutional amendment

**Rule AB1.**
- A legislature cannot overrule a judicial *decision* in the sense of reopening a judgment. It can change the law the decision applied.
- A holding interpreting statute S, or stating a common-law rule, is then "superseded by statute" as to:
  - conduct governed by the new law: on or after its effective date, or a retroactive date if the statute so provides;
  - the new statutory text.
- **It remains good law** for conduct before the effective date (absent clear retroactivity), and for issues not touched by the statute.
- Presumption against statutory retroactivity: *Landgraf v. USI Film Products*, 511 U.S. 244, 265–80 (1994) [L]. The Civil Rights Act of 1991, which superseded *Patterson*, *Wards Cove* and others, was not retroactive.
- Examples of express retroactivity:
  - Lilly Ledbetter Fair Pay Act of 2009, Pub. L. 111-2, signed 29 Jan 2009, superseding *Ledbetter v. Goodyear Tire & Rubber Co.*, 550 U.S. 618 (2007), with § 6 effective **as if enacted on 28 May 2007** (the day before *Ledbetter*) [L];
  - Civil Rights Restoration Act of 1988 (superseding *Grove City College v. Bell*, 465 U.S. 555 (1984)) [L].
- Constitutional amendments as superseders [L]:
  - *Chisholm v. Georgia*, 2 U.S. 419 (1793), by the 11th Amendment (declared 1798; ratified 7 Feb 1795);
  - *Dred Scott v. Sandford*, 60 U.S. 393 (1857), by the 13th and 14th Amendments (1865, 1868);
  - *Pollock v. Farmers' Loan & Trust Co.*, 157 U.S. 429 (1895), by the 16th (3 Feb 1913);
  - *Minor v. Happersett*, 88 U.S. 162 (1875), by the 19th (1920);
  - *Oregon v. Mitchell*, 400 U.S. 112 (1970), by the 26th (1 July 1971).
- State-level equivalents are common, e.g. state constitutional amendments reversing state-court constitutional holdings.
- **Rule amendments** (FRCP, FRE, state rules) supersede decisions interpreting the old rule; the effective date is the rule's (usually 1 December for federal rules).
- **How courts say it**:
  - "superseded by statute", "superseded by statute as stated in X" (a later court notes the supersession);
  - "legislatively overruled"; "abrogated by statute";
  - "Congress responded to [X] by enacting …";
  - "the legislature amended § N in response to …";
  - "(superseded by rule on other grounds)".
- **Detection hooks unique to this corpus**: the judgment overlay links each decision's statute citation to the section's version *on the day decided* (`law_commit`). A holding interpreting § N at version v is presumptively *version-scoped*. When the global-law history shows § N changed after the decision, flag the holding `possiblySuperseded (amendment := commit, effective := date)` for a reviewer. If a later case says "superseded by statute", confirm it. This is an automatic, sourced detector the commercial citators lack.
- Lean:
  - `Treatment.supersededByEnactment (enactment : LawChangeId) (effective : Date) (retroactiveTo : Option Date) (issues : IssueSet)`;
  - `goodLawFor x issue conductDate := ¬ (issue ∈ issues ∧ conductDate ≥ (retroactiveTo.getD effective))`;
  - a holding's `basis : List LawVersion`, used to auto-propose supersession.

---

## 8. Holdings, dicta, alternative holdings, "on other grounds"

### 8.1 Doctrine

**Rule HD1 — Only holdings bind. Dicta are at most persuasive.** A holding is a proposition necessary to the decision of an issue actually presented and decided. Sources:
- *Cohens v. Virginia*, 19 U.S. (6 Wheat.) 264, 399 (1821) ("general expressions … are to be taken in connection with the case in which those expressions are used") [L];
- *Seminole Tribe of Fla. v. Florida*, 517 U.S. 44, 67 (1996) (the result *and* "those portions of the opinion necessary to that result" bind) [L].
- Some circuits treat carefully considered *Supreme Court* dicta as nearly binding. Examples:
  - 9th Cir.: well-reasoned dicta of the circuit is law of the circuit (*Barapind v. Enomoto*, 400 F.3d 744, 750–51 (9th Cir. 2005) (en banc)) [L/U];
  - 6th, 10th and others give SCOTUS dicta substantial weight [L].
- Model these as force `persuasiveStrong`.

**Rule HD2 — Alternative holdings are each binding.**
- "Where a decision rests on two or more grounds, none can be relegated to the category of obiter dictum" (*Woods v. Interstate Realty Co.*, 337 U.S. 535, 537 (1949); *Massachusetts v. United States*, 333 U.S. 611, 623 (1948)) [L].
- Most circuits follow this. A minority of courts in some contexts treat alternative grounds as less weighty [U].

**Rule HD3 — Questions not decided are not precedent.**
- "Questions which merely lurk in the record, neither brought to the attention of the court nor ruled upon, are not to be considered as having been so decided as to constitute precedents" (*Webster v. Fall*, 266 U.S. 507, 511 (1925)) [L].
- Assumed-without-deciding is not a holding.
- **"Drive-by jurisdictional rulings"** have "no precedential effect" (*Steel Co. v. Citizens for a Better Env't*, 523 U.S. 83, 91 (1998); *Arbaugh v. Y&H Corp.*, 546 U.S. 500, 511 (2006)) [L].
- Sub silentio holdings are not binding [L].

**Rule HD4 — "On other grounds".** When X is reversed, overruled, abrogated or superseded "on other grounds", the status change applies only to the *other* issue. X remains good law for the proposition being cited. Citators flag the decision; a correct model keeps the cited issue green.

**Rule HD5 — State syllabus rules.**
- In Ohio before 1 May 2002, and in West Virginia (syllabus points), the *syllabus* written by the court is the authoritative statement of the holding. Kansas also uses a syllabus by the court [L].
- The extraction source is then explicit. The corpus head matter contains these syllabi in the first CAP build. Be careful to separate a court-written syllabus from a reporter-written one; CAP head matter mixes them.

**Rule HD6 — Plurality, physical precedent, equally divided** (F5, F6, S-GA). Force is per *part/issue* and depends on joins.

### 8.2 A computable holding model

```
Decision
  ├─ court, date, docket, caseKind (civil|criminal|…), bench (panel|enBanc|…), publication, form
  ├─ opinions : List Opinion           -- role, author, joins, parts
  ├─ issues : List Issue
  │    Issue
  │      ├─ key : IssueKey            -- a normalized legal question (curated/extracted), e.g. "FRCP12b6.pleading-standard"
  │      ├─ domain : IssueDomain      -- federalGeneral | federalPatent | stateLaw s | tax | …
  │      ├─ basis : List LawVersion   -- statute/rule versions applied (from the judgment overlay)
  │      ├─ holding : Option Proposition
  │      ├─ necessity : necessary | alternative | dictum | assumed | jurisdictionalDriveBy
  │      ├─ support : PartId → joins  -- which opinion parts state it; majority iff joins > n/2
  │      ├─ outcome : resolvedFor | resolvedAgainst | remandedOn | notReached
  │      └─ temporal : retroactive | prospectiveFrom d | …
  └─ disposition : affirmed | reversed | vacated | modified | remanded | dismissed | mixed (List (IssueKey × Disposition))
```

An issue's **precedential force** in court `c` on date `t`, for conduct date `u`, is computed by these rules in order:

1. If the decision is withdrawn, vacated or depublished as of `t` (over the issue's part), the force is `none` / `notCitable`.
2. If the issue's `necessity ∈ {dictum, assumed, jurisdictionalDriveBy}`, the force is at most `persuasive`.
3. If the issue lacks majority support (plurality / physical precedent / equally divided), the force is `resultOnly` or `persuasive`, unless a `marksHolding` row gives it.
4. If an overruling or abrogation of the issue is valid and effective by `t`, and its temporal scope covers `u`, the force is `overruled`.
5. If a supersession of the issue by enactment, effective by `u`, applies, the force is `superseded`.
6. Otherwise the force is `relation(court(decision), c, domain, t, publication, bench)` from §§1–4.

Where the issue is unknown (no extraction), the decision is treated as one *anonymous* issue `⊤`. A partial or "other grounds" treatment then yields status `partiallyNegative`, not `overruled`. This lets v2 run over the full 6.9M decisions before issue extraction exists.

---

## 9. Lean design implications (concise)

**Types**

1. `Date := Nat` (yyyymmdd, as in v1), plus `DatePrecision` (`day | month | year`), already in `decision-dates.tsv`.

2. `IssueDomain := federalGeneral | federalPatent | federalTax | stateLaw (s : SystemId) | localLaw (s) | unknown`.

3. `CaseKind := civil | criminal | juvenile | family | admin | unknown`.

4. `Tier := last | appellate | bap | trial | special | appellateDivisionOfTrial`.

5. Courts become timelines:
   ```
   CourtEpoch {court : CourtId, from to : Date, name : String, system : SystemId, tier : Tier,
               lastResortFor : Option CaseKind, unit : Option UnitId (district/division/department), circuit : Nat}
   ```
   `court.at (d : Date) : CourtEpoch`. This fixes Kentucky, New Jersey, Delaware and D.C.

6. ```
   Succession {old new : CourtId, date : Date, kind : rename | replace | split | absorb}
   Adoption   {adopter source : CourtId, upTo : Date, filter : DecisionPred, force : Force}
   ```
   Adoption rows: 11th←5th (30 Sept 1981, plus the Unit B filter); Fed.←Ct. Cl. and CCPA (30 Sept 1982); D.C. Ct. App.←D.C. Cir. (before 1 Feb 1971); Ky. Ct. App.←old Ky. Ct. App. (before 1976).

7. `Bench := panel | division | enBanc | limitedEnBanc | circulated | conflictPanel | wholeCourt`.

8. `Publication := published | unpublished | table | summaryOrder | memorandum | pca | unreported`.

9. `DecisionForm := full | perCuriam | summaryAffirmance | equallyDivided | certifiedAnswer | commission (adoption) | memorandum`.

10. `Force` as an ordered scale:
    ```
    binding > bindingAbsentConflict > persuasiveStrong > persuasive > citableNoWeight > notCitable > none
    ```
    Plus `resultOnly` and `physicalPrecedent` (≈ `persuasive`).

11. `Opinion {role, author, joins : List JudgeId, parts : List PartId}`; `Issue` as in §8.2.

12. Events:
    ```
    SameCaseEvent {target : DecisionId, by : Option DecisionId, date, kind :
       affirmed | reversed | vacated | modified | remanded | certDenied | reviewGranted | reviewDismissed
       | depublished | withdrawn | substitutedBy | rehearingEnBancGranted (vacatesPanel) | reinstated
       | txNotation (writRefused | nre | petRefused | …), parts : IssueScope}

    Treatment {target, by : DecisionId ⊕ LawChangeId, date, kind :
       overruled | disapproved | recededFrom | abrogated | supersededByEnactment (effective, retroactiveTo)
       | limited | questioned | criticized | distinguished | followed | declinedToFollow,
       scope : all | issues (List IssueKey) | partialUnknown | otherGrounds (List IssueKey),
       temporal : retroactive | prospectiveFrom d | pureProspective, explicit : Bool}
    ```

**Parameter tables** (data, each row with a source and a tag `S | L | U`)

13. `horizontal : SystemId → UnitScope → Date → HorizontalRule`, with values `strong | soft | none | withinUnitOnly`. Michigan's 1990 cutoff and Georgia's 2020 binding test are date-keyed.

14. `trialScope : SystemId → Date → TrialScope`, with values `statewide | statewideChooseOnConflict | ownUnitThenAny | ownUnitOnly`. Nebraska 1996–2007 is a date-ranged row.

15. `unpubForce : CourtId → Date(precedent) → Publication → Force`: the 5th Cir. 1996 and D.C. Cir. 2002 cutoffs; citability dates for IL 2021, PA 2008/2019, MD 2023, IN 2023, WA 2013, AZ 2015, NV 2016, WI 2009 and MA 2008.

16. `firstInTimeControls : CourtId → Bool`.

17. `circulationCountsAsEnBanc : CourtId → Bool`: 2d, 7th, 10th, D.C., and the 1st (?).

18. `enBancGrantVacatesPanel : CourtId → Bool`.

19. `stateFollowsCircuit : SystemId → Date → Force`. Default `persuasive`; rows for ME, NH, SD and NE flagged [U].

20. `marksHolding : DecisionId → IssueKey → Option Proposition`: curated.

21. `appealVenue` for the Tax Court (*Golsen*), and `transferor` for Texas TRAP 41.3: per-decision fields that make `binds` case-relative.

**Rules to state and prove**

22. `binds` → `force (src : Decision) (issue : Issue) (dst : CourtId) (t : Date) (u : Date) : Force`, as in §8.2. Prove these sanity theorems:
    - (a) SCOTUS majority holdings on federal issues have force `binding` everywhere;
    - (b) nothing binds the court of last resort on its own system's law except SCOTUS on federal questions;
    - (c) no state-court decision binds a federal court on federal law, and no federal decision binds a state court on state law (*Erie* is one-directional);
    - (d) district courts and state trial courts are never binding on anyone;
    - (e) force is monotone non-increasing in `t` in the fragment without vacatur, withdrawal or reversal of overrulers (generalizing `overruledOn_mono`), with a counterexample theorem for revival.

23. `mayOverrule` → `canChangeStatus (by : Decision) (target : Decision) (issue)`. It holds when:
    - the higher court of the same system has power over the issue domain; or
    - same court and `by.bench ≥ requiredBench (court, date)`, where `requiredBench = panel` if `horizontal ∈ {soft, none}`, else `enBanc` / `circulated` / `conflictPanel`; or
    - an adoption makes `by.court` the adopter; or
    - SCOTUS on a federal issue (abrogation of any lower federal or state decision on federal law).

    Keep `no_overrule_of_binding_superior`; add `no_panel_overrules_panel_in_strong`.

24. A conflict resolver: when several sources of equal tier bind `dst` on one issue and disagree, apply in order:
    - first-in-time (where the table says so);
    - own unit (for `ownUnitThenAny`);
    - otherwise `choice` (the result is a *set* of permissible holdings: California, New Jersey, New York, Illinois, Florida).

    The output type is `Finset Proposition`, not one answer.

25. Two-date queries: `goodLaw (x) (issue) (asOf t) (conduct u)`. This is needed for prospective overruling (*Sunburst*) and for supersession by statute.

26. Detection pipeline contracts (not Lean, but typed the same way): every event and treatment row carries `evidence : {decision, quote span, rule id}` and `confidence`.
    - A `Treatment` with `explicit = false` (an inferred abrogation) never proves status in a theorem. It only appears in findings.

27. Findings to add to v1's `citesOverruled`, which becomes issue-aware:
    - `citesVacated`, `citesUnpublishedAsBinding`, `citesWithdrawn`;
    - `appliesSupersededHolding` (where `conductDate` ≥ the supersession);
    - `ignoresBindingInUnit` (a trial court departs from its own unit, ownUnit rules);
    - `panelDepartsWithoutEnBanc` (strong-horizontal courts);
    - `pluralityTreatedAsBinding`.

---

## Sources consulted in this pass

Primary rules, cases and official pages:
- Cal. Rules of Court 8.1115 and comment: https://www.courts.ca.gov/cms/rules/index/eight/rule8_1115
- FJC, *Citing Unpublished Federal Appellate Opinions Issued Before 2007* (Reagan, 9 Mar 2007; 241 F.R.D. 328): https://www.fjc.gov/sites/default/files/2012/CitRules.pdf · https://www.fjc.gov/content/citing-unpublished-federal-appellate-opinions-issued-2007
- FRAP 32.1: https://www.law.cornell.edu/rules/frap/rule_32-1
- Ga. Ct. App. R. 33.2: https://www.courtrules.net/georgia/ga-court-of-appeals/rule-33-2 · https://www.gaappeals.gov/?p=683
- Ky. SCR 1.030: https://www.courtrules.net/kentucky/kentucky-supreme-court-rules/rule-1-030
- Md. Rule 1-104 (2023 order): https://www.courts.state.md.us/sites/default/files/import/cosappeals/pdfs/citationunreportedopinionsjuly2023.pdf
- Pa.R.A.P. 126(b): https://www.pabulletin.com/secure/data/vol49/49-18/653.html
- Ill. S. Ct. R. 23 (2021): https://illinoiscourts.gov/News/975/Supreme-Court-amends-Rule-23-to-Allow-Citation-of-Unpublished-Appellate-Court-Ruling/news-detail
- Ind. App. R. 65(D) (2022 order): https://www.in.gov/courts/files/order-rules-2022-1219-appellate-procedure.pdf
- Tex. R. App. P. 41.3: https://syfert.com/texas/sections/RAP/41.3.html · TRAP (current): https://www.txcourts.gov/media/1463134/texas-rules-of-appellate-procedure-02062026.pdf
- Okla. Sup. Ct. R. 1.200 (2013 order): https://law.justia.com/cases/oklahoma/supreme-court/2013/2013-ok-109.html
- MCR 7.215: https://state-rules.com/michigan/appellate/7.215
- Mo. Sup. Ct. OR 22.01: https://d1tvxue8o4w0fl.cloudfront.net/rule/missouri-court-rules/missouri-supreme-court-operating-rules/court-en-banc-review-of-division-opinions/rule-2201-court-en-banc-review-of-division-opinions
- Tenn. Sup. Ct. R. 4: https://www.courtrules.net/tennessee/tennessee-supreme-court/rule-4
- *Bonner v. City of Prichard*: https://openjurist.org/661/f2d/1206
- *Pardo v. State*: https://case-law.vlex.com/vid/pardo-v-state-no-891521748
- *In re Pers. Restraint of Arnold* (2018): https://www.courts.wa.gov/opinions/pdf/945446.pdf
- *State v. Patterson* (Ariz. App. 2009): https://law.justia.com/cases/arizona/court-of-appeals-division-one-published/2009/cr080610.html
- *Mountain View Coach Lines v. Storms*: https://www.studicata.com/summaries/appellate-division-of-the-supreme-court-of-new-york/mountain-view-coach-v-storms-1984-in6mwo · *Ocasio v. City of New York* (2006): https://www.nycourts.gov/reporter/3dseries/2006/2006_26223.htm
- *M.A.P. v. Ryan*: https://case-law.vlex.com/vid/m-p-v-ryan-895026763
- *Banks v. Int'l Rental & Leasing* (V.I. 2011): https://supreme.vicourts.org/court_opinions/published_opinions/2011_published_opinions/s_ct_civ_no_2011_0037 · 3d Cir. 2012: https://www2.ca3.uscourts.gov/opinarch/081603p.pdf
- *McKenzie v. Withers* (Tex. 1918): https://law.counselstack.com/opinion/mckenzie-v-withers-tex-1918

Surveys:
- D. C. Walker, *Precedential Power Policies*, 114 Law Libr. J. 167 (2022): https://www.albanylaw.edu/media/18456 (per-circuit and per-state citations; states bound by lower federal courts)
- C. J. Curtis, *State Court Structure and Precedent*, 45 N.C. Cent. L. Rev. 164 (2023): https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4269671
- S. Leben, *Disagreeing with Yourself: Horizontal Stare Decisis in State Intermediate Appellate Courts*, 73 Kan. L. Rev. (2025): https://irlaw.umkc.edu/faculty_works/1012/
- J. W. Mead, *Stare Decisis in the Inferior Courts of the United States*, 12 Nev. L.J. 787 (2012): https://scholars.law.unlv.edu/nlj/vol12/iss3/21 (not retrievable in this pass)
- Horvitz & Levy on Rule 8.1115(e): https://www.horvitzlevy.com/?p=16353
- Michael Dorf on state courts and lower federal precedent: https://www.dorfonlaw.org/2014/10/can-state-courts-gratuitously-give.html

## Open items (highest value to verify next)

1. Conflict rules for trial courts in AZ, CO, MO, TX, WA and LA (choose vs own unit).
2. Panel-binding rules in CO, HI, IA, MN, MS, NE, NM, NV, SC, ND and PR.
3. Exact dates:
   - TRAP 41.3 (2008?);
   - Ohio Rep.Op.R. (2002) and rule numbers;
   - FRAP 40 restyle (1 Dec 2024);
   - Arkansas 2009 publication rule;
   - Guam/NMI certiorari end (2004);
   - Connecticut rename (1965);
   - Delaware Supreme Court (1951).
4. Which circuits vacate panel opinions on grant of en banc, and current local-rule numbers after the 2024 FRAP restyle.
5. Whether ME, NH and SD still treat lower federal courts as binding (Walker's citations are 1984–1994).
6. Florida 6th DCA's position on inherited 2d DCA precedent.
7. BAP force, per circuit.
