import TaxKernel.Global2

/-!
# Toy calls of every kernel-2.1 to 2.9 part (`TaxKernel.Global2`), checked by `#guard`

`cd cmp20/kernel && lake env lean examples/Global2.lean`. Where a number reproduces a builder's region-side part
(R4 `Exc`/`MinTax`, FJ two-period VAT, TM art. 119 excise, SA/QA taxable share) the builder's own figure is used.
-/

open Lean TaxKernel TaxKernel.Global

/-- A global line from JSON text (default entity if it does not parse). -/
def gl (s : String) : CanonGlobal :=
  match Json.parse s with
  | .ok j => match parseGlobal j with | .ok g => g | .error _ => default
  | .error _ => default

def hh (consumption : String) (extra : String := "") : CanonGlobal :=
  gl ("{\"id\":\"h\",\"schema\":\"global/2.0\",\"household\":{\"id\":\"h\",\"adults\":[{\"age\":40}]},\"consumption\":"
    ++ consumption ++ extra ++ "}")

/-! ## Dates and line extras -/
#guard dayOfYear? 2025 "2025-08-01" == some 212
#guard dayOfYear? 2025 "2025-01-01" == some 0
#guard dayOfYear? 2024 "2024-03-01" == some 60          -- leap year
#guard dayOfYear? 2025 "2024-12-31" == some 0           -- earlier year: the start
#guard dayOfYear? 2025 "2026-01-05" == some 365         -- later year: the end
#guard dayOfYear? 2025 "1 Aug 2025" == none
#guard scaleDays 36500 212 365 == 21200
#guard scaleDays 36500 365 365 == 36500
#guard (consumptionX (hh "[{\"good\":\"beer\",\"amount\":100,\"platoBp\":1200,\"sub\":\"craft\",\"imported\":true}]")).map (·.2)
  == [{ platoBp := 1200, sub := "craft", imported := true }]
#guard (consumptionX (hh "[{\"good\":\"beer\",\"amount\":100}]" ",\"date\":\"2025-09-01\",\"importedGoods\":[\"beer\"]")).map (·.2)
  == [{ date := "2025-09-01", imported := true }]
#guard (consumptionX { id := "x", household := { id := "x" }, consumption := [{ good := .food, amount := 1 }] }).map (·.2) == [{}]

/-! ## Dated VAT (FJ: 15 % to 31 July 2025, 12.5 % from 1 August; financial services exempt) -/
def fjVat1 : Vat := { name := "VAT (to 31 July)", standard := 1500, classOf := fun g => if g == .financial then .exempt else .standard }
def fjVat2 : Vat := { fjVat1 with name := "VAT (from 1 August)", standard := 1250 }
def fj : DatedVat := { periods := [{ vat := fjVat1, statute := "s14 15%" }, { start := "2025-08-01", vat := fjVat2, statute := "s14 12.5%" }] }

-- undated basket: 212 days at 15 %, 153 at 12.5 % (FjGlobal.Consumption's own guard: [2765, 1700])
#guard (fj.basketCharges (hh "[{\"good\":\"food\",\"amount\":36500}]")).map (·.due) == [2765, 1700]
#guard (fj.basketCharges (hh "[{\"good\":\"food\",\"amount\":36500}]")).map (·.statute)
  == ["s14 15%; 212/365 of the basket", "s14 12.5%; 153/365 of the basket"]
#guard (fj.basketCharges (hh "[{\"good\":\"food\",\"amount\":36500}]")).map (·.base) == [21200, 15300]
-- the entity's date puts the whole basket in one period, statute without a note
#guard (fj.basketCharges (hh "[{\"good\":\"food\",\"amount\":11250}]" ",\"date\":\"2025-09-01\"")).map (fun c => (c.due, c.statute)) == [(1250, "s14 12.5%")]
#guard (fj.basketCharges (hh "[{\"good\":\"food\",\"amount\":11500}]" ",\"date\":\"2025-07-31\"")).map (·.due) == [1500]
-- per-line dates, mixed with an undated line
#guard (fj.basketCharges (hh "[{\"good\":\"food\",\"amount\":11500,\"date\":\"2025-03-01\"},{\"good\":\"food\",\"amount\":36500}]")).map (·.due)
  == [1500 + 2765, 1700]
#guard (fj.basketCharges (hh "[{\"good\":\"financial\",\"amount\":36500}]")).map (·.due) == [0, 0]
#guard (fj.basketCharges (hh "[]")).isEmpty
-- a single period is the 2.0 `Vat.basketCharge`
#guard (({ periods := [{ vat := fjVat1, statute := "s" }] } : DatedVat).basketCharges (hh "[{\"good\":\"food\",\"amount\":36500}]")).map (fun c => (c.due, c.statute))
  == [(fjVat1.basket [{ good := .food, amount := 36500 }], "s")]
-- supplies: the entity's date, else the regime at the end of the year, or split by days
def co1 : String := "{\"id\":\"c\",\"entity\":\"company\",\"company\":{\"turnover\":365000,\"sales\":[{\"good\":\"food\",\"net\":365000}],\"inputs\":[{\"good\":\"food\",\"net\":36500}]}"
#guard (fj.businessCharges (gl (co1 ++ "}"))).map (fun c => (c.due, c.statute))
  == [(45625 - 4562, "s14 12.5% (no date given: the rate in force at the end of 2025)")]
#guard (fj.businessCharges (gl (co1 ++ ",\"date\":\"2025-02-01\"}"))).map (·.due) == [54750 - 5475]
#guard (({ fj with undatedSupplies := .split } : DatedVat).businessCharges (gl (co1 ++ "}"))).map (·.due)
  == [31800 - 3180, 19125 - 1912]
#guard (fj.vatOn 2025 "2025-10-01").map (·.standard) == some 1250

/-! ## Excise rules -/
-- R4.Exc reproduced: beer 1 000 for 1 l, ad valorem 50 % on the value before excise and VAT 18 % → 282
def r4beer : ExciseRule := { good := .beer, adValoremBp := 5000, valueBase := .beforeTax, vatBp := 1800 }
#guard r4beer.dutyOn { good := .beer, amount := 1000, quantity := 1000 } {} == 282
-- R4.Exc: specific 100 per litre + 20 % ad valorem, VAT 16 % → 227
#guard ({ good := .petrol, perUnitNum := 100, adValoremBp := 2000, valueBase := .beforeTax, vatBp := 1600 } : ExciseRule).dutyOn
  { good := .petrol, amount := 1000, quantity := 1000 } {} == 227
-- TM art. 119 reproduced (rounded once): p·e/((1+e)(1+VAT)), beer 34,5 %, VAT 15 %
#guard ({ good := .beer, adValoremBp := 3450, valueBase := .beforeTax, vatBp := 1500, roundOnce := true } : ExciseRule).dutyOn
  { good := .beer, amount := 10000 } {} == 10000 * 3450 * 10000 / ((10000 + 3450) * (10000 + 1500))
-- withVat takes the class rate of a 2.0 Vat
#guard (({ good := .financial, valueBase := .beforeTax } : ExciseRule).withVat fjVat1).vatBp == 0
#guard (({ good := .beer, valueBase := .beforeTax } : ExciseRule).withVat fjVat1).vatBp == 1500
-- net of VAT: 10 % of 1 150 / 1,15
#guard ({ good := .spirits, adValoremBp := 1000, valueBase := .netOfVat, vatBp := 1500 } : ExciseRule).dutyOn { good := .spirits, amount := 1150 } {} == 100
-- a 2.0 ExciseRate as a rule: the same duty
def rate20 : ExciseRate := { good := .cigarettes, perUnitNum := 3, perUnitDen := 2, adValoremBp := 1500, minNum := 4 }
#guard [0, 1, 999, 20000, 123456].all fun q => (ExciseRule.ofRate rate20).dutyOn { good := .cigarettes, amount := q * 7, quantity := q } {}
  == rate20.duty { good := .cigarettes, amount := q * 7, quantity := q }
-- per tonne (KZ/AM/GE fuel): 100 000 per tonne, 1 000 l of diesel at 840 kg/m³ (840 000 mg per litre) = 0,84 t
def dieselT : ExciseRule := { good := .diesel, perKgNum := 100000, perKgDen := 1000, mgPerUnit := 840000 }
#guard dieselT.dutyOn { good := .diesel, amount := 1, quantity := 1000000 } {} == 84000
#guard dieselT.dutyOn { good := .diesel, amount := 1, quantity := 1000000 } { massG := 850000 } == 85000   -- mass given
-- per kg of tobacco (TL US$ 50 per kg), 20 sticks of 0.7 g
#guard ({ good := .cigarettes, perKgNum := 50, mgPerUnit := 700 } : ExciseRule).dutyOn { good := .cigarettes, amount := 1, quantity := 20000 } {} == 0
#guard ({ good := .cigarettes, perKgNum := 5000, mgPerUnit := 700 } : ExciseRule).dutyOn { good := .cigarettes, amount := 1, quantity := 20000 } {} == 70
-- per hl and degree Plato (AT BierStG: 2,00 per hl and °P → 2/100 per litre and degree): 100 l at 12 °P = 24
def atBeer : ExciseRule := { good := .beer, perPlatoNum := 2, perPlatoDen := 100 }
#guard atBeer.dutyOn { good := .beer, amount := 1, quantity := 100000 } { platoBp := 1200 } == 24
-- sugar bands (per litre, from 5 g and 8 g per 100 ml) and sub-categories
def sugary : ExciseRule := { good := .nonAlcoholic, sub := "sweetenedDrinks", sugarBands := [(5000, 18, 1), (8000, 24, 1)] }
#guard sugary.dutyOn { good := .nonAlcoholic, amount := 1, quantity := 10000 } { sugarMg100ml := 4999 } == 0
#guard sugary.dutyOn { good := .nonAlcoholic, amount := 1, quantity := 10000 } { sugarMg100ml := 5000 } == 180
#guard sugary.dutyOn { good := .nonAlcoholic, amount := 1, quantity := 10000 } { sugarMg100ml := 9000 } == 240
def energy : ExciseRule := { good := .nonAlcoholic, sub := "energyDrinks", adValoremBp := 10000, valueBase := .beforeTax, vatBp := 500 }
#guard (exciseRuleCharges [sugary, energy] (hh "[{\"good\":\"nonAlcoholic\",\"amount\":2100,\"sub\":\"energyDrinks\"},{\"good\":\"nonAlcoholic\",\"amount\":500,\"quantity\":1000,\"sub\":\"sweetenedDrinks\",\"sugarMg100ml\":6000},{\"good\":\"nonAlcoholic\",\"amount\":500}]")).map (fun c => (c.event, c.due))
  == [("energyDrinks", 1000), ("sweetenedDrinks", 18)]
-- strength bands and origin (R4 MG beer: 12,5 % local, 50 % imported)
def mgLocal : ExciseRule := { good := .beer, adValoremBp := 1250, valueBase := .beforeTax, imported := some false }
def mgImp : ExciseRule := { mgLocal with adValoremBp := 5000, imported := some true }
#guard (exciseRuleCharges [mgLocal, mgImp] (hh "[{\"good\":\"beer\",\"amount\":1125}]")).map (·.due) == [125]
#guard (exciseRuleCharges [mgLocal, mgImp] (hh "[{\"good\":\"beer\",\"amount\":1500,\"imported\":true}]")).map (·.due) == [500]
#guard (exciseRuleCharges [mgLocal, mgImp] (hh "[{\"good\":\"beer\",\"amount\":1500}]" ",\"importedGoods\":[\"beer\"]")).map (·.due) == [500]
def weak : ExciseRule := { good := .wine, perUnitNum := 10, maxAbvBp := 1500 }
def strong : ExciseRule := { good := .wine, perUnitNum := 30, minAbvBp := 1500 }
#guard (exciseRuleCharges [weak, strong] (hh "[{\"good\":\"wine\",\"amount\":1,\"quantity\":1000,\"abvBp\":1500},{\"good\":\"wine\",\"amount\":1,\"quantity\":1000,\"abvBp\":1501}]")).map (·.due) == [10, 30]
-- charges: retail rules book the quantity (as 2.0 Excise.charges), the others the amount and the value taxed (as R4)
#guard (exciseRuleCharges [r4beer] (hh "[{\"good\":\"beer\",\"amount\":1000,\"quantity\":1000}]")).map (fun c => (c.base, c.relieved, c.due)) == [(1000, 564, 282)]
#guard (exciseRuleCharges [.ofRate rate20] (hh "[{\"good\":\"cigarettes\",\"amount\":7000,\"quantity\":1000}]")).map (fun c => (c.base, c.relieved, c.due))
  == ((Excise.charges ⟨[rate20]⟩ [{ good := .cigarettes, amount := 7000, quantity := 1000 }]).map (fun c => (c.base, c.relieved, c.due)))
-- firstOnly: the first matching rule only (2.0 Excise.charges)
#guard (exciseRuleCharges [weak, { weak with perUnitNum := 99 }] (hh "[{\"good\":\"wine\",\"amount\":1,\"quantity\":1000}]") (firstOnly := true)).map (·.due) == [10]
#guard (exciseRuleCharges [weak, { weak with perUnitNum := 99 }] (hh "[{\"good\":\"wine\",\"amount\":1,\"quantity\":1000}]")).map (·.due) == [10, 99]
-- rates changing during the year (TZ: re-rated from 1 July): an undated line is taken for the days in the window
def julyOn : ExciseRule := { good := .petrol, perUnitNum := 100, validFrom := "2025-07-01" }
def toJune : ExciseRule := { good := .petrol, perUnitNum := 80, validTo := "2025-07-01" }
#guard (exciseRuleCharges [toJune, julyOn] (hh "[{\"good\":\"petrol\",\"amount\":1,\"quantity\":365000}]")).map (fun c => (c.due, c.statute))
  == [(181 * 80, "; 181/365 of the year"), (184 * 100, "; 184/365 of the year")]
#guard (exciseRuleCharges [toJune, julyOn] (hh "[{\"good\":\"petrol\",\"amount\":1,\"quantity\":1000,\"date\":\"2025-06-30\"}]")).map (·.due) == [80]
#guard (exciseRuleCharges [toJune, julyOn] (hh "[{\"good\":\"petrol\",\"amount\":1,\"quantity\":1000,\"date\":\"2025-07-01\"}]")).map (·.due) == [100]
#guard (exciseRuleFamily "toy" [julyOn]).name == "5121 toy"

/-! ## CIT with floored and capped minimum taxes, rounding, taxable share -/
def cit30 : CorpRegime := { name := "IS", sched := Schedule.flat 3000 }
-- SN CGI art. 40 shape: 0,5 % of turnover capped at 5 000 000
def sn : CorpRule := { regime := cit30, minTax := some { bp := 50, cap := 5000000 }, step := 1000 }
#guard sn.tax BP { turnover := 100000000, profit := 0 } == 500000
#guard sn.tax BP { turnover := 2000000000, profit := 0 } == 5000000
#guard sn.tax BP { turnover := 2000000000, profit := 1234567 * 100 } == 37036800   -- 123 456 700 → 123 456 000 × 30 %
#guard sn.taxable BP { profit := 1234999 } == 1234000
-- TG art. 120 shape: 1 %, floor 20 000
def tg : CorpRule := { regime := cit30, minTax := some { bp := 100, floor := 20000 } }
#guard tg.tax BP { turnover := 1000000 } == 20000
#guard tg.tax BP { turnover := 5000000 } == 50000
-- MG shape: a fixed amount + 1 %
#guard ({ regime := cit30, minTax := some { fixed := 100000, bp := 100 } } : CorpRule).tax BP { turnover := 10000000 } == 200000
-- R4.MinTax's own guards
#guard (({ bp := 100, floor := 500000, cap := 5000000 } : MinimumTax).amount { turnover := 10000000 }) == 500000
#guard (({ bp := 100, floor := 500000, cap := 5000000 } : MinimumTax).amount { turnover := 100000000 }) == 1000000
#guard (({ bp := 100, floor := 500000, cap := 5000000 } : MinimumTax).amount { turnover := 1000000000 }) == 5000000
-- a bare regime is the 2.0 CIT (with its own minimum)
def withMin : CorpRegime := { cit30 with minBp := 100, minFixed := 7 }
#guard [0, 1, 999, 5000000].all fun p => (CorpRule.ofRegime withMin).tax BP { profit := p, turnover := 3 * p } == withMin.citTax { profit := p, turnover := 3 * p }
-- taxable share from the line (SA: "zakatShareBp" is the Saudi share, not taxed; QA "exemptShareBp")
def sa : CorpRule := { regime := { name := "CIT", sched := Schedule.flat 2000 }, shareKey := "zakatShareBp", shareComplement := true }
def saLine (extra : String) : CanonGlobal := gl ("{\"id\":\"c\",\"entity\":\"company\",\"company\":{\"profit\":1000000}" ++ extra ++ "}")
#guard (sa.citCharge (saLine ",\"zakatShareBp\":4000") "ITL art. 7").due == 120000
#guard (sa.citCharge (saLine ",\"zakatShareBp\":4000") "ITL art. 7").relieved == 600000
#guard (sa.citCharge (saLine "") "ITL art. 7").due == 200000
#guard (sa.citCharge (saLine ",\"zakatShareBp\":12000") "ITL art. 7").due == 0
#guard (({ sa with shareKey := "taxableShareBp", shareComplement := false } : CorpRule).citCharge (saLine ",\"taxableShareBp\":2500") "x").due == 50000
#guard ((sn.family "IS" "CGI" { rules := [] }).run [] (saLine "") []).map (·.due) == [300000]
#guard ((sn.family "IS" "CGI" { rules := [] }).run [] (hh "[]") []).isEmpty

/-! ## What a gift is made of (2.1.1; MA CGI art. 133-I-C-4°: 1,5 % on gifts of immovables, direct line, spouses, siblings) -/
def maRates : List (Relation × Int) := [(.child, 150), (.parent, 150), (.grandchild, 150), (.spouse, 150), (.sibling, 150)]
def maGift : PartDuty := { name := "droits d'enregistrement (donations)", rates := maRates, statute := "CGI art. 133-I-C-4°" }
def tr (recs : String) : CanonGlobal := hh "[]" (",\"transfers\":" ++ recs)
#guard (transfersX (tr "[{\"kind\":\"gift\",\"value\":1000000,\"relation\":\"child\",\"assetKind\":\"home\"}]")).map (·.2) == [{ assetKind := some .home }]
-- a gift of a home to a child: 1,5 % of 1 000 000
#guard (maGift.charges (tr "[{\"kind\":\"gift\",\"value\":1000000,\"relation\":\"child\",\"assetKind\":\"home\"}]")).map (fun c => (c.oecd.code, c.base, c.relieved, c.due, c.event))
  == [("4300", 1000000, 1000000, 15000, "gift 1")]
-- only the immovable part of a mixed gift; the assessed value where given
#guard (maGift.charges (tr "[{\"kind\":\"gift\",\"value\":1000000,\"relation\":\"sibling\",\"realPropertyValue\":400000}]")).map (·.due) == [6000]
#guard (maGift.charges (tr "[{\"kind\":\"gift\",\"value\":1000000,\"assessed\":800000,\"relation\":\"spouse\",\"assetKind\":\"land\"}]")).map (·.due) == [12000]
-- movables: charged nothing (a charge of 0); not known: no charge, listed by `unknown`
#guard (maGift.charges (tr "[{\"kind\":\"gift\",\"value\":1000000,\"relation\":\"child\",\"assetKind\":\"deposits\"}]")).map (·.due) == [0]
#guard (maGift.charges (tr "[{\"kind\":\"gift\",\"value\":1000000,\"relation\":\"child\"}]")).isEmpty
#guard (maGift.unknown (tr "[{\"kind\":\"gift\",\"value\":1000000,\"relation\":\"child\"}]")).length == 1
-- relations not listed, and inheritances (gifts only by default), are outside it
#guard (maGift.charges (tr "[{\"kind\":\"gift\",\"value\":1000000,\"relation\":\"unrelated\",\"assetKind\":\"home\"},{\"kind\":\"inheritance\",\"value\":1000000,\"relation\":\"child\",\"assetKind\":\"home\"}]")).isEmpty
#guard (maGift.unknown (tr "[{\"kind\":\"gift\",\"value\":1,\"relation\":\"unrelated\"}]")).isEmpty
#guard (({ maGift with inheritances := true } : PartDuty).charges (tr "[{\"kind\":\"inheritance\",\"value\":1000000,\"relation\":\"child\",\"assetKind\":\"home\"}]")).map (fun c => (c.due, c.event)) == [(15000, "inheritance 1")]
#guard realPropertyPart { kind := .gift, value := 500, relation := .child } { realPropertyValue := 900 } == some 500
-- a part fed to the 2.0 InheritanceTax
#guard (Transfer.restrict { kind := .gift, value := 1000000, assessed := 2000000, relation := .child, homeValue := 700000 } 400000).statutoryValue == 400000
#guard (maGift.family).name == "4300 droits d'enregistrement (donations)"

/-! ## 2.2.0: a company-only entity bears no PIT charge (the CH 1.x minimum tax of 24 was booked for companies) -/
def toyLine : Json := Json.mkObj [("incomeTax", Json.num 24), ("employeeSocial", Json.num 0), ("benefits", Json.num 5)]
def toyPit : GlobalModel := { code := "ZZ", currency := "ZZD", pit := fun _ _ => toyLine }
def toyWithCit : GlobalModel := toyPit.withFamily { name := "1200 toy", covers := [.cit], run := fun _ g _ => if g.entity == .company then [flatCharge .cit "CIT" 100] else [] }
def coOnly : CanonGlobal := gl "{\"id\":\"c\",\"entity\":\"company\",\"company\":{\"profit\":1000}}"
#guard coOnly.companyOnly
#guard !({ id := "x", household := { id := "x" } } : CanonGlobal).companyOnly
#guard ({ id := "x", household := { id := "x" }, entity := .company } : CanonGlobal).companyOnly
-- company-only: no PIT charge, no 1.x benefits; the families still run
#guard (toyPit.computeGlobal [] coOnly).charges.isEmpty
#guard (toyPit.computeGlobal [] coOnly).benefits == 0
#guard ((toyWithCit.computeGlobal [] coOnly).charges.map (fun c => (c.tax, c.due))) == [("CIT", 100)]
#guard (toyWithCit.computeGlobal [] coOnly).total == 100
-- the 1.x line itself is still reported under "pit"
#guard jInt (toyPit.computeGlobal [] coOnly).pit "incomeTax" == 24
-- a household entity: unchanged (the 1.x lines are charges, benefits from the line)
#guard ((toyPit.computeGlobal [] (hh "[]")).charges.map (fun c => (c.tax, c.due))) == [("incomeTax", 24), ("localIncomeTax", 0), ("employeeSocial", 0)]
#guard (toyPit.computeGlobal [] (hh "[]")).benefits == 5
#guard !(hh "[]").companyOnly
-- a company line that does give a household keeps it (not company-only)
#guard !(gl "{\"id\":\"c\",\"entity\":\"company\",\"household\":{\"id\":\"c\",\"adults\":[{\"age\":40}]}}").companyOnly
#guard ((toyWithCit.computeGlobal [] (gl "{\"id\":\"c\",\"entity\":\"company\",\"household\":{\"id\":\"c\",\"adults\":[{\"age\":40}]}}")).charges.map (·.tax)) == ["incomeTax", "localIncomeTax", "employeeSocial", "CIT"]

/-! ## 2.3.0 (R-FT2-1): withholding no rule computes is listed as grade C, not booked as a computed 0 -/
def whtPart : Wht := { name := "WHT", rules := [{ kind := .dividend, rateBp := 1000, statute := "s. 1" },
                                                 WhtRule.zero .interest "s. 2: interest paid abroad exempt"] }
def toyWht : GlobalModel := toyWithCit.withFamily whtPart.family
def payLine (pays : String) : CanonGlobal :=
  gl ("{\"id\":\"c\",\"entity\":\"company\",\"company\":{\"profit\":1000,\"paymentsAbroad\":" ++ pays ++ "}}")
def divInt : CanonGlobal := payLine "[{\"kind\":\"dividend\",\"amount\":500},{\"kind\":\"interest\",\"amount\":300}]"
def roy : CanonGlobal := payLine "[{\"kind\":\"royalty\",\"amount\":500}]"
def gradeC (code : String) (i : Nat) (k : String) : String :=
  s!"{code} withholding on payment {i} ({k}) abroad: no rule read (grade C)"
-- a rule computes (10 % of 500); a cited statutory zero books a covered 0 with its citation; nothing listed
#guard ((toyWht.computeGlobal [] divInt).charges.map (fun c => (c.oecd.code, c.event, c.due, c.statute)))
  == [("1200", "year", 100, ""), ("1200", "payment 1 (dividend)", 50, "s. 1"),
      ("1200", "payment 2 (interest)", 0, "s. 2: interest paid abroad exempt")]
#guard (toyWht.computeGlobal [] divInt).unsupported.isEmpty
-- no rule for royalties: the 0 placeholder is dropped and the payment is listed as grade C
#guard (whtPart.charges roy.company).map (fun c => (c.due, c.statute)) == [(0, "no withholding rule")]
#guard ((toyWht.computeGlobal [] roy).charges.map (·.tax)) == ["CIT"]
#guard (toyWht.computeGlobal [] roy).unsupported == [gradeC "1200" 1 "royalty"]
#guard (toyWht.computeGlobal [] roy).total == 100
-- a recipient who is an individual: the heading of its charge, 1100
#guard (toyWht.computeGlobal [] (payLine "[{\"kind\":\"royalty\",\"amount\":500,\"toCompany\":false}]")).unsupported
  == [gradeC "1100" 1 "royalty"]
-- a stake condition not met is a payment no rule matches
def whtStake : Wht := { rules := [{ kind := .dividend, minStakeBp := 1000, rateBp := 0, statute := "s. 3 participation" }] }
#guard ((toyWithCit.withFamily whtStake.family).computeGlobal []
    (payLine "[{\"kind\":\"dividend\",\"amount\":9,\"stakeBp\":2500},{\"kind\":\"dividend\",\"amount\":9,\"stakeBp\":500}]")).unsupported
  == [gradeC "1200" 2 "dividend"]
