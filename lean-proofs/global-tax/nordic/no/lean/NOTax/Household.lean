import NOTax.Years

/-!
# NOTax.Household: the canonical household (contract) mapped onto Norwegian returns

* Each adult is a separate taxpayer (sktl. § 2-11 (1)). The household's capital income (interest, dividends,
  gains, rent), debt interest, IPS contributions and gifts are split equally between two adults (contract), unless
  the input names a share for adult 1 in basis points (`capitalShare1`, `debtShare1`, `pensionShare1`,
  `giftShare1`, `childcareShare1`): spouses may own capital in any proportion, and the foreldrefradrag "gis med en
  halvpart hos hver ... dersom de ikke er enige om en annen fordeling" (§ 6-48 (3)).
* Optional fields: `shareBasis` (cost of the shares, for the skjermingsfradrag § 10-12 at 3.6 %), `debtInterest`,
  `childcareCosts` (foreldrefradrag § 6-48), `bsu1`/`bsu2` (BSU saving § 16-10), `netWealth1`/`netWealth2` (for
  § 17-1 (3)), `alderspensjon1`/`alderspensjon2` (default: pension > 0 and age ≥ 67).
* Benefits: barnetrygd for each child under 18, utvidet barnetrygd for a single adult with children (nav.no).
-/

namespace NOTax
open TaxKernel Lean

/-- Split `x` by a share for adult 1 in basis points; adult 1 gets the odd unit at 5000 (= `half1`/`half2`). -/
def shareSplit (x bp : Int) : Int × Int := (x - x * (BP - bp) / BP, x * (BP - bp) / BP)

def shareOf (c : Canon) (k : String) : Int := (c.int? k).getD 5000

/-- Foreldrefradrag cap for `n` children under 12 (SV 2025 § 6-2). -/
def foreldreCap (n : Nat) : Int := if n = 0 then 0 else foreldreFirst + foreldreNext * ((n : Int) - 1)

def persons (c : Canon) : List PersonIn :=
  let two := c.isCouple
  let sp (x : Int) (k : String) : Int × Int := if two then shareSplit x (shareOf c k) else (x, 0)
  let (i1, i2) := sp c.interest "capitalShare1"
  let (d1, d2) := sp c.dividends "capitalShare1"
  let (g1, g2) := sp c.capitalGains "capitalShare1"
  let (r1, r2) := sp c.rentalIncome "capitalShare1"
  let basis := (c.int? "shareBasis").getD 0
  let (b1, b2) := sp basis "capitalShare1"
  let (di1, di2) := sp ((c.int? "debtInterest").getD 0) "debtShare1"
  let (p1, p2) := sp c.pensionContributions "pensionShare1"
  let (gf1, gf2) := sp c.charitable "giftShare1"
  let fcap := foreldreCap (c.childrenUnder foreldreAge)
  let fAllowed := min (pos ((c.int? "childcareCosts").getD 0)) fcap
  let (f1, f2) := sp fAllowed "childcareShare1"
  let mk (a : Adult) (i d b g r di ip gf f : Int) (bsuK nwK apK : String) : PersonIn :=
    { age := a.age, wages := a.wages, pension := a.pension, business := a.selfEmployment,
      interest := i, dividends := d, skjerming := skjermingsrente * pos b / BP, gains := g, rental := r,
      debtInterest := di, ips := ip, gifts := gf, foreldre := f,
      bsu := (c.int? bsuK).getD 0, netWealth := (c.int? nwK).getD 0,
      alderspensjon := (c.bool? apK).getD (decide (0 < a.pension) && decide (67 ≤ a.age)),
      spouse := two && c.married }
  let a1 := mk c.adult1 i1 d1 b1 g1 r1 di1 p1 gf1 f1 "bsu1" "netWealth1" "alderspensjon1"
  match c.adult2? with
  | some a => [a1, mk a i2 d2 b2 g2 r2 di2 p2 gf2 f2 "bsu2" "netWealth2" "alderspensjon2"]
  | none => [a1]

def barnetrygd (c : Canon) : Int := barnetrygdYear * (c.childrenUnder 18 : Int)
def utvidet (c : Canon) : Int := if c.adults.length = 1 && c.childrenUnder 18 > 0 then utvidetYear else 0

/-- Barnetrygd by year (Stortingets vedtak "Satser for barnetrygd" under barnetrygdloven § 10, in Innst. 14 S, round 5):
* 2022 (Innst. 14 S (2021–2022) III): "barn i alderen 0 år til og med måneden før fylte 6 år med 20 112 kroner per
  år", "6 år til og med måneden før fylte 18 år med 12 648 kroner per år", "Utvidet stønad ... med 12 648 kroner per år".
