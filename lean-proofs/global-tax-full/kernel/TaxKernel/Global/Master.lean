import TaxKernel.Global.Types

/-!
# TaxKernel.Global.Master (2.0.0): the master equation every jurisdiction implements

## The equation

For an entity `g` (a household or a company), a jurisdiction's model produces a list of **charges**. A charge is one
application of one tax to one base (the year's income, one disposal, one inheritance, one purchase, the consumption
basket, one payment abroad):

    due(charge)  = schedule(relief(base)) − credit          credit ≤ schedule(relief(base)) unless refundable
    tax(g, k)    = Σ { due(c) | c ∈ charges(g), oecd(c) = k }       for every OECD heading k
    total(g)     = Σ_k tax(g, k)  = Σ_{c ∈ charges(g)} (schedule_c(relief_c(base_c)) − credit_c)
    net(g)       = gross income(g) + benefits(g) − Σ { due(c) | c borne by the entity }

`Charge` stores the four stages (`base`, `relieved`, `gross`, `credit`) next to `due`, and `charge` is the only
constructor models need: it applies the relief and the schedule and caps a non-refundable credit, so every charge a
model builds satisfies `Charge.WF` (`due = gross − credit`) by construction (`charge_wf`), and the total is the sum
of the equation's terms (`total_eq_master`).

## The model

    structure GlobalModel where
      pit      : List String → Canon → Json         -- the 1.x model, unchanged (its output line, verbatim)
      route    : CanonGlobal → Canon                -- what the PIT model sees (default: the 1.x household)
      families : List Family                        -- each: List String → CanonGlobal → List Charge → List Charge
      absent   : List Absent                        -- headings the jurisdiction does not levy, with the citation
    GlobalModel.computeGlobal : GlobalModel → List String → CanonGlobal → OutGlobal

Families run in order and see every earlier charge, so a later tax can credit an earlier one (CIT credited against
the shareholder's dividend tax in an imputation system, trade tax credited against income tax, a wealth-tax cap that
reads the income tax). The PIT model's own lines come first (`legacyCharges`: income tax, surtaxes and local income
tax under 1100, employee contributions under 2100).

## Backward compatibility (the theorems at the end)

* `ofCountry k` wraps any 1.x `Country`: `pit := fun args c => (k.computeWith args c).toJson`, no families.
* `ofCountry_pit`: for every entity, its `pit` is the 1.x output on the household (`rfl`).
* `adapter_unchanged`: for every 1.x household `c`, `((ofCountry k).computeGlobal args (ofCanon c)).pit` is exactly
  `(k.computeWith args c).toJson`, the line the 1.x exe prints (`rfl`).
* `withFamily_charges`: adding a family appends its charges and changes nothing computed before it (in particular
  never the PIT output), so regional builders can add families one at a time without touching each other.
* `conservative_pit`: any model whose `pit` is the 1.x model and whose `route` returns the household for a 1.x input
  keeps every 1.x output unchanged.
-/

namespace TaxKernel.Global
open Lean TaxKernel

/-- Sum of a list of integers (structural, for proofs). -/
def isum : List Int → Int
  | [] => 0
  | x :: xs => x + isum xs

theorem isum_append (a b : List Int) : isum (a ++ b) = isum a + isum b := by
  induction a with
  | nil => simp [isum]
  | cons x xs ih => simp [isum, ih]; omega

theorem isum_nonneg (l : List Int) (h : ∀ x ∈ l, 0 ≤ x) : 0 ≤ isum l := by
  induction l with
  | nil => simp [isum]
  | cons x xs ih =>
    simp only [isum]
    have hx := h x (by simp)
    have := ih (fun y hy => h y (by simp [hy]))
    omega

/-- Government level that levies a charge. -/
inductive Level where
  | central | state | local | social
  deriving Repr, DecidableEq, Inhabited, BEq

def Level.name : Level → String
  | .central => "central" | .state => "state" | .local => "local" | .social => "social"

/-- Who bears the charge in the net-position identity: the entity itself, its employer (employer contributions on
the entity's wages), the entity as a consumer (VAT and excises inside the prices it pays; VAT a business remits on its
supplies), or the recipient of a payment the entity makes (tax withheld at source on payments abroad). -/
inductive Bearer where
  | entity | employer | consumer | withheld
  deriving Repr, DecidableEq, Inhabited, BEq

def Bearer.name : Bearer → String
  | .entity => "entity" | .employer => "employer" | .consumer => "consumer" | .withheld => "withheld"

