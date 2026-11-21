# Malta (income 2025 = year of assessment 2026): findings

Model: `~/cmp20/southeast/mt/lean` (lib `MtTax`, exe `mttax`). Statute texts in `law/` (Global law, official publisher
legislation.mt); official PDFs of Act IX of 2025, Act III of 2026 and L.N. 10 of 2025 in `refs/`. Every Lean name
below is proved (no `sorry`) in `MtTax/Findings.lean` or `MtTax/Theorems.lean`. Sources searched before calling
anything new: the EUROMOD Malta country report 2021-2024 (JRC141187), the ITA / ITMA / SSA texts and their
histories, the IE and PT CATALOGUE.md files (3 sources; the CfR and DSS websites refuse automated access, 403).

### F1 Dividend "relevant thresholds" still at the old band points
- kind: statute-fault (amount not updated when a related amount changed)
- provisions: ITA art. 12(1)(c)(iii)(C)(b) ("the relevant threshold is €28,700 / €19,500 / €21,200"); art. 56(1)
  as substituted by Act IX of 2025 (YA 2026) and by Act III of 2026 (YA 2027); ITMA art. 48(1) proviso (a).
- what: a dividend from a taxed account (not the final tax account) to an individual whose chargeable income
  without it reaches the threshold is exempt, so the 35 % company tax becomes final (no imputation refund). The
  three thresholds are the YA 2025 points where the old tables switched from "25 % - 2,815" to "25 % - 2,725" (and
  the married/parent equivalents; F3). Act IX of 2025 moved every band (25 % now starts at €16,000 / €23,000 /
  €17,500); Act III of 2026 added four tables and renumbered this provision's cross-references ("56(1)(b)(i)",
  "56(1)(b)(ii), (iv) and (v)") but left the amounts. The thresholds now sit inside the 25 % band of every table
  (Lean `f1_thresholds_inside_25pct_band`); for YA 2027 married parents of two (25 % from €32,000) €28,700 is in
  the 15 % band.
- households / amounts: single owner, salary €17,000, €3,250 net dividend (gross €5,000) from an unlisted company:
  €600 income tax instead of €850, i.e. €250 of company tax refunded on the €2,500 below the threshold
  (`f1_refund_below_stale_threshold`). Up to €350 (single), €570 (married), €370 (parent) a year is refundable that
  would not be if the thresholds tracked the start of the 25 % band. For a closely-held company the threshold, not
  the table, sets the rate: all-dividend pay at 2 AW of profit costs 26.9 % (listed-share rules 20.7 %;
  `results/owner_mt.json`).
- status: confirmed in the consolidated text at 2025-06-30 and 2026-10-06 (`law/cap123_art12_diff_2025_2026.txt`).
  The Act does not state the thresholds' purpose; we report the mismatch, not a "correct" value.

### F2 Act III of 2026: one-child parent table subtracts €10,270, not €10,275
- kind: statute-fault (next year: YA 2027, income 2026)
- provisions: ITA art. 56(1)(b)(iv)(d) inserted by Act III of 2026 s. 13 ("35% and then subtracting €10,270");
  official PDF `refs/Act_2026_3.txt` line 839 (not an OCR slip).
- what: every other Maltese table is continuous; here 25 % x 60,000 - 4,275 = 10,725 but 35 % x 60,000 - 10,270 =
  10,730. Earning €60,001 instead of €60,000 costs €5.35 (`f2_parent1_2027_jump`), and every parent of one child
  above €60,000 pays €5 a year more than the table's lower bands imply (`f2_continuous_with_10275`).
- status: confirmed in the official enacted text. Draft note (not filed) for the Ministry for Finance: "Cap. 123
  art. 56(1)(b)(iv)(d) (Act III of 2026): the subtraction €10,270 makes the table discontinuous at €60,000 (tax
  jumps by €5.35); the continuous value is €10,275, as in the pattern of the other tables."

### F3 The YA 2025 tables had €90 / €120 / €105 notches (removed for YA 2026)
- kind: statute-fault (historical, income 2024)
- provisions: ITA art. 56(1)(a)/(b) before Act IX of 2025 (`law/cap123_art56_diff_2024_2025.txt`): single "less than
  €19,501 ... 25% ... €2,815" then "exceeds €19,500 ... 25% ... €2,725".
- what: €19,500 -> €19,501 raised tax by €90.25 (`f3_single_2025_notch`); married €120.25 at €28,700
  (`f3_married_2025_notch`); parent €105.25 at €21,200 (`f3_parent_2025_notch`). Removed by Act IX of 2025 (YA 2026
  tables are continuous: `single_no_jump`, `married_no_jump`, `parent_no_jump`). The F1 thresholds are their fossil.

### F4 YA 2026 wording leaves the band edges uncovered
- kind: statute-fault (drafting; no money at stake)
- provisions: ITA art. 56(1): "exceeds €15,000 but is less than €23,000" then "exceeds €23,000" (the pre-2025 text
  used "less than €21,201" and covered every euro).
