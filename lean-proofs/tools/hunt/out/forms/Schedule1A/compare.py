"""Schedule 1-A (2025): statute vs form, written separately from each text, compared over a grid."""
import itertools, math, json, collections

JOINT = "mfj"


# ---------------- statute: sections 224, 225, 163(h)(4), 151(d)(5)(C) ----------------
def statute(c):
    # MAGI (224(b)(2)(B), 225(b)(2)(B), 163(h)(4)(C)(ii)(II), 151(d)(5)(C)(iii)(II)):
    # AGI "increased by any amount excluded from gross income under section 911, 931, or 933".
    # 911(a) excludes foreign earned income and the housing cost amount (the gross amounts). The 911(c)(4)
    # housing amount is "a deduction allowable in computing adjusted gross income", not an exclusion: not added.
    magi = c["agi"] + c["excl911"] + c["excl931"] + c["excl933"]
    joint = c["status"] == JOINT
    married_sep = c["status"] == "mfs"  # married within 7703, no joint return
    r = {}
    # 224
    if married_sep or not c["ssn"]:
        r["tips"] = 0
    else:
        t = 0
        # 224(a): on a 6041(d)(3)/6041A(e)(3)/6050W(f)(2)/6051(a)(18) statement or Form 4137;
        # 224(d)(2)(B): not received in a specified service trade or business
        if c["tip_stmt"] and not c["sstb"]:
            t += c["tips_emp"]
            # 224(c): only to the extent gross income of the business exceeds its deductions
            t += min(c["tips_se"], max(0, c["se_net"]))
        t = min(t, 25000)  # 224(b)(1): one cap, joint or not
        over = magi - (300000 if joint else 150000)
        if over > 0:
            t = max(0, t - 100 * (over // 1000))  # "$100 for each $1,000": whole thousands only
        r["tips"] = t
    # 225
    if married_sep or not c["ssn"]:
        r["ot"] = 0
    else:
        o = c["ot"] if c["ot_stmt"] else 0  # 225(a): "included on statements furnished ... 6041(d)(4) or 6051(a)(19)"
        o = min(o, 25000 if joint else 12500)
        over = magi - (300000 if joint else 150000)
        if over > 0:
            o = max(0, o - 100 * (over // 1000))
        r["ot"] = o
    # 163(h)(4): no joint-return rule; 873(a) bars a nonresident's deduction not connected with ECI;
    # (B)(i): indebtedness "incurred by the taxpayer"
    if c["nra"] or c["loan_inherited"]:
        r["car"] = 0
    else:
        i = min(c["car_int"], 10000)
        over = magi - (200000 if joint else 100000)
        if over > 0:
            i = max(0, i - 200 * math.ceil(over / 1000))  # "for each $1,000 (or portion thereof)"
        r["car"] = i
    # 151(d)(5)(C)
    if married_sep:
        r["senior"] = 0
    else:
        per = max(0, 6000 - 0.06 * max(0, magi - (150000 if joint else 75000)))
        k = (1 if c["age_self"] >= 65 and c["ssn"] else 0) + (1 if joint and c["age_sp"] >= 65 and c["ssn_sp"] else 0)
        r["senior"] = per * k
    r["magi"] = magi
    return r


# ---------------- form: Schedule 1-A (2025) lines 1-38 and its instructions ----------------
def form(c):
    l1 = c["agi"]
    l2a = c["excl933"]
    l2b = c["excl911"] - c["f2555_l44"]  # Form 2555 line 45 = line 43 - line 44
    l2c = c["housing_ded"]  # Form 2555 line 50
    l2d = c["excl931"]  # Form 4563 line 15
    l3 = l1 + l2a + l2b + l2c + l2d
    mfj = c["status"] == JOINT
    mfs = c["status"] == "mfs"
    r = {}
    # Part II (caution: married must file jointly; valid SSN)
    if mfs or not c["ssn"]:
        r["tips"] = 0
    else:
        l4c = c["tips_emp"]  # box 7 / Form 4070 / Form 4137 col (c); 2025: own records accepted
        l5 = min(c["tips_se"], max(0, c["se_net"]))  # net profit less other allocable deductions, per business
        # instructions (Notice 2025-69): a listed occupation is treated as not an SSTB
        l7 = min(l4c + l5, 25000)
        l10 = l3 - (300000 if mfj else 150000)
        if l10 <= 0:
            r["tips"] = l7
        else:
            l11 = math.floor(l10 / 1000)
            r["tips"] = max(0, l7 - l11 * 100)
    # Part III
    if mfs or not c["ssn"]:
        r["ot"] = 0
    else:
        l15 = min(c["ot"], 25000 if mfj else 12500)  # 14a/14b: own reasonable computation accepted for 2025
        l18 = l3 - (300000 if mfj else 150000)
        r["ot"] = l15 if l18 <= 0 else max(0, l15 - math.floor(l18 / 1000) * 100)
    # Part IV (1040-NR instructions: nonresidents generally not eligible; inherited loan counts)
    if c["nra"]:
        r["car"] = 0
    else:
        l24 = min(c["car_int"], 10000)
        l27 = l3 - (200000 if mfj else 100000)
        r["car"] = l24 if l27 <= 0 else max(0, l24 - math.ceil(l27 / 1000) * 200)
    # Part V
    if mfs:
        r["senior"] = 0
    else:
        l33 = l3 - (150000 if mfj else 75000)
        l35 = 6000 if l33 <= 0 else max(0, 6000 - 0.06 * l33)
        a = l35 if (c["ssn"] and c["age_self"] >= 65) else 0
        b = l35 if (mfj and c["ssn_sp"] and c["age_sp"] >= 65) else 0
        r["senior"] = a + b
    r["magi"] = l3
    return r


BASE = dict(status="single", agi=60000, excl911=0, f2555_l44=0, housing_ded=0, excl931=0, excl933=0,
            tips_emp=0, tips_se=0, se_net=0, sstb=False, tip_stmt=True, ot=0, ot_stmt=True,
            car_int=0, loan_inherited=False, nra=False, ssn=True, ssn_sp=True, age_self=40, age_sp=40)
PARTS = ["tips", "ot", "car", "senior"]
n = 0
diffs = collections.defaultdict(list)


def run(tag, **axes):
    global n
    keys = list(axes)
    for vals in itertools.product(*[axes[k] for k in keys]):
        c = dict(BASE)
        c.update(dict(zip(keys, vals)))
        if c["status"] != JOINT and (c["age_sp"] != 40 or not c["ssn_sp"]):
            continue
        if c["f2555_l44"] > c["excl911"]:
            continue
        n += 1
        s, f = statute(c), form(c)
        for p in PARTS:
            if abs(s[p] - f[p]) > 1e-9:
                diffs[(tag, p)].append((f[p] - s[p], {k: c[k] for k in keys}, s[p], f[p], s["magi"], f["magi"]))


ST = ["single", "hoh", "qss", "mfj", "mfs"]
EDGES = (75000, 100000, 150000, 175000, 200000, 250000, 300000, 400000, 550000)
AGI = sorted(set(list(range(0, 460001, 12500)) + [x + d for x in EDGES for d in (-1, 0, 1, 499, 500, 999, 1000, 1001)]))
# A. core arithmetic: caps, thresholds, rounding, joint/separate, ages, SSN
run("A core", status=ST, agi=AGI, tips_emp=[0, 8000, 25000, 40000], ot=[0, 5000, 12500, 30000],
    car_int=[0, 3000, 10000, 14000], age_self=[64, 65], age_sp=[40, 65], ssn=[True, False])
# B. self-employed tips against net income
run("B 224(c)", status=["single", "mfj"], agi=[40000, 160000, 320000], tips_emp=[0, 6000],
    tips_se=[0, 1800, 20000, 30000], se_net=[-5000, 0, 1000, 15000, 60000])
# C. section 911 / 931 / 933 amounts in MAGI
run("C MAGI", status=["single", "hoh", "mfj"], agi=[20000, 49000, 90000, 140000, 190000, 290000],
    excl911=[0, 70000, 130000], f2555_l44=[0, 10000, 39000], housing_ded=[0, 5000, 18200, 50000],
    excl933=[0, 30000], tips_emp=[0, 20000], ot=[0, 10000], car_int=[0, 8000], age_self=[40, 66], age_sp=[40, 66])
# D. 2025 reporting relief, SSTB relief, inherited loan, nonresident
run("D relief", status=ST, agi=[50000, 120000, 180000, 320000], tips_emp=[0, 20000], tips_se=[0, 9000], se_net=[20000],
    sstb=[False, True], tip_stmt=[True, False], ot=[0, 9000], ot_stmt=[True, False], car_int=[0, 6000],
    loan_inherited=[False, True], nra=[False, True], age_self=[40, 70])

out = {"grid_points": n, "groups": []}
print("grid points:", n)
for (tag, p), lst in sorted(diffs.items()):
    up = [d for d in lst if d[0] > 0]
    dn = [d for d in lst if d[0] < 0]
    print(f"\n== {tag} / {p}: {len(lst)} differing points; form gives more at {len(up)}, statute gives more at {len(dn)}")
    for name, sub, key in (("form more", up, max), ("statute more", dn, min)):
        if sub:
            d = key(sub, key=lambda x: x[0])
            print(f"   largest {name}: {d[0]:+,.0f}  statute={d[2]:,.0f} form={d[3]:,.0f} "
                  f"MAGI statute={d[4]:,} form={d[5]:,}  {d[1]}")
    out["groups"].append({"block": tag, "part": p, "points": len(lst), "form_more": len(up), "statute_more": len(dn),
                          "max_form_more": max([d[0] for d in up], default=0),
                          "max_statute_more": -min([d[0] for d in dn], default=0)})
for blk in ("A core", "B 224(c)"):
    if not any(k[0] == blk for k in diffs):
        print(f"\n{blk}: no differences")
json.dump(out, open("grid_summary.json", "w"), indent=1)
