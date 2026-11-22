import KrGlobal.Pit

/-!
# Korea 2025: property tax and acquisition tax (4100, 4400)
지방세법 (`kr/law/lawgo/지방세법_20260701.txt`, <개정 … 2019. 12. 31.> for art. 111):
* art. 111 (1) 3: housing 0.1 % to 6,000만, 0.15 % to 1.5억, 0.25 % to 3억, 0.4 % above, on the 과세표준 = 공시가격 × 60 %
  (공정시장가액비율, 시행령 art. 109); art. 111 (1) 2 다: other buildings 0.25 %. The one-home special rate (art. 111-2) and
  종합부동산세 are not modelled.
* art. 11 (1) 8: 취득세 on housing by price: ≤ 6억 1 %; 6-9억 (price × 2/3억 − 3) %; > 9억 3 %; art. 11 (1) 7 나: other 4 %.
  Multi-home rates (art. 13-2: 8 %, 12 %) and the 지방교육세/농특세 surcharges not modelled.

FT review (2026-11-21, third pass). **지방세특례제한법 art. 36-3 (1)** (law.go.kr, `kr/law/lawgo/지방세특례제한법_20260602.txt`;
the version saved is the one in force from 2026-06-02, amendment notes ending <2025. 12. 31.>; the 2025 version was not
saved, so the paragraph is taken as in force through 2025 (B)): a first home of at most 12억 bought
by a Korean national (not a minor) for own residence: "2. 제1호 외의 주택에 대해서는 산출세액이 200만원 이하인 경우에는 취득세를
면제하고, 산출세액이 200만원을 초과하는 경우에는 산출세액에서 200만원을 공제한다". The 1호 small-home tier (300만원: ≤ 60 m²
and ≤ 3억 / 6억 in the capital region; homes in population-decline areas) needs the floor area and location: listed.

Session 10 (2025 texts). **지방세법** as in force from 2025-01-01 (law.go.kr lsiSeq 268065, Law No. 20630,
`kr/law/lawgo/지방세법_20250101_268065.txt`): art. 111 (1) 3 as above; **art. 111-2 (1)**: a one-household-one-home
(시행령 art. 110-2) with 시가표준액 at most 9억: 0.05 % to 6,000만, 0.1 % to 1.5억, 0.2 % to 3억, 0.35 % above.
**지방세법 시행령** as in force on the 2025-06-01 assessment date (lsiSeq 271283, amended 2025-05-27,
`kr/law/lawgo/지방세법_시행령_20250527_271283.txt`): **art. 109 (1) 2**: housing 60 %, but for the 2025 liability a
one-household-one-home's ratio is 43 % (시가표준액 ≤ 3억), 44 % (to 6억), 45 % (above, also above 9억).
Modelled: a household entity with exactly one home is taken as one household with one home (other members' homes and
the art. 110-2 exceptions are not in the entity); companies and households with two or more homes take 60 % and art. 111
(1) 3. Not modelled: the base cap (art. 110 (3), 시행령 art. 109-2: needs the previous year's base), the art. 111-2 (3)
comparison with a locally adjusted rate, 지방교육세 on 재산세 (art. 151 (1) 6) and the 도시지역분 (art. 112).
Session 11: **지방교육세 on 재산세** (지방세법 version in force 2025-01-01, Law 20630, lsiSeq 268065, `kr/law/lawgo/
지방세법_20250101_268065.txt`): art. 151 (1) 6 "납부하여야 할 재산세액(제112조제1항제2호 및 같은 조 제2항에 따른 재산세액은
제외한다)의 100분의 20" (art. 151 (1) notes end 2021-12-28): 20 % of each 재산세 charge (`eduF`), booked under 4100 as the
재산세 itself (as the 자동차세 30 % sits with 5200). art. 151 (2): a local ordinance may vary the rate by up to 50 % (the
standard rate is used). The 도시지역분 (art. 112 (1) 2, 0.14 % of the base in urban zones designated by the council) stays
unmodelled (grade C): the entity has no location.
-/

