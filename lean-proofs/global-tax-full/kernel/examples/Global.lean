import TaxKernel.Global

/-!
# Toy calls of every kernel-2.0 part, checked by `#guard` (`cd cmp20/kernel && lake env lean examples/Global.lean`)

Numbers are toy values chosen to exercise each rule's edges; where a number has the shape of a real statute the
statute is named, but the pilots (`cmp20/global/pilots/`) are where statutes are modelled and cited.
-/

open TaxKernel TaxKernel.Global Lean

/-! ## Master equation -/
#guard (charge .cit "t" 1000 id (fun x => x * 2 / 10) 50).due == 150
#guard (charge .cit "t" 1000 id (fun x => x * 2 / 10) 500).due == 0           -- non-refundable: capped at the gross
#guard (charge .cit "t" 1000 id (fun x => x * 2 / 10) 500 (refundable := true)).due == -300

/-! ## Corporate -/
def toyCorp : CorpRegime :=
  { name := "toy CIT", sched := Schedule.flat 1500, lossFull := 1000000, lossExcessBp := 7000,
    interestCapBp := 3000, interestSafe := 3000000, safeIsThreshold := true,
    participationBp := 9500, participationMinBp := 1000 }
-- loss offset: 1,000,000 in full + 70 % of the next 1,000,000 = 1,700,000 of 2,000,000 income
#guard lossOffset 1000000 7000 2000000 5000000 == 1700000
#guard toyCorp.taxableProfit { profit := 2000000, lossesForward := 5000000 } == 300000
#guard toyCorp.citTax { profit := 2000000, lossesForward := 5000000 } == 45000
-- interest limitation with an all-or-nothing de minimis threshold: a notch at 3,000,000
#guard toyCorp.interestDisallowed { profit := 1000000, interestExpense := 2999999 } == 0
#guard toyCorp.interestDisallowed { profit := 1000000, interestExpense := 3000000 } == 3000000 - 1200000
-- participation exemption 95 % from a 10 % stake
#guard toyCorp.taxableProfit { profit := 1000000, dividendsReceived := 1000000, participationBp := 1000 } == 50000
#guard toyCorp.taxableProfit { profit := 1000000, dividendsReceived := 1000000, participationBp := 999 } == 1000000
-- a minimum tax of 1 % of turnover wins over a small regular tax
#guard ({ toyCorp with minBp := 100 }).citTax { profit := 10000, turnover := 5000000 } == 50000
#guard topUp 1500 1000000 200000 80000 == 40000

/-! ## Capital income and gains -/
def flat25 : FlatCapital := { rateBp := 2500, allowance := 1000 }
#guard flat25.tax 5000 == 1000
#guard flat25.tax 800 == 0
def gr : GainRule := { exemptAfterMonths := 120, inclusionShortBp := 10000 }
#guard gr.taxable 1 1 { kind := .realEstate, proceeds := 500000, cost := 300000, heldMonths := 119 } == 200000
#guard gr.taxable 1 1 { kind := .realEstate, proceeds := 500000, cost := 300000, heldMonths := 120 } == 0
def grIdx : GainRule := { indexCost := true, longAfterMonths := 12, inclusionLongBp := 5000 }
-- cost 100,000 indexed by 130/100: gain 200,000 − 130,000 = 70,000, half included after 12 months
#guard grIdx.taxable 130 100 { kind := .listedShares, proceeds := 200000, cost := 100000, heldMonths := 24 } == 35000
#guard grIdx.taxable 130 100 { kind := .listedShares, proceeds := 200000, cost := 100000, heldMonths := 6 } == 70000
#guard ({ amount := 1000, threshold := true } : AnnualExempt).apply 999 == 0
#guard ({ amount := 1000, threshold := true } : AnnualExempt).apply 1000 == 1000
#guard ({ amount := 1000 } : AnnualExempt).apply 1500 == 500
def wht : Wht := { rules := [{ kind := .dividend, toCompany := some true, minStakeBp := 1000, rateBp := 0 },
                             { kind := .dividend, rateBp := 2500 }, { kind := .royalty, rateBp := 1500 }] }
#guard wht.amount { kind := .dividend, amount := 100000, toCompany := true, stakeBp := 1500 } == 0
#guard wht.amount { kind := .dividend, amount := 100000, toCompany := true, stakeBp := 500 } == 25000
#guard wht.amount { kind := .royalty, amount := 100000 } == 15000
#guard wht.amount { kind := .interest, amount := 100000 } == 0
#guard afterCredit 1000 1500 false == 0
#guard afterCredit 1000 1500 true == -500

