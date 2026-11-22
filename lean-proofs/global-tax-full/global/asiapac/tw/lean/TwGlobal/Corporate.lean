import TwGlobal.Pit

/-!
# Taiwan 2025: profit-seeking enterprise income tax, withholding on non-residents (1200)

Source: 所得稅法 from law.moj.gov.tw (current text, last amended 2026-09-11; art. 5 last amended 2018-02-07, history
page checked): `tw/law/moj/ita_current.txt`.
* **art. 5 (5)**: taxable income ≤ 120,000 exempt; above, 20 % of the whole, "但其應納稅額不得超過營利事業課稅所得額超過
  十二萬元部分之半數" (item 3: 2018-2019 only).
* **art. 66-9**: 5 % on undistributed earnings (not modelled).
* Withholding: **art. 88** + 各類所得扣繳率標準 (dividends 21 %, interest 20 %, royalties 20 %, services 20 % to
  non-residents)

**Session 12 (registry sample), withholding grade A.** 各類所得扣繳率標準 (law.moj.gov.tw pcode G0340028, current text,
修正日期 民國110 = 2021, so in force throughout 2025; `tw/law/moj12/wht.html`) art. 3: non-resident individuals and enterprises
without a fixed place of business: 1 dividends 21 %; 4 (五) other interest 20 % (15 % on bills, securitisation, bonds:
not distinguished); 6 royalties 20 %; 8 professional fees 20 %; 10 other income of a foreign enterprise 20 %.
-/

namespace TwGlobal.Corporate
open TaxKernel TaxKernel.Global

def wht : Wht :=
  { name := "Withholding tax on payments to non-residents", rules := [
      { kind := .dividend, rateBp := 2100, statute := "所得稅法 88; 各類所得扣繳率標準 3 (1) (21 %)" },
      { kind := .interest, rateBp := 2000, statute := "各類所得扣繳率標準 3 (4) (五) (20 %)" },
      { kind := .royalty, rateBp := 2000, statute := "各類所得扣繳率標準 3 (6) (20 %)" },
      { kind := .services, rateBp := 2000, statute := "各類所得扣繳率標準 3 (8), (10) (20 %)" }] }

def cit : CorpRegime := { name := "營利事業所得稅", sched := Schedule.flat 2000 }
/-- art. 5 (5) 1-2: nothing up to 120,000; above, 20 % of the whole but at most half of the excess over 120,000. -/
def twTax (x : Int) : Int := if x ≤ 120000 then 0 else min (divR .down (2000 * x) BP) ((x - 120000) / 2)
def citTw (co : Company) : Charge :=
  charge .cit "營利事業所得稅" (cit.beforeLosses co) (fun _ => cit.taxableProfit co) twTax (statute := "所得稅法 art. 5 (5) (as amended 2018-02-07)")

def families : List Family :=
  [{ name := "1200 corporate income tax and withholding", covers := [.cit],
     run := fun _ g _ => if g.entity != .company then [] else
       wht.charges g.company
       ++ [citTw g.company] }]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  if g.entity != .company then [] else
  (if true then ["art. 66-9 5 % surtax on undistributed earnings and the alternative minimum tax (所得基本稅額條例) not modelled"] else [])

#guard twTax 120000 == 0
#guard twTax 150000 == 15000
#guard twTax 1000000 == 200000
#guard wht.amount { kind := .dividend, amount := 1000 } == 210
#guard wht.amount { kind := .interest, amount := 1000 } == 200
#guard wht.amount { kind := .royalty, amount := 1000 } == 200
#guard wht.amount { kind := .services, amount := 1000 } == 200

end TwGlobal.Corporate
