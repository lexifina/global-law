import AtTax.Social

/-!
# Austria 2025: one taxpayer's income tax (cents)

Austria taxes individuals (no joint return); the household enters only through the Absetzbeträge (AVAB, erhöhter
PAB, Familienbonus Plus allocation, Kindermehrbetrag) chosen in `Household.lean`.

Order of the computation (EStG 1988):
1. Einkünfte aus nichtselbständiger Arbeit: laufende Bezüge minus SV (§ 16 Abs. 1 Z 3 lit. a, Z 4, Z 5) minus the
   Werbungskostenpauschale (§ 16 Abs. 3, not for pensions, never into a loss); pensions minus their KV.
   Sonstige Bezüge within the Jahressechstel are "außer Ansatz" (§ 41 Abs. 4, § 67 Abs. 9) and taxed apart.
2. Self-employment: profit minus GSVG contributions (§ 4 Abs. 4 Z 1) minus the Grundfreibetrag (§ 10).
3. Veranlagungsfreibetrag (§ 39 Abs. 5) on the other (not lohnsteuerpflichtige) income of a wage earner.
4. Spenden (§ 18 Abs. 1 Z 7, at most 10 %). Einkommen (§ 2 Abs. 2). Tariff (§ 33 Abs. 1).
5. Familienbonus Plus, at most the tariff tax (§ 33 Abs. 2 Z 1); then the Absetzbeträge of Abs. 4-6 (§ 33 Abs. 2
   Z 2); a negative result is refunded only up to AVAB/AEAB + SV-Rückerstattung (§ 33 Abs. 8).
6. Kindermehrbetrag (§ 33 Abs. 7); tax on the sonstige Bezüge (§ 67 Abs. 1, § 41 Abs. 4); special-rate capital
   income (§ 27a), with the Regelbesteuerungsoption (§ 27a Abs. 5) when it is cheaper.
-/

namespace AtTax
open TaxKernel

/-- One taxpayer's income (cents). Wages are paid in `payments` equal instalments of `wagePay` (12 laufende + the
rest as sonstige Bezüge); a pension in 14 instalments of `pensionPay`. -/
structure PersonIn where
  wagePay : Int := 0
  payments : Int := 14
  pensionPay : Int := 0
  self : Int := 0
  rental : Int := 0
  interest : Int := 0
  other27 : Int := 0
  charitable : Int := 0
  /-- reproduce the BMF calculator's 6 % on the April pension Sonderzahlung (FINDINGS) -/
  aprilAt6 : Bool := false
  /-- switches for the loophole catalogue (what a relief is worth): no Gewinnfreibetrag, no Veranlagungsfreibetrag,
  no Regelbesteuerungsoption -/
  noGfb : Bool := false
  noVfb : Bool := false
  noRegel : Bool := false
  /-- tax year (2022-2025; `Params.ypOf`) -/
  year : Nat := 2025
  deriving Repr, Inhabited

/-- Everything before the Absetzbeträge (cents). -/
structure Base where
  wageL : Int
  wageSZ : Int
  sv : EmpSV
  svSZ : EmpSV
  penL : Int
  penSZ : Int
  kvPenL : Int
  kvPenSZ : Int
  gsvgC : Int
  nsa : Int
  selfE : Int
  vfbUsed : Int
  einkuenfte : Int
  spenden : Int
  einkommen : Int
  szIn : Int
  szB : Int
  szExcess : Int
  capital : Int
  deriving Repr, Inhabited

