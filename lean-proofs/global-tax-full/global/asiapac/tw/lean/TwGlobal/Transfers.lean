import TwGlobal.Pit

/-!
# Taiwan 2025: estate and gift tax (4300)
遺產及贈與稅法 art. 13 (estate), art. 19 (gift): 10 / 15 / 20 %; amounts indexed by the MOF announcement for 2025 (B):
estate exemption 1,333萬 (art. 18), brackets 5,621萬 and 1億1,242萬; gift annual exemption 244萬 (art. 22), brackets 2,811萬
and 5,621萬. The estate is taxed as one estate (`estateCharge`); spouse and dependant deductions not modelled.
-/

namespace TwGlobal.Transfers
open TaxKernel TaxKernel.Global

def inhF : Family :=
  { name := "4300 遺產稅・贈與稅", covers := [.estate],
    run := fun _ g _ =>
      (let ts := g.transfers.filter (·.kind == .inheritance)
       if ts.isEmpty then [] else [estateCharge "遺產稅" (Schedule.ofList [(0, 1000), (56210000, 1500), (112420000, 2000)]) {} 13330000 [.charity] ts "遺產及贈與稅法 arts. 13, 18 (2025 amounts)"])
      ++ (let ts := g.transfers.filter (·.kind == .gift)
          if ts.isEmpty then [] else [estateCharge "贈與稅" (Schedule.ofList [(0, 1000), (28110000, 1500), (56210000, 2000)]) {} 2440000 [.charity] ts "遺產及贈與稅法 arts. 19, 22 (2025 amounts)"]) }

def families : List Family := [inhF]

def absent : List Absent :=
  [{ oecd := .wealth, why := "No net wealth tax in Taiwan; grade B" }]

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  (if g.transfers.any (fun t => t.kind == .inheritance) then ["deductions for spouse (553萬), descendants, funeral costs (art. 17) not modelled"] else [])

#guard (inhF.run [] { id := "t", household := { id := "t" }, transfers := [{ kind := .inheritance, value := 23330000, relation := .child }] } []).map (·.due) == [1000000]
#guard (inhF.run [] { id := "t", household := { id := "t" }, transfers := [{ kind := .gift, value := 3440000, relation := .child }] } []).map (·.due) == [100000]

end TwGlobal.Transfers
