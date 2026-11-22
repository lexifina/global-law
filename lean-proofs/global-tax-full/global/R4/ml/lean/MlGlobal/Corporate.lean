import R4Common

/-!
# Mali 2025: corporate income tax (1200) and withholding (generated from `R4/specs/ml.json`)

The only local text is a CGI edition with amendment notes up to the LF 2018 (`cmp20/world/B07-west-africa-fr-pt/ml/src/CGI.txt`) and the DGI 2025 activity report (`RA-DGI-2025.ocr.txt`). Pass 9: the DGI's own online CGI (https://www.dgi.gouv.ml/CGI/, the 'Code Général des Impôts' link of dgi.gouv.ml, re-checked 2026-11-21) is still the 2017 consolidation held as `world/B07-west-africa-fr-pt/ml/src/CGI.txt`; the DGI annual report 2025 (`RA-DGI-2025.ocr.txt`) reports receipts only. Per the region convention an edition older than 2025 with no later finance law in hand is graded B and flagged.

art. 85: "(Loi n°11-078) Le taux de l'impôt est fixé à 30 %. La base taxable est arrondie au millier de francs inférieurs." art. 86: "(Loi n°11-078, L.F.2014, L.F.2015) Le montant de l'impôt dû par les contribuables imposés suivant le régime du bénéfice réel ne peut être inférieur à 1 % du montant du chiffre d'affaires hors taxe arrondi au millier de francs inférieurs. En ce qui concerne les entreprises soumises à l'impôt sur les sociétés, le chiffre d'affaires s'entend du montant des produits d'exploitation et des produits accessoires. Ce minimum forfaitaire est dû même en cas de déficit".

art. 42: "(L.F.2012, L.F.2013) Les taux de l'impôt sur les revenus des valeurs mobilières sont fixés ainsi qu'il suit : 1) 10 % pour les dividendes distribués. Ce taux est ramené à 7 % pour les dividendes distribués par les sociétés cotées ... 4) 9 % pour les intérêts, arrérages et autres produits des dépôts à vue ou à échéance fixe et des comptes courants. 5) 15 % pour les lots ... 6) 18 % pour tous les autres revenus." The taxable revenues include "7° les intérêts, arrérages et tous autres produits de créances hypothécaires, privilégiées et chirographaires, à l'exclusion de toute opération commerciale ne présentant pas le caractère juridique d'un prêt". Thirteenth pass (kernel 2.3.0 grade-C withholding): royalty 15 %: CGI (consolidation 2017) art. 94 b) (use of copyrights, patents, trade marks, secret processes, know-how), 95, 96, 97 (L.F.2013): retenue 30 % on the sum less the 50 % flat deduction for services (art. 96): 15 % of the gross (reading: the art. 94 b) items are prestations de toute nature, flag); services 15 %: CGI (consolidation 2017) art. 94 b) last indent ('toutes sommes payées en rémunération des prestations de toute nature fournies ou utilisées au Mali'), 95, 96 (50 % flat deduction), 97 (L.F.2013, 30 %): 15 % of the gross
-/

namespace MlGlobal
open TaxKernel TaxKernel.Global

def citR : CorpRegime :=
  { name := "Impôt sur les sociétés", sched := Schedule.flat 3000, lossFull := -1, lossExcessBp := 10000 }

def minT : R4.MinTax := { bp := 100, fixed := 0, floor := 0, cap := -1, onAssets := false }
#guard R4.corpTax citR minT { profit := 10000999, turnover := 100000000, lossesForward := 0 } 1000 == 3000000
#guard R4.corpTax citR minT { profit := 0, turnover := 1000000000, lossesForward := 0 } 1000 == 10000000
#guard R4.corpTax citR minT { profit := 5000000, turnover := 20000000, lossesForward := 30000000 } 1000 == 200000
#guard R4.corpTax citR minT { profit := 1000000, turnover := 400000000, lossesForward := 0 } 1000 == 4000000
def whtR : Wht :=
  { name := "Impôt sur les revenus des valeurs mobilières (payments abroad)",
    rules := [{ kind := .dividend, rateBp := 1000, statute := "CGI art. 42 1) (10 %)" },
              { kind := .interest, rateBp := 1800, statute := "CGI art. 42 6) (18 %, loan interest)" },
              { kind := .royalty, rateBp := 1500, statute := "CGI (consolidation 2017) art. 94 b) (use of copyrights, patents, trade marks, secret processes, know-how), 95, 96, 97 (L.F.2013): retenue 30 % on the sum less the 50 % flat deduction for services (art. 96): 15 % of the gross (reading: the art. 94 b) items are prestations de toute nature, flag)" },
              { kind := .services, rateBp := 1500, statute := "CGI (consolidation 2017) art. 94 b) last indent ('toutes sommes payées en rémunération des prestations de toute nature fournies ou utilisées au Mali'), 95, 96 (50 % flat deduction), 97 (L.F.2013, 30 %): 15 % of the gross" }] }
#guard whtR.amount { kind := .dividend, amount := 1000000 } == 100000
#guard whtR.amount { kind := .interest, amount := 1000000 } == 180000
#guard whtR.amount { kind := .royalty, amount := 1000000 } == 150000
#guard whtR.amount { kind := .services, amount := 1000000 } == 150000
def corporate : Family :=
  { name := "1200 Impôt sur les sociétés", covers := [.cit],
    run := fun _ g _ => if g.entity != .company then [] else [R4.citCharge citR minT g.company "CGI (consolidation 2017) art. 85 (Loi n°11-078: 30 %, base rounded down to 1 000 F) and art. 86 (L.F.2014, L.F.2015: minimum 1 % of turnover excluding tax, due even with a loss) — edition of 2017, flagged" (step := 1000)] ++ whtR.charges g.company }

def corporateNotes (g : CanonGlobal) : List String :=
  if g.entity != .company then [] else
  ["2017 consolidation (no LF 2018-2025 held): flagged", "the minimum's turnover is rounded down to 1 000 F in the statute (not applied); the art. 86 second-paragraph floor (IBIC share of the synthetic tax maximum) and the art. 86-A property-company minimum are not modelled", "2017 consolidation (no LF 2018-2025 held): flagged", "thirteenth pass: CGI art. 94-97 (personnes n'ayant pas au Mali d'installation professionnelle permanente) located: 30 % on 50 % of the gross = 15 % on services and royalties"]

end MlGlobal
