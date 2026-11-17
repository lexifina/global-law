"""Adapt Mlang's 2019 M driver (m_ext/2019/cibles.m) to the 2018 releases: repeatedly compile, and for every
'variable inconnue' in the driver, delete the enclosing 'si present(..) alors .. finsi' block (or the line).
usage: hist_adapt_driver.py RELEASE EXTDIR (one adapted driver per release; each deletion is printed)."""
import re, subprocess, sys, os
rel = sys.argv[1]; drv = os.path.expanduser("~/fr/hist/mlang/m_ext/" + sys.argv[2] + "/cibles.m")
M = os.path.expanduser("~/fr/hist/mlang"); SRC = os.path.expanduser(f"~/fr/hist/releases/{rel}")
fs = sorted(os.listdir(SRC))
sf = [f"{SRC}/tgvI.m", f"{SRC}/errI.m"] + [f"{SRC}/{f}" for f in fs if f.endswith(".m") and not f.startswith(("err", "tgv"))]
for it in range(80):
    r = subprocess.run([f"{M}/_build/default/src/main.exe", "-A", "iliad", "--precision", "double",
        "--mpp_function=enchainement_primitif", "--income-year=2018", "--comparison_error_margin=0.000001",
        "--dgfip_options=-g,-O,-k4,-m2018,-X", "--backend", "dgfip_c", "--output", "/tmp/hist_adapt/enchain.c"] + sf + [drv],
        capture_output=True, text=True)
    out = re.sub(r"\x1b\[[0-9;]*m", "", r.stdout + r.stderr)
    if r.returncode == 0:
        print("OK after", it, "edits"); break
    m = re.search(r"\[ERROR\] (.*?)\n\s*\n\s*--> (\S+)\n.*?\n\s*(\d+) \|", out, re.S)
    if not m or not m.group(2).endswith(sys.argv[2] + "/cibles.m"):
        print("OTHER ERROR:\n", out[-1500:]); break
    L = int(m.group(3)) - 1
    lines = open(drv).read().split("\n")
    a = L
    while a > 0 and not re.match(r"\s*si present", lines[a]) and L - a < 6: a -= 1
    b = L
    while b < len(lines) - 1 and lines[b].strip() != "finsi" and b - L < 6: b += 1
    if re.match(r"\s*si present", lines[a]) and lines[b].strip() == "finsi":
        print(f"[{m.group(1)}] delete block {a+1}-{b+1}: {lines[a].strip()} / {lines[L].strip()}"); del lines[a:b+1]
    else:
        print(f"[{m.group(1)}] delete line {L+1}: {lines[L].strip()}"); del lines[L]
    open(drv, "w").write("\n".join(lines))
