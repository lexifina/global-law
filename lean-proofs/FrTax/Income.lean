import FrTax.Decl

/-!
# From the boxes to the revenu net imposable

The categories of income (CGI art. 13), each net of its own allowances, add up to the revenu brut global;
the charges of art. 156 come off it to give the revenu net global, and the allowances of art. 157 bis and
art. 196 B come off that to give the revenu net imposable (art. 193). Every element is rounded to the euro
(art. 193, last paragraph).
-/

namespace FrTax

/-! ## Salaries (art. 79, art. 83) -/

/-- A person's salaries and the income taxed like salaries: salaries (1AJ...), other taxable income such as
unemployment benefit (1AP...), pay from private employers (1AA...), directors' pay under art. 62 (1GB...),
salaries with a French-tax-equal credit (1AF...) and other foreign salaries (1AG...). -/
def salaryBoxes : Who → List String
  | .v  => ["1AJ", "1AP", "1AA", "1GB", "1AF", "1AG"]
  | .c  => ["1BJ", "1BP", "1BA", "1HB", "1BF", "1BG"]
  | .p1 => ["1CJ", "1CP", "1CA", "1IB", "1CF", "1CG"]
  | .p2 => ["1DJ", "1DP", "1DA", "1JB", "1DF", "1DG"]
  | .p3 => ["1EJ", "1EP", "1EA", "1KB", "1EF", "1EG"]
  | .p4 => ["1FJ", "1FP", "1FA", "1LB", "1FF", "1FG"]

/-- Exempt overtime pay (art. 81 quater): 1GH, 1HH, 1IH, 1JH, 1KH, 1LH. -/
def overtimeBox : Who → String
  | .v => "1GH" | .c => "1HH" | .p1 => "1IH" | .p2 => "1JH" | .p3 => "1KH" | .p4 => "1LH"

/-- **art. 81 quater, I.** Overtime pay is exempt "dans une limite annuelle égale à 7 500 €" (loi n° 2022-1157,
since income 2022); what the box holds above that is taxable salary. -/
def taxableOvertime (d : Decl) (w : Who) : Int :=
  let lim : Int := if d.year = 2021 then 5000 else 7500   -- art. 81 quater, I, for each income year
  pos (d.get (overtimeBox w) - lim)

/-- Value-sharing bonus declared as exempt (prime de partage de la valeur), from income 2022: 1AD, 1BD, 1CD,
1DD, 1ED, 1FD; ticked 1AV, 1BV, ... when the employer has a profit-sharing scheme. -/
def ppvBox (w : Who) : String := row "1" "D" w
def ppvTick (w : Who) : String := row "1" "V" w

/-- **Loi n° 2022-1158 du 16 août 2022, art. 1, V, VI, VI bis.** The bonus is exempt from income tax "dans la
limite globale de 3 000 € par bénéficiaire et par année civile", "portée à 6 000 €" where the employer has a
profit-sharing scheme (V, third paragraph); the box holds the amount declared as exempt, and what it holds above
the limit is taxable salary (as M does: COD1ADLIM, COD1ADRET). No box before income 2022. -/
def ppvLimit (d : Decl) (w : Who) : Int := if d.has (ppvTick w) then 6000 else 3000

def ppvExempt (d : Decl) (w : Who) : Int :=
  if d.year < 2022 then 0 else max 0 (min (ppvLimit d w) (d.get (ppvBox w)))

def taxablePpv (d : Decl) (w : Who) : Int :=
  if d.year < 2022 then 0 else pos (d.get (ppvBox w) - ppvLimit d w)

def grossSalary (d : Decl) (w : Who) : Int := d.sum (salaryBoxes w) + taxableOvertime d w + taxablePpv d w

/-- Actual expenses claimed instead of the 10 % allowance (1AK, 1BK, ...). -/
def actualExpenses (d : Decl) (w : Who) : Int := d.get (row "1" "K" w)

/-- **art. 83, 3°.** The allowance for professional expenses: 10 % of the gross salary, at least `salMin`
and at most `salMax`, never more than the salary itself; or the actual expenses when claimed. -/
def salaryAllowance (p : Params) (d : Decl) (w : Who) : Int :=
  let g := grossSalary d w
  if g ≤ 0 then 0
  else
    let flat := min g (max p.salMin (min p.salMax (pct 1000 g)))
    -- The actual expenses replace the flat allowance only when larger: the option of art. 83, 3°, last
    -- paragraph, exercised in the taxpayer's favour (what M does: FRNV vs. 10 %). They are not capped at the
    -- salary: the excess is a deficit that comes off the other income (art. 156, I). The DGFiP's simulator nets
    -- it for income 2020 to 2024 alike (1AJ 21 036, 1AK 21 175, interest 449: taxable income 279).
    if d.has (row "1" "K" w) then max flat (actualExpenses d w) else flat

