import TaxKernel.World

/-!
# Tajikistan: income tax of individuals (Tax Code 2021, edition of 14.05.2025) and the insured person's social tax,
tax year 2025

Statutes read (official PDFs of the Tax Committee, andoz.tj > Legislation > Tax Code; fetched from the laptop because
the site does not answer lean1; files and sha256 in `tj/law/`): the Tax Code as amended to 14.05.2025 in Tajik
(`Tax-Code__14_05_2025-RT_tj.pdf`) and the Committee's English text of the same edition
(`Kodex_14_05_2025_Nav_ENG_en.pdf`; every number used was checked in the Tajik text):
* art. 183(1): "Taxable income of an individual resident at the main place of employment in excess of the amount of
  personal deduction shall be taxed at the rate of 12 percent" (Tajik "бо меъёри 12 фоиз"); (3) other natural persons
  15 % "without deductions provided for by Article 191 ... except for social tax for the insured person".
* art. 191(1): personal deduction "two calculated indicators for each calendar month" ("ду нишондиҳанда барои
  ҳисобҳо"); 191(6): the insured person's social tax withheld under art. 332(2) is deducted.
* art. 332(2): social tax of insured persons "for budgetary institutions - 1 percent; for other organizations - 2
  percent".
* art. 189(1)(4): "state and insurance pensions" not taxed; art. 237(1): dividends 12 % at source, final (237(2));
  art. 238(1): interest 12 % at source, final for a natural person (238(3)).
* Law on the State Budget 2025 (andoz.tj > Legislation > Laws; adopted 4 Dec 2024 No. 1487), art. 23(1): "Аз 1 январи
  соли 2025 нишондиҳанда барои ҳисобҳо ... ба андозаи 75 сомонӣ муқаррар карда шавад".
Default employer: an organisation other than a budgetary institution; input `"sector": "public"` gives 1 %.
-/

namespace TjTax
open TaxKernel

def pct (bp x : Int) : Int := divR .halfUp (x * bp) 10000

def indicator : Int := 75          -- budget law 2025 art. 23(1)
def rate : Int := 1200             -- art. 183(1)
def sched : Schedule := Schedule.flat rate
def otherRate : Int := 1500        -- art. 183(3)
def socRate : Int := 200           -- art. 332(2), other organisations
def socRatePublic : Int := 100     -- art. 332(2), budgetary institutions
def divRate : Int := 1200          -- art. 237(1)
def intRate : Int := 1200          -- art. 238(1)
/-- art. 191(1): two indicators a month. -/
def personalYear : Int := 12 * 2 * indicator
#guard personalYear = 1800

def out (c : Canon) : Out :=
  let pub := (c.str? "sector") == some "public"
  let rows := c.adults.map fun a =>
    let w := pos a.wages
    let soc := pct (if pub then socRatePublic else socRate) w
    let base := if w > 0 then pos (w - personalYear - soc) else 0
    (sched.tax Rule.unitHalfUp base + pct otherRate (pos a.selfEmployment), soc, base)
  let earnTax := sumInts (rows.map (·.1))
  let soc := sumInts (rows.map (·.2.1))
  let divTax := pct divRate (pos c.dividends)
  let intTax := pct intRate (pos c.interest)
  let rentTax := pct otherRate (pos c.rentalIncome)
  let cgTax := pct otherRate (pos c.capitalGains)
  Out.make c "TJ" "TJS" (earnTax + divTax + intTax + rentTax + cgTax) (employeeSocial := soc)
    (detail := [Out.d "taxableIncome" (sumInts (rows.map (·.2.2))), Out.d "earningsTax" earnTax,
      Out.d "socialTaxInsured" soc, Out.d "dividendTax" divTax, Out.d "interestTax" intTax,
      Out.d "rentTax" rentTax, Out.d "capitalGainsTax" cgTax,
      Out.dStr "note" "12 % above 2 indicators (75 TJS) a month at the main job, social tax 2 % deducted (TC arts. 183, 191, 332)"])
    (unsupported := ["wages assumed from one main employer for the whole year (personal deduction only there, art. 191(4)-(5))",
       "self-employment, rent and capital gains taxed at 15 % (art. 183(3)); patent/certificate regimes and the entrepreneur's social tax (art. 332(3)-(4)) not modelled",
       "pensions assumed state or insurance pensions: exempt (art. 189(1)(4))",
       "art. 191(8) deduction for non-cash spending (up to 10 % of income) not modelled (needs spending data)",
       "the Tax Committee's English text was used for reading; numbers checked in the Tajik text"])

def country : Country := { code := "TJ", name := "Tajikistan (income tax + social tax)", currency := "TJS", year := "2025", compute := out }

theorem sched_progressive : sched.progressive = true := by decide

/- 2 000 somoni a month: social tax 480, base 24 000 - 1 800 - 480 = 21 720, tax 2 606. -/
#guard (out { id := "t", adults := [{ wages := 24000 }] }).incomeTax = 2606

end TjTax