-- no withholding family at all: every payment abroad listed, after the model's own entries
def toyOwn : GlobalModel := { toyWithCit with unsupported := fun _ _ => ["own entry"] }
#guard (toyOwn.computeGlobal [] (payLine "[{\"kind\":\"dividend\",\"amount\":500},{\"kind\":\"services\",\"amount\":10}]")).unsupported
  == ["own entry", gradeC "1200" 1 "dividend", gradeC "1200" 2 "services"]
-- a model that hands a filtered list to Wht.charges (renumbered events, as CL): computed kinds are not listed
def clRun (_ : List String) (g : CanonGlobal) (_ : List Charge) : List Charge :=
  whtPart.charges { g.company with paymentsAbroad := g.company.paymentsAbroad.filter (·.kind != .royalty) }
def clLike : GlobalModel := toyWithCit.withFamily { name := "cl", covers := [.cit], run := clRun }
#guard (clLike.computeGlobal [] (payLine "[{\"kind\":\"royalty\",\"amount\":1},{\"kind\":\"dividend\",\"amount\":500},{\"kind\":\"interest\",\"amount\":7}]")).unsupported
  == [gradeC "1200" 1 "royalty"]
-- no payment abroad, or a household entity: nothing changes
#guard (toyOwn.computeGlobal [] coOnly).unsupported == ["own entry"]
#guard (toyOwn.computeGlobal [] (hh "[]")).unsupported == ["own entry"]
#guard (WhtRead.kept (hh "[]") (whtPart.charges roy.company)).length == 1
#guard (WhtRead.kept roy (whtPart.charges roy.company)).isEmpty
-- helpers: a cited absence for several kinds, as a family of its own
def noneWht : Wht := { name := "none", rules := Wht.zeroOn [.dividend, .interest, .royalty, .services] "Act s. 5: no withholding" }
#guard ((toyWithCit.withFamily noneWht.family).computeGlobal [] roy).unsupported.isEmpty
#guard (((toyWithCit.withFamily noneWht.family).computeGlobal [] roy).charges.map (fun c => (c.due, c.statute)))
  == [(100, ""), (0, "Act s. 5: no withholding")]
#guard noneWht.family.covers.map (·.code) == ["1200"]
#guard (noneWht.family.run [] (hh "[]") []).isEmpty

/-! ## 2.3.0 (R1 Europe pass 4): the small-company test on employees as well as turnover (LT PMĮ 5 str. 2 d.) -/
def ltCit : CorpRegime := { name := "Pelno mokestis", sched := Schedule.flat 1600, smallSched := Schedule.flat 600,
                            smallTurnover := 300000, smallEmployees := 10 }
def ltCo (to : Int) (emp : Nat) : Company := { turnover := to, profit := 100000, employees := emp }
#guard ltCit.isSmall (ltCo 300000 10)
#guard !ltCit.isSmall (ltCo 300000 11)          -- 11 employees: the 16 % schedule
#guard !ltCit.isSmall (ltCo 300001 3)           -- revenue above 300 000: the 16 % schedule
#guard ltCit.citTax (ltCo 250000 8) == 6000
#guard ltCit.citTax (ltCo 250000 12) == 16000
-- without an employee limit (the default −1): the turnover test of 2.2, whatever the employees
#guard ({ ltCit with smallEmployees := -1 } : CorpRegime).isSmall (ltCo 250000 500)
#guard !({ ltCit with smallEmployees := -1, smallTurnover := -1 } : CorpRegime).isSmall (ltCo 0 0)
-- an employee test alone (no turnover limit)
#guard ({ ltCit with smallTurnover := -1 } : CorpRegime).isSmall (ltCo 99999999 10)
#guard !({ ltCit with smallTurnover := -1 } : CorpRegime).isSmall (ltCo 1 11)
-- read from the company line's "employees"; CorpRule (2.1) uses the same test
#guard (CorpRule.ofRegime ltCit).tax 10000 (gl "{\"id\":\"c\",\"entity\":\"company\",\"company\":{\"turnover\":250000,\"profit\":100000,\"employees\":8}}").company == 6000

/-! ## 2.4.0 (R3-S4-1): excise rate chosen by the retail unit price -/
-- MM Union Taxation Law 2025 s. 11: cigarettes 14 / 27 / 30 kyats a stick for a pack of 20 sold up to 800, 801-1,100
-- and above 1,100 kyats (price of a pack of 20 sticks: `priceQty := 20000`)
def mmCig1 : ExciseRule :=
  { good := .cigarettes, name := "specific goods tax", perUnitNum := 14, priceQty := 20000,
    maxUnitPrice := 800, statute := "Union Taxation Law 2025 s. 11" }
def mmCig2 : ExciseRule := { mmCig1 with perUnitNum := 27, minUnitPrice := 800, maxUnitPrice := 1100 }
def mmCig3 : ExciseRule := { mmCig1 with perUnitNum := 30, minUnitPrice := 1100, maxUnitPrice := -1 }
def mmCig : List ExciseRule := [mmCig1, mmCig2, mmCig3]
def cigLine (amount packs : Int) (extra : String := "") : String :=
  "[{\"good\":\"cigarettes\",\"amount\":" ++ toString amount ++ ",\"quantity\":" ++ toString (packs * 20000) ++ extra ++ "}]"
def dues (rs : List ExciseRule) (g : CanonGlobal) : List Int := (exciseRuleCharges rs g).map (·.due)
#guard dues mmCig (hh (cigLine 8000 10)) == [2800]          -- 10 packs at 800: 200 sticks × 14
#guard dues mmCig (hh (cigLine 8005 10)) == [5400]          -- 800.50 a pack is above 800 (exact, no rounded unit price)
#guard dues mmCig (hh (cigLine 11000 10)) == [5400]
#guard dues mmCig (hh (cigLine 11001 10)) == [6000]
#guard dues mmCig (hh (cigLine 500 1)) == [280]
#guard dues mmCig (hh "[{\"good\":\"cigarettes\",\"amount\":8000}]") == []   -- no quantity: in no tier
-- every price falls in exactly one tier
#guard (List.range 3000).all fun p =>
  (mmCig.filter fun r => r.appliesTo 2025 { good := .cigarettes, amount := p, quantity := 20000 } {}).length == 1
-- liquor's top tier: 60 % of the price where the price per litre is above 28,600 (a 0.7 l bottle at 21,000 = 30,000 a litre)
def mmLiquorTop : ExciseRule := { good := .spirits, adValoremBp := 6000, minUnitPrice := 28600, statute := "UTL 2025 s. 11" }
#guard dues [mmLiquorTop] (hh "[{\"good\":\"spirits\",\"amount\":21000,\"quantity\":700}]") == [12600]
#guard dues [mmLiquorTop] (hh "[{\"good\":\"spirits\",\"amount\":20000,\"quantity\":700}]") == []   -- 28,571 a litre
-- a rule without a tier is unchanged (2.1-2.3 selection)
#guard !r4beer.hasPriceTier && mmLiquorTop.hasPriceTier
#guard (exciseRuleCharges [r4beer] (hh "[{\"good\":\"beer\",\"amount\":1180,\"quantity\":1000}]")).map (·.due) == [333]
#guard mmCig1.unitPrice { good := .cigarettes, amount := 8005, quantity := 200000 } {} == 800

-- EG (R5/eg, VAT Law 67/2016 Table أولاً 1/ب/3 as replaced by Law 157/2025, from 18/7/2025): 50 % of the consumer price
-- + 500 pt a pack (local, pack ≤ EGP 48), 750 pt (local 48-69, or imported ≤ 69), 800 pt (above 69). EG's own code
-- (EgGlobal.Consumption.cigTax) verbatim, against the same tax as ExciseRules with price tiers in piastres:
namespace EgMirror
def cigPeriod (d : Nat) : Nat := if d < 198 then 0 else if d < 308 then 1 else 2
def cigLimits : Nat → Int × Int
  | 0 => (3472, 5040) | 1 => (4800, 6900) | _ => (5376, 7728)
def cigAmounts : Nat → Int × Int × Int
  | 0 => (450, 700, 750) | _ => (500, 750, 800)
def cigPerPack (p : Nat) (packPt : Int) (imported : Bool) : Int :=
  let (lo, hi) := cigLimits p
  let (a1, a2, a3) := cigAmounts p
  if !imported && packPt ≤ lo then a1 else if packPt ≤ hi then a2 else a3
def cigTax (amount quantity : Int) (imported : Bool) (day : Option Nat) : Int :=
  let adv := divR .down (pos amount * 5000) BP
  if quantity ≤ 0 then adv else
  let packPt := divR .down (pos amount * 100 * 20000) quantity
  let specPt := match day with
    | some d => divR .down (quantity * cigPerPack (cigPeriod d) packPt imported) 20000
    | none => divR .down (quantity * (cigPerPack 0 packPt imported * 198 + cigPerPack 1 packPt imported * 110
        + cigPerPack 2 packPt imported * 57)) (20000 * 365)
  adv + divR .down specPt 100
end EgMirror
def egPack : ExciseRule := { good := .cigarettes, priceQty := 20000, priceDen := 100, perUnitDen := 2000 }  -- pt a pack → EGP a stick
def egRules : List ExciseRule :=
  [{ good := .cigarettes, adValoremBp := 5000 },
   { egPack with perUnitNum := 500, imported := some false, maxUnitPrice := 4800 },
   { egPack with perUnitNum := 750, imported := some false, minUnitPrice := 4800, maxUnitPrice := 6900 },
   { egPack with perUnitNum := 750, imported := some true, maxUnitPrice := 6900 },
   { egPack with perUnitNum := 800, minUnitPrice := 6900 }]
def egKernel (amount q : Int) (imp : Bool) : Int :=
  let s : Spend := { good := .cigarettes, amount, quantity := q }
  let x : SpendX := { imported := imp, date := "2025-08-01" }
  isum ((egRules.filter (·.appliesTo 2025 s x)).map (·.duty 2025 s x))
-- identical on 8,000 lines (EGP 0-799 for 1, 2, 4, 5 or 10 packs: pack prices to the piastre), local and imported
#guard (List.range 800).all fun k => [1, 2, 4, 5, 10].all fun n => [false, true].all fun imp =>
  egKernel k (n * 20000) imp == EgMirror.cigTax k (n * 20000) imp (some 212)
#guard egKernel 480 200000 false == 240 + 50 && egKernel 481 200000 false == 240 + 75
#guard egKernel 690 200000 true == 345 + 75 && egKernel 691 200000 true == 345 + 80
-- the whole path: origin from the line
#guard dues egRules (hh (cigLine 600 10 ",\"imported\":true,\"date\":\"2025-08-01\"")) == [300, 75]

/-! ## 2.4.0: floor area (`"areaM2"`), rate tables on a quantity, a tax per m² -/
def areaG : CanonGlobal := hh "[]" ",\"assets\":[{\"kind\":\"land\",\"value\":1,\"areaM2\":1250},{\"kind\":\"home\",\"value\":5,\"areaM2\":80},{\"kind\":\"land\",\"value\":1}]"
#guard (assetsArea areaG).map (·.2) == [1250, 80, 0]
#guard assetAreaM2 areaG 1 == 80 && assetAreaM2 areaG 7 == 0
-- R5 GE land tax (GeGlobal/Property.lean `landCharges`, verbatim) and the same as an AreaTax: identical charges
def geLandTaxM2 (area : Int) : Int := divR .down (pos area * 36) 100
def geLandAreaOf (g : CanonGlobal) (i : Nat) : Int := intField ((arrField g.raw "assets").toList.getD i Lean.Json.null) "areaM2"
def geLandCharges (g : CanonGlobal) : List Charge :=
  (g.assets.zipIdx.filter fun (a, i) => a.kind == .land && geLandAreaOf g i > 0).map fun (_, i) =>
    charge .propertyRecurrent "ქონების გადასახადი მიწაზე (land tax)" (geLandAreaOf g i) pos geLandTaxM2 (event := s!"land {i + 1}")
      (level := .local) (statute := "Tax Code art. 203, 204(2) (GEL 0.24 per m² × territorial coefficient, maximum 1.5)")
def geLand : AreaTax :=
  { name := "ქონების გადასახადი მიწაზე (land tax)", kinds := [.land], table := QtyTable.perUnit 36 100,
    event := "land", statute := "Tax Code art. 203, 204(2) (GEL 0.24 per m² × territorial coefficient, maximum 1.5)" }
#guard (geLand.charges areaG).map Charge.toJson == (geLandCharges areaG).map Charge.toJson
#guard (geLand.charges areaG).map (·.due) == [450]
#guard geLand.unknown areaG == ["4100 ქონების გადასახადი მიწაზე (land tax): asset 3 (land) has no areaM2 (grade C)"]
#guard geLand.family.covers.map (·.code) == ["4100"]
-- R5 AZ land tax: per 100 m² up to 1 ha and above (two marginal steps, rounded once), AZ's own formula
def azLand (r1 r2 area : Int) : Int := divR .down (min (pos area) 10000 * r1 + pos (area - 10000) * r2) 10000
#guard ([(6, 10), (2, 5), (100, 300)] : List (Int × Int)).all fun (r1, r2) => (List.range 40).all fun k =>
  ({ steps := [(0, r1), (10000, r2)], den := 10000 } : QtyTable).amount ((k : Int) * 997) == azLand r1 r2 ((k : Int) * 997)
-- R5 AZ dwellings: a rate per m² above 30 m²; DZ 15.60 DA per m²
#guard (List.range 300).all fun a => ({ steps := [(30, 28)], den := 100 } : QtyTable).amount a == divR .down (pos ((a : Int) - 30) * 28) 100
#guard (List.range 300).all fun a => (QtyTable.perUnit 1560 100).amount a == divR .down (pos (a : Int) * 1560) 100
-- a table by kind: DZ dwellings 1 560 c/m², commercial 3 114 c/m²
def dzTf : AreaTax :=
  { name := "الرسم العقاري", kinds := [.home, .realEstate], table := QtyTable.perUnit 3114 100,
    tableFor := fun a => if a.kind == .home then some (QtyTable.perUnit 1560 100) else none, event := "property" }
#guard (dzTf.charges areaG).map (fun c => (c.event, c.due)) == [("property 2", 1248)]
-- R4 vignettes ("up to c CV: a", R4Common.VehTariff) as a QtyTable: the same amounts
def r4Amount (bands : List (Int × Int)) (top hp : Int) : Int :=
  match bands.find? (fun b => hp ≤ b.1) with | some b => b.2 | none => top
def bjT : List (Int × Int) := [(7, 20000), (10, 30000), (15, 40000)]
def neT : List (Int × Int) := [(2, 5000), (6, 15000), (11, 20000), (14, 25000), (19, 35000), (24, 45000)]
#guard (List.range 60).all fun hp => (QtyTable.ofCeilings bjT 60000).amount hp == r4Amount bjT 60000 hp
#guard (List.range 60).all fun hp => (QtyTable.ofCeilings neT 60000).amount hp == r4Amount neT 60000 hp
-- started steps: per started 100 cm³
#guard ({ step := 100 } : QtyTable).counted 1598 == 1600 && ({ step := 100 } : QtyTable).counted 1600 == 1600

/-! ## 2.4.0 (R1 Europe pass 7): motor-vehicle taxes from vehicle attributes (5200) -/
-- DE KraftStG § 9 (1) Nr. 2 c (cars first registered from 2021): per started 100 cm³ 2,00 € (petrol) / 9,50 € (diesel),
-- plus per g CO2/km above 95: 2,00 € to 115, 2,20 to 135, 2,50 to 155, 2,90 to 175, 3,40 to 195, 4,00 above
def deCo2 : QtyTable := { steps := [(95, 200), (115, 220), (135, 250), (155, 290), (175, 340), (195, 400)], den := 100 }
def dePetrol : VehicleTax :=
  { name := "Kraftfahrzeugsteuer", kinds := ["car"], fuels := [.petrol],
    parts := [(.engineCcm, { step := 100, steps := [(0, 2)], den := 100 }), (.co2GKm, deCo2)], statute := "KraftStG § 9 (1) Nr. 2 c" }
def deDiesel : VehicleTax :=
  { dePetrol with
    fuels := [.diesel],
    parts := [(.engineCcm, { step := 100, steps := [(0, 950)], den := 10000 }), (.co2GKm, deCo2)] }
def deElectric : VehicleTax :=
  { name := "Kraftfahrzeugsteuer", kinds := ["car"], fuels := [.electric],
    statute := "KraftStG § 3d (electric cars exempt)" }
def deKfz : List VehicleTax := [dePetrol, deDiesel, deElectric]
def veh (assets : String) (extra : String := "") : CanonGlobal := hh "[]" (",\"assets\":[" ++ assets ++ "]" ++ extra)
def golf : String := "{\"kind\":\"vehicle\",\"value\":25000,\"engineCcm\":1598,\"co2GKm\":140,\"fuel\":\"petrol\",\"firstRegYear\":2023}"
def passat : String := "{\"kind\":\"vehicle\",\"value\":30000,\"engineCcm\":1968,\"co2GKm\":130,\"fuel\":\"diesel\",\"firstRegYear\":2022}"
def ev : String := "{\"kind\":\"vehicle\",\"value\":40000,\"fuel\":\"electric\",\"firstRegYear\":2025}"
#guard (veh (golf ++ "," ++ passat)).vehicles.map (fun v => (v.kind, v.engineCcm, v.co2GKm, v.fuel, v.value, v.source))
  == [("car", 1598, 140, VehicleFuel.petrol, 25000, "asset 1"), ("car", 1968, 130, VehicleFuel.diesel, 30000, "asset 2")]
-- 16 × 2,00 + (20 × 2,00 + 20 × 2,20 + 5 × 2,50 = 96,50 → 96) = 128; diesel 20 × 9,50 + 20 × 2,00 + 15 × 2,20 = 263
#guard (vehicleTaxCharges deKfz (veh (golf ++ "," ++ passat ++ "," ++ ev))).map (·.due) == [128, 263, 0]
#guard (vehicleTaxCharges deKfz (veh golf)).map (fun c => (c.oecd.code, c.event, c.base, c.relieved, c.due, c.statute))
  == [("5200", "vehicle 1 (asset 1)", 1598, 1600, 128, "KraftStG § 9 (1) Nr. 2 c")]
#guard (vehicleTaxFamily "Kraftfahrzeugsteuer" deKfz).covers.map (·.code) == ["5200"]
-- an attribute the tax needs is not given: no charge, a grade-C line
def golfNoCo2 : String := "{\"kind\":\"vehicle\",\"value\":1,\"engineCcm\":1598,\"fuel\":\"petrol\"}"
#guard (vehicleTaxCharges deKfz (veh golfNoCo2)).isEmpty
#guard vehicleTaxUnknown "Kfz-Steuer" deKfz (veh golfNoCo2) == ["5200 Kfz-Steuer: vehicle 1 (asset 1, car): co2GKm not given (grade C)"]
#guard vehicleTaxUnknown "Kfz-Steuer" deKfz (veh "{\"kind\":\"vehicle\",\"value\":1,\"engineCcm\":1598,\"co2GKm\":140}")
  == ["5200 Kfz-Steuer: vehicle 1 (asset 1, car): fuel not given (grade C)"]
