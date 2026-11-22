import JpGlobal.Pit

/-!
# Japan 2025: corporation tax, local corporation tax, withholding on non-residents (1200)

Sources: e-Gov API v2, asof 2025-07-01 (`jp/law/egov/hojinzei_2025-07-01.*`, `chihohojinzei_…`, `shotokuzei_…`, `fukko_…`).
* **法人税法 art. 66 (1)**: ordinary corporations "百分の二十三・二の税率"; **(2)**: capital ≤ 1億円, the first 8 m yen of
  income "百分の十九"; **租特 art. 42-3-2**: that 19 % read as 15 % for years beginning by 2027-03-31 (flag `sme`).
* **地方法人税法 art. 10 (1)**: "課税標準法人税額に百分の十・三の税率" (10.3 % of the corporation tax).
* **所得税法 arts. 212 (1), 213 (1) 1**: 20 % on domestic-source income paid to non-residents and foreign corporations;
  **復興財源確保法 art. 28**: special reconstruction income tax 2.1 % of that tax (to 2037): 20.42 %.
## FT review (2026-11-21, third pass): truncation of the base and of the tax
e-Gov API v2, 国税通則法 (昭和37年法律第66号) asof 2025-07-01 (`jp/law/egov/tsusokuho_2025-07-01.*`):
* **art. 118 (1)**: "国税（印紙税及び附帯税を除く。…）の課税標準 … を計算する場合において、その額に千円未満の端数があるとき、
  又はその全額が千円未満であるときは、その端数金額又はその全額を切り捨てる" (the base to 1,000 yen);
* **art. 119 (1)**: "国税（自動車重量税、印紙税及び附帯税を除く。…）の確定金額に百円未満の端数があるとき、又はその全額が百円未満
  であるときは、その端数金額又はその全額を切り捨てる" (the tax to 100 yen).
法人税 (base: 所得の金額) and 地方法人税 (base: 課税標準法人税額, art. 9 of its act) are both 国税 under these articles.
The withholding charges keep 1-yen amounts (art. 119 (2) with 施行令 art. 40: not changed here).
-/

namespace JpGlobal.Corporate
open TaxKernel TaxKernel.Global

def wht : Wht :=
  { name := "Withholding tax on payments to non-residents", rules := [
      { kind := .dividend, rateBp := 2042, statute := "所得税法 213 (1) 1 (20 %) + 復興財源確保法 28 (2.1 % of it)" },
      { kind := .royalty, rateBp := 2042, statute := "所得税法 161 (1) 11, 213 (1) 1 + 復興 28" },
      { kind := .services, rateBp := 2042, statute := "所得税法 161 (1) 6, 213 (1) 1 + 復興 28" },
      { kind := .interest, rateBp := 2042, statute := "所得税法 161 (1) 10 (loan interest), 213 (1) 1 (20 %) + 復興財源確保法 28 (2.1 % of it)" }] }

def cit : CorpRegime := { name := "法人税 (corporation tax)", sched := Schedule.flat 2320 }
def citSme : CorpRegime := { name := "法人税 (中小法人)", sched := Schedule.ofList [(0, 1500), (8000000, 2320)] }
def citOf (co : Company) : CorpRegime := if co.flags.contains "sme" then citSme else cit
def citStatute : String := "法人税法 (昭和40年法律第34号) art. 66 (1)-(2) (e-Gov revision 20250620, asof 2025-07-01); 租税特別措置法 art. 42-3-2 (15 % on the first 8 m yen, years beginning by 2027-03-31)"
/-- 国税通則法 art. 118 (1): a national tax's base is truncated to 1,000 yen; art. 119 (1): the tax to 100 yen. -/
def base1000 (x : Int) : Int := (Rule.downTo 1000).apply x
def citTaxJ (co : Company) : Int := (citOf co).sched.tax (Rule.downTo 100) (base1000 ((citOf co).taxableProfit co))
def citChargeJ (co : Company) : Charge :=
  charge .cit (citOf co).name ((citOf co).beforeLosses co) (fun _ => base1000 ((citOf co).taxableProfit co)) (fun _ => citTaxJ co)
    (statute := citStatute ++ "; 国税通則法 art. 118 (1) (base: 1,000 円未満切捨て), 119 (1) (tax: 100 円未満切捨て)")
/-- 地方法人税法 art. 10 (1): 10.3 % of the corporation tax (base and tax truncated, 国税通則法 118 (1), 119 (1)). -/
def localCorp (co : Company) : Charge :=
  let n := citTaxJ co
  charge .cit "地方法人税 (local corporation tax)" n base1000 (fun x => (Rule.downTo 100).apply (divR .down (1030 * x) BP)) (statute := "地方法人税法 art. 10 (1) (asof 2025-07-01); 国税通則法 art. 118 (1), 119 (1)")

def families : List Family :=
  [{ name := "1200 corporate income tax and withholding", covers := [.cit],
     run := fun _ g _ => if g.entity != .company then [] else
       wht.charges g.company
       ++ [citChargeJ g.company, localCorp g.company] }]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  if g.entity != .company then [] else
  (if true then ["enterprise tax (事業税, size-based above 1億 capital), 特別法人事業税 and corporate inhabitants tax (地方税法) not modelled"] else [])
  ++ (if !g.company.paymentsAbroad.isEmpty then ["15.315 % on bond and deposit interest (所得税法 161 (1) 8, 213 (1) 3) and listed dividends (租特 9-3) not distinguished: interest is taken as loan interest (161 (1) 10, 20.42 %); treaty rates not applied"] else [])

#guard citSme.citTax { profit := 10000000, flags := ["sme"] } == 1664000
#guard cit.citTax { profit := 1000000 } == 232000
#guard (localCorp { profit := 1000000 }).due == 23800
#guard citTaxJ { profit := 1000999 } == 232000
-- 1,003,999 yen: base 1,003,000 x 23.2 % = 232,696 -> 232,600; local: 232,000 x 10.3 % = 23,896 -> 23,800
#guard citTaxJ { profit := 1003999 } == 232600
#guard (localCorp { profit := 1003999 }).due == 23800
#guard wht.amount { kind := .interest, amount := 10000 } == 2042

end JpGlobal.Corporate
