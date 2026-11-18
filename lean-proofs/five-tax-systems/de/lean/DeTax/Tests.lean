import DeTax.Theorems

/-!
# Official values, checked

Every number below is printed by the BMF; the source and page are named at each block. No value is invented.

* **BMF, Datensammlung zur Steuerpolitik, Ausgabe 2026** (`refs/bmfde/datensammlung_2026.pdf`):
  - Tabelle 2.6, "Grenz- und Durchschnittssteuerbelastung bei der Einkommensteuer in Prozent", column T2025
    (44 values: marginal and average rates at 10 000 … 150 000 € of taxable income, single and splitting);
  - Tabelle 2.4.1, "Beginn der Steuerbelastung bei Einkünften aus nichtselbstständiger Arbeit", 2025: the first
    annual wage that bears Lohnsteuer in Steuerklasse I/0, II/0,5 and III/0 (average Zusatzbeitrag, no childless
    surcharge);
  - Tabelle 2.8.3, "Einkommensgrenzen, ab denen der Kinderfreibetrag dauerhaft günstiger ist als das Kindergeld",
    2025: Bruttolohn and taxable income (before the child allowances) for single parents and one-earner couples
    with one and two children (Berechnungen des Fraunhofer FIT).
* **BMF Tarifhistorie** (bmf-steuerrechner.de, 2025-10-14) and the Datensammlung, Tabelle 2.5.2: the 2025 formula
  (identical to the statute; `boundaries`).
* The BMF's external interface (PAP 2025) answers: `PapBmf.lean`, generated from `runs/bmf_pap/*.xml`.
-/

namespace DeTax.Tests
open DeTax DeTax.Th

/-- Average rate in tenths of a per cent, rounded half up. -/
def avg10 (tax x : Int) : Int := rndHalf (1000 * tax) x

/-- The marginal rate the formula gives at `x` ("der Steuersatz, mit dem die jeweils letzte Einheit des zu
versteuernden Einkommens besteuert wird", footnote 1 of Tabelle 2.6), in tenths of a per cent, rounded half up. -/
def marg10 (x : Int) : Int :=
  if x ≤ 12096 then 0
  else if x ≤ 17443 then rndHalf (2 * 93230 * (x - 12096) + 1400 * 1000000) 10000000
  else if x ≤ 68480 then rndHalf (2 * 17664 * (x - 17443) + 2397 * 1000000) 10000000
  else if x ≤ 277825 then 420 else 450

/-- Tabelle 2.6, T2025, Einzelveranlagung: (zvE, Grenzbelastung, Durchschnittsbelastung) in tenths of a per cent. -/
def tab26single : List (Int × Int × Int) :=
  [(10000, 0, 0), (20000, 249, 82), (30000, 284, 143), (40000, 319, 183), (50000, 355, 214), (60000, 390, 240),
   (70000, 420, 264), (80000, 420, 284), (90000, 420, 299), (100000, 420, 311), (150000, 420, 347)]

/-- Tabelle 2.6, T2025, Splittingverfahren. -/
def tab26split : List (Int × Int × Int) :=
  [(10000, 0, 0), (20000, 0, 0), (30000, 194, 32), (40000, 249, 82), (50000, 266, 117), (60000, 284, 143),
   (70000, 302, 165), (80000, 319, 183), (90000, 337, 199), (100000, 355, 214), (150000, 420, 275)]

-- 22 marginal and 22 average rates, all equal to the BMF's
#guard tab26single.all fun (x, g, d) => marg10 x == g && avg10 (t2025.est x) x == d
#guard tab26split.all fun (x, g, d) => marg10 (x / 2) == g && avg10 (t2025.estSplit x) x == d

/-- Tabelle 2.4.1, 2025: the first annual gross wage that bears Lohnsteuer: 16 836 € (Steuerklasse I, no child),
21 860 € (II, 0,5 Kinderfreibetrag), 31 586 € (III, no child) — the Lean PAP gives exactly these. -/
def lst (stkl : Nat) (zkf10 w : Int) : Int := (Pap.run { RE4 := 100 * w, STKL := stkl, ZKF10 := zkf10 }).LSTJAHR
#guard lst 1 0 16835 == 0 && lst 1 0 16836 > 0
#guard lst 2 5 21859 == 0 && lst 2 5 21860 > 0
#guard lst 3 0 31585 == 0 && lst 3 0 31586 > 0

/-- Tabelle 2.8.3, 2025: at the printed Bruttolohn the model's Einkommen (taxable income before the child
allowances) is the printed amount, and the Freibeträge win for every child; one euro of wages less, for the
one-child couple, the Kindergeld still wins. -/
def household (wage : Int) (married : Bool) (kids : Nat) : Household :=
  { adults := if married then [{ age := 40, wages := wage }, { age := 38 }] else [{ age := 40, wages := wage }],
    married, children := (List.range kids).map (fun _ => (5 : Int)) }

def einkommenAndFB (h : Household) : List (Int × Int) :=
  (assess {} h).units.map fun (_, r) => (euroDown r.einkommen, r.kidsFB)

#guard einkommenAndFB (household 101455 true 1) == [(84548, 1)]
#guard einkommenAndFB (household 101454 true 1) == [(84547, 0)]
#guard einkommenAndFB (household 110889 true 2) == [(94148, 2)]
#guard einkommenAndFB (household 62175 false 1) == [(44644, 1)]
#guard einkommenAndFB (household 73280 false 2) == [(54244, 2)]

