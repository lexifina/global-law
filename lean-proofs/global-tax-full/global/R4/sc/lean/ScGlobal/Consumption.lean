import R4Common

/-!
# Seychelles 2025: VAT (5111) and excises (5121) (generated from `R4/specs/sc.json` by `R4/tools/gen_country.py`)

Pass 10: official instruments from the Seychelles Revenue Commission legislation page (src.gov.sc / staging.src.gov.sc `wp-content/uploads/...`, links listed in `world/B09-southern-africa/sc/law/leg.html`), saved in `R4/fetch/sc10/` (SHA256SUMS; Business Tax schedule amendments in `R4/fetch/sc10/bt/`). Scanned gazettes were OCRed (tesseract eng; the VAT Act 2010 scan is landscape with one page per half: `tools/ocr10_halves.sh`) or read on the page image (S.I. 27 of 2010).

VAT Act 2010 s. 6: "(1) Subject to this Act, value added tax at the rate specified in subsection (3) is levied on— (a) taxable supplies made by a taxable person; (b) taxable imports. ... (3) The rate of VAT is— (a) in the case of a taxable supply that is a zero-rated supply, zero percent; or (b) in any other case, the rate specified in the Fourth Schedule." S.I. 4 of 2014 reg. 2 repeals the Schedules and substitutes new ones: "THIRD SCHEDULE RATE OF VAT The rate of VAT for the purposes of section 6 is 15%. FOURTH SCHEDULE REGISTRATION THRESHOLD ..." (the 15 % rate was first set by S.I. 49 of 2011 from 1 July 2012). First Schedule Part II: exempt supplies of "(a) financial services ...; (b) education services ...; (d) life insurance premiums, health insurance premiums ...; (e) hospital, medical and dental services ...; (i) fresh bread; (j) public utility services; ..." and "4. The leasing or renting of premises for the sole purpose of residential dwelling." Later instruments amend the First, Second and Fourth Schedules only (S.I. 108 of 2014 and S.I. 97 of 2024: registration threshold SCR 2,000,000; S.I. 13 of 2015, S.I. 20 and 56 of 2025: exemptions); the VAT (Amendment) Act 2024 (Act 16 of 2024, from 1 Jan 2025) amends ss. 3, 7-9, 12, 13, 23, 24 (no rate change).

S.I. 110 of 2023 Schedule (HS code, description, taxable base, rate): "2203.0033 - - - - [Beer having an alcoholic strength not exceeding 8% vol] In immediate bottle made of glass l/bot. SCR 23.08/l"; "2204.2112 - - - - [Other wine ... in containers holding 2 l or less, having an alcoholic strength exceeding 8% but not exceeding 16% vol.] In immediate containers made of glass l/bot. SCR 48.40/l"; "- Rum and other spirits obtained by distilling fermented sugar-cane products 2208.4020 - - - In immediate bottle made of glass l/bot. SCR 158.40/l" (whiskies and gin SCR 268.40/l, vodka SCR 158.40/l); "2402.2000 - Cigarettes containing tobacco No./kg SCR 734 per 200 cigarettes"; "2710.1220 - - - Motor Gasoline l SCR 8.5/l"; "2710.1921 - - - - Gasoil (Diesel) kg/l SCR 8.5/l". S.I. 55 of 2023 reg. 3: "All beverages specified in the Schedule, of which the sugar content exceeds 5 grams per 100 ml, shall be subject to a sugar tax of SCR 4/Litre." S.I. 31 and 56 of 2024 amend only HS 2205.1021, 8703.40 and 87.06.
-/

namespace ScGlobal
open TaxKernel TaxKernel.Global

def vatX : Vat :=
  { name := "Value added tax", standard := 1500, reduced := 0, reduced2 := 0,
    threshold := 0,
    classOf := fun gd => match gd with
      | .financial | .education | .health | .insurance | .rent | .water | .electricity => .exempt
      | _ => .standard }

