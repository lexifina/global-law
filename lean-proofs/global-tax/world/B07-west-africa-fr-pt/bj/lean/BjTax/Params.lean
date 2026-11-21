import TaxKernel.World

/-!
# Benin 2025: parameters, each with its dated source (whole francs CFA)

Source: "Code général des impôts 2023", Loi n° 2021-15 du 23 décembre 2021 portant code général des impôts, "Mise à
jour de la loi n° 2022-33 du 9 décembre 2022 portant loi de finances pour la gestion 2023", official edition published
by the Ministère de l'Economie et des Finances (https://finances.bj/wp-content/uploads/2023/01/63c7b8d3eef3c_Benin-CGI-2023-officiel.pdf,
fetched 2026-11-20; text `../src/CGI-2023.txt`). The lois de finances for 2024 and 2025 were NOT reached (finances.bj
lists none after 2023; sgg.gouv.bj's law list has no finance law for 2024-2025; the DGI site impots.finances.gouv.bj
is suspended): amounts are the 2023 code's (access B).
-/

namespace BjTax
open TaxKernel

/-- Art. 125 1): "L'impôt est calculé par application à la base d'imposition des taux progressifs suivants : 0% pour
la tranche inférieure ou égale à 60 000 francs CFA ; 10% ... entre 60 001 et 150 000 ; 15% ... entre 150 001 et
250 000 ; 19% ... entre 250 001 et 500 000 ; 30% pour la tranche supérieure à 500 000 francs CFA" (art. 122: the
"salaire mensuel imposable", gross: no deduction is provided). -/
def monthly : Schedule :=
  Schedule.ofList [(0, 0), (60000, 1000), (150000, 1500), (250000, 1900), (500000, 3000)]

/-- Art. 125 2): "L'impôt ... est majoré d'une redevance au profit de l'office de radiodiffusion et télévision du
Bénin de : mille (1 000) francs CFA sur le salaire du mois de mars ; trois mille (3 000) francs CFA sur le salaire du
mois de juin. Les personnes dont le montant du revenu imposable n'excède pas la première tranche du barème de l'impôt
sont exonérées du prélèvement de trois mille (3 000) francs CFA." -/
def ortbMarch : Int := 1000
def ortbJune : Int := 3000
def firstBand : Int := 60000

/-- Art. 86 2): "10% pour les dividendes autres que ceux mentionnés au paragraphe 1" (5 % for listed companies);
art. 88: "Pour les revenus des créances, dépôts et cautionnements, l'impôt est calculé ... d'un taux de 15%". -/
def dividendRate : Int := 1000
def interestRate : Int := 1500

/-- Art. 103-104: IRF on "le montant brut des loyers" at 12 %, "majoré d'une redevance de quatre mille (4 000)
francs CFA, au profit de l'ORTB". -/
def irfRate : Int := 1200
def irfOrtb : Int := 4000

end BjTax
