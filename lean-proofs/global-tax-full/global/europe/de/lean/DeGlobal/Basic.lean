import DeTax.Legacy
import TaxKernel.Global

/-!
# Germany 2025 on kernel 2.0 (pilot)

The 1.x model (`DeTax`, vendored from `cmp/de/lean`, sha256 in `VENDORED_FROM_cmp_de.sha256`; its `Main.lean` is
`DeTax/Legacy.lean` with `main` renamed `legacyMain`, nothing else changed) stays the PIT, through its own per-line
function `runHousehold` (`GlobalModel.ofLine`): legacy lines through this exe are byte-identical to `detax`.

Sources: www.gesetze-im-internet.de as archived in 2025 (Internet Archive copies of the official pages, timestamps and
sha256 in `cmp20/global/pilots/de/law/archived2025/ARCHIVE_INDEX.tsv`; the 2026 current texts are saved beside them).
Read against 2025:
* **KStG § 23 (1)**: "Veranlagungszeiträume bis 2027 15 Prozent". **§ 8b (1), (4), (5)**: dividends "bleiben … außer
  Ansatz" unless "die Beteiligung zu Beginn des Kalenderjahres unmittelbar weniger als 10 Prozent" (abs. 4); "5 Prozent
  als Ausgaben, die nicht als Betriebsausgaben abgezogen werden dürfen" (abs. 5): 95 % exempt in effect.
  **EStG § 10d (2)** (applied through KStG § 8 (1)): losses "bis zu einem Gesamtbetrag der Einkünfte von 1 Million
  Euro unbeschränkt, darüber hinaus bis zu 70 Prozent".
* **SolZG § 3 (1) Nr. 1, § 4**: 5,5 % of the assessed corporation tax (the exemption limit of § 3 (3) is for
  "einkommensteuerpflichtige Personen" only).
* **GewStG § 8 Nr. 1** (one quarter of interest etc. "soweit die Summe den Betrag von 200 000 Euro übersteigt"),
  **§ 8 Nr. 5** (dividends exempt under KStG § 8b added back unless § 9 Nr. 2a applies), **§ 9 Nr. 2a** (holding of
  "mindestens 15 Prozent"), **§ 11 (1) S. 3, (2)** (trade income rounded down to 100 €; Freibetrag 24 500 € only for
  natural persons and partnerships; "Die Steuermesszahl … beträgt 3,5 Prozent"), **§ 16 (1), (4)** (the municipality's
  Hebesatz; 2025 wording: "Er beträgt 200 Prozent, wenn die Gemeinde nicht einen höheren Hebesatz bestimmt hat"; the
  280 % of the current text applies from 2027, § 36 (5b)). Input `deHebesatz` (percent); without it the 2025 minimum.
* **EStG § 20 (2) S. 1 Nr. 1, § 32d (1)** (gains on shares: capital income at 25 %; the 1.x model computes it with the
  Sparer-Pauschbetrag of § 20 (9) and the § 32d (6) test), **§ 23 (1) Nr. 1** (land: taxable if held "nicht mehr als
  zehn Jahre", except own residential use "im Jahr der Veräußerung und in den beiden vorangegangenen Jahren"), **§ 23 (1)
  Nr. 2** (other assets held not more than one year, "Gegenstände des täglichen Gebrauchs" excepted), **§ 23 (3) S. 5**
  ("steuerfrei, wenn der … Gesamtgewinn im Kalenderjahr weniger als 1 000 Euro betragen hat"). § 23 gains are tariff
  income: stacked on the 1.x model as other tariff income (its `rentalIncome` field). § 17 holdings (≥ 1 %): not
  modelled.
* **UStG § 12 (1)** 19 %, **§ 12 (2) Nr. 1** + Anlage 2 (7 %: food, books, newspapers, tap water), **Nr. 10** (local
  passenger transport), **Nr. 11** (accommodation); **§ 19 (1)** small business: prior year ≤ 25 000 € and current year
  ≤ 100 000 € (the pilot takes `turnover` as both); exemptions **§ 4 Nr. 8** (financial), **Nr. 10** (insurance),
  **Nr. 12** (letting of land), **Nr. 14** (medical care), **Nr. 21** (education) read in the current text.
* **EnergieStG § 2 (1) Nr. 1 b)** petrol "654,50 EUR" per 1 000 l, **Nr. 4 b)** diesel "470,40 EUR" per 1 000 l.
* **ErbStG § 10 (1) S. 6** (taxable acquisition rounded down to full 100 €), **§ 14 (1), (3)** (ten-year
  aggregation; the tax for the last acquisition alone is a floor; "nicht mehr als 50 Prozent dieses Erwerbs"),
  **§ 15** (classes), **§ 16 (1)** (500 000 / 400 000 / 200 000 / 100 000 / 20 000 / 20 000), **§ 17** (Versorgungs-
  freibetrag on death: spouse 256 000; children 52 000 / 41 000 / 30 700 / 20 500 / 10 300 by age), **§ 19 (1)** table
  and **§ 19 (3)** hardship relief (half of the excess at rates up to 30 %, three quarters above).
