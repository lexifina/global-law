"""infra12: make_packs12 --exclude by identity whatever the id prefix (DESIGN12 section 3)."""
import os
C2 = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
p = os.path.join(C2, "round12", "audit", "make_packs12.py")
s = open(p, encoding="utf-8").read()
def rep(a, b):
    global s
    assert s.count(a) == 1, a[:70]
    s = s.replace(a, b)
rep(open(os.path.join(C2, "round12", "agents", "infra12", "ex_old1.txt"), encoding="utf-8").read(),
    open(os.path.join(C2, "round12", "agents", "infra12", "ex_new1.txt"), encoding="utf-8").read())
rep(open(os.path.join(C2, "round12", "agents", "infra12", "ex_old2.txt"), encoding="utf-8").read(),
    open(os.path.join(C2, "round12", "agents", "infra12", "ex_new2.txt"), encoding="utf-8").read())
rep(open(os.path.join(C2, "round12", "agents", "infra12", "ex_old3.txt"), encoding="utf-8").read(),
    open(os.path.join(C2, "round12", "agents", "infra12", "ex_new3.txt"), encoding="utf-8").read())
open(p, "w", encoding="utf-8", newline="\n").write(s)
print("patched")
