"""Checks on the global law tree. Run from the repo root after `git submodule update --init`:

  python -m unittest discover -s tests -v
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.dont_write_bytecode = True  # never leave cache files inside a corpus checkout (it blocks git checkout)
sys.path.insert(0, str(ROOT / 'tools'))
import law  # noqa: E402

USC = 'united-states/federal/usc/title-11/1182.md'
# Germany is found by country code, in whichever layout is pinned: the Grundgesetz alone (…/grundgesetz/artikel/) or
# all federal law (…/acts/grundgesetz/artikel/, with every other act beside it).
DE = next(c['path'] for c in law.manifest()['corpora'] if c.get('code') == 'DE')
GG = (DE if DE.endswith('/grundgesetz') else f'{DE}/grundgesetz') + '/artikel/{}.md'
SEND = 'united-kingdom/uk/legislation/uksi/2014/1530/regulation/13.md'


class Structure(unittest.TestCase):
    def test_every_level_describes_itself_and_its_children(self):
        tree = json.loads((ROOT / 'jurisdiction.json').read_text(encoding='utf-8'))
        stack = [('', tree)]
        seen = set()
        while stack:
            path, node = stack.pop()
            seen.add(path)
            for child in node['jurisdictions']:
                self.assertEqual(child.rsplit('/', 1)[0] if '/' in child else '', path)
                stack.append((child, json.loads((ROOT / child / 'jurisdiction.json').read_text(encoding='utf-8'))))
            for corpus in node['corpora']:
                self.assertTrue((ROOT / corpus / '.git').exists(), f'{corpus} is not checked out')
        corpora = {c['path'] for c in law.manifest()['corpora']}
        self.assertTrue(all(c.rsplit('/', 1)[0] in seen for c in corpora))

    def test_head_pins_each_corpus_at_its_latest_commit(self):
        events = law.timeline()  # once: with thousands of root commits, parsing it per corpus is the slow part
        last = {e.corpus: e.corpus_commit for e in events}
        pins = head_pins()
        for corpus in law.manifest()['corpora']:
            self.assertEqual(pins.get(corpus['path']), last[corpus['path']], corpus['path'])


def head_pins(commit: str = 'HEAD') -> dict[str, str]:
    """Every gitlink in one tree, in one git call."""
    out = {}
    for line in law.git('ls-tree', '-r', commit).splitlines():
        meta, path = line.split('\t', 1)
        mode, kind, sha = meta.split()
        if kind == 'commit':
            out[path] = sha
    return out


def pin_moves() -> list[tuple[str, dict[str, str]]]:
    """(root commit, {path: new gitlink}) for every first-parent root commit, from one `git log --raw`."""
    raw = law.git('log', '--first-parent', '--reverse', '--raw', '--no-abbrev', '--no-renames', '--format=@@%H')
    out: list[tuple[str, dict[str, str]]] = []
    for line in raw.splitlines():
        if line.startswith('@@'):
            out.append((line[2:], {}))
        elif line.startswith(':') and out:
            meta, path = line.split('\t', 1)
            _, new_mode, _, new_sha, _ = meta[1:].split()
            if new_mode == '160000':
                out[-1][1][path] = new_sha
    return out


class Timeline(unittest.TestCase):
    events = law.timeline()

    def test_in_force_order(self):
        dates = [e.in_force for e in self.events]
        self.assertEqual(dates, sorted(dates))

    def test_one_root_commit_per_corpus_commit(self):
        for corpus in law.manifest()['corpora']:
            path = ROOT / corpus['path']
            leaf = law.git('rev-list', '--first-parent', '--reverse', 'HEAD', cwd=path).split()
            ours = [e.corpus_commit for e in self.events if e.corpus == corpus['path']]
            self.assertEqual(ours, leaf, corpus['path'])

    def test_each_root_commit_moves_exactly_one_pin(self):
        # One `git log --raw` instead of a git call per commit per corpus (thousands of root commits since Malta).
        moves = dict(pin_moves())
        for event in self.events:
            self.assertEqual(moves.get(event.commit), {event.corpus: event.corpus_commit}, event.subject)
        law_commits = {e.commit for e in self.events}
        for commit, moved in moves.items():
            if commit not in law_commits:
                self.assertEqual(moved, {}, f'{commit[:7]} moves a pin but carries no Corpus trailer')

    def test_commit_dates_never_go_backwards(self):
        stamps = [int(s) for s in law.git('log', '--first-parent', '--reverse', '--format=%at').split()]
        self.assertEqual(stamps, sorted(stamps))


class OnADate(unittest.TestCase):
    def test_before_the_record_nothing_is_in_force(self):
        # Before the earliest record in the tree (Malta's starts in 1834) no corpus is pinned; and a record that
        # starts later is simply absent on earlier dates.
        first = min(e.in_force for e in law.timeline())
        self.assertIsNone(law.root_on(f'{int(first[:4]) - 1}-12-31'))
        self.assertIsNone(law.text_on('1949-05-23', GG.format('001')))
        self.assertIsNone(law.text_on('2017-12-31', USC))

    def test_us_small_business_debtor_limit_across_the_gap(self):
        # CARES Act raised the limit to $7.5 million; it lapsed on 27 March 2022 and Pub. L. 117-151 restored it
        # from 21 June 2022 until 21 June 2024.
        self.assertIn('7,500,000', law.text_on('2021-06-01', USC))
        self.assertNotIn('7,500,000', law.text_on('2022-05-01', USC))
        self.assertIn('7,500,000', law.text_on('2022-07-01', USC))
        self.assertNotIn('7,500,000', law.text_on('2024-07-01', USC))

    def test_grundgesetz_before_1970(self):
        # Art. 12a came with the 17th amendment, in force 28 June 1968; git cannot date that commit, the trailer can.
        self.assertIsNone(law.text_on('1968-06-27', GG.format('012a')))
        self.assertIsNotNone(law.text_on('1968-06-28', GG.format('012a')))
        self.assertIsNotNone(law.text_on('1949-05-24', GG.format('001')))

    def test_grundgesetz_art_91e_from_2010(self):
        self.assertIsNone(law.text_on('2010-07-26', GG.format('091e')))
        self.assertIsNotNone(law.text_on('2010-07-27', GG.format('091e')))

    def test_one_date_reads_every_jurisdiction(self):
        # Every corpus whose record had started by the date is pinned at that moment.
        events = law.timeline()
        commit = law.root_on('2022-05-01', events)
        pins = head_pins(commit)
        started = {e.corpus for e in events if e.in_force <= '2022-05-01'}
        for corpus in law.manifest()['corpora']:
            if corpus['path'] in started:
                self.assertIn(corpus['path'], pins, corpus['path'])
        self.assertIsNotNone(law.text_on('2022-05-01', SEND))

    def test_matches_each_corpus_read_on_its_own(self):
        events = law.timeline()
        corpora = [c['path'] for c in law.manifest()['corpora']]
        for date in ('1956-03-19', '1990-09-29', '2015-09-01', '2020-03-27', '2022-05-01', '2024-06-21'):
            pins = head_pins(law.root_on(date, events)) if law.root_on(date, events) else {}
            last: dict[str, str] = {}
            for e in events:
                if e.in_force > date:
                    break
                last[e.corpus] = e.corpus_commit
            for corpus in corpora:
                self.assertEqual(pins.get(corpus), last.get(corpus), (date, corpus))


class WhoWroteIt(unittest.TestCase):
    def test_blame_names_the_law(self):
        lines = law.blame_on('2022-07-01', USC)
        authors = {author for author, line in lines if '7,500,000' in line}
        self.assertTrue(authors and all('117-151' in a for a in authors), authors)

    def test_diff_between_dates(self):
        diff = law.diff_between('2022-05-01', '2022-07-01', USC)
        self.assertIn('{+', diff)
        self.assertIn('7,500,000', diff)
        self.assertEqual(law.diff_between('2022-07-01', '2022-07-02', USC), '')


class AgainstEachCorpusOwnTools(unittest.TestCase):
    """The tree must give the same answers as each corpus read with its own tools."""

    def test_grundgesetz_matches_its_own_reader(self):
        gg = ROOT / DE
        # Force: after a corpus force-push, an older clone keeps its old tags, and stand_am.py reads tags.
        law.git('fetch', '-q', '--force', '--tags', law.corpus_info(DE)['url'], cwd=gg)
        for date in ('1949-05-24', '1956-03-22', '1968-06-28', '1990-10-03', '1994-11-15', '2010-07-27', '2017-07-20'):
            for art in ('1', '12a', '16', '23', '91e', '143d'):
                own = subprocess.run([sys.executable, 'tools/stand_am.py', date, art], cwd=gg, capture_output=True,
                                     encoding='utf-8')
                ours = law.text_on(date, GG.format(art.zfill(3) if art.isdigit() else art.zfill(4)))
                if ours is None:
                    self.assertNotEqual(own.returncode == 0 and f'# Artikel {art}' in own.stdout, True, (date, art))
                else:
                    self.assertIn(ours.strip(), own.stdout, (date, art))

    def test_switzerland_matches_its_own_reader(self):
        # Found by country code, and read in whichever layout is pinned: the three-act build (bv/, dsg/, schkg/) or
        # the whole Classified Compilation (folders by SR number: 101/ is the BV, 235.1/ the DSG, 281.1/ the SchKG).
        corpus = next(c for c in law.manifest()['corpora'] if c.get('code') == 'CH')
        path = corpus['path']
        ch = ROOT / path
        law.git('fetch', '-q', '--force', '--tags', corpus['url'], cwd=ch)
        top = set(law.git('ls-tree', '--name-only', law.pinned('HEAD', path), cwd=ch).split())
        act_of = {'bv': '101', 'dsg': '235.1', 'schkg': '281.1'} if '101' in top else {k: k for k in ('bv', 'dsg', 'schkg')}
        checked = 0
        for name, art in (('bv', '010a'), ('bv', '001'), ('dsg', '024'), ('schkg', '006'), ('schkg', '008a'), ('schkg', '293a')):
            act = act_of[name]
            for date in ('2019-06-01', '2020-06-01', '2021-06-01', '2024-01-01', '2025-06-01', '2026-06-01'):
                ours = law.text_on(date, f'{path}/{act}/art-{art}.md')
                own = subprocess.run([sys.executable, 'tools/stand_am.py', date, act, art.lstrip('0') or '0'], cwd=ch,
                                     capture_output=True, encoding='utf-8')
                if ours is not None:
                    self.assertIn(ours.strip(), own.stdout, (act, art, date))
                    checked += 1
        self.assertGreaterEqual(checked, 12)

    def test_uk_matches_every_version_in_its_data(self):
        send = ROOT / 'united-kingdom/uk/legislation'
        sys.path.insert(0, str(send / 'tools'))
        import ukhistory  # the corpus's own builder
        history = json.loads((send / 'data/history.json').read_text(encoding='utf-8'))
        checked = 0
        for p in history['provisions']:
            last_per_day = {v['date']: v for v in p['versions']}
            for day, v in last_per_day.items():
                expected = ukhistory.render(p, v, history['instruments'][p['instrument']])
                self.assertEqual(law.text_on(day, f"united-kingdom/uk/legislation/{ukhistory.provision_path(p['id'])}"), expected, (p['id'], day))
                checked += 1
        self.assertGreaterEqual(checked, 20)


class Semantics(unittest.TestCase):
    """The reader's questions, answered from the tree."""

    def test_follow_a_section_lists_each_law_with_its_dates(self):
        h = law.history(USC)
        laws = [x['law'] for x in h]
        self.assertTrue(any('116-136' in l for l in laws) and any('117-151' in l for l in laws))
        cares = next(x for x in h if '116-136' in x['law'])
        self.assertEqual(cares['in_force'], '2020-03-27')
        self.assertEqual(cares['enacted'], '2020-03-27')
        self.assertEqual([x['in_force'] for x in h], sorted(x['in_force'] for x in h))

    def test_a_section_from_the_starting_edition_starts_there_not_at_its_first_amendment(self):
        # 11 U.S.C. §101 is in the 2017 edition, which carries no trailer of its own; the tree dates it as the baseline.
        path = USC.replace('1182.md', '101.md')
        first = law.history(path)[0]
        self.assertEqual(first['kind'], 'baseline')
        self.assertLess(first['in_force'], '2019-01-01')
        why = law.explain_missing('2010-01-01', path)
        self.assertIn('where this record starts', why)
        self.assertNotIn('not yet in force', why)

    def test_dates_differ_where_the_law_says_so(self):
        # Germany: the 58th amendment was promulgated before it took effect; the UK regulations were made before.
        art = law.history(GG.format('091e'))[0]
        self.assertEqual(art['in_force'], '2010-07-27')
        self.assertTrue(art['published'] and art['published'][:10] < art['in_force'])
        made, in_force = law.history(SEND)[:2]  # the SEND Regulations: made 4 June, in force 1 September 2014
        self.assertEqual((made['in_force'], in_force['in_force'], in_force['enacted']), ('2014-06-04', '2014-09-01', '2014-06-04'))

    def test_blame_names_the_law_in_every_jurisdiction(self):
        gg = {a for a, _ in law.blame_on('2017-07-20', GG.format('091e'))}
        self.assertTrue(any('58.' in a for a in gg), gg)
        uk = {a for a, line in law.blame_on('2021-12-31', SEND) if line.startswith('(')}
        self.assertTrue(all(a.startswith(('S.I.', '20')) for a in uk), uk)

    def test_words_are_credited_to_the_law_that_wrote_them(self):
        runs = law.words_on('2022-07-01', USC)
        by_law: dict[str, str] = {}
        for author, text in runs:
            by_law[author] = by_law.get(author, '') + text
        restored = next(a for a in by_law if '117-151' in a)
        self.assertIn('7,500,000', by_law[restored])
        self.assertIn('person engaged in commercial or business activities', by_law[restored])
        self.assertIn('Definitions', next(t for a, t in by_law.items() if '116-54' in a))
        self.assertEqual(''.join(t for _, t in runs), law.text_on('2022-07-01', USC))
        # Germany: Art. 79 keeps the 1949 words beside those of the 4th amendment (1954).
        authors = {a for a, _ in law.words_on('2017-07-20', GG.format('079'))}
        self.assertTrue({'Grundgesetz (1949)', '4. Änderung (1954)'} <= authors, authors)
        # UK: one word of reg. 13(3) is the coronavirus regulations' (S.I. 2020/471), the rest the 2014 regulations'.
        uk = [(a, t) for a, t in law.words_on('2021-12-31', SEND) if '2020/471' in a]
        self.assertTrue(uk and all(len(t.split()) <= 3 for _, t in uk), uk)

    def test_copied_tags_point_at_the_matching_world_state(self):
        for corpus in law.manifest()['corpora']:
            path = ROOT / corpus['path']
            # Every tag copied here must match the corpus's own. A corpus may add tags after this build (the US added
            # law/<pl> tags to commits already pinned); the next build copies them, so counts are not compared.
            own = {}
            for line in law.git('tag', '--format=%(refname:short) %(*objectname) %(objectname)', cwd=path).splitlines():
                name, *shas = line.split()
                own[name] = shas[0]
            ours = [t for t in law.git('tag', '--list', f"{corpus['path']}/*").split()]
            # Only tags on the pinned history are copied: tags on a future branch (Armenia's) are not missing.
            pinned = law.git('tag', '--merged', law.pinned('HEAD', corpus['path']), cwd=path).split()
            self.assertTrue(ours or not pinned, f"{corpus['path']}: none of its tags were copied")
            self.assertLessEqual({t[len(corpus['path']) + 1:] for t in ours}, set(own), corpus['path'])
            for tag in ours[:40]:
                name = tag[len(corpus['path']) + 1:]
                self.assertEqual(law.pinned(tag, corpus['path']), own[name], tag)

    def test_plain_git_checkout_gives_the_same_text(self):
        # What a reader without the tools would do: take the root commit for a date and read the pinned file.
        commit = law.root_on('2022-05-01')
        pin = law.git('ls-tree', commit, '--', 'united-states/federal/usc').split()[2]
        text = law.git('show', f'{pin}:title-11/1182.md', cwd=ROOT / 'united-states/federal/usc')
        self.assertEqual(text, law.text_on('2022-05-01', USC))

    def test_laws_in_a_window_across_jurisdictions(self):
        window = [e for e in law.timeline() if '2012-01-01' <= e.in_force <= '2014-12-31' and e.kind == 'law']
        # At least Germany and the UK changed in this window; other corpora may too as the tree grows.
        self.assertLessEqual({DE, 'united-kingdom/uk/legislation'}, {e.corpus for e in window})
        self.assertEqual([e.in_force for e in window], sorted(e.in_force for e in window))