/-- One application of one tax to one base. -/
structure Charge where
  oecd : Oecd
  /-- the statute's name of the tax ("Körperschaftsteuer", "Impuesto al Valor Agregado") -/
  tax : String
  /-- what was charged ("year", "disposal 1", "inheritance 1", "basket", "payment 2") -/
  event : String := "year"
  level : Level := .central
  bearer : Bearer := .entity
  /-- statutory base before reliefs -/
  base : Int
  /-- base after reliefs (allowances, exemptions, indexation, inclusion rates) -/
  relieved : Int
  /-- schedule applied to the relieved base -/
  gross : Int
  /-- credits applied against this charge -/
  credit : Int := 0
  due : Int
  /-- the provision(s) the charge follows -/
  statute : String := ""
  deriving Repr, Inhabited

/-- The master equation holds for the charge. -/
def Charge.WF (c : Charge) : Prop := c.due = c.gross - c.credit

/-- A credit as applied: a refundable credit in full, a non-refundable one up to the (non-negative) gross. -/
def appliedCredit (refundable : Bool) (credit gross : Int) : Int :=
  if refundable then credit else min (pos credit) (pos gross)

/-- **The constructor every model uses**: `due = schedule(relief(base)) − credit`. -/
def charge (oecd : Oecd) (tax : String) (base : Int) (relief : Int → Int) (schedule : Int → Int)
    (credit : Int := 0) (refundable : Bool := false) (event : String := "year") (level : Level := .central)
    (bearer : Bearer := .entity) (statute : String := "") : Charge :=
  let relieved := relief base
  let gross := schedule relieved
  let cr := appliedCredit refundable credit gross
  { oecd, tax, event, level, bearer, base, relieved, gross, credit := cr, due := gross - cr, statute }

/-- A charge whose amount is computed elsewhere (a 1.x line, a figure taken from another part): base = relieved =
gross = due, no credit. -/
def flatCharge (oecd : Oecd) (tax : String) (amount : Int) (event : String := "year") (level : Level := .central)
    (bearer : Bearer := .entity) (statute : String := "") (base : Int := amount) : Charge :=
  { oecd, tax, event, level, bearer, base, relieved := base, gross := amount, credit := 0, due := amount, statute }

theorem charge_wf (oecd tax base relief schedule credit refundable event level bearer statute) :
    (charge oecd tax base relief schedule credit refundable event level bearer statute).WF := by
  simp [charge, Charge.WF]

theorem flatCharge_wf (oecd tax amount event level bearer statute base) :
    (flatCharge oecd tax amount event level bearer statute base).WF := by
  simp [flatCharge, Charge.WF]

/-- The master equation term by term: the due amount is the schedule of the relieved base less the applied credit. -/
theorem charge_due (oecd tax base relief schedule credit refundable event level bearer statute) :
    (charge oecd tax base relief schedule credit refundable event level bearer statute).due
      = schedule (relief base) - appliedCredit refundable credit (schedule (relief base)) := rfl

/-- A non-refundable credit never makes a non-negative schedule's charge negative. -/
theorem charge_nonneg (oecd tax base relief schedule credit event level bearer statute)
    (h : 0 ≤ schedule (relief base)) :
    0 ≤ (charge oecd tax base relief schedule credit false event level bearer statute).due := by
  simp only [charge, appliedCredit]
  simp only [Bool.false_eq_true, ↓reduceIte, pos]
  omega

/-- A heading the jurisdiction does not levy, with the provision that shows it (absence is cited, not assumed). -/
structure Absent where
  oecd : Oecd
  why : String
  deriving Repr, Inhabited

/-- One tax family of a model (e.g. the corporate income tax with its trade tax): the headings it books under, and
its charges given the entity and every charge computed before it. -/
structure Family where
  name : String
  covers : List Oecd
  run : List String → CanonGlobal → List Charge → List Charge

/-- Read a JSON number as whole units (half up), 0 when absent. -/
def jInt (j : Json) (k : String) : Int := intField j k

/-- The charges the 1.x output line already holds: income tax, each surtax and the local income tax under 1100,
employee contributions under 2100. -/
def legacyCharges (j : Json) : List Charge :=
  let surt : List (String × Int) := match j.getObjVal? "surtaxes" with
    | .ok (.obj kvs) => kvs.toList.map fun (k, v) => (k, match v with | .num n => numToInt n | _ => 0)
    | _ => []
  [flatCharge .pit "incomeTax" (jInt j "incomeTax") (statute := "1.x model")]
  ++ surt.map (fun (k, v) => flatCharge .pit k v (statute := "1.x model"))
  ++ [flatCharge .pit "localIncomeTax" (jInt j "localIncomeTax") (level := .local) (statute := "1.x model"),
      flatCharge .sscEmployee "employeeSocial" (jInt j "employeeSocial") (level := .social) (statute := "1.x model")]

theorem legacyCharges_wf (j : Json) : ∀ c ∈ legacyCharges j, c.WF := by
  intro c hc
  simp only [legacyCharges, List.mem_append, List.mem_cons, List.mem_map, List.not_mem_nil] at hc
  rcases hc with ((h | h) | ⟨⟨k, v⟩, _, h⟩) | (h | h | h) <;> (try subst h) <;> (try (rw [← h])) <;>
    first | exact flatCharge_wf .. | (simp at h)

