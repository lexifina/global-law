// The country picker: every jurisdiction in the manifest, with the corpora each holds, which of them this clone has
// checked out, and the command that adds the others.
import {t, countryName, collator, num} from './i18n.js';
import {corpora} from './api.js';
import {$, h, clear, copy, HISTORY, HISTORY_COLOR, historyName, historyPill, historyKind} from './util.js';

const NATIONAL = new Set(['national', 'federal', 'bund', 'union', 'eu', 'commonwealth', 'state']);
const KINDS = new Set(['acts', 'caselaw', 'instruments', 'cfr', 'usc', 'statutes', 'legislation', 'regulations']);
const S = {sel: null, sort: 'name', q: '', dq: '', shown: null, returnFocus: null, countries: null};

const title = s => s.split('-').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ');

export async function countries() {
  if (S.countries) return S.countries;
  const by = new Map();
  for (const c of await corpora()) {
    const parts = c.path.split('/');
    const slug = parts[0];
    if (!by.has(slug)) by.set(slug, []);
    by.get(slug).push({...c, history: historyKind(c.history), parts, kind: parts[parts.length - 1]});
  }
  S.countries = [...by].map(([slug, corp]) => {
    const isos = corp.map(c => (c.iso_path || '').split('/')[0].split('-')[0]).filter(x => /^[a-z]{2}$/.test(x));
    const iso = isos.sort((a, b) => isos.filter(x => x === b).length - isos.filter(x => x === a).length)[0] || '';
    const hc = {};
    corp.forEach(c => { hc[c.history] = (hc[c.history] || 0) + 1; });
    const froms = corp.map(c => c.history_from).filter(Boolean).sort();
    return {slug, iso, corp, hc, oldest: froms[0] || '', held: corp.filter(c => c.checked_out).length};
  });
  return S.countries;
}

export const nameOf = c => countryName(c.iso, c.slug);

// A corpus's name in the interface: its kind for a national corpus, the court for case law, else the place.
export function corpusName(c) {
  const parts = c.parts || c.path.split('/');
  const kind = parts[parts.length - 1];
  const mid = parts.slice(1, -1);
  const kindName = KINDS.has(kind) ? t(`kind.${kind}`) : title(kind);
  if (kind === 'caselaw') return mid.map(s => (s.length <= 6 ? s.toUpperCase() : title(s))).join(' › ') || kindName;
  if (mid.length === 1 && NATIONAL.has(mid[0])) return kindName;
  return mid.map(title).join(' › ') + (kind !== 'acts' ? ` · ${kindName}` : '');
}

const yr = s => (s ? String(Number(s.slice(0, 4))) : '?');  // year 0201 is 201

function qbar(hc, total) {
  return h('span', {class: 'qbar'}, HISTORY.filter(k => hc[k]).map(k =>
    h('i', {style: {width: `${(100 * hc[k]) / total}%`, background: HISTORY_COLOR[k]}})));
}

function renderCountries() {
  const q = S.q.trim().toLowerCase();
  const coll = collator();
  let list = S.countries.filter(c => !q || nameOf(c).toLowerCase().includes(q) || c.slug.includes(q) || c.iso === q);
  const byName = (a, b) => coll.compare(nameOf(a), nameOf(b));
  if (S.sort === 'name') list.sort(byName);
  if (S.sort === 'held') list.sort((a, b) => (b.held > 0) - (a.held > 0) || byName(a, b));
  if (S.sort === 'count') list.sort((a, b) => b.corp.length - a.corp.length || byName(a, b));
  if (S.sort === 'old') list.sort((a, b) => (a.oldest || '9999').localeCompare(b.oldest || '9999'));
  const box = clear($('pk-countries'));
  if (!list.length) { box.append(h('div', {class: 'pk-empty'}, t('picker.none', {q: S.q}))); return; }
  for (const c of list) {
    box.append(h('button', {class: 'crow', role: 'option', 'aria-selected': String(c.slug === S.sel),
      onclick: () => { S.sel = c.slug; S.dq = ''; S.shown = null; $('picker').classList.add('detail'); renderCountries(); renderDetail(); }},
      h('span', {class: 'n'}, h('span', {}, nameOf(c)), c.iso ? h('span', {class: 'iso'}, c.iso) : null,
        c.held ? h('span', {class: 'pill', title: t('picker.held_title')}, t('picker.held', {n: c.held})) : null),
      h('span', {class: 'c'}, S.sort === 'old' && c.oldest ? `${yr(c.oldest)} · ` : '', t('picker.count', {n: c.corp.length})),
      qbar(c.hc, c.corp.length)));
  }
}

