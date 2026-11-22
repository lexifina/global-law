import TaxKernel.World

/-!
# Ecuador 2025: Impuesto a la Renta of a resident individual (personas naturales)

Sources (read 2026-11-20):
* Ley Organica de Regimen Tributario Interno (LRTI), SRI's codified text (PDF of 2025-10-31,
  `sri.gob.ec/o/sri-portlet-biblioteca-alfresco-internet/descargar/67a341b5-.../Ley de Regimen Tributario Interno.pdf`):
  art. 36 a) Tabla No. 1 "IMPUESTO A LA RENTA DE PERSONAS NATURALES Ano 2025" (as substituted by SRI Resolucion
  NAC-DGERCGC24-00000041, Registro Oficial Quinto Suplemento 708, 20-12-2024); the personal-expenses rebate article
  ("Art. (...)" after art. 10, Ley s/n RO Suplemento 461, 20-12-2023): 18 % of the lesser of the expenses and 7 canastas
  familiares basicas (no dependants).
* SRI page "Impuesto a la Renta" (`sri.gob.ec/impuesto-renta`): the base of employment income is "el ingreso gravado
  menos el valor de los aportes personales al IESS"; "Los adultos mayores se descontaran una fraccion basica gravada
  con tarifa cero" (official secondary for the LRTI art. 9 exemption); SRI "Tablas de calculo" PDF (same 2025 table).

Unit: the individual. Amounts in US dollars.

W5 pattern A (2026-11-20): when `ecIessPersonal` is not given, each adult's personal IESS contribution is 9.45 % of
wages: Resolución C.D. 515 (30 Mar 2016) Anexo Único, "Primera.- De los trabajadores del sector privado bajo relación
de dependencia ... Total Aportes 9,45 11,15 20,60" (personal / patronal / total; replacing the C.D. 501 table of 13 Nov
2015), on the whole materia gravada (no ceiling; Ley de Seguridad Social arts. 11-15 leave the rates to the Consejo
Directivo). IESS's own copies (iess.gob.ec/documents/10162/...), `ec/law/w5/`. Later C.D. resolutions were not checked
for changes to the private-sector totals. The contribution (given or computed) is now also reported as employeeSocial;
`"w5Contrib": false` restores the earlier outputs (no computed default, employeeSocial 0).
-/

namespace EcTax
open TaxKernel

/-- LRTI art. 36 a), Tabla No. 1, Ano 2025 (Fraccion basica, Impuesto fraccion basica, % impuesto fraccion excedente). -/
def tabla2025 : List CumRow :=
  [⟨0, 0, 0⟩, ⟨12081, 0, 500⟩, ⟨15387, 165, 1000⟩, ⟨19978, 624, 1200⟩, ⟨26422, 1398, 1500⟩, ⟨34770, 2650, 2000⟩,
   ⟨46089, 4914, 2500⟩, ⟨61359, 8731, 3000⟩, ⟨81817, 14869, 3500⟩, ⟨108810, 24316, 3700⟩]
/-- The same table read as marginal bands. -/
def bands2025 : Schedule :=
  Schedule.ofList [(0, 0), (12081, 500), (15387, 1000), (19978, 1200), (26422, 1500), (34770, 2000), (46089, 2500),
    (61359, 3000), (81817, 3500), (108810, 3700)]

/-- The printed table, applied literally (tax at the fraccion basica + rate on the excess), rounded to the dollar. -/
def tax2025 (base : Int) : Int := divR .halfUp (cumTicks tabla2025 base) BP

/-- First fraccion basica (the 0 % band): 12.081 USD. -/
def fraccionBasica : Int := 12081
/-- Rebate "equivalente al 18% del menor valor entre: los gastos personales ... y el valor de la canasta familiar
basica multiplicado por siete (7)". -/
def rebateRate : Int := 1800
def canastasNoDependants : Int := 7

structure Person where
  base : Int
  tax : Int
  rebate : Int
  net : Int
  deriving Repr

