"""Glyph-aware PDF -> text (PyMuPDF), same layout as pdf2txt.py (page break = a form-feed line).

Some Journal PDFs (OT2017-OT2025) embed Type1 fonts whose /Encoding /Differences name code 174 /fi and 175 /fl
(the ligature glyphs that are drawn), but whose /ToUnicode CMap maps those codes to "f" alone, so every extractor
that trusts ToUnicode prints "affrmed", "fle", "Offce". Repair (in memory only, the PDF file is not changed): for every
font dict with both an /Encoding /Differences array and a /ToUnicode CMap, each code whose glyph name is a ligature
(ff, fi, fl, ffi, ffl) and whose ToUnicode bfchar target is not that ligature (U+FB00-FB04) or its letters is
remapped to the ligature code point. Then the text is extracted exactly as pdf2txt.py does, so line numbers are the
same as an unrepaired extraction (a ligature is one character either way).

Usage: python -I pdf2txt_lig.py <out_dir> <report.tsv> <pdf> [<pdf> ...]
Writes <out_dir>/<basename>.txt and appends to report.tsv: pdf, font xref, tounicode xref, code, glyph name, old
target, new target.
"""
import sys, os, re
import pymupdf

LIG = {'ff': 'FB00', 'fi': 'FB01', 'fl': 'FB02', 'ffi': 'FB03', 'ffl': 'FB04'}
OK_TARGETS = {n: {LIG[n], ''.join('%04X' % ord(c) for c in n)} for n in LIG}


def differences(doc, fx):
    t = doc.xref_get_key(fx, 'Encoding')
    if t[0] == 'xref':
        obj = doc.xref_object(int(t[1].split()[0]))
    elif t[0] == 'dict':
        obj = t[1]
    else:
        return {}
    m = re.search(r'/Differences\s*\[(.*?)\]', obj, re.S)
    if not m:
        return {}
    out, code = {}, None
    for tok in re.findall(r'\d+|/[^\s/\[\]]+', m.group(1)):
        if tok.startswith('/'):
            if code is not None:
                out[code] = tok[1:]
                code += 1
        else:
            code = int(tok)
    return out


def fix_doc(doc, pdfname, report):
    changes = {}  # tounicode xref -> {code_hex: new_target}
    for x in range(1, doc.xref_length()):
        try:
            if doc.xref_get_key(x, 'Type') != ('name', '/Font'):
                continue
        except Exception:
            continue
        diffs = differences(doc, x)
        ligcodes = {c: n for c, n in diffs.items() if n in LIG}
        if not ligcodes:
            continue
        t = doc.xref_get_key(x, 'ToUnicode')
        if t[0] != 'xref':
            continue
        tx = int(t[1].split()[0])
        s = doc.xref_stream(tx).decode('latin-1')
        for code, name in ligcodes.items():
            for m in re.finditer(r'<(%02X)>\s*<([0-9A-Fa-f]+)>' % code, s):
                tgt = m.group(2).upper()
                if tgt not in OK_TARGETS[name]:
                    prev = changes.setdefault(tx, {}).get(m.group(1))
                    if prev and prev != LIG[name]:
                        raise SystemExit('conflicting ligature names for shared ToUnicode %d code %s' % (tx, m.group(1)))
                    changes[tx][m.group(1)] = LIG[name]
                    report.append([pdfname, str(x), str(tx), m.group(1), name, tgt, LIG[name]])
    for tx, ch in changes.items():
        s = doc.xref_stream(tx).decode('latin-1')
        for code, new in ch.items():
            s = re.sub(r'<%s>(\s*)<[0-9A-Fa-f]+>' % code, lambda m: '<%s>%s<%s>' % (code, m.group(1), new), s)
        doc.update_stream(tx, s.encode('latin-1'))
    return len(changes)


def main():
    out, rep = sys.argv[1], sys.argv[2]
    os.makedirs(out, exist_ok=True)
    for p in sys.argv[3:]:
        doc = pymupdf.open(p)
        report = []
        n = fix_doc(doc, os.path.basename(p), report)
        # re-open from the edited bytes so the text extraction sees the new CMaps
        data = doc.tobytes()
        doc.close()
        doc = pymupdf.open(stream=data, filetype='pdf')
        parts = [pg.get_text('text', sort=False) for pg in doc]
        npages = len(parts)
        doc.close()
        txt = '\n\f\n'.join(parts).replace('\r\n', '\n').replace('\r', '\n')
        name = os.path.splitext(os.path.basename(p))[0] + '.txt'
        with open(os.path.join(out, name), 'w', encoding='utf-8', newline='\n') as f:
            f.write(txt)
        with open(rep, 'a', encoding='utf-8', newline='\n') as f:
            for r in report:
                f.write('\t'.join(r) + '\n')
        print(name, npages, 'pages', len(txt), 'chars;', n, 'ToUnicode maps fixed,', len(report), 'codes', flush=True)


if __name__ == '__main__':
    main()
