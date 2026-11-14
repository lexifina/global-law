"""Round 5 patch 6: oclass is the LAST column of status_lines too (after `line`)."""
import os
p = r"~\Documents\global-law-lean\lean-proofs\LegalProofs\CaseLaw2\Run.lean"
s = open(p, encoding="utf-8").read()
pairs = [
("""\\t{path}" ++
            (if r5 then "\\t" ++ oclassOf ea h.issue d d else "")
          match ln with
          | none =>
            sh.putStrLn row
            nStatus := nStatus + 1
          | some l =>
            slh.putStrLn (row ++ "\\t" ++ lineName l)
            nLineRows := nLineRows + 1""",
"""\\t{path}"
          let oc := if r5 then "\\t" ++ oclassOf ea h.issue d d else ""
          match ln with
          | none =>
            sh.putStrLn (row ++ oc)
            nStatus := nStatus + 1
          | some l =>
            slh.putStrLn (row ++ "\\t" ++ lineName l ++ oc)
            nLineRows := nLineRows + 1"""),
]
for a, b in pairs:
    assert s.count(a) == 1, a[:50]
    s = s.replace(a, b)
open(p, "w", encoding="utf-8", newline="\n").write(s)
print("patched")