* 2023 (Innst. 14 S (2022–2023) III): under 6 "1 676 kroner i måneden fra 1. januar til og med 28. februar", "1 723
  kroner" from 1 March; 6-17 "1 054 kroner i måneden fra 1. januar til og med 28. februar", "1 083 kroner" from
  1 March; utvidet "1 054 kroner per måned" January-February, "2 489 kroner per måned" from 1 March; then from
  1 July 2023 (revised budget, Innst. 490 S (2022–2023) vedtak XXXVI): "0 år til og med måneden før fylte 6 år med
  1 766 kroner per måned", "6 år til og med måneden før fylte 18 år med 1 310 kroner per måned", "utvidet barnetrygd
  ... med 2 516 kroner per måned".
* 2024 (Innst. 14 S (2023–2024) III): under 6 "21 192 kroner per år", 6-17 "18 120 kroner per år", "utvidet
  barnetrygd med 30 192 kroner per år".
Småbarnstillegg (requires full overgangsstønad) is not modelled. -/
def btChildY (y : Nat) (age : Nat) : Int :=
  if y = 2022 then (if age < 6 then 20112 else 12648)
  else if y = 2023 then (if age < 6 then 2 * 1676 + 4 * 1723 + 6 * 1766 else 2 * 1054 + 4 * 1083 + 6 * 1310)
  else if y = 2024 then (if age < 6 then 21192 else 18120)
  else 0
def barnetrygdY (c : Canon) : Int :=
  (c.children.filter (·.age < 18)).foldl (fun a k => a + btChildY c.year k.age) 0
def utvidetY (c : Canon) : Int :=
  if c.adults.length = 1 && c.childrenUnder 18 > 0 then
    (if c.year = 2022 then 12648 else if c.year = 2023 then 2 * 1054 + 4 * 2489 + 6 * 2516
     else if c.year = 2024 then 30192 else 0)
  else 0

def personDetail (k : String) (p : PersonIn) : List (String × Json) :=
  [Out.d (k ++ "personinntekt") (personinntekt p), Out.d (k ++ "minstefradrag") (minstefradrag p.wages p.pension),
   Out.d (k ++ "alminneligInntekt") (alminnelig p), Out.d (k ++ "grunnlag") (grunnlag p),
   Out.d (k ++ "kommuneskatt") (kommuneskatt p), Out.d (k ++ "fylkesskatt") (fylkesskatt p),
   Out.d (k ++ "fellesskatt") (fellesskatt p), Out.d (k ++ "trinnskatt") (trinnskattOf p),
   Out.d (k ++ "trygdeavgift") (trygdeavgift p), Out.d (k ++ "pensionCredit") (pensionCredit p),
   Out.d (k ++ "skattebegrensning") (if sbApplies p then sbTax p else -1),
   Out.d (k ++ "bsuCredit") (bsuCredit p), Out.d (k ++ "totalTax") (totalTax p)]

def out (oecd : Bool) (c : Canon) : Out :=
  let ps := persons c
  let yq := ypFor c.year
  let single : Bool := c.adults.length == 1 && decide (c.childrenUnder 18 > 0)
  let ls := match yq with
    | some q => ps.map (fun (p : PersonIn) => linesY oecd q
        (if single then ({ p with foreldre := p.foreldre + saerfradragEnslig c.year } : PersonIn) else p))
    | none => ps.map (if oecd then linesOecd else lines)
  let central := sumInts (ls.map (·.central))
  let local_ := sumInts (ls.map (·.local_))
  let social := sumInts (ls.map (·.social))
  let bt := if yq.isSome then barnetrygdY c else barnetrygd c
  let ut := if yq.isSome then utvidetY c else utvidet c
  let det := (ps.zip (List.range ps.length)).foldl (fun acc (p, i) => acc ++ personDetail s!"p{i+1}_" p) []
  Out.make c "NO" "NOK" central (localIncomeTax := local_) (employeeSocial := social) (benefits := bt + ut)
    (detail := [Out.d "cgtc" (sumInts (ps.map (match yq with | some q => grunnlagY q | none => grunnlag))),
      Out.d "taxYear" (c.year : Int), Out.d "barnetrygd" bt, Out.d "utvidetBarnetrygd" ut,
      Out.dStr "region" "Oslo (municipal 12.75 % + county 2.65 % at the maxima)",
      Out.dStr "convention" (if oecd then "OECD Taxing Wages (--oecd): lines unrounded, rounded once half up"
        else "statute")] ++ det)
    (unsupported := (if yq.isSome then ["2022-2024: småbarnstillegg not modelled; "
        ++ "pension-credit taper rates, skjermingsrente, IPS cap and the per-person detail lines use 2025 values"] else [])
      ++ ["formuesskatt (wealth tax) not modelled",
      "deductions not in the household: fagforeningsfradrag, reisefradrag, særfradrag",
      "business income: no business capital, so no skjermingsfradrag (§ 12-12)",
      "kontantstøtte and other means-tested benefits not modelled",
      "§ 17-2 joint skattebegrensning for couples not modelled (each spouse alone)"])

def country (oecd : Bool := false) : Country :=
  { code := "NO", name := "Norway (Oslo)", currency := "NOK", year := "2025", compute := out oecd }

end NOTax
