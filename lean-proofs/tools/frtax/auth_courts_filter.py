"""Filter administrative-court decisions (DILA JADE tar.gz, justice-administrative monthly zips) down to those
mentioning any term of interest; write each kept decision as plain text with a metadata header.
Usage: python3 -I harness/auth_courts_filter.py OUTDIR ARCHIVE...   (runs one process per archive, at most 6)"""
import html, os, re, sys, tarfile, zipfile
from multiprocessing import Pool
TERMS = re.compile(r"199\s*quater\s*C|223\s*sexies|204\s*[HM]\b|204\s*E\b|1657|81\s*quater|197\s*C\b|taux\s+effectif|"
                   r"article\s+193\b|décote|hauts\s+revenus|cotisations?\s+syndicales?|151-0|prélèvement\s+à\s+la\s+source|"
                   r"taux\s+de\s+prélèvement|euro\s+le\s+plus\s+proche|seuil\s+de\s+(mise\s+en\s+)?recouvrement|heures\s+supplémentaires", re.I)
TAX = re.compile(r"impôt sur le revenu|code général des impôts|contribution exceptionnelle", re.I)
def text_of(raw):
    t = raw.decode("utf-8", "replace")
    meta = {}
    for k in ("ID", "TITRE", "DATE_DEC", "JURIDICTION", "NUMERO", "PUBLI_RECUEIL", "Identification", "Nom_Juridiction",
              "Code_Juridiction", "Numero_Dossier", "Date_Lecture", "Numero_ECLI", "Code_Publication"):
        m = re.search(rf"<{k}>(.*?)</{k}>", t, re.S)
        if m: meta[k] = html.unescape(m.group(1).strip())
    body = re.search(r"<(CONTENU|Texte_Integral)>(.*?)</\1>", t, re.S)
    b = body.group(2) if body else t
    b = re.sub(r"<br\s*/?>|</p>", "\n", b); b = html.unescape(re.sub(r"<[^>]+>", " ", b))
    b = re.sub(r"[ \t ]+", " ", b); b = re.sub(r"\n\s*\n+", "\n", b)
    return meta, b
def keep(name, raw, out, tag):
    if not TERMS.search(raw.decode("utf-8", "replace")): return None
    meta, b = text_of(raw)
    if not (TAX.search(b) and TERMS.search(b)): return None
    terms = sorted(set(m.group(0).lower() for m in TERMS.finditer(b)))
    fn = os.path.join(out, tag + "_" + os.path.basename(name).replace(".xml", ".txt"))
    with open(fn, "w", encoding="utf-8") as f:
        for k, v in meta.items(): f.write(f"{k}: {v}\n")
        f.write("TERMS: " + "; ".join(terms) + "\n\n" + b)
    return fn
def run(arg):
    out, path = arg
    n = k = 0
    if path.endswith(".zip"):
        tag = os.path.basename(path).split("_")[0]
        with zipfile.ZipFile(path) as z:
            for nm in z.namelist():
                if not nm.endswith(".xml"): continue
                n += 1; k += keep(nm, z.read(nm), out, tag) is not None
    else:
        with tarfile.open(path, "r:gz") as tf:
            for m in tf:
                if not (m.isfile() and m.name.endswith(".xml")): continue
                n += 1; k += keep(m.name, tf.extractfile(m).read(), out, "JADE") is not None
    return path, n, k
if __name__ == "__main__":
    out = sys.argv[1]; os.makedirs(out, exist_ok=True)
    arcs = sys.argv[2:]
    arcs.sort(key=lambda p: -os.path.getsize(p))
    with Pool(6) as p:
        for path, n, k in p.imap_unordered(run, [(out, a) for a in arcs]):
            print(path, n, k, flush=True)
