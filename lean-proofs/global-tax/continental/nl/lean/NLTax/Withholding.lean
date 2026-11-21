import NLTax.Tax

/-!
# NLTax.Withholding: the loonbelastingtabellen 2025 as the Belastingdienst computes them

Source: Belastingdienst, "Rekenvoorschriften voor de geautomatiseerde loonadministratie 2025, Uitgave januari 2025"
(LH 099 - 1Z52FD, `../refs/rekenvoorschriften_2025.txt`, https://download.belastingdienst.nl/belastingdienst/docs/rekenvoorschriften_voor_geautomatiseerde_loonadministratie_lh991z52fd.pdf)
and its "Bijlage parameterwaarden" (LH 991 B51FD). "De bedragen in de tabellen zijn bindend. Als u de
rekenvoorschriften toepast, moet de uitkomst dus hetzelfde zijn als wanneer u de tabellen raadpleegt" (§1), so this is
the witte tabel with loonheffingskorting, standard situation, resident, below the AOW age, at the annual level
(§2.2: x = X/F; the tables are generated from the annual "brontabel").

The withholding is an advance on the Wet IB 2001 + Wfsv assessment (art. 9.2 Wet IB). `Theorems.lean` bounds the
difference between the two for an employee with only this wage.
-/

namespace NLTax

/-- Tabel 1a: "Lv ... stapgrootte van het loon in de brontabel ... € 54"; "Lmax ... € 129.330". -/
def lbLv : Int := 54
def lbLmax : Int := 129330

/-- §2.2.1: "Rond het resultaat ... naar beneden af op veelvouden van Lv" (euros). -/
def lbTabelloon (L : Int) : Int := if L ≤ 0 then 0 else if L ≤ lbLmax then (L / lbLv) * lbLv else L

/-- §2.2.2, tabel 2 (below AOW age): a, b, c = 0 | 35,82 | 0; 38.441 | 37,48 | 13.769; 76.817 | 49,50 | 28.152.
§2.2.4: "X1 = (L - a) * b / 100 + c ... naar beneden afrondt op hele euro's ... minimale waarde ... € 0". Euros. -/
def lbX1 (L : Int) : Int :=
  if L ≤ 0 then 0
  else if L ≤ 38441 then 3582 * L / 10000
  else if L ≤ 76817 then 3748 * (L - 38441) / 10000 + 13769
  else 4950 * (L - 76817) / 10000 + 28152

/-- §2.2.3.1, tabel 3: AHK = 3.068 up to 28.406, then "ahkm1 - (L - ahkg1) * ahka1 ... naar boven afrondt op hele
euro's", ahka1 = 0,06337, and 0 above ahkg2 = a3 = 76.817. Euros. -/
def lbAHK (L : Int) : Int :=
  if L ≤ 28406 then 3068
  else if L ≤ 76817 then max 0 (-((-(3068 * 100000 - 6337 * (L - 28406))) / 100000))
  else 0

/-- §2.2.3.4, tabel 6: ARK as art. 8.11 (arko1 0,08053, arkm1 980, arko2 0,30030 from 12.169, arkm2 5.220,
arko3 0,02258 from 26.288, arkm3 5.599, arka1 0,06510 from 43.071), "naar boven afrondt op hele euro's", 0 above
arkg4 = 129.078. Euros. -/
def lbARK (L : Int) : Int :=
  if L ≤ 129078 then -((-akNum (100 * L)) / 10000000) else 0

/-- §2.2.4: "X = X1 - (AHK + OUK + ARK + AOK)", 0 if the kortingen exceed X1. Euros (annual). -/
def lbX (L : Int) : Int := max 0 (lbX1 L - (lbAHK L + lbARK L))

/-- The annual withholding for an annual wage `w` (euros) paid in equal months (table wage rounded to Lv; x = X/12
rounded to cents, twelve times). Cents. Only for `w ≤ Lmax`; above, `none`. -/
def lbAnnualMonthly (w : Int) : Option Int :=
  let L := lbTabelloon w
  if L > lbLmax then none
  else
    let x := (2 * (100 * lbX L) + 12) / 24   -- X/F with F = 12, rekenkundig op 2 decimalen (cents)
    some (12 * x)

end NLTax
