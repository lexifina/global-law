import TaxKernel

/-!
# Belgium, income year 2025 (exercice d'imposition / aanslagjaar 2026): parameters with their sources

Unit of account: **euro cents** (the assessment computes to the cent). Rates in basis points (bp) unless a statute
writes more decimals; then the denominator is written next to the rate (`pcm` = per 100 000, `ppm` = per 1 000 000).

Sources (copies in `cmp20/germanic/be/law` and `refs`):
* CIR 92 articles, dated versions: FisconetPlus (SPF Finances), "Article n, CIR 92 (historique)",
  `https://www.minfin.fgov.be/myminfin-rest/fisconetPlus/public/document/<guid>` (guids in `refs/cir92_hist_guids.json`).
  Justel's CIR 92 text is marked "LA MISE A JOUR DE CE TEXTE EST SUSPENDUE DEPUIS 2002", so Fisconet is the consolidation.
* Indexed amounts AI 2026: FisconetPlus "Indexation automatique - revenus 2025 - exercice d'imposition 2026"
  (guid 934106e5-36bd-4f61-8928-ba9ca100727f) = `law/fisconet_indexation_ai2026.txt` ("IDX" below).
* LSF (loi spéciale de financement 16.01.1989) art. 5/1, 5/2; AR 19.12.2017 (facteur d'autonomie); Brussels ordinance
  15.12.2014 art. 2 (as replaced by ord. 12.12.2016 art. 31): `law/lsf/`.
* Municipal rates: SPF Finances, `https://fin.belgium.be/sites/default/files/media/documents/taux-taxe-communale-2026.xlsx`.
* ONSS administrative instructions 2025/1-2025/4, "Le bonus à l'emploi" (socialsecurity.be): `refs/onss_workbonus_*.txt`.
* CSSS: loi du 30 mars 1994 portant des dispositions sociales, art. 106-108 (Justel cn 1994033031, updated to
  30-12-2025; art. 108 as replaced by L 28.03.2022 art. 3 and L 20.11.2022 art. 54): `law/l_19940330.u.html.txt`.
* Family allowances: Famiris barèmes "Applicable à partir du 01/01/2025" and "01/02/2025" (ordonnance 25.04.2019):
  `refs/famiris_2025-01-01.txt`, `refs/famiris_2025-02-01.txt`.
-/

namespace BETax
open TaxKernel

/-! ## Income tax (CIR 92, Titre II) -/

/-- Art. 130 (version from AI 2020, L 26.12.2015 art. 142/C): "25 % pour la tranche de revenus de 0,01 euros à
8.120,00 euros; 40 % ... à 14.330,00; 45 % ... à 24.800,00; 50 % pour la tranche supérieure"; indexed AI 2026 (IDX,
coeff. 2,2793): 16.320 / 28.800 / 49.840 (cents). -/
def art130 : Schedule := Schedule.ofList [(0, 2500), (1632000, 4000), (2880000, 4500), (4984000, 5000)]

/-- Art. 134 § 2 al. 2: "Cet impôt sur la quotité du revenu exemptée d'impôt est fixé à: 25 % ... 0,01 à 5.705 euros;
30 % ... 5.705 à 8.120; 40 % ... 8.120 à 13.530; 45 % ... 13.530 à 24.800; 50 % ... supérieure à 24.800" (montants de
base); IDX: 11.460 / 16.320 / 27.190 / 49.840. This is the pre-2017 art. 130 tariff, kept for the exempt sum only. -/
def art134 : Schedule :=
  Schedule.ofList [(0, 2500), (1146000, 3000), (1632000, 4000), (2719000, 4500), (4984000, 5000)]

/-- Art. 131 al. 1: "un montant de base de 4.785 euros (montant de base) est exempté d'impôt"; IDX: 10.910. -/
def exemptBase : Int := 1091000

/-- Art. 132 al. 1, 1°-5° (cumulative totals for 1, 2, 3, 4 children; per child beyond the 4th); IDX:
1.980 / 5.110 / 11.440 / 18.510; + 7.070. -/
def childTotals : List Int := [198000, 511000, 1144000, 1851000]
def childExtra : Int := 707000
/-- Art. 132 al. 1, 6°: "un montant supplémentaire de 325 euros (montant de base) pour chaque enfant n'ayant pas atteint
l'âge de 3 ans au 1er janvier de l'exercice d'imposition" (if no childcare deduction); IDX 740. -/
def under3Supp : Int := 74000
/-- Art. 133 al. 1, 1°: "870 euros (montant de base) pour un contribuable imposé isolément et qui a un ou plusieurs
enfants à charge"; IDX 1.980. -/
def singleParentSupp : Int := 198000
/-- Art. 133 al. 2-3 (version AI 2022, L 27.06.2021 art. 32): additional supplement when "le revenu imposable du
contribuable est inférieur à 10.700 euros" and "les revenus professionnels nets ... au moins égaux à 1.800 euros";
565 euros up to 8.445, then reduced linearly; IDX: limit 24.390, full 1.290 up to 19.250, net professional income
4.100, difference 5.140. -/
def spExtraFull : Int := 129000
def spExtraFrom : Int := 1925000
def spExtraTo : Int := 2439000
def spExtraMinProf : Int := 410000
/-- Art. 134 § 3 al. 2: refundable credit "ne peut pas excéder 550 euros (montant de base) par enfant à charge";
not indexed: art. 178 § 5, 3°/1 (L 18.12.2025) excludes "les montants visés aux articles 134, § 3, alinéa 2"
(IDX: "remplacé par le montant non-indexé de 550 euros"). -/
def childCreditCap : Int := 55000

