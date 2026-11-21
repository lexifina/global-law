import TaxKernel.World

/-!
# Senegal 2025: parameters, each with its dated source (whole francs CFA)

Source: Code général des impôts (Loi n° 2012-31 du 31 décembre 2012), "CGI annoté, mis à jour janvier 2025",
published by the Direction générale des Impôts et des Domaines (DGID), https://www.dgid.sn/storage/docs/CGI-2025.pdf
(fetched 2026-11-20, copy and text in `../src/CGI-2025.pdf`, `CGI-2025.txt`). The edition lists every amending text up
to "Loi n°2025-02 du 06 janvier 2025 portant loi de finances pour l'année 2025" and states "Ce code ne contient que du
droit positif". Each article below is quoted from that edition; the article's own amendment note (e.g. "(Loi n° 2022-19
du 27 mai 2022)") dates the wording.
-/

namespace SnTax
open TaxKernel

/-! ## Impôt sur le revenu: salaries, pensions (CGI arts. 164-168) -/

/-- Art. 168 b): "un abattement forfaitaire de 30 % représentatif des cotisations versées à titre obligatoire pour la
constitution d'une retraite et des frais inhérents à la fonction ou à l'emploi, sans que ce montant ne puisse dépasser
900 000 francs." -/
def wageAbatRate : Int := 3000
def wageAbatCap : Int := 900000

/-- Art. 164 1.: pensions and life annuities are taxable, "Toutefois, il est fait application d'un abattement égal à
40 % des pensions et rentes viagères, sans être inférieur à 1.800.000 de FCFA." Art. 168 b): "En ce qui concerne les
pensions et rentes viagères, l'abattement de 30 % susvisé n'est pas opéré". -/
def pensionAbatRate : Int := 4000
def pensionAbatMin : Int := 1800000

/-! ## Revenus fonciers (arts. 66-68) -/

/-- Art. 68 c): "une déduction forfaitaire fixée à 30 % des revenus bruts et représentant les dépenses d'entretien et
de réparation, les frais de gestion, l'assurance et l'amortissement". -/
def rentalAbatRate : Int := 3000

/-- Art. 75 1. (Loi n° 2018-10): the contribution globale foncière (CGF) may be chosen by individuals "dont le montant
brut locatif annuel n'excède pas trente (30) millions de francs". -/
def cgfLimit : Int := 30000000
/-- Art. 78 2.: CGF = 1/12 of the gross annual rent up to 12 000 000, 1,5/12 from 12 000 001 to 18 000 000, 2/12 from
18 000 001; art. 78 3.: "En aucun cas, le montant de la contribution globale foncière ne peut être inférieur à 30.000
francs." The CGF replaces the IR on rents, the minimum fiscal, the built-property tax and the employer's flat
contribution (art. 74 1.). -/
def cgfMin : Int := 30000

/-! ## Charges deductible from global income (art. 55) -/

/-- Art. 55 3.: "les versements volontaires pour la constitution de retraite, dans la limite de 10 % du montant total
des traitements, salaires, indemnités, émoluments et avantages en nature". -/
def volPensionCapRate : Int := 1000
/-- Art. 55 5.: gifts to the bodies of art. 9 3. "dans la limite de 0,50 % du revenu net avant déduction des charges
prévues au présent article". -/
def giftCapRate : Int := 50

/-! ## Barème (art. 173 1., Loi n° 2022-19 du 27 mai 2022) and exemption (art. 52 1.) -/

/-- Art. 173 1.: "le revenu imposable, arrondi au millier de franc inférieur, est soumis au barème progressif
suivant : 0 - 630 000 0% ; 630 001 - 1 500 000 20% ; 1 500 001 - 4 000 000 30% ; 4 000 001 - 8 000 000 35% ;
8 000 001 - 13 500 000 37% ; 13 500 001 - 50 000 000 40% ; + 50 000 000 43%". Art. 52 1. exempts persons whose net
taxable income "n'excède pas la somme de 630.000 francs" (the zero band). -/
def sched : Schedule :=
  Schedule.ofList [(0, 0), (630000, 2000), (1500000, 3000), (4000000, 3500), (8000000, 3700), (13500000, 4000),
    (50000000, 4300)]

