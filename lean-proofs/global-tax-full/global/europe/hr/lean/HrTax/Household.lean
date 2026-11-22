import HrTax.Tax

/-!
# Croatia 2025: the canonical household (contract) → taxes, contributions, child benefit

* Unit: individual assessment (ZPD čl. 2: each natural person is a taxpayer; no joint return).
* Investment income: split equally between spouses (`half1`/`half2`); the taxes on it are flat and final, so the
  split changes nothing but the cent rounding.
* Capital gains: the contract's gains are on long-held listed shares: exempt after two years (ZPD čl. 67 st. 8).
* Children: every child in the household is a dependent child (ZPD čl. 14 st. 3, čl. 17; no age limit while in
  education); the child allowance is shared between the parents as they agree (čl. 17 st. 5: equally unless agreed
  otherwise). Input `childShare1` (bp of the children's allowance to adult 1) fixes the split; without it the model
  takes the cheapest of 100/75/50/25/0 % (what EUROMOD simulates and what a couple can agree; see FINDINGS).
* A spouse or cohabiting partner whose own receipts are at most 3.600 € a year is a dependant of the other
  (čl. 14 st. 3 r.br. 1, čl. 17 st. 1; "bračni drug (... izvanbračnog druga ...)", Porezna uprava, Osobni odbitak).
* Self-employment: `selfEmployment` is the obrt's profit before the owner's own contributions (books, ZPD čl. 29-35;
  contributions are a business expense, čl. 33 st. 6); with `"pausal": true` it is the year's receipts, taxed on
  the paušal class (ZPD čl. 82; if receipts exceed 60.000 € the paušal is not available and books apply).
* Pillar II membership: default yes (compulsory for those born after 1961 who joined after 2002); `"pillar2": false`
  charges 20 % pillar I.
* Local rates: Zagreb by default; `"lowerRate"` / `"higherRate"` (bp) for another unit (checked against the ranges of
  čl. 19.a st. 2 only in `Theorems`).
* Booking: all income tax is **localIncomeTax**: porez na dohodak is "zajednički porez čiji se prihod dijeli između
  općina, gradova i županija" (Zakon o financiranju JLP(R)S, NN 127/17 čl. 5 st. 1; shares 74 % city, 20 % county,
  6 % decentralised functions, NN 138/20 čl. 1; the state keeps a 1 % collection fee, NN 114/23 čl. 1) and since 2024
  its rates are set by the city (ZPD čl. 19.a). `incomeTax` is 0.
-/

namespace HrTax
open TaxKernel

/-- Options read from the input line. -/
structure Opts where
  rates : Rates := zagreb2025
  pillar2 : Bool := true
  pausal1 : Bool := false
  pausal2 : Bool := false
  childShare1 : Option Int := none
  dzd : Bool := true

def Canon.opts (c : Canon) (y : YP := ypFor c.year) : Opts :=
  { rates := ⟨(c.int? "lowerRate").getD y.rates.lower, (c.int? "higherRate").getD y.rates.higher⟩,
    pillar2 := (c.bool? "pillar2").getD true,
    pausal1 := (c.bool? "pausal").getD ((c.bool? "pausal1").getD false),
    pausal2 := (c.bool? "pausal2").getD false,
    childShare1 := c.int? "childShare1",
    dzd := (c.bool? "childBenefit").getD true }

/-- One adult's own figures before the allowance split (cents). -/
structure Own where
  age : Nat
  wages : Int
  pension : Int
  se : Int
  pausal : Bool
  ee : Int          -- employee pension contributions on wages
  er : Int          -- employer health (detail)
  seC : Int         -- own contributions as self-employed
  seDoh : Int       -- books dohodak
  pTax : Int        -- paušal tax (final)
  interest : Int
  dividends : Int
  rent : Int
  receipts : Int    -- all receipts (for the dependant test and donation cap)

def mkOwn (y : YP) (o : Opts) (pausal : Bool) (a : Adult) (interest dividends gains rent : Int) : Own :=
  let w := C * pos a.wages
  let pe := C * pos a.pension
  let se := C * a.selfEmployment
  let usePausal := pausal && y.pausalOk && pos se ≤ y.pausalCeiling
  let ee := eeContribYearY y o.pillar2 w
  let seC := if se = 0 then 0 else if usePausal then pausalContribYearY y o.pillar2 else seContribYearY y o.pillar2
  { age := a.age, wages := w, pension := pe, se, pausal := usePausal, ee, er := healthYear w, seC,
    seDoh := if usePausal then 0 else se - seC,
    pTax := if usePausal then pausalTaxY y se else 0,
    interest := C * interest, dividends := C * dividends, rent := C * rent,
    receipts := w + pe + pos se + C * (pos interest + pos dividends + pos gains + pos rent) }

