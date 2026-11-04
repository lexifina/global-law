from pathlib import Path

HERE = Path(__file__).parent


def patch(name, pairs):
    p = HERE / name; t = p.read_text(encoding="utf-8")
    for a, b in pairs:
        assert a in t, (name, a[:70]); t = t.replace(a, b)
    p.write_text(t, encoding="utf-8", newline="\n")


patch("section3.html", [
    ("These five pictures use every corpus with dated acts: 612 histories from 182 countries, 479,003 acts.",
     "These five pictures use every corpus with dated changes: 612 histories from 182 countries, 479,003 dated changes. A dated change is one act where the record names the act, or one day's batch of changes where it credits only the publisher."),
    ('<span class="eyebrow">612 corpora with dated acts · 182 countries</span>', '<span class="eyebrow">612 corpora with dated changes · 182 countries</span>'),
    ("<b>France's single national history still holds 150,000 of the 479,003 dated acts, almost a third.</b> The federations are now constellations: Argentina has 86 corpora, Russia 83, Brazil 48, the United States 42 and Switzerland 39. Regional and city corpora hold 191,000 acts, 40% of the total.",
     "<b>France's single national history still holds 150,000 of the 479,003 dated changes, almost a third.</b> The federations are now constellations: Argentina has 87 corpora, Russia 83, Brazil 48, the United States 42 and Switzerland 39. Regional and city corpora hold 191,000 dated changes, 40% of the total."),
    ("Dated acts per corpus, counted as in global-law's analysis11.py: one act per author and in-force date, with snapshot, consolidated and generic commits left out. Circle area is proportional to the square root of acts, so small corpora stay visible.",
     "Dated changes per corpus, counted as in global-law's analysis11.py: one per crediting author and in-force date, with snapshot, consolidated and generic commits left out. Circle area is proportional to the square root of the count, so small corpora stay visible."),
    ("Each spoke is a day, and its length is the share of regional acts that start that day. <b>US states start 53% of their acts on 1 January, and Swiss cantons 81% on the first of some month.</b>",
     "Each spoke is a day, and its length is the share of regional changes that start that day. <b>53% of US state changes start on 1 January, and 81% of Swiss cantonal changes on the first of some month.</b>"),
    ("In-force dates of every dated act in each federation's regional and city corpora.", "In-force dates of every dated change in each federation's regional and city corpora."),
    ("Russian regional acts are dated by their official publication, which their record treats as the day they take effect.",
     "Russian regional changes are dated by their official publication, which their record treats as the day they take effect."),
    ("Each row is a region and each column a week, shaded by how many regional acts were published that week. The bars above count how many regions published anything. <b>In the week of 24 December 2018, 71 of the 82 regions published law, and December holds 19% of all regional acts.</b> That is the end-of-year round of budget and tax laws. A second, smaller wave comes at the end of November.",
     "Each row is a region and each column a week, shaded by how many days that week the region published changes to its law. The bars above count how many regions published anything. <b>In the week of 24 December 2018, 71 of the 82 regions published law, and December holds 19% of all regional publications.</b> The wave returns every December, with a smaller one at the end of November."),
    ('<div class="legend"><span>acts that week</span><span>1</span><span class="ramp"></span><span>10+</span></div>',
     '<div class="legend"><span>days with publications that week</span><span>1</span><span class="ramp"></span><span>5+</span></div>'),
    ("Publication dates of every dated act in the 82 Russian regional corpora with 20 or more acts in 2015–2025. Weeks start on Monday. Rows are sorted by total acts.",
     "Publication dates in the 82 Russian regional corpora with 20 or more dated changes in 2015–2025. Each corpus credits the official portal (publication.pravo.gov.ru), so a dated change is one day's publication. Weeks start on Monday. Rows are sorted by total publication days."),
])
patch("section3.js", [
    ("const cs = d3.scaleLog().domain([1, 10]).clamp(true);", "const cs = d3.scaleLog().domain([1, 5]).clamp(true);"),
    ("${rows[i].weeks[k]} acts published<br>", "published on ${rows[i].weeks[k]} day${rows[i].weeks[k] === 1 ? \"\" : \"s\"}<br>"),
    ("${(c.share[d] * 100).toFixed(c.share[d] < .01 ? 2 : 1)}% of regional acts start this day<br><span class=\"m\">busiest day ${d3.timeFormat(\"%-d %B\")(new Date(\"2024-\" + c.top[0]))} (${fmt(c.top[1])} acts)</span>",
     "${(c.share[d] * 100).toFixed(c.share[d] < .01 ? 2 : 1)}% of regional changes start this day<br><span class=\"m\">busiest day ${d3.timeFormat(\"%-d %B\")(new Date(\"2024-\" + c.top[0]))} (${fmt(c.top[1])} changes)</span>"),
    ("g.append(\"text\").attr(\"text-anchor\", \"middle\").attr(\"y\", r1 + 44).style(\"font-size\", \"10px\").text(`${c.corpora} corpora · ${fmt(c.acts)} acts`);",
     "g.append(\"text\").attr(\"text-anchor\", \"middle\").attr(\"y\", r1 + 44).style(\"font-size\", \"10px\").text(`${c.corpora} corpora · ${fmt(c.acts)} changes`);"),
    ("<br>${d.children.length} corpora · ${fmt(d3.sum(d.children, c => c.data.acts))} dated acts`", "<br>${d.children.length} corpora · ${fmt(d3.sum(d.children, c => c.data.acts))} dated changes`"),
    ("<br>${fmt(d.data.acts)} dated acts · ${d.data.level}<br>", "<br>${fmt(d.data.acts)} dated changes · ${d.data.level}<br>"),
])
print("patched")
