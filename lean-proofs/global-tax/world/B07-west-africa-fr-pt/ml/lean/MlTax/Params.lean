import TaxKernel.World

/-!
# Mali 2025: parameters, each with its dated source (whole francs CFA)

Source: "CODE GÉNÉRAL DES IMPÔTS DU MALI", the DGI's online code (https://www.dgi.gouv.ml/CGI/, fetched 2026-11-20; copy
`../src/CGI.html`, text `CGI.txt`). The DGI still serves it as its current code, but the document's own metadata is
dated 2017-08-23 and its latest amendment notes are Loi n° 2016-10 and the LF 2012/2013: the lois de finances 2018-2025
were NOT reached (the DGI site posts only summaries of the 2019 and 2020 annexes; sgg-mali.ml does not answer). Every
amount below is the 2017 consolidation's, carried to 2025 (access B, flagged in `unsupported`).
-/

namespace MlTax
open TaxKernel

/-- Art. 10 (Loi n° 2016-10): "A compter du 1er juillet 2015, les taux applicables au revenu imposable": 0 à 330.000:
0 %; 330.001 à 578.400: 5 %; 578.401 à 1.176.400: 12 %; 1.176.401 à 1.789.733: 18 %; 1.789.734 à 2.384.195: 26 %;
2.384.196 à 3.494.130: 31 %; au-delà de 3.494.130: 37 % (annual income). -/
def sched : Schedule :=
  Schedule.ofList [(0, 0), (330000, 500), (578400, 1200), (1176400, 1800), (1789733, 2600), (2384195, 3100),
    (3494130, 3700)]

/-- Art. 7 a): pension retentions deductible "dans la limite de 4 % des salaires bruts" (INPS employee rate not read:
not taken). -/
def pensionDedCap : Int := 400

/-- Art. 11: "célibataire, divorcé(e) ou veuf (veuve), sans enfant à charge : 0 % ; marié(e), sans enfant à charge :
10 % ; par enfant à charge, jusqu'au dixième inclus : 2,5 %"; "Dans le cas d'imposition séparée de la femme mariée,
chaque époux dispose de la réduction de 10 %, majorée éventuellement de celle à laquelle ouvrent droit les enfants
effectivement à sa charge". -/
def marriedRed : Int := 1000
def childRed : Int := 250
def maxChildren : Int := 10

/-- Art. 12: children count if "mineurs", or under 25 if studying. Reading: under 18. -/
def childAgeLimit : Nat := 18

/-- Art. 12-A (Loi n° 2008-002): "l'impôt calculé est réduit de deux points de pourcentage au profit de l'employé";
art. 12-B: the annual tax is the liquidated amount times "le taux réel amputé de la réduction de deux points".
Reading: the tax is reduced by 2 % of the taxable income (the average rate falls by two points), floored at 0. -/
def twoPoints : Int := 200

/-- Art. 22 (L.F. 2012): IRF "12 % pour les immeubles en dur et semi dur" on gross rent (art. 19: "aucune
réfaction"), "La base taxable est arrondie aux mille francs inférieurs". -/
def irfRate : Int := 1200

/-- Art. 42 (L.F. 2012, 2013): IRVM "10 % pour les dividendes distribués"; "9 % pour les intérêts, arrérages et
autres produits des dépôts à vue ou à échéance fixe et des comptes courants". -/
def dividendRate : Int := 1000
def depositInterestRate : Int := 900

end MlTax