/-! ## Property and wealth -/
-- value 300,000 × 0.31 ‰ = 93 (basic amount) × Hebesatz 810 % = 753.3 → 753
#guard twoStage {} 31 100000 81000 300000 == 753
def pt : PropertyTax := { sched := Schedule.ofList [(0, 0), (8000, 400), (30000, 600)], exempt := 0,
                          onAnnualValue := true }
#guard pt.amount { kind := .home, value := 2000000, annualValue := 40000 } == 880 + 600
def wt : WealthTax := { sched := Schedule.flat 100, allowance := 700000, entryThreshold := 1300000,
                        homeExempt := 300000, capBp := 6000, capMaxReliefBp := 8000 }
#guard wt.base [{ kind := .deposits, value := 1299999 }] == 0             -- entry threshold: a notch
#guard wt.base [{ kind := .deposits, value := 1300000 }] == 600000
#guard wt.base [{ kind := .home, value := 1000000 }, { kind := .listedShares, value := 1000000, debt := 100000 }] == 900000
#guard wt.capped 10000 59000 100000 == 2000                                   -- cap: at least 20 % remains
#guard wt.capped 10000 0 100000 == 10000

/-! ## Inheritance and gift (whole-amount tariff with a hardship relief of DE ErbStG § 19 (3) shape) -/
def rowsI : List (Int × Int) := [(75000, 700), (300000, 1100), (600000, 1500), (6000000, 1900), (13000000, 2300),
                                 (26000000, 2700)]
def relief19 (r : Int) : Int := if r ≤ 3000 then 5000 else 7500
#guard slabTicks rowsI 3000 75000 == 700 * 75000
#guard slabTicks rowsI 3000 75001 == 1100 * 75001
#guard slabRelieved rowsI 3000 relief19 75001 == 700 * 75000 + 5000 * 1        -- the notch is softened
#guard slabRelieved rowsI 3000 relief19 100000 == 1100 * 100000                  -- relief no longer binds
def it : InheritanceTax :=
  { classOf := fun r => if r == .child || r == .spouse then 0 else 1, lookbackYears := 10,
    classes := [{ allowance := 400000, slab := rowsI, slabTop := 3000, relief := some relief19,
                  baseRound := Rule.downTo 100 },
                { allowance := 20000, slab := [(75000, 1500), (300000, 2000)], slabTop := 2500 }] }
#guard it.tax { kind := .inheritance, value := 475000, relation := .child } == 5250
#guard it.tax { kind := .gift, value := 300000, relation := .child, prior := [(300000, 5)] } == 22000
#guard it.tax { kind := .gift, value := 300000, relation := .child, prior := [(300000, 10)] } == 0   -- outside 10 years
#guard (estateCharge "estate tax" (Schedule.flat 4000) {} 325000 [.spouse, .charity]
          [{ kind := .inheritance, value := 500000, relation := .child },
           { kind := .inheritance, value := 900000, relation := .spouse }] "toy").due == 70000

/-! ## Transfer duties -/
def sdlt : TransferDuty := { name := "toy SDLT", sched := Schedule.ofList [(0, 0), (125000, 200), (250000, 500)],
                             additionalBp := 500 }
#guard sdlt.amount { kind := .home, price := 300000 } == 2500 + 2500
#guard sdlt.amount { kind := .home, price := 300000, additionalHome := true } == 5000 + 15000
def slabDuty : TransferDuty := { name := "toy slab", slab := [(250000, 100), (500000, 300)], slabTop := 400 }
#guard slabDuty.amount { kind := .home, price := 250000 } == 2500
#guard slabDuty.amount { kind := .home, price := 250001 } == 7500               -- notch of 5,000 for 1 unit

/-! ## VAT, excise, payroll -/
def vat : Vat := { standard := 1900, reduced := 700,
                   classOf := fun g => match g with | .food | .books => .reduced | .rent | .health => .exempt
                                                    | _ => .standard,
                   threshold := 25000 }
