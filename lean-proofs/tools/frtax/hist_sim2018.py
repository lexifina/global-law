"""Ask the production simulator for income 2018 (calc-2019.cgi) about a few 6.3 -> 6.7 cases. Sequential, 1.2 s apart;
run under flock ~/fr/.sim.lock. Saves raw pages to runs/hist/sim2018/."""
import json, os, re, sys, time, html, urllib.parse, urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sim_run import form_fields
out = os.path.expanduser("~/fr/runs/hist/sim2018"); os.makedirs(out, exist_ok=True)
cases = {
 "plain": {"0AC": 1, "0DA": 1980, "1AJ": 30000},
 "p6_8ZZ": {"0AC": 1, "0DA": 1980, "1AJ": 30000, "8ZZ": 5000},
 "p1_rcmdef": {"0AC": 1, "0DA": 1980, "1AJ": 30000, "2TR": 1000, "2OP": 1, "2AN": 400, "2AQ": 800, "2AR": 500},
 "p5_9YT": {"0AC": 1, "0DA": 1980, "1AJ": 30000, "2TR": 2000, "9YT": 8},
}
res = {}
for k, b in cases.items():
    data = urllib.parse.urlencode(form_fields(b)).encode()
    try:
        req = urllib.request.Request("https://simulateur-ir-ifi.impots.gouv.fr/cgi-bin/calc-2019.cgi", data=data, headers={"User-Agent": "Mozilla/5.0"})
        page = urllib.request.urlopen(req, timeout=60).read().decode("latin-1")
        open(f"{out}/{k}.html", "w", encoding="latin-1").write(page)
        t = html.unescape(re.sub(r"<[^>]+>", "\n", page)); lines = [l.strip() for l in t.split("\n") if l.strip()]
        res[k] = lines
    except Exception as e:
        res[k] = ["ERR " + repr(e)[:200]]
    time.sleep(1.2)
json.dump(res, open(f"{out}/lines.json", "w"), ensure_ascii=False, indent=0)
for k, ls in res.items():
    print("==", k); print(" | ".join(ls[:0]) or "", "\n".join(l for l in ls if re.search(r"(mpôt|Revenu|CIMR|modernisation|PAYER|REMBOURS|taux|Erreur|impossible|déficit|Déficit)", l))[:1500])
