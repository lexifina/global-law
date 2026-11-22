import TaxKernel.Global
import R5Common

/-!
# Tunisia 2025: impôt sur la fortune immobilière (4200)

Décret-loi n° 2022-79 du 22 décembre 2022 portant loi de finances pour 2023, art. 23, as printed in the DGELF
"Recueil des textes relatifs aux droits et taxes non incorporés dans les codes fiscaux" (édition 2023, section 33;
1.x `law/recueil2023.txt`); the LF 2025 (1.x `law/LF2025.txt`) does not amend it (no reference to art. 23 or to
"الثروة"); the LF 2024 was not checked.
* 1): due on 1 January on the real property of each natural person "dont la valeur vénale est égale ou supérieure à
  3 millions de dinars", including that of minor children;
* 3): not subject: "l'habitation principale du redevable" (here: the person's first asset of kind `home`) and
  premises used in the person's own business (kind `business`: not counted);
* 4): the 3 million is reckoned on all subject property after deducting the debts borne by it; "Le taux … est fixé à
  0,5 %" (on the whole value once the threshold is reached: an entry threshold, not an allowance).
-/

namespace TnGlobal
open TaxKernel TaxKernel.Global R5Common

def ifiThreshold : Int := 3000000

def ifiCounted (as : List Asset) : List Asset :=
  let re := as.filter fun a => a.kind == .home || a.kind == .realEstate || a.kind == .land
  match re.findIdx? (·.kind == .home) with
  | some i => re.eraseIdx i
  | none => re

def ifiBase (as : List Asset) : Int :=
  let c := ifiCounted as
  pos (isum (c.map (·.value)) - isum (c.map (·.debt)))

def ifiTax (b : Int) : Int := if b < ifiThreshold then 0 else divR .down (50 * b) BP

def wealth : Family :=
  { name := "4200 impôt sur la fortune immobilière", covers := [.wealth],
    run := fun _ g _ =>
      if g.entity == .company then [] else
      ((g.assets.map (·.person)).eraseDups.filter fun p => ifiTax (ifiBase (g.assets.filter (·.person == p))) ≠ 0).map fun p =>
        charge .wealth "Impôt sur la fortune immobilière" (ifiBase (g.assets.filter (·.person == p))) id ifiTax
          (event := s!"person {p}") (statute := "DL 2022-79 (LF 2023) art. 23 (0,5 % from TND 3 million)") }

def wealthUnsupported (g : CanonGlobal) : List String :=
  if g.assets.any (fun a => a.kind.isRealEstate) then
    ["IFI: minor children's property and civil real-estate company shares not added; main home = the person's first home asset"] else []

#guard ifiTax 2999999 == 0
#guard ifiTax 3000000 == 15000
#guard ifiBase [{ kind := .home, value := 900000 }, { kind := .realEstate, value := 3500000, debt := 400000 }] == 3100000

end TnGlobal
