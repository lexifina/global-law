"""Step 6: read the effective-date and applicability provisions of a law for one amended US Code section, with the LLM.

    python s6_retro_llm.py <targets.tsv> [workers]
targets.tsv: key, law, usc (title:section(sub)), decision name, decided   (one row per law x amended section)
Writes statutes/llm/retro.jsonl (resumable: keys already there are skipped).

The packet: the law's approval date, the law sections that amend the US Code section (excerpts), and every passage of the
law that states an effective date or applicability (from lawinfo.jsonl), most specific first, capped at ~14k chars.
"""
import concurrent.futures as cf, json, os, re, sys, threading
sys.path.insert(0, os.path.dirname(__file__))
import common as C, llm
OUT = os.environ.get('RETRO_OUT', f'{C.S}/llm/retro.jsonl')
LI = {}
for l in open(f'{C.S}/lawinfo.jsonl', encoding='utf-8'):
    x = json.loads(l); LI[x['law']] = x
SCHEMA = {'type': 'object', 'properties': {
    'amending_section': {'type': 'string', 'description': 'law section that amends the US Code section, e.g. "sec. 3(a)"'},
    'effective_date': {'type': 'string', 'description': 'YYYY-MM-DD the amendment takes effect, or "" if not determinable'},
    'effective_basis': {'type': 'string', 'enum': ['statedDate', 'enactment', 'periodAfterEnactment', 'taxableYears', 'conductAfter', 'filedAfter', 'asIfEnacted', 'asIfIncluded', 'notStated', 'other']},
    'retro_class': {'type': 'string', 'enum': ['prospectiveOnly', 'appliesToPendingCases', 'retroactiveToDate', 'asIfIncluded', 'noProvision']},
    'retroactive_to': {'type': 'string', 'description': 'YYYY-MM-DD earliest conduct/claim date the amendment reaches when it reaches before enactment, else ""'},
    'applies_to_pending_cases': {'type': 'boolean'},
    'quote': {'type': 'string', 'description': 'the exact words of the law that decide it (<= 400 chars), or ""'},
    'confidence': {'type': 'string', 'enum': ['high', 'medium', 'low']},
    'note': {'type': 'string'}},
    'required': ['effective_date', 'effective_basis', 'retro_class', 'retroactive_to', 'applies_to_pending_cases', 'quote', 'confidence']}
SYS = """You read effective-date and applicability provisions of a US public law. For ONE amended US Code section, determine:
- effective_date: when the amendment to that section takes effect (YYYY-MM-DD). If the law says nothing, it takes effect on enactment (the approval date); use effective_basis "notStated".
- Tax laws name sections as "section N of the Internal Revenue Code of 1986" (= 26 U.S.C. N); other laws often name the amended Act's own section with the US Code cite in parentheses.
- retro_class:
  prospectiveOnly: any timing provision covering the amendment that sets a date at or after enactment: a stated or delayed effective date, or a limit to conduct, claims, cases, filings, sales or taxable years on or after such a date, or a statement that it does not apply to pending cases;
  appliesToPendingCases: the law says the amendment applies to cases/claims pending on (or after) enactment or some date, reaching conduct before enactment;
  retroactiveToDate: the law makes the amendment reach back to a date before enactment (e.g. "as if enacted on May 28, 2007", "shall apply to taxable years beginning after December 31, 2009" when enacted in 2010, conduct "before, on, or after" enactment);
  asIfIncluded: a technical/conforming correction that takes effect as if included in an earlier law (give that earlier law's date as retroactive_to if stated or inferable from the text);
  noProvision: no provision of the law covers the timing of this amendment (default rule: effective on enactment).
- retroactive_to: the earliest conduct or claim date the amendment reaches when earlier than enactment; for pending-case clauses without a date use the date the clause names, else "".
Only provisions that cover this section's amendment count (by "the amendments made by this section/subsection/title/Act" or by naming the amending section). Quote the deciding words exactly. Be literal; do not use outside knowledge."""

