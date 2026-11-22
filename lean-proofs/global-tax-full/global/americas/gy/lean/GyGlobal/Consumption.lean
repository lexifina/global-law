import GyGlobal.Pit

/-!
# Guyana 2025: Value-Added Tax (5111); excise grade C

Sources: Value-Added Tax Act Cap. 81:05 (Laws of Guyana L.R.O. 1/2012, mola.gov.gy PDF, Wayback capture 2022-07-27;
`gy/law/vat_cap81_05.pdf`); VAT (Amendment) Acts 3 of 2017, 2 of 2018 and 2019 (parliament.gov.gy, OCR); Fiscal
Enactments (Amendment) Acts 2022, No. 2 of 2022 and 2 of 2024 (the 1.x builder's copies); the rate from the Guyana
Revenue Authority's page "VAT Rates" (gra.gov.gy, fetched 2026-11-21: "Value Added Tax (VAT) is a 14% tax on all local
or imported goods and services, except if those goods or services are Exempt"): the Act's 16 % was cut to 14 % from
2017 by an amending Act not reached. Grade B.
* **Schedule I (zero rated, L.R.O. 1/2012)**: (o) "a supply of water services" by Guyana Water Incorporated; (p) "a
  supply of electricity" by an authorised person; (q) basic foods (wheat flour, raw white or brown rice ...); (dd)
  "a supply of medical services"; (ee) "a supply of education services and educational materials" (printed books,
  newspapers ...). Act 2 of 2018 restructured ss. 17-18 and the Schedules; Act 2 of 2024 adds zero-rated items.
* **Schedule II (exempt)**: financial services, residential rental and passenger transport read as exempt (flagged:
  the 2018 restructuring of Schedule II was not consolidated).

Pass 6: general sales tax (5112) cited not levied: the Value-Added Tax Act Cap. 81:05 (L.R.O. 1/2012, `gy/law/
vat_cap81_05.txt`) provides for refunds net of "any unpaid amounts under the repealed Consumption Tax Act" (c. 80:02):
the consumption tax, the general tax on goods before VAT, was repealed when VAT began (Act 10 of 2005). Grade A.
-/

namespace GyGlobal.Consumption
open TaxKernel TaxKernel.Global AmerCommon GyGlobal

def vat : Vat :=
  { name := "Value-Added Tax", standard := 1400,
    classOf := fun gd => match gd with
      | .food | .water | .electricity | .health | .education | .books | .newspapers => .zero
      | .financial | .insurance | .rent | .transport => .exempt
      | _ => .standard }

def vatStatute : String := "VAT Act Cap. 81:05 s. 10 (rate 14 % per GRA; Act 16 % cut from 2017), Sched. I (o), (p), (q), (dd), (ee) (zero), Sched. II (exempt)"

def vatF : Family := vatFamily "Value-Added Tax" vat vatStatute .vat .central

def families : List Family := [vatF]

def absent : List Absent :=
  [{ oecd := .salesTax, why := "the general Consumption Tax Act (Cap. 80:02) was repealed when the VAT Act Cap. 81:05 (Act 10 of 2005) took effect; the VAT Act refers to 'the repealed Consumption Tax Act'" }]

def notes : List String := []

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  when (true) "VAT: rate from the GRA page (the 2017 amending Act not reached); schedules as at L.R.O. 1/2012 with amendments of 2018-2024 not consolidated (grade B)"
  ++ when (g.consumption.any fun s => s.good == .food) "food: only the basic foods listed in Schedule I are zero rated; other food 14 % (lower bound)"
  ++ when (g.consumption.any fun s => s.good == .cigarettes || s.good == .tobaccoOther || s.good == .beer || s.good == .wine || s.good == .spirits || s.good == .petrol || s.good == .diesel) "excise tax not modelled (Excise Tax Act and orders not reached)"

#guard vat.embedded { good := .clothing, amount := 1140 } == 140
#guard vat.embedded { good := .electricity, amount := 1140 } == 0

end GyGlobal.Consumption
