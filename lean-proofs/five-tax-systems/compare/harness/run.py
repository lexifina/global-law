"""Run one scenario through every available country model and write the tidy results table.

    python3 run.py <scenario> [--countries US,FR,UK,DE,JP] [--slim]

Writes runs/<scenario>/<stamp>/: results.jsonl (one row per household x country: the contract's figures, net
income, gross in AW multiples and in PPP dollars, and the household's scenario fields), meta.json (exe hashes, sizes,
timings, countries skipped), and households_<C>.jsonl / outputs_<C>.jsonl unless --slim. runs/<scenario>/latest
points at the newest run.
"""
import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (COUNTRIES, ROOT, available, is_default, run_exe, run_with_elections, snapshot_exe,  # noqa: E402
                    tidy_row)
import scenarios  # noqa: E402

REGISTRY = {"oecd": scenarios.oecd_households, "curves": scenarios.curves, "scan": scenarios.scan}


def register(name, fn):
    REGISTRY[name] = fn


def run(name, countries=COUNTRIES, slim=False, gen=None, tag=None, elections=True):
    """`elections=False` runs each model on its defaults (the OECD check, which reproduces the OECD's assumptions:
    joint assessment, withholding), otherwise every household makes the cheapest election (common.ELECTIONS)."""
    gen = gen or REGISTRY[name]
    hs_by_c, meta = gen(countries)
    stamp = time.strftime("%Y%m%dT%H%M%S")
    run_dir = os.path.join(ROOT, "runs", name, stamp)
    os.makedirs(run_dir, exist_ok=True)
    info = {"scenario": name, "started": stamp, "tag": tag, "countries": {}}
    rows = []
    for c in countries:
        hs = hs_by_c.get(c, [])
        if not hs:
            continue
        if not available(c):
            info["countries"][c] = {"skipped": "exe not available"}
            continue
        cmd, cwd, h = snapshot_exe(c, run_dir)
        try:
            if elections:
                outs, dt, chosen = run_with_elections(c, cmd, cwd, hs)
            else:
                outs, dt = run_exe(cmd, cwd, hs)
                chosen = {}
        except Exception as e:  # keep the other countries
            info["countries"][c] = {"error": str(e)[:2000], "exe_sha256": h}
            continue
        info["countries"][c] = {"exe_sha256": h, "cmd": cmd, "n": len(hs), "seconds": round(dt, 3)}
        if chosen:
            info["countries"][c]["elections"] = {"households": len(chosen),
                                                 "not_default": sum(1 for v in chosen.values() if not is_default(c, v))}
        if not slim:
            with open(os.path.join(run_dir, f"households_{c}.jsonl"), "w") as f:
                for x in hs:
                    f.write(json.dumps(x) + "\n")
            with open(os.path.join(run_dir, f"outputs_{c}.jsonl"), "w") as f:
                for x in outs:
                    f.write(json.dumps(x, ensure_ascii=False) + "\n")
        for x, o in zip(hs, outs):
            r = tidy_row(c, x, o, meta.get(x["id"]))
            if slim:
                r.pop("detail", None)
                r.pop("unsupported", None)
            rows.append(r)
    with open(os.path.join(run_dir, "results.jsonl"), "w") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    info["finished"] = time.strftime("%Y%m%dT%H%M%S")
    info["rows"] = len(rows)
    json.dump(info, open(os.path.join(run_dir, "meta.json"), "w"), indent=1)
    latest = os.path.join(ROOT, "runs", name, "latest")
    if os.path.islink(latest) or os.path.exists(latest):
        os.remove(latest)
    os.symlink(stamp, latest)
    return run_dir, rows, info


def load(name):
    p = os.path.join(ROOT, "runs", name, "latest", "results.jsonl")
    return [json.loads(l) for l in open(p)]


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("scenario")
    ap.add_argument("--countries", default=",".join(COUNTRIES))
    ap.add_argument("--slim", action="store_true")
    a = ap.parse_args()
    d, rows, info = run(a.scenario, a.countries.split(","), slim=a.slim)
    print(d)
    print(json.dumps(info["countries"], indent=1))
