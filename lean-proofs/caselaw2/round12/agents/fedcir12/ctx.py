"""print D's text around J's citations (diagnosis helper): python -X utf8 ctx.py D J [width]"""
import json, re, subprocess, sys
D, J = sys.argv[1], sys.argv[2]
w = int(sys.argv[3]) if len(sys.argv) > 3 else 700
run = lambda n: subprocess.run([sys.executable, "-X", "utf8", "round6/history/r6lib.py", "text", n], capture_output=True,
                               text=True, encoding="utf-8").stdout
TJ, TD = run(J), run(D)
m = re.search(r"^citations:\s*(\[.*\])", TJ, re.M)
cites = json.loads(m.group(1)) if m else []
print("J cites", cites)
for c in cites:
    vol, rest = c.split(" ", 1)
    rep, page = rest.rsplit(" ", 1)
    rx = re.compile(re.escape(vol) + r"\s+" + r"\s*".join(map(re.escape, rep.replace(" ", ""))) + r"\s+" + re.escape(page))
    for mm in rx.finditer(TD):
        print("----", c, mm.start())
        print(TD[max(0, mm.start() - w):mm.end() + 300].replace("\n", " / "))
