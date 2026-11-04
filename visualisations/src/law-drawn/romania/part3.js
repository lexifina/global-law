
// ---- Part three ----
const seq = t => d3.interpolateLab(css("--seq-lo"), css("--seq-hi"))(t);
// 14. Every day of the Monitorul Oficial, 2014-2025, one calendar block per year
{
  const CAL = DATA.cal, years = d3.range(2014, 2026), cs = 8.2, gap = 1.4, cols = 2, blockW = 54 * cs, blockH = 7 * cs, colGap = 46, rowGap = 34, m = { t: 26, l: 34 };
  const W = m.l + cols * blockW + (cols - 1) * colGap + 8, H = m.t + Math.ceil(years.length / cols) * (blockH + rowGap) + 6;
  const svg = d3.select("#f-days").attr("viewBox", `0 0 ${W} ${H}`);
  const shade = d3.scaleLog().domain([1, 20]).clamp(true);
  const KIND = ["HG", "Legea", "OUG", "OG", "other"];
  years.forEach((yr, k) => {
    const gx = m.l + (k % cols) * (blockW + colGap), gy = m.t + Math.floor(k / cols) * (blockH + rowGap), g = svg.append("g").attr("transform", `translate(${gx},${gy})`);
    const days = d3.timeDays(new Date(yr, 0, 1), new Date(yr + 1, 0, 1)), wk = d => d3.timeMonday.count(d3.timeYear(d), d), dow = d => (d.getDay() + 6) % 7;
    const tot = d3.sum(days, d => (CAL[d3.timeFormat("%Y-%m-%d")(d)] || [0])[0]);
    g.append("text").attr("class", "ser").attr("x", 0).attr("y", -8).style("font-size", "13px").text(yr);
    g.append("text").attr("x", blockW - 6).attr("y", -8).attr("text-anchor", "end").attr("fill", "var(--muted)").style("font-size", "10px").text(`${fmt(tot)} acts`);
    if (k % cols === 0) ["M", "W", "F", "S"].forEach((t, i) => g.append("text").attr("x", -8).attr("y", [0, 2, 4, 6][i] * cs + cs - 1.5).attr("text-anchor", "end").style("font-size", "8.5px").text(t === "S" ? "Su" : t));
    g.selectAll("rect").data(days).join("rect").attr("x", d => wk(d) * cs).attr("y", d => dow(d) * cs).attr("width", cs - gap).attr("height", cs - gap).attr("rx", 1.5)
      .attr("fill", d => { const v = (CAL[d3.timeFormat("%Y-%m-%d")(d)] || [0])[0]; return v ? seq(.12 + .88 * shade(v)) : "var(--tint)"; })
      .on("pointermove", (ev, d) => { const key = d3.timeFormat("%Y-%m-%d")(d), v = CAL[key];
        showTip(ev, `<b>${d3.timeFormat("%A %-d %B %Y")(d)}</b><br>${v ? `${fmt(v[0])} act${v[0] > 1 ? "s" : ""} published` : "nothing published"}${v ? `<br><span class="m">${KIND.map((n, i) => v[i + 1] ? `${n} ${v[i + 1]}` : "").filter(Boolean).join(" · ")}</span>` : ""}`); })
      .on("pointerleave", hideTip);
    // Month boundaries along the top
    d3.timeMonths(new Date(yr, 0, 1), new Date(yr + 1, 0, 1)).forEach(mo => { if (k < cols) g.append("text").attr("x", wk(mo) * cs).attr("y", -20).style("font-size", "9px").text(d3.timeFormat("%b")(mo)); });
    if (yr === 2021) { const d = new Date(2021, 2, 3);
      g.append("rect").attr("x", wk(d) * cs - 2).attr("y", dow(d) * cs - 2).attr("width", cs + 2.6).attr("height", cs + 2.6).attr("fill", "none").attr("stroke", "var(--c2)").attr("stroke-width", 1.6).attr("rx", 2);
      g.append("text").attr("x", 40).attr("y", -8).attr("fill", "var(--c2)").style("font-size", "10px").text("□ 3 March: 154 decisions in one day"); }
  });
}

