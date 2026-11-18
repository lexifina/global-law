"""Referee A: an independent calculator for Japanese 2025 (令和7年分) taxes, written from the NTA's year-end-adjustment
procedure and printed tables, not from the statute text the Lean model copies.

Sources (copies under ~/cmp/jp/refs):
  [NC] 国税庁「令和７年分 年末調整のしかた」: the printed 給与所得控除後の給与等の金額の表 (pp.47-54, parsed from the PDF
       text, not from e-Gov), 所得金額調整控除 (p.37), 速算表 (p.55), 配偶者控除額及び配偶者特別控除額の一覧表 (p.55),
       基礎控除額の表 / 特定親族特別控除額の表 / 扶養控除額等の表 (p.56), 年調年税額 = 年調所得税額 x 102.1% (p.39).
  [TA] タックスアンサー No.2260 (rows above 18,050,000 yen: 40 % / 45 %), No.1600 (公的年金 速算表), No.1150 (寄附金控除),
       No.1411.
  [KK] 協会けんぽ 保険料額表 xlsx (令和6年度, 令和7年度; 東京): grade rows and the printed 折半額, rounded per note ①.
  [MH] 厚生労働省 雇用保険料率 (令和6年度 6/1000, 令和7年度 5.5/1000).
  [CF] こども家庭庁 児童手当 page: 3歳未満 15,000円, 3歳以上高校生年代まで 10,000円, 第3子以降 30,000円.
  [JU] 住民税: written from the 総務省 explanation and the amounts of 地方税法 (independent code).

usage: python3 nta_referee.py households.jsonl > out.jsonl
"""
import sys, json, re, os, zipfile
from fractions import Fraction as F
import xml.etree.ElementTree as ET

REFS = os.path.expanduser("~/cmp/jp/refs")


# ---------------------------------------------------------------------------------------------------------------- [NC]
def load_nta_table():
    """Parse the printed 4,000-yen table of the booklet: lines of 'lo hi value' triples."""
    txt = open(os.path.join(REFS, "nta/nencho2025_all.txt"), encoding="utf-8").read()
    rows = {}
    for line in txt.splitlines():
        nums = [int(x.replace(",", "")) for x in re.findall(r"\d{1,3}(?:,\d{3})+", line)]
        for i in range(0, len(nums) - 2):
            a, b, c = nums[i], nums[i + 1], nums[i + 2]
            if b - a == 4000 and 1900000 <= a < 6600000 and a % 4000 == 0 and 0 < c < a:
                rows[a] = c
    return rows


NTA_TABLE = load_nta_table()
assert len(NTA_TABLE) == 1175, len(NTA_TABLE)


def kyuyo_after(w):
    """給与所得控除後の給与等の金額 [NC] pp.36, 47-54; above 20,000,000 yen [TA] No.1410 (令和7年分: 1,950,000円)."""
    if w < 651000:
        return 0
    if w < 1900000:
        return w - 650000
    if w < 6600000:
        return NTA_TABLE[w - (w - 1900000) % 4000]
    if w < 8500000:
        return int(F(w) * F(9, 10) - 1100000)            # "１円未満の端数があるときは、これを切り捨て"
    return w - 1950000


