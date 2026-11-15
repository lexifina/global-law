// The reader: one provision as in force on a date, with the laws that wrote it, what changed and what the record holds.
import {t, date as fmtDate, num} from './i18n.js';
import {tool, corpusOf} from './api.js';
import {$, h, clear, loading, errorBox, toDays, fromDays, addDays, today, isDate, copy, toast, debounce,
  historyPill, historyHelp, COLORS} from './util.js';
import {render, diff, diffSegments, wordDiffSegments} from './text.js';
import {crumbs, href} from './views.js';

const COLOR_KEY = 'global-law.color';
let keyHandler = null;

function colorPref() {
  try { return localStorage.getItem(COLOR_KEY) !== 'off'; } catch (e) { return true; }
}

export async function read(view, params) {
  const S = {
    path: (params.get('path') || '').replace(/^\/+/, ''),
    date: isDate(params.get('date')) ? params.get('date') : today(),
    mode: ['read', 'changes', 'compare'].includes(params.get('mode')) ? params.get('mode') : 'read',
    b: isDate(params.get('b')) ? params.get('b') : null,
    color: colorPref(),
    focus: null,
    changes: [],       // provision_history, oldest first
    lawIndex: new Map(),
    seq: 0,            // the latest update asked; older answers are dropped
  };
  if (!S.path) { view.append(errorBox(new Error(t('reader.no_path')))); return; }

  view.append(await crumbs(S.path, params.get('date')));
  const title = h('h1', {}, S.path.split('/').pop().replace(/\.md$/, ''));
  view.append(title);
  const corpus = await corpusOf(S.path);

  // timeline
  const dateIn = h('input', {type: 'date', id: 'rd-date', max: '9999-12-31'});
  const verPill = h('span', {class: 'pill'});
  const prevB = h('button', {class: 'btn', onclick: () => step(-1)}, t('reader.prev'));
  const nextB = h('button', {class: 'btn', onclick: () => step(1)}, t('reader.next'));
  const todayB = h('button', {class: 'btn', onclick: () => setDate(today())}, t('reader.today'));
  const rail = h('div', {class: 'rail'});
  const ticks = h('div', {class: 'ticks'});
  const range = h('input', {type: 'range', class: 'range', 'aria-label': t('reader.slider')});
  const marks = h('div');
  const track = h('div', {class: 'track'}, rail, ticks, marks, range);
  view.append(h('section', {class: 'tl', 'aria-label': t('reader.timeline')},
    h('div', {class: 'tl-head'},
      h('div', {class: 'tl-date'}, h('label', {for: 'rd-date'}, t('reader.as_of')), dateIn, verPill),
      h('div', {class: 'btns'}, prevB, nextB, todayB)),
    track,
    h('div', {class: 'tl-hint'}, t('reader.hint'))));

  // text and facts
  const modeBtns = ['read', 'changes', 'compare'].map(m => h('button', {'aria-pressed': String(S.mode === m),
    onclick: () => { S.mode = m; modeBtns.forEach(b => b.setAttribute('aria-pressed', String(b === modeBtns[['read', 'changes', 'compare'].indexOf(m)]))); update(); }},
  t(`reader.mode_${m}`)));
  const colorBox = h('input', {type: 'checkbox', id: 'rd-color', checked: S.color});
  colorBox.addEventListener('change', () => {
    S.color = colorBox.checked;
    try { localStorage.setItem(COLOR_KEY, S.color ? 'on' : 'off'); } catch (e) { /* not kept */ }
    if (!S.color) S.focus = null;
    update();
  });
  const citeBtn = h('button', {class: 'btn primary'}, t('reader.cite'));
  const status = h('div', {class: 'status'});
  const body = h('div', {}, loading());
  const factBox = h('section', {class: 'card box'});
  const legendBox = h('section', {class: 'card box'});
  const versBox = h('section', {class: 'card box'});
  const limitBox = h('section', {class: 'card box'});
  const citeOut = h('div', {class: 'mono', hidden: true});
  view.append(h('div', {class: 'grid'},
    h('section', {class: 'card', 'aria-label': t('reader.text')},
      h('div', {class: 'bar'}, h('div', {class: 'segm', role: 'group', 'aria-label': t('reader.view')}, modeBtns),
        h('div', {class: 'btns'}, h('label', {class: 'switch', for: 'rd-color'}, colorBox, t('reader.color')), citeBtn)),
      status, body, h('div', {class: 'more'}, citeOut)),
    h('aside', {}, factBox, legendBox, versBox, limitBox)));

  // the provision's whole history, once
  try {
    const hist = await tool('provision_history', {path: S.path});
    S.changes = (hist.changes || []).slice().sort((a, b) => (a.in_force || '').localeCompare(b.in_force || ''));
  } catch (e) {
    clear(body).append(errorBox(e));
    return;
  }
  S.changes.forEach((c, i) => { if (!S.lawIndex.has(c.law)) S.lawIndex.set(c.law, S.lawIndex.size % COLORS); });

  const first = S.changes[0]?.in_force || corpus?.history_from || '1950-01-01';
  const end = [today(), ...S.changes.map(c => c.in_force)].sort().pop();
  const pad = Math.max(30, Math.round((toDays(end) - toDays(first)) * 0.03)) || 365;
  const lo = toDays(first) - pad, hi = toDays(end);
  range.min = lo; range.max = hi; range.step = 1;
  const pos = d => Math.max(0, Math.min(100, ((toDays(d) - lo) / (hi - lo)) * 100));
  drawTicks();

  range.addEventListener('input', () => { S.date = fromDays(+range.value); dateIn.value = S.date; later(); });
  dateIn.addEventListener('change', () => { if (isDate(dateIn.value)) setDate(dateIn.value); });
  const later = debounce(() => update(), 180);
  citeBtn.addEventListener('click', () => cite());

  if (keyHandler) document.removeEventListener('keydown', keyHandler);
  keyHandler = e => {
    if (!document.body.contains(track)) { document.removeEventListener('keydown', keyHandler); return; }
    if (e.target.closest('input,textarea,select') || e.altKey || e.ctrlKey || e.metaKey) return;
    if (e.key === 'ArrowLeft') { e.preventDefault(); step(-1); }
    if (e.key === 'ArrowRight') { e.preventDefault(); step(1); }
  };
  document.addEventListener('keydown', keyHandler);

  let last = null;  // the latest read_law answer

  function setDate(d) { S.date = d; update(); }
  function step(dir) {
    const ds = S.changes.map(c => c.in_force).filter(Boolean);
    const target = dir < 0 ? ds.filter(d => d < S.date).pop() : ds.find(d => d > S.date);
    if (target) setDate(target);
  }
  function lawColor(name) {
    if (!name) return 0;
    if (S.lawIndex.has(name)) return S.lawIndex.get(name);
    for (const [k, v] of S.lawIndex) if (name.startsWith(k) || k.startsWith(name.split(' (text as')[0])) { S.lawIndex.set(name, v); return v; }
    const v = S.lawIndex.size % COLORS;
    S.lawIndex.set(name, v);
    return v;
  }
  const changeOf = name => S.changes.find(c => c.law === name || (name && name.startsWith(c.law)));
  function currentChange() {
    return S.changes.filter(c => c.in_force && c.in_force <= S.date).pop() || null;
  }

  function keepURL() {
    const params = {path: S.path, date: S.date === today() ? null : S.date, mode: S.mode === 'read' ? null : S.mode,
      b: S.mode === 'compare' ? S.b : null};
    try { history.replaceState(null, '', href('read', params)); } catch (e) { /* the address is a convenience */ }
  }

  function drawTicks() {
    const y0 = Number(fromDays(lo).slice(0, 4)), y1 = Number(fromDays(hi).slice(0, 4));
    const span = Math.max(1, y1 - y0);
    const stepY = [1, 2, 5, 10, 20, 25, 50, 100, 200].find(s => span / s <= 7) || 500;
    clear(ticks);
    for (let y = Math.ceil(y0 / stepY) * stepY; y <= y1; y += stepY) {
      const p = pos(`${String(y).padStart(4, '0')}-01-01`);
      if (p > 2 && p < 98) ticks.append(h('span', {style: {left: `${p}%`}}, String(y)));
    }
    if (!ticks.childNodes.length) {  // a span of under a year: its two ends, dated
      ticks.append(h('span', {style: {left: '6%'}}, fmtDate(fromDays(lo), 'short')), h('span', {style: {left: '94%'}}, fmtDate(fromDays(hi), 'short')));
    }
  }

  function drawTrack() {
    clear(rail); clear(marks);
    const cur = currentChange();
    S.changes.forEach((c, i) => {
      if (!c.in_force) return;
      const nextD = S.changes[i + 1]?.in_force;
      const a = pos(c.in_force), b = nextD ? pos(nextD) : 100;
      rail.append(h('div', {class: 'seg', style: {left: `${a}%`, width: `${Math.max(0, b - a)}%`, background: `var(--c${lawColor(c.law)})`}}));
      const label = `${c.law} · ${t('reader.in_force_on', {date: fmtDate(c.in_force)})}`;
      marks.append(h('button', {class: `mark${c === cur ? ' on' : ''}`, title: label, 'aria-label': label,
        style: {left: `${a}%`, background: `var(--c${lawColor(c.law)})`}, onclick: () => setDate(c.in_force)}));
    });
    range.value = Math.max(lo, Math.min(hi, toDays(S.date)));
    dateIn.value = S.date;
    const ds = S.changes.map(c => c.in_force).filter(Boolean);
    prevB.disabled = !ds.some(d => d < S.date);
    nextB.disabled = !ds.some(d => d > S.date);
    todayB.disabled = S.date === today();
  }

  async function update() {
    const seq = ++S.seq;
    legendBox.hidden = S.mode !== 'read';
    keepURL();
    drawTrack();
    clear(body).append(loading());
    let r;
    try {
      r = await tool('read_law', {path: S.path, date: S.date});
    } catch (e) {
      if (seq === S.seq) clear(body).append(errorBox(e));
      return;
    }
    if (seq !== S.seq) return;
    last = r;
    const head = (r.text || '').match(/^#{1,6}[ \t]+(.+)$/m);
    if (head) title.textContent = head[1].trim();
    verPill.textContent = r.last_change ? t('reader.version_of', {law: r.last_change.law}) : t('reader.not_yet');
    drawStatus(r);
    drawFacts(r);
    drawVersions();
    drawLimits(r);
    if (S.mode === 'compare') await drawCompare(seq, r);
    else if (S.mode === 'changes') await drawChanges(seq, r);
    else await drawRead(seq, r);
  }

  function drawStatus(r) {
    clear(status);
    if (!r.in_force || r.text == null) {
      status.append(h('span', {class: 'pill warn'}, t('reader.not_in_force')));
      return;
    }
    const same = r.latest && r.latest.state === 'same';
    status.append(h('span', {class: same ? 'pill' : 'pill warn'}, same ? t('reader.current') : t('reader.earlier')));
    const cur = currentChange();
    const nextD = r.next_change?.in_force;
    if (cur) status.append(nextD ? t('reader.span', {from: fmtDate(cur.in_force), to: fmtDate(addDays(nextD, -1))})
      : t('reader.span_open', {from: fmtDate(cur.in_force)}));
  }

  function notInForce(r) {
    const box = h('div', {class: 'empty'}, h('p', {}, t('reader.not_in_force_long', {date: fmtDate(S.date)})),
      r.why ? h('p', {class: 'engine'}, r.why) : null);
    if (r.next_change?.in_force) box.append(h('button', {class: 'btn', onclick: () => setDate(r.next_change.in_force)},
      t('reader.go_first', {date: fmtDate(r.next_change.in_force)})));
    return box;
  }

  async function plainText(r) {
    let text = r.text;
    let next = r.text_part?.next_offset;
    const box = h('div', {class: 'law'});
    box.append(render([{text}]));
    const wrap = h('div', {}, box);
    if (next != null) {
      const more = h('button', {class: 'btn', onclick: async () => {
        more.disabled = true;
        try {
          const p = await tool('read_law', {path: S.path, date: S.date, offset: next});
          text += p.text || '';
          next = p.text_part?.next_offset;
          clear(box).append(render([{text}]));
          if (next == null) more.remove(); else more.disabled = false;
        } catch (e) { more.replaceWith(errorBox(e)); }
      }}, t('reader.load_rest'));
      wrap.append(h('div', {class: 'more'}, more));
    }
    return wrap;
  }

  async function drawRead(seq, r) {
    clear(legendBox);
    if (r.text == null) { clear(body).append(notInForce(r)); return; }
    if (!S.color) {
      const el = await plainText(r);
      if (seq === S.seq) clear(body).append(el);
      legendBox.append(h('h3', {}, t('reader.who')), h('p', {class: 'muted'}, t('reader.color_off')));
      return;
    }
    let w;
    try {
      w = await tool('who_wrote', {path: S.path, date: S.date, include_runs: true});
    } catch (e) { w = null; }
    if (seq !== S.seq) return;
    if (!w || !w.runs || w.granularity !== 'word') {
      clear(body).append(await plainText(r));
      legendBox.append(h('h3', {}, t('reader.who')), h('p', {class: 'muted'}, t('reader.no_words')));
      return;
    }
    const segs = w.runs.map(run => ({text: run.text, cls: `run c${lawColor(run.law)}`, data: {law: run.law}}));
    const box = h('div', {class: `law colored${S.focus ? ' focus' : ''}`});
    box.append(render(segs));
    if (S.focus) box.querySelectorAll('.run').forEach(el => { if (el.dataset.law === S.focus) el.classList.add('hit'); });
    box.addEventListener('click', e => {
      const run = e.target.closest('.run');
      if (run && !getSelection().toString()) { S.focus = S.focus === run.dataset.law ? null : run.dataset.law; update(); }
    });
    clear(body).append(box);
    drawLegend(w);
  }

  function drawLegend(w) {
    clear(legendBox).append(h('h3', {}, t('reader.who')));
    const total = w.laws.reduce((n, l) => n + l.words, 0) || 1;
    const laws = w.laws.slice().sort((a, b) => (changeOf(a.law)?.in_force || '').localeCompare(changeOf(b.law)?.in_force || ''));
    const ul = h('ul', {class: 'legend'});
    for (const l of laws) {
      const c = changeOf(l.law);
      const pc = Math.round((100 * l.words) / total);
      ul.append(h('li', {}, h('button', {'aria-pressed': String(S.focus === l.law),
        onclick: () => { S.focus = S.focus === l.law ? null : l.law; update(); }},
      h('span', {class: 'sw', style: {background: `var(--c${lawColor(l.law)})`}}),
      h('span', {class: 'nm'}, l.law, c?.in_force ? h('small', {}, t('reader.in_force_on', {date: fmtDate(c.in_force, 'short')})) : null),
      h('span', {class: 'pc'}, `${t('reader.words', {n: l.words})} · ${pc} %`),
      h('span', {class: 'meter'}, h('i', {style: {width: `${pc}%`, background: `var(--c${lawColor(l.law)})`}})))));
    }
    legendBox.append(ul, h('p', {class: 'muted'}, t('reader.focus_hint')));
    if (w.restored?.length) legendBox.append(h('p', {class: 'engine'}, t('reader.restored', {n: w.restored.length})));
  }

  async function textOn(d) {
    const r = await tool('read_law', {path: S.path, date: d, max_chars: 400000});
    return r.text;
  }

  async function drawChanges(seq, r) {
    clear(legendBox);
    if (r.text == null) { clear(body).append(notInForce(r)); return; }
    const cur = currentChange();
    const idx = cur ? S.changes.indexOf(cur) : -1;
    const intro = h('div', {class: 'status'});
    if (!cur || idx <= 0) {
      intro.append(t('reader.first_version'));
      const el = h('div', {class: 'law'});
      el.append(render(diffSegments([{op: '+', text: r.text}], 'both')));
      clear(body).append(intro, el);
      return;
    }
    const before = addDays(cur.in_force, -1);
    let old, now;
    try { [old, now] = await Promise.all([textOn(before), textOn(S.date)]); } catch (e) { clear(body).append(errorBox(e)); return; }
    if (seq !== S.seq) return;
    intro.append(t('reader.changed_by', {law: cur.law, date: fmtDate(cur.in_force)}));
    const ops = diff(old || '', now || '');
    const el = h('div', {class: 'law'});
    if (ops) el.append(render(diffSegments(ops, 'both')));
    else el.append(h('p', {class: 'muted'}, t('reader.too_long')));
    clear(body).append(intro, el);
    if (cur.what) body.append(h('p', {class: 'engine more'}, cur.what));
  }

  async function drawCompare(seq, r) {
    clear(legendBox);
    if (!S.b) {
      const cur = currentChange();
      const idx = cur ? S.changes.indexOf(cur) : -1;
      S.b = idx > 0 ? addDays(cur.in_force, -1) : (S.changes[0]?.in_force || S.date);
      keepURL();
    }
    const [a, b] = [S.b, S.date].sort();
    let ta, tb;
    try { [ta, tb] = await Promise.all([textOn(a), textOn(b)]); } catch (e) { clear(body).append(errorBox(e)); return; }
    if (seq !== S.seq) return;
    const bIn = h('input', {type: 'date', id: 'rd-b', value: S.b});
    bIn.addEventListener('change', () => { if (isDate(bIn.value)) { S.b = bIn.value; update(); } });
    const col = (label, d, segs, input) => h('div', {},
      h('div', {class: 'cmp-h'}, input ? h('label', {for: 'rd-b'}, label) : h('span', {}, label), input || h('b', {}, fmtDate(d))),
      h('div', {class: 'law'}, segs ? render(segs) : h('p', {class: 'muted'}, t('reader.nothing_then'))));
    if (ta == null || tb == null) {
      clear(body).append(h('div', {class: 'cmp'},
        col(t('reader.compare_with'), S.b, (S.b === a ? ta : tb) != null ? [{text: S.b === a ? ta : tb}] : null, bIn),
        col(t('reader.as_of'), S.date, (S.date === a ? ta : tb) != null ? [{text: S.date === a ? ta : tb}] : null)));
      return;
    }
    const ops = diff(ta, tb);
    if (!ops) {
      let cd;
      try { cd = await tool('compare_dates', {path: S.path, date_a: a, date_b: b}); } catch (e) { clear(body).append(errorBox(e)); return; }
      if (seq !== S.seq) return;
      clear(body).append(h('div', {class: 'cmp-h'}, h('label', {for: 'rd-b'}, t('reader.compare_with')), bIn),
        h('div', {class: 'law'}, render(wordDiffSegments(cd.word_diff))));
      return;
    }
    const oldSegs = diffSegments(ops, 'old'), newSegs = diffSegments(ops, 'new');
    const left = S.b === a ? oldSegs : newSegs, right = S.b === a ? newSegs : oldSegs;
    clear(body).append(h('div', {class: 'cmp'}, col(t('reader.compare_with'), S.b, left, bIn), col(t('reader.as_of'), S.date, right)));
    const between = S.changes.filter(c => c.in_force > a && c.in_force <= b);
    body.append(h('p', {class: 'muted more'}, between.length
      ? t('reader.between', {n: between.length, laws: between.map(c => c.law).join(', ')})
      : t('reader.between_none')));
  }

  function drawFacts(r) {
    clear(factBox);
    const lc = r.last_change;
    if (!lc) {
      factBox.append(h('h3', {}, t('reader.from')), h('p', {class: 'summary'}, t('reader.not_yet')));
      return;
    }
    const full = S.changes.find(c => c.commit === lc.commit) || lc;
    const dl = h('dl', {class: 'kv'},
      h('dt', {}, t('reader.in_force')), h('dd', {}, fmtDate(lc.in_force)),
      full.enacted ? [h('dt', {}, t('reader.enacted')), h('dd', {}, fmtDate(full.enacted))] : null,
      full.published ? [h('dt', {}, t('reader.published')), h('dd', {}, full.published)] : null,
      r.next_change ? [h('dt', {}, t('reader.replaced')), h('dd', {}, h('button', {class: 'btn sm', onclick: () => setDate(r.next_change.in_force)},
        `${fmtDate(r.next_change.in_force)} · ${r.next_change.law}`))] : null);
    factBox.append(h('h3', {}, t('reader.from')), h('p', {class: 'big'}, lc.law), dl);
    if (full.what) factBox.append(h('p', {class: 'summary engine'}, full.what));
    const links = [...(r.sources || []), ...(full.sources || [])].filter((u, i, a) => /^https?:\/\//.test(u) && a.indexOf(u) === i);
    if (r.cite?.official_url) links.unshift(r.cite.official_url);
    if (links.length) {
      factBox.append(h('p', {class: 'summary'}, t('reader.sources')), h('ul', {class: 'caveats'},
        [...new Set(links)].slice(0, 5).map(u => h('li', {}, h('a', {href: u, target: '_blank', rel: 'noopener noreferrer'}, u.replace(/^https?:\/\//, ''))))));
    }
  }

  function drawVersions() {
    clear(versBox).append(h('h3', {}, t('reader.versions', {n: S.changes.length})));
    const cur = currentChange();
    const ul = h('ul', {class: 'vers'});
    S.changes.slice().reverse().forEach(c => {
      ul.append(h('li', {}, h('button', {'aria-current': String(c === cur), onclick: () => setDate(c.in_force)},
        h('span', {class: 'dot', style: {background: `var(--c${lawColor(c.law)})`}}),
        h('span', {class: 'dt'}, c.in_force || '?'),
        h('span', {class: 'id'}, c.law))));
    });
    versBox.append(ul);
  }

  function drawLimits(r) {
    clear(limitBox).append(h('h3', {}, t('reader.limits')));
    if (corpus) {
      limitBox.append(h('p', {}, historyPill(corpus.history)), h('p', {class: 'summary'}, historyHelp(corpus.history)));
    }
    if (r.latest?.summary) limitBox.append(h('p', {class: 'engine'}, r.latest.summary));
    if (r.freshness) limitBox.append(h('p', {class: 'engine'}, r.freshness));
    const notes = [...(r.caveats || []), ...(r.beyond_the_words || []).map(x => (typeof x === 'string' ? x : JSON.stringify(x)))];
    if (notes.length) {
      limitBox.append(h('details', {}, h('summary', {}, t('reader.caveats', {n: notes.length})),
        h('ul', {class: 'caveats engine-list'}, notes.map(n => h('li', {class: 'engine'}, n)))));
    }
  }

  function cite() {
    if (!last || last.text == null) { toast(t('reader.nothing_to_cite')); return; }
    const c = last.cite || {};
    const text = [c.pincite || `${S.path}, ${fmtDate(S.date)}`, c.official_url,
      t('reader.cite_record', {path: S.path, date: S.date})].filter(Boolean).join('\n');
    copy(text, citeOut);
  }

  await update();
}

// Shows which law wrote a run of words while the pointer rests on it.
export function setupTooltip() {
  const tip = $('tip');
  document.addEventListener('mouseover', e => {
    const r = e.target.closest?.('.colored .run');
    if (!r) { tip.hidden = true; return; }
    clear(tip).append(h('b', {}, r.dataset.law || ''), t('reader.tip'));
    tip.hidden = false;
  });
  document.addEventListener('mousemove', e => {
    if (tip.hidden) return;
    const x = Math.min(e.clientX + 14, innerWidth - tip.offsetWidth - 8);
    const y = e.clientY + 18 + tip.offsetHeight > innerHeight ? e.clientY - tip.offsetHeight - 10 : e.clientY + 18;
    tip.style.left = `${x}px`;
    tip.style.top = `${y}px`;
  });
  document.addEventListener('click', e => {
    if (e.target.closest?.('.colored .run')) tip.hidden = true;
  });
}

export {num};