// 15. Where government decisions land: four hex tile maps of the counties, one per topic
{
  const H = DATA.hex, TOP = [["prefect", "Prefects and subprefects", "--c1"], ["arms", "Flags and coats of arms", "--c2"], ["property", "Public and private property of the state", "--c3"], ["works", "Works, investments and expropriations", "--c4"]];
  const r = 23, w = Math.sqrt(3) * r, pw = 480, ph = 312, W = pw * 2, Hh = ph * 2;
  const svg = d3.select("#f-hex").attr("viewBox", `0 0 ${W} ${Hh}`);
  const hexPath = "M" + d3.range(6).map(i => { const a = Math.PI / 180 * (60 * i - 90); return [(r - 1.2) * Math.cos(a), (r - 1.2) * Math.sin(a)].map(v => v.toFixed(2)).join(","); }).join("L") + "Z";
  const pos = ([c, rw]) => [c * w + (rw % 2 ? w / 2 : 0), rw * 1.5 * r];
  const names = Object.keys(H);
  TOP.forEach(([key, label, hue], k) => {
    const g = svg.append("g").attr("transform", `translate(${(k % 2) * pw + 24},${Math.floor(k / 2) * ph + 22})`);
    const vals = names.map(n => H[n][3][k]), max = d3.max(vals), sum = d3.sum(vals);
    const ramp = t => d3.interpolateLab(css("--tint"), css(hue))(t), sc = d3.scaleSqrt().domain([0, max]);
    g.append("text").attr("class", "ser").style("font-size", "14px").attr("y", 0).text(label);
    g.append("text").attr("y", 16).attr("fill", "var(--muted)").style("font-size", "11px").text(`${fmt(sum)} county mentions · from ${d3.min(vals)} to ${max} a county`);
    const m = g.append("g").attr("transform", `translate(${w / 2 + 2},${r + 34})`);
    names.forEach(n => {
      const v = H[n][3][k], [x, y] = pos(H[n]), fill = ramp(.06 + .94 * sc(v)), c = d3.rgb(fill), dark = (.2126 * c.r + .7152 * c.g + .0722 * c.b) / 255 < .5;
      const cell = m.append("g").attr("transform", `translate(${x},${y})`).style("cursor", "default")
        .on("pointermove", ev => showTip(ev, `<b>${esc(n)}</b><br>${fmt(v)} decision${v === 1 ? "" : "s"} on ${label.toLowerCase()}, ${(100 * v / sum).toFixed(1)}% of all<br><span class="m">${TOP.map((t, j) => `${t[1].split(" ")[0]} ${H[n][3][j]}`).join(" · ")}</span>`))
        .on("pointerleave", hideTip);
      cell.append("path").attr("d", hexPath).attr("fill", fill).attr("stroke", v === max ? "var(--ink)" : "none").attr("stroke-width", 1.4);
      cell.append("text").attr("text-anchor", "middle").attr("y", -3).style("font-size", "8.5px").style("letter-spacing", ".04em").style("fill", dark ? "#fff" : "#18202e").style("fill-opacity", .7).text(H[n][2]);
      cell.append("text").attr("text-anchor", "middle").attr("y", 9).style("font-size", "11px").style("font-weight", 600).style("font-variant-numeric", "tabular-nums").style("fill", dark ? "#fff" : "#18202e").text(v);
    });
  });
}

