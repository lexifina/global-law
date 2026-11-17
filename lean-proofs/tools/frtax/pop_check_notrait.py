"""Check that M's results do not depend on V_NOTRAIT 23 for returns M accepts anyway.
usage: pop_check_notrait.py cases.jsonl workdir_of_a_pop_run n
Runs the first n accepted returns again with V_NOTRAIT/23 and compares every M variable collected."""
import json, os, subprocess, sys
cases_path, work, n = sys.argv[1], sys.argv[2], int(sys.argv[3])
m = {json.loads(l)["id"]: json.loads(l) for l in open(f"{work}/m.jsonl")}
cases = [json.loads(l) for l in open(cases_path)]
sel = [dict(c, m_extra={"V_NOTRAIT": 23}) for c in cases if c["id"] in m and "_notrait23" not in m[c["id"]]][:n]
tmp = f"{work}/notrait_check"
os.makedirs(tmp, exist_ok=True)
with open(f"{tmp}/c.jsonl", "w") as f:
    f.writelines(json.dumps(c) + "\n" for c in sel)
subprocess.run([sys.executable, os.path.join(os.path.dirname(__file__), "pop_run.py"), f"{tmp}/c.jsonl", tmp, "12", "200"], check=True)
m2 = {json.loads(l)["id"]: json.loads(l) for l in open(f"{tmp}/m.jsonl")}
diff = [cid for cid in m2 if any(m2[cid].get(k) != v for k, v in m[cid].items() if k != "id")]
print(f"V_NOTRAIT 23 check: {len(m2)} returns rerun, {len(diff)} with any differing M variable", diff[:10])