def chosei_kojo(w, has_child_u23):
    """[NC] p.37: (給与の総額(1,000万円上限) - 850万円) x 10%, 1円未満切り上げ."""
    if not has_child_u23 or w <= 8500000:
        return 0
    x = F(min(w, 10000000) - 8500000) / 10
    return -((-x.numerator) // x.denominator)


def nenkin_zatsu(p, other, over65):
    """[TA] No.1600 速算表 (令和2年分以後) for 公的年金等に係る雑所得以外の合計所得金額 <= 1,000万円 (other brackets
    by the same table's shifted rows)."""
    if p <= 0:
        return 0
    shift = 0 if other <= 10000000 else (100000 if other <= 20000000 else 200000)
    if over65:
        rows = [(3299999, F(1), -1100000), (4099999, F(3, 4), -275000), (7699999, F(85, 100), -685000),
                (9999999, F(95, 100), -1455000), (10 ** 12, F(1), -1955000)]
    else:
        rows = [(1299999, F(1), -600000), (4099999, F(3, 4), -275000), (7699999, F(85, 100), -685000),
                (9999999, F(95, 100), -1455000), (10 ** 12, F(1), -1955000)]
    if over65 and p <= 3299999:
        v = p - 1100000 + shift
    elif not over65 and p <= 1299999:
        v = p - 600000 + shift
    else:
        for hi, r, c in rows:
            if p <= hi:
                v = int(F(p) * r + c + shift)
                break
    return max(0, v)


def kiso(g):
    """[NC] p.56 基礎控除額の表."""
    for hi, d in [(1320000, 950000), (3360000, 880000), (4890000, 680000), (6550000, 630000),
                  (23500000, 580000), (24000000, 480000), (24500000, 320000), (25000000, 160000)]:
        if g <= hi:
            return d
    return 0


# [NC] p.55 一覧表: rows by the spouse's 合計所得金額 (upper bound), columns by the claimant (<=900万, <=950万, <=1000万)
SPOUSE_ROWS = [(580000, (380000, 260000, 130000)), (950000, (380000, 260000, 130000)),
               (1000000, (360000, 240000, 120000)), (1050000, (310000, 210000, 110000)),
               (1100000, (260000, 180000, 90000)), (1150000, (210000, 140000, 70000)),
               (1200000, (160000, 110000, 60000)), (1250000, (110000, 80000, 40000)),
               (1300000, (60000, 40000, 20000)), (1330000, (30000, 20000, 10000))]
SPOUSE_OLD = (480000, 320000, 160000)   # 老人控除対象配偶者 (p.55 一覧表, 配偶者控除 row)


def spouse_deduction(g, s, spouse_old):
    if g > 10000000:
        return 0
    col = 0 if g <= 9000000 else (1 if g <= 9500000 else 2)
    if s <= 580000 and spouse_old:
        return SPOUSE_OLD[col]
    for hi, vals in SPOUSE_ROWS:
        if s <= hi:
            return vals[col]
    return 0


TOKUTEI_ROWS = [(850000, 630000), (900000, 610000), (950000, 510000), (1000000, 410000), (1050000, 310000),
                (1100000, 210000), (1150000, 110000), (1200000, 60000), (1230000, 30000)]   # [NC] p.56


def dependant_deduction(age, inc):
    """[NC] p.56 扶養控除額等の表 and 特定親族特別控除額の表; ages on 31 December."""
    if inc <= 580000:
        if age < 16:
            return 0
        if 19 <= age < 23:
            return 630000
        if age >= 70:
            return 480000
        return 380000
    if 19 <= age < 23 and inc <= 1230000:
        for hi, d in TOKUTEI_ROWS:
            if inc <= hi:
                return d
    return 0


def sokusan(t):
    """[NC] p.55 速算表, and [TA] No.2260 for the 40 % and 45 % rows."""
    for hi, r, c in [(1950000, 5, 0), (3300000, 10, 97500), (6950000, 20, 427500), (9000000, 23, 636000),
                     (18000000, 33, 1536000), (40000000, 40, 2796000), (10 ** 15, 45, 4796000)]:
        if t <= hi:
            return max(0, t * r // 100 - c)


# ---------------------------------------------------------------------------------------------------------------- [KK]
def load_kyoukai(fname):
    z = zipfile.ZipFile(os.path.join(REFS, "kyoukai", fname))
    ns = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    ss = ["".join(t.itertext()) for t in ET.fromstring(z.read("xl/sharedStrings.xml")).findall("m:si", ns)]
    wb = ET.fromstring(z.read("xl/workbook.xml"))
    rels = ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
    rmap = {r.get("Id"): r.get("Target") for r in rels}
    target = None
    for s in wb.find("m:sheets", ns):
        if s.get("name") == "東京":
            target = rmap[s.get("{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id")]
    sh = ET.fromstring(z.read("xl/" + target.lstrip("/").replace("xl/", "")))
    grid = {}
    for c in sh.iter("{%s}c" % ns["m"]):
        v = c.find("m:v", ns)
        if v is None:
            continue
        val = ss[int(v.text)] if c.get("t") == "s" else v.text
        grid[c.get("r")] = val
    rows = []
    for r in range(12, 62):
        std = grid.get("B%d" % r)
        if std is None:
            continue
        lo = grid.get("C%d" % r)
        hi = grid.get("E%d" % r)
        rows.append(dict(std=int(float(std)), lo=int(float(lo)) if lo else 0, hi=int(float(hi)) if hi else 10 ** 12,
                         half_nokaigo=F(grid["G%d" % r]).limit_denominator(100),
                         half_kaigo=F(grid["I%d" % r]).limit_denominator(100),
                         half_nenkin=(F(grid["K%d" % r]).limit_denominator(100) if ("K%d" % r) in grid else None)))
    return rows


KK6 = load_kyoukai("r6ippan3.xlsx")
KK7 = load_kyoukai("r7ippan3.xlsx")


def withhold_round(x):
    """[KK] note ①: 50銭以下切り捨て、50銭を超える場合は切り上げ."""
    i = x.numerator // x.denominator
    return i + (1 if x - i > F(1, 2) else 0)


def kk_row(rows, m):
    for r in rows:
        if r["lo"] <= m < r["hi"]:
            return r
    return rows[-1]


def nenkin_row(rows, m):
    """厚生年金 grades: rows 4(1) .. 35(32); 4(1) reads "93,000円未満", 35(32) "635,000円以上" ([KK] notes)."""
    nk = [r for r in rows if r["half_nenkin"] is not None]
    if m < 93000:
        return nk[0]
    if m >= 635000:
        return nk[-1]
    return kk_row(nk, m)


def social(w, age):
    if w < 12 * 88000:
        return dict(health=0, pension=0, koyo=0)
    m = F(w, 12)
    health = pension = koyo = 0
    for month in range(1, 13):
        rows = KK6 if month <= 2 else KK7
        r = kk_row(rows, m)
        if age < 75:
            health += withhold_round(r["half_kaigo"] if 40 <= age <= 64 else r["half_nokaigo"])
        if age < 70:
            pension += withhold_round(nenkin_row(rows, m)["half_nenkin"])
        pay = w // 12 if month < 12 else w - 11 * (w // 12)
        rate = F(6, 1000) if month <= 3 else F(55, 10000)                      # [MH]
        koyo += withhold_round(pay * rate)
    return dict(health=health, pension=pension, koyo=koyo)


# ---------------------------------------------------------------------------------------------------------------- [CF]
def jido_teate_month(ages):
    """[CF]: count children from the oldest (up to age 22 for the order); 3rd and later 30,000; else 15,000 / 10,000."""
    counted = sorted([a for a in ages if 0 <= a <= 22], reverse=True)
    total = 0
    for rank, a in enumerate(counted, start=1):
        if a > 18:
            continue
        total += 30000 if rank >= 3 else (15000 if a < 3 else 10000)
    return total


# ---------------------------------------------------------------------------------------------------------------- [JU]
def jumin(sogo, social_ins, ideco, spouse, deps, single_parent, mother, n_hijo, div=0, ddiv=0, dgain=0):
    """住民税 (令和8年度) for one person in Tokyo's wards: deductions, 10 % (4 + 6), 調整控除, 非課税, 均等割 + 森林環境税.
    ddiv / dgain: listed-share dividends / gains declared separately (地方税法附則第33条の2, 第35条の2の2): counted in the
    合計所得金額 and 総所得金額等, absorbing deductions left after the 総所得金額, taxed 2 % + 3 %."""
    g = sogo + max(0, ddiv) + max(0, dgain)
    if single_parent and g <= 1350000:
        return dict(pref=0, muni=0, kinto=0)
    ded = social_ins + ideco
    ded += 430000 if g <= 24000000 else (290000 if g <= 24500000 else (150000 if g <= 25000000 else 0))
    jinteki = 50000 if g <= 25000000 else 0          # 人的控除額の差: 基礎控除 5万
    if single_parent and g <= 5000000:
        ded += 300000
        jinteki += 50000 if mother else 10000
    if spouse is not None and g <= 10000000:
        s_age, s = spouse
        col = 0 if g <= 9000000 else (1 if g <= 9500000 else 2)
        if s <= 580000:
            ded += (380000, 260000, 130000)[col] if s_age >= 70 else (330000, 220000, 110000)[col]
            jinteki += (100000, 60000, 30000)[col] if s_age >= 70 else (50000, 40000, 20000)[col]
        elif s <= 1330000:
            base = 330000 if s <= 1000000 else (380000 - (50000 * ((s - 900001) // 50000) - 30000) if s <= 1300000 else 30000)
            if col == 1:
                base = -((-2 * base) // 30000) * 10000
            elif col == 2:
                base = -((-base) // 30000) * 10000
            ded += base
    for (age, inc) in deps:
        if inc <= 580000 and age >= 16:
            if 19 <= age < 23:
                ded += 450000; jinteki += 180000
            elif age >= 70:
                ded += 380000; jinteki += 100000
            else:
                ded += 330000; jinteki += 50000
        elif 19 <= age < 23 and 580000 < inc <= 1230000:
            if inc <= 950000:
                ded += 450000
            else:
                ded += dependant_deduction(age, inc)
    taxable = max(0, sogo - ded) // 1000 * 1000
    rest = max(0, ded - sogo)                                   # deductions left for the separate incomes
    t_gain = max(0, max(0, dgain) - rest) // 1000 * 1000
    rest = max(0, rest - max(0, dgain))
    t_div = max(0, max(0, ddiv) - rest) // 1000 * 1000
    pref = taxable * 4 // 100 + (t_gain + t_div) * 2 // 100
    muni = taxable * 6 // 100 + (t_gain + t_div) * 3 // 100
    if g <= 25000000:
        base = min(jinteki, taxable) if taxable <= 2000000 else max(50000, jinteki - (taxable - 2000000))
        pref -= min(pref, base * 2 // 100)
        muni -= min(muni, base * 3 // 100)
    pref, muni = F(pref), F(muni)
    if div > 0:          # 住民税 配当控除 (地方税法附則第5条): 1.2 % + 1.6 %, half on the part above 10 M of taxable income
        over = min(div, taxable + t_div - 10000000) if taxable + t_div > 10000000 else 0
        pref = pref - min(pref, F(12 * (div - over) + 6 * over, 1000))
        muni = muni - min(muni, F(16 * (div - over) + 8 * over, 1000))
    lim = 350000 * (n_hijo + 1) + 100000 + (320000 if n_hijo else 0)
    if g <= lim:
        pref = muni = F(0)
    elif pref + muni > 0 and lim > g - (pref + muni):
        ex = lim - (g - (pref + muni))
        tot = pref + muni
        pref, muni = pref - ex * pref / tot, muni - ex * muni / tot
    pref = int(pref) // 100 * 100
    muni = int(muni) // 100 * 100
    kinto_lim = 350000 * (n_hijo + 1) + 100000 + (210000 if n_hijo else 0)
    kinto = 0 if g <= kinto_lim else 5000
    return dict(pref=pref, muni=muni, kinto=kinto)


# ---------------------------------------------------------------------------------------------------------------- household
def split(x, n):
    """Household totals split equally between the adults, the remainder to the first."""
    q = x // n
    return [x - q * (n - 1)] + [q] * (n - 1)


def sep15(x):
    """措置法第3条 / 第8条の5 / 第37条の11 with 復興 0.315 %: 15.315 % withheld (cut to the yen), of which 15 % is 所得税;
    and the 5 % 利子割 / 配当割 / 株式等譲渡所得割."""
    x = max(0, x)
    tot = x * 15315 // 100000
    it = x * 15 // 100
    return it, tot - it, x * 5 // 100


def compute(h):
    adults = h["adults"]
    n = len(adults)
    married = bool(h.get("married")) and n == 2
    kids = [(c.get("age", 0), kyuyo_after(c.get("wages", 0))) for c in h.get("children", [])]
    u23 = any(a < 23 and inc <= 580000 for a, inc in kids)
    soc = [social(a.get("wages", 0), a.get("age", 40)) for a in adults]
    soc_tot = [s["health"] + s["pension"] + s["koyo"] for s in soc]
    agg = h.get("jpDividends") == "aggregate"
    dec = h.get("jpDividends") == "declared"                     # 申告分離課税 (措置法第8条の4)
    decg = h.get("jpGains") == "declared"                        # 措置法第37条の11, declared
    zero = [0] * n
    rent = split(h.get("rentalIncome", 0), n)
    divs = split(h.get("dividends", 0), n) if agg else zero
    sdiv = zero if (agg or dec) else split(h.get("dividends", 0), n)
    ddiv = split(h.get("dividends", 0), n) if dec else zero
    sint = split(h.get("interest", 0), n)
    sgain = zero if decg else split(h.get("capitalGains", 0), n)
    dgain = split(h.get("capitalGains", 0), n) if decg else zero
    per = []
    for i, a in enumerate(adults):
        w = a.get("wages", 0)
        se = a.get("selfEmployment", 0)
        k = kyuyo_after(w) - chosei_kojo(w, u23)
        other = max(0, max(0, k) + se + rent[i] + divs[i]) + max(0, ddiv[i]) + max(0, dgain[i])
        z = nenkin_zatsu(a.get("pension", 0), other, a.get("age", 40) >= 65)
        if k > 0 and z > 0:
            k -= max(0, min(k, 100000) + min(z, 100000) - 100000)
        per.append(max(0, max(0, k) + z + se + rent[i] + divs[i]))
    # 合計所得金額: the declared listed-share income counts (措置法第8条の4第3項第1号)
    gok = [per[i] + max(0, ddiv[i]) + max(0, dgain[i]) for i in range(n)]
    top = max(range(n), key=lambda i: (gok[i], -i))
    single_parent = n == 1 and not h.get("married") and any(inc <= 580000 for _, inc in kids)
    mother = h.get("jpSingleParentSex", "F") != "M"
    # iDeCo (確定拠出年金法施行令第36条): 23,000 a month for an insured employee or a 第3号 spouse, 68,000 otherwise,
    # none from 65; the household total to the first adult first
    left = max(0, h.get("pensionContributions", 0))
    ideco = []
    for i, a in enumerate(adults):
        o = adults[1 - i] if n == 2 else {}
        ins = a.get("wages", 0) >= 12 * 88000
        dep = (bool(h.get("married")) and n == 2 and o.get("wages", 0) >= 12 * 88000
               and a.get("wages", 0) + a.get("selfEmployment", 0) + a.get("pension", 0) < 1300000)
        cap = 0 if a.get("age", 40) >= 65 else (276000 if ins or dep else 816000)
        take = min(cap, left)
        ideco.append(take)
        left -= take
    out = []
    for i, a in enumerate(adults):
        s = per[i]                                              # 総所得金額
        g = gok[i]                                              # 合計所得金額
        ded = soc_tot[i] + ideco[i] + kiso(g)
        if i == top and h.get("charitable", 0) > 0:           # [TA] No.1150: (寄附金 - 2,000), within 40 % of 総所得金額等
            ded += max(0, min(h["charitable"], g * 4 // 10) - 2000)
        spouse = None
        if married and i == top:
            j = 1 - i
            spouse = (adults[j].get("age", 40), gok[j])
            ded += spouse_deduction(g, gok[j], spouse[0] >= 70)
        deps = kids if i == top else []
        for age, inc in deps:
            ded += dependant_deduction(age, inc)
        if single_parent and g <= 5000000:
            ded += 350000
        t = max(0, s - ded) // 1000 * 1000
        rest = max(0, ded - s)                                  # deductions left: gains first, then dividends
        t_gain = max(0, max(0, dgain[i]) - rest) // 1000 * 1000
        rest = max(0, rest - max(0, dgain[i]))
        t_div = max(0, max(0, ddiv[i]) - rest) // 1000 * 1000
        tax = sokusan(t)
        if divs[i] > 0:                                         # [TA] No.1250 配当控除 (剰余金の配当等)
            tt = t + t_div
            low = min(divs[i], tt - 10000000) if tt > 10000000 else 0
            credit = F(5 * low + 10 * (divs[i] - low), 100)
            tax = int(F(tax) - min(credit, F(tax)))
        tax += (t_gain + t_div) * 15 // 100                     # 措置法第8条の4, 第37条の11: 15 %
        i_n, i_f, i_l = sep15(sint[i])
        d_n, d_f, d_l = sep15(sdiv[i])
        g_n, g_f, g_l = sep15(sgain[i])
        # 措置法第41条の19 (from 2025): 22.5 % of the 基準所得金額 above 330,000,000 less the 基準所得税額
        mini = max(0, (g + max(0, sdiv[i]) + max(0, sgain[i]) - 330000000) * 225 // 1000 - (tax + d_n + g_n))
        fukko = (tax + mini) * 21 // 1000
        n_hijo = (1 if spouse and spouse[1] <= 580000 else 0) + sum(1 for age, inc in deps if inc <= 580000)
        ju = jumin(s, soc_tot[i], ideco[i], spouse, deps, single_parent, mother, n_hijo, divs[i], ddiv[i], dgain[i])
        out.append(dict(g=g, taxable=t, tax=tax + mini + i_n + d_n + g_n, fukko=fukko + i_f + d_f + g_f,
                        local=ju["pref"] + ju["muni"] + ju["kinto"] + i_l + d_l + g_l))
    return {"id": h.get("id"), "incomeTax": sum(o["tax"] for o in out),
            "surtaxes": {"復興特別所得税": sum(o["fukko"] for o in out)},
            "localIncomeTax": sum(o["local"] for o in out),
            "employeeSocial": sum(soc_tot),
            "benefits": 12 * jido_teate_month([c.get("age", 0) for c in h.get("children", [])]),
            "detail": {"persons": out, "social": soc}}


if __name__ == "__main__":
    for line in open(sys.argv[1], encoding="utf-8"):
        line = line.strip()
        if line:
            print(json.dumps(compute(json.loads(line)), ensure_ascii=False))
