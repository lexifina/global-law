# Vulnerability heatmaps

Calendar heatmaps in the style of the well-known "Vulnerability Publications by Day" chart of CVEs: one panel per year,
seven rows (Mon to Sun), one column per week, the year's total at the left, and a grey → green → yellow/orange → red →
purple → near-black scale. No Lean was run for these; every count comes from existing outputs.

Rebuild: `python compute.py [CACHE_DIR]` (daily counts → `series/`, `series.json`), then `python plot.py` (PNG at
2200 px wide, SVG, a 1400 px WebP for the report, `heatmaps.json`). `plot.py` needs matplotlib. On this machine the
newest kiwisolver/contourpy wheels are blocked by Application Control; matplotlib 3.9.2 with kiwisolver 1.4.7 and
contourpy 1.3.0 load.

| Chart | Files | Years | Total | Peak day |
|---|---|---|---:|---|
| Decisions relying on bad law | `caselaw_bad_law_by_day.{png,svg}` | 1990–2019 | 49,541 decisions | 27 on Fri 30 Jun 2000 |
| Precedent broken | `caselaw_precedent_broken_by_day.{png,svg}` | 1990–2019 | 12,597 events | 14 on Wed 14 Feb 1996 |
| US Code vulnerabilities introduced (combined) | `uscode_vulnerabilities_by_day.{png,svg}` | 1995–2026 | 8,212 defects | 817 on Fri 19 Dec 2014 |
| …cross-references that start to dangle | `uscode_xref_by_day.{png,svg}` | 1995–2026 | 6,494 | 795 on 19 Dec 2014 |
| …amending instructions not executable as written | `uscode_amend_by_day.{png,svg}` | 2013–2026 | 1,198 | 106 on 10 Dec 2015 |
| …duplicate sibling designations | `uscode_dup_by_day.{png,svg}` | 1995–2026 | 520 | 94 on 12 Jan 2018 |

## A. US case law (caselaw-lean-2 run over 6.9M decisions)

Numbers below are generated from `series.json` and `heatmaps.json` (2026-11-12 23:30, the round-4 final run) by `update_md.py`; run it after `plot.py`.

### Decisions relying on bad law, by day

**Definition.** A decision counts once, on the day it was decided, if the Lean run reports at least one of
`citesOverruled`, `citesVacated`, `citesWithdrawn`, `citesNotCitable` or `appliesSupersededHolding` with it as the
citing decision (`out/findings.tsv`, rows from the 48M citation edges). These findings mean that on the citing date the
cited decision (or holding, issue-aware) already had a negative status in the citing court's chain of authority:
overruled or abrogated, vacated or reversed, withdrawn, superseded by statute, or not citable (unpublished or
depublished). Dates come from `data/decisions2.tsv`.

**Totals.** 88,704 citing decisions over all years (98,105 finding rows; 97,117 firm). 1990–2019: 49,541. Decisions with each kind (overlapping): cites overruled 24,103, vacated or reversed 21,565, withdrawn 4,009, not citable 1,223, superseded holding 0 (`appliesSupersededHolding` is not emitted: the data carry no conduct date). Generated from `heatmaps.json` of 2026-11-12 23:30.

**Peaks.** 30 Jun 2000 (27), 29 Jun 2001 (26), 25 Mar 1997 (24), 22 Dec 1994 (23), 31 Aug 1999 (23). Peaks are small (tens, not hundreds): the series is spread across many courts and days. The courts behind each peak day were last broken down for the first run and are not repeated here.
### Precedent broken, by day

**Definition.** One event per distinct witness row behind an `out/status.tsv` row of class `negativeAdmitted`: a
certified treatment (`data/treatments.tsv`) or same-case history row (`data/history.tsv`) that the Lean run gave
effect, so the treating court had power over the target. Each event is dated by the treating decision; all 22,384
decision-made events have the same date in the treatment/history row and in `decisions2.tsv`. The 15 supersessions by
statute have no treating decision and are dated by the day the effect starts.

**Totals.** 23,421 events over all years: reversed 11,742, overruled 8,922, vacated 2,067, withdrawn 656, abrogated 17, superseded 15, depublished 2. 1990–2019: 12,597 (overruled 3,855, reversed 7,047, vacated 1,290, withdrawn 390, superseded 15). The certificate checker passes more negative treatments than this; only the ones the run admitted with power count here.

**Peaks.** 14 Feb 1996 (14), 26 Feb 1998 (12), 19 Nov 1992 (11), 31 Dec 1992 (11), 16 Jun 2005 (11).
### Date precision

Many older decisions carry only a month or a year: 11.2% of all decision dates fall on the 1st of a month (chance is
about 3.3%), and in the 1790s–1870s most do. We treat a date as imprecise when it is 1 January, or when it falls on the
1st of a month in a court-year with at least three decisions on a 1st and more than 12% of its decisions on a 1st.
That flags 6,611 of 58,487 court-years and 598,750 of 6,892,454 decision dates; these are dropped (664 bad-law decisions and 244
broken-precedent events over all years, very few after 1940). A real decision on the 1st in a flagged court-year is
dropped with them. In 1990–2019 the share of 1st-of-month dates is the chance rate, so the charts are barely affected.