#guard vehicleTaxUnknown "Kfz-Steuer" deKfz (veh (golf ++ "," ++ ev)) == []
-- no rule selects a vehicle: listed only by vehicleTaxUnmatched (a cited zero rule covers an exemption)
#guard vehicleTaxUnmatched "Kfz-Steuer" [dePetrol, deDiesel] (veh ev) == ["5200 Kfz-Steuer: vehicle 1 (asset 1, car, electric): no rule for the vehicle (grade C)"]
#guard vehicleTaxUnmatched "Kfz-Steuer" deKfz (veh ev) == []
-- held 6 months: half the year's amount, noted in the statute
#guard (vehicleTaxCharges deKfz (veh "{\"kind\":\"vehicle\",\"value\":1,\"engineCcm\":1598,\"co2GKm\":140,\"fuel\":\"petrol\",\"months\":6}")).map (fun c => (c.due, c.statute))
  == [(64, "KraftStG § 9 (1) Nr. 2 c; 6/12 of the year")]
-- a CO2 band table ("up to c g/km: a", IE motor-tax shape)
def ieBands : QtyTable := QtyTable.ofCeilings [(50, 120), (80, 140), (100, 170), (110, 180), (120, 190), (130, 200), (140, 210),
  (155, 280), (170, 390), (190, 570), (225, 750)] 1200
def ieMotor : VehicleTax := { name := "motor tax", kinds := ["car"], parts := [(.co2GKm, ieBands)] }
#guard ([0, 50, 51, 120, 121, 225, 226, 400] : List Int).map ieBands.amount == [120, 120, 140, 190, 200, 750, 1200, 1200]
-- age factors and a local multiplier (kW table; 7 years old: 80 %; multiplier 150 %), within a minimum and a cap
def kwTax : VehicleTax :=
  { name := "vehicle tax", parts := [(.engineKw, QtyTable.ofCeilings [(55, 300), (75, 500), (100, 700)] 900)],
    ageFactors := [(0, 10000), (5, 8000), (10, 6000)], multiplierBp := 15000, minAmount := 100, maxAmount := 1000, level := .local }
def kwCar (kw yr : Nat) : CanonGlobal :=
  veh ("{\"kind\":\"vehicle\",\"value\":1,\"engineKw\":" ++ toString kw ++ ",\"firstRegYear\":" ++ toString yr ++ "}")
#guard (vehicleTaxCharges [kwTax] (kwCar 70 2018)).map (·.due) == [600]     -- 500 × 0.8 × 1.5
#guard (vehicleTaxCharges [kwTax] (kwCar 70 2024)).map (·.due) == [750]     -- 500 × 1.0 × 1.5
#guard (vehicleTaxCharges [kwTax] (kwCar 120 2024)).map (·.due) == [1000]   -- 900 × 1.5 = 1350, cap 1000
#guard (vehicleTaxCharges [{ kwTax with multiplierBp := 1000 }] (kwCar 40 2010)).map (·.due) == [100]  -- 18, minimum 100
#guard (vehicleTaxCharges [kwTax] (kwCar 70 0)).isEmpty                    -- age not given
-- a registration tax: only a vehicle registered in the tax year (first registration this year, or "registeredThisYear")
def regTax : VehicleTax := { name := "registration tax", occasion := .registration, parts := [(.value, QtyTable.perUnit 1000 10000)] }
#guard (vehicleTaxCharges [regTax] (veh (golf ++ "," ++ ev))).map (fun c => (c.event, c.due)) == [("vehicle 2 (asset 2)", 4000)]
#guard (vehicleTaxCharges [regTax] (veh "{\"kind\":\"vehicle\",\"value\":9000,\"firstRegYear\":2019,\"registeredThisYear\":true}")).map (·.due) == [900]
-- attribute ranges (`when`) and `firstOnly`: motorcycles above 125 cm³ only
def moto : VehicleTax := { name := "m", kinds := ["motorcycle"], when := [(.engineCcm, 125, 100000)], fixed := 50 }
#guard (vehicleTaxCharges [moto] (veh "{\"kind\":\"vehicle\",\"value\":1,\"vehicleKind\":\"motorcycle\",\"engineCcm\":125},{\"kind\":\"vehicle\",\"value\":1,\"vehicleKind\":\"motorcycle\",\"engineCcm\":600}")).map (·.event) == ["vehicle 2 (asset 2)"]
#guard (vehicleTaxCharges [dePetrol, { dePetrol with name := "second" }] (veh golf) (firstOnly := true)).length == 1
-- a company's fleet (`company.vehicles`) and R4's fiscal horsepower (the R4 vignette's figures, R4Common.Vehicle)
def fleet : CanonGlobal := gl "{\"id\":\"c\",\"entity\":\"company\",\"company\":{\"profit\":1,\"vehicles\":[{\"kind\":\"van\",\"massKg\":2800,\"fuel\":\"diesel\",\"fiscalHp\":11},{\"fiscalHp\":7}]}}"
#guard fleet.vehicles.map (fun v => (v.kind, v.massKg, v.fiscalHp, v.source)) == [("van", 2800, 11, "company vehicle 1"), ("car", -1, 7, "company vehicle 2")]
def bjTvm : VehicleTax := { name := "TVM", parts := [(.fiscalHp, QtyTable.ofCeilings bjT 60000)] }
#guard (vehicleTaxCharges [bjTvm] fleet).map (·.due) == [40000, 20000]
#guard (vehicleTaxCharges [bjTvm] (veh "{\"kind\":\"vehicle\",\"value\":1,\"fiscalHp\":11},{\"kind\":\"home\",\"value\":1},{\"kind\":\"vehicle\",\"value\":1,\"fiscalHp\":7}")).map (fun c => (c.event, c.due))
  == [("vehicle 1 (asset 1)", 40000), ("vehicle 2 (asset 3)", 20000)]
-- a household line's "company" object is not read for vehicles (companies only)
#guard (hh "[]" ",\"company\":{\"vehicles\":[{\"fiscalHp\":7}]}").vehicles.isEmpty
-- no vehicle, no change: the family books nothing and every charge and total stay as they were
def toyVeh : GlobalModel := toyWithCit.withFamily (vehicleTaxFamily "Kfz" deKfz)
#guard (hh "[]").vehicles.isEmpty && areaG.vehicles.isEmpty
#guard ((toyVeh.computeGlobal [] areaG).charges.map Charge.toJson) == ((toyWithCit.computeGlobal [] areaG).charges.map Charge.toJson)
#guard (toyVeh.computeGlobal [] coOnly).total == (toyWithCit.computeGlobal [] coOnly).total
#guard ((toyVeh.computeGlobal [] (veh golf)).charges.map (·.due)) == [24, 0, 0, 128]

/-! ## 2.4.0 (R1 Europe pass 8): withholding conditional on the recipient's state -/
-- ES TRLIRNR art. 25.1 a): 19 % to EU/EEA residents, else 24 %; an absent fact: the general rate, and a note
def esWht : StateWht := { name := "IRNR", rules := [
  { rule := { kind := .interest, rateBp := 1900, statute := "TRLIRNR art. 25.1 a) (EU/EEA)" }, tests := [.euEea true], ifUnknown := .general },
  StateRule.plain { kind := .interest, rateBp := 2400, statute := "TRLIRNR art. 25.1 a)" }] }
def intTo (facts : String) : CanonGlobal := payLine ("[{\"kind\":\"interest\",\"amount\":1000" ++ facts ++ "}]")
#guard (esWht.charges (intTo ",\"recipientState\":\"DE\",\"euEea\":true")).map (fun c => (c.due, c.statute)) == [(190, "TRLIRNR art. 25.1 a) (EU/EEA)")]
#guard (esWht.charges (intTo ",\"recipientState\":\"US\",\"euEea\":false")).map (·.due) == [240]
#guard (esWht.charges (intTo "")).map (·.due) == [240]
#guard esWht.notes (intTo "") == ["1200 withholding on payment 1 (interest): conditional rate 1900 bp (TRLIRNR art. 25.1 a) (EU/EEA)) not tested: euEea not given; 2400 bp booked (TRLIRNR art. 25.1 a))"]
#guard esWht.notes (intTo ",\"euEea\":false") == []
#guard paymentXOf (intTo ",\"recipientState\":\"NL\",\"lowTax\":false,\"treaty\":true") 0
  == { recipientState := "NL", lowTax := some false, treaty := some true }
-- CZ ZDP § 36 (1) c): 35 % unless the recipient is resident in a treaty or information-exchange state (presumed until shown)
def czWht : StateWht := { name := "srážková daň", rules := [
  { rule := { kind := .dividend, rateBp := 3500, statute := "ZDP § 36 (1) c)" }, tests := [.treaty false], ifUnknown := .presume },
  StateRule.plain { kind := .dividend, rateBp := 1500, statute := "ZDP § 36 (2) a)" }] }
def divTo (facts : String) : CanonGlobal := payLine ("[{\"kind\":\"dividend\",\"amount\":1000" ++ facts ++ "}]")
#guard (czWht.charges (divTo "")).map (fun c => (c.due, c.statute)) == [(350, "ZDP § 36 (1) c)" ++ presumedNote)]
#guard (czWht.charges (divTo ",\"treaty\":true")).map (fun c => (c.due, c.statute)) == [(150, "ZDP § 36 (2) a)")]
#guard (czWht.charges (divTo ",\"treaty\":false")).map (fun c => (c.due, c.statute)) == [(350, "ZDP § 36 (1) c)")]
-- FR CGI 182 B III: 75 % to a non-cooperative state (the model's list); state not given: no rate (grade C)
def frEtnc : List String := ["AI", "BS", "FJ", "GU", "PA", "PW", "AS", "VI", "VU", "WS", "TT", "RU"]
def frWht : StateWht := { name := "retenue à la source", rules := [
  { rule := { kind := .royalty, rateBp := 7500, statute := "CGI 182 B III" }, tests := [.inStates frEtnc], ifUnknown := .gradeC },
  StateRule.plain { kind := .royalty, rateBp := 2500, statute := "CGI 182 B I" }] }
def royTo (facts : String) : CanonGlobal := payLine ("[{\"kind\":\"royalty\",\"amount\":1000" ++ facts ++ "}]")
#guard (frWht.charges (royTo ",\"recipientState\":\"PA\"")).map (·.due) == [750]
#guard (frWht.charges (royTo ",\"recipientState\":\"DE\"")).map (·.due) == [250]
#guard (frWht.charges (royTo "")).map (fun c => (c.due, c.statute)) == [(0, noWhtRule)]
#guard frWht.notes (royTo "") == ["1200 withholding on payment 1 (royalty): the rate depends on recipientState, not given (CGI 182 B III)"]
-- through the master equation: the placeholder is dropped and the payment listed as grade C (2.3.0)
def toyFr : GlobalModel := { toyWithCit.withFamily frWht.family with unsupported := fun _ g => frWht.notes g }
#guard (toyFr.computeGlobal [] (royTo "")).charges.map (·.tax) == ["CIT"]
#guard (toyFr.computeGlobal [] (royTo "")).unsupported
  == ["1200 withholding on payment 1 (royalty): the rate depends on recipientState, not given (CGI 182 B III)", gradeC "1200" 1 "royalty"]
#guard (toyFr.computeGlobal [] (royTo ",\"recipientState\":\"FJ\"")).unsupported == []
-- a 2.0 Wht as plain rules: the same charges whatever the facts (ofWht_charges)
def divIntX : CanonGlobal := payLine "[{\"kind\":\"dividend\",\"amount\":500,\"recipientState\":\"AE\",\"lowTax\":true},{\"kind\":\"interest\",\"amount\":300}]"
#guard ((StateWht.ofWht whtPart).charges divIntX).map Charge.toJson == (whtPart.charges divIntX.company).map Charge.toJson
#guard ((StateWht.ofWht whtPart).charges divInt).map Charge.toJson == (whtPart.charges divInt.company).map Charge.toJson
-- NL Wet bronbelasting 2021: 25,8 % on interest to a related entity in a low-tax state; lowTax not given: general (0)
def nlWht : StateWht := { name := "bronbelasting", rules := [
  { rule := { kind := .interest, rateBp := 2580, minStakeBp := 5000, statute := "Wet bronbelasting 2021 art. 2.1" }, tests := [.lowTax true], ifUnknown := .general },
  StateRule.plain (WhtRule.zero .interest "Wet bronbelasting 2021: no withholding otherwise")] }
def intRel (facts : String) : CanonGlobal := payLine ("[{\"kind\":\"interest\",\"amount\":1000,\"stakeBp\":10000" ++ facts ++ "}]")
#guard (nlWht.charges (intRel ",\"recipientState\":\"BM\",\"lowTax\":true")).map (·.due) == [258]
#guard (nlWht.charges (intRel "")).map (·.due) == [0] && (nlWht.notes (intRel "")).length == 1
#guard (nlWht.charges (payLine "[{\"kind\":\"interest\",\"amount\":1000,\"lowTax\":true}]")).map (·.due) == [0]   -- not related

/-! ## 2.5.0 (R4-13-1): income stacked on the 1.x income tax (capital gains at the marginal rate) -/
-- The ZA 1.x model, copied from R4/za/lean/ZaTax/Basic.lean (SARS 2026 rate table, s. 6 rebates, s. 10 (1) (i)
-- interest exemption; UIF and the dividends tax left out): each adult's taxable income is wages + selfEmployment +
-- pension + interest above the exemption + rent, the household's interest and rent split equally between spouses.
namespace ZaToy
def sched : Schedule :=
  Schedule.ofList [(0, 1800), (237100, 2600), (370500, 3100), (512800, 3600), (673000, 3900), (857900, 4100), (1817000, 4500)]
def rebate (age : Nat) : Int := 17235 + (if age ≥ 65 then 9444 else 0) + (if age ≥ 75 then 3145 else 0)
def interestExempt (age : Nat) : Int := if age ≥ 65 then 34500 else 23800
def personTax (age : Nat) (ti : Int) : Int := pos (sched.tax Rule.unitDown (pos ti) - rebate age)
def personTI (a : Adult) (interest rental : Int) : Int :=
  a.wages + a.selfEmployment + a.pension + pos (interest - interestExempt a.age) + rental
def out (c : Canon) : Out :=
  let n : Int := c.adults.length
  let share (x : Int) (i : Nat) : Int := if n = 1 then x else if i = 0 then half1 x else half2 x
  let tis := (c.adults.zip (List.range c.adults.length)).map fun (a, i) =>
    (a.age, personTI a (share c.interest i) (share c.rentalIncome i))
  Out.make c "ZA" "ZAR" (sumInts (tis.map fun (age, ti) => personTax age ti))
    (detail := [Out.d "taxableIncome" (sumInts (tis.map (·.2)))])
def country : Country :=
  { code := "ZA", name := "South Africa (copy of the 1.x model)", currency := "ZAR", year := "2025", compute := out }
end ZaToy

-- Eighth Schedule: 40 % of the net capital gain after the R40 000 annual exclusion, per natural person, in taxable
-- income (s. 26A); the 1.x model adds `selfEmployment` in full to the person's taxable income, so the amount goes there.
def zaCgt : StackRule :=
  { name := "Capital gains tax (taxable capital gain in taxable income)",
    statute := "Income Tax Act 58 of 1962 s. 26A; Eighth Schedule para 5 (1) (annual exclusion R40 000), para 10 (a) (inclusion rate 40 %), para 45 (1) (primary residence: R2 000 000 of the gain); rates: s. 5 (1.x model)",
    gainKinds := [.home, .realEstate, .land, .listedShares, .unlistedShares, .bonds, .business, .other],
    gainRule := { mainHomeExempt := true, mainHomeCap := 2000000 },
    exclusion := { amount := 40000 }, pool := .person, inclusionBp := 4000, into := .selfEmployment }
def zaBase : GlobalModel := GlobalModel.ofCountry ZaToy.country
def zaModel : GlobalModel := zaBase.withStack [zaCgt]
def zaLine (adults disposals : String) : CanonGlobal :=
  gl ("{\"id\":\"z\",\"schema\":\"global/2.0\",\"household\":{\"id\":\"z\",\"adults\":" ++ adults ++ "},\"disposals\":"
    ++ disposals ++ "}")
/-- the charges that are not the 1.x line's: (event, base, relieved, due, level) -/
def stackedOf (o : OutGlobal) : List (String × Int × Int × Int × String) :=
  (o.charges.filter (·.statute != "1.x model")).map fun c => (c.event, c.base, c.relieved, c.due, c.level.name)

-- single, wages R600 000, shares sold at a gain of R240 000: (240 000 − 40 000) × 40 % = 80 000 in taxable income;
-- tax(680 000) − tax(600 000) = (179 147 + 7 000 × 39 %) − (121 475 + 87 200 × 36 %) = 181 877 − 152 867 = 29 010
def z1 : CanonGlobal :=
  zaLine "[{\"age\":40,\"wages\":600000}]" "[{\"kind\":\"listedShares\",\"proceeds\":500000,\"cost\":260000,\"heldMonths\":30}]"
#guard stackedOf (zaModel.computeGlobal [] z1) == [("disposal 1 (listedShares)", 240000, 80000, 29010, "central")]
#guard ((zaModel.computeGlobal [] z1).charges.filter (·.statute != "1.x model")).map (·.tax)
  == ["Capital gains tax (taxable capital gain in taxable income)"]
#guard (zaModel.computeGlobal [] z1).pit == (zaBase.computeGlobal [] z1).pit                -- the 1.x line: identical
#guard (zaModel.computeGlobal [] z1).total == (zaBase.computeGlobal [] z1).total + 29010
#guard (zaModel.computeGlobal [] z1).totalOf .pit == (zaBase.computeGlobal [] z1).totalOf .pit + 29010
-- the same number as the builders' hand form (`stackedTax`: 1.x tax with 80 000 more income less without)
#guard stackedTax (fun c => jsonIncomeTax (zaBase.pit [] c)) z1.household { rentalIncome := 80000 } == 29010
-- below the exclusion: a computed 0 (the rule has an item: the charge is booked, due 0)
#guard stackedOf (zaModel.computeGlobal [] (zaLine "[{\"age\":40,\"wages\":600000}]"
    "[{\"kind\":\"listedShares\",\"proceeds\":50000,\"cost\":20000}]")) == [("disposal 1 (listedShares)", 30000, 0, 0, "central")]
-- a loss offsets the gains of the year; a net loss gives 0 (no carry-forward)
#guard stackedOf (zaModel.computeGlobal [] (zaLine "[{\"age\":40,\"wages\":600000}]"
    "[{\"kind\":\"listedShares\",\"proceeds\":500000,\"cost\":260000},{\"kind\":\"land\",\"proceeds\":100000,\"cost\":300000}]"))
  == [("disposal 1 (listedShares), disposal 2 (land)", 40000, 0, 0, "central")]
-- per person: spouses with gains of 30 000 (adult 1: below the exclusion) and 100 000 (adult 2): only adult 2's
-- (100 000 − 40 000) × 40 % = 24 000 enters, on adult 2's income of 300 000 (26 % band): 6 240
def z3 : CanonGlobal :=
  zaLine "[{\"age\":40,\"wages\":400000},{\"age\":40,\"wages\":300000}]"
    "[{\"kind\":\"realEstate\",\"proceeds\":130000,\"cost\":100000},{\"kind\":\"listedShares\",\"proceeds\":200000,\"cost\":100000,\"person\":1}]"
#guard zaCgt.amounts 2 z3 == [(0, 0), (1, 24000)]
#guard stackedOf (zaModel.computeGlobal [] z3) == [("disposal 1 (realEstate), disposal 2 (listedShares)", 130000, 24000, 6240, "central")]
-- primary residence: R2 000 000 of the gain excluded (para 45): 2 500 000 → 500 000 − 40 000 → 184 000 included;
-- tax(784 000) − tax(600 000) = 222 437 − 152 867 = 69 570
#guard stackedOf (zaModel.computeGlobal [] (zaLine "[{\"age\":40,\"wages\":600000}]"
    "[{\"kind\":\"home\",\"proceeds\":4000000,\"cost\":1500000,\"mainHome\":true}]")) == [("disposal 1 (home)", 500000, 184000, 69570, "central")]
-- never guessed: a disposal of a person who is not an adult of the household: no charge, grade C
def z5 : CanonGlobal :=
  zaLine "[{\"age\":40,\"wages\":600000}]" "[{\"kind\":\"listedShares\",\"proceeds\":500000,\"cost\":260000,\"person\":1}]"
#guard stackedOf (zaModel.computeGlobal [] z5) == []
#guard (zaModel.computeGlobal [] z5).unsupported
  == ["1100 Capital gains tax (taxable capital gain in taxable income): disposal 1 (listedShares) is of person 1, who is not an adult of the household (not stacked) (grade C)"]
-- an entity without disposals (every 1.x household): the very same output (`withStack_noItems`, `withStack_ofCanon`)
def zLegacy : CanonGlobal := CanonGlobal.ofCanon { id := "x", adults := [{ wages := 600000 }] }
#guard (zaModel.computeGlobal [] zLegacy).toJson.compress == (zaBase.computeGlobal [] zLegacy).toJson.compress
#guard (zaModel.computeGlobal [] (hh "[{\"good\":\"food\",\"amount\":1000}]")).toJson.compress
  == (zaBase.computeGlobal [] (hh "[{\"good\":\"food\",\"amount\":1000}]")).toJson.compress
-- a company entity: nothing stacked
#guard (stackCharges zaBase.pit zaBase.route [zaCgt] [] { z1 with entity := .company }).isEmpty
-- a household pool on a household field (the 1.x model splits rent between spouses): one exclusion for the household
def zaPool : StackRule := { zaCgt with pool := .household, into := .rentalIncome }
#guard zaPool.amounts 2 z3 == [(0, 36000)]
#guard stackedOf ((zaBase.withStack [zaPool]).computeGlobal [] z3)
  == [("disposal 1 (realEstate), disposal 2 (listedShares)", 130000, 36000,
       stackedTax (fun c => jsonIncomeTax (zaBase.pit [] c)) z3.household { rentalIncome := 36000 }, "central")]
-- monotone 1.x tax (`StackMono`): the slice is ≥ 0 on a grid of incomes and gains
#guard (List.range 30).all fun i => (List.range 6).all fun k =>
  let g := zaLine s!"[\{\"age\":40,\"wages\":{i * 70000}}]" s!"[\{\"kind\":\"listedShares\",\"proceeds\":{k * 150000},\"cost\":0}]"
  (stackCharges zaBase.pit zaBase.route [zaCgt] [] g).all (0 ≤ ·.due)