* **GrEStG § 11** (3,5 %, rounded down to full euros); a Land's own rate (Art. 105 (2a) GG) by input `deGrEStRateBp`.
-/

namespace DeGlobal
open TaxKernel TaxKernel.Global Lean

/-! ## The 1.x model as a line function -/

/-- The 1.x options, exactly as `legacyMain` builds them. -/
def deOpts (args : List String) : DeTax.Opts :=
  let kist : Int := (args.filterMap fun a =>
    if a.startsWith "--kist=" then (a.drop 7).toString.toInt? else none).headD 0
  let compat := args.contains "--gettsim-compat"
  { kistBp := kist, joint := !args.contains "--separate",
    perChild := !(compat || args.contains "--all-children-together" || args.contains "--oecd"),
    opt32d6 := !(compat || args.contains "--no-32d6"), g := compat,
    gTariff := args.contains "--g-tariff", gVors := args.contains "--g-vors", gAlte := args.contains "--g-alte",
    gSv := args.contains "--g-sv" }

def pitLine (args : List String) (j : Json) : Json := _root_.runHousehold (deOpts args) j

def pitOf (args : List String) (c : Canon) : Int := jsonIncomeTax (pitLine args c.raw)

/-! ## 1200: Körperschaftsteuer, Solidaritätszuschlag, Gewerbesteuer -/

def kst : CorpRegime :=
  { name := "Körperschaftsteuer", sched := Schedule.flat 1500, lossFull := 1000000, lossExcessBp := 7000,
    participationBp := 9500, participationMinBp := 1000 }

def hebesatzPct (g : CanonGlobal) : Int := intField g.raw "deHebesatz" 200

/-- Gewerbeertrag before rounding: the KSt income before losses + § 8 Nr. 1 (a quarter of interest above 200 000 €)
+ § 8 Nr. 5 (the exempt dividends back when the holding is below 15 %). -/
def gewerbeertrag (co : Company) : Int :=
  kst.beforeLosses co + divR .down (pos (co.interestExpense - 200000)) 4
    + (if co.participationBp < 1500 then kst.participationExempt co else 0)

def gewerbesteuer (hebesatz : Int) (co : Company) : Int :=
  twoStage {} 35 1000 (hebesatz * 100) (toMultiple .down 100 (pos (gewerbeertrag co)))

def corporate : Family :=
  { name := "1200 KSt, SolZ, GewSt", covers := [.cit],
    run := fun _ g _ =>
      if g.entity != .company then [] else
      let co := g.company
      let k := kst.citTax co
      [kst.citCharge co "KStG § 23 (1) 15 %; § 8b (1), (4), (5); EStG § 10d (2) (1 Mio + 70 %)",
       charge .cit "Solidaritätszuschlag" k id (fun x => divR .down (550 * x) BP) (statute := "SolZG § 3 (1) Nr. 1, § 4 (5,5 %)"),
       charge .cit "Gewerbesteuer" (gewerbeertrag co) (fun x => toMultiple .down 100 (pos x))
         (fun _ => gewerbesteuer (hebesatzPct g) { co with lossesForward := 0 }) (level := .local)
         (statute := s!"GewStG §§ 8 Nr. 1, 5, 9 Nr. 2a, 11 (3,5 %), 16 (Hebesatz {hebesatzPct g} %)")] }

/-! ## 1100: gains (EStG §§ 20 (2), 23) stacked on the 1.x model -/

def isAbgeltung (d : Disposal) : Bool := (d.kind.isShares && decide (d.stakeBp < 100)) || d.kind == .bonds

def isPrivateSale (d : Disposal) : Bool :=
  (d.kind.isRealEstate && !d.mainHome && decide (d.heldMonths ≤ 120))
  || ((d.kind == .other) && decide (d.heldMonths ≤ 12))

