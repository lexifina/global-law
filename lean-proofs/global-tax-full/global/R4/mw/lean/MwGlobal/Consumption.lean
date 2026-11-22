import R4Common
import TaxKernel.Global2

/-!
# Malawi 2025: VAT (5111) and excises (5121) (generated from `R4/specs/mw.json` by `R4/tools/gen_country.py`)

Pass 10: Malawi Revenue Authority downloads via Wayback (`www.mra.mw/assets/upload/downloads/…`, `www.mra.mw/admin/storage/download_files/…`; CDX `url=mra.mw&matchType=domain&filter=mimetype:application/pdf`) and the MalawiLII media copy of the Value Added Tax (Amendment) (No. 2) Act 2025 (`media.malawilii.org/media/legislation/15246/…`, the Government Printer's gazette bundle with Acts 36 and 37 of 2025), in `R4/fetch/mw10/` (scanned Acts OCRed, tesseract eng). Not held: the principal Acts (Cap. 41:01, Cap. 42:02), the 2023 Taxation amendment, the non-resident tax schedule.

Act No. 37 of 2025 s. 2: "The Value Added Tax Act is amended, in section 9, by deleting the word '16.5' and substituting therefor the word '17.5'." (assent 20 December 2025, published 30 December 2025). MRA public notice 'New tax measures for mid-year budget review': "The new measures are effective from 30th December, 2025 ... Increased VAT rate from 16.5% to 17.5%". Customs and Excise (Tariffs) Order (2024-2025 update), Part I para 4 (j): "column 11 contains Value Added Tax rates"; 2710.12.19 Other motor spirit and 2710.12.99 distillates (including diesel oil, gas oil): "Exempt". MRA VAT guide (2021): "Standard rated supplies ... at a standard rate of 16.5 percent"; exempt supplies "are specified in the First Schedule to the VAT Act".

Customs and Excise (Tariffs) Order (HS 2022, updated 2024-2025) Part I para 4: "(i) column 10 contains excise rates; (j) column 11 contains Value Added Tax rates"; Part II para 2: excise duties on goods produced or manufactured in Malawi "ad valorem or ad rem as set out in Column [10] of Part III"; para 4: excise on imported goods (s. 82A). Part III: "2203.00.90 Other [beer made from malt] l 30% 25% 14% 30% Free 15% 40% 16.5% 10%"; "2204.21.10 --In containers holding 2 l or less l 30% 25% 6% 12.5% Free Free 95% 16.5% 10%"; "2208.30.90 --Other [whiskies] l/laa ... 110% 16.5% 10%"; "2202.10.29 ----Other l ... 10% 16.5% 10%"; "2710.12.19 ----Other motor spirit kg/litre 10% 10% 2% 10% Free Free 10% Exempt 10%"; "2710.12.99 ----Distillates and other fuels n.e.s. (including diesel oil, gas oil ...) ... 10% Exempt 10%"; "2402.20.00 - Cigarettes containing tobacco ... USD 15 per 1,000 sticks".
-/

namespace MwGlobal
open TaxKernel TaxKernel.Global

def vatX : Vat :=
  { name := "Value added tax", standard := 1650, reduced := 0, reduced2 := 0,
    threshold := 0,
    classOf := fun gd => match gd with
      | .petrol | .diesel => .exempt
      | _ => .standard }

def vat : Family := R4.vatFamily vatX "Value Added Tax Act Cap. 42:02 s. 9 (16.5 %; the Value Added Tax (Amendment) (No. 2) Act 2025, Act No. 37 of 2025, published 30 Dec 2025, deletes \"16.5\" and substitutes \"17.5\"); fuels exempt per the VAT column (column 11) of the Customs and Excise (Tariffs) Order [text version: VAT Act Cap. 42:02 s. 9 as read in Act No. 37 of 2025 (published 30 December 2025): 16.5 % until 29 December 2025 (applied all year; 17.5 % for two days not split)]"

-- the standard rate as printed: 16.5 % inside a tax-inclusive 11650
#guard vatX.embedded { good := .other, amount := 11650 } == 1650
#guard vatX.embedded { good := .petrol, amount := 10000 } == 0
#guard vatX.embedded { good := .diesel, amount := 10000 } == 0
def accises : List R4.Exc :=
  [ { good := .beer, name := "Excise duty (beer, 2203.00.90)", advBp := 4000, vatBp := 1650, statute := "Tariff Order Part III column 10, 2203.00.90: 40 %" },
    { good := .wine, name := "Excise duty (wine in containers of 2 l or less, 2204.21.10)", advBp := 9500, vatBp := 1650, statute := "Tariff Order Part III column 10, 2204.21.10: 95 %" },
    { good := .spirits, name := "Excise duty (spirits, 2208.30.90 / 2208.50.99)", advBp := 11000, vatBp := 1650, statute := "Tariff Order Part III column 10, 2208.x0.90/99 (not in sachets or plastic bottles): 110 %" },
    { good := .nonAlcoholic, name := "Excise duty (sweetened waters, 2202.10)", advBp := 1000, vatBp := 1650, statute := "Tariff Order Part III column 10, 2202.10.11-29: 10 %" },
    { good := .petrol, name := "Excise duty (motor spirit, 2710.12.19)", advBp := 1000, vatBp := 0, statute := "Tariff Order Part III column 10, 2710.12.19: 10 % (VAT exempt)" },
    { good := .diesel, name := "Excise duty (diesel and gas oil, 2710.12.99)", advBp := 1000, vatBp := 0, statute := "Tariff Order Part III column 10, 2710.12.99: 10 % (VAT exempt)" } ]
def excise : Family := R4.exciseFamily "Excise duty" accises
-- Tariff Order Part III column 10, 2203.00.90: 40 %: 10000 paid for 1 unit(s) at 5 % vol → 2452
#guard (R4.exciseCharges [{ good := .beer, name := "Excise duty (beer, 2203.00.90)", advBp := 4000, vatBp := 1650, statute := "Tariff Order Part III column 10, 2203.00.90: 40 %" }] [{ good := .beer, amount := 10000, quantity := 1000, abvBp := 500 }] []).map (·.due) == [2452]
-- Tariff Order Part III column 10, 2204.21.10: 95 %: 10000 paid for 1 unit(s) at 12 % vol → 4180
#guard (R4.exciseCharges [{ good := .wine, name := "Excise duty (wine in containers of 2 l or less, 2204.21.10)", advBp := 9500, vatBp := 1650, statute := "Tariff Order Part III column 10, 2204.21.10: 95 %" }] [{ good := .wine, amount := 10000, quantity := 1000, abvBp := 1200 }] []).map (·.due) == [4180]
-- Tariff Order Part III column 10, 2208.x0.90/99 (not in sachets or plastic bottles): 110 %: 10000 paid for 1 unit(s) at 40 % vol → 4495
#guard (R4.exciseCharges [{ good := .spirits, name := "Excise duty (spirits, 2208.30.90 / 2208.50.99)", advBp := 11000, vatBp := 1650, statute := "Tariff Order Part III column 10, 2208.x0.90/99 (not in sachets or plastic bottles): 110 %" }] [{ good := .spirits, amount := 10000, quantity := 1000, abvBp := 4000 }] []).map (·.due) == [4495]
-- Tariff Order Part III column 10, 2202.10.11-29: 10 %: 10000 paid for 1 unit(s) at 0 % vol → 780
#guard (R4.exciseCharges [{ good := .nonAlcoholic, name := "Excise duty (sweetened waters, 2202.10)", advBp := 1000, vatBp := 1650, statute := "Tariff Order Part III column 10, 2202.10.11-29: 10 %" }] [{ good := .nonAlcoholic, amount := 10000, quantity := 1000, abvBp := 0 }] []).map (·.due) == [780]
-- Tariff Order Part III column 10, 2710.12.19: 10 % (VAT exempt): 10000 paid for 1 unit(s) at 0 % vol → 909
#guard (R4.exciseCharges [{ good := .petrol, name := "Excise duty (motor spirit, 2710.12.19)", advBp := 1000, vatBp := 0, statute := "Tariff Order Part III column 10, 2710.12.19: 10 % (VAT exempt)" }] [{ good := .petrol, amount := 10000, quantity := 1000, abvBp := 0 }] []).map (·.due) == [909]
-- Tariff Order Part III column 10, 2710.12.99: 10 % (VAT exempt): 10000 paid for 1 unit(s) at 0 % vol → 909
#guard (R4.exciseCharges [{ good := .diesel, name := "Excise duty (diesel and gas oil, 2710.12.99)", advBp := 1000, vatBp := 0, statute := "Tariff Order Part III column 10, 2710.12.99: 10 % (VAT exempt)" }] [{ good := .diesel, amount := 10000, quantity := 1000, abvBp := 0 }] []).map (·.due) == [909]
def accisesUsd (r : FxRate) : List R4.Exc :=
  [ { good := .cigarettes, name := "Excise duty (cigarettes, 2402.20)", perUnitNum := 15 * r.num, perUnitDen := 1000 * r.den, statute := "Tariff Order Part III column 10, 2402.20: US$15 per 1 000 sticks" ++ "; " ++ r.note } ]
def exciseUsdGoods : List Good := [.cigarettes]
def exciseUsd : Family :=
  { name := "5121 Excise duty (US$ duties)", covers := [.excise],
    run := fun a g p => match fxFor g "USD" none with
      | some r => (R4.exciseFamily "Excise duty (US$ duties)" (accisesUsd r)).run a g p
      | none => [] }
def exciseUsdNotes (g : CanonGlobal) : List String :=
  if (fxFor g "USD" none).isNone && g.consumption.any (fun s => exciseUsdGoods.contains s.good)
  then [fxUnknownLine "5121" "Excise duty" "USD"] else []
def usdTestRate0 : FxRate := { currency := "USD", num := 173500, den := 100, source := "test rate", date := "2025-07-01" }
#guard (R4.exciseCharges (accisesUsd usdTestRate0) [{ good := .cigarettes, amount := 10000, quantity := 20000, abvBp := 0 }] []).map (·.due) == [520]

def consumptionNotes (g : CanonGlobal) : List String :=
  if g.consumption.isEmpty then [] else
  ["the First (exempt) and Second (zero-rated) Schedules of the VAT Act are not held: apart from fuels (exempt per the tariff's VAT column) every basket line is charged at 16.5 % — financial, medical, educational and rental exemptions, if any, are not applied (grade B)", "the 17.5 % rate applies only from 30 December 2025 (two days of the year; not split)", "MRA's consolidated 2024-2025 tariff (official table) is applied to the whole of 2025; changes of the 2025/26 budget (from April 2025) were not read (flagged)", "beer, wine and spirits in sachets or plastic bottles pay 250 % (not separated); other non-alcoholic drinks (2202.99.90) 20 %", "nineteenth pass (kernel 2.7.0 Fx): cigarettes US$15 per 1 000 sticks converted at the line's own fxRates.USD (no declared rate: no official 2025 Reserve Bank of Malawi rate publication was reached); without it a cigarette line is listed (grade C). Hand case: 20 sticks at MK1 735.00 per US$ -> 520 (0.30 x 1 735 = 520.50, rounded down)"] ++ exciseUsdNotes g

end MwGlobal