def netSalary (p : Params) (d : Decl) (w : Who) : Int := grossSalary d w - salaryAllowance p d w

/-- The exempt overtime pay counted in the revenu fiscal de référence (art. 1417, IV, 1°, c): at most the
7 500 € exempt under art. 81 quater, I, and, when the 10 % allowance applies, its share of the net salary:
`net × overtime / gross`, the 10 % allowance being computed on salary and overtime together. Reading: "le
montant net ... des revenus" in the first sentence of art. 1417, IV, 1° governs the additions. The share is
cut to the cent and then rounded to the euro, as M does (XHSUPV, chap-87.m). -/
def exemptShare (p : Params) (d : Decl) (w : Who) (amt : Int) : Int :=
  if amt ≤ 0 then 0 else
  -- the 10 % allowance is computed on salary, exempt overtime and exempt value-sharing bonus together (XEXTSV)
  let g := grossSalary d w + max 0 (min p.overtimeMax (d.get (overtimeBox w))) + ppvExempt d w
  let flat := min g (max p.salMin (min p.salMax (pct 1000 g)))
  let real := min (actualExpenses d w) g
  if d.has (row "1" "K" w) && real > flat then amt
  else rnd (((g - flat) * amt * 100) / g) 100

def overtimeForRfr (p : Params) (d : Decl) (w : Who) : Int :=
  exemptShare p d w (min p.overtimeMax (d.get (overtimeBox w)))

/-- **Loi n° 2022-1158, art. 1, VI quater.** The exempt value-sharing bonus is "incluse dans le montant du revenu
fiscal de référence défini au 1° du IV de l'article 1417": net of its share of the 10 % allowance, as the exempt
overtime above (M: XPRIMV, chap-87.m). -/
def ppvForRfr (p : Params) (d : Decl) (w : Who) : Int :=
  exemptShare p d w (ppvExempt d w)

/-! ## Pensions (art. 79, art. 158, 5, a) -/

/-- A person's pensions: retirement pensions (1AS...), disability pensions (1AZ...), alimony received
(1AO...). -/
def pensionBoxes : Who → List String
  | .v  => ["1AS", "1AZ", "1AO", "1AL", "1AM"]
  | .c  => ["1BS", "1BZ", "1BO", "1BL", "1BM"]
  | .p1 => ["1CS", "1CZ", "1CO", "1CL", "1CM"]
  | .p2 => ["1DS", "1DZ", "1DO", "1DL", "1DM"]
  | .p3 => ["1ES", "1EZ", "1EO", "1EL", "1EM"]
  | .p4 => ["1FS", "1FZ", "1FO", "1FL", "1FM"]

def grossPension (d : Decl) (w : Who) : Int := d.sum (pensionBoxes w)

/-- **art. 158, 5, a.** 10 % of each pensioner's pensions, at least `penMin` each (never more than the
pension), the household's total at most `penMax`. -/
def pensionAllowance (p : Params) (d : Decl) : Int :=
  let each := Who.all.map fun w =>
    let g := grossPension d w
    if g ≤ 0 then 0 else min g (max p.penMin (pct 1000 g))
  min p.penMax (each.foldl (· + ·) 0)

/-- **art. 158, 6.** Life annuities bought for value are taxed on a fraction fixed by the annuitant's age
at the first payment: 70 % under 50 (1AW), 50 % from 50 to 59 (1BW), 40 % from 60 to 69 (1CW), 30 % from 70
(1DW). -/
def annuities (d : Decl) : Int :=
  pct 7000 (d.get "1AW") + pct 5000 (d.get "1BW") + pct 4000 (d.get "1CW") + pct 3000 (d.get "1DW")

def netPensions (p : Params) (d : Decl) : Int :=
  (Who.all.foldl (fun a w => a + grossPension d w) 0) - pensionAllowance p d + annuities d

def netSalaries (p : Params) (d : Decl) : Int := Who.all.foldl (fun a w => a + netSalary p d w) 0

/-! ## Investment income taxed at the scale on option (art. 200 A, 2; art. 158, 3) -/