/-- Art. 173 1.: "arrondi au millier de franc inférieur". -/
def incomeRounding : Int := 1000

/-- Art. 174 1. (Loi n° 2022-19): "Toutefois, le montant de l'impôt ne peut excéder 43 % du revenu imposable." -/
def taxCapRate : Int := 4300

/-- Art. 174 1.: "réduction pour charges de famille, en fonction du nombre de parts ... tableau suivant qui détermine
les taux, ainsi que les montants minimum et maximum de la réduction". Rows: (half-parts, rate bp, minimum, maximum):
1 part 0 % 0 0; 1,5 10 % 100 000 300 000; 2 15 % 200 000 650 000; 2,5 20 % 300 000 1 100 000; 3 25 % 400 000
1 650 000; 3,5 30 % 500 000 2 030 000; 4 35 % 600 000 2 490 000; 4,5 40 % 700 000 2 755 000; 5 45 % 800 000
3 180 000. -/
def redTable : List (Int × Int × Int × Int) :=
  [(2, 0, 0, 0), (3, 1000, 100000, 300000), (4, 1500, 200000, 650000), (5, 2000, 300000, 1100000),
   (6, 2500, 400000, 1650000), (7, 3000, 500000, 2030000), (8, 3500, 600000, 2490000), (9, 4000, 700000, 2755000),
   (10, 4500, 800000, 3180000)]

/-- Art. 174 4.: "le nombre de parts ... ne pourra en aucun cas dépasser cinq (5)" (10 half-parts). -/
def maxHalfParts : Int := 10

/-- Art. 177 1.: children count if "mineurs ou infirmes ou âgés de moins de 25 ans lorsque ceux-ci poursuivent leurs
études". Reading: "mineurs" taken as under 18 (the age of majority was not read from the Code de la famille); students
aged 18-24 cannot be expressed in the household contract and are not counted. -/
def childAgeLimit : Nat := 18

/-! ## Revenus de capitaux mobiliers (art. 173 2., arts. 203, 208-209) -/

/-- Art. 173 2.: "10 %, pour les produits des actions, parts sociales et parts d'intérêts des sociétés passibles de
l'impôt sur les sociétés"; art. 203 2. a): the withholding "est libératoire de l'impôt sur le revenu des personnes
physiques". -/
def dividendRate : Int := 1000
/-- Art. 173 2.: 16 % on "revenus des créances, dépôts et cautionnements", "ramené à 8 % pour les intérêts, arrérages et
autres produits des comptes de dépôts et des comptes courants ... ouverts dans les comptes d'une banque"; art. 209:
"pour les particuliers, la retenue à la source effectuée conformément aux dispositions de l'article 208 est libératoire
de l'impôt sur le revenu". Reading: the household's interest is bank-deposit interest (8 %). -/
def bankInterestRate : Int := 800

/-! ## Taxe représentative de l'impôt du minimum fiscal (TRIMF, arts. 275-282) -/

/-- Art. 282: the TRIMF is a flat amount read off "l'une des six (6) tranches" of gross income ("revenu brut du
contribuable, y compris ses avantages en argent et en nature"): 0 - 599 999: 900; 600 000 - 999 999: 3 600;
1 000 000 - 1 999 999: 4 800; 2 000 000 - 6 999 999: 12 000; 7 000 000 - 11 999 999: 18 000; 12 000 000 et plus:
36 000. Rows: (lower limit, amount). -/
def trimfTable : List (Int × Int) :=
  [(12000000, 36000), (7000000, 18000), (2000000, 12000), (1000000, 4800), (600000, 3600), (0, 900)]

end SnTax