/-- `burdenSingle` (used by `marginal_peak`) is the model's burden for a childless single employee aged 40, for every
wage from 24 001 € to 140 000 € in steps of 7 €. -/
def modelBurden (w : Int) : Int :=
  let r := assess {} { adults := [{ age := 40, wages := w }] }
  r.incomeTax + r.soli + r.employeeSocial

#guard (List.range 16572).all fun (i : Nat) => let w : Int := 24001 + 7 * (i : Int); burdenSingle w == modelBurden w

end DeTax.Tests

namespace DeTax.Tests
open DeTax

/-! ## OECD, Taxing Wages 2026 (year 2025), Germany

The OECD's member-country table (SDMX dataflow `OECD.CTP.TPS,DSD_TAX_WAGES_COU@DF_TW_COU,2.1`, fetched 2026-11-18,
`refs/oecd/tw_cou_2025.csv`): average wage (AW) 66 700,04 €; for each household the employees' compulsory social
security contributions (EECSSC), the central-government income tax liability before tax credits (CGITLETC, which for
Germany includes the Soli) and the Kindergeld, which the OECD books as a tax credit (TC). Wages here are the OECD's
rounded to the euro; children aged 6 and 11. -/

def oecdHousehold (ws : List Int) (married : Bool) (kids : List Int) : Household :=
  { adults := ws.map fun w => { age := 40, wages := w }, married, children := kids }

/-- (household, OECD EECSSC in cents, OECD CGITLETC in cents, OECD TC in cents). -/
def oecd2025 : List (Household × Int × Int × Int) :=
  [ (oecdHousehold [44689] false [], 963049, 562500, 0),               -- single, 67 % AW
    (oecdHousehold [66700] false [], 1431363, 1148400, 0),             -- single, 100 % AW
    (oecdHousehold [111389] false [], 1748303, 2965061, 0),            -- single, 167 % AW
    (oecdHousehold [44689] false [6, 11], 925063, 441900, 612000),     -- single parent, 67 % AW, 2 children
    (oecdHousehold [66700, 0] true [6, 11], 1375135, 659000, 612000),  -- couple, 100 % + 0, 2 children
    (oecdHousehold [66700, 66700] true [6, 11], 2750271, 1670400, 0),  -- couple, 100 % + 100 %, 2 children
    (oecdHousehold [66700, 44689] true [], 2394412, 1683400, 0) ]      -- couple, 100 % + 67 %, no children

-- contributions within one cent; income tax with Soli and the Kindergeld to the cent
#guard oecd2025.all fun (h, ssc, tax, tc) =>
  let r := assess {} h
  (r.employeeSocial - ssc).natAbs ≤ 1 && r.incomeTax + r.soli == tax && r.kindergeldKept == tc

/-- The eighth OECD household, a couple with 100 % + 67 % AW and two children: the OECD keeps the Kindergeld for both
children (tax 17 146 €, credit 6 120 €), which is what comparing all the children's Freibeträge with all the
Kindergeld at once gives; the child-by-child comparison (FINDINGS G7, O1) deducts the first child's Freibeträge
(Einkommen 87 682 € is above the 84 548 € threshold, below 94 148 €): tax 14 032 €, Kindergeld kept 3 060 €, 54 € less
in all. -/
def oecdCouple2 : Household := oecdHousehold [66700, 44689] true [6, 11]
#guard let r := assess { perChild := false } oecdCouple2
  (r.employeeSocial - 2300198).natAbs ≤ 1 && r.incomeTax + r.soli == 1714600 && r.kindergeldKept == 612000
#guard let r := assess {} oecdCouple2
  r.incomeTax + r.soli == 1403200 && r.kindergeldKept == 306000

end DeTax.Tests

namespace DeTax.Tests
open DeTax

/-! ## The 2026 tariff (for the record): Tabelle 2.6, column T2026 -/

/-- The marginal rate of any year's formula, in tenths of a per cent, rounded half up. -/
def margT10 (t : Tarif) (x : Int) : Int :=
  if x ≤ t.gfb then 0
  else if x ≤ t.e2 then rndHalf (2 * t.a2 * (x - t.gfb) + t.b2 * 1000000) 10000000
  else if x ≤ t.e3 then rndHalf (2 * t.a3 * (x - t.e2) + t.b3 * 1000000) 10000000
  else if x ≤ t.e4 then 10 * t.r4 else 10 * t.r5

def tab26single2026 : List (Int × Int × Int) :=
  [(10000, 0, 0), (20000, 247, 79), (30000, 282, 141), (40000, 317, 180), (50000, 351, 211), (60000, 386, 237),
   (70000, 420, 261), (80000, 420, 281), (90000, 420, 296), (100000, 420, 309), (150000, 420, 346)]
def tab26split2026 : List (Int × Int × Int) :=
  [(10000, 0, 0), (20000, 0, 0), (30000, 189, 29), (40000, 247, 79), (50000, 265, 114), (60000, 282, 141),
   (70000, 299, 162), (80000, 317, 180), (90000, 334, 196), (100000, 351, 211), (150000, 420, 272)]

#guard tab26single2026.all fun (x, g, d) => margT10 t2026 x == g && avg10 (t2026.est x) x == d
#guard tab26split2026.all fun (x, g, d) => margT10 t2026 (x / 2) == g && avg10 (t2026.estSplit x) x == d
-- and the generic marginal rate agrees with the 2025 one
#guard tab26single.all fun (x, g, _) => margT10 t2025 x == g

end DeTax.Tests
