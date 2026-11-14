"""Regression test for hard-wrapped texts (round 3). Run: python -X utf8 test_hardwrap.py

Checks: (1) the sample is detected as hard-wrapped and an ordinary one-line-per-paragraph text is not; (2) the
sentence of a wrapped act is whole, not the line; (3) a pattern split by line-end hyphenation is found and its span is
an offset span of the ORIGINAL text; (4) every candidate's quote, cut from the original text at the recorded offsets
and normalised as SCHEMA says (tab/newline -> space, one for one), equals the stored window slice, i.e. what
certify2.py asserts and what the checkers re-check; (5) the v1 path (HW_MODE off) is unchanged.
"""
import os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common, scan, scan2  # noqa: E402,F401

FILL = ("   The parties dispute whether the statute reaches the conduct at issue here, and the\n"
        "court of appeals held that it does. We granted certiorari to decide that question, and\n"
        "we now reverse the judgment below for the reasons that follow in this opinion today.\n") * 12
SAMPLE = ("# Dobbs v. Jackson\n\n## Combined\n\n" + FILL +
          "firm or overrule Roe and Casey. Brief for Respondents 50.\n"
          "   We hold that Roe v. Wade, 410 U. S. 113 (1973), and Planned Parenthood of South-\n"
          "eastern Pa. v. Casey, 505 U. S. 833 (1992), must be overruled. The Con-\n"
          "stitution makes no reference to abortion, and no such right\n"
          "is implicitly protected by any constitutional provision.\n\n"
          "\x0c                 Cite as: 597 U. S. ____ (2022)          5\n\n"
          "                        Opinion of the Court\n\n"
          "   For these reasons the decision in Smith v. Jones, 300 U. S. 1 (1937), is hereby over-\n"
          "ruled. Courts must exercise their independent judgment in such cases.\n" + FILL)
PLAIN = "# A v. B\n\n## Majority\n\n" + ("We overrule Smith v. Jones, 300 U. S. 1 (1937). " * 40 + "\n\n") * 30


def norm(s):
    return s.replace("\t", " ").replace("\n", " ")


def main():
    assert common.hard_wrapped(SAMPLE) and not common.hard_wrapped(PLAIN)
    view = common.unwrap_view(SAMPLE)
    assert len(view) == len(SAMPLE) and norm(view) == norm(SAMPLE)
    dh, omap = common.dehyphen(SAMPLE, 0, view)
    assert "overruled. Courts" in dh and omap[len(dh)] == len(view)
    for i in range(0, len(dh), 97):
        assert dh[i] == view[omap[i]]
    scan.HW_MODE, scan.HW_ONLY = True, True
    assert scan.scan_text(1, "x", PLAIN) is None
    d, cands, _ = scan.scan_text(1, "x", SAMPLE)
    sents = [norm(SAMPLE[c["s0"]:c["s1"]]) for c in cands]
    assert any(s.startswith("We hold that Roe v. Wade, 410 U. S. 113 (1973), and Planned") and
               s.endswith("must be overruled.") for s in sents), sents
    hy = [c for c in cands if "over- ruled" in norm(SAMPLE[c["s0"]:c["s1"]])]
    assert hy and hy[0]["hw"] == 1, sents
    a, b = hy[0]["m"][0]
    assert SAMPLE[a:b] == "over-\nruled", repr(SAMPLE[a:b])
    assert common.dehyphen_norm(norm(SAMPLE[hy[0]["s0"]:hy[0]["s1"]])).endswith("is hereby overruled.")
    for c in cands:
        assert c["w"][c["s0"] - c["w0"]:c["s1"] - c["w0"]] == norm(SAMPLE[c["s0"]:c["s1"]])
        assert all(SAMPLE[o0:o1] and c["s0"] - 400 <= o0 for o0, o1, k in c["c"])
        assert "\n" not in SAMPLE[c["s0"]:c["s1"]].replace("\n", " ", 99) 
    # the old behaviour: with HW_MODE off the wrapped act is cut at the line
    scan.HW_MODE, scan.HW_ONLY = False, False
    d0, cands0, _ = scan.scan_text(1, "x", SAMPLE)
    assert not any(norm(SAMPLE[c["s0"]:c["s1"]]).endswith("must be overruled.") and "Roe" in SAMPLE[c["s0"]:c["s1"]]
                   for c in cands0)
    print("ok", len(cands), "candidates;", len(cands0), "without unwrapping")


if __name__ == "__main__":
    main()
