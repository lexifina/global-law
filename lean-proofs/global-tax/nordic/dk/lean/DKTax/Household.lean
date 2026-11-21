import DKTax.Tax

/-!
# The canonical household (`~/cmp/shared/CONTRACT.md`) through the Danish rules, and the cash benefits

Mapping (stated choices, `FAMILY_NOTES.md`):
* each adult is taxed individually (PSL); spouses (`married`) get the PSL transfers (§§ 6 stk. 3, 7 stk. 5-11,
  8 a stk. 4/6, 10 stk. 3, 11 stk. 3-4, 13 stk. 2); an unmarried couple is two individuals;
* household `interest` is positive kapitalindkomst, `dividends` + `capitalGains` (listed shares) aktieindkomst,
  `pensionContributions` private ratepension (PBL § 18), `charitable` gifts under LL § 8 A, each split equally
  (first adult gets the odd krone); `rentalIncome` is not modelled;
* wage earners pay the full-time ATP contribution (A-sats); employees have no occupational pension unless the input
  says so;
* municipality København and no church membership (as the OECD) unless the input says otherwise.

Extension fields (optional): per adult `ownPension employerPension atpOwn ratepension interestIncome
interestExpense aktie union akasse commute otherDeductions gifts groupLife`; per household `municipalRate7`
(10⁻⁷), `churchRate7`, `church` (Bool), `oecd` (Bool: OECD conventions, F3).

Benefits (`benefits`): børne- og ungeydelse (lov § 1, Skatteministeriet table) split equally between two parents
("Fra og med 2022 deles børne- og ungeydelsen som udgangspunkt lige mellem barnets forældre", Skatteministeriet,
satser for børne- og ungeydelsesloven), each share reduced by 2 pct. of the recipient's topskat base above the
bundfradrag (§ 1 a); grøn check for children (LBK 1306/2022 § 1, stk. 2 and § 5: 120 kr. per child, at most 2
children, doubled for a sole recipient) withdrawn by 7,5 pct. (§ 2, stk. 2); ordinært and ekstra børnetilskud for a
single parent (børnetilskudsloven §§ 2-3).
-/

namespace DKTax
open TaxKernel Lean

def jInt (j : Json) (k : String) (d : Int := 0) : Int := intField j k d

/-- The input object of adult `i` (for extension fields). -/
def adultRaw (c : Canon) (i : Nat) : Json := (arrField c.raw "adults")[i]?.getD Json.null

def kroner (t : Int) : Int := divR .halfUp t BP

/-- Børne- og ungeydelse for one child of `age` (lov § 1 bands). -/
def buyFor (P : Params) (age : Nat) : Int :=
  if age ≤ 2 then P.buy02 else if age ≤ 6 then P.buy36 else if age ≤ 14 then P.buy714
  else if age ≤ 17 then P.buy1517 else 0

/-- § 1 a: the ydelse a recipient receives, reduced by 2 pct. of the topskat base over the bundfradrag. -/
def buyTaper (P : Params) (share : Int) : Taper :=
  { full := share, start := P.buyTaperStart, num := P.buyTaperRate, den := BP }

/-- Grøn check for children (§ 1, stk. 2, § 5) withdrawn by 7,5 pct. (§ 2, stk. 2). -/
def gcTaper (P : Params) (full : Int) : Taper :=
  { full, start := P.gcStart, num := P.gcRate, den := BP }

/-- A household in the model's own terms (pure: every function below reduces in the kernel, so a concrete
household's figures are theorems by `decide`). `kids`: ages of the children (under 18). -/
structure HH where
  year : Nat := 2025
  married : Bool := false
  persons : List PIn
  kids : List Nat := []
  o : Opts := { munRate7 := 2350000 }
  deriving Repr

def HH.P (h : HH) : Params := paramsFor h.year
def HH.single (h : HH) : Bool := h.persons.length == 1 && !h.kids.isEmpty
def HH.bases (h : HH) : List PBase :=
  h.persons.map fun x => personBase h.P h.o.oecd { x with singleParent := h.single }
def HH.results (h : HH) : List PRes := computeTaxes h.P h.o (h.married && h.persons.length == 2) h.bases

def sumL (l : List Int) : Int := l.foldl (· + ·) 0

def HH.buyTotal (h : HH) : Int := sumL (h.kids.map (buyFor h.P))
def HH.buyShare (h : HH) (i : Nat) : Int :=
  if h.persons.length == 2 then (if i == 0 then half1 h.buyTotal else half2 h.buyTotal) else h.buyTotal
