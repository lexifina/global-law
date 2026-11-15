// Law text as the corpora write it: Markdown-like, blocks separated by a blank line, "#" headings, line breaks kept.
// The text arrives in segments, each with a class (the law that wrote it, or a diff mark), and is laid out in blocks
// without ever being parsed as markup.
import {h} from './util.js';

// segments: [{text, cls?, data?}]. Returns a fragment of <h2..h4>/<p> blocks whose runs keep each segment's class.
export function render(segments) {
  const flat = segments.map(s => s.text).join('');
  const owner = new Int32Array(flat.length);
  let at = 0;
  segments.forEach((s, i) => { owner.fill(i, at, at + s.text.length); at += s.text.length; });

  const frag = document.createDocumentFragment();
  const re = /\n[ \t]*\n+/g;
  let start = 0, m;
  const blocks = [];
  while ((m = re.exec(flat))) { blocks.push([start, m.index]); start = m.index + m[0].length; }
  blocks.push([start, flat.length]);

  for (let [a, b] of blocks) {
    while (a < b && flat[a] === '\n') a++;
    if (a >= b) continue;
    const head = /^(#{1,6})[ \t]+/.exec(flat.slice(a, Math.min(b, a + 10)));
    let el;
    if (head) {
      el = h(`h${Math.min(4, head[1].length + 1)}`);
      a += head[0].length;
    } else el = h('p');
    let i = a;
    while (i < b) {
      const seg = segments[owner[i]];
      let j = i;
      while (j < b && owner[j] === owner[i]) j++;
      const piece = flat.slice(i, j);
      const lines = piece.split('\n');
      const span = seg.cls ? h('span', {class: seg.cls}) : null;
      if (span && seg.data) Object.assign(span.dataset, seg.data);
      const into = span || el;
      lines.forEach((line, k) => {
        if (k) into.append(h('br'));
        if (line) into.append(document.createTextNode(line));
      });
      if (span) el.append(span);
      i = j;
    }
    frag.append(el);
  }
  return frag;
}

// Word-level differences between two texts: [{text, op: '=' | '-' | '+'}], whitespace kept with the word before it.
// Returns null when the texts are too long to compare here (the server's word diff is used instead).
const MAX_CELLS = 6_000_000;
export function diff(a, b) {
  const ta = tokens(a), tb = tokens(b);
  let pre = 0;
  while (pre < ta.length && pre < tb.length && ta[pre] === tb[pre]) pre++;
  let suf = 0;
  while (suf < ta.length - pre && suf < tb.length - pre && ta[ta.length - 1 - suf] === tb[tb.length - 1 - suf]) suf++;
  const A = ta.slice(pre, ta.length - suf), B = tb.slice(pre, tb.length - suf);
  if (A.length * B.length > MAX_CELLS) return null;
  const n = A.length, m = B.length;
  const dp = new Array(n + 1);
  for (let i = 0; i <= n; i++) dp[i] = new Uint32Array(m + 1);
  for (let i = n - 1; i >= 0; i--) for (let j = m - 1; j >= 0; j--)
    dp[i][j] = A[i] === B[j] ? dp[i + 1][j + 1] + 1 : Math.max(dp[i + 1][j], dp[i][j + 1]);
  const out = [];
  const push = (op, text) => {
    const last = out[out.length - 1];
    if (last && last.op === op) last.text += text; else out.push({op, text});
  };
  ta.slice(0, pre).forEach(x => push('=', x));
  let i = 0, j = 0;
  while (i < n && j < m) {
    if (A[i] === B[j]) { push('=', A[i]); i++; j++; }
    else if (dp[i + 1][j] >= dp[i][j + 1]) push('-', A[i++]);
    else push('+', B[j++]);
  }
  while (i < n) push('-', A[i++]);
  while (j < m) push('+', B[j++]);
  ta.slice(ta.length - suf).forEach(x => push('=', x));
  return out;
}

function tokens(s) { return (s || '').match(/\S+\s*|\s+/g) || []; }

// Segments for one side of a diff: 'both' (inline), 'old' (deletions marked) or 'new' (insertions marked).
export function diffSegments(ops, side) {
  const segs = [];
  for (const o of ops) {
    if (o.op === '=') segs.push({text: o.text});
    else if (o.op === '-' && side !== 'new') segs.push({text: o.text, cls: 'del'});
    else if (o.op === '+' && side !== 'old') segs.push({text: o.text, cls: 'ins'});
  }
  return segs;
}

// git's plain word diff ("[-old-]{+new+}", with @@ hunk lines) as segments, for texts too long to compare here.
export function wordDiffSegments(wd) {
  const segs = [];
  const body = (wd || '').split('\n').filter(l => !l.startsWith('@@')).join('\n');
  const re = /\[-([\s\S]*?)-\]|\{\+([\s\S]*?)\+\}/g;
  let last = 0, m;
  while ((m = re.exec(body))) {
    if (m.index > last) segs.push({text: body.slice(last, m.index)});
    segs.push(m[1] !== undefined ? {text: m[1], cls: 'del'} : {text: m[2], cls: 'ins'});
    last = re.lastIndex;
  }
  if (last < body.length) segs.push({text: body.slice(last)});
  return segs;
}
