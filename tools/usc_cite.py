"""US Code citations in court text, read one way for the case-law builders (the judgment overlays) and for
resolve_citations (tools/mcp_server.py): the same file is kept in both places (scripts/us-caselaw/usc_cite.py and
global-law's tools/usc_cite.py).

  "11 U.S.C. § 362(a)"                      -> 11/362 (the "(a)" is a subsection, never a section)
  "28 U.S.C. §§ 1331, 1332, and 1343(a)(3)" -> 28/1331, 28/1332, 28/1343
  "11 U.S.C. § 707(a), § 1112(b)(1)"         -> 11/707, 11/1112
  "9 U.S.C. §§ 1-16", "§§ 1 through 16"      -> a range: 9/1 to 9/16 (its two ends)
  "15 USC 78j(b)", "11 U.S.C, § 1126", "11 U.S.C., Sec. 104", "11 U.S.C.S. § 523", "11 U. S. C. A. § 110"
  "11 U.S.C. (1976 ed.) § 103(a)", "17 U.S.C. § 101 (1976 ed.)" -> flagged: an edition before the title's present
                                              numbering (Bankruptcy Act, Copyright Act of 1909 ...)
  "Title 11, United States Code, section 541", "section 1334 of title 28" (long forms)

What is not a citation: the PACER page stamps of the courts of appeals ("USCA4 Appeal: 19-1234 ... Pg: 3 of 47" read as
"3 USCA4", "13 USCA11"): "U.S.C." must be followed by a separator (§, "Sec.", "section", a comma or a space) and a
section number, never by a digit or letter. A number after a list's comma that is followed by a reporter ("365 F.3d",
"1997 WL") or by another "U.S.C." is not a further section.

When a section number names the law it names today: each title's present numbering starts on the day it was enacted
as positive law or recodified (RECODIFIED); a decision before that day, or a citation to an edition before it ("(1976
ed.)"), or "former 11 U.S.C. § 35", cites the old numbering (11 U.S.C. § 110 of 1938 is the Bankruptcy Act's § 70, not
today's § 110 on petition preparers). Sections added after the recodification (ADDED, and any section whose first
version in the US Code record is after the record starts) are not cited by a decision older than them."""
from __future__ import annotations

import re

# The day each held title's present numbering took effect. Title 11: the Bankruptcy Reform Act of 1978 (Pub. L. 95-598),
# effective 1979-10-01; before it "11 U.S.C." numbered the Bankruptcy Act of 1898. Title 17: the Copyright Act of 1976
# (Pub. L. 94-553), effective 1978-01-01; before it the Copyright Act of 1909. Title 35: the Patent Act of 1952 (Pub. L.
# 82-593), effective 1953-01-01. Title 9: enacted as positive law 1947-07-30 (Pub. L. 80-282). Titles 1 and 4: 1947-07-30
# (Pub. L. 80-278, 80-279). Title 3: 1948-06-25 (Pub. L. 80-771). Title 13: 1954-08-31 (Pub. L. 83-740). Title 39: the
# Postal Reorganization Act (Pub. L. 91-375), effective 1971-07-01.
RECODIFIED = {1: '1947-07-30', 3: '1948-06-25', 4: '1947-07-30', 9: '1947-07-30', 11: '1979-10-01', 13: '1954-08-31',
              17: '1978-01-01', 35: '1953-01-01', 39: '1971-07-01'}
RECODIFIED_BY = {1: 'title 1 enacted as positive law (1947)', 3: 'title 3 enacted as positive law (1948)',
                 4: 'title 4 enacted as positive law (1947)', 9: 'title 9 enacted as positive law (1947)',
                 11: 'the Bankruptcy Reform Act of 1978 (in effect 1979-10-01); before it, 11 U.S.C. numbered the Bankruptcy Act of 1898',
                 13: 'title 13 enacted as positive law (1954)', 17: 'the Copyright Act of 1976 (in effect 1978-01-01); before it, the Copyright Act of 1909',
                 35: 'the Patent Act of 1952 (in effect 1953-01-01)', 39: 'the Postal Reorganization Act (in effect 1971-07-01)'}
