"""Transfers the disposition tables do not list: Pub. L. 111-314 sec. 4(d) moved chapters 701 and 703 of title 49
into title 51 by renumbering. The credits of each title 51 section say so ("renumbered §70101 then §50901 of title
51"). Writes data/transfers.tsv in the dispo_rows format (title, src, caption, left, right)."""
import os, re, html
B = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
t = open(os.path.join(B, 'cache', 'USCODE-2011-title51.htm'), encoding='utf-8').read()
t = re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', t)))
ms = sorted(set(re.findall(r'renumbered §\s?(\d+[a-z]?)\s*then §\s?(\d+[a-z]?) of title 51', t)))
with open(os.path.join(B, 'data', 'transfers.tsv'), 'w', newline='\n', encoding='utf-8') as f:
    for old, new in ms:
        f.write(f'51\t49\tcredits: renumbered by Pub. L. 111-314 sec. 4(d)\t{old}\t{new}\n')
print(len(ms), 'transfers')
