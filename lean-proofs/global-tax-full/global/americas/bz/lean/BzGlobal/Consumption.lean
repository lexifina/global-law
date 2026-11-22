import BzGlobal.Pit

/-!
# Belize 2025: General Sales Tax (5111); excise grade C

Source: General Sales Tax Act, Chapter 63, Revised Edition 2011 ("showing the substantive laws as at 31st December,
2011"), as posted by the Belize Tax Service (`bts.gov.bz/wp-content/uploads/2020/06/Chap-63-General-Sales-Tax-Act.pdf`,
Wayback capture 2026-04-18; `bz/law/gst_act_cap63_rev2020.pdf`, ARCHIVE_INDEX.tsv). Grade B (a 2011 consolidation still
posted by the administration; Statutory Instruments after 2011 not read; the 2021-2025 Acts held by the 1.x builder do
not mention the GST).
* **s. 9 (1)**: "(a) if the supply or import is zero-rated under the First Schedule, the Second Schedule or the Third
  Schedule, 0%; or (b) in any other case, 12.5%" (s. 9 (2): variable by Ministerial Order; none read).
* **Third Schedule (zero rated)**, substituted by S.I. 38 of 2010: I. food itemized (unprocessed: rice, flour, ...;
  processed: "Bread, Corn and Flour tortilla ..."); "A supply of water (other than water supplied in bottles ...)"; IV.
  listed medicines (analgesics, cough and cold preparations, insulin, oral rehydration ...); "Petroleum Products, namely:
  Premium and Regular Gasoline, Illuminating Kerosene, Diesel and Gas oils" (S.I. 21 of 2011).
* **Fourth Schedule (exempt)**: 1 financial services; 4 "A supply of residential accommodation"; 5 education by an
  Educational Institution; 7 textbooks; 9 "Medical, dental, hospital, optical and paramedical services"; 10 "The supply
  of accommodation in a hotel, inn, guesthouse"; 11 "A supply of electricity to consumers who use up to $200.00 of
  electricity"; 13 "domestic public transport of passengers"; 19 internet services.

Pass 6: general sales tax (5112) cited not levied (grade A): General Sales Tax Act Cap. 63 (Rev. Ed. 2020, `bz/law/gst_act_cap63_rev2020.txt`) **s. 98 (1)**: "The Sales Tax Act, Revised Edition 2000, is hereby repealed" (s. 99 repeals the Entertainment Tax Act): the GST of the P1 row replaced the sales tax.

**5121 (gap pass 2, 2026-11-22)**: excise duties of the Customs and Excise Duties Act Cap. 48 s. 21, Schedule II (on goods produced locally or imported): beer $7.62, wine $20.00, spirits $90.00 per imperial gallon (4.54609 l); cigarettes $65.00 per 1,000. Fuels (heading 27.10) are left at grade C: their rates changed by Order about twice a month in 2025.
-/

namespace BzGlobal.Consumption
open TaxKernel TaxKernel.Global AmerCommon BzGlobal

def vat : Vat :=
  { name := "General Sales Tax", standard := 1250,
    classOf := fun gd => match gd with
      | .food | .water | .medicines | .petrol | .diesel => .zero
      | .financial | .rent | .education | .books | .health | .hotels | .electricity | .transport => .exempt
      | _ => .standard }

def vatStatute : String := "GST Act Cap. 63 (Rev. Ed. 2011) s. 9 (1) (12.5 %; 0 % Scheds. 1-3); Third Schedule I, II, IV and petroleum (S.I. 21/2011) (zero); Fourth Schedule items 1, 4, 5, 7, 9, 10, 11, 13 (exempt)"

def vatF : Family := vatFamily "General Sales Tax" vat vatStatute .vat .central

