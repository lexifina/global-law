"""GOV.UK content-API JSON -> text (body HTML stripped). usage: python3 -I govuk2txt.py file.json"""
import sys, json, re, html
d = json.load(open(sys.argv[1], encoding='utf-8'))
out = [d.get('title', ''), d.get('base_path', ''), 'updated: ' + str(d.get('public_updated_at', ''))]
det = d.get('details', {})
def strip(h):
    h = re.sub(r'<(br|/p|/li|/h\d|/tr|/div)[^>]*>', '\n', h)
    h = re.sub(r'<(td|th)[^>]*>', ' | ', h)
    h = re.sub(r'<[^>]+>', '', h)
    return re.sub(r'\n\s*\n+', '\n', html.unescape(h))
if 'body' in det:
    b = det['body']
    if isinstance(b, list): b = ' '.join(x.get('content', '') for x in b if isinstance(x, dict))
    out.append(strip(b))
for p in det.get('parts', []):
    out.append('## PART ' + p.get('title', '') + ' (' + p.get('slug', '') + ')')
    b = p.get('body', '')
    if isinstance(b, list): b = ' '.join(x.get('content', '') for x in b if isinstance(x, dict))
    out.append(strip(b))
for s in det.get('child_section_groups', []) or []:
    for c in s.get('child_sections', []):
        out.append('- ' + c.get('section_id', '') + ' ' + c.get('title', '') + ' ' + c.get('base_path', ''))
print('\n'.join(out))
