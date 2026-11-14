"""nj9: how many decisions filed under court 1095 (old NJ Supreme Court) carry the Court of Errors and Appeals vote roll
("For affirmance -- The Chancellor ..." / "For reversal -- The Chancellor ..."), i.e. are E&A decisions mis-filed.
Corpus text only.  Usage: python -X utf8 ea_roll.py > ea_roll.tsv"""
import os, re, sys
C2 = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, os.path.join(C2, 'round6', 'history'))
import r6lib as L

ROLL = re.compile(r"For (affirmance|reversal|modification)\s*[-—–:,.]+\s*The Chancellor", re.I)


def main():
    nodes = []
    with open(os.path.join(C2, 'round8', 'stage', 'v8e', 'decisions2.tsv'), encoding='utf-8') as f:
        for line in f:
            p = line.split('\t', 3)
            if p[1] == '1095':
                nodes.append(int(p[0]))
    n_roll = 0
    for i in range(0, len(nodes), 2000):
        for n, (_s, t) in L.fetch_texts(nodes[i:i + 2000]).items():
            m = ROLL.search(t)
            if m:
                n_roll += 1
                sys.stdout.write('%d\t%s\n' % (n, L.norm(t[m.start():m.start() + 80])))
    sys.stderr.write('1095 decisions %d, with E&A vote roll %d\n' % (len(nodes), n_roll))


if __name__ == '__main__':
    main()
