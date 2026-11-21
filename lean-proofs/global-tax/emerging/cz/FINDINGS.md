# Czechia 2025: findings

### F1 OECD taxes the unrounded wage; § 16 odst. 2 rounds the base down to the hundred
- kind: model-fix (referee convention), households: all 8 OECD TW types.
- amounts: CGITLETC/CGITFP differ by −3 to −18 CZK = 15 % × (wage mod 100) per earner (S100 87 705 vs 87 712; M100_67 −18).
- provisions: ZDP § 16 odst. 2 ("zaokrouhleného na celá sta Kč dolů"); daňový řád § 146 odst. 1.
- who is right: the statute; the OECD's CGITLETC 87 712 = 15 % × 584 744 exactly (convention, not an error that
  matters: ≤ 23 CZK). Lean: `roundBase_saving`, `Tests.lean` (87 705).
- status: explained.

### F2 Contributions are computed and rounded each month; the OECD applies 11,6 % to the annual wage
- kind: model-fix (referee convention), households: all 8 types.
- amounts: EECSSC +5 to +29 CZK a year (S67 45 468 vs 45 446): 12 social + 12 health monthly roundings up
  (ZPSZ § 7 odst. 3, ZPVZP § 2 odst. 2) and the employee third of the rounded health premium (ZVZP § 9 odst. 2).
- who is right: the statute (monthly rozhodné období); the OECD's annual rate × wage is a convention. THP agrees to
  ≤ 11 CZK in every case.
- status: explained.

### F3 § 35c odst. 7 still preserves a "maximální výše daňového bonusu podle odstavce 3" that no longer exists
- kind: statute-fault (dangling cross-reference), households: parents of a ZTP/P child.
- provisions: ZDP § 35c odst. 7 (2025 text: "maximální výše daňového bonusu podle odstavce 3 zůstává zachována");
  § 35c odst. 3 lost its cap "maximálně však do výše 60 300 Kč ročně" through zákon č. 609/2020 Sb., čl. II bod 66
  (in force 2021-01-01). Global law phrase_history: the phrase was added by zákon 669/2004 Sb. (2005-01-01) and
  never removed; "60 300 Kč" removed 2021-01-01. Confirmed on e-Sbírka versions 2020-11-03 and 2025-10-01.
- effect: none on the amount (the cap is gone), but the sentence says the doubled ZTP/P amount must respect a
  maximum that § 35c odst. 3 no longer states; a reader could take it to cap the bonus at the undoubled amount.
  Lean: `bonus_le_childCredit` (the only maximum today is the zvýhodnění itself).
- classification: error (drafting remnant). Draft fix: delete "; maximální výše daňového bonusu podle odstavce 3
  zůstává zachována" from § 35c odst. 7.
- status: confirmed.

### F4 Přídavek na dítě for the whole of 2025
- kind: model-fix, households: SP67, M100_0 (OECD CTGG 35 280 = 2 × 1 470 × 12, zvýšená výměra, ZSSP § 18 odst. 3).
- provisions: ZSSP §§ 17–18 (version 2025-05-01) were repealed from 2025-10-01 (dávka státní sociální pomoci,
  zákon č. 151/2025 Sb.); zákon č. 152/2025 Sb., část 10, čl. 14 bod 1: a přídavek already granted "se vyplácí
  příjemci ve stejné výši" until 31 December 2025 (31 March 2026 if a DSSP claim is filed). So 12 months of 2025 is
  right for a family already receiving it (the OECD convention); a new claim from October 2025 falls under the DSSP,
  not modelled (`czPridavekMonths`).
- status: explained.

### F5 Forgo a child credit to qualify for přídavek na dítě (N1)
- kind: loophole-new. households: couple, one earner 730 930 Kč (1,25 AW), spouse without income, children 6 and 11.
- amounts: default (earner claims both children): no přídavek (family net 50 405 Kč/month > limit 49 674); the
  earner does not claim the first child (or the non-earning spouse "claims" it and cannot use it): tax +15 204,
  family net 49 138 < 49 674 → přídavek 35 280 Kč; **gain 20 076 Kč a year**. With children 1, 6, 11: 36 036 Kč.
