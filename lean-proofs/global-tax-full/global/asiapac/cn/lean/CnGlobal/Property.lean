import CnGlobal.Pit

/-!
# China 2025 (Beijing): deed tax and house property tax (4400, 4100)
* 契税法 (2020) art. 3: 3-5 %, set by the province (Beijing 3 %); 财政部 税务总局 住房城乡建设部公告2024年第16号: an
  individual's only home ≤ 140 m² 1 %, larger 1.5 % (second home: 1 %/2 %): homes modelled at 1 % (area not in the input).
* 房产税暂行条例 (1986, amended 2011) arts. 3-5: 1.2 % of the original value less 10-30 % (Beijing 30 %); owner-occupied
  homes of individuals exempt (art. 5 (4)): non-home real estate only.
-/

namespace CnGlobal.Property
open TaxKernel TaxKernel.Global

def prop0 : PropertyTax :=
  { name := "房产税 (1.2 % of 70 % of value)", sched := Schedule.flat 120, ratioNum := 70, ratioDen := 100, exempt := 0, kinds := [.realEstate] }

def fam0 : Family :=
  { name := "4100 recurrent taxes on immovable property", covers := [.propertyRecurrent],
    run := fun _ g _ => 
      prop0.charges g.assets "房产税暂行条例 arts. 3-4 (Beijing deduction 30 %)" (level := .local) }

def duty0 : TransferDuty :=
  { name := "契税 (home, 1 %)", sched := Schedule.flat 100, kinds := [.home] }

def duty1 : TransferDuty :=
  { name := "契税 (Beijing 3 %)", sched := Schedule.flat 300, kinds := [.realEstate, .land] }

def fam1 : Family :=
  { name := "4400 transfer duties on property", covers := [.transactions],
    run := fun _ g _ => 
      duty0.charges g.purchases "契税法 art. 3; 公告2024年第16号" (level := .state)
      ++ duty1.charges g.purchases "契税法 art. 3; 北京市契税适用税率 3 %" (level := .state) }

def families : List Family := [fam0, fam1]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  (if g.purchases.any (fun p => p.kind == .home) then ["home deed tax by floor area (> 140 m² 1.5 %/2 %) not modelled"] else [])
  ++ (if g.disposals.any (fun d => d.kind.isRealEstate) then ["土地增值税 (30-60 %), 城镇土地使用税 and seller stamp duty not modelled"] else [])

#guard duty0.amount { kind := .home, price := 3000000 } == 30000
#guard prop0.amount { kind := .realEstate, value := 1000000 } == 8400

end CnGlobal.Property
