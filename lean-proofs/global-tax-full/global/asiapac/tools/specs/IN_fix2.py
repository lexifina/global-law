# IN_fix2.py (session 4): services notifications 15/2025 and 16/2025-CT(Rate) found in the e-Gazette (ID 266220) -> grade A
import os, re
p = os.path.expanduser("cmp20/global/asiapac/tools/in_gst.py"); s = open(p).read()
rep = [
 ("Sources (B): Notification 1/2017-Central Tax (Rate) as amended",
  "Sources (A, session 4): Notification 1/2017-Central Tax (Rate) as amended"),
 ("meeting. The notifications' own PDFs were not reached (gstcouncil.gov.in lists to 08/2025; CBIC not archived); the rates are\nread from",
  "meeting. Official e-Gazette texts read: G.S.R. 641(E) (9/2025-CT(Rate), ID 266209), G.S.R. 660(E) (10/2025-CT(Rate), ID 266210),\nG.S.R. 663(E) (15/2025-CT(Rate), amending 11/2017: serial 7 (i) hotel accommodation 2.5 % CGST, serial 35 beauty 2.5 %, serial\n34 betting 20 %) and G.S.R. 666(E) (16/2025-CT(Rate), amending 12/2017: S. Nos. 36C, 36D individual life and health insurance\nnil), all of 17 September 2025, in force 22 September (ID 266220). Period-1 figures appear as the replaced entries (\"for the\nfigure 6, the figure 9\"). Summary first read from"),
 ('"IN 5111: GST in two periods (kernel 2.1 DatedVat); goods rates from 22 Sep 2025 checked in G.S.R. 641(E) (e-Gazette); services from the WB synopsis (B)"',
  '"IN 5111: GST in two periods (kernel 2.1 DatedVat); from 22 Sep 2025: G.S.R. 641(E), 660(E), 663(E), 666(E) (e-Gazette, A)"'),
 ('10/2025-CT(Rate) (from 22 September 2025)"', '10/2025-CT(Rate) (G.S.R. 660(E)); services 11/2017 and 12/2017-CT(Rate) as amended by 15/2025 (G.S.R. 663(E)) and 16/2025-CT(Rate) (G.S.R. 666(E)) (from 22 September 2025)"'),
 ('"statute": "CGST/SGST Acts 2017 s. 9; Notifications 1/2017-CT(Rate) (to 21 Sep 2025), 9/2025 and 10/2025-CT(Rate) (from 22 Sep 2025)"',
  '"statute": "CGST/SGST Acts 2017 s. 9; Notifications 1/2017, 11/2017, 12/2017-CT(Rate) as amended (to 21 Sep 2025); 9/2025, 10/2025, 15/2025, 16/2025-CT(Rate) of 17 Sep 2025 (from 22 Sep 2025)"'),
 ('"grade": "B", "status": "modelled"', '"grade": "A", "status": "modelled"'),
 ("services rates (Notification 15/2025-CT(Rate), amending 11/2017) and 10/2025 nil goods not reached in the e-Gazette (IDs 266190-266262 scanned): those still from the WB Commercial Taxes synopsis (official, secondary)",
  "services from 22 Sep 2025 read in the e-Gazette: 15/2025-CT(Rate) G.S.R. 663(E) and 16/2025-CT(Rate) G.S.R. 666(E) (egazette.gov.in WriteReadData/2025/266220.pdf); 10/2025-CT(Rate) G.S.R. 660(E) (266210.pdf); period-1 rates taken from the entries these notifications replace"),
]
for a, b in rep:
    assert a in s, a[:60]
    s = s.replace(a, b)
open(p, "w").write(s); print("fixed")
