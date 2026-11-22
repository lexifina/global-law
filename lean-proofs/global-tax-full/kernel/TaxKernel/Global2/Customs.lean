import TaxKernel.Global2.ExciseRule
import TaxKernel.Global2.Fx

/-!
# TaxKernel.Global2.Customs (2.8.0, 2026-11-21): customs import duties on the basket (OECD 5123)

Customs duties (OECD Revenue Statistics 5123, "import duties") are levied on imported goods by tariff classification and
origin; before 2.8.0 a basket line carried neither, so no model could compute one. `Spend` is unchanged: as for the
2.1.0 line extras (`Basket`), the facts are read from the line's own JSON.

**Basket-line fields** (all optional; `CustomsX`, `consumptionC g`):

| JSON field on a `consumption` line | meaning |
|---|---|
| `"hs"` | the Harmonized System code of the good, **a string** of 2, 4, 6 or 8 digits (a national 10-digit line is accepted; dots, spaces and dashes are ignored: `"2203.00"` = `"220300"`) |
| `"origin"` | ISO 3166 code of the country of origin (`"JM"`, `"USA"`; read in upper case), or `"domestic"` |
| `"imported"` | (2.1.0, unchanged) the good is imported; a foreign `"origin"` also makes the line imported |
| `"customsValue"` | the customs value of the line, money (default: the price before tax, below) |

**The tariff** (`TariffRule`), declared by the model:
* `lines`: MFN tariff lines `{ hs := "2203", adValoremBp, perUnitNum/perUnitDen (money per canonical unit), perKgNum/perKgDen
  (money per kg; mass = the line's `"massG"`, else quantity × `mgPerUnit`), higherOf (mixed duty "x % or y, whichever is
  greater"; else the sum), statute }`. **The longest heading that prefixes the line's code wins** (`hsBest`,
  `hsBest_longest`); `otherBp` the rate for goods no line covers (−1: none, grade C);
* `preferences`: regimes keyed on origin, `{ name, partners := ["JM", "BB", …], rateBp := 0, byHs, hsOnly, hsExcept,
  keepSpecific, statute }` (CARICOM, MERCOSUR, the EU, ECOWAS, SACU …): a line originating in a partner pays the
  preferential rate (by HS prefix in `byHs`, else `rateBp`; specific parts only with `keepSpecific`), or MFN where that is
  lower (the importer claims the lower; `pickLower_le`);
