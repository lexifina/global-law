#!/usr/bin/env python3
"""Print the text of norms from a gesetze-im-internet.de XML file: norm.py FILE '§ 32a' ['§ 2' ...]"""
import sys, re, xml.etree.ElementTree as ET
f = sys.argv[1]; wanted = sys.argv[2:]
root = ET.parse(f).getroot()
def text(el):
    out = []
    def walk(e, depth=0):
        tag = e.tag
        if tag in ('P',): out.append('\n')
        if tag in ('DT',): out.append('\n  ')
        if tag == 'BR': out.append('\n')
        if e.text: out.append(e.text)
        for c in e: walk(c, depth+1)
        if tag in ('DD',): out.append('')
        if e.tail: out.append(e.tail)
    walk(el)
    s = ''.join(out)
    s = re.sub(r'[ \t]+', ' ', s)
    s = re.sub(r'\n\s*\n+', '\n', s)
    return s.strip()
for norm in root.iter('norm'):
    md = norm.find('metadaten')
    enbez = md.findtext('enbez') or ''
    if wanted and enbez.strip() not in wanted: continue
    titel = md.findtext('titel') or ''
    td = norm.find('textdaten')
    print('=====', enbez, '|', titel)
    if td is not None:
        t = td.find('text')
        if t is not None: print(text(t))
        fn = td.find('fussnoten')
        if fn is not None: print('--- Fußnoten:', text(fn)[:3000])
