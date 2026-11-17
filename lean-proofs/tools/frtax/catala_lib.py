"""Shared runners for the Catala head-to-head: the Catala impot_revenu module (OCaml backend, driver
~/fr/catala/ocaml/driver/catala_ir.ml), the Lean model (frtax) and Mlang (cal<year>), on returns in the 2042 box
format {"id", "year", "boxes": {"1AJ": 30000, ...}}.

Catala figures (driver output): NBPT, ABAT196B, TS_RBG, TS_DEF, RENTES, BIC_RBG, BIC_DEF*, BNC_RBG, BNC_DEF*,
RBG (our sum of the three category scopes, less professional deficits), DEFGLOB; IGNORED = boxes the mapping does
not read; ERR = the Catala code stopped (assertion, no applicable rule).
"""
import json, os, re, subprocess, tempfile, time, glob

HOME = os.path.expanduser("~")
CATALA = f"{HOME}/fr/catala/ocaml/_build/default/driver/catala_ir.exe"
LEAN = f"{HOME}/fr/lean/.lake/build/bin/frtax"
BIN = f"{HOME}/fr/bin"

# M variables read back (restituee): parts, revenu brut global, revenu net global, taxable income, RFR, and the
# category nets
MVARS = ["NBPT", "RBG1", "RNG", "RNI", "REVKIRE", "TSPR", "TSPRT", "RVTOT", "BIN", "BICNPF", "BNN", "BNCIF",
         "BNCPHQF", "BNCNPHQF", "BNCDF", "BNCDF1", "BNCDF2", "BNCDF3", "BNCDF4", "BNCDF5", "BNCDF6", "DAR", "RBL",
         "ABTPA", "ABTMA", "ABVIE", "ABMAR"]


def line(c):
    return f"{c['id']};{c['year']};" + ",".join(f"{k}={v}" for k, v in c["boxes"].items())


def parse_kv(s):
    out = {}
    for kv in s.split(";")[1:]:
        if "=" in kv:
            k, v = kv.split("=", 1)
            if k in ("ERR", "IGNORED"):
                out[k] = v
            else:
                try:
                    out[k] = float(v)
                except ValueError:
                    out[k] = v
    return out


def run_catala(cases, time_reps=0):
    inp = "".join(line(c) + "\n" for c in cases)
    args = [CATALA] + (["-time", str(time_reps)] if time_reps else [])
    r = subprocess.run(args, input=inp, capture_output=True, text=True)
    out = {}
    for l in r.stdout.splitlines():
        if l.startswith("ERR;"):
            continue
        out[l.split(";", 1)[0]] = parse_kv(l)
    if time_reps:
        m = re.search(r"TIME (\d+) evaluations, ([\d.]+) us", r.stderr)
        out["_time_us"] = float(m.group(2)) if m else None
    return out


def run_lean(cases):
    inp = "".join(line(c) + "\n" for c in cases)
    r = subprocess.run([LEAN], input=inp, capture_output=True, text=True)
    out = {}
    for l in r.stdout.splitlines():
        p = l.split(";")
        if p[0] != "ERR":
            out[p[0]] = {kv.split("=")[0]: float(kv.split("=")[1]) for kv in p[1:] if "=" in kv}
    return out


def run_m(year, cases, mvars=MVARS):
    """Mlang cal<year> on the returns (REGCO/1, ANREV/<year> as in ofsuite_run). A return M refuses comes back as
    {"_refused": <anomaly>}. M omits variables that are zero."""
    cal = f"{BIN}/cal{year}"
    d = tempfile.mkdtemp(prefix="catala_m_")
    os.makedirs(d + "/o")
    files, names = [], {}
    for k, c in enumerate(cases):
        n = f"c{k}"
        names[n] = c["id"]
        body = ["#NOM", n, "#ENTREES-PRIMITIF", "REGCO/1", f"ANREV/{year}"] + [f"{b}/{v}" for b, v in c["boxes"].items()]
        body += ["#CONTROLES-PRIMITIF", "#RESULTATS-PRIMITIF", "#ENTREES-CORRECTIF", "#CONTROLES-CORRECTIF",
                 "#RESULTATS-CORRECTIF", "##"]
        open(f"{d}/{n}.irj", "w").write("\n".join(body) + "\n")
        files.append(f"{d}/{n}.irj")
    out = {}
    for i in range(0, len(files), 2000):
        chunk = files[i:i + 2000]
        r = subprocess.run([cal, "-completion", "-m", "p", "-a", str(year), "-dst", d + "/o"] + chunk,
                           capture_output=True, text=True)
        ko = {}
        for block in r.stdout.split("traitement du fichier ")[1:]:
            m = re.search(r"ATRT000 \| KO \| (\S+)", block)
            if m:
                ko[block.split('"')[1].rsplit("/", 1)[-1][:-4]] = m.group(1)
        for f in chunk:
            n = f.rsplit("/", 1)[-1][:-4]
            p = f"{d}/o/{n}.irj"
            vals = {}
            if os.path.exists(p) and n not in ko:
                for l in open(p):
                    if "/" in l:
                        k, v = l.strip().split("/", 1)
                        if k in mvars and k not in vals:
                            try:
                                vals[k] = float(v)
                            except ValueError:
                                pass
            if not vals.get("NBPT"):
                vals = {"_refused": ko.get(n, "no parts")}
            out[names[n]] = vals
    subprocess.run(["rm", "-rf", d])
    return out


def mget(m, k):
    if m is None or "_refused" in m:
        return None
    return m.get(k, 0.0)


def load_irj(path):
    b, year, cid = {}, None, None
    lines = open(path).read().split("\n")
    cid = lines[1].strip()
    for l in lines:
        if l.startswith("#CONTROLES"):
            break
        if "/" in l and not l.startswith("#"):
            k, v = l.split("/", 1)
            if k == "ANREV":
                year = int(v)
            elif k != "REGCO":
                b[k] = int(float(v))
    return {"id": cid, "year": year, "boxes": b}
