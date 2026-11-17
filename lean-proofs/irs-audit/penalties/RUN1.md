# What the IRS publishes about the sanctions it imposes, checked against a Lean model of the statute

Run 1 of 17 November 2026: a seeded random sample of 1,004 docket entries. Run 2 ([RUN2.md](RUN2.md)) repeats it on
every reachable opinion. Fetching was polite and sequential; every request is logged in `cache/_status.tsv` (the
cache is not published: the scripts rebuild it). Lean code in `lean/`, scripts in `scripts/`, intermediate data in
`data/`. Standard of proof as in [../FINDINGS.md](../FINDINGS.md): recompute from the words of the statute in force
for the year, then verify every flag by hand in the document before calling it a disagreement.

## 1. What is public about IRS sanctions, and how reachable it is

| Source | What it shows | Reachable? | Used here |
|---|---|---|---|
| **US Tax Court opinions** (DAWSON public API, `public-api.dawson.ustaxcourt.gov`) | The notice of deficiency in the opinion's first paragraph (deficiency, additions to tax, penalties, by year), the holding, and the form of decision (for respondent / for petitioner / under Rule 155) | Yes. Open JSON API behind the court's own opinion search, no key. At most 5,000 hits per query; PDFs via short-lived S3 links. `www.ustaxcourt.gov/robots.txt` disallows only `/admin/` | **Yes: the core of this audit** |
| Tax Court decision documents (the figures finally entered) | Final amounts after Rule 155 | Mostly no: for paper-era cases the docket shows `DEC DECISION ENTERED` with no file attached (checked for Watts, docket 9289-98) | No |
| CourtListener, court id `tax` | Same opinions, full text | REST API v4 returns `401 Authentication credentials were not provided` without a token. **Needs an account: not used.** Bulk CSV is the whole US case-law corpus | No |
| Caselaw Access Project (`static.case.law/tc/`) | Reports of the Tax Court with figures | `robots.txt`: `User-agent: *` / `Disallow: /` | No (robots) |
| Pile of Law `taxrulings` (54,064 records) | **Not Tax Court opinions**: IRS written determinations (letter rulings etc.; `../wd/pile_taxrulings.json` classifies 54,063 as "other", 1 CCA), dollar amounts replaced by `dollar_figure` | On disk | No (wrong collection, no figures) |
| **IRS final adverse determinations** (exemption denials and revocations) among the written determinations (`irs.gov/pub/irs-wd/`) | Letter text, Code sections, stated grounds; names, dates and amounts redacted | Yes: 33,374 PDFs already harvested, 7,658 of them without a text layer | **Yes: counted and classified** |
| **Office of Professional Responsibility** disciplinary announcements (Circular 230) in the Internal Revenue Bulletin | Name, city, designation, sanction, stated ground, effective date | Yes, in the IRB corpus (`src/irs-guidance/announcement`) | **Yes: counted and classified** |
| IRS Criminal Investigation annual report (Publication 3583) and press releases | Aggregate case counts and dollars; individual sentencings | Yes. FY2025 report (released 11 Dec 2025): $10.59 billion of financial crimes identified, about $4.5 billion of it tax fraud (IRS release; secondary summaries, not re-verified) | Mapped only: sentences follow the Sentencing Guidelines, not a Code formula |
| TIGTA audits | Whether the IRS followed penalty procedure | Yes. Report 2026-300-021 (1 May 2026), *Procedures Are Needed to Prevent Backdating Penalty Approvals*: after *LakePoint Land II* (T.C. Memo. 2023-111) the IRS reviewed 829 docketed syndicated-easement cases; "13 docketed cases ... did not comply with I.R.C. § 6751(b) due to a lack of valid supervisory approval. Of the 13 cases, 7 involved backdated penalty approvals where the IRS conceded over $68 million in penalties"; TIGTA found 6 potential exceptions in 439 nondocketed cases | Read (one PDF) as context for §6751(b) |
| IRS Data Book; National Taxpayer Advocate "Most Litigated Issues" | Aggregate civil penalties assessed and abated; yearly lists of litigated penalty cases | Yes | Mapped only (aggregates) |
| IRS Appeals decisions; Collection Due Process determinations | Settlements, CDP determinations | Not published; visible only when a Tax Court opinion recites them | Only through opinions |

