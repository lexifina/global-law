import MnGlobal.Pit

/-!
# Mongolia 2025: corporate income tax and withholding on non-residents (1200)

Аж ахуйн нэгжийн орлогын албан татварын тухай хууль (2019-03-22): text not fetched (legalinfo.mn); rates from the
registry's official-portal reading (B).
* **art. 20.1**: 10 % of taxable income up to MNT 6 bn, 25 % above.
* **art. 20.2**: non-residents' Mongolian-source dividends, interest, royalties and services 20 %.

Gap-closing session: the law's consolidated text on legalinfo.mn (lawId=14407), read in lexifina/mongolia-law
`law/2019/14407` (current text of 2026-10-28 with amendment notes):
* **art. 20.2.7** (no amendment note: the 2019 text): notwithstanding 20.1, a taxpayer whose income subject to tax under
  18.2-18.5 for the year is up to MNT 300 m, outside the sectors of 22.1.1-22.1.3, is taxed at 1 % of its taxable income.
* **art. 22.1**: a taxpayer whose income subject to tax is not above MNT 1.5 bn (2.5 bn only from 1 January 2027 by the law
  of 2026-06-26), outside mining (22.1.1), alcohol and tobacco (22.1.2) and petroleum products and fuel (22.1.3), gets 90 % of
  the 20.1 tax refunded on its annual return (22.2): 1 % of taxable income in effect. Modelled together: income subject to
  tax (the line's `turnover`) above 0 and up to 1.5 bn and no excluded sector (`company.sector` or `flags`) -> 1 %.
* **art. 20.1** in 2025: 10 % to MNT 6 bn, 25 % above (the consolidated text shows the 10/15/25 % bands that apply from
  1 January 2027; the 2025 wording is not in the repository: B).
Related-party aggregation (22.3) is not applied.
-/

namespace MnGlobal.Corporate
open TaxKernel TaxKernel.Global

def wht : Wht :=
  { name := "Withholding tax on payments to non-residents", rules := [
      { kind := .dividend, rateBp := 2000, statute := "CIT law art. 20.2" },
      { kind := .interest, rateBp := 2000, statute := "art. 20.2" },
      { kind := .royalty, rateBp := 2000, statute := "art. 20.2" },
      { kind := .services, rateBp := 2000, statute := "art. 20.2" }] }

/-- `company.sector` (string or array) and `flags` of the input line. -/
def sectorsOf (g : CanonGlobal) : List String :=
  (match (g.raw.getObjValD "company").getObjValD "sector" with
   | Lean.Json.str s => [s]
   | Lean.Json.arr a => a.toList.filterMap fun j => match j with | Lean.Json.str s => some s | _ => none
   | _ => []) ++ g.company.flags
/-- CIT law art. 22.1.1-22.1.3: mining, alcohol and tobacco, petroleum products and fuel. -/
def excludedSectors : List String := ["mining", "petroleum", "fuel", "alcohol", "tobacco"]
/-- art. 20.2.7, 22.1 (2025: limit MNT 1.5 bn): small entities pay 1 % of taxable income. -/
def smallEntity (g : CanonGlobal) : Bool :=
  decide (0 < g.company.turnover) && decide (g.company.turnover ≤ 1500000000) && !(sectorsOf g).any (fun s => excludedSectors.contains s)
def cit (small : Bool) : CorpRegime :=
  { name := "Corporate income tax",
    sched := if small then Schedule.flat 100 else Schedule.ofList [(0, 1000), (6000000000, 2500)] }
def citStatuteOf (small : Bool) : String :=
  if small then "CIT law (2019) art. 20.2.7, 22.1 (income subject to tax not above MNT 1.5 bn: 1 % of taxable income)" else "CIT law (2019) art. 20.1"

def families : List Family :=
  [{ name := "1200 corporate income tax and withholding", covers := [.cit],
     run := fun _ g _ => if g.entity != .company then [] else
       wht.charges g.company
       ++ [(cit (smallEntity g)).citCharge g.company (citStatuteOf (smallEntity g))] }]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  if g.entity != .company then [] else
  (if g.company.turnover ≤ 0 then ["turnover (income subject to tax) not given: the 1 % regime for small entities (CIT law art. 20.2.7, 22.1: up to MNT 1.5 bn) not tested, art. 20.1 applied"] else [])
  ++ (if true then ["related-party aggregation of the small-entity limit (art. 22.3) not applied"] else [])

#guard wht.amount { kind := .dividend, amount := 1000 } == 200
#guard wht.amount { kind := .interest, amount := 1000 } == 200
#guard wht.amount { kind := .royalty, amount := 1000 } == 200
#guard wht.amount { kind := .services, amount := 1000 } == 200
#guard (cit false).citTax { profit := 7000000000 } == 850000000
#guard (cit true).citTax { profit := 100000000 } == 1000000
#guard smallEntity { id := "t", household := { id := "t" }, company := { profit := 100000000, turnover := 1500000000 } } == true
#guard smallEntity { id := "t", household := { id := "t" }, company := { profit := 100000000, turnover := 1500000001 } } == false
#guard smallEntity { id := "t", household := { id := "t" }, company := { profit := 100000000, turnover := 900000000, flags := ["mining"] } } == false

end MnGlobal.Corporate
