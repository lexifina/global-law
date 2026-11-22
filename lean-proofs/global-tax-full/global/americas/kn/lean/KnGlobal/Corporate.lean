import KnGlobal.Pit

/-!
# Saint Kitts and Nevis 2025: corporation tax (1200)

Source: Income Tax Act Cap. 20.22, Revised Laws revision date 31 Dec 2017 (1.x builder's copy
`world/B15-no-pit/kn/law/ita_ch20_22_2017.txt`): "(b) in respect of a company there shall be charged, levied and
collected corporation tax of 33% in respect of income ... earned thereafter in subsequent years" (Substituted by Act 5
of 2013). The Income Tax (Amendment) Act No. 12 of 2021 (also held) changes residence and permanent establishment only.
Amending Acts of 2018-2020 and 2022-2025 were not checked, and the IRD corporate income tax page (sknird.com,
`kn/law/ird_cit.txt`, fetched 2026-11-21) states no rate: grade B. Withholding on payments to non-residents not read.

**Pass 7 (2026-11-21), withholding on payments abroad:** Income Tax Act Cap. 20.22 s. 36 (1) (words substituted and paras inserted by Act 2 of 2016): a resident who pays a non-resident (a) a dividend, (b) interest, (c) royalty payments, (e) commissions, fees, (f) charges for personal services, commercial advice, managerial skills, (i) technical, professional and other service fees ... withholds 15 % of the amount paid. Grade A (Revised Edition 2017; later Acts other than No. 12 of 2021 not checked).
-/

namespace KnGlobal.Corporate
open TaxKernel TaxKernel.Global AmerCommon KnGlobal

def regime : CorpRegime :=
  { name := "Corporation tax", sched := Schedule.flat 3300 }

def citStatute : String := "Income Tax Act Cap. 20.22 s. 32 (1) (b) (Act 5 of 2013): 'corporation tax of 33%'"

def wht : Wht :=
  { name := "Withholding tax (non-residents)", rules := [{ kind := .dividend, rateBp := 1500, statute := "ITA Cap. 20.22 s. 36 (1) (Act 2 of 2016): 15 % of the amount paid to a non-resident" }, { kind := .interest, rateBp := 1500, statute := "ITA Cap. 20.22 s. 36 (1) (Act 2 of 2016): 15 % of the amount paid to a non-resident" }, { kind := .royalty, rateBp := 1500, statute := "ITA Cap. 20.22 s. 36 (1) (Act 2 of 2016): 15 % of the amount paid to a non-resident" }, { kind := .services, rateBp := 1500, statute := "ITA Cap. 20.22 s. 36 (1) (Act 2 of 2016): 15 % of the amount paid to a non-resident" }] }

def citF : Family := corpFamily "1200 Corporation tax" (fun _ => regime) (fun _ => citStatute) wht (fun _ => [])

def families : List Family := [citF]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  when (g.entity == .company) "losses brought forward, interest limitation and participation exemptions not modelled: taxable profit = profit + add-backs − exempt income"
  ++ when (g.entity == .company && !g.company.paymentsAbroad.isEmpty) "amending Acts after 2017 (other than No. 12 of 2021) not checked for s. 36"

#guard regime.citTax { profit := 1000000 } == 330000
#guard wht.amount { kind := .dividend, amount := 1000000 } == 150000
#guard wht.amount { kind := .interest, amount := 1000000 } == 150000
#guard wht.amount { kind := .royalty, amount := 1000000 } == 150000
#guard wht.amount { kind := .services, amount := 1000000 } == 150000

end KnGlobal.Corporate
