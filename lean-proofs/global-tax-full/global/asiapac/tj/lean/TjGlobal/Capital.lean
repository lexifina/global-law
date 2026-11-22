import TjGlobal.Pit

/-!
# Tajikistan 2025: withholding taxes on dividends and interest of individuals (1100, final)

Tax Code (2021), edition of 14 May 2025 (`cmp20/world/B05-former-ussr/tj/law/tc_en_20250514.txt`, Tajik original governs):
* **art. 237 (1)**: dividends paid by resident enterprises are subject to withholding tax at 12 % (Law No. 2159 of 15 Apr
  2025); (2) taxed dividends are not included in the recipient's gross income: final.
* **art. 238 (1)**: interest paid by a resident or a permanent establishment, Tajik source, 12 %; (3) not included in an
  individual's gross income: final; (2) interest paid to resident credit institutions is not subject (not a household case).
Capital gains of individuals and rental income (taxed in the PIT line) are not modelled here.
-/

namespace TjGlobal.Capital
open TaxKernel TaxKernel.Global

def fam0 : Family :=
  { name := "1100 capital income (final/schedular)", covers := [.pit],
    run := fun _ g _ => if g.entity == .company then [] else
      ((g.incomes.zipIdx.filter fun (i, _) => i.kind == .dividend && !i.foreign).map fun (i, k) =>
        charge .pit "Withholding tax on dividends (12 %, final)" i.amount pos (fun b => divR .down (1200 * b) BP) (event := s!"income {k + 1}") (level := .central) (statute := "Tax Code 2021 art. 237 (1), (2)"))
      ++ ((g.incomes.zipIdx.filter fun (i, _) => i.kind == .interest && !i.foreign).map fun (i, k) =>
        charge .pit "Withholding tax on interest (12 %, final)" i.amount pos (fun b => divR .down (1200 * b) BP) (event := s!"income {k + 1}") (level := .central) (statute := "Tax Code 2021 art. 238 (1), (3)")) }

def families : List Family := [fam0]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  (if g.disposals.length > 0 then ["gains of individuals on disposals not modelled"] else [])

#guard (fam0.run [] { id := "t", household := { id := "t" }, incomes := [{ kind := .dividend, amount := 1000 }] } []).map (·.due) == [120]
#guard (fam0.run [] { id := "t", household := { id := "t" }, incomes := [{ kind := .interest, amount := 1000 }] } []).map (·.due) == [120]

end TjGlobal.Capital