## 2. Method

### 2.1 The rules in Lean (`lean/Penalties.lean`, `lean/Verified.lean`, runner `lean/Run.lean`)
Money in cents (`Nat`), percentages as exact fractions. Written from the statute in force (US Code history via
`../tools/usc_at.sh`); the operative words are quoted in the file header.

- §6662(a) and (b) flush: 20% of the portion of the underpayment; no §6662 penalty on a portion that carries a §6663 penalty.
- §6662(d)(1)(A): substantial understatement = more than the greater of 10% of the tax required to be shown or $5,000;
  (d)(1)(B) corporations before and after the 2004 Act ($10,000; then the lesser of 10%-or-$10,000 and $10 million);
  (d)(1)(C) 5% for §199A claimants after 2017.
- §6662(h) (and (i), (j)): 40%.  §6663: 75% of the portion attributable to fraud.
- §6651(a)(1) 5% a month to 25%; (a)(2)/(a)(3) 0.5% a month to 25%; (c)(1) (a)(1) reduced by (a)(2) for months both run
  (so at most 22.5% when (a)(2) runs from the due date); (f) 15%/75%; the flush-language minimum ($100 from 1983, $135
  from 2009, $205 from 2016, $435 from 2020, indexed under (j)) as the lesser of the minimum or 100% of the tax.
- §6654(e)(1): no addition when the tax after withholding is under $1,000 ($500 before 1998). Anything more needs
  installment dates and payments that opinions do not state, so §6654 amounts are counted, not checked.
- §6665(b)(1): deficiency procedures reach a §6651 addition only "to that portion of such addition which is
  attributable to a deficiency in tax described in section 6211".
- Proved (kernel-checked): an understatement of at most $5,000 is never substantial for an individual
  (`not_substantial_small`); disjoint 20%/75% portions are bounded by the deficiency (`disjoint_bases`); the (c)(1)-reduced
  (a)(1) addition never exceeds 22.5% when (a)(2) runs on the same base (`ftf_reduced_cap`); one theorem per verified
  disagreement in `Verified.lean`.
- §6751(b) (written supervisory approval) is procedural: tagged in the text, not formalised.

What the check can and cannot say. An opinion states the **deficiency**; the penalty is charged on the
**underpayment** (§6664(a); Treas. Reg. §1.6664-2). They coincide in the ordinary case, so the test is
*penalty ≤ rate × deficiency* ($1 tolerance, since opinions round to dollars), and *penalty = rate × deficiency*
means the full rate on the whole deficiency. A penalty above that can still be lawful when the underpayment exceeds the
deficiency: carrybacks do not reduce the underpayment (Treas. Reg. §1.6664-2(f)), nor does an amended return that is
not a "qualified amended return" (§1.6664-2(c)(2)-(3)); and the IRS often pleads §6663 with §6662 in the alternative.
Such cases are reported as explained, not as errors.

### 2.2 Sampling (Tax Court)
DAWSON opinion search (memorandum, summary and division opinions), one query per keyword: `6662` (5,000 hits, the cap),
`6651` (3,790), `6663` (852), `6654` (1,543), `6662(h)` (2,482), `6751(b)` (854). From each pool, per filing year, a
seeded random draw (seed 20261117) of 18 / 6 / 5 / 3 / 3 / 0 docket entries: **1,004 docket entries**, filed 1995-2026
(one 1991). Consolidated cases appear under several docket entries; duplicate opinions were removed by citation.
Fetching: one request at a time, at least 2 s apart on the API, back-off on 403/429/5xx, generic user agent.

### 2.3 Extraction, Lean classification, hand verification
`scripts/parse.py` reads the determination passage at the start of each opinion (tables and prose, including OCR'd
older PDFs) into year-records: deficiency plus each penalty or addition by section. What it cannot align is left
unparsed and counted. `scripts/check.py` writes the year-records as TSV and runs `lake exe run` (Lean), which labels
each record; every FLAG was then read by hand in the opinion (`scripts/verify_view.py`) and given a verdict in
`data/verdicts.json`. `scripts/stats.py` produces the tables below.

## 3. Coverage

