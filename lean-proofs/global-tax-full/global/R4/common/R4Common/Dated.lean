import R4Common.Basic
import TaxKernel.Global2

/-! # R4Common.Dated (R4 pass 20): rates that change during 2025, as the region's generators write them

Imported only by the generated modules that use a date window (`gen_country.py` wht rules / vat `knownTo`,
`gen_pkgs.py` finalWht `periods`); no other module imports it, so no other model changes.

* **Dated withholding on payments abroad** (`DatedWhtRule`, `datedWhtCharges`): each rule has a window
  `validFrom ≤ day < validTo` (ISO, `""` open). A payment's day is its record's `"date"` (in
  `company.paymentsAbroad`), else the entity's top-level `"date"`; the rules in force that day are the 2.0 `Wht`
  rules (first match). **A payment without a date is never guessed** (kernel 2.7.0 stacking and `AdvanceTax` rule): it
  is tried on 1 January and on every bound in the year; when every try books the same amount from a rule, that charge
  stands (statute + `undatedSameNote`), otherwise the 2.0 placeholder is booked, which `computeGlobal` drops and lists
  as grade C, and `datedWhtNotes` says why.
* **Dated final withholding on income items** (`DatedRate`, `datedFinalWhtFamily`): as `finalWhtFamily`, the rate
  read by the income record's `"date"` (`incomes[i].date`, else the entity's); an undated item is charged only when
  every try gives the same rate, else nothing and `datedFinalWhtNotes` lists it (grade C).
* **VAT known up to a day** (`vatKnownToFamily`): the rates are known before `knownTo` only. Basket lines dated
  before it are charged, dated lines on or after it are not (listed, grade C), undated lines are charged for the
  share of the year before it (`scaleDays`); a company's supplies only with an entity `"date"` before it.
* **Excise gaps** (`exciseGapNotes`): the lines of the goods whose rate is not known in a window (dated inside it, or
  undated while the window has days in the year) are listed (grade C).
-/

namespace R4
open Lean TaxKernel TaxKernel.Global

/-- The `dayOrd` of an ISO date (`none`: not a calendar day). -/
def isoDay? (s : String) : Option Nat := (isoYmd? s).map fun (y, m, d) => dayOrd y m d

/-- The day of a record: its `"date"`, else the entity's top-level `"date"`. -/
def recordDayOr (g : CanonGlobal) (j : Json) : Option Nat :=
  match isoDay? (strField j "date") with
  | some d => some d
  | none => (g.str? "date").bind isoDay?

/-- `validFrom ≤ d < validTo` (`""` open; the generators assert the bounds are dates). -/
def inWin (validFrom validTo : String) (d : Nat) : Bool :=
  (match isoDay? validFrom with | some f => decide (f ≤ d) | none => true) &&
  (match isoDay? validTo with | some t => decide (d < t) | none => true)

/-- The days an undated record is tried on: 1 January of `year` and every bound inside `year`. -/
def probeDays (year : Nat) (bounds : List String) : List Nat :=
  dayOrd year 1 1 :: bounds.filterMap fun s => match isoYmd? s with
    | some (y, m, d) => if y == year then some (dayOrd y m d) else none
    | none => none

def undatedSameNote : String := " (no date given: the same rate throughout 2025)"

/-! ## Withholding on payments abroad -/

structure DatedWhtRule where
  rule : WhtRule
  validFrom : String := ""
  validTo : String := ""
  deriving Repr, Inhabited

def whtAtDay (name : String) (rs : List DatedWhtRule) (d : Nat) : Wht :=
  { name := name, rules := (rs.filter fun r => inWin r.validFrom r.validTo d).map (·.rule) }

def whtBounds (rs : List DatedWhtRule) : List String := rs.flatMap fun r => [r.validFrom, r.validTo]

def paymentRecords (g : CanonGlobal) : List Json :=
  let cj := match g.raw.getObjVal? "company" with | .ok c => c | .error _ => Json.null
  (arrField cj "paymentsAbroad").toList

