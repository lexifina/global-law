import MxGlobal.Pit
import TaxKernel.Global2

/-!
# MX 2025: capital income and gains of households (1100), stacked on the 1.x model

The 1.x model (vendored unchanged; its statute sources and grades are in its own `results/summary.json`) taxes the
household's `interest`, `dividends`, `rentalIncome` and `capitalGains` (the contract: gains on long-held listed
shares). A global line's **additional** items of exactly those kinds (income items `interest`, `dividend`, `rent`;
disposals of listed shares held over 12 months) are routed into those fields and charged as the 1.x income tax with
them less the 1.x income tax without them (kernel `stackedTax`, DESIGN §6). Gains on real estate, unlisted shares and
short holdings, and other income kinds, need the country's own gains rules: listed as unsupported (not computed).

## Pass 11 (2026-11-21): real estate (LISR art. 120) and listed shares held 12 months or less (art. 129)

Source: LISR, texto vigente, última reforma DOF 01-04-2024 (Cámara de Diputados PDF via Wayback 2025-06-17,
`mx/law/LISR.txt`), in force for 2025. **Art. 120** (hand form; the kernel's `StackRule` cannot divide each gain
by its own years): the gain of each sale is divided by the years held (at most 20); that part is added to the
seller's ingresos acumulables (stacked on the 1.x model as that adult's `selfEmployment`, which the 1.x model
accumulates in full in the general regime: `PersonTax.other`) and charged as the 1.x ISR with it less without it;
the rest is charged at the **art. 120 fr. III a) rate**: the art. 152 tarifa on all ingresos acumulables of the
year (the accumulable part included) less the deductions other than art. 151 fr. I-III, divided by that amount.
The deductions: **art. 121** fr. I (cost updated, for real estate "cuando menos 10% del monto de la enajenación"),
**art. 124** fr. I-II (land 20 % of the cost when not separated; construction less 3 % a year, at least 20 %;
updated by the INPC factor = the disposal's `indexBp`), fr. III-IV (the line's `costs`). Guard case: a building
sold for 3,000,000 after 10 years at a cost of 1,000,000, no other income: cost 760,000, gain 2,240,000, 224,000
accumulated (tarifa 27,830.42 -> 27,830), 2,016,000 at 12.424 % -> 250,474 (by hand from the art. 152 rows of the
1.x model). **Art. 129 fr. I**: listed shares held 12 months or less, 10 % definitive (the longer holdings stay
the 1.x `capitalGains`). Not modelled (listed): the casa habitación exemption (art. 93 XIX a), 700,000 UDIs of the
price), unlisted shares, losses (art. 122), the five-year average option (fr. III b), the provisional payment
(art. 126, credited against the annual tax).
-/

namespace MxGlobal.Capital
open TaxKernel TaxKernel.Global AmerCommon MxGlobal

def capF : Family := stackFamily pitOf "1.x model income tax on household interest, dividends, rentalIncome, capitalGains (stackedTax)"

/-- LISR Capítulo IV (arts. 119-126): real estate of an individual. The casa habitación (art. 93 fr. XIX a), exempt up
to 700,000 UDIs of the price) is not here: it is listed grade C (the UDI value of the date of sale is not an input). -/
def isReMx (d : Disposal) : Bool := d.kind == .realEstate || d.kind == .land || (d.kind == .home && !d.mainHome)
/-- Full years between acquisition and sale. -/
def fullYears (d : Disposal) : Int := ((d.heldMonths / 12 : Nat) : Int)
/-- Art. 120 fr. I: the years, at most 20 (a sale within the first year divides by 1: our reading, flagged). -/
def yearsOf (d : Disposal) : Int := max 1 (min 20 (fullYears d))
/-- Art. 124 fr. I-II: land 20 % of the cost when not separated (all of it for land), the construction less 3 % a year
(at least 20 % of it), updated by the INPC factor (`indexBp`); art. 121 fr. I: at least 10 % of the proceeds. -/
def costMx (d : Disposal) : Int :=
  let land := if d.kind == .land then d.cost else divR .down (2000 * d.cost) BP
  let built := divR .down ((d.cost - land) * max 2000 (10000 - 300 * fullYears d)) BP
  max (divR .down ((land + built) * d.indexBp) BP) (divR .down (1000 * d.proceeds) BP)
