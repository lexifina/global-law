"""Totality and content checks for the six restatements in the record.

    python tools/analyze.py

Reads data/dispo_rows.tsv (from parse_tables.py) and the record (usc-full.git). Writes
  data/old_provisions.tsv  one row per old provision: title, source title, section, status, reason, images,
                           images found in the record (0/1), vanished from the record by the next edition (0/1)
  data/app_rows.tsv        46 App. (and 40 App.) rows: the record does not hold the Appendix, so listed, not checked
  data/pairs.tsv           content check of each mapped old section with text in the record
  data/rows_unparsed.tsv   table rows whose cells the grammar did not read
  data/summary.json
  data/lean/<title>.tsv    input to the Lean runner
"""
import json, os, re, sys, datetime, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from recod import *

NEW_TITLE_FROM = {51: 20120103, 54: 20150105}  # first record commit holding the restated title
NEW_HTML = {36: 'USCODE-1998-title36.htm', 40: 'USCODE-2002-title40.htm', 46: 'USCODE-2006-title46.htm',
            51: 'USCODE-2011-title51.htm', 41: 'USCODE-2011-title41.htm', 54: 'USCODE-2014-title54.htm'}


def html_text(fn):
    import html as H
    t = open(os.path.join(BASE, 'cache', fn), encoding='utf-8').read()
    t = re.sub(r'[\x00-\x1f]?g025', '', t)
    t = re.sub(r'</?(em|i|sup)>', '', t)
    return re.sub(r'\s+', ' ', H.unescape(re.sub(r'<[^>]+>', ' ', t))).replace('–', '-').replace('—', '-')


def prior_note(newtext, s, law):
    """The new title's 'Prior Provisions' note for a positive-law section the restatement rewrote: "A prior section
    12110 ... prior to being omitted in the general amendment of this chapter by Pub. L. 109-304. See section 12114"."""
    m = re.search(rf'\[§{re.escape(s)}\. Repealed\. {re.escape(law)}, ([^\]]*)\] (.{{0,600}}?)(?=§\d|\[§|$)', newtext)
    if m:
        see = re.search(r'See (sections?) ([^.]*?) of this title', m.group(2))
        what = re.search(r'related to ([^.]+)', m.group(2))
        return ('repealed by ' + m.group(1).split(',')[0] + '; ' + ('related to ' + what.group(1) + '; ' if what else '')
                + ('see ' + see.group(2) if see else 'no successor named') + ' (repeal note)')
    for m in re.finditer(rf'A prior section {re.escape(s)}\b', newtext):
        seg = newtext[m.start(): m.start() + 2500]
        seg = seg[: (seg.find('A prior section', 10) if seg.find('A prior section', 10) > 0 else len(seg))]
        if law in seg:
            see = re.search(r'See (sections?|section) ([^.]*?) of this title', seg)
            what = re.search(r'related to ([^,]+)', seg)
            return ('related to ' + what.group(1) + '; ' if what else '') + (
                'see ' + see.group(2) if see else 'no successor named') + f' (Prior Provisions note, {law})'
    return None


