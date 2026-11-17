"""Dump each #[test] scope of catala-examples/impot_revenu/tests: the scope's code block (inputs) and the
expected result block (catala-test-cli), without the zero lines. usage: catala_tests_dump.py [file ...]"""
import re, sys, glob, os

D = os.path.expanduser("~/fr/refs/catala-examples/impot_revenu/tests")
files = sys.argv[1:] or sorted(glob.glob(D + "/*.catala_fr"))
FENCE = "`" * 3
for f in files:
    txt = open(f, encoding="utf-8").read()
    blocks = re.findall(FENCE + r"(catala|catala-test-cli)\n(.*?)" + FENCE, txt, re.S)
    for kind, body in blocks:
        if kind == "catala" and "#[test]" not in body:
            continue
        lines = [l for l in body.splitlines() if l.strip() and not re.search(
            r"^\s*[()}]+\s*$|\)\.sortie|résultat sortie contenu|^champ d'application|définition sortie|^[└┌]|^\$ catala|: 0,00 €$|: \[\]$|#\[test\]", l)]
        print(("== " + os.path.basename(f) + " ") if kind == "catala" else "-- expected", "\n" + "\n".join(lines))
