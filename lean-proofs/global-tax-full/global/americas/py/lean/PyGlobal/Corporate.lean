import PyGlobal.Pit

/-!
# Paraguay 2025: IRE and withholding on non-residents (1200)

Source: Ley 6380/19 (DNIT text of the act as enacted; `world/.../py/src/l6380page.txt`): grade B.
* **art. 21**: "La tasa del IRE será del 10% (diez por ciento), sobre la renta neta".
* Dividends (IDU, art. 43): "15% (quince por ciento) cuando el perceptor … sea … no residente".
* **art. 76** (INR): "La tasa del INR será del 15% (quince por ciento)" on the net income the act presumes for each
  kind of payment (the presumed shares, art. 73-75, not read: applied to the gross amount, flagged).
-/

namespace PyGlobal.Corporate
open TaxKernel TaxKernel.Global AmerCommon PyGlobal

def regime : CorpRegime :=
  { name := "Impuesto a la Renta Empresarial (IRE)", sched := Schedule.flat 1000 }

def citStatute : String := "Ley 6380/19 art. 21 (10 %)"

def wht : Wht :=
  { name := "Withholding tax (non-residents)", rules := [{ kind := .dividend, rateBp := 1500, statute := "Ley 6380/19 art. 43 2 (IDU 15 %, non-resident)" }, { kind := .interest, rateBp := 1500, statute := "Ley 6380/19 art. 76 (INR 15 %; presumed base not applied)" }, { kind := .royalty, rateBp := 1500, statute := "Ley 6380/19 art. 76 (INR 15 %; presumed base not applied)" }, { kind := .services, rateBp := 1500, statute := "Ley 6380/19 art. 76 (INR 15 %; presumed base not applied)" }] }

def citF : Family := corpFamily "1200 Impuesto a la Renta Empresarial (IRE)" (fun _ => regime) (fun _ => citStatute) wht (fun _ => [])

def families : List Family := [citF]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  when (g.entity == .company) "losses brought forward, interest limitation and participation exemptions not modelled: taxable profit = profit + add-backs − exempt income"
  ++ when (g.entity == .company) "IRE SIMPLE / RESIMPLE regimes and the INR presumed net income shares not modelled"
  ++ when (g.entity == .company && g.company.paymentsAbroad.any (fun p => p.kind == .interest || p.kind == .royalty || p.kind == .services || p.kind == .dividend)) "payments abroad of a kind without a rule read get no withholding"

#guard regime.citTax { profit := 1000000 } == 100000
#guard wht.amount { kind := .dividend, amount := 1000000 } == 150000
#guard wht.amount { kind := .interest, amount := 1000000 } == 150000
#guard wht.amount { kind := .royalty, amount := 1000000 } == 150000
#guard wht.amount { kind := .services, amount := 1000000 } == 150000

end PyGlobal.Corporate