### Caveats

- **Range.** Bulk coverage falls from about 8,000 decisions a month to under 2,000 after mid-2019, and the run reports
  one bad-law finding after 2019, so the charts stop at 2019 and 2019 is partial.
- **Weekdays.** Weekends are nearly empty (bad law: 53 Saturday, 56 Sunday decisions in 30 years), as in the CVE
  original. Mondays are low (5,114 against 8,768–11,628 on other weekdays): Monday holidays, and many courts release
  opinions later in the week.
- **Not-citable** was the largest kind with "vacated or reversed" before the publication labels were corrected
  (21,400 decisions in 1990–2019; now 1,223, the smallest). A citation to an unpublished decision is not always
  improper (many courts allow it as persuasive), so this part still over-counts reliance on bad law.
- Findings are only as good as the citation edges and the reader's treatments; see the Evaluation section of the
  report for measured precision.

## B. The US Code (uses/xrefs, uses/amendments)

**Combined definition.** One count per defect introduced into the Code on a day, summed over three kinds:

1. **Cross-references that start to dangle** (`uses/xrefs/dangling_episodes.tsv`): an explicit reference (a section of
   a title, a designation within it, or a subsection of the same section) that resolved and was then broken by a later
   law or edition (class `broken`, 3,566), or was written so that it never resolved (class `written`, 2,928). Dated by
   the day of the change that broke or wrote it. The 2,824 episodes already dangling at the record start (Jan 1995) are
   left out. Held-out audit: 68% real (Wilson 52–80%).
2. **Amending instructions not executable as written** (`uses/amendments/data/results.tsv`): Lean class `not_found`
   (the struck words are nowhere in the section), main scope only (the record credits the law with a change to that
   section), laws of the 113th–119th Congresses (2013 on; older laws have no USLM). Dated by the law's enactment
   (approval) day from `instructions.jsonl`; effective dates are rarely stated. 1,198 operations. Only `not_found`
   is used because it is the one failure class the audit found mostly real (18 of 20). Of those 18, 16 are the Code's
   editorial wording (the Act strikes "section 6", the Code prints "section 2605 of this title"), so most are
   "cannot be executed against the Code's text as printed", not drafting errors. Left out: `no_target` (4/20 real,
   1,582), `wrong_target` (9/20, 260), `ambiguous` (7/20, 404).
3. **Duplicate sibling designations** (from `uses/xrefs/data/scan.pkl` over `usc/versions.tsv`, the same computation as
   `duplicates_laws.tsv`): a designation that appears twice among siblings, dated by the section version that first
   made it. The 122 present in the 1994 edition at the record start are left out; 520 counted. Audit: 13 of 20 real
   (7 were the record printing a clause at the wrong indent).

**Totals (1995–2026).** 8,212 = 6,494 cross-references + 1,198 amendments + 520 duplicates.

**Peaks.**
- **19 Dec 2014, 817** (795 references, 18 amendments, 4 duplicates). Pub. L. 113-287 enacted title 54 (National Park
  Service and related programs), moving the laws out of title 16: 730 references broke in one day. The FY2015 NDAA
  (Pub. L. 113-291) and Pub. L. 113-295 were signed the same day. Most were rewritten in the next edition 17 days
  later.
- 14 Jan 2019, 248: the 2018 edition of the US Code (244 references written or broken by the edition).
- 1 Jan 2021, 197: the FY2021 NDAA (Pub. L. 116-283), enacted that day over the veto.
- 23 Mar 2010, 177: the Affordable Care Act (Pub. L. 111-148).
- 6 Jan 2017, 165: the 2016 edition (153).
- Per kind: amendments peak 10 Dec 2015, 106 (Every Student Succeeds Act, Pub. L. 114-95, then 21st Century Cures Act
  13 Dec 2016, 62); duplicates peak 12 Jan 2018, 94 (causes that day: the 2017 edition of the Code, 114 defects across
  kinds, and the Tax Cuts and Jobs Act, 40).

**Caveats.**
- Before 2017 the record dates a change on the day the law was enacted, not the day it took effect; editions appear
  as single big days (the release date of the edition).
- Fridays dominate (2,706 of 8,212): laws are often signed and editions released then. Weekend days are real here
  (bills signed on Saturdays, records dated on effective dates such as 1 January); they are not date-precision
  artifacts.
- Amendments cover only 2013 on, so the combined chart understates earlier years against later ones.
- Dangling references count once per designation named ("subparagraph (A), (B), (C), or (D)" is four).
- These are defects in the text, not proof that the law cannot be read: the Code's editors explain most in notes
  ("References in Text", "So in original").
