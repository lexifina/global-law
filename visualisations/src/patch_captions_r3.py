"""Round 3 caption updates (Croatia, Gibraltar, Denmark, Hong Kong), each checked against the data printed in round3.log."""
from pathlib import Path
import re

p = Path("part_new_figs.html"); s = p.read_text(encoding="utf-8")
R = [
 ("Across twelve jurisdictions · updated every half hour", "Across sixteen jurisdictions · updated every half hour"),
 ("Germany, Switzerland, the UK, the US, Estonia, Finland, Liechtenstein, Luxembourg, Malta, Monaco, Slovakia and Slovenia.",
  "Germany, Switzerland, the UK, the US, Croatia, Denmark, Estonia, Finland, Gibraltar, Hong Kong, Liechtenstein, Luxembourg, Malta, Monaco, Slovakia and Slovenia."),
 ('<span class="eyebrow">Eight constitutions</span><h2>Constitutions grow', '<span class="eyebrow">Eleven constitutions</span><h2>Constitutions grow'),
 ("Estonia's, Slovenia's and Finland's (2000) are within 6% of their adopted length.",
  "Croatia's 1990 constitution grew by half (×1.47) through five reforms. Estonia's, Slovenia's and Finland's are within 6% of their adopted length, and Denmark's 1953 and Gibraltar's 2006 constitutions have never been amended."),
 ('<span class="eyebrow">Eight constitutions</span><h2>Constitutional wording lasts 28 years in Slovakia and 88 in Luxembourg</h2>',
  '<span class="eyebrow">Eleven constitutions</span><h2>Constitutional wording lasts 7 years in Croatia and 88 in Luxembourg</h2>'),
 ("<b>The median wording lasts about 28 years in Slovakia, 45 in Germany, 71 in Liechtenstein and 88 in Luxembourg.</b>",
  "<b>The median wording lasts about 7 years in Croatia, 28 in Slovakia, 45 in Germany, 71 in Liechtenstein and 88 in Luxembourg.</b>"),
 ("In Estonia, Slovenia, Monaco and Finland fewer than half of the versions have ever been rewritten, so no median is reached yet.",
  "In Estonia, Slovenia, Monaco and Finland fewer than half of the versions have ever been rewritten, and in Denmark and Gibraltar none has, so no median is reached."),
 ('<span class="eyebrow">Five countries</span><h2>Temporary law', '<span class="eyebrow">Six countries</span><h2>Temporary law'),
 ("<b>37 provisions in 11 episodes across five countries.</b>", "<b>57 provisions in 13 episodes across six countries.</b>"),
 ("Six were undone by a later act: two inside Luxembourg's COVID-19 law (one after 16 days), two Slovak election-law changes, one in the Slovak constitution and one in Estonia's election act.",
  "Eight were undone by a later act: two inside Luxembourg's COVID-19 law (one after 16 days), two Slovak election-law changes, one in the Slovak constitution, one in Estonia's election act, and two in Croatia's constitution, where the 2010 reform restored 19 articles to their pre-2001 wording."),
 ("Edition reconciliations and versions whose amending act is not identified (portal consolidations in Monaco and Slovenia) are excluded.",
  "Edition reconciliations, correction notices and versions whose amending act is not identified (portal consolidations in Monaco, Slovenia, Denmark and Hong Kong) are excluded."),
 ('<span class="eyebrow">Eleven jurisdictions</span><h2>Switzerland starts its law on 1 January. Most others start it any day</h2>',
  '<span class="eyebrow">Fifteen jurisdictions</span><h2>Switzerland and Denmark start their law on 1 January. Most others start it any day</h2>'),
 ("<b>Over half of Swiss changes start on 1 January, and two thirds of Slovak ones on the first of a month.</b>",
  "<b>Over half of Swiss changes and almost half of Danish ones start on 1 January, and two thirds of Slovak ones on the first of a month.</b>"),
 ("as are jurisdictions with fewer than ten dated acts (Finland so far).", "as are jurisdictions with fewer than ten dated acts (Finland and Croatia so far)."),
 ('<span class="eyebrow">Twelve jurisdictions · round 2</span>', '<span class="eyebrow">Fifteen jurisdictions · round 2</span>'),
 ("<b>In all seven countries with both, the constitution has more prohibitions per word than ordinary law</b>",
  "<b>In all nine countries with both, the constitution has more prohibitions per word than ordinary law</b>"),
 ("In five of the seven, ordinary law has more obligations.", "In six of the nine, ordinary law has more obligations."),
 ("Across languages the counts can't be compared: English drafting uses \"shall\" for almost every rule, so the US, UK and Malta score 10–14 where German-language law, drafted in the indicative, scores 0.4–2.3.",
  "Across languages the counts can't be compared: English and Danish drafting put \"shall\" or \"skal\" in almost every rule, so English-language law scores 7–14 and Danish 8–9, where German-language law, drafted in the indicative, scores 0.4–2.3."),
 ('<span class="eyebrow">Fourteen jurisdictions · round 3</span>', '<span class="eyebrow">Sixteen jurisdictions · round 3</span>'),
]
for a, b in R:
    assert a in s, a[:70]
    s = s.replace(a, b)
p.write_text(s, encoding="utf-8")

j = Path("part_new_js.js"); t = j.read_text(encoding="utf-8")
a = 'const x = d3.scaleUtc([P("2003-06-01"), P("2025-06-01")], [m.l, W - m.r]);'
assert a in t
t = t.replace(a, 'const x = d3.scaleUtc([P("1999-06-01"), P("2025-06-01")], [m.l, W - m.r]);')
j.write_text(t, encoding="utf-8")
print("captions patched")
