from pathlib import Path
def patch(fn, pairs):
    p = Path(fn); s = p.read_text(encoding="utf-8")
    for a, b in pairs:
        if b in s: continue
        assert a in s, (fn, a[:60]); s = s.replace(a, b, 1)
    p.write_text(s, encoding="utf-8")
patch("analysis6.py", [('"gi": ("gibraltar-law", r"^(constitution|stamp-duties)/(?!README|arrangement)")}',
                        '"gi": ("gibraltar-law", r"^(constitution|stamp-duties)/(?!README|arrangement)"),\n         "dk": ("denmark-law", r"^(grundloven|skatteforvaltningsloven)/(?!README)"), "hk": ("hong-kong-law", r"^cap-[0-9]+/(?!README)")}'),
                       ('Legimonaco|', 'Legimonaco|Retsinformation|Department of Justice|')])
patch("episodes.py", [('Finlex|Legilux|Service central")', 'Finlex|Legilux|Service central|Retsinformation|Department of Justice")')])
patch("part_new_js.js", [('hr: "Croatia", gi: "Gibraltar" };', 'hr: "Croatia", gi: "Gibraltar", dk: "Denmark", hk: "Hong Kong" };'),
                         ('hr: "var(--c6)", gi: "var(--c7)" };', 'hr: "var(--c6)", gi: "var(--c7)", dk: "var(--ink)", hk: "var(--c6)" };'),
                         ('"fi", "hr", "gi"]', '"fi", "hr", "gi", "dk"]')])
patch("compose.py", [('"fi", "hr", "gi")', '"fi", "hr", "gi", "dk")')])
patch("analysis2.py", [('("Riigi Teataja", "Rechtsdienst", "Bundeskanzlei")', '("Riigi Teataja", "Rechtsdienst", "Bundeskanzlei", "Retsinformation", "Department of Justice")')])
print("ok")
