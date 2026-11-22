import R4Common

/-!
# Equatorial Guinea 2025: corporate income tax (1200) and withholding (generated from `R4/specs/gq.json`)

Source: Ley Núm. 1/2024 (Ley Tributaria), OCR of the BOE-style edition (`cmp20/world/B08-central-africa-fr/gq/law/rescue3/Ley1-2024_ocr_spa.txt`).

art. 75: "… fracción del beneficio imponible inferior a 1.000 FCFA será despreciable. 2) El tipo de gravamen del Impuesto sobre Sociedades se fija en 25%. 3) El importe mínimo del impuesto sobre sociedades … no podrá ser inferior al que resulte de la aplicación del 1,5% sobre el volumen de ingresos obtenido por la entidad en el ejercicio fiscal en curso y, se denominará Cuota Mínima Fiscal."

art. 76: "Los obligados tributarios no residentes, pagarán en concepto del Impuesto sobre Sociedades o en Impuesto sobre Beneficios de Negocios, un tipo de gravamen equivalente al 10% sobre la facturación bruta obtenida en Guinea Ecuatorial". The preamble: IRCM "del 25% al 15% para las personas físicas y jurídicas no residentes" (the IRCM article itself not located: grade B).
-/

namespace GqGlobal
open TaxKernel TaxKernel.Global

def citR : CorpRegime :=
  { name := "Impuesto sobre Sociedades", sched := Schedule.flat 2500, lossFull := -1, lossExcessBp := 10000 }

def minT : R4.MinTax := { bp := 150, fixed := 0, floor := 0, cap := -1, onAssets := false }
#guard R4.corpTax citR minT { profit := 10000999, turnover := 100000000, lossesForward := 0 } 1000 == 2500000
#guard R4.corpTax citR minT { profit := 0, turnover := 1000000000, lossesForward := 0 } 1000 == 15000000
#guard R4.corpTax citR minT { profit := 5000000, turnover := 20000000, lossesForward := 30000000 } 1000 == 300000
#guard R4.corpTax citR minT { profit := 1000000, turnover := 400000000, lossesForward := 0 } 1000 == 6000000
def whtR : Wht :=
  { name := "Retenciones a no residentes",
    rules := [{ kind := .services, rateBp := 1000, statute := "Ley 1/2024 art. 76 (10 %)" },
              { kind := .royalty, rateBp := 1000, statute := "Ley 1/2024 art. 76 (10 %)" },
              { kind := .dividend, rateBp := 1500, statute := "Ley 1/2024 IRCM (15 % non-residents, per the preamble)" },
              { kind := .interest, rateBp := 1500, statute := "Ley 1/2024 IRCM (15 % non-residents, per the preamble)" }] }
#guard whtR.amount { kind := .services, amount := 1000000 } == 100000
#guard whtR.amount { kind := .royalty, amount := 1000000 } == 100000
#guard whtR.amount { kind := .dividend, amount := 1000000 } == 150000
#guard whtR.amount { kind := .interest, amount := 1000000 } == 150000
def corporate : Family :=
  { name := "1200 Impuesto sobre Sociedades", covers := [.cit],
    run := fun _ g _ => if g.entity != .company then [] else [R4.citCharge citR minT g.company "Ley 1/2024 art. 75 (25 %; Cuota Mínima Fiscal 1,5 % of revenue)" (step := 1000)] ++ whtR.charges g.company }

def corporateNotes (g : CanonGlobal) : List String :=
  if g.entity != .company then [] else
  ["Ley 1/2024 art. 75: revenue (volumen de ingresos) taken as the turnover"]

end GqGlobal
