#!/usr/bin/env python3
"""Query the BMF's external interface (bmf-steuerrechner.de, PAP 2025) for each case, politely.

bmf_interface.py cases.jsonl OUTDIR

The interface is published "für die automatisierte, maschinelle Prüfung eines Lohn- und Einkommensteuerrechners gegen
den des BMF" (interface description, shown after accepting its terms of use: program tests only, no commercial use);
the code parameter is the one that description publishes. robots.txt asks for Crawl-Delay: 60, so requests are
sequential and 61 s apart. Responses are saved as OUTDIR/<id>.xml; cases already saved are skipped (resumable).
"""
import json, os, sys, time, urllib.parse, urllib.request

URL = "https://www.bmf-steuerrechner.de/interface/2025Version1.xhtml"
CODE = "LSt2026ext"   # "Der Code ist gültig bis zum 15.01.2027" (interface description)
UA = "Mozilla/5.0 (compatible; tax-model-test; non-commercial research)"

def params(c):
    p = {"code": CODE}
    for k in ["LZZ", "RE4", "STKL", "KRV", "PKV", "PKPV", "PVS", "PVZ", "R", "ALTER1", "AJAHR", "LZZFREIB", "LZZHINZU"]:
        v = c.get(k, 0)
        if v:
            p[k] = str(int(v))
    if c.get("ZKF"):
        p["ZKF"] = f"{c['ZKF']:.1f}"
    p["KVZ"] = f"{c.get('KVZ', 0):.2f}"
    if c.get("PVA"):
        p["PVA"] = str(int(c["PVA"]))
    return p

def main():
    cases = [json.loads(l) for l in open(sys.argv[1]) if l.strip()]
    out = sys.argv[2]
    os.makedirs(out, exist_ok=True)
    for c in cases:
        path = os.path.join(out, c["id"] + ".xml")
        if os.path.exists(path) and os.path.getsize(path) > 0:
            continue
        url = URL + "?" + urllib.parse.urlencode(params(c))
        t0 = time.time()
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            body = urllib.request.urlopen(req, timeout=90).read()
            with open(path, "wb") as f:
                f.write(body)
            print(time.strftime("%H:%M:%S"), c["id"], len(body), flush=True)
        except Exception as e:
            print(time.strftime("%H:%M:%S"), c["id"], "ERROR", e, flush=True)
        time.sleep(max(0.0, 61 - (time.time() - t0)))
    print("DONE", flush=True)

if __name__ == "__main__":
    main()
