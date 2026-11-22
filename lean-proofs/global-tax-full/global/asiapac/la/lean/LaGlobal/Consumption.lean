import LaGlobal.Pit

/-!
# Laos 2025: value added tax (5111); excise tax not modelled

Source: Law on Value Added Tax (revised) No. 60/NA of 28 June 2024, promulgated by presidential decree, in force
1 January 2025 (art. 61; it replaces Law No. 48/NA of 20 June 2018). Lao text from the Lao Trade Portal
(`laotradeportal.gov.la/upload/files/legal_lo_la_20250312015522.pdf`, scanned), Tesseract OCR (lao, tessdata_fast)
(`la/law/la_vat2024.pdf`, `la/law/la_vat2024_ocr.txt`, sha256 in `SHA256SUMS`).
* **art. 17 (1)**: "ອັດຕາ ສິບສ່ວນຮ້ອຍ (10%)" on imports and taxable supplies in the Lao PDR; **17 (2)** 0 % on exports.
* **art. 33**: every registered enterprise with a taxpayer number and business licence enters the VAT system;
  micro-enterprises by separate regulation (not read): no threshold applied.
* **art. 12 (2)** exempt domestic supplies: 2.1 agricultural crops not processed or only primarily processed (milling,
  husking); 2.2 animals and their parts unprocessed or only kept fresh; 2.9 school textbooks; 2.11 education services
  (nurseries to universities); 2.12 deposit and loan interest, transfers, foreign exchange and other financial
  transactions of licensed institutions; 2.14 health, life, livestock and crop insurance; 2.15 examination, treatment
  and diagnosis of humans and animals; 2.17 traditional medicines, prostheses, blood; 2.20 electricity supplied by
  producers to the electricity enterprise (not retail electricity).
-/

namespace LaGlobal.Consumption
open TaxKernel TaxKernel.Global

def vat : Vat :=
  { name := "Value added tax", standard := 1000,
    classOf := fun gd => match gd with
      | .food | .education | .financial | .health => .exempt
      | _ => .standard }

def vatStatute : String := "Law on VAT No. 60/NA (2024) art. 17 (10 %), art. 12 (2)"

def families : List Family :=
  [{ name := "5111 Value added tax", covers := [.vat],
     run := fun _ g _ =>
       (if g.consumption.isEmpty then [] else [vat.basketCharge g.consumption vatStatute])
       ++ (if g.entity == .company && !g.company.sales.isEmpty then [vat.businessCharge g.company vatStatute] else []) }]

def absent : List Absent :=
  []

def notes : List String := ["LA 5111: Law on VAT (revised) No. 60/NA of 28 June 2024, in force 1 Jan 2025 (Lao OCR)"]

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  (if g.consumption.any (fun s => s.good == .food) then ["unprocessed and primarily processed crops, animals, meat and fish are exempt (Law on VAT 2024 art. 12 (2) 2.1-2.2); processed food is taxable at 10 %: food modelled as exempt"] else [])
  ++ (if g.consumption.any (fun s => s.good == .insurance) then ["only health, life, livestock and crop insurance are exempt (art. 12 (2) 2.14); insurance is modelled as taxable"] else [])
  ++ (if g.consumption.any (fun s => s.good == .medicines) then ["only traditional medicines are exempt (art. 12 (2) 2.17); medicines are modelled at 10 %"] else [])
  ++ (if g.consumption.any (fun s => s.good == .books || s.good == .newspapers) then ["only school textbooks and non-commercial political publications are exempt (art. 12 (2) 2.9-2.10); modelled at 10 %"] else [])
  ++ (if true then ["no registration threshold applied (art. 33; micro-enterprises by separate regulation, not read)"] else [])
  ++ (if g.consumption.any (fun s => s.good == .spirits || s.good == .wine || s.good == .beer || s.good == .cigarettes || s.good == .tobaccoOther || s.good == .petrol || s.good == .diesel) then ["excise tax (Law on Excise Tax) not modelled"] else [])

#guard vat.embedded { good := .clothing, amount := 1100 } == 100
#guard vat.embedded { good := .electricity, amount := 1100 } == 100
#guard vat.embedded { good := .education, amount := 1100 } == 0

end LaGlobal.Consumption
