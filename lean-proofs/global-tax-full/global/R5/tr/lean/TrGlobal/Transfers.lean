import TaxKernel.Global
import R5Common

/-!
# Türkiye 2025: tapu harcı (4400) and emlak vergisi on buildings (4100)

* Harçlar Kanunu No. 492 (`law/tr_492.pdf`), tariff (4) 20 a): on transfers of immovable property for consideration,
  on the declared value "emlak vergisi değerinden az olmamak üzere", "devir eden ve devir alan için ayrı ayrı" at
  "(Binde 20)" (as raised from binde 16,5; the original column prints binde 10): 2 % from the buyer (purchases) and
  2 % from the seller (disposals).
* Emlak Vergisi Kanunu No. 1319 (`law/tr_1319.pdf`) art. 7-8 (4736, 2002): building tax on the tax value at "meskenlerde
  binde bir, diğer binalarda ise binde iki", "% 100 artırımlı" inside metropolitan municipalities (input field
  `metropolitan`: true/false, default false). Land (arsa, arazi: art. 18) not modelled. Level: local.
-/

namespace TrGlobal
open TaxKernel TaxKernel.Global R5Common

def tapuHarci : TransferDuty := { name := "Tapu harcı (alıcı)", sched := Schedule.flat 200, higherOfAssessed := true }

def metropolitan (g : CanonGlobal) : Bool :=
  match g.raw.getObjValAs? Bool "metropolitan" with | .ok b => b | .error _ => false

def emlak (g : CanonGlobal) : PropertyTax :=
  { name := "Emlak vergisi (bina)", sched := Schedule.flat 20, homeSched := some (Schedule.flat 10),
    multiplierBp := if metropolitan g then 20000 else 10000, kinds := [.home, .realEstate] }

def transfers : Family :=
  { name := "4400 tapu harcı, 4100 emlak vergisi", covers := [.transactions, .propertyRecurrent],
    run := fun _ g _ =>
      tapuHarci.charges g.purchases "Harçlar Kanunu tariff (4) 20 a) (binde 20, buyer)"
      ++ ((g.disposals.zipIdx.filter fun (d, _) => d.kind.isRealEstate).map fun (d, i) =>
          charge .transactions "Tapu harcı (satıcı)" d.proceeds pos (fun x => divR .down (200 * x) BP) (event := s!"disposal {i + 1}")
            (statute := "Harçlar Kanunu tariff (4) 20 a) (binde 20, seller)"))
      ++ (emlak g).charges g.assets "Emlak Vergisi Kanunu art. 8 (binde 1 homes, binde 2 other buildings; × 2 metropolitan)" }

def transfersUnsupported (g : CanonGlobal) : List String :=
  if g.assets.any (·.kind == .land) then ["emlak vergisi on land (arsa binde 3, arazi binde 1: art. 18) not read; not computed"] else []

#guard tapuHarci.amount { kind := .home, price := 1000000, assessed := 1200000 } == 24000
#guard (emlak { id := "t", household := { id := "t" } }).amount { kind := .home, value := 5000000, assessed := 2000000 } == 2000

end TrGlobal