def day_before(d):
    x = datetime.date(d // 10000, d // 100 % 100, d % 100) - datetime.timedelta(days=1)
    return int(x.strftime('%Y%m%d'))


def next_edition(t, d):
    for s, dd, a, sub in title_log(t):
        if dd > d and 'edition' in a:
            return s, dd
    return None, None


def law_deletions(t, d0, d1):
    """Sections of title t deleted by a law commit with day in (d0, d1]."""
    out = {}
    for s, dd, a, sub in title_log(t):
        if d0 < dd <= d1 and 'edition' not in a:
            for l in git('show', '--format=', '--name-status', s, '--', f'title-{t}/').splitlines():
                st, p = l.split('\t')[:2]
                if st == 'D' or (st == 'M' and PLACEHOLDER.match(git('show', f'{s}:{p}'))):
                    out[p.split('/', 1)[1][:-3]] = a
    return out


def main():
    rows = [l.rstrip('\n').split('\t') for l in open(os.path.join(DATA, 'dispo_rows.tsv'), encoding='utf-8')]
    rows += [l.rstrip('\n').split('\t') for l in open(os.path.join(DATA, 'transfers.tsv'), encoding='utf-8')]
    blobs = Blobs()
    out_old, out_pairs, out_app, out_unp, out_unrel, summary = [], [], [], [], [], {}
    lean_dir = os.path.join(DATA, 'lean')
    os.makedirs(lean_dir, exist_ok=True)
    for T, law, D in RESTATEMENTS:
        prev = day_before(D)
        newtext = html_text(NEW_HTML[T])
        law_dash = law.replace('-', '–')
        trows = [r for r in rows if int(r[0]) == T]
        old = {}
        def known(src, s):
            if src.endswith('A'):
                return False
            st = int(src)
            if st not in old:
                old[st] = in_force(st, commit_on(st, prev))
            return s in old[st]
        parsed = []
        for r in trows:
            src, kind, items = parse_left(r[3], int(r[1]), known)
            if T == 46 and not (kind == 'note' and items and items[0][0] == 'one' and known('46', items[0][1])):
                src = '46A'
            disp = parse_right(r[4], T)
            parsed.append((src, kind, items, disp, r[3], r[4], r[2]))
            if not items or disp[0] == 'unknown':
                out_unp.append((T, r[3], r[4]))
        srcs = sorted({p[0] for p in parsed if not p[0].endswith('A')}, key=int)
        full = [T] if T in (36, 40, 41, 46) else []
        extra = [49] if T == 51 else []
        new_commit = commit_on(T, max(D, NEW_TITLE_FROM.get(T, D)))
        new_secs = in_force(T, new_commit)
        new_day = max(D, NEW_TITLE_FROM.get(T, D))
        if T not in NEW_TITLE_FROM:
            # on the restatement day the record still holds the old files until the next edition; the new title is
            # what the restating law wrote that day plus whatever survives into the next edition
            touched = set()
            for c, dd, a, sub in title_log(T):
                if dd == D and a.startswith(law + ' ') or a == law:
                    if dd == D:
                        touched |= {l.split('\t')[1].split('/', 1)[1][:-3] for l in
                                    git('show', '--format=', '--name-status', c, '--', f'title-{T}/').splitlines()
                                    if l and l[0] in 'AM'}
            ecT, _ = next_edition(T, D)
            survive = in_force(T, ecT) if ecT else {}
            new_secs = {s: b for s, b in new_secs.items() if s in touched or s in survive}
        info = {'law': law, 'day': D, 'new_title_commit': new_commit, 'new_title_day': new_day,
                'new_title_sections': len(new_secs), 'table_rows': len(trows), 'sources': {}}
        oldset = {}  # (src, sec) -> vanished flag
        for S in sorted(set(int(s) for s in srcs) | set(full) | set(extra)):
            bc = commit_on(S, prev)
            before = in_force(S, bc)
            old[S] = before
            ec, ed = next_edition(S, D)
            after = in_force(S, ec) if ec else {}
            dels = law_deletions(S, D, ed or D)
            named = set()
            for src, kind, items, disp, l, rr, cap in parsed:
                if src != str(S) or kind != 'sec':
                    continue
                for it in items:
                    if it[0] == 'one':
                        if it[1] in before:
                            named.add(it[1])
                    else:
                        named |= {s for s in before if in_range(s, it[1], it[2])}
            vanished_all = {s for s in before if s not in after}
            if S == T and T in (36, 40, 41, 46):
                cand = set(before)
                unrelated = set()
            else:
                # a section of another title that left the record by the next edition belongs to this restatement
                # only if the tables, the transfer credits, the new title's text and notes (Historical and
                # Revision Notes cite sources as "42:2451"), or its own repeal placeholder name it or the law
                def related(s):
                    if s in named:
                        return True
                    if re.search(rf'(?<![\w-]){S}:{re.escape(s)}(?![\w-])|section {re.escape(s)} of (former )?'
                                 rf'title {S}\b|{S} U\.S\.C\. {re.escape(s)}(?![\w-])', newtext):
                        return True
                    ph = sections(S, ec).get(s) if ec else None
                    return bool(ph and law_dash in blob_text(ph).split('\n')[0])
                cand = named | {s for s in vanished_all if related(s)}
                unrelated = vanished_all - cand
            for s in cand:
                oldset[(S, s)] = (s not in after, dels.get(s))
            for s in sorted(unrelated, key=skey):
                out_unrel.append((T, S, s, dels.get(s, ''), blob_text(before[s]).split('\n')[0][2:120]))
            info['sources'][S] = {'before_commit': bc, 'sections_before': len(before), 'next_edition': ec,
                                  'next_edition_day': ed, 'vanished': len(vanished_all),
                                  'vanished_unrelated': len(unrelated),
                                  'named_in_table': len(named), 'old_provisions': len(cand)}
        # covering rows per old provision
        by_src = collections.defaultdict(list)
        for p in parsed:
            by_src[p[0]].append(p)
        def covering(S, s):
            res = []
            for p in by_src.get(str(S), []):
                if p[1] != 'sec':
                    continue
                for it in p[2]:
                    if (it[0] == 'one' and it[1] == s) or (it[0] == 'range' and in_range(s, it[1], it[2])):
                        res.append(p)
                        break
            return res
        def resolve(disp, S, depth=0):
            if disp[0] == 'see_former' and depth < 3:
                rs = covering(S, disp[1])
                return [d for p in rs for d in resolve(p[3], S, depth + 1)] or [('omit', 'see former ' + disp[1])]
            return [disp]
        other_titles = {}
        def tree_of(tt):
            if tt not in other_titles:
                other_titles[tt] = new_secs if tt == T else in_force(tt, commit_on(tt, new_day))
            return other_titles[tt]
        def expand(tt, target):
            secs = tree_of(tt)
            if not isinstance(target, tuple) and target not in secs and '-' in target:
                a, b = target.rsplit('-', 1)
                if a in secs and b in secs:  # "T. 4 §§4-10" is a range, not a hyphenated section
                    target = ('range', a, b)
            if isinstance(target, tuple):
                return sorted((s for s in secs if in_range(s, target[1], target[2])), key=skey), True
            return [target], target in secs
        ed_trees = {}
        edT_day = max(new_day, min(v['next_edition_day'] or 99999999 for v in info['sources'].values()))
        def ed_tree(tt):
            if tt not in ed_trees:
                ed_trees[tt] = in_force(tt, commit_on(tt, edT_day))
            return ed_trees[tt]
        counts = collections.Counter()
        lean_rows = []
        for (S, s), (vanished, deleted_by) in sorted(oldset.items(), key=lambda x: (x[0][0], skey(x[0][1]))):
            cov = covering(S, s)
            disps = []
            for p in cov:
                for d in resolve(p[3], S):
                    # "16723 to 16725 => 40113 to 40115": pair the two ranges in order when they are the same length
                    if (d[0] == 'map' and len(p[2]) == 1 and p[2][0][0] == 'range' and len(d[1]) == 1
                            and isinstance(d[1][0][1], tuple) and not d[1][0][2]):
                        lefts = sorted((x for x in old.get(S, {}) if in_range(x, p[2][0][1], p[2][0][2])), key=skey)
                        rights, _ = expand(d[1][0][0], d[1][0][1])
                        if len(lefts) == len(rights) and s in lefts:
                            d = ('map', [(d[1][0][0], rights[lefts.index(s)], False)])
                    disps.append(d)
            images, notes, reasons, other = [], [], [], []
            for d in disps:
                if d[0] == 'map':
                    for tt, tg, isnote in d[1]:
                        if isnote:
                            notes.append(f'{tt}:{tg if isinstance(tg, str) else tg[1] + "-" + tg[2]} note')
                        else:
                            images.append((tt, tg))
                elif d[0] == 'omit':
                    reasons.append(d[1])
                elif d[0] == 'act':
                    other.append(d[1])
                else:
                    other.append('unread: ' + d[1])
            img_ids, img_ok = [], True
            for tt, tg in images:
                ids, ok = expand(tt, tg)
                img_ok &= ok and bool(ids)
                img_ids += [f'{tt}:{i}' for i in ids]
            img_ids = list(dict.fromkeys(img_ids))
            if img_ids:
                status = 'transferred' if any(p[6].startswith('credits') for p in cov) else 'mapped'
            elif notes:
                status = 'note'
            elif reasons or other:
                status = 'omitted'
            elif S == 46 and not vanished:
                status = 'kept'  # positive-law title 46 section left in place
                img_ids, img_ok = [f'46:{s}'], s in new_secs
            elif deleted_by:
                status = 'other_law'
            elif S == T and prior_note(newtext, s, law):
                status = 'prior_note'
            elif not vanished and S == T:
                status = 'unaccounted_still_printed'
            else:
                status = 'unaccounted'
            reason = '; '.join(dict.fromkeys(reasons + other + notes))
            if status == 'prior_note':
                reason = prior_note(newtext, s, law)
            if status == 'kept':
                reason = 'positive-law section kept at its number'
            if status == 'other_law':
                reason = 'deleted by ' + deleted_by
            counts[status] += 1
            out_old.append((T, S, s, status, reason, ' '.join(img_ids), int(img_ok) if img_ids else '',
                            int(vanished), len(cov)))
            # Lean rows: the old provision, and its official disposition if any
            oid = f'{S}:{s}'
            lean_rows.append(f'O\t{oid}')
            if img_ids:
                lean_rows.append(f'M\t{oid}\t' + ','.join(img_ids))
            elif status in ('omitted', 'note'):
                lean_rows.append(f'X\t{oid}\t{reason}')
            elif status in ('other_law', 'prior_note'):
                lean_rows.append(f'E\t{oid}\t{reason}')
            # content check
            if status == 'mapped' and s in old.get(S, {}):
                otext = body(blobs.get(old[S][s]))
                ntext = ''
                found = 0
                for i in img_ids:
                    tt, sec = i.split(':', 1)
                    # the words of the new section as the first edition after the restatement prints them: on the
                    # restatement day the record can still hold an old section at a colliding number
                    tr = ed_tree(int(tt))
                    if sec in tr:
                        ntext += '\n' + body(blobs.get(tr[sec]))
                        found += 1
                if not found:
                    continue
                ow, nw = words(otext), words(ntext)
                on, nn = numbers(otext), numbers(ntext)
                nvals = {v for (c, v) in nn}
                lost = sorted({(c, v) for (c, v) in on if v not in nvals})
                onames, nnames = name_tokens(otext), name_tokens(ntext)
                lost_names = sorted(onames - nnames - nw)
                cover = len(ow & nw) / len(ow) if ow else 1.0
                out_pairs.append((T, S, s, ' '.join(img_ids), len(otext), len(ntext), len(ow), round(cover, 3),
                                  len(on), len(lost), ' '.join(f'{c}:{v}' for c, v in lost),
                                  len(onames), ' '.join(lost_names[:20]), len(set(on))))
        # Appendix rows: not in the record
        app_lines, app_seen = [], {}
        for src, kind, items, disp, l, rr, cap in parsed:
            if src.endswith('A'):
                ds = resolve(disp, src)
                out_app.append((T, src, l, rr, ds[0][0] if ds else 'unknown'))
                if kind != 'sec':
                    continue
                # the Appendix is not in the record: its provisions are only those the table names (a range
                # counts once), so totality is by construction; what Lean checks is that the images exist
                imgs = []
                for d in ds:
                    if d[0] == 'map':
                        for tt, tg, isnote in d[1]:
                            if not isnote:
                                ids, ok = expand(tt, tg)
                                imgs += [f'{tt}:{i}' for i in ids]
                for it in items:
                    oid = f'{src}:{it[1]}' if it[0] == 'one' else f'{src}:{it[1]}-{it[2]}'
                    e = app_seen.setdefault(oid, ([], []))
                    e[0].extend(imgs)
                    for d in ds:
                        if d[0] in ('omit', 'act'):
                            e[1].append(str(d[1]))
                        elif d[0] == 'map' and all(x[2] for x in d[1]):
                            e[1].append('kept as a note')
        app_seen = app_seen if isinstance(app_seen, dict) else {}
        for oid, (imgs, reasons) in app_seen.items():
            app_lines.append(f'O\t{oid}')
            if imgs:
                app_lines.append(f'M\t{oid}\t' + ','.join(dict.fromkeys(imgs)))
            elif reasons:
                app_lines.append(f'X\t{oid}\t{reasons[0]}')
        if app_lines:
            with open(os.path.join(lean_dir, f'{T}A.tsv'), 'w', newline='\n', encoding='utf-8') as f:
                for r in app_lines:
                    f.write(r + '\n')
                for tt, tr in sorted(other_titles.items()):
                    for s in sorted(tr, key=skey):
                        f.write(f'N\t{tt}:{s}\n')
        info['status_counts'] = dict(counts)
        # one file per title: O old provision, M mapped (images), X omitted (reason), E explained by the record
        # (another law), N a provision in force once the restatement took effect
        with open(os.path.join(lean_dir, f'{T}.tsv'), 'w', newline='\n', encoding='utf-8') as f:
            for r in lean_rows:
                f.write(r + '\n')
            for s in sorted(new_secs, key=skey):
                f.write(f'N\t{T}:{s}\n')
            for tt, tr in sorted(other_titles.items()):
                if tt != T:
                    for s in sorted(tr, key=skey):
                        f.write(f'N\t{tt}:{s}\n')
        # the same check against what is in force at the first edition after the restatement
        with open(os.path.join(lean_dir, f'{T}.ed.tsv'), 'w', newline='\n', encoding='utf-8') as f:
            for r in lean_rows:
                f.write(r + '\n')
            for tt in sorted(set(other_titles) | {T}):
                edT = max(new_day, min(v['next_edition_day'] or 99999999 for v in info['sources'].values()))
                ec = commit_on(tt, edT)
                info.setdefault('edition_for_images', {})[tt] = edT
                for s in sorted(in_force(tt, ec) if ec else {}, key=skey):
                    f.write(f'N\t{tt}:{s}\n')
        summary[T] = info
        print(T, law, json.dumps(info['status_counts']), flush=True)
    def w(name, rows, head):
        with open(os.path.join(DATA, name), 'w', newline='\n', encoding='utf-8') as f:
            f.write('\t'.join(head) + '\n')
            for r in rows:
                f.write('\t'.join(map(str, r)) + '\n')
    w('old_provisions.tsv', out_old, ['title', 'src', 'section', 'status', 'reason', 'images', 'images_in_record',
                                      'vanished_by_next_edition', 'table_rows'])
    w('pairs.tsv', out_pairs, ['title', 'src', 'section', 'images', 'old_chars', 'new_chars', 'old_words',
                               'word_coverage', 'old_numbers', 'numbers_lost', 'lost', 'old_names', 'lost_names',
                               'old_number_types'])
    w('app_rows.tsv', out_app, ['title', 'src', 'left', 'right', 'disposition'])
    w('rows_unparsed.tsv', out_unp, ['title', 'left', 'right'])
    w('vanished_unrelated.tsv', out_unrel, ['title', 'src', 'section', 'deleted_by_law', 'heading_before'])
    json.dump(summary, open(os.path.join(DATA, 'summary.json'), 'w', newline='\n'), indent=1)


if __name__ == '__main__':
    main()
