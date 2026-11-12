# Draft subsection for the blog post (section 7, after "Does the change matter?")

### Watching the sections you depend on

The same record answers a forward-looking question. A lawyer who relies on 18 U.S.C. § 924(c), or a firm whose
practice rests on thirty sections of the Bankruptcy Code, wants to know when Congress changes them. We built a watch:
give it a list of citations, or any document, and a date, and it reports every change since, the law that made it,
and the words struck and inserted.

Lean makes the decision to alert. A watch raises an alert for each law that came into force after the date and
changed the words watched. A version made by an edition of the Code, a reprint or an editorial change, never alerts.
If it changed the words it is listed apart, as a notice. Lean proves three things about this rule. With no alert and
no notice, the words in force today are the words in force on the date. Watching from an earlier date gives every
alert a later date gives, and possibly more. And an edition never alerts: every alert is one of the law changes the
statute model already counts.

The watch follows the deepest designation the citation names. Watching § 924(c)(1)(A), the five-year minimum for
carrying a gun during a drug crime, and § 924(c)(1)(C), the 25 years for a "second or subsequent conviction", shows
why that matters. The First Step Act of 2018 rewrote (c)(1)(C). It left (c)(1)(A) alone, so a watch on (c)(1)(A)
stays quiet.

<figure: figure.svg>

We ran it on a firearms and drug sentencing list of 22 provisions, watched from 1 January 2015. Eight alert, from
five laws: the First Step Act (2018), the Consolidated Appropriations Act, 2022, the Bipartisan Safer Communities Act
(2022), the defense authorization act for 2025, and the HALT Fentanyl Act (2025). Seven provisions had other parts of
their section amended but not the words watched. Six did not change at all. A bankruptcy list of 30 provisions, over
the same years, gets 11 alerts from 7 laws, most from the Small Business Reorganization Act of 2019 and the pandemic
laws that raised its debt limit and later let it lapse.

A document works the same way. *Texas v. United States*, the Fifth Circuit's 2015 decision against the deferred-action
program for parents, cites 49 distinct provisions of the Code. Watched from the day it was decided, four have since
been changed by a law: the eligibility rules for public benefits (8 U.S.C. § 1641, 2020), adjustment of status
(§ 1255, 2022), the asylum statute's fees (§ 1158, 2025) and the earned income credit (26 U.S.C. § 32, 2021). For 17,
a law amended another part of the section. The exemption from notice and comment at the center of the case, 5 U.S.C.
§ 553(b)(A), reads as it did. Seven more changed only in an edition: the 2015 edition of title 8 dropped "of this
section" from its cross-references, which is not a change in the law and does not alert.

Run weekly over a date range, the same check is a digest for a firm. For the 25 sections courts cite most, the last 12
months of the record (to 3 November 2026) brought one change: the Consolidated Appropriations Act, 2026 amended ERISA's
civil enforcement section, 29 U.S.C. § 1132. For the 100 most cited, three laws changed three sections.

It is cheap. A watch over those 100 sections since 2015, 169 versions in all, takes 3 to 6 seconds on one desktop
machine, of which Lean takes about one. Over the 1,000 most cited sections it takes 17 seconds.

The limits are the record's and the reader's. An alert is only as good as the record's credit for each change. When
the record cannot say which law made a change, it credits it to the next edition, and the watch reports a notice, not
an alert. The First Step Act's rewrite of the drug penalties in 21 U.S.C. § 841(b)(1)(A), from 20 years to 15 for a
second offense, is one: the record credits it to the 2018 edition. The watch marks any edition notice that changes 20
or more words for review. Over the 1,000 most cited sections since 2015, 346 of 609 edition notices do, so this is not
rare. Below the subsection, the watch finds a paragraph by its designation in the printed text, which fails on some
layouts; it then watches the parent and says so. A section moved to another title (such as the transfers to title 34
in 2017) is reported as moved, but the watch does not yet follow it there. And an alert says the words changed, not
that the change reaches the point a reader relies on.

---

## Checkable claims (paths under ~/Documents/us-caselaw-lean-work/uses/watch/ unless given)

- Rule and proofs: lean-proofs `LegalProofs/USCaseLaw/Watch.lean` (`alerts`, `notices`; `no_alert_same_words`,
  `no_alert_subDiffers`, `no_alert_wordsDiffer`, `alerts_mono`, `alert_mono`, `alert_byLaw`, `alert_mem_lawChanges`,
  `no_law_no_alert`); runner `RunWatch.lean`; tool `tools/caselaw/usc_watch.py`.
- § 924(c)(1)(A) vs (c)(1)(C): demo_practice/firearms.txt, .json, .html.
- Firearms 22 / 8 alerts / 5 laws / 7 other parts / 6 unchanged / 1 edition only: demo_practice/firearms.json.
- Bankruptcy 30 / 11 alerts / 7 laws (Pub. L. 116-51, 116-54, 116-136, 116-189, 116-260, 117-151, 117-347):
  demo_practice/bankruptcy.json.
- Texas v. United States, 809 F.3d 134 (decided 2015-11-25): 49 items; 4 alerts (Pub. L. 116-260, 117-2, 117-103,
  119-21); 17 other parts; 7 edition only; 21 unchanged: demo_opinion/watch.*.
- Top 25 digest 2025-11-04 to 2026-11-03: demo_top25/digest.*; top 100: demo_top25/digest_top100.* (Pub. L. 119-75,
  118-42, 119-124).
- Timing and the 1,000-section run: timing/timing.md, timing/*.json.
- 841(b)(1)(A) credited to the 2018 edition: versions.tsv rows for title-21/841.md (no row for Pub. L. 115-391);
  the notice's diff in demo_practice/firearms.json.
