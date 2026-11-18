"""Render legislation.gov.uk CLML XML as readable text (structure kept, commentary listed at the end).
usage: python3 -I leg2txt.py file.xml [--notes]"""
import sys, re
import xml.etree.ElementTree as ET
NS = '{http://www.legislation.gov.uk/namespaces/legislation}'
def tag(e): return e.tag.split('}')[-1]
def inline(e):
    parts = []
    def rec(x):
        t = tag(x)
        if t in ('CommentaryRef', 'FootnoteRef'): pass
        elif t == 'Pnumber' and x is not e: pass
        else:
            if x.text: parts.append(x.text)
            for c in x: rec(c); 
        if x.tail and x is not e: parts.append(x.tail)
    rec(e)
    return re.sub(r'\s+', ' ', ''.join(parts)).strip()
out = []
def emit(s, ind): out.append('  ' * ind + s)
def render(e, ind=0, prefix=''):
    t = tag(e)
    if t in ('Commentaries', 'Metadata', 'Contents', 'Footnotes'): return
    if t in ('Part', 'Chapter', 'Pblock', 'PsubBlock', 'Schedule'):
        num = e.find(NS + 'Number'); title = e.find(NS + 'Title')
        emit('# ' + ' '.join(x for x in [inline(num) if num is not None else '', inline(title) if title is not None else ''] if x), ind)
        for c in e:
            if tag(c) not in ('Number', 'Title'): render(c, ind, prefix)
        return
    if t == 'P1group':
        title = e.find(NS + 'Title')
        if title is not None: emit('## ' + inline(title), ind)
        for c in e:
            if tag(c) != 'Title': render(c, ind, prefix)
        return
    if t in ('P1', 'P2', 'P3', 'P4', 'P5', 'P6'):
        pn = e.find(NS + 'Pnumber')
        num = inline(pn) if pn is not None else ''
        lab = (num + '.') if t == 'P1' else ('(' + num + ')')
        first = True
        for c in e:
            if tag(c) == 'Pnumber': continue
            if first and tag(c).endswith('para'):
                # first Text of the para goes on the label line
                kids = list(c)
                if kids and tag(kids[0]) == 'Text':
                    emit(prefix + lab + ' ' + inline(kids[0]), ind)
                    for k in kids[1:]: render(k, ind + 1, prefix)
                    first = False
                    continue
            if first: emit(prefix + lab, ind); first = False
            render(c, ind + 1, prefix)
        if first: emit(prefix + lab, ind)
        return
    if t == 'Text':
        s = inline(e)
        if s: emit(prefix + s, ind)
        return
    if t == 'BlockAmendment':
        for c in e: render(c, ind + 1, prefix + '> ')
        return
    if t == 'Tabular' or t == 'table':
        for row in e.iter():
            if tag(row) == 'tr':
                cells = [inline(c) for c in row if tag(c) in ('td', 'th')]
                emit(prefix + ' | '.join(cells), ind)
        return
    if t == 'Title':
        emit('## ' + inline(e), ind); return
    for c in e: render(c, ind, prefix)
root = ET.parse(sys.argv[1]).getroot()
for b in root.iter():
    if tag(b) in ('Body', 'Schedules'): render(b)
if '--notes' in sys.argv:
    out.append('\n---- commentary ----')
    for c in root.iter(NS + 'Commentary'):
        out.append('[' + c.get('id', '') + '] ' + inline(c))
print('\n'.join(out))
