import TaxKernel.World

/-!
# Panama 2025: Impuesto sobre la Renta of a natural person (Codigo Fiscal art. 700), territorial system

Source: Ley 8 de 15 de marzo de 2010 "Que reforma el Codigo Fiscal ..." (Gaceta Oficial 26489-A), Legispan PDF
`asamblea.gob.pa/APPS/LEGISPAN/PDF_NORMAS/2010/2010/2010_573_0634.PDF` (Internet Archive capture 2010-03-31; sha256
a16dd0858fc0d400...), art. 10: "El articulo 700 del Codigo Fiscal queda asi: ... Hasta B/.11,000.00 0%; De mas de
B/.11,000.00 hasta B/.50,000.00 El 15% por el excedente de B/.11,000.00 ...; De mas de B/.50,000.00 Pagaran
B/.5,850.00 por los primeros B/.50,000.00 y una tarifa del 25% sobre el excedente". The territorial source rule
(registry: territorial system) was not read in the Codigo Fiscal, so `foreignIncome` is ignored and listed as
unsupported. Amendments to art. 700 after 2010
were not checked (the Codigo Fiscal consolidation, Gaceta Oficial and DGI sites gave no text to scripts): access B.
W5 pattern A (2026-11-20): Caja de Seguro Social. Ley 462 de 18 de marzo de 2025 (Gaceta Oficial Digital 30238 of
18/03/2025, gacetaoficial.gob.pa; page 51 read by OCR, `pa/law/w5/`), art. 84: "El articulo 101 de la Ley 51 de 2005
queda asi: ... 1. La cuota pagada por los empleados, la cual sera el equivalente a 9.75 % de sus sueldos" (the employer
share rises in steps; the employee share is the 9.75 % of Ley 51 before the reform, so all of 2025). No ceiling in art.
101. Not deducted from the art. 700 base (the Codigo Fiscal deductions were not read). Seguro Educativo (Decreto de
Gabinete 168 de 1971) and the thirteenth month's own CSS quota were not reached. Input `"w5Contrib": false` drops it.
-/

namespace PaTax
open TaxKernel

/-- Codigo Fiscal art. 700 (Ley 8/2010 art. 10), in balboas. -/
def art700 : List CumRow := [⟨0, 0, 0⟩, ⟨11000, 0, 1500⟩, ⟨50000, 5850, 2500⟩]
def art700Bands : Schedule := Schedule.ofList [(0, 0), (11000, 1500), (50000, 2500)]

structure Person where
  base : Int
  tax : Int
  deriving Repr

def person (wage se rent : Int) : Person :=
  let base := pos wage + pos se + pos rent
  { base, tax := divR .halfUp (cumTicks art700 base) BP }

/-- Ley 51/2005 art. 101 (1) as replaced by Ley 462/2025 art. 84: employee 9.75 % of wages. -/
def cssEmployee (w : Int) : Int := divR .halfUp (975 * pos w) BP

#guard cssEmployee 50000 = 4875

def out (c : Canon) : Out :=
  let n := c.adults.length
  let w5 := (c.bool? "w5Contrib").getD true
  let css := if w5 then sumInts (c.adults.map fun a => cssEmployee a.wages) else 0
  let sh := fun (x : Int) => if n == 2 then [half1 x, half2 x] else [x]
  let ps := (c.adults.zip (sh c.rentalIncome)).map fun (a, r) => person a.wages a.selfEmployment r
  let unsup :=
    ["Seguro Educativo and the thirteenth-month CSS quota not reached; CSS (9.75 %) not deducted from the art. 700 base (deductions not read)",
     "personal deductions of the Codigo Fiscal (not read) not modelled",
     "art. 700 as written by Ley 8/2010; later amendments not checked; the thirteenth-month salary treatment not modelled"] ++
    (if c.foreignIncome != 0 then ["foreignIncome: territorial source rule not read; ignored"] else []) ++
    (if c.dividends != 0 || c.interest != 0 || c.capitalGains != 0 then ["dividends, interest, capital gains: their own Codigo Fiscal rules not read; ignored"] else []) ++
    (if c.adults.any (·.selfEmployment != 0) then ["selfEmployment: gross taxed; costs not modelled"] else []) ++
    (if c.adults.any (·.pension != 0) then ["pensions: not modelled"] else [])
  Out.make c "PA" "PAB" (sumInts (ps.map (·.tax))) (employeeSocial := css)
    (detail := [Out.d "cssEmployee" css, Out.d "taxableIncome" (sumInts (ps.map (·.base))),
                Out.d "foreignIncomeIgnored" c.foreignIncome])
    (unsupported := unsup)

def country : Country :=
  { code := "PA", name := "Panama (Impuesto sobre la Renta, persona natural, Codigo Fiscal art. 700)", currency := "PAB",
    year := "2025", compute := out }

#guard (person 11000 0 0).tax == 0
#guard (person 50000 0 0).tax == 5850

end PaTax
