
// ---- Round 13: depth, volume and momentum maps ----
{
  const val = d => d.first;
  const col = d3.scaleSequential(d3.interpolateViridis).domain([1800, 2020]).clamp(true);
  worldMap("#f-mdp", val, col, { fmt: v => `history from ${v}`, items: [[1800, "1800"], [1850, "1850"], [1900, "1900"], [1950, "1950"], [2000, "2000"]] });
  const R = J.slice().sort((a, b) => a.first - b.first), pre1900 = R.filter(d => d.first < 1900).map(d => `${d.name} (${d.first})`);
  const since2000 = R.filter(d => d.first >= 2000).length;
  document.getElementById("mdp-text").innerHTML = `The earliest year each country's loaded history reaches. <b>${pre1900.length} reach back before 1900: ${pre1900.join(", ")}. ${since2000} of ${R.length} start in 2000 or later.</b>`;
}
{
  const val = d => d.acts;
  const col = d3.scaleSequentialLog(d3.interpolateGnBu).domain([5, d3.max(J, d => d.acts)]).clamp(true);
  worldMap("#f-mv", val, col, { fmt: v => `${fmt(v)} dated acts`, items: [[10, "10"], [100, "100"], [1000, "1,000"], [10000, "10,000"], [100000, "100,000"]] });
  const big = J.filter(d => d.acts >= 1000);
  document.getElementById("mv-text").innerHTML = `How much dated amending law each loaded history holds. <b>${big.length} histories hold at least 1,000 dated acts (${big.map(d => d.name).join(", ")}), together ${Math.round(100 * d3.sum(big, d => d.acts) / totalActs)}% of all ${fmt(totalActs)}.</b>`;
}
{
  const avg = d => d3.sum(d3.range(2015, 2025), y => d.years[y] || 0) / 10;
  // Only histories that cover the whole decade: the early half must hold at least half as many acts as the late half
  const half = (d, a, b) => d3.sum(d3.range(a, b + 1), y => d.years[y] || 0);
  const covers = d => half(d, 2015, 2019) >= .5 * half(d, 2020, 2024);
  const val = d => avg(d) * 10 >= 50 && covers(d) ? (d.years[2025] || 0) / avg(d) : null;
  const col = d3.scaleDiverging(d3.interpolateRdBu).domain([2, 1, 0]).clamp(true);
  worldMap("#f-mmo", val, col, { fmt: v => `2025 at ${v.toFixed(2)}× the 2015–2024 average`, items: [[0.25, "¼ of usual"], [0.5, "half"], [1, "usual"], [1.5, "1.5×"], [2, "double"]] });
  const R = J.filter(d => val(d) != null).map(d => [d.name, val(d)]).sort((a, b) => b[1] - a[1]);
  const up = R.filter(r => r[1] > 1.1), down = R.filter(r => r[1] < .9);
  document.getElementById("mmo-text").innerHTML = `2025's amending acts against each jurisdiction's average year from 2015 to 2024. <b>${up.length} legislated noticeably more than usual (${up.map(([n, v]) => `${n} ×${v.toFixed(1)}`).join(", ")}); ${down.length} noticeably less (${down.map(([n, v]) => `${n} ×${v.toFixed(1)}`).join(", ")}).</b> Histories that barely cover 2015–2019 are greyed out, since their baseline would be too low.`;
}
