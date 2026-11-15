// Home, browse and search. The reader is in reader.js.
import {t, countryName, num, date as fmtDate} from './i18n.js';
import {tool, corpora, corpusOf} from './api.js';
import {h, clear, loading, errorBox, historyPill, isDate, today, natural} from './util.js';
import {countries, corpusName, open as openPicker} from './picker.js';

export const href = (route, params = {}) => {
  const q = new URLSearchParams(Object.entries(params).filter(([, v]) => v !== undefined && v !== null && v !== ''));
  const s = q.toString();
  return `#/${route}${s ? `?${s}` : ''}`;
};
// A heading as the engine gives it, without its explanation for AI clients (after two spaces and a bracket).
export const cleanHeading = x => (x || '').split(/\s{2}\(/)[0].trim();

export const linkFor = (path, date) => (path.endsWith('.md') ? href('read', {path, date}) : href('browse', {path, date}));

// Country › corpus › folders, for a path in the tree; the last part is plain text.
export async function crumbs(path, date) {
  const nav = h('nav', {class: 'crumbs', 'aria-label': t('common.where')});
  const c = await corpusOf(path).catch(() => null);
  if (!c) { nav.append(h('b', {}, path)); return nav; }
  const all = await countries();
  const country = all.find(x => x.slug === c.path.split('/')[0]);
  nav.append(h('button', {onclick: () => openPicker(country?.slug), title: t('picker.change')},
    country ? countryName(country.iso, country.slug) : c.path.split('/')[0]), '›');
  const inner = path.slice(c.path.length).replace(/^\/+/, '').split('/').filter(Boolean);
  const parts = [[c.path, corpusName(c)], ...inner.map((p, i) => [`${c.path}/${inner.slice(0, i + 1).join('/')}`, p.replace(/\.md$/, '')])];
  parts.forEach(([p, label], i) => {
    if (i) nav.append('›');
    nav.append(i === parts.length - 1 ? h('b', {}, label) : h('a', {href: href('browse', {path: p, date})}, label));
  });
  return nav;
}

const EXAMPLES = [
  ['germany/bund/acts', 'Art. 13 GG'],
  ['sweden/national/acts', '6 kap. 1 § brottsbalken'],
  ['united-states/federal/usc', '11 U.S.C. § 1182'],
  ['switzerland/bund/acts', 'Art. 8 BV'],
  ['france/national/acts', 'article 9 code civil'],
];

export async function home(view) {
  view.append(h('section', {class: 'hero'},
    h('h1', {}, t('home.title')),
    h('p', {}, t('home.lead'))));
  const held = h('section', {}, loading());
  view.append(held);
  let served = [];
  try {
    served = (await tool('list_jurisdictions', {})).corpora || [];
  } catch (e) {
    clear(held).append(errorBox(e));
    return;
  }
  const all = await corpora();
  const byPath = new Map(all.map(c => [c.path, c]));
  const cs = await countries();
  clear(held);
  held.append(h('div', {class: 'section-h'}, h('h2', {}, t('home.held')),
    h('button', {class: 'btn', onclick: () => openPicker()}, t('home.add'))));
  if (!served.length) {
    held.append(h('p', {class: 'muted'}, t('home.none')),
      h('p', {}, h('code', {class: 'mono'}, 'python3 tools/countries.py add sweden')));
  } else {
    const tiles = h('div', {class: 'tiles'});
    for (const s of served) {
      const m = byPath.get(s.path) || {path: s.path};
      const country = cs.find(c => c.slug === s.path.split('/')[0]);
      tiles.append(h('a', {class: 'card tile', href: href('browse', {path: s.path})},
        h('span', {class: 'label'}, country ? countryName(country.iso, country.slug) : ''),
        h('span', {class: 't'}, corpusName(m)),
        h('span', {}, historyPill(s.history || m.history), ' ',
          h('span', {class: 'muted'}, t('home.record', {from: fmtDate(s.record_starts || m.history_from, 'year'),
            to: fmtDate(s.record_to || m.record_to, 'short')}))),
        s.provision_files ? h('span', {class: 'muted'}, t('home.files', {n: s.provision_files})) : null,
        h('span', {class: 'p'}, s.path)));
    }
    held.append(tiles);
  }
  const tries = EXAMPLES.filter(([p]) => byPath.get(p)?.checked_out);
  const extra = served.filter(s => s.example_path && !tries.some(([p]) => p === s.path)).slice(0, 4);
  if (tries.length || extra.length) {
    held.append(h('div', {class: 'section-h'}, h('h2', {}, t('home.try'))),
      h('ul', {class: 'list'},
        tries.map(([, q]) => h('li', {}, h('a', {href: href('search', {q})}, h('span', {class: 't'}, q), h('span', {class: 'r'}, t('home.search'))))),
        extra.map(s => h('li', {}, h('a', {href: href('read', {path: s.example_path})},
          h('span', {class: 't'}, h('small', {}, s.example_path)), h('span', {class: 'r'}, t('home.read')))))));
  }
  held.append(h('footer', {}, t('home.footer')));
}

export async function browse(view, params) {
  const path = (params.get('path') || '').replace(/^\/+|\/+$/g, '');
  const date = isDate(params.get('date')) ? params.get('date') : today();
  const offset = Number(params.get('offset')) || 0;
  view.append(await crumbs(path, params.get('date')));
  const corpus = await corpusOf(path);
  const title = h('h1', {}, corpus && path.startsWith(corpus.path + '/') ? path.slice(corpus.path.length + 1) : path.split('/').pop());
  view.append(title);
  if (corpus && corpus.path === path) title.textContent = corpusName(corpus);

  const dateIn = h('input', {type: 'date', id: 'browse-date', value: date, max: '9999-12-31', 'aria-label': t('browse.date')});
  dateIn.addEventListener('change', () => { if (isDate(dateIn.value)) location.hash = href('browse', {path, date: dateIn.value}); });
  view.append(h('div', {class: 'toolbar'}, h('label', {class: 'muted', for: 'browse-date'}, t('browse.date')), dateIn,
    corpus ? historyPill(corpus.history) : null,
    corpus && !corpus.checked_out ? h('span', {class: 'pill warn'}, t('browse.not_held')) : null));

  const body = h('section', {}, loading());
  view.append(body);
  let r;
  try {
    r = await tool('list_provisions', {path, date, offset, max_results: 500, by_folder: true});
  } catch (e) {
    clear(body).append(errorBox(e));
    return;
  }
  clear(body);
  if (r.folder && r.folder.title) title.textContent = r.folder.title;
  const list = h('ul', {class: 'list'});
  const folders = Array.isArray(r.folders) ? r.folders : [];
  for (const f of folders) {
    if (typeof f === 'string') {
      const p = `${path}/${f}`;
      list.append(h('li', {}, h('a', {href: href('browse', {path: p, date: params.get('date')})},
        h('span', {class: 't'}, `${f}/`), h('span', {class: 'r'}, t('browse.folder')))));
    } else {
      const last = f.last_change;
      list.append(h('li', {}, h('a', {href: href('browse', {path: f.folder, date: params.get('date')})},
        h('span', {class: 't'}, f.title || f.folder.split('/').pop(), h('small', {}, f.folder.split('/').pop())),
        h('span', {class: 'r'}, t('browse.files', {n: f.files || 0}),
          last ? h('span', {}, h('br'), t('browse.changed', {date: fmtDate(last.in_force, 'short')})) : null))));
    }
  }
  const provs = (r.provisions || []).slice().sort((a, b) => natural(a.path, b.path));
  for (const p of provs) {
    list.append(h('li', {}, h('a', {href: href('read', {path: p.path, date: params.get('date')})},
      h('span', {class: 't'}, p.heading || p.path.split('/').pop(), h('small', {}, p.path.split('/').pop())),
      h('span', {class: 'r'}, '→'))));
  }
  if (!folders.length && !provs.length) list.append(h('li', {class: 'empty'}, r.summary || t('browse.empty')));
  body.append(h('p', {class: 'muted'}, t('browse.count', {n: r.count ?? (folders.length + provs.length), date: fmtDate(date)})), list);
  if (r.page && r.page.next_offset != null) {
    body.append(h('p', {}, h('a', {class: 'btn', href: href('browse', {path, date: params.get('date'), offset: r.page.next_offset})}, t('common.more'))));
  }
}

export async function search(view, params) {
  const q = (params.get('q') || '').trim();
  view.append(h('h1', {class: 'page-h'}, t('search.title', {q})));
  const body = h('section', {}, loading());
  view.append(body);
  if (!q) { clear(body).append(h('p', {class: 'muted'}, t('search.empty'))); return; }
  let r;
  try {
    r = await tool('find_provision', {query: q, max_results: 50});
  } catch (e) {
    clear(body).append(errorBox(e));
    return;
  }
  clear(body);
  const rows = r.results || [];
  body.append(h('p', {class: 'muted'}, t('search.count', {n: r.page?.total ?? rows.length})));
  const list = h('ul', {class: 'list'});
  for (const x of rows) {
    list.append(h('li', {}, h('a', {href: linkFor(x.path)},
      h('span', {class: 't'}, x.title || cleanHeading(x.heading) || x.path.split('/').pop(), h('small', {}, x.path)),
      h('span', {class: 'r'}, x.path.endsWith('.md') ? t('search.provision') : t('search.act', {n: x.files || 0})))));
  }
  if (!rows.length) list.append(h('li', {class: 'empty'}, t('search.none')));
  body.append(list, h('p', {class: 'engine'}, r.summary || ''));
}

// Suggestions under the search box: provisions and acts, then countries whose name starts with a word typed.
export async function suggest(q) {
  const words = q.toLowerCase().split(/\s+/).filter(w => w.length >= 2 && !/^\d/.test(w));
  const cs = await countries();
  const lands = words.length ? cs.filter(c => words.some(w => countryName(c.iso, c.slug).toLowerCase().startsWith(w)
    || c.slug.startsWith(w) || c.iso === w)).slice(0, 4) : [];
  let hits = [];
  try {
    hits = q.length >= 2 ? (await tool('find_provision', {query: q, max_results: 8})).results || [] : [];
  } catch (e) { hits = []; }
  return {hits, lands};
}

export {num};
