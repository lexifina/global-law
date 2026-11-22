import UaGlobal.Pit

/-!
# UA 2025: Податок на додану вартість (5111); excises not modelled in this pass

Source: Податковий кодекс України (2755-VI), zakon.rada.gov.ua (official) as captured by the Internet Archive on 2025-06-20 (`ua/law/ptk_wb20250620.txt`, copied from the 1.x model's law folder); sha256 in `law/SHA256SUMS`.
* 193.1: "а) 20 відсотків; б) 0 відсотків; в) 7 відсотків по операціях з: постачання ... лікарських засобів ...; постачання послуг із тимчасового розміщування (проживання), що надаються готелями"
* 181.1: registration when supplies "перевищує 1000000 гривень (без урахування податку на додану вартість)"
-/

namespace UaGlobal.Consumption
open TaxKernel TaxKernel.Global

def vat : Vat :=
  { name := "Податок на додану вартість", standard := 2000, superReduced := 700, threshold := 1000000,
    classOf := fun gd => match gd with
      | .medicines | .hotels => .superReduced
      | .health | .education | .financial | .insurance => .exempt
      | _ => .standard }

def vatStatute : String := "Податковий кодекс ст. 193.1 (20 %, 0 %, 7 %, 14 %); ст. 196-197 (звільнення); ст. 181.1 (1000000 гривень)"

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "5111 Податок на додану вартість", covers := [.vat],
     run := fun args g prev =>
       (if g.consumption.isEmpty then [] else [vat.basketCharge g.consumption vatStatute])
       ++ (if g.entity == .company && !g.company.sales.isEmpty then [vat.businessCharge g.company vatStatute] else []) }]

def absent : List Absent :=
  []

def notes : List String := ["UA 5111: zakon.rada.gov.ua via Internet Archive 2025-06-20"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if g.consumption.any (fun s => s.good == .petrol || s.good == .diesel || s.good == .cigarettes || s.good == .beer || s.good == .wine || s.good == .spirits) then ["excise (Податковий кодекс розділ VI (акцизний податок, ст. 215.3: multi-year rate tables, not extracted in this pass)) not modelled in this pass"] else [])

#guard vat.embedded { good := .clothing, amount := 12000 } == 2000
#guard vat.embedded { good := .medicines, amount := 10700 } == 700
#guard vat.net { turnover := 1000000, sales := [{ good := .other, net := 1000000 }] } == 0

end UaGlobal.Consumption
