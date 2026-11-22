import BgTax.Social

/-!
# The personal income tax of one person (ЗДДФЛ), in stotinki

ЗДДФЛ чл. 17: "Общата годишна данъчна основа е сумата от годишните данъчни основи по чл. 25, 30, 32, 34 и 36,
намалена с предвидените в този закон данъчни облекчения"; чл. 48, ал. 1: × 10 %. Each source has its own base:
* employment (чл. 24-25): the wage "се намалява с удържаните от работодателя задължителни осигурителни вноски, които
  са за сметка на физическото лице";
* free profession (чл. 29, ал. 1, т. 3 and чл. 30): income less 25 % statutory expenses, less the self-insured
  contributions "които самоосигуряващото се лице е задължено да прави за данъчната година за своя сметка";
* rent (чл. 31-32): income less 10 % expenses.
Exempt (чл. 13, ал. 1): pensions from compulsory insurance (т. 6), interest on deposits with EU/EEA banks (т. 8),
gains on financial instruments traded on a regulated market (т. 3, § 1, т. 11 ДР), family allowances (т. 17).
Dividends: final tax 5 % on the gross amount (чл. 38, ал. 1-2; чл. 46, ал. 3), outside the annual base (чл. 16, ал. 2).

Reliefs (чл. 19, 22, 22в; ЗДБРБ 2025 ПЗР § 3): voluntary pension contributions up to 10 % and donations up to 5 % of
the sum of the annual bases; the child relief up to that sum, the unused part passing to the other parent (чл. 22в,
ал. 4: "разликата може да се ползва от другия родител").
-/

namespace BgTax
open TaxKernel

/-- The flat schedule of чл. 48, ал. 1 as a kernel schedule (10 % from the first stotinka). -/
def pitSchedule : Schedule := Schedule.flat pitRate

/-- Tax on a base in stotinki: 10 %, half up to the stotinka. -/
def pitOn (base : Int) : Int := pitSchedule.tax stRound (pos base)

/-- `pct` of `x`, half up to the stotinka. -/
def pctOf (rate x : Int) : Int := stRound.ofTicks (rate * x)

/-- One person's incomes (stotinki) and household items assigned to them. -/
structure PersonIn where
  age : Nat := 40
  wages : Int := 0
  selfEmployment : Int := 0
  pension : Int := 0
  rent : Int := 0
  dividends : Int := 0
  volPension : Int := 0
  donations : Int := 0
  deriving Repr, Inhabited

/-- Born before 1 Jan 1960 (65 or older on 1 Jan 2025). -/
def PersonIn.pre1960 (p : PersonIn) : Bool := p.age ≥ 65

/-- Everything computed for one person before the child relief. -/
structure PersonCalc where
  eeSocial : Int
  seSocial : Int
  empBase : Int
  seTaxable : Int
  seBaseV : Int
  freelanceBase : Int
  rentBase : Int
  sumBases : Int
  volRelief : Int
  donRelief : Int
  /-- what the child relief can still use (sum of bases less the other reliefs) -/
  room : Int
  dividendTax : Int
  deriving Repr, Inhabited

def calcPerson (p : PersonIn) (seRate : Int := freelanceExpenseRate) (y : Nat := 2025) (es : Bool := false)
    (em : Bool := false) : PersonCalc :=
  let ee := if em then eeContribJ y p.pre1960 p.wages else if es then eeContribE y p.pre1960 p.wages else
    if y ≥ 2025 then eeContrib p.pre1960 p.wages else eeContribY y p.pre1960 p.wages
  let empBase := pos (p.wages - ee)
  let seTaxable := pos p.selfEmployment - pctOf seRate (pos p.selfEmployment)
  let base := if p.pension > 0 then 0 else
    if em then seBaseJ y seTaxable (insurableYearJ y p.wages) else
    if es then seBaseE y seTaxable (insurableYearE y p.wages) else
    if y ≥ 2025 then seBase seTaxable (insurableYear p.wages) else seBaseY y seTaxable (insurableYearY y p.wages)
  let se := seContrib p.pre1960 base
  let freelanceBase := pos (seTaxable - se)
  let rentBase := pos p.rent - pctOf rentExpenseRate (pos p.rent)
  let s := empBase + freelanceBase + rentBase
  let vol := min (pos p.volPension) (pctOf voluntaryPensionCapRate s)
  let don := min (pos p.donations) (pctOf donationCapRate s)
  { eeSocial := ee, seSocial := se, empBase, seTaxable, seBaseV := base, freelanceBase, rentBase, sumBases := s,
    volRelief := vol, donRelief := don, room := pos (s - vol - don),
    dividendTax := pctOf dividendRate (pos p.dividends) }

/-- The annual tax of a person who uses `child` of the child relief (chl. 48, ал. 1). -/
def PersonCalc.pit (c : PersonCalc) (child : Int) : Int := pitOn (c.room - min child c.room)

/-- Child relief for a household: the first parent uses what their bases allow, the other parent the rest. -/
def splitRelief (r room1 room2 : Int) : Int × Int :=
  let u1 := min (pos r) (pos room1)
  (u1, min (pos r - u1) (pos room2))

end BgTax
