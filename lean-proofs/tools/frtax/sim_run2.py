"""Oracle: the DGFiP's production simulator (simulateur-ir-ifi.impots.gouv.fr, calc-2025.cgi for income 2024,
calc-2026.cgi for income 2025). Posts returns at about one request every 1.2 s, saves each answer (resumable).

usage: sim_run.py cases.jsonl out.jsonl N_PER_YEAR
"""
import html, json, os, random, re, sys, time, urllib.parse, urllib.request

URL = "https://simulateur-ir-ifi.impots.gouv.fr/cgi-bin/calc-{}.cgi"
LABELS = {
    "Nombre de parts": "NBPT",
    "Revenu fiscal de référence": "REVKIRE",
    "Revenu brut global ou déficit": "RBG",
    "Revenu net imposable ou déficit à reporter": "RNI",
    "Droits simples": "IDRS",
    "Décote": "IDEC",
    "Total des réductions d'impôt": "ITRED",
    "Impôt proportionnel": "PROP",
    "Contribution exceptionnelle sur les hauts revenus nette": "CEHR",
    "Contribution différentielle sur les hauts revenus nette": "CDHR",
    "Impôt avant crédits d'impôts": "AVCR",
    "Impôt sur le revenu net": "IRNET",
    "Montant net des prélèvements sociaux (sur revenus du patrimoine et revenus d'activité et de remplacement de source étrangère)": "PS",
}


def parse(page):
    t = html.unescape(re.sub(r"<[^>]+>", "\n", page))
    lines = [l.strip() for l in t.split("\n") if l.strip()]
    out = {}
    for i, l in enumerate(lines[:-1]):
        if l in LABELS and LABELS[l] not in out:
            m = re.search(r"-?\d[\d ]*(?:[.,]\d+)?", lines[i + 1].replace("\xa0", " "))
            if m:
                out[LABELS[l]] = float(m.group(0).replace(" ", "").replace(",", "."))
    err = [l for l in lines if l.startswith("Erreur")]
    if err:
        out["_error"] = err[0][:200]
    return out


SIT = {"0AM": "M", "0AO": "O", "0AC": "C", "0AD": "D", "0AV": "V"}


def form_fields(boxes):
    """The fields the simulator's own page posts: situation and residence as pre_ fields, birth years of disabled
    children (0G0.., 0I0..) and of disabled dependants (0R0..)."""
    f = {"pre_situation_residence": "M"}
    for k, v in boxes.items():
        if k in SIT:
            f["pre_situation_famille"] = SIT[k]
        else:
            f[k] = v
    for i in range(boxes.get("0CG", 0)):
        f[f"0G{i}"] = boxes.get(f"0F{i}", 2015)
    for i in range(boxes.get("0CI", 0)):
        f[f"0I{i}"] = boxes.get(f"0H{i}", 2015)
    for i in range(boxes.get("0CR", 0)):
        f[f"0R{i}"] = 1960
    return f


def post(year, boxes):
    data = urllib.parse.urlencode(form_fields(boxes)).encode()
    req = urllib.request.Request(URL.format(year + 1), data=data, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read().decode("latin-1")


def main():
    cases = [json.loads(l) for l in open(sys.argv[1])]
    out_path, n = sys.argv[2], int(sys.argv[3])
    done = set()
    if os.path.exists(out_path):
        done = {json.loads(l)["id"] for l in open(out_path)}
    random.seed(7)
    sel = []
    for year in (2024, 2025):
        ys = [c for c in cases if c["year"] == year]
        high = [c for c in ys if any(c["boxes"].get(k, 0) > 100000 for k in ("1AJ", "2DC", "3VG"))]
        sel += random.sample(high, min(len(high), n // 7)) + random.sample(ys, n - min(len(high), n // 7))
    with open(out_path, "a") as f:
        for c in sel:
            if c["id"] in done:
                continue
            try:
                r = parse(post(c["year"], c["boxes"]))
            except Exception as e:
                r = {"_error": repr(e)[:200]}
            f.write(json.dumps({"id": c["id"], "year": c["year"], "sim": r}) + "\n")
            f.flush()
            time.sleep(1.2)
    print("SIM-DONE")


if __name__ == "__main__":
    main()
