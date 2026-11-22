import JpGlobal.Pit

/-!
# Japan 2025: inheritance and gift tax (4300)
e-Gov asof 2025-07-01 (`sozokuzei_2025-07-01.xml`).
* 相続税法 art. 15: basic exemption 3,000万 + 600万 × statutory heirs; art. 16 table: ≤ 1,000万 10 %, ≤ 3,000万 15 %, ≤ 5,000万
  20 %, ≤ 1億 30 %, ≤ 2億 40 %, ≤ 3億 45 %, ≤ 6億 50 %, above 55 %. Modelled for one acquirer who is the sole statutory heir
  (exemption 3,600万; the statutory-share computation for several heirs is not modelled).
* art. 21-7 table (gifts, general): ≤ 200万 10 %, ≤ 300万 15 %, ≤ 400万 20 %, ≤ 600万 30 %, ≤ 1,000万 40 %, ≤ 1,500万 45 %,
  ≤ 3,000万 50 %, above 55 %; art. 21-5 basic exemption 60万, 110万 under 租特 art. 70-2-4. The special table for lineal
  descendants aged 18+ (租特 70-2-5): below (FT review, second pass).
* **租特 art. 70-2-5 (1)** (e-Gov asof 2025-07-01, `sozeitokubetsu_2025-07-01.xml`, the table read from the XML):
  "平成二十七年一月一日以後に直系尊属からの贈与により財産を取得した者（その年一月一日において十八歳以上の者に限る。）
  のその年中の当該財産に係る贈与税の額は、相続税法第二十一条の七の規定にかかわらず、前条の規定による控除後の課税価格を
  次の表 ...": 二百万円以下 百分の十; 四百万円以下 百分の十五; 六百万円以下 百分の二十; 千万円以下 百分の三十; 千五百万円以下
  百分の四十; 三千万円以下 百分の四十五; 四千五百万円以下 百分の五十; 超 百分の五十五. A gift to a `child` or `grandchild`
  (the donor a lineal ascendant) whose `recipientAge` is 18 or more takes this table after the 110万 of art. 70-2-4;
  the recipient's age is read as the age on 1 January. FT review 2026-11-21 (second pass).
-/

namespace JpGlobal.Transfers
open TaxKernel TaxKernel.Global

def inh : InheritanceTax :=
  { name := "相続税", classOf := fun _ => 0, exemptRelations := [.charity],
    classes := [{ allowance := 36000000, sched := Schedule.ofList [(0, 1000), (10000000, 1500), (30000000, 2000), (50000000, 3000), (100000000, 4000), (200000000, 4500), (300000000, 5000), (600000000, 5500)] }] }
def gift : InheritanceTax :=
  { name := "贈与税", classOf := fun _ => 0, exemptRelations := [.charity],
    classes := [{ allowance := 1100000, sched := Schedule.ofList [(0, 1000), (2000000, 1500), (3000000, 2000), (4000000, 3000), (6000000, 4000), (10000000, 4500), (15000000, 5000), (30000000, 5500)] }] }
def inhF : Family :=
  { name := "4300 相続税・贈与税", covers := [.estate],
    run := fun _ g _ => inh.charges (g.transfers.filter (·.kind == .inheritance)) "相続税法 arts. 15-16 (sole statutory heir)"
      ++ gift.charges (g.transfers.filter (·.kind == .gift)) "相続税法 arts. 21-5, 21-7; 租特 70-2-4 (一般税率)" }
/-- 租特 art. 70-2-5 (1): gifts from a lineal ascendant to a recipient aged 18+ on 1 January (特例税率). -/
def giftSp : InheritanceTax :=
  { name := "贈与税 (特例税率)", classOf := fun _ => 0, exemptRelations := [.charity],
    classes := [{ allowance := 1100000, sched := Schedule.ofList [(0, 1000), (2000000, 1500), (4000000, 2000), (6000000, 3000), (10000000, 4000), (15000000, 4500), (30000000, 5000), (45000000, 5500)] }] }
def isSpecialGift (t : Transfer) : Bool :=
  t.kind == .gift && (t.relation == .child || t.relation == .grandchild) && decide (18 ≤ t.recipientAge)
def inhF2 : Family :=
  { name := "4300 相続税・贈与税", covers := [.estate],
    run := fun _ g _ => inh.charges (g.transfers.filter (·.kind == .inheritance)) "相続税法 arts. 15-16 (sole statutory heir)"
      ++ gift.charges (g.transfers.filter (fun t => t.kind == .gift && !isSpecialGift t)) "相続税法 arts. 21-5, 21-7; 租特 70-2-4 (一般税率)"
      ++ giftSp.charges (g.transfers.filter isSpecialGift) "相続税法 art. 21-5; 租特 70-2-4, 70-2-5 (1) (特例税率: 直系尊属からの贈与, 18歳以上)" }

def families : List Family := [inhF2]

def absent : List Absent :=
  [{ oecd := .wealth, why := "No net wealth tax in Japan (the 1950 富裕税 was repealed in 1953); grade B" }]

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  (if g.transfers.any (fun t => t.kind == .inheritance) then ["inheritance tax computed as for a sole statutory heir (art. 16 statutory-share method for several heirs, spouse credit art. 19-2, small-site relief not modelled)"] else [])
  ++ (if g.transfers.any (fun t => t.kind == .gift && (t.relation == .child || t.relation == .grandchild)) then ["相続時精算課税 not modelled; 租特 70-2-5 read with recipientAge as the age on 1 January"] else [])
  ++ (if g.transfers.any isSpecialGift && g.transfers.any (fun t => t.kind == .gift && !isSpecialGift t) then ["special and general gifts in one year: the 租特 70-2-5 (3) apportionment is not modelled (each gift on its own table)"] else [])

#guard inh.tax { kind := .inheritance, value := 100000000, relation := .child } == 12200000
#guard gift.tax { kind := .gift, value := 3100000, relation := .unrelated } == 200000
#guard giftSp.tax { kind := .gift, value := 5000000, relation := .child, recipientAge := 30 } == 485000
#guard gift.tax { kind := .gift, value := 5000000, relation := .sibling } == 530000
#guard isSpecialGift { kind := .gift, value := 5000000, relation := .child, recipientAge := 17 } == false
#guard isSpecialGift { kind := .gift, value := 5000000, relation := .grandchild, recipientAge := 18 } == true
#guard giftSp.tax { kind := .gift, value := 46100000, relation := .child } == 18350000

end JpGlobal.Transfers
