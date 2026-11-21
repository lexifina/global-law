import BETax.Params

/-!
# Belgium: income years 2022, 2023 and 2024 (exercices d'imposition 2023, 2024, 2025) next to 2025

Added in improvement round 5 (2026-11-19). The 2025 record `p2025` is built from the definitions in `Params.lean`
unchanged, so every 2025 result is the same as before. Sources of the earlier years (copies in
`~/cmp20/improve-central/refs/be/`):

* **IDX AI 2023 / AI 2024 / AI 2025**: SPF Finances, "Avis relatif à l'indexation automatique en matière d'impôts sur
  les revenus", FisconetPlus guids 8e3f32e5-3d4c-4fca-9843-5234016d0e1f (revenus 2022, coefficient art. 178 §§ 1-2:
  1,9379; § 3 al. 1, 2°: 1,7085), 748975ad-ce7a-4873-a552-1e6a2a199eda (revenus 2023: 2,1238; 1,8724),
  15618a3b-1ef1-4baa-a454-bdc34e1c5586 (revenus 2024: 2,2099; 1,9484): `indexation_ai2023.txt`, `indexation_ai2024.txt`,
  `fisconet_indexation_ai2025.txt`. Each table row is "montant de base | montant indexé".
* **Art. 289ter/1 CIR 92** (fiscal work bonus), dated versions in `~/cmp20/germanic/be/law/cir92/fisconet_art289ter_1.txt`:
  AI 2023: "33,14 % de la réduction ... ne peut excéder ... 540 euros (montant de base)" (L 21.12.2022 art. 31, applicable
  from AI 2023; it replaced L 05.07.2022's 530 and L 12.12.2021's 515); AI 2024: 33,14 %, 550 euros (L 31.07.2023
  art. 32, 2°); AI 2025: 710 euros (Lprog 22.12.2023 art. 19, 2°), and for reductions granted from 01.04.2024 "33,14 %
  du montant du volet A" and "52,54 % du montant du volet B" (art. 19, 1°). Indexed with the art. 178 § 3 al. 1, 2°
  coefficient, "arrondis au multiple de 10 euros" (art. 178 § 3): 540 × 1,7085 = 922,59 -> 920; 550 × 1,8724 =
  1.029,82 -> 1.030; 710 × 1,9484 = 1.383,36 -> 1.380 (= IDX AI 2025). The IDX tables of AI 2023 and AI 2024 still
  print 515 -> 880 and 540 -> 1.010: they predate the later laws (weak point of those two tables, noted in the log).
* **Social work bonus** (loi 20.12.1999 art. 2): ONSS administrative instructions 2022/1-2024/4, "Bonus à l'emploi",
  `onss/workbonus_<quarter>.txt` (https://www.socialsecurity.be/employer/instructions/dmfa/fr/<quarter>/instructions/
  deductions/workers_reductions/workbonus.html), employees (100 %): the tables "applicables à partir du" 1.1.2022,
  1.3.2022, 1.4.2022, 1.5.2022, 1.8.2022, 1.11.2022, 1.12.2022, 1.7.2023, 1.11.2023, "pour avril 2024" and 1.5.2024.
* **CSSS** (loi 30.03.1994 art. 108): the scale in `Params.lean` applies to all four years: L 28.03.2022 art. 5 ("L'article
  3 est applicable aux cotisations spéciales dues sur les revenus recueillis à partir du 1er janvier 2022", copy
  `L_2022-03-28.u.txt`) and L 20.11.2022 art. 54 (threshold 40 997,26, "En vigueur : 01-01-2022"); no later change of
  art. 108 before L 15.07.2026 (Justel modification list).
* **Famiris** barèmes (ordonnance 25.04.2019), `famiris/<date>.txt` from https://famiris.brussels/wp-content/uploads/...:
  in force from 1.1.2022, 1.3.2022, 1.5.2022, 1.8.2022, 1.11.2022, 1.12.2022, 1.1.2023, 1.7.2023, 1.11.2023, 1.5.2024
  (parsed by `famiris/parse_famiris.py`; the parser reproduces the 2025 barèmes already in `Params.lean` exactly).
