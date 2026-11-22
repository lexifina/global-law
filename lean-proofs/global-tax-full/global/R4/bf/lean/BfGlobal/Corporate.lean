import R4Common

/-!
# Burkina Faso 2025: corporate income tax (1200) and withholding (generated from `R4/specs/bf.json`)

Sources: CGI updated to the LF 2023 (`cmp20/world/B07-west-africa-fr-pt/bf/src/CGI-LF2023-b.txt`), LF 2024 and LFR 2024 OCR.

art. 87: "Le taux de l'impôt sur les sociétés est de 27,5 %. … Toute fraction du bénéfice imposable inférieure à mille …"; art. 24 (loi n° 051-2019): "Le minimum forfaitaire est égal à 0,5 % du chiffre d'affaires … En aucun cas le montant ne peut être inférieur à : un million (1.000.000) de francs CFA pour les contribuables relevant du régime du bénéfice réel normal" (300 000 F under the simplified regime).

art. 210: "une retenue à la source est opérée sur les sommes que les personnes physiques ou morales non résidentes au Burkina Faso perçoivent en rémunération de prestations de toute nature fournies ou utilisées au Burkina Faso"; art. 211 lists studies, consulting, technical assistance, head-office costs and the use of patents, trademarks, designs and copyrights; art. 212: "Le taux de la retenue à la source est fixé à 20 % du montant net des sommes versées aux personnes non établies au Burkina Faso". Art. 140: income from securities 12,5 %; income from claims 25 % (halved for deposit accounts). A loan from a foreign lender is a claim: 25 %.
-/

namespace BfGlobal
open TaxKernel TaxKernel.Global

def citR : CorpRegime :=
  { name := "Impôt sur les sociétés", sched := Schedule.flat 2750, lossFull := -1, lossExcessBp := 10000 }

def minT : R4.MinTax := { bp := 50, fixed := 0, floor := 1000000, cap := -1, onAssets := false }
#guard R4.corpTax citR minT { profit := 10000999, turnover := 100000000, lossesForward := 0 } 1000 == 2750000
#guard R4.corpTax citR minT { profit := 0, turnover := 1000000000, lossesForward := 0 } 1000 == 5000000
#guard R4.corpTax citR minT { profit := 5000000, turnover := 20000000, lossesForward := 30000000 } 1000 == 1000000
#guard R4.corpTax citR minT { profit := 1000000, turnover := 400000000, lossesForward := 0 } 1000 == 2000000
def whtR : Wht :=
  { name := "IRVM / retenues non-résidents",
    rules := [{ kind := .services, rateBp := 2000, statute := "CGI art. 210-212 (20 %)" },
              { kind := .royalty, rateBp := 2000, statute := "CGI art. 211-212 (use of patents, trademarks, copyrights: 20 %)" },
              { kind := .dividend, rateBp := 1250, statute := "CGI art. 140 2) (IRVM 12,5 %)" },
              { kind := .interest, rateBp := 2500, statute := "CGI art. 140 1) (income from claims 25 %)" }] }
#guard whtR.amount { kind := .services, amount := 1000000 } == 200000
#guard whtR.amount { kind := .royalty, amount := 1000000 } == 200000
#guard whtR.amount { kind := .dividend, amount := 1000000 } == 125000
#guard whtR.amount { kind := .interest, amount := 1000000 } == 250000
def corporate : Family :=
  { name := "1200 Impôt sur les sociétés", covers := [.cit],
    run := fun _ g _ => if g.entity != .company then [] else [R4.citCharge citR minT g.company "CGI art. 87 (27,5 %, fraction below 1 000 F dropped), art. 23-24 (minimum forfaitaire 0,5 % of turnover, at least 1 000 000 F under the régime du réel normal)" (step := 1000)] ++ whtR.charges g.company }

def corporateNotes (g : CanonGlobal) : List String :=
  if g.entity != .company then [] else
  ["CGI art. 24: 300 000 F floor for the régime du réel simplifié not applied", "LF 2025 not held", "art. 212: 10 % for road transport by ECOWAS providers without proof of residence, not modelled; interest on deposit accounts is halved (12,5 %), a loan from abroad is taken at 25 %"]

end BfGlobal