def packet(law, usc):
    x = LI.get(law)
    if not x or not x['secs']: return None
    t, s = usc.split(':')[0], re.sub(r'\(.*$', '', usc.split(':')[1])
    key = f'{t}:{s}'
    amend = [sc for sc in x['secs'] if key in sc['usc']]
    L = C.lines(law); Lc = C.clean(L)
    ex = []
    for m in re.finditer(r'\(' + re.escape(t) + r' U\.S\.C\. ?' + re.escape(s) + r'(?![\w\-])', Lc):
        ex.append(Lc[max(0, m.start() - 500):m.start() + 1500])
        if len(ex) >= 2: break
    if not ex:
        pat = r'[Ss]ection ' + re.escape(s) + r'(?:\([^)]*\))* of (?:title ' + re.escape(t) + r'\b' + (r'|the Internal Revenue Code of 1986' if t == '26' else '') + ')'
        for m in re.finditer(pat, Lc):
            ex.append(Lc[max(0, m.start() - 500):m.start() + 1500])
            if len(ex) >= 2: break
    ams = {sc['i'] for sc in amend}
    nums = {sc['num'] for sc in amend}
    divs = {sc['div'] for sc in amend}; titles = {sc['title'] for sc in amend}
    def rank(e):
        if e['sec_i'] in ams: return 0
        if e['scope'].startswith('secs:') and nums & set(e['scope'][5:].split(',')): return 1
        if e['scope'] == 'title' and e['title'] in titles: return 2
        if e['scope'] == 'act': return 3
        if re.search(r'[Ss]ections? ' + re.escape(s) + r'(?![\w\-])', e['text']): return 1
        if e['div'] in divs and e['kind']: return 4
        if not amend and e['kind']: return 5
        return 9
    effs = sorted((e for e in x['eff'] if rank(e) < 9 or len(x['eff']) <= 12), key=lambda e: (rank(e), e['id']))
    body, n = [], 0
    for e in effs:
        s_ = f"[law sec. {e['sec']}{(' ' + e['div']) if e['div'] else ''}{(' ' + e['title']) if e['title'] else ''}] {e['text'][:2500]}"
        if n + len(s_) > 14000: break
        body.append(s_); n += len(s_)
    return dict(enacted=x['enacted'], amend=[f"sec. {sc['num']} {sc['head']}" for sc in amend][:8], ex=ex, eff=body)

def one(row):
    key, law, usc, dname, decided = row
    p = packet(law, usc)
    if p is None:
        return dict(key=key, law=law, usc=usc, err='no law text')
    e = p['enacted']
    user = (f"Law: {law}, approved {e // 10000}-{e // 100 % 100:02d}-{e % 100:02d}.\n"
            f"Amended US Code section: {usc.replace(':', ' U.S.C. ')}\n"
            f"Law sections that amend it: {'; '.join(p['amend']) or 'not located'}\n\n"
            f"Where the law amends it (excerpts):\n" + '\n[...]\n'.join(p['ex'])[:4000] +
            "\n\nEvery passage of the law on effective dates or applicability that may cover it (most specific first):\n" +
            '\n\n'.join(p['eff']) + ('\n(none found)' if not p['eff'] else ''))
    r, model = llm.chat([{'role': 'system', 'content': SYS}, {'role': 'user', 'content': user}], SCHEMA, name='retro', max_out=1200, tag='retro')
    return dict(key=key, law=law, usc=usc, enacted=e, model=model, packet_chars=len(user), **r)

if __name__ == '__main__':
    rows = [l.rstrip('\n').split('\t') for l in open(sys.argv[1], encoding='utf-8') if l.strip()]
    done = set()
    if os.path.exists(OUT):
        done = {json.loads(l)['key'] for l in open(OUT, encoding='utf-8')}
    todo = [r for r in rows if r[0] not in done]
    print('todo', len(todo), 'done', len(done), flush=True)
    lk = threading.Lock()
    with cf.ThreadPoolExecutor(int(sys.argv[2]) if len(sys.argv) > 2 else 4) as ex:
        def safe(row):
            try:
                return one(row)
            except Exception as e:
                return dict(key=row[0], law=row[1], usc=row[2], err=str(e)[:300])
        futs = [ex.submit(safe, r) for r in todo]
        for f in cf.as_completed(futs):
            res = f.result()
            with lk, open(OUT, 'a', encoding='utf-8', newline='\n') as fo:
                fo.write(json.dumps(res, ensure_ascii=False) + '\n')
    print('done', llm._total[0], 'tokens total', flush=True)
