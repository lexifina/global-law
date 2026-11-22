import R4Common

/-!
# DR Congo 2025: corporate income tax (1200) and withholding (generated from `R4/specs/cd.json`)

Sources: Code des impôts 2023 (`cmp20/world/B08-central-africa-fr/cd/law/CODE-DES-IMPOTS-2023.txt`). Pass 11: Code des accises (Ordonnance-loi n° 18/002 du 8 mars 2018) from droitcongolais.info (file 621.03.18-Code-des-accises.pdf, R4/fetch/cd11, SHA256SUMS); finance laws 2019-2025 not read for later changes.

art. 83: "Le taux de l'impôt professionnel est fixé à 30% sur les bénéfices et profits des personnes morales et physiques soumises au régime de droit commun. Le taux de l'impôt professionnel est fixé à 14% sur les sommes payées en rémunération des prestations de services de toute nature fournies par des personnes physiques ou morales non établies en République Démocratique du Congo." Code des impôts 2023 edition; LF 2024-2025 not held: grade B.

art. 83 al. 2 (see the CIT entry): 14 % on payments for services of any kind supplied by persons not established in the DRC. Twelfth pass (kernel 2.3.0 grade-C withholding): dividend 20 %: Code des impôts 2023, Livre I IIe partie art. 13 1°, art. 26 (impôt mobilier 20 %); interest 20 %: Code des impôts 2023, Livre I IIe partie art. 13 3°, art. 26 (impôt mobilier 20 % on interest on capital borrowed by DRC companies); royalty 14 %: Code des impôts 2023, Livre I IIe partie art. 13 8°, art. 26 (20 % of the net royalty; charges fixed at 30 % of the gross absent evidence: 14 % of the gross)
-/

namespace CdGlobal
open TaxKernel TaxKernel.Global

def citR : CorpRegime :=
  { name := "Impôt professionnel sur les bénéfices", sched := Schedule.flat 3000, lossFull := -1, lossExcessBp := 10000 }

def minT : R4.MinTax := { bp := 0, fixed := 0, floor := 0, cap := -1, onAssets := false }
#guard R4.corpTax citR minT { profit := 10000999, turnover := 100000000, lossesForward := 0 } 1 == 3000299
#guard R4.corpTax citR minT { profit := 0, turnover := 1000000000, lossesForward := 0 } 1 == 0
#guard R4.corpTax citR minT { profit := 5000000, turnover := 20000000, lossesForward := 30000000 } 1 == 0
#guard R4.corpTax citR minT { profit := 1000000, turnover := 400000000, lossesForward := 0 } 1 == 300000
def whtR : Wht :=
  { name := "Impôt professionnel sur les prestations des non-résidents",
    rules := [{ kind := .services, rateBp := 1400, statute := "art. 83 al. 2 (14 %)" },
              { kind := .dividend, rateBp := 2000, statute := "Code des impôts 2023, Livre I IIe partie art. 13 1°, art. 26 (impôt mobilier 20 %)" },
              { kind := .interest, rateBp := 2000, statute := "Code des impôts 2023, Livre I IIe partie art. 13 3°, art. 26 (impôt mobilier 20 % on interest on capital borrowed by DRC companies)" },
              { kind := .royalty, rateBp := 1400, statute := "Code des impôts 2023, Livre I IIe partie art. 13 8°, art. 26 (20 % of the net royalty; charges fixed at 30 % of the gross absent evidence: 14 % of the gross)" }] }
#guard whtR.amount { kind := .services, amount := 1000000 } == 140000
#guard whtR.amount { kind := .dividend, amount := 1000000 } == 200000
#guard whtR.amount { kind := .interest, amount := 1000000 } == 200000
#guard whtR.amount { kind := .royalty, amount := 1000000 } == 140000
def corporate : Family :=
  { name := "1200 Impôt professionnel sur les bénéfices", covers := [.cit],
    run := fun _ g _ => if g.entity != .company then [] else [R4.citCharge citR minT g.company "Code des impôts 2023, Ordonnance-loi 69/009 art. 83 (30 %, as amended to LF 18/025)" (step := 1)] ++ whtR.charges g.company }

def corporateNotes (g : CanonGlobal) : List String :=
  if g.entity != .company then [] else
  ["art. 83: 30 %; minimum tax and loss rules not read"]

end CdGlobal
