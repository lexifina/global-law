p = 'make_r9.py'
s = open(p, encoding='utf-8').read()
for old in ["    ('near_claim_para', F_, dict(gap=250, gapmod='para', win='none')),\n",
            "    ('far_para', F_, dict(gap=700, gapmod='para', exp='joinedFarPara')),\n",
            "    ('far_para_first', F_, dict(gap=700, gapmod='para_first', exp='joinedFarPara')),\n",
            "    ('far_para_last', F_, dict(gap=700, gapmod='para_last', exp='joinedFarPara')),\n"]:
    assert old in s, old
    s = s.replace(old, '')
old = "R9_MAIN = [\n"
new = ("# (no joinedFarPara case: a window is one TSV field, so it cannot hold a LF; the cert_text windows of the corpus\n"
       "# are normalised, tab / newline -> space (r6lib.norm). REF_QUESTIONS9.md Q9-13.)\n" + old)
s = s.replace(old, new, 1)
open(p, 'w', encoding='utf-8', newline='\n').write(s)
print('ok')
