import re, html, sys, os, glob
def txt(f):
    t = open(f, errors='replace').read()
    i = t.find('<main'); t = t[i:] if i > 0 else t
    t = re.sub(r'<(script|style)[^>]*>.*?</\1>', ' ', t, flags=re.S)
    t = re.sub(r'</(p|div|tr|li|h\d|table)>', '\n', t); t = re.sub(r'<t[dh][^>]*>', ' | ', t)
    t = re.sub(r'<[^>]+>', ' ', t); t = html.unescape(t)
    return '\n'.join(' '.join(l.split()) for l in t.splitlines() if l.strip())
if __name__ == '__main__':
    os.makedirs(os.path.expanduser(os.environ.get('IRS_AUDIT', '~/irs-audit') + '/irm/txt'), exist_ok=True)
    for f in glob.glob(os.path.expanduser(os.environ.get('IRS_AUDIT', '~/irs-audit') + '/cache/www.irs.gov/irm/part*/irm_*/index.html')) + glob.glob(os.path.expanduser(os.environ.get('IRS_AUDIT', '~/irs-audit') + '/cache/www.irs.gov/irm/part*/irm_*')):
        if os.path.isdir(f): continue
        name = f.split('/irm/')[1].replace('/index.html', '').replace('/', '__')
        out = os.path.expanduser(os.environ.get('IRS_AUDIT', '~/irs-audit') + '/irm/txt/' + name + '.txt')
        if not os.path.exists(out): open(out, 'w').write(txt(f))