/-- Art. 51 al. 2, 1°: "pour les rémunérations des travailleurs: 30 %"; al. 3: "ne peut, en aucun cas, dépasser
2.950 euros (montant de base)"; IDX: 5.930. Same for "bénéfices" (al. 2, 5°). -/
def forfaitRate : Int := 3000
def forfaitCap : Int := 593000

/-- Art. 87-88 (quotient conjugal, versions in force for AI 2026): "Cette quote-part est égale à 30 % de ces revenus
sans pouvoir excéder 6.700 euros (montant de base)"; IDX: 13.460. -/
def quotientPct : Int := 3000
def quotientCap : Int := 1346000

/-- Art. 289ter/1 (version AI 2026, Lprog 22.12.2023 art. 19, 3°): credit = "33,14 % du montant du volet A" and
"52,54 % du montant du volet B" of the social work bonus actually granted; "ne peut excéder ... 765 euros (montant
de base)"; IDX 1.540. Rates in pcm (per 100 000). -/
def wbFiscalA : Int := 33140
def wbFiscalB : Int := 52540
def wbFiscalCap : Int := 154000

/-- Art. 21, 14° + AR/CIR 92 art. 2ter: exempt dividends, IDX "860 après gel: 833" (per taxpayer, via the return). -/
def dividendExempt : Int := 83300
/-- Art. 171, 3° (dividends, interest): separate taxation at 30 % (the précompte mobilier is liberatory). -/
def movableRate : Int := 3000

/-! ## Regional and municipal -/

/-- LSF art. 5/2 § 1: "L'impôt Etat réduit est l'impôt Etat diminué d'un montant égal à l'impôt Etat multiplié par le
facteur d'autonomie"; AR 19.12.2017 art. 1: facteur d'autonomie "déterminé à 24,957 %" (pcm). -/
def autonomyPcm : Int := 24957
/-- Brussels ordinance 15.12.2014 art. 2 § 1 (ord. 12.12.2016): centimes = "[100/(100 – f)] × [99,5 – (100 – f)]",
"arrondi au millième supérieur": with f = 24,957 this is 32,591 (pcm), see `Theorems.bxl_centimes_formula`. -/
def brusselsCentimesPcm : Int := 32591
/-- City of Brussels additional municipal tax (CIR 92 art. 465-466), AI 2026: 4,9 % (SPF Finances list
`taux-taxe-communale-2026.xlsx`, row "Bruxelles"; AI 2025 list: 6). bp. -/
def cityOfBrusselsBp : Int := 490
/-- Municipal rate the OECD's Taxing Wages 2025 lines imply for Belgium (SLT − regional) / (federal + regional):
6,0 % for all eight household types (see `results/oecd_check.md`). bp. -/
def oecdMunicipalBp : Int := 600

/-! ## Social contributions -/