# Sections added after their title's recodification and before the US Code record starts (2017-2018), by the law that
# added them: a decision before that day cites some other text under the number (or none).
_ADDED = [
    (9, range(201, 209), '1970-07-31'),     # Pub. L. 91-368: the New York Convention
    (9, range(301, 308), '1990-08-15'),     # Pub. L. 101-369: the Panama Convention
    (11, range(110, 111), '1994-10-22'),    # Pub. L. 103-394: bankruptcy petition preparers
    (11, range(111, 113), '2005-04-20'),    # Pub. L. 109-8 (BAPCPA)
    (11, range(1201, 1232), '1986-10-27'),  # Pub. L. 99-554: chapter 12
    (11, range(1501, 1533), '2005-04-20'),  # Pub. L. 109-8: chapter 15
    (17, range(1001, 1011), '1992-10-28'),  # Pub. L. 102-563: Audio Home Recording Act
    (17, range(1101, 1102), '1994-12-08'),  # Pub. L. 103-465
    (17, range(1201, 1206), '1998-10-28'),  # Pub. L. 105-304: DMCA
    (17, range(1301, 1333), '1998-10-28'),  # Pub. L. 105-304: vessel hulls
    (35, range(273, 274), '1999-11-29'),    # Pub. L. 106-113
    (35, range(321, 330), '2011-09-16'),    # Pub. L. 112-29 (AIA): post-grant review
]
ADDED = {(t, str(s)): d for t, r, d in _ADDED for s in r}

_SIGN = r'(?:§\s?§?|�{1,2}|[Ss]ections?(?![a-z])|[Ss]ecs?\.?(?![a-z]))'
_NUM = r'(?>\d{1,5}(?!\d)[a-z]{0,3}(?:-\d{1,4}[a-z]{0,2})?)'
_SUB = r'(?:\s?\((?!(?:19|20)\d\d\))[a-zA-Z0-9]{1,6}\))*+'  # never a year: "(1976)" is an edition
# A list's later number is not a section when a reporter, a Westlaw cite or another title follows it.
_NOT_SECTION = r'(?!\s{0,2}U\s?\.?\s?S\s?\.?\s?C|\s+WL\b|\s+[A-Z][A-Za-z]{0,7}\.|\s+(?:Stat|Cong|Fed|Pub)\b)'
_JOIN = r'(?>\s*,\s*(?:and\s+|or\s+|&\s*)?|\s+(?:and|or)\s+|\s*&\s*|\s+(?:through|thru|to)\s+|\s?[-–—]\s?)'
_ITEM = _SIGN + r'?\s*' + _NUM + _NOT_SECTION + _SUB
_REST = r'(?:' + _JOIN + _ITEM + r'){0,40}+'  # possessive: a long list that is no citation fails at once, not by every split of its spaces
_EDITION = r'\((?:(?:19|20)\d{2}|Supp\.?)[^()]{0,30}\)'
USC = re.compile(
    r'(?<![\w.§])(?P<title>\d{1,2})\s{0,2}U\s?\.?\s?S\s?\.?\s?C\s?\.?(?:\s?[AS]\.?)?(?![A-Za-z0-9])'
    r'(?P<ed>\s*,?\s*' + _EDITION + r')?\s*,?'
    r'(?:\s*(?P<sign>' + _SIGN + r')\s*\.?\s*|\s+)'
    r'(?P<list>' + _NUM + _SUB + _REST + r')'
    r'(?P<etseq>\s*,?\s*et\.?\s?seq\.?)?')
# "Title 11, United States Code, section 541"; "section 1334 of title 28"; "§ 541 of Title 11 of the United States Code".
LONG_TITLE_FIRST = re.compile(
    r'\b[Tt]itle\s+(?P<title>\d{1,2})\s*,?\s+(?:of\s+the\s+)?United\s+States\s+Code(?:\s+Annotated)?\s*,?\s*'
    r'(?P<sign>' + _SIGN + r')\s*(?P<list>' + _NUM + _SUB + _REST + r')(?P<etseq>\s*,?\s*et\.?\s?seq\.?)?')
LONG_SECTION_FIRST = re.compile(
    r'(?<![\w.])(?P<sign>' + _SIGN + r')\s*(?P<list>' + _NUM + _SUB + _REST + r')\s+of\s+[Tt]itle\s+(?P<title>\d{1,2})'
    r'(?=\s*(?:,?\s*(?:of\s+the\s+)?United\s+States\s+Code|\s*U\s?\.?\s?S\s?\.?\s?C|\s*\(|[\s,.;)]|$))')
_ITEM_RX = re.compile(r'(?P<join>' + _JOIN + r')?(?P<sign>' + _SIGN + r')?\s*(?P<num>' + _NUM + r')' + _SUB)
AFTER = re.compile(r'\s*,?\s*\((?:[A-Z][A-Za-z.]*\s+)*(?:Supp\.?\s*[IVX]*,?\s*)?(?P<year>(?:19|20)\d{2})(?:\s*(?:ed\.?|edition|Supp\.?[^()]{0,20}|&[^()]{0,25}|,[^()]{0,25}))?\)')
FORMER = re.compile(r'\b(?:former(?:ly)?|old|repealed)\s*$', re.I)


