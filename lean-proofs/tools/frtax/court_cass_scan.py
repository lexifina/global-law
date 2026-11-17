"""Courts as test cases, judicial side: scan the DILA CASS and INCA dumps (Cour de cassation, published and
unpublished) for criminal tax-fraud judgments (art. 1741 CGI / fraude fiscale) about income tax, and keep those
that state income-tax computation figures (parts, taxable income, tax due/evaded).
usage: python3 -I harness/court_cass_scan.py OUTDIR TARGZ..."""
import html, json, os, re, sys, tarfile
from multiprocessing import Pool
IR = re.compile(r"imp[ôo]t\s+sur\s+le\s+revenu", re.I)
FRAUD = re.compile(r"fraude\s+fiscale|1741\s+du\s+code\s+g[ée]n[ée]ral|soustraction\s+frauduleuse", re.I)
FIG = re.compile(r"quotient\s+familial|nombre\s+de\s+parts|revenu\s+(net\s+)?imposable[^.]{0,80}\d|droits\s+[ée]lud[ée]s[^.]{0,80}\d|imp[ôo]t\s+(d[ûu]|[ée]lud[ée])[^.]{0,80}\d", re.I)
def run(arg):
    out, path = arg
    n = ir = fr = k = 0
    rows = []
    with tarfile.open(path, "r:gz") as tf:
        for m in tf:
            if not (m.isfile() and m.name.endswith(".xml")): continue
            n += 1
            t = tf.extractfile(m).read().decode("utf-8", "replace")
            if not IR.search(t): continue
            ir += 1
            if not FRAUD.search(t): continue
            fr += 1
            meta = {kk: html.unescape(mm.group(1).strip()) for kk in ("ID", "FORMATION", "DATE_DEC", "NUMERO_AFFAIRE", "JURIDICTION", "ECLI", "SOLUTION")
                    for mm in [re.search(rf"<{kk}>(.*?)</{kk}>", t, re.S)] if mm}
            b = re.search(r"<CONTENU>(.*?)</CONTENU>", t, re.S)
            b = html.unescape(re.sub(r"<[^>]+>", " ", re.sub(r"<br\s*/?>", "\n", b.group(1) if b else t)))
            figs = FIG.findall(b)
            if not FIG.search(b): continue
            k += 1
            fid = os.path.basename(m.name)[:-4]
            open(f"{out}/{fid}.txt", "w", encoding="utf-8").write("\n".join(f"{a}: {v}" for a, v in meta.items()) + "\n\n" + b)
            rows.append({"id": fid, **meta, "nfig": len(FIG.findall(b))})
    return path, n, ir, fr, k, rows
if __name__ == "__main__":
    out = sys.argv[1]; os.makedirs(out, exist_ok=True)
    with Pool(2) as p, open(out + "/../cass_scan.jsonl", "w") as f:
        for path, n, ir, fr, k, rows in p.imap_unordered(run, [(out, a) for a in sys.argv[2:]]):
            f.write(json.dumps({"archive": os.path.basename(path), "scanned": n, "ir": ir, "fraud_ir": fr, "with_figures": k, "rows": rows}, ensure_ascii=False) + "\n")
            print(path, n, ir, fr, k, flush=True)
    print("CASS-DONE")
