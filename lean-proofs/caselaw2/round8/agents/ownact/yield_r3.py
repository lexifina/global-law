"""Round 8 ownact: yield model from the answered round-3 own-act packs (0-141) by (level, tier, pattern).

Reads only reader answers and the round-3 certifier's own output (no answer key). Prints per stratum:
read, yes, certified (status-changing kinds), smoothed rate, unread count. Writes yield_r3.json.
"""
import collections
import glob
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
C2 = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
Q = os.path.join(C2, "work", "round3", "queue")
CHG = {"overruled", "disapproved", "recededFrom", "abrogated"}


def main():
    snap = {}
    for line in open(os.path.join(Q, "queue_snapshot.tsv"), encoding="utf-8"):
        f = line.rstrip("\n").split("\t")
        snap[f[0]] = f
    ans = {}
    for fn in glob.glob(os.path.join(Q, "packs", "ans_*.jsonl")):
        for line in open(fn, encoding="utf-8"):
            line = line.strip()
            if line:
                r = json.loads(line)
                ans[str(r["id"])] = r
    cert = {}
    rows = {}
    for line in open(os.path.join(Q, "cert", "treatments_new.tsv"), encoding="utf-8"):
        f = line.rstrip("\n").split("\t")
        rows[f[0]] = f[4]
    for line in open(os.path.join(Q, "cert", "treatments_items_new.tsv"), encoding="utf-8"):
        f = line.rstrip("\n").split("\t")
        cert[f[1]] = rows.get(f[0], "")
    tot, yes, cc, unread = (collections.Counter() for _ in range(4))
    for i, f in snap.items():
        k = (f[2], f[3], f[4])
        if i in ans:
            tot[k] += 1
            yes[k] += bool(ans[i].get("own_act"))
            cc[k] += cert.get(i) in CHG
        elif int(f[5]) >= 142:
            unread[k] += 1
    out = {}
    print("answers", len(ans), "cert items", len(cert))
    print("lvl tier pat | read yes certCHG rate | unread")
    for k in sorted(set(tot) | set(unread), key=lambda k: -unread[k]):
        rate = (cc[k] + 0.5) / (tot[k] + 4)
        out["|".join(k)] = {"read": tot[k], "yes": yes[k], "cert": cc[k], "rate": rate, "unread": unread[k]}
        print(k, tot[k], yes[k], cc[k], "%.3f" % rate, unread[k])
    print("unread total", sum(unread.values()))
    json.dump(out, open(os.path.join(HERE, "yield_r3.json"), "w", encoding="utf-8", newline="\n"), indent=1)


if __name__ == "__main__":
    main()
