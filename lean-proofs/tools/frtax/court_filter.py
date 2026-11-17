"""Courts as test cases, stage A. Scan every administrative decision (DILA JADE dump + justice-administrative open-data
zips) and keep those that are about French personal income tax AND touch a computation topic. For each kept decision
write a plain-text copy (metadata header + body) and one JSON line of features.

usage: python3 -I harness/court_filter.py OUTDIR ARCHIVE...  (12 worker processes)
Writes OUTDIR/text/<tag>_<id>.txt, OUTDIR/features.jsonl (kept), OUTDIR/scan_counts.jsonl (per archive)."""
import html, json, os, re, sys, tarfile, zipfile
from multiprocessing import Pool

IR = re.compile(r"imp[ôo]t\s+sur\s+le\s+revenu", re.I)
TOPICS = {
    "qf": r"quotient\s+familial|demi[- ]parts?|nombre\s+de\s+parts|parts?\s+(fiscales?|suppl[ée]mentaires?)|\bcase\s+[TLPWSFGHN]\b|article\s+19[45]\b|parent\s+isol[ée]|r[ée]sidence\s+altern[ée]e|ancien\s+combattant|carte\s+d.invalidit[ée]|carte\s+mobilit[ée]\s+inclusion",
    "frais": r"frais\s+r[ée]els|d[ée]duction\s+forfaitaire\s+de\s+10|frais\s+professionnels|bar[èe]me\s+kilom[ée]trique",
    "pension": r"pensions?\s+alimentaires?|6\s*GU|6\s*EL|article\s+156\b.{0,40}II.{0,10}2|contribution\s+aux\s+charges\s+du\s+mariage|enfants?\s+majeurs?",
    "157bis": r"157\s*bis|abattement.{0,40}personnes?\s+[âa]g[ée]es",
    "decote": r"d[ée]cote|1657|seuil\s+de\s+(mise\s+en\s+)?recouvrement",
    "cehr": r"contribution\s+exceptionnelle\s+sur\s+les\s+hauts\s+revenus|223\s*sexies",
    "pfu": r"pr[ée]l[èe]vement\s+forfaitaire\s+unique|200\s*A\b|option\s+(globale\s+)?pour\s+le\s+bar[èe]me|2\s*OP\b|abattement\s+de\s+40",
    "micro": r"micro[- ](BIC|BNC|entreprise|entrepreneur|social|fiscal|foncier)|r[ée]gime\s+d[ée]claratif\s+sp[ée]cial|50-0|102\s*ter|32\b.{0,20}code\s+g[ée]n[ée]ral|versement\s+lib[ée]ratoire|151-0",
    "foncier": r"revenus?\s+fonciers?|d[ée]ficit\s+foncier|156\s*I.{0,10}3",
    "pv": r"plus-values?\s+de\s+cession\s+de\s+(valeurs\s+mobili[èe]res|titres|droits\s+sociaux)|150-0\s*[AD]|abattement\s+pour\s+dur[ée]e\s+de\s+d[ée]tention",
    "red_credit": r"r[ée]duction\s+d.imp[ôo]t|cr[ée]dit\s+d.imp[ôo]t|199\s*sexdecies|200\s*quater\s*B|200\b.{0,30}code\s+g[ée]n[ée]ral|emploi\s+[àa]\s+domicile|garde\s+des?\s+(jeunes\s+)?enfants|\bdons?\b.{0,40}(organismes?|associations?)",
    "plafond": r"200-0\s*A|plafonnement\s+(global\s+)?des\s+(avantages|niches)",
    "quotient": r"163-0\s*A|syst[èe]me\s+du\s+quotient|revenus?\s+exceptionnels?|revenus?\s+diff[ée]r[ée]s",
    "liquid": r"droits\s+(simples|rappel[ée]s)|imp[ôo]t\s+(brut|net|d[ûu])|revenu\s+(net\s+)?imposable|revenu\s+fiscal\s+de\s+r[ée]f[ée]rence|bar[èe]me\s+progressif|tranche",
}
TOPIC_RE = {k: re.compile(v, re.I) for k, v in TOPICS.items()}
EUROS = re.compile(r"\d[\d  .]*(?:,\d+)?\s*(?:euros?|€)", re.I)
YEARS = re.compile(r"(?:au\s+titre\s+de[s]?\s+(?:l.ann[ée]e\s+|ann[ée]es\s+)|revenus\s+(?:de\s+l.ann[ée]e\s+)?)((?:19|20)\d\d)", re.I)
PARTS = re.compile(r"(\d(?:[,.]\d+)?|une|deux|trois|quatre)\s+parts?\b", re.I)