- provisions: ZSSP § 5 odst. 1 písm. a) (income counted "po odpočtu daně z příjmů připadající na tyto příjmy"), § 17
  (3,4 × životní minimum, all-or-nothing), § 18 odst. 3; ZDP § 35c odst. 1 (a right, not a duty), odst. 4, odst. 9.
- mechanism: the means test counts income after tax, so paying more tax lowers counted income; at the cliff one
  crown of extra tax is worth 35 280 Kč of benefit.
- Lean: `n1_forgo_credit_gain` (Walls.lean, `decide` on the full household computation).
- known? not found in 6 sources searched (ZSSP text; MPSV "Úplný výčet příjmů pro posouzení nároku na přídavek na
  dítě"; MF "Kvantifikace daňových úlev 2023"; Finanční správa paušální-daň page; Grant Thornton/PAQ 2025; one web
  search on přídavek / rozhodný příjem / daňový bonus / druhý rodič, which returned benefit guides only).
- persistence: the dávka státní sociální pomoci (zákon č. 151/2025 Sb., from 2025-10-01) uses the same definition
  (§ 4 odst. 1 písm. a), odst. 2: "po odpočtu daně z příjmů fyzických osob připadající na tyto příjmy"); its other
  conditions are not modelled.
- status: model-proved; reading-dependent (assumes the Úřad práce uses the tax actually withheld, as the employer
  income confirmation reports it).

### F6 Let the low earner claim the children: same tax, lower counted income (N2)
- kind: loophole-new. households: couple 700 000 + 150 000 Kč, children 4, 8, 12.
- amounts: total income tax identical either way (the bonus is refundable; both pass the 124 800 Kč test), but when
  the low earner claims, the high earner's tax is not reduced and the low earner's bonus (65 364 Kč) is not income
  under ZSSP § 5: the family passes the přídavek test → **51 240 Kč a year** (1 330 + 1 470 + 1 470 Kč × 12).
- provisions: ZSSP § 5 odst. 1 (the bonus is not in the list; the MPSV úplný výčet confirms), § 17; ZDP § 35c
  odst. 3, 9; § 35d (the bonus is paid monthly by the low earner's employer).
- Lean: `n2_allocation_gain` (tax equal, burden differs by 51 240).
- known? not found in the same 6 sources. Same persistence note as F5.
- status: model-proved; reading-dependent (as F5).

### F7 Přídavek na dítě cliff: 35 280–51 238 Kč lost for one crown
- kind: loophole-known (cliff; found blind by the kernel METR scanner). households: single parent, children 6 and
  11: limit at wage 494 436 Kč; one-earner couple, children 6 and 11: 719 010 Kč; children 1, 6, 11: 788 784 Kč.
- provisions: ZSSP § 17 (all-or-nothing at 3,4 × životní minimum), § 18; NV 436/2022 (životní minimum).
- amounts: net income falls by 35 278 / 35 279 / 51 237 Kč for one more crown of wage (`runs/notches.md`).
- status: confirmed; the 2025-10 DSSP replaces the cliff with a withdrawal (pracovní bonus, zákon 151/2025 § 41).

### F8 Paušální daň band edges are notches of up to 124 728 Kč
- kind: loophole-new (timing: keep the year's receipts at the band limit). households: OSVČ in the paušální daň.
- amounts: one crown above 1 000 000 Kč (40 % class) moves the whole year to band 2: +96 348 Kč; above 1 500 000 Kč
  (40 %) to band 3: +124 728 Kč; 1 500 000 (60 %): +96 348; 2 000 000 (60 %, out of the regime): +70 700;
  2 000 000 (80 %): +26 520.
- provisions: ZDP § 2a odst. 5, § 7a odst. 1 písm. a), § 38lk odst. 7; ZPSZ § 14 odst. 3; ZPVZP § 3a odst. 5.
- Lean: `pausal_band_notch` (96 348 Kč).
- known? the bands are published with examples (Finanční správa); the size of the one-crown notch was not found in
  the 6 sources searched.
- status: confirmed.

### F9 Other notches (known by design)
- kind: loophole-known. Bonus test 124 800 Kč (ZDP § 35c odst. 4): one crown is worth 15 204 Kč (1 child) to
  65 364 Kč (3 children) (`bonus_notch_124800`); spouse credit at 68 000 Kč of the spouse's income (§ 35bb odst. 2):
  24 840 Kč (`spouse_credit_value`); DPP at 11 500 Kč a month (ZDP § 6 odst. 4, zákon 187/2006 § 7a): 16 022 Kč a
  year (`dpp_notch_year`); side OSVČ at the rozhodná částka 111 736 Kč (zákon 155/1995 § 10 odst. 2): 17 948 Kč
  (`side_threshold_notch`).
- status: confirmed; all four are all-or-nothing tests with no taper.

### F10 Monthly withholding never under-collects, and over-collects 100–123 Kč a year on average
- kind: gov-error? no: statute design (classification: convention written into the statute). households: one
  employer, steady wage 1–300 000 Kč a month, 0–3 children (1,2 million cases, `runs/wh_summary.txt`).
- amounts: settlement (withheld − annual tax) ≥ 0 in every case; mean 122,5 Kč (no children), max 284 Kč; with
  children max 684 Kč (a monthly bonus below 50 Kč is not paid, § 35d odst. 4; the annual minimum is 100 Kč,
  § 35c odst. 3).
- provisions: § 38h odst. 1 (monthly base rounded up to the hundred) vs § 16 odst. 2 (annual base rounded down);
  § 38h odst. 2 (monthly threshold 3 × AW = 1/12 of 36 × AW).
- Lean: `withholding_ge_annual` (never under-collects before credits, all wages), `withholding_excess_le` (≤ 312 Kč).
- note: the excess comes back only through the roční zúčtování or a return; the spouse credit is never given
  monthly (§ 35d odst. 1).
- status: proved.

### F11 The spouse-credit income limit has not moved since 2008
- kind: statute-fault (classification: policy / un-indexed amount, not an error). households: one-earner couples
  with a child under 3.
- provisions: § 35bb odst. 2 písm. b) "68 000 Kč": in ZDP since 2008-12-31 (zákon č. 482/2008 Sb.; Global law
  phrase_history), unchanged; related tests in the same act are indexed to the minimum wage (bonus 6 × minimum wage,
  § 35c odst. 4; pension exemption 36 × minimum wage, § 4 odst. 1 písm. g)). In 2025, 68 000 Kč is 3,3 months of
  minimum wage (20 800 Kč).
