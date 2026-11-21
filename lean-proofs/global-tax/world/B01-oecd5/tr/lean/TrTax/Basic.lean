import TrTax.Params

/-!
# Türkiye 2025: wage tax, minimum-wage exemption, contributions, stamp duty, annual declaration

Unit of assessment: the individual (GVK art. 92 and 86: each person declares his own income; no joint return).
Amounts in kuruş inside, whole TL in the output (contract).

Wages (GVK art. 61-64, 94, 103-104): a year's wage is paid in 12 equal monthly instalments (canonical household;
the remainder of the division goes to the later months). Each month:
1. employee premiums 15 % (SSK art. 81 (a), (f); İSK art. 49) on the wage up to the art. 82 ceiling;
2. the tax base is the wage less those premiums (GVK art. 63 "gerçek safi değer"; İSK art. 49: "sigortalılarca
   ödenen primler de gerçek ücretin hesaplanmasında gelir vergisi matrahından indirilir");
3. the month's tax is the wage tariff on the cumulative base less the tariff on the previous cumulative base
   (the cumulative method; `cumWithholdings`, kernel 1.3); with equal pay this sums to the tariff on the annual base
   (GVK art. 104 first paragraph);
4. the minimum-wage exemption (GVK art. 23 (18)): the tax "istisna tutara isabet eden kısım" is deducted, and the tax
   not collected "ilgili ayda aylık asgari ücret üzerinden hesaplanması gereken vergiyi aşamaz": the model deducts,
   each month, the lesser of the month's tax and the cumulative-method tax of a minimum-wage earner in that month
   (reading R1 in FINDINGS: the cap read as the minimum-wage earner's own cumulative tax for the month);
5. stamp duty 7,59 ‰ on the wage less the monthly gross minimum wage (DVK (2) sayılı tablo IV-34 and (1) sayılı tablo
   IV-1 (b)).
-/

namespace TrTax
open TaxKernel

/-- Month `m` (1..12) of an annual amount in kuruş: equal instalments, remainder spread to later months. -/
def monthOf (annual : Int) (m : Int) : Int := annual * m / 12 - annual * (m - 1) / 12

def months : List Int := [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]

/-- Employee premium on a monthly wage (kuruş, half-up to the kuruş: reading, the statute sets no rounding). -/
def premium (g : Int) : Int := divR .halfUp (min g ssCeiling * rateEmployee) BP

/-- Tax (kuruş, down) of the wage tariff on a cumulative base in kuruş. -/
def wageT (x : Int) : Int := wageTariff.ticks x / BP

/-- Tax (kuruş, down) of the general tariff. -/
def genT (x : Int) : Int := tariff.ticks x / BP

/-- Monthly tax base of a minimum-wage earner: the gross minimum wage less the employee premiums (GVK art. 23 (18):
"asgari ücretin aylık brüt tutarından işçi sosyal güvenlik kurumu primi ve işsizlik sigorta primi düşüldükten sonra
kalan tutarı"). -/
def mwBase : Int := minWage - premium minWage

/-- One month's figures for a person with annual wage `w` kuruş. -/
structure Month where
  gross : Int
  prem : Int
  base : Int
  cum : Int
  taxGross : Int
  exempt : Int
  stamp : Int
  deriving Repr

def monthFig (w : Int) (m : Int) : Month :=
  let cumBase := fun (k : Int) => (List.range (Int.toNat k)).foldl (fun s (i : Nat) =>
    let g := monthOf w ((i : Int) + 1)
    s + (g - premium g)) 0
  let g := monthOf w m
  let p := premium g
  let cum := cumBase m
  let prev := cumBase (m - 1)
  let own := wageT cum - wageT prev
  let mw := wageT (m * mwBase) - wageT ((m - 1) * mwBase)
  { gross := g, prem := p, base := g - p, cum, taxGross := own, exempt := min own mw,
    stamp := divR .halfUp (pos (g - minWage) * stampNum) stampDen }

/-- A person's wage year. -/
structure WageYear where
  premiums : Int
  base : Int
  taxGross : Int
  exempt : Int
  tax : Int
  stamp : Int
  deriving Repr

def wageYear (wTL : Int) : WageYear :=
  if wTL ≤ 0 then ⟨0, 0, 0, 0, 0, 0⟩ else
  let w := wTL * KR
  let ms := months.map (monthFig w)
  { premiums := sumInts (ms.map (·.prem)), base := sumInts (ms.map (·.base)),
    taxGross := sumInts (ms.map (·.taxGross)), exempt := sumInts (ms.map (·.exempt)),
    tax := sumInts (ms.map fun x => pos (x.taxGross - x.exempt)), stamp := sumInts (ms.map (·.stamp)) }

/-- Residential rent declared by one person (TL in, kuruş out): GVK art. 21 exemption (47.000 TL, lost when gross
income exceeds 1.200.000 TL), then the 15 % lump-sum expense of art. 74 on the taxable part. -/
def rentNet (rentTL grossTL : Int) : Int :=
  if rentTL ≤ 0 then 0 else
  let ex := if grossTL ≤ rentExemptLimitTL then min rentTL rentExemptTL else 0
  let taxable := (rentTL - ex) * KR
  taxable - divR .down (taxable * rentLumpRate) BP

/-- One person's tax (kuruş): wage withholding net of the exemption, plus the annual declaration of rent and
self-employment income (GVK art. 85-86, 103). Wages are declared only above the art. 86 (1) (b) limit; then the
declared income is stacked on the wage base under the general tariff (reading R2). -/
structure Person where
  wage : WageYear
  rent : Int
  se : Int
  wagesDeclared : Bool
  declTax : Int
  deriving Repr

def person (wTL seTL rentTL : Int) : Person :=
  let wy := wageYear wTL
  let gross := wTL + seTL + rentTL
  let rn := rentNet rentTL gross
  let se := pos seTL * KR
  let other := rn + se
  let decl := wy.base > wageDeclLimitTL * KR
  let dt := if other ≤ 0 then 0 else
    if decl then pos (genT (wy.base + other) - genT wy.base) else genT other
  { wage := wy, rent := rn, se, wagesDeclared := decl, declTax := dt }

def toTL (k : Int) : Int := divR .halfUp k KR

def out (c : Canon) : Out :=
  let n := c.adults.length
  let rentShares : List Int := if n == 2 then [half1 c.rentalIncome, half2 c.rentalIncome] else [c.rentalIncome]
  let ps := (c.adults.zip rentShares).map fun (a, r) => person a.wages a.selfEmployment r
  let wageTax := sumInts (ps.map (·.wage.tax))
  let decl := sumInts (ps.map (·.declTax))
  let stamp := sumInts (ps.map (·.wage.stamp))
  let prem := sumInts (ps.map (·.wage.premiums))
  let unsup :=
    (if c.interest != 0 then ["interest: final withholding at rates set by presidential decision (GVK geçici 67); not modelled"] else []) ++
    (if c.dividends != 0 then ["dividends: half exempt (GVK art. 22 (3)) with withholding under art. 94 at a rate set by presidential decision not reached; not modelled"] else []) ++
    (if c.capitalGains != 0 then ["capitalGains: listed shares taxed by withholding under GVK geçici 67 at rates set by presidential decision; not modelled"] else []) ++
    (if c.adults.any (·.pension != 0) then ["pension: SGK pension treatment not modelled"] else []) ++
    (if c.adults.any (·.selfEmployment != 0) then ["selfEmployment: taken as net income (GVK art. 66-68 expenses unknown); Bağ-Kur premiums (SSK art. 4/1-b) not modelled"] else []) ++
    (if c.charitable != 0 || c.pensionContributions != 0 then ["charitable/pensionContributions: GVK art. 63 (3) and 89 deductions not modelled"] else [])
  Out.make c "TR" "TRY" (toTL (wageTax + decl)) (surtaxes := [("stampDutyOnWages", toTL stamp)])
    (employeeSocial := toTL prem)
    (detail := [Out.d "wageTaxBase" (toTL (sumInts (ps.map (·.wage.base)))),
                Out.d "wageTaxBeforeExemption" (toTL (sumInts (ps.map (·.wage.taxGross)))),
                Out.d "minimumWageExemption" (toTL (sumInts (ps.map (·.wage.exempt)))),
                Out.d "wageTax" (toTL wageTax), Out.d "declaredIncomeTax" (toTL decl),
                Out.d "taxableIncome" (toTL (sumInts (ps.map fun p => p.wage.base + p.rent + p.se))),
                Out.dStr "note" "individual assessment; no child relief: GVK art. 31 has disability amounts only; art. 32 (asgari geçim indirimi) is among the repealed provisions (193-mulga)"])
    (unsupported := unsup)

def country : Country :=
  { code := "TR", name := "Türkiye (gelir vergisi, damga vergisi, SGK)", currency := "TRY", year := "2025",
    compute := out }

end TrTax