/-- § 39 Abs. 5: Veranlagungsfreibetrag on other income `x` ("bis zu 730 Euro … vermindert sich um jenen Betrag, um
den die anderen Einkünfte 730 Euro übersteigen"). -/
def vfbAmount (x : Int) : Int := pos (min x vfb - pos (x - vfb))

/-- § 10 Abs. 1 Z 3: Grundfreibetrag, 15 % of the first 33 000 € of profit. -/
def grundfreibetrag (gewinn : Int) (y : YP := yp2025) : Int := r2 (gfbRate * clamp 0 y.gfbBase gewinn)

/-- Steps 1-4. `regel`: the Regelbesteuerungsoption (§ 27a Abs. 5) puts all special-rate capital income into the
Einkommen. -/
def base (p : PersonIn) (regel : Bool) : Base :=
  let y := ypOf p.year
  let k := max 0 (p.payments - 12)
  let wageL := 12 * p.wagePay
  let wageSZ := k * p.wagePay
  let sv := (svMonth p.wagePay y).scale 12
  let svSZ := svSonder p.wagePay k y
  let penL := 12 * p.pensionPay
  let penSZ := 2 * p.pensionPay
  let (kvPenL, kvPenSZ) := if p.pensionPay > 0 then kvPension p.pensionPay p.aprilAt6 y else (0, 0)
  -- § 16 Abs. 3: the Pauschale, never into a loss; § 16 Abs. 1 Z 3 lit. a, 4, 5: SV is deducted on top
  let wN := wageL - sv.total
  let wkp := if wageL > 0 then min wkPauschale (pos wN) else 0
  let nsa := (wN - wkp) + (penL - kvPenL)
  -- § 67 Abs. 1-2, 12; § 41 Abs. 4: sonstige Bezüge within the sixth (with 12-14 instalments always within it)
  let szIn := wageSZ + penSZ
  let szB0 := szIn - svSZ.total - kvPenSZ
  let szExcess := pos (szB0 - szFixedMax)
  let szB := szB0 - szExcess
  let gsvgC := gsvg p.self y
  let gewinn := p.self - gsvgC
  let selfE := if p.self = 0 then 0 else gewinn - (if p.noGfb then 0 else grundfreibetrag gewinn y)
  let capital := p.interest + p.other27
  let other := selfE + p.rental
  let vfbUsed := if wageL + penL > 0 ∧ other > 0 ∧ ¬ p.noVfb then vfbAmount other else 0
  let einkuenfte := nsa + szExcess + selfE + p.rental + (if regel then capital else 0)
  let gde := einkuenfte - vfbUsed
  let spenden := min (pos p.charitable) (r2 (spendenCap * pos gde))
  { wageL, wageSZ, sv, svSZ, penL, penSZ, kvPenL, kvPenSZ, gsvgC, nsa, selfE, vfbUsed, einkuenfte, spenden,
    einkommen := gde - spenden, szIn, szB, szExcess, capital }

/-- § 33 Abs. 1: the tariff tax on the Einkommen (cents, commercial rounding of the cent). -/
def tariffTax (e : Int) (y : YP := yp2025) : Int := r2 (y.tariff.ticks e)

/-- § 67 Abs. 1 and § 41 Abs. 4: tax on the sonstige Bezüge within the Jahressechstel. `szIn` = those Bezüge
(gross), `b` = Bemessungsgrundlage (after their SV, § 67 Abs. 12). Freigrenze tested on the gross Bezüge ("wenn diese
sonstigen Bezüge 2 570 Euro übersteigen"; the next sentence defines the Bemessungsgrundlage separately). -/
def szTax (szIn b : Int) (y : YP := yp2025) : Int :=
  if szIn ≤ y.szFreigrenze then 0
  else if szIn ≤ szGlideMaxSixth then
    min (r2 (szRate * pos (b - szFreibetrag))) (r2 (szGlideRate * pos (b - y.szGlideStart)))
  else r2 (szSchedule.ticks b)

/-- § 67 Abs. 1 as withheld (no § 41 Abs. 4 recomputation): 6 % above 620 € once the Freigrenze is passed. -/
def szTaxWh (szIn b : Int) (y : YP := yp2025) : Int :=
  if szIn ≤ y.szFreigrenze then 0 else r2 (szSchedule.ticks b)

/-- What the household assigns to this taxpayer. -/
structure Claims where
  /-- Familienbonus Plus applied for (cents a year) -/
  fbp : Int := 0
  /-- Alleinverdiener- or Alleinerzieherabsetzbetrag (cents) -/
  avab : Int := 0
  /-- erhöhter Pensionistenabsetzbetrag -/
  pabHigh : Bool := false
  /-- Kindermehrbetrag paid to this taxpayer (computed by the household, § 33 Abs. 7) -/
  kmb : Int := 0
  /-- withholding mode (Lohnsteuer as the BMF calculator computes it): no Zuschlag (§ 33 Abs. 5 Z 3 is granted only in
  the Veranlagung), no refunds of § 33 Abs. 8, no Kindermehrbetrag, § 67 Abs. 1 without the § 41 Abs. 4 cap, no § 39
  Abs. 3 rounding -/
  wh : Bool := false
  deriving Repr, Inhabited

structure PTax where
  t1 : Int
  fbpUsed : Int
  vabC : Int
  pabC : Int
  /-- 2022 Teuerungsabsetzbetrag (§ 124b Z 407) -/
  tab : Int := 0
  avab : Int
  t2 : Int
  refundCap : Int
  afterCredits : Int
  sz : Int
  kmb : Int
  kest : Int
  /-- income tax of this taxpayer, cents (assessed part rounded per § 39 Abs. 3 later) -/
  total : Int
  deriving Repr, Inhabited

/-- Steps 5-6 for a computed `Base`. -/
def taxOf (b : Base) (cl : Claims) (regel : Bool) (p : PersonIn) : PTax :=
  let y := ypOf p.year
  let t1 := tariffTax b.einkommen y
  let fbpUsed := min (pos cl.fbp) (pos t1)
  -- § 33 Abs. 5: Verkehrsabsetzbetrag "bei Einkünften aus einem bestehenden Dienstverhältnis" + Zuschlag (Z 3)
  let vabC := if b.wageL > 0 then y.vab + (if cl.wh then 0 else y.zuschlag.amount b.einkommen) else 0
  -- § 33 Abs. 6: Pensionistenabsetzbetrag if Abs. 5 does not apply; taper on the "zu versteuernden laufenden
  -- Pensionseinkünften"
  let penN := b.penL - b.kvPenL
  let pabC := if b.wageL = 0 ∧ b.penL > 0 then (if cl.pabHigh then y.pabHigh.amount penN else y.pab.amount penN) else 0
  -- § 124b Z 407 lit. a (2022): Teuerungsabsetzbetrag "bei Anspruch auf den Verkehrsabsetzbetrag", in the
  -- Veranlagung. Lit. b (pensioners) is 0 for every statutory pensioner: excluded after the § 772a ASVG Einmalzahlung
  -- (Gesamtpensionseinkommen up to 2 250 EUR a month), and nil from 25 500 EUR of laufende Pensionseinkünfte
  -- (12 x 2 250 = 27 000 EUR); `refs/at/asvg_2022-09-01.txt` § 772a Abs. 1, `estg_2022-12-31.txt` § 124b Z 407.
  let tabC := if b.wageL > 0 ∧ ¬ cl.wh then y.tabWage.amount b.einkommen else 0
  let t2 := t1 - fbpUsed - cl.avab - vabC - pabC - tabC
  -- § 33 Abs. 8 Z 1-3, 5: refunds
  let svr :=
    if b.wageL > 0 then
      min (r2 (y.svrRate * b.sv.total)) (y.svrMax + (if b.einkommen < y.zuschlagEnd then y.svBonus else 0))
    else if b.penL > 0 then min (r2 (y.svrPenRate * b.kvPenL)) y.svrPenMax else 0
  let refundCap := cl.avab + svr
  let afterCredits := if cl.wh then max t2 0 else max t2 (-refundCap)
  let sz := if cl.wh then szTaxWh b.szIn b.szB y else szTax b.szIn b.szB y
  let kest := if regel then 0 else r2 (kestBank * p.interest) + r2 (kestOther * p.other27)
  { t1, fbpUsed, vabC, pabC, tab := tabC, avab := cl.avab, t2, refundCap, afterCredits, sz, kmb := cl.kmb, kest,
    total := if cl.wh then afterCredits + sz + kest else assessedRound (afterCredits + sz - cl.kmb) * 100 + kest }

/-- The taxpayer's tax with the cheaper of special rate and Regelbesteuerungsoption (§ 27a Abs. 5; "kann nur für
sämtliche Einkünfte … ausgeübt werden"). Returns (tax, base used, regel?). -/
def bestTax (p : PersonIn) (cl : Claims) : PTax × Base × Bool :=
  let b0 := base p false
  let t0 := taxOf b0 cl false p
  if p.interest + p.other27 = 0 ∨ p.noRegel then (t0, b0, false) else
  let b1 := base p true
  let t1 := taxOf b1 cl true p
  if t1.total < t0.total then (t1, b1, true) else (t0, b0, false)

/-- § 33 Abs. 7 Kindermehrbetrag for `n` children and the tariff tax `t1` (Abs. 1): literal reading, "Ergibt sich …
nach Abs. 1 eine Einkommensteuer unter 700 Euro … Die Differenz zwischen 700 Euro und der Einkommensteuer … erhöht
sich für jedes weitere Kind … um … 700 Euro". `perChild`: the alternative reading `700 n − t1` whenever positive. -/
def kmbAmount (n : Nat) (t1 : Int) (perChild : Bool) (y : YP := yp2025) : Int :=
  if n = 0 then 0
  else if perChild then pos (y.kmbPerChild * n - t1)
  else if t1 < y.kmbPerChild then y.kmbPerChild * n - pos t1 else 0

end AtTax
