"""nj9: the NJ courts' own words on the authority of the pre-1948 courts' decisions.
Greps the texts of post-1948 NJ decisions (courts 1096 Sup, 1099 AppDiv, 1222 ChanDiv, 1224 LawDiv, 1227 Superior)
dated 1948-09-15..1995 for sentences naming a pre-1948 court together with a binding / overruling word.
Corpus text only (round6/history/r6lib.fetch_texts); no key.  Usage: python -X utf8 nj_grep.py > grep.tsv"""
import os, re, sys
C2 = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, os.path.join(C2, 'round6', 'history'))
import r6lib as L

COURTS = {1096: 'Sup', 1099: 'AppDiv', 1222: 'ChanDiv', 1224: 'LawDiv', 1227: 'Superior'}
OLD = r"(former|old|then|pre-1948|predecessor)\s+(New Jersey\s+)?(Supreme Court|Court of Errors and Appeals|Court of Chancery|Prerogative Court|E\s*&\s*A|Chancery)|Court of Errors and Appeals|E\.\s*&\s*A\."
BIND = r"\bbind|\bbound\b|\boverrul|stare decisis|\bdepart\b|controlling|not (?:be )?followed|successor|predecessor|equal (?:dignity|authority|rank)|coordinate"
OLD_RE = re.compile(OLD, re.I)
BIND_RE = re.compile(BIND, re.I)
SPLIT = re.compile(r"(?<=[.;])\s+(?=[A-Z(\"'])")


class _Sent:
    """finditer over sentences (split at . ; followed by a capital) holding both an old-court name and a binding word."""
    @staticmethod
    def finditer(t):
        last = -1
        for m in OLD_RE.finditer(t):
            if m.start() < last:
                continue
            a, b = max(0, m.start() - 250), min(len(t), m.end() + 250)
            w = t[a:b]
            if BIND_RE.search(w):
                last = b
                yield _M(w, a)


class _M:
    def __init__(self, s, st):
        self.s, self._st = s, st

    def group(self, _i=0):
        return self.s

    def start(self):
        return self._st


SENT = _Sent


def main():
    nodes = []
    with open(os.path.join(C2, 'round8', 'stage', 'v8e', 'decisions2.tsv'), encoding='utf-8') as f:
        for line in f:
            p = line.split('\t', 3)
            c = int(p[1]) if p[1] else -1
            d = int(p[2] or 0)
            if c in COURTS and 19480915 <= d <= 19951231:
                nodes.append((int(p[0]), c, d))
    sys.stderr.write('%d decisions\n' % len(nodes))
    info = {n: (c, d) for n, c, d in nodes}
    ids = [n for n, _, _ in nodes]
    for i in range(0, len(ids), 2000):
        texts = L.fetch_texts(ids[i:i + 2000])
        for n, (_sha, t) in texts.items():
            for m in SENT.finditer(t):
                s = L.norm(m.group(0)).strip()
                if len(s) > 30:
                    c, d = info[n]
                    sys.stdout.write('%d\t%s\t%d\t%d\t%s\n' % (n, COURTS[c], d, m.start(), s))
        sys.stderr.write('%d\n' % (i + 2000))


if __name__ == '__main__':
    main()