#guard vat.embedded { good := .clothing, amount := 119 } == 19
#guard vat.embedded { good := .food, amount := 107 } == 7
#guard vat.embedded { good := .rent, amount := 1000 } == 0
#guard vat.basket [{ good := .clothing, amount := 1190 }, { good := .food, amount := 1070 }] == 190 + 70
#guard vat.net { turnover := 25000, sales := [{ good := .other, net := 25000 }] } == 0
#guard vat.net { turnover := 100000, sales := [{ good := .other, net := 100000 }],
                 inputs := [{ good := .other, net := 40000 }] } == 19000 - 7600
#guard vat.net { turnover := 100000, sales := [{ good := .other, net := 50000 }, { good := .health, net := 50000 }],
                 inputs := [{ good := .other, net := 40000 }] } == 9500 - 3800
def petrol : ExciseRate := { good := .petrol, perUnitNum := 65450, perUnitDen := 100000 }
#guard petrol.duty { good := .petrol, amount := 2000, quantity := 1000000 } == 654
def cig : ExciseRate := { good := .cigarettes, perUnitNum := 10, perUnitDen := 100, adValoremBp := 2000,
                          minNum := 25, minDen := 100 }
#guard cig.duty { good := .cigarettes, amount := 100, quantity := 200000 } == 50     -- 20 specific + 20 ad valorem < 50 minimum
#guard ({ rateBp := 545, threshold := 1200000 } : PayrollTax).amount 2000000 == 43600
#guard ({ rateBp := 545, threshold := 1200000, deduct := false } : PayrollTax).amount 1200000 == 0
#guard ({ rateBp := 545, threshold := 1200000, deduct := false } : PayrollTax).amount 1200001 == 65400

/-! ## A toy jurisdiction end to end -/
def toyPit (c : Canon) : Out :=
  let w := sumInts (c.adults.map (·.wages))
  Out.make c "ZZ" "ZZD" ((Schedule.ofList [(0, 0), (10000, 2000)]).tax {} w) (employeeSocial := w / 10)

def toyCountry : Country := { code := "ZZ", name := "Toy", currency := "ZZD", compute := toyPit }

def toyModel : GlobalModel :=
  (GlobalModel.ofCountry toyCountry)
  |>.withFamily { name := "corporate", covers := [.cit], run := fun _ g _ =>
                    if g.entity == .company then [toyCorp.citCharge g.company "toy CIT act"] else [] }
  |>.withFamily { name := "capital gains", covers := [], run := fun _ g _ =>
                    g.disposals.zipIdx.map fun (d, i) =>
                      charge .pit "toy CGT" d.gain (fun _ => gr.taxable 1 1 d) (fun x => x * 2500 / 10000)
                        (event := s!"disposal {i + 1}") }
  |>.withFamily { name := "VAT", covers := [.vat], run := fun _ g _ =>
                    if g.consumption.isEmpty then [] else [vat.basketCharge g.consumption "toy VAT act"] }

def hh : Canon := { id := "h1", adults := [{ wages := 50000 }] }

-- the adapter leaves the 1.x line unchanged (also a theorem: `adapter_unchanged`)
#guard ((GlobalModel.ofCountry toyCountry).computeGlobal [] (CanonGlobal.ofCanon hh)).pit.compress
        == (toyPit hh).toJson.compress
#guard (toyModel.computeGlobal [] (CanonGlobal.ofCanon hh)).pit.compress == (toyPit hh).toJson.compress
#guard (toyModel.computeGlobal [] (CanonGlobal.ofCanon hh)).total == 8000 + 5000

def hhG : CanonGlobal :=
  { CanonGlobal.ofCanon hh with
    disposals := [{ kind := .realEstate, proceeds := 500000, cost := 300000, heldMonths := 24 }],
    consumption := [{ good := .clothing, amount := 1190 }, { good := .food, amount := 1070 }] }
#guard (toyModel.computeGlobal [] hhG).totalOf .pit == 8000 + 50000
#guard (toyModel.computeGlobal [] hhG).totalOf .vat == 260
#guard (toyModel.computeGlobal [] hhG).total == 8000 + 5000 + 50000 + 260
#guard (toyModel.computeGlobal [] hhG).notModelled.length == Oecd.all.length - 4
-- the global JSON reader: a 1.x line is read as `ofCanon`
#guard match Json.parse "{\"id\":\"x\",\"adults\":[{\"wages\":50000}]}" with
  | .ok j => match parseGlobal j with
    | .ok g => g.isLegacy && (toyModel.computeGlobal [] g).pit.compress == (toyPit { hh with id := "x" }).toJson.compress
    | _ => false
  | _ => false
