"""Assemblée nationale written questions (open-data zips) -> one text file per question that mentions income tax.
Usage: python3 -I harness/auth_an_extract.py OUTDIR ZIP..."""
import html, json, os, re, sys, zipfile
out = sys.argv[1]; os.makedirs(out, exist_ok=True)
TAX = re.compile(r"impôt sur le revenu|impôts?\b|prélèvement à la source|code général des impôts|fiscal", re.I)
def g(o, *ks):
    for k in ks:
        if isinstance(o, list): o = o[0] if o else None
        if not isinstance(o, dict): return None
        o = o.get(k)
    return o
def texts(node, key):
    v = node.get(key) if isinstance(node, dict) else None
    if v is None: return []
    return v if isinstance(v, list) else [v]
n = k = 0
for zp in sys.argv[2:]:
    with zipfile.ZipFile(zp) as z:
        for nm in z.namelist():
            if not nm.endswith(".json"): continue
            n += 1
            q = json.loads(z.read(nm))["question"]
            qs = texts(q.get("textesQuestion") or {}, "texteQuestion")
            rs = texts(q.get("textesReponse") or {}, "texteReponse")
            body = "\n".join((x.get("texte") or "") for x in qs) + "\n=== RÉPONSE ===\n" + "\n".join((x.get("texte") or "") for x in rs)
            body = html.unescape(re.sub(r"<[^>]+>", " ", body))
            if not TAX.search(body): continue
            k += 1
            hdr = {"uid": q.get("uid"), "numero": g(q, "identifiant", "numero"), "legislature": g(q, "identifiant", "legislature"),
                   "rubrique": g(q, "indexationAN", "rubrique"), "analyse": g(q, "indexationAN", "analyses", "analyse"),
                   "ministere": g(q, "minInt", "developpe"),
                   "jo_question": [(g(x, "infoJO", "dateJO"), g(x, "infoJO", "pageJO")) for x in qs],
                   "jo_reponse": [(g(x, "infoJO", "dateJO"), g(x, "infoJO", "pageJO")) for x in rs],
                   "cloture": g(q, "cloture", "libelleCloture")}
            with open(os.path.join(out, f"{q.get('uid')}.txt"), "w", encoding="utf-8") as f:
                for a, b in hdr.items(): f.write(f"{a}: {b}\n")
                f.write("\n" + body)
print(n, "questions;", k, "kept")
