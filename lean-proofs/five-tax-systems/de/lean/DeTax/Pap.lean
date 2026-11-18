import DeTax.Tariff

/-!
# The BMF's Programmablaufplan (PAP) for the Lohnsteuer 2025, as executable Lean

Source: the BMF's XML pseudo-code `Lohnsteuer2025.xml` (bmf-steuerrechner.de, "XML-Pseudocodes", file header
"Stand: 2025-09-17", ITZBund Berlin; local copy `refs/bmf/Lohnsteuer2025.xml`), which the BMF publishes so that
programs reproduce its calculator exactly: "Um Rundungsfehlern beim Einsatz von Gleitkommazahlen ... zu vermeiden, wird
der Einsatz einer Klasse für numerisches Rechnen empfohlen (BigDecimal)".

Translated method by method for the *laufender Arbeitslohn* (no sonstige Bezüge: `SONSTB = MBV = 0`, so `MSONST`
only zeroes its outputs) and **without Versorgungsbezüge** (`VBEZ = 0`): `MPARA`, `MRE4JL`, `MRE4` (with
`ZVBEZJ = 0`), `MRE4ALTE`, `MRE4ABZ`, `MBERECH`, `MZTABFB`, `MLSTJAHR`, `UPEVP`, `MVSP`, `UPMLST`, `UPTAB25`, `MST5_6`,
`UP5_6`, `MSOLZ`, `UPANTEIL`, `UPLSTLZZ`, `UPVKV(LZZ)`.

BigDecimal is modelled with integers at the scale the pseudo-code fixes at each step:
* amounts in euros "mit 2 Dezimalstellen" are held in cents;
* `setScale(n, ROUND_DOWN)` truncates towards zero (`Int.tdiv`), `ROUND_UP` rounds away from zero;
* rates are held in millionths (`KVSATZAN` = 0.0825 ↦ 82 500).
-/

namespace DeTax.Pap

/-- `a / d` truncated towards zero (BigDecimal `ROUND_DOWN`), `d > 0`. -/
def down (a d : Int) : Int := Int.tdiv a d

/-- `a / d` rounded away from zero (BigDecimal `ROUND_UP`), `d > 0`. -/
def up (a d : Int) : Int := if 0 ≤ a then (a + d - 1) / d else -((-a + d - 1) / d)

/-- The inputs of the PAP used here (names as in the XML). Amounts in cents. -/
structure In where
  /-- Lohnzahlungszeitraum: 1 Jahr, 2 Monat, 3 Woche, 4 Tag. -/
  LZZ : Nat := 1
  /-- Steuerpflichtiger Arbeitslohn für den Lohnzahlungszeitraum, in Cent. -/
  RE4 : Int
  STKL : Nat := 1
  /-- Zahl der Freibeträge für Kinder, in Zehnteln (0,5 ↦ 5). -/
  ZKF10 : Int := 0
  /-- 0: pflichtversichert in der gesetzlichen Rentenversicherung; 1: nicht. -/
  KRV : Nat := 0
  /-- Kassenindividueller Zusatzbeitragssatz in hundredths of a per cent (2,50 % ↦ 250). -/
  KVZbp : Int := 250
  /-- 0 gesetzlich, 1 privat ohne, 2 privat mit Arbeitgeberzuschuss. -/
  PKV : Nat := 0
  /-- Monthly private KV/PV premium, in cents. -/
  PKPV : Int := 0
  PVS : Nat := 0
  PVZ : Nat := 0
  /-- Number of PV reductions for the 2nd to 5th child (0–4). -/
  PVA : Int := 0
  /-- Religionsgemeinschaft (0: none). -/
  R : Nat := 0
  ALTER1 : Nat := 0
  AJAHR : Int := 0
  LZZFREIB : Int := 0
  LZZHINZU : Int := 0
  /-- Faktor in thousandths (1,000 ↦ 1000). -/
  f1000 : Int := 1000
  deriving Repr

structure Out where
  LSTLZZ : Int
  SOLZLZZ : Int
  BK : Int
  VKVLZZ : Int
  VFRB : Int
  WVFRB : Int
  /-- Internal values kept for tests: the zu versteuernder Jahresbetrag in cents and the annual tax. -/
  ZVEc : Int
  LSTJAHR : Int
  JBMG : Int
  VSP : Int
  deriving Repr

/-- `TAB4` (Altersentlastungsbetrag, Prozentsatz) in thousandths, index `K` = 1 … 54 (`AJAHR − 2004`). -/
def tab4 (k : Int) : Int :=
  if k ≤ 1 then 400 else if k ≤ 16 then 400 - 16 * (k - 1) else if k ≤ 18 then 160 - 8 * (k - 16)
  else if k ≤ 54 then 144 - 4 * (k - 18) else 0

