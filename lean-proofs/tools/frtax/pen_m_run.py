"""Penalty study: run correctif cases through Mlang (DGFiP M code + Mlang's correctif driver m_ext/<year>/correctif.m)
and read off the penalty variables.
Usage: python3 -I harness/pen_m_run.py CASES.json OUT.json [jobs]
CASES.json: list of {"id", "year", "decl": {box: value}, "rappels": [[MMYYYY, code, amount, penalty], ...]}
(an empty "rappels" runs the primitif only). Each case is written as runs/pen/m/<id>.irj; every output variable is
given the expected value -1 so the interpreter prints what it computed."""
import json, os, re, subprocess, sys
from multiprocessing import Pool
OUTV = ["NBMOIS2", "NBMOIS", "RETX", "RETIR", "NMAJ1", "NMAJ3", "NMAJ4", "MAJTX1", "MAJTX3", "MAJTX4", "IRN", "IRNET",
        "TOTIRCUM", "IAN", "IINET", "IDRS", "NATMAJ", "TL_IR", "IRANT", "ANTIRAFF", "IRNIN", "IRNIN_INR"]
PRIMV = ["IRN", "IAN", "IINET", "IDRS", "NBPT", "IRNET", "RNI"]
HERE = os.path.expanduser("~/fr")
def irj(c):
    L = ["#NOM", "PEN_" + c["id"], "#ENTREES-PRIMITIF", f"ANREV/{c['year']}", "REGCO/1"]
    L += [f"{k}/{v}" for k, v in c["decl"].items()]
    L += ["NOTRAIT/23" if c["rappels"] else "NOTRAIT/16", "#CONTROLES-PRIMITIF", "#RESULTATS-PRIMITIF"]
    if not c["rappels"]:
        L += [f"{v}/-1" for v in PRIMV] + ["#ENTREES-CORRECTIF", "#CONTROLES-CORRECTIF", "#RESULTATS-CORRECTIF", "##"]
        return "\n".join(L) + "\n"
    L += ["NBPT/-1", "#ENTREES-RAPPELS"]
    for i, (my, code, amt, pen) in enumerate(c["rappels"]):
        mm, yy = int(str(my)[:-4]), int(str(my)[-4:])
        L.append(f"{yy:04d}{mm:02d}15/{i+1}/{code}/{amt}/R/{int(pen):02d}//{int(my):06d}/")
    L += ["#CONTROLES-RAPPELS", "#RESULTATS-RAPPELS"] + [f"{v}/-1" for v in OUTV] + ["##"]
    return "\n".join(L) + "\n"
def run(c):
    d = os.path.join(HERE, "runs/pen/m"); os.makedirs(d, exist_ok=True)
    f = os.path.join(d, c["id"] + ".irj")
    open(f, "w").write(irj(c))
    p = subprocess.run([os.path.join(HERE, "harness/pen_mlang_corr.sh"), str(c["year"]), f], capture_output=True,
                       text=True, timeout=900)
    out = p.stdout + p.stderr
    vals = {m.group(1): float(m.group(2)) for m in re.finditer(r"KO \| (\w+) attendue : -1 - evalu\S+ : (-?[\d.]+)", out)}
    anos = re.findall(r"(A\d{3}\w*|DD\d+\w*)", " ".join(l for l in out.splitlines() if "nomalie" in l or "ANO" in l))
    return {"id": c["id"], "vals": vals, "anos": anos, "ok": "Test exécuté" in out or "Test ex" in out,
            "tail": out[-400:] if not vals else ""}
if __name__ == "__main__":
    cases = json.load(open(sys.argv[1]))
    jobs = int(sys.argv[3]) if len(sys.argv) > 3 else 10
    with Pool(jobs) as p:
        res = list(p.imap(run, cases))
    json.dump(res, open(sys.argv[2], "w"), indent=1)
    print(len(res), "cases;", sum(1 for r in res if r["vals"]), "with values")