class GitReadsTheDates(unittest.TestCase):
    """git's own trailer parser must find each law commit's in-force date, so plain git (interpret-trailers,
    %(trailers)) works without our parser. Trailer keys must be ASCII: a key like `Verkündet:` makes git reject the
    whole block. List a corpus in KNOWN_OPEN while a fix is pending."""

    KNOWN_OPEN: set[str] = set()  # the Grundgesetz was fixed in its 2026-10-28 rebuild (Verkuendet)

    def test_in_force_date_is_a_git_trailer(self):
        for corpus in law.manifest()['corpora']:
            key = corpus['in_force_trailer']
            raw = law.git('log', '--format=%H%x1f%(trailers:key=' + key + ',valueonly)%x1f%B%x1e', cwd=ROOT / corpus['path'])
            missing = []
            for record in raw.split('\x1e'):
                if not record.strip():
                    continue
                sha, parsed, body = record.strip('\n').split('\x1f', 2)
                if law.trailers(body).get(key) and not parsed.strip():
                    missing.append(sha[:7])
            if corpus['path'] in self.KNOWN_OPEN:
                if not missing:
                    self.fail(f"{corpus['path']} is fixed: remove it from KNOWN_OPEN")
                continue
            self.assertEqual(missing, [], f"{corpus['path']}: git cannot read {key} in {len(missing)} commits")


