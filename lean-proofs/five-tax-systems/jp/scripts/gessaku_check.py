"""Withholding tables, 令和7年分:
 (1) 所得税法 別表第二 (月額表, statute, 所得税 only) from the e-Gov XML (version in force in 2025);
 (2) the NTA's combined 月額表 (所得税 + 復興特別所得税) from the 令和7年分 源泉徴収税額表 PDF;
 (3) the 電算機計算の特例 (平成24年財務省告示第116号, 令和5年改正) formula.
Checks: NTA booklet table == e-Gov 別表第五 (給与所得控除後); NTA 月額表 == round10(statute x 1.021)?; formula vs NTA.
Writes lean/JpTax/GessakuData.lean (statute and NTA rows, 甲 columns 0-7) for the Lean checks.
usage: python3 -I gessaku_check.py"""
import re, os, sys
import xml.etree.ElementTree as ET
from fractions import Fraction as F

HOME = os.path.expanduser("~/cmp/jp")
FW = str.maketrans("０１２３４５６７８９，", "0123456789,")


def num(s):
    s = s.translate(FW).replace(",", "").replace("円", "").strip()
    return int(s) if re.fullmatch(r"\d+", s) else None


root = ET.parse(HOME + "/law/shotokuzeiho_2025-12-31.xml").getroot()


def table(title):
    for t in root.iter("AppdxTable"):
        tt = t.find("AppdxTableTitle")
        if tt is not None and title == "".join(tt.itertext()).strip():
            return t


# ---- (0) 別表第五: statute vs NTA printed
st5 = {}
for tr in table("別表第五").iter("TableRow"):
    v = [num("".join(c.itertext())) for c in tr.findall("TableColumn")]
    for i in range(len(v) - 2):
        if None not in v[i:i + 3] and v[i + 1] - v[i] == 4000 and 1900000 <= v[i] < 6600000:
            st5[v[i]] = v[i + 2]
nta5 = {}
for line in open(HOME + "/refs/nta/nencho2025_all.txt", encoding="utf-8"):
    nums = [int(x.replace(",", "")) for x in re.findall(r"\d{1,3}(?:,\d{3})+", line)]
    for i in range(len(nums) - 2):
        a, b, c = nums[i:i + 3]
        if b - a == 4000 and 1900000 <= a < 6600000 and a % 4000 == 0 and 0 < c < a:
            nta5[a] = c
print("別表第五 rows: statute %d, NTA booklet %d, identical: %s" % (len(st5), len(nta5), st5 == nta5))

# ---- (1) statute 別表第二 甲 columns
st2 = []
for tr in table("別表第二").iter("TableRow"):
    v = [num("".join(c.itertext())) for c in tr.findall("TableColumn")]
    if len(v) >= 10 and v[0] is not None and v[1] is not None and v[0] < v[1] and all(x is not None for x in v[2:10]):
        st2.append((v[0], v[1], v[2:10]))
st2.sort()
print("別表第二 (statute) rows with 甲 0-7:", len(st2), "first", st2[0][:2], "last", st2[-1][:2])

# ---- (2) NTA combined 月額表 rows
nta2 = {}
for line in open(HOME + "/refs/nta/zeigakuhyo2024_all.txt", encoding="utf-8"):
    nums = [int(x.replace(",", "")) for x in re.findall(r"\d{1,3}(?:,\d{3})*", line)]
    if len(nums) >= 10 and 88000 <= nums[0] < 740000 and nums[0] < nums[1] <= 740000:
        nta2[(nums[0], nums[1])] = nums[2:10]
print("月額表 (NTA, combined) rows:", len(nta2))
same_rows = sum(1 for lo, hi, _ in st2 if (lo, hi) in nta2)
print("rows present in both:", same_rows)


