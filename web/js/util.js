import {t} from './i18n.js';

export const $ = id => document.getElementById(id);

// h('a', {href: '#', class: 'x', onclick: fn}, 'text', child...): an element. Law text and engine notes are data, so
// they only ever become text nodes, never markup.
export function h(tag, attrs = {}, ...children) {
  const el = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs || {})) {
    if (v === null || v === undefined || v === false) continue;
    if (k.startsWith('on') && typeof v === 'function') el.addEventListener(k.slice(2), v);
    else if (k === 'class') el.className = v;
    else if (k === 'style' && typeof v === 'object') Object.assign(el.style, v);
    else if (k === 'dataset') Object.assign(el.dataset, v);
    else if (v === true) el.setAttribute(k, '');
    else el.setAttribute(k, v);
  }
  append(el, children);
  return el;
}

export function append(el, children) {
  for (const c of children.flat(Infinity)) {
    if (c === null || c === undefined || c === false) continue;
    el.append(c instanceof Node ? c : document.createTextNode(String(c)));
  }
  return el;
}

export function clear(el) { while (el.firstChild) el.firstChild.remove(); return el; }

// Dates as YYYY-MM-DD strings, counted in whole days (UTC) so a time zone never moves them.
const DAY = 864e5;
export const toDays = s => Math.round(Date.parse(s.slice(0, 10) + 'T00:00:00Z') / DAY);
export const fromDays = n => new Date(n * DAY).toISOString().slice(0, 10);
export const addDays = (s, n) => fromDays(toDays(s) + n);
export function today() {
  const d = new Date();
  return fromDays(Math.floor((d.getTime() - d.getTimezoneOffset() * 6e4) / DAY));
}
export const isDate = s => typeof s === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(s) && !Number.isNaN(Date.parse(s + 'T00:00:00Z'));

// The five kinds of history a corpus can hold (MCP.md, "How a corpus describes itself").
// A corpus the manifest does not describe yet (it has no corpus.json until checked out) is 'unknown'.
export const HISTORY = ['in-force', 'replayed', 'as-enacted', 'current-only', 'metadata-only', 'unknown'];
export const HISTORY_COLOR = {'in-force': 'var(--h-full)', 'replayed': 'var(--h-repl)', 'as-enacted': 'var(--h-enac)',
  'current-only': 'var(--h-cur)', 'metadata-only': 'var(--h-meta)', 'unknown': 'var(--muted)'};
export const historyKind = k => (HISTORY.includes(k) ? k : 'unknown');
export const historyName = k => t(`history.${historyKind(k)}`);
export const historyHelp = k => t(`history.${historyKind(k)}.help`);
export function historyPill(k) {
  return h('span', {class: 'hp', title: historyHelp(k), style: {color: HISTORY_COLOR[historyKind(k)]}}, historyName(k));
}

export const COLORS = 8;  // law colours c0..c7 in app.css

let toastTimer = 0;
export function toast(msg) {
  const el = $('toast');
  el.textContent = msg;
  el.hidden = false;
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => { el.hidden = true; }, 2600);
}

// Copies text from a click; where the browser refuses, selects it in `box` for the reader to copy.
export async function copy(text, box) {
  try {
    await navigator.clipboard.writeText(text);
    toast(t('common.copied'));
  } catch (e) {
    if (box) {
      box.hidden = false;
      box.textContent = text;
      const r = document.createRange();
      r.selectNodeContents(box);
      const s = getSelection();
      s.removeAllRanges();
      s.addRange(r);
    }
    toast(t('common.copy_select'));
  }
}

export function debounce(fn, ms) {
  let id = 0;
  return (...a) => { clearTimeout(id); id = setTimeout(() => fn(...a), ms); };
}

export function loading() { return h('div', {class: 'loading', role: 'status'}, t('common.loading')); }

export function errorBox(e) {
  const msg = e && e.message === 'offline' ? t('error.offline') : (e && e.message) || String(e);
  return h('div', {class: 'err', role: 'alert'}, h('b', {}, t('error.title')), ' ', h('span', {class: 'engine-text'}, msg));
}

// A file name sorted the way people count: 2 before 10.
export function natural(a, b) {
  return String(a).localeCompare(String(b), undefined, {numeric: true, sensitivity: 'base'});
}