def s23Gain (ds : List Disposal) : Int :=
  let tot := isum ((ds.filter isPrivateSale).map (·.gain))
  ({ amount := 1000, threshold := true } : AnnualExempt).apply tot

def gainsCharges (args : List String) (g : CanonGlobal) : List Charge :=
  let ds := g.disposals
  let abg := isum ((ds.filter isAbgeltung).map (·.gain))
  let s23 := s23Gain ds
  let st := stackedTax (pitOf args) g.household
  let tAbg := st { capitalGains := abg }
  let tBoth := st { capitalGains := abg, rentalIncome := s23 }
  [charge .pit "Einkommensteuer + SolZ auf Veräußerungsgewinne (§ 20 (2))" abg id (fun _ => tAbg)
     (event := "shares and bonds") (statute := "EStG § 20 (2) S. 1 Nr. 1, Nr. 7, § 32d (1); stacked on the 1.x model"),
   charge .pit "Einkommensteuer + SolZ auf private Veräußerungsgeschäfte (§ 23)"
     (isum ((ds.filter isPrivateSale).map (·.gain))) (fun _ => s23) (fun _ => tBoth - tAbg)
     (event := "land ≤ 10 years, other ≤ 1 year") (statute := "EStG § 23 (1) Nr. 1, 2, (3) S. 5 (< 1 000 € exempt); tariff, stacked")]

def capitalGains : Family :=
  { name := "1100 Veräußerungsgewinne", covers := [],
    run := fun args g _ => if g.entity == .company || g.disposals.isEmpty then [] else gainsCharges args g }

/-! ## 5111 Umsatzsteuer, 5121 Energiesteuer -/

def ust : Vat :=
  { name := "Umsatzsteuer", standard := 1900, reduced := 700, threshold := 25000,
    classOf := fun gd => match gd with
      | .food | .books | .newspapers | .water | .hotels | .transport => .reduced
      | .rent | .health | .education | .financial | .insurance => .exempt
      | _ => .standard }

def energie : Excise :=
  { rates := [{ good := .petrol, name := "Energiesteuer (Benzin)", perUnitNum := 65450, perUnitDen := 100000,
                statute := "EnergieStG § 2 (1) Nr. 1 b): 654,50 EUR / 1 000 l" },
              { good := .diesel, name := "Energiesteuer (Diesel)", perUnitNum := 47040, perUnitDen := 100000,
                statute := "EnergieStG § 2 (1) Nr. 4 b): 470,40 EUR / 1 000 l" },
              -- FT review (2026-11-21, second pass): EnergieStG § 2 (3) Nr. 1 b) "für 1 000 l ordnungsgemäß
              -- gekennzeichnete Gasöle ... mit einem Schwefelgehalt von höchstens 50 mg/kg 61,35 EUR" (heating oil)
              { good := .heatingOil, name := "Energiesteuer (Heizöl, gekennzeichnetes Gasöl)", perUnitNum := 6135, perUnitDen := 100000,
                statute := "EnergieStG § 2 (3) Nr. 1 b): 61,35 EUR / 1 000 l (gekennzeichnete Gasöle, höchstens 50 mg/kg Schwefel)" }] }

def consumption : Family :=
  { name := "5111 USt, 5121 EnergieSt", covers := [.vat, .excise],
    run := fun _ g _ =>
      (if g.consumption.isEmpty then [] else
        [ust.basketCharge g.consumption "UStG § 12 (1), (2) Nr. 1 + Anlage 2, Nr. 10, 11; § 4 Nr. 8, 10, 12, 14, 21"])
      ++ energie.charges g.consumption
      ++ (if g.entity == .company && !g.company.sales.isEmpty then
            [ust.businessCharge g.company "UStG §§ 12, 15, 19 (1) (25 000 €)"] else []) }

/-! ## 4300 Erbschaft- und Schenkungsteuer -/

def rowsI : List (Int × Int) := [(75000, 700), (300000, 1100), (600000, 1500), (6000000, 1900), (13000000, 2300), (26000000, 2700)]
def rowsII : List (Int × Int) := [(75000, 1500), (300000, 2000), (600000, 2500), (6000000, 3000), (13000000, 3500), (26000000, 4000)]
def rowsIII : List (Int × Int) := [(75000, 3000), (300000, 3000), (600000, 3000), (6000000, 3000), (13000000, 5000), (26000000, 5000)]