class EveryCountry(unittest.TestCase):
    """The tree lists every country, and only real law is pinned (scripts/world-law/countries.json)."""

    def test_every_country_has_a_folder_with_its_sources(self):
        world = json.loads((ROOT / 'jurisdiction.json').read_text(encoding='utf-8'))
        nodes = {p: json.loads((ROOT / p / 'jurisdiction.json').read_text(encoding='utf-8')) for p in world['jurisdictions']}
        # The European Union sits beside the countries (level 'union') and is not counted as one.
        countries = [p for p, node in nodes.items() if node['level'] == 'country']
        self.assertEqual(len(countries), law.manifest()['countries'])
        self.assertGreaterEqual(len(countries), 209)  # 193 UN members and 16 other jurisdictions in countries.json
        for country in countries:
            # SOURCES.md comes from the world register (countries.json); a territory placed by its own corpus.json
            # (Åland) has none yet.
            if nodes[country].get('build'):
                self.assertTrue((ROOT / country / 'SOURCES.md').exists(), country)

    def test_every_pinned_corpus_documents_itself(self):
        waiting = set(law.manifest().get('awaiting_corpus_json', []))
        for corpus in law.manifest()['corpora']:
            files = law.git('ls-tree', '--name-only', law.pinned('HEAD', corpus['path']), cwd=ROOT / corpus['path']).split()
            self.assertIn('REPRODUCE.md', files, corpus['path'])
            if corpus['path'] not in waiting:
                self.assertIn('corpus.json', files, corpus['path'])

    def test_no_placeholder_is_pinned(self):
        for corpus in law.manifest()['corpora']:
            laws = [e for e in law.timeline() if e.corpus == corpus['path'] and e.kind != 'documentation']
            self.assertTrue(laws, f"{corpus['path']} holds no law; a placeholder repo must never be pinned")
            # The pinned commit itself is never the scaffold (a corpus may keep the scaffold as its first commit).
            subject = law.git('log', '-1', '--format=%s', law.pinned('HEAD', corpus['path']), cwd=ROOT / corpus['path'])
            self.assertNotIn('sources, before any law', subject, corpus['path'])

    def test_nothing_on_main_is_in_force_after_the_build(self):
        built = law.git('log', '-1', '--format=%cs', 'HEAD').strip()
        late = [(e.corpus, e.in_force) for e in law.timeline() if e.in_force > built]
        self.assertEqual(late, [], 'laws not yet in force belong on a corpus future branch, never on main')


