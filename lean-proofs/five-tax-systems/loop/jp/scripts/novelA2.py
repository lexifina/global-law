"""N-A (refined): extra ふるさと burden caused by deductions missing from the 人的控除差 table.
Paired families at the same wage: (a) a 特定親族 student (wages 1,400,000: 合計所得 750,000) vs a 特定扶養 student (0);
(b) spouse 合計所得 850,000 (配偶者特別控除, no table row) vs spouse 0 (配偶者控除, row 50,000).
Burden at a 30,000-yen gift (below the 20 % cap for these wages)."""
import json, os
from jp import adult, hh, run
D = 30000
pairs = {
  "student": (lambda w, d: hh([adult(50, w, furusato=d), adult(48, 0)], children=[{"age": 20, "wages": 1400000}]),
              lambda w, d: hh([adult(50, w, furusato=d), adult(48, 0)], children=[{"age": 20, "wages": 0}])),
  "spouse": (lambda w, d: hh([adult(50, w, furusato=d), adult(48, 1500000)]),
             lambda w, d: hh([adult(50, w, furusato=d), adult(48, 0)])),
}
out = {}
for name, (fa, fb) in pairs.items():
    rows = []
    ws = list(range(2500000, 12000001, 5000))
    hs = []
    for w in ws:
        hs += [fa(w, 0), fa(w, D), fb(w, 0), fb(w, D)]
    res = run(hs)
    for i, w in enumerate(ws):
        a0, a1, b0, b1 = res[4*i:4*i+4]
        ba = D - (a0["_tax"] - a1["_tax"]); bb = D - (b0["_tax"] - b1["_tax"])
        rows.append((w, ba, bb, ba - bb))
    bad = [r for r in rows if r[3] > 500]
    print(name, "wages where the gift costs >500 yen more than in the paired family:", len(bad), "of", len(rows))
    # contiguous bands
    bands = []
    for r in bad:
        if bands and r[0] - bands[-1][1] <= 5000:
            bands[-1][1] = r[0]; bands[-1][2] = max(bands[-1][2], r[3])
        else:
            bands.append([r[0], r[0], r[3]])
    print("  bands (from, to, max extra burden on 30,000):", bands)
    out[name] = rows
json.dump(out, open(os.path.expanduser("~/cmp/loop/jp/runs/novel_A2.json"), "w"))
