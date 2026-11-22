import WsGlobal.Pit

/-!
# Samoa 2025: tax on interest (final withholding), dividends exempt (1100); capital gains tax not modelled

Source: Income Tax Act 2012 (as amended to the Income Tax Amendment Act 2022), text copied by the 1.x WS builder
(`cmp20/world/B14-pacific/ws/law/Income_Tax_Act_2012.txt`).
* **s. 94**: "a licensed financial institution paying interest to a resident individual must withhold tax from the gross
  amount of the interest at the rate of 15%"; **s. 104**: that tax is a final tax.
* **Schedule 2 Part A (1) (b)**: "a dividend paid by a resident company" is exempt income.
* **ss. 63-66, Schedule 1 (8)**: capital gains tax on the net capital gain, the cost raised by 5 % a year (s. 65 (2)),
  at 10 % if the asset is sold within 12 months and 27 % if sold after: not modelled (the uplift and the asset list of
  s. 66 not applied).
-/

namespace WsGlobal.Capital
open TaxKernel TaxKernel.Global

def fam0 : Family :=
  { name := "1100 capital income (final/schedular)", covers := [.pit],
    run := fun _ g _ => if g.entity == .company then [] else
      ((g.incomes.zipIdx.filter fun (i, _) => i.kind == .interest && !i.foreign).map fun (i, k) =>
        charge .pit "Final withholding on interest (15 %)" i.amount pos (fun b => divR .down (1500 * b) BP) (event := s!"income {k + 1}") (level := .central) (statute := "Income Tax Act 2012 s. 94, s. 104")) }

def families : List Family := [fam0]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  (if g.disposals.length > 0 then ["capital gains tax (ITA 2012 ss. 63-66, Schedule 1 (8): 10 % within 12 months, 27 % after, cost raised by 5 % a year) not modelled"] else [])

#guard (fam0.run [] { id := "t", household := { id := "t" }, incomes := [{ kind := .interest, amount := 10000 }] } []).map (·.due) == [1500]

end WsGlobal.Capital
