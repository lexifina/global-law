import re, os
p = os.path.expanduser("cmp20/global/asiapac/tools/in_gst.py"); s = open(p).read()
s = s.replace('def st2 : String := "CGST/SGST Acts 2017 s. 9; Notification 9/2025-CT(Rate), 10/2025-CT(Rate) (from 22 September 2025)"',
 'def st2 : String := "CGST/SGST Acts 2017 s. 9; Notification 9/2025-CT(Rate), G.S.R. 641(E) of 17 Sep 2025 (Schedules I 2.5 %, II 9 %, III 20 %, VII 14 % CGST), 10/2025-CT(Rate) (from 22 September 2025)"')
s = s.replace('"unsupported": ["notification PDFs not reached: rates from the WB Commercial Taxes synopsis (official, secondary)"',
 '"unsupported": ["goods rates from 22 Sep 2025 checked against the official e-Gazette text of G.S.R. 641(E) (9/2025-CT(Rate), egazette.gov.in WriteReadData/2025/266209.pdf): Sch. I apparel <= Rs 2,500 (S. Nos. near 1163-1166 of the text), 3004 medicaments S. No. 234, domestic LPG; Sch. III 2202 sweetened/flavoured beverages; Sch. VII 2402/2403 tobacco; services rates (Notification 15/2025-CT(Rate), amending 11/2017) and 10/2025 nil goods not reached in the e-Gazette (IDs 266190-266262 scanned): those still from the WB Commercial Taxes synopsis (official, secondary)"')
s = s.replace('rates from the WB Commercial Taxes synopsis of the 56th Council (B)"]', 'goods rates from 22 Sep 2025 checked in G.S.R. 641(E) (e-Gazette); services from the WB synopsis (B)"]')
open(p, "w").write(s); print(s.count("641(E)"))