- status: confirmed (amount history).

### F12 The MF tax-relief quantification leaves out the self-employed reliefs
- kind: gov-error (classification: reading/convention: MF states that not all reliefs can be quantified).
- provisions: MF ČR, "Kvantifikace daňových úlev v České republice za rok 2023" (2025-11-14), Tabulka 1: 27 PIT
  reliefs (560,5 mld Kč), neither the výdaje paušálem (ZDP § 7 odst. 7) nor the paušální daň (§ 2a, § 7a).
- amounts (model, per household): the 60 % paušál on 1 M Kč of receipts with 10 % real costs saves 178 338 Kč (L02);
  the paušální daň on top 26 520–108 510 Kč (L03).
- status: confirmed (table read); no population estimate made.

### F13 § 35bb was reused for a different credit in 2024 (checked, clean)
- kind: statute-fault check (no error found). § 35bb was "Sleva za umístění dítěte" until 2023 and is "Sleva na
  manžela" from 2024 (zákon 349/2023 bod 71: "§ 35bb včetně nadpisu zní"); Global law search: no provision in force
  in 2025 cites § 35bb in the old sense. The monthly-bonus cap (5 025 Kč, § 35d odst. 4) was removed cleanly in 2021.
- status: checked, clean.

### F14 Dividends are outside the přídavek income test
- kind: loophole-known (statutory list) with an exploitation not found documented. households: couple, children 6
  and 11, the earner runs a one-person s.r.o. with profit 1 350 000 Kč paid out as dividends.
- amounts: the family receives the přídavek (35 280 Kč) with about 900 000 Kč of dividends after tax, while a
  700 000 Kč wage earner with the same family receives 0 (`runs/recreate.md`, L16: 23 280 Kč net of other effects).
- provisions: ZSSP § 5 odst. 1 písm. a) (only ZDP §§ 6, 7, 9, 10 income; § 8 capital income is not listed; MPSV
  úplný výčet příjmů confirms); the DSSP keeps the same list (zákon 151/2025 § 4 odst. 1 písm. a)).
- known? the list is official; its use through an s.r.o. was not found in the 6 sources searched.
- status: model-recreated.