def round10(x):          # 四捨五入 to 10 yen
    return int((x + 5) // 10 * 10)


cells = mism = 0
worst = []
for lo, hi, vals in st2:
    if (lo, hi) not in nta2:
        continue
    for k in range(8):
        cells += 1
        pred = round10(F(vals[k]) * F(1021, 1000))
        if pred != nta2[(lo, hi)][k]:
            mism += 1
            worst.append((lo, hi, k, vals[k], nta2[(lo, hi)][k], pred))
print("NTA cell == round10(statute x 1.021): %d of %d cells; mismatches %d" % (cells - mism, cells, mism), worst[:10])


# ---- (3) 告示 formula (令和7年分)
def kyuyo_kojo(a):
    if a <= 135416:
        return F(45834)
    if a <= 149999:
        x = F(a) * F(40, 100) - 8333
    elif a <= 299999:
        x = F(a) * F(30, 100) + 6667
    elif a <= 549999:
        x = F(a) * F(20, 100) + 36667
    elif a <= 708330:
        x = F(a) * F(10, 100) + 91667
    else:
        return F(162500)
    return F(-((-x.numerator) // x.denominator))       # 1円未満切り上げ


def kiso(a):
    return 40000 if a <= 2162499 else (26667 if a <= 2204166 else (13334 if a <= 2245833 else 0))


def denshi(a, n):
    b = a - kyuyo_kojo(a) - kiso(a) - 31667 * n
    if b <= 0:
        return 0
    for hi, r, c in [(162500, F(5105, 100000), 0), (275000, F(10210, 100000), 8296), (579166, F(20420, 100000), 36374),
                     (750000, F(23483, 100000), 54113), (1500000, F(33693, 100000), 130688),
                     (3333333, F(40840, 100000), 237893), (10 ** 12, F(45945, 100000), 408061)]:
        if b <= hi:
            return round10(b * r - c)


diffs = []
for (lo, hi), vals in sorted(nta2.items()):
    for k in range(8):
        for a in (lo, (lo + hi - 1) // 2, hi - 1):
            diffs.append((abs(denshi(a, k) - vals[k]), lo, hi, k, a, denshi(a, k), vals[k]))
mid = [d for d in diffs if d[4] == (d[1] + d[2] - 1) // 2]
print("告示 formula vs NTA 月額表: max |diff| over row ends and midpoints %d yen; at the row midpoint: %d of %d cells equal, max |diff| %d" %
      (max(d[0] for d in diffs), sum(1 for d in mid if d[0] == 0), len(mid), max(d[0] for d in mid)))
print("largest:", sorted(diffs, reverse=True)[:5])

# ---- write Lean data (statute and NTA 甲 rows)
with open(HOME + "/lean/JpTax/GessakuData.lean", "w") as f:
    f.write("/-!\n# 月額表 data (machine-extracted, do not edit)\n\n`gessakuStatute`: 所得税法 別表第二 (甲, 0-7 扶養親族等), e-Gov revision 340AC0000000033_20251218_507AC0000000013\n")
    f.write("(the table in force for 2025 payments; 所得税 only). `gessakuNTA`: the combined (所得税 + 復興特別所得税) 月額表 of the NTA's\n「令和7年分 源泉徴収税額表」 (zeigakuhyo2024/data/all.pdf). Rows: (以上, 未満, [甲 0, ..., 甲 7]). Generated by\n`scripts/gessaku_check.py`.\n-/\n\nnamespace JpTax\n\n")
    rows = [(lo, hi, vals, nta2[(lo, hi)]) for lo, hi, vals in st2 if (lo, hi) in nta2]
    CH = 20
    for ci in range(0, len(rows), CH):
        f.write("def gessakuChunk%d : List (Int × Int × List Int × List Int) := [\n" % (ci // CH))
        f.write(",\n".join("  (%d, %d, [%s], [%s])" % (lo, hi, ", ".join(map(str, a)), ", ".join(map(str, b)))
                           for lo, hi, a, b in rows[ci:ci + CH]))
        f.write("]\n\n")
    n = (len(rows) + CH - 1) // CH
    f.write("def gessakuChunks : List (List (Int × Int × List Int × List Int)) := [\n  ")
    f.write(", ".join("gessakuChunk%d" % i for i in range(n)) + "]\n\nend JpTax\n")
print("wrote GessakuData.lean with", len(rows), "rows in", n, "chunks")