/-- `iess` = the person's personal IESS contributions (optional input); `expenses`/`canasta` = declared personal
expenses and the INEC January canasta familiar basica (optional inputs). -/
def person (wage se rent interest iess expenses canasta : Int) (age : Nat) : Person :=
  let gross := pos wage + pos se + pos rent + pos interest
  let afterIess := pos (gross - pos iess)
  let base := if age ≥ 65 then pos (afterIess - fraccionBasica) else afterIess
  let tax := tax2025 base
  let rebate := if canasta > 0 then min tax (divR .halfUp (min (pos expenses) (canastasNoDependants * canasta) * rebateRate) BP) else 0
  { base, tax, rebate, net := tax - rebate }

def out (c : Canon) : Out :=
  let n := c.adults.length
  let sh := fun (x : Int) => if n == 2 then [half1 x, half2 x] else [x]
  /- W5 review pass 2 (sweep P2-6): the household-total employee contribution is allotted to the adults in
  proportion to their wages (each person's own contribution is deducted from that person's income); it was halved, which
  gave a one-earner couple half its deduction. Halves only when nobody has wages. -/
  let socW : List Int := c.adults.map (fun a => pos a.wages)
  let wsumS := sumInts socW
  let socBy (x : Int) (i : Nat) : Int :=
    if n ≤ 1 then x else if wsumS = 0 then (if i = 0 then half1 x else half2 x)
    else if i = 0 then x - divR .down (x * socW.getD 1 0) wsumS else divR .down (x * socW.getD 1 0) wsumS
  let shW := fun (x : Int) => if n == 2 then [socBy x 0, socBy x 1] else [x]
  let w5 := (c.bool? "w5Contrib").getD true
  let given := c.int? "ecIessPersonal"
  let statIess : List Int := c.adults.map fun a => divR .halfUp (945 * pos a.wages) BP
  let iess := match given with
    | some x => x
    | none => if w5 then sumInts statIess else 0
  let iessBy : List Int := match given with
    | some x => shW x
    | none => if w5 then statIess else shW 0
  let exps := (c.int? "ecPersonalExpenses").getD 0
  let canasta := (c.int? "ecCanasta").getD 0
  let rows := ((((c.adults.zip (sh c.rentalIncome)).zip (sh c.interest)).zip iessBy).zip (sh exps))
  let ps := rows.map fun ((((a, r), i), s), e) => person a.wages a.selfEmployment r i s e canasta a.age
  let unsup :=
    (if w5 then (if given.isNone then ["personal IESS 9.45 % (C.D. 515) computed on all wages; public-sector and other affiliate tables not applied"] else [])
     else ["personal IESS contributions: rate law (Ley de Seguridad Social) not reached; pass ecIessPersonal (annual household total) or the base is overstated"]) ++ [
     "personal-expenses rebate needs ecPersonalExpenses and ecCanasta (INEC January canasta familiar basica, not reached); the dependants' table (RO Supl. 335, 20-06-2023, p. 19) not reached, so 7 canastas are used for everyone"] ++
    (if c.dividends != 0 then ["dividends: LRTI art. 39.3 / withholding regime not modelled; ignored"] else []) ++
    (if c.interest != 0 then ["interest: taxed in the global base; the art. 9 exemption for deposits of a year or more not modelled"] else []) ++
    (if c.capitalGains != 0 then ["capitalGains: not modelled"] else []) ++
    (if c.adults.any (·.selfEmployment != 0) then ["selfEmployment: gross income taxed; costs and the RIMPE regime not modelled"] else []) ++
    (if c.adults.any (·.pension != 0) then ["pensions: IESS pensions exempt (LRTI art. 9) not checked; not taxed"] else [])
  Out.make c "EC" "USD" (sumInts (ps.map (·.net))) (employeeSocial := if w5 then pos iess else 0)
    (detail := [Out.d "taxableIncome" (sumInts (ps.map (·.base))),
                Out.d "taxBeforeCredits" (sumInts (ps.map (·.tax))),
                Out.d "rebateGastosPersonales" (sumInts (ps.map (·.rebate)))])
    (unsupported := unsup)

def country : Country :=
  { code := "EC", name := "Ecuador (Impuesto a la Renta, personas naturales)", currency := "USD", year := "2025",
    compute := out }

#guard tax2025 12081 == 0
#guard tax2025 15387 == 165
#guard tax2025 108810 == 24316

end EcTax
