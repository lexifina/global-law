S = dict(cc="LA", family_name="5111 Value added tax",
doc=r'''# Laos 2025: value added tax (5111); excise tax not modelled

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
  producers to the electricity enterprise (not retail electricity).''',
vat=dict(name="Value added tax", standard=1000, statute="Law on VAT No. 60/NA (2024) art. 17 (10 %), art. 12 (2)",
  classes={"food":"exempt","education":"exempt","financial":"exempt","health":"exempt"}),
notes=["LA 5111: Law on VAT (revised) No. 60/NA of 28 June 2024, in force 1 Jan 2025 (Lao OCR)"],
unsupported=[[["food"],"unprocessed and primarily processed crops, animals, meat and fish are exempt (Law on VAT 2024 art. 12 (2) 2.1-2.2); processed food is taxable at 10 %: food modelled as exempt"],
 [["insurance"],"only health, life, livestock and crop insurance are exempt (art. 12 (2) 2.14); insurance is modelled as taxable"],
 [["medicines"],"only traditional medicines are exempt (art. 12 (2) 2.17); medicines are modelled at 10 %"],
 [["books","newspapers"],"only school textbooks and non-commercial political publications are exempt (art. 12 (2) 2.9-2.10); modelled at 10 %"],
 ["*","no registration threshold applied (art. 33; micro-enterprises by separate regulation, not read)"],
 [["spirits","wine","beer","cigarettes","tobaccoOther","petrol","diesel"],"excise tax (Law on Excise Tax) not modelled"]],
extra_run=[],
guards=["vat.embedded { good := .clothing, amount := 1100 } == 100","vat.embedded { good := .electricity, amount := 1100 } == 100","vat.embedded { good := .education, amount := 1100 } == 0"],
taxes=[{"oecd":"5111","tax":"Value added tax (10 %)","statute":"Law on Value Added Tax (revised) No. 60/NA of 28 June 2024 arts. 11, 12, 17, 33, 61","dated":"in force 1 Jan 2025 (art. 61): the whole of 2025","grade":"A","kernel_parts":["Vat"],"unsupported":["partial exemptions (food, insurance, medicines, books) applied by whole class","micro-enterprise rules (art. 33) not read"]},
 {"oecd":"5121","tax":"Excise tax","statute":"Law on Excise Tax (2019) as amended","grade":"C","status":"unsupported","kernel_parts":[],"unsupported":["tried: Lao Trade Portal legal-document list (the excise law is listed with a Lao scanned PDF; not OCR'd in this pass); would unlock: OCR of the Law on Excise Tax and its 2025 rate table (ad valorem by product)"]}])