def vat : Family := R4.vatFamily vatX "Value Added Tax Act 2010 s. 6 (1)-(3) and Third Schedule (\"The rate of VAT for the purposes of section 6 is 15%\") as substituted by the Value Added Tax (Amendment of Schedules) Regulations 2014 (S.I. 4 of 2014); First Schedule Part II exempt supplies [text version: the Act and regulations as published, with the S.I. listed (to S.I. 107 of 2024, in force 1 January 2025)]"

-- the standard rate as printed: 15 % inside a tax-inclusive 11500
#guard vatX.embedded { good := .other, amount := 11500 } == 1500
#guard vatX.embedded { good := .financial, amount := 10000 } == 0
#guard vatX.embedded { good := .education, amount := 10000 } == 0
#guard vatX.embedded { good := .health, amount := 10000 } == 0
def accises : List R4.Exc :=
  [ { good := .beer, name := "Excise tax (beer not exceeding 8 % vol, HS 2203.0033)", perUnitNum := 23080, perUnitDen := 1000, vatBp := 1500, maxAbvBp := 800, statute := "S.I. 110 of 2023, HS 2203.0031-0039: SCR 23.08 per litre" },
    { good := .wine, name := "Excise tax (wine 8-16 % vol in containers of 2 l or less, HS 2204.21)", perUnitNum := 48400, perUnitDen := 1000, vatBp := 1500, minAbvBp := 800, maxAbvBp := 1600, statute := "S.I. 110 of 2023, HS 2204.2111-2119: SCR 48.40 per litre" },
    { good := .spirits, name := "Excise tax (rum, HS 2208.40)", perUnitNum := 158400, perUnitDen := 1000, vatBp := 1500, statute := "S.I. 110 of 2023, HS 2208.4010-4090: SCR 158.40 per litre" },
    { good := .cigarettes, name := "Excise tax (cigarettes, HS 2402.2000)", perUnitNum := 3670, perUnitDen := 1000, vatBp := 1500, statute := "S.I. 110 of 2023, HS 2402.2000: SCR 734 per 200 cigarettes (SCR 3.67 per cigarette)" },
    { good := .nonAlcoholic, name := "Sugar tax on drinks", perUnitNum := 4000, perUnitDen := 1000, vatBp := 1500, statute := "S.I. 55 of 2023 reg. 3: SCR 4 per litre of a scheduled beverage with more than 5 g of sugar per 100 ml" },
    { good := .petrol, name := "Excise tax (motor gasoline, HS 2710.1220)", perUnitNum := 8500, perUnitDen := 1000, vatBp := 1500, statute := "S.I. 110 of 2023, HS 2710.1220: SCR 8.5 per litre" },
    { good := .diesel, name := "Excise tax (gasoil, HS 2710.1921)", perUnitNum := 8500, perUnitDen := 1000, vatBp := 1500, statute := "S.I. 110 of 2023, HS 2710.1921: SCR 8.5 per litre" } ]
