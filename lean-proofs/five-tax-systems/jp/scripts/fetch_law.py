"""Fetch one law from e-Gov 法令API v2 at an as-of date; save the XML and the revision info.
usage: python3 -I fetch_law.py <law_id> <asof YYYY-MM-DD> <outname>"""
import sys, json, base64, urllib.request, time, os
law_id, asof, name = sys.argv[1:4]
url = f"https://laws.e-gov.go.jp/api/2/law_data/{law_id}?asof={asof}&response_format=json&law_full_text_format=xml"
req = urllib.request.Request(url, headers={"User-Agent": "tax-formalisation-research/1.0"})
with urllib.request.urlopen(req, timeout=120) as r:
    d = json.load(r)
out = os.path.expanduser("~/cmp/jp/law")
xml = base64.b64decode(d["law_full_text"])
open(f"{out}/{name}_{asof}.xml", "wb").write(xml)
info = {"url": url, "law_info": d["law_info"], "revision_info": d["revision_info"]}
json.dump(info, open(f"{out}/{name}_{asof}.info.json", "w"), ensure_ascii=False, indent=1)
ri = d["revision_info"]
print(name, asof, ri["law_title"], ri["law_revision_id"], ri["amendment_law_title"], ri["amendment_law_num"], ri["amendment_enforcement_date"], len(xml))
