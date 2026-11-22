import R4Common

/-!
# Zambia 2025: VAT (5111) and excises (5121) (generated from `R4/specs/zm.json` by `R4/tools/gen_country.py`)

Zambia Revenue Authority, 'Tax information' page (`cmp20/global/R4/fetch/zm8/`, live copy of 2026-11-21 and Wayback capture of 2025-05-16, SHA256SUMS); Income Tax (Amendment) Acts 2023-2025 (`cmp20/world/B09-southern-africa/zm/law/`). The consolidated Income Tax, VAT and Customs and Excise Acts are not held. Pass 9: amendment Acts from parliament.gov.zm (/acts-of-parliament → /node/<n> → sites/default/files/documents/acts/*.pdf): Customs and Excise (Amendment) Acts No. 25 of 2022, No. 25 of 2023, No. 24 of 2024 (in operation 1 Jan 2025) and No. 11 of 2025 (published 19 Aug 2025); Income Tax (Amendment) Acts No. 17 of 2018, No. 15 of 2019, No. 43 of 2021, No. 24 of 2022, No. 22 of 2023, No. 22 of 2024 (1 Jan 2025) and No. 10 of 2025 (published 19 Aug 2025). Texts and SHA256SUMS in `R4/fetch/zm9/` (pdftotext -layout). The consolidated Acts (Cap. 322, Cap. 323) are not held: only rates whose figure and unit are printed in an amending Act are modelled.

ZRA, Tax information, Value Added Tax: "STANDARD RATED SUPPLIES: These are supplies that attract VAT at the prescribed standard rate 16%. ZERO RATED SUPPLIES: These are supplies that attract VAT at 0%. EXEMPT SUPPLIES: These are supplies that do not attract any VAT at all." Grade B: the Act was not read.

Customs and Excise (Amendment) Act No. 24 of 2024 (in operation 1 Jan 2025), App. II: "(e) heading 9, by the deletion of subheading (3) and the substitution therefor of the following: ... (a) Petroleum spirit (Motor spirit) 2710.12.10 Decalitre K2.34/ltr ... (e) Automotive gas-Oils diesel 2710.19.10 Decalitre K0.75"; "(d) heading 7 ... headings 24.01 and 24.02, by the deletion of the figure 'K400' and the substitution therefor of the figure 'K452'"; "(c) heading 3 ... 2202.10.20, 2202.91.00 and 2202.99.00 by the deletion of the figure 'K0.30' and the substitution therefor of the figure 'K1.00'". Customs and Excise (Amendment) Act No. 11 of 2025 (19 Aug 2025), App. I: "(c) heading 4 ... opposite subheading 2203.00.90, by the deletion of the figure '60%' and the substitution therefor of the figure '50%'; (d) heading 5 ... opposite headings 22.04 and 22.05, by the deletion of the figure '60%' and the substitution therefor of the figure '80%'; (e) heading 6 ... opposite subheadings 2207.10.00, 2207.20.10, 2207.20.90 and Ex.22.08, by the deletion of the figure '60%' and the substitution therefor of the figure '80%'; (f) heading 7 ... 'K452' ... 'K750'".
-/

namespace ZmGlobal
open TaxKernel TaxKernel.Global

def vatX : Vat :=
  { name := "Value Added Tax", standard := 1600, reduced := 0, reduced2 := 0,
    threshold := 0,
    classOf := fun gd => match gd with
      | _ => .standard }

def vat : Family := R4.vatFamily vatX "Value Added Tax Act Cap. 331 (standard rate 16 %), per the Zambia Revenue Authority guide (official secondary; the same sentence in the Wayback capture of 2025-05-16 and the live page)"

-- the standard rate as printed: 16 % inside a tax-inclusive 11600
#guard vatX.embedded { good := .other, amount := 11600 } == 1600
def accises : List R4.Exc :=
  [ { good := .beer, name := "Excise clear beer (2203.00.90)", advBp := 6000, vatBp := 1600, statute := "Second Schedule heading 4, 2203.00.90: 60 % (to 18 Aug 2025)" },
    { good := .wine, name := "Excise wine (22.04)", advBp := 6000, vatBp := 1600, statute := "Second Schedule heading 5, 22.04: 60 % (to 18 Aug 2025)" },
    { good := .spirits, name := "Excise spirits (Ex.22.08)", advBp := 6000, vatBp := 1600, statute := "Second Schedule heading 6, Ex.22.08: 60 % (to 18 Aug 2025)" },
    { good := .petrol, name := "Excise petroleum spirit (2710.12.10)", perUnitNum := 2340, perUnitDen := 1000, vatBp := 1600, statute := "Second Schedule heading 9 (3) (a) (Act No. 24 of 2024): K2.34 per litre" } ]
def excise : Family := R4.exciseFamily "Excise duty (Customs and Excise Act, Second Schedule)" accises
-- Second Schedule heading 4, 2203.00.90: 60 % (to 18 Aug 2025): 10000 paid for 1 unit(s) at 5 % vol → 3232
#guard (R4.exciseCharges [{ good := .beer, name := "Excise clear beer (2203.00.90)", advBp := 6000, vatBp := 1600, statute := "Second Schedule heading 4, 2203.00.90: 60 % (to 18 Aug 2025)" }] [{ good := .beer, amount := 10000, quantity := 1000, abvBp := 500 }] []).map (·.due) == [3232]
-- Second Schedule heading 5, 22.04: 60 % (to 18 Aug 2025): 10000 paid for 1 unit(s) at 12 % vol → 3232
#guard (R4.exciseCharges [{ good := .wine, name := "Excise wine (22.04)", advBp := 6000, vatBp := 1600, statute := "Second Schedule heading 5, 22.04: 60 % (to 18 Aug 2025)" }] [{ good := .wine, amount := 10000, quantity := 1000, abvBp := 1200 }] []).map (·.due) == [3232]
-- Second Schedule heading 6, Ex.22.08: 60 % (to 18 Aug 2025): 10000 paid for 1 unit(s) at 40 % vol → 3232
#guard (R4.exciseCharges [{ good := .spirits, name := "Excise spirits (Ex.22.08)", advBp := 6000, vatBp := 1600, statute := "Second Schedule heading 6, Ex.22.08: 60 % (to 18 Aug 2025)" }] [{ good := .spirits, amount := 10000, quantity := 1000, abvBp := 4000 }] []).map (·.due) == [3232]
-- Second Schedule heading 9 (3) (a) (Act No. 24 of 2024): K2.34 per litre: 10000 paid for 1 unit(s) at 0 % vol → 2
#guard (R4.exciseCharges [{ good := .petrol, name := "Excise petroleum spirit (2710.12.10)", perUnitNum := 2340, perUnitDen := 1000, vatBp := 1600, statute := "Second Schedule heading 9 (3) (a) (Act No. 24 of 2024): K2.34 per litre" }] [{ good := .petrol, amount := 10000, quantity := 1000, abvBp := 0 }] []).map (·.due) == [2]

def consumptionNotes (g : CanonGlobal) : List String :=
  if g.consumption.isEmpty then [] else
  ["zero-rated and exempt supplies are not listed in the guide: not applied", "rates in force from 1 Jan 2025 are applied to the whole year; Act No. 11 of 2025 (from 19 Aug 2025) sets clear beer 50 %, wine and spirits 80 %, tobacco K750 and non-alcoholic drinks K2.00 (not split by date)", "cigarettes (24.02: K452 from 1 Jan 2025), non-alcoholic drinks (2202.10.20: K1.00) and diesel (2710.19.10: K0.75) are not modelled: the amending Acts print the figure but not the unit it is charged per (the consolidated Second Schedule is not held); opaque beer 2203.00.10 not modelled"]

end ZmGlobal
