"""Assign each changed return of the 2018 6.3 -> 6.7 run to the code changes it shows (a return can show several)."""
import json, sys, re, collections
import gzip
rows = [json.loads(l) for l in (gzip.open if sys.argv[1].endswith(".gz") else open)(sys.argv[1])]
def ch(r, *vs): return any(v in r["diff"] for v in vs)
RCM = {"2AA", "2AL", "2AM", "2AN", "2AQ", "2AR", "2VN", "2VO", "2VP", "2YY", "2ZZ"}
rules = {
 "C1 rate: LF2020 scale for the Jan-2020 rate": lambda r: ch(r, "RASTXFOYER", "RASTXDEC1", "RASTXDEC2"),
 "C1b tax-without-CIMR from the rate pass (IITAZIR)": lambda r: ch(r, "IITAZIR", "IINETCIMR", "IRESTCIMR"),
 "C2 CIMR ratio: 8ZZ in the denominator": lambda r: "8ZZ" in r["boxes"] and ch(r, "CIMR", "IRE"),
 "C3 CIMR withheld under a penalty code": lambda r: ("9YT" in r["boxes"] or "9XT" in r["boxes"]) and ch(r, "CIMR", "IRE"),
 "C4 RCM deficits left to carry forward (DFRCM*)": lambda r: any(v.startswith("DFRCM") for v in r["diff"]),
 "C5a art. 1731 bis RCM base with life insurance (BRCMBISB)": lambda r: ch(r, "BRCMBISB", "REPRCMB"),
 "C5b RNI with RCM deficits/life insurance": lambda r: ch(r, "RNI") and RCM & set(r["boxes"]) and "9YA" not in r["boxes"],
 "C6 cancelled return (9YA): RNI nil": lambda r: "9YA" in r["boxes"] and ch(r, "RNI"),
 "C7 ZRA in IRNIN (interest/penalty base)": lambda r: "ZRA" in r["boxes"] and ch(r, "IRNIN"),
 "C8 RNG rounded to the euro": lambda r: ch(r, "RNG") and "." in r["diff"]["RNG"][0] and not r["diff"]["RNG"][0].endswith(".00"),
 "C9 penalty bases only": lambda r: any(re.search(r"(BASE_MAJO|^IRBASE)", v) for v in r["diff"]),
}
FINAL = {"IRN", "IINET", "IRNET", "NAPCR", "NAPTIR", "NAPTOT", "IREST", "IDRS", "IAN", "RNI", "RNG", "REVKIRE", "NBPT", "ITRED", "IRE", "CHRAPRES", "CSNET", "PSOLNET", "RDNET", "IDEC"}
out = {}
for k, f in rules.items():
    m = [r for r in rows if f(r)]
    rnd = sum("random" in r["tags"] for r in m)
    fin = sum(bool(FINAL & set(r["diff"])) for r in m)
    out[k] = {"returns": len(m), "random": rnd, "targeted": len(m) - rnd, "with_final_tax_change": fin}
    print(f"{k}: {len(m)} returns ({rnd} random, {len(m)-rnd} targeted); final tax/income figure changed on {fin}")
unexpl = [r for r in rows if FINAL & set(r["diff"]) and not any(f(r) for k, f in rules.items() if k[:2] in ("C2", "C3", "C4", "C5", "C6", "C8"))]
print("final-figure changes not in C2-C8:", len(unexpl))
for r in unexpl[:12]: print("  ", r["id"], r["tags"], json.dumps(r["boxes"])[:200], {v: r["diff"][v] for v in FINAL & set(r["diff"])})
json.dump(out, open(sys.argv[2], "w"), indent=1)
