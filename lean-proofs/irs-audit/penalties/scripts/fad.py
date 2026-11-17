"""Final adverse determinations (exemption denials and revocations) among the harvested IRS written determinations:
count, year, kind, stated grounds, and any section 6033(j) (three consecutive years not filing) trigger."""
import os, re, json, collections, glob
T = os.path.expanduser(os.environ.get('IRS_AUDIT', '~/irs-audit') + '/wd/text')
fs = sorted(glob.glob(T + '/irs-wd__*.txt'))
fl = lambda s: re.sub(r'\s+', ' ', s)
FINAL = re.compile(r"final adverse determination|final determination that you do(?:n.t| not) qualify|final revocation|this is a final determination|our final determination", re.I)
REV = re.compile(r"(?:determination letter|exempt status|exemption)[^.]{0,80}(?:is|are|is hereby) revoked|we (?:are )?revok|revocation of your (?:tax.)?exempt", re.I)
GROUNDS = {
 'failed_to_establish_or_respond': r"(?:failed|did not|didn.t|have not|has not)\s+(?:to\s+)?(?:respond|establish|demonstrate|provide (?:the )?(?:requested )?information|show)|not established",
 'inurement_private_benefit': r"inure|inurement|private benefit|private shareholder|insider",
 'not_exclusively_exempt_purpose': r"not (?:organized and )?operated exclusively|substantial non.?exempt|more than an insubstantial|substantial part of your activities",
 'organizational_test': r"organizational test|articles of (?:incorporation|organization)[^.]{0,80}(?:do not|don.t|fail)|dissolution clause",
 'records_or_returns_not_filed': r"(?:failed|fail|did not|didn.t) (?:to )?(?:file|keep|maintain|produce)[^.]{0,60}(?:return|form 990|records|books)|section 6001|section 6033",
 'political_or_lobbying': r"political campaign|intervene|lobbying|influenc(?:e|ing) legislation",
 'commercial_or_business': r"commercial|trade or business|unrelated business",
 'social_club_tests': r"non.?member income|501\(c\)\(7\)",
 'down_payment_or_credit_counseling': r"down payment assistance|credit counseling",
 'conservation_easement_or_tax_shelter': r"conservation easement|tax shelter|abusive",
}
GR = {k: re.compile(v, re.I) for k, v in GROUNDS.items()}
out = []; c = collections.Counter(); g = collections.Counter(); yr = collections.Counter(); s6033j = []
for f in fs:
    t = open(f, errors='ignore').read()
    if len(t.strip()) < 200: continue
    head = fl(t[:5000])
    if not (FINAL.search(head) or (REV.search(head) and re.search(r'50[1-9]\s?\(c\)', head))): continue
    # skip private letter rulings that merely discuss revocation
    if re.search(r'ruling request|requested rulings?|this letter responds to your (?:request|letter)', head, re.I) and not FINAL.search(head): continue
    num = re.search(r'irs-wd__(\d+)', f).group(1)
    year = ('20' + num[:2]) if len(num) == 7 else num[:4]
    kind = 'revocation' if REV.search(fl(t[:8000])) else 'denial'
    body = fl(t)
    grounds = [k for k, r in GR.items() if r.search(body)]
    m = re.search(r"6033\(j\)|three consecutive (?:years|tax years)|3 consecutive years", body, re.I)
    if m: s6033j.append((num, fl(body[max(0, m.start()-300):m.end()+300])))
    sec = re.findall(r"501\s?\(c\)\s?\((\d+|n)\)", head)
    out.append(dict(num=num, year=year, kind=kind, grounds=grounds, sections=sorted(set(sec))))
    c[kind] += 1; yr[year] += 1
    for k in grounds: g[k] += 1
json.dump(out, open(os.path.expanduser(os.environ.get('IRS_AUDIT', '~/irs-audit') + '/penalties/data/fad.json'), 'w'), indent=0)
print('final adverse determinations', len(out), dict(c))
print('by year', sorted(yr.items()))
print('grounds', g.most_common())
print('section', collections.Counter(s for o in out for s in o['sections']).most_common(8))
print('6033(j)/three-consecutive-years mentions', len(s6033j))
json.dump(s6033j, open(os.path.expanduser(os.environ.get('IRS_AUDIT', '~/irs-audit') + '/penalties/data/fad_6033j.json'), 'w'), indent=0)
for n, s in s6033j[:6]: print('--', n, s[:600])