/-- § 19 (3): the excess may be covered by half (rate ≤ 30 %) or three quarters (rate > 30 %) of the excess value. -/
def relief19 (r : Int) : Int := if r ≤ 3000 then 5000 else 7500

def cls (allow : Int) (rows : List (Int × Int)) (top : Int) : TaxClass :=
  { allowance := allow, slab := rows, slabTop := top, relief := some relief19, baseRound := Rule.downTo 100 }

/-- § 15 / § 16: 0 spouse (I, 500 000), 1 child (I, 400 000), 2 grandchild (I, 200 000), 3 other class I (100 000),
4 class II (20 000), 5 class III (20 000). Parents: class I on death, class II for gifts; other relatives are taken
as class III (cousins; in-laws and step-parents, class II, are not distinguished by the input). -/
def classIdx (gift : Bool) (r : Relation) : Nat :=
  match r with
  | .spouse => 0 | .child => 1 | .grandchild => 2
  | .parent => if gift then 4 else 3
  | .sibling | .nieceNephew => 4
  | _ => 5

/-- § 17: on death, 256 000 for the spouse; for a child by age. -/
def versorgung (t : Transfer) : Int :=
  if t.kind == .gift then 0 else
  match t.relation with
  | .spouse => 256000
  | .child => if t.recipientAge ≤ 5 then 52000 else if t.recipientAge ≤ 10 then 41000 else if t.recipientAge ≤ 15 then 30700
              else if t.recipientAge ≤ 20 then 20500 else if t.recipientAge < 27 then 10300 else 0
  | _ => 0

def erbst (gift : Bool) : InheritanceTax :=
  { name := if gift then "Schenkungsteuer" else "Erbschaftsteuer", classOf := classIdx gift, lookbackYears := 10,
    extraAllowance := versorgung,
    classes := [cls 500000 rowsI 3000, cls 400000 rowsI 3000, cls 200000 rowsI 3000, cls 100000 rowsI 3000,
                cls 20000 rowsII 4300, cls 20000 rowsIII 5000] }

/-- § 14 (1) S. 4 and (3): never less than the tax on this acquisition alone, never more than half of it. -/
def erbstTax (t : Transfer) : Int :=
  let it := erbst (t.kind == .gift)
  let alone := it.taxOn t t.statutoryValue
  min (max (it.tax t) alone) (pos t.statutoryValue / 2)

def erbschaft : Family :=
  { name := "4300 ErbSt", covers := [.estate],
    run := fun _ g _ =>
      (g.transfers.filter (·.relation != .charity)).zipIdx.map fun (t, i) =>
        let it := erbst (t.kind == .gift)
        charge .estate it.name t.statutoryValue (fun v => it.taxableOf t (it.priorWithin t + v)) (fun _ => erbstTax t)
          (event := s!"{if t.kind == .gift then "gift" else "inheritance"} {i + 1}")
          (statute := "ErbStG § 10 (1) S. 6, § 14 (1), (3), §§ 15, 16, 17, 19 (1), (3)") }

/-! ## 4400 Grunderwerbsteuer -/

def grest (g : CanonGlobal) : TransferDuty :=
  { name := "Grunderwerbsteuer", sched := Schedule.flat (intField g.raw "deGrEStRateBp" 350) }

def grunderwerb : Family :=
  { name := "4400 GrESt", covers := [.transactions],
    run := fun _ g _ => (grest g).charges g.purchases s!"GrEStG § 11 ({intField g.raw "deGrEStRateBp" 350} bp; Land rate by input), rounded down" (level := .state) }

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  (if g.company.lossesForward ≠ 0 then ["Gewerbesteuer: loss carry-forward (GewStG § 10a) not read; trade tax computed without it"] else [])
  ++ (if g.entity == .company && (intField g.raw "deHebesatz" 0) == 0 then ["Gewerbesteuer at the 2025 statutory minimum Hebesatz (200 %): give deHebesatz for the municipality"] else [])
  ++ (if g.disposals.any (fun d => d.kind.isShares && decide (d.stakeBp ≥ 100)) then ["EStG § 17 holdings (≥ 1 %): not modelled"] else [])
  ++ (if g.transfers.any (·.relation == .charity) then ["ErbStG § 13 exemptions for charities not modelled"] else [])
  ++ (if g.transfers.any (fun t => t.homeValue ≠ 0 || t.businessValue ≠ 0) then ["ErbStG § 13 (1) Nr. 4b/4c family home and §§ 13a-13c business reliefs not modelled"] else [])
  ++ (if g.assets.any (·.kind.isRealEstate) then ["Grundsteuer (GrStG 2025 Messzahlen, municipal Hebesatz) not modelled in the pilot"] else [])
  ++ (if g.consumption.any (fun s => s.good == .spirits || s.good == .beer || s.good == .wine || s.good == .cigarettes || s.good == .tobaccoOther) then ["alcohol and tobacco duties not modelled in the pilot (VAT only)"] else [])

