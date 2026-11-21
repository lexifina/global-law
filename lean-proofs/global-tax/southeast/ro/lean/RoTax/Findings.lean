import RoTax.Basic

/-!
# Romania 2025: the findings, each proved on concrete households (see `FINDINGS.md` for the prose)

Monthly figures are lei per month of the art. 78 final monthly wage tax; `netM g base n young` is take-home pay for a
gross monthly wage `g`, contractual base salary `base`, `n` dependants, under 26 or not.
-/

namespace RoTax
open TaxKernel

def netM (g base : Int) (n : Nat) (young : Bool) : Int :=
  wageNet (law2025 1) { gross := g, baseWage := base, deps := n, young, schoolKids := 0 }

/-! ## F1: every one of the 40 steps of the art. 77 alin. (4) table costs more than the leu that crosses it -/

/-- For every row boundary `salariul minim + 50 k` (k = 0..39), every number of dependants (0..4+) and under-26 or
not, one leu more gross pay gives less take-home pay: the marginal effective rate exceeds 100 % at 40 points. -/
theorem F1_step_metr_over_100 :
    (List.range 40).all (fun k => (List.range 5).all fun n => [false, true].all fun y =>
      decide (netM (minWage2025 + 50 * k + 1) (minWage2025 + 50 * k + 1) n y
        < netM (minWage2025 + 50 * k) (minWage2025 + 50 * k) n y)) = true := by decide

/-- Inside a row the marginal rate is the ordinary 41,5 % (25 % + 10 % + 10 % of 65 %, up to rounding): e.g. from
4.101 to 4.150 lei, 49 lei more gross give 28 lei more net. -/
theorem F1_inside_row : netM 4150 4150 0 false - netM 4101 4101 0 false = 28 := by decide

/-! ## F2: the cliff at 2.001 lei above the minimum wage (parents, dependants, under-26s) -/

/-- At 6.050 → 6.051 lei a month (minimum wage + 2.000 → + 2.001) the basic deduction disappears for anyone with a
dependant (the table's last row is still 5-25 %) and the 15 % under-26 deduction disappears: take-home pay falls by
19, 39, 60, 100 lei a month for 1, 2, 3, 4+ dependants; by 60 lei for an under-26 without dependants; by 161 lei for
an under-26 with 4 dependants. -/
theorem F2_cliff :
    (List.range 5).map (fun n => netM 6050 6050 n false - netM 6051 6051 n false) = [-1, 19, 39, 60, 100] ∧
    (List.range 5).map (fun n => netM 6050 6050 n true - netM 6051 6051 n true) = [60, 80, 100, 120, 161] := by
  decide

/-! ## F3: the OUG 156/2024 300 lei: a notch at 4.300 lei and at the first leu above the minimum base salary -/

/-- Base salary at the minimum wage, gross 4.300 → 4.301 lei: −126 lei a month (−1.512 a year). -/
theorem F3_notch_4300 : netM 4300 4050 0 false - netM 4301 4050 0 false = 126 := by decide
/-- A raise of the base salary from 4.050 to 4.051 lei: −125 lei a month (the base salary must rise to 4.279 lei, by 229 lei,
to leave the worker as well off). -/
theorem F3_notch_base : netM 4050 4050 0 false - netM 4051 4051 0 false = 125 := by decide
theorem F3_break_even : netM 4278 4278 0 false < netM 4050 4050 0 false ∧ netM 4050 4050 0 false ≤ netM 4279 4279 0 false := by
  decide

/-! ## F4: the dependent spouse test (20 % of the minimum wage) is a cross-person notch -/

def coupleCanon (spouseWages : Int) : Canon :=
  { id := "F4", adults := [{ wages := 48600 }, { wages := spouseWages }], married := true, children := [{ age := 8 }] }

/-- Earner at the minimum wage, one child; the spouse earns 810 lei a month (a dependant) or 811 (not): 12 lei more a
year for the spouse cost the household 240 lei of tax. -/
theorem F4_spouse_notch :
    (out (coupleCanon 9732)).incomeTax - (out (coupleCanon 9720)).incomeTax = 240 := by native_decide

/-! ## F5: CASS on investment income in three bands with a cap (art. 170 alin. (2)-(4)) -/

def divCass (d : Int) : Int := (investment {} { dividends := d }).2.2.2

/-- Dividends of 26.999 lei: no CASS; 27.000 lei (24.300 after the 10 % tax = 6 minimum wages): 2.430 lei. Likewise at
54.000 (+2.430) and 108.000 (+4.860). -/
theorem F5_notches : [26999, 27000, 53999, 54000, 107999, 108000].map divCass = [0, 2430, 2430, 4860, 4860, 9720] := by
  decide

/-- art. 170 alin. (3) lit. c): at or above 24 minimum wages the base is 24 minimum wages. -/
theorem invCassBase_top (mw inc : Int) (h : 24 * mw ≤ inc) : invCassBase mw inc = 24 * mw := by
  unfold invCassBase; simp [h]

