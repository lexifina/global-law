"""Later drift, from the Code's own notes (2024 edition of each restated title, govinfo): laws that amended an old
location after the restating bill's cutoff date, so their words are not in the new section's printed text, or that
directed amendments to a section already repealed. Three phrasings:

  'Amendment(s) Not Shown in Text': "This section was derived from section 1f of Title 16, which was amended by
      Pub. L. 113-40 ... For applicability of that amendment to this section, see section 6(b) of Pub. L. 113-287"
  'directed the amendment of former ...': title 46, "Pub. L. 109-241, §310, which directed the amendment of former
      section 12105 of this title from which this section was derived in part, was repealed by Pub. L. 110-181"
  'amended after the ... cutoff date': title 36, "Section 5201(b) of former Title 36, from which this section was
      derived, was amended after the Aug. 15, 1997, cutoff date by Pub. L. 105-276"

Writes data/drift_notes.tsv: title, section, kind, amending laws (enactment order), note excerpt."""
import os, re, sys, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from analyze import html_text

out = []
for t in [36, 40, 41, 46, 51, 54]:
    x = html_text(f'USCODE-2024-title{t}.htm')
    heads = [(m.start(), m.group(1)) for m in re.finditer(r'§(\d+[a-z]?(?:-\d+)?)\. [A-Z]', x)]
    def sec_at(pos):
        lo, hi, best = 0, len(heads) - 1, ''
        while lo <= hi:
            mid = (lo + hi) // 2
            if heads[mid][0] <= pos:
                best, lo = heads[mid][1], mid + 1
            else:
                hi = mid - 1
        return best
    found = []
    for m in re.finditer(r'Amendments? Not Shown in Text ((?:This|Subsec|Subsection|Section|Subsecs)\b.{0,8000}?)(?=Statutory Notes|Editorial Notes|Amendments \d{4}|'
                         r'Historical and Revision|§\d+[a-z]?\. [A-Z]|$)', x):
        seg = m.group(1)
        # only the laws that amended the old provision: between "which was amended by" and "For applicability"
        part = seg.split('For applicability')[0]
        part = part[part.find('amended by'):] if 'amended by' in part else part
        laws = re.findall(r'Pub\. L\. (\d+-\d+)', part)
        found.append((m.start(), 'not shown in text', laws, seg[:400]))
    for m in re.finditer(r'(Pub\. L\. (\d+-\d+)[^.]{0,60}?), which directed the amendment of ([^.]{0,160}?former[^.]{0,160}?)'
                         r', (was|were) repealed by Pub\. L\. (\d+-\d+)', x):
        found.append((m.start(), 'directed amendment of a former section; repealed by Pub. L. ' + m.group(5),
                      [m.group(2)], m.group(0)[:400]))
    for m in re.finditer(r'(was|were) amended after the ([A-Z][a-z]+\.? \d+, \d{4}),? cutoff date by (.{0,300})', x):
        laws = re.findall(r'Pub\. L\. (\d+-\d+)', m.group(3).split(', see section')[0])
        found.append((m.start(), 'amended after the cutoff date', laws, x[max(0, m.start() - 120): m.end()][:400]))
    restating = {36: '105-225', 40: '107-217', 41: '111-350', 46: '109-304', 51: '111-314', 54: '113-287'}[t]
    for pos, kind, laws, ex in found:
        laws = [l for l in dict.fromkeys(laws) if l != restating]
        out.append((t, sec_at(pos), kind, ' '.join(laws), ex.replace('\t', ' ')))
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'drift_notes.tsv'), 'w',
          newline='\n', encoding='utf-8') as f:
    f.write('title\tsection\tkind\tlaws\texcerpt\n')
    for r in out:
        f.write('\t'.join(map(str, r)) + '\n')
c = collections.Counter((r[0], r[2].split(';')[0]) for r in out)
for k, v in sorted(c.items()):
    print(k, v)
laws = collections.Counter((r[0], l) for r in out for l in r[3].split())
print('distinct (title, amending law):', len(laws))
print('sections with a note:', len({(r[0], r[1]) for r in out}))
