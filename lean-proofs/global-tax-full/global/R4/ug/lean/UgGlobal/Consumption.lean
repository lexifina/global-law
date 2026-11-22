import R4Common

/-!
# Uganda 2025: VAT (5111) and excises (5121) (generated from `R4/specs/ug.json` by `R4/tools/gen_country.py`)

Source: Income Tax Act Cap. 338 (ULII, 23 December 2024: `cmp20/world/B10-anglophone-africa/ug/law/ita_2024-12-23.txt`). VAT: URA guide pages (Wayback captures of ura.go.ug/en/value-added-tax-vat/ 2025-09-04 and thetaxman.ura.go.ug); excise: Excise Duty Act 2014 ULII consolidation at 2023-12-31 (Wayback 2025-05-21) and the Excise Duty (Amendment) Act 2024 (parliament.go.ug CMIS PDF); saved in `cmp20/global/R4/fetch/ug8/` with SHA256SUMS.

URA, 'Value Added Tax (VAT)' (Wayback capture 2025-09-04): "Standard rated supplies : These are supplies on which VAT is charged at a rate of 18%. These include all supplies excluding supplies that are included under the second and third schedules of the VAT law"; "Exempt supplies are listed under the second schedule to the VAT law and include; Health insurance and life insurance services Petroleum fuels Social welfare services Educational services Financial Services Passenger transportation services". URA 'A simplified guide to Value Added Tax': "Zero-rated supplies : These are supplies charged VAT at a rate of 0%. Such supplies are listed in the third schedule to the VAT Act. They, among others, include all exports and supply of drugs and medicines". Grade B: the Act itself was not read.

Schedule 2 Part I (consolidation at 31 Dec 2023): "1. Cigarettes ... (b) Hinge lid (i) locally manufactured Ushs. 80,000 per 1000 sticks (ii) imported Ushs. 100,000 per 1000 sticks ... 2. Beer (a) Malt beer 60% or Ushs. 2050 per litre, whichever is higher ... 5. Non-alcoholic beverages (a) Non-alcoholic beverages not including fruit or vegetable juices 12% or Ushs. 250 per litre, whichever is higher". Excise Duty (Amendment) Act 2024 s. 1: "This Act shall come into force on 1st July, 2024"; s. 3 (c): "(c) Any other un-denatured spirits (i) that are locally produced, of alcoholic strength by volume of less than 80%; or (ii) that are imported, of alcoholic strength by volume of less than 80%: 80% or Shs 1700 per litre, whichever is higher"; (d): "(b) Other wines 100% or Shs 10,000 per litre, whichever is higher"; (h): "(a) Motor spirit (gasoline) Shs 1550 per litre (b) Gas oil (automotive, light, amber for high speed engine) Shs 1230 per litre". Percentages are taken on the value before excise and VAT. Grade B: the Excise Duty (Amendment) Act 2025 was not reached.
-/

namespace UgGlobal
open TaxKernel TaxKernel.Global

def vatX : Vat :=
  { name := "Value Added Tax", standard := 1800, reduced := 0, reduced2 := 0,
    threshold := 0,
    classOf := fun gd => match gd with
      | .financial | .insurance | .education | .transport | .petrol | .diesel => .exempt
      | .medicines => .zero
      | _ => .standard }

def vat : Family := R4.vatFamily vatX "Value Added Tax Act Cap. 349 s. 24 (standard rate 18 %), Second Schedule (exempt supplies), Third Schedule (zero-rated supplies), per the Uganda Revenue Authority guide (official secondary)"

