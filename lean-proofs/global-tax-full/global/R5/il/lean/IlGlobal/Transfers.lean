import TaxKernel.Global
import R5Common

/-!
# Israel 2025: purchase tax on dwellings (מס רכישה, 4400)

Real Estate Taxation Law (Appreciation and Purchase), 5723-1963 (חוק מיסוי מקרקעין (שבח ורכישה)), Hebrew Wikisource
consolidation with the amounts "נקוב לשנת 2025" (`law/il_ret.txt`), art. 9:
* (ג1ג)(2)-(3): an Israeli-resident individual buying his only dwelling (דירה יחידה; also when the previous one is
  sold within 24 months): nil up to 1,978,745 NIS, 3.5 % to 2,347,040, 5 % to 6,055,070, 8 % to 20,183,565, 10 % above;
* (ג1ו)(1) (temporary order, extended to 31.12.2026): any other dwelling: 8 % up to 6,055,070 NIS, 10 % above;
* (ג2): the amounts are not indexed in 2025-2027.
Purchases of kind `home` are dwellings: the single-dwelling scale unless `additionalHome` or `nonResident`. Land and
other real estate: the rate is set by the Minister's regulations (art. 9(א)), not read: not computed.
-/

namespace IlGlobal
open TaxKernel TaxKernel.Global R5Common

def singleDwelling : Schedule :=
  Schedule.ofList [(0, 0), (1978745, 350), (2347040, 500), (6055070, 800), (20183565, 1000)]

def otherDwelling : Schedule := Schedule.ofUpper [(6055070, 800)] 1000

def purchaseTax (p : Purchase) : Int :=
  (if p.additionalHome || p.nonResident then otherDwelling else singleDwelling).tax {} (pos p.price)

def transfers : Family :=
  { name := "4400 מס רכישה", covers := [.transactions],
    run := fun _ g _ =>
      (g.purchases.zipIdx.filter fun (p, _) => p.kind == .home).map fun (p, i) =>
        charge .transactions "מס רכישה" p.price pos (fun _ => purchaseTax p) (event := s!"purchase {i + 1}")
          (statute := if p.additionalHome || p.nonResident then "RETL art. 9(ג1ו) (8 % / 10 %)" else "RETL art. 9(ג1ג)(3) (single dwelling)") }

def transfersUnsupported (g : CanonGlobal) : List String :=
  if g.purchases.any (fun p => p.kind != .home) then ["purchase tax on land and non-residential property (regulations under art. 9(א)) not read: not computed"] else []

#guard purchaseTax { kind := .home, price := 1978745 } == 0
#guard purchaseTax { kind := .home, price := 2347040 } == 12890
#guard purchaseTax { kind := .home, price := 3000000, additionalHome := true } == 240000
#guard purchaseTax { kind := .home, price := 7055070, additionalHome := true } == 584405

end IlGlobal