* **Municipal tax**, City of Brussels: 6 % for AI 2024 and AI 2025 (SPF Finances `taux-taxe-communale-2024.xlsx`,
  `-2025.xlsx`, row "Bruxelles"). AI 2023: the list was not reachable (fin.belgium.be no longer serves it); 6 % is
  carried back from AI 2024 and the output says so (weak).
* Unchanged in all four years: ONSS 13,07 %, art. 51 rate 30 %, art. 87-88 30 %, the LSF autonomy factor 24,957 % and
  the Brussels centimes 32,591 %, art. 131-134 structure (dated versions in `law/cir92/`).
-/

namespace BETax
open TaxKernel

/-- A pre-April-2024 work-bonus table (one reduction, no volets): R = max up to `thr`; max − coef1·(S − thr) up to
`mid`; max2 − coef2·(S − thr) up to `stop`; 0 above (tables from 1.7.2023 have the two linear pieces; earlier ones
have one: mid = stop, max2 = max, coef2 = coef1). Coefficients per 10 000. -/
structure WbOld where
  thr : Int
  max : Int
  coef1 : Int
  mid : Int
  max2 : Int
  coef2 : Int
  stop : Int
  deriving Repr

/-- One month's work-bonus rules. -/
inductive WbSpec where
  | old (w : WbOld)
  | ab (w : WorkBonus)
  deriving Repr

def oneLine (thr max coef stop : Int) : WbOld :=
  { thr, max, coef1 := coef, mid := stop, max2 := max, coef2 := coef, stop }

/-- "à partir du 1er janvier 2022": ≤ 1.742,14: 213,96; 213,96 − (0,2194 × (S − 1.742,14)) up to 2.717,30. -/
def wb2201 : WbOld := oneLine 174214 21396 2194 271730
/-- "à partir du 1er mars 2022": 218,24; 0,2194; 1.776,97 to 2.771,79. -/
def wb2203 : WbOld := oneLine 177697 21824 2194 277179
/-- "à partir du 1er avril 2022": 228,48; 0,2313; 1.860,34 to 2.847,98. -/
def wb2204 : WbOld := oneLine 186034 22848 2313 284798
/-- "à partir du 1er mai 2022": 233,05; 0,2313; 1.897,55 to 2.904,93. -/
def wb2205 : WbOld := oneLine 189755 23305 2313 290493
/-- "à partir du 1er août 2022": 237,71; 0,2313; 1.935,50 to 2.963,04. -/
def wb2208 : WbOld := oneLine 193550 23771 2313 296304
/-- "à partir du 1er novembre 2022": 242,46; 0,2313; 1.974,20 to 3.022,28. -/
def wb2211 : WbOld := oneLine 197420 24246 2313 302228
/-- "à partir du 1er décembre 2022" (also January-June 2023, instructions 2023/1-2023/2): 247,31; 0,2313;
2.013,64 to 3.082,66. -/
def wb2212 : WbOld := oneLine 201364 24731 2313 308266
/-- "à partir du 1er juillet 2023 au 31 octobre 2023": ≤ 2.013,64: 262,16; to 2.571,45: 262,16 − (0,2579 × (S −
2.013,64)); to 3.082,66: 247,31 − (0,2313 × (S − 2.013,64)). -/
def wb2307 : WbOld := { thr := 201364, max := 26216, coef1 := 2579, mid := 257145, max2 := 24731, coef2 := 2313,
                        stop := 308266 }
/-- "à partir du 1er novembre 2023" (also January-March 2024, instructions 2024/1): ≤ 2.054,01: 267,42; to 2.623,00:
267,42 − 0,2579 × (S − 2.054,01); to 3.144,45: 252,26 − 0,2313 × (S − 2.054,01). -/
def wb2311 : WbOld := { thr := 205401, max := 26742, coef1 := 2579, mid := 262300, max2 := 25226, coef2 := 2313,
                        stop := 314445 }
/-- "pour avril 2024": volet A ≤ 2.669,96: 115,91; − 0,2443 × (S − 2.669,96) up to 3.144,45; volet B ≤ 2.090,78:
156,30; − 0,2699 × (S − 2.090,78) up to 2.669,96. -/
def wb2404 : WorkBonus := { thrA := 266996, maxA := 11591, coefA := 2443, endA := 314445,
                            thrB := 209078, maxB := 15630, coefB := 2699 }