def Own.person (x : Own) (paExtra donations : Int) : Person :=
  { age := x.age, wageDoh := x.wages - x.ee, pensDoh := x.pension, seDoh := x.seDoh, paExtraMonthly := paExtra,
    donations, receipts := x.wages + x.pension + pos x.se }

/-- Final taxes of one adult (cents); in 2023 with the prirez on the capital-income taxes and on the paušal tax
(Pravilnik o paušalnom oporezivanju NN 1/20 čl. 4 st. 2: "povećava se i za prirez porezu na dohodak"). -/
def Own.finalTax (y : YP) (x : Own) : Int :=
  let cap := capTaxY y x.interest + capTaxY y x.dividends + rentTaxY y x.rent
  cap + surtaxY y cap + x.pTax + surtaxY y x.pTax

/-- Result for one adult: annual tax, final taxes, contributions (cents). -/
structure PR where
  annual : Int
  final : Int
  social : Int
  person : Person

/-- The annual tax includes the year's prirez (2023: 18 % of the tax after the young relief). -/
def Own.result (y : YP) (r : Rates) (x : Own) (paExtra donations : Int) : PR :=
  let p := x.person paExtra donations
  let t := p.taxY y r
  { annual := t + surtaxY y t, final := x.finalTax y, social := x.ee + x.seC, person := p }

/-! ## Child benefit (doplatak za djecu): brackets from `Params.dzdBrackets` (ZDD NN 94/01 as amended by NN 156/23;
before March 2024 `dzdBracketsOld`, ZDD čl. 17 as in NN 138/06 and NN 58/18) -/

/-- Monthly amount per child for income per member `x` (cents), 0 above the limit. -/
def dzdPerChild (x : Int) : Int :=
  match dzdBrackets.find? (fun (lim, _) => x ≤ lim) with
  | some (_, v) => v
  | none => 0

/-- Annual doplatak for `n` eligible children with household net income `net` (cents, the year) and `members`. -/
def dzdYear (n members : Nat) (net : Int) : Int :=
  if n = 0 || members = 0 then 0 else
  let x := pos net / (12 * (members : Int))
  let per := dzdPerChild x
  if per = 0 then 0 else
  12 * ((n : Int) * per + (if n = 3 then dzdSupp3 else if n ≥ 4 then dzdSupp4 else 0))

/-- Monthly amount per child, schedule before 2024-03-01 (`dzdBracketsOld`). -/
def dzdPerChildOld (x : Int) : Int :=
  match dzdBracketsOld.find? (fun (lim, _) => x ≤ lim) with
  | some (_, v) => v
  | none => 0

/-- The year's doplatak: `y.dzdOldMonths` months under the old schedule, the rest under NN 156/23. -/
def dzdYearY (y : YP) (n members : Nat) (net : Int) : Int :=
  if n = 0 || members = 0 then 0 else
  let x := pos net * y.dzdIncomeFactorBp / 10000 / (12 * (members : Int))
  let supp := if n = 3 then dzdSupp3 else if n ≥ 4 then dzdSupp4 else 0
  let month (per : Int) : Int := if per = 0 then 0 else (n : Int) * per + supp
  y.dzdOldMonths * month (dzdPerChildOld x) + (12 - y.dzdOldMonths) * month (dzdPerChild x)

/-! ## The household -/

structure HhResult where
  tax : Int           -- all income tax (cents)
  social : Int
  employerHealth : Int
  benefit : Int
  share1 : Int
  dep1 : Bool
  dep2 : Bool
  annual1 : Int
  annual2 : Int
  final : Int
  young : Int
  base1 : Int
  base2 : Int
  pausal : Bool

def shareOptions : List Int := [10000, 7500, 5000, 2500, 0]