class Pins(unittest.TestCase):
    def test_every_pin_is_on_its_corpus_published_main(self):
        # A force-pushed corpus orphans the pin; once GitHub collects it, a fresh clone cannot fetch it.
        for corpus in law.manifest()['corpora']:
            path = ROOT / corpus['path']
            law.git('fetch', '-q', corpus['url'], '+HEAD:refs/remotes/published/HEAD', cwd=path)
            pin = law.pinned('HEAD', corpus['path'])
            done = subprocess.run(['git', 'merge-base', '--is-ancestor', pin, 'refs/remotes/published/HEAD'], cwd=path)
            self.assertEqual(done.returncode, 0, f"{corpus['path']}: pin {pin[:7]} is not on the published main; rebuild global-law")


class CorpusDescriptions(unittest.TestCase):
    """Each pinned corpus's corpus.json follows the shared rules (git_for_law.md), so the tools read every country
    the same way."""

    MODIFIES = {'modified', 'disapplied', 'amount-adjusted', 'applied-with-modifications', 'ended'}
    ISO = re.compile(r'\d{4}-\d{2}-\d{2}')

    def test_corpus_json_follows_the_shared_rules(self):
        for corpus in law.manifest()['corpora']:
            pin = law.pinned('HEAD', corpus['path'])
            shown = subprocess.run(['git', 'show', f'{pin}:corpus.json'], cwd=ROOT / corpus['path'],
                                   capture_output=True, encoding='utf-8')
            if shown.returncode:
                continue  # awaiting its corpus.json; manifest.json lists these
            cj = json.loads(shown.stdout)
            where = corpus['path']
            kinds = set((cj.get('modifies') or {}).get('kinds') or [])
            self.assertLessEqual(kinds, self.MODIFIES, f'{where}: modifies.kinds is for words-unchanged effects only')
            reach = (cj.get('scope') or {}).get('default_reach')
            if reach:
                self.assertIs(reach.get('decided_here'), False, f'{where}: the default reach is a presumption, not data')
            for key in ('history_from', 'record_to'):
                if cj.get(key):
                    self.assertRegex(cj[key], self.ISO, f'{where}: {key} must be YYYY-MM-DD')

    def test_authors_are_laws_not_file_names(self):
        # A builder once reused a loop variable and named 3,118 commits "index.md" (germany-law, caught before push).
        for corpus in law.manifest()['corpora']:
            names = set(law.git('log', law.pinned('HEAD', corpus['path']), '--format=%an', cwd=ROOT / corpus['path']).split('\n'))
            # A file name or a path ("index.md", "cap/586/art-1.md"); a law number with a slash ("Decreto 342/2025",
            # "L.N. 234/2022") is a real author.
            bad = [n for n in names if re.search(r'\.(md|json|xml|html?|txt)$|\\|^[\w.-]+(/[\w.-]+)+$', n)]
            self.assertEqual(bad, [], f"{corpus['path']}: commit authors look like file names")

    def test_date_trailers_hold_dates(self):
        # A trailer named as a date (in-force, baseline, correction) must hold an ISO date in every commit, never a URL.
        for corpus in law.manifest()['corpora']:
            keys = [corpus.get(k) for k in ('in_force_trailer', 'baseline_trailer', 'correction_trailer') if corpus.get(k)]
            raw = law.git('log', law.pinned('HEAD', corpus['path']), '--format=%B%x1e', cwd=ROOT / corpus['path'])
            for body in raw.split('\x1e'):
                t = law.trailers(body)
                for key in keys:
                    if key in t:
                        self.assertRegex(t[key], r'^\d{4}-\d{2}-\d{2}', f"{corpus['path']}: {key}: {t[key][:40]}")


