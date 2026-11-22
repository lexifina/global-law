import TaxKernel.Global
import R5Common

/-!
# Saudi Arabia 2025: white land fee (4100)

White Land Fees Law (Royal Decree M/4, 12/2/1437H; title amended to "… والعقارات الشاغرة" by Royal Decree M/244,
7/11/1446H), laws.boe.gov.sa as archived on 2025-07-10 (`law/whiteland_2025.html`, ARCHIVE_INDEX.tsv), art. 3:
"يفرض رسم سنوي على الأراضي البيضاء، المملوكة لشخص أو أكثر من ذوي الصفة الطبيعية أو الصفة الاعتبارية غير الحكومية،
بنسبة (2.5%) من قيمة الأرض". White land (art. 1): vacant land zoned residential or residential-commercial inside the
urban boundary; which plots are subject (area, phase, city) is set by the Regulations (art. 4) and notified to the
owner (art. 5): the input field `whiteLand` (true: the entity's land assets were notified as subject) selects them,
valued at their assessed value where given (the Regulations' valuation), else market value.
The archive shows art. 3 unamended at 2,5 %; the M/244 amendments to the rates (if any in force in 2025) not shown.
-/

namespace SaGlobal
open TaxKernel TaxKernel.Global R5Common

def whiteLandFlag (g : CanonGlobal) : Bool :=
  match g.raw.getObjValAs? Bool "whiteLand" with | .ok b => b | .error _ => false

def whiteLandFee (v : Int) : Int := divR .down (250 * pos v) BP

def property : Family :=
  { name := "4100 رسوم الأراضي البيضاء", covers := [.propertyRecurrent],
    run := fun _ g _ =>
      if !whiteLandFlag g then [] else
      ((g.assets.zipIdx.filter fun (a, _) => a.kind == .land).map fun (a, i) =>
        charge .propertyRecurrent "رسوم الأراضي البيضاء" a.statutoryValue pos whiteLandFee (event := s!"land {i + 1}")
          (statute := "White Land Fees Law (M/4) art. 3 (2.5 % of the land value)")) }

def propertyUnsupported (g : CanonGlobal) : List String :=
  if g.assets.any (·.kind == .land) && !whiteLandFlag g then
    ["land held: white land fee applies only to plots notified under the Regulations (input whiteLand): not charged"] else []

#guard whiteLandFee 4000000 == 100000

end SaGlobal