def excise : Family := R4.exciseFamily "Excise tax" accises
-- S.I. 110 of 2023, HS 2203.0031-0039: SCR 23.08 per litre: 10000 paid for 1 unit(s) at 5 % vol → 23
#guard (R4.exciseCharges [{ good := .beer, name := "Excise tax (beer not exceeding 8 % vol, HS 2203.0033)", perUnitNum := 23080, perUnitDen := 1000, vatBp := 1500, maxAbvBp := 800, statute := "S.I. 110 of 2023, HS 2203.0031-0039: SCR 23.08 per litre" }] [{ good := .beer, amount := 10000, quantity := 1000, abvBp := 500 }] []).map (·.due) == [23]
-- S.I. 110 of 2023, HS 2204.2111-2119: SCR 48.40 per litre: 10000 paid for 1 unit(s) at 12 % vol → 48
#guard (R4.exciseCharges [{ good := .wine, name := "Excise tax (wine 8-16 % vol in containers of 2 l or less, HS 2204.21)", perUnitNum := 48400, perUnitDen := 1000, vatBp := 1500, minAbvBp := 800, maxAbvBp := 1600, statute := "S.I. 110 of 2023, HS 2204.2111-2119: SCR 48.40 per litre" }] [{ good := .wine, amount := 10000, quantity := 1000, abvBp := 1200 }] []).map (·.due) == [48]
-- S.I. 110 of 2023, HS 2208.4010-4090: SCR 158.40 per litre: 10000 paid for 1 unit(s) at 40 % vol → 158
#guard (R4.exciseCharges [{ good := .spirits, name := "Excise tax (rum, HS 2208.40)", perUnitNum := 158400, perUnitDen := 1000, vatBp := 1500, statute := "S.I. 110 of 2023, HS 2208.4010-4090: SCR 158.40 per litre" }] [{ good := .spirits, amount := 10000, quantity := 1000, abvBp := 4000 }] []).map (·.due) == [158]
-- S.I. 110 of 2023, HS 2402.2000: SCR 734 per 200 cigarettes (SCR 3.67 per cigarette): 10000 paid for 1 unit(s) at 0 % vol → 3
#guard (R4.exciseCharges [{ good := .cigarettes, name := "Excise tax (cigarettes, HS 2402.2000)", perUnitNum := 3670, perUnitDen := 1000, vatBp := 1500, statute := "S.I. 110 of 2023, HS 2402.2000: SCR 734 per 200 cigarettes (SCR 3.67 per cigarette)" }] [{ good := .cigarettes, amount := 10000, quantity := 1000, abvBp := 0 }] []).map (·.due) == [3]
-- S.I. 55 of 2023 reg. 3: SCR 4 per litre of a scheduled beverage with more than 5 g of sugar per 100 ml: 10000 paid for 1 unit(s) at 0 % vol → 4
#guard (R4.exciseCharges [{ good := .nonAlcoholic, name := "Sugar tax on drinks", perUnitNum := 4000, perUnitDen := 1000, vatBp := 1500, statute := "S.I. 55 of 2023 reg. 3: SCR 4 per litre of a scheduled beverage with more than 5 g of sugar per 100 ml" }] [{ good := .nonAlcoholic, amount := 10000, quantity := 1000, abvBp := 0 }] []).map (·.due) == [4]
-- S.I. 110 of 2023, HS 2710.1220: SCR 8.5 per litre: 10000 paid for 1 unit(s) at 0 % vol → 8
#guard (R4.exciseCharges [{ good := .petrol, name := "Excise tax (motor gasoline, HS 2710.1220)", perUnitNum := 8500, perUnitDen := 1000, vatBp := 1500, statute := "S.I. 110 of 2023, HS 2710.1220: SCR 8.5 per litre" }] [{ good := .petrol, amount := 10000, quantity := 1000, abvBp := 0 }] []).map (·.due) == [8]
-- S.I. 110 of 2023, HS 2710.1921: SCR 8.5 per litre: 10000 paid for 1 unit(s) at 0 % vol → 8
#guard (R4.exciseCharges [{ good := .diesel, name := "Excise tax (gasoil, HS 2710.1921)", perUnitNum := 8500, perUnitDen := 1000, vatBp := 1500, statute := "S.I. 110 of 2023, HS 2710.1921: SCR 8.5 per litre" }] [{ good := .diesel, amount := 10000, quantity := 1000, abvBp := 0 }] []).map (·.due) == [8]

def consumptionNotes (g : CanonGlobal) : List String :=
  if g.consumption.isEmpty then [] else
  ["the rate schedule moved from the Fourth to the Third Schedule with S.I. 4 of 2014; no later instrument in the SRC list amends the Third Schedule (S.I. 16 of 2013 is the only illegible one and concerns business tax)", "only life and health insurance premiums are exempt (other insurance is taxable); public utility services (water, electricity) are exempt; zero-rated and exempt imported foods are inside the processed-food basket line (taxed)", "the spirits line is charged at the rum / vodka rate (SCR 158.40/l); whiskies, gin and 'other' spirits pay SCR 268.40/l, grape brandy SCR 224.40/l", "beer above 8 % vol (SCR 48.40/l) and above 16 % (SCR 105.60/l) not separated beyond the strength band of the line; stout SCR 16.67/l", "the non-alcoholic basket line is treated as scheduled sugary drinks above 5 g/100 ml (sugar tax); juices and waters without added sugar are outside it"]

end ScGlobal