/-- "à partir du 1er mai 2024" (instructions 2024/2-2024/4): the table `wbJan` (the same table applies in January
2025). -/
theorem wb2405_eq_wbJan : wbJan = { thrA := 272336, maxA := 11822, coefA := 2442, endA := 320740,
                                    thrB := 213259, maxB := 15943, coefB := 2699 } := rfl

/-! ## Famiris barèmes 2022-2024 (cents; fields as `FamBareme`) -/

def fam2201 : FamBareme :=
  { base011 := 15918, base1217 := 16979, deduct := 1061, plafond1 := 3325940, plafond2 := 4827977,
    soc1 := (4245, 5306), soc2mono := (8490, 9551), soc2 := (7428, 8490), soc3mono := (13796, 14857),
    soc3 := (11673, 12734), mid2 := 2653, mid3 := 7641, old := [10167, 18811, 28086],
    oldMono := [5175, 3208, 2587], ageFirst := [1771, 2697, 3109], ageOther := [3532, 5397, 6862] }
def fam2203 : FamBareme :=
  { base011 := 16236, base1217 := 17318, deduct := 1082, plafond1 := 3392383, plafond2 := 4924428,
    soc1 := (4330, 5412), soc2mono := (8659, 9742), soc2 := (7577, 8659), soc3mono := (14071, 15154),
    soc3 := (11906, 12989), mid2 := 2706, mid3 := 7793, old := [10370, 19189, 28650],
    oldMono := [5279, 3272, 2639], ageFirst := [1807, 2751, 3171], ageOther := [3603, 5505, 7000] }
def fam2205 : FamBareme :=
  { base011 := 16562, base1217 := 17666, deduct := 1104, plafond1 := 3460394, plafond2 := 5023153,
    soc1 := (4416, 5521), soc2mono := (8833, 9937), soc2 := (7729, 8833), soc3mono := (14353, 15457),
    soc3 := (12145, 13249), mid2 := 2760, mid3 := 7950, old := [10578, 19572, 29222],
    oldMono := [5385, 3338, 2692], ageFirst := [1843, 2806, 3234], ageOther := [3675, 5615, 7139] }
def fam2208 : FamBareme :=
  { base011 := 16893, base1217 := 18019, deduct := 1126, plafond1 := 3529658, plafond2 := 5123698,
    soc1 := (4505, 5631), soc2mono := (9010, 10136), soc2 := (7883, 9010), soc3mono := (14641, 15767),
    soc3 := (12388, 13514), mid2 := 2816, mid3 := 8109, old := [10789, 19964, 29807],
    oldMono := [5492, 3405, 2745], ageFirst := [1880, 2862, 3299], ageOther := [3748, 5727, 7282] }
def fam2211 : FamBareme :=
  { base011 := 17231, base1217 := 18379, deduct := 1149, plafond1 := 3600176, plafond2 := 5226062,
    soc1 := (4595, 5744), soc2mono := (9190, 10338), soc2 := (8041, 9190), soc3mono := (14933, 16082),
    soc3 := (12636, 13784), mid2 := 2872, mid3 := 8271, old := [11005, 20362, 30402],
    oldMono := [5602, 3473, 2800], ageFirst := [1917, 2919, 3365], ageOther := [3823, 5842, 7428] }
def fam2212 : FamBareme :=
  { base011 := 17576, base1217 := 18747, deduct := 1172, plafond1 := 3672261, plafond2 := 5330702,
    soc1 := (4687, 5859), soc2mono := (9374, 10545), soc2 := (8202, 9374), soc3mono := (15232, 16404),
    soc3 := (12889, 14060), mid2 := 2929, mid3 := 8436, old := [11225, 20770, 31011],
    oldMono := [5714, 3542, 2856], ageFirst := [1956, 2978, 3432], ageOther := [3900, 5959, 7576] }
