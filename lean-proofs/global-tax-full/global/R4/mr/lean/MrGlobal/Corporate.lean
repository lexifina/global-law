import R4Common

/-!
# Mauritania 2025: corporate income tax (1200) and withholding (generated from `R4/specs/mr.json`)

Sources: CGI 2023 French (`cmp20/world/B06-mena/mr/law/cgi2023fr.txt`).

art. 51 1): the IS due is 25 % of the net taxable profit or 2 % of the taxable products of art. 8 (excluding transfers and write-backs of charges) if higher; minimum collection 100 000 MRU (bénéfice réel normal). Turnover stands for the art. 8 products. LF 2024-2025 held only in Arabic, not checked.

art. 132 1): "une retenue à la source est opérée sur les sommes que les personnes physiques ou morales non-résidentes en Mauritanie et n'y disposant pas d'un établissement stable perçoivent en rémunération de prestations de toute nature fournies ou utilisées en Mauritanie"; art. 133 1): "Le taux de la retenue à la source est fixé à 15 % du montant des sommes dues aux personnes non-résidentes". Art. 126: "le taux de l'impôt est fixé à : 20 % pour les plus-values de cession de valeurs mobilières si le cédant est établi dans un État à fiscalité privilégiée ... ; 10 % dans tous les autres cas" (IRCM on distributed income, art. 120, and on interest from claims, art. 121). Thirteenth pass (kernel 2.3.0 grade-C withholding): royalty 15 %: CGI version officielle janvier 2023 art. 132 1) ('prestations de toute nature fournies ou utilisées en Mauritanie') read with art. 210 4) j) (TVA: 'les cessions et concessions d'exploitation de brevet, de droits ou de marque' are prestations de services) and art. 214 1° (non-residents' services 'soumises à la retenue à la source prévue à l'article 132'); art. 133 1): 15 %
-/

namespace MrGlobal
open TaxKernel TaxKernel.Global

def citR : CorpRegime :=
  { name := "Impôt sur les sociétés", sched := Schedule.flat 2500, lossFull := -1, lossExcessBp := 10000 }

def minT : R4.MinTax := { bp := 200, fixed := 0, floor := 100000, cap := -1, onAssets := false }
#guard R4.corpTax citR minT { profit := 10000999, turnover := 100000000, lossesForward := 0 } 1 == 2500249
#guard R4.corpTax citR minT { profit := 0, turnover := 1000000000, lossesForward := 0 } 1 == 20000000
#guard R4.corpTax citR minT { profit := 5000000, turnover := 20000000, lossesForward := 30000000 } 1 == 400000
#guard R4.corpTax citR minT { profit := 1000000, turnover := 400000000, lossesForward := 0 } 1 == 8000000
def whtR : Wht :=
  { name := "Retenues (non-résidents)",
    rules := [{ kind := .services, rateBp := 1500, statute := "CGI art. 133 1) (15 %)" },
              { kind := .dividend, rateBp := 1000, statute := "CGI art. 120, 126 (IRCM 10 %)" },
              { kind := .interest, rateBp := 1000, statute := "CGI art. 121, 126 (IRCM 10 %)" },
              { kind := .royalty, rateBp := 1500, statute := "CGI version officielle janvier 2023 art. 132 1) ('prestations de toute nature fournies ou utilisées en Mauritanie') read with art. 210 4) j) (TVA: 'les cessions et concessions d'exploitation de brevet, de droits ou de marque' are prestations de services) and art. 214 1° (non-residents' services 'soumises à la retenue à la source prévue à l'article 132'); art. 133 1): 15 %" }] }
#guard whtR.amount { kind := .services, amount := 1000000 } == 150000
#guard whtR.amount { kind := .dividend, amount := 1000000 } == 100000
#guard whtR.amount { kind := .interest, amount := 1000000 } == 100000
#guard whtR.amount { kind := .royalty, amount := 1000000 } == 150000
def corporate : Family :=
  { name := "1200 Impôt sur les sociétés", covers := [.cit],
    run := fun _ g _ => if g.entity != .company then [] else [R4.citCharge citR minT g.company "CGI version officielle janvier 2023 art. 51 1) (LFI 2022): régime du bénéfice réel normal" (step := 1)] ++ whtR.charges g.company }

def corporateNotes (g : CanonGlobal) : List String :=
  if g.entity != .company then [] else
  ["thirteenth pass: royalties are prestations de services under the code's own definition (art. 210 4) j)): 15 % (art. 133)"]

end MrGlobal
