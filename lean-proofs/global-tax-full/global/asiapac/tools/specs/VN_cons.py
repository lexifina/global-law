S = dict(cc="VN", family_name="5111 Thuế giá trị gia tăng",
doc=r'''# Vietnam 2025: value added tax (5111); special consumption tax not modelled

Source: Law on VAT No. 48/2024/QH15 (in force 1 July 2025), official consolidated text No. 12/VBHN-VPQH of 06/02/2026
(datafiles.chinhphu.vn, via a second machine route; `vn/law/vat/vbhn12_2026_law48.pdf`, sha256 in `SHA256SUMS`). The
consolidation marks each later amendment with its effective date; provisions changed by Law 149/2025/QH15 from
2026-01-01 are not used.
* **Điều 9 khoản 2**: 5 % on a) clean water, d) unprocessed crop and livestock products, h) medicines and medical devices,
  l) books (other than those of Điều 5 khoản 15); **khoản 3**: 10 % on everything else.
* **Footnote 5 (Nghị quyết số 204/2025/QH15, from 1 July 2025 to 31 December 2026)**: "Giảm 2% thuế suất … khoản 3
  Điều 9 … (còn 8%), trừ … viễn thông, hoạt động tài chính, ngân hàng, chứng khoán, bảo hiểm, kinh doanh bất động sản,
  sản phẩm kim loại, sản phẩm khai khoáng (trừ than), … hàng hóa và dịch vụ chịu thuế tiêu thụ đặc biệt (trừ xăng)".
* **Điều 5** not subject to VAT: 8. life and health insurance, 9. credit services, 10. medical services, 13. teaching.
First half of 2025: the 2008 VAT Law and Resolution 174/2024/QH15 applied; they were not read, and the second-half rules
are applied to the whole year (flagged per entity).''',
vat=dict(name="Thuế giá trị gia tăng", standard=1000, reduced=500, reduced2=800, statute="Luật Thuế GTGT 48/2024/QH15 Điều 5, Điều 9 khoản 2-3; Nghị quyết 204/2025/QH15 (8 % from 1 July 2025)",
  classes={"water":"reduced","medicines":"reduced","books":"reduced","newspapers":"reduced",
           "food":"reduced2","nonAlcoholic":"reduced2","clothing":"reduced2","electricity":"reduced2","gas":"reduced2","petrol":"reduced2","diesel":"reduced2","heatingOil":"reduced2",
           "transport":"reduced2","recreation":"reduced2","restaurants":"reduced2","hotels":"reduced2","rent":"reduced2","other":"reduced2",
           "education":"exempt","health":"exempt","financial":"exempt","insurance":"exempt"}),
notes=["VN 5111: Law 48/2024/QH15 (consolidation 12/VBHN-VPQH) with Resolution 204/2025/QH15; second-half-2025 rules"],
unsupported=[["basket","first half of 2025 (VAT Law 13/2008 with Resolution 174/2024/QH15) not read: the second-half rules are applied to the whole year"],
 [["beer","wine","spirits","cigarettes","tobaccoOther","petrol","diesel"],"special consumption tax (on the producer's price) and environmental protection tax on fuel not modelled"],
 [["food"],"food taken at the reduced 8 % (processed food); unprocessed produce is 5 % (Điều 9 khoản 2 d)"]],
guards=["vat.embedded { good := .clothing, amount := 10800 } == 800","vat.embedded { good := .beer, amount := 11000 } == 1000","vat.embedded { good := .water, amount := 10500 } == 500","vat.embedded { good := .health, amount := 10500 } == 0"],
taxes=[{"oecd":"5111","tax":"Thuế giá trị gia tăng","statute":"Law 48/2024/QH15 Điều 5, 9; Resolution 204/2025/QH15 art. 1 (1) (as quoted in the official consolidation)","dated":"consolidation 12/VBHN-VPQH (provisions in force from 1 July 2025)","grade":"B","kernel_parts":["Vat"],"unsupported":["H1 2025 under Law 13/2008 and Resolution 174/2024 not read","the household-business threshold of Điều 5 khoản 25 (2025 wording replaced in 2026)","credit method vs direct method"]},
 {"oecd":"5121","tax":"Thuế tiêu thụ đặc biệt; thuế bảo vệ môi trường","statute":"Law on SCT 27/2008/QH12 as amended; Law on EPT 57/2010/QH12; Resolution on EPT rates","grade":"C","status":"unsupported","kernel_parts":[],"unsupported":["texts not read; SCT is levied on the producer's or importer's price (not in the basket); would unlock: the consolidated SCT law and the 2025 EPT resolution"]}])
