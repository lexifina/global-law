import TaxKernel.Global
import R5Common

/-!
# Türkiye 2025: veraset ve intikal vergisi (4300) and değerli konut vergisi (4100)

**Veraset ve İntikal Vergisi Kanunu No. 7338** (`law/tr_7338.pdf.txt`, mevzuat.gov.tr) with the 2025 amounts of the
VİVK Genel Tebliği Seri No. 56 (Resmî Gazete 30/12/2024, 32768 2. Mükerrer; `law/rg_20241230M2-5.htm`), in force
1/1/2025:
* art. 4(b): each descendant's (füruğ, adopted children included) and the spouse's inheritance share is exempt up to
  2.316.628 TL; the spouse's share up to 4.636.103 TL when there are no descendants (input `noDescendants`: true);
* art. 4(d): gratuitous transfers (ivazsız intikaller) exempt up to 53.339 TL;
* art. 16 (4369, 1998) with the Tebliğ's bands: inheritance 1/3/5/7/10 %, gratuitous 10/15/20/25/30 % on the first
  2.400.000, next 5.700.000, next 12.000.000, next 24.000.000 TL and above 44.100.000 TL; second paragraph: gifts to
  a person from the mother, father, spouse or children are taxed at half the gratuitous rates.
  (The 2026 paragraph of Law 7582 on art. 20/D heirs is not in force in 2025.)
**Emlak Vergisi Kanunu No. 1319**, fourth part (7194/7221; `law/tr_1319.pdf.txt`) with the 2025 amounts of the EVK
Genel Tebliği Seri No. 86 (same Gazette, `law/rg_20241230M2-9.htm`) art. 5-6: dwellings whose building tax value
(bina vergi değeri: the asset's `assessed` value, else market value) exceeds 15.709.000 TL; on the excess binde 3 up
to 23.564.000 TL, binde 6 up to 31.421.000 TL, binde 10 above (art. 44). Art. 46(b): an owner of a single dwelling
is exempt, and an owner of several is exempt on the lowest-valued subject dwelling. Assets of kind `home` are the
dwellings, per owner (`person`).
-/

namespace TrGlobal
open TaxKernel TaxKernel.Global R5Common

def vivkSched (r0 r1 r2 r3 r4 : Int) : Schedule :=
  Schedule.ofUpper [(2400000, r0), (8100000, r1), (20100000, r2), (44100000, r3)] r4

def noDescendants (g : CanonGlobal) : Bool :=
  match g.raw.getObjValAs? Bool "noDescendants" with | .ok b => b | .error _ => false

/-- Inheritance: class 0 descendants and spouse (2.316.628), 1 the spouse without descendants (4.636.103), 2 others. -/
def veraset (nd : Bool) : InheritanceTax :=
  { name := "Veraset ve intikal vergisi (veraset)",
    classOf := fun r => match r with
      | .child | .grandchild => 0
      | .spouse => if nd then 1 else 0
      | _ => 2,
    classes := [{ allowance := 2316628, sched := vivkSched 100 300 500 700 1000 },
                { allowance := 4636103, sched := vivkSched 100 300 500 700 1000 },
                { allowance := 0, sched := vivkSched 100 300 500 700 1000 }] }

/-- Gratuitous transfers: class 0 from the mother, father, spouse or children (half rates), 1 others. -/
def ivazsiz : InheritanceTax :=
  { name := "Veraset ve intikal vergisi (ivazsız intikal)",
    classOf := fun r => match r with
      | .child | .spouse | .parent => 0
      | _ => 1,
    classes := [{ allowance := 53339, sched := vivkSched 500 750 1000 1250 1500 },
                { allowance := 53339, sched := vivkSched 1000 1500 2000 2500 3000 }] }

def dkSched : Schedule := Schedule.ofList [(0, 0), (15709000, 30), (23564000, 60), (31421000, 100)]

/-- The subject dwellings of one owner after the art. 46(b) exemption. -/
def dkTaxed (homes : List Asset) : List Asset :=
  if homes.length ≤ 1 then [] else
  let subj := homes.filter (·.statutoryValue > 15709000)
  match (subj.map (·.statutoryValue)).min? with
  | none => []
  | some m => subj.eraseIdx ((subj.findIdx? (·.statutoryValue == m)).getD 0)

def assetPersons (g : CanonGlobal) : List Nat := (g.assets.map (·.person)).eraseDups

def wealth : Family :=
  { name := "4300 veraset ve intikal vergisi, 4100 değerli konut vergisi", covers := [.estate],
    run := fun _ g _ =>
      (veraset (noDescendants g)).charges (g.transfers.filter (·.kind == .inheritance)) "VİVK art. 4(b), 16 (Tebliğ Seri 56: 2025 bands)"
      ++ ivazsiz.charges (g.transfers.filter (·.kind == .gift)) "VİVK art. 4(d), 16 (half rates from parents, spouse, children)"
      ++ ((assetPersons g).flatMap fun p =>
          (dkTaxed (g.assets.filter fun a => a.kind == .home && a.person == p)).map fun a =>
            charge .propertyRecurrent "Değerli konut vergisi" a.statutoryValue pos (fun v => dkSched.tax {} v)
              (event := s!"dwelling of person {p}") (statute := "EVK art. 42, 44, 46(b) (Tebliğ Seri 86: 2025 amounts)")) }

def wealthUnsupported (g : CanonGlobal) : List String :=
  (if g.transfers.any (fun t => t.prior.length > 0) then ["VİVK: earlier gifts from the same donor not aggregated"] else [])
  ++ (if g.assets.any (fun a => a.kind == .realEstate) then ["değerli konut: assets of kind realEstate not treated as dwellings"] else [])

#guard (veraset false).tax { kind := .inheritance, value := 4716628, relation := .child } == 24000
#guard (veraset true).tax { kind := .inheritance, value := 4636103, relation := .spouse } == 0
#guard ivazsiz.tax { kind := .gift, value := 1053339, relation := .unrelated } == 100000
#guard ivazsiz.tax { kind := .gift, value := 1053339, relation := .child } == 50000
#guard dkSched.tax {} 23564000 == 23565
#guard dkSched.tax {} 31421000 == 70707
#guard (dkTaxed [{ kind := .home, value := 20000000 }]).length == 0
#guard (dkTaxed [{ kind := .home, value := 20000000 }, { kind := .home, value := 18000000 }]).map (·.value) == [20000000]

end TrGlobal
