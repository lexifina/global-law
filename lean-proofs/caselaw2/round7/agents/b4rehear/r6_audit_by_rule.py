"""Round-6 blind-audit results of the rehear classes, by linker rule (src) and measure.
Reads only audit outputs (sample.tsv, verdicts_*.jsonl) of round6/history/audit/{r1,a3}; no answer key.
Writes r6_audit_items.tsv (one line per audited rehear row) and prints per-rule counts."""
import collections, glob, json, os, sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
AUD = os.path.normpath(os.path.join(HERE, "..", "..", "..", "round6", "history", "audit"))
sys.path.insert(0, AUD)
import score_audit as S  # noqa: E402

out = []
for run in ("r1", "a3"):
    smp = {}
    for line in open(os.path.join(AUD, run, "sample.tsv"), encoding="utf-8"):
        p = line.rstrip("\n").split("\t")
        if p[0] == "item":
            hdr = p
            continue
        smp[p[0]] = dict(zip(hdr, p))
    ver = {}
    for f in glob.glob(os.path.join(AUD, run, "verdicts_*.jsonl")):
        for line in open(f, encoding="utf-8"):
            line = line.strip()
            if line:
                v = json.loads(line)
                ver[v["item"]] = S.norm_verdict(v)[0]
    for it, k in smp.items():
        if not k["class"].startswith("rehear/") or k["role"] != "real" or it not in ver:
            continue
        j = S.judge(k, ver[it])
        v = ver[it]
        out.append([run, it, k["class"], k["src"], k["kind"], k["scope"], k["by_node"], k["target_node"],
                    k["kind_group"], int(j["link"]), int(j["link_effect"]), v["disposition"], v["whole"],
                    v["note"].replace("\t", " ")[:200]])
with open(os.path.join(HERE, "r6_audit_items.tsv"), "w", encoding="utf-8", newline="\n") as o:
    o.write("run\titem\tclass\tsrc\tkind\tscope\tby\ttarget\tgroup\tlink\tlink_effect\tdisp\twhole\tnote\n")
    for r in out:
        o.write("\t".join(map(str, r)) + "\n")
agg = collections.defaultdict(lambda: [0, 0, 0])
for r in out:
    if r[8] != "status":
        continue
    for key in ((r[0], r[3]), (r[0], r[2])):
        a = agg[key]
        a[0] += 1
        a[1] += r[9]
        a[2] += r[10]
for k in sorted(agg):
    a = agg[k]
    print("%s %-28s n=%3d link=%3d effect=%3d (%.2f)" % (k[0], k[1], a[0], a[1], a[2], a[2] / a[0]))