* `mfnIfOriginUnknown`: the model's convention when a preference could apply and the line gives no origin (MFN; else grade C);
* `dutyInVatBase` (default true): customs duty enters the VAT base (as it usually does); `vatBp` or `vatOf` (a 2.0 `Vat`:
  the good's class) is the import VAT used to take the value out of a tax-inclusive price;
* `goods` (`[]`: every good), `country` (an origin equal to it is domestic), `oecd := .goodsOther` (output code 5120, the
  5122-5128 heading that holds 5123), `level`, `statute`.

**The customs value.** `"customsValue"` when the line gives it. Otherwise the price before tax `b`: the basket amount `p`
is tax-inclusive, with the duty `d = a·b + s` (`a` ad valorem, `s` the specific part) and VAT `v` inside it:
`p = (b + d)(1 + v)` when the duty is in the VAT base, so `b = (p/(1+v) − s)/(1+a)`; `p = b(1+v) + d` when it is not, so
`b = (p − s)/(1+v+a)`; a mixed `higherOf` duty takes the branch that is consistent. Rounded down at each step (as
`ExciseRule.beforeTax`). Where an excise is also inside the price, give `"customsValue"`. The duty is `⌊a·b⌋ + s`
(`higherOf`: `max(⌊a·b⌋, s)`).

**Never guessed (grade C, `TariffRule.unknown`, "5120 <name>: line 3 (spirits): … (grade C)")**: an imported line without
`"hs"`, or one that is not an HS code; a code no line covers when `otherBp < 0`; a code coarser than the tariff where the
finer lines differ (`"22"` against `2203` and `2204` at different rates); a specific duty without the quantity or mass it
needs; the origin when a preference could apply and the model declares no MFN convention; `"imported": true` with origin
`"domestic"`. **Domestic lines pay nothing** (`lineOutcome_domestic`, `lineOutcome_notImported`).

One charge per dutiable line: `base = relieved` = the customs value, `due` = the duty, event `"line <i> (<good>)"`, bearer
consumer, statute = the rule's and the tariff line's statute, the heading applied and the preference.
`GlobalModel.withCustoms m [t]` adds the family and the grade-C lines. With the duty outside the VAT base, the 2.0 basket
VAT (`Vat.embedded`, VAT on the whole price) overstates by `t.vatOverstated g`.

Theorems: `hsBest_none`, `hsBest_covers`, `hsBest_mem`, `hsBest_longest`, `customsValueOf_given`, `customsDutyOn_nonneg`,
`pickLower_le`, `lineOutcome_domestic`, `lineOutcome_notImported`, `lineOutcome_noHs`, `consumptionC_fst`,
`TariffRule.charges_ofCanon`, `unknown_ofCanon`, `withCustoms_pit`, `withCustoms_ofCanon`.
-/

namespace TaxKernel.Global
open Lean TaxKernel

/-! ## HS codes -/

/-- The digits of an HS code as written (`"2203.00"`, `"2203 00"`, `"2203-00"` → `"220300"`). -/
def hsDigits (s : String) : String := String.ofList (s.toList.filter fun c => c != '.' && c != ' ' && c != '-')

/-- An HS code of 2, 4, 6, 8 (or a national 10) digits; `none` otherwise. -/
def hsNormalize (s : String) : Option String :=
  let d := hsDigits s
  if [2, 4, 6, 8, 10].contains d.length && d.toList.all Char.isDigit then some d else none

/-- The heading `p` covers the code `hs` (it is a prefix of it). -/
def hsCovers (p hs : String) : Bool := hs.startsWith (hsDigits p)

/-- The heading `p` is strictly finer than the code `hs` (the code is too coarse to choose against it). -/
def hsFiner (p hs : String) : Bool := decide (hs.length < (hsDigits p).length) && (hsDigits p).startsWith hs

/-- **The longest heading of the table that covers `hs`** (ties: the first). -/
def hsBest {α : Type} : List (String × α) → String → Option (String × α)
  | [], _ => none
  | (p, a) :: rest, hs =>
    match hsBest rest hs with
    | some (q, b) =>
      if hsCovers p hs && decide ((hsDigits q).length ≤ (hsDigits p).length) then some (p, a) else some (q, b)
    | none => if hsCovers p hs then some (p, a) else none

theorem hsBest_none {α : Type} (l : List (String × α)) (hs : String) (h : hsBest l hs = none) :
    ∀ x ∈ l, hsCovers x.1 hs = false := by
  induction l with
  | nil => simp
  | cons hd rest ih =>
    obtain ⟨p, a⟩ := hd
    simp only [hsBest] at h
    split at h
    · split at h <;> simp at h
    · rename_i hr
      intro x hx
      simp only [List.mem_cons] at hx
      rcases hx with hx | hx
      · subst hx; split at h <;> simp_all
      · exact ih hr x hx

theorem hsBest_covers {α : Type} (l : List (String × α)) (hs : String) (p : String) (a : α)
    (h : hsBest l hs = some (p, a)) : hsCovers p hs = true := by
  induction l with
  | nil => simp [hsBest] at h
  | cons hd rest ih =>
    obtain ⟨p0, a0⟩ := hd
    simp only [hsBest] at h
    split at h
    · rename_i q b hr
      split at h
      · rename_i hc
        simp only [Option.some.injEq, Prod.mk.injEq] at h
        obtain ⟨rfl, rfl⟩ := h
        simp only [Bool.and_eq_true] at hc
        exact hc.1
      · simp only [Option.some.injEq, Prod.mk.injEq] at h
        obtain ⟨rfl, rfl⟩ := h
        exact ih hr
    · split at h
      · rename_i hc
        simp only [Option.some.injEq, Prod.mk.injEq] at h
        obtain ⟨rfl, rfl⟩ := h
        exact hc
      · simp at h

theorem hsBest_mem {α : Type} (l : List (String × α)) (hs : String) (p : String) (a : α)
    (h : hsBest l hs = some (p, a)) : (p, a) ∈ l := by
  induction l with
  | nil => simp [hsBest] at h
  | cons hd rest ih =>
    obtain ⟨p0, a0⟩ := hd
    simp only [hsBest] at h
    split at h
    · rename_i q b hr
      split at h
      · simp only [Option.some.injEq, Prod.mk.injEq] at h
        obtain ⟨rfl, rfl⟩ := h
        simp
      · simp only [Option.some.injEq, Prod.mk.injEq] at h
        obtain ⟨rfl, rfl⟩ := h
        exact List.mem_cons_of_mem _ (ih hr)
    · split at h
      · simp only [Option.some.injEq, Prod.mk.injEq] at h
        obtain ⟨rfl, rfl⟩ := h
        simp
      · simp at h

/-- **The longest prefix wins**: no heading of the table that covers the code is longer than the one chosen. -/
theorem hsBest_longest {α : Type} (l : List (String × α)) (hs : String) (q : String) (b : α)
    (h : hsBest l hs = some (q, b)) : ∀ x ∈ l, hsCovers x.1 hs = true →
      (hsDigits x.1).length ≤ (hsDigits q).length := by
  induction l generalizing q b with
  | nil => simp
  | cons hd rest ih =>
    obtain ⟨p0, a0⟩ := hd
    intro x hx hcx
    simp only [hsBest] at h
    split at h
    · rename_i q1 b1 hr
      split at h
      · rename_i hc
        simp only [Option.some.injEq, Prod.mk.injEq] at h
        obtain ⟨rfl, rfl⟩ := h
        simp only [Bool.and_eq_true, decide_eq_true_eq] at hc
        simp only [List.mem_cons] at hx
        rcases hx with rfl | hx
        · exact Nat.le_refl _
        · exact Nat.le_trans (ih q1 b1 hr x hx hcx) hc.2
      · rename_i hc
        simp only [Option.some.injEq, Prod.mk.injEq] at h
        obtain ⟨rfl, rfl⟩ := h
        simp only [List.mem_cons] at hx
        rcases hx with rfl | hx
        · simp only [Bool.and_eq_true, decide_eq_true_eq, not_and] at hc
          exact Nat.le_of_lt (Nat.lt_of_not_le (hc hcx))
        · exact ih _ _ hr x hx hcx
    · rename_i hr
      split at h
      · simp only [Option.some.injEq, Prod.mk.injEq] at h
        obtain ⟨rfl, rfl⟩ := h
        simp only [List.mem_cons] at hx
        rcases hx with rfl | hx
        · exact Nat.le_refl _
        · have := hsBest_none rest hs hr x hx
          simp [this] at hcx
      · simp at h

/-! ## The line's customs facts -/

/-- The customs facts of a basket line (2.8.0). -/
structure CustomsX where
  /-- `"hs"` as given (`""`: not given; a JSON number is read as its digits) -/
  hsRaw : String := ""
  /-- `"origin"`: an ISO code in upper case, `"domestic"`, or `""` (not given) -/
  origin : String := ""
  /-- `"customsValue"`, money (−1: not given) -/
  customsValue : Int := -1
  deriving Repr, Inhabited, BEq

/-- An origin as the rule compares it: `"domestic"` (any case) or the code in upper case, without spaces. -/
def normOrigin (s : String) : String :=
  let o := String.ofList (s.toList.filter (· != ' '))
  if o.toLower == "domestic" then "domestic" else o.toUpper

def CustomsX.ofJson (j : Json) : CustomsX :=
  { hsRaw := match j.getObjVal? "hs" with
      | .ok (.str s) => s
      | .ok (.num n) => toString (numToInt n)
      | _ => "",
    origin := normOrigin (strField j "origin"),
    customsValue := let v := intField j "customsValue" (-1); if 0 ≤ v then v else -1 }

/-- Each basket line with its 2.1.0 extras and its customs facts, in basket order. -/
def consumptionC (g : CanonGlobal) : List (Spend × SpendX × CustomsX) :=
  let js := (arrField g.raw "consumption").toList
  (consumptionX g).zipIdx.map fun ((s, x), i) => (s, x, CustomsX.ofJson (js.getD i Json.null))

theorem consumptionC_fst (g : CanonGlobal) : (consumptionC g).map (·.1) = g.consumption := by
  rw [← consumptionX_fst g]
  simp only [consumptionC, List.map_map, Function.comp_def]
  rw [show (fun x : (Spend × SpendX) × Nat => x.1.fst) = Prod.fst ∘ Prod.fst from rfl, ← List.map_map,
    List.zipIdx_map_fst]

/-! ## The tariff -/

/-- An MFN tariff line: an HS heading and its duties. -/
structure TariffLine where
  /-- the heading (2-10 digits; dots allowed): the line covers every code it prefixes -/
  hs : String
  adValoremBp : Int := 0
  /-- specific duty, `perUnitNum / perUnitDen` money per canonical unit (litre, stick, kWh) -/
  perUnitNum : Int := 0
  perUnitDen : Int := 1
  /-- specific duty per kg, `perKgNum / perKgDen` (per tonne: `perKgDen × 1000`) -/
  perKgNum : Int := 0
  perKgDen : Int := 1
  /-- statutory mass of one canonical unit, mg (when the line gives no `"massG"`) -/
  mgPerUnit : Int := 0
  /-- mixed duty: the higher of the ad valorem and the specific parts; else their sum -/
  higherOf : Bool := false
  statute : String := ""
  /-- 2.9.0 (R2-GAP-1): the line is in force for goods entered on `validFrom ≤ date < validTo` (ISO, the basket line's
  `"date"`; `""`: open) -/
  validFrom : String := ""
  validTo : String := ""
  /-- 2.9.0: the specific amounts (`perUnitNum`, `perKgNum`) are in this currency (ISO 4217; `""`: the model's), converted
  at the entity's `"fxRates"` or the rule's `fxRate` (none: grade C) -/
  currency : String := ""
  deriving Repr, Inhabited, BEq

namespace TariffLine

/-- Same duty (the statute and the dates aside). -/
def sameDuty (a b : TariffLine) : Bool :=
  a.adValoremBp == b.adValoremBp && a.perUnitNum == b.perUnitNum && a.perUnitDen == b.perUnitDen
    && a.perKgNum == b.perKgNum && a.perKgDen == b.perKgDen && a.mgPerUnit == b.mgPerUnit && a.higherOf == b.higherOf
    && a.currency == b.currency

/-- The specific part of the duty on a basket line; an error names the fact it needs and the line does not give. -/
def specific? (l : TariffLine) (s : Spend) (x : SpendX) : Except String Int :=
  let pu : Except String Int :=
    if l.perUnitNum == 0 then .ok 0
    else if s.quantity ≤ 0 then .error "quantity not given"
    else .ok (divR .down (s.quantity * l.perUnitNum) (l.perUnitDen * 1000))
  let mass : Option Int :=
    if 0 ≤ x.massG then some x.massG
    else if 0 < l.mgPerUnit && 0 < s.quantity then some (divR .down (s.quantity * l.mgPerUnit) 1000000) else none
  let pk : Except String Int :=
    if l.perKgNum == 0 then .ok 0
    else match mass with
      | some m => .ok (divR .down (m * l.perKgNum) (l.perKgDen * 1000))
      | none => .error "massG not given"
  match pu, pk with
  | .ok a, .ok b => .ok (a + b)
  | .error e, _ => .error e
  | _, .error e => .error e

end TariffLine

/-- A preference regime keyed on origin (a free-trade agreement, a customs union's common external tariff). -/
structure TariffPreference where
  /-- e.g. `"CARICOM (Revised Treaty of Chaguaramas)"` -/
  name : String
  /-- ISO codes of the partner states, as the lines' `"origin"` gives them -/
  partners : List String
  /-- the preferential ad valorem rate, bp (0: duty-free) -/
  rateBp : Int := 0
  /-- preferential rates by HS heading (the longest prefix wins; else `rateBp`) -/
  byHs : List (String × Int) := []
  /-- the headings the preference covers (`[]`: every good) -/
  hsOnly : List String := []
  /-- headings excluded from it -/
  hsExcept : List String := []
  /-- the MFN specific parts still apply to partner goods -/
  keepSpecific : Bool := false
  statute : String := ""
  /-- 2.9.0 (R2-GAP-1): in force for goods entered on `validFrom ≤ date < validTo` (`""`: open) -/
  validFrom : String := ""
  validTo : String := ""
  deriving Repr, Inhabited, BEq

namespace TariffPreference

def hasPartner (p : TariffPreference) (origin : String) : Bool := p.partners.any (·.toUpper == origin)

/-- Does the preference cover the code? `none`: the code is too coarse to tell (a finer heading is listed or excluded). -/
def coversHs? (p : TariffPreference) (hs : String) : Option Bool :=
  if p.hsExcept.any (hsCovers · hs) then some false
  else if p.hsExcept.any (hsFiner · hs) then none
  else if p.hsOnly.isEmpty || p.hsOnly.any (hsCovers · hs) then some true
  else if p.hsOnly.any (hsFiner · hs) then none
  else some false

/-- The preferential ad valorem rate for the code (an error: the code is coarser than `byHs` where the rates differ). -/
def rateFor (p : TariffPreference) (hs : String) : Except String Int :=
  let r := match hsBest p.byHs hs with | some (_, r) => r | none => p.rateBp
  let finer := p.byHs.filter fun (q, _) => hsFiner q hs
  if finer.any (·.2 != r) then .error s!"hs {hs} is coarser than the {p.name} rates ({", ".intercalate (finer.map fun q => hsDigits q.1)} differ)"
  else .ok r

end TariffPreference

/-- 2.9.0 (R2-GAP-1): an additional duty **added** to the MFN or preferential duty, by origin, HS heading and date (US
HTSUS chapter 99: IEEPA, reciprocal and s. 232 duties; CA surtax orders on US and Chinese goods). -/
structure TariffSurcharge where
  name : String
  /-- ISO codes of the origins it applies to (`[]`: every foreign origin) -/
  origins : List String := []
  /-- origins it does not apply to -/
  exceptOrigins : List String := []
  /-- the headings it covers (`[]`: every good) -/
  hsOnly : List String := []
  /-- headings excluded from it -/
  hsExcept : List String := []
  adValoremBp : Int := 0
  /-- specific parts, as `TariffLine` (money per canonical unit / per kg, in `currency`) -/
  perUnitNum : Int := 0
  perUnitDen : Int := 1
  perKgNum : Int := 0
  perKgDen : Int := 1
  mgPerUnit : Int := 0
  currency : String := ""
  /-- goods entered on `validFrom ≤ date < validTo` (ISO; `""`: open) -/
  validFrom : String := ""
  validTo : String := ""
  /-- not charged on a line that claims one of these preferences (by name; `"*"`: any): USMCA-qualifying goods -/
  exceptPreferences : List String := []
  statute : String := ""
  deriving Repr, Inhabited, BEq

namespace TariffSurcharge

/-- Its specific parts as a tariff line (to reuse `TariffLine.specific?`). -/
def asLine (u : TariffSurcharge) : TariffLine :=
  { hs := "", perUnitNum := u.perUnitNum, perUnitDen := u.perUnitDen, perKgNum := u.perKgNum, perKgDen := u.perKgDen,
    mgPerUnit := u.mgPerUnit, currency := u.currency }

/-- Does it cover the code? `none`: the code is too coarse to tell. -/
def coversHs? (u : TariffSurcharge) (hs : String) : Option Bool :=
  ({ name := u.name, partners := [], hsOnly := u.hsOnly, hsExcept := u.hsExcept } : TariffPreference).coversHs? hs

/-- It applies whatever the origin (no origin list, no exception). -/
def anyOrigin (u : TariffSurcharge) : Bool := u.origins.isEmpty && u.exceptOrigins.isEmpty

/-- It applies to goods of this (foreign, upper-case) origin. -/
def hasOrigin (u : TariffSurcharge) (origin : String) : Bool :=
  (u.origins.isEmpty || u.origins.any (·.toUpper == origin)) && !u.exceptOrigins.any (·.toUpper == origin)

/-- Waived when the line claims the preference named `p`. -/
def waivedBy (u : TariffSurcharge) (p : String) : Bool := u.exceptPreferences.any fun n => n == "*" || n == p

end TariffSurcharge

/-! ### Date windows (2.9.0) -/

/-- In force on day `d` of `year` (0-based): `validFrom ≤ d < validTo`, an empty bound open. -/
def inForceOn (year : Nat) (validFrom validTo : String) (d : Nat) : Bool :=
  (validFrom == "" || decide (startDay year validFrom ≤ d)) && (validTo == "" || decide (d < endDay year validTo))

theorem inForceOn_open (year d : Nat) : inForceOn year "" "" d = true := by simp [inForceOn]

/-! ## Value and duty -/

/-- **The customs value**: the line's `"customsValue"` (`cv ≥ 0`), else the price before tax taken out of the
tax-inclusive price `p` (VAT `v`, ad valorem `a`, specific part `sp`; the duty in the VAT base or not). -/
def customsValueOf (inBase higherOf : Bool) (p v a sp cv : Int) : Int :=
  if 0 ≤ cv then cv else
  let pp := pos p
  if inBase then
    let net := divR .down (pp * BP) (BP + v)
    if higherOf then
      let bA := divR .down (net * BP) (BP + a)
      if sp ≤ divR .down (a * bA) BP then bA else pos (net - sp)
    else divR .down (pos (net - sp) * BP) (BP + a)
  else
    if higherOf then
      let bA := divR .down (pp * BP) (BP + v + a)
      if sp ≤ divR .down (a * bA) BP then bA else divR .down (pos (pp - sp) * BP) (BP + v)
    else divR .down (pos (pp - sp) * BP) (BP + v + a)

/-- The duty on a customs value `b`: ad valorem plus specific, or the higher of the two. -/
def customsDutyOn (higherOf : Bool) (a sp b : Int) : Int :=
  let av := divR .down (a * b) BP
  if higherOf then max av sp else av + sp

theorem customsValueOf_given (inBase higherOf : Bool) (p v a sp cv : Int) (h : 0 ≤ cv) :
    customsValueOf inBase higherOf p v a sp cv = cv := by simp [customsValueOf, h]

theorem customsDutyOn_nonneg (h : Bool) (a sp b : Int) (ha : 0 ≤ a) (hs : 0 ≤ sp) (hb : 0 ≤ b) :
    0 ≤ customsDutyOn h a sp b := by
  have : 0 ≤ divR .down (a * b) BP := by
    simp only [divR, BP]; exact Int.ediv_nonneg (Int.mul_nonneg ha hb) (by omega)
  unfold customsDutyOn; cases h <;> simp <;> omega

/-- The importer claims the lower of the MFN and the preferential duty: `(value, duty, note)`. -/
def pickLower (bM dM bP dP : Int) (noteP noteM : String) : Int × Int × String :=
  if dP ≤ dM then (bP, dP, noteP) else (bM, dM, noteM)

theorem pickLower_le (bM dM bP dP : Int) (nP nM : String) : (pickLower bM dM bP dP nP nM).2.1 ≤ dM := by
  unfold pickLower; split <;> simp <;> omega

/-! ## The rule -/

/-- What the rule does with one basket line. -/
inductive CustomsOutcome where
  /-- no duty: a domestic line, a good the rule does not take -/
  | none
  /-- the duty: customs value, duty, statute -/
  | due (value duty : Int) (statute : String)
  /-- not computed: why (grade C) -/
  | unknown (why : String)
  deriving Repr, Inhabited, BEq

structure TariffRule where
  name : String := "customs duty"
  /-- the model's own ISO code (an origin equal to it is domestic) -/
  country : String := ""
  /-- the MFN tariff lines -/
  lines : List TariffLine := []
  /-- the ad valorem rate for goods no line covers, bp (−1: none, grade C) -/
  otherBp : Int := -1
  preferences : List TariffPreference := []
  /-- a preference could apply and the line gives no origin: MFN (the model's declared convention); else grade C -/
  mfnIfOriginUnknown : Bool := false
  /-- the duty enters the VAT base -/
  dutyInVatBase : Bool := true
  /-- import VAT, bp (to take the value out of the tax-inclusive price) -/
  vatBp : Int := 0
  /-- a 2.0 `Vat` whose class for the good gives the rate (instead of `vatBp`) -/
  vatOf : Option Vat := none
  /-- the goods the rule takes (`[]`: all) -/
  goods : List Good := []
  oecd : Oecd := .goodsOther
  level : Level := .central
  statute : String := ""
  /-- 2.9.0 (R2-GAP-1): additional duties added to the MFN or preferential duty -/
  surcharges : List TariffSurcharge := []
  /-- 2.9.0: the rate for amounts in a foreign currency when the entity gives none (`"fxRates"` wins) -/
  fxRate : Option FxRate := none
  deriving Inhabited

namespace TariffRule

def takesGood (t : TariffRule) (g : Good) : Bool := t.goods.isEmpty || t.goods.contains g

def vatRate (t : TariffRule) (g : Good) : Int :=
  match t.vatOf with
  | some v => v.rateOf g
  | none => t.vatBp

/-- An origin that is domestic: `"domestic"` or the model's own code. -/
def isDomestic (t : TariffRule) (c : CustomsX) : Bool :=
  c.origin == "domestic" || (t.country != "" && c.origin == t.country.toUpper)

/-- The MFN line for a code: (heading, line); an error when none covers it or the code is too coarse. -/
def mfnLine (t : TariffRule) (hs : String) : Except String (String × TariffLine) :=
  let finer := t.lines.filter fun l => hsFiner l.hs hs
  let heads := ", ".intercalate (finer.map fun l => hsDigits l.hs)
  let chosen : Option (String × TariffLine) :=
    match hsBest (t.lines.map fun l => (l.hs, l)) hs with
    | some r => some r
    | none => if 0 ≤ t.otherBp then some ("", { hs := "", adValoremBp := t.otherBp }) else none
  match chosen with
  | none =>
    if finer.isEmpty then .error s!"no tariff line for hs {hs}"
    else .error s!"hs {hs} is coarser than the tariff (lines {heads})"
  | some (p, l) =>
    if finer.any (fun f => !f.sameDuty l) then .error s!"hs {hs} is coarser than the tariff (lines {heads} differ)"
    else .ok (p, l)

/-- The preference that applies: `(none, note)` MFN; `(some (p, rate), "")` the preference; an error: grade C. -/
def prefFor (t : TariffRule) (hs origin : String) : Except String (Option (TariffPreference × Int) × String) :=
  if origin == "" then
    let maybe := t.preferences.filter fun p => p.coversHs? hs != some false
    let names := ", ".intercalate (maybe.map (·.name))
    if maybe.isEmpty then .ok (none, "")
    else if t.mfnIfOriginUnknown then .ok (none, s!"; origin not given: MFN, the model's convention ({names} not applied)")
    else .error s!"origin not given (a preference may apply: {names})"
  else
    match (t.preferences.filter fun p => p.hasPartner origin && p.coversHs? hs != some false).head? with
    | none => .ok (none, "")
    | some p =>
      match p.coversHs? hs with
      | none => .error s!"hs {hs} is coarser than the products of the {p.name} preference"
      | some _ =>
        match p.rateFor hs with
        | .error e => .error e
        | .ok r => .ok (some (p, r), "")

def statuteOf (t : TariffRule) (parts : List String) : String := "; ".intercalate ((t.statute :: parts).filter (· != ""))

/-- The duty on an imported line. -/
def importedOutcome (t : TariffRule) (s : Spend) (x : SpendX) (c : CustomsX) : CustomsOutcome :=
  if c.hsRaw == "" then .unknown "imported and no hs given" else
  match hsNormalize c.hsRaw with
  | none => .unknown s!"hs \"{c.hsRaw}\" is not an HS code of 2, 4, 6, 8 or 10 digits"
  | some hs =>
  match t.mfnLine hs with
  | .error e => .unknown e
  | .ok (p, l) =>
  match l.specific? s x with
  | .error e => .unknown s!"{e} (the duty on hs {hs} is specific)"
  | .ok sp =>
  let v := t.vatRate s.good
  let bM := customsValueOf t.dutyInVatBase l.higherOf s.amount v l.adValoremBp sp c.customsValue
  let dM := customsDutyOn l.higherOf l.adValoremBp sp bM
  let heading := if p == "" then s!"HS {hs}: other goods {t.otherBp} bp" else s!"HS {hsDigits p} (MFN)"
  match t.prefFor hs c.origin with
  | .error e => .unknown e
  | .ok (none, note) => .due bM dM (t.statuteOf [l.statute, heading ++ note])
  | .ok (some (pr, r), _) =>
    let spP := if pr.keepSpecific then sp else 0
    let hP := l.higherOf && pr.keepSpecific
    let bP := customsValueOf t.dutyInVatBase hP s.amount v r spP c.customsValue
    let dP := customsDutyOn hP r spP bP
    let res := pickLower bM dM bP dP
      (t.statuteOf [pr.statute, s!"HS {hs}: {pr.name} preference, origin {c.origin}"])
      (t.statuteOf [l.statute, heading ++ s!" (lower than the {pr.name} rate)"])
    .due res.1 res.2.1 res.2.2

/-- **What the rule does with a basket line**: nothing for a good it does not take or a domestic line; else the duty or
why it cannot be computed. -/
def lineOutcome (t : TariffRule) (s : Spend) (x : SpendX) (c : CustomsX) : CustomsOutcome :=
  if !t.takesGood s.good then .none else
  if t.isDomestic c then (if x.imported then .unknown "\"imported\": true but origin domestic" else .none) else
  if !(x.imported || c.origin != "") then .none else
  t.importedOutcome s x c

/-! ### 2.9.0 (R2-GAP-1, SSA note): dated lines, surcharges by origin, specific duties in a foreign currency -/

/-- The rule uses a 2.9.0 field (a date window, a surcharge, a foreign currency); else the 2.8.0 path, unchanged. -/
def uses29 (t : TariffRule) : Bool :=
  !t.surcharges.isEmpty || t.lines.any (fun l => l.validFrom != "" || l.validTo != "" || l.currency != "")
    || t.preferences.any (fun p => p.validFrom != "" || p.validTo != "")

/-- The rule as in force on day `d` of `year`: the lines, preferences and surcharges in force that day. -/
def onDay (t : TariffRule) (year d : Nat) : TariffRule :=
  { t with lines := t.lines.filter (fun l => inForceOn year l.validFrom l.validTo d),
           preferences := t.preferences.filter (fun p => inForceOn year p.validFrom p.validTo d),
           surcharges := t.surcharges.filter (fun u => inForceOn year u.validFrom u.validTo d) }

/-- Insert by day (a day already present is kept once). -/
def insertByDay (p : Nat × String) : List (Nat × String) → List (Nat × String)
  | [] => [p]
  | q :: r => if p.1 < q.1 then p :: q :: r else if p.1 == q.1 then q :: r else q :: insertByDay p r

/-- The days inside `year` on which a window of the rule opens or closes (after the first day), with the date as written. -/
def bounds (t : TariffRule) (year : Nat) : List (Nat × String) :=
  let ws := t.lines.map (fun l => (l.validFrom, l.validTo)) ++ t.preferences.map (fun p => (p.validFrom, p.validTo))
    ++ t.surcharges.map (fun u => (u.validFrom, u.validTo))
  let raw := ws.flatMap fun (f, e) =>
    (if f == "" then [] else [(startDay year f, f)]) ++ (if e == "" then [] else [(endDay year e, e)])
  (raw.filter fun (d, _) => decide (0 < d) && decide (d < daysInYear year)).foldl (fun acc p => insertByDay p acc) []

/-- A line's specific amounts at a rate, exactly (the rate scales the fractions: one rounding). -/
def lineAtRate (l : TariffLine) (r : FxRate) : TariffLine :=
  { l with perUnitNum := l.perUnitNum * r.num, perUnitDen := l.perUnitDen * r.den,
           perKgNum := l.perKgNum * r.num, perKgDen := l.perKgDen * r.den, currency := "" }

/-- The line in the model's currency, with the note on the rate; an error when its currency has no rate. -/
def inLocal (t : TariffRule) (g : CanonGlobal) (l : TariffLine) : Except String (TariffLine × String) :=
  if l.currency == "" || (l.perUnitNum == 0 && l.perKgNum == 0) then .ok (l, "") else
  match fxFor g l.currency t.fxRate with
  | some r => .ok (lineAtRate l r, r.note)
  | none => .error s!"amounts in {l.currency} and no exchange rate given (fxRates.{l.currency})"

/-- The surcharges on a code and origin, each with its specific part in money and its rate note; an error: grade C
(the code too coarse, the origin not given where a surcharge limited by origin could apply, a missing quantity or rate). -/
def surchargesFor (t : TariffRule) (g : CanonGlobal) (hs origin : String) (s : Spend) (x : SpendX) :
    Except String (List (TariffSurcharge × Int × String)) :=
  t.surcharges.foldlM (fun acc u =>
    match u.coversHs? hs with
    | some false => .ok acc
    | none => .error s!"hs {hs} is coarser than the products of the {u.name} surcharge"
    | some true =>
      if origin == "" && !u.anyOrigin then .error s!"origin not given (a surcharge may apply: {u.name})"
      else if origin != "" && !u.hasOrigin origin then .ok acc
      else match t.inLocal g u.asLine with
        | .error e => .error s!"{u.name}: {e}"
        | .ok (l, fx) => match l.specific? s x with
          | .error e => .error s!"{e} (the {u.name} surcharge is specific)"
          | .ok sp => .ok (acc ++ [(u, sp, fx)])) []

/-- Each surcharge's duty on a customs value `b`. -/
def surDuties (sur : List (TariffSurcharge × Int × String)) (b : Int) : List (TariffSurcharge × Int × String) :=
  sur.map fun (u, sp, fx) => (u, divR .down (u.adValoremBp * b) BP + sp, fx)

/-- One path (MFN, or a preference): the customs value, the duty with the surcharges, each surcharge's duty. With a
surcharge the value comes out of the price with the surcharge inside it (`a + a_s`, `s + s_s`); a mixed `higherOf` duty
with a surcharge needs the line's `"customsValue"`. -/
def pathDuty (t : TariffRule) (s : Spend) (c : CustomsX) (v : Int) (higherOf : Bool) (a sp : Int)
    (sur : List (TariffSurcharge × Int × String)) : Except String (Int × Int × List (TariffSurcharge × Int × String)) :=
  if sur.isEmpty then
    let b := customsValueOf t.dutyInVatBase higherOf s.amount v a sp c.customsValue
    .ok (b, customsDutyOn higherOf a sp b, [])
  else if higherOf && decide (c.customsValue < 0) then
    .error "a mixed duty (the higher of two) with a surcharge: give the line's \"customsValue\""
  else
    let aS := isum (sur.map (·.1.adValoremBp))
    let spS := isum (sur.map (·.2.1))
    let b := if 0 ≤ c.customsValue then c.customsValue
      else customsValueOf t.dutyInVatBase false s.amount v (a + aS) (sp + spS) (-1)
    let ds := surDuties sur b
    .ok (b, customsDutyOn higherOf a sp b + isum (ds.map (·.2.1)), ds)

/-- The statute words of the surcharges charged. -/
def surNote (ds : List (TariffSurcharge × Int × String)) : List String :=
  ds.map fun (u, d, fx) => "; ".intercalate ([u.statute, s!"+ {u.name}: {d}", fx].filter (· != ""))

/-- The duty on an imported line under the rule in force (2.9.0: foreign-currency specific parts, surcharges). -/
def importedOutcome29 (t : TariffRule) (g : CanonGlobal) (s : Spend) (x : SpendX) (c : CustomsX) : CustomsOutcome :=
  if c.hsRaw == "" then .unknown "imported and no hs given" else
  match hsNormalize c.hsRaw with
  | none => .unknown s!"hs \"{c.hsRaw}\" is not an HS code of 2, 4, 6, 8 or 10 digits"
  | some hs =>
  match t.mfnLine hs with
  | .error e => .unknown e
  | .ok (p, l0) =>
  match t.inLocal g l0 with
  | .error e => .unknown s!"{e} (the duty on hs {hs} is specific)"
  | .ok (l, fxM) =>
  match l.specific? s x with
  | .error e => .unknown s!"{e} (the duty on hs {hs} is specific)"
  | .ok sp =>
  match t.prefFor hs c.origin with
  | .error e => .unknown e
  | .ok (pref, note) =>
  match t.surchargesFor g hs c.origin s x with
  | .error e => .unknown e
  | .ok sur =>
  let v := t.vatRate s.good
  let heading := if p == "" then s!"HS {hs}: other goods {t.otherBp} bp" else s!"HS {hsDigits p} (MFN)"
  match t.pathDuty s c v l.higherOf l.adValoremBp sp sur with
  | .error e => .unknown e
  | .ok (bM, dM, dsM) =>
  let stM (extra : String) : String := t.statuteOf ([l.statute, heading ++ extra, fxM] ++ surNote dsM)
  match pref with
  | none => .due bM dM (stM note)
  | some (pr, r) =>
    let spP := if pr.keepSpecific then sp else 0
    let hP := l.higherOf && pr.keepSpecific
    let surP := sur.filter fun (u, _, _) => !u.waivedBy pr.name
    match t.pathDuty s c v hP r spP surP with
    | .error e => .unknown e
    | .ok (bP, dP, dsP) =>
      let res := pickLower bM dM bP dP
        (t.statuteOf ([pr.statute, s!"HS {hs}: {pr.name} preference, origin {c.origin}"]
          ++ (if pr.keepSpecific then [fxM] else []) ++ surNote dsP))
        (stM s!" (lower than the {pr.name} rate)")
      .due res.1 res.2.1 res.2.2

/-- **Dates**: a dated line under the rule in force on its date; an undated line only when the rule gives the same value
and duty on every day of the year (checked on the first day and on each day a window opens or closes), else grade C. -/
def datedOutcome (t : TariffRule) (g : CanonGlobal) (s : Spend) (x : SpendX) (c : CustomsX) : CustomsOutcome :=
  match dayOfYear? g.year x.date with
  | some d => (t.onDay g.year d).importedOutcome29 g s x c
  | none =>
    let bs := t.bounds g.year
    let o0 := (t.onDay g.year 0).importedOutcome29 g s x c
    if bs.isEmpty then o0 else
    if x.date != "" then .unknown s!"date \"{x.date}\" is not a date (YYYY-MM-DD) and the duty changes within the year" else
    let same (o : CustomsOutcome) : Bool := match o0, o with
      | .due b d _, .due b' d' _ => b == b' && d == d'
      | .unknown w, .unknown w' => w == w'
      | .none, .none => true
      | _, _ => false
    if bs.all (fun (d, _) => same ((t.onDay g.year d).importedOutcome29 g s x c)) then
      match o0 with
      | .due b d st => .due b d (st ++ "; no date: the same duty all year")
      | o => o
    else .unknown s!"no \"date\" and the duty changes within the year (on {", ".intercalate (bs.map (·.2))}): give the line's \"date\""

/-- 2.9.0: what the rule does with a basket line (as `lineOutcome`, then `datedOutcome`). -/
def lineOutcome29 (t : TariffRule) (g : CanonGlobal) (s : Spend) (x : SpendX) (c : CustomsX) : CustomsOutcome :=
  if !t.takesGood s.good then .none else
  if t.isDomestic c then (if x.imported then .unknown "\"imported\": true but origin domestic" else .none) else
  if !(x.imported || c.origin != "") then .none else
  t.datedOutcome g s x c

/-- **What the rule does with a line**: the 2.8.0 `lineOutcome` unless the rule uses a 2.9.0 field (`outcome_v28`). -/
def outcome (t : TariffRule) (g : CanonGlobal) (s : Spend) (x : SpendX) (c : CustomsX) : CustomsOutcome :=
  if t.uses29 then t.lineOutcome29 g s x c else t.lineOutcome s x c

/-- **A rule that uses no 2.9.0 field computes exactly as 2.8.0.** -/
theorem outcome_v28 (t : TariffRule) (g : CanonGlobal) (s : Spend) (x : SpendX) (c : CustomsX) (h : t.uses29 = false) :
    t.outcome g s x c = t.lineOutcome s x c := by
  simp [outcome, h]

/-- The 2.9.0 fields at their defaults: no window, no surcharge, no foreign currency. -/
theorem uses29_eq_false (t : TariffRule) (hs : t.surcharges = [])
    (hl : ∀ l ∈ t.lines, l.validFrom = "" ∧ l.validTo = "" ∧ l.currency = "")
    (hp : ∀ p ∈ t.preferences, p.validFrom = "" ∧ p.validTo = "") : t.uses29 = false := by
  simp only [uses29, hs, List.isEmpty_nil, Bool.not_true, Bool.false_or, Bool.or_eq_false_iff, List.any_eq_false]
  refine ⟨fun l hm => ?_, fun p hm => ?_⟩
  · obtain ⟨h1, h2, h3⟩ := hl l hm; simp [h1, h2, h3]
  · obtain ⟨h1, h2⟩ := hp p hm; simp [h1, h2]

/-- A dated line is priced under the rule in force on its date. -/
theorem datedOutcome_dated (t : TariffRule) (g : CanonGlobal) (s : Spend) (x : SpendX) (c : CustomsX) (d : Nat)
    (h : dayOfYear? g.year x.date = some d) :
    t.datedOutcome g s x c = (t.onDay g.year d).importedOutcome29 g s x c := by
  simp [datedOutcome, h]

/-- With no window anywhere the rule in force on any day is the rule. -/
theorem onDay_open (t : TariffRule) (y d : Nat) (hl : ∀ l ∈ t.lines, l.validFrom = "" ∧ l.validTo = "")
    (hp : ∀ p ∈ t.preferences, p.validFrom = "" ∧ p.validTo = "")
    (hu : ∀ u ∈ t.surcharges, u.validFrom = "" ∧ u.validTo = "") : t.onDay y d = t := by
  have e1 : t.lines.filter (fun l => inForceOn y l.validFrom l.validTo d) = t.lines :=
    List.filter_eq_self.2 fun l hm => by obtain ⟨h1, h2⟩ := hl l hm; simp [inForceOn, h1, h2]
  have e2 : t.preferences.filter (fun p => inForceOn y p.validFrom p.validTo d) = t.preferences :=
    List.filter_eq_self.2 fun p hm => by obtain ⟨h1, h2⟩ := hp p hm; simp [inForceOn, h1, h2]
  have e3 : t.surcharges.filter (fun u => inForceOn y u.validFrom u.validTo d) = t.surcharges :=
    List.filter_eq_self.2 fun u hm => by obtain ⟨h1, h2⟩ := hu u hm; simp [inForceOn, h1, h2]
  simp only [onDay, e1, e2, e3]

/-- An undated line whose rule has no window inside the year is priced as on the first day. -/
theorem datedOutcome_noBounds (t : TariffRule) (g : CanonGlobal) (s : Spend) (x : SpendX) (c : CustomsX)
    (h : dayOfYear? g.year x.date = none) (hb : t.bounds g.year = []) :
    t.datedOutcome g s x c = (t.onDay g.year 0).importedOutcome29 g s x c := by
  simp [datedOutcome, h, hb]

/-- 2.9.0 domestic lines pay nothing either. -/
theorem lineOutcome29_domestic (t : TariffRule) (g : CanonGlobal) (s : Spend) (x : SpendX) (c : CustomsX)
    (hd : t.isDomestic c = true) (hi : x.imported = false) : t.lineOutcome29 g s x c = .none := by
  unfold lineOutcome29; split <;> simp_all

/-- **A surcharge never lowers the duty**: each surcharge's duty is ≥ 0 (non-negative rates, specific parts and value). -/
theorem surDuties_nonneg (sur : List (TariffSurcharge × Int × String)) (b : Int) (hb : 0 ≤ b)
    (h : ∀ p ∈ sur, 0 ≤ p.1.adValoremBp ∧ 0 ≤ p.2.1) : ∀ q ∈ surDuties sur b, 0 ≤ q.2.1 := by
  intro q hq
  simp only [surDuties, List.mem_map] at hq
  obtain ⟨⟨u, sp, fx⟩, hm, rfl⟩ := hq
  obtain ⟨h1, h2⟩ := h _ hm
  have : 0 ≤ divR .down (u.adValoremBp * b) BP := by
    simp only [divR, BP]; exact Int.ediv_nonneg (Int.mul_nonneg h1 hb) (by omega)
  simp only at h2 ⊢
  omega

/-- The surcharges charged are the ones that apply, in order. -/
theorem surDuties_fst (sur : List (TariffSurcharge × Int × String)) (b : Int) :
    (surDuties sur b).map (·.1) = sur.map (·.1) := by
  simp [surDuties, List.map_map, Function.comp_def]

/-- One charge per dutiable line. -/
def charges (t : TariffRule) (g : CanonGlobal) : List Charge :=
  (consumptionC g).zipIdx.filterMap fun ((s, x, c), i) =>
    match t.outcome g s x c with
    | .due b d st =>
      some (charge t.oecd t.name b pos (fun _ => d) (event := s!"line {i + 1} ({s.good.name})") (level := t.level)
        (bearer := .consumer) (statute := st))
    | _ => none

/-- The lines the rule cannot compute, for `unsupported` (grade C). -/
def unknown (t : TariffRule) (g : CanonGlobal) : List String :=
  (consumptionC g).zipIdx.filterMap fun ((s, x, c), i) =>
    match t.outcome g s x c with
    | .unknown why => some s!"{t.oecd.code} {t.name}: line {i + 1} ({s.good.name}): {why} (grade C)"
    | _ => none

/-- With the duty outside the VAT base, the VAT the 2.0 basket VAT (`Vat.embedded`) counts on the duty. -/
def vatOverstated (t : TariffRule) (g : CanonGlobal) : Int :=
  if t.dutyInVatBase then 0 else
  isum ((consumptionC g).map fun (s, x, c) =>
    match t.outcome g s x c with
    | .due _ d _ => let v := t.vatRate s.good; divR .down (pos d * v) (BP + v)
    | _ => 0)

def family (t : TariffRule) : Family :=
  { name := s!"{t.oecd.code} {t.name}", covers := [t.oecd], run := fun _ g _ => t.charges g }

theorem lineOutcome_domestic (t : TariffRule) (s : Spend) (x : SpendX) (c : CustomsX) (hd : t.isDomestic c = true)
    (hi : x.imported = false) : t.lineOutcome s x c = .none := by
  unfold lineOutcome; split <;> simp_all

theorem lineOutcome_notImported (t : TariffRule) (s : Spend) (x : SpendX) (c : CustomsX) (hi : x.imported = false)
    (ho : c.origin = "") : t.lineOutcome s x c = .none := by
  unfold lineOutcome
  split
  · rfl
  · split
    · simp [hi]
    · simp [hi, ho]

/-- **An imported line without an HS code is never charged**: it is grade C. -/
theorem lineOutcome_noHs (t : TariffRule) (s : Spend) (x : SpendX) (c : CustomsX) (hg : t.takesGood s.good = true)
    (hd : t.isDomestic c = false) (hi : x.imported = true) (hh : c.hsRaw = "") :
    t.lineOutcome s x c = .unknown "imported and no hs given" := by
  simp [lineOutcome, importedOutcome, hg, hd, hi, hh]

/-- A 1.x household (no basket) is untouched. -/
theorem charges_ofCanon (t : TariffRule) (c : Canon) : t.charges (CanonGlobal.ofCanon c) = [] := by
  simp [charges, consumptionC, consumptionX, CanonGlobal.ofCanon]

theorem unknown_ofCanon (t : TariffRule) (c : Canon) : t.unknown (CanonGlobal.ofCanon c) = [] := by
  simp [unknown, consumptionC, consumptionX, CanonGlobal.ofCanon]

end TariffRule

/-- The customs family of several rules (one charge per line and rule). -/
def customsFamily (ts : List TariffRule) (name : String := "5123 customs import duties") : Family :=
  { name, covers := (ts.map (·.oecd)).eraseDups, run := fun _ g _ => ts.flatMap (·.charges g) }

/-- **Customs on a model**: the family last, and the grade-C lines after the model's own `unsupported`. -/
def GlobalModel.withCustoms (m : GlobalModel) (ts : List TariffRule) (name : String := "5123 customs import duties") :
    GlobalModel :=
  { m with families := m.families ++ [customsFamily ts name],
           unsupported := fun args g => m.unsupported args g ++ ts.flatMap (·.unknown g) }

theorem withCustoms_pit (m : GlobalModel) (ts : List TariffRule) (n : String) (args : List String) (g : CanonGlobal) :
    ((m.withCustoms ts n).computeGlobal args g).pit = (m.computeGlobal args g).pit := rfl

/-- A 1.x household gets no customs charge and no customs line. -/
theorem withCustoms_ofCanon (ts : List TariffRule) (c : Canon) :
    ts.flatMap (·.charges (CanonGlobal.ofCanon c)) = [] ∧ ts.flatMap (·.unknown (CanonGlobal.ofCanon c)) = [] := by
  constructor <;> simp [TariffRule.charges_ofCanon, TariffRule.unknown_ofCanon]

end TaxKernel.Global