theorem legacyCharges_bearer (j : Json) : ∀ c ∈ legacyCharges j, c.bearer = .entity := by
  intro c hc
  simp only [legacyCharges, List.mem_append, List.mem_cons, List.mem_map, List.not_mem_nil] at hc
  rcases hc with ((h | h) | ⟨⟨k, v⟩, _, h⟩) | (h | h | h) <;> (try subst h) <;> (try (rw [← h])) <;>
    first | rfl | (simp at h)

/-- A jurisdiction model of kernel 2.0. -/
structure GlobalModel where
  code : String
  name : String := ""
  currency : String
  year : String := "2025"
  /-- the 1.x model (its output line), unchanged -/
  pit : List String → Canon → Json
  /-- the household the PIT model sees; must return `g.household` for a 1.x entity (`RouteConservative`) -/
  route : CanonGlobal → Canon := fun g => g.household
  /-- how the PIT output is booked as charges -/
  pitCharges : Json → List Charge := legacyCharges
  families : List Family := []
  absent : List Absent := []
  notes : List String := []
  /-- what this entity holds that the model does not compute (listed, never silently dropped) -/
  unsupported : List String → CanonGlobal → List String := fun _ _ => []

/-- Gross resources of an entity for the net position: a household's 1.x gross income plus its extra income items,
realised gains and the inheritances and gifts it receives; a company's profit before tax. -/
def CanonGlobal.grossResources (g : CanonGlobal) : Int :=
  if g.entity == .company then g.company.profit
  else g.household.gross + isum (g.incomes.map (·.amount)) + isum (g.disposals.map (·.gain))
    + isum (g.transfers.map (·.statutoryValue))

/-- What a model returns for one entity. -/
structure OutGlobal where
  id : String
  country : String
  currency : String
  /-- the 1.x output line for the routed household, verbatim -/
  pit : Json
  charges : List Charge
  benefits : Int
  covered : List Oecd
  absent : List Absent
  notes : List String := []
  unsupported : List String := []
  /-- gross resources of the entity (household: 1.x gross + extra incomes + realised gains; company: profit) -/
  gross : Int := 0

namespace OutGlobal
def total (o : OutGlobal) : Int := isum (o.charges.map (·.due))
def totalOf (o : OutGlobal) (k : Oecd) : Int := isum ((o.charges.filter (·.oecd == k)).map (·.due))
def borneBy (o : OutGlobal) (b : Bearer) : Int := isum ((o.charges.filter (·.bearer == b)).map (·.due))
/-- Headings neither covered by a family nor cited as absent. -/
def notModelled (o : OutGlobal) : List Oecd :=
  Oecd.all.filter fun k => !(o.covered.contains k) && !(o.absent.any (·.oecd == k))
/-- Net position: gross income + benefits − every charge the entity bears itself (consumption taxes are inside the
prices the entity pays; employer charges are on top of its wages). -/
def net (o : OutGlobal) (gross : Int) : Int := gross + o.benefits - o.borneBy .entity
end OutGlobal

/-- The master equation for the whole entity: with every charge well formed, the total is the sum over charges of
`gross − credit`, i.e. of `schedule(relief(base)) − credit`. -/
theorem total_eq_master (o : OutGlobal) (h : ∀ c ∈ o.charges, c.WF) :
    o.total = isum (o.charges.map fun c => c.gross - c.credit) := by
  unfold OutGlobal.total
  congr 1
  apply List.map_congr_left
  intro c hc
  exact h c hc

/-- The headings' totals add up to the total when every charge is under one of `Oecd.all` (always). -/
theorem isum_filter_split (l : List Charge) (p : Charge → Bool) :
    isum (l.map (·.due)) = isum ((l.filter p).map (·.due)) + isum ((l.filter (fun c => !p c)).map (·.due)) := by
  induction l with
  | nil => simp [isum]
  | cons x xs ih =>
    by_cases hp : p x = true
    · simp [List.filter, hp, isum, ih]; omega
    · simp [List.filter, hp, isum, ih]; omega

