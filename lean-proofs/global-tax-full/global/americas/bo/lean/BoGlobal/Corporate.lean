import BoGlobal.Pit

/-!
# Bolivia 2025: IUE and IUE beneficiarios del exterior (1200)

Source: Ley 843 T.O. actualizado al 30/09/2023 (`world/.../bo/src/l843_0923.txt`): grade B.
* **art. 50**: "Las empresas … veinticinco por ciento (25%)".
* **art. 51**: payments to "beneficiarios del exterior": the net income is presumed "equivalente al 50%" of the amount,
  withheld at "la tasa del 25%": 12.5 % of the payment.
-/

namespace BoGlobal.Corporate
open TaxKernel TaxKernel.Global AmerCommon BoGlobal

def regime : CorpRegime :=
  { name := "Impuesto sobre las Utilidades de las Empresas (IUE)", sched := Schedule.flat 2500 }

def citStatute : String := "Ley 843 art. 50 (25 %)"

def wht : Wht :=
  { name := "Withholding tax (non-residents)", rules := [{ kind := .dividend, rateBp := 1250, statute := "Ley 843 art. 51 (25 % of a presumed 50 %)" }, { kind := .interest, rateBp := 1250, statute := "Ley 843 art. 51 (25 % of a presumed 50 %)" }, { kind := .royalty, rateBp := 1250, statute := "Ley 843 art. 51 (25 % of a presumed 50 %)" }, { kind := .services, rateBp := 1250, statute := "Ley 843 art. 51 (25 % of a presumed 50 %)" }] }

def citF : Family := corpFamily "1200 Impuesto sobre las Utilidades de las Empresas (IUE)" (fun _ => regime) (fun _ => citStatute) wht (fun _ => [])

def families : List Family := [citF]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  when (g.entity == .company) "losses brought forward, interest limitation and participation exemptions not modelled: taxable profit = profit + add-backs − exempt income"
  ++ when (g.entity == .company) "the IUE additional 25 % on extractive activities and the AA-IUE financial surcharge not modelled"
  ++ when (g.entity == .company && g.company.paymentsAbroad.any (fun p => p.kind == .interest || p.kind == .royalty || p.kind == .services || p.kind == .dividend)) "payments abroad of a kind without a rule read get no withholding"

#guard regime.citTax { profit := 1000000 } == 250000
#guard wht.amount { kind := .dividend, amount := 1000000 } == 125000
#guard wht.amount { kind := .interest, amount := 1000000 } == 125000
#guard wht.amount { kind := .royalty, amount := 1000000 } == 125000
#guard wht.amount { kind := .services, amount := 1000000 } == 125000

end BoGlobal.Corporate