def _year(s: str | None) -> int | None:
    m = re.search(r'(?:19|20)\d{2}', s or '')
    return int(m.group(0)) if m else None


def _parse(m: re.Match, text: str, exists, long: bool = False) -> list[dict]:
    title = int(m.group('title'))
    lst, base = m.group('list'), m.start('list')
    plural = (m.group('sign') or '').replace(' ', '') in ('§§', '��') or re.match(r'[Ss](?:ections|ecs)', m.group('sign') or '')
    edition = _year(m.group('ed')) if 'ed' in m.groupdict() else None
    after = AFTER.match(text, m.end())
    if after and edition is None:
        edition = int(after.group('year'))
    former = bool(FORMER.search(text[max(0, m.start() - 12):m.start()]))
    how = re.sub(r'\s+', ' ', m.group(0)).strip()
    items, prev = [], None
    for im in _ITEM_RX.finditer(lst):
        num, join = im.group('num'), (im.group('join') or '').strip().lower()
        at, iend = base + im.start('num'), base + im.end()
        # "1-16" is a range (or a hyphenated section, "2000e-2", where the record has it)
        if '-' in num:
            a, b = num.split('-', 1)
            if exists and exists(title, num):
                pass
            elif a.isdigit() and b.isdigit() and int(a) < int(b) and (plural or not exists or exists(title, a)):
                items.append({'section': a, 'at': at, 'item_end': iend, 'role': 'range-start', 'range_to': b})
                items.append({'section': b, 'at': at + len(a) + 1, 'item_end': iend, 'role': 'range-end', 'range_from': a})
                prev = items[-1]
                continue
            else:
                num = a
        if join in ('through', 'thru', 'to', '-', '–', '—') and prev is not None and prev['role'] in ('cited', 'range-start'):
            prev['role'], prev['range_to'], prev['item_end'] = 'range-start', num, iend
            items.append({'section': num, 'at': at, 'item_end': iend, 'role': 'range-end', 'range_from': prev['section']})
        else:
            items.append({'section': num, 'at': at, 'item_end': iend, 'role': 'cited'})
        prev = items[-1]
    for it in items:
        it.update(title=title, how=how, start=m.start(), end=m.end(), edition=edition, former=former,
                  et_seq=bool(m.groupdict().get('etseq')), long_form=long)
    return items


def cites(text: str, exists=None, long_forms: bool = False) -> list[dict]:
    """Every section a text cites: {'title', 'section', 'at' (where its number is), 'start', 'end' (the citation),
    'how' (its words), 'item_end' (where this section's words end), 'role' ('cited', 'range-start', 'range-end'), 'range_to'/'range_from', 'edition' (a year in an
    edition parenthesis), 'former', 'et_seq', 'long_form'}. `exists(title, section)` tells a hyphenated section
    ("2000e-2") from a range ("1-16") where the record knows; `long_forms` also reads "Title 11, United States Code,
    section 541" and "section 1334 of title 28"."""
    if not text:
        return []
    out = []
    for m in USC.finditer(text):
        out += _parse(m, text, exists)
    if long_forms:
        taken = [(c['start'], c['end']) for c in out]
        for rx in (LONG_TITLE_FIRST, LONG_SECTION_FIRST):
            for m in rx.finditer(text):
                if not any(s < m.end() and m.start() < e for s, e in taken):
                    out += _parse(m, text, exists, long=True)
                    taken.append((m.start(), m.end()))
    out.sort(key=lambda c: c['at'])
    return out


def sections_added() -> dict:
    return dict(ADDED)


def old_numbering(c: dict, decided: str | None = None, first_version: str | None = None,
                  record_from: str | None = None) -> str | None:
    """Why a citation names a section under an older numbering than the record's, or None when it may name today's
    section. `decided`: the decision's day; `first_version`: the day of the section's first version in the record, which
    counts as its creation only when after `record_from` (the record's start)."""
    t, s = c['title'], c['section']
    cut = RECODIFIED.get(t)
    if c.get('former'):
        return 'cited as former'
    if cut and c.get('edition') and c['edition'] < int(cut[:4]):
        return f"cites the {c['edition']} edition, before {RECODIFIED_BY.get(t, f'title {t} was recodified')}"
    if decided:
        if cut and decided < cut:
            return f'decided {decided}, before {RECODIFIED_BY.get(t, f"title {t} was recodified ({cut})")}'
        added = ADDED.get((t, re.sub(r'[a-z]+$', '', s)))
        if added and decided < added:
            return f'decided {decided}, before the section was added ({added})'
        if first_version and record_from and first_version > record_from and decided < first_version:
            return f'decided {decided}, before the section was added (its first version in the record: {first_version})'
    return None
