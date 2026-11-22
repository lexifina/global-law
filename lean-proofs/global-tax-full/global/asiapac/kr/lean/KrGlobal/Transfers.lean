import KrGlobal.Pit

/-!
# Korea 2025: inheritance and gift tax (4300)
상속세 및 증여세법 (`kr/law/lawgo/상속세및증여세법_20260102.txt`):
* art. 26: 1억 이하 10 %; 5억 이하 20 %; 10억 이하 30 %; 30억 이하 40 %; above 50 % (art. 56: gifts, same table).
* art. 21 (1): lump-sum deduction 5억; art. 19 (4): spouse at least 5억 (spouse: 10억 in all).
* art. 53 (<개정 … 2025. 3. 14.>): gifts from a spouse 6억, from lineal ascendants 5천만 (minors 2천만), from lineal
  descendants 5천만, other relatives 1천만, over 10 years (the look-back).

FT review (2026-11-21, third pass). **art. 19 (1)**: "배우자가 실제 상속받은 금액의 경우 다음 각 호의 금액 중 작은 금액을 한도로
… 공제한다 … 1. 다음 계산식에 따라 계산한 한도금액 [the legal-share limit] 2. 30억원"; **(4)**: "실제 상속받은 금액이 없거나 …
5억원 미만이면 … 5억원을 공제한다". The spouse's deduction is the amount received, at least 5억 and at most 30억, on top of
the art. 21 lump sum 5억: for a spouse acquirer the deductions reach 35억 (the class allowance: below 30억 the deduction
covers the whole amount). The legal-share limit (1호, 민법 1009) needs the co-heirs, which the entity does not state, and
art. 19 (2) needs the division registered by its deadline: both taken as met (listed). **art. 69 (1), (2)** (3 % 신고세액공제)
is granted only when the return is filed under art. 67 / 68: not applied (a filing fact, not in the entity).
-/

namespace KrGlobal.Transfers
open TaxKernel TaxKernel.Global

def rates : Schedule := Schedule.ofList [(0, 1000), (100000000, 2000), (500000000, 3000), (1000000000, 4000), (3000000000, 5000)]
def inh : InheritanceTax :=
  { name := "상속세", exemptRelations := [.charity], classOf := fun r => if r == .spouse then 1 else 0,
    classes := [{ allowance := 500000000, sched := rates }, { allowance := 3500000000, sched := rates }] }
def gift : InheritanceTax :=
  { name := "증여세", exemptRelations := [.charity], lookbackYears := 10,
    classOf := fun r => match r with | .spouse => 0 | .child | .grandchild | .parent => 1 | .unrelated => 3 | _ => 2,
    classes := [{ allowance := 600000000, sched := rates }, { allowance := 50000000, sched := rates },
                { allowance := 10000000, sched := rates }, { allowance := 0, sched := rates }] }
def inhF : Family :=
  { name := "4300 상속세·증여세", covers := [.estate],
    run := fun _ g _ => inh.charges (g.transfers.filter (·.kind == .inheritance)) "상증법 arts. 19, 21, 26"
      ++ gift.charges (g.transfers.filter (·.kind == .gift)) "상증법 arts. 53, 56" }

def families : List Family := [inhF]

def absent : List Absent :=
  [{ oecd := .wealth, why := "No net wealth tax (종합부동산세 is a property tax, 4100); grade B" }]

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  (if g.transfers.any (fun t => t.kind == .inheritance) then ["inheritance tax per acquirer on the acquirer's value (the estate-based total and shares, financial-asset and cohabiting-home deductions not modelled)"] else [])
  ++ (if g.transfers.any (fun t => t.relation == .grandchild) then ["generation-skipping surcharge (art. 27, 57: 30 %/40 %) and minors' 2천만 deduction not modelled"] else [])
  ++ (if g.transfers.any (fun t => t.kind == .inheritance && t.relation == .spouse) then ["spouse deduction (art. 19 (1)): the amount received, 5억 to 30억; the legal-share limit (co-heirs not in the entity) and the art. 19 (2) division deadline taken as met"] else [])
  ++ (if !g.transfers.isEmpty then ["신고세액공제 3 % (art. 69) not applied: it needs a return filed by the art. 67 / 68 deadline"] else [])

#guard (inhF.run [] { id := "t", household := { id := "t" }, transfers := [{ kind := .inheritance, value := 1500000000, relation := .child }] } []).map (·.due) == [240000000]
#guard (inhF.run [] { id := "t", household := { id := "t" }, transfers := [{ kind := .gift, value := 150000000, relation := .child }] } []).map (·.due) == [10000000]
-- spouse inherits 50억: deductions 5억 + 30억; 15억 taxed: 2.4억 + 5억 x 40 % = 4.4억
#guard (inhF.run [] { id := "t", household := { id := "t" }, transfers := [{ kind := .inheritance, value := 5000000000, relation := .spouse }] } []).map (·.due) == [440000000]

end KrGlobal.Transfers
