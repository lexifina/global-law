from pathlib import Path

p = Path(__file__).parent / "section3.html"
t = p.read_text(encoding="utf-8")
R = [
    ("COPY_EYEBROW", "145 municipal corpora · Argentina, Brazil, Switzerland, Mexico and Indonesia"),
    ("COPY_TITLE", "Towns copy their laws, mostly from the province's templates"),
    ("COPY_TEXT",
     "Each dot is a town. A line joins two towns whose law shares at least one long article word for word, and its colour is the kind of text shared. "
     "<b>499 articles of 25 words or more appear in two or more towns, linking 100 of the 145 towns.</b> Most links are in Buenos Aires province. "
     "Towns there pass the province's model ordinances to borrow from it, and copy each other's municipal tax codes. "
     "The most widely shared article comes from ordinances rescheduling debts owed to the province's COVID-19 emergency health fund. "
     "24 towns passed it word for word between September 2020 and November 2022. "
     "In Switzerland, the neighbouring Zug communes of Oberägeri and Unterägeri share 27 articles. Brazilian towns share passages of their town charters (leis orgânicas)."),
    ("COPY_SRC",
     "Current text of every municipal corpus in global-law. Articles are normalised (lower case, with accents, numbers and punctuation removed) and compared exactly. "
     "Articles under 25 words are left out because they are mostly boilerplate. Each article's family comes from its wording and its ordinance's title. "
     "Argentine town corpora hold a sample of about 200 recent ordinances each, so these are the copies visible in the sample, not all of them."),
]
for a, b in R:
    assert a in t, a; t = t.replace(a, b)
p.write_text(t, encoding="utf-8", newline="\n")
print("patched")