-- A European progressive case: CZ-shaped (ZDP § 16: 15 % up to 36 × the average wage, CZK 1 676 052 in 2025, 23 %
-- above; § 35ba (1) a) taxpayer credit CZK 30 840). Toy 1.x model: each adult's wages + selfEmployment (+ a share of
-- rentalIncome) at the scale. Gains are "other income" (§ 10 (1) b)) taxed at the scale, exempt after the time test
-- (§ 4 (1) w): securities held more than 3 years, here 37 whole months; § 4 (1) b): 10 years for real estate). The
-- CZK 100 000 proceeds exemption of § 4 (1) w) is on proceeds, not gains: not part of this toy.
namespace CzToy
def sched : Schedule := Schedule.ofList [(0, 1500), (1676052, 2300)]
def out (c : Canon) : Out :=
  let n := c.adults.length
  let tis := (c.adults.zip (List.range n)).map fun (a, i) =>
    a.wages + a.selfEmployment + (if n = 1 then c.rentalIncome else if i = 0 then half1 c.rentalIncome else half2 c.rentalIncome)
  Out.make c "CZ" "CZK" (sumInts (tis.map fun ti => pos (sched.tax Rule.unitDown (pos ti) - 30840)))
    (detail := [Out.d "taxBase" (sumInts tis)])
def country : Country := { code := "CZ", name := "Czechia (toy)", currency := "CZK", year := "2025", compute := out }
/-- an exe-level form: the per-line function an `ofLine` model wraps (it re-reads the input line) -/
def line (args : List String) (j : Json) : Json :=
  match parseCanon j with
  | .ok c => (country.computeWith args c).toJson
  | .error e => Json.mkObj [("error", Json.str e)]
end CzToy
def czShares : StackRule :=
  { name := "Daň z příjmů fyzických osob: ostatní příjmy (§ 10), cenné papíry",
    statute := "ZDP § 10 (1) b) 2., § 4 (1) w) (exempt when held more than 3 years); rates § 16 (1.x model)",
    gainKinds := [.listedShares, .unlistedShares, .bonds], gainRule := { exemptAfterMonths := 37 }, into := .selfEmployment }
def czLand : StackRule :=
  { czShares with
    name := "Daň z příjmů fyzických osob: ostatní příjmy (§ 10), nemovité věci",
    statute := "ZDP § 10 (1) b) 1., § 4 (1) b) (exempt after 10 years); rates § 16 (1.x model)",
    gainKinds := [.home, .realEstate, .land], gainRule := { exemptAfterMonths := 121 } }
def czBase : GlobalModel := GlobalModel.ofCountry CzToy.country
def czLineBase : GlobalModel := GlobalModel.ofLine "CZ" "Czechia (toy, exe-level)" "CZK" "2025" CzToy.line
def czLine (adults disposals : String) : CanonGlobal :=
  gl ("{\"id\":\"c\",\"schema\":\"global/2.0\",\"household\":{\"id\":\"c\",\"adults\":" ++ adults ++ "},\"disposals\":"
    ++ disposals ++ "}")
-- wages 1 600 000 + a 200 000 gain on shares held 2 years crosses the 23 % threshold:
-- 76 052 × 15 % + 123 948 × 23 % = 11 407.80 + 28 508.04 → tax(1 800 000) − tax(1 600 000) = 279 915 − 240 000 = 39 915
def c1 : CanonGlobal :=
  czLine "[{\"age\":40,\"wages\":1600000}]" "[{\"kind\":\"listedShares\",\"proceeds\":300000,\"cost\":100000,\"heldMonths\":24}]"
#guard (stackCharges czBase.pit czBase.route [czShares, czLand] [] c1).map (·.due) == [39915]
-- held 40 months: exempt (a covered 0)
#guard (stackCharges czBase.pit czBase.route [czShares, czLand] []
    (czLine "[{\"age\":40,\"wages\":1600000}]" "[{\"kind\":\"listedShares\",\"proceeds\":300000,\"cost\":100000,\"heldMonths\":40}]")).map
      (fun c => (c.base, c.relieved, c.due)) == [(0, 0, 0)]
-- two rules stack in order: the land gain of 500 000 sits on top of the shares (all at 23 %: 115 000); the slices add
-- up to the 1.x tax with both less without both (394 915 − 240 000 = 154 915)
def c3 : CanonGlobal :=
  czLine "[{\"age\":40,\"wages\":1600000}]"
    "[{\"kind\":\"listedShares\",\"proceeds\":300000,\"cost\":100000,\"heldMonths\":24},{\"kind\":\"land\",\"proceeds\":900000,\"cost\":400000,\"heldMonths\":60}]"
#guard (stackCharges czBase.pit czBase.route [czShares, czLand] [] c3).map (fun c => (c.event, c.due))
  == [("disposal 1 (listedShares)", 39915), ("disposal 2 (land)", 115000)]
#guard stackedTax (fun c => jsonIncomeTax (czBase.pit [] c)) c3.household { rentalIncome := 700000 } == 39915 + 115000
-- the exe-level form (`ofLine`, the 1.x line re-read from the input line) prices the same household: same charges
#guard (stackCharges czLineBase.pit czLineBase.route [czShares, czLand] [] c3).map Charge.toJson
  == (stackCharges czBase.pit czBase.route [czShares, czLand] [] c3).map Charge.toJson
#guard ((czLineBase.withStack [czShares, czLand]).computeGlobal [] c3).pit == (czLineBase.computeGlobal [] c3).pit
-- amounts with decimals in the input line: the line gets exactly the amount added (`jsonNumAdd_int`)
def c4 : CanonGlobal :=
  czLine "[{\"age\":40,\"wages\":1600000,\"selfEmployment\":1000.5}]" "[{\"kind\":\"bonds\",\"proceeds\":300000,\"cost\":100000}]"
#guard (stackCharges czLineBase.pit czLineBase.route [czShares] [] c4).map (·.due)
  == (stackCharges czBase.pit czBase.route [czShares] [] c4).map (·.due)
#guard stackRawAgrees (StackField.selfEmployment.addAll c4.household [(0, 200000)])
#guard jsonAddField (Json.mkObj [("rentalIncome", (Json.parse "1000.5").toOption.get!)]) "rentalIncome" 200 ==
  Json.mkObj [("rentalIncome", (Json.parse "1200.5").toOption.get!)]
-- a household built in Lean (no input line): the `ofCountry` form prices it (the structure moved, the 1.x line moved);
-- the `ofLine` form cannot (its line is an error): no charge, grade C
def cLean : CanonGlobal :=
  { id := "n", household := { id := "n", adults := [{ wages := 1600000 }] },
    disposals := [{ kind := .listedShares, proceeds := 300000, cost := 100000, heldMonths := 24 }] }
#guard (stackCharges czBase.pit czBase.route [czShares] [] cLean).map (·.due) == [39915]
#guard (stackCharges czLineBase.pit czLineBase.route [czShares] [] cLean).isEmpty
#guard (stackUnknown czLineBase.pit czLineBase.route [czShares] [] cLean).map (fun s => s.startsWith "1100 Daň z příjmů" && (s.splitOn "answers with an error").length == 2 && s.endsWith "(grade C)")
  == [true]
-- a later rule is never priced on top of one that was not: both grade C
#guard (stackUnknown czLineBase.pit czLineBase.route [czShares, czLand] []
    { cLean with disposals := cLean.disposals ++ [{ kind := .land, proceeds := 2, cost := 1 }] }).length == 2

-- income items: foreign dividends included in full, interest only above a household threshold of 1 000 (toy)
def czDiv : StackRule :=
  { name := "foreign dividends at the scale (toy)", statute := "toy", incomeKinds := [.dividend],
    foreign := some true, pool := .household, into := .rentalIncome }
#guard czDiv.items (gl "{\"id\":\"i\",\"household\":{\"id\":\"i\",\"adults\":[{\"wages\":100000}]},\"incomes\":[{\"kind\":\"dividend\",\"amount\":5000,\"foreign\":true},{\"kind\":\"dividend\",\"amount\":7000},{\"kind\":\"interest\",\"amount\":3000,\"foreign\":true}]}")
  == [(0, 5000, "income 1 (dividend)")]

-- a 1.x model with a local income tax: the local part is its own `.local` charge (toy: 20 % above 10 000 + 10 % local)
def locOut (c : Canon) : Out :=
  let ti := c.adult1.wages + c.rentalIncome
  Out.make c "LX" "X" (pos (ti - 10000) / 5) (localIncomeTax := ti / 10)
def locToy : Country := { code := "LX", name := "toy", currency := "X", year := "2025", compute := locOut }
def locRule : StackRule :=
  { name := "gains at the scale", statute := "toy", gainKinds := AssetKind.every, pool := .household,
    into := .rentalIncome }
#guard (stackCharges (GlobalModel.ofCountry locToy).pit (fun g => g.household) [locRule] []
    (gl "{\"id\":\"l\",\"household\":{\"id\":\"l\",\"adults\":[{\"wages\":50000}]},\"disposals\":[{\"kind\":\"other\",\"proceeds\":3000,\"cost\":1000}]}")).map
      (fun c => (c.tax, c.level.name, c.due)) == [("gains at the scale", "central", 400), ("gains at the scale (local income tax)", "local", 200)]

/-! ## 2.5.0 (R1 Europe pass 9): Euro emission class and list price on the vehicle record -/
#guard euroStageOf "Euro 6d-TEMP" == 64 && euroStageOf "6d" == 65 && euroStageOf "EURO 5b" == 52
#guard euroStageOf "Euro 6" == -1 && euroStageOf "Euro 4" == 40 && euroStageOf "6d-ISC-FCM" == 66 && euroStageOf "diesel" == -1
#guard euroClassOf "Euro 6" == 6 && euroClassOf "6d-TEMP" == 6 && euroClassOf "Euro 3" == 3 && euroClassOf "diesel" == -1
def dsl (e : String) (extra : String := "") : String :=
  "{\"kind\":\"vehicle\",\"value\":30000,\"co2GKm\":130,\"fuel\":\"diesel\",\"firstRegYear\":2024,\"euroClass\":" ++ e ++ extra ++ "}"
#guard (veh (dsl "\"Euro 6d-TEMP\"" ",\"listPrice\":45000")).vehicles.map (fun v => (v.euroClass, v.euroStage, v.listPrice, v.value))
  == [(6, 64, 45000, 30000)]
#guard (veh (dsl "6")).vehicles.map (fun v => (v.euroClass, v.euroStage)) == [(6, -1)]
#guard (veh (dsl "4")).vehicles.map (fun v => (v.euroClass, v.euroStage)) == [(4, 40)]
#guard (veh (dsl "6.5")).vehicles.map (fun v => (v.euroClass, v.euroStage)) == [(-1, -1)]
#guard (veh golf).vehicles.map (fun v => (v.euroClass, v.euroStage, v.listPrice)) == [(-1, -1, -1)]   -- not given
-- a diesel test on Euro 6d (UK VERA Sch. 1 para 1GC (3)-(5) shape; toy amounts): 6d or later one rate, else another
def vedMeets : VehicleTax :=
  { name := "VED (toy)", kinds := ["car"], fuels := [.diesel], fixed := 10,
    «when» := [(.euroStage, euroStageOf "6d-TEMP", 100)], statute := "para 1GC Table 1 (meets Euro 6d)" }
def vedOther : VehicleTax :=
  { vedMeets with
    fixed := 20, «when» := [(.euroStage, -1, euroStageOf "6d-TEMP")], statute := "para 1GC (3)-(5) Table 2" }
#guard (vehicleTaxCharges [vedMeets, vedOther] (veh (dsl "\"6d\""))).map (·.due) == [10]
#guard (vehicleTaxCharges [vedMeets, vedOther] (veh (dsl "\"6d-TEMP\""))).map (·.due) == [20]
-- a plain "Euro 6" never passes (or fails) a 6d test: no charge, grade C
#guard (vehicleTaxCharges [vedMeets, vedOther] (veh (dsl "\"Euro 6\""))).isEmpty
#guard vehicleTaxUnknown "VED" [vedMeets, vedOther] (veh (dsl "\"Euro 6\""))
  == ["5200 VED: vehicle 1 (asset 1, car): euroStage not given (grade C)"]
-- by class (IT bollo / DE § 9 (1) Nr. 2 a shape; toy amounts): every Euro 6 alike
def byClass : VehicleTax := { name := "bollo (toy)", parts := [(.euroClass, QtyTable.ofCeilings [(3, 300), (5, 200)] 100)] }
#guard (vehicleTaxCharges [byClass] (veh (dsl "\"Euro 6\""))).map (·.due) == [100]
#guard (vehicleTaxCharges [byClass] (veh (dsl "4"))).map (·.due) == [200]
-- the list price (UK para 1GE shape: over 40 000 when new; toy amount): never read from `value`
def dear : VehicleTax := { name := "expensive car (toy)", kinds := ["car"], fixed := 1, «when» := [(.listPrice, 40000, 1000000000000)] }
#guard (vehicleTaxCharges [dear] (veh (dsl "\"6d\"" ",\"listPrice\":45000"))).map (·.due) == [1]
#guard (vehicleTaxCharges [dear] (veh (dsl "\"6d\"" ",\"listPrice\":35000"))).isEmpty
#guard vehicleTaxUnknown "VED" [dear] (veh (dsl "\"6d\"")) == ["5200 VED: vehicle 1 (asset 1, car): listPrice not given (grade C)"]
-- taxes that read none of the new attributes: unchanged (`Vehicle.attr?_old`)
#guard (vehicleTaxCharges deKfz (veh (golf ++ "," ++ passat ++ "," ++ ev))).map (·.due) == [128, 263, 0]

/-! ## 2.5.0 (R2-P9-1): the company's sector (`company.sector`) and CIT rates by sector -/
-- GY Corporation Tax Act Cap. 81:03 s. 10: a telephone company 45 %, a commercial company 40 % with a minimum of 2 % of
-- turnover, any other company 25 %
def gyGeneral : CorpRule := { regime := { name := "Corporation tax", sched := Schedule.flat 2500 } }
def gyCit (a : SectorAbsent) : SectorCorp :=
  { general := gyGeneral, statute := "Corporation Tax Act s. 10 (25 %)", ifAbsent := a,
    bySector := [
      { sectors := ["telecom"], rule := { regime := { name := "Corporation tax", sched := Schedule.flat 4500 } },
        statute := "Corporation Tax Act s. 10 (telephone company, 45 %)" },
      { sectors := ["commercialTrading", "bank", "insurer"],
        rule := { regime := { name := "Corporation tax", sched := Schedule.flat 4000 }, minTax := some { bp := 200 } },
        statute := "Corporation Tax Act s. 10 (commercial company, 40 %; minimum 2 % of turnover)" }] }
def gyCo (profit : Int) (sector : String) : CanonGlobal :=
  gl ("{\"id\":\"co\",\"entity\":\"company\",\"company\":{\"turnover\":10000000,\"profit\":" ++ toString profit ++ sector ++ "}}")
#guard companySectors (gyCo 1 ",\"sector\":\"telecom\"") == some ["telecom"]
#guard companySectors (gyCo 1 ",\"sector\":[\"manufacturing\",\"commercialTrading\"]") == some ["manufacturing", "commercialTrading"]
#guard companySectors (gyCo 1 "") == none
#guard Sector.canonical.all Sector.isCanonical && !Sector.isCanonical "commercial"
#guard ((gyCit .general).citCharges (gyCo 1000000 ",\"sector\":\"commercialTrading\"")).map (fun c => (c.due, c.statute))
  == [(400000, "Corporation Tax Act s. 10 (commercial company, 40 %; minimum 2 % of turnover)")]
#guard ((gyCit .general).citCharges (gyCo 100000 ",\"sector\":\"commercialTrading\"")).map (·.due) == [200000]   -- the 2 % minimum
#guard ((gyCit .general).citCharges (gyCo 1000000 ",\"sector\":\"telecom\"")).map (·.due) == [450000]
#guard ((gyCit .general).citCharges (gyCo 1000000 ",\"sector\":[\"manufacturing\",\"commercialTrading\"]")).map (·.due) == [400000]
#guard ((gyCit .general).citCharges (gyCo 1000000 ",\"sector\":\"manufacturing\"")).map (·.due) == [250000]  -- any other company
-- the sector not given: the model declares what that means
#guard ((gyCit .general).citCharges (gyCo 1000000 "")).map (fun c => (c.due, c.statute))
  == [(250000, "Corporation Tax Act s. 10 (25 %)" ++ absentSectorNote)]
#guard (gyCit .general).notes "Corporation tax" (gyCo 1000000 "")
  == ["1200 Corporation tax: company.sector not given: the general rule applied (declared by the model)"]
#guard ((gyCit .gradeC).citCharges (gyCo 1000000 "")).isEmpty
#guard (gyCit .gradeC).unknown "Corporation tax" (gyCo 1000000 "")
  == ["1200 Corporation tax: company.sector not given; the rate depends on it (grade C)"]
#guard (gyCit .gradeC).unknown "Corporation tax" (gyCo 1000000 ",\"sector\":\"telecom\"") == []
-- no sector rates: the CorpRule's own charge, whatever the line says (`ofRule_citCharges`)
#guard (({ general := gyGeneral, statute := "s. 10", ifAbsent := .gradeC } : SectorCorp).citCharges (gyCo 1000000 "")).map Charge.toJson
  == [(gyGeneral.citCharge (gyCo 1000000 "") "s. 10").toJson]
#guard (((gyCit .general).family "Corporation tax" { rules := [] }).run [] (gyCo 1000000 ",\"sector\":\"telecom\"") []).map (·.due) == [450000]

/-! ## 2.5.0 (MENA pass 3k): an open upper bound in `VehicleTax.when` (`noBound`, −1, as `maxUnitPrice`) -/
def vDear (hi : Int) : VehicleTax :=
  { name := "supplement (toy)", kinds := ["car"], fixed := 1, «when» := [(.value, 40000, hi)] }
#guard (vehicleTaxCharges [vDear VehicleTax.noBound] (veh (dsl "\"6d\"" ""))).isEmpty                    -- value 30 000
#guard (vehicleTaxCharges [vDear VehicleTax.noBound] (veh "{\"kind\":\"vehicle\",\"value\":40001}")).map (·.due) == [1]
#guard (vehicleTaxCharges [vDear VehicleTax.noBound] (veh "{\"kind\":\"vehicle\",\"value\":900000000000000}")).map (·.due) == [1]
-- a large number as the bound (the 2.4.0 workaround) selects as before (`inRange_bounded`)
#guard (vehicleTaxCharges [vDear 1000000000000] (veh "{\"kind\":\"vehicle\",\"value\":40001}")).map (·.due) == [1]
#guard (vehicleTaxCharges [vDear 1000000000000] (veh "{\"kind\":\"vehicle\",\"value\":900000000000000}")).isEmpty
#guard VehicleTax.inRange (-1) 1300 1300 && !VehicleTax.inRange (-1) 1300 1301 && VehicleTax.inRange 1300 (-1) 99999

/-! ## 2.6.0 (FT reviewer 6): when in the year a vehicle was first registered -/
def regV (fields : String) : CanonGlobal := veh ("{\"kind\":\"vehicle\",\"value\":20000,\"co2GKm\":115,\"fuel\":\"petrol\"" ++ fields ++ "}")
def regOf (g : CanonGlobal) : List (Nat × Nat × Nat × Bool) := g.vehicles.map fun v => (v.firstRegYear, v.firstRegMonth, v.firstRegDay, v.newReg)
#guard regOf (regV ",\"firstRegYear\":2025,\"firstRegMonth\":7") == [(2025, 7, 0, true)]
#guard regOf (regV ",\"firstRegYear\":2025,\"firstRegDate\":\"2025-03-14\"") == [(2025, 3, 14, true)]  -- the date gives month and day
#guard regOf (regV ",\"firstRegDate\":\"2025-03-14\"") == [(0, 0, 0, false)]   -- the year only from firstRegYear (2.5.0 reads alike)
#guard regOf (regV ",\"firstRegYear\":2025,\"firstRegDate\":\"2025-03\"") == [(2025, 3, 0, true)]
#guard regOf (regV ",\"firstRegYear\":2024,\"firstRegDate\":\"2025-03-14\"") == [(2024, 0, 0, false)]  -- years disagree: no month
#guard regOf (regV ",\"firstRegYear\":2025,\"firstRegMonth\":13,\"firstRegDate\":\"14/03/2025\"") == [(2025, 0, 0, true)]
#guard regOf (regV ",\"firstRegYear\":2025,\"firstRegDate\":\"2025-02-30\"") == [(2025, 0, 0, true)]             -- not a calendar day
#guard regOf (veh golf) == [(2023, 0, 0, false)]                                           -- a 2.5.0 record reads the same
#guard isoYmd? "2024-02-29" == some (2024, 2, 29) && isoYmd? "2025-02-29" == none && daysInMonth 2025 4 == 30
-- FR malus shape: the 2024 barème for cars first registered to 28 February 2025, the 2025 barème from 1 March 2025
-- (CIBS L. 421-58 ff. as amended by LF 2025; first band only, thresholds 118 and 113 g/km, 50 EUR: the tables go on)
def malus24 : VehicleTax :=
  { name := "malus (toy, first band)", occasion := .registration, fixed := 50, «when» := [(.co2GKm, 117, VehicleTax.noBound)],
    regToDate := "2025-02-28", statute := "CIBS L. 421-62 (barème 2024)" }
def malus25 : VehicleTax :=
  { malus24 with
    «when» := [(.co2GKm, 112, VehicleTax.noBound)], regToDate := "", regFromDate := "2025-03-01",
    statute := "CIBS L. 421-62 (barème 2025, from 1 March 2025)" }
def malus : List VehicleTax := [malus24, malus25]
#guard malus24.hasWindow && !dePetrol.hasWindow
#guard (vehicleTaxCharges malus (regV ",\"firstRegYear\":2025,\"firstRegDate\":\"2025-03-02\"")).map (fun c => (c.due, c.statute))
  == [(50, "CIBS L. 421-62 (barème 2025, from 1 March 2025)")]
#guard (vehicleTaxCharges malus (regV ",\"firstRegYear\":2025,\"firstRegMonth\":3")).map (·.due) == [50]   -- the month decides
#guard (vehicleTaxCharges malus (regV ",\"firstRegYear\":2025,\"firstRegMonth\":2")).isEmpty               -- 115 g: under 118
#guard (vehicleTaxCharges malus (regV ",\"firstRegYear\":2025,\"firstRegMonth\":2,\"co2GKm\":120")).map (fun c => (c.due, c.statute))
  == [(50, "CIBS L. 421-62 (barème 2024)")]
-- the year only: either barème could apply; never guessed: no charge, grade C naming the month
#guard (vehicleTaxCharges malus (regV ",\"firstRegYear\":2025")).isEmpty
#guard vehicleTaxUnknown "malus" malus (regV ",\"firstRegYear\":2025")
  == ["5200 malus: vehicle 1 (asset 1, car): firstRegMonth not given (grade C)"]
#guard vehicleTaxUnknown "malus" malus (regV ",\"firstRegYear\":2025,\"firstRegMonth\":3") == []
-- a bound inside a month needs the day (a levy for vehicles first registered from 15 July; toy amount)
def mid : VehicleTax := { name := "levy (toy)", occasion := .registration, fixed := 7, regFromDate := "2025-07-15" }
#guard (vehicleTaxCharges [mid] (regV ",\"firstRegYear\":2025,\"firstRegMonth\":7")).isEmpty
#guard vehicleTaxUnknown "levy" [mid] (regV ",\"firstRegYear\":2025,\"firstRegMonth\":7")
  == ["5200 levy: vehicle 1 (asset 1, car): firstRegDay not given (grade C)"]
