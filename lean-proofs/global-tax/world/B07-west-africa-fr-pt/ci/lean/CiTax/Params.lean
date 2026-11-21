import TaxKernel.World

/-!
# Côte d'Ivoire 2025: parameters, each with its dated source (whole francs CFA)

Sources (copies and text in `../src/`):
* Code général des impôts, the DGI's online edition (the DGI's publications list, `backend.dgi.gouv.ci:8000/api/publications`
  item 13 "CODE GENERAL DES IMPOTS 2025", links to https://cgici.com/; pages served from `cgici.com/V2026/page-N.html`,
  fetched 2026-11-20). Each article carries its amendment notes; the ITS articles used here are in the wording of
  "Ord n° 2023-719 du 13 sept. 2023, art. 1er" (in force for incomes from 2024).
* Annexe fiscale à la loi de finances 2025 (Loi n° 2024-1109 du 18 déc. 2024), DGI e-book
  `dgi.gouv.ci/assets/documents/EBOOK/ANNEXE_FISCALE_2025/` (its page text, `annexe2025.txt`): it adds art. 120 bis (dockers)
  and changes no other ITS article; art. 37 raises the IRVM rates for individuals from 2025 distributions.
* CNPS, "Employeur" page (https://www.cnps.ci/employeur, fetched 2026-11-20): rates and ceilings of the Code de prévoyance
  sociale as the CNPS publishes them (official secondary).
-/

namespace CiTax
open TaxKernel

/-- CGI art. 119 bis (Ord. 2023-719): "barème d'imposition progressive par tranche de salaires": monthly income
0 - 75 000: 0 %; 75 001 - 240 000: 16 %; 240 001 - 800 000: 21 %; 800 001 - 2 400 000: 24 %; 2 400 001 - 8 000 000:
28 %; au-dessus de 8 000 000: 32 %. Art. 119 (2023): the taxable income "est le total des rémunérations" (no
deduction; the former 20 % abattement is gone). -/
def monthly : Schedule :=
  Schedule.ofList [(0, 0), (75000, 1600), (240000, 2100), (800000, 2400), (2400000, 2800), (8000000, 3200)]

/-- CGI art. 120 1° (Ord. 2023-719): the Réduction d'Impôt pour Charges de Famille (RICF), "Montant mensuel en
francs" by number of parts: 1: 0; 1,5: 5 500; 2: 11 000; 2,5: 16 500; 3: 22 000; 3,5: 27 500; 4: 33 000; 4,5: 38 500;
5: 44 000 (annual amounts 12 times these). Half-parts → monthly reduction. -/
def ricfMonthly (n2 : Int) : Int := 5500 * (pos (min n2 10 - 2))

/-- Art. 120 1°: "Les personnes retraitées âgées de plus de soixante-dix ans bénéficient d'un abattement de 75 % de
l'impôt calculé après application de la RICF." -/
def retiree70Abat : Int := 7500

/-- Art. 120 2°: "le nombre de parts ... ne pourra en aucun cas dépasser cinq (5)"; children count if minors or under
27 and studying. Reading: "mineurs" = under 18 (age of majority not read); students cannot be expressed. -/
def childAgeLimit : Nat := 18

/-- Art. 116 13- 1°: exempt "La fraction des pensions de retraite et des rentes viagères égale ou inférieure à 320 000
francs par mois" (the page's current wording, with the note "ord n° 2023-719 du 13 sept. 2023"; the earlier wording
printed beside it says 300 000). -/
def pensionExemptMonthly : Int := 320000

/-- CGI art. 182 (Loi n° 2024-1109, an. fiscale, art. 37-1): IRVM 15 % "porté à 17 % en ce qui concerne les revenus
ci-dessus dont le bénéficiaire est une personne physique. Ce taux s'applique aux distributions effectuées à partir de
l'année 2025." -/
def dividendRate : Int := 1700

/-- CNPS (official secondary): "Les cotisations pour la retraite sont à la charge conjointe de l'employeur et du salarié
à raison de 7,7 % pour l'employeur et 6,3 % pour le salarié"; ceiling "45 fois le SMIG soit actuellement : 19 767 780 F
par an (... 1 647 315 FCFA par mois) pour la retraite"; base "ne peut être inférieur au SMIG dont le montant actuel est de
60000 FCFA". -/
def pensionEmployeeRate : Int := 630
def pensionCeilingMonthly : Int := 1647315
def smigMonthly : Int := 60000

end CiTax
