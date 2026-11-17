"""The DGFiP's production simulator as arbiter for the withholding rates: posts returns (calc-<year+1>.cgi), saves each
page, and reads the household rate ("taux foyer ... serait de : X%"), the individualised rates ("... seraient de :
X% pour le déclarant 1 et de Y% pour le déclarant 2") and the hidden fields of the rate-detail form (PASNUMF,
PASDENF, IRTOTAL, RASTXFOYER, ...). Strictly sequential, 1.2 s between requests; run it under flock ~/fr/.sim.lock.

usage: pas_sim.py cases.jsonl out.jsonl [ids_file]
       pas_sim.py --parse out.jsonl        # re-read the saved pages
"""
import html, json, os, re, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sim_run as S


def num(s):
    return float(s.replace(",", ".").replace("\xa0", "").replace(" ", ""))


def parse_pas(page):
    out = S.parse(page)
    t = html.unescape(re.sub(r"<[^>]+>", " ", page))
    t = re.sub(r"\s+", " ", t)
    m = re.search(r"taux foyer\)? apr[eè]s actualisation en septembre (\d{4}) serait de : ?([\d.,]+) ?%", t)
    if m:
        out["PASYEAR"] = int(m.group(1))
        out["TXFOYER"] = num(m.group(2))
    m = re.search(r"seraient de : ?([\d.,]+) ?% pour le d[ée]clarant 1 et de ?([\d.,]+) ?% pour le d[ée]clarant 2", t)
    if m:
        out["TXDEC1"], out["TXDEC2"] = num(m.group(1)), num(m.group(2))
    j = page.find("form name='tauxpas'")
    if j >= 0:
        for k, v in re.findall(r'name="([A-Z0-9_]+)" value="([^"]*)"', page[j:j + 30000]):
            try:
                out["h_" + k] = float(v)
            except ValueError:
                pass
    if "TXFOYER" not in out:
        # a couple shown individualised rates gets no household-rate sentence; the rate-detail form still holds it
        if "h_RASTXFOYER" in out:
            out["TXFOYER"] = out["h_RASTXFOYER"]
            out["TXFOYER_from"] = "hidden field RASTXFOYER"
        i = t.find("lèvement à la source")
        out["_pas_text"] = t[i - 100:i + 400] if i >= 0 else None
    return out


def main():
    if sys.argv[1] == "--parse":
        path = sys.argv[2]
        rows = [json.loads(l) for l in open(path)]
        with open(path, "w") as f:
            for r in rows:
                p = f"{path}.html/{r['id']}.html"
                if os.path.exists(p):
                    r["sim"] = parse_pas(open(p, encoding="latin-1").read())
                f.write(json.dumps(r) + "\n")
        return
    cases = [json.loads(l) for l in open(sys.argv[1])]
    out_path = sys.argv[2]
    if len(sys.argv) > 3:
        want = set(open(sys.argv[3]).read().split())
        cases = [c for c in cases if c["id"] in want]
    done = set()
    if os.path.exists(out_path):
        done = {json.loads(l)["id"] for l in open(out_path)}
    os.makedirs(out_path + ".html", exist_ok=True)
    with open(out_path, "a") as f:
        for c in cases:
            if c["id"] in done:
                continue
            try:
                page = S.post(c["year"], c["boxes"])
                open(f"{out_path}.html/{c['id']}.html", "w", encoding="latin-1", errors="replace").write(page)
                r = parse_pas(page)
            except Exception as e:
                r = {"_error": repr(e)[:200]}
            f.write(json.dumps({"id": c["id"], "year": c["year"], "sim": r}) + "\n")
            f.flush()
            time.sleep(1.2)
    print("PAS-SIM-DONE")


if __name__ == "__main__":
    main()
