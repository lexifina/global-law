import LegalProofs.USTax.WashSale.Theorems

/-!
# A blind search for a loss that can be taken without leaving the market

An investor holds three positions at a loss: an index fund, a single stock, and bitcoin. The question put to the
search: which sequences of trades recognise a loss this year while never leaving the investor without exposure to the
same market? The assets available are the three held, a second index fund tracking a different index of the same
market, and a bitcoin exchange-traded fund. The search tries every sequence of up to four trades on two trading days,
31 days apart, and keeps those that hold at least one unit of each market at the end of every trading day.

Which assets are securities and which are substantially identical is the data below; the search is told nothing else.

    lake env lean LegalProofs/USTax/WashSale/Search.lean
-/

namespace Legal.USTax.WashSale.Search
open Legal.USTax.WashSale

def names : Nat → String
  | 0 => "index fund A" | 1 => "index fund B" | 2 => "stock X" | 3 => "bitcoin" | _ => "bitcoin ETF"

/-- Index funds A and B track different indexes of the same market, so they are not substantially identical; bitcoin
is property, not a security (IRS Notice 2014-21); a bitcoin ETF's shares are securities. Prices are flat over the
period, so every economic result is the same and only the tax differs. -/
def M : Market where
  assets := fun | 0 => ⟨true, 0⟩ | 1 => ⟨true, 1⟩ | 2 => ⟨true, 2⟩ | 3 => ⟨false, 3⟩ | _ => ⟨true, 4⟩
  price := fun a _ => match a with | 0 | 1 => 7000 | 2 => 6000 | _ => 5000

def market : Nat → Nat | 0 | 1 => 0 | 2 => 2 | _ => 3
def markets : List (String × List Nat) := [("the stock market (index funds)", [0, 1]), ("stock X", [2]), ("bitcoin", [3, 4])]

/-- What is held at the start, each bought long ago for $10,000. -/
def start (assets : List Nat) : Book :=
  ⟨assets.filterMap (fun a => if a = 0 ∨ a = 2 ∨ a = 3 then some ⟨a, 1000 + a, 0, 10000⟩ else none), [], [], 0, 0, 0, 0⟩

def days : List Nat := [40, 71]

def sequences (assets : List Nat) : Nat → List (List Trade)
  | 0 => [[]]
  | n + 1 => [] :: ((sequences assets n).flatMap fun s =>
      (days.flatMap fun d => assets.flatMap fun a => [true, false].map fun b => (⟨d, a, b⟩ : Trade)).filterMap fun t =>
        match s.getLast? with
        | some l => if l.day ≤ t.day then some (s ++ [t]) else none
        | none => some [t])

/-- Units held of the market after all trades of each trading day. -/
def exposed (assets : List Nat) (ts : List Trade) : Bool :=
  let held0 := (start assets).lots.length
  days.all fun d =>
    let upto := ts.filter (·.day ≤ d)
    held0 + (upto.filter (·.buy)).length ≥ (upto.filter (!·.buy)).length + 1

def peak (assets : List Nat) (ts : List Trade) : Nat :=
  days.foldl (fun m d => let upto := ts.filter (·.day ≤ d)
    max m ((start assets).lots.length + (upto.filter (·.buy)).length - (upto.filter (!·.buy)).length)) 0

def showTrade (t : Trade) : String := s!"day {t.day}: {if t.buy then "buy" else "sell"} {names t.asset}"

def run : IO Unit := do
  for (name, assets) in markets do
    let mut best : Option (Int × Nat × Nat × List Trade × Book) := none
    let mut tried := 0
    for ts in (sequences assets 4).eraseDups do
      if exposed assets ts then
        match execute M ts (start assets) with
        | none => pure ()
        | some b =>
          tried := tried + 1
          let better := match best with
            | none => true
            | some (r, pk, n, _, _) => b.recognized < r || (b.recognized == r && (peak assets ts < pk ||
                (peak assets ts == pk && ts.length < n)))
          if better then best := some (b.recognized, peak assets ts, ts.length, ts, b)
    IO.println s!"== {name}: {tried} plans keep the exposure =="
    match best with
    | none => IO.println "  none"
    | some (r, _, _, ts, b) =>
      IO.println s!"  largest loss recognised, then least capital: ${-r}; disallowed ${b.disallowed}; units held at the peak: {peak assets ts}"
      for t in ts do IO.println s!"    {showTrade t}"
    -- the obvious trade, sell and buy back the same day, for comparison
    let a := assets.head!
    match execute M [⟨40, a, false⟩, ⟨40, a, true⟩] (start assets) with
    | some b => IO.println s!"  selling and buying back {names a} the same day: recognised ${-b.recognized}, disallowed ${b.disallowed}"
    | none => pure ()

#eval run

end Legal.USTax.WashSale.Search
