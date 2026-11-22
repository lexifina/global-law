import R4Common.Stamp

/-! # R4Common: charges placed on the person the statute makes liable (twelfth pass).

The kernel's input holds the household's own sales (`disposals`), and its `transfers` are read either as what the
entity receives (recipient-based duties) or, for an estate- or donor-based tax, from the deceased's or donor's side
(`TaxKernel.Global.Transfer` docstring; `estateCharge`; the UK and US models do the same).

* `disposalDutyFamily`: a transfer duty the statute charges on the **transferor** (seller): one charge on each
  disposal of the listed kinds, on its proceeds (bands as `bandDuty`). Event `disposal i` (ZM Property Transfer Tax).
* `estateWholeFamily`: an **estate** duty: the entity's inheritances are read as the legacies of one estate; one charge
  (event `estate`) on their sum less the legacies to exempt relations, after an abatement (kernel `estateCharge`,
  `Schedule.ofUpper bands top`). ZA estate duty.
* `donorGiftFamily`: a gift tax charged on the **donor**: each gift record is read from the donor's side (one donor
  per gift, this gift the donor's only one of the year); the annual exemption comes off the gift, and the gift is
  taxed on top of the donor's earlier gifts (`prior`) within `lookbackYears` (tax on prior + gift less tax on prior).
  ZA donations tax.
-/

namespace R4
open TaxKernel TaxKernel.Global

def disposalDutyFamily (name : String) (kinds : List AssetKind) (bands : List (Int × Int)) (top : Int)
    (marginal : Bool) (nilUpTo : Int) (statute : String) (level : Level := .central) : Family :=
  { name := s!"4400 {name}", covers := [.transactions],
    run := fun _ g _ =>
      (g.disposals.zipIdx.filter (fun (d, _) => kinds.contains d.kind)).map fun (d, i) =>
        charge .transactions name d.proceeds id (fun y => bandDuty bands top marginal nilUpTo y)
          (event := s!"disposal {i + 1}") (level := level) (statute := statute) }

def estateWholeFamily (name : String) (bands : List (Int × Int)) (top nilBand : Int) (exempt : List Relation)
    (statute : String) : Family :=
  { name := s!"4300 {name}", covers := [.estate],
    run := fun _ g _ =>
      let inh := g.transfers.filter (·.kind == .inheritance)
      if inh.isEmpty then [] else [estateCharge name (Schedule.ofUpper bands top) {} nilBand exempt inh statute] }

def priorWithin (t : Transfer) (years : Nat) : Int :=
  isum ((t.prior.filter (fun p => decide (p.2 ≤ years))).map (·.1))

def donorGiftFamily (name : String) (bands : List (Int × Int)) (top annualExempt : Int) (exempt : List Relation)
    (lookbackYears : Nat) (statute : String) : Family :=
  { name := s!"4300 {name}", covers := [.estate],
    run := fun _ g _ =>
      (g.transfers.zipIdx.filter (fun (t, _) => t.kind == .gift)).map fun (t, i) =>
        let p := pos (priorWithin t lookbackYears)
        charge .estate name t.statutoryValue
          (fun v => if exempt.contains t.relation then 0 else pos (v - annualExempt))
          (fun y => divR .down (bandTicks bands top 0 (p + y)) BP - divR .down (bandTicks bands top 0 p) BP)
          (event := s!"gift {i + 1}") (statute := statute) }

def tLia : CanonGlobal :=
  { id := "x", household := { id := "x" },
    disposals := [{ kind := .home, proceeds := 1000000, cost := 400000 }, { kind := .listedShares, proceeds := 5, cost := 1 }],
    purchases := [{ kind := .home, price := 777 }],
    transfers := [{ kind := .inheritance, value := 20000000, relation := .child },
                  { kind := .inheritance, value := 30000000, relation := .spouse },
                  { kind := .inheritance, value := 20000000, relation := .sibling },
                  { kind := .gift, value := 1150000, relation := .child, prior := [(29500000, 2), (1000000, 9)] },
                  { kind := .gift, value := 900000, relation := .spouse }] }
-- seller side: the home sold, not the purchase: 5 % of 1 000 000
#guard ((disposalDutyFamily "t" [.home, .land] [] 500 false 0 "s").run [] tLia []).map (fun c => (c.event, c.due)) == [("disposal 1", 50000)]
-- one estate: 40 m to non-exempt heirs less 3,5 m = 36,5 m: 20 % of 30 m + 25 % of 6,5 m = 7 625 000
#guard ((estateWholeFamily "t" [(30000000, 2000)] 2500 3500000 [.spouse] "s").run [] tLia []).map (fun c => (c.event, c.due)) == [("estate", 7625000)]
-- donor side: 1 150 000 less 150 000 on top of 29,5 m given within 7 years: 0,5 m at 20 % + 0,5 m at 25 %; spouse 0
#guard ((donorGiftFamily "t" [(30000000, 2000)] 2500 150000 [.spouse] 7 "s").run [] tLia []).map (·.due) == [225000, 0]

end R4
