import TaxKernel.World

/-!
# Nepal: income tax of a resident natural person, income year 2081/82 (16 July 2024 - 16 July 2025)

Access tier A. CONTRACTWORLD: the fiscal year that holds most of calendar 2025 is 2081/82 (1 Jan - 16 Jul 2025,
196 days) rather than 2082/83 (17 Jul - 31 Dec 2025, 168 days). Both give the same model: every provision used here
was last changed by the Finance Act 2080 or earlier (the footnotes of the consolidated text date each wording).

Statute: आयकर ऐन, २०५८ (Income Tax Act 2058) "आर्थिक ऐन, २०८२ ले गरेको संशोधन सहित" (consolidated with the
amendments up to the Finance Act 2082), published by the Government of Nepal on its document CDN
(giwmscdnone.gov.np/media/pdf_upload/...; the CDN refuses scripted GETs, so read from the Internet Archive copy of
2026-04-20, `np/law/ita2058_fa2082.pdf`, sha256 8a1ca760...; text layer in Devanagari, checked against the page
text). Schedule 1 para 1 (1), (2), (9क), (11); s. 12; s. 50; s. 63; s. 88 (2)(क), (3); s. 92 (1)(क), (ङ).
Income Tax Rules 2059 r. 21 (consolidation to the 13th amendment, 2079; Internet Archive 2026-08-11,
`np/law/itr2059.pdf`, sha256 b903dbd5...). Global law holds only the 2018 Law Commission compilation (outdated).
The Finance Act 2081 itself is on mof.gov.np as a flip-book whose PDF the CDN does not serve to scripts.
-/

namespace NpTax
open TaxKernel

def roundR : Rule := { mode := .halfUp }

/-- Schedule 1 para 1 (1) (natural person; (ङ) as amended by the Finance Act 2080): (क) up to 5 lakh of employment
taxable income 1 %; (ख) 5-7 lakh: 5,000 + 10 %; (ग) 7-10 lakh: 25,000 + 20 %; (घ) 10-20 lakh: 85,000 + 30 %; (ङ) 20-50
lakh: "खण्ड (घ) बमोजिम लागेको करको दरमा थप बीस प्रतिशत" (30 % + 20 % of 30 % = 36 %), above 50 lakh "थप तीस प्रतिशत"
(30 % + 30 % of 30 % = 39 %). The 1 % of (क) is shown separately (`sst`); the band schedule has 0 there. -/
def single : Schedule :=
  Schedule.ofList [(0, 0), (500000, 1000), (700000, 2000), (1000000, 3000), (2000000, 3600), (5000000, 3900)]

/-- Para 1 (2): a couple that elects under s. 50: (क) 6 lakh 1 %; (ख) 6-8 lakh 6,000 + 10 %; (ग) 8-11 lakh 26,000 +
20 %; (घ) 11-20 lakh 86,000 + 30 %; (ङ) as (1). -/
def couple : Schedule :=
  Schedule.ofList [(0, 0), (600000, 1000), (800000, 2000), (1100000, 3000), (2000000, 3600), (5000000, 3900)]

def firstBand (isCouple : Bool) : Int := if isCouple then 600000 else 500000

/- The printed amounts (5,000 / 25,000 / 85,000; couple 6,000 / 26,000 / 86,000) are the 1 % band plus the band sums. -/
#guard (single.ticks 700000) / BP + 5000 = 25000 ∧ (single.ticks 1000000) / BP + 5000 = 85000
#guard (couple.ticks 800000) / BP + 6000 = 26000 ∧ (couple.ticks 1100000) / BP + 6000 = 86000

/-- Para 1 (1)(क) proviso: the 1 % does not apply to registered sole proprietors, pension income, or a person who
contributes to the contribution-based Social Security Fund or a pension fund. -/
def sst (empTI band : Int) (exempt : Bool) : Int := if exempt then 0 else divR .halfUp (100 * min (pos empTI) band) BP

/-- Para 1 (9क): a resident person with pension income deducts 25 % of the first-band amount (cap "तोकिए बमोजिम":
not located in the 2079 Rules; not applied). -/
def pensionDeduction (isCouple : Bool) (pension : Int) : Int := if pension > 0 then min pension (firstBand isCouple / 4) else 0

/-- Rules 2059 r. 21: retirement contribution deduction (s. 63) up to "तीन लाख रुपैयाँ वा ... निर्धारणयोग्य आयको एक
तिहाई" whichever is less (SSF contributors: five lakh). -/
def retirementCap (assessable : Int) (ssf : Bool) : Int := min (if ssf then 500000 else 300000) (pos assessable / 3)

/-- s. 12 (2): donations deductible up to "एक लाख रुपैयाँ वा ... समायोजित करयोग्य आयको पाँच प्रतिशत" whichever is less. -/
def donationCap (adjusted : Int) : Int := min 100000 (divR .down (500 * pos adjusted) BP)

