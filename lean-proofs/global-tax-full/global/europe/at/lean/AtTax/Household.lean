import AtTax.Tax

/-!
# Austria 2025: the household (contract `Canon` → `Out`)

* Taxpayers: each adult is assessed alone. Investment income (household totals) is split equally (contract);
  interest is taken as bank interest (§ 27a Abs. 1 Z 1, 25 %), dividends and capital gains as listed shares (27,5 %).
* Wages are paid in 14 instalments by default (12 laufende + 13th/14th as sonstige Bezüge, as the OECD assumes);
  `--payments=12|13|14` or the household field `"atPayments"` changes that.
* A couple (§ 106 Abs. 3, § 33 Abs. 4 Z 1): married, or `"cohabiting": true`. Two other adults are two separate
  taxpayers; the children are then the first adult's (Alleinerzieher).
* Children: Familienbeihilfe for every child under 18 (FLAG § 2 Abs. 1 lit. a); 18-23 only with the household
  field `"atChildrenInEducation": true` (lit. b, not checked further). Kinderabsetzbetrag with each.
* Familienbonus Plus (§ 33 Abs. 3a Z 3): a couple may claim each child's amount on one partner or half each; the
  model tries every allocation and keeps the cheapest (`--fbp=a1|a2|half` fixes it).
* Familienbeihilfe recipient (for § 33 Abs. 7 lit. b): the second adult (FLAG § 2a: the household-running parent,
  "vorrangig … die Mutter"; assumption).
