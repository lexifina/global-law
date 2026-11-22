import TaxKernel.Global
import R5Common

/-!
# Tunisia 2025: income tax on capital gains of individuals (1100: real property and company shares)

Source: Code de l'IRPP et de l'IS, DGELF edition 2025 (`law/code2025fr.txt`, the TN 1200 source), with its amendment
notes to LF 2025:
* art. 27-2 (LF 2023): the gain on the sale of shares in real-estate companies, built property and land is a property
  income; not for sales to the spouse, ascendants or descendants, expropriations, land-reserve sales, or **the first
  sale of a single dwelling of at most 1 000 m² at a price below 500 000 dinars**;
* art. 28-IV: the gain is the declared price less the cost of acquisition, gift or construction (land included),
  **raised by the justified outlays and by 10 % per year of holding**;
* art. 44-III-1: **15 %** when the sale is within five years of possession, **10 %** after five years; 10 % for
  inherited property whatever the holding;
* art. 33 (second paragraph) and 44-III-3 (LF 2023, for sales from 1/1/2023): share gains (net of the year's losses)
  **10 %** for shares listed on the BVMT sold before the end of the year following the year of acquisition and for
  other shares and interests sold after it; **15 %** for unlisted shares and interests sold before it.
Model (households): property (home, realEstate, land): gain = proceeds − cost × (1 + 10 % × full years held) −
costs; 15 % under 60 months held, else 10 %; a disposal flagged `mainHome` of kind home with proceeds below 500 000 is
exempt (taken as the first sale of the single dwelling). Shares: held under 12 months, listed 10 % / unlisted 15 %;
unlisted held 24 months or more 10 %; listed held 24 months or more not charged (no rate in art. 44-III-3: the
exemption article was not read), 12-23 months undecided (the rule reads calendar years): listed. Interest, dividends
and rents stay with the 1.x model. Grade A (2025 code text read).
-/

namespace TnGlobal
open TaxKernel TaxKernel.Global R5Common

def tnYears (d : Disposal) : Int := ((d.heldMonths / 12 : Nat) : Int)

def tnPropertyGain (d : Disposal) : Int := pos (d.proceeds - d.cost - d.cost * tnYears d / 10 - d.costs)

def tnPropertyExempt (d : Disposal) : Bool := d.kind == .home && d.mainHome && d.proceeds < 500000

def tnPropertyRate (d : Disposal) : Int := if d.heldMonths < 60 then 1500 else 1000

/-- art. 44-III-3: `some rate` when the holding decides it, `none` otherwise -/
def tnShareRate (d : Disposal) : Option Int :=
  let listed := d.listed || d.kind == .listedShares
  if d.heldMonths < 12 then some (if listed then 1000 else 1500)
  else if d.heldMonths ≥ 24 then (if listed then none else some 1000)
  else none

def capital : Family :=
  { name := "1100 IRPP: plus-values", covers := [.pit],
    run := fun _ g _ =>
      if g.entity == .company then [] else
      g.disposals.zipIdx.filterMap fun (d, i) =>
        if d.kind.isRealEstate then
          if tnPropertyExempt d then none else
          some (charge .pit "IRPP: plus-value immobilière" (pos (d.proceeds - d.cost)) (fun _ => tnPropertyGain d)
            (fun b => b * tnPropertyRate d / 10000) (event := s!"disposal {i + 1}")
            (statute := "Code IRPP-IS art. 27-2, 28-IV (cost + 10 % a year), 44-III-1 (15 % within 5 years, 10 % after)"))
        else if d.kind.isShares then
          match tnShareRate d with
          | some r =>
            some (charge .pit "IRPP: plus-value de cession de titres" (pos (d.proceeds - d.cost - d.costs)) pos
              (fun b => b * r / 10000) (event := s!"disposal {i + 1}")
              (statute := "Code IRPP-IS art. 33 (2nd paragraph), 44-III-3 (10 % / 15 %, LF 2023)"))
          | none => none
        else none }

def capitalUnsupported (g : CanonGlobal) : List String :=
  if g.entity == .company then [] else
  (if g.disposals.any (·.kind.isRealEstate) then
    ["IRPP on property gains: sales to the spouse, ascendants or descendants and inherited property (10 % whatever the holding) are not told apart; the dwelling exemption taken for a mainHome sale below 500 000 dinars (first sale and the 1 000 m² limit assumed)"] else []) ++
  ((g.disposals.zipIdx.filter fun (d, _) => d.kind.isShares && (tnShareRate d).isNone).map fun (d, i) =>
    if d.heldMonths ≥ 24 then s!"IRPP on share gains: disposal {i + 1} (listed, held 24 months or more): no rate in art. 44-III-3, exemption article not read: not charged"
    else s!"IRPP on share gains: disposal {i + 1} held 12-23 months: whether it was sold before the end of the year after acquisition needs the dates (grade C)") ++
  (if g.disposals.any (·.kind.isShares) then ["IRPP on share gains: the year's losses are not netted (art. 33)"] else [])

#guard tnPropertyGain { kind := .realEstate, proceeds := 500000, cost := 300000, heldMonths := 36 } == 110000
#guard tnShareRate { kind := .unlistedShares, proceeds := 1, cost := 0, heldMonths := 6 } == some 1500

end TnGlobal