// 16. What Parliament's laws are for: a river as wide as the laws passed each year, coloured where the corpus holds the law
{
  const P = DATA.purpose, KEYS = [["treaty", "ratify a treaty", "--c4"], ["ordinance", "approve or reject a government ordinance", "--c2"], ["new", "new law", "--c1"], ["amend", "amend or repeal an earlier law", "--c3"], ["other", "days, years, property, budgets", "--muted"]];
  const rows = P.map(([y, iss, ...v]) => { const o = { y, iss }; ["new", "amend", "ordinance", "treaty", "other"].forEach((k, i) => o[k] = v[i]); o.held = d3.sum(v); o.gapA = Math.max(0, iss - o.held) / 2; o.gapB = o.gapA; return o; });
  const W = 960, H = 470, m = { t: 24, r: 18, b: 34, l: 18 };
  const svg = d3.select("#f-purpose").attr("viewBox", `0 0 ${W} ${H}`);
  const order = ["gapA", ...KEYS.map(k => k[0]), "gapB"];
  const st = d3.stack().keys(order).offset(d3.stackOffsetSilhouette)(rows);
  const x = d3.scaleLinear().domain([1991, 2025]).range([m.l + 10, W - m.r - 10]);
  const ext = d3.max(rows, r => r.iss) / 2, cy = (m.t + H - m.b) / 2, k = (H - m.t - m.b) / 2 / ext;
  const y = v => cy - v * k;
  const area = d3.area().x(d => x(d.data.y)).y0(d => y(d[0])).y1(d => y(d[1])).curve(d3.curveMonotoneX);
  const col = Object.fromEntries(KEYS.map(kk => [kk[0], kk[2]]));
  // Year rules behind the river
  d3.range(1995, 2026, 5).forEach(yr => svg.append("line").attr("x1", x(yr)).attr("x2", x(yr)).attr("y1", m.t).attr("y2", H - m.b).attr("stroke", "var(--rule)").attr("stroke-dasharray", "2 3"));
  svg.append("g").selectAll("path").data(st).join("path").attr("d", area)
    .attr("fill", d => d.key.startsWith("gap") ? "var(--tint)" : `var(${col[d.key]})`).attr("fill-opacity", d => d.key === "other" ? .55 : 1)
    .attr("stroke", d => d.key.startsWith("gap") ? "var(--ghost)" : "var(--plate)").attr("stroke-width", d => d.key.startsWith("gap") ? .6 : .5);
  svg.append("g").attr("transform", `translate(0,${H - m.b + 4})`).call(d3.axisBottom(x).tickValues(d3.range(1995, 2026, 5)).tickFormat(d3.format("d")).tickSize(0)).call(axisStyle).call(g => g.select(".domain").remove());
  // Scale bar: 100 laws
  svg.append("line").attr("x1", W - m.r - 6).attr("x2", W - m.r - 6).attr("y1", m.t + 4).attr("y2", m.t + 4 + 100 * k).attr("stroke", "var(--ink)").attr("stroke-width", 1.4);
  svg.append("text").attr("x", W - m.r - 12).attr("y", m.t + 4 + 50 * k + 4).attr("text-anchor", "end").style("font-size", "10.5px").attr("fill", "var(--muted)").text("100 laws");
  // Direct labels at the year each band is thickest after 2014, placed in its middle
  const lab = (key, yr, text, dark) => { const s = st.find(s => s.key === key), d = s.find(d => d.data.y === yr);
    svg.append("text").attr("x", x(yr)).attr("y", y((d[0] + d[1]) / 2) + 4).attr("text-anchor", "middle").style("font-size", "11.5px").style("font-weight", 600).style("fill", dark ? "#18202e" : "#fff").style("pointer-events", "none").text(text); };
  lab("amend", 2023, "amend a law", false); lab("ordinance", 2021, "approve an ordinance", false); lab("new", 2015, "new law", false);
  // Annotations
  const note = (yr, vy, lines, anchor = "start") => { const g = svg.append("g").attr("transform", `translate(${x(yr)},${vy})`);
    lines.forEach((t, i) => g.append("text").attr("y", i * 13).attr("text-anchor", anchor).style("font-size", "10.5px").attr("fill", i ? "var(--muted)" : "var(--ink)").text(t)); };
  const r01 = rows.find(r => r.y === 2001), r23 = rows.find(r => r.y === 2023);
  svg.append("line").attr("x1", x(2001)).attr("x2", x(2001)).attr("y1", y(r01.iss / 2) - 4).attr("y2", m.t + 30).attr("stroke", "var(--muted)").attr("stroke-width", .8);
  note(2001.3, m.t + 6, ["2001: 788 laws passed", `the corpus holds ${r01.held} of them`]);
  note(2025, y(-r23.iss / 2) + 18, ["2023: 431 laws passed", `${r23.amend} amend, ${r23.ordinance} approve ordinances, ${r23.new} are new`], "end");
  note(1991, H - m.b - 40, ["the pale edges: laws passed", "that the corpus does not hold"]);
  // Hover: one column per year
  const fx = d3.scaleLinear().domain(x.range()).range([1991, 2025]).clamp(true);
  const rule = svg.append("line").attr("y1", m.t).attr("y2", H - m.b).attr("stroke", "var(--ink)").attr("stroke-width", .8).style("opacity", 0).style("pointer-events", "none");
  svg.append("rect").attr("x", m.l).attr("y", m.t).attr("width", W - m.l - m.r).attr("height", H - m.t - m.b).attr("fill", "transparent")
    .on("pointermove", function (ev) { const yr = Math.round(fx(d3.pointer(ev, this)[0])), r = rows.find(r => r.y === yr); rule.attr("x1", x(yr)).attr("x2", x(yr)).style("opacity", .5);
      showTip(ev, `<b>${yr}</b>: ${fmt(r.iss)} laws passed, ${fmt(r.held)} held<br>${KEYS.slice().reverse().map(([kk, n]) => `${n}: ${r[kk]}`).join("<br>")}`); })
    .on("pointerleave", () => { rule.style("opacity", 0); hideTip(); });
  legend("lg-purpose", [...KEYS.slice().reverse().map(([, n, c]) => [n, c]), ["passed, not held", "--tint"]], true);
}