/-- 1.1.2023 (and 1.7.2023: same amounts and ceilings): the 1.12.2022 amounts with the 2023 ceilings. -/
def fam2301 : FamBareme := { fam2212 with plafond1 := 3712655, plafond2 := 5389339 }
def fam2311 : FamBareme :=
  { base011 := 17927, base1217 := 19122, deduct := 1195, plafond1 := 3786801, plafond2 := 5496969,
    soc1 := (4780, 5976), soc2mono := (9561, 10756), soc2 := (8366, 9561), soc3mono := (15536, 16731),
    soc3 := (13146, 14341), mid2 := 2988, mid3 := 8605, old := [11449, 21185, 31631],
    oldMono := [5828, 3613, 2913], ageFirst := [1995, 3037, 3501], ageOther := [3978, 6078, 7728] }
/-- 1.5.2024: the January-2025 amounts (`famJan`) with the 2024 ceilings 38.625,31 / 56.068,99. -/
def fam2405 : FamBareme := { famJan with plafond1 := 3862531, plafond2 := 5606899 }

/-! ## The year record -/

structure YearP where
  year : Nat
  art130 : Schedule
  art134 : Schedule
  exemptBase : Int
  childTotals : List Int
  childExtra : Int
  under3Supp : Int
  singleParentSupp : Int
  spExtraFull : Int
  spExtraFrom : Int
  spExtraTo : Int
  spExtraMinProf : Int
  childCreditCap : Int
  forfaitCap : Int
  quotientCap : Int
  wbFiscalCap : Int
  dividendExempt : Int
  communeBp : Int
  /-- the twelve months' work-bonus tables, January first -/
  wbMonths : List WbSpec
  /-- the twelve months' Famiris barèmes, January first -/
  famMonths : List FamBareme
  /-- art. 15 July age supplement: 0-5, 6-11, 12-24 (no higher education), from the barème in force in July -/
  julyAmts : List Int
  /-- the July amounts of the barème in force on 1 January (for `--jan-table`) -/
  julyAmtsJan : List Int
  /-- CONVENTION (`--oecd` only, not statute): the municipal rate implied by the OECD's Taxing Wages SLT lines for this
  year, (SLT − regional) / (federal reduced + regional): 6,00 % for 2024 and 2025, 6,30 % for 2022 and 2023 (computed
  on the dev country tables, improve-central round 5; derived from the referee's own lines, so a consistency check,
  not evidence). The statute rate is `communeBp` (City of Brussels). -/
  oecdCommuneBp : Int
  deriving Repr

/-- Income year 2025 (AI 2026): the `Params.lean` values. -/
def p2025 : YearP :=
  { year := 2025, art130, art134, exemptBase, childTotals, childExtra, under3Supp, singleParentSupp, spExtraFull,
    spExtraFrom, spExtraTo, spExtraMinProf, childCreditCap, forfaitCap, quotientCap, wbFiscalCap, dividendExempt,
    communeBp := cityOfBrusselsBp,
    wbMonths := WbSpec.ab wbJan :: List.replicate 11 (WbSpec.ab wbFeb),
    famMonths := famJan :: List.replicate 11 famFeb, julyAmts := [2487, 3730, 6217],
    julyAmtsJan := [2438, 3657, 6095], oecdCommuneBp := oecdMunicipalBp }

/-- Income year 2024 (AI 2025). IDX AI 2025 (coefficient 2,2099; § 3: 1,9484): art. 130 tranches 15.820 / 27.920 /
48.320; art. 134 § 2: 11.120 / 15.820 / 26.360 / 48.320; art. 131 al. 1: 10.570; art. 132 al. 1, 1°-5°: 1.920 /
4.950 / 11.090 / 17.940, + 6.850; 6°: 720; art. 133 al. 1, 1°: 1.920; al. 2-3: limit 23.650, net professional
income 3.980, supplement 1.250 up to 18.660; art. 134 § 3 al. 2: 550 per child; art. 51 al. 3: 5.750; art. 87-88:
13.050; art. 289ter/1: 1.380; art. 21, 14°: 833. -/
def p2024 : YearP :=
  { year := 2024,
    art130 := Schedule.ofList [(0, 2500), (1582000, 4000), (2792000, 4500), (4832000, 5000)],
    art134 := Schedule.ofList [(0, 2500), (1112000, 3000), (1582000, 4000), (2636000, 4500), (4832000, 5000)],
    exemptBase := 1057000, childTotals := [192000, 495000, 1109000, 1794000], childExtra := 685000,
    under3Supp := 72000, singleParentSupp := 192000, spExtraFull := 125000, spExtraFrom := 1866000,
    spExtraTo := 2365000, spExtraMinProf := 398000, childCreditCap := 55000, forfaitCap := 575000,
    quotientCap := 1305000, wbFiscalCap := 138000, dividendExempt := 83300, communeBp := 600,
    wbMonths := List.replicate 3 (WbSpec.old wb2311) ++ [WbSpec.ab wb2404] ++ List.replicate 8 (WbSpec.ab wbJan),
    famMonths := List.replicate 4 fam2311 ++ List.replicate 8 fam2405, julyAmts := [2438, 3657, 6095],
    julyAmtsJan := [2390, 3585, 5976], oecdCommuneBp := 600 }

