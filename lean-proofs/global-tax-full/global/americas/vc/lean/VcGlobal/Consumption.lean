import VcGlobal.Pit

/-!
# Saint Vincent and the Grenadines 2025: Value Added Tax (5111); excises grade C

Sources (`vc/law/`, ARCHIVE_INDEX.tsv):
* Rates: Inland Revenue Department page "Taxes" (ird.gov.vc, Wayback capture 25 Apr 2025,
  `ird_taxes_wb20250425.html`): "What is the current rate? Standard Rated - 16% | Accommodation (Rooms) - 11% | Zero
  Rated - 0% | Exempt Rated - No rate"; registration for businesses "grossing in sales of $300,000.00 XCD annually".
* Scope: VAT Act Cap. 445, Revised Edition 2009 (IRD PDF, OCR `vat_act_cap445_live.ocr.txt`): s. 8 (3) (15 % and 10 %
  then; raised to 16 %/11 % from 1 May 2017 by an amendment not held); **Third Schedule** zero-rated: (1) listed staple
  foods (rice, sugar, milk, flour, cooking oil, salt ...), (2) residential electricity, the first 200 kWh a month, (3)
  gasoline, kerosene, diesel and LPG, (5) newspapers, (10) residential water; **Fourth Schedule** exempt: (2) financial
  services and insurance, (6) residential lettings, (10) domestic passenger transport, (11) education, (12) medical and
  dental services, (14) prescription medicines, (27) bakery products, (30) printed matter (books, per the Regulations).
Grade B: the rates come from the official page, not from the amending Act; the VAT (Amendment) Acts No. 4 of 2019 and
No. 8 of 2022 (and the zero-rating changes announced in December 2025, after the 2025 year) were not read.
Mapping: food 16 % (only the listed staples are zero-rated and bakery exempt: upper bound), electricity zero (above 200
kWh a month taxable: lower bound), gas/petrol/diesel/water/newspapers zero, books, medicines, health, education,
transport, rent, financial, insurance exempt, hotels 11 %.
-/

namespace VcGlobal.Consumption
open TaxKernel TaxKernel.Global AmerCommon VcGlobal

def vat : Vat :=
  { name := "Value Added Tax", standard := 1600, reduced := 1100, threshold := 300000,
    classOf := fun gd => match gd with
      | .hotels => .reduced
      | .electricity | .gas | .petrol | .diesel | .water | .newspapers => .zero
      | .books | .medicines | .health | .education | .transport | .rent | .financial | .insurance => .exempt
      | _ => .standard }

def vatStatute : String := "VAT Act Cap. 445 s. 8 as amended (IRD page 2025: 16 %, accommodation 11 %); Third Schedule items 1-3, 5, 10 (zero); Fourth Schedule items 2, 6, 10-12, 14, 27, 30 (exempt)"

def vatF : Family := vatFamily "Value Added Tax" vat vatStatute .vat .central

def families : List Family := [vatF]

def absent : List Absent :=
  [{ oecd := .salesTax, why := "Not levied (convention R2-P13-CARIB (no tax-legality clause in the constitution: revenue authority's list of the taxes it administers + consolidated index of revenue Acts), pass 13): the Inland Revenue Department (ird.gov.vc) list of the taxes it administers, `vc/law/ird_taxes_20250425024416.*` ('List of Taxes: The following taxes are administered by the Inland Revenue Department', Wayback 2025-04-25), names: Corporate Income Tax, Value Added Tax, Personal Income Tax, Withholding Taxes, Excise Tax, Climate Resiliency Levy, PAYE, Travel Tax, Insurance Business Tax, Property Tax; consolidated index of revenue Acts not held; none of them is a general sales or turnover tax beside the VAT of the 5111 row." }]

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  when (g.consumption.any fun s => s.good == .food) "food taxed at 16 % (only the listed staples are zero-rated and bakery products exempt): upper bound"
  ++ when (g.consumption.any fun s => s.good == .electricity) "electricity zero-rated (only the first 200 kWh a month of a residence are): lower bound"
  ++ when (g.consumption.any fun s => s.good == .cigarettes || s.good == .tobaccoOther || s.good == .beer || s.good == .wine || s.good == .spirits) "excise tax on alcohol and tobacco not modelled"

#guard vat.embedded { good := .clothing, amount := 1160 } == 160
#guard vat.embedded { good := .hotels, amount := 1110 } == 110
#guard vat.embedded { good := .rent, amount := 1160 } == 0
#guard vat.embedded { good := .petrol, amount := 1160 } == 0

end VcGlobal.Consumption
