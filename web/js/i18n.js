// Interface languages. Each language is one file, web/i18n/<code>.json, listed in web/i18n/index.json; a key missing
// from a language falls back to English. Dates, numbers and country names come from the browser's Intl, so they follow
// the chosen language without being translated by hand. Law text and the engine's notes are never translated.

const FALLBACK = 'en';
const STORE_KEY = 'global-law.lang';
let languages = [];          // [{code, name}]
let lang = FALLBACK;
let strings = {};            // the chosen language
let fallback = {};           // English
const listeners = new Set();

async function loadJSON(url) {
  const r = await fetch(url, {cache: 'no-cache'});
  if (!r.ok) throw new Error(`${url}: ${r.status}`);
  return r.json();
}

function pickInitial() {
  let saved = null;
  try { saved = localStorage.getItem(STORE_KEY); } catch (e) { /* storage may be blocked */ }
  const codes = languages.map(l => l.code);
  if (saved && codes.includes(saved)) return saved;
  for (const want of navigator.languages || [navigator.language || FALLBACK]) {
    const base = String(want).toLowerCase().split('-')[0];
    if (codes.includes(want)) return want;
    if (codes.includes(base)) return base;
  }
  return FALLBACK;
}

export async function init() {
  languages = await loadJSON('i18n/index.json');
  fallback = await loadJSON(`i18n/${FALLBACK}.json`);
  await setLanguage(pickInitial(), false);
}

export async function setLanguage(code, remember = true) {
  if (!languages.some(l => l.code === code)) code = FALLBACK;
  strings = code === FALLBACK ? fallback : await loadJSON(`i18n/${code}.json`).catch(() => ({}));
  lang = code;
  document.documentElement.lang = code;
  const dir = languages.find(l => l.code === code)?.dir || 'ltr';
  document.documentElement.dir = dir;
  if (remember) { try { localStorage.setItem(STORE_KEY, code); } catch (e) { /* not kept */ } }
  apply(document);
  listeners.forEach(fn => fn(code));
}

export const current = () => lang;
export const available = () => languages;
export const onChange = fn => listeners.add(fn);

// t('reader.words', {n: 3}): a string, or a plural form {"one": ..., "other": ...} chosen by Intl.PluralRules on `n`.
export function t(key, vars = {}) {
  let s = key in strings ? strings[key] : (key in fallback ? fallback[key] : key);
  if (s && typeof s === 'object') {
    const form = new Intl.PluralRules(lang).select(Number(vars.n ?? 0));
    s = s[form] ?? s.other ?? Object.values(s)[0];
  }
  return String(s).replace(/\{(\w+)\}/g, (m, k) => (k in vars ? (typeof vars[k] === 'number' ? num(vars[k]) : vars[k]) : m));
}

// Fills every element marked data-i18n="key" (its text) and data-i18n-attr="attr:key,attr:key" (attributes).
export function apply(root) {
  root.querySelectorAll('[data-i18n]').forEach(el => { el.textContent = t(el.dataset.i18n); });
  root.querySelectorAll('[data-i18n-attr]').forEach(el => {
    el.dataset.i18nAttr.split(',').forEach(pair => {
      const [attr, key] = pair.split(':').map(s => s.trim());
      if (attr && key) el.setAttribute(attr, t(key));
    });
  });
}

export const num = n => new Intl.NumberFormat(lang).format(n);

// A YYYY-MM-DD date in the chosen language; style 'long' (8 March 1998), 'short' or 'year'.
export function date(iso, style = 'long') {
  if (!iso || !/^\d{4}-\d{2}-\d{2}/.test(iso)) return iso || '';
  const [y, m, d] = iso.slice(0, 10).split('-').map(Number);
  const when = new Date(Date.UTC(y, m - 1, d));
  if (y < 100) return iso.slice(0, 10);  // Intl cannot show a year before 100 unambiguously
  const opts = style === 'year' ? {year: 'numeric'} : style === 'short'
    ? {year: 'numeric', month: 'short', day: 'numeric'} : {year: 'numeric', month: 'long', day: 'numeric'};
  return new Intl.DateTimeFormat(lang, {...opts, timeZone: 'UTC'}).format(when);
}

const regionCache = new Map();
// A country's name in the chosen language from its ISO 3166 code, else the folder name written out.
export function countryName(iso, slug) {
  const key = `${lang}:${iso}:${slug}`;
  if (regionCache.has(key)) return regionCache.get(key);
  let name = (slug || '').split('-').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ');
  if (iso) {
    try {
      const n = new Intl.DisplayNames([lang], {type: 'region'}).of(iso.toUpperCase());
      if (n && n.toUpperCase() !== iso.toUpperCase()) name = n;
    } catch (e) { /* unknown code: keep the folder name */ }
  }
  regionCache.set(key, name);
  return name;
}

export function languageName(code) {
  try { return new Intl.DisplayNames([lang], {type: 'language'}).of(code) || code; } catch (e) { return code; }
}

export function collator() { return new Intl.Collator(lang); }