/-- The option for the progressive scale (box 2OP) covers all the household's investment income and gains
(art. 200 A, 2). -/
def scaleOption (d : Decl) : Bool := d.has "2OP"

/-! ## Life insurance (art. 125-0 A; art. 200 A, 2 and 2 bis)

Proceeds of contracts held eight years or more share one allowance of 4 600 € (9 200 € for a couple taxed
jointly), used first on proceeds of premiums paid before 27 September 2017 taxed at the scale (2CH), then on
those that bore the 7.5 % levy at source (2DH), then on post-2017 proceeds taxed at 7.5 % (2VV), then on those
taxed at 12.8 % (2WW) (what M does). Post-2017 proceeds of contracts under eight years (2ZZ) get no allowance and
the flat 12.8 %; pre-2017 proceeds under eight years not under the levy (2YY) are taxed at the scale. -/

structure LifeSplit where
  ch : Int   -- allowance used on 2CH
  dh : Int   -- on 2DH
  vv : Int   -- on 2VV
  ww : Int   -- on 2WW

def lifeSplit (d : Decl) : LifeSplit :=
  let a := if d.couple then 9200 else 4600
  let ch := min (pos (d.get "2CH")) a
  let dh := min (pos (d.get "2DH")) (a - ch)
  let vv := min (pos (d.get "2VV")) (a - ch - dh)
  let ww := min (pos (d.get "2WW")) (a - ch - dh - vv)
  { ch, dh, vv, ww }

/-- Post-2017 life-insurance proceeds after the allowance: at 7.5 % (2VV) and at 12.8 % (2WW, plus 2ZZ). -/
def life75 (d : Decl) : Int := pos (d.get "2VV") - (lifeSplit d).vv
def life128 (d : Decl) : Int := pos (d.get "2WW") - (lifeSplit d).ww + pos (d.get "2ZZ")

/-- **art. 158, 3, 2° and 4°.** With the option, dividends (2DC) are taxed on 60 % of their amount; fixed
income (2TR), other distributions (2TS), unlisted PEA income (2FU) in full; expenses (2CA) come off. -/
def investmentAtScale (d : Decl) : Int :=
  -- the expenses (2CA) come off all investment income taxed at the scale, life insurance included
  let opt := if scaleOption d then
    d.get "2DC" - pct 4000 (d.get "2DC") + d.get "2TR" + d.get "2TS" + d.get "2FU" + life75 d + life128 d else 0
  let life := pos (d.get "2CH") - (lifeSplit d).ch + pos (d.get "2YY")
  -- the expenses (2CA) come off only under the option (without it the flat tax of art. 200 A, 1 applies to
  -- gross income and the expenses are not deductible)
  if scaleOption d then pos (opt + life - d.get "2CA") else life

/-- **art. 125-0 A, II** (by reference from art. 158, 6 bis). Life-insurance proceeds of contracts held eight
years or more on premiums paid before 27 September 2017 (2CH) are taxed at the scale after an allowance of
4 600 €, 9 200 € for a couple taxed jointly. -/
def lifeInsuranceAtScale (d : Decl) : Int :=
  pos (d.get "2CH" - (if d.couple then 9200 else 4600))

/-- Gains on securities taxed at the scale on option (3VG net of losses 3VH). -/
def gainsAtScale (d : Decl) : Int :=
  if scaleOption d then pos (d.get "3VG" - d.get "3VH") else 0

/-! ## Property income (art. 32, art. 28) -/

/-- **art. 32, 1.** The micro-foncier: gross rents (4BE) less a flat 30 %. Under the real regime the net
result (4BA) less deficits on property income (4BB, 4BD). A deficit on general income (4BC) comes off the
revenu brut global (art. 156, I, 3°). -/
def propertyIncome (d : Decl) : Int :=
  let micro := d.get "4BE" - pct 3000 (d.get "4BE")
  pos (d.get "4BA" - d.get "4BB" - d.get "4BD") + micro

/-! ## Micro-enterprise profits (art. 50-0, art. 102 ter) -/

