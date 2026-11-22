import TaxKernel.Global2
import R5Common

/-!
# Armenia 2025: gifts and inheritances (4300)

No tax on the gift or inheritance itself: Tax Code ՀՕ-165-Ն art. 147(1)(13) counts property and money received from
natural persons by inheritance or gift as non-taxable income (except property given by a natural person who is the
developer of a multi-apartment building, art. 145(1)(1): income tax, 1100). Text read in every 2025 version of the
team's git history of the arlis.am texts (lexifina/armenia-law, act 109017; the change in force 30/10/2025, ՀՕ-324-Ն,
only adds "(non-taxable)" to the wording).

What is charged is the state duty on the notarial act: Law ՀՕ-186 "On State Duty" (act 487; art. 8 and art. 11 the same
text in every version in force from 1/1/2025 to 7/1/2026), art. 11(10): for issuing certificates of the right of
inheritance and certifying gift contracts, to first-order heirs **2-fold** the base duty, to second- and third-order
heirs **3-fold**, to other persons **5-fold**; art. 8: base duty **AMD 1 000**; art. 3: paid by the person using the
service (the heir, the donee).
Model: one duty per gift or inheritance of immovable property (the act whose certificate or certified contract the
registration of the right needs); other property is not charged (a deposit or insurance money passes without the duty,
art. 24; a gift of movables needs no certified contract). Heir orders from the relation: spouse, child, grandchild,
parent first order; sibling, niece or nephew second; everyone else is charged as another person (an aunt, uncle or
cousin, third order, would pay 3-fold: not told apart). Fixed amounts. Grade A (statute text read; the heir orders
are the Civil Code's, not read).
-/

namespace AmGlobal
open TaxKernel TaxKernel.Global R5Common

def notarialMultiple : Relation → Int
  | .spouse | .child | .grandchild | .parent => 2
  | .sibling | .nieceNephew => 3
  | _ => 5

def giftDuty (r : Relation) : Int := notarialMultiple r * 1000

def wealth : Family :=
  { name := "4300 Պետական տուրք (ժառանգության վկայագիր, նվիրատվության պայմանագիր)", covers := [.estate],
    run := fun _ g _ =>
      (transfersX g).zipIdx.filterMap fun ((t, x), i) =>
        match realPropertyPart t x with
        | some v =>
          if 0 < v then
            some (charge .estate
              (if t.kind == .gift then "state duty: certification of the gift contract" else "state duty: certificate of the right of inheritance")
              t.statutoryValue (fun _ => v) (fun _ => giftDuty t.relation)
              (event := s!"{if t.kind == .gift then "gift" else "inheritance"} {i + 1}")
              (statute := "Law HO-186 on State Duty art. 11(10) (2-, 3- or 5-fold of the base duty, art. 8: AMD 1 000), art. 3; Tax Code art. 147(1)(13): no income tax on gifts and inheritances from natural persons"))
          else none
        | none => none }

def wealthUnsupported (g : CanonGlobal) : List String :=
  ((transfersX g).zipIdx.filterMap fun ((_, x), i) =>
    if x.assetKind.isNone && x.realPropertyValue < 0 then
      some s!"state duty art. 11(10): transfer {i + 1} does not say whether it is immovable property (give \"assetKind\"): not charged"
    else none) ++
  (if g.transfers.any (fun t => t.relation == .otherRelative) then
    ["state duty art. 11(10): an 'otherRelative' is charged as another person (5-fold); a third-order heir pays 3-fold"] else [])

#guard giftDuty .child == 2000
#guard giftDuty .sibling == 3000
#guard giftDuty .unrelated == 5000

end AmGlobal