| Stage | Count |
|---|---|
| Docket entries sampled / PDFs fetched | 1,004 / 1,004 (2,014 requests, all HTTP 200; no 403/429/5xx) |
| Unique opinions after removing consolidated duplicates | 929 (722 memorandum, 138 summary, 69 division; filed 1991-2026, about 30 a year from 1999) |
| No notice-of-deficiency figures in the opinion (CDP, fees, motions, TEFRA, syllabus-only) | 258 |
| Figures present but not aligned by the parser (left out, not guessed) | 136 |
| Parsed | 535 |
| Opinions with at least one in-scope penalty year checked by Lean | **389** (931 year-records) |
| Opinions with only pre-1990 sections (§6653, §6659, §6661: outside the formalised rules) | 9 |
| §6654 amounts seen (counted, not checkable) | 165 year-records |

## 4. Results

### 4.1 Opinion level (389 opinions with checkable figures)

| Class | Opinions | Share |
|---|---|---|
| **IRS figure agrees with Lean**: penalty = statutory rate × stated deficiency (20%, 40%, 75%; §6651(a)(1) 25% or 22.5% after (c)(1)) for every checked year | **173** | 44% |
| **Consistent with Lean**: within the statutory rate; the penalty was asserted on part of the deficiency (the opinion does not state that part, so it cannot be recomputed) | **152** | 39% |
| Apparent excess with a lawful explanation (40% valuation rate under a generic "§6662" label; carryback, Treas. Reg. §1.6664-2(f); non-qualified amended return; §6663 and §6662 pleaded in the alternative) | 7 | 2% |
| **Disagrees; corrected before decision** (IRS's own revised computation, or the court found the error) | 2 | 0.5% |
| §6651 addition computed on the tax shown on a late return as well as on the deficiency (late return stated in the opinion) | 5 | 1% |
| §6651(a)(1) above 25% of the deficiency, reason not stated; decision under Rule 155 or later computation | 8 | 2% |
| Other unexplained excess; court left the computation to Rule 155 (absorbed, so not counted as an IRS error) | 11 | 3% |
| **Unexplained excess or inconsistent figures not reconciled in the opinion** (decision not under Rule 155, or the opinion disposes of something else) | 6 | 1.5% |
| Parser error (false flag, checked by hand) | 16 | 4% |

By filing decade the picture is the same (agree + consistent: 1990s 46 of 59; 2000s 132 of 155; 2010s 106 of 123;
2020s 41 of 52).

### 4.2 Year-record level (Lean labels before hand verification)

| Rule | Exact | Within the rate | Flagged |
|---|---|---|---|
| §6662(a) 20% | 376 | 70 | 28 (+2 at exactly 40%) |
| §6663 75% | 77 | 12 | 4 |
| §6662(h) 40% | 4 | - | 2 |
| Mixed 20/40/75% portions (sum of implied bases ≤ deficiency) | 11 | 14 | 12 |
| §6651(a)(1) 25% max | 83 at 25%; **22 at exactly 22.5%** (the (c)(1) reduction applied); 1 at the §6651(a) minimum | 171 | 28 |
| §6651(a)(2)/(3) | - | 98 | 7 |
| §6651(f) 75% | 22 | 53 | 2 |

No year-record showed the IRS using a wrong *rate*: every exact match is at a statutory percentage, and the 22
records at 22.5% show the §6651(c)(1) interaction being applied.

### 4.3 Substantial understatement (§6662(d)(1)(A))
Six opinions with a deficiency of $5,000 or less discuss the substantial-understatement test. Five apply it
correctly (e.g. T.C. Summary Opinion 2008-57: "Petitioner's understatement is $4,970 ; thus, respondent has not met his
burden of production with respect to a substantial understatement"; T.C. Memo. 2014-126 leaves the test to the Rule 155
computation for a $6,300 deficiency). One does not (D1 below). In larger cases the 10% limb could not be checked: no
opinion in the sample states the tax required to be shown except incidentally (T.C. Memo. 2001-295 does, and is right).

### 4.4 §6751(b) (procedural, tagged only)
148 of the 929 opinions mention §6751(b); in 14 a phrase match finds the IRS failing to show timely written supervisory
approval (all after *Graev*, 2017). Not formalised: it turns on dates and who the "immediate supervisor" was. TIGTA's
2026 report (section 1) is the better evidence on this point: 13 of 829 reviewed docketed cases lacked valid approval,
7 with backdated approvals and over $68 million conceded.

### 4.5 Court outcomes on the accuracy-related penalty (phrase match, coarse)
Of 262 opinions with a stated §6662 amount: sustained in whole or part 89, mixed 36, not sustained or conceded 13, no
holding phrase found 124.

## 5. Verified disagreements (each read in the opinion; statute as in force for the year)

**D1. Ni v. Commissioner, 115 T.C. No. 37 (2000), docket 9820-99 et al.** The Nis Family Trust, 1995: deficiency **$83**,
§6662 penalty $17 (20%, correct). The court: "based on the deficiencies in tax determined by respondent, which we will
sustain, we find that all of the underpayments of tax here in question are attributable to substantial understatements
of tax." An $83 understatement cannot exceed "the greater of 10 percent ... or $5,000" (`ni_trust_not_substantial`).
Harmless: the court also found negligence ("Based either on the negligence of petitioners or their substantial
understatements"). A court misstatement, not an IRS error. Confidence high.

**D2. Summary Opinion 2010-109 (Panuthos, S.T.J.), docket 17006-09.** The IRS's own arithmetic, caught by the court:
"Respondent arrived at this amount by subtracting $ 5,261 as tax shown on the return from $19,821 as total tax ... In
fact, the return shows a tax due of $5,231 . Respondent has not sought an increase in the deficiency ; thus we will
treat it as a concession." $19,821 − $5,231 = $14,590, not $14,560: a $30 error in the taxpayer's favour, corrected
(conceded). The notice's §6651(a)(1) $4,947.75 is exactly 25% of $19,791 (deficiency plus the tax on the late return),
see D4 (`so2010_109`). Confidence high.

**D3. Watts v. Commissioner, T.C. Memo. 1999-416, docket 9289-98 (decision entered for respondent).** The opinion's
table: "1994 $3,624 [deficiency] $7,035 [§6651(a)(1)] $5,628 [§6662]; 1995 5,150 2,431 2,567". 20% of $3,624 is $724.80
and 25% is $906; both stated additions are instead exactly 25% and 20% of **$28,140** (`watts_1994_acc`,
`watts_1994_ftf`). 1995's penalty is 20% of $12,835 against a $5,150 deficiency. The returns were filed late (1994 "14
months late, on June 19, 1996"), so the (a)(1) figure may include tax shown on the late return (D4), but a §6662 penalty
cannot: the underpayment excludes tax shown on a return (§6664(a)). Either the opinion misprints the deficiencies or the
penalties exceed the statute; the decision document is not attached in DAWSON (paper case), so which one cannot be
settled. Nobody remarks on it in the opinion. Confidence: high that the figures as published are inconsistent; low on
whether the IRS's notice itself was wrong.

**D4 (pattern). §6651(a)(1) additions in notices computed on the whole balance due, including tax the taxpayer had
already reported on a late return.** §6665(b)(1) brings a §6651 addition into the deficiency procedure only "to that
portion of such addition which is attributable to a deficiency". Verified exactly in **Brown v. Commissioner, T.C.
Memo. 2018-91** (docket 4900-15): 2009 deficiency $5,538 and reported balance due $7,228; notice addition $3,192 =
25% of $12,766; 2010: $20,394 + $7,129, addition $6,881 = 25% of $27,523 (`brown_2009`, `brown_2010`). The court
describes it: "the section 6651(a)(1) additions to tax ... were computed on the basis of the net amounts due ... no
separate allocation was set forth in the notice as to what portion ... was attributable to (1) petitioners'
self-reported tax liability and (2) the determined deficiency", and notes the notice "incorrectly (and inexplicably)
listed the '[p]reviously assessed/previously agreed Failure to Pay Penalty' for 2009 as zero". The same shape (late
return stated in the opinion, addition above 25% of the deficiency): Norton, T.C. Memo. 2002-137 (1994: $25,457 vs 25% =
$25,307.50; return received 3 Jan 1996); Mansour, T.C. Memo. 2004-154 (1996: $23,494.20 vs $23,388; return received
28 Sep 1998); Chamberlin, T.C. Memo. 2000-50 (1985: deficiency **$0** with §6651(a)(1) $212 and (a)(2) $192; 1986
$2,991 against a $5,282 deficiency; returns filed 1988-1995); T.C. Memo. 2025-8 (2015: $11,948.50 vs $11,519.75;
return filed 18 Dec 2017); and D2. In Norton, Mansour, Chamberlin, T.C. Memo. 2025-8 and D2 the court sustained the
additions without allocating and left the amounts to Rule 155; in Brown the court set the problem out itself. This is a question of scope (what the notice may carry), not arithmetic: the amounts are lawful additions,
but the part on self-reported tax is assessable without a notice and outside the court's deficiency jurisdiction.
Confidence: high on the arithmetic; medium on the legal characterisation.

**D5. Cordes v. Commissioner, T.C. Memo. 2002-125 (Rule 155).** Joseph P. and Jean Ann Richard: "1994 $1,757,554 ...
$351,590; 1995 980,285 196,884". 20% is $351,510.80 and $196,057: excess $79.20 and $827. The other three petitioners'
rows in the same table are exact (e.g. "$1,759,679 $351,936"). No carryback is mentioned for the Richards. Left to the
Rule 155 computation, so not counted as an IRS error (`richard_1994`, `richard_1995`). Confidence: high that the stated
figures exceed 20%; the cause is unknown.

**D6. Swanson v. Commissioner, T.C. Memo. 2008-265.** Notice, 1995: deficiency $414,030, penalty $82,963 (20% =
$82,806.00, +$157). The IRS's own revised computation after trial: "1995 ... 191,486 ... 38,297.20", exactly 20%.
Corrected before decision.

**D7. T.C. Memo. 2011-9 (decision for respondent).** The opinion's table gives for 2004 a §6651(f) addition of
**$371,949.00** on a deficiency of $99,240 (the statutory maximum is 75%, $74,430) and, for 2003-2005, §6651(a)(2) amounts
of $127,077.67, $116,870.80 and $110,651.19 against deficiencies of $117,729, $99,240 and $96,829 (the cap is 25%). Every
other year in the same table is at or under the caps (e.g. 2002: $63,172.88 = 72.5%, $21,783.75 = 25%). The only issue
decided was liability for §6651(f). Probably a transcription error in the opinion's table; the decision document is not
public. Confidence: high that the printed figures exceed the statute; low on where the error sits.

Smaller unexplained excesses, all left to Rule 155 (listed in `data/verdicts.json`): T.C. Memo. 2014-126 ($1,269 vs
$1,260), 2001-164 (+$2.40), 2013-133 (§6663 up to $16,368 over 75%), Summary Op. 2003-131 ($2,212.20 on a $7,571
deficiency), 2001-295 (1992: $379 on $1,395), 2005-68 (§6663 $48,376.50 on $22,412), 2022-94, 2013-89, 2002-124
(§6662 on the whole deficiency plus §6663 on part), 2000-208 (several family members' 20%/40% portions exceeding the
deficiency by up to 3%). Not reconciled and not under Rule 155: T.C. Memo. 2006-145 (2000: $284 vs $269.20, decision
otherwise), 2020-16 (TEFRA; $652,266 vs 40% = $652,236.80; court held it lacked penalty jurisdiction), 2021-15 (+$4.20),
1997-24 (+$65).

Explained, not errors: T.C. Memo. 2009-289 (§6662(h) $79,334 on a $10,521 deficiency: the underpayment ignores an amended
return that is not "qualified"), 2015-185 (NOL carryback case, §1.6664-2(f)), 2014-26 and 2020-21 (40% valuation
penalties labelled "§6662"), 122 T.C. No. 6, 2024-66 and 1995-517 (fraud and accuracy penalties pleaded in the alternative).

## 6. Exemption revocations and denials (final adverse determinations)
459 final adverse determination letters in the harvested written determinations (271 denials of an application, 188
revocations; 304 under §501(c)(3), 55 (c)(7), 21 (c)(4)); by release year 2005-2025, concentrated in 2014-2016 and
2022-2023, which reflects what was harvested, not what the IRS issued. Stated grounds (keyword matches, several per
letter, boilerplate included): private benefit or inurement 383, not operated exclusively for an exempt purpose 333,
failure to establish or respond 274, commercial activity 254, organizational test 198, political or lobbying 118,
records or returns not kept or filed 105, social-club tests 76. There is no arithmetic to check. The one mechanical
trigger, automatic revocation for not filing for three consecutive years (§6033(j)), appears in 4 letters (201620012,
201622033, 202247016, 202335019), each about an organisation applying for reinstatement; every date is redacted
("20XX", "D"), so the three-year count cannot be checked.

## 7. Practitioner sanctions (OPR, Circular 230)
123 IRB announcements 2002-2026; 2,845 sanction rows parsed for 2004-2026 (the 2002-2003 layout was not parsed):
suspended 2,296, disbarred 318, censured 91, reinstated 135, disqualified appraisers 2. Grounds are published only from
late 2007: of the rows with a stated ground, loss of a state licence 1,126, criminal conviction 185, not filing or
paying one's own taxes 84, due diligence or false returns 19, injunction 2. 1,313 suspensions are expedited (§10.82).
The one mechanical trigger (§10.82: failing to file in 4 of the 5 preceding years) never appears as the stated ground of
an expedited suspension: all 15 expedited suspensions involving non-filing rest on a conviction (mostly 26 U.S.C. §7203).
A citation slip: Announcement 2009-7 cites "28 U.S.C. § 7203" for 26 U.S.C. §7203.

## 8. What was out of reach, and why
- **Final figures.** Opinions state the notice's figures; the figures actually entered (stipulated decisions, Rule 155
  computations) are mostly not public. Most disagreements above sit in Rule 155 cases and may have been absorbed.
