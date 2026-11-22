import IdGlobal.Pit

/-!
# Indonesia 2025 (DKI Jakarta): BPHTB (4400); PBB-P2 not reached
UU 1/2022 (HKPD) Pasal 44-49 and Perda DKI Jakarta 1/2024 (B): BPHTB 5 % of the acquisition value less the NPOPTKP of
Rp 80 m (Jakarta). PBB-P2 (HKPD Pasal 38-43, max 0.5 %; Jakarta's NJOP bands): not reached (C).
-/

namespace IdGlobal.Property
open TaxKernel TaxKernel.Global

def bphtb (v : Int) : Int := divR .down (500 * pos (v - 80000000)) BP
def bphtbF : Family :=
  { name := "4400 BPHTB (Jakarta)", covers := [.transactions],
    run := fun _ g _ => (g.purchases.filter (·.kind.isRealEstate)).zipIdx.map fun (p, i) =>
      charge .transactions "BPHTB (5 %)" (max p.price p.assessed) id bphtb (event := s!"purchase {i + 1}") (level := .state) (statute := "UU 1/2022 Pasal 44-49; Perda DKI 1/2024 (NPOPTKP Rp 80 m)") }

def families : List Family := [bphtbF]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (_ : CanonGlobal) : List String := []

#guard bphtb 1080000000 == 50000000

end IdGlobal.Property