#guard (vehicleTaxCharges [mid] (regV ",\"firstRegYear\":2025,\"firstRegDate\":\"2025-07-20\"")).map (·.due) == [7]
#guard (vehicleTaxCharges [mid] (regV ",\"firstRegYear\":2025,\"firstRegDate\":\"2025-07-14\"")).isEmpty
#guard (vehicleTaxCharges [mid] (regV ",\"firstRegYear\":2025,\"firstRegMonth\":8")).map (·.due) == [7]   -- August: inside
#guard vehicleTaxUnmatched "levy" [mid] (regV ",\"firstRegYear\":2025,\"firstRegMonth\":6") != []          -- June: outside
-- TZ Finance Act 2025 shape (from 1 July 2025; toy amounts): a window on the 1st of a month is decided by the month
def tzOld : VehicleTax := { name := "registration (toy)", occasion := .registration, fixed := 100, regToDate := "2025-06-30" }
def tzNew : VehicleTax := { tzOld with fixed := 130, regToDate := "", regFromDate := "2025-07-01" }
#guard ([1, 6, 7, 12] : List Nat).map (fun m => (vehicleTaxCharges [tzOld, tzNew]
    (regV (",\"firstRegYear\":2025,\"firstRegMonth\":" ++ toString m))).map (·.due)) == [[100], [100], [130], [130]]
-- a vehicle first registered in an earlier year (registered again this year): decided by the year alone
#guard (vehicleTaxCharges [tzOld, tzNew] (regV ",\"firstRegYear\":2019,\"registeredThisYear\":true")).map (·.due) == [100]
-- a bound that is not a date selects nothing (never read as open)
#guard (vehicleTaxCharges [{ tzNew with regFromDate := "1 July 2025" }] (regV ",\"firstRegYear\":2025,\"firstRegDate\":\"2025-08-01\"")).isEmpty
-- the month as an attribute (`when`): CL first permits priced by the month (DL 3.063 art. 12 shape; toy amounts)
def clFirst : List VehicleTax := (List.range 12).map fun (k : Nat) =>
  { name := "permiso de circulación (toy)", occasion := .registration, fixed := 1000 * ((k : Int) + 1),
    «when» := [(.firstRegMonth, (k : Int), (k : Int) + 1)], statute := s!"month {k + 1}" }
#guard (vehicleTaxCharges clFirst (regV ",\"firstRegYear\":2025,\"firstRegMonth\":3")).map (fun c => (c.due, c.statute)) == [(3000, "month 3")]
#guard (vehicleTaxCharges clFirst (regV ",\"firstRegYear\":2025")).isEmpty
#guard vehicleTaxUnknown "permiso" clFirst (regV ",\"firstRegYear\":2025")
  == ["5200 permiso: vehicle 1 (asset 1, car): firstRegMonth not given (grade C)"]
-- taxes without a window are untouched by the month (`computes_noWindow`)
#guard (vehicleTaxCharges deKfz (veh (golf ++ "," ++ passat ++ "," ++ ev))).map (·.due) == [128, 263, 0]
#guard (vehicleTaxCharges deKfz (veh "{\"kind\":\"vehicle\",\"value\":1,\"engineCcm\":1598,\"co2GKm\":140,\"fuel\":\"petrol\",\"firstRegDate\":\"2025-05-01\"}")).map (·.due) == [128]

/-! ## 2.6.0 (R1 Europe pass 10): a share of the stacked charge, or the global (average) rate -/
-- LU L.I.R. art. 131 (1) c: the gains of art. 99ter / 100 (art. 132 (2)) at "un taux égal à la moitié du taux global
-- correspondant au revenu imposable ajusté"; the ordinary income keeps the tariff (the 1.x line, unchanged). Shown on the
-- ZA toy (its 1.x line gives `detail.taxableIncome`).
def halfGlobal : StackRule :=
  { name := "half the global rate", statute := "L.I.R. art. 131 (1) c, art. 132 (2) (shape)", gainKinds := [.unlistedShares],
    into := .selfEmployment, mode := .averageRate "taxableIncome", shareBp := 5000 }
def hgLine : CanonGlobal :=
  zaLine "[{\"age\":40,\"wages\":600000}]" "[{\"kind\":\"unlistedShares\",\"proceeds\":340000,\"cost\":100000,\"stakeBp\":2000}]"
def hgModel : GlobalModel := zaBase.withStack [halfGlobal]
-- with the gain: taxable income 840 000, tax (179 147 + 167 000 × 39 %) − 17 235 = 227 042;
-- 240 000 × ½ × 227 042 / 840 000 = 32 434.57 → 32 434
#guard jsonIncomeTax (zaBase.pit [] (StackField.selfEmployment.addTo hgLine.household 0 240000)) == 227042
#guard StackSlice.stackLineInt? (zaBase.pit [] (StackField.selfEmployment.addTo hgLine.household 0 240000)) "taxableIncome" == some 840000
#guard stackedOf (hgModel.computeGlobal [] hgLine) == [("disposal 1 (unlistedShares)", 240000, 240000, 32434, "central")]
#guard (hgModel.computeGlobal [] hgLine).pit == (zaBase.computeGlobal [] hgLine).pit         -- the 1.x line: identical
#guard (hgModel.computeGlobal [] hgLine).unsupported == []
-- the other reading, (PIT(income + gain) − PIT(income)) × ½: (244 277 − 152 867) / 2 = 45 705
#guard stackedOf ((zaBase.withStack [{ halfGlobal with mode := .marginal }]).computeGlobal [] hgLine)
  == [("disposal 1 (unlistedShares)", 240000, 240000, 45705, "central")]
-- the whole global rate (shareBp 10000): 240 000 × 227 042 / 840 000 = 64 869.14 → 64 869
#guard stackedOf ((zaBase.withStack [{ halfGlobal with shareBp := 10000 }]).computeGlobal [] hgLine)
  == [("disposal 1 (unlistedShares)", 240000, 240000, 64869, "central")]
-- a line without the taxable income named: no rate, never guessed: no charge, grade C
def hgNoKey : StackRule := { halfGlobal with mode := .averageRate "revenuImposableAjuste" }
#guard stackedOf ((zaBase.withStack [hgNoKey]).computeGlobal [] hgLine) == []
#guard ((zaBase.withStack [hgNoKey]).computeGlobal [] hgLine).unsupported
  == ["1100 half the global rate: no global rate: the 1.x line with 240000 added gives no usable revenuImposableAjuste (absent, or not positive while income tax is due) or a negative income tax (grade C)"]
-- a taxable income of 0 with no income tax is a rate of 0 (priced 0), not grade C
def zeroToy : Country :=
  { code := "Z0", name := "toy", currency := "Z", year := "2025",
    compute := fun c => Out.make c "Z0" "Z" 0 (detail := [Out.d "taxableIncome" 0]) }
#guard (stackCharges (GlobalModel.ofCountry zeroToy).pit (fun g => g.household) [halfGlobal] [] hgLine).map (·.due) == [0]
#guard (stackUnknown (GlobalModel.ofCountry zeroToy).pit (fun g => g.household) [halfGlobal] [] hgLine) == []
-- nothing included: a priced 0 even without the key
#guard stackedOf ((zaBase.withStack [hgNoKey]).computeGlobal [] (zaLine "[{\"age\":40,\"wages\":600000}]"
    "[{\"kind\":\"unlistedShares\",\"proceeds\":100,\"cost\":300}]")) == [("disposal 1 (unlistedShares)", -200, 0, 0, "central")]
-- the 2.5.0 rule spelled with the new defaults gives the very same output (`StackSlice.due_default`)
#guard (zaModel.computeGlobal [] z1).toJson.compress
  == ((zaBase.withStack [{ zaCgt with mode := .marginal, shareBp := 10000 }]).computeGlobal [] z1).toJson.compress
-- the local income tax part follows the same share (the local toy: 400 central + 200 local at the margin, × ½)
#guard (stackCharges (GlobalModel.ofCountry locToy).pit (fun g => g.household) [{ locRule with shareBp := 5000 }] []
    (gl "{\"id\":\"l\",\"household\":{\"id\":\"l\",\"adults\":[{\"wages\":50000}]},\"disposals\":[{\"kind\":\"other\",\"proceeds\":3000,\"cost\":1000}]}")).map
      (fun c => (c.level.name, c.due)) == [("central", 200), ("local", 100)]

/-! ## 2.6.0 (R4-14-1): the employer of a household's wages (per-employer levies) -/
-- NA VET levy: 1 % of payroll for employers with an annual payroll of N$1 000 000 or more (VET Act 2008 s. 35;
-- GN 67 of 2021 para 3)
def naVet : EmployerLevy :=
  { name := "VET levy",
    rules := [
      { rateBp := 100, tests := [.payrollAtLeast 1000000], ifUnknown := .gradeC,
        statute := "VET Act 2008 s. 35; GN 67 of 2021 para 3" }] }
def empLine (adults : String) (extra : String := "") : CanonGlobal :=
  gl ("{\"id\":\"e\",\"schema\":\"global/2.0\",\"household\":{\"id\":\"e\",\"adults\":" ++ adults ++ "}" ++ extra ++ "}")
def e1 : CanonGlobal := empLine "[{\"age\":40,\"wages\":240000,\"employerPayroll\":5000000,\"employerEmployees\":40,\"employerSector\":\"mining\",\"employerRiskClass\":3},{\"age\":38,\"wages\":90000,\"employerPayroll\":800000}]"
#guard employerOf e1 0 == { payroll := 5000000, employees := 40, sectors := some ["mining"], riskClass := "3" }
#guard employerOf e1 1 == { payroll := 800000 }
#guard employerOf (empLine "[{\"age\":40,\"wages\":1}]") 0 == {}                     -- not given
#guard (naVet.charges e1).map (fun c => (c.oecd.code, c.event, c.bearer.name, c.base, c.relieved, c.due))
  == [("3000", "adult 1 wages", "employer", 240000, 240000, 2400)]                       -- adult 2's employer: below N$1 m
-- the payroll not given: no charge, grade C
def e2 : CanonGlobal := empLine "[{\"age\":40,\"wages\":240000}]"
#guard (naVet.charges e2).isEmpty
#guard naVet.unknown e2 == ["3000 VET levy: adult 1 wages: the rate depends on employerPayroll, not given (VET Act 2008 s. 35; GN 67 of 2021 para 3) (grade C)"]
#guard naVet.unknown e1 == []
-- CD INPP shape: 3 % (1-50 workers), 2 % (51-300), 1 % (more); an employer contribution (2200)
def cdInpp : EmployerLevy :=
  { name := "INPP", oecd := .sscEmployer, level := .social, rules := [
      { rateBp := 300, tests := [.employeesAtMost 50], ifUnknown := .gradeC, statute := "INPP 1-50" },
      { rateBp := 200, tests := [.employeesAtMost 300], ifUnknown := .gradeC, statute := "INPP 51-300" },
      { rateBp := 100, ifUnknown := .gradeC, statute := "INPP above 300" }] }
#guard ([10, 50, 51, 300, 301] : List Nat).map (fun n => (cdInpp.charges (empLine ("[{\"age\":30,\"wages\":100000,\"employerEmployees\":" ++ toString n ++ "}]"))).map (·.due))
  == [[3000], [3000], [2000], [2000], [1000]]
#guard (cdInpp.charges e2).isEmpty && (cdInpp.unknown e2).length == 1
-- risk classes with a per-employee cap; a presumed rate (its statute says so) and a passed-over one (noted)
def ecToy : EmployerLevy :=
  { name := "employers compensation (toy)", oecd := .sscEmployer, rules := [
      { rateBp := 250, tests := [.riskClasses ["3", "4"]], ifUnknown := .general, wageCap := 100000, statute := "class 3-4" },
      { rateBp := 80, tests := [.inSectors ["mining", "petroleum"]], ifUnknown := .presume, statute := "extractive" },
      { rateBp := 50, ifUnknown := .gradeC, statute := "other" }] }
#guard (ecToy.charges e1).map (fun c => (c.relieved, c.due, c.statute)) == [(100000, 2500, "class 3-4"), (90000, 720, "extractive" ++ employerPresumedNote)]
#guard ecToy.notes e1 == ["2200 employers compensation (toy): adult 2 wages: conditional rate 250 bp (class 3-4) not tested: employerRiskClass not given; 80 bp booked (extractive)"]
-- no fact given never yields a conditional rate silently (`employerPick_noFacts`)
#guard match (employerPick {} naVet.rules).1 with | .gradeC _ => true | _ => false
#guard match (employerPick {} ecToy.rules).1 with | .rule r true => r.statute == "extractive" | _ => false
-- adults without wages: nothing; a company entity only with `companies := true`, on its own payroll
#guard (naVet.charges (empLine "[{\"age\":70,\"pension\":100000,\"employerPayroll\":5000000}]")).isEmpty
def eCo : CanonGlobal := gl "{\"id\":\"c\",\"entity\":\"company\",\"company\":{\"profit\":1,\"payroll\":2000000,\"employees\":12}}"
#guard (naVet.charges eCo).isEmpty
#guard (EmployerLevy.charges { naVet with companies := true } eCo).map (fun (c : Charge) => (c.event, c.due)) == [("payroll", 20000)]
#guard (naVet.family).covers.map (·.code) == ["3000"]
-- a model with the family: an entity without wages keeps its charges and total (the family adds heading 3000 to `covered`)
#guard ((toyWithCit.withFamily naVet.family).computeGlobal [] (hh "[]")).charges.map Charge.toJson == (toyWithCit.computeGlobal [] (hh "[]")).charges.map Charge.toJson
#guard ((toyWithCit.withFamily naVet.family).computeGlobal [] (hh "[]")).covered.map (·.code) == ["1100", "2100", "1200", "3000"]

/-! ## 2.6.0 (Asia-Pacific PK): advance income tax on a transaction, credited against the year's income tax -/
-- a 1.x toy: income tax 10 % of wages above 600 000
def pkToy : Country :=
  { code := "PK", name := "toy", currency := "PKR", year := "2025",
    compute := fun c => Out.make c "PK" "PKR" (pos (sumInts (c.adults.map (·.wages)) - 600000) / 10) }
def pk236C (cr : AdvanceCredit) : AdvanceTax :=
  { name := "Advance tax on sale of immovable property", source := .disposals [.home, .realEstate, .land],
    rates := [
      { ceilings := [(50000000, 450), (100000000, 500)], topBp := 550,
        statute := "ITO 2001 s. 236C; First Schedule Part IV Division X" }],
    credit := cr, creditStatute := "adjustable (s. 147, 168)" }
def pk236K : AdvanceTax :=
  { name := "Advance tax on purchase of immovable property", source := .purchases [.home, .realEstate, .land],
    rates := [
      { ceilings := [(50000000, 300), (100000000, 350)], topBp := 400, dateTo := "2025-06-30",
        statute := "ITO 2001 s. 236K; Division XVIII (to 30 June 2025)" },
      { ceilings := [(50000000, 150), (100000000, 200)], topBp := 250, dateFrom := "2025-07-01",
        statute := "ITO 2001 s. 236K; Division XVIII (Finance Act 2025, from 1 July 2025)" }],
    credit := .adjustable, creditStatute := "s. 236K (2) adjustable" }
def pkModel (ts : List AdvanceTax) : GlobalModel := (GlobalModel.ofCountry pkToy).withFamily (advanceTaxFamily "advance tax" ts)
def pkLine (wages : Nat) (extra : String) : CanonGlobal :=
  gl ("{\"id\":\"p\",\"schema\":\"global/2.0\",\"household\":{\"id\":\"p\",\"adults\":[{\"age\":45,\"wages\":" ++ toString wages ++ "}]}" ++ extra ++ "}")
def advOf (o : OutGlobal) : List (String × String × Int × Int × Int × Int) :=
  (o.charges.filter (·.statute != "1.x model")).map fun c => (c.oecd.code, c.event, c.base, c.gross, c.credit, c.due)
-- a home sold for 60 m: 5 % = 3 000 000 advance tax; the income tax of 300 000 on wages of 3 600 000 is credited:
-- 2 700 000 more is due (the year's 1100 total is the larger of the two, 3 000 000)
def pkSale : CanonGlobal := pkLine 3600000 ",\"disposals\":[{\"kind\":\"home\",\"proceeds\":60000000,\"cost\":20000000}]"
#guard advOf ((pkModel [pk236C .adjustable]).computeGlobal [] pkSale) == [("1100", "disposal 1 (home)", 60000000, 3000000, 300000, 2700000)]
#guard ((pkModel [pk236C .adjustable]).computeGlobal [] pkSale).totalOf .pit == 3000000
#guard ((pkModel [pk236C .refundable]).computeGlobal [] pkSale).totalOf .pit == 300000          -- excess refunded
#guard ((pkModel [pk236C .final]).computeGlobal [] pkSale).totalOf .pit == 3300000               -- not credited
-- the bands: the whole base at the rate of its band (up to 50 m 4.5 %, to 100 m 5 %, above 5.5 %)
#guard ([50000000, 50000001, 100000000, 100000001] : List Int).map ((pk236C .final).rates.head!.bpOf) == [450, 500, 500, 550]
-- income tax larger than the advance tax: all of it credited, nothing more due
#guard advOf ((pkModel [pk236C .adjustable]).computeGlobal [] (pkLine 60000000 ",\"disposals\":[{\"kind\":\"land\",\"proceeds\":10000000,\"cost\":1}]"))
  == [("1100", "disposal 1 (land)", 10000000, 450000, 450000, 0)]
-- the purchaser's rate by the date of the transaction (s. 236K before and after 1 July 2025)
#guard advOf ((pkModel [pk236K]).computeGlobal [] (pkLine 600000 ",\"purchases\":[{\"kind\":\"home\",\"price\":40000000,\"date\":\"2025-08-01\"}]"))
  == [("1100", "purchase 1 (home)", 40000000, 600000, 0, 600000)]
#guard advOf ((pkModel [pk236K]).computeGlobal [] (pkLine 600000 ",\"purchases\":[{\"kind\":\"home\",\"price\":40000000,\"assessed\":45000000,\"date\":\"2025-06-30\"}]"))
  == [("1100", "purchase 1 (home)", 45000000, 1350000, 0, 1350000)]
-- no date: the rate is not guessed: no charge, grade C
def pkUndated : CanonGlobal := pkLine 600000 ",\"purchases\":[{\"kind\":\"home\",\"price\":40000000}]"
#guard advOf ((pkModel [pk236K]).computeGlobal [] pkUndated) == []
#guard advanceTaxUnknown [pk236K] pkUndated == ["1100 Advance tax on purchase of immovable property: purchase 1 (home): the rate depends on the date of the transaction, not given (grade C)"]
-- seller and buyer in one family share the income tax to credit, in order (300 000 credited to the first)
#guard advOf ((pkModel [pk236C .adjustable, pk236K]).computeGlobal [] (pkLine 3600000
    ",\"disposals\":[{\"kind\":\"home\",\"proceeds\":10000000,\"cost\":1}],\"purchases\":[{\"kind\":\"land\",\"price\":10000000,\"date\":\"2025-09-01\"}]"))
  == [("1100", "disposal 1 (home)", 10000000, 450000, 300000, 150000), ("1100", "purchase 1 (land)", 10000000, 150000, 0, 150000)]
-- shown as a transaction tax (4400) if the model says so
#guard advOf ((pkModel [{ pk236C .adjustable with oecd := .transactions }]).computeGlobal [] pkSale) == [("4400", "disposal 1 (home)", 60000000, 3000000, 300000, 2700000)]
-- no such transaction: the model's output is unchanged (`advanceTaxFamily_noItems`)
#guard ((pkModel [pk236C .adjustable, pk236K]).computeGlobal [] (pkLine 3600000 "")).toJson.compress
  == ((GlobalModel.ofCountry pkToy).computeGlobal [] (pkLine 3600000 "")).toJson.compress

/-! ## 2.7.0 (R4-17-1): amounts fixed in a foreign currency, at an explicitly declared rate -/
-- the entity's rate: a number, or a record with its source and date (read exactly: 26.75 = 2675/100)
def fxLine (rates : String) (assets : String := "") : CanonGlobal :=
  gl ("{\"id\":\"f\",\"schema\":\"global/2.0\",\"household\":{\"id\":\"f\",\"adults\":[{\"age\":40}]}" ++ rates
    ++ (if assets.isEmpty then "" else ",\"assets\":[" ++ assets ++ "]") ++ "}")
#guard (fxInput? (fxLine ",\"fxRates\":{\"USD\":26.75}") "USD").map (fun r => (r.num, r.den, r.source)) == some (2675, 100, "input fxRates")
#guard (fxInput? (fxLine ",\"fxRates\":{\"USD\":{\"rate\":26.75,\"source\":\"RBZ interbank mid-rate\",\"date\":\"2025-06-30\"}}") "USD").map FxRate.note
  == some "USD amounts at 26.75 (RBZ interbank mid-rate, 2025-06-30)"
