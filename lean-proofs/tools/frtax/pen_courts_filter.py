"""Penalty study: filter administrative-court decisions (DILA JADE tar.gz, justice-administrative monthly zips) to
income-tax decisions about interest for late payment or majorations (CGI art. 1727-1730, 1758 A, L62 LPF).
Writes one JSONL.gz per archive: {"src","meta","terms","text"}.
Usage: python3 -I harness/pen_courts_filter.py OUTDIR ARCHIVE...   (at most 10 processes)"""
import gzip, html, json, os, re, sys, tarfile, zipfile
from multiprocessing import Pool
PEN = re.compile(r"\b17(27|28|29|30)\b|1758\s*A\b|intérêts?\s+de\s+retard|manquement\s+délibéré|manoeuvres\s+frauduleuses|"
                 r"manœuvres\s+frauduleuses|abus\s+de\s+droit|activité\s+occulte|droit\s+à\s+l'erreur|L\.?\s*62\b|"
                 r"majorations?\s+de\s+(10|40|80)\s*%", re.I)
TAX = re.compile(r"impôt\s+sur\s+le\s+revenu|contributions?\s+sociales|contribution\s+exceptionnelle\s+sur\s+les\s+hauts", re.I)
QUICK = re.compile(rb"1727|1728|1729|1730|1758|int\xc3\xa9r\xc3\xaats? de retard|manquement d\xc3\xa9lib\xc3\xa9r\xc3\xa9|frauduleuses|abus de droit|occulte|droit \xc3\xa0 l'erreur|L\.? ?62")
def text_of(t):
    meta = {}
    for k in ("ID", "TITRE", "DATE_DEC", "JURIDICTION", "NUMERO", "PUBLI_RECUEIL", "Identification", "Nom_Juridiction",
              "Code_Juridiction", "Numero_Dossier", "Date_Lecture", "Numero_ECLI", "Code_Publication", "TYPE_REC", "FORMATION"):
        m = re.search(rf"<{k}>(.*?)</{k}>", t, re.S)
        if m: meta[k] = html.unescape(m.group(1).strip())
    body = re.search(r"<(CONTENU|Texte_Integral)>(.*?)</\1>", t, re.S)
    b = body.group(2) if body else t
    b = re.sub(r"<br\s*/?>|</p>", "\n", b); b = html.unescape(re.sub(r"<[^>]+>", " ", b))
    b = re.sub(r"[ \t  ]+", " ", b); b = re.sub(r"\n\s*\n+", "\n", b)
    return meta, b
def keep(name, raw):
    if not QUICK.search(raw): return None
    meta, b = text_of(raw.decode("utf-8", "replace"))
    if not (TAX.search(b) and PEN.search(b)): return None
    terms = sorted(set(m.group(0).lower() for m in PEN.finditer(b)))
    return {"src": os.path.basename(name), "meta": meta, "terms": terms, "text": b}
def run(arg):
    out, path = arg
    n = k = 0
    tag = os.path.basename(path).split(".")[0]
    fo = gzip.open(os.path.join(out, tag + ".jsonl.gz"), "wt", encoding="utf-8")
    def emit(nm, raw):
        nonlocal n, k
        n += 1; r = keep(nm, raw)
        if r: k += 1; fo.write(json.dumps(r, ensure_ascii=False) + "\n")
    if path.endswith(".zip"):
        with zipfile.ZipFile(path) as z:
            for nm in z.namelist():
                if nm.endswith(".xml"): emit(nm, z.read(nm))
    else:
        with tarfile.open(path, "r:gz") as tf:
            for m in tf:
                if m.isfile() and m.name.endswith(".xml"): emit(m.name, tf.extractfile(m).read())
    fo.close()
    return path, n, k
if __name__ == "__main__":
    out = sys.argv[1]; os.makedirs(out, exist_ok=True)
    arcs = sorted(sys.argv[2:], key=lambda p: -os.path.getsize(p))
    with Pool(10) as p:
        for path, n, k in p.imap_unordered(run, [(out, a) for a in arcs]):
            print(path, n, k, flush=True)