// 17. The Fiscal Code, article by article: a quilt in reading order, one row group per Title
{
  const Q = DATA.fiscal_q, T = Q.titles, A = Q.arts, cs = 15, pitch = 17.5, lw = 232, cols = 41, W = lw + cols * pitch + 8;
  const groups = T.map((t, i) => ({ t, i, arts: A.filter(a => a[1] === i) }));
  let yy = 14; groups.forEach(g => { g.y = yy; g.rows = Math.ceil(g.arts.length / cols); yy += Math.max(g.rows * pitch, 30) + 12; });
  const svg = d3.select("#f-quilt").attr("viewBox", `0 0 ${W} ${yy}`);
  const year = t => seq(.22 + .78 * (t - 2016) / 10);
  const top = new Set(A.slice().sort((a, b) => b[2] - a[2]).slice(0, 3).map(a => a[0]));
  groups.forEach(g => {
    const n = g.arts.length, orig = g.arts.filter(a => !a[2] && !a[4]).length;
    g.el = svg.append("g").attr("transform", `translate(0,${g.y})`);
    g.el.append("text").attr("class", "ser").attr("y", 11).style("font-size", "13px").text(`${g.t[0]} · ${g.t[1]}`);
    g.el.append("text").attr("y", 25).attr("fill", "var(--muted)").style("font-size", "10.5px").text(`${n} articles · ${Math.round(100 * orig / n)}% as enacted`);
    g.arts.forEach((a, j) => {
      const x = lw + (j % cols) * pitch, y = Math.floor(j / cols) * pitch, c = g.el.append("g").attr("transform", `translate(${x},${y})`);
      const rep = a[5], og = !a[2] && !a[4];
      c.append("rect").attr("width", cs).attr("height", cs).attr("rx", 2)
        .attr("fill", rep ? "var(--plate)" : og ? "var(--tint)" : year(a[3])).attr("stroke", rep || og ? "var(--ghost)" : top.has(a[0]) ? "var(--ink)" : "none").attr("stroke-width", top.has(a[0]) ? 1.6 : .8);
      if (top.has(a[0]) && !rep) c.select("rect").attr("stroke", "var(--c2)").attr("stroke-width", 2);
      if (rep) c.append("path").attr("d", `M3,${cs - 3}L${cs - 3},3`).attr("stroke", "var(--ghost)").attr("stroke-width", 1.1);
      if (a[4]) c.append("path").attr("d", "M0,2Q0,0 2,0L7,0L0,7Z").attr("fill", "var(--c2)");
      c.append("rect").attr("width", pitch).attr("height", pitch).attr("x", -1).attr("y", -1).attr("fill", "transparent")
        .on("pointermove", ev => showTip(ev, `<b>Art. ${esc(a[0])}</b> · ${esc(g.t[1])}<br>${rep ? "repealed" : og ? "still as enacted in 2015" : `changed ${a[2]} time${a[2] > 1 ? "s" : ""}; current wording from ${a[3]}`}${a[4] ? "<br>inserted after 2015" : ""}`))
        .on("pointerleave", hideTip);
    });
  });
  // Year ramp legend
  const lg = d3.select("#lg-quilt").html(`<span><i class="bar" style="background:var(--tint);outline:1px solid var(--ghost)"></i>as enacted in 2015</span><span>wording from 2016</span>${d3.range(2016, 2027).map(y => `<i class="bar" style="background:${year(y)};margin:0 -4px"></i>`).join("")}<span>2026</span><span><i class="bar" style="background:var(--plate);outline:1px solid var(--ghost)"></i>repealed</span><span><svg width="10" height="10"><path d="M0,2Q0,0 2,0L8,0L0,8Z" fill="var(--c2)"/></svg>inserted after 2015</span><span><i class="bar" style="background:transparent;outline:2px solid var(--c2)"></i>three most changed</span>`);
}

