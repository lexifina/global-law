import TaxKernel.World

/-!
# Somalia (Federal Government): income tax of a resident individual, Income Tax Law (Sharciga Canshuurta Dakhliga),
Law No. 37 of 11 May 2025, tax year 2025

Authority: the Federal Government of Somalia (Mogadishu). Federal member states and Somaliland levy their own taxes;
they are not modelled. Grade A for the federal law text (official copy published by the Ministry of Finance), with the
caveat that the law entered into force on signature in May 2025 ("Waxa uu sharcigan dhaqan gelayaa isla marka uu
Madaxwaynaha J.F.S saxiixo": it enters into force as soon as the President signs) and no transitional rule for the
2025 tax year was read: the model applies it to the whole year.

Source: "Sh.Lr.37 - SHARCIGA CANSHUURTA DAKHLIGA" (Ministry of Finance, mof.gov.so/sites/default/files/Publications/,
Internet Archive capture 2025-10-01; 146-page scan in Somali, OCR with tesseract eng, the table checked against the page
image of p. 137 (law p. 114); `so/law/sharciga_cashuurta_dakhliga_37.pdf`). Cover: "SHARCI LR.37 TAARIIKH: 11-DA MAAJO
2025". First Schedule ("JADWALKA KOWAAD: BOQOLLEYDA CANSHUURTA (TAX RATES) (Qodobka 9)"), para. 1(1) "Rates of Income
Tax for Individuals", resident individual, annual taxable income:
  1. "Dakhliga aan ka badnayn $1,200 USD" (not exceeding $1,200): "Wax canshuur ah lagama rabo" (no tax);
  2. "Dakhliga u dhexeeya $1,201 USD ilaa $6,000 USD": "Boqolkiiba lix (6%)";
  3. "Dakhliga u dhexeeya $6,001 USD ilaa $18,000 USD": "$288 USD oo lagu daray boqolkiiba laba iyo toban (12%) oo lagu
     dhuftay inta ka badan $6000 USD" ($288 plus 12 % of the excess over $6,000);
  4. "Dakhliga ka badan $18,000 USD": "$1,788 USD oo lagu daray boqolkiiba siddeed iyo toban (18%)" of the excess over
     $18,000.
Row 4's printed $1,788 is not row 3 at $18,000 (288 + 12 % x 12,000 = 1,728): read literally the tax jumps by $60 at
$18,001 (FINDINGS F1). Model default: the printed table (`soBandReading: true` gives the band-consistent reading with
1,728). Para. 1(2): residents under 18 taxed at a flat 20 % (not modelled: the contract's adults are 18+); para. 1(4):
non-residents 18 % flat. Currency: the law is in US dollars (USD), so the model is in USD.
-/

namespace SoTax
open TaxKernel

/-- First Schedule para. 1(1) as a band schedule (the reading consistent with row 3). -/
def sched : Schedule := Schedule.ofList [(0, 0), (1200, 600), (6000, 1200), (18000, 1800)]
/-- The printed column (in ticks): rows 3 and 4 with their printed fixed amounts. -/
def printedTicks (x : Int) : Int :=
  if x ≤ 1200 then 0
  else if x ≤ 6000 then 600 * (x - 1200)
  else if x ≤ 18000 then 288 * BP + 1200 * (x - 6000)
  else 1788 * BP + 1800 * (x - 18000)

def taxPrinted (x : Int) : Int := Rule.unitDown.ofTicks (printedTicks (pos x))
def taxBand (x : Int) : Int := sched.tax Rule.unitDown (pos x)

/-- The printed rows in the kernel's column form (row 4 from 18,000). -/
def printedRows : List CumRow := [⟨0, 0, 0⟩, ⟨1200, 0, 600⟩, ⟨6000, 288, 1200⟩, ⟨18000, 1788, 1800⟩]

/-- First Schedule para. 1(3) (Law No. 37 of 2025, OCR p. 138, read on the page): when a resident individual's taxable
income includes "kororka faa'ido (gains) ee shakhsigu ka helay gacan-ka-saarista hanti maalgashi ee canshuur-gal ah"
(gains from disposing of chargeable investment assets) or a lump-sum retirement payment: "(a) dakhliga canshuur-galka ah ee
aan ka badnayn $18,000 USD" is taxed at para. 1's rates; "(b) dakhliga canshuur-galka ah ee ka badan $18,000 USD": "(i)
boqolkiiba shan iyo toban (15%), iyada oo aysan ka badan karin cadadka dhabta ah ee kororka faa'ido" (15 %, on no more than
the actual gain) and "(ii) wixii dakhli ah ee intaas kabadan ... (18%)". Art. 6 (4): gains on chargeable investment assets
(shares, interests in non-resident trusts, immovable property) are taxed on disposal; art. 14 includes them in investment
income. Round D6: `capitalGains` (net gain) now enters taxable income under this rule. -/
def taxWithGain (f : Int → Int) (other gain : Int) : Int :=
  let ti := pos other + pos gain
  if gain ≤ 0 || ti ≤ 18000 then f ti
  else
    let above := ti - 18000
    let g15 := min (pos gain) above
    f 18000 + divR .down (1500 * g15) BP + divR .down (1800 * (above - g15)) BP

/- Employment 12,000 and a gain of 10,000: 1,728 at 18,000, then 15 % of 4,000 = 600: 2,328 (the printed table on
22,000 alone would give 2,508). Employment 30,000 and a gain of 5,000: 1,728 + 15 % x 5,000 + 18 % x 12,000 = 4,638. -/
#guard taxWithGain taxPrinted 12000 10000 = 2328 ∧ taxPrinted 22000 = 2508
#guard taxWithGain taxPrinted 30000 5000 = 4638

def out (c : Canon) : Out :=
  let band := (c.bool? "soBandReading").getD false
  let f := if band then taxBand else taxPrinted
  let n := c.adults.length
  let share (x : Int) (i : Nat) : Int := if n = 1 then x else if i = 0 then half1 x else half2 x
  let ps := (c.adults.zip (List.range n)).map fun (a, i) =>
    taxWithGain f (pos (a.wages + a.selfEmployment)) (share c.capitalGains i)
  let unsup :=
    (if c.interest ≠ 0 || c.dividends ≠ 0 || c.rentalIncome ≠ 0 then ["interest, dividends and rents (withholding) not modelled"] else []) ++
    (if c.capitalGains ≠ 0 then ["capitalGains read as the net gain on chargeable investment assets (art. 6 (4)); First Schedule para. 1(3) 15 % slice applied; split equally for a couple"] else []) ++
    (if (c.adults.map (·.pension)).any (· ≠ 0) then ["pensions not modelled"] else [])
  Out.make c "SO" "USD" (sumInts ps)
    (detail := [Out.d "taxableIncome" (sumInts (c.adults.map fun a => pos (a.wages + a.selfEmployment)) + pos c.capitalGains),
      Out.dStr "reading" (if band then "band-consistent ($1,728 at $18,000)" else "printed First Schedule ($1,788 + 18 % above $18,000)"),
      Out.dStr "authority" "Federal Government of Somalia (Law No. 37 of 11 May 2025); member states and Somaliland not modelled",
      Out.dStr "note" "annual tax on taxable income in US dollars; employment and business income on the same scale"])
    (unsupported := unsup ++ ["law in force from signature (11 May 2025): applied to the whole 2025 year (transitional rules not read)",
      "deductions and exemptions of the Law (Somali text, OCR) not modelled: gross income taxed", "no social contributions found in the federal law read",
      "Federal Member State and Somaliland taxes not modelled"])

def country : Country := { code := "SO", name := "Somalia (federal Income Tax Law No. 37 of 2025)", currency := "USD", year := "2025", compute := out }

theorem sched_progressive : sched.progressive = true := by decide

/- Row 3's printed $288 is exactly row 2 at $6,000: -/
#guard taxBand 6000 = 288 ∧ taxPrinted 6000 = 288
/- Row 4's printed $1,788 is $60 more than the bands give at $18,000 ($1,728): the printed table jumps by $60 at $18,001. -/
#guard taxBand 18000 = 1728 ∧ taxPrinted 18000 = 1728 ∧ taxPrinted 18001 = 1788
#guard (cumJumps printedRows).map (·.2) = [0, 0, 0, 60 * BP]

end SoTax