def computeCentsY (y : YP) (c : Canon) : HhResult :=
  let o := Canon.opts c y
  let a1 := c.adult1
  let two := c.isCouple
  let inv (x : Int) (first : Bool) : Int := if two then (if first then half1 x else half2 x) else x
  let x1 := mkOwn y o o.pausal1 a1 (inv c.interest true) (inv c.dividends true) (inv c.capitalGains true) (inv c.rentalIncome true)
  let x2? : Option Own := c.adult2?.map fun a2 =>
    mkOwn y o o.pausal2 a2 (inv c.interest false) (inv c.dividends false) (inv c.capitalGains false) (inv c.rentalIncome false)
  let partners := two && (c.married || (c.bool? "cohabiting").getD false)
  let kids := childAllowanceMonthlyY y c.nChildren
  let depAmt := dependantAmountY y
  let don := C * pos c.charitable
  match x2? with
  | none =>
    let r1 := x1.result y o.rates kids don
    let tax := r1.annual + r1.final
    let social := r1.social
    let net := C * c.gross - tax - social
    let ben := if o.dzd then dzdYearY y (c.childrenUnder 19) (1 + c.nChildren) net else 0
    { tax, social, employerHealth := x1.er, benefit := ben, share1 := 10000, dep1 := false, dep2 := false,
      annual1 := r1.annual, annual2 := 0, final := r1.final, young := r1.person.youngReliefY y o.rates,
      base1 := r1.person.baseY y, base2 := 0, pausal := x1.pausal }
  | some x2 =>
    -- dependent partner: own receipts at most 3.600 € (čl. 17 st. 1)
    let dep2 := partners && x2.receipts ≤ dependantLimitY y
    let dep1 := partners && x1.receipts ≤ dependantLimitY y && !dep2
    let eval (s : Int) : PR × PR :=
      let k1 := kids * s / BP
      let k2 := kids - k1
      let r1 := x1.result y o.rates (k1 + (if dep2 then depAmt else 0)) (half1 don)
      let r2 := x2.result y o.rates (k2 + (if dep1 then depAmt else 0)) (half2 don)
      (r1, r2)
    let total (s : Int) : Int := let (r1, r2) := eval s; r1.annual + r2.annual
    let s := match o.childShare1 with
      | some v => max 0 (min BP v)
      | none => shareOptions.foldl (fun best v => if total v < total best then v else best) 10000
    let (r1, r2) := eval s
    let tax := r1.annual + r2.annual + r1.final + r2.final
    let social := r1.social + r2.social
    let net := C * c.gross - tax - social
    let ben := if o.dzd then dzdYearY y (c.childrenUnder 19) (2 + c.nChildren) net else 0
    { tax, social, employerHealth := x1.er + x2.er, benefit := ben, share1 := s, dep1, dep2,
      annual1 := r1.annual, annual2 := r2.annual, final := r1.final + r2.final,
      young := r1.person.youngReliefY y o.rates + r2.person.youngReliefY y o.rates,
      base1 := r1.person.baseY y, base2 := r2.person.baseY y, pausal := x1.pausal || x2.pausal }

/-- The household for its tax year (2023, 2024; 2025 for any other year). -/
def computeCents (c : Canon) : HhResult := computeCentsY (ypFor c.year) c

/-- Cents to whole euros, half up. -/
def eur (x : Int) : Int := divR .halfUp x C