/-- s. 88 (2)(क) 5 % on dividends and s. 88 (3) 6 % on bank and listed-company interest to natural persons; both
final withholding payments under s. 92 (1)(क) and (ङ). -/
def dividendRate : Int := 500
def interestRate : Int := 600

/-- Tax of one return (one person, or an electing couple): employment income, other business income, pension. -/
structure ReturnIn where
  isCouple : Bool
  emp : Int
  bus : Int
  pension : Int
  retirement : Int
  donation : Int
  ssf : Bool
  womanOnlyRemuneration : Bool

structure ReturnOut where
  ti : Int
  tax : Int
  sstAmt : Int

def taxReturn (r : ReturnIn) : ReturnOut :=
  let assess := r.emp + r.bus + r.pension
  let ret := min r.retirement (retirementCap assess r.ssf)
  let adj := pos (assess - ret)
  let don := min r.donation (donationCap adj)
  let pd := pensionDeduction r.isCouple r.pension
  let ti := pos (adj - don - pd)
  let empTI := min ti (pos (r.emp - ret))
  let s := if r.isCouple then couple else single
  let main := s.tax roundR ti
  let soc := sst empTI (firstBand r.isCouple) (r.ssf || (r.emp = 0 && r.pension > 0))
  -- Para 1 (11): a resident woman earning only remuneration gets a 10 % rebate of the tax (applied to both parts).
  let reb (x : Int) : Int := if r.womanOnlyRemuneration && r.bus = 0 then x - divR .halfUp (x * 1000) BP else x
  { ti, tax := reb main + reb soc, sstAmt := reb soc }

def compute (c : Canon) : Out :=
  let n := c.adults.length
  let female (i : Nat) := c.str? (if i = 0 then "npSex1" else "npSex2") == some "female"
  let ssf := (c.bool? "npSSF").getD false
  let mk (i : Nat) (a : Adult) : ReturnIn :=
    { isCouple := false, emp := a.wages, bus := a.selfEmployment, pension := a.pension,
      retirement := if i = 0 then c.pensionContributions else 0, donation := if i = 0 then c.charitable else 0,
      ssf := ssf, womanOnlyRemuneration := female i && a.selfEmployment = 0 }
  let sep := (c.adults.zip (List.range n)).map fun (a, i) => taxReturn (mk i a)
  let sepTax := sumInts (sep.map (·.tax))
  -- s. 50: a resident person and resident spouse may elect to be treated as a couple (one return).
  let coupleR : Option ReturnOut :=
    if n = 2 && c.married then
      let a := c.adult1
      let b := c.adults[1]!
      let r : ReturnIn :=
        { isCouple := true, emp := a.wages + b.wages, bus := a.selfEmployment + b.selfEmployment,
          pension := a.pension + b.pension, retirement := c.pensionContributions, donation := c.charitable,
          ssf := ssf, womanOnlyRemuneration := false }
      some (taxReturn r)
    else none
  let forced := c.bool? "npCoupleElection"
  let useCouple := match coupleR, forced with
    | some _, some f => f
    | some r, none => r.tax < sepTax
    | none, _ => false
  let (tax, ti, sstT) := match coupleR, useCouple with
    | some r, true => (r.tax, r.ti, r.sstAmt)
    | _, _ => (sepTax, sumInts (sep.map (·.ti)), sumInts (sep.map (·.sstAmt)))
  Out.make c "NP" "NPR" (tax - sstT)
    (surtaxes := [("socialSecurityTax1pct", sstT), ("interestFinal6", divR .halfUp (interestRate * pos c.interest) BP),
                  ("dividendFinal5", divR .halfUp (dividendRate * pos c.dividends) BP)])
    (detail := [Out.d "taxableIncome" ti, Out.dStr "unit" (if useCouple then "couple (s. 50 election)" else "individual")])
    (unsupported := (if c.rentalIncome ≠ 0 then ["rental income of a non-business natural person: final payment (s. 92 (1)(ख)) taxed by local government house-rent tax; not modelled"] else []) ++
      (if c.capitalGains ≠ 0 then ["gains on non-business taxable assets (para 1 (4): 5 %/7.5 %/10 % by asset and holding) not modelled"] else []) ++
      ["women's 10 % rebate (para 1 (11)) applied only with npSex1/npSex2 = female; Social Security Fund contributions (11 %) not modelled (npSSF only removes the 1 % tax)",
       "pension deduction cap 'as prescribed' (para 1 (9क)) not located: 25 % of the first band applied in full"])

def country : Country :=
  { code := "NP", name := "Nepal (income year 2081/82)", currency := "NPR", year := "2081/82 (2024-25)", compute := compute }

theorem sched_progressive : single.progressive = true := by decide
abbrev sched : Schedule := single

end NpTax
