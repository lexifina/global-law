"""Audit population files for the lead's fresh blind audit (make_packs7.py --ids).

    python -X utf8 audit_spec.py      -> audit/ids_<subclass>.txt, audit/SPEC.md counts (stdout)

Population per sub-class = admitted row ids of the certify7 deltas, minus every (acting, target) pair drawn in a
round-6 blind audit (round6/history/audit/{v1,v2,r1,a3}/sample.tsv, real rows and decoys) and (the pairs this agent read during
development are listed apart in audit/read_by_agent_<subclass>.txt, not removed). Set-aside rows on base history rows are listed by their base id
(history_claim_delta.tsv)."""
import collections, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
C2 = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
AUD6 = os.path.join(C2, "round6", "history", "audit")
OUT = os.path.join(HERE, "audit")
os.makedirs(OUT, exist_ok=True)


def pair_of(i):
    p = i.split(":")
    return int(p[1]), int(p[2])


excl = set()
for run in ("v1", "v2", "r1", "a3"):
    hdr = None
    for line in open(os.path.join(AUD6, run, "sample.tsv"), encoding="utf-8"):
        p = line.rstrip("\n").split("\t")
        if hdr is None:
            hdr = p
            continue
        d = dict(zip(hdr, p))
        try:
            excl.add((int(d["by_node"]), int(d["target_node"])))
        except (KeyError, ValueError):
            pass
n6 = len(excl)
read = set()
if os.path.exists(os.path.join(HERE, "read_ids.txt")):
    for x in open(os.path.join(HERE, "read_ids.txt"), encoding="utf-8").read().split():
        read.add(pair_of(x))


def sub_of(src):
    s = src.split(":")
    if s[0] == "r7":
        s = s[1:]
    if s[0] == "r7setaside":
        return "setaside"
    v = s[2].split("-")
    v = v[0] + "-" + v[1]
    if s[1] == "docket":
        return "docket"
    return {"c-reh": "enbanc-silent", "c-order": "enbanc-order"}.get(v, "enbanc-act")


pops = collections.defaultdict(list)
readpop = collections.defaultdict(list)
cnt = collections.Counter()
for folder in ("cert_enbanc_act", "cert_enbanc_order", "cert_enbanc_silent", "cert_docket", "cert_setaside"):
    d = os.path.join(HERE, folder)
    rows = []
    for line in open(os.path.join(d, "history_delta.tsv"), encoding="utf-8"):
        p = line.rstrip("\n").split("\t")
        rows.append((p[0], p[12]))
    if os.path.exists(os.path.join(d, "history_claim_delta.tsv")):
        delta_ids = {r[0] for r in rows}
        for line in open(os.path.join(d, "history_claim_delta.tsv"), encoding="utf-8"):
            p = line.rstrip("\n").split("\t")
            if p[0] not in delta_ids:
                rows.append((p[0], p[2]))
    for rid, src in rows:
        sc = sub_of(src)
        cnt[sc + ":all"] += 1
        pr = pair_of(rid)
        if pr in excl:
            cnt[sc + ":excluded_round6_audit"] += 1
            continue
        if pr in read:
            cnt[sc + ":of_which_read_by_agent"] += 1
            readpop[sc].append(rid)
        pops[sc].append(rid)
for sc, ids in sorted(pops.items()):
    with open(os.path.join(OUT, "ids_%s.txt" % sc), "w", encoding="utf-8", newline="\n") as o:
        o.write("\n".join(ids) + "\n")
    cnt[sc + ":population"] = len(ids)
    with open(os.path.join(OUT, "read_by_agent_%s.txt" % sc), "w", encoding="utf-8", newline="\n") as o:
        o.write("\n".join(readpop[sc]) + "\n")
print("round-6 audited pairs excluded:", n6, "| pairs read by this agent:", len(read))
for k, v in sorted(cnt.items()):
    print(k, v)
