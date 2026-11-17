"""Courts as test cases, stage A' (second pass). Stage A kept income-tax decisions that touch a named computation
topic; this pass looks at the other income-tax decisions for a *liquidation*: one paragraph that states both a
taxable income (or RFR) figure and a tax figure, for an income year from 2015. Writes the kept decisions next to
stage A's (data/court/text/, tag prefix L_) and data/court/features_liq.jsonl.

usage: python3 -I harness/court_filter_liq.py OUTDIR ARCHIVE...   (12 worker processes)
"""
import json, os, re, sys, tarfile, zipfile
from multiprocessing import Pool
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from court_filter import IR, text_of  # noqa: E402

E = r"\d{1,3}(?:[  .]\d{3})*(?:,\d{1,2})?\s*(?:euros?|€)"
INC = re.compile(r"(?:revenu\s+(?:net\s+)?(?:global\s+)?imposable|revenu\s+fiscal\s+de\s+r[ée]f[ée]rence|base\s+d.imposition)[^.;]{0,120}?" + E, re.I)
TAXF = re.compile(r"(?:imp[ôo]t\s+(?:sur\s+le\s+revenu\s+)?(?:brut|net|d[ûu]|correspondant|r[ée]sultant|s.[ée]l[èe]ve)|droits\s+(?:simples|dus|rappel[ée]s)|montant\s+de\s+l.imp[ôo]t|cotisation\s+(?:d.imp[ôo]t\s+)?(?:de|s.[ée]l[èe]ve))[^.;]{0,120}?" + E, re.I)
YR = re.compile(r"(?:au\s+titre\s+de[s]?\s+(?:l.ann[ée]e\s+|ann[ée]es\s+)|revenus\s+(?:de\s+l.ann[ée]e\s+)?)(20(?:1[5-9]|2[0-5]))", re.I)


def one(name, raw, out, tag, skip):
    s = raw.decode("utf-8", "replace")
    if not IR.search(s):
        return 0, None
    fid = tag + "_" + os.path.basename(name).replace(".xml", "")
    if fid in skip:
        return 1, None
    meta, b = text_of(raw)
    if not YR.search(b):
        return 1, None
    paras = b.split("\n")
    hits = [p for p in paras if INC.search(p) and TAXF.search(p)]
    if not hits:
        return 1, None
    feat = {"id": "L_" + fid, "court": meta.get("Nom_Juridiction") or meta.get("JURIDICTION"),
            "date": meta.get("Date_Lecture") or meta.get("DATE_DEC"), "number": meta.get("Numero_Dossier") or meta.get("NUMERO"),
            "ecli": meta.get("Numero_ECLI") or meta.get("ECLI"), "len": len(b), "liq_paras": len(hits),
            "years": sorted({int(y) for y in YR.findall(b)})}
    with open(os.path.join(out, "text", feat["id"] + ".txt"), "w", encoding="utf-8") as f:
        for k, v in meta.items():
            f.write(f"{k}: {v}\n")
        f.write("\n" + b)
    return 1, feat


def run(arg):
    out, path, skip = arg
    n = ir = 0
    feats = []
    if path.endswith(".zip"):
        tag = os.path.basename(path).split("_")[0]
        with zipfile.ZipFile(path) as z:
            for nm in z.namelist():
                if nm.endswith(".xml"):
                    n += 1
                    a, f = one(nm, z.read(nm), out, tag, skip)
                    ir += a
                    feats += [f] if f else []
    else:
        with tarfile.open(path, "r:gz") as tf:
            for m in tf:
                if m.isfile() and m.name.endswith(".xml"):
                    n += 1
                    a, f = one(m.name, tf.extractfile(m).read(), out, "JADE", skip)
                    ir += a
                    feats += [f] if f else []
    return path, n, ir, feats


if __name__ == "__main__":
    out = sys.argv[1]
    skip = {json.loads(l)["id"] for l in open(out + "/features.jsonl")}
    arcs = sorted(sys.argv[2:], key=lambda p: -os.path.getsize(p))
    with Pool(12) as p, open(out + "/features_liq.jsonl", "w") as ff:
        for path, n, ir, feats in p.imap_unordered(run, [(out, a, skip) for a in arcs]):
            for f in feats:
                ff.write(json.dumps(f, ensure_ascii=False) + "\n")
            ff.flush()
            print(path, n, ir, len(feats), flush=True)
    print("LIQ-DONE")
