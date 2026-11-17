"""Show one converted test: the YAML input, each box with the label M gives it that year, the expected values and
what OpenFisca, M and Lean give.   usage: ofsuite_show.py results.jsonl ID-substring [M variables...]"""
import glob, json, os, re, sys, subprocess, tempfile
import yaml

res = [json.loads(l) for l in open(sys.argv[1])]
extra = sys.argv[3:]


def labels(year):
    src = sorted(glob.glob(os.path.expanduser(f"~/fr/mlang/ir-calcul/sources{year}m_*")))[-1]
    lab = {}
    for f in glob.glob(src + "/tgv*.m"):
        for m in re.finditer(r"^(\w+)\s*:\s*saisie[^\n]*?\balias\s+(\w+)\s*:\s*\"([^\"]*)\"", open(f, encoding="latin-1").read(), re.M):
            lab[m.group(2)] = (m.group(1), m.group(3))
    return lab


for c in res:
    if sys.argv[2] not in c["id"]:
        continue
    print("==", c["id"], c["year"], c["tier"], c["verdict"])
    f, i = c["file"], int(c["id"].split("#")[1].split("/")[0])
    docs = yaml.safe_load(open(os.path.expanduser("~/fr/refs/openfisca-france/tests/" + f)))
    t = (docs if isinstance(docs, list) else [docs])[i]
    print("name:", t.get("name"))
    print("input:", json.dumps(t.get("input"), default=str)[:1500])
    lab = labels(c["year"])
    for k, v in c["boxes"].items():
        print(f"   {k:4s} {v:>8} {lab.get(k, ('?', '?'))[0]:10s} {lab.get(k, ('?', '?'))[1][:90]}")
    for n, fg in c["figures"].items():
        print("  ", n, {k: fg[k] for k in ("stated", "OpenFisca", "M", "Lean")})
    if extra:
        d = tempfile.mkdtemp()
        os.makedirs(d + "/o")
        body = ["#NOM", "x", "#ENTREES-PRIMITIF", "REGCO/1", f"ANREV/{c['year']}"] + [f"{k}/{v}" for k, v in c["boxes"].items()]
        body += ["#CONTROLES-PRIMITIF", "#RESULTATS-PRIMITIF", "#ENTREES-CORRECTIF", "#CONTROLES-CORRECTIF", "#RESULTATS-CORRECTIF", "##"]
        open(d + "/x.irj", "w").write("\n".join(body) + "\n")
        r = subprocess.run([os.path.expanduser(f"~/fr/bin/cal{c['year']}"), "-completion", "-m", "p", "-a", str(c["year"]),
                            "-dst", d + "/o", d + "/x.irj"], capture_output=True, text=True)
        vals = {}
        if os.path.exists(d + "/o/x.irj"):
            for line in open(d + "/o/x.irj"):
                if "/" in line:
                    k, v = line.strip().split("/", 1)
                    vals.setdefault(k, v)
        print("   M:", {k: vals.get(k) for k in extra} if extra != ["ALL"] else vals)
