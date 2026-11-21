import TaxKernel.World

/-!
# Dominican Republic: impuesto sobre la renta of a resident employee and SDSS contributions, 2025 (access B)

Sources (files in `do/law/`):
* Código Tributario (Ley 11-92), Título II (DGII, `CodigoTributario_Titulo2_dgii.pdf`, 2014 consolidation):
  art. 296 (as amended by Ley 253-12): "pagarán sobre la renta neta gravable del ejercicio fiscal, las sumas que
  resulten de aplicar en forma progresiva, la siguiente escala: 1. Rentas hasta los RD$399,923.00 exentas; 2. ... hasta
  RD$599,884.00, 15%, 3. ... hasta RD$833,171.00, 20%, 4. ... en adelante, 25%"; Párrafo I: "La escala establecida será
  ajustada anualmente por la inflación acumulada"; art. 327 a) 1): the adjustment applies to "Los tramos de la escala
  impositiva establecidos por el artículo 296"; art. 300: fiscal year = calendar year; art. 299 o): exempt "La renta
  neta anual de las personas naturales residentes ... hasta la suma de RD$257,280.00, ajustables por inflación"
  (FINDINGS: a second, older exempt amount left in the Code).
* The 2025 amounts (official secondary): DGII "Impuesto sobre la Renta" page as archived on 2025-06-22 (Internet
  Archive, fetched from the laptop): "Escala retención asalariados 2025": "Rentas hasta RD$416,220.00 | Exento";
  "desde RD$416,220.01 hasta RD$624,329.00 | 15% del excedente de RD$416,220.01"; "desde RD$624,329.01 hasta
  RD$867,123.00 | RD$31,216.00 más el 20% del excedente de RD$624,329.01"; "desde RD$867,123.01 en adelante |
  RD$79,776.00 más el 25% del excedente de RD$867,123.01".
* SDSS (Ley 87-01; official secondary): Tesorería de la Seguridad Social, "Preguntas frecuentes" no. 13 (tss.gob.do,
  read 2026-11-20): worker "Seguro Familiar de Salud 3.04%", "Seguro de Vejez, Discapacidad y Sobrevivencia 2.87%";
  no. 14: caps "Seguro Familiar de Salud 10 SMN", "Seguro de Vejez, Discapacidad y Sobrevivencia 20 SMN" (the page
  shows the 2026 SMN only; the 2025 SMN was not reached: optional input `doSmn`, monthly, else no cap).
-/

namespace DoTax
open TaxKernel

/-- DGII 2025 annual scale (whole pesos; thresholds as printed, the cents dropped). -/
def sched : Schedule := Schedule.ofList [(0, 0), (416220, 1500), (624329, 2000), (867123, 2500)]

/-- The printed fixed amounts of the DGII table. -/
def printedTax (x : Int) : Int :=
  if x ≤ 416220 then 0
  else if x ≤ 624329 then divR .down (1500 * (x - 416220)) 10000
  else if x ≤ 867123 then 31216 + divR .down (2000 * (x - 624329)) 10000
  else 79776 + divR .down (2500 * (x - 867123)) 10000

structure Person where
  sfs : Int
  afp : Int
  taxable : Int
  tax : Int

def person (a : Adult) (smn : Option Int) : Person :=
  let w := pos a.wages
  let capS := match smn with | some s => 12 * 10 * s | none => w
  let capA := match smn with | some s => 12 * 20 * s | none => w
  let sfs := divR .down (304 * min w capS) 10000
  let afp := divR .down (287 * min w capA) 10000
  let taxable := w + pos a.selfEmployment
  { sfs := sfs, afp := afp, taxable := taxable, tax := printedTax taxable }

def out (c : Canon) : Out :=
  let smn := c.int? "doSmn"
  let ps := c.adults.map (fun a => person a smn)
  let unsup :=
    (if smn.isNone then ["SDSS caps (10 and 20 SMN) not applied: the 2025 salario minimo cotizable was not reached (input doSmn)"] else []) ++
    (if c.interest ≠ 0 || c.dividends ≠ 0 || c.rentalIncome ≠ 0 || c.capitalGains ≠ 0 then
      ["interest, dividends (withholding arts. 308, 306 bis), rents and gains not modelled"] else []) ++
    (if (c.adults.map (·.pension)).any (· ≠ 0) then ["pensions not modelled"] else [])
  Out.make c "DO" "DOP" (sumInts (ps.map (·.tax))) (employeeSocial := sumInts (ps.map (fun p => p.sfs + p.afp)))
    (detail := [Out.d "taxableIncome" (sumInts (ps.map (·.taxable))), Out.d "sfs" (sumInts (ps.map (·.sfs))),
      Out.d "afp" (sumInts (ps.map (·.afp))),
      Out.dStr "note" "individual taxation; art. 296 scale indexed, DGII 2025 table (official secondary) with its printed fixed amounts; SDSS 3.04 % + 2.87 % (TSS, official secondary); tax on wages before SDSS (no deduction found in Titulo II)"])
    (unsupported := unsup ++ ["deductibility of SDSS contributions (Ley 87-01) not read: tax computed on gross wages",
      "salario de Navidad (13th month) exemption (Codigo de Trabajo) not modelled"])

def country : Country := { code := "DO", name := "Dominican Republic (Codigo Tributario art. 296; DGII 2025 scale)", currency := "DOP", year := "2025", compute := out }

theorem sched_progressive : sched.progressive = true := by decide

/- F: the printed fixed amounts against the bands: 15 % x 208,109 = 31,216.35 (printed 31,216);
   31,216.35 + 20 % x 242,794 = 79,775.15 (printed 79,776). -/
#guard sched.tax Rule.unitDown 624329 = 31216
#guard sched.tax Rule.unitDown 867123 = 79775
#guard printedTax 867123 = 79774
#guard printedTax 867124 = 79776
#guard printedTax 867124 - printedTax 867123 = 2      -- the printed table jumps by 2 pesos at its own threshold

end DoTax