- **Underpayment vs deficiency.** The penalty base is the underpayment; opinions state the deficiency. Carrybacks,
  non-qualified amended returns, prior assessments and refundable credits make them differ; the check is therefore an
  upper bound, and "consistent" cases (152) cannot be recomputed because the penalised portion is not stated.
- **§6654** needs installment dates and payments (165 year-records counted only). **§6651(a)(2)/(a)(3)** amounts usually
  appear as "to be computed". **§6651 minimum** applied in one record only.
- **Parser coverage.** 136 opinions with figures were not aligned automatically, and 16 flags were parser errors; the
  sample is random within keyword pools, not of all opinions (the `6662` pool hit DAWSON's 5,000-result cap).
- **CourtListener** needs an API token (not used); **Caselaw Access Project** bulk files are disallowed by
  robots.txt; **Pile of Law taxrulings** turned out to be IRS letter rulings, not opinions.
- **Appeals and CDP** determinations are not published. **Criminal cases** (CI report, press releases): sentences follow
  the Sentencing Guidelines, not a Code formula, so there is nothing for Lean to recompute.
- **§6751(b)** turns on dates and supervisory roles; tagged, not formalised.

## 9. Conclusion
Where the Tax Court's opinions let the IRS's penalty arithmetic be read, the IRS uses the statute's rates correctly: in
389 opinions (1991-2026) its accuracy-related, fraud and late-filing amounts equal the statutory percentage of the stated
deficiency in 173 and stay within it in 152 more, and 22 late-filing additions show the §6651(c)(1) reduction applied.
The few figures above the statutory bound mostly have lawful explanations or sit in Rule 155 cases the court recomputes;
the one recurring pattern is late-filing additions charged on the whole balance due, including tax the taxpayer had
already reported, which the Code keeps outside the notice of deficiency.

Files: `lean/Penalties.lean` (rules), `lean/Run.lean` (classifier), `lean/Verified.lean` (one theorem per verified
item; `#print axioms`: none or `propext`/`Quot.sound`), `scripts/` (fetch, parse, check, stats, opr, fad,
verify_view), `data/` (parsed.json, rows.tsv, classified.tsv, flags.json, verdicts.json, stats.json, fad.json,
su_candidates.json). Not published: `data/opr.json` (the practitioners' names and cities, as printed in the IRB; the
counts above are its summary, and `scripts/opr.py` rebuilds it from the IRB corpus) and `cache/` (sample.json, search
pools, 1,004 PDFs, request log).