/-- Employee contribution 13,07 % (ONSS instructions 2025: "travailleurs ... redevables d'une cotisation personnelle de
13,07 %"; loi 29.06.1981 art. 38 § 2). Employees (white collar) on 100 % of the wage. -/
def onssBp : Int := 1307

/-- Bonus à l'emploi social (loi 20.12.1999 art. 2; ONSS instructions 2025/1-4, employés): monthly reference wage S.
Volet A: R = maxA if S ≤ thrA; maxA − coefA·(S − thrA) up to endA; 0 above. Volet B: maxB if S ≤ thrB;
maxB − coefB·(S − thrB) up to thrA. Coefficients per 10 000. -/
structure WorkBonus where
  thrA : Int
  maxA : Int
  coefA : Int
  endA : Int
  thrB : Int
  maxB : Int
  coefB : Int
  deriving Repr

/-- "Tranches et montants d'application applicables en janvier 2025": A ≤ 2.723,36: 118,22; 118,22 − 0,2442 × (S −
2.723,36) up to 3.207,40; B ≤ 2.132,59: 159,43; 159,43 − 0,2699 × (S − 2.132,59) up to 2.723,36. -/
def wbJan : WorkBonus := { thrA := 272336, maxA := 11822, coefA := 2442, endA := 320740,
                           thrB := 213259, maxB := 15943, coefB := 2699 }
/-- "Tranches et montants d'application à partir du 1er février 2025": A ≤ 2.777,83: 120,59; − 0,2443 × (S − 2.777,83)
up to 3.271,48; B ≤ 2.175,25: 162,62; − 0,2699 × (S − 2.175,25) up to 2.777,83. -/
def wbFeb : WorkBonus := { thrA := 277783, maxA := 12059, coefA := 2443, endA := 327148,
                           thrB := 217525, maxB := 16262, coefB := 2699 }

/-- CSSS, loi 30.03.1994 art. 108 § 1 al. 2 (individual taxation): "18 592,02 à 21 070,96: 5 p.c.";
"21 070,97 à 37 344,00: 123,95 euros augmentés de 1,3 p.c."; "37 344,01 à 40 997,26: 335,50 euros augmentés de 4,0090
p.c."; "40 997,27 à 60 181,95: 481,96 euros augmentés de 1,2996 p.c."; "supérieur à 60 181,95: 731,28 euros".
Rates in ppm. -/
def csssIndividual (r : Int) : Int :=
  let hu := fun (n : Int) => divR .halfUp n 1000000
  if r ≤ 1859202 then 0
  else if r ≤ 2107096 then hu (50000 * (r - 1859202))
  else if r ≤ 3734400 then 12395 + hu (13000 * (r - 2107096))
  else if r ≤ 4099726 then 33550 + hu (40090 * (r - 3734400))
  else if r ≤ 6018195 then 48196 + hu (12996 * (r - 4099726))
  else 73128

/-- CSSS art. 108 § 1 al. 3 (imposition commune): 5 p.c. from 18 592,02; "21 070,97 à 60 181,95: 123,95 euros
augmentés de 1,3 p.c."; "60 181,96 à 74 688,00: 632,39 euros"; "74 688,01 à 81 944,00: 632.39 euros augmentés de 1,3629
p.c."; "supérieur à 81 944,00: 731,28 euros". -/
def csssJoint (r : Int) : Int :=
  let hu := fun (n : Int) => divR .halfUp n 1000000
  if r ≤ 1859202 then 0
  else if r ≤ 2107096 then hu (50000 * (r - 1859202))
  else if r ≤ 6018195 then 12395 + hu (13000 * (r - 2107096))
  else if r ≤ 7468800 then 63239
  else if r ≤ 8194400 then 63239 + hu (13629 * (r - 7468800))
  else 73128

/-! ## Brussels family allowances (Famiris, ordonnance 25.04.2019) -/

/-- One month's barème. -/
structure FamBareme where
  base011 : Int        -- art. 7: 0 à 11 ans (born from 01/12/2019)
  base1217 : Int       -- 12 à 17 ans, 18-24 "autre situation"
  deduct : Int         -- art. 35: born before 01/12/2019 "diminués d'un montant fixe"
  plafond1 : Int       -- art. 9 premier plafond
  plafond2 : Int       -- deuxième plafond
  soc1 : Int × Int     -- 3.2 family of 1 child: (0-11, 12-24)
  soc2mono : Int × Int
  soc2 : Int × Int
  soc3mono : Int × Int
  soc3 : Int × Int
  mid2 : Int           -- 3.3 between the ceilings, family of 2
  mid3 : Int           -- 3.3 family of 3+
  old : List Int       -- LGAF transitional: 1st, 2nd, 3rd+ child
  oldMono : List Int   -- monoparental supplements 1st, 2nd, 3rd+
  ageFirst : List Int  -- LGAF age supplements, first child without supplements: 6-11, 12-17, 18-24
  ageOther : List Int  -- other children: 6-11, 12-17, 18-24
  deriving Repr

/-- Famiris barème "Applicable à partir du 01/01/2025" (indice-pivot 128,11). -/
def famJan : FamBareme :=
  { base011 := 18285, base1217 := 19504, deduct := 1219, plafond1 := 3901196, plafond2 := 5663027,
    soc1 := (4876, 6095), soc2mono := (9752, 10971), soc2 := (8533, 9752), soc3mono := (15847, 17066),
    soc3 := (13409, 14628), mid2 := 3048, mid3 := 8777, old := [11679, 21609, 32264],
    oldMono := [5945, 3685, 2972], ageFirst := [2035, 3098, 3571], ageOther := [4057, 6199, 7882] }

/-- Famiris barème "Applicable à partir du 01/02/2025" (indice-pivot 130,67). -/
def famFeb : FamBareme :=
  { base011 := 18651, base1217 := 19894, deduct := 1243, plafond1 := 3979284, plafond2 := 5776380,
    soc1 := (4974, 6217), soc2mono := (9947, 11191), soc2 := (8704, 9947), soc3mono := (16164, 17408),
    soc3 := (13677, 14921), mid2 := 3109, mid3 := 8952, old := [11912, 22041, 32908],
    oldMono := [6064, 3759, 3031], ageFirst := [2075, 3160, 3642], ageOther := [4138, 6323, 8040] }

/-- Art. 15 "supplément d'âge annuel", paid with July (barème 01/02/2025): 0-5: 24,87; 6-11: 37,30; 12-24 (no higher
education): 62,17. -/
def julyAgeSupp (age : Nat) : Int :=
  if age ≤ 5 then 2487 else if age ≤ 11 then 3730 else if age ≤ 24 then 6217 else 0

end BETax
