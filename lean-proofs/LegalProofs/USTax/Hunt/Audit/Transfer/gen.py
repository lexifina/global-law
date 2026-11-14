"""Red-team generator: builds variants of Transfer.lean (never edits the original)."""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ORIG = os.path.join(HERE, "..", "..", "Transfer.lean")


def sub1(src, old, new):
    assert src.count(old) == 1, (src.count(old), old[:60])
    return src.replace(old, new)


def build(name, incFrac=0, split2519=True, spTaxFromTrust=True, growth=True, excl=15000000,
          score="wealth s", extra="", ns_extra="", minimal=False):
    src = io.open(ORIG, encoding="utf-8").read().replace("\r\n", "\n")
    src = sub1(src, '#eval runScenario "A"\n', '')
    # parameters
    src = sub1(src, "def annualExcl : Nat := 19000\n",
        "def annualExcl : Nat := 19000\n"
        "/-- RED: per-mille of the QTIP value that is the income interest (a §2511 gift, not a §2519 transfer). -/\n"
        f"def incFrac : Nat := {incFrac}\n"
        "/-- RED: does §2513 reach the §2519 deemed transfer? -/\n"
        f"def split2519 : Bool := {'true' if split2519 else 'false'}\n"
        "/-- RED: may the trust pay the consenting spouse's half of the tax (§2207A(b) read broadly)? -/\n"
        f"def spTaxFromTrust : Bool := {'true' if spTaxFromTrust else 'false'}\n")
    if minimal:
        # T2, the one minimal edit: §2513 does not apply to a transfer treated as made under §2519
        assert incFrac == 0 and not split2519
        src = sub1(src,
            "    let (s2, gt, _) := taxGift s d s.q.v false\n    match (Pot.mk s.q.v s.q.b).pay gt with\n",
            "    let (sB, gt, _) := taxGift { s with split := false } d s.q.v false\n"
            "    let s2 : St := { sB with split := s.split }\n"
            "    match (Pot.mk s.q.v s.q.b).pay gt with\n")
        src = sub1(src,
            "      else if s.split && s.married then\n        let g2 : Pot := ⟨pot.v / 2, pot.b / 2⟩\n",
            "      else if false then\n        let g2 : Pot := ⟨pot.v / 2, pot.b / 2⟩\n")
    else:
        src = sub1(src,
            "    let (s2, gt, _) := taxGift s d s.q.v false\n    match (Pot.mk s.q.v s.q.b).pay gt with\n",
            "    let aInc := s.q.v * incFrac / 1000\n"
            "    let (sA, gtA, _) := taxGift s d aInc false\n"
            "    let (sB, gtB, _) := taxGift { sA with split := sA.split && split2519 } d (s.q.v - aInc) false\n"
            "    let s2 : St := { sB with split := s.split }\n"
            "    let gt := gtA + gtB\n"
            "    let gtSp := if s.split && s.married then (s2.per (sp d)).gtax - (s.per (sp d)).gtax else 0\n"
            "    if !spTaxFromTrust && gtSp > 0 then none else\n"
            "    match (Pot.mk s.q.v s.q.b).pay gt with\n")
        src = sub1(src,
            "      else if s.split && s.married then\n        let g2 : Pot := ⟨pot.v / 2, pot.b / 2⟩\n",
            "      else if s.split && s.married then\n        let sh := if split2519 then 1000 else incFrac\n"
            "        let g2 : Pot := ⟨pot.v * sh / 2000, pot.b * sh / 2000⟩\n")
    if not growth:
        assert src.count("1403 / 1000") == 5, src.count("1403 / 1000")
        src = src.replace("1403 / 1000", "1000 / 1000")
        src = sub1(src, "113 ^ t / 100 ^ t", "100 ^ t / 100 ^ t")
        assert src.count("5751 / 1000") == 2
        src = src.replace("5751 / 1000", "5000 / 1000")
    if excl != 15000000:
        src = sub1(src, "((15000000 * 1", f"(({excl} * 1")
    src = sub1(src, "def prune (sc : Sched)", f"def score (s : St) : Nat := {score}\n\ndef prune (sc : Sched)")
    src = sub1(src, "(wealth (finish sc s), sig p, s, p)", "(score (finish sc s), sig p, s, p)")
    src = sub1(src, "let scored := xs.map fun (s, p) => (wealth s, sig p, s, p)",
               "let scored := xs.map fun (s, p) => (score s, sig p, s, p)")
    tail = io.open(os.path.join(HERE, "tail.lean.txt"), encoding="utf-8").read().replace("\r\n", "\n")
    if not growth:
        tail = tail.replace("1403", "1000")
    head, _rest = src.split("end Legal.USTax.Hunt.Transfer\n")
    out = (head + tail + ns_extra + "\nend Legal.USTax.Hunt.Transfer\n\n"
           "def main (args : List String) : IO Unit := Legal.USTax.Hunt.Transfer.redMain args\n" + extra)
    io.open(os.path.join(HERE, f"Red{name}.lean"), "w", encoding="utf-8", newline="\n").write(out)


def kern(name):
    return io.open(os.path.join(HERE, name), encoding="utf-8").read().replace("\r\n", "\n")


if __name__ == "__main__":
    build("Orig")                                              # reproduces the original rules
    build("Closed", split2519=False, minimal=True)             # T2: the one minimal edit
    for f in (200, 300, 400, 500):
        build(f"ClosedF{f}", incFrac=f, split2519=False)       # T2 with the §2511 income-interest gift left splittable
    build("Strict", spTaxFromTrust=False)                      # T1: trust may not pay the consenting spouse's tax
    build("NoGrowth", growth=False)
    build("NoGrowthClosed", growth=False, split2519=False, minimal=True)
    build("Excl2025", excl=13990000)
    build("Excl7", excl=7000000)
    build("MinTax", score="1000000000000 - s.xfer")
    build("MaxGross", score="s.k.v + s.k529 + s.c.own.v + s.tH.v + s.tW.v + s.q.v + (if s.newH then 0 else s.h.own.v) + (if s.newW then 0 else s.w.own.v)")
    if os.path.exists(os.path.join(HERE, "kernel_orig.lean.txt")):
        build("KernelOrig", ns_extra=kern("kernel_orig.lean.txt"))
    if os.path.exists(os.path.join(HERE, "kernel_closed.lean.txt")):
        build("KernelClosed", split2519=False, minimal=True, ns_extra=kern("kernel_closed.lean.txt"))