/-- Above 108.000 lei of dividends the CASS is a fixed 9.720 lei for any amount: the marginal CASS rate is 0, so the
average CASS rate falls towards 0 (regressive cap). Proved for all amounts. -/

theorem F5_cap (d : Int) (h : 108000 ≤ d) : divCass d = 9720 := by
  have e : divCass d = pctOf cassRate (invCassBase minWage2025
      ((pos 0 - pctOf interestRate (pos 0)) + (pos d - pctOf dividendRate2025 (pos d)) + pos 0
        + (pos 0 - pctOf rentForfeit (pos 0)))) := rfl
  rw [e, invCassBase_top]
  · decide
  · simp only [pctOf, divR, pos, BP, minWage2025, interestRate, dividendRate2025, rentForfeit]; omega

/-! ## F6: splitting dividends with a spouse, or across years, below the 6-minimum-wage threshold -/

/-- 53.998 lei of dividends in one hand: 2.430 lei CASS; split 26.999 + 26.999 between spouses (or two years): 0. -/
theorem F6_split : divCass 53998 = 2430 ∧ divCass 26999 + divCass 26999 = 0 := by decide

/-- But above the cap splitting doubles the CASS: 400.000 lei in one hand pay 9.720; split, 19.440. -/
theorem F6_split_high : divCass 400000 = 9720 ∧ divCass 200000 + divCass 200000 = 19440 := by decide

/-! ## F7: timing: dividends distributed in 2025 (10 %) instead of 2026 (16 %) -/

theorem F7_timing : (investment {} { dividends := 100000 }).1 = 10000 ∧
    (investment { divRate := dividendRate2026 } { dividends := 100000 }).1 = 16000 ∧
    (investment { divRate := dividendRate2024 } { dividends := 100000 }).1 = 8000 := by decide

/-! ## F8: independent activities: the 12-minimum-wage CAS notch (art. 148) -/

def pfaNet (se : Int) (exempt : Bool) : Int := let (a, b, c) := pfa minWage2025 se exempt; se - a - b - c

/-- Net income 48.599 → 48.600 lei (12 minimum wages): CAS of 12.150 lei becomes due; take-home falls by 10.934 lei.
At 24 minimum wages (97.200) the CAS base doubles: −12.150 + 1.215 of tax relief. -/
theorem F8_cas_notch : pfaNet 48599 true - pfaNet 48600 true = 10934 ∧
    pfaNet 97199 true - pfaNet 97200 true = 10934 := by decide

/-! ## F9: pensions month by month in 2025 (CASS from August, art. 157^6) -/

/-- A pension of 5.000 lei a month: January-July 200 lei tax a month; August-December 200 lei CASS and 180 lei tax:
2025 totals CASS 1.000, tax 2.300 (a full year under the new rule would be 2.400 + 2.160). -/
theorem F9_pension_2025 : pensionYear 60000 = (1000, 2300) := by decide

/-! ## F10: owner-manager: PFA (sistem real) overtakes micro-enterprise + minimum salary + dividends -/

/-- Micro-enterprise with revenue = profit `p` (art. 51: 1 % up to 60.000 EUR = 298.446 lei at the BNR rate of
31.12.2024, 3 % above), the owner employed at the minimum wage (art. 47 alin. (1) lit. g); CAM 2,25 %, art. 220^3, not
on the 300 lei), the rest paid out as 2025 dividends (10 % + CASS bands). Owner's take-home. -/
def microRoute (p : Int) : Int :=
  let wage := 12 * minWage2025
  let cam := pctOf 225 (wage - 12 * untaxed2025)
  let rate := if p ≤ 298446 then microLow else microHigh
  let d := p - wage - cam - pctOf rate p
  let w := wageYear law2025 wage (fun _ => minWage2025) 0 false 0
  let (it, _, _, cc) := investment {} { dividends := d }
  wage + d - w.cas - w.cass - w.tax - it - cc

/-- At 400.000 lei of profit the micro route leaves more; at 1.000.000 lei the PFA does (CAS capped at 24 and CASS at 60
minimum wages, art. 148 and 170 alin. (1), against 3 % of revenue + 10 % of dividends). -/
theorem F10_crossover : pfaNet 400000 false < microRoute 400000 ∧ microRoute 1000000 < pfaNet 1000000 false := by
  decide

end RoTax