def HH.gcFull (h : HH) : Int :=
  if h.kids.isEmpty then 0 else (if h.persons.length == 1 then 2 else 1) * h.P.gcChild * (min h.kids.length 2 : Nat)
/-- Børne- og ungeydelse received, per person (after the § 1 a taper). -/
def HH.buy (h : HH) : List Int :=
  (h.results.zip (List.range h.results.length)).map fun (r, i) => (buyTaper h.P (h.buyShare i)).amount r.topBase
def HH.gc (h : HH) : List Int := h.results.map fun r => (gcTaper h.P (h.gcFull + h.P.gcAdult)).amount r.topBase
def HH.bt (h : HH) : Int := if h.single then h.P.ordBT * h.kids.length + h.P.ekstraBT else 0
def HH.benefits (h : HH) : Int := sumL h.buy + sumL h.gc + h.bt
/-- State income tax incl. aktieindkomstskat, ticks. -/
def HH.stateT (h : HH) : Int := sumL (h.results.map fun r => r.final.bund + r.final.top + r.final.ak42 + r.ak27)
def HH.localT (h : HH) : Int := sumL (h.results.map fun r => r.final.mun + r.final.ch)
def HH.am (h : HH) : Int := sumL (h.bases.map (·.am))
def HH.atp (h : HH) : Int := sumL (h.persons.map (·.atpOwn))
/-- What the household pays, net of cash benefits (kroner): state + local income tax + AM-bidrag + ATP − benefits. -/
def HH.burden (h : HH) : Int := kroner (h.stateT + h.localT) + h.am + h.atp - h.benefits
/-- Gross income (contract sense) of the household's persons. -/
def HH.gross (h : HH) : Int :=
  sumL (h.persons.map fun x => x.wages + x.selfEmp + x.pension + x.interestIncome + x.aktie)
def HH.net (h : HH) : Int := h.gross - h.burden

/-! ## OECD Taxing Wages conventions (`dktax --oecd`, round 1 2026-11-19; FINDINGS F3)

Not statute: reproduced only behind the flag (TESTING.md 2.2). (1) The OECD's average municipal rate, unrounded,
as implied by its own S100 row (SLT / (CGTC − personfradrag)): 25,018 % (2023), 25,067 % (2024), 25,068 % (2025);
Danmarks Statistik PSKAT "Hele landet" publishes 25,07 % (2024, 2025), rounded. (2) The OECD's unstated
occupational pension: employer contributions of 14,962 % (2023), 14,982 % (2024), 15,086 % (2025) of gross pay,
implied by its S67 ST_ETCD (LL § 9 J base). (3) `oecd := true`: ATP and AM-bidrag treated as the OECD does
(`Person.personBase`). Both parameters come from the dev referee itself, so a convention-mode score for DK is a
consistency check, not independent evidence. -/
def oecdMun7 (y : Nat) : Int :=
  if y = 2022 then 2498200 else if y = 2023 then 2501800 else if y = 2024 then 2506700 else 2506800
/-- Employer pension share of gross pay, in 10⁻⁷. -/
def oecdPension7 (y : Nat) : Int :=
  if y = 2022 then 1513546 else if y = 2023 then 1496242 else if y = 2024 then 1498157 else 1508641

/-- The assumed employer pension of a wage earner under `--oecd` (half-up to the krone); 0 otherwise. -/
def oecdEmployerPension (oecdFlag : Bool) (y : Nat) (w : Int) : Int :=
  if oecdFlag then (if (0 : Int) < w then divR .halfUp (oecdPension7 y * w) 10000000 else 0) else 0