/-- `TAB5` (Altersentlastungsbetrag, Höchstbetrag in euros). -/
def tab5 (k : Int) : Int :=
  if k ≤ 1 then 1900 else if k ≤ 16 then 1900 - 76 * (k - 1) else if k ≤ 18 then 760 - 38 * (k - 16)
  else if k ≤ 54 then 684 - 19 * (k - 18) else 0

/-- **UPTAB25** for an amount `X` in cents (the PAP calls it with whole euros from `UPMLST`, and with
`ZX × 1,25` and `ZX × 0,75` "mit 2 Dezimalstellen" from `UP5_6`). Returns `ST` before the factor `KZTAB`. -/
def uptab25 (X2 : Int) : Int :=
  if X2 < (12096 + 1) * 100 then 0
  else if X2 < 1744400 then
    -- Y = (X − GFB) / 10000, 6 Dezimalstellen, ROUND_DOWN: exact, Y·10⁶ = X2 − 1 209 600
    let Y6 := X2 - 1209600
    let RW8 := Y6 * 93230 + 1400 * 100000000          -- RW = Y × 932,30 + 1 400 (scale 8)
    down (RW8 * Y6) 100000000000000                  -- ST = (RW × Y).setScale(0, ROUND_DOWN)
  else if X2 < 6848100 then
    let Y6 := X2 - 1744300
    let RW8 := Y6 * 17664 + 2397 * 100000000          -- RW = Y × 176,64 + 2 397
    down (RW8 * Y6 + 101513 * 1000000000000) 100000000000000   -- (RW × Y + 1 015,13).setScale(0, DOWN)
  else if X2 < 27782600 then down (X2 * 42 - 109119200) 10000   -- (X × 0,42 − 10 911,92)
  else down (X2 * 45 - 192466700) 10000                          -- (X × 0,45 − 19 246,67)

/-- `UP5_6` (Steuerklassen V, VI): twice the difference between the tax on 1,25 × ZX and 0,75 × ZX, at least
14 % of ZX. `ZX` in whole euros. -/
def up56 (ZX : Int) : Int :=
  let ST1 := uptab25 (ZX * 125)          -- X = (ZX × 1,25).setScale(2, DOWN): exact in cents
  let ST2 := uptab25 (ZX * 75)
  let DIFF := (ST1 - ST2) * 2
  let MIST := down (ZX * 14) 100
  if MIST > DIFF then MIST else DIFF

