import CaTax.Household

/-!
# The findings, as statements Lean checks (FINDINGS.md numbers them)

Each `#guard` evaluates the model at build time; each `theorem` is proved for the stated inputs. Households are
canonical-contract households (whole dollars; Ontario resident; 2025).
-/

namespace CaTax
open TaxKernel

def spWith (kids : List Nat) (w : Int) : Canon :=
  { id := "sp", adults := [{ age := 35, wages := w }], children := kids.map fun a => { age := a } }

/-! F1. METR above 100 %: a single parent of four (ages 2, 4, 7, 9) earning $48,500 keeps 20 cents less after a
$100 raise (the Ontario Health Premium's 25 % step stacks on the CCB, CWB, OCB, GST/HST credit and OSTC
withdrawals and the taxes and contributions). -/
#guard netCents (spWith [2, 4, 7, 9] 48600) - netCents (spWith [2, 4, 7, 9] 48500) < 0
#guard netCents (spWith [2, 4, 7, 9] 48550) - netCents (spWith [2, 4, 7, 9] 48450) = -20

/-- F2. Pension income splitting (ITA s. 60.03): a couple aged 70 with one $200,000 pension saves $19,136.47. -/
def pensioners : Canon := { id := "p", adults := [{ age := 70, pension := 200000 }, { age := 70 }], married := true }
#guard netCents pensioners { splitPension := true } - netCents pensioners = 1913647

/-- F3. Who holds the capital: $150,000 of eligible dividends held by the spouse with no earnings rather than split
equally (wages $260,000 / $0, two children) gains $13,007.50 a year. -/
def divCouple (s : Int) : Canon :=
  { id := "d", adults := [{ age := 45, wages := 260000 }, { age := 45 }], married := true,
    children := [{ age := 8 }, { age := 12 }], dividends := 150000,
    raw := Lean.Json.mkObj [("investmentShare1", Lean.toJson s)] }
#guard netCents (divCouple 0) - netCents (divCouple 5000) = 1300750

/-- F4. Being a couple costs a two-earner family with two children ($35,000 + $60,000) $16,651.93 a year compared
with two separate households (family-income tests of the CCB, OCB, GST/HST credit, OSTC and CWB). -/
def coupleKids (m : Bool) : Canon :=
  { id := "m", adults := [{ age := 45, wages := 35000 }, { age := 45, wages := 60000 }], married := m,
    children := [{ age := 8 }, { age := 12 }] }
#guard netCents (coupleKids false) - netCents (coupleKids true) = 1712547

/-- F5. Spreading a $1,000,000 capital gain over two years (no other income) saves $42,710.50. -/
def gain (g : Int) : Canon := { id := "g", adults := [{ age := 50 }], capitalGains := g }
#guard 2 * netCents (gain 500000) - netCents (gain 1000000) - netCents (gain 0) = 4260750

/-- F8. Ontario Health Premium on "combined income" (OTA s. 24(0.1), years after 2023: taxable income plus split
income) vs the ON428 chart (taxable income only): with $20,000 taxable income and $50,000 of split income the
statute's premium is $600, the form's $0. -/
theorem ohp_split_income_gap : ohp (dol 70000) - ohp (dol 20000) = 60000 := by decide

/-- F6. Bunching beats smoothing for a family with children: a one-earner couple with two children (4 and 9) who
earns $117,534 one year and $36,221 the next keeps $10,356.20 (round 8, with the 2026 GST/HST credit changes; $10,084.20 in round 7, benefits paired with the base taxation year; $10,147.28 before) more over the two years than with $76,877 in each
(the income-tested benefits are concave: zero-reduction floors, the CCB rate falling from 13.5 % to 5.7 % above
$81,222, the CWB; and the CPP/EI ceilings). -/
def oneEarner2 (w : Int) : Canon :=
  { id := "b", adults := [{ age := 40, wages := w }, { age := 40 }], married := true,
    children := [{ age := 4 }, { age := 9 }] }
#guard netCents (oneEarner2 117534) + netCents (oneEarner2 36221) - 2 * netCents (oneEarner2 76877) = 1035620

end CaTax
