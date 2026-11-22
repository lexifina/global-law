import TaxKernel

/-!
# Luxembourg 2025: parameters, each with its source

Statute: loi modifiée du 4 décembre 1967 concernant l'impôt sur le revenu (L.I.R.), "Texte coordonné en vigueur au
1er janvier 2025" published by the Administration des contributions directes (ACD), actualised 02/02/2026
(`law/LIR_2025-01-01.txt`, from
https://impotsdirects.public.lu/dam-assets/fr/legislation/LIR/texte-coordonn-en-vigueur-au-1er-janvier-2025.pdf). The
2025 barème is art. 118 as amended by the loi du 20 décembre 2024 (Mémorial A 2024 n° 589,
`law/loi_2024-12-20_a589.txt`). Fonds pour l'emploi: loi modifiée du 30 juin 1976, art. 6 (legilux consolidation of
1 January 2024, `law/loi_1976-06-30_fonds_emploi_cons20240101.txt`). Social security: Code de la sécurité sociale
(CSS, legilux consolidation 1 January 2025, `law/css_20250101.txt`) and the CCSS table of social parameters
(https://ccss.lu/fr/parametres-sociaux/, `refs/ccss_parametres_sociaux.txt`). Social minimum wage: Code du travail
art. L. 222-9 (`law/code_travail_20250101.txt`).

Money in whole euros unless a name ends in `C` (cents). Rates in basis points (bp).
-/

namespace LuTax
open TaxKernel

/-- L.I.R. art. 118 (L. 20.12.24, Mémorial A 2024 n° 589): "0% pour la tranche de revenu inférieure à 13 230 euros;
8% ... entre 13 230 et 15 435 euros; ... 42% pour la tranche de revenu dépassant 234 870 euros" (23 bands). -/
def tarifBands : List (Int × Int) :=
  [(0, 0), (13230, 800), (15435, 900), (17640, 1000), (19845, 1100), (22050, 1200), (24255, 1400),
   (26550, 1600), (28845, 1800), (31140, 2000), (33435, 2200), (35730, 2400), (38025, 2600), (40320, 2800),
   (42615, 3000), (44910, 3200), (47205, 3400), (49500, 3600), (51795, 3800), (54090, 3900), (117450, 4000),
   (176160, 4100), (234870, 4200)]

/-- L.I.R. art. 120bis: class 1a: "revenu imposable ajusté réduit d'un quart de son complément à 79 380 euros". -/
def c1aComplement : Int := 79380
/-- L.I.R. art. 120bis: "le taux d'accroissement maximal ne puisse pas dépasser 39 pour cent pour la tranche de revenu
comprise entre 51 804 euros et 117 450 euros, 40 pour cent ... 117 450 ... 176 160 ..., 41 pour cent ... 234 870 euros
et 42 pour cent pour la tranche de revenu dépassant 234 870 euros". -/
def c1aCapFrom : Int := 51804

/-- L.I.R. art. 126 (2): "Avant l'application du tarif, le revenu imposable est arrondi au multiple inférieur de
50 euros." -/
def incomeStep : Int := 50
/-- L.I.R. art. 124 (2): "Les cotes d'impôt inférieures à 12 euros sont considérées comme nulles." -/
def minCote : Int := 12

/-- Loi modifiée du 30 juin 1976, art. 6, 1.: "l'impôt sur le revenu des personnes physiques est porté à 107% du
montant qui se dégage de l'application des dispositions des articles 118, 120, 120bis, 121 ..." -/
def feRate : Int := 700
/-- Same, art. 6, 1., second sentence: "Le même impôt est porté à 109% pour la tranche du revenu imposable ajusté
dépassant respectivement 150.000 € en classes 1 et 1a ou 300.00 € [sic] en classe 2." -/
def feRateHigh : Int := 900
def feThreshold12 : Int := 150000
def feThreshold2 : Int := 300000

/-- L.I.R. art. 107 (1) 1.: frais d'obtention "minimum forfaitaire ... 540 euros pour les revenus nets provenant d'une
occupation salariée"; 2.: "300 euros pour les revenus nets résultant de pensions ou de rentes"; 3.: "25 euros pour les
revenus nets provenant de capitaux mobiliers"; (4): "doublés lorsque des époux ... perçoivent chacun". -/
def foWage : Int := 540
def foPension : Int := 300
def foCapital : Int := 25

/-- L.I.R. art. 113 (1): "Il est déduit un minimum forfaitaire de 480 euros au titre des dépenses spéciales ..." -/
def dsForfait : Int := 480
/-- L.I.R. art. 111bis (7): prévoyance-vieillesse "Le montant annuel maximal déductible ... est fixé à 3.200 euros." -/
def prevoyanceCap : Int := 3200
/-- L.I.R. art. 109 (1) 3.: libéralités "dans la mesure où elles ne dépassent pas vingt pour-cent du total des revenus
nets, ni 1.000.000 euros". -/
def giftPct : Int := 2000
def giftCap : Int := 1000000

/-- L.I.R. art. 129b (1): "abattement extra-professionnel et fixé à 4.500 euros"; "2.250 euros" per spouse under
art. 3ter (2). -/
def abattExtraPro : Int := 4500
def abattExtraProIndiv : Int := 2250

/-- L.I.R. art. 115 n° 15a: "50% des revenus de capitaux" (dividends of fully taxable companies) exempt. -/
def divExemptPct : Int := 5000
/-- L.I.R. art. 115 n° 15: "la première tranche de 1.500 euros par an des revenus visés à l'article 97 et imposables par
voie d'assiette ... à majorer de son propre montant en cas d'imposition collective". -/
def capExempt : Int := 1500

/-- Loi modifiée du 23 décembre 2005 (retenue à la source libératoire, RELIBI), art. 6, 1., as amended by the loi du
23 décembre 2016 portant mise en oeuvre de la réforme fiscale 2017, art. 9, 1°: "les termes «10 pour cent» sont
remplacés par les termes «20 pour cent»" (`law/relibi_2005-12-23_jo.txt`, `law/loi_2016-12-23_reforme.txt`). -/
def relibiRate : Int := 2000

/-! ## Crédits d'impôt (L.I.R. art. 154quater, 154quinquies, 152ter, 154ter, 139quater; L. 20.12.24 n° 558, 589) -/

/-- Art. 154quater (2): CIS "de 936 euros à 11.265 euros ... [300 + (salaire brut - 936) x 0,029]"; "de 11.266 euros à
40.000 euros ... 600 euros"; "de 40.001 euros à 79.999 euros ... [600 - (salaire brut - 40.000) x 0,015]"; "A partir
d'un salaire brut de 80.000 euros ... ne sont pas accordés". Same figures for the CIP (art. 154quinquies, which adds
"de 300 à 935 euros, le CIP s'élève à 300 euros") and the CII (art. 152ter). -/
def cisLow : Int := 936
def cisKink : Int := 11265
def cisBase : Int := 300
def cisInRateM : Int := 29   -- per mille (0,029)
def cisFull : Int := 600
def cisStart : Int := 40000
def cisOutRateM10 : Int := 150  -- per ten-thousand (0,015)
def cisEnd : Int := 80000
/-- Art. 154quater (2): CI-CO2 salarié "de 936 euros à 40.000 euros ... 192 euros par an"; "de 40.001 euros à
79.999 euros ... [192 - (salaire brut - 40.000) x 0,0048]". -/
def co2Full : Int := 192
def co2OutRateM10 : Int := 48   -- per ten-thousand (0,0048)
/-- Art. 154ter (2) (L. 20.12.24 n° 589): CIM "inférieur à 60 000 euros ... 3 504 euros"; "entre 60 000 euros et 105 000
euros ... [3 504 – (revenu imposable ajusté – 60 000) x 0,0612]"; "supérieur à 105 000 euros ... 750 euros". -/
def cimFull : Int := 3504
def cimStart : Int := 60000
def cimRateM10 : Int := 612
def cimEnd : Int := 105000
def cimFloor : Int := 750
/-- Art. 139quater (3): CISSM "de 1 800 euros à 3 000 euros ... 81 euros par mois"; "de 3 000 à 3 600 euros ...
81 / 600 x [3 600 – salaire brut mensuel (fictif)]"; below 1 800 or from 3 600 "n'est pas accordé". -/
def cissmFull : Int := 81
def cissmLow : Int := 1800
def cissmKink : Int := 3000
def cissmEnd : Int := 3600

