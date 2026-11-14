import sys, collections
b = open(sys.argv[1], 'rb').read(5000000)
lines = b.split(b'\n')[:-1]
BS = bytes([92])
print('lines', len(lines), 'backslash-n', b.count(BS + b'n'), 'CR', b.count(b'\r'))
diff = collections.Counter()
for l in lines[:2000]:
    p = l.split(b'\t')
    w = p[3].decode('utf-8')
    diff[len(w) - (int(p[2]) - int(p[1]))] += 1
print('len(w) - (e0-s0):', sorted(diff.items())[:10])
l = lines[1].split(b'\t')
w = l[3].decode('utf-8')
i = w.find(chr(92))
print(repr(w[max(0, i - 40):i + 40]))
