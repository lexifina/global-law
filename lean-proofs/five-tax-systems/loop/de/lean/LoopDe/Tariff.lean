import LoopDe.Basic

/-!
# The income tax tariff: EStG § 32a

Text for VZ 2025 (EStG § 32a as amended by the Steuerfortentwicklungsgesetz, BGBl. 2024 I Nr. 449, in force
2025-01-01; `law/2025/estg_32a.md`):

> (1) ¹Die tarifliche Einkommensteuer bemisst sich nach dem auf volle Euro abgerundeten zu versteuernden Einkommen.
> ²Sie beträgt ab dem Veranlagungszeitraum 2025 ... jeweils in Euro für zu versteuernde Einkommen
> 1. bis 12 096 Euro (Grundfreibetrag): 0;
> 2. von 12 097 Euro bis 17 443 Euro: (932,30 • y + 1 400) • y;
> 3. von 17 444 Euro bis 68 480 Euro: (176,64 • z + 2 397) • z + 1 015,13;
> 4. von 68 481 Euro bis 277 825 Euro: 0,42 • x – 10 911,92;
> 5. von 277 826 Euro an: 0,45 • x – 19 246,67.
> ³Die Größe „y“ ist ein Zehntausendstel des den Grundfreibetrag übersteigenden Teils des auf einen vollen
> Euro-Betrag abgerundeten zu versteuernden Einkommens. ⁴Die Größe „z“ ist ein Zehntausendstel des 17 443 Euro
> übersteigenden Teils ... ⁵Die Größe „x“ ist das auf einen vollen Euro-Betrag abgerundete zu versteuernde
> Einkommen. ⁶Der sich ergebende Steuerbetrag ist auf den nächsten vollen Euro-Betrag abzurunden.

The statute writes the tariff as a formula with coefficients, not as brackets. `y` and `z` are exact (an integer
number of euros divided by 10 000), so the formula has no intermediate rounding: there is exactly one rounding,
of the result, down to the euro. We compute it exactly in units of 10⁻¹⁰ euro (`num`), then round once (`est`).

* zone 2: `(932,30·y + 1 400)·y = (93 230·d + 1 400·10⁶)·d / 10¹⁰`, `d = x − 12 096`;
* zone 3: `(176,64·z + 2 397)·z + 1 015,13 = ((17 664·e + 2 397·10⁶)·e + 101 513·10⁸) / 10¹⁰`, `e = x − 17 443`;
* zones 4, 5: `(42·x − 1 091 192)·10⁸ / 10¹⁰`, `(45·x − 1 924 667)·10⁸ / 10¹⁰`.
-/

namespace LoopDe

/-- The coefficients of § 32a (1) for one Veranlagungszeitraum. Amounts with cents are stored in cents. -/
structure Tarif where
  vz : Nat
  /-- Nr. 1: "bis ... Euro (Grundfreibetrag): 0". -/
  gfb : Int
  /-- Nr. 2 ends ("bis 17 443 Euro"); also the subtrahend of `z` (Satz 4). -/
  e2 : Int
  /-- Nr. 3 ends ("bis 68 480 Euro"). -/
  e3 : Int
  /-- Nr. 4 ends ("bis 277 825 Euro"). -/
  e4 : Int
  /-- Nr. 2: `(a2/100 • y + b2) • y`. -/
  a2 : Int
  b2 : Int
  /-- Nr. 3: `(a3/100 • z + b3) • z + c3/100`. -/
  a3 : Int
  b3 : Int
  c3 : Int
  /-- Nr. 4: `r4/100 • x – c4/100`. -/
  r4 : Int
  c4 : Int
  /-- Nr. 5: `r5/100 • x – c5/100`. -/
  r5 : Int
  c5 : Int
  deriving Repr

/-- VZ 2025: EStG § 32a (1) as amended by Art. 1 Steuerfortentwicklungsgesetz (BGBl. 2024 I Nr. 449). -/
def t2025 : Tarif where
  vz := 2025
  gfb := 12096
  e2 := 17443
  e3 := 68480
  e4 := 277825
  a2 := 93230
  b2 := 1400
  a3 := 17664
  b3 := 2397
  c3 := 101513
  r4 := 42
  c4 := 1091192
  r5 := 45
  c5 := 1924667

/-- VZ 2026 (for comparison only): EStG § 32a (1) as in force from 2026-01-01 (gesetze-im-internet.de, 2026-11-18):
"bis 12 348 Euro (Grundfreibetrag): 0; ... bis 17 799 Euro: (914,51 • y + 1 400) • y; ... bis 69 878 Euro:
(173,10 • z + 2 397) • z + 1 034,87; ... bis 277 825 Euro: 0,42 • x – 11 135,63; ... 0,45 • x – 19 470,38". -/
def t2026 : Tarif where
  vz := 2026
  gfb := 12348
  e2 := 17799
  e3 := 69878
  e4 := 277825
  a2 := 91451
  b2 := 1400
  a3 := 17310
  b3 := 2397
  c3 := 103487
  r4 := 42
  c4 := 1113563
  r5 := 45
  c5 := 1947038

/-- The zone (1–5) of § 32a (1) Satz 2 that applies to `x` whole euros. -/
def Tarif.zone (t : Tarif) (x : Int) : Nat :=
  if x ≤ t.gfb then 1 else if x ≤ t.e2 then 2 else if x ≤ t.e3 then 3 else if x ≤ t.e4 then 4 else 5

/-- The statute's formula before its single rounding, in units of 10⁻¹⁰ euro, for `x` whole euros. -/
def Tarif.num (t : Tarif) (x : Int) : Int :=
  if x ≤ t.gfb then 0
  else if x ≤ t.e2 then (t.a2 * (x - t.gfb) + t.b2 * 1000000) * (x - t.gfb)
  else if x ≤ t.e3 then (t.a3 * (x - t.e2) + t.b3 * 1000000) * (x - t.e2) + t.c3 * 100000000
  else if x ≤ t.e4 then (t.r4 * x - t.c4) * 100000000
  else (t.r5 * x - t.c5) * 100000000

/-- **§ 32a (1).** The tariff income tax, in whole euros, on `x` whole euros of zu versteuerndes Einkommen
(already "auf volle Euro abgerundet", Satz 1); the result "auf den nächsten vollen Euro-Betrag abzurunden"
(Satz 6). -/
def Tarif.est (t : Tarif) (x : Int) : Int := t.num x / 10000000000

/-- **§ 32a (1) Satz 1** for an amount in cents: round the zvE down to whole euros first. -/
def Tarif.estCents (t : Tarif) (zveCents : Int) : Int := t.est (euroDown zveCents)

/-- **§ 32a (5), Splitting-Verfahren.** "das Zweifache des Steuerbetrags, der sich für die Hälfte ihres gemeinsam
zu versteuernden Einkommens nach Absatz 1 ergibt": the half is taken of the joint zvE and then, by Absatz 1 Satz 1,
rounded down to whole euros. `x` is the joint zvE in whole euros (⌊⌊X⌋/2⌋ = ⌊X/2⌋, so it does not matter whether
the joint amount was rounded first). -/
def Tarif.estSplit (t : Tarif) (x : Int) : Int := 2 * t.est (x / 2)

/-- Tariff tax for a single (`joint = false`) or a jointly assessed couple (`joint = true`). -/
def Tarif.tax (t : Tarif) (joint : Bool) (x : Int) : Int := if joint then t.estSplit x else t.est x

end LoopDe
