import UsGlobal.Pit

/-!
# United States 2025: federal corporate income tax and withholding on foreign persons (1200)

Source: 26 U.S.C. (Cornell LII, current Code; `us/law/usc26_11.txt`, `usc26_881.txt`, `usc26_1442.txt`).
* **§ 11 (b)**: "The amount of the tax imposed by subsection (a) shall be 21 percent of taxable income."
* **§ 881 (a)**: "a tax of 30 percent of the amount received from sources within the United States by a foreign
  corporation" as interest, dividends, rents, royalties and other FDAP income; § 1442 makes the payer withhold it.
  Portfolio interest (§ 881 (c)) is exempt: flagged. California franchise tax (R&TC § 23151) not read.

**Pass 7 (2026-11-21), withholding on payments abroad:** services: a payment abroad for services is taken as for services performed outside the US: § 862 (a) (3) makes it foreign-source and § 881 (a) / § 1442 reach only US-source amounts: a cited 0 (services performed in the US: 30 %, flagged).

**FT review (2026-11-21, third pass): net operating losses.** 26 U.S.C. § 172 (Cornell LII, fetched 2026-11-21,
`us/law/usc26_172.txt`) (a) (2): for a taxable year beginning after December 31, 2020 the deduction is "(A) the
aggregate amount of net operating losses arising in taxable years beginning before January 1, 2018 ... plus (B) the
lesser of— (i) the aggregate amount of net operating losses arising in taxable years beginning after December 31, 2017
... or (ii) 80 percent of the excess (if any) of— (I) taxable income computed without regard to the deductions under
this section and sections 199A and 250, over (II) the amount determined under subparagraph (A)." The entity's
`lossesForward` are read as post-2017 losses (the pre-2018 kind, unlimited, flagged).
-/

namespace UsGlobal.Corporate
open TaxKernel TaxKernel.Global AmerCommon UsGlobal

def regime : CorpRegime :=
  { name := "Federal corporate income tax", sched := Schedule.flat 2100, lossFull := 0, lossExcessBp := 8000 }

def citStatute : String := "26 U.S.C. § 11 (b): 21 %; § 172 (a) (2) (B) (NOL deduction at most 80 % of taxable income)"

def wht : Wht :=
  { name := "Withholding tax (non-residents)", rules := [{ kind := .dividend, rateBp := 3000, statute := "26 U.S.C. §§ 881 (a), 1442: 30 %" }, { kind := .royalty, rateBp := 3000, statute := "26 U.S.C. §§ 881 (a), 1442: 30 %" }, { kind := .interest, rateBp := 3000, statute := "26 U.S.C. §§ 881 (a), 1442: 30 % (portfolio interest exempt, § 881 (c): not modelled)" }, { kind := .services, rateBp := 0, statute := "26 U.S.C. § 862 (a) (3): compensation for services performed without the United States is foreign-source; § 881 (a) taxes US-source amounts only: none withheld" }] }

def citF : Family := corpFamily "1200 Federal corporate income tax" (fun _ => regime) (fun _ => citStatute) wht (fun _ => [])

def families : List Family := [citF]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  when (g.entity == .company) "interest limitation and participation exemptions not modelled: taxable profit = profit + add-backs − exempt income"
  ++ when (g.entity == .company) "California franchise tax (R&TC § 23151, 8.84 %) and the corporate AMT (§ 55, 15 % of adjusted financial statement income above $1 billion) not modelled"
  ++ when (g.entity == .company && !g.company.paymentsAbroad.isEmpty) "services performed in the United States by the foreign recipient (30 %, §§ 881 (a), 1442) not distinguished: payments abroad for services taken as performed abroad"
  ++ when (g.entity == .company && g.company.lossesForward > 0) "losses brought forward read as post-2017 NOLs (§ 172 (a) (2) (B): 80 % limit); pre-2018 NOLs (unlimited) not separated"

#guard regime.citTax { profit := 1000000 } == 210000
#guard wht.amount { kind := .dividend, amount := 1000000 } == 300000
#guard wht.amount { kind := .royalty, amount := 1000000 } == 300000
#guard wht.amount { kind := .interest, amount := 1000000 } == 300000
#guard wht.amount { kind := .services, amount := 1000000 } == 0
#guard regime.citTax { profit := 1000000, lossesForward := 5000000 } == 42000
#guard regime.citTax { profit := 1000000, lossesForward := 500000 } == 105000

end UsGlobal.Corporate
