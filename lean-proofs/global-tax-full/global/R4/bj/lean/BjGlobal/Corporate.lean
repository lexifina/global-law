import R4Common

/-!
# Benin 2025: impôt sur les sociétés (1200) and withholding — grade B (2023 edition)

Source: CGI 2023 (`cmp20/world/B07-west-africa-fr-pt/bj/src/CGI-2023.txt`).

* art. 46 1): "Le taux de l'impôt est fixé à : a) 25 % du bénéfice imposable pour les personnes morales ayant une
  activité industrielle, à l'exception des industries extractives; les écoles privées …; b) 30 %" otherwise.
* art. 47 (LF 2023): minimum "égal à … 1% des produits encaissables dans tous les autres cas" (10 % real-estate
  companies, 3 % construction); 3): "Dans tous les cas, l'impôt ne peut être inférieur à deux cent cinquante mille
  (250.000) francs CFA". Produits encaissables are taken as the turnover.
* art. 43: losses carried forward "jusqu'au cinquième exercice qui suit l'exercice déficitaire".
* art. 142 (LF 2023): "Le taux de la retenue est fixé à 20%", on sums due to non-residents not established in Benin.
-/

namespace BjGlobal
open TaxKernel TaxKernel.Global

def isOf (co : Company) : CorpRegime :=
  { name := "Impôt sur les sociétés", sched := Schedule.flat (if co.flags.contains "industrial" then 2500 else 3000) }

def minOf (co : Company) : R4.MinTax :=
  { bp := if co.flags.contains "realEstate" then 1000 else if co.flags.contains "construction" then 300 else 100, floor := 250000 }

def wht : Wht :=
  { name := "Retenue à la source (non-résidents)",
    rules := [{ kind := .royalty, rateBp := 2000, statute := "CGI 2023 art. 142 (20 %)" },
              { kind := .services, rateBp := 2000, statute := "CGI 2023 art. 142 (20 %)" },
              { kind := .dividend, rateBp := 500, statute := "CGI 2023 art. 86 1) (IRCM 5 % on dividends distributed to non-resident partners)" },
              { kind := .interest, rateBp := 1500, statute := "CGI 2023 art. 71, 85, 88 (IRCM 15 % on interest from claims, deposits and current accounts)" }] }

def corporate : Family :=
  { name := "1200 impôt sur les sociétés", covers := [.cit],
    run := fun _ g _ =>
      if g.entity != .company then [] else
      [R4.citCharge (isOf g.company) (minOf g.company) g.company
        "CGI 2023 art. 46 (30 %; 25 % industry), art. 47 (minimum 1 % of produits encaissables, at least 250 000 F)"]
      ++ wht.charges g.company }

def corporateNotes (g : CanonGlobal) : List String :=
  if g.entity != .company then [] else
  ["Benin: CGI 2023 edition; LF 2024-2025 changes not available",
   "IRVM on dividends and interest paid abroad: rate article not read (no charge)"]

#guard R4.corpTax (isOf {}) (minOf {}) { profit := 1000000, turnover := 10000000 } == 300000
#guard R4.corpTax (isOf {}) (minOf {}) { profit := 0, turnover := 10000000 } == 250000

end BjGlobal