class CommandLine(unittest.TestCase):
    """The mistakes a reader makes, and the limits of each record, must give a clear answer, never a wrong one."""

    def cli(self, *args):
        done = subprocess.run([sys.executable, str(ROOT / 'tools/law.py'), *args], capture_output=True, encoding='utf-8',
                              env={**__import__('os').environ, 'PYTHONIOENCODING': 'utf-8', 'PYTHONDONTWRITEBYTECODE': '1'})
        return done.returncode, done.stdout, done.stderr

    def test_bad_dates_are_refused(self):
        for bad in ('2022-5-1', '2022-13-45', 'yesterday', '05/01/2022'):
            code, out, err = self.cli('world', bad)
            self.assertNotEqual(code, 0, bad)
            self.assertIn('Not a date', err, bad)

    def test_paths_written_differently_still_work(self):
        for path in (f'./{USC}', USC.replace('/', '\\')):
            code, out, _ = self.cli('show', '2022-07-01', path)
            self.assertEqual(code, 0, path)
            self.assertIn('7,500,000', out)

    def test_a_mistyped_path_is_not_reported_as_not_in_force(self):
        code, _, err = self.cli('show', '2022-07-01', 'united-states/federal/usc/title-11/1183x.md')
        self.assertNotEqual(code, 0)
        self.assertIn('not in this record at any date', err)

    def test_missing_text_says_why(self):
        _, _, before = self.cli('show', '2010-07-26', GG.format('091e'))
        self.assertIn('first appears on 2010-07-27', before)
        _, _, start = self.cli('show', '2015-01-01', USC)
        self.assertIn('record starts on 2018-01-12', start)

    def test_dates_past_a_record_carry_a_warning(self):
        code, out, err = self.cli('show', '2027-06-01', GG.format('016a'))
        self.assertEqual(code, 0)
        self.assertIn('record runs to 2026-10-28', err)
        self.assertNotIn('Note:', out)
        _, _, quiet = self.cli('show', '2016-01-01', GG.format('016a'))
        self.assertNotIn('Note:', quiet)

    def test_diff_from_before_a_record_shows_the_text_arriving(self):
        _, out, err = self.cli('diff', '1990-01-01', '2022-07-01', USC)
        self.assertIn('7,500,000', out)
        self.assertIn('record starts', err)

    def test_reversed_window_and_missing_arguments(self):
        _, out, _ = self.cli('laws', '2022-12-31', '2022-01-01', 'united-states')
        self.assertIn('117-151', out)
        code, _, err = self.cli('world')
        self.assertNotEqual(code, 0)
        self.assertNotIn('Traceback', err)

    def test_today_answers_same_or_different(self):
        _, out, _ = self.cli('today', '2022-07-01', USC)
        self.assertIn('worded differently today', out)
        self.assertIn('7,500,000', out)
        _, out, _ = self.cli('today', '1990-01-01', GG.format('001'))
        self.assertIn('on 1990-01-01: ', out)

    def test_blame_prints_real_in_force_dates_before_1970(self):
        _, out, _ = self.cli('blame', '2017-07-20', GG.format('012a'))
        self.assertIn('1968-06-28', out)
        self.assertNotIn('1970-01-01', out)

    def test_words_is_fast_on_a_long_section(self):
        import time
        start = time.time()
        code, out, _ = self.cli('words', '2026-04-01', 'united-states/federal/usc/title-17/115.md')
        self.assertEqual(code, 0)
        self.assertLess(time.time() - start, 8, 'law.py words took too long on 17 U.S.C. §115 (124 KB)')


