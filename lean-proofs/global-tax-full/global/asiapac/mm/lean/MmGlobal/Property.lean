import MmGlobal.Pit

/-!
# Myanmar 2025: stamp duty on conveyances of immovable property (4400)
Secondary-source sweep, grade B (guide facts; the Stamp Act 1899 as amended not read): PwC Worldwide Tax Summaries, Myanmar, Individual - Other taxes, last reviewed 3 June 2025 (Wayback capture 2025-11-08, asiapac/mm/law/pwc_mm_indother_wb20251108.txt), stamp duty section:
2 % of the price or value on a conveyance of property; for immovable property in Nay Pyi Taw, Yangon and Mandalay a further
2 % applies (the guide ties it to a consideration at market value). The model charges 2 % of each purchase of a home, other
real estate or land on the price (or the assessed value when higher); the further 2 % for the three cities is not applied
(the purchase record has no city) and is listed. Other instruments in the guide (share transfers 0.1 %, bonds 0.5 %, leases
0.5 % / 2 % of the annual rent) are not modelled. The registry's figure (4 % plus 3 % in Yangon) is not supported by the 2025
guide.
-/

namespace MmGlobal.Property
open TaxKernel TaxKernel.Global

def duty0 : TransferDuty :=
  { name := "Stamp duty on conveyances of immovable property (2 %)", sched := Schedule.flat 200, higherOfAssessed := true, kinds := [.home, .realEstate, .land] }

def fam0 : Family :=
  { name := "4400 transfer duties on property", covers := [.transactions],
    run := fun _ g _ => 
      duty0.charges g.purchases "Stamp Act 1899 as amended (not read); rate from PwC Worldwide Tax Summaries, Myanmar, Individual - Other taxes, last reviewed 3 June 2025 (Wayback capture 2025-11-08, asiapac/mm/law/pwc_mm_indother_wb20251108.txt)" (level := .central) }

def families : List Family := [fam0]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  (if g.purchases.any (fun p => [AssetKind.home, .realEstate, .land].contains p.kind) then ["4400 Myanmar stamp duty: the further 2 % on immovable property in Nay Pyi Taw, Yangon and Mandalay (PwC 2025) not applied: the purchase has no city (grade C part)"] else [])

#guard (fam0.run [] { id := "t", household := { id := "t" }, purchases := [{ kind := .home, price := 100000000 }] } []).map (·.due) == [2000000]

end MmGlobal.Property