/-- Art. 121 last paragraph: the gain = proceeds less the deductions (fr. III-IV: `costs`); a loss gives 0 (art. 122
not modelled). -/
def gainMx (d : Disposal) : Int := pos (d.proceeds - costMx d - d.costs)
/-- Art. 120 fr. II: the part added to the year's ingresos acumulables. -/
def accMx (d : Disposal) : Int := divR .down (gainMx d) (yearsOf d)

/-- (adult, accumulable part, non-accumulable part) of each adult who sold real estate. -/
def reParts (g : CanonGlobal) : List (Nat × Int × Int) :=
  (List.range g.household.adults.length).filterMap fun p =>
    let ds := g.disposals.filter fun d => isReMx d && d.person == p
    if ds.isEmpty then none else
    let a := isum (ds.map accMx)
    some (p, a, isum (ds.map gainMx) - a)

/-- The 1.x persons are all in the general regime (else the accumulable part would meet RESICO: grade C). -/
def regimeOk (c : Canon) : Bool := (MxTax.personsOf c).all (·.regime == "general")

/-- Art. 120 fr. III a): the tarifa of art. 152 on the person's ingresos acumulables (accumulable part included) less the
deductions other than art. 151 fr. I-III (in the 1.x model: fr. V), divided by that amount, times the non-accumulable
part `n` (pesos); result in centavos. -/
def nonAccCents (c' : Canon) (p : Nat) (n : Int) : Int :=
  let pin := (MxTax.personsOf c').getD p default
  let o := MxTax.personTax pin
  let b := o.acumulables - o.ppr
  if b ≤ 0 then 0 else divR .halfUp (MxTax.cts n * MxTax.tarifaTicks (MxTax.tarifa152Y pin.wage.yr) b) (BP * b)

def reF : Family :=
  { name := "1100 ISR enajenación de inmuebles (LISR arts. 120, 121, 124)", covers := [.pit],
    run := fun args g _ =>
      let ps := reParts g
      if g.entity == .company || ps.isEmpty || !regimeOk g.household then [] else
      let c := g.household
      let c' := StackField.selfEmployment.addAll c (ps.map fun (p, a, _) => (p, a))
      [flatCharge .pit "ISR enajenación de inmuebles: parte acumulable (art. 120 fr. I-II)" (pitOf args c' - pitOf args c)
         (base := isum (ps.map (·.2.1))) (event := "real estate sales") (statute := "LISR (DOF 11-12-2013, última reforma DOF 01-04-2024) art. 120 fr. I-II: \"La ganancia se dividirá entre el número de años transcurridos entre la fecha de adquisición y la de enajenación, sin exceder de 20 años\"; the result \"se sumará a los demás ingresos acumulables del año\"; art. 121 (deducciones; inmuebles: costo actualizado cuando menos 10 % del monto de la enajenación), art. 124 fr. I-II (terreno 20 %, construcción menos 3 % anual, mínimo 20 %); tarifa art. 152 (1.x model)")]
      ++ ps.map fun (p, _, n) =>
        flatCharge .pit "ISR enajenación de inmuebles: parte no acumulable (art. 120 fr. III a)" (MxTax.cffPesos (nonAccCents c' p n))
          (base := n) (event := s!"person {p + 1}") (statute := "LISR art. 120 fr. III and inciso a): \"La parte de la ganancia no acumulable se multiplicará por la tasa\" = the art. 152 tarifa on all ingresos acumulables of the year less the deductions other than art. 151 fr. I-III, divided by that amount") }

/-- Art. 129 fr. I: listed shares held 12 months or less (the longer holdings are the 1.x `capitalGains`, above). -/
def isShortListed (d : Disposal) : Bool := d.kind == .listedShares && !isLongListed d
def shortGain (g : CanonGlobal) : Int := pos (isum ((g.disposals.filter isShortListed).map (·.gain)))
def shortF : Family :=
  { name := "1100 ISR art. 129 (10 %): listed shares held 12 months or less", covers := [.pit],
    run := fun _ g _ => if g.entity == .company || shortGain g == 0 then [] else
      [charge .pit "ISR definitivo 10 % (art. 129 fr. I): acciones enajenadas en bolsa" (shortGain g) id (fun b => divR .halfDown b 10)
        (event := "listed shares (12 months or less)") (statute := "LISR art. 129 fr. I: \"aplicando la tasa del 10% a las ganancias obtenidas en el ejercicio\" on shares sold through the bolsas de valores concesionadas (pago definitivo); CFF art. 20 rounding")] }

def otherDisp (d : Disposal) : Bool := !(isLongListed d || isShortListed d || isReMx d)

/-- Guard household: one adult, no other income, a building sold for 3,000,000 after 10 years at a cost of 1,000,000. -/
def gx : CanonGlobal :=
  { id := "gx", household := { id := "gx", adults := [{}] },
    disposals := [{ kind := .realEstate, proceeds := 3000000, cost := 1000000, heldMonths := 120 }] }

def families : List Family := [capF, reF, shortF]

def absent : List Absent :=
  []

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String := (if g.entity == .company then [] else
  when (g.disposals.any otherDisp) "disposals other than real estate and listed shares (the casa habitación: art. 93 fr. XIX a) exemption to 700,000 UDIs of the price, UDI of the date of sale not an input; unlisted shares: art. 120 with the art. 22-24 cost; bonds, movables): not modelled (grade C)"
  ++ when (g.disposals.any isReMx) "real estate: art. 124 cost = the line's cost (land 20 % when not separated) x indexBp (the INPC factor, default none); art. 121 fr. III-IV costs not updated; art. 122 losses not offset; the art. 120 fr. III b) five-year average rate (an option) not modelled; years held: full years, at least 1"
  ++ when (g.disposals.any isReMx && !regimeOk g.household) "real estate sold by a household with a person in RESICO or the own-company option: art. 120 not applied (grade C)"
  ++ when (g.disposals.any fun d => isReMx d && decide (d.person ≥ g.household.adults.length)) "real estate of a person who is not an adult of the household: not charged (grade C)"
  ++ when (g.disposals.any isShortListed) "art. 129 (10 %): gains and losses netted within each holding class (12 months or less here; longer in the 1.x model), not across them; losses of earlier years not carried")
  ++ when (g.entity != .company && g.incomes.any fun i => i.kind != .interest && i.kind != .dividend && i.kind != .rent) "additional income items other than interest, dividends and rent: not taxed by this family"
  ++ when (g.entity != .company && (g.disposals.any isLongListed || g.incomes.any fun i => i.kind == .interest || i.kind == .dividend || i.kind == .rent)) "additional capital income is routed into the 1.x household totals and taxed as the 1.x model taxes them (its conventions: split between adults, long-held listed shares)"

example (args : List String) (c : Canon) : capF.run args (CanonGlobal.ofCanon c) [] = [] := stackFamily_legacy _ _ args c []
#guard (capF.run [] { id := "g", household := { id := "g" } } []).length == 0
-- art. 124: land 200,000 + construction 800,000 x 70 % = 760,000 (> 10 % of 3,000,000); gain 2,240,000; / 10 years
#guard costMx { kind := .realEstate, proceeds := 3000000, cost := 1000000, heldMonths := 120 } == 760000
#guard accMx { kind := .realEstate, proceeds := 3000000, cost := 1000000, heldMonths := 120 } == 224000
-- art. 121 fr. I floor: cost 100,000 held 30 years -> 20,000 + 80,000 x 20 % = 36,000 < 10 % of 2,000,000
#guard costMx { kind := .realEstate, proceeds := 2000000, cost := 100000, heldMonths := 360 } == 200000
#guard yearsOf { kind := .land, proceeds := 1, cost := 0, heldMonths := 360 } == 20
#guard yearsOf { kind := .land, proceeds := 1, cost := 0, heldMonths := 5 } == 1
-- tarifa 152 on 224,000.00: 19,682.13 + 21.36 % x 38,147.42 = 27,830.42 -> CFF 27,830 (accumulable part)
#guard ((reF.run [] gx []).map (·.due)) == [27830, 250474]
-- fr. III a): rate = 27,830.418912 / 224,000 x 2,016,000 = 250,473.77 -> CFF 250,474
#guard ((shortF.run [] { gx with disposals := [{ kind := .listedShares, proceeds := 150000, cost := 100000, heldMonths := 6 }] } []).map (·.due)) == [5000]
#guard (reF.run [] { gx with disposals := [{ kind := .home, proceeds := 3000000, cost := 1000000, heldMonths := 120, mainHome := true }] } []).length == 0

end MxGlobal.Capital
