p = 'make_r9.py'
s = open(p, encoding='utf-8').read()
old = """            pz = os.path.join(data, 'part_zone.tsv')
            if os.path.exists(pz):
                os.remove(pz)
            if mode == 'empty':"""
new = """            pz = os.path.join(data, 'part_zone.tsv')
            if os.path.exists(pz):
                os.remove(pz)
            kp = os.path.join(data, 'treatment_class.tsv')      # the round-9 claims (DESIGN9 §5, §7) dropped
            if os.path.exists(kp):
                with open(kp, 'rb') as fh:
                    kl = fh.read().split(b'\n')
                with open(kp, 'wb') as fh:
                    fh.write(b'\n'.join(l for l in kl if not (len(l.split(b'\t')) > 1 and l.split(b'\t')[1] in (
                        b'joinedFar', b'implicitReject'))))
            if mode == 'empty':"""
assert old in s
s = s.replace(old, new)
s = s.replace('''    """Round 9 off: with part_zone.tsv absent / empty / blank the current reference writes what the pre-round-9 copy
    writes; with lines only on unknown nodes, or only bad lines, every output file but ref_stats.tsv is the same."""''',
'''    """Round 9 off: with part_zone.tsv absent / empty / blank and no joinedFar / implicitReject class line, the
    current reference writes what the pre-round-9 copy writes; with zone lines only on unknown nodes, or only bad
    lines, every output file but ref_stats.tsv is the same."""''')
open(p, 'w', encoding='utf-8', newline='\n').write(s)
print('ok')