def lines : List ExLine :=
  [{ good := .beer, name := "Excise duty (beer, Cap. 48 Sched. II)", num := 762000, den := 454609, vatBp := 1250, statute := "Customs and Excise Duties Act Cap. 48 s. 21; Schedule II items 7-8 (2203.00.10, 2203.00.20): $7.62 per imperial gallon (4.54609 l)" },
    { good := .wine, name := "Excise duty (wine, Cap. 48 Sched. II)", num := 2000000, den := 454609, vatBp := 1250, statute := "Cap. 48 s. 21; Schedule II items 9-13 (22.04, 22.05): $20.00 per imperial gallon" },
    { good := .spirits, name := "Excise duty (spirits, Cap. 48 Sched. II)", num := 9000000, den := 454609, vatBp := 1250, statute := "Cap. 48 s. 21; Schedule II items 16-25 (22.08: brandy, whisky, rum, gin, vodka, liqueurs): $90.00 per imperial gallon" },
    { good := .cigarettes, name := "Excise duty (cigarettes, Cap. 48 Sched. II)", num := 65, den := 1000, vatBp := 1250, statute := "Cap. 48 s. 21; Schedule II item 27 (2402.20.00): $65.00 per 1,000 cigarettes" }]

def exciseF : Family :=
  { name := "5121 excises", covers := [.excise],
    run := fun _ g _ => exciseCharges lines g.consumption }

def families : List Family := [vatF, exciseF]

def absent : List Absent :=
  [{ oecd := .salesTax, why := "the Sales Tax Act (Rev. Ed. 2000) was repealed by the General Sales Tax Act Cap. 63 s. 98 (1)" }]

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  when (g.consumption.any fun s => s.good == .food) "food: only the itemized Third Schedule foods (rice, flour, bread, tortillas ...) are zero rated; other food is taxed at 12.5 % (lower bound)"
  ++ when (g.consumption.any fun s => s.good == .medicines || s.good == .books) "medicines and books: only the listed medicines and textbooks are relieved (lower bound)"
  ++ when (g.consumption.any fun s => s.good == .electricity) "electricity is exempt only for consumers using up to $200 a month (Fourth Schedule item 11): read as within the cap (lower bound)"
  ++ when (g.consumption.any fun s => s.good == .petrol || s.good == .diesel) "excise duties on motor spirit and diesel (Cap. 48 Sched. II heading 27.10) not computed: the Minister changed the rates by Order about twice a month in 2025 (S.I. 14, 25, 32, 33, 36, 53, 56, 70, 71, 78, 79, 94, 99, 114, 141, 144, 147, 151 of 2025): dated rates (grade C)"
  ++ when (g.consumption.any fun s => s.good == .tobaccoOther || s.good == .nonAlcoholic) "excise on cigars ($65 per 1,000, item 26), other tobacco products ($3 per pack, item 28) and aerated or sweetened waters ($1.75 per imperial gallon, items 4-6; not juices) not computed: the canonical goods do not separate these products"

#guard vat.embedded { good := .clothing, amount := 1125 } == 125
#guard vat.embedded { good := .petrol, amount := 1125 } == 0
#guard vat.embedded { good := .hotels, amount := 1125 } == 0
-- beer: 100 l x 7.62 / 4.54609 = 167.62 -> 167
#guard (lines.find? (·.good == .beer)).get!.duty { good := .beer, amount := 1000, quantity := 100000 } == 167
-- wine: 20 l x 20 / 4.54609 = 87.99 -> 87; spirits: 10 l x 90 / 4.54609 = 197.97 -> 197
#guard (lines.find? (·.good == .wine)).get!.duty { good := .wine, amount := 500, quantity := 20000 } == 87
#guard (lines.find? (·.good == .spirits)).get!.duty { good := .spirits, amount := 600, quantity := 10000 } == 197
-- cigarettes: 1,000 sticks x $65 per 1,000 = 65
#guard (lines.find? (·.good == .cigarettes)).get!.duty { good := .cigarettes, amount := 300, quantity := 1000000 } == 65

end BzGlobal.Consumption
