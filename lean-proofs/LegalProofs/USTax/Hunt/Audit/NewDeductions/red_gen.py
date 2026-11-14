# Builds Red*.lean from the untouched copy of the original (rules + search, without its #eval block).
import sys, io
src = io.open('Orig.copy.lean', encoding='utf-8').read()
head = src.split('\n#eval do')[0]
END = '\nend Legal.USTax.Hunt.NewDeductions\n'

def sub(s, old, new):
    assert s.count(old) == 1, (old, s.count(old))
    return s.replace(old, new)

# search with a move filter (for ablation); nothing else changes
SIG_OLD = 'def search (title : String) (cutQbi : Bool) (f : Facts) (lit : Bool := false) : IO Unit := do'
SIG_NEW = 'def search (title : String) (cutQbi : Bool) (f : Facts) (lit : Bool := false) (keep : Move → Bool := fun _ => true) : IO Unit := do'
base = sub(head, SIG_OLD, SIG_NEW)
base = sub(base, '  let ms := moves f\n  let consider', '  let ms := (moves f).filter keep\n  let consider')

CAP_OLD = '''  let cap := if r.joint then capFull else if saltLiteral then capFull / 2
             else max (saltFloor / 2) (saltCap / 2 - 30 * (agi - thr) / 100)'''
def write(name, text, tail):
    io.open(name, 'w', encoding='utf-8', newline='\n').write(text + '\n' + tail + END)

tails = {k: io.open(k + '.tail', encoding='utf-8').read() for k in sys.argv[1:]}
for k, tail in tails.items():
    t = base
    if k == 'RedT2':   # Congress's fix: the reduction applies to the halved amount (the literal branch is deleted)
        t = sub(t, CAP_OLD, '''  let cap := if r.joint then capFull
             else max (saltFloor / 2) (saltCap / 2 - 30 * (agi - thr) / 100)''')
    if k == 'RedT1b':  # third reading: halve first, then clause (iii) floor of $10,000 as written
        t = sub(t, CAP_OLD, '''  let cap := if r.joint then capFull else if saltLiteral then max saltFloor (saltCap / 2 - 30 * (agi - thr) / 100)
             else max (saltFloor / 2) (saltCap / 2 - 30 * (agi - thr) / 100)''')
    if k in ('RedT4', 'RedT4b'):   # §164(b)(6) before Pub. L. 119-21: "$10,000 ($5,000 in the case of a married individual filing a separate return)"
        t = sub(t, CAP_OLD, '  let cap := if r.joint then min capFull 10000 else 5000')
    if k == 'RedT4b':  # also before the 2026 changes to §170(b)(1)(I) (0.5% floor), §170(p) and §68
        t = sub(t, '  let giftItem := min r.gifts (60 * agi / 100) - 5 * agi / 1000', '  let giftItem := min r.gifts (60 * agi / 100)')
        t = sub(t, '  let giftNonItem := min r.gifts (if r.joint then 2000 else 1000)', '  let giftNonItem := 0')
        t = sub(t, '  let cut68 := if r.itemize then 2 * (min itemPre (tiPre - qbi + itemPre - thr37)) / 37 else 0', '  let cut68 := 0')
    if k == 'RedT1':   # strict allocation: household items paid from joint funds are each spouse's as to half
        t = sub(t, 'salt := p.stateTax + (if pays then house else 0), mortgage := if pays then f.mortgage else 0,', 'salt := p.stateTax + house / 2, mortgage := f.mortgage / 2,')
        t = sub(t, '      gifts := if pays then gifts else 0, carInt := loan,', '      gifts := gifts / 2, carInt := loan,')
    write(k + '.lean', t, tail)
