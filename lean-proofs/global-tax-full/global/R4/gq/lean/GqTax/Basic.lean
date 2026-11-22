import TaxKernel.World

/-!
# Equatorial Guinea: Impuesto sobre Sueldos y Salarios (ISS), 2025

Access tier B (rescue pass 3, 2026-11-20). Statute text: **Ley núm. 1/2024, de fecha 19 de noviembre, General Tributaria
de la República de Guinea Ecuatorial**, as printed by the Boletín Oficial del Estado ("Imprime: Dirección General del
BOE, Presidencia del Gobierno", 268 pages, signed in Malabo on 19 November 2024; in force on publication, Disposición
final; it repeals Ley 4/2004, Disposición derogatoria primera). The copy reached is a scan of that BOE print with a law
firm's watermark on every page, published by the firm on its own site (`jonesandsacristan.es/assets/uploads/
leytributaria.pdf`, found through the site's own public law search; sha256 442b86ac…; OCR spa + page images;
`gq/law/rescue3/`). Why B and not A: secondary host (the Ministry of Finance's current site, minhacienda-gob.com,
still offers only Ley 4/2004 under "Ley Tributaria"), and the 2025 budget law was not reached (the 2026 budget law,
Ley 9/2025, cites Ley 1/2024 art. 94 only). Version: Ley 1/2024 as enacted (19 Nov 2024), no later amendment seen.

* art. 122: the ISS "grava los ingresos netos obtenidos por las personas físicas, que trabajan por cuenta ajena".
  art. 123(1): "Los sueldos, salarios, emolumentos y remuneraciones similares o conexas, así como las rentas
  vitalicias, estarán sujetos". art. 128(1): the base takes "el monto neto de los sueldos, salarios, dietas,
  remuneraciones, emolumentos, pensiones, rentas vitalicias y similares".
* art. 129: deductible: (1) employer pension-fund retentions for expatriates (limit), (2) "Las cotizaciones a los seguros
  sociales obligatorios de INSESO, a cargo del empleado", (3) the employee's Fondo de protección al trabajador.
* art. 130(1) (read on the page image, BOE p. 92): "gravará el total de la renta neta anual imponible con arreglo al
  siguiente baremo": De 0 a 1.400.000 0 % Exento; De 1.400.001 a 5.000.000 10 % 360.000; De 5.000.001 a 12.500.000
  15 % 1.485.000; De 12.500.001 a 20.000.000 20 % 2.985.000; Más de 20.000.000 25 %. (The "Impuesto" column is the
  cumulative tax at each band's top: checked below.) art. 130(3): non-residents 15 % of gross.
* art. 105(1)(a): IRCM withheld at "10% sobre las rentas percibidas por las personas físicas residentes".
* art. 29: optional Declaración Global de Rentas Anuales (art. 133(3): withholding is a payment on account only "siempre
  y cuando que el contribuyente opte por la declaración global"): 20 % professional expenses capped at the annual
  Salario Mínimo Interprofesional (29(5)); exempt up to the annual SMI (29(6)). The SMI is fixed outside this law (not
  reached): the DGRA option is not modelled.

Household mapping: each adult's `wages` + `pension` = ISS base (residents, annual baremo; INSESO and FPT employee
contributions not deducted: rates not reached); `dividends` + `interest` at 10 %. Rounding: not printed; whole francs
down. Ley 4/2004 art. 252 (repealed; ministry print, minhacienda-gob.com media/stream/8243) is kept for comparison only.
-/

namespace GqTax
open TaxKernel

/-- Ley 1/2024 art. 130(1): annual baremo (FCFA; each rate applies above the lower bound). -/
def baremo : Schedule := Schedule.ofList [(0, 0), (1400000, 1000), (5000000, 1500), (12500000, 2000), (20000000, 2500)]

def issTax (base : Int) : Int := baremo.tax (Rule.downTo 1) (pos base)

/-- art. 105(1)(a): residents' capital-income withholding, 10 %. -/
def ircmTax (x : Int) : Int := pos x * 10 / 100

/-- Repealed Ley 4/2004 art. 252(1) baremo (comparison only). -/
def baremo2004 : Schedule := Schedule.ofList
  [(0, 0), (1000000, 1000), (3000000, 1500), (5000000, 2000), (10000000, 2500), (15000000, 3000), (20000000, 3500)]
/-- Ley 4/2004 art. 252(2) read as a 20 % professional-expense deduction from the base (comparison only). -/
def tax2004 (gross : Int) : Int := baremo2004.tax (Rule.downTo 1) (pos gross - pos gross * 20 / 100)

-- The statute's own figures: art. 130(1) "Impuesto" column = cumulative tax at each band's top.
#guard issTax 1400000 = 0
#guard issTax 5000000 = 360000
#guard issTax 12500000 = 1485000
#guard issTax 20000000 = 2985000
#guard issTax 20000001 - issTax 20000000 = 0 ∧ issTax 20000004 - issTax 20000000 = 1
-- Ley 4/2004 art. 252(1) printed column (200.000; 500.000; 1.500.000; 2.750.000; 4.250.000).
#guard [3000000, 5000000, 10000000, 15000000, 20000000].map (baremo2004.tax (Rule.downTo 1)) =
  [200000, 500000, 1500000, 2750000, 4250000]
-- The 2024 reform without the optional DGRA: dearer below ~12 M, cheaper above (2004 reading with the 20 % deduction).
#guard tax2004 3600000 = 188000 ∧ issTax 3600000 = 220000
#guard tax2004 5000000 = 350000 ∧ issTax 5000000 = 360000
#guard tax2004 12500000 = 1500000 ∧ issTax 12500000 = 1485000
#guard tax2004 20000000 = 3050000 ∧ issTax 20000000 = 2985000

def out (c : Canon) : Out :=
  let iss := sumInts (c.adults.map fun a => issTax (a.wages + a.pension))
  let rcm := ircmTax c.dividends + ircmTax c.interest
  Out.make c "GQ" "XAF" (iss + rcm)
    (employeeSocial := 0)
    (detail := [Out.d "impuestoSueldosSalarios" iss, Out.d "ircm" rcm,
      Out.d "law2004Comparison" (sumInts (c.adults.map fun a => tax2004 (a.wages + a.pension))),
      Out.dStr "note" "Ley 1/2024 General Tributaria (BOE print, secondary host) arts. 105, 122-130; residents; DGRA option not modelled"])
    (unsupported := ["INSESO and Fondo de protección al trabajador employee contributions: rates not reached (employeeSocial = 0; not deducted from the ISS base, art. 129(2)-(3))",
      "optional Declaración Global de Rentas Anuales (art. 29: 20 % professional expenses capped at the annual SMI; exemption up to the SMI): SMI not reached",
      "2025 budget law not reached (Ley 1/2024 as enacted)"] ++
      (if c.adults.any (fun a => a.selfEmployment ≠ 0) then ["self-employment: Impuesto sobre Beneficios de Negocios (25 %, art. 87) or REAM (arts. 90-94): not modelled"] else []) ++
      (if c.adults.any (fun a => a.pension ≠ 0) then ["pensions taxed under arts. 123/128(1); State social-security pensions may be exempt under art. 124(4)(a) (reading)"] else []) ++
      (if c.rentalIncome ≠ 0 then ["rental income (IRCI, arts. 112-119): not modelled"] else []) ++
      (if c.capitalGains ≠ 0 then ["capital gains: not modelled"] else []))

def country : Country := { code := "GQ", name := "Equatorial Guinea", currency := "XAF", year := "2025", compute := out }

theorem baremo_progressive : baremo.progressive = true := by decide

end GqTax