namespace KrGlobal.Property
open TaxKernel TaxKernel.Global

/-- 지방세법 art. 111 (1) 3 (housing) on 시가표준액 × 60 % (시행령 art. 109 (1) 2). -/
def prop0 : PropertyTax :=
  { name := "재산세 (주택)", sched := (Schedule.ofList [(0, 10), (60000000, 15), (150000000, 25), (300000000, 40)]), ratioNum := 60, ratioDen := 100, exempt := 0, kinds := [.home] }

/-- 지방세법 art. 111 (1) 2 다 (other buildings 0.25 %) on 시가표준액 × 70 % (시행령 art. 109 (1) 1). -/
def prop1 : PropertyTax :=
  { name := "재산세 (건축물 0.25 %)", sched := Schedule.flat 25, ratioNum := 70, ratioDen := 100, exempt := 0, kinds := [.realEstate] }

/-- 지방세법 시행령 art. 109 (1) 2 단서 (2025-05-27 wording, 2025 liabilities only): a one-household-one-home's ratio. -/
def oneHomeRatio (v : Int) : Int := if v ≤ 300000000 then 43 else if v ≤ 600000000 then 44 else 45

/-- 지방세법 art. 111-2 (1): the one-household-one-home rates (시가표준액 ≤ 9억). -/
def oneHomeSched : Schedule := Schedule.ofList [(0, 5), (60000000, 10), (150000000, 20), (300000000, 35)]

def oneHomeTax (v : Int) : PropertyTax :=
  { name := "재산세 (주택, 1세대 1주택)", sched := (if v ≤ 900000000 then oneHomeSched else prop0.sched),
    ratioNum := oneHomeRatio v, ratioDen := 100, exempt := 0, kinds := [.home] }

/-- A household entity holding exactly one home is taken as one household with one home. -/
def oneHomeValue (g : CanonGlobal) : Option Int :=
  match g.entity, g.assets.filter (·.kind == .home) with
  | .household, [a] => some a.statutoryValue
  | _, _ => none

def propF : Family :=
  { name := "4100 recurrent taxes on immovable property", covers := [.propertyRecurrent],
    run := fun _ g _ =>
      (match oneHomeValue g with
       | some v => (oneHomeTax v).charges g.assets
           (if v ≤ 900000000 then "지방세법 art. 111-2 (1) (1세대 1주택, 시가표준액 9억 이하); 시행령 art. 109 (1) 2 단서 (2025: 43 / 44 / 45 %)"
            else "지방세법 art. 111 (1) 3; 시행령 art. 109 (1) 2 단서 (2025 one-home ratio 45 %)") (level := .local)
       | none => prop0.charges g.assets "지방세법 art. 111 (1) 3; 시행령 art. 109 (1) 2 (60 %)" (level := .local))
      ++ prop1.charges g.assets "지방세법 art. 111 (1) 2 다; 시행령 art. 109 (1) 1 (70 %)" (level := .local) }

/-- 지방세법 art. 11 (1) 8: housing acquisition tax rate by price (bp); 6-9억: (price × 2/3억 − 3) %. -/
def homeRateBp (p : Int) : Int := if p ≤ 600000000 then 100 else if p > 900000000 then 300 else p / 1500000 - 300
def acqTax (p : Purchase) : Int :=
  let v := max p.price p.assessed
  if p.kind == .home then divR .down (homeRateBp v * v) BP else divR .down (400 * v) BP
/-- 지방세특례제한법 art. 36-3 (1) 2: first home ≤ 12억: 취득세 less 200만원 (nil at most). -/
def firstHomeRelief (p : Purchase) (t : Int) : Int :=
  if p.kind == .home && p.firstHome && !p.nonResident && max p.price p.assessed ≤ 1200000000 then max 0 (t - 2000000) else t
