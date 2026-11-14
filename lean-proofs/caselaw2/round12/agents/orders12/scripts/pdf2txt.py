"""Convert PDFs to text (PyMuPDF), page breaks marked with a form feed line. Usage:
python -I pdf2txt.py <out_dir> <pdf> [<pdf> ...]   -> <out_dir>/<basename>.txt (UTF-8, LF)"""
import sys, os
import pymupdf


def main():
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    for p in sys.argv[2:]:
        doc = pymupdf.open(p)
        parts = []
        for i, pg in enumerate(doc):
            parts.append(pg.get_text('text', sort=False))
        doc.close()
        txt = '\n\f\n'.join(parts).replace('\r\n', '\n').replace('\r', '\n')
        name = os.path.splitext(os.path.basename(p))[0] + '.txt'
        with open(os.path.join(out, name), 'w', encoding='utf-8', newline='\n') as f:
            f.write(txt)
        print(name, len(parts), 'pages', len(txt), 'chars', flush=True)


if __name__ == '__main__':
    main()
