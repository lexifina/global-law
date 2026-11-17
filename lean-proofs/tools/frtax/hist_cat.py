"""Count changed returns by output category (final tax figures, CIMR display, withholding rate/instalments,
penalty bases, other).  usage: hist_cat.py diffs.jsonl"""
import json, sys, re, collections
FINAL = {"IRN", "IINET", "IRNET", "NAPCR", "NAPCRP", "NAPTIR", "NAPTOT", "IREST", "IRESTIT", "IRESTITIR", "IDRS", "IDRS2", "IDRS3",
         "IDRS4", "IAN", "IAMD1", "IAMD2", "RNI", "RNG", "REVKIRE", "NBPT", "ITRED", "IRE", "CHRAPRES", "CSNET", "RDNET",
         "PSOLNET", "IAVIM", "IDEC", "IPROP", "TOTIRPS", "NAPT", "TOTCR", "IFI4BASE", "IFINET", "ILITOTIRNET", "IRNIN", "IINETIR"}
def cat(v):
    if v in FINAL: return "final"
    if re.match(r"^(IINETCIMR|IITAZIR|IRESTCIMR|INDIRN1|CIMR\w*)$", v): return "cimr"
    if re.match(r"^(RAS|PAS)", v): return "pas"
    if re.search(r"(BASE_MAJO|^IRBASE|INR|MAJO|TARDIF)", v): return "penalty_base"
    if re.match(r"^(LIG|ZIG|IND|NAT|FLAG)", v): return "display"
    return "other"
rows = [json.loads(l) for l in open(sys.argv[1])]
c = collections.Counter(); combo = collections.Counter(); fv = collections.Counter(); ov = collections.Counter()
for r in rows:
    cs = sorted({cat(v) for v in r["diff"]})
    for x in cs: c[x] += 1
    combo[tuple(cs)] += 1
    for v in r["diff"]:
        if cat(v) == "final": fv[v] += 1
        if cat(v) == "other": ov[v] += 1
print("returns changed:", len(rows)); print("by category:", dict(c)); print("combos:", combo.most_common(12))
print("final vars:", fv.most_common(30)); print("other vars:", ov.most_common(30))
