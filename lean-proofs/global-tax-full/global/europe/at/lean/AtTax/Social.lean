import AtTax.Params

/-!
# Austria 2025: employee, pensioner and self-employed social contributions (cents)

Employees (ASVG, AMPFG, AKG, WBFG 2018): contributions are charged per month on the laufende Bezüge, capped at the
monthly Höchstbeitragsgrundlage, and separately on the Sonderzahlungen (13th/14th salary) with their own annual
ceiling and without AK-Umlage and Wohnbauförderungsbeitrag (both are levied on the "allgemeine Beitragsgrundlage",
AKG § 61 Abs. 2, WBFG 2018 § 2 Abs. 1, which excludes Sonderzahlungen, ASVG § 49 Abs. 2). Nothing is due on a
geringfügig employment (ASVG § 5 Abs. 2). The AV rate falls to 2 / 1 / 0 % on low monthly bases (AMPFG § 2a): that
rule is a **notch** (the rate applies to the whole base), proved in `Theorems.lean`.
-/

namespace AtTax
open TaxKernel

/-- Ticks (cents × bp) to cents, commercial rounding (amounts "auf Cent zu runden", ASVG § 108 Abs. 6). -/
def r2 (t : Int) : Int := divR .halfUp t BP

/-- AMPFG § 2a Abs. 1: the employee's AV rate (bp) for a monthly Beitragsgrundlage `m` (cents): "bis 1 648 € 0 vH,
über 1 648 bis 1 798 € 1 vH, über 1 798 bis 1 948 € 2 vH" (2025 amounts, `Params.avStep1`…), else half of 5,9 %. -/
def avRate (m : Int) (y : YP := yp2025) : Int :=
  if m ≤ y.avStep1 then 0 else if m ≤ y.avStep2 then 100 else if m ≤ y.avStep3 then 200 else y.avRateFull

/-- Employee contributions by branch (cents). -/
structure EmpSV where
  kv : Int := 0
  pv : Int := 0
  av : Int := 0
  ak : Int := 0
  wbf : Int := 0
  /-- the employee's contribution as withheld: the total rate on the base, rounded once (the branches above are
  rounded separately for information only; the BMF calculator rounds the total, `harness/bmf_grid.py`) -/
  tot : Int := 0
  deriving Repr, Inhabited

def EmpSV.total (s : EmpSV) : Int := s.tot
def EmpSV.scale (k : Int) (s : EmpSV) : EmpSV :=
  { kv := k * s.kv, pv := k * s.pv, av := k * s.av, ak := k * s.ak, wbf := k * s.wbf, tot := k * s.tot }
def EmpSV.add (s t : EmpSV) : EmpSV :=
  { kv := s.kv + t.kv, pv := s.pv + t.pv, av := s.av + t.av, ak := s.ak + t.ak, wbf := s.wbf + t.wbf, tot := s.tot + t.tot }

/-- One month of laufende Bezüge `m` (cents): ASVG § 51 Abs. 3, § 45 Abs. 1; AMPFG § 2, § 2a; AKG § 61;
WBFG 2018 § 2. -/
def svMonth (m : Int) (y : YP := yp2025) : EmpSV :=
  if m ≤ y.geringfuegig then {} else
  let b := min m y.hbglMonth
  { kv := r2 (kvRate * b), pv := r2 (pvRate * b), av := r2 (avRate b y * b), ak := r2 (akRate * b),
    wbf := r2 (wbfRate * b), tot := r2 ((kvRate + pvRate + avRate b y + akRate + wbfRate) * b) }

/-- The year's Sonderzahlungen: `k` instalments of `m` (each one monthly pay). ASVG § 54 Abs. 1 ("bis zum
60fachen Betrag der … Höchstbeitragsgrundlage"), AMPFG § 2 Abs. 2 (same ceiling for the AV). The AV rate of § 2a is
taken from the instalment itself (reading: § 2a speaks of "monatliche Beitragsgrundlage"; each Sonderzahlung is
assessed on its own). Geringfügig employment: none. -/
def szOne (m b : Int) (y : YP := yp2025) : EmpSV :=
  let r := avRate (min m y.hbglMonth) y
  { kv := r2 (kvRate * b), pv := r2 (pvRate * b), av := r2 (r * b), tot := r2 ((kvRate + pvRate + r) * b) }

/-- Instalments of `m` against the remaining annual ceiling `room`, each assessed (and rounded) on its own. -/
def szLoop (y : YP) (m : Int) : Nat → Int → EmpSV
  | 0, _ => {}
  | k + 1, room => let b := max 0 (min m room); (szOne m b y).add (szLoop y m k (room - b))

def svSonder (m : Int) (k : Int) (y : YP := yp2025) : EmpSV :=
  if m ≤ y.geringfuegig ∨ k ≤ 0 then {} else szLoop y m k.toNat y.szCeiling

/-- KV on a pension paid 14 times (`pm` = one instalment): ASVG § 73 Abs. 1 Z 1, 5,1 % to May and 6 % from June
2025 (§ 809 Abs. 1 Z 2); Sonderzahlungen in April (5,1 %) and October (6 %) (§ 105 Abs. 1). Contributions on the part of the year's
pensions above 35 times the daily Höchstbeitragsgrundlage for each month (90 300 €) are refunded (§ 70a Abs. 1;
netted here in proportion: the year's contributions times 90 300 € / pensions). Returns (laufend, SZ). -/
def kvPension (pm : Int) (aprilAt6 : Bool := false) (y : YP := yp2025) : Int × Int :=
  let cap := 12 * 35 * y.hbglDay
  let l := 5 * r2 (y.kvPenOld * pm) + 7 * r2 (y.kvPenNew * pm)
  let s := r2 ((if aprilAt6 then y.kvPenNew else y.kvPenOld) * pm) + r2 (y.kvPenNew * pm)
  if 14 * pm ≤ cap then (l, s) else (divR .halfUp (l * cap) (14 * pm), divR .halfUp (s * cap) (14 * pm))

/-- GSVG contributions of a self-employed person with annual Einkünfte `s` (cents, before these contributions):
§ 25 Abs. 1-2 (base = Einkünfte plus the contributions themselves, i.e. profit before them), Abs. 4 (minimum
551,10 € a month), § 48 (maximum 7 525 € a month), § 27 (6,8 % KV, 18,5 % PV), ASVG § 74 (UV 12,07 € a month).
Not insured at or below the yearly Versicherungsgrenze of 12 × 551,10 € (reading of GSVG § 4 Abs. 1 Z 5 for "neue
Selbständige"; Gewerbetreibende are insured from the first euro: not modelled). -/
def gsvg (s : Int) (y : YP := yp2025) : Int :=
  if s ≤ 12 * y.geringfuegig then 0 else
  let b := clamp (12 * y.geringfuegig) (12 * y.gsvgMaxMonth) s
  r2 (gsvgKv * b) + r2 (gsvgPv * b) + 12 * y.gsvgUvMonth

end AtTax
