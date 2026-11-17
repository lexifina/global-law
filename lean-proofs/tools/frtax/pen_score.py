"""Penalty study: score stated figures (BOFiP examples, court decisions) against the Lean functions.
Usage: python3 -I harness/pen_score.py CASES.txt OUT.json
CASES lines: id|source|...|Lean line|stated KEY=VALUE;...[|note]  (the Lean line is the field starting with a
case code; the stated figures the field after it)."""
import json, os, re, subprocess, sys
rows = []
for l in open(sys.argv[1], encoding="utf-8"):
    if not l.strip() or l.startswith("#"): continue
    f = l.rstrip("\n").split("|")
    k = next(i for i, x in enumerate(f) if re.match(r"(IR|I|S|L|W|M|T|G|P|X);", x))
    rows.append({"id": f[0], "source": " | ".join(f[1:k]), "lean_line": f[k], "stated": dict(kv.split("=", 1) for kv in f[k + 1].split(";")),
                 "note": "|".join(f[k + 2:])})
env = dict(os.environ, PATH=os.path.expanduser("~/.elan/bin:") + os.environ["PATH"])
p = subprocess.run(["lake", "env", "lean", "--run", "../harness/pen_eval.lean"], cwd=os.path.expanduser("~/fr/lean"),
                   input="\n".join(r["lean_line"] for r in rows) + "\n", capture_output=True, text=True, env=env, timeout=600)
out = {}
for l in p.stdout.splitlines():
    q = l.split(";"); out[q[0]] = dict(x.split("=", 1) for x in q[1:] if "=" in x)
ok = 0
for r in rows:
    lid = r["lean_line"].split(";")[1]
    got = out.get(lid, {})
    r["lean"] = got
    r["match"] = all(got.get(k) == v for k, v in r["stated"].items())
    r["diff"] = {k: (int(got[k]) - int(v)) if k in got and re.fullmatch(r"-?\d+", v) and re.fullmatch(r"-?\d+", got[k]) else None
                 for k, v in r["stated"].items() if got.get(k) != v}
    ok += r["match"]
    print(f"{r['id']:5s} {'OK ' if r['match'] else 'DIFF'} stated {r['stated']} lean {{{', '.join(f'{k}={got.get(k)}' for k in r['stated'])}}} {r['diff'] or ''} | {r['source'][:90]}")
print(f"{ok}/{len(rows)} stated figures reproduced exactly")
json.dump(rows, open(sys.argv[2], "w"), indent=1, ensure_ascii=False)