def ofCanonWith (oecdFlag : Bool) (c : Canon) : HH :=
  let P := paramsFor c.year
  let n := c.adults.length
  let split (x : Int) (i : Nat) : Int := if n == 2 then (if i == 0 then half1 x else half2 x) else x
  let o : Opts :=
    { munRate7 := (c.int? "municipalRate7").getD (if oecdFlag then oecdMun7 c.year else P.munRate7),
      churchRate7 := (c.int? "churchRate7").getD P.churchRate7,
      church := (c.bool? "church").getD false,
      oecd := (c.bool? "oecd").getD oecdFlag }
  let ins : List PIn := (List.range n).map fun i =>
    let a := c.adults[i]!
    let j := adultRaw c i
    let atpDefault := if a.wages > 0 then P.atpOwn else 0
    { age := a.age, wages := a.wages, selfEmp := a.selfEmployment, pension := a.pension,
      ownPension := jInt j "ownPension",
      employerPension := jInt j "employerPension"
        (oecdEmployerPension oecdFlag c.year a.wages),
      atpOwn := jInt j "atpOwn" atpDefault, atpEmployer := jInt j "atpEmployer" (2 * jInt j "atpOwn" atpDefault),
      groupLife := jInt j "groupLife",
      ratepension := split c.pensionContributions i + jInt j "ratepension",
      interestIncome := split c.interest i + jInt j "interestIncome",
      interestExpense := jInt j "interestExpense",
      aktie := split (c.dividends + c.capitalGains) i + jInt j "aktie",
      union := jInt j "union", akasse := jInt j "akasse", commute := jInt j "commute",
      otherDed := jInt j "otherDeductions", gifts := split c.charitable i + jInt j "gifts" }
  { year := c.year, married := c.married && n == 2, persons := ins,
    kids := (c.children.filter (·.age ≤ 17)).map (·.age), o }

def ofCanon (c : Canon) : HH := ofCanonWith false c

def out (oecdFlag : Bool) (c : Canon) : Out :=
  let h := ofCanonWith oecdFlag c
  let n := h.persons.length
  let bs := h.bases
  let rs := h.results
  let am := h.am
  let atp := h.atp
  let per (k : String) (f : PRes → Int) : List (String × Json) :=
    (rs.zip (List.range n)).map fun (r, i) => Out.d s!"{k}_{i+1}" (f r)
  let detail : List (String × Json) :=
    [Out.d "taxableIncome" (sumL (rs.map (·.taxable))),
     Out.d "taxBeforeCredits" (kroner (sumL (rs.map fun r => r.bundGross + r.topPersonal + r.topCapital))),
     Out.d "basicCredit" (kroner (sumL (rs.map (·.pfState)))),
     Out.d "amBidrag" am,
     Out.d "amOnPensionContributions" (sumL (bs.map (·.amPension))),
     Out.d "atpEmployee" atp,
     Out.d "bundskat" (kroner (sumL (rs.map (·.bundGross)))),
     Out.d "topskat" (kroner (sumL (rs.map fun r => r.topPersonal + r.topCapital))),
     Out.d "aktieskat" (kroner (sumL (rs.map fun r => r.ak27 + r.ak42))),
     Out.d "kommuneKirkeGross" (kroner (sumL (rs.map fun r => r.gross.mun + r.gross.ch))),
     Out.d "personfradragUsed" (kroner (sumL (rs.map (·.pfUsed)))),
     Out.d "nedslagNegKapital" (kroner (sumL (rs.map (·.nedslag11)))),
     Out.d "carriedForward" (kroner (sumL (rs.map (·.carryForward)))),
     Out.d "boerneUngeydelse" (sumL h.buy), Out.d "groenCheck" (sumL h.gc), Out.d "boernetilskud" h.bt]
    ++ per "personalIncome" (·.b.personal) ++ per "capitalIncome" (·.b.kapital) ++ per "aktieIncome" (·.b.aktie)
    ++ per "beskaeftigelsesfradrag" (·.b.bf) ++ per "jobfradrag" (·.b.job) ++ per "ekstraPensionsfradrag" (·.b.pensDed)
    ++ per "enligForsoergerFradrag" (·.b.enlig) ++ per "taxable" (·.taxable) ++ per "topBase" (·.topBase)
  let unsupported : List String :=
    (if c.rentalIncome ≠ 0 then ["rentalIncome (LL §§ 15 O-Q / business rules not modelled; ignored)"] else [])
    ++ (if rs.any (·.b.personal < 0) then ["negative personal income (PSL § 13, stk. 3-4) not modelled"] else [])
    ++ (if sumL (rs.map (·.carryForward)) > 0 then ["deficit / negative aktieindkomst carried forward (not in this year's tax)"] else [])
    ++ (if c.adults.any (·.selfEmployment ≠ 0) then ["self-employment taxed outside virksomhedsordningen"] else [])
  Out.make c "DK" "DKK" (kroner h.stateT) (surtaxes := [("AMbidrag", am)]) (localIncomeTax := kroner h.localT)
    (employeeSocial := atp) (benefits := h.benefits) (detail := detail) (unsupported := unsupported)

def country (oecdFlag : Bool := false) : Country :=
  { code := "DK", name := "Denmark (København)", currency := "DKK", year := "2025", compute := out oecdFlag }

end DKTax