/-! ## Social security (employee side), 2025 -/

/-- CSS art. 238 (5): pension "taux de cotisation global est fixé à vingt-quatre pour cent", art. 239: "L'État supporte
un tiers", art. 240 1): the rest "par parts égales aux assurés et aux employeurs": 8 % employee. CCSS table: Pension 16
(employer + insured). -/
def pensionRate : Int := 800
/-- CSS art. 29 note 4): soins de santé "fixé à 5,60%"; art. 32: "par parts égales aux assurés et aux employeurs":
2,80 % employee. CCSS table "Maladie - soins de santé 5,60". -/
def healthRate : Int := 280
/-- CSS art. 29 al. 2: "le taux de cotisation est majoré de 0,5 pour cent" (prestations en espèces), half each: 0,25 %. -/
def cashRate : Int := 25
/-- CSS art. 376 (2): "Le taux de la contribution dépendance est fixé à 1,4 pour cent." -/
def depRate : Int := 140
/-- Self-employed: whole pension rate 16 % (CSS art. 240 3), health 5,60 % + 0,50 % (CSS art. 29); CCSS table. -/
def sePensionRate : Int := 1600
def seHealthRate : Int := 610

/-- CCSS "Nombre indice, salaire social minimum non-qualifié, minimum et maximum cotisable": 2025, échéance 01.01.2025:
indice 944,43, SSM 2.637,79, maximum cotisable 13.188,96; échéance 01.05.2025: indice 968,04, SSM 2.703,74, maximum
13.518,68 (monthly, cents). Code du travail art. L. 222-9: "279,30 euros au nombre 100 de l'indice"; CSS art. 241 (3)
"le quintuple des douze salaires sociaux minima mensuels". Jan-Apr = 4 months, May-Dec = 8 months. -/
def ssm1C : Int := 263779
def ssm2C : Int := 270374
def maxCot1C : Int := 1318896
def maxCot2C : Int := 1351868
def months1 : Int := 4
def months2 : Int := 8

/-! ## Allocations familiales (CSS art. 272, 275) -/

/-- CSS art. 272: "Le montant de l'allocation familiale est fixé à 31,75 euros par enfant et par mois ... majoré
mensuellement de 2,40 euros pour chaque enfant à partir du mois où il atteint l'âge de six ans et de 5,99 euros ...
à partir du mois où il atteint l'âge de douze ans"; amounts "au nombre cent de l'indice" (art. 272, al. 3), indexed
like civil servants' pay: index 944,43 (Jan-Apr 2025) and 968,04 (from 1 May 2025) (CCSS table). The CAE publishes
315,04 / +23,81 / +59,44 at index 992,24 (2026), which these formulas reproduce. -/
def afBaseC100 : Int := 3175
def afSupp6C100 : Int := 240
def afSupp12C100 : Int := 599
def index1 : Int := 94443   -- index × 100
def index2 : Int := 96804
/-- CSS art. 275 (1): "115 euros pour l'enfant âgé de plus de six ans; 235 euros pour l'enfant âgé de plus de douze
ans" (allocation de rentrée scolaire, paid in August; not indexed: CAE page). -/
def rentree6 : Int := 115
def rentree12 : Int := 235

end LuTax