#guard fxInput? (fxLine ",\"fxRates\":{\"USD\":0}") "USD" == none                 -- not a positive rate: not given
#guard fxInput? (fxLine ",\"fxRates\":{\"USD\":26.75}") "ZAR" == none             -- another currency
#guard fxInput? (fxLine "") "USD" == none
-- in the household record works too (the request's form)
#guard ((fxInput? (gl "{\"id\":\"f\",\"household\":{\"id\":\"f\",\"adults\":[{\"age\":40}],\"fxRates\":{\"USD\":25.8}}}") "USD").map (·.rateText)) == some "25.8"
-- a rule-level rate is declared with its source and date (both fields are required by the structure)
def zwRbz : FxRate := { currency := "USD", num := 2690, den := 100, source := "RBZ average interbank rate 2025 (declared)", date := "2025-12-31" }
#guard (fxFor (fxLine "") "USD" (some zwRbz)).map (·.num) == some 2690             -- no input: the declared rate
#guard (fxFor (fxLine ",\"fxRates\":{\"USD\":26.75}") "USD" (some zwRbz)).map (·.num) == some 2675   -- the input wins
#guard fxFor (fxLine "") "USD" none == none                                         -- never a rate of its own
#guard fxFor (fxLine "") "EUR" (some zwRbz) == none                                 -- a rate for another currency
#guard zwRbz.convert 30 == 807 && zwRbz.toForeign 807 == 30
#guard fxUnknownLine "5200" "vehicle licence" "USD" == "5200 vehicle licence: amounts in USD and no exchange rate given (fxRates.USD) (grade C)"
-- a table in US$ converted exactly (one rounding): US$ 1.25 per started 100 kg = 125/100 per unit at 26.75
def usdTable : QtyTable := { step := 100, steps := [(0, 125)], den := 10000 }
#guard usdTable.amount 1350 == 17 && usdTable.amountFx { zwRbz with num := 2675 } 1350 == 468   -- 17.5 × 26.75 = 468.125
#guard (List.range 50).all fun q => usdTable.amountAt 1 1 (q * 97) == usdTable.amount (q * 97)
-- ZW-shaped vehicle licence (toy tariff in US$ by mass band, Third Schedule shape): the amounts are in US$
def zwLicence : VehicleTax :=
  { name := "vehicle licence", parts := [(.massKg, QtyTable.ofCeilings [(1000, 20), (2300, 30), (4600, 40)] 60)],
    currency := "USD", statute := "Vehicle Registration and Licensing Regulations Third Schedule Part II (SI 67 of 2024)" }
def zwCar : String := "{\"kind\":\"vehicle\",\"value\":1,\"massKg\":1500,\"firstRegYear\":2018}"
#guard (vehicleTaxCharges [zwLicence] (fxLine ",\"fxRates\":{\"USD\":26.75}" zwCar)).map (fun c => (c.due, c.statute))
  == [(802, "Vehicle Registration and Licensing Regulations Third Schedule Part II (SI 67 of 2024); USD amounts at 26.75 (input fxRates)")]
-- no rate given: no charge, grade C (never a built-in rate)
#guard (vehicleTaxCharges [zwLicence] (fxLine "" zwCar)).isEmpty
#guard vehicleTaxUnknown "vehicle licence" [zwLicence] (fxLine "" zwCar)
  == ["5200 vehicle licence: vehicle 1 (asset 1, car): fxRates.USD not given (grade C)"]
-- a declared rule-level rate: used when the entity gives none, named in the statute
#guard (vehicleTaxCharges [{ zwLicence with fxRate := some zwRbz }] (fxLine "" zwCar)).map (fun c => (c.due, c.statute))
  == [(807, "Vehicle Registration and Licensing Regulations Third Schedule Part II (SI 67 of 2024); USD amounts at 26.90 (RBZ average interbank rate 2025 (declared), 2025-12-31)")]
-- min and max are in the same currency: a US$ 50 cap, US$ 10 floor
#guard (vehicleTaxCharges [{ zwLicence with maxAmount := 25, minAmount := 10 }] (fxLine ",\"fxRates\":{\"USD\":26.75}" zwCar)).map (·.due) == [668]
-- a 2.6.0 tax is untouched (the theorems `vehicleTaxCharges_v26`, `vehicleTaxUnknown_v26`)
#guard (vehicleTaxCharges deKfz (veh (golf ++ "," ++ passat ++ "," ++ ev))).map Charge.toJson
  == (vehicleTaxCharges26 deKfz (veh (golf ++ "," ++ passat ++ "," ++ ev))).map Charge.toJson
#guard !dePetrol.uses27 && zwLicence.uses27

/-! ## 2.7.0 (R1 Europe pass 15, 1): an annual vehicle tax by days held (IS lög 39/1988 3. gr.) -/
-- IS-shaped bifreiðagjald (toy amount 30 000 a year), levied for two periods, 1 January - 30 June (181 days in 2025)
-- and 1 July - 31 December (184): a vehicle registered during a period pays from its registration day
def isGjald : VehicleTax :=
  { name := "bifreiðagjald", fixed := 30000, dayPeriods := [("01-01", "06-30"), ("07-01", "12-31")],
    statute := "lög 39/1988 3. gr." }
def isDays : VehicleTax := { isGjald with dayPeriods := [], proRataDays := true }
def isNew : String := "{\"kind\":\"vehicle\",\"value\":1,\"firstRegYear\":2025,\"firstRegDate\":\"2025-03-15\"}"
-- registered 15 March 2025 (day 73): period 1 108 of 181 days, period 2 whole: 30 000 × 108 / 362 + 15 000 = 8 950 + 15 000
#guard (vehicleTaxCharges [isGjald] (veh isNew)).map (fun c => (c.due, c.statute))
  == [(23950, "lög 39/1988 3. gr.; days held by period 108/181, 184/184")]
-- by days of the year: 292 / 365 × 30 000 = 24 000
#guard (vehicleTaxCharges [isDays] (veh isNew)).map (fun c => (c.due, c.statute))
  == [(24000, "lög 39/1988 3. gr.; 292/365 days of the year")]
-- held all year: the year's amount
#guard (vehicleTaxCharges [isGjald, isDays] (veh "{\"kind\":\"vehicle\",\"value\":1,\"firstRegYear\":2019}")).map (·.due) == [30000, 30000]
-- bought on 1 July 2025 (first registered 2019): the second period only; by days 184 / 365
#guard (vehicleTaxCharges [isGjald, isDays] (veh "{\"kind\":\"vehicle\",\"value\":1,\"firstRegYear\":2019,\"heldFrom\":\"2025-07-01\"}")).map (·.due)
  == [15000, 15123]
-- scrapped on 31 March 2025 (90 days): 30 000 × 90 / 362 = 7 458; by days 7 397
#guard (vehicleTaxCharges [isGjald, isDays] (veh "{\"kind\":\"vehicle\",\"value\":1,\"firstRegYear\":2019,\"heldTo\":\"2025-03-31\"}")).map (·.due)
  == [7458, 7397]
-- registered this year with the month only: never guessed (grade C, firstRegDay); a registration this year of a
-- vehicle first registered abroad in 2021 needs the day it was registered here ("heldFrom")
#guard (vehicleTaxCharges [isGjald] (veh "{\"kind\":\"vehicle\",\"value\":1,\"firstRegYear\":2025,\"firstRegMonth\":3}")).isEmpty
#guard vehicleTaxUnknown "bifreiðagjald" [isGjald] (veh "{\"kind\":\"vehicle\",\"value\":1,\"firstRegYear\":2025,\"firstRegMonth\":3}")
  == ["5200 bifreiðagjald: vehicle 1 (asset 1, car): firstRegDay not given (grade C)"]
#guard vehicleTaxUnknown "bifreiðagjald" [isGjald] (veh "{\"kind\":\"vehicle\",\"value\":1,\"firstRegYear\":2021,\"registeredThisYear\":true}")
  == ["5200 bifreiðagjald: vehicle 1 (asset 1, car): heldFrom not given (grade C)"]
-- six months held and no dates: the days are not located (grade C), where the 2.6.0 tax takes 6/12
#guard vehicleTaxUnknown "bifreiðagjald" [isDays] (veh "{\"kind\":\"vehicle\",\"value\":1,\"firstRegYear\":2019,\"months\":6}")
  == ["5200 bifreiðagjald: vehicle 1 (asset 1, car): heldFrom not given (grade C)"]
#guard (vehicleTaxCharges [{ isDays with proRataDays := false }] (veh "{\"kind\":\"vehicle\",\"value\":1,\"firstRegYear\":2019,\"months\":6}")).map (·.due) == [15000]
-- a period that is not "MM-DD": grade C, never a guess
#guard vehicleTaxUnknown "x" [{ isGjald with dayPeriods := [("01-01", "06-31")] }] (veh "{\"kind\":\"vehicle\",\"value\":1,\"firstRegYear\":2019}")
  == ["5200 x: vehicle 1 (asset 1, car): dayPeriods (\"MM-DD\") not given (grade C)"]
-- a registration tax is never prorated
#guard (vehicleTaxCharges [{ isDays with occasion := .registration }] (veh isNew)).map (·.due) == [30000]
#guard VehicleTax.periodsAmount 30001 0 364 [(0, 180), (181, 364)] == 30001

/-! ## 2.7.0 (R1 Europe pass 15, 2): a part only for the first N months after first registration (SE 2 kap. 9 a §) -/
-- SE-shaped fordonsskatt (toy figures): 360 + 22 per g CO2 above 75; for the first 36 months the CO2 amount is 107 per g
-- (132 above 125) instead: the window part adds the difference, 85 per g above 75 and 110 above 125
def seSkatt : VehicleTax :=
  { name := "fordonsskatt", fixed := 360,
    parts := [(.co2GKm, { steps := [(75, 22)] }), (.co2GKm, { steps := [(75, 85), (125, 110)] })],
    partWindows := [{ part := 1, months := 36 }], statute := "vägtrafikskattelag 2006:227 2 kap. 7, 9 a §§" }
def seCar (reg : String) : CanonGlobal := veh ("{\"kind\":\"vehicle\",\"value\":1,\"co2GKm\":140" ++ reg ++ "}")
-- first registered April 2022: the window ends March 2025, 3 months of 2025: 1 790 + 5 900 × 3 / 12 = 3 265
#guard (vehicleTaxCharges [seSkatt] (seCar ",\"firstRegYear\":2022,\"firstRegMonth\":4")).map (fun c => (c.due, c.statute))
  == [(3265, "vägtrafikskattelag 2006:227 2 kap. 7, 9 a §§; part 2: 3/12 (first 36 months)")]
-- June 2023: the whole of 2025 is inside: 1 790 + 5 900
#guard (vehicleTaxCharges [seSkatt] (seCar ",\"firstRegYear\":2023,\"firstRegMonth\":6")).map (·.due) == [7690]
-- 2021 with no month: the window ended in 2024 whatever the month: decided, 1 790
#guard (vehicleTaxCharges [seSkatt] (seCar ",\"firstRegYear\":2021")).map (·.due) == [1790]
-- 2022 with no month: the window ends inside 2025 (grade C, firstRegMonth)
#guard (vehicleTaxCharges [seSkatt] (seCar ",\"firstRegYear\":2022")).isEmpty
#guard vehicleTaxUnknown "fordonsskatt" [seSkatt] (seCar ",\"firstRegYear\":2022")
  == ["5200 fordonsskatt: vehicle 1 (asset 1, car): firstRegMonth not given (grade C)"]
-- no year: grade C, firstRegYear
#guard vehicleTaxUnknown "fordonsskatt" [seSkatt] (seCar "") == ["5200 fordonsskatt: vehicle 1 (asset 1, car): firstRegYear not given (grade C)"]
-- new in July 2025, held 6 months: the other parts × 6/12 (895), the window part for its 6 months (2 950)
#guard (vehicleTaxCharges [seSkatt] (seCar ",\"firstRegYear\":2025,\"firstRegMonth\":7,\"months\":6")).map (·.due) == [3845]
-- counted from the month after registration (fromNextMonth): April 2022 -> May 2022 - April 2025, 4 months
#guard (vehicleTaxCharges [{ seSkatt with partWindows := [{ part := 1, months := 36, fromNextMonth := true }] }]
    (seCar ",\"firstRegYear\":2022,\"firstRegMonth\":4")).map (·.due) == [3756]
-- sold on 28 February 2025 (heldTo): the window part for January-February only, 5 900 × 2 / 12 = 983
#guard (vehicleTaxCharges [seSkatt] (seCar ",\"firstRegYear\":2022,\"firstRegMonth\":4,\"heldTo\":\"2025-02-28\"")).map (·.due) == [1790 + 983]
#guard winMonthsIn 2025 (2022 * 12 + 3) 36 1 12 == 3

/-! ## 2.7.0 (R1 Europe pass 15, 3): zone value and coefficients on real estate (GR ENFIA shape) -/
def grAssets (a : String) : CanonGlobal := hh "[]" (",\"assets\":[" ++ a ++ "]")
def grFlat : String := "{\"kind\":\"home\",\"value\":150000,\"areaM2\":100,\"zoneValueM2\":1200,\"buildYear\":1990,\"floor\":4,\"frontages\":1}"
#guard assetZoneValueM2 (grAssets grFlat) 0 == 1200 && assetZoneValueM2 (grAssets grFlat) 1 == -1
#guard [AssetFact.areaM2, .zoneValueM2, .buildYear, .age, .floor, .frontages, .field "nope"].map (assetFact? (grAssets grFlat) 0)
  == [some 100, some 1200, some 1990, some 35, some 4, some 1, none]
-- ENFIA-shaped principal tax (toy rates): € per m² by zone-price band × age, floor and frontage coefficients
def enfia : ZoneTax :=
  { name := "ΕΝΦΙΑ κύριος φόρος", kinds := [.home, .realEstate],
    base := .perArea [(0, QtyTable.perUnit 200 100), (551, QtyTable.perUnit 280 100), (1051, QtyTable.perUnit 290 100)],
    coefs := [{ fact := .age, bands := [(0, 10000), (25, 9000)] }, { fact := .floor, bands := [(0, 10000), (3, 10200)] },
              { fact := .frontages, bands := [(0, 10000), (2, 10100)] }],
    statute := "ν. 4223/2013 άρθ. 4 (shape)" }
-- 100 m² × 2,90 × 0,90 × 1,02 × 1,00 = 266,22 → 266 (one rounding)
#guard (enfia.charges (grAssets grFlat)).map (fun c => (c.oecd.code, c.event, c.base, c.due)) == [("4100", "asset 1", 100, 266)]
-- a fact missing: no charge, grade C (never guessed)
def grNoYear : String := "{\"kind\":\"home\",\"value\":1,\"areaM2\":80,\"zoneValueM2\":700,\"floor\":1,\"frontages\":1}"
#guard (enfia.charges (grAssets grNoYear)).isEmpty
#guard enfia.unknown (grAssets (grNoYear ++ "," ++ "{\"kind\":\"realEstate\",\"value\":1,\"areaM2\":50}"))
  == ["4100 ΕΝΦΙΑ κύριος φόρος: asset 1 (home): age not given (grade C)",
      "4100 ΕΝΦΙΑ κύριος φόρος: asset 2 (realEstate): zoneValueM2, age, floor, frontages not given (grade C)"]
-- a table on the objective value (area × zone value × coefficients): 100 × 1 200 × 0,918 = 110 160; 0,1 % = 110
def objTax : ZoneTax := { enfia with name := "objective value tax", base := .onValue (QtyTable.perUnit 1 1000) }
#guard (objTax.charges (grAssets grFlat)).map (fun c => (c.base, c.due)) == [(110160, 110)]
-- land with its own coefficients (none), by kind
def enfiaLand : ZoneTax :=
  { enfia with
    name := "ΕΝΦΙΑ οικόπεδα", kinds := [.land], coefsFor := (fun a => if a.kind == .land then some [] else none),
    base := .perArea [(0, QtyTable.perUnit 1 100), (1001, QtyTable.perUnit 5 100)] }
#guard (enfiaLand.charges (grAssets "{\"kind\":\"land\",\"value\":1,\"areaM2\":600,\"zoneValueM2\":1500}")).map (·.due) == [30]
#guard enfia.family.covers.map (·.code) == ["4100"]

/-! ## 2.7.0 (FT reviewer 7, IMPROVE_FT R5-6): a date window on stacking rules (LU art. 99ter, 2025) -/
-- a quarter of the global rate for sales to 30 September 2025, half from 1 October (shape on the ZA toy, whose line
-- gives `detail.taxableIncome`); both rules read the rate of the whole stack (`rateFromStack`)
def luQuarter : StackRule :=
  { halfGlobal with name := "art. 99ter (quarter)", shareBp := 2500, dateTo := "2025-09-30", rateFromStack := true }
def luHalf : StackRule :=
  { halfGlobal with name := "art. 99ter (half)", shareBp := 5000, dateFrom := "2025-10-01", rateFromStack := true }
def luModel : GlobalModel := zaBase.withStack [luQuarter, luHalf]
def luSales (d1 d2 : String) : CanonGlobal :=
  zaLine "[{\"age\":40,\"wages\":600000}]"
    ("[{\"kind\":\"unlistedShares\",\"proceeds\":340000,\"cost\":100000,\"stakeBp\":2000" ++ d1 ++ "},"
      ++ "{\"kind\":\"unlistedShares\",\"proceeds\":200000,\"cost\":100000,\"stakeBp\":2000" ++ d2 ++ "}]")
def luBoth : CanonGlobal := luSales ",\"date\":\"2025-05-10\"" ",\"date\":\"2025-11-03\""
-- the whole stack: taxable income 940 000, income tax 267 684
#guard jsonIncomeTax (zaBase.pit [] (StackField.selfEmployment.addTo luBoth.household 0 340000)) == 267684
-- sold 10 May: 240 000 × ¼ × 267 684 / 940 000 = 17 086; sold 3 November: 100 000 × ½ × 267 684 / 940 000 = 14 238
#guard stackedOf (luModel.computeGlobal [] luBoth)
  == [("disposal 1 (unlistedShares)", 240000, 240000, 17086, "central"), ("disposal 2 (unlistedShares)", 100000, 100000, 14238, "central")]
-- without `rateFromStack` the first rule reads the line with its own amount only (840 000: 60 000 × 227 042 / 840 000)
#guard stackedOf ((zaBase.withStack [{ luQuarter with rateFromStack := false }, { luHalf with rateFromStack := false }]).computeGlobal [] luBoth)
  == [("disposal 1 (unlistedShares)", 240000, 240000, 16217, "central"), ("disposal 2 (unlistedShares)", 100000, 100000, 14238, "central")]
-- an undated sale that the windows need: no charge, grade C, never guessed
def luUndated : CanonGlobal := luSales ",\"date\":\"2025-05-10\"" ""
#guard stackedOf (luModel.computeGlobal [] luUndated) == []
#guard (luModel.computeGlobal [] luUndated).unsupported
  == ["1100 art. 99ter (quarter): disposal 2 (unlistedShares) has no date (the rule takes items dated to 2025-09-30) (grade C)",
      "1100 art. 99ter (half): stacked on an earlier rule that was not priced (grade C)"]
-- both in the first window: the half rule has nothing (skipped, no charge)
#guard stackedOf (luModel.computeGlobal [] (luSales ",\"date\":\"2025-05-10\"" ",\"date\":\"2025-09-30\""))
  == [("disposal 1 (unlistedShares), disposal 2 (unlistedShares)", 340000, 340000, 24205, "central")]
-- a rule without a window is the 2.6.0 rule, dated or not
#guard (hgModel.computeGlobal [] luUndated).toJson.compress == ((zaBase.withStack [{ halfGlobal with dateFrom := "", dateTo := "" }]).computeGlobal [] luUndated).toJson.compress
#guard !halfGlobal.hasWindow && luQuarter.hasWindow

/-! ## 2.7.0 (R4-18-1): the employer's turnover (NG Industrial Training Fund) -/
-- ITF (Amendment) Act 2011 s. 6 (1): 1 % of payroll for an employer of five or more employees, or of fewer than five with
-- a turnover of N50 m or more
def ngItf : EmployerLevy :=
  { name := "ITF contribution",
    rules := [
      { rateBp := 100, tests := [.employeesAtLeast 5], ifUnknown := .general, statute := "ITF Act s. 6 (1) (5 or more employees)" },
      { rateBp := 100, tests := [.employeesAtMost 4, .turnoverAtLeast 50000000], ifUnknown := .gradeC,
        statute := "ITF Act s. 6 (1) (turnover N50 m or more)" }] }
def ngAdult (facts : String) : CanonGlobal := empLine ("[{\"age\":35,\"wages\":100000" ++ facts ++ "}]")
#guard employerOf (ngAdult ",\"employerTurnover\":60000000") 0 == { turnover := 60000000 }
#guard (ngItf.charges (ngAdult ",\"employerEmployees\":3,\"employerTurnover\":60000000")).map (fun c => (c.due, c.statute))
  == [(1000, "ITF Act s. 6 (1) (turnover N50 m or more)")]
#guard (ngItf.charges (ngAdult ",\"employerEmployees\":3,\"employerTurnover\":10000000")).isEmpty   -- outside the Act
#guard (ngItf.charges (ngAdult ",\"employerEmployees\":12")).map (·.due) == [1000]
-- fewer than five and no turnover given: grade C, never guessed
#guard ngItf.unknown (ngAdult ",\"employerEmployees\":3")
  == ["3000 ITF contribution: adult 1 wages: the rate depends on employerTurnover, not given (ITF Act s. 6 (1) (turnover N50 m or more)) (grade C)"]
#guard [EmployerTest.turnoverAtLeast 5, .turnoverBelow 5].map (·.eval {}) == [none, none]
#guard (EmployerTest.turnoverBelow 50).eval { turnover := 49 } == some true
-- a company entity's own turnover (`companies := true`)
#guard (({ ngItf with companies := true } : EmployerLevy).charges (gl "{\"id\":\"c\",\"entity\":\"company\",\"company\":{\"profit\":1,\"payroll\":2000000,\"employees\":3,\"turnover\":80000000}}")).map (·.due) == [20000]

/-! ## 2.7.0 (R4-18-2): a sector taxed under another Act (NA petroleum) -/
def naCit : SectorCorp :=
  { general := gyGeneral, statute := "Income Tax Act 1981 Schedule 4 (shape)", ifAbsent := .general,
    outside := [{ sectors := ["petroleum"], statute := "the Petroleum (Taxation) Act 1991" }] }
#guard (naCit.citCharges (gyCo 1000000 ",\"sector\":\"petroleum\"")).isEmpty
#guard naCit.unknown "Income tax (companies)" (gyCo 1000000 ",\"sector\":\"petroleum\"")
  == ["1200 Income tax (companies): company.sector is taxed under the Petroleum (Taxation) Act 1991, not this tax (grade C)"]
#guard (naCit.citCharges (gyCo 1000000 ",\"sector\":\"mining\"")).map (·.due) == [250000]
#guard naCit.unknown "Income tax (companies)" (gyCo 1000000 ",\"sector\":\"mining\"") == []
-- no sector given: the declared absent rule, as before
#guard (naCit.citCharges (gyCo 1000000 "")).map (·.due) == [250000]
-- without `outside` the 2.6.0 charges (`citCharges_noOutside`)
#guard ((gyCit .general).citCharges (gyCo 1000000 ",\"sector\":\"telecom\"")).map (·.due) == [450000]

/-! ## 2.7.0 (R4-18-3): stacking with an elective flat rate (GH Act 896 First Schedule para 1 (3)) -/
-- shown on the ZA toy: the gain in chargeable income, or 25 % at the individual's election (the lower)
def ghGain : StackRule :=
  { name := "gain on an investment asset", statute := "Act 896 First Schedule para 1 (3) (Act 1094) (shape)",
    gainKinds := [.unlistedShares], into := .selfEmployment, electFlatBp := 2500 }
-- wages 600 000, gain 240 000: stacked 91 410, 25 % = 60 000: the election is taken
#guard stackedOf ((zaBase.withStack [ghGain]).computeGlobal [] hgLine) == [("disposal 1 (unlistedShares)", 240000, 240000, 60000, "central")]
#guard ((zaBase.withStack [ghGain]).computeGlobal [] hgLine).charges.getLast?.map (·.statute)
  == some "Act 896 First Schedule para 1 (3) (Act 1094) (shape); elective flat rate 2500 bp taken (lower than the stacked tax)"
