import CoTax.Params

/-!
# Colombia 2025: impuesto sobre la renta of a resident individual (cédula general, pensiones, dividendos)

Unit: the individual (ET art. 7: "Las personas naturales ... son contribuyentes"; spouses are taxed separately).
Steps (ET art. 330-336, 241, 242, 254-1):
1. cédula general: labour income (wages; self-employment as rentas de trabajo no laborales) + capital income
   (interest, rent), less INCR = mandatory pension and health contributions (art. 55, 56);
2. less exempt income and deductions limited to 40 % and 1.340 UVT (art. 336 num. 3): the 25 % labour exemption
   (art. 206 num. 10, max 790 UVT) and the dependants' deduction (art. 387: 10 % of gross labour income, max
   32 UVT a month); plus 72 UVT per dependant (max 4) outside the limit (art. 336 num. 3 inc. 2);
3. cédula de pensiones: pensions less the monthly 1.000 UVT exemption (art. 206 num. 5, 337);
4. cédula de dividendos: dividends from profits taxed at company level (art. 242 inc. 1, 331);
5. art. 241 table on the sum (art. 331), less the dividend discount of art. 254-1.
W5 pattern A (2026-11-20; input `"w5Contrib": false` restores the earlier outputs; not applied with `--oecd`):
* pension rate 16 % from 2008 (Decreto 4982 de 2007 art. 1, D.O. 46.854: "la tasa de cotización al Sistema General
  de Pensiones será del 16% del ingreso base de cotización"), employee 25 % (Ley 797 de 2003 art. 7, Ley 100 art. 20:
  "Los empleadores pagarán el 75% de la cotización total y los trabajadores el 25% restante") = 4 %;
