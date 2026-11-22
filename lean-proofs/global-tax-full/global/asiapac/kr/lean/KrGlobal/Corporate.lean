import KrGlobal.Pit

/-!
# Korea 2025: corporate income tax, local income tax on corporations, withholding on foreign corporations (1200)

Source: 법인세법 from law.go.kr (current text, `kr/law/lawgo/법인세법_20260701.txt`), dated by the article notes.
* **art. 55 (1)** (<개정 2024. 12. 31., 2025. 12. 23.>): the 2025 table (2024.12.31 wording; the 2025.12.23 amendment
  raises the rates by one point for years beginning 2026-01-01): ≤ 2억 9 %; ≤ 200억 19 %; ≤ 3,000억 21 %; above 24 %.
  The table itself is an image in the current text: grade B.
* **지방세법 art. 103-20**: local income tax on corporations, one tenth of those rates (0.9/1.9/2.1/2.4 %), modelled as a
  separate charge on the same base.
* **art. 98 (1)** (<개정 … 2019. 12. 31.>): interest 20 % (bonds 14 %), dividends 20 %, personal services 20 %,
  royalties 20 % of the amount paid to a foreign corporation.

**Session 10: the 2025 texts.** 법인세법 as in force on 2025-07-01 (law.go.kr lsiSeq 267551, Law No. 20613 of 2024-12-31,
`kr/law/lawgo/법인세법_20250701_267551.txt`): art. 55 (1) 1 table ≤ 2억 9 %, to 200억 19 %, to 3,000억 21 %, above 24 %
(1,800만 + 19 % over 2억; 37억 8천만 + 21 % over 200억; 625억 8천만 + 24 % over 3,000억). 지방세법 as in force on
2025-01-01 (lsiSeq 268065, Law No. 20630): art. 103-20 (1) 1 the same brackets at 9 / 19 / 21 / 24 per 1,000. The later
2025 versions (2025-10-01, Law 21065, Government Organization Act) do not amend these articles.
-/

namespace KrGlobal.Corporate
open TaxKernel TaxKernel.Global

def cit : CorpRegime :=
  { name := "법인세 (corporate income tax)",
    sched := Schedule.ofList [(0, 900), (200000000, 1900), (20000000000, 2100), (300000000000, 2400)] }

def citStatute : String := "법인세법 제55조 ① 1. (2025 version, Law 20613)"

def wht : Wht :=
  { name := "Withholding tax on payments to non-residents", rules := [
      { kind := .dividend, rateBp := 2000, statute := "법인세법 98 (1) 2" },
      { kind := .royalty, rateBp := 2000, statute := "법인세법 98 (1) 6" },
      { kind := .services, rateBp := 2000, statute := "법인세법 98 (1) 4" },
      { kind := .interest, rateBp := 2000, statute := "법인세법 98 (1) 1 나 (bonds 14 %: 가)" }] }

/-- 지방세법 art. 103-20: local income tax on corporations, one tenth of the 법인세법 art. 55 rates, same base. -/
def localIncome (co : Company) : Charge :=
  let b := cit.taxableProfit co
  charge .cit "법인지방소득세 (local income tax)" b id (fun x => (Schedule.ofList [(0, 90), (200000000, 190), (20000000000, 210), (300000000000, 240)]).tax {} x) (level := .local) (statute := "지방세법 art. 103-20 (2025 rates)")

def families : List Family :=
  [{ name := "1200 corporate income tax and withholding", covers := [.cit],
     run := fun _ g _ => if g.entity != .company then [] else
       [cit.citCharge g.company citStatute]
       ++ wht.charges g.company
       ++ [localIncome g.company] }]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  if g.entity != .company then [] else
  (if true then ["minimum tax (조특법 132), the land-gain surtax (art. 55-2) and the 투자ㆍ상생 surtax (조특법 100-32) not modelled"] else [])
  ++ (if !g.company.paymentsAbroad.isEmpty then ["bond interest 14 % (art. 98 (1) 1 가) and the 10 % local income tax withheld on top (지방세법 103-52) not modelled"] else [])

#guard cit.citTax { profit := 1000000000 } == 170000000
#guard cit.citTax { profit := 1000000000 } == 170000000
#guard (localIncome { profit := 1000000000 }).due == 17000000
#guard wht.amount { kind := .dividend, amount := 1000 } == 200
#guard wht.amount { kind := .royalty, amount := 1000 } == 200
#guard wht.amount { kind := .services, amount := 1000 } == 200
#guard wht.amount { kind := .interest, amount := 1000 } == 200

end KrGlobal.Corporate