def text_of(raw):
    t = raw.decode("utf-8", "replace")
    meta = {}
    for k in ("ID", "TITRE", "DATE_DEC", "JURIDICTION", "NUMERO", "PUBLI_RECUEIL", "ECLI", "Identification", "Nom_Juridiction",
              "Code_Juridiction", "Numero_Dossier", "Date_Lecture", "Numero_ECLI", "Code_Publication"):
        m = re.search(rf"<{k}>(.*?)</{k}>", t, re.S)
        if m:
            meta[k] = html.unescape(m.group(1).strip())
    body = re.search(r"<(CONTENU|Texte_Integral)>(.*?)</\1>", t, re.S)
    b = body.group(2) if body else t
    b = re.sub(r"<br\s*/?>|</p>", "\n", b)
    b = html.unescape(re.sub(r"<[^>]+>", " ", b))
    b = re.sub(r"[ \t ]+", " ", b)
    b = re.sub(r"\n\s*\n+", "\n", b)
    return meta, b


def one(name, raw, out, tag):
    """returns (is_ir, kept_features or None)"""
    if not IR.search(raw.decode("utf-8", "replace")):
        return 0, None
    meta, b = text_of(raw)
    if not IR.search(b):
        return 0, None
    topics = {k: len(r.findall(b)) for k, r in TOPIC_RE.items()}
    topics = {k: v for k, v in topics.items() if v}
    if not any(k != "liquid" for k in topics):
        return 1, None
    fid = tag + "_" + os.path.basename(name).replace(".xml", "")
    feat = {"id": fid, "court": meta.get("Nom_Juridiction") or meta.get("JURIDICTION"),
            "date": meta.get("Date_Lecture") or meta.get("DATE_DEC"), "number": meta.get("Numero_Dossier") or meta.get("NUMERO"),
            "ecli": meta.get("Numero_ECLI") or meta.get("ECLI"), "len": len(b), "topics": topics,
            "euros": len(EUROS.findall(b)), "years": sorted({int(y) for y in YEARS.findall(b)}),
            "parts": len(PARTS.findall(b))}
    with open(os.path.join(out, "text", fid + ".txt"), "w", encoding="utf-8") as f:
        for k, v in meta.items():
            f.write(f"{k}: {v}\n")
        f.write("\n" + b)
    return 1, feat


def run(arg):
    out, path = arg
    n = ir = 0
    feats = []
    if path.endswith(".zip"):
        tag = os.path.basename(path).split("_")[0]
        with zipfile.ZipFile(path) as z:
            for nm in z.namelist():
                if not nm.endswith(".xml"):
                    continue
                n += 1
                a, f = one(nm, z.read(nm), out, tag)
                ir += a
                if f:
                    feats.append(f)
    else:
        with tarfile.open(path, "r:gz") as tf:
            for m in tf:
                if not (m.isfile() and m.name.endswith(".xml")):
                    continue
                n += 1
                a, f = one(m.name, tf.extractfile(m).read(), out, "JADE")
                ir += a
                if f:
                    feats.append(f)
    return path, n, ir, feats


if __name__ == "__main__":
    out = sys.argv[1]
    os.makedirs(out + "/text", exist_ok=True)
    arcs = sorted(sys.argv[2:], key=lambda p: -os.path.getsize(p))
    with Pool(12) as p, open(out + "/features.jsonl", "w") as ff, open(out + "/scan_counts.jsonl", "w") as fc:
        for path, n, ir, feats in p.imap_unordered(run, [(out, a) for a in arcs]):
            for f in feats:
                ff.write(json.dumps(f, ensure_ascii=False) + "\n")
            fc.write(json.dumps({"archive": os.path.basename(path), "scanned": n, "ir": ir, "kept": len(feats)}) + "\n")
            fc.flush(); ff.flush()
            print(path, n, ir, len(feats), flush=True)
    print("FILTER-DONE")
