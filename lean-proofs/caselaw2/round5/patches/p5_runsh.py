"""Round 5 patch 5: run_lean.sh writes the oclass headers and merges classes-*.tsv in round-5 mode."""
p = r"~\Documents\us-caselaw-lean-work\caselaw-lean-2\run_lean.sh"
s = open(p, encoding="utf-8").read()
pairs = [
("""merge status  $'node\\tissue\\tholding\\tfrom\\tto\\tstatus\\tclass\\tfirm\\twitness_row\\tactor\\tpath'
merge findings $'finding\\tciting\\tcited\\tissue\\tdetail\\tfirm\\tpath'
""",
"""# round 5 (DESIGN5 section 1): treatment_class.tsv in the data dir turns round-5 output on: one more column
# (oclass) on status, status_lines and findings, and classes.tsv
OC=; [ -f "$DATA/treatment_class.tsv" ] && OC=$'\\toclass'
merge status  $'node\\tissue\\tholding\\tfrom\\tto\\tstatus\\tclass\\tfirm\\twitness_row\\tactor\\tpath'"$OC"
merge findings $'finding\\tciting\\tcited\\tissue\\tdetail\\tfirm\\tpath'"$OC"
"""),
("""merge status_lines $'node	issue	holding	from	to	status	class	firm	witness_row	actor	path	line'
""",
"""merge status_lines $'node	issue	holding	from	to	status	class	firm	witness_row	actor	path	line'"$OC"
if [ -n "$OC" ]; then merge classes $'id\\tclass\\tclaim\\tverdict\\tfield_limit\\tdoctrine\\twitness'; rm -f "$OUT"/classes-*.tsv; fi
"""),
]
for a, b in pairs:
    assert s.count(a) == 1, a[:50]
    s = s.replace(a, b)
open(p, "w", encoding="utf-8", newline="\n").write(s)
print("patched")
