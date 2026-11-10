import LegalProofs.USTax.Trusts.Sale

/-!
# A blind search over trust instruments and plans

Every power the rules describe (10 kinds × 5 holders × 2 capacities × 2 standards = 200), every instrument of one or
two powers (20,300), each classified by the two tests; then, for every instrument, every plan: keep the asset, sell
it to the trust, or sell it and use any substitution power the instrument contains just before death. Each plan is
scored by what the heirs keep. Nothing tells the search which instrument or plan to prefer.

    lake env lean LegalProofs/USTax/Trusts/Search.lean
-/

namespace Legal.USTax.Trusts.Search
open Legal.USTax.Trusts

def kinds : List Kind := [.revoke, .incomeToGrantor, .incomeToSpouse, .premiums, .substitute, .borrow, .sprinkle,
  .addBeneficiary, .voteStock, .reversion]
def holders : List Holder := [.grantor, .spouse, .nonadverse, .adverse, .independent]
def powers : List Power :=
  kinds.flatMap fun k => holders.flatMap fun h => [false, true].flatMap fun f => [false, true].map fun st => ⟨k, h, f, st⟩

def pairs : List Power → List Instrument
  | [] => []
  | p :: rest => rest.map (fun q => [p, q]) ++ pairs rest

def instruments : List Instrument := (powers.map fun p => [p]) ++ pairs powers

def canSwap (i : Instrument) : Bool := i.any fun p => p.kind == .substitute && !p.fiduciary

def showStatus : Status → String
  | .complete => "complete" | .defective => "defective" | .trap => "trap" | .incomplete => "incomplete"
def showPower (p : Power) : String :=
  s!"{repr p.kind} held by {repr p.holder}{if p.fiduciary then " as trustee" else ""}{if p.standard then " (with a standard)" else ""}"

/-- The scenario: a founder's $50 million stake, basis $5 million, growing 8% a year with a 3% taxable yield, held for
20 years; note interest at 4.6%; yield taxed at 23.8%, interest at 40.8%, gains at 23.8%; the exclusion already used. -/
def R : Rates := ⟨460, 2380, 4080, 2380, 0⟩
def path : List (Int × Int) := List.replicate 20 (800, 300)
def s0 : St := ⟨50000000, 10000000, 0, 0, 0⟩
def basis : Int := 5000000

def plans (i : Instrument) : List (String × Hold × Bool) :=
  [("keep the asset", ⟨false, false⟩, false), ("sell it to the trust for a note", ⟨true, grantorTrust i⟩, false)] ++
  (if canSwap i then [("sell it to the trust, then swap it back for cash just before death", ⟨true, grantorTrust i⟩, true)] else [])

def run : IO Unit := do
  let mut counts : List (String × Nat) := [("complete", 0), ("defective", 0), ("trap", 0), ("incomplete", 0)]
  for i in instruments do
    let k := showStatus (status i)
    counts := counts.map fun (n, c) => if n == k then (n, c + 1) else (n, c)
  IO.println s!"{instruments.length} instruments: {counts}"
  for (label, want) in [("defective (the grantor's for income tax, outside the estate)", Status.defective),
                        ("a trap (in the estate, not the grantor's for income tax)", Status.trap)] do
    IO.println s!"single powers that make a trust {label}:"
    for k in kinds do
      for h in holders do
        let ok := [false, true].flatMap fun f => [false, true].filterMap fun st =>
          if status [⟨k, h, f, st⟩] == want then some s!"{if f then "as trustee" else "not as trustee"}{if st then " + standard" else ""}" else none
        if !ok.isEmpty then IO.println s!"  {repr k} held by {repr h}: {if ok.length == 4 then "in any capacity" else ", ".intercalate ok}"
  -- every instrument, every plan
  let mut best : Int × String := (-1000000000000, "")
  let mut byStatus : List (String × Int) := []
  for i in instruments do
    for (name, h, swap) in plans i do
      let o := outcome R h (inEstate i) swap basis path s0
      let st := showStatus (status i)
      if byStatus.all (fun (n, v) => n != st ++ " / " ++ name || v < o.heirs) then
        byStatus := (byStatus.filter (fun (n, _) => n != st ++ " / " ++ name)) ++ [(st ++ " / " ++ name, o.heirs)]
      if o.heirs > best.1 then best := (o.heirs, s!"{name}, to a trust whose powers are {i.map showPower} ({st})")
  IO.println "best for the heirs, by status and plan:"
  for (n, v) in byStatus do IO.println s!"  {n}: ${v}"
  IO.println s!"best of all: ${best.1}: {best.2}"
  let keep := outcome R ⟨false, false⟩ false false basis path s0
  IO.println s!"keeping the asset: estate ${keep.estate}, estate tax ${keep.estateTax}, heirs ${keep.heirs}"

#eval run

end Legal.USTax.Trusts.Search