* base capped at 25 SMMLV (Ley 797 art. 5, Ley 100 art. 18: "El límite de la base de cotización será de veinticinco
  (25) salarios mínimos"), for pension and health ("las cotizaciones al sistema de salud se hagan sobre la misma base");
* Fondo de Solidaridad Pensional (Ley 797 art. 7 last para. and art. 8, Ley 100 art. 27): 1 % from 4 SMMLV, plus 0.2 /
  0.4 / 0.6 / 0.8 / 1 % from 16 / 17 / 18 / 19 / 20 SMMLV; part of the mandatory pension contribution, so INCR (art. 55);
* SMMLV 2025 = 1.423.500 (Decreto 1572 de 2024 art. 1, D.O. 52.980; repealed for 2026 by Decreto 1469 de 2025).
Texts: Global law `colombia/act/2003/reforma-pensional` (Ley 797 as in force to 2025-12-31); decrees from the
Colpensiones normogram (official, `co/law/w5/`). Ley 2381 de 2024 (art. 94: from 1 July 2025) has its own FSP rules:
not applied (its articles are not in the Global law copy; entry into force in 2025 not established here). The 1-SMMLV
floor of art. 18 and the PILA rounding to the hundred pesos are not applied (monthly amounts rounded to the peso).
Children count as dependants for the parent with the larger labour income (the statute lets one taxpayer claim each
dependant; the model's choice is stated in `detail.dependantsClaimedBy`).
-/

namespace CoTax
open TaxKernel

def u (n : Int) : Int := n * uvt

/-- Art. 241 tax in pesos on a base in pesos: the printed table with thresholds and fixed amounts converted at the UVT
(the statute writes "Base Gravable en UVT"; exact rational arithmetic, rounded half-up to the peso at the end). -/
def art241Pesos : List CumRow := art241.map fun r => { r with lo := u r.lo, base := u r.base }
def tax241 (base : Int) : Int := divR .halfUp (cumTicks art241Pesos base) BP

/-- Employee contributions on a wage (pesos): pension 3,875 % (Ley 100 art. 20 as read), health 4 % (art. 204).
No ceiling/floor applied: the 25-SMMLV cap and 1-SMMLV floor (art. 18) and the solidarity fund (art. 20, 27) need the
2025 SMMLV, not reached. -/
def pensionContribAt (rateTenthBp : Int) (w : Int) : Int := divR .halfUp (pos w * rateTenthBp) 100000
def pensionContrib (w : Int) : Int := pensionContribAt pensionRateEmployeeTenthBp w

/-- OECD Taxing Wages convention (`--oecd`; Taxing Wages 2025, Part II, Colombia chapter): health and pension
contributions "are not classified as taxes but as a NTCP since more than 50% goes to private sector", while "the
employee's contributions to pensions and health are included in the model as non-taxable income": employeeSocial = 0,
the contributions still excluded from income; and the chapter's employee pension rate "4.0% of the employee's monthly
earnings" (16 % x 25 %, the 2008 one-point increase that the model's statute reading lacks). -/
def oecdPensionTenthBp : Int := 4000
def healthContrib (w : Int) : Int := divR .halfUp (pos w * healthRateEmployee) BP

/-! ### W5 pattern A: 16 % pension rate, 25-SMMLV cap, Fondo de Solidaridad Pensional -/
def smmlv2025 : Int := 1423500
/-- FSP rate in tenths of a basis point for a monthly base `ibc` (Ley 797 arts. 7-8). -/
def fspTenthBp (ibc : Int) : Int :=
  (if ibc ≥ 4 * smmlv2025 then 1000 else 0) +
  (if ibc ≥ 20 * smmlv2025 then 1000 else if ibc ≥ 19 * smmlv2025 then 800 else if ibc ≥ 18 * smmlv2025 then 600
   else if ibc ≥ 17 * smmlv2025 then 400 else if ibc ≥ 16 * smmlv2025 then 200 else 0)
/-- Annual (pension incl. FSP, health) of a wage, monthly base = wage / 12 capped at 25 SMMLV. -/
def w5Contribs (w : Int) : Int × Int :=
  let ibc := min (pos w / 12) (25 * smmlv2025)
  (12 * divR .halfUp (ibc * (4000 + fspTenthBp ibc)) 100000, 12 * divR .halfUp (ibc * healthRateEmployee) BP)

#guard fspTenthBp (4 * smmlv2025) = 1000 ∧ fspTenthBp (16 * smmlv2025) = 1200 ∧ fspTenthBp (25 * smmlv2025) = 2000
#guard (w5Contribs (12 * 1000000)).1 = 12 * 40000 ∧ (w5Contribs (12 * 100000000)).1 = 12 * 2135250

structure Person where
  incr : Int
  grossGeneral : Int
  exempt25 : Int
  depDed : Int
  limited : Int
  depExtra : Int
  general : Int
  pension : Int
  dividends : Int
  tax : Int
  divDiscount : Int
  social : Int
  deriving Repr

def person (pRate : Int) (wage se interest rent pension dividends : Int) (deps : Nat) (w5 : Bool := false) : Person :=
  let pc := if w5 then (w5Contribs wage).1 else pensionContribAt pRate wage
  let hc := if w5 then (w5Contribs wage).2 else healthContrib wage
  let incr := pc + hc
  let labour := pos wage + pos se
  let gross := labour + pos interest + pos rent
  let afterIncr := pos (gross - incr)
  let depDed := if deps > 0 && wage > 0 then min (divR .down (pos wage * depRate) BP) (12 * u depCapUVTMonth) else 0
  let labourNet := pos (labour - incr - depDed)
  let ex25 := min (divR .down (labourNet * exempt25Rate) BP) (u exempt25CapUVT)
  let limit := min (divR .down (afterIncr * limitRate) BP) (u limitCapUVT)
  let limited := min (ex25 + depDed) limit
  let depExtra := if wage > 0 then u depExtraUVT * (min deps depExtraMax : Nat) else 0
  let general := pos (afterIncr - limited - depExtra)
  let pens := pos (pension - 12 * u pensionExemptUVTMonth)
  let divs := pos dividends
  let base := general + pens + divs
  let t := tax241 base
  let disc := if divs > u divDiscountFromUVT then divR .halfUp ((divs - u divDiscountFromUVT) * divDiscountRate) BP else 0
  let social := incr + divR .halfUp (pos pension * healthRatePensioner) BP
  { incr, grossGeneral := gross, exempt25 := ex25, depDed, limited, depExtra, general, pension := pens,
    dividends := divs, tax := pos (t - min disc t), divDiscount := min disc t, social }

def out (args : List String) (c : Canon) : Out :=
  let oecd := args.contains "--oecd"
  let pRate := if oecd then oecdPensionTenthBp else pensionRateEmployeeTenthBp
  let w5 := !oecd && (c.bool? "w5Contrib").getD true
  let n := c.adults.length
  let sh := fun (x : Int) => if n == 2 then [half1 x, half2 x] else [x]
  let deps := c.childrenUnder (depChildMaxAge + 1)
  -- dependants claimed by the adult with the larger wage (first adult on a tie)
  let claimant : Nat := match c.adults with
    | [a, b] => if b.wages > a.wages then 1 else 0
    | _ => 0
  let rows := (((c.adults.zip (sh c.interest)).zip (sh c.rentalIncome)).zip (sh c.dividends))
  let ps := (rows.zipIdx).map fun ((((a, i), r), d), k) =>
    person pRate a.wages a.selfEmployment i r a.pension d (if k == claimant then deps else 0) w5
  let tax := sumInts (ps.map (·.tax))
  let unsup :=
    (if w5 then ["contributions: the 1-SMMLV minimum base (Ley 100 art. 18) and PILA rounding not applied; Ley 2381 de 2024 FSP rules not applied"] else
    ["solidarity pension fund (Ley 100 art. 20, 27: 1 % from 4 SMMLV) and the 25-SMMLV contribution cap: 2025 SMMLV not reached",
     "pension contribution at 25 % of 15,5 % (Ley 100 art. 20 as read); the 2008 one-point increase decree was not reached"]) ++
    (if c.interest != 0 then ["interest: componente inflacionario (ET art. 38-41) not deducted"] else []) ++
    (if c.rentalIncome != 0 then ["rentalIncome: costs and expenses (ET art. 336 num. 4) unknown; gross rent taxed"] else []) ++
    (if c.adults.any (·.selfEmployment != 0) then ["selfEmployment: taken as rentas de trabajo no laborales with the 25 % exemption (art. 206 par. 5); contributions of independents (40 % IBC) not modelled"] else []) ++
    (if c.capitalGains != 0 then ["capitalGains: listed shares below 3 % of a company are not income (ET art. 36-1); taken as 0"] else []) ++
    (if c.charitable != 0 || c.pensionContributions != 0 then ["charitable/pensionContributions: ET art. 126-1, 257 not modelled"] else []) ++
    ["ET art. 336 num. 5 (1 % of e-invoiced purchases, max 240 UVT) not modelled",
     "subsidio familiar (cajas de compensación; regional cuota monetaria) not modelled"] ++
    (if oecd then ["--oecd: OECD Taxing Wages conventions (contributions as NTCP: employeeSocial 0; employee pension 4 %)"] else [])
  Out.make c "CO" "COP" tax (employeeSocial := if oecd then 0 else sumInts (ps.map (·.social)))
    (detail := [Out.d "taxableIncome" (sumInts (ps.map fun p => p.general + p.pension + p.dividends)),
                Out.d "rentaLiquidaCedulaGeneral" (sumInts (ps.map (·.general))),
                Out.d "incr" (sumInts (ps.map (·.incr))),
                Out.d "exempt25" (sumInts (ps.map (·.exempt25))),
                Out.d "dependantsDeduction" (sumInts (ps.map (·.depDed))),
                Out.d "dependantsExtra72UVT" (sumInts (ps.map (·.depExtra))),
                Out.d "limitedExemptAndDeductions" (sumInts (ps.map (·.limited))),
                Out.d "dividendDiscount" (sumInts (ps.map (·.divDiscount))),
                Out.d "dependantsClaimedBy" (claimant + 1), Out.d "uvt" uvt])
    (unsupported := unsup)

def country : Country :=
  { code := "CO", name := "Colombia (impuesto sobre la renta, personas naturales residentes)", currency := "COP",
    year := "2025", compute := out [], computeWith := out }

end CoTax