// 18. Who rewrites the most-amended acts: a two-column Sankey from kind of amending act to the 14 acts with the most amendments
{
  const SK = DATA.sankey, IK = [["law", "Laws of Parliament", "--c1"], ["oug", "Emergency ordinances", "--c2"], ["og", "Ordinances", "--c4"], ["ccr", "Constitutional Court", "--c3"], ["portal", "No act named", "--ghost"], ["other", "Other acts", "--muted"]];
  const acts = SK.map(([t, gloss, status, v]) => { const o = { t, gloss, status, v, tot: d3.sum(v) }; o.gov = (v[1] + v[2]) / (v[0] + v[1] + v[2]); return o; }).sort((a, b) => b.gov - a.gov);
  const src = IK.map(([k, n, c], i) => ({ k, n, c, i, tot: d3.sum(acts, a => a.v[i]) }));
  const W = 960, H = 690, m = { t: 16, b: 16 }, pad = 9, x0 = 196, x1 = 612, nw = 12;
  const kk = (H - m.t - m.b - pad * (acts.length - 1) - 30) / d3.sum(acts, a => a.tot);
  const svg = d3.select("#f-sankey").attr("viewBox", `0 0 ${W} ${H}`);
  const lH = d3.sum(src, s => s.tot) * kk + pad * 3 * (src.length - 1); let ly = (H - lH) / 2;
  src.forEach(s => { s.y = ly; s.h = s.tot * kk; s.off = s.y; ly += s.h + pad * 3; });
  const cut = acts.findIndex(a => a.gov <= .5), gapX = 30;
  let ry = m.t; acts.forEach((a, i) => { if (i === cut) ry += gapX; a.y = ry; a.h = a.tot * kk; a.off = a.y; ry += a.h + pad; });
  const links = [];
  src.forEach(s => acts.forEach(a => { const v = a.v[s.i]; if (!v) return; links.push({ s, a, v, sy: s.off, h: v * kk }); s.off += v * kk; }));
  acts.forEach(a => links.filter(l => l.a === a).sort((p, q) => p.s.i - q.s.i).forEach(l => { l.ty = a.off; a.off += l.h; }));
  const xm = (x0 + nw + x1) / 2;
  const ribbon = l => `M${x0 + nw},${l.sy}C${xm},${l.sy} ${xm},${l.ty} ${x1},${l.ty}L${x1},${l.ty + l.h}C${xm},${l.ty + l.h} ${xm},${l.sy + l.h} ${x0 + nw},${l.sy + l.h}Z`;
  const lk = svg.append("g").selectAll("path").data(links).join("path").attr("d", ribbon).attr("fill", l => `var(${l.s.c})`).attr("fill-opacity", l => l.s.k === "portal" ? .45 : .5)
    .on("pointermove", (ev, l) => { lk.attr("fill-opacity", o => o === l ? .85 : .15); showTip(ev, `<b>${esc(l.a.gloss)}</b> (${esc(l.a.t)})<br>${fmt(l.v)} amendment${l.v > 1 ? "s" : ""} by ${l.s.n.toLowerCase()}, ${Math.round(100 * l.v / l.a.tot)}% of its ${l.a.tot}`); })
    .on("pointerleave", () => { lk.attr("fill-opacity", l => l.s.k === "portal" ? .45 : .5); hideTip(); });
  const focus = (pred) => lk.attr("fill-opacity", l => pred(l) ? .85 : .12);
  const reset = () => { lk.attr("fill-opacity", l => l.s.k === "portal" ? .45 : .5); hideTip(); };
  src.forEach(s => { const g = svg.append("g").on("pointermove", ev => { focus(l => l.s === s); showTip(ev, `<b>${s.n}</b><br>${fmt(s.tot)} amendments to these 14 acts`); }).on("pointerleave", reset);
    g.append("rect").attr("x", x0).attr("y", s.y).attr("width", nw).attr("height", Math.max(1.5, s.h)).attr("fill", `var(${s.c})`).attr("rx", 1.5);
    g.append("text").attr("x", x0 - 8).attr("y", s.y + s.h / 2 - 2).attr("text-anchor", "end").style("font-size", "12px").style("font-weight", 600).text(s.n);
    g.append("text").attr("x", x0 - 8).attr("y", s.y + s.h / 2 + 11).attr("text-anchor", "end").style("font-size", "10.5px").attr("fill", "var(--muted)").text(fmt(s.tot)); });
  acts.forEach(a => { const g = svg.append("g").on("pointermove", ev => { focus(l => l.a === a); showTip(ev, `<b>${esc(a.gloss)}</b> (${esc(a.t)}) · ${esc(a.status)}<br>${IK.map(([, n], i) => a.v[i] ? `${n}: ${a.v[i]}` : "").filter(Boolean).join("<br>")}`); }).on("pointerleave", reset);
    g.append("rect").attr("x", x1).attr("y", a.y).attr("width", nw).attr("height", a.h).attr("fill", "var(--ink)").attr("fill-opacity", .75).attr("rx", 1.5);
    const rep = a.status.startsWith("repealed") ? ` · repealed ${a.status.slice(9, 13)}` : "";
    const t1 = g.append("text").attr("x", x1 + nw + 8).attr("y", a.y + a.h / 2 - 2).style("font-size", "12px").style("font-weight", 600).text(a.gloss);
    if (rep) t1.append("tspan").style("font-weight", 400).style("font-size", "10.5px").style("fill", "var(--muted)").text(rep);
    g.append("text").attr("x", x1 + nw + 8).attr("y", a.y + a.h / 2 + 11).style("font-size", "10.5px").attr("fill", "var(--muted)").text(`${a.t.startsWith("Cod") ? "" : a.t.replace(" nr.", "") + " · "}${a.tot} changes · ${Math.round(100 * a.gov)}% government`); });
  // Where the government's share falls below half
  const cy = (acts[cut - 1].y + acts[cut - 1].h + acts[cut].y) / 2;
  svg.append("line").attr("x1", x1).attr("x2", W - 6).attr("y1", cy).attr("y2", cy).attr("stroke", "var(--muted)").attr("stroke-dasharray", "3 3");
  svg.append("text").attr("x", W - 6).attr("y", cy - 4).attr("text-anchor", "end").style("font-size", "10px").style("fill", "var(--c2)").text("↑ the government makes more than half");
  svg.append("text").attr("x", W - 6).attr("y", cy + 11).attr("text-anchor", "end").style("font-size", "10px").style("fill", "var(--c1)").text("↓ Parliament makes half or more");
  legend("lg-sankey", IK.map(([, n, c]) => [n, c]), true);
}