function renderDetail() {
  const d = clear($('pk-detail'));
  const c = S.countries.find(x => x.slug === S.sel);
  if (!c) { d.append(h('div', {class: 'pk-empty'}, t('picker.pick'))); return; }
  const dq = S.dq.trim().toLowerCase();
  const items = c.corp.filter(k => !dq || k.path.includes(dq) || corpusName(k).toLowerCase().includes(dq)
    || (k.publisher || '').toLowerCase().includes(dq));
  const groups = [['picker.group_national', []], ['picker.group_caselaw', []], ['picker.group_local', []]];
  for (const k of items) {
    const mid = k.parts.slice(1, -1);
    if (k.kind === 'caselaw') groups[1][1].push(k);
    else if (mid.length === 1 && NATIONAL.has(mid[0])) groups[0][1].push(k);
    else groups[2][1].push(k);
  }
  const coll = collator();
  groups.forEach(g => g[1].sort((a, b) => (b.checked_out - a.checked_out) || coll.compare(corpusName(a), corpusName(b))));

  const head = h('div', {class: 'pk-dhead'},
    h('h3', {}, nameOf(c), c.iso ? h('span', {class: 'iso'}, c.iso) : null),
    h('p', {}, t('picker.summary', {n: c.corp.length, held: c.held}),
      c.oldest ? ` ${t('picker.oldest', {year: yr(c.oldest)})}` : ''),
    h('ul', {class: 'hlegend'}, HISTORY.filter(k => c.hc[k]).map(k =>
      h('li', {title: t(`history.${k}.help`)}, h('i', {style: {background: HISTORY_COLOR[k]}}), `${historyName(k)} · ${num(c.hc[k])}`))));
  if (c.corp.length > 8) {
    const f = h('input', {class: 'pk-dfind', type: 'search', value: S.dq, placeholder: t('picker.filter', {n: c.corp.length}),
      'aria-label': t('picker.filter', {n: c.corp.length})});
    f.addEventListener('input', () => {
      S.dq = f.value;
      const pos = f.selectionStart;
      renderDetail();
      const g = $('pk-detail').querySelector('.pk-dfind');
      g.focus();
      try { g.setSelectionRange(pos, pos); } catch (e) { /* search inputs may refuse */ }
    });
    head.append(f);
  }
  d.append(head);

  const row = k => {
    const cmd = `python3 tools/countries.py add ${k.path}`;
    const box = h('div', {class: 'cmd', hidden: S.shown !== k.path},
      h('span', {}, t('picker.add_how')), h('code', {}, cmd),
      h('span', {}, h('button', {class: 'btn sm', onclick: () => copy(cmd)}, t('common.copy'))));
    return h('div', {class: 'corp'},
      h('div', {class: 't'}, corpusName(k), h('small', {}, k.path)),
      h('div', {class: 'r'}, historyPill(k.history), h('span', {class: 'yrs'}, `${yr(k.history_from)}–${yr(k.record_to)}`),
        k.checked_out
          ? h('a', {class: 'btn sm primary', href: `#/browse?path=${encodeURIComponent(k.path)}`, onclick: close}, t('picker.open'))
          : h('button', {class: 'btn sm', 'aria-expanded': String(S.shown === k.path),
            onclick: () => { S.shown = S.shown === k.path ? null : k.path; renderDetail(); }}, t('picker.add'))),
      k.publisher ? h('div', {class: 'pub'}, k.publisher) : null,
      box);
  };
  const scroll = h('div', {class: 'pk-scroll'});
  const shown = groups.filter(g => g[1].length);
  if (!shown.length) scroll.append(h('div', {class: 'pk-empty'}, t('picker.no_corpora')));
  for (const [key, list] of shown) {
    scroll.append(h('div', {class: 'grp'}, h('h4', {}, `${t(key)} · ${num(list.length)}`), list.map(row)));
  }
  d.append(scroll);
}

export async function open(slug) {
  S.returnFocus = document.activeElement;
  await countries();
  if (slug) S.sel = slug;
  if (!S.sel) S.sel = (S.countries.find(c => c.held) || S.countries[0]).slug;
  S.q = ''; S.dq = ''; S.shown = null;
  $('pk-q').value = '';
  $('scrim').hidden = false;
  document.body.style.overflow = 'hidden';
  $('picker').classList.toggle('detail', Boolean(slug));
  const total = S.countries.reduce((n, c) => n + c.corp.length, 0);
  $('pk-meta').textContent = t('picker.meta', {countries: S.countries.length, corpora: total});
  renderCountries();
  renderDetail();
  $('pk-countries').querySelector('[aria-selected="true"]')?.scrollIntoView({block: 'center'});
  (slug && innerWidth <= 720 ? $('pk-back') : $('pk-q')).focus();
}

export function close() {
  if ($('scrim').hidden) return;
  $('scrim').hidden = true;
  document.body.style.overflow = '';
  S.returnFocus?.focus?.();
}

export function setup() {
  $('pk-close').addEventListener('click', close);
  $('pk-back').addEventListener('click', () => { $('picker').classList.remove('detail'); $('pk-q').focus(); });
  $('scrim').addEventListener('click', e => { if (e.target.id === 'scrim') close(); });
  $('pk-q').addEventListener('input', e => { S.q = e.target.value; renderCountries(); });
  $('pk-q').addEventListener('keydown', e => { if (e.key === 'Enter') $('pk-countries').querySelector('.crow')?.click(); });
  document.querySelectorAll('.pk-sort button').forEach(b => b.addEventListener('click', () => {
    S.sort = b.dataset.s;
    document.querySelectorAll('.pk-sort button').forEach(x => x.setAttribute('aria-pressed', String(x === b)));
    renderCountries();
  }));
  document.addEventListener('keydown', e => { if (e.key === 'Escape' && !$('scrim').hidden) close(); }, true);
}

export function refresh() { if (!$('scrim').hidden) { renderCountries(); renderDetail(); } }