def acqF : Family :=
  { name := "4400 취득세", covers := [.transactions],
    run := fun _ g _ => g.purchases.zipIdx.map fun (p, i) =>
      charge .transactions "취득세" (max p.price p.assessed) id (fun _ => firstHomeRelief p (acqTax p)) (event := s!"purchase {i + 1}") (level := .local) (statute := "지방세법 art. 11 (1) 7-8; 지방세특례제한법 art. 36-3 (1) 2 (first home: less 200만원)") }

/-- 지방세법 art. 151 (1) 6: 지방교육세 = 20 % of the 재산세 due (the 도시지역분 of art. 112 (1) 2 is not computed, so nothing
is excluded); one charge per 재산세 charge, same event. -/
def eduF : Family :=
  { name := "4100 지방교육세 (재산세분)", covers := [.propertyRecurrent],
    run := fun y g acc => (propF.run y g acc).map fun c =>
      charge .propertyRecurrent "지방교육세 (재산세분, 20 %)" c.due id (fun b => divR .down (2000 * b) BP) (event := c.event) (level := .local)
        (statute := "지방세법 art. 151 (1) 6 (version in force 2025-01-01, lsiSeq 268065): 20 % of the 재산세 due; art. 151 (2) local variation not applied") }

def families : List Family := [propF, acqF, eduF]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  (if g.assets.any (fun a => a.kind == .home && a.statutoryValue > 900000000) then ["종합부동산세 (above 9억; 12억 for one home) not modelled"] else [])
  ++ (if g.purchases.any (fun p => p.additionalHome) then ["multi-home acquisition rates (art. 13-2) and surcharges not modelled"] else [])
  ++ (if g.purchases.any (fun p => p.firstHome) then ["first home (지방세특례제한법 art. 36-3): the 200만원 relief applied (buyer taken as a Korean national, not a minor, never owning a home); the 300만원 small-home tier (1호) needs floor area and location: not applied"] else [])
  ++ (if (oneHomeValue g).isSome then ["재산세: the household's only home is taken as a 1세대 1주택 (시행령 art. 110-2; homes of household members outside the entity unknown); the base cap (art. 110 (3)) and the art. 111-2 (3) local-rate comparison not applied"] else [])
  ++ (if g.assets.any (fun a => a.kind == .home || a.kind == .realEstate) then ["도시지역분 (지방세법 art. 112 (1) 2: 0.14 % of the base in urban zones designated by the council; up to 0.23 % by ordinance, (2)) not modelled: the entity has no location (grade C); 지방교육세 on 재산세 (art. 151 (1) 6) at the standard 20 %"] else [])

#guard prop0.amount { kind := .home, value := 500000000 } == 570000
#guard homeRateBp 750000000 == 200
#guard acqTax { kind := .home, price := 500000000 } == 5000000
#guard firstHomeRelief { kind := .home, price := 500000000, firstHome := true } 5000000 == 3000000
#guard firstHomeRelief { kind := .home, price := 150000000, firstHome := true } 1500000 == 0
#guard firstHomeRelief { kind := .home, price := 1300000000, firstHome := true } 39000000 == 39000000
-- one home, 시가표준액 5억: base 44 % = 2.2억; 120,000 + 7천만 x 0.2 % = 260,000
#guard (oneHomeTax 500000000).amount { kind := .home, value := 500000000 } == 260000
-- one home 2억: 43 % = 8,600만; 30,000 + 2,600만 x 0.1 % = 56,000
#guard (oneHomeTax 200000000).amount { kind := .home, value := 200000000 } == 56000
-- one home 12억 (above 9억): 45 % = 5.4억; standard rates 570,000 + 2.4억 x 0.4 % = 1,530,000
#guard (oneHomeTax 1200000000).amount { kind := .home, value := 1200000000 } == 1530000
#guard (propF.run [] { id := "t", household := { id := "t" }, assets := [{ kind := .home, value := 500000000 }, { kind := .home, value := 500000000 }] } []).map (·.due) == [570000, 570000]
#guard (eduF.run [] { id := "t", household := { id := "t" }, assets := [{ kind := .home, value := 500000000 }] } []).map (·.due) == [52000]

end KrGlobal.Property