-- no other income: the stacked tax (26 197) is lower than 25 % (60 000): no election
#guard stackedOf ((zaBase.withStack [ghGain]).computeGlobal [] (zaLine "[{\"age\":40,\"wages\":0}]" "[{\"kind\":\"unlistedShares\",\"proceeds\":340000,\"cost\":100000}]"))
  == [("disposal 1 (unlistedShares)", 240000, 240000, 26197, "central")]
#guard stackedOf ((zaBase.withStack [{ ghGain with electFlatBp := -1 }]).computeGlobal [] hgLine)
  == [("disposal 1 (unlistedShares)", 240000, 240000, 91410, "central")]

/-! ## 2.8.0 (OECD 5123): customs import duties, a CARICOM-style tariff (toy rates: the shape, not a country's figures) -/
-- MFN lines by HS heading (the longest prefix wins), a CARICOM preference keyed on origin, VAT 12,5 % on the duty-inclusive
-- value: a Trinidad-and-Tobago-shaped Common External Tariff
def caricom : List String := ["AG", "BB", "BS", "BZ", "DM", "GD", "GY", "HT", "JM", "KN", "LC", "MS", "SR", "TT", "VC"]
def cetTariff : TariffRule :=
  { name := "import duty (CET, shape)", country := "TT", vatBp := 1250,
    lines := [{ hs := "22", adValoremBp := 2000 }, { hs := "2203", adValoremBp := 4000 },
              { hs := "2204", adValoremBp := 2000 },
              { hs := "2208", adValoremBp := 2000, perUnitNum := 6, higherOf := true,
                statute := "CET 2208 (shape): 20 % or 6 per litre, the higher" },
              { hs := "1701", perKgNum := 50, perKgDen := 100 }, { hs := "6109", adValoremBp := 2000 }],
    preferences := [{ name := "CARICOM (Revised Treaty of Chaguaramas art. 164)", partners := caricom, hsExcept := ["2208"] }],
    statute := "Customs Act Chap. 78:01 First Schedule (shape)" }
def bkt (lines : String) : CanonGlobal := hh ("[" ++ lines ++ "]")
def beerLine (extra : String) : String := "{\"good\":\"beer\",\"amount\":1350,\"quantity\":6000,\"abvBp\":480" ++ extra ++ "}"
-- beer from the United States, HS 2203.00: value = (1 350 / 1,125) / 1,40 = 857, duty 40 % = 342
#guard (cetTariff.charges (bkt (beerLine ",\"hs\":\"2203.00\",\"origin\":\"US\""))).map (fun c => (c.oecd.code, c.event, c.base, c.due, c.statute))
  == [("5120", "line 1 (beer)", 857, 342, "Customs Act Chap. 78:01 First Schedule (shape); HS 2203 (MFN)")]
-- from Jamaica (CARICOM): duty-free, the value the whole price before VAT
#guard (cetTariff.charges (bkt (beerLine ",\"hs\":\"2203\",\"origin\":\"jm\""))).map (fun c => (c.base, c.due, c.statute))
  == [(1200, 0, "Customs Act Chap. 78:01 First Schedule (shape); HS 2203: CARICOM (Revised Treaty of Chaguaramas art. 164) preference, origin JM")]
-- domestic lines pay nothing (origin "domestic", the model's own code, or no origin and not imported)
#guard (cetTariff.charges (bkt (beerLine ",\"hs\":\"2203\",\"origin\":\"domestic\"" ++ "," ++ beerLine ",\"hs\":\"2203\",\"origin\":\"TT\"" ++ "," ++ beerLine ""))).isEmpty
#guard (cetTariff.unknown (bkt (beerLine ",\"hs\":\"2203\",\"origin\":\"domestic\"" ++ "," ++ beerLine ""))).isEmpty
-- the longest heading wins: wine 2204 at 20 %, other beverages of chapter 22 at 20 %, beer 2203 at 40 %
#guard (cetTariff.charges (bkt "{\"good\":\"wine\",\"amount\":1125,\"hs\":\"220421\",\"origin\":\"CL\"}")).map (·.due) == [166]
#guard (cetTariff.charges (bkt "{\"good\":\"nonAlcoholic\",\"amount\":1125,\"hs\":\"2202\",\"origin\":\"US\"}")).map (fun c => (c.due, c.statute))
  == [(166, "Customs Act Chap. 78:01 First Schedule (shape); HS 22 (MFN)")]
-- spirits: 20 % or 6 per litre, the higher; the CARICOM preference excludes 2208, so Barbados rum pays MFN
-- 2 750 for 0,7 l: net 2 444, value 2 036, 20 % = 407 (above 6 × 0,7 = 4)
#guard (cetTariff.charges (bkt "{\"good\":\"spirits\",\"amount\":2750,\"quantity\":700,\"abvBp\":4000,\"hs\":\"2208.40\",\"origin\":\"BB\"}")).map (fun c => (c.base, c.due, c.statute))
  == [(2036, 407, "Customs Act Chap. 78:01 First Schedule (shape); CET 2208 (shape): 20 % or 6 per litre, the higher; HS 2208 (MFN)")]
-- a cheap litre: 30 → net 26; 20 % of 21 = 4 < 6, so the specific 6 on a value of 26 − 6 = 20
#guard (cetTariff.charges (bkt "{\"good\":\"spirits\",\"amount\":30,\"quantity\":1000,\"hs\":\"2208\",\"origin\":\"US\"}")).map (fun c => (c.base, c.due)) == [(20, 6)]
-- a specific duty per kg: sugar 0,50 per kg on the line's mass (no other part): 25 kg = 12
#guard (cetTariff.charges (bkt "{\"good\":\"food\",\"amount\":400,\"massG\":25000,\"hs\":\"1701.99\",\"origin\":\"BR\"}")).map (·.due) == [12]
-- the customs value given on the line: 40 % of 500 = 200
#guard (cetTariff.charges (bkt (beerLine ",\"hs\":\"2203\",\"origin\":\"US\",\"customsValue\":500"))).map (fun c => (c.base, c.due)) == [(500, 200)]
-- the duty outside the VAT base: value = 1 350 / (1 + 0,125 + 0,40) = 885, duty 354; the basket VAT over-counts 354 × 0,125/1,125 = 39
def cetNoVat : TariffRule := { cetTariff with dutyInVatBase := false }
#guard (cetNoVat.charges (bkt (beerLine ",\"hs\":\"2203\",\"origin\":\"US\""))).map (fun c => (c.base, c.due)) == [(885, 354)]
#guard cetNoVat.vatOverstated (bkt (beerLine ",\"hs\":\"2203\",\"origin\":\"US\"")) == 39
#guard cetTariff.vatOverstated (bkt (beerLine ",\"hs\":\"2203\",\"origin\":\"US\"")) == 0
-- missing facts: never guessed (grade C)
def cetBad : CanonGlobal := bkt (beerLine ",\"imported\":true" ++ "," ++ beerLine ",\"hs\":\"22\",\"origin\":\"US\"" ++ ","
  ++ beerLine ",\"hs\":\"2203\",\"imported\":true" ++ "," ++ beerLine ",\"hs\":\"9999\",\"origin\":\"US\"" ++ ","
  ++ "{\"good\":\"food\",\"amount\":400,\"hs\":\"1701\",\"origin\":\"BR\"}" ++ "," ++ beerLine ",\"hs\":\"22O3\",\"origin\":\"US\"" ++ ","
  ++ beerLine ",\"hs\":\"2203\",\"origin\":\"domestic\",\"imported\":true")
#guard (cetTariff.charges cetBad).isEmpty
#guard cetTariff.unknown cetBad ==
  ["5120 import duty (CET, shape): line 1 (beer): imported and no hs given (grade C)",
   "5120 import duty (CET, shape): line 2 (beer): hs 22 is coarser than the tariff (lines 2203, 2204, 2208 differ) (grade C)",
   "5120 import duty (CET, shape): line 3 (beer): origin not given (a preference may apply: CARICOM (Revised Treaty of Chaguaramas art. 164)) (grade C)",
   "5120 import duty (CET, shape): line 4 (beer): no tariff line for hs 9999 (grade C)",
   "5120 import duty (CET, shape): line 5 (food): massG not given (the duty on hs 1701 is specific) (grade C)",
   "5120 import duty (CET, shape): line 6 (beer): hs \"22O3\" is not an HS code of 2, 4, 6, 8 or 10 digits (grade C)",
   "5120 import duty (CET, shape): line 7 (beer): \"imported\": true but origin domestic (grade C)"]
-- the model's declared convention: no origin = MFN (noted); a rate for every other good (5 % of 1 142 = 57)
def cetMfn : TariffRule := { cetTariff with mfnIfOriginUnknown := true, otherBp := 500 }
#guard (cetMfn.charges (bkt (beerLine ",\"hs\":\"2203\",\"imported\":true" ++ "," ++ beerLine ",\"hs\":\"9999\",\"origin\":\"US\""))).map (fun c => (c.due, c.statute))
  == [(342, "Customs Act Chap. 78:01 First Schedule (shape); HS 2203 (MFN); origin not given: MFN, the model's convention (CARICOM (Revised Treaty of Chaguaramas art. 164) not applied)"),
      (57, "Customs Act Chap. 78:01 First Schedule (shape); HS 9999: other goods 500 bp")]
-- the top-level `"importedGoods"` (2.1.0) marks a line imported too
#guard (cetTariff.unknown (hh ("[" ++ beerLine "" ++ "]") ",\"importedGoods\":[\"beer\"]")).length == 1
-- a preference that is not lower than MFN is not claimed; a preference rate by heading (`byHs`)
def cetPref2 : TariffRule :=
  { cetTariff with preferences := [{ name := "FTA", partners := ["CR"], rateBp := 5000, byHs := [("2204", 500)] }] }
#guard (cetPref2.charges (bkt (beerLine ",\"hs\":\"2203\",\"origin\":\"CR\"" ++ "," ++ "{\"good\":\"wine\",\"amount\":1125,\"hs\":\"2204\",\"origin\":\"CR\"}"))).map (fun c => (c.due, c.statute))
  == [(342, "Customs Act Chap. 78:01 First Schedule (shape); HS 2203 (MFN) (lower than the FTA rate)"),
      (47, "Customs Act Chap. 78:01 First Schedule (shape); HS 2204: FTA preference, origin CR")]
-- the family and the model wrapper
#guard (customsFamily [cetTariff]).covers.map (·.code) == ["5120"]
#guard hsBest [("22", 1), ("2203", 2), ("220300", 3), ("2204", 4)] "22030010" == some ("220300", 3)
#guard hsBest [("22", 1), ("2203", 2)] "2204" == some ("22", 1)
#guard hsNormalize "2203.00" == some "220300" && hsNormalize "220" == none && hsNormalize "0901" == some "0901"
#guard (CustomsX.ofJson (Json.mkObj [("hs", Json.num 2203), ("origin", "usa"), ("customsValue", Json.num (-5))])) == { hsRaw := "2203", origin := "USA" }

/-! ## 2.8.0: local taxes at the municipality's rate (`localRates`) -/
-- canonical keys (entity fields v4): "propertyTax", "businessTax", "vehicleTax"; any other key works the same
-- a municipal property tax inside a national range: PT IMI on urban property, CIMI art. 112.º n.º 1 c): 0,3 % to 0,45 % of
-- the valor patrimonial tributário, the municipality fixing the rate (the Lisboa entry below is an input of the case)
def ptImi : LocalTax :=
  { key := "propertyTax", name := "IMI (prédios urbanos)", base := .assets [.home, .realEstate], unit := .percent,
    minNum := 3, minDen := 10, maxNum := 45, maxDen := 100, statute := "CIMI art. 112.º n.º 1 c)" }
def imiHome (rate : String) (assetExtra : String := "") : CanonGlobal :=
  hh "[]" (",\"assets\":[{\"kind\":\"home\",\"value\":350000,\"assessed\":200000" ++ assetExtra ++ "}]" ++ rate)
def lisboa : String :=
  ",\"localRates\":{\"propertyTax\":{\"rate\":0.3,\"source\":\"deliberação da Assembleia Municipal (case input)\",\"date\":\"2024-12-17\",\"municipality\":\"Lisboa\"}}"
-- 200 000 × 0,3 % = 600, on the assessed value; the statute names the rate and where it comes from
#guard (ptImi.charges (imiHome lisboa)).map (fun c => (c.oecd.code, c.level.name, c.base, c.relieved, c.due, c.statute))
  == [("4100", "local", 200000, 200000, 600,
       "CIMI art. 112.º n.º 1 c); rate 0.3 % (Lisboa, deliberação da Assembleia Municipal (case input), 2024-12-17; localRates)")]
-- the rate inside the household record, as a plain number; an asset's own rate wins for that asset
#guard (ptImi.charges (gl "{\"id\":\"h\",\"schema\":\"global/2.0\",\"household\":{\"id\":\"h\",\"adults\":[{\"age\":40}],\"localRates\":{\"propertyTax\":0.45}},\"assets\":[{\"kind\":\"home\",\"value\":1,\"assessed\":200000}]}")).map (·.due) == [900]
#guard (ptImi.charges (imiHome lisboa ",\"localRates\":{\"propertyTax\":0.4}")).map (·.due) == [800]
-- outside the statutory range: flagged, never used nor clamped
#guard (ptImi.charges (imiHome ",\"localRates\":{\"propertyTax\":0.5}")).isEmpty
#guard ptImi.unknown (imiHome ",\"localRates\":{\"propertyTax\":0.5}")
  == ["4100 IMI (prédios urbanos): asset 1: localRates 0.5 % is outside the statutory range (within 0.3 % to 0.45 %) (grade C)"]
-- no rate and none declared: grade C (the kernel has no rate of its own)
#guard (ptImi.charges (imiHome "")).isEmpty
#guard ptImi.unknown (imiHome "") == ["4100 IMI (prédios urbanos): asset 1: localRates.propertyTax not given (the municipality's rate, within 0.3 % to 0.45 %) (grade C)"]
#guard ptImi.unknown (imiHome ",\"localRates\":{\"propertyTax\":\"x\"}") == ["4100 IMI (prédios urbanos): asset 1: localRates.propertyTax is not a rate (a number ≥ 0 or {rate, source, date, municipality}) (grade C)"]
-- a declared default municipality rate (its own source and date): used for an asset with no region or in that municipality;
-- an asset in another municipality: grade C
def ptImiDflt : LocalTax :=
  { ptImi with default := some { municipality := "Lisboa", num := 3, den := 10, source := "deliberação AM Lisboa (shape)", date := "2024-12-17" } }
#guard (ptImiDflt.charges (imiHome "")).map (fun c => (c.due, c.statute))
  == [(600, "CIMI art. 112.º n.º 1 c); rate 0.3 % (Lisboa, deliberação AM Lisboa (shape), 2024-12-17; the model's default municipality Lisboa)")]
#guard (ptImiDflt.charges (imiHome "" ",\"region\":\"Lisboa\"")).map (·.due) == [600]
#guard (ptImiDflt.charges (imiHome "" ",\"region\":\"Porto\"")).isEmpty
#guard ptImiDflt.unknown (imiHome "" ",\"region\":\"Porto\"")
  == ["4100 IMI (prédios urbanos): asset 1: no declared rate for municipality Porto: localRates.propertyTax not given, within 0.3 % to 0.45 % (grade C)"]
-- the entity's rate wins over the declared default
#guard (ptImiDflt.charges (imiHome ",\"localRates\":{\"propertyTax\":0.45}")).map (·.due) == [900]
-- framework only: the range, no number
def ptImiFw : LocalTax := LocalTax.framework "propertyTax" "IMI (prédios urbanos)" (.assets [.home, .realEstate]) .percent 3 10 45 100 "CIMI art. 112.º n.º 1 c)"
#guard (ptImiFw.charges (imiHome lisboa)).isEmpty
#guard ptImiFw.unknown (imiHome lisboa)
  == ["4100 IMI (prédios urbanos): asset 1: framework only: the municipality sets the rate, within 0.3 % to 0.45 %; not computed (grade C)"]
-- DE Grundsteuer B (GrStG §§ 13, 15, 25): Grundsteuerwert × 0,31 ‰ = Messbetrag, × the Hebesatz: 300 000 → 93 × 470 % = 437,
-- exactly the 2.0 `twoStage`
def deGrSt : LocalTax :=
  { key := "propertyTax", name := "Grundsteuer B", base := .assets [.home, .realEstate], ratioNum := 31, ratioDen := 100000,
    statute := "GrStG §§ 13, 15, 25" }
def berlin : String := ",\"localRates\":{\"propertyTax\":{\"rate\":470,\"source\":\"Hebesatz (case input)\",\"date\":\"2025-01-01\",\"municipality\":\"Berlin\"}}"
#guard (deGrSt.charges (hh "[]" (",\"assets\":[{\"kind\":\"home\",\"value\":300000}]" ++ berlin))).map (fun c => (c.base, c.relieved, c.due))
  == [(300000, 93, twoStage {} 31 100000 47000 300000)]
#guard twoStage {} 31 100000 47000 300000 == 437
-- the GewSt (GewStG §§ 11, 16 (4): Hebesatz at least 200 %) on an amount the model computes, reading the pilot's `deHebesatz`
def deGewSt : LocalTax :=
  { key := "businessTax", name := "Gewerbesteuer", unit := .percent, ratioNum := 35, ratioDen := 1000, minNum := 200,
    base := .amount (fun g => if g.entity == .company then some g.company.profit else none), inputAlias := "deHebesatz",
    oecd := .cit, statute := "GewStG §§ 11, 16" }
def deCo (extra : String) : CanonGlobal :=
  gl ("{\"id\":\"c\",\"entity\":\"company\",\"company\":{\"profit\":1000000,\"turnover\":5000000}" ++ extra ++ "}")
#guard (deGewSt.charges (deCo ",\"deHebesatz\":490")).map (fun c => (c.oecd.code, c.event, c.relieved, c.due, c.statute))
  == [("1200", "year", 35000, 171500, "GewStG §§ 11, 16; rate 490 % (input; deHebesatz)")]
#guard (deGewSt.charges (deCo ",\"localRates\":{\"businessTax\":410},\"deHebesatz\":490")).map (·.due) == [143500]
#guard deGewSt.unknown (deCo ",\"deHebesatz\":150") == ["1200 Gewerbesteuer: year: deHebesatz 150 % is outside the statutory range (at least 200 %) (grade C)"]
#guard deGewSt.unknown (deCo "") == ["1200 Gewerbesteuer: year: localRates.businessTax not given (the municipality's rate, at least 200 %) (grade C)"]
#guard (deGewSt.charges (hh "[]" ",\"deHebesatz\":490")).isEmpty      -- not a company: the amount does not apply
-- a tax per m² at the municipality's rate (per unit): 120 m² × 1,50 = 180; no area: grade C
def areaLocal : LocalTax := { key := "propertyTax", name := "land tax", base := .area [.land], unit := .perUnit, statute := "(shape)" }
#guard (areaLocal.charges (hh "[]" ",\"assets\":[{\"kind\":\"land\",\"value\":1,\"areaM2\":120}],\"localRates\":{\"propertyTax\":1.5}")).map (·.due) == [180]
#guard areaLocal.unknown (hh "[]" ",\"assets\":[{\"kind\":\"land\",\"value\":1}],\"localRates\":{\"propertyTax\":1.5}") == ["4100 land tax: asset 1 (land: areaM2 not given) (grade C)"]
#guard (localTaxFamily [ptImi, deGewSt]).covers.map (·.code) == ["4100", "1200"]

/-! ## 2.8.0 (R1 Europe pass 17): an undated item the rule taxes at 0; coefficients chosen from the asset's record -/
-- LU art. 99ter windows with an undated sale of the main home, exempt whatever the date: with `undatedIfTaxable` it no longer
-- blocks the windows (2.7.0: grade C for every LU gains line)
def luQ8 : StackRule := { luQuarter with gainKinds := [.unlistedShares, .home], gainRule := { mainHomeExempt := true } }
def luH8 : StackRule := { luHalf with gainKinds := [.unlistedShares, .home], gainRule := { mainHomeExempt := true } }
def luHomeLine : CanonGlobal :=
  zaLine "[{\"age\":40,\"wages\":600000}]"
    ("[{\"kind\":\"unlistedShares\",\"proceeds\":340000,\"cost\":100000,\"stakeBp\":2000,\"date\":\"2025-05-10\"},"
      ++ "{\"kind\":\"home\",\"proceeds\":500000,\"cost\":300000,\"mainHome\":true}]")
#guard stackedOf ((zaBase.withStack [luQ8, luH8]).computeGlobal [] luHomeLine) == []
#guard stackedOf ((zaBase.withStack [{ luQ8 with undatedIfTaxable := true }, { luH8 with undatedIfTaxable := true }]).computeGlobal [] luHomeLine)
  == [("disposal 1 (unlistedShares)", 240000, 240000, 16217, "central")]
-- an undated item the rule does tax still blocks it
#guard stackedOf ((zaBase.withStack [{ luQ8 with undatedIfTaxable := true }]).computeGlobal [] (luSales ",\"date\":\"2025-05-10\"" "")) == []
-- GR ΕΝ.Φ.Ι.Α. άρθ. 4 Α παρ. 2 ε (shape): a detached house takes 1,02 instead of the floor coefficient, chosen by `"detached": 1`
def enfiaDet : ZoneTax :=
  { enfia with
    coefsAt := fun g i _ => if assetFact? g i (.field "detached") == some 1 then
      some [{ fact := .age, bands := [(0, 10000), (25, 9000)] }, { fact := .field "detached", bands := [(1, 10200)] },
            { fact := .frontages, bands := [(0, 10000), (2, 10100)] }] else none }
def grDetached : String := "{\"kind\":\"home\",\"value\":1,\"areaM2\":100,\"zoneValueM2\":1200,\"buildYear\":1990,\"frontages\":1,\"detached\":1}"
-- 100 × 2,90 × 0,90 × 1,02 = 266 with no floor given (a detached house needs none)
#guard (enfiaDet.charges (grAssets grDetached)).map (·.due) == [266]
#guard enfia.unknown (grAssets grDetached) == ["4100 ΕΝΦΙΑ κύριος φόρος: asset 1 (home): floor not given (grade C)"]
-- without `"detached"` the 2.7.0 coefficients
#guard (enfiaDet.charges (grAssets grFlat)).map (·.due) == (enfia.charges (grAssets grFlat)).map (·.due)

/-! ## 2.9.0 (R3-GAP-1): zakat by the payer's faith, a Maldives-style case -/
-- MV zakat al-mal (shape): 2,5 % of the zakatable wealth of a Muslim held for a lunar year, above the nisab (the value of
-- 85 g of gold, here a declared MVR 110 000); deposits, shares, bonds and business assets; the rate and nisab the model's
def mvZakat : ZakatRule :=
  { name := "zakat al-mal (shape)", nisab := 110000, nisabSource := "85 g of gold at the Ministry's 2025 rate (case input)",
    oecd := .wealth, statute := "MV Ministry of Islamic Affairs zakat rules (shape)" }
