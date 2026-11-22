import TaxKernel.Global
import R5Common

/-!
# Georgia 2025: income tax on gifts and inheritances (4300)

Georgia has no separate inheritance or gift tax; property received by gift or inheritance is income of the natural
person (Tax Code art. 82(1) lists the exemptions; the rest is taxable income at **20 %**, art. 81(1)). Text read in the
team's git history of the matsne.gov.ge texts (lexifina/georgia-law, act 1043717, versions in force 1/12/2024,
2/1/2025, 30/12/2025 and 1/1/2026: art. 82(1)(ზ), (თ), (ი) and the heir orders the same text in all; art. 81(1) the same
line):
* art. 82(1)(ზ): the value of property received in the tax year by gift or inheritance by **first- and second-order
  heirs** is exempt;
* art. 82(1)(თ): property received by gift up to **GEL 1 000** in the tax year is exempt (not gifts from the employer);
* art. 82(1)(ი): property received by gift or inheritance by **third- and fourth-order heirs** is exempt up to
  **GEL 150 000** in the tax year;
* art. 82 (heir orders for gifts and inheritance by will): first order spouse, child, adopted child, grandchild and
  further descendants, parent, adoptive parent; second order sister, brother, their children and grandchildren; third
  order grandparents and their parents; fourth order uncles and aunts.
Classification: the charge falls on what each recipient receives and by his relation to the giver (Guide §52 features
of an inheritance tax); it is collected through the income tax, which is why the OECD tables would show it in 1100.
Model: per year, third/fourth-order receipts above GEL 150 000, gifts from others above GEL 1 000 and inheritances from
others are taxed at 20 %. Relations: spouse, child, grandchild, parent first order; sibling, niece or nephew second;
`otherRelative` read as a third/fourth-order heir (grandparent, uncle, aunt); everyone else outside the heir orders.
Grade A (statute text read).
-/

namespace GeGlobal
open TaxKernel TaxKernel.Global R5Common

def heirOrder12 (r : Relation) : Bool :=
  r == .spouse || r == .child || r == .grandchild || r == .parent || r == .sibling || r == .nieceNephew
def heirOrder34 (r : Relation) : Bool := r == .otherRelative

def giftRateBp : Int := 2000
def order34Free : Int := 150000
def giftFree : Int := 1000

def sumOf (ts : List Transfer) : Int := (ts.map fun t => pos t.statutoryValue).foldl (· + ·) 0

def wealth : Family :=
  { name := "4300 საშემოსავლო გადასახადი (ჩუქება, მემკვიდრეობა)", covers := [.estate],
    run := fun _ g _ =>
      let ts := g.transfers
      let o34 := ts.filter fun t => heirOrder34 t.relation
      let og := ts.filter fun t => !heirOrder12 t.relation && !heirOrder34 t.relation && t.kind == .gift
      let oi := ts.filter fun t => !heirOrder12 t.relation && !heirOrder34 t.relation && t.kind == .inheritance
      let mk (nm : String) (xs : List Transfer) (free : Int) (st : String) : List Charge :=
        if xs.isEmpty then [] else
          [charge .estate nm (sumOf xs) (fun v => max 0 (v - free)) (fun b => b * giftRateBp / 10000)
            (event := "2025") (statute := st)]
      mk "income tax: gifts and inheritances from third- and fourth-order heirs" o34 order34Free
          "Tax Code art. 82(1)(ი) (GEL 150 000 a year exempt), art. 81(1) (20 %)" ++
      mk "income tax: gifts from others" og giftFree "Tax Code art. 82(1)(თ) (GEL 1 000 a year exempt), art. 81(1) (20 %)" ++
      mk "income tax: inheritances from others" oi 0 "Tax Code art. 82(1), art. 81(1) (20 %)" }

def wealthUnsupported (g : CanonGlobal) : List String :=
  (if g.transfers.any (fun t => t.relation == .otherRelative) then
    ["income tax on gifts: 'otherRelative' read as a third- or fourth-order heir (grandparent, uncle, aunt: GEL 150 000 exempt); a cousin is outside the heir orders"] else []) ++
  (if g.transfers.any (fun t => t.kind == .gift && t.relation == .unrelated) then
    ["income tax on gifts: a gift from the employer gets no GEL 1 000 exemption (art. 82(1)(თ)); the record does not say who gave"] else [])

#guard giftRateBp * (250000 - order34Free) / 10000 == 20000
#guard heirOrder12 .nieceNephew && !heirOrder12 .otherRelative

end GeGlobal