/-- Income year 2023 (AI 2024). IDX AI 2024 (2,1238; § 3: 1,8724): art. 130: 15.200 / 26.830 / 46.440; art. 134 § 2:
10.680 / 15.200 / 25.330 / 46.440; art. 131: 10.160; art. 132: 1.850 / 4.760 / 10.660 / 17.250, + 6.580; 6°: 690;
art. 133 al. 1, 1°: 1.850; al. 2-3: 22.720, 3.820, 1.200 up to 17.940; art. 134 § 3: 530; art. 51: 5.520;
art. 87-88: 12.550; art. 21, 14°: 800. Art. 289ter/1: 550 × 1,8724 -> 1.030. -/
def p2023 : YearP :=
  { year := 2023,
    art130 := Schedule.ofList [(0, 2500), (1520000, 4000), (2683000, 4500), (4644000, 5000)],
    art134 := Schedule.ofList [(0, 2500), (1068000, 3000), (1520000, 4000), (2533000, 4500), (4644000, 5000)],
    exemptBase := 1016000, childTotals := [185000, 476000, 1066000, 1725000], childExtra := 658000,
    under3Supp := 69000, singleParentSupp := 185000, spExtraFull := 120000, spExtraFrom := 1794000,
    spExtraTo := 2272000, spExtraMinProf := 382000, childCreditCap := 53000, forfaitCap := 552000,
    quotientCap := 1255000, wbFiscalCap := 103000, dividendExempt := 80000, communeBp := 600,
    wbMonths := List.replicate 6 (WbSpec.old wb2212) ++ List.replicate 4 (WbSpec.old wb2307) ++
      List.replicate 2 (WbSpec.old wb2311),
    famMonths := List.replicate 10 fam2301 ++ List.replicate 2 fam2311, julyAmts := [2343, 3515, 5859],
    julyAmtsJan := [2343, 3515, 5859], oecdCommuneBp := 630 }

/-- Income year 2022 (AI 2023). IDX AI 2023 (1,9379; § 3: 1,7085): art. 130: 13.870 / 24.480 / 42.370; art. 134 § 2:
9.750 / 13.870 / 23.120 / 42.370; art. 131: 9.270; art. 132: 1.690 / 4.340 / 9.730 / 15.740, + 6.010; 6°: 630;
art. 133 al. 1, 1°: 1.690; al. 2-3: 20.740, 3.490, 1.090 up to 16.370; art. 134 § 3: 480; art. 51: 5.040;
art. 87-88: 11.450; art. 21, 14°: 800. Art. 289ter/1: 540 × 1,7085 -> 920. -/
def p2022 : YearP :=
  { year := 2022,
    art130 := Schedule.ofList [(0, 2500), (1387000, 4000), (2448000, 4500), (4237000, 5000)],
    art134 := Schedule.ofList [(0, 2500), (975000, 3000), (1387000, 4000), (2312000, 4500), (4237000, 5000)],
    exemptBase := 927000, childTotals := [169000, 434000, 973000, 1574000], childExtra := 601000,
    under3Supp := 63000, singleParentSupp := 169000, spExtraFull := 109000, spExtraFrom := 1637000,
    spExtraTo := 2074000, spExtraMinProf := 349000, childCreditCap := 48000, forfaitCap := 504000,
    quotientCap := 1145000, wbFiscalCap := 92000, dividendExempt := 80000, communeBp := 600,
    wbMonths := [WbSpec.old wb2201, WbSpec.old wb2201, WbSpec.old wb2203, WbSpec.old wb2204] ++
      List.replicate 3 (WbSpec.old wb2205) ++ List.replicate 3 (WbSpec.old wb2208) ++
      [WbSpec.old wb2211, WbSpec.old wb2212],
    famMonths := [fam2201, fam2201, fam2203, fam2203, fam2205, fam2205, fam2205, fam2208, fam2208, fam2208,
      fam2211, fam2212],
    julyAmts := [2208, 3312, 5521], julyAmtsJan := [2122, 3184, 5306], oecdCommuneBp := 630 }