def mvLine (adults : String) (assets : String) : CanonGlobal :=
  gl ("{\"id\":\"z\",\"schema\":\"global/2.0\",\"household\":{\"id\":\"z\",\"adults\":" ++ adults ++ "},\"assets\":" ++ assets ++ "}")
def mvAssets : String :=
  "[{\"kind\":\"deposits\",\"value\":300000},{\"kind\":\"home\",\"value\":900000},{\"kind\":\"listedShares\",\"value\":50000,\"person\":1},{\"kind\":\"deposits\",\"value\":20000,\"debt\":5000,\"person\":1}]"
-- a Muslim adult with MVR 300 000 on deposit (the home is not zakatable): 2,5 % = 7 500
#guard (mvZakat.charges (mvLine "[{\"age\":45,\"religion\":\"Muslim\"}]" mvAssets)).map (fun c => (c.oecd.code, c.event, c.base, c.relieved, c.due))
  == [("4200", "adult 1", 300000, 300000, 7500)]
-- the second adult holds 50 000 of shares and 15 000 net on deposit: 65 000 is below the nisab, a computed 0
#guard (mvZakat.charges (mvLine "[{\"religion\":\"muslim\"},{\"zakatLiable\":true}]" mvAssets)).map (fun c => (c.event, c.due, c.statute))
  == [("adult 1", 7500, "MV Ministry of Islamic Affairs zakat rules (shape); nisab 110000 (85 g of gold at the Ministry's 2025 rate (case input))"),
      ("adult 2", 0, "MV Ministry of Islamic Affairs zakat rules (shape); nisab 110000 (85 g of gold at the Ministry's 2025 rate (case input)); below the nisab")]
-- not a Muslim, or `"zakatLiable": false`: no charge and no grade C
#guard (mvZakat.charges (mvLine "[{\"religion\":\"Buddhist\"},{\"zakatLiable\":false,\"religion\":\"muslim\"}]" mvAssets)).isEmpty
#guard (mvZakat.unknown (mvLine "[{\"religion\":\"Buddhist\"}]" mvAssets)).isEmpty
-- nothing said of the faith: never presumed by the kernel (grade C)
#guard (mvZakat.charges (mvLine "[{\"age\":45}]" mvAssets)).isEmpty
#guard mvZakat.unknown (mvLine "[{\"age\":45}]" mvAssets)
  == ["4200 zakat al-mal (shape): adult 1: religion not given (\"zakatLiable\" or \"religion\"; the rule presumes nothing) (grade C)"]
-- a model that declares a presumption, with its reason, computes it and says so
def mvZakatP : ZakatRule := { mvZakat with presume := some true, presumeNote := "Constitution art. 9 (d): citizens are Muslims (shape)" }
#guard (mvZakatP.charges (mvLine "[{\"age\":45}]" mvAssets)).map (fun c => (c.due, c.statute))
  == [(7500, "MV Ministry of Islamic Affairs zakat rules (shape); nisab 110000 (85 g of gold at the Ministry's 2025 rate (case input)); presumed liable (the model's declared presumption: Constitution art. 9 (d): citizens are Muslims (shape))")]
#guard (mvZakatP.unknown (mvLine "[{\"age\":45}]" mvAssets)).isEmpty
-- the adult's own zakatable figure wins over the assets
#guard (mvZakat.charges (mvLine "[{\"religion\":\"muslim\",\"zakatableWealth\":200000}]" mvAssets)).map (·.due) == [5000]
-- PK (Zakat and Ushr Ordinance 1980, shape): deposits only, a declaration of exemption (CZ-50) exempts a Muslim
def pkZakat : ZakatRule :=
  { name := "zakat (deduction at source, shape)", nisab := 179689, nisabSource := "notified nisab 2025-26 (shape)",
    adults := some (.wealth [.deposits]), exemptByDeclaration := true, statute := "Zakat and Ushr Ordinance 1980 s. 3 (shape)" }
#guard (pkZakat.charges (mvLine "[{\"religion\":\"muslim\"}]" "[{\"kind\":\"deposits\",\"value\":400000},{\"kind\":\"listedShares\",\"value\":900000}]")).map (·.due) == [10000]
#guard (pkZakat.charges (mvLine "[{\"religion\":\"muslim\",\"zakatExemptDeclared\":true}]" "[{\"kind\":\"deposits\",\"value\":400000}]")).isEmpty
-- MY (zakat on income, shape): wages less an allowance (had al-kifayah), on the excess
def myZakat : ZakatRule :=
  { name := "zakat pendapatan (shape)", adults := some (.income [.selfEmployment]), allowance := 20000, statute := "(shape)" }
#guard (myZakat.charges (gl "{\"id\":\"m\",\"schema\":\"global/2.0\",\"household\":{\"id\":\"m\",\"adults\":[{\"age\":40,\"wages\":120000,\"religion\":\"islam\"}]}}")).map (·.due) == [2500]
-- a company: the zakatable base × the Muslim-held share (60 %): 1 000 000 × 60 % × 2,5 % = 15 000
def mvZakatCo : ZakatRule := { mvZakat with adults := none, companies := some {} }
def mvCo (extra : String) : CanonGlobal :=
  gl ("{\"id\":\"c\",\"entity\":\"company\",\"company\":{\"turnover\":5000000,\"profit\":400000" ++ extra ++ "}}")
#guard (mvZakatCo.charges (mvCo ",\"zakatBase\":1000000,\"muslimOwnershipBp\":6000")).map (fun c => (c.base, c.relieved, c.due, c.statute))
  == [(1000000, 600000, 15000, "MV Ministry of Islamic Affairs zakat rules (shape); Muslim-held share 6000 bp")]
#guard (mvZakatCo.charges (mvCo ",\"zakatBase\":1000000,\"zakatLiable\":true")).map (·.due) == [25000]
#guard (mvZakatCo.charges (mvCo ",\"zakatBase\":1000000")).isEmpty
#guard mvZakatCo.unknown (mvCo ",\"zakatBase\":1000000")
  == ["4200 zakat al-mal (shape): year: the Muslim-held share not given (\"muslimOwnershipBp\" or \"zakatLiable\" on the company) (grade C)"]
#guard mvZakatCo.unknown (mvCo ",\"muslimOwnershipBp\":10000")
  == ["4200 zakat al-mal (shape): year: the zakatable base not given (company \"zakatBase\") (grade C)"]
#guard (mvZakatCo.charges (mvLine "[{\"religion\":\"muslim\"}]" mvAssets)).isEmpty     -- a household under a company-only rule
#guard zakatDue 250 110000 false 109999 == 0 && zakatDue 250 110000 false 110000 == 2750 && zakatDue 250 110000 true 210000 == 2500

/-! ## 2.9.0 (R2-GAP-1): dated tariff lines and surcharges by origin, a US-style case -/
-- HTSUS (shape): cotton T-shirts 6109.10 at 16,5 % column 1; chapter 99 additional duties added to it: IEEPA China
-- (EO 14195) 10 % from 4 Feb 2025, 20 % from 4 Mar; reciprocal (EO 14257) 10 % from 5 Apr on every origin but CA and MX;
-- IEEPA Canada/Mexico (EO 14193/14194) 25 % from 4 Mar, not on goods claiming USMCA. The US has no VAT (`vatBp` 0).
def usTariff : TariffRule :=
  { name := "customs duty (HTSUS, shape)", country := "US",
    lines := [{ hs := "6109.10", adValoremBp := 1650 }, { hs := "6109.90", adValoremBp := 3200 }],
    preferences := [{ name := "USMCA", partners := ["CA", "MX"] }],
    surcharges := [
      { name := "IEEPA China 10 %", origins := ["CN"], adValoremBp := 1000, validFrom := "2025-02-04", validTo := "2025-03-04", statute := "EO 14195" },
      { name := "IEEPA China 20 %", origins := ["CN"], adValoremBp := 2000, validFrom := "2025-03-04", statute := "EO 14195, EO 14228" },
      { name := "reciprocal 10 %", exceptOrigins := ["CA", "MX"], adValoremBp := 1000, validFrom := "2025-04-05", statute := "EO 14257" },
      { name := "IEEPA Canada/Mexico 25 %", origins := ["CA", "MX"], adValoremBp := 2500, validFrom := "2025-03-04",
        exceptPreferences := ["USMCA"], statute := "EO 14193, EO 14194" }],
    statute := "HTSUS (shape)" }
def tee (extra : String) : String := "{\"good\":\"clothing\",\"amount\":1000,\"hs\":\"6109.10.00\"" ++ extra ++ "}"
-- a Chinese T-shirt bought on 10 May 2025 for 1 000: value 1 000 / (1 + 0,165 + 0,20 + 0,10) = 682; 112 + 136 + 68 = 316
#guard (usTariff.charges (bkt (tee ",\"origin\":\"CN\",\"date\":\"2025-05-10\""))).map (fun c => (c.base, c.due, c.statute))
  == [(682, 316, "HTSUS (shape); HS 610910 (MFN); EO 14195, EO 14228; + IEEPA China 20 %: 136; EO 14257; + reciprocal 10 %: 68")]
-- the same shirt bought on 15 January: column 1 only, 1 000 / 1,165 = 858, 16,5 % = 141 (the 2.8.0 figure)
#guard (usTariff.charges (bkt (tee ",\"origin\":\"CN\",\"date\":\"2025-01-15\""))).map (fun c => (c.base, c.due)) == [(858, 141)]
-- undated: the duty changes within the year, so grade C (never a guessed date)
#guard (usTariff.charges (bkt (tee ",\"origin\":\"CN\""))).isEmpty
#guard usTariff.unknown (bkt (tee ",\"origin\":\"CN\""))
  == ["5120 customs duty (HTSUS, shape): line 1 (clothing): no \"date\" and the duty changes within the year (on 2025-02-04, 2025-03-04, 2025-04-05): give the line's \"date\" (grade C)"]
-- the origin is needed where a surcharge limited by origin could apply
#guard usTariff.unknown (bkt (tee ",\"imported\":true,\"date\":\"2025-06-01\""))
  == ["5120 customs duty (HTSUS, shape): line 1 (clothing): origin not given (a preference may apply: USMCA) (grade C)"]
-- a Vietnamese shirt on 1 June: column 1 + reciprocal 10 %: 1 000 / 1,265 = 790; 130 + 79 = 209
#guard (usTariff.charges (bkt (tee ",\"origin\":\"VN\",\"date\":\"2025-06-01\""))).map (fun c => (c.base, c.due)) == [(790, 209)]
-- a Canadian shirt claiming USMCA pays nothing (the IEEPA duty waived); the MFN path would be 16,5 % + 25 %
#guard (usTariff.charges (bkt (tee ",\"origin\":\"CA\",\"date\":\"2025-06-01\""))).map (fun c => (c.base, c.due, c.statute))
  == [(1000, 0, "HTSUS (shape); HS 61091000: USMCA preference, origin CA")]
-- the same shirt with no preference available: 1 000 / 1,415 = 706; 116 + 176 = 292
def usNoUsmca : TariffRule := { usTariff with preferences := [] }
#guard (usNoUsmca.charges (bkt (tee ",\"origin\":\"CA\",\"date\":\"2025-06-01\""))).map (fun c => (c.base, c.due)) == [(706, 292)]
-- a dated tariff line (AR Decreto 333/2025 shape: mobile phones 16 % to 8 % from 15 May 2025); the top-level "date" dates every line
def arPhones : TariffRule :=
  { name := "derecho de importación (shape)", country := "AR",
    lines := [{ hs := "8517.13", adValoremBp := 1600, validTo := "2025-05-15" },
              { hs := "8517.13", adValoremBp := 800, validFrom := "2025-05-15", statute := "Decreto 333/2025 (shape)" }] }
def phone : String := "{\"good\":\"communication\",\"amount\":1080,\"hs\":\"851713\",\"origin\":\"CN\"}"
#guard (arPhones.charges (hh ("[" ++ phone ++ "]") ",\"date\":\"2025-03-01\"")).map (·.due) == [148]
#guard (arPhones.charges (hh ("[" ++ phone ++ "]") ",\"date\":\"2025-06-01\"")).map (fun c => (c.due, c.statute)) == [(80, "Decreto 333/2025 (shape); HS 851713 (MFN)")]
#guard (arPhones.unknown (bkt phone)).length == 1
-- undated but the same duty all year (only another heading changes): computed, and said
#guard (arPhones.charges (bkt "{\"good\":\"other\",\"amount\":500,\"hs\":\"9999\",\"origin\":\"CN\"}")).isEmpty
def arOther : TariffRule := { arPhones with otherBp := 1000 }
#guard (arOther.charges (bkt "{\"good\":\"other\",\"amount\":1100,\"hs\":\"9999\",\"origin\":\"CN\"}")).map (fun c => (c.due, c.statute))
  == [(100, "HS 9999: other goods 1000 bp; no date: the same duty all year")]
-- a rule with no 2.9.0 field is the 2.8.0 rule (`outcome_v28`): the CARICOM tariff above is unchanged
#guard cetTariff.uses29 == false && usTariff.uses29 && arPhones.uses29
-- EAC CET (shape, SSA note): rice "75 % or US$ 345 per tonne, the higher", the specific part in US dollars, converted at a
-- declared rate (the entity's "fxRates" wins); no rate: grade C
def eacRice : TariffRule :=
  { name := "import duty (EAC CET, shape)", country := "KE",
    lines := [{ hs := "1006", adValoremBp := 7500, perKgNum := 345, perKgDen := 1000, currency := "USD", higherOf := true }],
    fxRate := some { currency := "USD", num := 129, source := "CBK mean rate (shape)", date := "2025-06-30" } }
def rice (extra : String) : String := "{\"good\":\"food\",\"amount\":100000,\"hs\":\"1006.30\",\"origin\":\"PK\",\"customsValue\":60000" ++ extra ++ "}"
-- 2 t: US$ 690 × 129 = 89 010 > 75 % of 60 000 = 45 000
#guard (eacRice.charges (bkt (rice ",\"massG\":2000000"))).map (fun c => (c.due, c.statute))
  == [(89010, "HS 1006 (MFN); USD amounts at 129 (CBK mean rate (shape), 2025-06-30)")]
-- 500 kg: US$ 172.50 × 129 = 22 252 < 45 000
#guard (eacRice.charges (bkt (rice ",\"massG\":500000"))).map (·.due) == [45000]
#guard (eacRice.charges (hh ("[" ++ rice ",\"massG\":2000000" ++ "]") ",\"fxRates\":{\"USD\":130}")).map (·.due) == [89700]
#guard ({ eacRice with fxRate := none } : TariffRule).unknown (bkt (rice ",\"massG\":2000000"))
  == ["5120 import duty (EAC CET, shape): line 1 (food): amounts in USD and no exchange rate given (fxRates.USD) (the duty on hs 100630 is specific) (grade C)"]

/-! ## 2.9.0 (R3-GAP-2): a duty per container, a Hong Kong-style case -/
-- HK Cap. 109 Sch. 1 Part I para. 1A-1C (from 16 Oct 2024, shape): liquor above 30 % vol: 100 % of the first $200 of the
-- value of each container of not more than 1 litre, 10 % of the rest; containers above 1 litre per litre. The value is
-- before the duty (no VAT in HK): the bands are inverted out of the price.
def hkLiquor : GoodsValueTax :=
  { name := "liquor duty (shape)", goods := [.spirits], minAbvBp := 3000, value := .beforeTax,
    bands := [(200, 10000), (-1, 1000)], perContainer := true, maxContainerMl := 1000,
    statute := "Dutiable Commodities Ordinance Cap. 109 Sch. 1 Part I para. 1A (shape)" }
def whisky (extra : String) : String := "{\"good\":\"spirits\",\"abvBp\":4000" ++ extra ++ "}"
-- one 750 ml bottle at $500: value 290 (290 + 200 + 9 = 499), duty 209
#guard (hkLiquor.charges (bkt (whisky ",\"amount\":500,\"quantity\":750,\"containerMl\":750"))).map (fun c => (c.oecd.code, c.base, c.relieved, c.due, c.statute))
  == [("5121", 500, 290, 209, "Dutiable Commodities Ordinance Cap. 109 Sch. 1 Part I para. 1A (shape); on the value before the tax; per container of 750 ml")]
-- six bottles at $200 each ($1 200): every bottle below $200 of value, 100 %: value 600, duty 600
#guard (hkLiquor.charges (bkt (whisky ",\"amount\":1200,\"quantity\":4500,\"containerMl\":750"))).map (fun c => (c.relieved, c.due)) == [(600, 600)]
-- a 1,5 l bottle at $900 is taxed per litre ($600 a litre): 381.8 + 200 + 18.2 a litre, value 572, duty 327
#guard (hkLiquor.charges (bkt (whisky ",\"amount\":900,\"quantity\":1500,\"containerMl\":1500"))).map (fun c => (c.relieved, c.due, c.statute))
  == [(572, 327, "Dutiable Commodities Ordinance Cap. 109 Sch. 1 Part I para. 1A (shape); on the value before the tax; containers of 1500 ml: per litre")]
-- no container size, or a strength the duty does not take
#guard hkLiquor.unknown (bkt (whisky ",\"amount\":500,\"quantity\":750"))
  == ["5121 liquor duty (shape): line 1 (spirits): containerMl not given (the tax is per container) (grade C)"]
#guard (hkLiquor.charges (bkt "{\"good\":\"spirits\",\"abvBp\":1500,\"amount\":500,\"quantity\":750,\"containerMl\":750}")).isEmpty
-- the customs value of the line instead of the price
#guard (({ hkLiquor with value := .customs } : GoodsValueTax).charges (bkt (whisky ",\"amount\":500,\"quantity\":750,\"containerMl\":750,\"customsValue\":300"))).map (·.due) == [210]
#guard dutyAt [(200, 10000), (-1, 1000)] 750 750 290 == 209 && dutyAt [(-1, 1000)] 1 1 5000 == 500

/-! ## 2.9.0: the manufacturer's value (MY Sales Tax Act 2018 s. 9, MM specific goods tax, shape) -/
def mySst : GoodsValueTax :=
  { name := "sales tax (shape)", goods := [.clothing, .other], imported := some false, value := .exFactory, rateBp := 1000,
    oecd := .salesTax, statute := "Sales Tax Act 2018 s. 9, Sales Tax (Rates of Tax) Order 2025 (shape)" }
-- a local good sold by its manufacturer at 800: 10 % = 80, whatever the shop's price
#guard (mySst.charges (bkt "{\"good\":\"clothing\",\"amount\":1500,\"exFactoryValue\":800}")).map (fun c => (c.oecd.code, c.base, c.relieved, c.due))
  == [("5112", 1500, 800, 80)]
#guard (mySst.charges (bkt "{\"good\":\"other\",\"amount\":1500,\"manufacturerValue\":600}")).map (·.due) == [60]
-- not given: grade C, unless the model declares a fallback (here the value before the tax: 1 100 / 1,10 = 1 000)
#guard mySst.unknown (bkt "{\"good\":\"clothing\",\"amount\":1100}")
  == ["5112 sales tax (shape): line 1 (clothing): the manufacturer's value not given (\"exFactoryValue\") (grade C)"]
#guard (({ mySst with fallback := some .beforeTax } : GoodsValueTax).charges (bkt "{\"good\":\"clothing\",\"amount\":1100}")).map (fun c => (c.relieved, c.due, c.statute))
  == [(1000, 100, "Sales Tax Act 2018 s. 9, Sales Tax (Rates of Tax) Order 2025 (shape); on the value before the tax")]
-- imported lines are outside this rule (`imported := some false`)
#guard (mySst.charges (bkt "{\"good\":\"clothing\",\"amount\":1500,\"exFactoryValue\":800,\"origin\":\"CN\",\"imported\":true}")).isEmpty
-- a dated rule: an undated line is grade C
#guard (({ mySst with validFrom := "2025-07-01" } : GoodsValueTax).unknown (bkt "{\"good\":\"clothing\",\"amount\":1500,\"exFactoryValue\":800}")).length == 1
#guard (({ mySst with validFrom := "2025-07-01" } : GoodsValueTax).charges (bkt "{\"good\":\"clothing\",\"amount\":1500,\"exFactoryValue\":800,\"date\":\"2025-06-30\"}")).isEmpty

/-! ## 2.9.0: the tenant's nationality on a lease (BH municipal fee, shape) -/
def bhFee : RentLevy :=
  { name := "municipal fee on rent (shape)", country := "BH", rateBp := 1000, tests := [.nonNational], ifUnknown := .gradeC,
    statute := "Legislative Decree 13/1979 (shape)" }
def bhLet (lessee : String) : CanonGlobal :=
  hh "[]" (",\"assets\":[{\"kind\":\"realEstate\",\"value\":500000,\"rent\":120000" ++ lessee ++ "},{\"kind\":\"home\",\"value\":300000}]")
-- let to an Indian national: 10 % of the rent 120 000 = 12 000; the owner's own home is not let
#guard (bhFee.charges (bhLet ",\"lessee\":{\"nationality\":\"in\"}")).map (fun c => (c.oecd.code, c.event, c.level.name, c.base, c.due))
  == [("4100", "asset 1", "local", 120000, 12000)]
#guard (bhFee.charges (bhLet ",\"tenantNationality\":\"BH\"")).isEmpty
#guard (bhFee.charges (bhLet ",\"lessee\":{\"national\":false}")).map (·.due) == [12000]
-- a let asset whose tenant is not described: grade C (`.gradeC`), or not applied and noted (`.general`)
#guard bhFee.unknown (bhLet ",\"let\":true") == ["4100 municipal fee on rent (shape): asset 1: the tenant's nationality not given (grade C)"]
#guard ({ bhFee with ifUnknown := .general } : RentLevy).notes (bhLet ",\"let\":true")
  == ["4100 municipal fee on rent (shape): asset 1: the tenant's nationality not given: not applied (the rule's general case)"]
-- the tenant side: a household of a foreign national paying rent (its first adult's nationality)
def bhTenant : RentLevy := { bhFee with side := .tenant, bearer := .entity }
#guard (bhTenant.charges (gl "{\"id\":\"t\",\"schema\":\"global/2.0\",\"household\":{\"id\":\"t\",\"adults\":[{\"age\":30,\"nationality\":\"PH\"}]},\"consumption\":[{\"good\":\"rent\",\"amount\":6000}]}")).map (fun c => (c.event, c.due))
  == [("line 1 (rent)", 600)]
#guard (bhTenant.charges (gl "{\"id\":\"t\",\"schema\":\"global/2.0\",\"household\":{\"id\":\"t\",\"adults\":[{\"age\":30,\"national\":true}]},\"consumption\":[{\"good\":\"rent\",\"amount\":6000}]}")).isEmpty
