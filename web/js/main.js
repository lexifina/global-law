// The page: header (search, country, language) and one view at a time, chosen by the address's #/route?params.
import * as i18n from './i18n.js';
import {t} from './i18n.js';
import {$, h, clear, errorBox, debounce} from './util.js';
import * as picker from './picker.js';
import {home, browse, search, suggest, href, linkFor, cleanHeading} from './views.js';
import {read, setupTooltip} from './reader.js';
import {corpusOf} from './api.js';

const ROUTES = {'': home, browse, search, read};
let routeSeq = 0;

async function route() {
  const raw = location.hash.replace(/^#\/?/, '');
  const [name, query] = raw.split('?');
  const view = $('view');
  const fn = ROUTES[name] || home;
  ++routeSeq;
  // Each visit draws into its own container: a slower answer for a page already left lands in a detached one.
  const fresh = h('div');
  clear(view).append(fresh);
  scrollTo(0, 0);
  updateCountryButton();
  try {
    await fn(fresh, new URLSearchParams(query || ''));
  } catch (e) {
    console.error(e);
    fresh.append(errorBox(e));
  }
}

// The header's country button names the country being read, once a path is open.
async function updateCountryButton() {
  const params = new URLSearchParams(location.hash.split('?')[1] || '');
  const path = params.get('path');
  const label = $('cbtn-label');
  label.dataset.slug = '';
  if (!path) { label.textContent = t('picker.choose'); return; }
  const c = await corpusOf(path).catch(() => null);
  if (!c) { label.textContent = t('picker.choose'); return; }
  const all = await picker.countries();
  const country = all.find(x => x.slug === c.path.split('/')[0]);
  label.textContent = country ? i18n.countryName(country.iso, country.slug) : t('picker.choose');
  label.dataset.slug = country?.slug || '';
}

function setupSearch() {
  const q = $('q'), box = $('sugg');
  let active = -1;
  const show = on => { box.hidden = !on; q.setAttribute('aria-expanded', String(on)); };
  const items = () => [...box.querySelectorAll('a')];
  const mark = i => { items().forEach((a, k) => a.setAttribute('aria-selected', String(k === i))); active = i; };

  const fill = debounce(async () => {
    const text = q.value.trim();
    if (text.length < 2) { show(false); return; }
    const asked = text;
    const {hits, lands} = await suggest(text);
    if (q.value.trim() !== asked) return;
    clear(box);
    for (const x of hits) {
      box.append(h('a', {href: linkFor(x.path), role: 'option'},
        h('span', {}, x.title || cleanHeading(x.heading) || x.path.split('/').pop()), h('span', {class: 'p'}, x.path)));
    }
    for (const c of lands) {
      box.append(h('a', {href: '#', role: 'option', onclick: e => { e.preventDefault(); show(false); picker.open(c.slug); }},
        h('span', {}, i18n.countryName(c.iso, c.slug)), h('span', {class: 'p'}, t('search.country', {n: c.corp.length}))));
    }
    box.append(h('a', {href: href('search', {q: text}), role: 'option'}, h('span', {}, t('search.all', {q: text})), h('span', {class: 'p'}, '↵')));
    if (!hits.length && !lands.length) box.prepend(h('div', {class: 'note'}, t('search.none_short')));
    active = -1;
    show(true);
  }, 220);

  q.addEventListener('input', fill);
  q.addEventListener('focus', () => { if (q.value.trim().length >= 2) fill(); });
  q.addEventListener('keydown', e => {
    const list = items();
    if (e.key === 'ArrowDown' && list.length) { e.preventDefault(); show(true); mark(Math.min(list.length - 1, active + 1)); }
    else if (e.key === 'ArrowUp' && list.length) { e.preventDefault(); mark(Math.max(0, active - 1)); }
    else if (e.key === 'Escape') show(false);
    else if (e.key === 'Enter') {
      e.preventDefault();
      if (active >= 0 && list[active]) list[active].click();
      else if (q.value.trim()) location.hash = href('search', {q: q.value.trim()});
      show(false);
    }
  });
  document.addEventListener('click', e => { if (!e.target.closest('.search')) show(false); });
  box.addEventListener('click', e => { if (e.target.closest('a')) show(false); });
}

function setupLanguage() {
  const sel = $('lang');
  const fill = () => {
    clear(sel);
    for (const l of i18n.available()) sel.append(h('option', {value: l.code, selected: l.code === i18n.current()}, l.name));
    sel.setAttribute('aria-label', t('lang.label'));
  };
  fill();
  sel.addEventListener('change', async () => { await i18n.setLanguage(sel.value); fill(); route(); });
}

async function start() {
  try {
    await i18n.init();
  } catch (e) {
    $('view').append(errorBox(e));
    return;
  }
  document.title = t('app.name');
  i18n.onChange(() => { document.title = t('app.name'); picker.refresh(); });
  picker.setup();
  setupSearch();
  setupLanguage();
  setupTooltip();
  $('cbtn').addEventListener('click', () => picker.open($('cbtn-label').dataset.slug || undefined));
  addEventListener('hashchange', route);
  route();
}

start();
