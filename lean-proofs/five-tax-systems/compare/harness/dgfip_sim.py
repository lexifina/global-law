"""Ask the DGFiP's production simulator (simulateur-ir-ifi.impots.gouv.fr) for the French income tax of the OECD's
two-earner couple (100 % + 100 % of the average wage, two children), income 2025 and income 2024, to arbitrate the
gap between the Lean model and the OECD's Taxing Wages table. Two requests, several seconds apart. Field handling
copied from ~/fr/harness/sim_run2.py (form_fields, parse). Raw pages saved in refs/dgfip/."""
import os
import html, json, re, sys, time, urllib.parse, urllib.request
URL = "https://simulateur-ir-ifi.impots.gouv.fr/cgi-bin/calc-{}.cgi"
LABELS = {"Nombre de parts": "NBPT", "Revenu fiscal de référence": "REVKIRE", "Revenu brut global ou déficit": "RBG",
          "Revenu net imposable ou déficit à reporter": "RNI", "Droits simples": "IDRS", "Décote": "IDEC",
          "Impôt avant crédits d'impôts": "AVCR", "Impôt sur le revenu net": "IRNET"}
SIT = {"0AM": "M", "0AO": "O", "0AC": "C", "0AD": "D", "0AV": "V"}
def parse(page):
    t = html.unescape(re.sub(r"<[^>]+>", "\n", page))
    lines = [l.strip() for l in t.split("\n") if l.strip()]
    out = {}
    for i, l in enumerate(lines[:-1]):
        if l in LABELS and LABELS[l] not in out:
            m = re.search(r"-?\d[\d ]*(?:[.,]\d+)?", lines[i + 1].replace("\xa0", " "))
            if m:
                out[LABELS[l]] = float(m.group(0).replace(" ", "").replace(",", "."))
    return out
def post(year, boxes):
    f = {"pre_situation_residence": "M"}
    for k, v in boxes.items():
        if k in SIT: f["pre_situation_famille"] = SIT[k]
        else: f[k] = v
    req = urllib.request.Request(URL.format(year + 1), data=urllib.parse.urlencode(f).encode(),
                                 headers={"User-Agent": "Mozilla/5.0 (research; five-country tax comparison)"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read().decode("latin-1")
cases = json.loads(sys.argv[1])
res = []
for c in cases:
    page = post(c["year"], c["boxes"])
    open(os.path.expanduser(f"~/cmp/compare/refs/dgfip/{c['id']}.html"), "w").write(page)
    r = parse(page); r["id"] = c["id"]; res.append(r); print(json.dumps(r))
    time.sleep(3)
json.dump(res, open(os.path.expanduser("~/cmp/compare/refs/dgfip/oecd_m100_100.json"), "w"), indent=1)