/-- A company entity whose line gives no `"household"` (`parseGlobal`'s company branch fills in a placeholder
one-adult household, or a company built in Lean without `raw`). The 1.x PIT model has nobody to tax there, so its line
is not booked (kernel 2.2.0: before, a 1.x minimum tax such as CH's 24 CHF was charged to companies). A household
entity is never company-only (`ofCanon_companyOnly`); a company line that gives a household keeps its PIT. -/
def CanonGlobal.companyOnly (g : CanonGlobal) : Bool :=
  g.entity == .company && (match g.raw.getObjVal? "household" with | .ok _ => false | .error _ => true)

theorem CanonGlobal.ofCanon_companyOnly (c : Canon) : (CanonGlobal.ofCanon c).companyOnly = false := rfl

/-! ## Unread withholding (kernel 2.3.0, R-FT2-1)

`Wht.charges` (`Capital`) books a charge for every payment abroad; with no matching rule it used to book **due 0 with
statute `noWhtRule`** ("no withholding rule"), and a model with no withholding family books nothing for a payment.
Both read as a computed 0, because heading 1200 is computed by the CIT. From 2.3.0 `computeGlobal`, for a company
entity:
* drops those placeholders (`Charge.unreadWht`: bearer withheld, statute `noWhtRule`, due 0; `WhtRead.kept`), and
* lists every payment abroad that no withheld charge computes (`WhtRead.unreadPayments`) in `unsupported`, after the
  model's own entries, as `"1200 withholding on payment <i> (<kind>) abroad: no rule read (grade C)"` (`1100` when the
  recipient is an individual: the heading its charge would have). That is the form the FT scorer reads as
  "not reached (grade C)" (`tests/tools/ft_common.ft_charge`).
A payment counts as computed when a withheld charge other than a placeholder carries its event `payment <i> (<kind>)`,
or when the withheld charges carry at least as many distinct events of its kind as there are payments of that kind (a
model that hands a filtered payment list to `Wht.charges` renumbers the events: CL). **A statutory zero is a rule**:
`rateBp := 0` with its citation (`WhtRule.zero`, `Wht.zeroOn`) books a covered 0 (`Wht.chargeOf_rule_kept`).
Totals never change (`WhtRead.kept_total`: every dropped charge is 0); household entities and companies without
payments abroad are untouched (`WhtRead.kept_household`, `WhtRead.unread_household`, `WhtRead.unread_noPayments`).
-/

/-- The statute `Wht.charges` gives a payment that no rule matches: a placeholder, not a computed 0. -/
def noWhtRule : String := "no withholding rule"

/-- A withholding placeholder: bearer withheld, statute `noWhtRule`, due 0. -/
def Charge.unreadWht (c : Charge) : Bool := c.bearer == .withheld && c.statute == noWhtRule && c.due == 0

namespace WhtRead

/-- The event `Wht.charges` gives the payment of (0-based) index `i`. -/
def event (i : Nat) (p : Payment) : String := s!"payment {i + 1} ({p.kind.name})"

/-- The events of the withheld charges that are not placeholders. -/
def events (cs : List Charge) : List String :=
  (cs.filter fun c => c.bearer == .withheld && !c.unreadWht).map (·.event)

/-- How many distinct events `payment … (<kind>)` those charges carry. -/
def kindEvents (cs : List Charge) (k : IncomeKind) : Nat :=
  ((events cs).filter fun e => e.startsWith "payment " && e.endsWith s!" ({k.name})").eraseDups.length

/-- Payment `p` (index `i`) is computed by some withheld charge. -/
def computed (co : Company) (cs : List Charge) (p : Payment) (i : Nat) : Bool :=
  (events cs).contains (event i p)
  || decide ((co.paymentsAbroad.filter (·.kind == p.kind)).length ≤ kindEvents cs p.kind)

/-- The payments abroad no withheld charge computes, with their index. -/
def unreadPayments (co : Company) (cs : List Charge) : List (Payment × Nat) :=
  co.paymentsAbroad.zipIdx.filter fun (p, i) => !computed co cs p i