def model : GlobalModel :=
  { (GlobalModel.ofLine "DE" "Germany" "EUR" "2025" pitLine) with
    families := [corporate, capitalGains, consumption, erbschaft, grunderwerb], unsupported,
    notes := ["Germany 2025 kernel-2.0 pilot (cmp20/global/pilots/de): statutes as archived in 2025"] }

/-- Every 1.x output is unchanged: the PIT is the 1.x line function on the household's own line. -/
theorem model_pit (args : List String) (c : Canon) :
    (model.computeGlobal args (CanonGlobal.ofCanon c)).pit = _root_.runHousehold (deOpts args) c.raw := rfl

/-! ## Checks against the statute's own arithmetic -/

-- KSt: 2 Mio profit, 5 Mio losses: 1 Mio + 70 % of 1 Mio offset, 15 % of 300 000
#guard kst.citTax { profit := 2000000, lossesForward := 5000000 } == 45000
-- § 8b: dividends from a 10 % holding 95 % exempt; from 9,99 % taxable
#guard kst.citTax { profit := 1000000, dividendsReceived := 1000000, participationBp := 1000 } == 7500
#guard kst.citTax { profit := 1000000, dividendsReceived := 1000000, participationBp := 999 } == 150000
-- GewSt: 1 Mio trade income, 400 % Hebesatz: 3,5 % × 1 Mio × 4 = 140 000; interest 600 000: + ¼ × 400 000
#guard gewerbesteuer 400 { profit := 1000000 } == 140000
#guard gewerbesteuer 400 { profit := 1000000, interestExpense := 600000 } == 140000 + 14000
-- § 8 Nr. 5: a 10 % holding's dividends come back into trade income, a 15 % holding's do not
#guard gewerbeertrag { profit := 1000000, dividendsReceived := 1000000, participationBp := 1000 } == 1000000
#guard gewerbeertrag { profit := 1000000, dividendsReceived := 1000000, participationBp := 1500 } == 50000
-- ErbSt: child inherits 475 000 at 30: 75 000 taxable at 7 %
#guard erbstTax { kind := .inheritance, value := 475000, relation := .child, recipientAge := 30 } == 5250
-- § 19 (3): 75 100 taxable: 11 % would be 8 261; relief: 5 250 + half of 100
#guard erbstTax { kind := .inheritance, value := 475100, relation := .child, recipientAge := 30 } == 5300
-- § 17: a 4-year-old child: 52 000 more
#guard erbstTax { kind := .inheritance, value := 475000, relation := .child, recipientAge := 4 } == 1610
-- § 14: second gift of 300 000 to a child after 300 000 four years before: tax on 600 000 less tax on 300 000
#guard erbstTax { kind := .gift, value := 300000, relation := .child, prior := [(300000, 4)] } == 22000
-- class III: 100 000 to an unrelated person: 80 000 at 30 %
#guard erbstTax { kind := .inheritance, value := 100000, relation := .unrelated } == 24000
-- § 23 (3) S. 5: 999 € of private sale gains is exempt, 1 000 € is taxed in full
#guard s23Gain [{ kind := .realEstate, proceeds := 100999, cost := 100000, heldMonths := 24 }] == 0
#guard s23Gain [{ kind := .realEstate, proceeds := 101000, cost := 100000, heldMonths := 24 }] == 1000
#guard s23Gain [{ kind := .realEstate, proceeds := 200000, cost := 100000, heldMonths := 121 }] == 0
#guard s23Gain [{ kind := .home, proceeds := 200000, cost := 100000, heldMonths := 24, mainHome := true }] == 0
#guard ust.embedded { good := .food, amount := 107 } == 7
#guard energie.duty { good := .petrol, amount := 1700, quantity := 1000000 } == 654
#guard energie.duty { good := .heatingOil, amount := 1000, quantity := 1000000 } == 61

end DeGlobal
