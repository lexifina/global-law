import DeTax.Params

/-!
# Employee social contributions 2025 (Sozialversicherung)

For each adult, on a year of earnings paid evenly over twelve months:

* **Beschäftigte** (SGB IV § 7): Rentenversicherung 9,3 % and Arbeitslosenversicherung 1,3 % up to the BBG of
  96 600 €; Krankenversicherung 7,3 % + half the average Zusatzbeitrag (1,25 %) and Pflegeversicherung 1,8 %
  (+ 0,6 % childless from 23; − 0,25 % for each child under 25 from the second to the fifth) up to 66 150 €.
* **Geringfügige Beschäftigung** (Minijob, SGB IV § 8 (1) Nr. 1: at most 556 € a month = 6 672 € a year): no
  employee contribution; we assume the employee has asked to be exempt from RV (SGB VI § 6 (1b)), as most do.
* **Übergangsbereich** (SGB IV § 20 (2), (2a); SGB V § 249 (3)): 556,01 € to 2 000 € a month: the employee's share
  is computed on the reduced base `OG / (OG − G) × (AE − G)` = 2 000 / 1 444 × (AE − 556).
* **Rentner** (statutory pension, KVdR): KV 7,3 % + 1,25 % (SGB V § 249a) and the full PV 3,6 % (SGB XI § 59 (1)),
  with wages first under the KV ceiling.
* **Selbständige** whose self-employment is their main activity (more than any wage above the Minijob limit, above
  the family-insurance limit of 535 € a month, no statutory pension): voluntary GKV at the ermäßigter Beitragssatz
  14,0 % (no Krankengeld, SGB V § 243) plus the full Zusatzbeitrag 2,5 %, and PV 3,6 % (+ 0,6 %), on the profit
  between the minimum base 14 980 € (SGB V § 240 (4)) and 66 150 €. Rental and capital income, which
  SGB V § 240 also counts for voluntary members, are left out.

Simplifications (stated): annual instead of monthly computation (the BBG and the Übergangsbereich are monthly in
law; with equal monthly pay the result is the same up to cent rounding); employees over 66 with a pension, and all
over 67, past the Regelaltersgrenze, pay no RV/AV (SGB VI § 5 (4), SGB III § 28 (1) Nr. 1); no Saxony PV rule; the
average Zusatzbeitrag for every insurer; no private health insurance; no Midijob for apprentices.
Each annual amount is rounded half up to the cent.
-/

namespace DeTax

/-- One adult's contributions, in cents. -/
structure Sv where
  rv : Int := 0
  av : Int := 0
  kv : Int := 0
  pv : Int := 0
  /-- Tax-free employer share of RV (EStG § 3 Nr. 62), needed for § 10 (3) Satz 5. -/
  rvEmployer : Int := 0
  /-- Of `kv`, the part deductible under § 10 (1) Nr. 3 (after the 4 % cut where Krankengeld can be due). -/
  kvBasis : Int := 0
  /-- § 10 (4) Höchstbetrag that applies to this person (euros). -/
  hb4 : Int := P.hb10_4Employee
  minijob : Bool := false
  /-- Of the total, the KV/PV on the statutory pension and the voluntary KV/PV on self-employment (cents). -/
  onPension : Int := 0
  onSelfEmployment : Int := 0
  /-- 0 regular, 1 Minijob, 2 Übergangsbereich, 3 pensioner only, 4 self-employed (voluntary GKV), 5 none. -/
  kind : Nat := 5
  deriving Repr

def Sv.total (s : Sv) : Int := s.rv + s.av + s.kv + s.pv

/-- `bp` basis points of `baseC` cents, rounded half up to the cent. -/
def bpOf (bp baseC : Int) : Int := rndHalf (bp * baseC) 10000

/-- The employee's PV rate in basis points (SGB XI § 55 (3), § 58 (1)): `childless` (and aged 23 or more, born
1940 or later) adds 0,6 points; a parent with `under25` children under 25 gets 0,25 points off for each child from
the second to the fifth. `full`: the whole 3,6 % (pensioners, self-employed) instead of the employee half. -/
def pvRateBp (full : Bool) (age : Int) (childless : Bool) (under25 : Int) (g : Bool := false) : Int :=
  let base := if full then P.pvBp else P.pvEmployeeBp
  if childless then (if age ≥ 23 ∧ (age < 86 ∨ g) then base + P.pvKinderlosBp else base)
  else base - P.pvAbschlagBp * (min (pos (under25 - 1)) 4)