/-- CONVENTION (`--jan-table`, not statute): the rules in force on 1 January applied to the whole year (work-bonus
table, Famiris barème and its July amounts), as OECD TaxBEN does with its 1 January policy date. -/
def YearP.janOnly (P : YearP) : YearP :=
  { P with wbMonths := List.replicate 12 (P.wbMonths.headD (WbSpec.ab wbJan)),
           famMonths := List.replicate 12 (P.famMonths.headD famJan), julyAmts := P.julyAmtsJan }

/-- `--eurostat` (Eurostat earn_net ESMS 3.4, sha256 89ab2734..., `tests/data/_methodology/earn_net_esms.htm`: "Income
tax and social security contributions parameters refer to the beginning of the fiscal year, i.e. changes occurring
later during the year are ignored"): the ONSS work-bonus table of January for all twelve months. Tax parameters are
annual already; family-allowance timing is not a tax/SSC parameter and stays as in the statute. Convention only. -/
def YearP.startOfYear (P : YearP) : YearP :=
  { P with wbMonths := List.replicate 12 (P.wbMonths.headD (WbSpec.ab wbJan)) }

/-- `--euromod` (EUROMOD J2.0+ convention, never statute mode; round 15): EUROMOD's reference date for legislative
parameters is 30 June of the policy year ("Nowcasting prices" note, Feb 2025, section 1.3 table "Reference date
parameters: End June y" and section 1.4 "Legislative parameters of the tax system are referred in EM to 30 June";
`software/euromod/model/Documentation/Nowcasting prices_note_Feb2025.pdf`). The EUROMOD Country Report Belgium
2022-2025 states no other treatment for these two policies (its 2.2.1 says only that benefits rise "every time
price-indices reach a certain level" and tax amounts are indexed "at the transition to the next fiscal year"). So the
ONSS work-bonus table and the Famiris barème in force on 30 June (month 6) apply to all twelve months; tax parameters
are annual already. Check against the CR: Table 2.43 prints 233,05 / 1.897,55 (2022) and 247,31 / 2.013,64 (2023),
the June tables `wb2205` and `wb2212`; Table 2.44 prints 120,59 / 2.777,83 for 2025 (`wbFeb`, June 2025), but
115,91 / 2.669,96 for 2024, the April-2024 table `wb2404`, while the June 2024 table is the May one (118,22 /
2.723,36, `wbJan`). The 30-June rule, not the 2024 column of Table 2.44, is applied (the table states amounts, not a
treatment); the 2024 mismatch is recorded in improve-central/round15/belu.md. The July school premium (`julyAmts`) is
already the June/July barème's in every year. -/
def YearP.atJune (P : YearP) : YearP :=
  { P with wbMonths := List.replicate 12 (P.wbMonths.getD 5 (WbSpec.ab wbJan)),
           famMonths := List.replicate 12 (P.famMonths.getD 5 famJan) }

/-- The record for income year `y`: 2022-2025; other years are computed with the nearest one (the output says so). -/
def yearP (y : Nat) : YearP :=
  if y ≤ 2022 then p2022 else if y = 2023 then p2023 else if y = 2024 then p2024 else p2025

def supportedYear (y : Nat) : Bool := 2022 ≤ y && y ≤ 2025

theorem months_twelve :
    p2022.wbMonths.length = 12 ∧ p2023.wbMonths.length = 12 ∧ p2024.wbMonths.length = 12 ∧
    p2025.wbMonths.length = 12 ∧ p2022.famMonths.length = 12 ∧ p2023.famMonths.length = 12 ∧
    p2024.famMonths.length = 12 ∧ p2025.famMonths.length = 12 := by decide

end BETax
