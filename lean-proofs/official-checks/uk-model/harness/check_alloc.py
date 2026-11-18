"""Independent check of the s. 25(2) allocation: re-implement Step 4 from the statute (separately from the Lean code),
sample many feasible allocations of the Step 2/3 deductions, and verify none gives less Step 5 tax than Lean's choice.
usage: python3 -I check_alloc.py households.jsonl lean_out.jsonl [samples_per_person]"""
import json, random, sys
sys.path.insert(0, '/home/lean/cmp/uk/harness')
from pe_run import persons_of

SRL, DA = 500000, 50000           # pence
R = dict(b=2000, h=4000, a=4500, sb=2000, sh=4000, sa=4500, do=875, du=3375, da=3935)

def ov(a, b, lo, hi): return max(0, min(b, hi) - max(a, lo))

def tax(c1, c2, t, brl, hrl):
    # PSA (s. 12B, HMRC reading): by where the Step 3 income ends
    psa = 0 if t > hrl else (50000 if t > brl else 100000)
    T = R['b'] * ov(0, c1, 0, brl) + R['h'] * ov(0, c1, brl, hrl) + R['a'] * max(0, c1 - hrl)
    m = max(c1, SRL)                              # s. 12: [c1, min(c2, SRL)] at 0 %
    nil = min(max(0, c2 - m), psa)                # s. 12A: lowest £A above the SRL
    s0 = m + nil
    T += R['sb'] * ov(s0, c2, 0, brl) + R['sh'] * ov(s0, c2, brl, hrl) + R['sa'] * max(0, c2 - max(s0, hrl))
    d0 = c2 + min(max(0, t - c2), DA)             # s. 13A
    T += R['do'] * ov(d0, t, 0, brl) + R['du'] * ov(d0, t, brl, hrl) + R['da'] * max(0, t - max(d0, hrl))
    return T

def main():
    hs = [json.loads(l) for l in open(sys.argv[1])]
    lo = [json.loads(l) for l in open(sys.argv[2])]
    K = int(sys.argv[3]) if len(sys.argv) > 3 else 400
    rng = random.Random(7)
    checked = worse = better = 0
    for h, o in zip(hs, lo):
        for p, d in zip(persons_of(h), o["detail"]["persons"]):
            N = 100 * max(0, p["employment"] + p["trading"] + p["pension"] + p["property"])
            S = 100 * max(0, p["interest"]); D = 100 * max(0, p["dividends"])
            if S == 0 and D == 0: continue
            if d["marriageAllowanceReduction"]: continue      # objective includes the reduction
            ded = round(100 * d["deductedSteps2and3"]); brl = round(100 * d["basicRateLimit"]); hrl = round(100 * d["higherRateLimit"])
            t = N + S + D - min(ded, N + S + D)
            lean = round(100 * d["taxAtStep5"])                # pence
            dd = min(ded, N + S + D)
            best = None
            pts = []
            for _ in range(K):
                aN = rng.randint(max(0, dd - S - D), min(N, dd))
                rest = dd - aN
                aS = rng.randint(max(0, rest - D), min(S, rest))
                pts.append((N - aN, N - aN + S - aS))
            # also the corners
            for aN in (min(N, dd), max(0, dd - S - D)):
                rest = dd - aN
                for aS in (min(S, rest), max(0, rest - D)):
                    pts.append((N - aN, N - aN + S - aS))
            for c1, c2 in pts:
                v = tax(c1, c2, t, brl, hrl) // 10000
                best = v if best is None else min(best, v)
            checked += 1
            if best < lean - 1: worse += 1; print("SAMPLE BEATS LEAN", h["id"], lean, best)
            if best > lean + 1: better += 1
    print(f"persons checked {checked}; a sample beat Lean: {worse}; Lean strictly better than every sample: {better}")

main()