/-- One payment: the charge, and whether it is an undated payment the rules cannot price. -/
def datedWhtOne (name : String) (rs : List DatedWhtRule) (g : CanonGlobal) (p : Payment) (i : Nat) : Charge × Bool :=
  match recordDayOr g ((paymentRecords g).getD i Json.null) with
  | some d => ((whtAtDay name rs d).chargeOf p i, false)
  | none =>
    let cs := (probeDays g.year (whtBounds rs)).map fun d => (whtAtDay name rs d).chargeOf p i
    match cs with
    | c :: rest =>
      if !c.unreadWht && rest.all (fun c' => !c'.unreadWht && c'.due == c.due) then
        ({ c with statute := c.statute ++ undatedSameNote }, false)
      else (({ name := name, rules := [] } : Wht).chargeOf p i, rest.any (fun c' => !c'.unreadWht) || !c.unreadWht)
    | [] => (({ name := name, rules := [] } : Wht).chargeOf p i, false)

def datedWhtCharges (name : String) (rs : List DatedWhtRule) (g : CanonGlobal) : List Charge :=
  g.company.paymentsAbroad.zipIdx.map fun (p, i) => (datedWhtOne name rs g p i).1

/-- Undated payments whose rate changes during the year (their placeholder is listed as grade C by the kernel). -/
def datedWhtNotes (name : String) (rs : List DatedWhtRule) (change : String) (g : CanonGlobal) : List String :=
  if g.entity != .company then [] else
  g.company.paymentsAbroad.zipIdx.filterMap fun (p, i) =>
    let r := datedWhtOne name rs g p i
    if r.2 then some s!"{name}: {r.1.event} has no date and the rate changes during 2025 ({change}): not computed (grade C)"
    else none

/-! ## Final withholding on income items -/

structure DatedRate where
  rateBp : Int
  validFrom : String := ""
  validTo : String := ""
  statute : String := ""
  deriving Repr, Inhabited

def DatedRate.at (ps : List DatedRate) (d : Nat) : Option DatedRate := ps.find? fun p => inWin p.validFrom p.validTo d

/-- An undated item: the rate when every try finds the same one. -/
def DatedRate.undated (ps : List DatedRate) (year : Nat) : Option DatedRate :=
  match (probeDays year (ps.flatMap fun p => [p.validFrom, p.validTo])).map (DatedRate.at ps) with
  | some p :: rest => if rest.all (fun q => match q with | some q => q.rateBp == p.rateBp | none => false)
      then some { p with statute := p.statute ++ undatedSameNote } else none
  | _ => none

def datedRateOf (ps : List DatedRate) (g : CanonGlobal) (i : Nat) : Option DatedRate :=
  match recordDayOr g ((arrField g.raw "incomes").toList.getD i Json.null) with
  | some d => DatedRate.at ps d
  | none => DatedRate.undated ps g.year

def datedFinalWhtFamily (kind : IncomeKind) (name : String) (ps : List DatedRate) : Family :=
  { name := s!"1100 {name}", covers := [],
    run := fun _ g _ =>
      if g.entity == .company then [] else
      (g.incomes.zipIdx.filter (fun (x, _) => x.kind == kind && !x.foreign)).filterMap fun (x, i) =>
        (datedRateOf ps g i).map fun p =>
          charge .pit name x.amount id (fun y => divR .down (p.rateBp * pos y) BP) (event := s!"income {i + 1} ({kind.name})")
            (statute := p.statute) }

def datedFinalWhtNotes (kind : IncomeKind) (name : String) (ps : List DatedRate) (why : String) (g : CanonGlobal) : List String :=
  if g.entity == .company then [] else
  (g.incomes.zipIdx.filter (fun (x, _) => x.kind == kind && !x.foreign)).filterMap fun (_, i) =>
    if (datedRateOf ps g i).isSome then none else
    some s!"1100 {name}: income {i + 1} ({kind.name}): {why} (grade C)"

/-! ## VAT known up to a day -/

def vatKnownLines (knownTo : String) (g : CanonGlobal) : List Spend :=
  let n := daysInYear g.year
  let k := startDay g.year knownTo
  (consumptionX g).filterMap fun (s, x) => match dayOfYear? g.year x.date with
    | some d => if d < k then some s else none
    | none => some { s with amount := scaleDays s.amount k n }

def vatKnownToFamily (v : Vat) (statute knownTo : String) : Family :=
  { name := s!"5111 {v.name}", covers := [.vat],
    run := fun _ g _ =>
      let n := daysInYear g.year
      let k := startDay g.year knownTo
      let undated := (consumptionX g).any fun (_, x) => (dayOfYear? g.year x.date).isNone
      (if g.consumption.isEmpty then [] else
        [v.basketCharge (vatKnownLines knownTo g) (statute ++ (if undated then s!"; {k}/{n} of the undated basket" else ""))])
      ++ (if g.entity == .company && !g.company.sales.isEmpty then
            match (g.str? "date").bind (dayOfYear? g.year) with
            | some d => if d < k then [v.businessCharge g.company statute] else []
            | none => []
          else []) }

def vatKnownToNotes (name knownTo why : String) (g : CanonGlobal) : List String :=
  let k := startDay g.year knownTo
  let lines := (consumptionX g).zipIdx.filterMap fun ((s, x), i) => match dayOfYear? g.year x.date with
    | some d => if k ≤ d then some s!"5111 {name}: basket line {i + 1} ({s.good.name}) dated {x.date}: {why} (grade C)" else none
    | none => none
  let undated := if (consumptionX g).any (fun (_, x) => (dayOfYear? g.year x.date).isNone) && k < daysInYear g.year
    then [s!"5111 {name}: undated basket lines are charged for {k}/{daysInYear g.year} of the year; the rest of the year: {why} (grade C)"] else []
  let sup := if g.entity == .company && !g.company.sales.isEmpty &&
      (match (g.str? "date").bind (dayOfYear? g.year) with | some d => k ≤ d | none => true)
    then [s!"5111 {name}: supplies without an entity date before {knownTo}: {why} (grade C)"] else []
  lines ++ undated ++ sup

/-! ## Excise lines whose rate is not known in a window -/

def winText (validFrom validTo : String) : String :=
  if validFrom == "" then s!"before {validTo}" else if validTo == "" then s!"from {validFrom}" else s!"from {validFrom} to before {validTo}"

def exciseGapNotes (name : String) (goods : List Good) (validFrom validTo why : String) (g : CanonGlobal) : List String :=
  (consumptionX g).zipIdx.filterMap fun ((s, x), i) =>
    if !goods.contains s.good then none else
    if !(({ good := s.good, validFrom := validFrom, validTo := validTo } : ExciseRule).inWindow g.year x) then none else
    some (if (dayOfYear? g.year x.date).isSome
      then s!"5121 {name}: basket line {i + 1} ({s.good.name}) dated {x.date}: {why} (grade C)"
      else s!"5121 {name}: basket line {i + 1} ({s.good.name}) has no date: the part of the year {winText validFrom validTo}: {why} (grade C)")

/-! ## Checks -/

private def tRules : List DatedWhtRule :=
  [{ rule := { kind := .dividend, rateBp := 1000, statute := "old" }, validTo := "2025-08-07" },
   { rule := { kind := .dividend, rateBp := 1500, statute := "new" }, validFrom := "2025-08-07" },
   { rule := { kind := .interest, rateBp := 1000, statute := "old i" }, validTo := "2025-08-07" },
   { rule := { kind := .interest, rateBp := 1000, statute := "new i" }, validFrom := "2025-08-07" }]

private def tLine (s : String) : CanonGlobal :=
  match Json.parse s with
  | .ok j => (match parseGlobal j with | .ok g => g | .error _ => default)
  | .error _ => default

private def tPay : CanonGlobal := tLine "{\"id\":\"c\",\"entity\":\"company\",\"company\":{\"paymentsAbroad\":[{\"kind\":\"dividend\",\"amount\":1000000,\"date\":\"2025-08-06\"},{\"kind\":\"dividend\",\"amount\":1000000,\"date\":\"2025-08-07\"},{\"kind\":\"dividend\",\"amount\":1000000},{\"kind\":\"interest\",\"amount\":1000000}]}}"

-- 6 August: 10 %; 7 August: 15 %; undated dividend: placeholder (0, grade C); undated interest: 10 % both sides
#guard (datedWhtCharges "w" tRules tPay).map (·.due) == [100000, 150000, 0, 100000]
#guard ((datedWhtCharges "w" tRules tPay).getD 2 default).unreadWht
#guard (datedWhtNotes "w" tRules "7 August 2025" tPay).length == 1

private def tRates : List DatedRate := [{ rateBp := 1000, validTo := "2025-08-07" }, { rateBp := 1500, validFrom := "2025-08-07" }]
private def tInc : CanonGlobal := tLine "{\"id\":\"h\",\"household\":{\"id\":\"h\",\"adults\":[{\"age\":40}]},\"incomes\":[{\"kind\":\"dividend\",\"amount\":200000,\"date\":\"2025-03-01\"},{\"kind\":\"dividend\",\"amount\":200000,\"date\":\"2025-12-01\"},{\"kind\":\"dividend\",\"amount\":200000}]}"
#guard ((datedFinalWhtFamily .dividend "d" tRates).run [] tInc []).map (·.due) == [20000, 30000]
#guard (datedFinalWhtNotes .dividend "d" tRates "x" tInc).length == 1

private def tVat : Vat := { name := "Sales tax", standard := 1800 }
private def tBasket : CanonGlobal := tLine "{\"id\":\"h\",\"household\":{\"id\":\"h\",\"adults\":[{\"age\":40}]},\"consumption\":[{\"good\":\"other\",\"amount\":118000,\"date\":\"2025-03-01\"},{\"good\":\"other\",\"amount\":118000,\"date\":\"2025-09-01\"},{\"good\":\"other\",\"amount\":365000}]}"
-- dated March line 18 000; September line not charged; undated 365 000 × 181/365 = 181 000 → 18/118 of it = 27 610
#guard ((vatKnownToFamily tVat "s" "2025-07-01").run [] tBasket []).map (·.due) == [18000 + 27610]
#guard (vatKnownToNotes "Sales tax" "2025-07-01" "x" tBasket).length == 2

end R4