-- the standard rate as printed: 18 % inside a tax-inclusive 11800
#guard vatX.embedded { good := .other, amount := 11800 } == 1800
#guard vatX.embedded { good := .financial, amount := 10000 } == 0
#guard vatX.embedded { good := .insurance, amount := 10000 } == 0
#guard vatX.embedded { good := .education, amount := 10000 } == 0
def accises : List R4.Exc :=
  [ { good := .beer, name := "Excise duty malt beer", advBp := 6000, vatBp := 1800, minNum := 2050, minDen := 1, statute := "Excise Duty Act 2014 Sch. 2 item 2 (a): 60 % or Ushs 2050 per litre" },
    { good := .wine, name := "Excise duty other wines", advBp := 10000, vatBp := 1800, minNum := 10000, minDen := 1, statute := "Excise Duty Act 2014 Sch. 2 item 4 (b) (Act 2024 s. 3 (d)): 100 % or Shs 10,000 per litre" },
    { good := .spirits, name := "Excise duty un-denatured spirits < 80 %", advBp := 8000, vatBp := 1800, maxAbvBp := 7999, minNum := 1700, minDen := 1, statute := "Excise Duty Act 2014 Sch. 2 item 3 (c) (Act 2024 s. 3 (c)): 80 % or Shs 1700 per litre" },
    { good := .cigarettes, name := "Excise duty cigarettes hinge lid (local)", perUnitNum := 80000, perUnitDen := 1000, vatBp := 1800, imported := some false, statute := "Excise Duty Act 2014 Sch. 2 item 1 (b) (i): Ushs 80,000 per 1000 sticks" },
    { good := .cigarettes, name := "Excise duty cigarettes hinge lid (imported)", perUnitNum := 100000, perUnitDen := 1000, vatBp := 1800, imported := some true, statute := "Excise Duty Act 2014 Sch. 2 item 1 (b) (ii): Ushs 100,000 per 1000 sticks" },
    { good := .nonAlcoholic, name := "Excise duty non-alcoholic beverages", advBp := 1200, vatBp := 1800, minNum := 250, minDen := 1, statute := "Excise Duty Act 2014 Sch. 2 item 5 (a): 12 % or Ushs 250 per litre" },
    { good := .petrol, name := "Excise duty motor spirit", perUnitNum := 1550000, perUnitDen := 1000, vatBp := 0, statute := "Excise Duty Act 2014 Sch. 2 item 8 (a) (Act 2024 s. 3 (h)): Shs 1550 per litre" },
    { good := .diesel, name := "Excise duty gas oil", perUnitNum := 1230000, perUnitDen := 1000, vatBp := 0, statute := "Excise Duty Act 2014 Sch. 2 item 8 (b) (Act 2024 s. 3 (h)): Shs 1230 per litre" } ]
