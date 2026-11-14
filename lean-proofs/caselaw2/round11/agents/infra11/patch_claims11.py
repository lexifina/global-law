"""infra11 (lead request 05:2x, DESIGN11 section 5.1 / D11-4): claims anchorWide and anchorTribunal in
round11/certify11_claims.py (asserted replacements).

    python -X utf8 round11/agents/infra11/patch_claims11.py
"""
import os

C2 = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
p = os.path.join(C2, "round11", "certify11_claims.py")
s = open(p, encoding="utf-8").read()
assert "anchorTribunal" not in s, "already patched"


def rep(a, b):
    global s
    assert s.count(a) == 1, (a[:60], s.count(a))
    s = s.replace(a, b)


rep('''# round 11 (agent infra11): round10/certify10_claims.py with base round10/stage/v10d, ids t11: / h11: (nothing else
# changed); for rows with claim joinedFar or implicitReject.
''', '''# round 11 (agent infra11): round10/certify10_claims.py with base round10/stage/v10d, ids t11: / h11:; for rows with
# claim joinedFar or implicitReject; and (lead, D11-4, DESIGN11 section 5.1) the history claims
#   anchorWide      anchored row: the anchor-cue test uses anchor + anchor_wide + anchor_wide9 (cue_table.json; the v10d
#                   Lean's anchorWide, Certificate.lean anchorWide9_sound)
#   anchorTribunal  as anchorWide plus the list anchor_tribunal (cue_table.json once lean11 adds it; until then the six
#                   phrases of DESIGN11 section 5.1, ANCHOR_TRIBUNAL below)
#   "anchorWide+anchorTribunal" = both (the union). Every other check unchanged. The claim line(s) are written only
#   for an admitted ANCHORED row (a claim on a row without an anchor has no effect in the Lean; counted
#   claim_anchor_unused in stats.json).
''')
rep('''H_CLAIMS = ("-", "orderHead", "setAside")
''', '''H_CLAIMS = ("-", "orderHead", "setAside", "anchorWide", "anchorTribunal", "anchorWide+anchorTribunal")
ANCHOR_CLAIMS = ("anchorWide", "anchorTribunal")
# DESIGN11 section 5.1 (D11-4): used until cue_table.json has the key anchor_tribunal (stats.json: cue_source)
ANCHOR_TRIBUNAL = ["court of international trade", "customs court", "court of federal claims", "claims court",
                   "veterans court", "court of veterans appeals"]


def anchor_claims(claim):
    """The anchor claims a row's claim field carries (anchorWide / anchorTribunal, or both joined by '+')."""
    return [c for c in claim.split("+") if c in ANCHOR_CLAIMS]
''')
rep('''    for k, fb in DESIGN7_NUM.items():
''', '''    # round 11: the anchor lists of the claims anchorWide / anchorTribunal
    for k in ("anchor_wide", "anchor_wide9"):
        v = t.get(k)
        cues[k] = [c for c in v if c] if isinstance(v, list) else []
        src[k] = "cue_table.json" if isinstance(v, list) else "missing in cue_table.json (empty)"
    v = t.get("anchor_tribunal")
    if isinstance(v, list) and v:
        cues["anchor_tribunal"], src["anchor_tribunal"] = [c for c in v if c], "cue_table.json"
    else:
        cues["anchor_tribunal"] = list(ANCHOR_TRIBUNAL)
        src["anchor_tribunal"] = "DESIGN11 section 5.1 list (key not in cue_table.json yet)"
    for k, fb in DESIGN7_NUM.items():
''')
rep('''        if not any(c in al for c in cues["anchor"]):
            return "anchorNoCue", "", None
''', '''        acl = anchor_claims(r["claim"])
        alist = list(cues["anchor"])
        if acl:  # round 11: anchorWide / anchorTribunal widen the anchor-cue list (union)
            alist += cues["anchor_wide"] + cues["anchor_wide9"]
            if "anchorTribunal" in acl:
                alist += cues["anchor_tribunal"]
        if not any(c in al for c in alist):
            return "anchorNoCue", "", None
''')
rep('''    sha["history_claim_delta.tsv"] = write("history_claim_delta.tsv", (
        (r.get("base_id") or r["id"], r["claim"], "r7:" + r["rule"]) for r in out_h + out_claim_base
        if r["claim"] == "orderHead" or (r["claim"] == "setAside" and r["kind"] == "vacated")))
''', '''    sha["history_claim_delta.tsv"] = write("history_claim_delta.tsv", [
        (r.get("base_id") or r["id"], r["claim"], "r7:" + r["rule"]) for r in out_h + out_claim_base
        if r["claim"] == "orderHead" or (r["claim"] == "setAside" and r["kind"] == "vacated")] +
        [(r.get("base_id") or r["id"], c, "r7:" + r["rule"]) for r in out_h + out_claim_base
         if r["anchor"] is not None for c in anchor_claims(r["claim"])])
    st["claim_anchor_unused"] = sum(1 for r in out_h + out_claim_base if anchor_claims(r["claim"]) and r["anchor"] is None)
''')
open(p, "w", encoding="utf-8", newline="\n").write(s)
print("patched round11/certify11_claims.py")