- what: chargeable income of exactly €16,000, €23,000, €17,500 or €60,000 matches no formula. Both neighbours give
  the same tax there (`f4_gaps_harmless`); table = formula for every income (`single_eq_formula`,
  `married_eq_formula`, `parent_eq_formula`).

### F5 Tenth Schedule (Class One) rows misprinted in L.N. 10 of 2025
- kind: gov-error (published legal notice, repeated in the consolidated Cap. 318)
- provisions: SSA Tenth Schedule Part I as substituted by L.N. 10 of 2025 (official PDF, `refs/LN_2025_10.txt`, pp.
  B 90-91): category C (born 1962+) "does not exceed €523.28"; the €42.31 row of category D reads "Persons born on
  1 January 1962 or after ... exceeds €532.29"; the €53.23 row "... exceeds €515.99".
- what: read literally, nobody born in 1961 or earlier earning over €423.07 a week has a category (the €42.31 row
  names the wrong cohort), and a person born 1962+ earning €516.00-€523.28 a week is in both C (10 % = €51.60) and
  D (€53.23): €1.63 a week, €84.76 a year apart (`f5_overlap`); from €523.29 to €532.29 only the flat €53.23
  applies although 10 % is less (`f5_gap_for_old_cohort_literal`). mttax uses the intended reading (C to €532.28 /
  €423.07, D above; EUROMOD Table 2.19 and Note 2's €27,679.09).
- draft note (not filed) to the DSS / Legislation Unit: "L.N. 10 of 2025, Tenth Schedule Part I: the €42.31 row of
  category D should read 'born on 31 December 1961 or before ... exceeds €423.07'; the €53.23 row 'exceeds
  €532.29'; category C (born 1962+) should end at €532.28, not €523.28."

### F6 Joint computation is the default and costs two-earner couples up to €8,850 a year
- kind: loophole-known (election)
- provisions: ITA art. 49 (joint by default), art. 50 (separate computation: "the responsible spouse may elect",
  year by year, only for the other spouse's income from employment, trade or pension; other income goes to the
  higher earner), art. 49A (separate returns: until revoked, then 4 years' bar), art. 56(1)(b) (each spouse's
  table; parent table where "a parent maintained under his or her custody a child").
- amounts: two earners on €60,000: joint €31,450, separate €23,200 (`f6_separate_saves_8250`); with a child
  €22,600 (`f6_separate_saves_8850_with_child`); two parents on €13,000 each: €1,950 joint, €0 separate
  (`f6_low_earners`). Bounds over every split: separate saves at most €8,250 / €8,850 (`separate_saving_le`,
  `separate_parent_saving_le`), joint at most €1,150 / €850 (one earner; `joint_saving_le`,
  `joint_parent_saving_le`). Found blind by the generic unit scanner: election_gain 8,850 at 3.7 AW, 50 %, 2
  children; marriage bonus 1,150.
- note: the parent table for each spouse under separate computation follows the wording (the proviso sits in para.
  (b), which names "each spouse where ... separate computation"); EUROMOD says "single person's rate" (F10).

### F7 Lone parents: €1 of maintenance, or living with the other parent, costs up to €850
- kind: loophole-new (notch; not found as a quantified notch in the 3 sources searched)
- provisions: ITA art. 56(1)(b) proviso (a)-(b): an unmarried/separated/divorced parent gets the married table only
  if (iii) "not in receipt of any financial assistance in respect of the maintenance of the said child from the
  other parent" and (iv) "not living or residing at the same house with the other parent"; otherwise the parent
  table. Maintenance itself is exempt (art. 12(1)(t)). Kept by Act III of 2026 as (b)(iii)(A)-(D).
- amounts: lone parent on €23,000: €1,200 on the married table, €2,050 if any maintenance is received
  (`f7_lone_parent_cliff`); €850 at every income from €23,000 up (`f7_gap_le_850`). A €1 transfer costs €850.

### F8 Class One minimum: a €1,110 notch at the first euro of wages
- kind: loophole-known (design). SSA Tenth Schedule cat. B (€21.35 a week up to €213.54); art. 7(2)(a) proviso
  (only part-timers may elect 10 %). `f8_class1_floor`; found blind by the METR and edges scanners ("1,109 at 0").

### F9 Owner-manager: dividends beat salary; above €19,500 the company tax is final
- kind: loophole-known (income-type conversion) + lead
- provisions: ITA art. 56(6) (35 %), arts. 31, 59-60 (full imputation), art. 12(1)(c)(iii) (F1); SSA Tenth
  Schedule (Class One on both sides, each capped at €53.23 a week).
- amounts (`harness/owner_mt.py`, `results/owner_mt.json`, one-person company, profit fully paid out): all-dividend
  is cheapest at every level: total tax 4.3 % vs 20.9 % all-salary at 0.5 AW (€16,434), 18.7 % vs 29.4 % at 1 AW,
  26.9 % vs 27.7 % at 2 AW, 33.4 % vs 33.5 % at 10 AW (`f9_owner_dividend_declared`). Not modelled: Class Two on
  the investment income of a person with no employment (EUROMOD §2.6.4), which narrows the gap.
- lead (NOT confirmed): ITMA art. 48(4A) lets "a person in receipt of a dividend" claim six-sevenths of the company
  tax; art. 48(5)(b) reduces the credit only "when such dividend is included in the chargeable income", and ITA
  art. 12(1)(c)(iii)(B) blocks only the art. 48(1) and art. 60 refunds. On the text, a resident owner above the
  threshold could keep an exempt dividend and the 6/7 refund: 5.2-6.5 % in all (`rate_with_6_7`), the "5 % route"
  usually described for non-resident shareholders (CATALOGUE K3). CfR practice not checked (site refuses automated
  access): a question for the CfR, not a result.

### F10 EUROMOD's Malta description disagrees with the statute in four places
- kind: gov-error (EUROMOD CR MT 2021-2024, JRC141187; documentation only, its code not inspected)
- (a) §2.7.1 lone-parent married rates: "The individual was in receipt of financial assistance ... from the other
  parent" where the Act says "was not in receipt" (art. 56(1)(b) proviso (b)(iii)); and "not over sixteen" where
  the Act says 18 (23 in education). (b) §2.7.4 parent computation: "not over 21 years if receiving full-time
  instruction"; the Act says 23. (c) §2.7.3 "Social insurance contributions (Class One and Class Two) are deducted
  from the gross income earned": art. 14 lists no such deduction (mttax deducts none; to confirm with the CfR).
  (d) §2.7.1 separately computed spouses taxed "at the single person's rate": the parent proviso applies (F6).
- classification: error (a), (b); reading (c), (d). Draft issue (not filed) to the EUROMOD MT team: "CR MT
  2021-2024 §2.7.1 states the lone-parent condition as 'was in receipt of financial assistance'; Cap. 123 art.
  56(1)(b) proviso (b)(iii) requires that the parent 'was not in receipt'. §2.7.1 and §2.7.4 give ages 16 and 21
  where the Act gives 18 and 23."

### F11 The 2025 contribution and children's-allowance schedules were not published by October 2026
- kind: gov-error (publication lag)
- provisions: SSA arts. 7, 76; Tenth and Fourteenth Schedules. L.N. 10 of 2025 (published 10 January 2025) set the
  2024 amounts retroactively ("deemed to have come into force on 1st January 2024"); Global law's record to
  2026-10-06 shows no later change, and legislation.mt L.N. 1-60 of 2026 contain no schedule amendment.
- what: the 2025 amounts actually collected (uprated administratively each January) have, on the published record,
  no schedule in force yet. mttax uses the text in force (2024 amounts) and says so in `unsupported`.
- evidence (Eurostat earn_nt_net 2025, `results/eurostat_check_2025.txt`): the EC model charges a 2025 maximum of
  EUR 2,838.14 a year (EUR 54.58 a week, about 10 % of a EUR 28,381 ceiling) against the schedule's EUR 53.23
  (EUR 2,768): EUR 70 a year per employee at or above the ceiling is collected on amounts not yet in the published
  schedule.

### F12 Eurostat 2025 referee: what it adds and where it differs (household level)
- kind: model-fix (conventions; no model change) / confirmation
- source: Eurostat earn_nt_net 2025 for MT (13 OECD-method household types), `harness/eurostat_check.py`:
  52 lines, 14 within EUR 1, 22 within 1 %.
- confirms: two earners on 2 AW pay exactly mttax's separate-computation tax (EUR 9,634 without children, EUR 9,034
  with two children). The second figure requires the parent table for EACH spouse under art. 50, i.e. the statute's
  wording, not EUROMOD's "single person's rate" (F6, F10(d) now settled for the EC model).
- differs, explained: (1) every other TAX line is lower by a constant per return (EUR 95.5 single up to 0.8 AW,
  EUR 60 single from 1 AW, EUR 110 married one-earner, EUR 65 separate couples under EUR 60,000, EUR 105 lone
  parent, zero for returns above EUR 60,000): the annual budget tax refund, not in Cap. 123 or any S.L. found in
  Global law (search_law "refund of tax rules"), so not modelled; (2) the lone parent is charged on the parent
  table (EUR 1,805 less the refund), not the married table of art. 56(1)(b) proviso (a): Eurostat's convention
  treats the proviso conditions as not met; mttax keeps the statute default (`mtLoneParentConditions`, F7);
  (3) SOC: 2025 administrative ceiling (F11) and 10 % with no minimum for a second earner below the minimum wage
  (part-time election, SSA art. 7(2)(a) proviso); (4) FAM EUR 3,460 / EUR 2,880 for two children vs the
  Fourteenth Schedule's EUR 901 / EUR 934: supplements outside the schedule, not modelled; (5) NET adds in-work
  benefit for low-paid singles (EUR 2,085 at 0.5 AW).