/-- Contributions of one adult. `childless`: no child ever (we take: none in the household); `under25`: the
household's children under 25. Amounts in euros. -/
def svPerson (age wages selfEmp pension : Int) (childless : Bool) (under25 : Int) (g : Bool := false) : Sv :=
  let wC := ct wages
  -- Regelaltersgrenze (SGB VI § 235 (2)): 66 years for those born in 1958, 66 and 2 months for 1959. Aged 67 or
  -- more at the end of 2025 (born 1958 or earlier), a person was past it all year: no AV (SGB III § 28 (1) Nr. 1)
  -- and, drawing an old-age pension, no RV (SGB VI § 5 (4) Nr. 1); a 66-year-old is taken as insured all year.
  -- `g`: GETTSIM 1.3 readings, for the referee comparison only (no exemption after the Regelaltersgrenze, pension
  -- under its own KV ceiling, the childless surcharge also for those born before 1940)
  let avFree : Bool := age ≥ 67 ∧ !g
  let rvFree : Bool := age ≥ 67 ∧ pension > 0 ∧ !g
  let pvEmp := pvRateBp false age childless under25 g
  -- wages
  let (rv, av, kv, kvBasis, pv, rvEmp, kvBaseUsedC, kind) : Int × Int × Int × Int × Int × Int × Int × Nat :=
    if wages ≤ 12 * P.minijobMonat then (0, 0, 0, 0, 0, 0, 0, if wages > 0 then 1 else 5)
    else
      let regular := wages > 12 * P.uebergangOG
      -- employee's base: full wage, or the Übergangsbereich formula 2000/1444 × (AE − 556) per month
      let baseAN : Int := if regular then wC
        else rndHalf (P.uebergangOG * (wC - ct (12 * P.minijobMonat))) (P.uebergangOG - P.minijobMonat)
      let rvBase := min baseAN (ct P.bbgRV)
      let kvBase := min baseAN (ct P.bbgKV)
      let rv := if rvFree then 0 else bpOf P.rvEmployeeBp rvBase
      let av := if avFree then 0 else bpOf P.avEmployeeBp rvBase
      let kvRate := P.kvEmployeeBp + P.kvZusatzBp / 2
      let kv := bpOf kvRate kvBase
      -- § 10 (1) Nr. 3 a Satz 4: 4 % less when Krankengeld can be due (employees)
      let kvBasis := kv - bpOf P.kvKrankengeldCutBp kv
      -- the contribution base `BE` of SGB IV § 20 (2a) Satz 1 (in the Übergangsbereich
      -- BE = F × G + (OG/(OG−G) − G/(OG−G) × F) × (AE − G), F = 0,6683 for 2025: 28 % / 41,9 %)
      let beC : Int := if regular then min wC (ct P.bbgRV)
        else (P.faktorF * ct (12 * P.minijobMonat)) / 10000
          + ((P.uebergangOG * 10000 - P.minijobMonat * P.faktorF) * (wC - ct (12 * P.minijobMonat)))
            / ((P.uebergangOG - P.minijobMonat) * 10000)
      -- PV: in the Übergangsbereich the employee's half (and the child reductions) is computed on the reduced base
      -- (SGB XI § 58 (5) with SGB V § 249 (3)); the childless surcharge, a raise of the member's rate that "tragen
      -- die Beschäftigten" (SGB XI § 58 (1) Satz 3, § 55 (3)), on the contribution base BE itself
      let surcharge := childless ∧ age ≥ 23 ∧ (age < 86 ∨ g)
      let pv := if regular then bpOf pvEmp kvBase
        else bpOf (if childless then P.pvEmployeeBp else pvEmp) kvBase
          + (if surcharge then bpOf P.pvKinderlosBp (min beC (ct P.bbgKV)) else 0)
      -- the employer's RV share (tax-free, EStG § 3 Nr. 62): the total on BE less the employee's share; after the
      -- Regelaltersgrenze the employer still pays its half (SGB VI § 172 (1))
      let rvEmp := bpOf (2 * P.rvEmployeeBp) beC - rv
      (rv, av, kv, kvBasis, pv, rvEmp, kvBase, if regular then 0 else 2)
  -- statutory pension (KVdR): KV half rate + half Zusatz, full PV, under what is left of the KV ceiling
  let penBase := if g then min (ct pension) (ct P.bbgKV) else min (ct pension) (pos (ct P.bbgKV - kvBaseUsedC))
  let kvP := if pension > 0 then bpOf (P.kvEmployeeBp + P.kvZusatzBp / 2) penBase else 0
  let pvP := if pension > 0 then bpOf (pvRateBp true age childless under25 g) penBase else 0
  -- self-employed as main activity: voluntary GKV
  let selfMain := selfEmp > 12 * P.familienversicherungMonat ∧ wages ≤ 12 * P.minijobMonat ∧ pension ≤ 0
  let seBase := min (max (ct selfEmp) P.mindestBemessungJahrC) (ct P.bbgKV)
  let kvS := if selfMain then bpOf (P.kvErmaessigtBp + P.kvZusatzBp) seBase else 0
  let pvS := if selfMain then bpOf (pvRateBp true age childless under25 g) seBase else 0
  let kind' : Nat := if kind = 5 ∧ pension > 0 then 3 else if kind = 5 ∧ selfMain then 4 else kind
  { rv, av, kv := kv + kvP + kvS, pv := pv + pvP + pvS, rvEmployer := rvEmp,
    kvBasis := kvBasis + kvP + kvS,
    hb4 := if selfMain then P.hb10_4 else P.hb10_4Employee,
    onPension := kvP + pvP, onSelfEmployment := kvS + pvS,
    minijob := kind = 1, kind := kind' }

end DeTax