Options: `--oecd` (OECD convention for the age band of the 6-year-old child, FINDINGS F2), `--kmb-literal`
(literal reading of § 33 Abs. 7; default is the BMF's per-child reading, FINDINGS), `--payments=N`, `--fbp=…`.
-/

namespace AtTax
open TaxKernel

structure Opts where
  oecd : Bool := false
  kmbLiteral : Bool := false
  payments : Option Int := none
  fbp : String := "auto"
  withholding : Bool := false
  aprilAt6 : Bool := false
  noGfb : Bool := false
  noVfb : Bool := false
  noRegel : Bool := false
  /-- `--eurostat`: Eurostat earn_net ESMS 3.4 (sha256 89ab2734..., `tests/data/_methodology/earn_net_esms.htm`) -/
  eurostat : Bool := false
  deriving Repr, Inhabited

def parseOpts (args : List String) : Opts :=
  args.foldl (fun o a =>
    if a == "--oecd" then { o with oecd := true }
    else if a == "--eurostat" then { o with eurostat := true }
    else if a == "--no-gfb" then { o with noGfb := true }
    else if a == "--no-vfb" then { o with noVfb := true }
    else if a == "--no-regel" then { o with noRegel := true }
    else if a == "--bmf-pension-april" then { o with aprilAt6 := true }
    else if a == "--withholding" then { o with withholding := true }
    else if a == "--kmb-literal" then { o with kmbLiteral := true }
    else if a.startsWith "--payments=" then { o with payments := (a.drop 11).toString.toInt? }
    else if a.startsWith "--fbp=" then { o with fbp := (a.drop 6).toString }
    else o) {}

/-- Children for whom Familienbeihilfe (and so the Kinderabsetzbetrag, § 106 Abs. 1) is paid. -/
def fbChildren (c : Canon) : List Nat :=
  let edu := (c.bool? "atChildrenInEducation").getD false
  (c.children.map (·.age)).filter fun a => a < 18 ∨ (edu ∧ a < 24)

/-- FLAG § 8 Abs. 2, 3, 8; § 9; EStG § 33 Abs. 3: Familienbeihilfe + Geschwisterstaffel + Schulstartgeld +
Mehrkindzuschlag + Kinderabsetzbetrag for the year (cents). `oecd`: a child aged 3-9 gets the amount from age 10. -/
def familyBenefits (ages : List Nat) (oecd : Bool) (familyEinkommen : Int) (y : YP := yp2025) (eurostat : Bool := false) :
    Int :=
  let n := ages.length
  let fb := sumInts (ages.map fun a =>
    -- `eurostat` (ESMS 3.4): "dependent children aged between 6 and 11 years ... If the amounts vary within this age
    -- range, the most generous are used": a child aged 6-11 gets the largest FLAG § 8 Abs. 2 amount over ages 6-11
    if eurostat ∧ 6 ≤ a ∧ a ≤ 11 then 12 * ([6, 7, 8, 9, 10, 11].map (fbByAgeY y)).foldl max 0
    else 12 * fbByAgeY y (if oecd ∧ 3 ≤ a ∧ a < 10 then 10 else a))
  let gs := 12 * (n : Int) * geschwisterY y n
  let ss := y.schulstart * ((ages.filter fun a => 6 ≤ a ∧ a ≤ 15).length : Int)
  let mkz := if n ≥ 3 ∧ familyEinkommen ≤ mkzLimit then 12 * y.mkzMonth * ((n : Int) - 2) else 0
  let kab := 12 * y.kabMonth * (n : Int)
  -- FLAG § 8 Abs. 10: one-off amount per child (August 2022)
  let oneOff := y.fbOneOff * (n : Int)
  fb + gs + ss + mkz + kab + oneOff

/-- Familienbonus Plus per child and year (§ 33 Abs. 3a Z 1). -/
def fbpYear (age : Nat) (y : YP := yp2025) : Int := if age < 18 then 12 * y.fbpU18 else 12 * y.fbp18

/-- All allocations of the children's Familienbonus between two partners: each child to the first (0), the
second (1) or half each (2) (§ 33 Abs. 3a Z 3 lit. a). Returns (amount on partner 1, amount on partner 2). -/
def fbpAllocations : List Int → List (Int × Int)
  | [] => [(0, 0)]
  | a :: rest =>
    (fbpAllocations rest).flatMap fun (x, y) =>
      [(x + a, y), (x, y + a), (x + a / 2, y + (a - a / 2))]

def personsOf (c : Canon) (o : Opts) : List PersonIn :=
  let pay := (o.payments.getD ((c.int? "atPayments").getD 14))
  let pay := clamp 12 14 pay
  let n := c.adults.length
  let inv1 := fun (x : Int) => if n ≥ 2 then half1 x else x
  let inv2 := fun (x : Int) => if n ≥ 2 then half2 x else 0
  c.adults.zipIdx.map fun (a, i) =>
    let sel := fun (x : Int) => if i = 0 then inv1 x else if i = 1 then inv2 x else 0
    { wagePay := divR .halfUp (100 * a.wages) pay, payments := pay,
      pensionPay := divR .halfUp (100 * a.pension) 14, self := 100 * a.selfEmployment,
      rental := 100 * sel c.rentalIncome, interest := 100 * sel c.interest,
      other27 := 100 * sel (c.dividends + c.capitalGains), charitable := 100 * sel c.charitable,
      aprilAt6 := o.aprilAt6, noGfb := o.noGfb, noVfb := o.noVfb, noRegel := o.noRegel, year := c.year }

/-- Has income from § 2 Abs. 3 Z 1-4 (the 30-day condition of § 33 Abs. 7; assumed met when there is any). -/
def active (p : PersonIn) : Bool := p.wagePay > 0 ∨ p.pensionPay > 0 ∨ p.self ≠ 0

/-- § 33 Abs. 7: who receives the Kindermehrbetrag (at most one taxpayer). Eligibility threshold: "unter 700 Euro"
(`literal`) or 700 € per child (BMF: "Einkommensteuer unter 1.400 Euro" for two children). Lit. a: the taxpayer with
the AVAB/AEAB; lit. b: both partners below the threshold, then "nur der Familienbeihilfeberechtigte" (the second
adult, assumption). -/
def kmbRecipient (literal : Bool) (nKids : Nat) (couple av1 av2 : Bool) (t1a t1b : Int) (act1 act2 : Bool)
    (y : YP := yp2025) : Option Nat :=
  let thr := if literal then y.kmbPerChild else y.kmbPerChild * (nKids : Int)
  if nKids = 0 then none
  else if av1 ∧ t1a < thr ∧ act1 then some 0
  else if av2 ∧ t1b < thr ∧ act2 then some 1
  else if couple ∧ t1a < thr ∧ t1b < thr then (if act2 then some 1 else if act1 then some 0 else none)
  else none

structure HhResult where
  taxes : List PTax
  bases : List Base
  regel : List Bool
  fbpAlloc : Int × Int
  benefits : Int
  deriving Inhabited

/-- Taxes of all adults for one Familienbonus allocation. -/
def evalAlloc (c : Canon) (o : Opts) (ps : List PersonIn) (couple : Bool) (nKids : Nat) (alloc : Int × Int) :
    List (PTax × Base × Bool) :=
  let y := ypOf c.year
  let b0s := ps.map fun p => base p false
  let eink := b0s.map (·.einkuenfte)
  let t1s := b0s.map fun b => tariffTax b.einkommen y
  let e1 := eink.headD 0
  let e2 := eink[1]?.getD 0
  -- § 33 Abs. 4 Z 1: Alleinverdiener (couple, ≥ 1 child, partner's Einkünfte ≤ 7 284 €; both → the higher earner)
  let q1 := couple ∧ nKids > 0 ∧ e2 ≤ y.avabPartnerLimit
  let q2 := couple ∧ nKids > 0 ∧ e1 ≤ y.avabPartnerLimit
  let av1 := q1 ∧ (¬ q2 ∨ e1 ≥ e2)
  let av2 := q2 ∧ ¬ av1
  -- § 33 Abs. 4 Z 2: Alleinerzieher (no partner, ≥ 1 child): the first adult
  let ae1 := ¬ couple ∧ nKids > 0
  let avab := fun (i : Nat) =>
    if (i = 0 ∧ (av1 ∨ ae1)) ∨ (i = 1 ∧ av2) then avabAmountY y nKids else 0
  -- § 33 Abs. 6 Z 1: erhöhter PAB (married, partner's Einkünfte ≤ 2 673 €, no AVAB)
  let pabH := fun (i : Nat) =>
    c.married ∧ c.adults.length = 2 ∧ avab i = 0 ∧ (if i = 0 then e2 else e1) ≤ y.pabPartnerLimit
  -- § 33 Abs. 7: Kindermehrbetrag, to one taxpayer
  let t1a := t1s.headD 0
  let t1b := t1s[1]?.getD 0
  let p1 := ps.headD {}
  let p2 := ps[1]?.getD {}
  let kmbTo := kmbRecipient o.kmbLiteral nKids couple (avab 0 > 0) (avab 1 > 0) t1a t1b (active p1) (active p2) y
  ps.zipIdx.map fun (p, i) =>
    let fbp := if i = 0 then alloc.1 else if i = 1 then alloc.2 else 0
    let kmb := if kmbTo = some i then kmbAmount nKids (t1s[i]?.getD 0) (!o.kmbLiteral) y else 0
    bestTax p { fbp, avab := avab i, pabHigh := pabH i, kmb := if o.withholding then 0 else kmb, wh := o.withholding }

def household (c : Canon) (o : Opts) : HhResult :=
  let y := ypOf c.year
  let ps := personsOf c o
  let couple := c.adults.length = 2 ∧ (c.married ∨ (c.bool? "cohabiting").getD false)
  let kids := fbChildren c
  let nKids := kids.length
  let fbps := kids.map (fbpYear · y)
  let total := sumInts fbps
  let allocs : List (Int × Int) :=
    if ¬ couple then [(total, 0)]
    else if o.fbp == "a1" then [(total, 0)]
    else if o.fbp == "a2" then [(0, total)]
    else if o.fbp == "half" then [(total - total / 2, total / 2)]
    else if nKids ≤ 6 then fbpAllocations fbps else [(total - total / 2, total / 2)]
  let scored := allocs.map fun al =>
    let r := evalAlloc c o ps couple nKids al
    (sumInts (r.map (·.1.total)), al, r)
  let best := scored.foldl (fun acc x => if x.1 < acc.1 then x else acc) (scored.headD (0, (0, 0), []))
  let r := best.2.2
  let famE := sumInts (r.map fun x => x.2.1.einkommen)
  { taxes := r.map (·.1), bases := r.map (·.2.1), regel := r.map (·.2.2), fbpAlloc := best.2.1,
    benefits := familyBenefits kids o.oecd famE y o.eurostat }

def toEur (cents : Int) : Int := divR .halfUp cents 100

def out (o : Opts) (c : Canon) : Out :=
  let h := household c o
  let it := sumInts (h.taxes.map (·.total))
  let ss := sumInts (h.bases.map fun b => b.sv.total + b.svSZ.total + b.kvPenL + b.kvPenSZ + b.gsvgC)
  let cgtc := sumInts (h.bases.map fun b => b.einkommen + b.szB)
  let cgitletc := sumInts (h.taxes.map fun t => t.t1 + t.sz)
  let un : List String :=
    ["Pendlerpauschale/Pendlereuro, Unterhaltsabsetzbetrag, Kirchenbeitrag, außergewöhnliche Belastungen, investment-related Gewinnfreibetrag, Selbständigenvorsorge (BMSVG 1,53 %) not modelled",
     "pensionContributions: no deduction in Austrian law since 2021 for private pension saving (ignored)"] ++
    (if o.eurostat then ["--eurostat (Eurostat earn_net ESMS 3.4): a child aged 6-11 gets the most generous Familienbeihilfe of ages 6-11 (the amount from age 10); the Schulstartgeld is the same for ages 6-15; no 2025 EStG/ASVG/AMPFG parameter changes within the year, so the start-of-year rule changes nothing in 2025" ++ (if c.year < 2025 then "; for tax years before 2025 within-year changes (e.g. the 2022 tariff of § 124b Z 390) are not re-timed to 1 January" else "")] else []) ++
    (if c.year < 2025 then
      ["tax year " ++ toString c.year ++ ": EStG, ASVG/AMPFG and FLAG amounts of that year (improve-central round 4); GSVG § 27 KV 6,8 % / PV 18,5 %, AKG § 61 Abs. 2 (at most 0,5 %), EStG § 27a Abs. 1 KESt 25 % / 27,5 % and the § 18 Abs. 1 Z 7 Spenden cap (10 %) read in the RIS versions of 2022-09-01, 2023-07-01 and 2024-07-01: the same as 2025 (round 5); the Wohnbauförderung rate is Land law (WBFG 2018 § 2 Abs. 2), taken as 0,5 % as for 2025"] ++
      (if c.year = 2022 then
       ["2022: the Teuerungsabsetzbetrag for pensioners (§ 124b Z 407 lit. b) is 0 for every statutory pensioner the contract represents: it is excluded for those who received the § 772a ASVG Einmalzahlung (monthly Gesamtpensionseinkommen up to 2 250 EUR) and ends at 25 500 EUR of annual laufende Pensionseinkünfte (12 x 2 250 = 27 000 is above it); Klimabonus and other transfers outside EStG/FLAG not in the contract"] else [])
     else [])
  Out.make c "AT" "EUR" (toEur it) (employeeSocial := toEur ss) (benefits := toEur h.benefits)
    (detail := [Out.d "CGTC" (toEur cgtc), Out.d "CGITLETC" (toEur cgitletc),
      Out.d "taxCents" it, Out.d "socialCents" ss, Out.d "benefitsCents" h.benefits,
      Out.d "taxableIncome" (toEur (sumInts (h.bases.map (·.einkommen)))),
      Out.d "tariffTax" (toEur (sumInts (h.taxes.map (·.t1)))),
      Out.d "sonstigeBezuegeTax" (toEur (sumInts (h.taxes.map (·.sz)))),
      Out.d "familienbonusUsed" (toEur (sumInts (h.taxes.map (·.fbpUsed)))),
      Out.d "fbpOnAdult1" (toEur h.fbpAlloc.1), Out.d "fbpOnAdult2" (toEur h.fbpAlloc.2),
      Out.d "verkehrsabsetzbetrag" (toEur (sumInts (h.taxes.map (·.vabC)))),
      Out.d "pensionistenabsetzbetrag" (toEur (sumInts (h.taxes.map (·.pabC)))),
      Out.d "teuerungsabsetzbetrag" (toEur (sumInts (h.taxes.map (·.tab)))),
      Out.d "alleinverdienerErzieher" (toEur (sumInts (h.taxes.map (·.avab)))),
      Out.d "kindermehrbetrag" (toEur (sumInts (h.taxes.map (·.kmb)))),
      Out.d "kest" (toEur (sumInts (h.taxes.map (·.kest)))),
      Out.d "t1Adult1" (toEur ((h.taxes.headD default).t1)),
      Out.d "taxAdult1" (toEur ((h.taxes.headD default).total)),
      Out.d "taxAdult2" (toEur ((h.taxes[1]?.getD default).total)),
      Out.dBool "regelbesteuerung" (h.regel.any id)])
    (unsupported := un)

def country : Country :=
  { code := "AT", name := "Austria (federal; no local income tax)", currency := "EUR", year := "2025",
    compute := out {}, computeWith := fun args => out (parseOpts args) }

end AtTax