/-- **art. 50-0, 1; art. 102 ter, 1.** Micro-enterprise profits. For each person, one allowance per category on
the total turnover of that category: 71 % on sales (5KO, 5LO, 5MO), 50 % on services (5KP, 5LP, 5MP) together
with furnished letting outside a profession (5ND, 5OD, 5PD; income 2024 only, the 2025 return replaced these
boxes), 34 % on BNC receipts (5HQ, 5IQ, 5JQ); each allowance at least 305 € and at most the turnover. -/
def microCategories (d : Decl) : Who → List (List String × Int)
  | .v  => [(["5KO"], 7100), (["5KP"] ++ (if d.year ≤ 2024 then ["5ND"] else []), 5000), (["5HQ"], 3400)]
  | .c  => [(["5LO"], 7100), (["5LP"] ++ (if d.year ≤ 2024 then ["5OD"] else []), 5000), (["5IQ"], 3400)]
  | .p1 => [(["5MO"], 7100), (["5MP"] ++ (if d.year ≤ 2024 then ["5PD"] else []), 5000), (["5JQ"], 3400)]
  | _   => []

def microNet (d : Decl) : Int :=
  Who.all.foldl (fun a w =>
    a + (microCategories d w).foldl (fun a2 (bs, r) =>
      let g := d.sum bs
      a2 + (if g ≤ 0 then 0 else g - min g (max 305 (pct r g)))) 0) 0

/-- Profits under the real (or declared) regimes, entered as computed: BIC (5KC, 5LC, 5MC), BNC (5QC, 5RC, 5SC),
farm profits (5HC, 5IC, 5JC). -/
def realProfits (d : Decl) : Int := d.sum ["5KC", "5LC", "5MC", "5QC", "5RC", "5SC", "5HC", "5IC", "5JC"]

/-- **art. 151-0 and 197 C.** Micro-entrepreneurs who paid the flat levy (versement libératoire): sales (5TA,
5UA, 5VA), services (5TB, 5UB, 5VB), BNC (5TE, 5UE, 5VE). Their income is not taxed at the scale but counts
for the rate (art. 197 C) and in the RFR (art. 1417, IV, 1°, c), "pour leur montant diminué ... de
l'abattement prévu au 1 de l'article 50-0 ou au 1 de l'article 102 ter": 71 %, 50 %, 34 %, at least 305 €. -/
def flatLevyIncome (d : Decl) : Int :=
  -- For the rate and the RFR the allowance is computed once per person and category on the regular and the
  -- flat-levy turnover together (M: TMIB_ABVV, chap-teff.m); the flat-levy income is the combined net less the
  -- regular net.
  let net (g r : Int) := if g ≤ 0 then 0 else g - min g (max 305 (pct r g))
  let cat (reg : List String) (vl : String) (r : Int) := net (d.sum reg + d.get vl) r - net (d.sum reg) r
  let svc (x : String) := if d.year ≤ 2024 then [x] else []
  cat ["5KO"] "5TA" 7100 + cat ["5LO"] "5UA" 7100 + cat ["5MO"] "5VA" 7100
    + cat (["5KP"] ++ svc "5ND") "5TB" 5000 + cat (["5LP"] ++ svc "5OD") "5UB" 5000 + cat (["5MP"] ++ svc "5PD") "5VB" 5000
    + cat ["5HQ"] "5TE" 3400 + cat ["5IQ"] "5UE" 3400 + cat ["5JQ"] "5VE" 3400

/-! ## Revenu brut global, revenu net global, revenu net imposable -/

def grossGlobal (p : Params) (d : Decl) : Int :=
  netSalaries p d + netPensions p d + investmentAtScale d + gainsAtScale d
    + propertyIncome d + microNet d + realProfits d
    - d.get "4BC"

/-- **art. 154 quinquies, II.** With the scale option, 6.8 % of the investment income already charged to
CSG (2BH) is deductible. -/
def csgOnInvestments (d : Decl) : Int := if scaleOption d then pct 680 (d.get "2BH") else 0

/-- **art. 158, 7, 3°.** "Le montant des revenus et charges énumérés ci-après, retenu pour le calcul de l'impôt
[...], est multiplié par un coefficient de 1,25. Ces dispositions s'appliquent : [...] 3° Aux sommes mentionnées au
2° du II de l'article 156 versées en vertu d'une décision de justice devenue définitive avant le 1er janvier 2006"
(unchanged for income 2020-2025; the 1,2 / 1,15 / 1,1 of 2020-2022 concern the 1° only). The taxpayer declares
the amount paid and the increase is made in the computation (BOI-IR-BASE-20-30-20-50 § 120). Boxes: 6GP (other
alimony) and 6GI, 6GJ (adult children); not 6GU, 6EL, 6EM. Rounded to the euro (M: arr(x * MAJREV)). -/
def preReformAlimony (x : Int) : Int := pct 12500 x

