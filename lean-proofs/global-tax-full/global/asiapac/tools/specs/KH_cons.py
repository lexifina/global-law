S = dict(cc="KH", family_name="5111 Value added tax",
doc=r'''# Cambodia 2025: value added tax (5111); specific tax not modelled

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
  Prakas (art. 90): not modelled.''',
vat=dict(name="Value added tax", standard=1000, statute="Law on Taxation 2023 art. 65 (1) (10 %), art. 63 (1), (3), (5), (6), (9)",
  classes={"education":"exempt","health":"exempt","insurance":"exempt","electricity":"exempt","water":"exempt","financial":"exempt"}),
notes=["KH 5111: Law on Taxation 2023 (Royal Kram NS/RKM/0523/0059) arts. 58, 63, 65 (Khmer OCR)"],
unsupported=[[["food"],"unprocessed domestic agricultural products are not taxable (Law on Taxation 2023 art. 63 (7)); the basket's food is modelled at 10 %"],
 [["transport"],"only passenger transport by a wholly state-owned public system is not taxable (art. 63 (4)); transport is modelled at 10 %"],
 [["medicines"],"medical goods are not taxable only when incidental to hospital, medical or dental services (art. 63 (3)); pharmacy sales are modelled at 10 %"],
 ["*","the self-declaration regime thresholds (art. 58; Prakas on taxpayer classification) are not applied"],
 [["spirits","wine","beer","cigarettes","tobaccoOther","petrol","diesel","communication"],"specific tax (Law on Taxation 2023 arts. 88-90; rates by sub-decree, base by Prakas) not modelled"]],
extra_run=[],
guards=["vat.embedded { good := .clothing, amount := 1100 } == 100","vat.embedded { good := .water, amount := 1100 } == 0","vat.embedded { good := .rent, amount := 1100 } == 100"],
taxes=[{"oecd":"5111","tax":"Value added tax (10 %)","statute":"Law on Taxation (Royal Kram NS/RKM/0523/0059, 2023) arts. 58, 59, 63, 65","dated":"Law on Taxation 2023 as promulgated (Khmer OCR); later amendments not searched","grade":"A","kernel_parts":["Vat"],"unsupported":["self-declaration regime thresholds (Prakas) not applied","art. 63 (4), (7) partial exemptions not applied to the basket"]},
 {"oecd":"5121","tax":"Specific tax on certain goods and services","statute":"Law on Taxation 2023 arts. 88-90; sub-decree on specific tax rates","grade":"C","status":"unsupported","kernel_parts":[],"unsupported":["tried: Law on Taxation 2023 arts. 88-90 read (OCR): rates are set by sub-decree (art. 89) and the base by Prakas (art. 90); would unlock: the sub-decree on specific tax rates in force in 2025 (tax.gov.kh)"]}])
