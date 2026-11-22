import JpGlobal.Pit

/-!
# Japan 2025: fixed asset tax, city planning tax, real estate acquisition tax, registration tax, stamp tax (4100, 4400)
e-Gov asof 2025-07-01 (`chihozei_…`, `torokumenkyozei_…`).
* 地方税法 art. 350 (1): 固定資産税 "標準税率は、百分の一・四"; art. 702-4: 都市計画税 up to 0.3 % (Tokyo 23 wards 0.3 %),
  on the assessed value (`assessed`).
* art. 73-15 (1): 不動産取得税 "標準税率は、百分の四"; 附則 art. 11-2: 3 % for land and houses to 2027-03-31.
* 登録免許税法 別表第一 一 (二) ハ: transfer by sale 2 % of the assessed value; 租特 art. 72: land 1.5 % to 2026-03-31.
* 印紙税法 (e-Gov asof 2025-07-01, `inshizei_…`) 別表第一 第一号 1 "不動産 ... の譲渡に関する契約書", 課税標準及び税率 1:
  契約金額 "十万円以下のもの 二百円" ...; 非課税物件 1: 契約金額 "一万円未満のもの". **租特 art. 91 (1)** (`sozeitokubetsu_…`):
  不動産譲渡契約書 made "平成二十六年四月一日から令和九年三月三十一日までの間" with 契約金額 "十万円を超えるもの": 一通につき
  200 (to 50万円), 500 (100万円), 1,000 (500万円), 5,000 (1,000万円), 10,000 (5,000万円), 30,000 (1億円), 60,000 (5億円),
  160,000 (10億円), 320,000 (50億円), 480,000 (above). One copy (the buyer's) per purchase (FT review 2026-11-21).

**Convention (R3 session 9)**: 固定資産税 = 1.4 % (art. 350 (1) 標準税率; a municipality's own higher rate is not applied) of
the 課税標準, which is the price registered in the 固定資産課税台帳 (art. 349 (1)): read from the asset's `assessed` field
(the kernel's statutory value), else from `value`. Charged on the owner on the assessment date, 1 January (art. 343 (1),
art. 359). Not applied: the 免税点 of art. 351 (no tax when the aggregate 課税標準 of one owner's land in the municipality is
under 300,000 yen, houses under 200,000 yen: the canonical `home` does not split land from the house) and the residential
land reductions of art. 349-3-2 (1/6, 1/3).
-/

namespace JpGlobal.Property
open TaxKernel TaxKernel.Global

def prop0 : PropertyTax :=
  { name := "固定資産税 (1.4 %)", sched := Schedule.flat 140, ratioNum := 1, ratioDen := 1, exempt := 0, kinds := [.home, .realEstate, .land] }

def prop1 : PropertyTax :=
  { name := "都市計画税 (Tokyo 0.3 %)", sched := Schedule.flat 30, ratioNum := 1, ratioDen := 1, exempt := 0, kinds := [.home, .realEstate, .land] }

def fam0 : Family :=
  { name := "4100 recurrent taxes on immovable property", covers := [.propertyRecurrent],
    run := fun _ g _ => 
      prop0.charges g.assets "地方税法 art. 350 (1)" (level := .local)
      ++ prop1.charges g.assets "地方税法 art. 702-4 (max 0.3 %)" (level := .local) }

def duty0 : TransferDuty :=
  { name := "不動産取得税 (land, houses 3 %)", sched := Schedule.flat 300, higherOfAssessed := true, kinds := [.home, .land] }

def duty1 : TransferDuty :=
  { name := "不動産取得税 (other buildings 4 %)", sched := Schedule.flat 400, higherOfAssessed := true, kinds := [.realEstate] }

def duty2 : TransferDuty :=
  { name := "登録免許税 (land 1.5 %)", sched := Schedule.flat 150, higherOfAssessed := true, kinds := [.land] }

def duty3 : TransferDuty :=
  { name := "登録免許税 (buildings 2 %)", sched := Schedule.flat 200, higherOfAssessed := true, kinds := [.home, .realEstate] }

def fam1 : Family :=
  { name := "4400 transfer duties on property", covers := [.transactions],
    run := fun _ g _ => 
      duty0.charges g.purchases "地方税法 art. 73-15; 附則 11-2" (level := .state)
      ++ duty1.charges g.purchases "地方税法 art. 73-15 (1)" (level := .state)
      ++ duty2.charges g.purchases "登録免許税法 別表第一 一 (二) ハ; 租特 art. 72" (level := .central)
      ++ duty3.charges g.purchases "登録免許税法 別表第一 一 (二) ハ" (level := .central) }

/-- 印紙税法 別表第一 第一号 (契約金額 1万円未満 非課税; 10万円以下 200円) and 租特 art. 91 (1) (reduced rates for
不動産譲渡契約書 made 2014-04-01 .. 2027-03-31), one copy, by the contract amount (the price). -/
def inshi (amt : Int) : Int :=
  if amt < 10000 then 0 else if amt ≤ 500000 then 200 else if amt ≤ 1000000 then 500
  else if amt ≤ 5000000 then 1000 else if amt ≤ 10000000 then 5000 else if amt ≤ 50000000 then 10000
  else if amt ≤ 100000000 then 30000 else if amt ≤ 500000000 then 60000 else if amt ≤ 1000000000 then 160000
  else if amt ≤ 5000000000 then 320000 else 480000
def inshiF : Family :=
  { name := "4400 印紙税 (不動産譲渡契約書)", covers := [.transactions],
    run := fun _ g _ => (g.purchases.zipIdx.filter fun (p, _) => p.kind.isRealEstate).map fun (p, i) =>
      charge .transactions "印紙税 (不動産譲渡契約書)" p.price id (fun _ => inshi p.price) (event := s!"purchase {i + 1}")
        (statute := "印紙税法 別表第一 第一号; 租税特別措置法 art. 91 (1) (one copy)") }

def families : List Family := [fam0, fam1, inshiF]

def absent : List Absent :=
  []

def notes : List String := ["JP 4100 convention: 固定資産税 1.4 % (地方税法 art. 350 (1)) of the 台帳 price (art. 349), input as the asset's `assessed` value (else `value`), on the owner at 1 January (art. 343, 359); art. 351 免税点 and art. 349-3-2 reductions not applied"]

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  (if g.assets.any (fun a => a.kind == .home || a.kind == .land) then ["residential land base reductions (地方税法 349-3-2: 1/6, 1/3) and new-house reductions not modelled"] else [])
  ++ (if !g.purchases.isEmpty then ["the duty base is the fixed-asset assessed value (taken as the higher of price and `assessed`); 住宅用家屋 0.3 % (租特 73); 印紙税: one copy of the contract (the buyer's)"] else [])
  ++ (if g.assets.any (fun a => (a.kind == .home || a.kind == .land) && a.statutoryValue < 300000) then ["地方税法 art. 351 免税点 (land < 300,000, houses < 200,000 yen per owner and municipality) not applied: the canonical home does not split land and house"] else [])

#guard prop0.amount { kind := .home, value := 10000000 } == 140000
#guard duty0.amount { kind := .land, price := 10000000 } == 300000
-- 印紙税法 別表第一 第一号 and 租特 art. 91 (1): the band edges
#guard inshi 9999 == 0
#guard inshi 10000 == 200
#guard inshi 500000 == 200
#guard inshi 500001 == 500
#guard inshi 10000000 == 5000
#guard inshi 10000001 == 10000
#guard inshi 100000000 == 30000
#guard inshi 100000001 == 60000
#guard inshi 5000000001 == 480000

end JpGlobal.Property
