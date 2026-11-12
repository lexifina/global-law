"""Audit helper: python tools/law_text.py "Pub. L. 117-103" "<a few words of the instruction>" [chars]
Prints the Act's text (from the cached GovInfo USLM XML) around the first place those words occur."""
import re, sys
from lxml import etree
sys.path.insert(0, 'tools')
import fetch
law, words = sys.argv[1], sys.argv[2]
n = int(sys.argv[3]) if len(sys.argv) > 3 else 2500
c, k = (int(x) for x in law.replace('Pub. L. ', '').split('-'))
x = fetch.fetch(fetch.plaw_uslm(c, k), offline=True)
t = re.sub(r'\s+', ' ', ' '.join(etree.fromstring(x).itertext()))
norm = lambda s: re.sub(r'[\s“”"‘’\'—–-]', '', s)
i = norm(t).find(norm(re.sub(r'\s+', ' ', words)))
print(fetch.plaw_uslm(c, k))
if i < 0:
    print('NOT FOUND in law text'); sys.exit()
# map position back approximately
j = int(i * len(t) / max(1, len(norm(t))))
sys.stdout.reconfigure(encoding='utf-8')
print(t[max(0, j - n // 2): j + n])