def excise : Family := R4.exciseFamily "Excise duty" accises
-- Excise Duty Act 2014 Sch. 2 item 2 (a): 60 % or Ushs 2050 per litre: 10000 paid for 1 unit(s) at 5 % vol → 3177
#guard (R4.exciseCharges [{ good := .beer, name := "Excise duty malt beer", advBp := 6000, vatBp := 1800, minNum := 2050, minDen := 1, statute := "Excise Duty Act 2014 Sch. 2 item 2 (a): 60 % or Ushs 2050 per litre" }] [{ good := .beer, amount := 10000, quantity := 1000, abvBp := 500 }] []).map (·.due) == [3177]
-- Excise Duty Act 2014 Sch. 2 item 4 (b) (Act 2024 s. 3 (d)): 100 % or Shs 10,000 per litre: 10000 paid for 1 unit(s) at 12 % vol → 10000
#guard (R4.exciseCharges [{ good := .wine, name := "Excise duty other wines", advBp := 10000, vatBp := 1800, minNum := 10000, minDen := 1, statute := "Excise Duty Act 2014 Sch. 2 item 4 (b) (Act 2024 s. 3 (d)): 100 % or Shs 10,000 per litre" }] [{ good := .wine, amount := 10000, quantity := 1000, abvBp := 1200 }] []).map (·.due) == [10000]
-- Excise Duty Act 2014 Sch. 2 item 3 (c) (Act 2024 s. 3 (c)): 80 % or Shs 1700 per litre: 10000 paid for 1 unit(s) at 40 % vol → 3765
#guard (R4.exciseCharges [{ good := .spirits, name := "Excise duty un-denatured spirits < 80 %", advBp := 8000, vatBp := 1800, maxAbvBp := 7999, minNum := 1700, minDen := 1, statute := "Excise Duty Act 2014 Sch. 2 item 3 (c) (Act 2024 s. 3 (c)): 80 % or Shs 1700 per litre" }] [{ good := .spirits, amount := 10000, quantity := 1000, abvBp := 4000 }] []).map (·.due) == [3765]
-- Excise Duty Act 2014 Sch. 2 item 1 (b) (i): Ushs 80,000 per 1000 sticks: 10000 paid for 1 unit(s) at 0 % vol → 80
#guard (R4.exciseCharges [{ good := .cigarettes, name := "Excise duty cigarettes hinge lid (local)", perUnitNum := 80000, perUnitDen := 1000, vatBp := 1800, imported := some false, statute := "Excise Duty Act 2014 Sch. 2 item 1 (b) (i): Ushs 80,000 per 1000 sticks" }] [{ good := .cigarettes, amount := 10000, quantity := 1000, abvBp := 0 }] []).map (·.due) == [80]
-- Excise Duty Act 2014 Sch. 2 item 1 (b) (ii): Ushs 100,000 per 1000 sticks: 10000 paid for 1 unit(s) at 0 % vol → 100
#guard (R4.exciseCharges [{ good := .cigarettes, name := "Excise duty cigarettes hinge lid (imported)", perUnitNum := 100000, perUnitDen := 1000, vatBp := 1800, imported := some true, statute := "Excise Duty Act 2014 Sch. 2 item 1 (b) (ii): Ushs 100,000 per 1000 sticks" }] [{ good := .cigarettes, amount := 10000, quantity := 1000, abvBp := 0 }] ["cigarettes"]).map (·.due) == [100]
-- Excise Duty Act 2014 Sch. 2 item 5 (a): 12 % or Ushs 250 per litre: 10000 paid for 1 unit(s) at 0 % vol → 907
#guard (R4.exciseCharges [{ good := .nonAlcoholic, name := "Excise duty non-alcoholic beverages", advBp := 1200, vatBp := 1800, minNum := 250, minDen := 1, statute := "Excise Duty Act 2014 Sch. 2 item 5 (a): 12 % or Ushs 250 per litre" }] [{ good := .nonAlcoholic, amount := 10000, quantity := 1000, abvBp := 0 }] []).map (·.due) == [907]
-- Excise Duty Act 2014 Sch. 2 item 8 (a) (Act 2024 s. 3 (h)): Shs 1550 per litre: 10000 paid for 1 unit(s) at 0 % vol → 1550
#guard (R4.exciseCharges [{ good := .petrol, name := "Excise duty motor spirit", perUnitNum := 1550000, perUnitDen := 1000, vatBp := 0, statute := "Excise Duty Act 2014 Sch. 2 item 8 (a) (Act 2024 s. 3 (h)): Shs 1550 per litre" }] [{ good := .petrol, amount := 10000, quantity := 1000, abvBp := 0 }] []).map (·.due) == [1550]
-- Excise Duty Act 2014 Sch. 2 item 8 (b) (Act 2024 s. 3 (h)): Shs 1230 per litre: 10000 paid for 1 unit(s) at 0 % vol → 1230
#guard (R4.exciseCharges [{ good := .diesel, name := "Excise duty gas oil", perUnitNum := 1230000, perUnitDen := 1000, vatBp := 0, statute := "Excise Duty Act 2014 Sch. 2 item 8 (b) (Act 2024 s. 3 (h)): Shs 1230 per litre" }] [{ good := .diesel, amount := 10000, quantity := 1000, abvBp := 0 }] []).map (·.due) == [1230]

def consumptionNotes (g : CanonGlobal) : List String :=
  if g.consumption.isEmpty then [] else
  ["insurance is exempt only for health and life insurance; all insurance taken as exempt", "other Second/Third Schedule items (unprocessed food, residential rent, water, etc.) not applied: the schedules were not read", "local-content beers (30 %), soft-cap cigarettes, opaque beer, local wine (20 %) and bottled water (10 %) not separable from the basket lines", "petroleum fuels are VAT-exempt (vatBp 0 in the excise base split)", "the Excise Duty (Amendment) Act 2025 (from 1 July 2025) was not reached"]

end UgGlobal
