"""Print the OLRC amendment notes of a Title 26 section that mention a given Public Law (prior text of amended items)."""
import re, sys, os
s = open(os.path.expanduser('~/Documents/tax-formalization-data/xml/usc26.xml'), encoding='utf-8').read()
sec, pl = sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else '119–21'
i = s.find(f'identifier="/us/usc/t26/s{sec}"')
j = s.find('<section', i + 10)
t = re.sub(r'<[^>]+>', ' ', s[i:j]); t = re.sub(r'[ \t]+', ' ', t)
k = t.find('Amendments')
for para in re.split(r'(?=\d{4}—Subsec)|(?=Subsec\. )|(?=Pars?\. )|(?=Subpars?\. )', t[k:]):
    if pl in para: print(para.strip()[:1500]); print('--')
