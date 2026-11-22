import VnGlobal.Pit

/-!
# Viet Nam 2025: corporate income tax and foreign contractor tax (1200)

Luật Thuế TNDN 67/2025/QH15 (datafiles.chinhphu.vn signed PDF, OCR `vn/law/cit/vn_cit67_2025_ocr.txt`; session 12, A): art. 19 (1)
in force 1 Oct 2025 "và áp dụng từ kỳ tính thuế thu nhập doanh nghiệp năm 2025" (the whole 2025 tax period).
* **art. 10**: (1) 20 %; (2) 15 % for enterprises with total annual revenue not above VND 3 bn; (3) 17 % above 3 bn up
  to 50 bn; the revenue is that of the preceding tax period (the model reads the line's `turnover`; session 12 added the 17 % band).
* Foreign contractor tax (Circular 103/2014/TT-BTC): CIT portion 5 % on services and interest, 10 % on royalties;
  dividends to foreign companies 0 %.
-/

namespace VnGlobal.Corporate
open TaxKernel TaxKernel.Global

/-- Luật 67/2025/QH15 art. 10 (1)-(3): 15 % to VND 3 bn of annual revenue, 17 % to 50 bn, else 20 %. -/
def rateOf (co : Company) : Int :=
  if co.turnover ≤ 3000000000 then 1500 else if co.turnover ≤ 50000000000 then 1700 else 2000

def cit (co : Company) : CorpRegime :=
  { name := "Thuế thu nhập doanh nghiệp (corporate income tax)",
    sched := Schedule.flat (rateOf co) }

def citStatute : String := "Luật 67/2025/QH15 art. 10 (1)-(3), art. 19 (1)"

def wht : Wht :=
  { name := "Withholding tax on payments to non-residents", rules := [
      { kind := .dividend, toCompany := some true, rateBp := 0, statute := "Luật Thuế TNDN 67/2025/QH15 art. 4 (7): income shared from capital contributions or shares in domestic enterprises, after their CIT, is exempt (in force 1 Oct 2025, applies from the 2025 tax period, art. 19 (1))" },
      { kind := .dividend, toCompany := some false, rateBp := 500, statute := "PIT Law (VBHN 28/VBHN-VPQH, 2025) art. 27: investment income of non-resident individuals 5 %" },
      { kind := .interest, toCompany := some false, rateBp := 500, statute := "PIT Law (VBHN 28/VBHN-VPQH, 2025) art. 27 (5 %)" },
      { kind := .royalty, toCompany := some false, rateBp := 500, statute := "PIT Law (VBHN 28/VBHN-VPQH, 2025) art. 30 (1): 5 % (on the part above 10 m dong per contract)" },
      { kind := .interest, rateBp := 500, statute := "Circular 103/2014/TT-BTC art. 13" },
      { kind := .royalty, rateBp := 1000, statute := "Circular 103/2014 art. 13" },
      { kind := .services, rateBp := 500, statute := "Circular 103/2014 art. 13" }] }

def families : List Family :=
  [{ name := "1200 corporate income tax and withholding", covers := [.cit],
     run := fun _ g _ => if g.entity != .company then [] else
       [(cit g.company).citCharge g.company citStatute]
       ++ wht.charges g.company }]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  if g.entity != .company then [] else
  (if true then ["revenue test on the preceding tax period read from the line's turnover; incentive rates (art. 13: 10 %, 15 %, 17 %) and sector rates (art. 10 (4)) not modelled"] else [])

#guard wht.amount { kind := .interest, amount := 1000 } == 50
#guard wht.amount { kind := .royalty, amount := 1000 } == 100
#guard wht.amount { kind := .services, amount := 1000 } == 50
#guard wht.amount { kind := .dividend, amount := 1000, toCompany := false } == 50
#guard wht.amount { kind := .dividend, amount := 1000 } == 0
#guard (cit { profit := 1000000, turnover := 2000000000 }).citTax { profit := 1000000, turnover := 2000000000 } == 150000
#guard (cit { profit := 1000000, turnover := 5000000000 }).citTax { profit := 1000000, turnover := 5000000000 } == 170000
#guard (cit { profit := 1000000, turnover := 60000000000 }).citTax { profit := 1000000, turnover := 60000000000 } == 200000

end VnGlobal.Corporate
