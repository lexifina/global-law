import R4Common
import R4Common.K21

/-!
# Madagascar 2025: impôt sur les revenus of companies (1200) and withholding

Source: CGI suivant la LFI 2025 (`cmp20/world/B08-central-africa-fr/mg/law/cdi_lfi2025.txt`).

* **IR** art. 01.01.14 I A: "Le taux de l'impôt est fixé à 20p.100. … le bénéfice imposable est arrondi au millier
  d'Ariary inférieur." Minimum: "En aucun cas, l'impôt calculé au titre d'un exercice ne peut être inférieur au minimum
  fixé ci-dessous: Ar 500 000, majoré de 1p.100 du chiffre d'affaires annuel hors taxe …, pour les personnes imposables
  exerçant des activités agricoles, artisanales, industrielles, minières, hôtelières, touristiques; Ar 1 000 000,
  majoré de 1p.100 … pour les autres entreprises" (petroleum companies 7 per mille, fuel retailers 1 per mille).
* **Déficits** art. 01.01.10 11°: "Ce report peut être effectué sur une période de 5 ans."
* **IRCM** art. 01.04.04: "Le taux de l'impôt sur le revenu des capitaux mobiliers est fixé à 20p.100" (interest on
  créances, art. 01.04.02).
* **Non-residents** art. 01.01.14 II: "il est appliqué un taux de 10p.100 … A. sur le montant des sommes payées à des
  personnes … qui ne possèdent pas d'installation fixe d'affaires à Madagasikara … en rémunération des prestations de
  services de toute nature …; B. sur les dividendes versés aux personnes non résidentes …; C. sur les redevances de
  toute nature, versées … aux personnes non-résidentes."
-/

namespace MgGlobal
open TaxKernel TaxKernel.Global

def ir : CorpRegime := { name := "Impôt sur les revenus (personnes morales)", sched := Schedule.flat 2000 }

def minimumOf (co : Company) : R4.MinTax :=
  if co.flags.contains "petroleum" then { fixed := 1000000, bp := 70 }
  else if co.flags.contains "fuelRetail" then { bp := 10 }
  else if co.flags.contains "agriIndustryTourism" then { fixed := 500000, bp := 100 }
  else { fixed := 1000000, bp := 100 }

def retenues : Wht :=
  { name := "Retenue (non-résidents)",
    rules := [{ kind := .dividend, rateBp := 1000, statute := "CGI art. 01.01.14 II B (10 %)" },
              { kind := .interest, rateBp := 2000, statute := "CGI art. 01.04.02, 01.04.04 (IRCM 20 %)" },
              { kind := .royalty, rateBp := 1000, statute := "CGI art. 01.01.14 II C (10 %)" },
              { kind := .services, rateBp := 1000, statute := "CGI art. 01.01.14 II A (10 %)" }] }

def corporate : Family :=
  { name := "1200 impôt sur les revenus", covers := [.cit],
    run := fun _ g _ =>
      if g.entity != .company then [] else
      [(R4.corpRule ir (minimumOf g.company) 1000).citCharge g
        "CGI art. 01.01.14 I A (20 %, base rounded down to Ar 1 000; minimum Ar 1 000 000 / 500 000 + 1 % of turnover)"]
      ++ retenues.charges g.company }

def corporateNotes (g : CanonGlobal) : List String :=
  if g.entity != .company then [] else
  (if g.company.lossesForward ≠ 0 then ["CGI art. 01.01.10 11°: losses carry forward 5 years; their age is not an input"] else [])
  ++ ["CGI art. 01.01.14 I A: the Ar 500 000 minimum applies to agricultural, craft, industrial, mining, hotel and tourism activities (flag agriIndustryTourism)"]

-- 20 % of 100 000 999 Ar rounded down: 20 000 000; minimum 1 000 000 + 1 % of 500 M = 6 000 000
#guard R4.corpTax ir (minimumOf {}) { profit := 100000999, turnover := 500000000 } 1000 == 20000000
#guard R4.corpTax ir (minimumOf {}) { profit := 0, turnover := 500000000 } 1000 == 6000000
#guard R4.corpTax ir (minimumOf { flags := ["agriIndustryTourism"] }) { profit := 0, turnover := 500000000 } 1000 == 5500000


-- kernel 2.1 `CorpRule` gives the R4 figures (each minimum regime)
#guard [([], 100000999, 500000000), ([], 0, 500000000), (["agriIndustryTourism"], 0, 500000000), (["petroleum"], 0, 900000000), (["fuelRetail"], 5000, 900000000)].all fun (f, p, t) => (R4.corpRule ir (minimumOf { flags := f }) 1000).tax 10000 { profit := p, turnover := t, flags := f } == R4.corpTax ir (minimumOf { flags := f }) { profit := p, turnover := t, flags := f } 1000

end MgGlobal