/-- The `unsupported` entry of an unread payment (the scorer's grade-C form). -/
def line (p : Payment) (i : Nat) : String :=
  s!"{(if p.toCompany then Oecd.cit else Oecd.pit).code} withholding on payment {i + 1} ({p.kind.name}) abroad: no rule read (grade C)"

/-- The charges booked: a company entity's placeholders dropped. -/
def kept (g : CanonGlobal) (cs : List Charge) : List Charge :=
  if g.entity == .company then cs.filter (fun c => !c.unreadWht) else cs

/-- The entries added to `unsupported`: one per unread payment of a company entity. -/
def unread (g : CanonGlobal) (cs : List Charge) : List String :=
  if g.entity == .company then (unreadPayments g.company cs).map (fun (p, i) => line p i) else []

theorem kept_household (g : CanonGlobal) (cs : List Charge) (h : (g.entity == .company) = false) :
    kept g cs = cs := by
  simp [kept, h]

theorem unread_household (g : CanonGlobal) (cs : List Charge) (h : (g.entity == .company) = false) :
    unread g cs = [] := by
  simp [unread, h]

theorem unread_noPayments (g : CanonGlobal) (cs : List Charge) (h : g.company.paymentsAbroad = []) :
    unread g cs = [] := by
  unfold unread unreadPayments
  split <;> simp [h]

/-- With no placeholder among the charges nothing is dropped. -/
theorem kept_of_none (g : CanonGlobal) (cs : List Charge) (h : ∀ c ∈ cs, c.unreadWht = false) : kept g cs = cs := by
  unfold kept
  split
  · exact List.filter_eq_self.mpr (fun c hc => by simp [h c hc])
  · rfl

/-- Only placeholders are dropped: every other charge is kept. -/
theorem mem_kept (g : CanonGlobal) (cs : List Charge) (c : Charge) (hc : c ∈ cs) (hu : c.unreadWht = false) :
    c ∈ kept g cs := by
  unfold kept
  split
  · exact List.mem_filter.mpr ⟨hc, by simp [hu]⟩
  · exact hc

theorem placeholder_due (c : Charge) (h : c.unreadWht = true) : c.due = 0 := by
  simp only [Charge.unreadWht, Bool.and_eq_true, beq_iff_eq] at h
  exact h.2

/-- **Dropping placeholders never changes a total**: each of them is 0. -/
theorem kept_total (g : CanonGlobal) (cs : List Charge) :
    isum ((kept g cs).map (·.due)) = isum (cs.map (·.due)) := by
  unfold kept
  split
  · induction cs with
    | nil => rfl
    | cons c cs ih =>
      by_cases hc : c.unreadWht = true
      · simp [List.filter, hc, isum, ih, placeholder_due c hc]
      · simp only [Bool.not_eq_true] at hc
        simp [List.filter, hc, isum, ih]
  · rfl

/-- **A payment is listed only when no withheld charge other than a placeholder carries its event.** -/
theorem unread_sound (co : Company) (cs : List Charge) (p : Payment) (i : Nat)
    (h : (p, i) ∈ unreadPayments co cs) :
    ¬ ∃ c ∈ cs, (c.bearer == .withheld && !c.unreadWht) = true ∧ c.event = event i p := by
  rintro ⟨c, hc, hw, he⟩
  have hn := (List.mem_filter.mp h).2
  have hm : event i p ∈ events cs := List.mem_map.mpr ⟨c, List.mem_filter.mpr ⟨hc, hw⟩, he⟩
  simp only [computed, Bool.not_or, Bool.and_eq_true, Bool.not_eq_true'] at hn
  have := hn.1
  simp [hm] at this

/-- Every listed payment is one of the entity's payments abroad. -/
theorem unread_mem (co : Company) (cs : List Charge) (p : Payment) (i : Nat) (h : (p, i) ∈ unreadPayments co cs) :
    (p, i) ∈ co.paymentsAbroad.zipIdx :=
  (List.mem_filter.mp h).1

end WhtRead

/-- The 1.x lines are never withholding placeholders. -/
theorem legacyCharges_unreadWht (j : Json) (c : Charge) (hc : c ∈ legacyCharges j) : c.unreadWht = false := by
  unfold Charge.unreadWht
  rw [legacyCharges_bearer j c hc]
  rfl

namespace GlobalModel

def runFamilies (fs : List Family) (args : List String) (g : CanonGlobal) (init : List Charge) : List Charge :=
  fs.foldl (fun acc f => acc ++ f.run args g acc) init

/-- The PIT line's charges as booked for an entity: none for a company-only entity. -/
def pitChargesFor (m : GlobalModel) (g : CanonGlobal) (pj : Json) : List Charge :=
  if g.companyOnly then [] else m.pitCharges pj

/-- The charges before the withholding check of 2.3.0: the PIT line's charges (none for a company-only entity), then
every family. -/
def rawCharges (m : GlobalModel) (args : List String) (g : CanonGlobal) : List Charge :=
  runFamilies m.families args g (m.pitChargesFor g (m.pit args (m.route g)))

/-- **The master function**: the PIT line on the routed household, its lines as charges (not for a company-only
entity), then every family; for a company entity, withholding placeholders are dropped and the payments abroad no
charge computes are listed in `unsupported` as grade C (2.3.0, `WhtRead`). -/
def computeGlobal (m : GlobalModel) (args : List String) (g : CanonGlobal) : OutGlobal :=
  let pj := m.pit args (m.route g)
  let cs := runFamilies m.families args g (m.pitChargesFor g pj)
  { id := g.id, country := m.code, currency := m.currency, pit := pj,
    charges := WhtRead.kept g cs,
    benefits := if g.companyOnly then 0 else jInt pj "benefits",
    covered := [.pit, .sscEmployee] ++ m.families.flatMap (·.covers),
    absent := m.absent, notes := m.notes, gross := g.grossResources,
    unsupported := m.unsupported args g ++ WhtRead.unread g cs }

theorem computeGlobal_charges (m : GlobalModel) (args : List String) (g : CanonGlobal) :
    (m.computeGlobal args g).charges = WhtRead.kept g (m.rawCharges args g) := rfl

theorem computeGlobal_unsupported (m : GlobalModel) (args : List String) (g : CanonGlobal) :
    (m.computeGlobal args g).unsupported = m.unsupported args g ++ WhtRead.unread g (m.rawCharges args g) := rfl

/-- Wrap a 1.x country: its model as the PIT, nothing else modelled yet. -/
def ofCountry (k : Country) : GlobalModel :=
  { code := k.code, name := k.name, currency := k.currency, year := k.year,
    pit := fun args c => (k.computeWith args c).toJson }

/-- Wrap a 1.x model by the exe's own per-line function (input line → output line), for models whose `main` does
more than `countryMain` (IT PT BG CY GR print cents as decimal units; AU ES NL CZ PL SE run their own loop; the five
models not built on the kernel). The PIT re-reads the household's own input line (`Canon.raw`), so the 1.x line is
reproduced exactly (`ofLine_unchanged`). A route that changes the household must also change `raw` (`addToRaw`). -/
def ofLine (code name currency year : String) (line : List String → Json → Json) : GlobalModel :=
  { code, name, currency, year, pit := fun args c => line args c.raw }

/-- Add a family at the end. -/
def withFamily (m : GlobalModel) (f : Family) : GlobalModel := { m with families := m.families ++ [f] }

/-- The model's route returns the 1.x household for every 1.x entity. -/
def RouteConservative (m : GlobalModel) : Prop := ∀ c : Canon, m.route (CanonGlobal.ofCanon c) = c

/-- The model's PIT is the 1.x country's model. -/
def PitIs (m : GlobalModel) (k : Country) : Prop := ∀ args c, m.pit args c = (k.computeWith args c).toJson

end GlobalModel

open GlobalModel

/-- The adapter passes the household to the 1.x model untouched, for every entity. -/
theorem ofCountry_pit (k : Country) (args : List String) (g : CanonGlobal) :
    ((ofCountry k).computeGlobal args g).pit = (k.computeWith args g.household).toJson := rfl

/-- **Every 1.x output is unchanged by the adapter**: on a 1.x household the global model's PIT line is the line the
1.x model prints. -/
theorem adapter_unchanged (k : Country) (args : List String) (c : Canon) :
    ((ofCountry k).computeGlobal args (CanonGlobal.ofCanon c)).pit = (k.computeWith args c).toJson := rfl

/-- The adapter adds no charge beyond the 1.x lines (for an entity with a household; kernel 2.2.0 added the
hypothesis: a company-only entity gets none, `computeGlobal_companyOnly`). -/
theorem adapter_charges (k : Country) (args : List String) (g : CanonGlobal) (h : g.companyOnly = false) :
    ((ofCountry k).computeGlobal args g).charges = legacyCharges (k.computeWith args g.household).toJson := by
  have e : (ofCountry k).rawCharges args g = legacyCharges (k.computeWith args g.household).toJson := by
    simp [rawCharges, ofCountry, pitChargesFor, runFamilies, h]
  rw [computeGlobal_charges, e]
  exact WhtRead.kept_of_none _ _ (fun c hc => legacyCharges_unreadWht _ c hc)

/-- **The total is the total of the charges before the 2.3.0 withholding check** (only zero placeholders dropped). -/
theorem computeGlobal_total (m : GlobalModel) (args : List String) (g : CanonGlobal) :
    (m.computeGlobal args g).total = isum ((m.rawCharges args g).map (·.due)) :=
  WhtRead.kept_total g _

/-- On every household entity the charges are the 1.x lines' charges, then the families (unchanged by 2.2.0 and
2.3.0; 2.3.0 narrowed the hypothesis from `companyOnly = false` to a household entity: a company line that gives a
household has its withholding placeholders dropped, `computeGlobal_withHousehold_charges`). -/
theorem computeGlobal_household_charges (m : GlobalModel) (args : List String) (g : CanonGlobal)
    (h : (g.entity == .company) = false) :
    (m.computeGlobal args g).charges = runFamilies m.families args g (m.pitCharges (m.pit args (m.route g))) := by
  have hc : g.companyOnly = false := by simp [CanonGlobal.companyOnly, h]
  rw [computeGlobal_charges, WhtRead.kept_household _ _ h]
  simp [rawCharges, pitChargesFor, hc]

theorem computeGlobal_household_unsupported (m : GlobalModel) (args : List String) (g : CanonGlobal)
    (h : (g.entity == .company) = false) : (m.computeGlobal args g).unsupported = m.unsupported args g := by
  rw [computeGlobal_unsupported, WhtRead.unread_household _ _ h, List.append_nil]

theorem computeGlobal_withHousehold_charges (m : GlobalModel) (args : List String) (g : CanonGlobal)
    (h : g.companyOnly = false) :
    (m.computeGlobal args g).charges
      = WhtRead.kept g (runFamilies m.families args g (m.pitCharges (m.pit args (m.route g)))) := by
  simp [computeGlobal_charges, rawCharges, pitChargesFor, h]

theorem computeGlobal_household_benefits (m : GlobalModel) (args : List String) (g : CanonGlobal)
    (h : g.companyOnly = false) : (m.computeGlobal args g).benefits = jInt (m.pit args (m.route g)) "benefits" := by
  simp [computeGlobal, h]

/-- **A company-only entity bears no PIT charge**: only its families' charges, and no 1.x benefits. -/
theorem computeGlobal_companyOnly (m : GlobalModel) (args : List String) (g : CanonGlobal) (h : g.companyOnly = true) :
    (m.computeGlobal args g).charges = WhtRead.kept g (runFamilies m.families args g [])
      ∧ (m.computeGlobal args g).benefits = 0 := by
  constructor
  · simp [computeGlobal_charges, rawCharges, pitChargesFor, h]
  · simp [computeGlobal, h]

theorem ofCanon_charges (m : GlobalModel) (args : List String) (c : Canon) :
    (m.computeGlobal args (CanonGlobal.ofCanon c)).charges
      = runFamilies m.families args (CanonGlobal.ofCanon c) (m.pitCharges (m.pit args (m.route (CanonGlobal.ofCanon c)))) :=
  computeGlobal_household_charges m args _ rfl

/-- The line adapter reproduces the 1.x exe's line for every 1.x household. -/
theorem ofLine_unchanged (code name currency year : String) (line : List String → Json → Json) (args : List String)
    (c : Canon) : ((ofLine code name currency year line).computeGlobal args (CanonGlobal.ofCanon c)).pit
      = line args c.raw := rfl

theorem ofCountry_routeConservative (k : Country) : (ofCountry k).RouteConservative := fun _ => rfl
theorem ofCountry_pitIs (k : Country) : (ofCountry k).PitIs k := fun _ _ => rfl

/-- Any model that keeps the 1.x PIT and a conservative route leaves every 1.x output unchanged. -/
theorem conservative_pit (m : GlobalModel) (k : Country) (hp : m.PitIs k) (hr : m.RouteConservative)
    (args : List String) (c : Canon) :
    (m.computeGlobal args (CanonGlobal.ofCanon c)).pit = (k.computeWith args c).toJson := by
  simp [computeGlobal, hr c, hp args c]

theorem runFamilies_append (fs : List Family) (f : Family) (args : List String) (g : CanonGlobal) (init : List Charge) :
    runFamilies (fs ++ [f]) args g init
      = runFamilies fs args g init ++ f.run args g (runFamilies fs args g init) := by
  simp [runFamilies, List.foldl_append]

/-- **Adding a family changes nothing computed before it**: the PIT line is the same, and the old charges are a prefix
of the new ones. -/
theorem withFamily_pit (m : GlobalModel) (f : Family) (args : List String) (g : CanonGlobal) :
    ((m.withFamily f).computeGlobal args g).pit = (m.computeGlobal args g).pit := rfl

/-- Before the 2.3.0 withholding check, a new family appends its charges and changes nothing computed before it. -/
theorem withFamily_rawCharges (m : GlobalModel) (f : Family) (args : List String) (g : CanonGlobal) :
    (m.withFamily f).rawCharges args g = m.rawCharges args g ++ f.run args g (m.rawCharges args g) := by
  simp [rawCharges, withFamily, runFamilies_append, pitChargesFor]

/-- On a household entity the booked charges are those (2.3.0 added the hypothesis; on a company entity the same
holds for `rawCharges`, and the booked charges are `WhtRead.kept` of them). -/
theorem withFamily_charges (m : GlobalModel) (f : Family) (args : List String) (g : CanonGlobal)
    (h : (g.entity == .company) = false) :
    ((m.withFamily f).computeGlobal args g).charges
      = (m.computeGlobal args g).charges ++ f.run args g (m.computeGlobal args g).charges := by
  simp only [computeGlobal_charges, WhtRead.kept_household _ _ h, withFamily_rawCharges]

theorem withFamily_routeConservative (m : GlobalModel) (f : Family) (h : m.RouteConservative) :
    (m.withFamily f).RouteConservative := h

theorem withFamily_pitIs (m : GlobalModel) (f : Family) (k : Country) (h : m.PitIs k) : (m.withFamily f).PitIs k := h

/-- Total of a model with one more family = old total + the new family's charges. -/
theorem withFamily_total (m : GlobalModel) (f : Family) (args : List String) (g : CanonGlobal) :
    ((m.withFamily f).computeGlobal args g).total
      = (m.computeGlobal args g).total + isum ((f.run args g (m.rawCharges args g)).map (·.due)) := by
  simp only [computeGlobal_total, withFamily_rawCharges, List.map_append, isum_append]

/-! ## Routing detail into the 1.x household

A country's full 1100 model often routes a detail item into a 1.x field that its PIT model already taxes the right
way (DE: a § 23 EStG private sale of land is tariff income like rent; CL: rent is global complementario income). The
helper `addToHousehold` adds amounts; `route_add_zero` shows it is the identity when nothing is added, which is how a
country discharges `RouteConservative`. -/

structure HouseholdAdd where
  interest : Int := 0
  dividends : Int := 0
  capitalGains : Int := 0
  rentalIncome : Int := 0
  deriving Repr, Inhabited

def addToHousehold (c : Canon) (a : HouseholdAdd) : Canon :=
  { c with interest := c.interest + a.interest, dividends := c.dividends + a.dividends,
           capitalGains := c.capitalGains + a.capitalGains, rentalIncome := c.rentalIncome + a.rentalIncome }

theorem route_add_zero (c : Canon) : addToHousehold c {} = c := by
  cases c; simp [addToHousehold]

/-- `addToHousehold`, also written into the input line (`raw`) for models that re-read it (`ofLine`); a field is
rewritten only when something is added to it. -/
def addToRaw (c : Canon) (a : HouseholdAdd) : Canon :=
  let set (j : Json) (k : String) (v d : Int) : Json := if d = 0 then j else j.setObjVal! k (Lean.toJson (v + d))
  let r1 := set c.raw "interest" c.interest a.interest
  let r2 := set r1 "dividends" c.dividends a.dividends
  let r3 := set r2 "capitalGains" c.capitalGains a.capitalGains
  let r4 := set r3 "rentalIncome" c.rentalIncome a.rentalIncome
  { addToHousehold c a with raw := r4 }

theorem addToRaw_zero (c : Canon) : addToRaw c {} = c := by
  cases c; simp [addToRaw, addToHousehold]

/-- Income tax of a 1.x output line (income tax + surtaxes + local income tax, half up to units). -/
def jsonIncomeTax (j : Json) : Int := isum (((legacyCharges j).filter (·.oecd == .pit)).map (·.due))

/-- **Stacking a detail item on the 1.x PIT**: the tax on amounts routed into the household (a gain taxed at the
scale, an election's alternative) is the 1.x income tax with them less the 1.x income tax without them. -/
def stackedTax (pit : Canon → Int) (c : Canon) (add : HouseholdAdd) : Int := pit (addToRaw c add) - pit c

theorem stackedTax_zero (pit : Canon → Int) (c : Canon) : stackedTax pit c {} = 0 := by
  simp [stackedTax, addToRaw_zero]

/-! ## Output line -/

def Charge.toJson (c : Charge) : Json :=
  Json.mkObj [("oecd", Json.str c.oecd.code), ("tax", Json.str c.tax), ("event", Json.str c.event),
    ("level", Json.str c.level.name), ("bearer", Json.str c.bearer.name), ("base", Lean.toJson c.base),
    ("relieved", Lean.toJson c.relieved), ("gross", Lean.toJson c.gross), ("credit", Lean.toJson c.credit),
    ("due", Lean.toJson c.due), ("statute", Json.str c.statute)]

def OutGlobal.toJson (o : OutGlobal) : Json :=
  let codes := Oecd.all.filter fun k => o.charges.any (·.oecd == k)
  Json.mkObj [("id", Json.str o.id), ("country", Json.str o.country), ("currency", Json.str o.currency),
    ("schema", Json.str "global/2.0"), ("pit", o.pit),
    ("taxes", Json.arr (o.charges.map Charge.toJson).toArray),
    ("byOecd", Json.mkObj (codes.map fun k => (k.code, Lean.toJson (o.totalOf k)))),
    ("total", Lean.toJson o.total),
    ("borne", Json.mkObj [("entity", Lean.toJson (o.borneBy .entity)), ("employer", Lean.toJson (o.borneBy .employer)),
      ("consumer", Lean.toJson (o.borneBy .consumer)), ("withheld", Lean.toJson (o.borneBy .withheld))]),
    ("benefits", Lean.toJson o.benefits), ("gross", Lean.toJson o.gross), ("net", Lean.toJson (o.net o.gross)),
    ("covered", Json.arr ((Oecd.all.filter fun k => o.covered.contains k).map (Json.str ·.code)).toArray),
    ("notLevied", Json.arr (o.absent.map fun a => Json.mkObj [("oecd", Json.str a.oecd.code), ("why", Json.str a.why)]).toArray),
    ("notModelled", Json.arr (o.notModelled.map (Json.str ·.code)).toArray),
    ("notes", Json.arr (o.notes.map Json.str).toArray),
    ("unsupported", Json.arr (o.unsupported.map Json.str).toArray)]

end TaxKernel.Global
