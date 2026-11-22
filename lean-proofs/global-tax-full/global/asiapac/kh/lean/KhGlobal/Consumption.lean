import KhGlobal.Pit

/-!
# Cambodia 2025: value added tax (5111); specific tax not modelled

Source: Law on Taxation promulgated by Royal Kram NS/RKM/0523/0059 (May 2023), Khmer text, Tesseract OCR made by the
1.x builder (`world/B03-asia-east-se/kh/law/law_taxation_2023_khm_ocr.txt`, copied to
`kh/law/kh_law_taxation_2023_khm_ocr.txt`, sha256 in `SHA256SUMS`), chapter on value added tax (arts. 57-81).
* **art. 65 (1)**: VAT at "១០ (ដប់) ភាគរយ" (10 %) on the taxable value of each taxable supply in Cambodia; **65 (2)**
  0 % on exports and services performed abroad.
* **art. 58**: taxable person = a person in the self-declaration regime making taxable supplies (the regime's turnover
  thresholds are set by Prakas: not read, no threshold applied).
* **art. 63** non-taxable supplies: (1) education services; (2) public postal services; (3) hospital, clinic, medical
  and dental services and incidental medical goods; (4) passenger transport by a wholly state-owned public transport
  system; (5) insurance services; (6) electricity and clean water supply; (7) unprocessed domestic agricultural
  products; (8) waste collection; (9) basic financial services as set by Prakas; (10) personal imports within customs
  allowances; (11) recognised non-profit public-interest activities.
* Residential letting is not listed in art. 63: standard-rated.
* **arts. 88-90** specific tax: goods and services listed in art. 88, rates "set by sub-decree" (art. 89), base by
  Prakas (art. 90): not modelled.
-/

namespace KhGlobal.Consumption
open TaxKernel TaxKernel.Global

def vat : Vat :=
  { name := "Value added tax", standard := 1000,
    classOf := fun gd => match gd with
      | .education | .health | .insurance | .electricity | .water | .financial => .exempt
      | _ => .standard }

def vatStatute : String := "Law on Taxation 2023 art. 65 (1) (10 %), art. 63 (1), (3), (5), (6), (9)"

def families : List Family :=
  [{ name := "5111 Value added tax", covers := [.vat],
     run := fun _ g _ =>
       (if g.consumption.isEmpty then [] else [vat.basketCharge g.consumption vatStatute])
       ++ (if g.entity == .company && !g.company.sales.isEmpty then [vat.businessCharge g.company vatStatute] else []) }]

def absent : List Absent :=
  []

def notes : List String := ["KH 5111: Law on Taxation 2023 (Royal Kram NS/RKM/0523/0059) arts. 58, 63, 65 (Khmer OCR)"]

def unsupported (_ : List String) (g : CanonGlobal) : List String :=
  (if g.consumption.any (fun s => s.good == .food) then ["unprocessed domestic agricultural products are not taxable (Law on Taxation 2023 art. 63 (7)); the basket's food is modelled at 10 %"] else [])
  ++ (if g.consumption.any (fun s => s.good == .transport) then ["only passenger transport by a wholly state-owned public system is not taxable (art. 63 (4)); transport is modelled at 10 %"] else [])
  ++ (if g.consumption.any (fun s => s.good == .medicines) then ["medical goods are not taxable only when incidental to hospital, medical or dental services (art. 63 (3)); pharmacy sales are modelled at 10 %"] else [])
  ++ (if true then ["the self-declaration regime thresholds (art. 58; Prakas on taxpayer classification) are not applied"] else [])
  ++ (if g.consumption.any (fun s => s.good == .spirits || s.good == .wine || s.good == .beer || s.good == .cigarettes || s.good == .tobaccoOther || s.good == .petrol || s.good == .diesel || s.good == .communication) then ["specific tax (Law on Taxation 2023 arts. 88-90; rates by sub-decree, base by Prakas) not modelled"] else [])

#guard vat.embedded { good := .clothing, amount := 1100 } == 100
#guard vat.embedded { good := .water, amount := 1100 } == 0
#guard vat.embedded { good := .rent, amount := 1100 } == 100

end KhGlobal.Consumption
