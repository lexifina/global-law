import PhGlobal.Pit

/-!
# Philippines 2025: estate tax and donor's tax (4300)
(B: RA 10963 TRAIN text on the build server not re-read.) NIRC s. 84: estate tax 6 % of the net estate; s. 86 (A) (1): standard deduction
PHP 5 m (family home up to 10 m not modelled). s. 99 (A): donor's tax 6 % of gifts above PHP 250,000 in the year.
-/

namespace PhGlobal.Transfers
open TaxKernel TaxKernel.Global

def inhF : Family :=
  { name := "4300 estate tax, donor's tax", covers := [.estate],
    run := fun _ g _ =>
      (let ts := g.transfers.filter (·.kind == .inheritance)
       if ts.isEmpty then [] else [estateCharge "Estate tax (6 %)" (Schedule.flat 600) {} 5000000 [.charity] ts "NIRC s. 84, s. 86 (A) (1)"])
      ++ (let ts := g.transfers.filter (·.kind == .gift)
          if ts.isEmpty then [] else [estateCharge "Donor's tax (6 %)" (Schedule.flat 600) {} 250000 [.charity] ts "NIRC s. 99 (A)"]) }

def families : List Family := [inhF]

def absent : List Absent :=
  [{ oecd := .wealth, why := "No net wealth tax; grade B" }]

def notes : List String := []

def unsupported (_ : List String) (_ : CanonGlobal) : List String := []

#guard (inhF.run [] { id := "t", household := { id := "t" }, transfers := [{ kind := .inheritance, value := 15000000, relation := .child }] } []).map (·.due) == [600000]

end PhGlobal.Transfers
