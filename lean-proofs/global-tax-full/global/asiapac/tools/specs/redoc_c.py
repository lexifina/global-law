# redoc_c.py (session 4): re-document P1 C entries (what was tried this session) in results/taxes/Consumption.json and
# tools/specs/bulk_cons_c.json; move bulk entries of countries now modelled to bulk_cons_c_retired.json (mkcons_c.py
# regenerates every country in its input: re-running it on the old file would overwrite modelled families).
import json, os, glob, re
R = os.path.expanduser("cmp20/global/asiapac")
NEW = {
 "MH": {"5112": "tried (session 4): rmiparliament.org lists the Consumption Tax Act 2025 (2025-0047A) and Excise Tax Act 2025 (2025-0046), both 'Date Commenced 7 October 2025'; their PDFs answered 502 (2026-11-21); the Net Profit Tax Act 2025 of the same package applies from tax years beginning 1 Oct 2026 (s. 749 (2)), so the consumption tax may too; would unlock: the Consumption Tax Act 2025 text and its application date, and the Import Duties Act (48 MIRC Ch. 2) rates",
        "5121": "tried (session 4): as above (Excise Tax Act 2025 PDF 502); would unlock: the Import Duties Act schedule in force in 2025"},
 "BD": {"5111": "tried (session 4): nbr.gov.bd regulations/acts/vat (table loaded by script: empty in the HTML), VAT Instruction PDFs (only 2026-27 published), bdlaws.minlaw.gov.bd (no answer), Wayback (offline 2026-11-21); would unlock: the VAT and SD Act 2012 as amended to 2025 (First Schedule exemptions, Third Schedule reduced rates) and the 2024-25/2025-26 VAT Instructions",
        "5121": "tried (session 4): as above; would unlock: the Third Schedule supplementary duty rates"},
 "BT": {"5112": "tried (session 4): drc.gov.bt WordPress media API (searches 'sales tax', 'tariff', 'Act', 'rules'): the Sales Tax, Customs and Excise Act 2000 is not published there (only the GST Act 2020 consolidation, Excise Tax Act 2025 and the 2026 tariff schedule, for 2026); Tax-Act-of-Bhutan-2022.pdf is damaged; Wayback offline; would unlock: the 2000 Act with the 2025 sales tax schedule (BTCTS 2022 sales tax column)",
        "5121": "tried (session 4): as above (Excise Tax Act of Bhutan 2025 applies with the GST from 2026); would unlock: the 2025 excise/green tax schedule"},
 "MV": {"5111": "tried (session 4): mira.gov.mv 403, mof.gov.mv no answer, Wayback offline (2026-11-21); customs.gov.mv answers (tariff, not the GST Act); would unlock: the GST Act (Law 10/2011) consolidation with the 2025 tourism rate change",
        "5121": "tried (session 4): customs.gov.mv answers (import duty tariff, not read this pass); would unlock: the 2025 tariff for tobacco and alcohol"},
 "IR": {"5111": "tried (session 4): qavanin.ir answers with a bot-check page (not bypassed); rc.majlis.ir and intamedia.ir no answer; Wayback offline; would unlock: the permanent VAT Law (1400) and the Budget Law 1404 rate",
        "5121": "tried (session 4): as above"},
}
for cc, m in NEW.items():
    p = f"{R}/{cc.lower()}/results/taxes/Consumption.json"; d = json.load(open(p))
    for t in d:
        if t.get("grade") == "C" and t["oecd"] in m: t["unsupported"] = [m[t["oecd"]]]
    json.dump(d, open(p, "w"), indent=1, ensure_ascii=False)
b = f"{R}/tools/specs/bulk_cons_c.json"; B = json.load(open(b)); ret = {}
for cc, s in list(B.items()):
    if cc in NEW:
        for t in s["taxes"]:
            if t.get("grade") == "C" and t["oecd"] in NEW[cc]: t["unsupported"] = [NEW[cc][t["oecd"]]]
    G = cc.lower().replace("-", "").capitalize() + "Global"
    lean = open(f"{R}/{cc.lower()}/lean/{G}/Consumption.lean").read()
    if "def families : List Family := []" not in lean:
        ret[cc] = B.pop(cc)
json.dump(B, open(b, "w"), indent=1, ensure_ascii=False)
rp = f"{R}/tools/specs/bulk_cons_c_retired.json"
old = json.load(open(rp)) if os.path.exists(rp) else {}
old.update(ret); json.dump(old, open(rp, "w"), indent=1, ensure_ascii=False)
print("kept in bulk:", sorted(B)); print("retired:", sorted(ret))