def _corpus_by_repo(repo: str) -> str | None:
    """A corpus's path, found by its repository name so the test survives path renames."""
    return next((c['path'] for c in law.manifest()['corpora'] if c['url'].removesuffix('.git').endswith('/' + repo)), None)


class KindsAndDates(unittest.TestCase):
    """What each commit is, and the dates a reader sees (review of 2026-10-28, findings 2, 3, 6 and 7)."""

    def test_documentation_is_never_a_law(self):
        laws = [e for e in law.timeline() if e.kind == 'law' and e.law == 'Lexifina']
        self.assertEqual(laws, [], 'a corpus docs commit is filed as a law')
        out = subprocess.run([sys.executable, 'tools/law.py', 'laws', '1800-01-01', '2100-12-31'], cwd=ROOT,
                             capture_output=True, encoding='utf-8').stdout
        self.assertNotIn(' Lexifina\n', out)

    def test_consolidated_versions_are_in_history(self):
        malta = _corpus_by_repo('malta-law')
        if not malta:
            self.skipTest('Malta is not in this build')
        name = next(n for n in law.git('ls-tree', '-r', '--name-only', 'HEAD', cwd=ROOT / malta).split() if n.startswith('cap/'))
        h = law.history(f'{malta}/{name}')
        self.assertTrue(h, f'{name} shows no dated change')
        self.assertTrue(all(law.ISO_DAY.fullmatch(x['in_force']) for x in h))

    def test_adoption_and_publication_dates_are_read(self):
        estonia = _corpus_by_repo('estonia-law')
        if not estonia:
            self.skipTest('Estonia is not in this build')
        name = next(n for n in law.git('ls-tree', '-r', '--name-only', 'HEAD', cwd=ROOT / estonia).split()
                    if n.endswith('.md') and '/' in n and not n.endswith('README.md'))
        h = law.history(f'{estonia}/{name}')
        self.assertTrue(any(x['enacted'] for x in h) and any(x['published'] for x in h), name)

    def test_printings_that_change_the_text_are_in_history(self):
        us = _corpus_by_repo('united-states-law')
        if not us:
            self.skipTest('the US is not in this build')
        kinds = {x['kind'] for x in law.history(f'{us}/title-17/114.md')}
        self.assertIn('printing', kinds)


if __name__ == '__main__':
    unittest.main()