/-- `MST5_6`. `ZZX` = X in whole euros. -/
def mst56 (ZZX : Int) : Int :=
  let W1 : Int := 13785
  let W2 : Int := 34240
  let W3 : Int := 222260
  if ZZX > W2 then
    let ST := up56 W2
    if ZZX > W3 then
      let ST := down (ST * 100 + (W3 - W2) * 42) 100
      down (ST * 100 + (ZZX - W3) * 45) 100
    else down (ST * 100 + (ZZX - W2) * 42) 100
  else
    let ST := up56 ZZX
    if ZZX > W1 then
      let VERGL := ST
      let ST' := up56 W1
      let HOCH := down (ST' * 100 + (ZZX - W1) * 42) 100
      if HOCH < VERGL then HOCH else VERGL
    else ST

/-- `UPANTEIL`: the share of an annual amount `JW` (cents) for the pay period. -/
def anteil (LZZ : Nat) (JW : Int) : Int :=
  match LZZ with
  | 1 => JW
  | 2 => down JW 12
  | 3 => down (JW * 7) 360
  | _ => down JW 360

/-- `UPEVP` + `MVSP`: the Vorsorgepauschale in whole euros, from `ZRE4VP` (cents). Also returns `VSP2`, `VSP3`
(cents) for `UPVKV`. -/
def vorsorge (i : In) (ZRE4VPc : Int) : Int × Int × Int :=
  let BBGRV : Int := if i.KRV < 1 then 96600 else 0
  let RVSATZAN : Int := if i.KRV < 1 then 93000 else 0          -- 0,093 in millionths
  let KVSATZAN : Int := i.KVZbp * 50 + 70000                     -- KVZ / 2 / 100 + 0,07
  let KVSATZAG : Int := 12500 + 70000
  let (pvan, PVSATZAG) : Int × Int := if i.PVS = 1 then (23000, 13000) else (18000, 18000)
  let PVSATZAN : Int := if i.PVZ = 1 then pvan + 6000 else pvan - i.PVA * 2500
  -- UPEVP
  let (zvp, VSP1) : Int × Int :=
    if i.KRV = 1 then (ZRE4VPc, 0)
    else
      let z := if ZRE4VPc > BBGRV * 100 then BBGRV * 100 else ZRE4VPc
      (z, down (z * RVSATZAN) 1000000)
  let VSP2a := down (zvp * 12) 100
  let VHB : Int := if i.STKL = 3 then 3000 else 1900
  let VSP2 := if VSP2a > VHB * 100 then VHB * 100 else VSP2a
  let VSPN := up (VSP1 + VSP2) 100
  -- MVSP
  let zkv := if zvp > 66150 * 100 then 66150 * 100 else zvp
  let VSP3 : Int :=
    if i.PKV > 0 then
      if i.STKL = 6 then 0
      else
        let v := i.PKPV * 12                                        -- PKPV × 12 / 100 euros = cents × 12
        if i.PKV = 2 then down (v * 1000000 - zkv * (KVSATZAG + PVSATZAG)) 1000000 else v
    else down (zkv * (KVSATZAN + PVSATZAN)) 1000000
  let VSP := up (VSP3 + VSP1) 100
  ((if VSPN > VSP then VSPN else VSP), VSP2, VSP3)

/-- `MZTABFB` (without Versorgungsbezüge): `(ANP, ZTABFB in cents, KZTAB, KFB in euros)`. -/
def ztabfb (i : In) (ZRE4c : Int) : Int × Int × Int × Int :=
  let ANP : Int :=
    if i.STKL < 6 ∧ ZRE4c > 0 then (if ZRE4c < 123000 then up ZRE4c 100 else 1230) else 0
  let (EFA, SAP, KZTAB, KFB) : Int × Int × Int × Int :=
    match i.STKL with
    | 1 => (0, 36, 1, down (i.ZKF10 * 9600) 10)
    | 2 => (4260, 36, 1, down (i.ZKF10 * 9600) 10)
    | 3 => (0, 36, 2, down (i.ZKF10 * 9600) 10)
    | 4 => (0, 36, 1, down (i.ZKF10 * 4800) 10)
    | 5 => (0, 36, 1, 0)
    | _ => (0, 0, 1, 0)
  (ANP, (EFA + ANP + SAP) * 100, KZTAB, KFB)

/-- `UPMLST`: from `ZVE` (cents) to the annual tax `ST` (euros). -/
def mlst (i : In) (ZVEc KZTAB : Int) : Int :=
  let X : Int := if ZVEc < 100 then 0 else down ZVEc (100 * KZTAB)
  if i.STKL < 5 then uptab25 (X * 100) * KZTAB else mst56 X

/-- The whole PAP for a current wage. -/
def run (i : In) : Out :=
  -- MRE4JL
  let ZRE4Jc : Int := match i.LZZ with
    | 1 => i.RE4 | 2 => i.RE4 * 12 | 3 => down (i.RE4 * 360) 7 | _ => i.RE4 * 360
  let conv (a : Int) : Int := match i.LZZ with
    | 1 => a | 2 => a * 12 | 3 => down (a * 360) 7 | _ => a * 360
  let JLFREIBc := conv i.LZZFREIB
  let JLHINZUc := conv i.LZZHINZU
  let f := if i.f1000 ≤ 0 then 1000 else i.f1000
  -- MRE4ALTE (ZVBEZJ = 0)
  let ALTE : Int :=
    if i.ALTER1 = 0 then 0
    else
      let K : Int := if i.AJAHR < 2006 then 1 else if i.AJAHR < 2058 then i.AJAHR - 2004 else 54
      let a := up (ZRE4Jc * tab4 K) 100000
      if a > tab5 K then tab5 K else a
  -- MRE4ABZ
  let ZRE4c := let z := ZRE4Jc - ALTE * 100 - JLFREIBc + JLHINZUc; if z < 0 then 0 else z
  -- MBERECH
  let (ANP, ZTABFBc, KZTAB, KFB) := ztabfb i ZRE4c
  let VFRB := ANP * 100
  let (VSP, VSP2, VSP3) := vorsorge i ZRE4Jc
  let ZVEc := ZRE4c - ZTABFBc - VSP * 100
  let ST := mlst i ZVEc KZTAB
  let WVFRB := let w := ZVEc - 12096 * 100; if w < 0 then 0 else w
  let LSTJAHR := down (ST * f) 1000
  let LSTLZZ := anteil i.LZZ (LSTJAHR * 100)
  let VKV : Int := if i.PKV > 0 then (if VSP2 > VSP3 then VSP2 else VSP3) else 0
  let VKVLZZ := anteil i.LZZ VKV
  let JBMG : Int :=
    if i.ZKF10 > 0 then
      let ZVE2 := ZRE4c - (ZTABFBc + KFB * 100) - VSP * 100
      down (mlst i ZVE2 KZTAB * f) 1000
    else LSTJAHR
  -- MSOLZ
  let SOLZFREI := 19950 * KZTAB
  let SOLZLZZ :=
    if JBMG > SOLZFREI then
      let SOLZJ := down (JBMG * 55) 10
      let SOLZMIN := down ((JBMG - SOLZFREI) * 119) 10
      anteil i.LZZ (if SOLZMIN < SOLZJ then SOLZMIN else SOLZJ)
    else 0
  let BK := if i.R > 0 then anteil i.LZZ (JBMG * 100) else 0
  { LSTLZZ, SOLZLZZ, BK, VKVLZZ, VFRB, WVFRB, ZVEc, LSTJAHR, JBMG, VSP }

end DeTax.Pap