/-- `--eurostat` (convention, Eurostat earn_net ESMS 3.4: tax parameters "refer to the beginning of the fiscal year, i.e.
changes occurring later during the year are ignored"): for 2025 the Zagreb rates in force on 1. 1. 2025, the 2024
decision 23,6 % / 35,4 % (`zagreb2024`), which NN 152/24 čl. 14 st. 4 keeps for advances until the new decision
(NN 28/2025-291, applied from 1 March and, by čl. 14 st. 3, in the annual assessment for the whole year). A unit's
own `lowerRate`/`higherRate` input still wins. -/
def ypEurostat (y : Nat) : YP := if y = 2025 then { ypFor y with rates := zagreb2024 } else ypFor y

/-- `--euromod` (convention, EUROMOD J2.0+, documented; never statute): EUROMOD has no data on the unit of residence and
uses PIT-revenue-weighted average local rates by degree of urbanisation (EUROMOD Country Report Croatia 2022-2025,
Urban & Bezeredi, JRC 2026, § 2.8.1.7 "Tax schedules" and § 2.8.2 "Surtax (tmu_hr)"; values in "EUROMOD policy
parameters J2.0+.xlsx", sheet HR, rows 20.2.1 $tmu_rate1, 20.2.4 $tin_stdrate11, 20.2.7 $tin_stdrate21: densely
populated areas). The EUROMOD grid's template person has `drgur` = 1 (densely populated: the modal value of the HR
training data, software/euromod/MAPPING.md), so the densely-populated rates apply: 2023 surtax 16,5 % on the national
20/30 % (instead of Zagreb's 18 %); 2024 22,8 % / 34,2 %; 2025 22,4 % / 32,4 %. A unit's own `lowerRate` /
`higherRate` input still wins.
Round 15, the 30 June rule (EUROMOD "Nowcasting prices" note, Feb 2025, s. 1.3-1.4, sha256 64eb954e350abd1c...; the
HR country report itself: Annex 2, "tax-benefit policies in a given year are taken as of 30th of June",
`refs/em_CR_HR_Y16.txt` l. 5037-5038): the doplatak schedule in force on 30 June 2024 (ZDD as amended by NN 156/23,
in force 1 March 2024) applies to all twelve months of 2024 (`dzdOldMonths := 0`). No other HR tax, contribution or
doplatak parameter changes within 2023-2025 in this model (the 2025 Zagreb decision is replaced by the average rates
above anyway).
Also documented by EUROMOD for the doplatak (Country Report Croatia 2022-2025 § 2.6.8, "EUROMOD modelling",
`refs/em_CR_HR_Y16.txt` l. 2172-2176): "the income test considers incomes from the previous calendar year (Y–1).
Therefore, we multiply the current year income with a factor, which is calculated as the ratio between average
(national) net employment income in Y–1 and Y (stored in the constant $empnr)"; values from "EUROMOD policy parameters
J2.0+.xlsx", sheet HR, row 31.2.13 $empnr: 2023 0,885, 2024 0,871, 2025 0,917 (`dzdIncomeFactorBp`). -/
def ypEuromod (y : Nat) : YP :=
  if y = 2023 then { ypFor y with surtaxBp := 1650, dzdIncomeFactorBp := 8850 }
  else if y = 2024 then { ypFor y with rates := ⟨2280, 3420⟩, dzdOldMonths := 0, dzdIncomeFactorBp := 8710 }
  else { ypFor y with rates := ⟨2240, 3240⟩, dzdIncomeFactorBp := 9170 }

def outWith (args : List String) (c : Canon) : Out :=
  let est := args.contains "--eurostat"
  let y := if args.contains "--euromod" then ypEuromod c.year else if est then ypEurostat c.year else ypFor c.year
  let h := computeCentsY y c
  let unsup := ["income tax booked as localIncomeTax (shared tax of cities and counties, ZFJLP(R)S čl. 5)",
    "pensioner health contributions, disability allowances, assisted-area (I. skupina) and returnee reliefs not modelled",
    "doplatak za djecu: amounts and brackets from ZDD (NN 94/01, 138/06, 58/18, 156/23); the income test uses the year's own income where ZDD uses the previous year's; children under 19 eligible; the +15 % supplement for a child with a missing parent (čl. 21 st. 2) not modelled",
    "self-employment losses not offset against other income; drugi dohodak not modelled"] ++
    (if c.year = 2023 then ["2023: prirez of Grad Zagreb 18 % (NN 28/2017-654 čl. 4; NN titles 2016/116-2018/120 scanned: the only later Zagreb decision, NN 122/2017-2790, deletes čl. 10 on holiday homes; later issues to 2023 not scanned); paušal classes NN 156/22 + 15/23 with the 18 % prirez; doplatak schedule before NN 156/23"]
     else if c.year = 2024 then ["2024: Zagreb 23,6 %/35,4 %; doplatak: January-February old schedule, March-December NN 156/23"]
     else if c.year ≠ 2025 then ["tax year " ++ toString c.year ++ " not modelled: computed with the 2025 rules"] else [])
  Out.make c "HR" "EUR" 0 (localIncomeTax := eur h.tax) (employeeSocial := eur h.social) (benefits := eur h.benefit)
    (detail := [Out.d "taxableIncome" (eur (h.base1 + h.base2)), Out.d "annualTax1" (eur h.annual1),
      Out.d "annualTax2" (eur h.annual2), Out.d "finalTaxes" (eur h.final), Out.d "youngRelief" (eur h.young),
      Out.d "employerHealth" (eur h.employerHealth), Out.d "childShare1Bp" h.share1,
      Out.dBool "dependantPartner" (h.dep1 || h.dep2), Out.dBool "pausal" h.pausal,
      Out.d "lowerRateBp" (Canon.opts c y).rates.lower, Out.d "higherRateBp" (Canon.opts c y).rates.higher,
      Out.dStr "note" ("Zagreb " ++ toString (ypFor c.year).year ++ "; amounts computed in cents")])
    (unsupported := unsup)

def out (c : Canon) : Out := outWith [] c

def country : Country :=
  { code := "HR", name := "Croatia (Zagreb)", currency := "EUR", year := "2025", compute := out, computeWith := outWith }

end HrTax
