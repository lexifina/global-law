import BrGlobal.Pit

/-!
# Brazil 2025: IRPJ and CSLL on lucro real (1200)

Sources: Lei 9.249/1995 (Planalto, archived 2025-07-02) and Lei 7.689/1988 (archived 2025-06-25), `br/law/`.
* **Lei 9.249 art. 3**: "A alíquota do imposto de renda das pessoas jurídicas é de quinze por cento"; § 1° the profit
  "que exceder a R$ 240.000,00 … sujeita-se à incidência de adicional de" ten per cent: 15 % + 10 % above R$ 240.000.
* **Lei 7.689 art. 3 III**: CSLL "9% (nove por cento), no caso das demais pessoas jurídicas".
* **Lei 9.249 art. 10**: dividends paid out of profits from 1996 are not subject to withholding (0 %).

**Pass 7 (2026-11-21), withholding on payments abroad:** IRRF on remittances abroad: interest 15 % (Lei 9.249 art. 28, the DL 5.844 art. 100 rate); royalties and technical services 15 % (MP 2.159-70 art. 3, with CIDE); other services 25 % (Lei 9.779 art. 7); 25 % for low-tax jurisdictions (Lei 9.779 art. 8). Dividends: Lei 9.249 art. 10 exempt in 2025 (Lei 15.270 of 26 Nov 2025 adds 10 % from 2026). Grade A.
-/

namespace BrGlobal.Corporate
open TaxKernel TaxKernel.Global AmerCommon BrGlobal

def regime : CorpRegime :=
  { name := "IRPJ", sched := Schedule.ofList [(0, 1500), (240000, 2500)] }

def citStatute : String := "Lei 9.249/1995 art. 3 (15 % + 10 % adicional above R$ 240.000)"

def wht : Wht :=
  { name := "Withholding tax (non-residents)", rules := [{ kind := .dividend, rateBp := 0, statute := "Lei 9.249/1995 art. 10 (wording in force in 2025; the 10 % of § 4 inserted by Lei 15.270/2025 applies from 1 Jan 2026, its art. 8)" }, { kind := .interest, rateBp := 1500, statute := "Lei 9.249/1995 art. 28 (DL 5.844/1943 art. 100): 15 %" }, { kind := .royalty, rateBp := 1500, statute := "MP 2.159-70/2001 art. 3: royalties 15 %" }, { kind := .services, rateBp := 2500, statute := "Lei 9.779/1999 art. 7 (Lei 13.315/2016): services 25 %" }] }

def citF : Family := corpFamily "1200 IRPJ" (fun _ => regime) (fun _ => citStatute) wht (fun g => [charge .cit "CSLL" g.company.profit pos (fun b => divR .down (900 * b) BP) (statute := "Lei 7.689/1988 art. 3 III (9 %)")])

def families : List Family := [citF]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  when (g.entity == .company) "losses brought forward, interest limitation and participation exemptions not modelled: taxable profit = profit + add-backs − exempt income"
  ++ when (g.entity == .company && strField g.raw "regime" != "") "1200 cit: the elected regime named in the entity (\"regime\") is not modelled (grade C for that regime): the model computes the general regime only"
  ++ when (g.entity == .company && !g.company.paymentsAbroad.isEmpty) "technical services at 15 % (MP 2.159-70 art. 3), the 25 % for low-tax jurisdictions (Lei 9.779 art. 8) and CIDE (Lei 10.168, 10 %) not modelled: services at the general 25 %"

#guard regime.citTax { profit := 1000000 } == 36000 + 190000
#guard wht.amount { kind := .dividend, amount := 1000000 } == 0
#guard wht.amount { kind := .interest, amount := 1000000 } == 150000
#guard wht.amount { kind := .royalty, amount := 1000000 } == 150000
#guard wht.amount { kind := .services, amount := 1000000 } == 250000

end BrGlobal.Corporate