/-- **art. 156, II.** The charges deducted from the revenu brut global: deductible CSG (6DE), alimony to
adult children (6EL, 6EM, each at most the amount of art. 196 B: "La déduction est limitée, par enfant majeur, au
montant fixé pour l'abattement prévu par l'article 196 B"; 6GI, 6GJ under decisions before 2006, increased by
25 % and then capped the same way, what M and the production simulator do), other alimony (6GU; 6GP under a
decision before 2006, increased by 25 %), various deductions (6DD). -/
def charges (p : Params) (d : Decl) : Int :=
  d.get "6DE" + csgOnInvestments d + min (d.get "6EL") p.attached + min (d.get "6EM") p.attached
    + min (preReformAlimony (d.get "6GI")) p.attached + min (preReformAlimony (d.get "6GJ")) p.attached
    + d.get "6GU" + preReformAlimony (d.get "6GP") + d.get "6DD"

/-- **art. 163 quatervicies.** Contributions to retirement savings (PERP and assimilated 6RS, 6RT, 6RU; new PER
6NS, 6NT, 6NU) are deductible within each person's ceiling: the ceiling of the year and the unused ceilings
of the three previous years, as printed on the last notice (APS, DPS, CPS, BPS for declarant 1; ...T for
declarant 2; ...U for a dependant). With box 6QR a married couple pools their ceilings (art. 163 quatervicies,
I, 3, c). -/
def retirementDeduction (d : Decl) : Int :=
  let ceil (s : String) := d.sum ["AP" ++ s, "DP" ++ s, "CP" ++ s, "BP" ++ s]
  let cv := d.get "6RS" + d.get "6NS"
  let cc := d.get "6RT" + d.get "6NT"
  let cp := d.get "6RU" + d.get "6NU"
  let pv := ceil "S"
  let pc := ceil "T"
  let pp := ceil "U"
  let couplePart :=
    if d.couple && d.has "6QR" then min (cv + cc) (pv + pc) else min cv pv + min cc pc
  couplePart + min cp pp

/-- The retirement deduction actually used: at most the revenu global left after the other charges (a
deduction cannot create a deficit, art. 156, II, opening words "déduction faite"). -/
def retirementUsed (p : Params) (d : Decl) (extra : Int := 0) : Int :=
  min (retirementDeduction d) (pos (grossGlobal p d + extra - charges p d))

def netGlobal (p : Params) (d : Decl) : Int := pos (grossGlobal p d - charges p d - retirementDeduction d)

/-- The revenu net global with extra income `x` added before the charges (for the rate of art. 197 C). -/
def netGlobalWith (p : Params) (d : Decl) (x : Int) : Int :=
  pos (grossGlobal p d + x - charges p d - retirementDeduction d)

/-- Is declarant 1 / declarant 2 over 65 at the end of the year (born before `year - 64`)? Years of birth:
0DA, 0DB. -/
def over65 (d : Decl) (box : String) : Bool :=
  let b := d.get box
  b > 0 && b < (d.year : Int) - 64

/-- **art. 157 bis.** For each of the couple over 65 or disabled (0AP, 0AF): `ageHi` if the revenu net
global is at most `ageT1`, `ageLo` if at most `ageT2`. -/
def ageAllowance (p : Params) (d : Decl) (rng : Int) : Int :=
  let n : Int := (if over65 d "0DA" || d.has "0AP" then 1 else 0) +
    (if d.couple && (over65 d "0DB" || d.has "0AF") then 1 else 0)
  let per := if rng ≤ p.ageT1 then p.ageHi else if rng ≤ p.ageT2 then p.ageLo else 0
  n * per

/-- **art. 196 B.** Per married (or parent) child attached (0DN), an allowance on the revenu global net. -/
def attachedAllowance (p : Params) (d : Decl) : Int := d.get "0DN" * p.attached

def taxableIncomeOn (p : Params) (d : Decl) (rng : Int) : Int :=
  pos (rng - ageAllowance p d rng - attachedAllowance p d)

def taxableIncome (p : Params) (d : Decl) : Int := taxableIncomeOn p d (netGlobal p d)

/-- The flat levy paid by micro-entrepreneurs (art. 151-0, II): 1 % of sales, 1.7 % of services, 2.2 % of BNC
receipts. -/
def flatLevyPaid (d : Decl) : Int :=
  pct 100 (d.sum ["5TA", "5UA", "5VA"]) + pct 170 (d.sum ["5TB", "5UB", "5VB"]) + pct 220 (d.sum ["5TE", "5UE", "5VE"])

end FrTax
